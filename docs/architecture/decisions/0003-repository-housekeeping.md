---
status: "accepted"
date: "2025-11-24"
decision-makers: ["terrylica"]
---

# ADR-0003: Repository Housekeeping and Root Directory Cleanup

## Context and Problem Statement

After v4.0.1 release and ClickHouse migration (ADR-0001), the repository accumulated temporary artifacts, outdated documentation, and configuration errors. A comprehensive 6-agent parallel survey identified:

- **Root directory clutter**: 31 files including 3 completed audit reports, 2 outdated release notes, and historical validation docs
- **tmp/ accumulation**: 468 KB of temporary investigation artifacts from v4.0.0 migration
- **Critical .gitignore gaps**: .mypy_cache/ (110 MB) and .pytest_cache/ (68 KB) at risk of accidental commit
- **Critical config errors**: cliff.toml references wrong project ("RangeBar"), .cz.toml references non-existent Cargo.toml
- **Outdated version references**: DOCUMENTATION.md shows v3.2.0 while current version is v4.0.1
- **Naming inconsistencies**: sdk-quality-standards.yaml uses kebab-case while convention is UPPERCASE_SNAKE_CASE

**Investigation Methodology**: Multi-agent DCTL (Dynamically Created Todo List) survey across 6 perspectives:
1. Root directory structure
2. Configuration files
3. Temporary/build artifacts
4. Documentation organization
5. Scripts and tools
6. Naming conventions

## Decision Drivers

- **Maintainability SLO**: Reduce cognitive load by removing completed/obsolete files
- **Correctness SLO**: Fix config errors breaking release automation
- **Observability SLO**: Clear version references, accurate documentation
- **Repository hygiene**: Prevent accidental commits of large cache files (110 MB mypy)

## Considered Options

### Option 1: Comprehensive Cleanup (SELECTED)
- Fix all P0 config errors immediately
- Delete completed audit reports (findings captured in current docs)
- Delete tmp/ directory entirely (findings incorporated into ADRs)
- Update .gitignore for critical caches
- Update version references to v4.0.1
- Fix naming inconsistency

### Option 2: Conservative Cleanup
- Archive audit reports to docs/audit/ instead of deleting
- Archive tmp/ findings to docs/validation/archives/
- Skip config fixes (defer to separate task)
- Keep version references as-is

### Option 3: Minimal Cleanup
- Only add .gitignore entries
- Keep all files for historical reference
- Skip config fixes and version updates

## Decision Outcome

**Chosen option: Option 1 (Comprehensive Cleanup)**

Rationale:
- CHANGELOG.md is canonical version history (no need for duplicate RELEASE_NOTES)
- Completed audits (Sept 2025) are historical snapshots; current state in docs/CURRENT_ARCHITECTURE_STATUS.yaml
- tmp/ artifacts from v4.0.0 migration already incorporated into ADR-0001
- Config errors break automation (must fix)
- Outdated version references mislead users and AI agents

## Consequences

### Positive

- **Root directory**: 31 → 26 files (16% reduction, clearer navigation)
- **Disk space**: ~468 KB freed immediately, 110 MB prevented (future .mypy_cache)
- **Automation fixed**: Release notes will link to correct repository
- **Accurate documentation**: Version references match current v4.0.1
- **Repository hygiene**: Python cache files properly ignored

### Negative

- **Historical data loss**: Audit reports and tmp/ investigation artifacts permanently deleted
  - *Mitigation*: All findings already incorporated into ADRs and current documentation
- **Minor risk**: Deleting tmp/ before verifying all findings extracted
  - *Mitigation*: ADR-0001 (repository split), ADR-0008 (clickhouse viz), ADR-0011 (PyPI fork rejection) capture key findings

### Neutral

- Five granular commits for detailed audit trail (vs single commit)
- Naming standardization limited to one file (sdk-quality-standards.yaml only)

## Implementation

See: `docs/plan/0003-repository-housekeeping/plan.md`

**Commit Strategy** (5 commits):
1. Update .gitignore (.mypy_cache/, .pytest_cache/)
2. Fix config errors (cliff.toml, cliff-release-notes.toml, publish.yml, delete .cz.toml)
3. Delete root files (3 audits + 2 release notes + tmp/)
4. Update DOCUMENTATION.md version (v3.2.0 → v4.0.1)
5. Rename sdk-quality-standards.yaml → SDK_QUALITY_STANDARDS.yaml

**Validation**:
- Git status confirms clean tree
- Lychee link validation passes
- CHANGELOG generation works (cliff.toml fix verified)

## Links

- **Investigation**: 6-agent DCTL survey (2025-11-24)
- **Related ADRs**: ADR-0001 (ClickHouse split), ADR-0002 (Lychee validation)
- **Supersedes**: None
- **Superseded by**: None
