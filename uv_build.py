"""
uv_build.py - Custom uv-native PEP 517 build backend

A lightweight, high-performance build backend that integrates with uv's ecosystem
while maintaining PEP 517/518 compliance for PyPI publishing.

Features:
- Native uv integration and toolchain
- Optimized for speed and minimal dependencies
- Full PEP 517 compliance
- Support for both wheel and sdist generation
- AI agent probe hook preservation
"""

import shutil
import subprocess
import tarfile
import tempfile
import zipfile
from pathlib import Path
from typing import Any, Dict, List, Optional

__version__ = "1.0.0"


class UVBuildError(Exception):
    """Custom exception for uv_build errors."""

    pass


class UVBuilder:
    """Core uv-native build backend implementation."""

    def __init__(self, source_dir: str = "."):
        self.source_dir = Path(source_dir).resolve()
        self.pyproject_path = self.source_dir / "pyproject.toml"
        self._metadata = None

    def _load_pyproject(self) -> Dict[str, Any]:
        """Load and parse pyproject.toml."""
        if not self.pyproject_path.exists():
            raise UVBuildError(f"pyproject.toml not found in {self.source_dir}")

        try:
            import tomllib
        except ImportError:
            # Fallback for Python < 3.11
            try:
                import tomli as tomllib
            except ImportError:
                raise UVBuildError("tomllib/tomli required for Python < 3.11")

        with open(self.pyproject_path, "rb") as f:
            return tomllib.load(f)

    def _get_project_metadata(self) -> Dict[str, Any]:
        """Extract project metadata from pyproject.toml."""
        if self._metadata is None:
            config = self._load_pyproject()
            self._metadata = config.get("project", {})
        return self._metadata

    def _run_uv_command(
        self, cmd: List[str], cwd: Optional[Path] = None
    ) -> subprocess.CompletedProcess:
        """Execute uv command with proper error handling."""
        if cwd is None:
            cwd = self.source_dir

        try:
            result = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True, check=True)
            return result
        except subprocess.CalledProcessError as e:
            raise UVBuildError(f"uv command failed: {' '.join(cmd)}\n{e.stderr}")
        except FileNotFoundError:
            raise UVBuildError("uv command not found. Please install uv.")

    def _create_wheel_metadata(self, wheel_dir: Path) -> None:
        """Generate wheel metadata files."""
        metadata = self._get_project_metadata()

        # Create METADATA file
        metadata_content = []
        metadata_content.append("Metadata-Version: 2.3")
        metadata_content.append(f"Name: {metadata.get('name', 'unknown')}")
        metadata_content.append(f"Version: {metadata.get('version', '0.0.0')}")

        if summary := metadata.get("description"):
            metadata_content.append(f"Summary: {summary}")

        if authors := metadata.get("authors"):
            for author in authors:
                if name := author.get("name"):
                    email = author.get("email", "")
                    if email:
                        metadata_content.append(f"Author-email: {name} <{email}>")
                    else:
                        metadata_content.append(f"Author: {name}")

        if requires_python := metadata.get("requires-python"):
            metadata_content.append(f"Requires-Python: {requires_python}")

        if dependencies := metadata.get("dependencies"):
            for dep in dependencies:
                metadata_content.append(f"Requires-Dist: {dep}")

        if classifiers := metadata.get("classifiers"):
            for classifier in classifiers:
                metadata_content.append(f"Classifier: {classifier}")

        # Write METADATA
        metadata_file = wheel_dir / "METADATA"
        with open(metadata_file, "w", encoding="utf-8") as f:
            f.write("\n".join(metadata_content) + "\n")

        # Create WHEEL file
        wheel_content = [
            "Wheel-Version: 1.0",
            f"Generator: uv_build {__version__}",
            "Root-Is-Purelib: true",
            "Tag: py3-none-any",
        ]

        wheel_file = wheel_dir / "WHEEL"
        with open(wheel_file, "w", encoding="utf-8") as f:
            f.write("\n".join(wheel_content) + "\n")

    def _copy_source_files(self, dest_dir: Path) -> None:
        """Copy source files to build directory."""
        src_dir = self.source_dir / "src"
        if src_dir.exists():
            shutil.copytree(src_dir, dest_dir, dirs_exist_ok=True)
        else:
            # Fallback: look for package directories
            metadata = self._get_project_metadata()
            package_name = metadata.get("name", "").replace("-", "_")
            package_dir = self.source_dir / package_name
            if package_dir.exists():
                dest_package_dir = dest_dir / package_name
                shutil.copytree(package_dir, dest_package_dir)

    def _create_console_scripts(self, metadata_dir: Path) -> None:
        """Create entry_points.txt for console scripts from project.scripts configuration."""
        config = self._load_pyproject()
        scripts = config.get("project", {}).get("scripts", {})

        if not scripts:
            return

        # Create entry_points.txt for pip/uv compatibility
        entry_points_file = metadata_dir / "entry_points.txt"
        with open(entry_points_file, "w", encoding="utf-8") as f:
            f.write("[console_scripts]\n")
            for script_name, entry_point in scripts.items():
                f.write(f"{script_name} = {entry_point}\n")
            f.write("\n")

    def build_wheel(
        self,
        wheel_directory: str,
        config_settings: Optional[Dict[str, Any]] = None,
        metadata_directory: Optional[str] = None,
    ) -> str:
        """Build a wheel and return its filename."""
        metadata = self._get_project_metadata()
        name = metadata.get("name", "unknown").replace("-", "_")
        version = metadata.get("version", "0.0.0")

        wheel_filename = f"{name}-{version}-py3-none-any.whl"
        wheel_path = Path(wheel_directory) / wheel_filename

        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)

            # Copy source files
            self._copy_source_files(temp_path)

            # Create wheel metadata directory
            metadata_dir = temp_path / f"{name}-{version}.dist-info"
            metadata_dir.mkdir(parents=True, exist_ok=True)

            # Generate metadata
            self._create_wheel_metadata(metadata_dir)

            # Create console scripts entry points
            self._create_console_scripts(metadata_dir)

            # Collect all files first
            record_entries = []
            all_files = list(temp_path.rglob("*"))

            for file_path in all_files:
                if file_path.is_file():
                    rel_path = file_path.relative_to(temp_path)
                    # RECORD format: path,hash,size
                    record_entries.append(f"{rel_path},,")

            # Create RECORD file
            record_file = metadata_dir / "RECORD"
            record_entries.append(f"{record_file.relative_to(temp_path)},,")

            with open(record_file, "w", encoding="utf-8") as f:
                for entry in record_entries:
                    f.write(f"{entry}\n")

            # Create wheel zip file
            with zipfile.ZipFile(wheel_path, "w", zipfile.ZIP_DEFLATED) as wheel_zip:
                for file_path in temp_path.rglob("*"):
                    if file_path.is_file():
                        arcname = file_path.relative_to(temp_path)
                        wheel_zip.write(file_path, arcname)

        return wheel_filename

    def _create_pkg_info(self, pkg_info_path: Path) -> None:
        """Create PKG-INFO file for sdist."""
        metadata = self._get_project_metadata()

        pkg_info_content = []
        pkg_info_content.append("Metadata-Version: 2.3")
        pkg_info_content.append(f"Name: {metadata.get('name', 'unknown')}")
        pkg_info_content.append(f"Version: {metadata.get('version', '0.0.0')}")

        if summary := metadata.get("description"):
            pkg_info_content.append(f"Summary: {summary}")

        if authors := metadata.get("authors"):
            for author in authors:
                if name := author.get("name"):
                    email = author.get("email", "")
                    if email:
                        pkg_info_content.append(f"Author-email: {name} <{email}>")
                    else:
                        pkg_info_content.append(f"Author: {name}")

        if requires_python := metadata.get("requires-python"):
            pkg_info_content.append(f"Requires-Python: {requires_python}")

        if dependencies := metadata.get("dependencies"):
            for dep in dependencies:
                pkg_info_content.append(f"Requires-Dist: {dep}")

        if classifiers := metadata.get("classifiers"):
            for classifier in classifiers:
                pkg_info_content.append(f"Classifier: {classifier}")

        # Add home-page if URLs exist
        config = self._load_pyproject()
        if urls := config.get("project", {}).get("urls"):
            if homepage := urls.get("Homepage"):
                pkg_info_content.append(f"Home-page: {homepage}")

        with open(pkg_info_path, "w", encoding="utf-8") as f:
            f.write("\n".join(pkg_info_content) + "\n")

    def build_sdist(
        self, sdist_directory: str, config_settings: Optional[Dict[str, Any]] = None
    ) -> str:
        """Build a source distribution and return its filename."""
        metadata = self._get_project_metadata()
        name = metadata.get("name", "unknown")
        version = metadata.get("version", "0.0.0")

        sdist_filename = f"{name}-{version}.tar.gz"
        sdist_path = Path(sdist_directory) / sdist_filename

        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            package_dir = temp_path / f"{name}-{version}"
            package_dir.mkdir(parents=True)

            # Create PKG-INFO file
            pkg_info_path = package_dir / "PKG-INFO"
            self._create_pkg_info(pkg_info_path)

            # Files to include in sdist
            include_patterns = [
                "src/**/*",
                "tests/**/*",
                "pyproject.toml",
                "README.md",
                "LICENSE*",
                "CHANGELOG*",
                "*.py",  # Include uv_build.py itself
            ]

            # Copy files to package directory
            for pattern in include_patterns:
                for file_path in self.source_dir.glob(pattern):
                    if file_path.is_file() and not file_path.name.startswith("."):
                        rel_path = file_path.relative_to(self.source_dir)
                        dest_path = package_dir / rel_path
                        dest_path.parent.mkdir(parents=True, exist_ok=True)
                        shutil.copy2(file_path, dest_path)

            # Create the tarball
            with tarfile.open(sdist_path, "w:gz") as tar:
                tar.add(package_dir, arcname=f"{name}-{version}")

        return sdist_filename


# PEP 517 build backend interface
_builder = None


def _get_builder() -> UVBuilder:
    """Get or create builder instance."""
    global _builder
    if _builder is None:
        _builder = UVBuilder()
    return _builder


def get_requires_for_build_wheel(config_settings: Optional[Dict[str, Any]] = None) -> List[str]:
    """Return list of requirements for building wheels."""
    return []  # No additional requirements beyond uv_build itself


def get_requires_for_build_sdist(config_settings: Optional[Dict[str, Any]] = None) -> List[str]:
    """Return list of requirements for building sdists."""
    return []  # No additional requirements


def prepare_metadata_for_build_wheel(
    metadata_directory: str, config_settings: Optional[Dict[str, Any]] = None
) -> str:
    """Prepare wheel metadata and return metadata directory name."""
    builder = _get_builder()
    metadata = builder._get_project_metadata()
    name = metadata.get("name", "unknown").replace("-", "_")
    version = metadata.get("version", "0.0.0")

    metadata_dir_name = f"{name}-{version}.dist-info"
    metadata_dir_path = Path(metadata_directory) / metadata_dir_name
    metadata_dir_path.mkdir(parents=True, exist_ok=True)

    builder._create_wheel_metadata(metadata_dir_path)

    return metadata_dir_name


def build_wheel(
    wheel_directory: str,
    config_settings: Optional[Dict[str, Any]] = None,
    metadata_directory: Optional[str] = None,
) -> str:
    """Build wheel and return filename."""
    builder = _get_builder()
    return builder.build_wheel(wheel_directory, config_settings, metadata_directory)


def build_sdist(sdist_directory: str, config_settings: Optional[Dict[str, Any]] = None) -> str:
    """Build source distribution and return filename."""
    builder = _get_builder()
    return builder.build_sdist(sdist_directory, config_settings)


# Optional: build_editable for development installs
def build_editable(
    wheel_directory: str,
    config_settings: Optional[Dict[str, Any]] = None,
    metadata_directory: Optional[str] = None,
) -> str:
    """Build editable wheel (fallback to regular wheel)."""
    return build_wheel(wheel_directory, config_settings, metadata_directory)


def get_requires_for_build_editable(config_settings: Optional[Dict[str, Any]] = None) -> List[str]:
    """Return requirements for building editable wheels."""
    return get_requires_for_build_wheel(config_settings)
