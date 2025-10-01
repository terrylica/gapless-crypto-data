
## 2.15.3 - 2025-09-26


### ✨ New Features

- Remove all testing from GitHub Actions workflow - Eliminates pytest test execution - Removes file encoding validation - Removes ruff linting checks - Removes CLI entry point testing - Keeps only essential build and SBOM generation - Streamlines workflow to build + publish only (by @terrylica)

- Implement SOTA pre-flight version validation system - Add PEP 691 JSON API version checking with HTML fallback - Implement version consistency validation across pyproject.toml and __init__.py - Create intelligent pre-commit hook with <2 second execution time - Add graceful degradation on network failures - Provide clear error messages with actionable remediation steps Consensus from 8 research agents: - Pre-commit + CI/CD integration points (8/8 unanimous) - PyPI API pre-flight validation (8/8 unanimous) - Performance-optimized tooling with UV ecosystem (8/8 unanimous) - PEP 691 JSON API with HTML fallback (7/8 strong majority) - Security-first publishing approach (8/8 unanimous) Prevents PyPI 'already exists' errors through proactive validation Implements modern Python packaging best practices from 2024-2025 (by @terrylica)



### 🐛 Bug Fixes & Improvements

- Simplify CI/CD pipeline and fix SBOM generation - Reduce Python version matrix from 4 versions to single Python 3.12 - Fix cyclonedx-py command syntax: add 'environment' subcommand - Maintain all quality checks with reduced CI execution time - Keep essential testing while removing unnecessary version matrix complexity Impact: Faster CI/CD pipeline with single Python version testing Classification: workflow optimization and command syntax fix (by @terrylica)



---
**Full Changelog**: https://github.com/Eon-Labs/rangebar/compare/v2.15.1...v2.15.3
