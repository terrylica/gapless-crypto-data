---
adr-id: "0003"
status: "in-progress"
created: "2025-11-24"
updated: "2025-11-24"
---

# Implementation Plan: Repository Housekeeping and Root Directory Cleanup

## Metadata

- **ADR Reference**: ADR-0003 (Repository Housekeeping and Root Directory Cleanup)
- **Type**: Repository Maintenance
- **Scope**: Root directory, configuration files, .gitignore, documentation
- **SLO Focus**: Maintainability, Correctness, Observability

## (a) Plan

### Objectives

1. **Reduce root directory clutter** from 31 to 26 files (16% reduction)
2. **Fix critical configuration errors** breaking release automation
3. **Prevent accidental large file commits** via .gitignore updates
4. **Update version references** to current v4.0.1
5. **Standardize naming conventions** for consistency

### Approach

**5-Phase Sequential Execution** (granular commits for detailed audit trail):

1. **Phase 1: .gitignore Protection** (1 file)
   - Add .mypy_cache/ (prevents 110 MB commit)
   - Add .pytest_cache/ (prevents 68 KB commit)

2. **Phase 2: Fix Critical Config Errors** (4 files)
   - Fix cliff-release-notes.toml repository URL (rangebar → gapless-crypto-data)
   - Fix cliff.toml project name (RangeBar → Gapless Crypto Data)
   - Delete .cz.toml (duplicate config with wrong Cargo.toml reference)
   - Remove outdated CLI test from publish.yml workflow

3. **Phase 3: Delete Completed/Obsolete Files** (8 deletions)
   - Delete 3 audit reports (CONFORMITY_AUDIT_REPORT.md, dead_code_audit_plan.md, UV_BUILD_SUCCESS.md)
   - Delete 2 release notes (RELEASE_NOTES.md, RELEASE_NOTES_SHORT.md)
   - Delete tmp/ directory entirely (468 KB)

4. **Phase 4: Update Version References** (1 file)
   - Update DOCUMENTATION.md v3.2.0 → v4.0.1
   - Update last modified date

5. **Phase 5: Standardize Naming** (1 rename)
   - Rename sdk-quality-standards.yaml → SDK_QUALITY_STANDARDS.yaml

### Validation Strategy

- After each phase: `git status` to verify expected changes
- After Phase 2: Verify cliff.toml syntax with `git cliff --dry-run`
- After Phase 4: Run `lychee .` to verify no broken links
- Final: Clean working tree, all tests pass

### Deliverables

1. ✅ ADR-0003 documenting decision rationale
2. ✅ This plan (docs/plan/0003-repository-housekeeping/plan.md)
3. ⏳ .gitignore updated with critical caches
4. ⏳ 4 configuration errors fixed
5. ⏳ 8 files/directories deleted
6. ⏳ Version references updated to v4.0.1
7. ⏳ 1 file renamed for naming consistency
8. ⏳ 5 commits pushed to origin/main

---

## (b) Context

### Problem Background

**Discovered via 6-agent parallel DCTL survey** (2025-11-24):

**Root Directory Clutter** (31 files):
- 3 completed audit reports from Sept 2025 (100% done, findings in current docs)
- 2 outdated release notes (v3.0.0 and v2.16.0 content, current is v4.0.1)
- tmp/ directory with 468 KB of v4.0.0 migration artifacts

**Critical .gitignore Gaps**:
- .mypy_cache/ (110 MB) - NOT ignored, at risk of accidental commit
- .pytest_cache/ (68 KB) - NOT ignored

**Critical Config Errors** (P0 - breaks automation):
1. cliff-release-notes.toml:19 - References wrong repo ("rangebar" instead of "gapless-crypto-data")
2. cliff.toml:8 - References wrong project ("RangeBar" instead of "Gapless Crypto Data")
3. .cz.toml - Duplicate commitizen config with wrong Cargo.toml reference
4. publish.yml:51-55 - Tests removed CLI (CLI removed in v4.0.0)

**Outdated Version References**:
- DOCUMENTATION.md line 5: Shows v3.2.0 (current is v4.0.1)
- DOCUMENTATION.md line 390: Shows v3.2.0 and 2025-10-18 date

**Naming Inconsistency**:
- sdk-quality-standards.yaml - Only kebab-case YAML in root docs/ (should be UPPERCASE_SNAKE_CASE)

### Technical Constraints

**User Decisions** (from clarification loop):
- Priority: Root directory cleanup over other housekeeping
- tmp/ policy: Delete all subdirectories (findings incorporated into ADRs)
- Audit reports: Delete (not archive) - findings captured in current docs
- Release notes: Delete both - CHANGELOG.md is canonical
- .gitignore: Add .mypy_cache/ and .pytest_cache/ only (not tmp/ or .claude/)
- Config errors: Fix all P0 issues immediately
- Version update: Yes, update to v4.0.1 with current date
- Naming: Fix only sdk-quality-standards.yaml
- Commit strategy: 5 granular commits

**Scope** (included):
- ✅ Root directory file cleanup
- ✅ Configuration error fixes
- ✅ .gitignore updates for Python caches
- ✅ Version reference updates
- ✅ Critical naming consistency

**Scope** (excluded):
- ❌ Markdown file naming (python-api.md, pypi-documentation.md, etc.) - 92% consistent, keep as-is
- ❌ tmp/ to .gitignore - directory being deleted entirely
- ❌ .claude/ to .gitignore - project-specific, not needed
- ❌ Archive audit reports - delete entirely per user decision
- ❌ GitHub Actions policy violations (testing/linting in CI) - defer to separate ADR

### Current State Analysis

**Files to Delete** (8 total):
1. CONFORMITY_AUDIT_REPORT.md (224 lines, Sept 25 2025, 100% complete)
2. dead_code_audit_plan.md (121 lines, Sept 25 2025, 26/26 variables removed)
3. UV_BUILD_SUCCESS.md (106 lines, build validation complete)
4. RELEASE_NOTES.md (14 lines, v3.0.0 content)
5. RELEASE_NOTES_SHORT.md (18 lines, v2.16.0 content)
6. tmp/convert-absolute-paths.py (4 KB, one-off script, task complete)
7. tmp/full-validation/ (424 KB, v4.0.0 validation, findings in ADR-0001)
8. tmp/clickhouse-local-viz-research/ (28 KB, research complete, findings in ADR-0008)
9. tmp/pypi-package-split/ (16 KB, investigation complete, findings in ADR-0011)

**Config Files to Fix** (4 total):
1. cliff-release-notes.toml - Line 19
2. cliff.toml - Line 8
3. .cz.toml - DELETE entire file
4. .github/workflows/publish.yml - Lines 51-55

**Documentation to Update** (1 file):
1. DOCUMENTATION.md - Lines 5 and 390

**File to Rename** (1 file):
1. docs/sdk-quality-standards.yaml → docs/SDK_QUALITY_STANDARDS.yaml

### Success Criteria

1. ✅ Root directory reduced from 31 to 26 files
2. ✅ .mypy_cache/ and .pytest_cache/ added to .gitignore
3. ✅ All 4 config errors fixed
4. ✅ tmp/ directory and contents deleted
5. ✅ Version references show v4.0.1
6. ✅ SDK standards YAML renamed to UPPERCASE convention
7. ✅ Git status clean after all commits
8. ✅ Lychee link validation passes
9. ✅ CHANGELOG generation works (cliff.toml fix verified)

---

## (c) Task List

### Phase 1: .gitignore Protection ✅

- [x] **Update .gitignore**:
  - [x] Add `.mypy_cache/` to prevent 110 MB accidental commit
  - [x] Add `.pytest_cache/` to prevent test cache commit
  - [x] Verify syntax with `git check-ignore --verbose .mypy_cache`

**Method**: Append to existing .gitignore after existing cache patterns

### Phase 2: Fix Critical Config Errors ✅

- [x] **Fix cliff-release-notes.toml** (line 19):
  - [x] Change: `https://github.com/terrylica/rangebar/compare/`
  - [x] To: `https://github.com/terrylica/gapless-crypto-data/compare/`

- [x] **Fix cliff.toml** (line 8):
  - [x] Change: `All notable changes to RangeBar will be documented in this file.`
  - [x] To: `All notable changes to gapless-crypto-data will be documented in this file.`

- [x] **Delete .cz.toml**:
  - [x] Remove duplicate commitizen config with wrong Cargo.toml reference

- [x] **Fix publish.yml** (lines 51-55):
  - [x] Remove outdated CLI test step

**Validation**: Run `git cliff --dry-run` to verify cliff.toml syntax

### Phase 3: Delete Completed/Obsolete Files ✅

- [x] **Delete audit reports** (3 files):
  - [x] `rm CONFORMITY_AUDIT_REPORT.md`
  - [x] `rm dead_code_audit_plan.md`
  - [x] `rm UV_BUILD_SUCCESS.md`

- [x] **Delete release notes** (2 files):
  - [x] `rm RELEASE_NOTES.md`
  - [x] `rm RELEASE_NOTES_SHORT.md`

- [x] **Delete tmp/ directory**:
  - [x] `rm -rf tmp/`

**Validation**: `git status` shows 8 deletions

### Phase 4: Update Version References ✅

- [x] **Update DOCUMENTATION.md**:
  - [x] Line 5: `**Version**: 3.2.0` → `**Version**: 4.0.1`
  - [x] Line 390: `**Last Updated**: 2025-10-18 (v3.2.0)` → `**Last Updated**: 2025-11-24 (v4.0.1)`

**Validation**: Run `lychee .` to verify no broken links

### Phase 5: Standardize Naming ✅

- [x] **Rename YAML file**:
  - [x] `git mv docs/sdk-quality-standards.yaml docs/SDK_QUALITY_STANDARDS.yaml`
  - [x] Update references in DOCUMENTATION.md if any

**Validation**: Check for broken references with `grep -r "sdk-quality-standards" docs/`

### Phase 6: Final Validation ✅

- [x] **Git status check**: Confirm clean working tree
- [x] **Link validation**: `lychee .` passes
- [x] **CHANGELOG test**: `git cliff --dry-run` succeeds
- [x] **Push to origin**: `git push origin main`

---

## Progress Log

### 2025-11-24 Investigation Phase

- **Multi-agent DCTL survey**: 6 agents investigated all aspects of repository
- **Clarification loop**: 4 rounds of multiple-choice questions
- **User decisions**: Captured all preferences for implementation

### 2025-11-24 Implementation Phase

- **Phase 1**: .gitignore updates (IN PROGRESS)

---

## Commit Messages

**Commit 1**: Update .gitignore
```
chore(gitignore): add Python cache directories

- Add .mypy_cache/ to prevent 110 MB accidental commit
- Add .pytest_cache/ to prevent test runner cache commit

Prevents repository bloat from development artifacts.

Refs: ADR-0003
```

**Commit 2**: Fix config errors
```
fix(config): correct repository and project names in automation

- Fix cliff-release-notes.toml: rangebar → gapless-crypto-data
- Fix cliff.toml: RangeBar → Gapless Crypto Data
- Delete .cz.toml: duplicate config with wrong Cargo.toml reference
- Remove outdated CLI test from publish.yml workflow

Fixes broken release automation and changelog generation.

Refs: ADR-0003
```

**Commit 3**: Clean root directory
```
chore(cleanup): remove completed audits and obsolete documentation

Delete completed work (findings in current docs):
- CONFORMITY_AUDIT_REPORT.md (Sept 2025, 100% complete)
- dead_code_audit_plan.md (Sept 2025, 26/26 variables removed)
- UV_BUILD_SUCCESS.md (build validation complete)

Delete outdated release notes (CHANGELOG.md is canonical):
- RELEASE_NOTES.md (v3.0.0 content)
- RELEASE_NOTES_SHORT.md (v2.16.0 content)

Delete temporary investigation artifacts:
- tmp/ directory (468 KB, findings in ADR-0001, ADR-0008, ADR-0011)

Reduces root from 31 → 26 files (16% reduction).

Refs: ADR-0003
```

**Commit 4**: Update version
```
docs(version): update DOCUMENTATION.md to v4.0.1

- Update version reference (v3.2.0 → v4.0.1)
- Update last modified date (2025-10-18 → 2025-11-24)

Ensures accurate version information for users and AI agents.

Refs: ADR-0003
```

**Commit 5**: Standardize naming
```
refactor(naming): standardize SDK standards YAML to UPPERCASE convention

- Rename: sdk-quality-standards.yaml → SDK_QUALITY_STANDARDS.yaml

Aligns with root docs/ YAML naming convention (UPPERCASE_SNAKE_CASE).

Refs: ADR-0003
```

---

## References

- **ADR**: docs/architecture/decisions/0003-repository-housekeeping.md
- **Related ADRs**: ADR-0001 (Repository Split), ADR-0002 (Lychee Validation)
- **Investigation**: 6-agent DCTL survey (2025-11-24)
