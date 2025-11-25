---
status: "accepted"
date: "2025-11-24"
decision-makers: ["terrylica"]
---

# ADR-0004: YAML Documentation Audit and Redundancy Removal

## Context and Problem Statement

A comprehensive 3-agent parallel DCTL survey of all YAML files identified significant accuracy issues and redundancies:

**Inventory**: 31 YAML files (~8,000 lines total)
- 23 historical v2.x milestone files (5,809 lines, 73% of all YAML)
- 6 documentation/specification files
- 3 GitHub Actions workflows

**Critical Inaccuracies Found**:
1. CLAUDE.md shows v2.5.0 (should be v4.0.1)
2. CLAUDE.md references removed features (joblib, Polars, PyOD, CLI)
3. CURRENT_ARCHITECTURE_STATUS.yaml shows v3.0.0 (should be v4.0.1)
4. CURRENT_ARCHITECTURE_STATUS.yaml shows CLI as "PRODUCTION_READY" (removed in v4.0.0)
5. SDK_QUALITY_STANDARDS.yaml shows features as "pending" (actually implemented)

**Major Redundancies**:
1. DOCUMENTATION_INVENTORY.yaml (508 lines) - superseded by SSOT_DOCUMENTATION_ARCHITECTURE.yaml
2. 23 v2.x milestone files (5,809 lines) - project at v4.0.1, history preserved in git
3. Stale docs/api/ planning files for completed releases

## Decision Drivers

- **Correctness SLO**: Inaccurate version/feature information misleads users and AI agents
- **Maintainability SLO**: 73% of YAML content is historical milestone documentation
- **Observability SLO**: Documentation should reflect actual codebase state
- **Repository hygiene**: Reduce cognitive load by removing obsolete files

## Considered Options

### Option 1: Comprehensive Cleanup (SELECTED)
- Delete all v2.x milestone files (23 files, 5,809 lines)
- Archive v3.x milestones (not delete)
- Delete DOCUMENTATION_INVENTORY.yaml (superseded)
- Fix all accuracy issues (CRITICAL + HIGH + MEDIUM)
- Review and clean stale docs/api/ files

### Option 2: Archive Only
- Move v2.x milestones to archive instead of deleting
- Keep DOCUMENTATION_INVENTORY for reference
- Fix only critical accuracy issues

### Option 3: Minimal Intervention
- Keep all files
- Fix only CLAUDE.md version number
- Defer other cleanup

## Decision Outcome

**Chosen option: Option 1 (Comprehensive Cleanup)**

Rationale:
- v2.x milestone history preserved in git (deletions recoverable)
- DOCUMENTATION_INVENTORY superseded by more recent SSOT file (v1.2.0 vs Oct 20)
- Inaccurate documentation actively misleads users (especially AI agents reading CLAUDE.md)
- 80% YAML reduction improves maintainability

## Consequences

### Positive

- **YAML reduction**: ~8,000 → ~1,500 lines (80%+ reduction)
- **Accurate documentation**: All version references aligned to v4.0.1
- **Reduced maintenance burden**: Fewer files to keep in sync
- **Cleaner repository**: Focus on current architecture, not historical releases

### Negative

- **Historical data in git only**: v2.x milestones no longer browsable in file tree
  - *Mitigation*: History preserved in git, can be recovered if needed
- **Reference updates required**: Must update any links to deleted files
  - *Mitigation*: Validate with lychee after deletions

### Neutral

- Two-commit strategy separates deletions from accuracy fixes
- v3.x milestones archived (not deleted) for reference

## Implementation

See: `docs/plan/0004-yaml-audit-redundancy-removal/plan.md`

**Commit Strategy**:
1. Delete redundant files + archive v3.x milestones
2. Fix all accuracy issues (CLAUDE.md, YAML files)

**Validation**:
- Lychee link validation after each commit
- Verify no broken references to deleted files
- Confirm version consistency across documentation

## Links

- **Investigation**: 3-agent DCTL survey (2025-11-24)
- **Related ADRs**: ADR-0003 (Repository Housekeeping)
- **Supersedes**: None
- **Superseded by**: None
