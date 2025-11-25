---
adr-id: "0004"
status: "completed"
created: "2025-11-24"
updated: "2025-11-25"
---

# Implementation Plan: YAML Documentation Audit and Redundancy Removal

## Metadata

- **ADR Reference**: ADR-0004 (YAML Documentation Audit and Redundancy Removal)
- **Type**: Documentation Cleanup and Accuracy Fix
- **Scope**: All YAML files, CLAUDE.md
- **SLO Focus**: Correctness, Maintainability, Observability

## (a) Plan

### Objectives

1. **Remove redundant YAML files** (~6,300 lines, 80% reduction)
2. **Fix all accuracy issues** in remaining documentation
3. **Archive v3.x milestones** for reference
4. **Validate all links** after cleanup

### Approach

**2-Phase Sequential Execution** (two commits for clear audit trail):

1. **Phase 1: Deletions and Archives** (Commit 1)
   - Delete 23 v2.x milestone files (5,809 lines)
   - Delete DOCUMENTATION_INVENTORY.yaml (508 lines)
   - Archive v3.x milestones to docs/milestones/archive/
   - Delete stale docs/api/ planning files

2. **Phase 2: Accuracy Fixes** (Commit 2)
   - Fix CLAUDE.md version and feature list (CRITICAL)
   - Fix CURRENT_ARCHITECTURE_STATUS.yaml version and CLI status (HIGH)
   - Fix SDK_QUALITY_STANDARDS.yaml feature status (HIGH)
   - Fix SSOT_DOCUMENTATION_ARCHITECTURE.yaml line count (MEDIUM)
   - Update any references to deleted files

### Validation Strategy

- After Phase 1: Run `lychee .` to find broken links from deletions
- After Phase 2: Run `lychee .` to verify all fixes complete
- Final: Git status clean, all validation passes

### Deliverables

1. ✅ ADR-0004 documenting decision rationale
2. ✅ This plan (docs/plan/0004-yaml-audit-redundancy-removal/plan.md)
3. ✅ 27 files deleted (23 milestones + inventory + 2 API plans + v3.x moves)
4. ✅ v3.x milestones archived to docs/milestones/archive/
5. ✅ All accuracy issues fixed (8 issues across 5 files)
6. ✅ 2 commits pushed to origin/main

---

## (b) Context

### Problem Background

**Discovered via 3-agent parallel DCTL survey** (2025-11-24):

**Agent 1 (Inventory)**: Found 31 YAML files totaling ~8,000 lines
- 73% is historical milestone documentation (v2.x series)
- Project is at v4.0.1, making v2.x milestones obsolete

**Agent 2 (Accuracy)**: Found 8 inaccuracies
- 2 CRITICAL: CLAUDE.md version/features wrong
- 4 HIGH: CURRENT_ARCHITECTURE_STATUS and SDK_QUALITY_STANDARDS outdated
- 2 MEDIUM: Minor discrepancies

**Agent 3 (Redundancy)**: Found major redundancies
- DOCUMENTATION_INVENTORY.yaml superseded by SSOT file
- 23 v2.x milestone files are historical-only
- Stale planning files for completed releases

### Files Inventory

**To Delete (24 files, ~6,300 lines)**:
- docs/milestones/MILESTONE_v2.0.0.yaml through v2.15.1.yaml (23 files)
- docs/DOCUMENTATION_INVENTORY.yaml (1 file)

**To Archive (2 files)**:
- docs/MILESTONE_v3.0.0.yaml → docs/milestones/archive/
- docs/MILESTONE_v3.1.0.yaml → docs/milestones/archive/

**To Fix (5 files, 8 issues)**:
- CLAUDE.md (2 issues: lines 66, 70)
- docs/CURRENT_ARCHITECTURE_STATUS.yaml (2 issues: lines 26, 59-67)
- docs/SDK_QUALITY_STANDARDS.yaml (2 issues: lines 20-24, 31-46)
- docs/SSOT_DOCUMENTATION_ARCHITECTURE.yaml (1 issue: line 362)
- DOCUMENTATION.md (update references to deleted files)

### Technical Constraints

**User Decisions** (from clarification loop):
- v2.x milestones: Delete entirely (not archive)
- v3.x milestones: Archive (not delete)
- DOCUMENTATION_INVENTORY.yaml: Delete
- CLAUDE.md fixes: Yes, fix inaccuracies
- Fix scope: All severities (CRITICAL + HIGH + MEDIUM)
- docs/api/ files: Review and clean stale planning files
- Commit strategy: Two commits (deletions, then fixes)

### Success Criteria

1. ✅ YAML file count reduced from 31 to ~7
2. ✅ All version references show v4.0.1
3. ✅ CLI status reflects removal in v4.0.0
4. ✅ Feature status shows "implemented" not "pending"
5. ✅ No broken links (lychee validation passes)
6. ✅ Git status clean after all commits

---

## (c) Task List

### Phase 1: Deletions and Archives ⏳

#### 1.1 Delete v2.x Milestone Files (23 files)

- [ ] Delete docs/milestones/MILESTONE_v2.0.0.yaml
- [ ] Delete docs/milestones/MILESTONE_v2.0.1.yaml
- [ ] Delete docs/milestones/MILESTONE_v2.0.2.yaml
- [ ] Delete docs/milestones/MILESTONE_v2.0.3.yaml
- [ ] Delete docs/milestones/MILESTONE_v2.0.4.yaml
- [ ] Delete docs/milestones/MILESTONE_v2.0.5.yaml
- [ ] Delete docs/milestones/MILESTONE_v2.1.0.yaml
- [ ] Delete docs/milestones/MILESTONE_v2.1.1.yaml
- [ ] Delete docs/milestones/MILESTONE_v2.2.0.yaml
- [ ] Delete docs/milestones/MILESTONE_v2.3.0.yaml
- [ ] Delete docs/milestones/MILESTONE_v2.4.0.yaml
- [ ] Delete docs/milestones/MILESTONE_v2.5.0.yaml
- [ ] Delete docs/milestones/MILESTONE_v2.6.0.yaml
- [ ] Delete docs/milestones/MILESTONE_v2.6.1.yaml
- [ ] Delete docs/milestones/MILESTONE_v2.7.0.yaml
- [ ] Delete docs/milestones/MILESTONE_v2.8.0.yaml
- [ ] Delete docs/milestones/MILESTONE_v2.9.0.yaml
- [ ] Delete docs/milestones/MILESTONE_v2.10.0.yaml
- [ ] Delete docs/milestones/MILESTONE_v2.11.0.yaml
- [ ] Delete docs/milestones/MILESTONE_v2.12.0.yaml
- [ ] Delete docs/milestones/MILESTONE_v2.14.0.yaml
- [ ] Delete docs/milestones/MILESTONE_v2.15.0.yaml
- [ ] Delete docs/milestones/MILESTONE_v2.15.1.yaml

#### 1.2 Delete Redundant Inventory File

- [ ] Delete docs/DOCUMENTATION_INVENTORY.yaml

#### 1.3 Archive v3.x Milestones

- [ ] Create docs/milestones/archive/ directory
- [ ] Move docs/MILESTONE_v3.0.0.yaml → docs/milestones/archive/
- [ ] Move docs/MILESTONE_v3.1.0.yaml → docs/milestones/archive/

#### 1.4 Review and Delete Stale docs/api/ Files

- [ ] Check docs/api/v3.0.0-stabilization-plan.yaml (v3.0.0 released - DELETE)
- [ ] Check docs/api/v3.1.0-test-quality-plan.yaml (v3.1.0 released - DELETE)
- [ ] Review other docs/api/ files for relevance

#### 1.5 Commit Phase 1

- [ ] Stage all deletions and moves
- [ ] Commit with conventional message
- [ ] Validate with lychee

### Phase 2: Accuracy Fixes ⏳

#### 2.1 Fix CLAUDE.md (CRITICAL)

- [ ] Line 66: Update version v2.5.0 → v4.0.1
- [ ] Line 70: Remove references to joblib, Polars, PyOD, CLI

#### 2.2 Fix CURRENT_ARCHITECTURE_STATUS.yaml (HIGH)

- [ ] Line 26: Update canonical_version v3.0.0 → v4.0.1
- [ ] Lines 59-67: Update CLI status to REMOVED_IN_V4.0.0

#### 2.3 Fix SDK_QUALITY_STANDARDS.yaml (HIGH)

- [ ] Lines 20-24: Update status pending → implemented
- [ ] Lines 31-32, 45-46: Update version references

#### 2.4 Fix SSOT_DOCUMENTATION_ARCHITECTURE.yaml (MEDIUM)

- [ ] Line 362: Update CLAUDE.md line count 72 → 70

#### 2.5 Update References to Deleted Files

- [ ] Check DOCUMENTATION.md for milestone references
- [ ] Update any broken references found

#### 2.6 Commit Phase 2

- [ ] Stage all accuracy fixes
- [ ] Commit with conventional message
- [ ] Validate with lychee
- [ ] Push to origin/main

---

## Progress Log

### 2025-11-24 Investigation Phase

- **3-agent DCTL survey**: Inventory, Accuracy, Redundancy agents
- **Clarification loop**: 2 rounds of multiple-choice questions
- **User decisions**: Delete v2.x, archive v3.x, fix all severities

### 2025-11-24 Implementation Phase

- **Started**: Creating ADR-0004 and plan

### 2025-11-25 Implementation Complete

- **Commit 1** (`8540bf6`): Deleted 27 files, archived v3.x milestones (6,943 deletions)
- **Commit 2** (`4c1a2da`): Fixed all accuracy issues (8 fixes across 5 files)
- **Validation**: Lychee link validation passed for ADR-0004 scope
- **YAML reduction**: ~8,000 → ~1,700 lines (79% reduction)

---

## Commit Messages

**Commit 1**: Deletions and archives
```
chore(yaml): remove 24 redundant files and archive v3.x milestones

Delete 23 v2.x milestone files (5,809 lines) - project at v4.0.1
Delete DOCUMENTATION_INVENTORY.yaml - superseded by SSOT file
Delete stale docs/api/ planning files for completed releases
Archive v3.x milestones to docs/milestones/archive/

~6,300 lines removed (~80% YAML reduction)

Refs: ADR-0004
```

**Commit 2**: Accuracy fixes
```
fix(docs): correct version references and feature status

CRITICAL:
- CLAUDE.md: Update version v2.5.0 → v4.0.1
- CLAUDE.md: Remove references to removed dependencies (CLI, joblib, Polars, PyOD)

HIGH:
- CURRENT_ARCHITECTURE_STATUS: Update canonical_version v3.0.0 → v4.0.1
- CURRENT_ARCHITECTURE_STATUS: Update CLI status to REMOVED_IN_V4.0.0
- SDK_QUALITY_STANDARDS: Update feature status pending → implemented

MEDIUM:
- SSOT_DOCUMENTATION_ARCHITECTURE: Fix CLAUDE.md line count 72 → 70

Refs: ADR-0004
```

---

## References

- **ADR**: docs/architecture/decisions/0004-yaml-audit-redundancy-removal.md
- **Related ADRs**: ADR-0003 (Repository Housekeeping)
- **Investigation**: 3-agent DCTL survey (2025-11-24)
