---
adr-id: "0005"
status: "completed"
created: "2025-11-25"
updated: "2025-11-25"
---

# Implementation Plan: Earthly Release-Validation Pipeline

## Metadata

- **ADR Reference**: ADR-0005 (Earthly Release-Validation Pipeline with Observability)
- **Type**: CI/CD Infrastructure Refactoring
- **Scope**: Earthfile, GitHub Actions, semantic-release, Pushover
- **SLO Focus**: Observability, Maintainability, Correctness

## (a) Plan

### Objectives

1. **Create Earthfile** with release-validation targets
2. **Configure semantic-release** for automated versioning
3. **Remove policy violations** (tests/linting from GitHub Actions)
4. **Add Pushover alerts** for release notifications
5. **Wire Earthly into GitHub Actions**

### Approach

**4-Phase Sequential Execution**:

1. **Phase 1: Earthfile Creation**
   - Create Earthfile with build, release-stats, pushover targets
   - Validate locally with `earthly +build`

2. **Phase 2: semantic-release Configuration**
   - Create .releaserc.json with conventional-changelog
   - Configure GitHub token access
   - Test dry-run locally

3. **Phase 3: GitHub Actions Refactoring**
   - Remove ci.yml (tests/linting forbidden)
   - Simplify publish.yml (remove tests)
   - Update release.yml to use Earthly

4. **Phase 4: Pushover Integration**
   - Add PUSHOVER_USER_KEY and PUSHOVER_API_TOKEN to Doppler
   - Create Earthly target for notifications
   - Test end-to-end flow

### Validation Strategy

- After Phase 1: `earthly +build` succeeds locally
- After Phase 2: `npx semantic-release --dry-run` shows expected version
- After Phase 3: GitHub Actions workflow runs without tests
- After Phase 4: Pushover notification received

### Deliverables

1. [x] Earthfile with release-validation targets
2. [x] .releaserc.json for semantic-release
3. [x] Updated GitHub Actions workflows (no tests/linting)
4. [x] Pushover integration for release alerts
5. [x] Documentation updates

---

## (b) Context

### Problem Background

**Current State Analysis** (2025-11-25):

| Workflow    | Issues                                      |
| ----------- | ------------------------------------------- |
| ci.yml      | Contains tests + linting (POLICY VIOLATION) |
| publish.yml | Contains tests + linting (POLICY VIOLATION) |
| release.yml | Uses deprecated actions/create-release@v1   |

**User Requirements** (from conversation):

- Earthly as canonical pipeline
- semantic-release for versioning
- Pushover alerts linking to GitHub Release
- No tests/linting in GitHub Actions
- Observability-first release-validation

### Technical Constraints

**Doppler Secrets (notifications/prd)**:

- `PUSHOVER_USER_KEY`: Pushover user identifier (exists)
- `PUSHOVER_APP_TOKEN`: Pushover application token (exists)
- `GH_TOKEN`: GitHub token for semantic-release (uses `gh auth token` locally, GITHUB_TOKEN in CI)

**Earthly Requirements**:

- Earthly CLI installed locally
- Docker/Colima running for containerized builds

**semantic-release Requirements**:

- Node.js for npx execution
- Conventional commit history

### Success Criteria

1. [x] `earthly +build` succeeds locally
2. [x] `earthly +release-stats` outputs structured JSON
3. [x] `earthly +pushover-notify` sends test notification
4. [x] GitHub Actions uses Earthly (no direct test/lint steps)
5. [x] Release creates GitHub Release + PyPI publish + Pushover alert

---

## (c) Task List

### Phase 1: Earthfile Creation

- [x] Create Earthfile with VERSION declaration
- [x] Add +deps target for Python dependencies
- [x] Add +build target for package build
- [x] Add +release-stats target for structured output
- [x] Add +pushover-notify target for alerts
- [x] Test locally: `earthly +build` - VALIDATED

### Phase 2: semantic-release Configuration

- [x] Create .releaserc.json
- [x] Configure @semantic-release/commit-analyzer
- [x] Configure @semantic-release/release-notes-generator
- [x] Configure @semantic-release/changelog
- [x] Configure @semantic-release/github
- [x] Test dry-run: `npm run release:dry` - VALIDATED (v5.0.0)

### Phase 3: GitHub Actions Refactoring

- [x] Delete ci.yml (policy violation)
- [x] Update publish.yml: remove tests/linting steps
- [x] Update release.yml: use Earthly, remove deprecated actions
- [x] Add Earthly setup action to workflows
- [x] Validate workflow syntax - actionlint passed

### Phase 4: Pushover Integration

- [x] Pushover credentials found in Doppler (notifications/prd)
- [x] GitHub secrets set: PUSHOVER_USER_KEY, PUSHOVER_APP_TOKEN
- [x] Create scripts/test-pushover.sh for local testing
- [x] Integrate into Earthly +pushover-notify target
- [x] Integrate into GitHub Actions release.yml
- [x] Test notification sent successfully

### Phase 5: Documentation and Commit

- [x] Create ADR-0005 and plan
- [x] Commit with conventional messages
- [x] Push to origin/main

---

## Progress Log

### 2025-11-25 Assessment Phase

- **Current state audit**: Identified 3 workflows with policy violations
- **ADR-0005 created**: Decision documented
- **Plan created**: This file

### 2025-11-25 Implementation Complete

- **Commit 1** (`a45a321`): Earthfile + semantic-release + package.json
- **Commit 2** (`9e149c7`): GitHub Actions refactoring (removed ci.yml, updated workflows)
- **Commit 3** (`a403ffd`): Pushover scripts + .gitignore updates

**Files created**:

- `Earthfile` - Build, release-stats, pushover-notify targets
- `.releaserc.json` - semantic-release configuration
- `package.json` - Node.js dependencies for semantic-release
- `scripts/test-pushover.sh` - Local Pushover testing script

**Files modified**:

- `.github/workflows/publish.yml` - Removed tests/linting
- `.github/workflows/release.yml` - Modern actions + Earthly + Pushover
- `.gitignore` - Added node_modules, logs

**Files deleted**:

- `.github/workflows/ci.yml` - Policy violation (tests in CI)

### 2025-11-25 End-to-End Validation Complete

**Commit 4** (`54c3e4e`): Fix Doppler secret names (PUSHOVER_APP_TOKEN)
**Commit 5** (`a7b776e`): Fix Earthfile with --no-install-project flag

**Validation Results**:

| Component | Status | Details |
|-----------|--------|---------|
| Earthly +build | ✅ PASS | Builds Python package successfully |
| semantic-release | ✅ PASS | Dry run shows v5.0.0 release |
| Pushover | ✅ PASS | Test notification received |
| GitHub Secrets | ✅ PASS | PUSHOVER_USER_KEY, PUSHOVER_APP_TOKEN set |
| GitHub Actions | ✅ PASS | Workflows validated with actionlint |

**Key Fixes Applied**:

1. Earthfile: Added `--no-install-project` to prevent README.md missing error
2. Pushover: Corrected secret name to `PUSHOVER_APP_TOKEN` (not API_TOKEN)
3. Doppler: Using `notifications/prd` project (credentials already exist)
4. GitHub Secrets: Synced from Doppler using `gh secret set`

**Release Ready**: Run `npm run release` to create v5.0.0 with:
- GitHub Release with changelog
- Pushover notification with release link
- Package build artifacts

---

## Commit Messages

**Commit 1**: Earthfile and semantic-release

```
feat(ci): add Earthly pipeline and semantic-release configuration

- Create Earthfile with build, release-stats, pushover-notify targets
- Add .releaserc.json for automated versioning
- Observability-first release-validation flow

Refs: ADR-0005
```

**Commit 2**: GitHub Actions refactoring

```
refactor(ci): remove tests from GitHub Actions per local-first policy

- Delete ci.yml (tests/linting run locally only)
- Update publish.yml to use Earthly
- Update release.yml with modern actions

BREAKING CHANGE: CI no longer runs tests (run locally before push)

Refs: ADR-0005
```

**Commit 3**: Pushover integration

```
feat(ci): add Pushover notifications for release events

- Add Earthly +pushover-notify target
- Configure Doppler secrets for Pushover API
- Link notifications to GitHub Release

Refs: ADR-0005
```

---

## References

- **ADR**: docs/architecture/decisions/0005-earthly-release-pipeline.md
- **Skills**: semantic-release, pypi-doppler
- **Earthly Docs**: https://docs.earthly.dev/
- **semantic-release Docs**: https://semantic-release.gitbook.io/
- **Pushover API**: https://pushover.net/api
