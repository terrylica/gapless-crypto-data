# ADR-0002: Lychee Link Validation and Broken Link Remediation

## Status

Accepted (2025-01-23)

## Context

### Problem Statement

Link rot in documentation creates poor user experience and maintenance burden:

1. **14 broken internal links** detected by lychee (8% error rate)
   - 4 links to files moved during hub-and-spoke refactoring (Oct 2025)
   - 10 links to missing historical milestone files (v2.2.1, v2.4.x, v2.5.x, etc.)

2. **56 absolute file paths** in documentation
   - Pattern: `~/eon/gapless-crypto-data/docs/...`
   - Not portable across developers, GitHub web UI, or published PyPI documentation
   - Affects: CLAUDE.md (12), docs/architecture/ (19), docs/guides/ (13), docs/validation/ (12)

3. **No automated link validation**
   - Manual link checking is error-prone
   - Documentation changes can introduce broken links unnoticed
   - No CI/CD validation before merge

### Current State

**Lychee tool** already installed locally (v0.21.0 via Homebrew):

- Scan results exist: `.lychee-results.json`, `.lychee-results.txt`
- No configuration file (lychee.toml)
- No .gitignore rules for lychee outputs
- No automated workflow

**Documentation architecture** (post hub-and-spoke refactoring):

- Total: 77+ documentation files (40 markdown, 37 YAML)
- Hub documents: CLAUDE.md, DOCUMENTATION.md, README.md
- Spoke documents: docs/architecture/, docs/guides/, docs/validation/, docs/development/

### Business Impact

**User-facing issues**:

- Broken links in hub documents (DOCUMENTATION.md, CLAUDE.md) create poor first impression
- CLI migration guide links fail for v4.0.0 users
- GitHub web UI broken links reduce documentation credibility

**Developer-facing issues**:

- Absolute paths don't work for other contributors
- AI agents (Claude Code) can't navigate documentation from published package
- PyPI documentation may have broken internal references

### Technical Context

**Recent changes affecting links**:

- Oct 2025: Hub-and-spoke refactoring moved CLI_MIGRATION_GUIDE.md, PUBLISHING.md to docs/development/
- Jan 2025: v4.0.1 release updated CLI removal documentation
- Missing milestones: Patch versions (v2.x.1, v2.x.2) never created or deleted

## Decision

**Implement lychee-based link validation with automated remediation**:

1. **Fix all 14 broken links immediately**
   - Update moved file references (4 links)
   - Remove missing milestone references (10 links)

2. **Standardize on relative paths repository-wide**
   - Convert 56 absolute paths to relative
   - Establish relative path as standard pattern

3. **Configure lychee for ongoing validation**
   - Create lychee.toml with project-specific settings
   - Add lychee outputs to .gitignore
   - Exclude non-critical paths (tmp/, sample_data/)

4. **Document link maintenance policy**
   - Relative paths for all internal links
   - Lychee validation before major documentation changes

### Constraints

**Scope limitations** (user decisions):

- ✅ Check: Core documentation (docs/, README, CLAUDE, CHANGELOG) + config files
- ❌ Exclude: Temporary files (tmp/), sample data metadata (1167 Binance URLs)
- ❌ No CI/CD integration (no GitHub Actions, no pre-commit hooks)

**Policy decisions** (user decisions):

- Missing milestones: Remove all references (not create stubs or redirect)
- Path standard: Convert all absolute paths to relative (not hybrid)
- Lychee setup: Configuration file + .gitignore only (not automation)

## Consequences

### Positive

- **Improved user experience**: All hub document links functional
- **Portability**: Documentation works across developers, GitHub, PyPI
- **Maintainability**: Lychee configuration codifies link checking standards
- **Observability**: Clear baseline (0 broken links) for future validation

### Negative

- **Historical documentation loss**: 10 milestone references removed (v2.2.1, v2.4.x, etc.)
- **Manual validation burden**: No automated CI/CD checking (user decision)
- **One-time effort**: 70 link/path edits across 15+ files

### Neutral

- **Configuration file added**: lychee.toml (single source of truth for link checking)
- **Pattern change**: Absolute → relative paths (requires editor context adjustment)

## Implementation

### Phase 1: Broken Link Fixes (14 fixes)

**Category 1: Moved Files** (4 fixes):

```
DOCUMENTATION.md: docs/CLI_MIGRATION_GUIDE.md → docs/development/CLI_MIGRATION_GUIDE.md
DOCUMENTATION.md: docs/PUBLISHING.md → docs/development/PUBLISHING.md
docs/README.md: PUBLISHING.md → development/PUBLISHING.md
docs/development/CLI_MIGRATION_GUIDE.md: ../docs/examples → ../../examples/
```

**Category 2: Missing Milestones** (10 removals):

```
Remove from DOCUMENTATION.md:
- MILESTONE_v2.2.1.yaml
- MILESTONE_v2.4.1.yaml, v2.4.2.yaml
- MILESTONE_v2.5.1.yaml, v2.5.2.yaml
- MILESTONE_v2.6.2.yaml
- MILESTONE_v2.8.1.yaml, v2.8.2.yaml
- MILESTONE_v2.10.1.yaml
- MILESTONE_v2.13.0.yaml
```

### Phase 2: Path Standardization (56 conversions)

**Files affected** (12 files):

- CLAUDE.md: 12 absolute paths
- docs/architecture/OVERVIEW.md: 11 paths
- docs/guides/python-api.md: 6 paths
- docs/architecture/DATA_FORMAT.md: 5 paths
- docs/guides/DATA_COLLECTION.md: 5 paths
- docs/validation/OVERVIEW.md: 6 paths
- docs/development/SETUP.md: 4 paths
- docs/development/COMMANDS.md: 3 paths
- docs/development/CLI_MIGRATION_GUIDE.md: 2 paths
- docs/validation/STORAGE.md: 2 paths
- docs/validation/QUERY_PATTERNS.md: 2 paths

**Conversion logic**:

- From project root (CLAUDE.md): `/Users/.../docs/X.md` → `./docs/X.md`
- From docs/architecture/: `/Users/.../docs/X.md` → `../X.md`
- From docs/guides/: `/Users/.../docs/X.md` → `../X.md`

### Phase 3: Lychee Configuration

**lychee.toml**:

- Scope: markdown, YAML, HTML files
- Exclusions: tmp/, sample_data/, social media domains
- Cache: 7-day max age
- Output: .lychee-results.md

**.gitignore additions**:

```
.lycheecache
.lychee-results.txt
.lychee-results.json
.lychee-results.md
```

### Validation

**Pre-fix baseline**: `lychee --format json . > baseline.json` (expect 14 errors)
**Post-fix verification**: `lychee --format detailed .` (expect 0 errors)

## References

- **Link Checker Tool**: [Lychee GitHub](https://github.com/lycheeverse/lychee)
- **Lychee Documentation**: https://lychee.cli.rs/
- **Plan**: docs/plan/0002-lychee-link-validation/plan.md
- **Related**: ADR-0001 (Repository Split) - caused CLI_MIGRATION_GUIDE.md move

---

**Decision Date**: 2025-01-23
**Implemented By**: Lychee link validation and automated remediation
