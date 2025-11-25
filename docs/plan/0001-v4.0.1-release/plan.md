---
adr-id: "0001"
status: "completed"
created: "2025-01-22"
updated: "2025-01-22"
completed: "2025-01-22"
---

# Release Plan: v4.0.1 - CLI Removal and Repository Split Implementation

## Metadata

- **ADR Reference**: ADR-0001 (Repository Split for ClickHouse Implementation)
- **Release Type**: Major version (v3.3.0 → v4.0.1)
- **Breaking Changes**: Yes (CLI removal)
- **Migration Path**: docs/development/CLI_MIGRATION_GUIDE.md

## (a) Plan

### Objectives

1. Release v4.0.1 as the correct file-based v4.x implementation
2. Complete CLI removal (breaking change planned since v3.3.0)
3. Replace yanked v4.0.0 (published in error with ClickHouse)
4. Establish clean separation between file-based and database-first implementations

### Release Workflow

```
[Code Changes] → [Commit] → [Push] → [Tag] → [GitHub Release] → [PyPI Publish]
     ✅              ✅         ⏳        ⏳            ⏳                ⏳
```

### Deliverables

1. **Git Tag**: v4.0.1 with annotated tag message
2. **GitHub Release**: v4.0.1 with changelog and release notes
3. **PyPI Package**: gapless-crypto-data v4.0.1 (replaces yanked v4.0.0)
4. **Documentation**: Updated CHANGELOG.md, README.md, CLI_MIGRATION_GUIDE.md

## (b) Context

### Background

**Repository Split Decision** (ADR-0001):

- ClickHouse implementation moved to `~/eon/gapless-crypto-clickhouse`
- This repository (`gapless-crypto-data`) continues file-based CSV collection
- v4.0.0 was published to PyPI in error with ClickHouse references (yanked 2025-01-22)

**CLI Deprecation Timeline**:

- v3.3.0 (2025-10-18): CLI deprecated with warnings
- v4.0.0 (planned): CLI removal
- v4.0.1 (this release): Actual CLI removal implementation

### Problem Statement

v4.0.0 was published to PyPI containing:

- ClickHouse database integration (moved to separate repo)
- Database-first architecture (not appropriate for this repo)
- Incorrect implementation for gapless-crypto-data package

**Actions Taken**:

1. ✅ Yanked v4.0.0 from PyPI (2025-01-22)
2. ✅ Deleted v4.0.0 tag and GitHub release
3. ✅ Deleted main-clickhouse branch
4. ✅ Created ADR-0001 documenting repository split

**Current State**:

- Repository at v3.3.0 on main branch
- Code updated to v4.0.1 (commits ready)
- Need to release v4.0.1 as correct v4.x implementation

### Technical Constraints

- **Python Compatibility**: Python 3.9-3.13 (no change from v3.x)
- **Dependencies**: duckdb, httpx, pandas, pydantic, pyarrow (no ClickHouse)
- **Architecture**: File-based CSV collection with DuckDB validation
- **Breaking Change**: CLI entry point removed completely

### Success Criteria

1. ✅ v4.0.1 tag created and pushed to GitHub
2. ✅ GitHub release published with changelog
3. ✅ PyPI package published and installable
4. ✅ Installation succeeds: `pip install gapless-crypto-data==4.0.1`
5. ✅ Python API works: `import gapless_crypto_data; gapless_crypto_data.fetch_data(...)`
6. ✅ CLI properly rejected: `gapless-crypto-data` command exits with error message

## (c) Task List

### Phase 1: Code Changes ✅

- [x] Remove CLI entry point from pyproject.toml
- [x] Update version to 4.0.1 in pyproject.toml and **init**.py
- [x] Update CLI deprecation notices to past tense (README, CLI_MIGRATION_GUIDE)
- [x] Update cli.py main() to exit with removal error
- [x] Add CHANGELOG entry for v4.0.1
- [x] Remove empty clickhouse directory
- [x] Commit changes: `ad3f945` and `11cf144`

### Phase 2: Repository Operations ✅

- [x] Push commits to origin/main
- [x] Verified Git LFS objects uploaded

### Phase 3: Release Management ✅

- [x] Create annotated git tag v4.0.1
- [x] Push tag to origin
- [x] Create GitHub release from tag
  - Release title: "v4.0.1 - CLI Removal (File-based Implementation)"
  - Release notes: Extracted from CHANGELOG.md
  - Marked as latest release
  - Included migration guide link
  - Release URL: https://github.com/terrylica/gapless-crypto-data/releases/tag/v4.0.1

### Phase 4: PyPI Publishing ✅

- [x] Create canonical publish script (scripts/publish-to-pypi.sh)
- [x] Build distribution: `uv build`
- [x] Verify build artifacts (wheel + sdist)
- [x] Publish to PyPI: `uv publish` with Doppler token
- [x] Verify PyPI listing: https://pypi.org/project/gapless-crypto-data/4.0.1/
- [x] Commit and push publish script

### Phase 5: Validation ✅

- [x] PyPI package verified available
- [x] GitHub release created and marked as latest
- [x] All commits pushed to origin/main
- [x] Update plan status to "completed"

## Progress Log

### 2025-01-22 Implementation

- **23:30-23:42**: Code changes for v4.0.1
  - Removed CLI entry point from pyproject.toml
  - Updated version to 4.0.1
  - Updated all CLI references to past tense
  - Updated cli.py to exit with error
  - Added CHANGELOG entry
  - Commits: ad3f945, 11cf144

- **23:42-23:45**: Created release plan (this document)
  - Structured plan with (a) plan, (b) context, (c) task list
  - Linked to ADR-0001
  - Ready for execution

- **23:45-24:05**: Release execution and PyPI publishing
  - Pushed commits to origin/main (handled Git LFS upload)
  - Created annotated v4.0.1 tag with comprehensive release notes
  - Published GitHub release: https://github.com/terrylica/gapless-crypto-data/releases/tag/v4.0.1
  - Created canonical publish script (scripts/publish-to-pypi.sh) with CI guards
  - Published to PyPI using Doppler credentials
  - Verified package available: https://pypi.org/project/gapless-crypto-data/4.0.1/
  - Committed and pushed publish script
  - **Status**: COMPLETED ✅

## Risk Assessment

### Low Risk

- Python API unchanged (fully backward compatible)
- File-based architecture unchanged
- No new dependencies

### Medium Risk

- CLI removal (breaking change)
  - **Mitigation**: Deprecated since v3.3.0, comprehensive migration guide
  - **Impact**: Users still on CLI must migrate to Python API

### Negligible Risk

- PyPI v4.0.0 already yanked
- Version number gap (v4.0.0 → v4.0.1) documented in CHANGELOG

## References

- **ADR-0001**: docs/architecture/decisions/0001-repository-split-clickhouse.md
- **Migration Guide**: docs/development/CLI_MIGRATION_GUIDE.md
- **CHANGELOG**: CHANGELOG.md lines 8-31
- **Commits**:
  - ad3f945: feat(v4.0.1): remove CLI interface completely
  - 11cf144: docs: improve markdown formatting and readability
  - 1ae3a72: docs(adr): document ClickHouse repository split decision

## Next Actions

1. Execute Phase 2: Push commits to remote
2. Execute Phase 3: Create tag and GitHub release (use semantic-release skill)
3. Execute Phase 4: Publish to PyPI (use pypi-doppler skill)
4. Execute Phase 5: Validation
