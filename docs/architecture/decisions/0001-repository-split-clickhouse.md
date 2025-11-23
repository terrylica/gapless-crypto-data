# ADR-0001: Repository Split for ClickHouse Implementation

## Status

Implemented (2025-01-22)

## Context

### Problem Statement

The ClickHouse database integration represents a fundamentally different architecture from the file-based CSV collection approach:

1. **File-based (v3.x)**: Simple CSV output, no database, minimal dependencies, Python 3.9-3.13
2. **Database-first (v4.x)**: ClickHouse primary storage, DuckDB validation, Python 3.12+ only, CLI removed

These approaches serve different use cases and maintaining both in a single repository creates:

- **Version confusion**: v3.x users don't need ClickHouse dependencies
- **Maintenance overhead**: Different test suites, deployment workflows, documentation
- **Breaking changes**: v4.0.0 breaks backward compatibility extensively

### Initial Approach Attempted

Initially attempted to publish v4.0.0 with ClickHouse to PyPI as `gapless-crypto-data`:

- Created main-clickhouse branch
- Published v4.0.0 to PyPI (2025-01-22)
- Created GitHub release and tag

**Problem identified**: This creates confusion for existing v3.x users and mixes two incompatible architectures in a single package namespace.

## Decision

**Split ClickHouse implementation into separate repository**: `gapless-crypto-clickhouse`

### Repository Allocation

- **gapless-crypto-data** (this repo): File-based CSV collection (v3.x)
  - Continue v3.x development
  - No ClickHouse dependencies
  - Python 3.9-3.13 support
  - CLI remains available

- **gapless-crypto-clickhouse** (new repo): Database-first ClickHouse implementation
  - Location: `~/eon/gapless-crypto-clickhouse`
  - Independent version lifecycle starting from v1.0.0
  - ClickHouse + DuckDB dependencies
  - Python 3.12+ only
  - No CLI (programmatic API only)

### Cleanup Actions

1. **PyPI v4.0.0**: Yank from PyPI (published in error with ClickHouse references)
2. **GitHub v4.0.0 tag/release**: Delete (removed 2025-01-22)
3. **main-clickhouse branch**: Delete from remote (removed 2025-01-22)
4. **This repository**: Remain at v3.3.0, continue file-based development

## Consequences

### Positive

- **Clear separation**: Users choose file-based vs database-first approach
- **Independent evolution**: Each repository evolves at its own pace
- **No breaking changes**: v3.x users unaffected by ClickHouse development
- **Simpler dependencies**: File-based repo remains lightweight

### Negative

- **Duplicate code**: Some utilities duplicated across repositories
- **Multiple packages**: Users need to know which package to use
- **Documentation split**: Must maintain two sets of documentation

### Neutral

- **Version reset**: gapless-crypto-clickhouse starts at v1.0.0
- **Package discovery**: Both packages discoverable via PyPI search

## Implementation

### Completed (2025-01-22)

- ✅ Created `~/eon/gapless-crypto-clickhouse` repository
- ✅ Deleted v4.0.0 tag and GitHub release from gapless-crypto-data
- ✅ Deleted main-clickhouse branch from remote
- ✅ Switched gapless-crypto-data back to main branch (v3.3.0)

### Pending

- [ ] Yank v4.0.0 from PyPI (requires web interface authentication)
- [ ] Update gapless-crypto-data README to link to gapless-crypto-clickhouse
- [ ] Document in gapless-crypto-clickhouse that it supersedes v4.0.0

## References

- **Separate Repository**: ~/eon/gapless-crypto-clickhouse
- **Erroneous Release**: PyPI gapless-crypto-data v4.0.0 (to be yanked)
- **This Repository**: gapless-crypto-data (file-based v3.x)

---

**Decision Date**: 2025-01-22
**Implemented By**: Repository reorganization and cleanup
