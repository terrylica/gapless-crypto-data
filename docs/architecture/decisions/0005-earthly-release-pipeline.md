---
status: "accepted"
date: "2025-11-25"
decision-makers: ["terrylica"]
---

# ADR-0005: Earthly Release-Validation Pipeline with Observability

## Context and Problem Statement

Current CI/CD infrastructure has multiple issues:

1. **Policy Violations**: `ci.yml` and `publish.yml` contain testing/linting (forbidden per CLAUDE.md)
2. **No semantic-release**: Manual versioning and changelog generation
3. **No observability**: No structured release stats or alerting
4. **Deprecated actions**: Using `actions/create-release@v1` (archived)
5. **Duplicate workflows**: `release.yml` and `publish.yml` both build packages
6. **No Earthly**: Missing canonical local-first pipeline

## Decision Drivers

- **Observability SLO**: Release events should produce structured stats and alerts
- **Maintainability SLO**: Single canonical pipeline (Earthly) reduces duplication
- **Correctness SLO**: semantic-release ensures consistent versioning from commits
- **Local-first philosophy**: Quality checks run locally, not in CI

## Considered Options

### Option 1: Earthly + semantic-release + Pushover (SELECTED)

- Earthly as canonical pipeline for local and CI execution
- semantic-release for automated versioning from conventional commits
- Pushover alerts linking to GitHub Release
- GitHub Actions only for release automation (no tests/linting)

### Option 2: Keep Current Workflows

- Fix deprecated actions
- Remove tests from CI
- No Earthly, no semantic-release

### Option 3: GitHub Actions Only

- Consolidate into single workflow
- Add semantic-release GitHub Action
- No Earthly

## Decision Outcome

**Chosen option: Option 1 (Earthly + semantic-release + Pushover)**

Rationale:

- Earthly provides reproducible local-first pipeline
- semantic-release eliminates manual versioning errors
- Pushover alerts provide immediate release visibility
- Aligns with user's explicit requirements

## Consequences

### Positive

- **Observability**: Structured release stats, Pushover notifications
- **Maintainability**: Single Earthfile as source of truth
- **Correctness**: Automated versioning from conventional commits
- **Policy compliance**: No tests/linting in GitHub Actions

### Negative

- **New dependency**: Earthly CLI required for local development
  - _Mitigation_: Simple installation via Homebrew
- **Learning curve**: Team must learn Earthly syntax
  - _Mitigation_: Well-documented Earthfile with comments

### Neutral

- Existing workflows replaced (not extended)
- pypi-doppler skill used for local publishing only

## Implementation

See: `docs/plan/0005-earthly-release-pipeline/plan.md`

**Commit Strategy**:

1. Add Earthfile with release-validation targets
2. Add semantic-release configuration
3. Update GitHub Actions to use Earthly
4. Add Pushover notification integration

**Validation**:

- Local Earthly execution passes
- GitHub Actions workflow succeeds
- Pushover notification received on release

## Links

- **Related ADRs**: ADR-0003 (Repository Housekeeping), ADR-0004 (YAML Audit)
- **Skills**: semantic-release, pypi-doppler
- **Dependencies**: Earthly, semantic-release, curl (Pushover API)
