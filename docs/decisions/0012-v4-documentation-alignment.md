# ADR-0012: v4.0.0 Documentation Alignment

## Status

Accepted (2025-01-22)

## Context

### Problem Statement

Comprehensive documentation audit revealed critical misalignment between documentation and v4.0.0 implementation:

1. **Canonical architecture document outdated**: `docs/CURRENT_ARCHITECTURE_STATUS.yaml` describes v3.0.0 with 3 dependencies, missing ClickHouse/DuckDB database layer
2. **CLI migration guide uses future tense**: Describes CLI removal as future event when already completed in v4.0.0
3. **Sample data metadata version lag**: All sample files report v2.10.0 generator version vs current v4.0.0

**Current State**:

- **pyproject.toml**: v4.0.0, 7 dependencies (clickhouse-driver, duckdb, httpx, pandas, pydantic, pyarrow, python-dotenv), no CLI
- **CURRENT_ARCHITECTURE_STATUS.yaml**: Claims v3.0.0, 3 dependencies, CLI "PRODUCTION_READY", no database layer
- **CLI_MIGRATION_GUIDE.md**: "CLI will be removed in v4.0.0" (future tense)
- **Sample metadata**: All files show "version": "v2.10.0"

### Impact

**Availability**: AI agents and developers receive incorrect architecture information from canonical reference
**Correctness**: Documentation contradicts implementation (CLI status, dependency count, database layer)
**Maintainability**: Outdated canonical reference cascades errors to dependent documentation
**Observability**: Version metadata in sample data does not reflect current system state

### Constraints

1. **Doc-as-code discipline**: ADR ↔ plan ↔ code synchronization mandatory
2. **Canonical reference integrity**: CURRENT_ARCHITECTURE_STATUS.yaml must be single source of truth
3. **No promotional language**: Documentation describes capabilities without superlatives
4. **Intent over implementation**: Focus on what/why, not how
5. **Backward compatibility**: Not required (v4.0.0 is breaking change)

## Decision

Update all documentation to accurately reflect v4.0.0 implementation:

### 1. Update CURRENT_ARCHITECTURE_STATUS.yaml

**Changes**:
- Version: v3.0.0 → v4.0.0
- Database layer: Add ClickHouse (primary storage) and DuckDB (validation persistence)
- Dependencies: 3 → 7 (add clickhouse-driver, duckdb, pydantic, python-dotenv)
- CLI interface: Remove "PRODUCTION_READY" status, document removal in v4.0.0
- Removed concepts: Update to reflect v4.0.0 changes

**Rationale**: Canonical reference must reflect current reality, not historical state

### 2. Update CLI_MIGRATION_GUIDE.md

**Changes**:
- Tense: Future → past ("will be removed" → "was removed")
- Timeline: Update v4.0.0 from "2025 Q2" to "Released"
- Warning banner: Update to reflect completed migration

**Rationale**: Guide serves users migrating from v3.x; must accurately describe v4.0.0 state

### 3. Document Sample Data Metadata Versioning Policy

**Changes**:
- Add `docs/architecture/SAMPLE_DATA_POLICY.md`
- Document version freeze at v2.10.0 for sample data
- Explain sample data serves as test fixtures, not current generator output

**Rationale**: Clarify intentional version lag vs unintentional staleness

## Consequences

### Positive

- **Correctness**: Documentation matches implementation
- **Maintainability**: Single source of truth for v4.0.0 architecture
- **Observability**: Clear versioning policy for all artifacts
- **Developer experience**: AI agents receive accurate architecture information

### Negative

- **Documentation churn**: Updates cascade to dependent documents
- **Historical discontinuity**: v3.0.0 architecture description lost (mitigated by git history)

### Neutral

- **Sample data unchanged**: Intentional v2.10.0 freeze documented as policy

## Implementation

See: `docs/plan/0012-v4-documentation-alignment/plan.md`

## References

- Audit report: Generated 2025-01-22 via mdfind-based documentation search
- Current implementation: pyproject.toml v4.0.0
- Canonical reference: docs/CURRENT_ARCHITECTURE_STATUS.yaml (to be updated)
- CLI migration: docs/development/CLI_MIGRATION_GUIDE.md
