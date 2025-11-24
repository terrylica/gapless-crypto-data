#!/usr/bin/env python3
"""
Convert absolute file paths to relative paths in documentation.

Usage: python3 tmp/convert-absolute-paths.py
"""
import re
from pathlib import Path

# Base directory
BASE_DIR = Path("/Users/terryli/eon/gapless-crypto-data")

# Absolute path pattern
ABS_PATH_PATTERN = r'/Users/terryli/eon/gapless-crypto-data/'

# Files to process with their absolute path counts
FILES_TO_PROCESS = {
    "CLAUDE.md": 12,
    "docs/architecture/OVERVIEW.md": 11,
    "docs/guides/python-api.md": 6,
    "docs/architecture/DATA_FORMAT.md": 5,
    "docs/guides/DATA_COLLECTION.md": 5,
    "docs/validation/OVERVIEW.md": 6,
    "docs/development/SETUP.md": 4,
    "docs/development/COMMANDS.md": 3,
    "docs/development/CLI_MIGRATION_GUIDE.md": 2,
    "docs/validation/STORAGE.md": 2,
    "docs/validation/QUERY_PATTERNS.md": 2,
}

def calculate_relative_path(file_path: Path, target_path: Path) -> str:
    """
    Calculate relative path from file_path to target_path.

    Args:
        file_path: Source file path
        target_path: Target file path (absolute)

    Returns:
        Relative path string
    """
    file_dir = file_path.parent
    try:
        # Calculate relative path
        rel_path = Path(target_path).relative_to(BASE_DIR)

        # Calculate how many levels up we need to go
        file_rel_path = file_dir.relative_to(BASE_DIR)
        depth = len(file_rel_path.parts)

        if depth == 0:
            # File is at project root
            return f"./{rel_path}"
        else:
            # File is in a subdirectory
            up_levels = "../" * depth
            return f"{up_levels}{rel_path}"
    except ValueError:
        # Target is not relative to BASE_DIR
        return str(target_path)

def convert_file(file_path: Path) -> tuple[int, int]:
    """
    Convert absolute paths in a file to relative paths.

    Returns:
        Tuple of (conversions_made, total_absolute_paths_found)
    """
    content = file_path.read_text()
    original_content = content

    # Pattern to match markdown links with absolute paths
    pattern = r'\]\(/Users/terryli/eon/gapless-crypto-data/([\w/.-]+)\)'

    def replace_abs_path(match):
        """Replace absolute path with relative path"""
        target_rel = match.group(1)  # Part after base dir
        target_abs = BASE_DIR / target_rel

        # Calculate relative path from current file to target
        rel_path = calculate_relative_path(file_path, target_abs)

        return f"]({rel_path})"

    # Replace all absolute paths
    new_content = re.sub(pattern, replace_abs_path, content)

    # Count changes
    abs_count = len(re.findall(pattern, original_content))
    conversions = abs_count if new_content != original_content else 0

    # Write back if changed
    if new_content != original_content:
        file_path.write_text(new_content)
        print(f"✅ {file_path.relative_to(BASE_DIR)}: {conversions} paths converted")
    else:
        print(f"⚠️  {file_path.relative_to(BASE_DIR)}: No absolute paths found (expected {FILES_TO_PROCESS.get(str(file_path.relative_to(BASE_DIR)), 0)})")

    return conversions, abs_count

def main():
    """Main conversion function"""
    print("🔄 Converting absolute file paths to relative paths...\n")

    total_conversions = 0
    total_files = 0

    for file_rel_path in FILES_TO_PROCESS.keys():
        file_path = BASE_DIR / file_rel_path

        if not file_path.exists():
            print(f"❌ {file_rel_path}: File not found")
            continue

        conversions, abs_count = convert_file(file_path)
        total_conversions += conversions
        total_files += 1

    print(f"\n✅ Complete: {total_conversions} paths converted across {total_files} files")

if __name__ == "__main__":
    main()
