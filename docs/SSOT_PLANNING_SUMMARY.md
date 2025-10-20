# Single Source of Truth (SSoT) Documentation Architecture Planning

**Status**: Planning Phase
**Effective Date**: 2025-10-20
**Version**: 1.0.0

---

## Overview

This document summarizes the plan to reorganize project documentation using Link Farm + Hub-and-Spoke architecture with Progressive Disclosure.

**Current State**: CLAUDE.md is 476 lines, mixing essentials with detailed technical content
**Target State**: CLAUDE.md becomes a 50-70 line navigation hub with links to detailed spoke documents

---

## Executive Summary

### The Problem
- CLAUDE.md tries to be comprehensive, but becomes difficult to maintain
- Updates to one section require editing a massive monolithic file
- No clear version tracking for different topics
- New users can't find what they need quickly
- No progressive disclosure (essentials → deep dives)

### The Solution
1. **Hub (CLAUDE.md)**: 50-70 line navigation hub with links to spokes
2. **Spokes**: Detailed specification documents organized by topic
3. **Progressive Disclosure**: Essentials → Quick Start → Guides → Implementation Details
4. **Version Tracking**: Each spoke has independent version numbers
5. **Single Source of Truth**: One document per topic, clear ownership

---

## Documentation Architecture

### Current Mixture in CLAUDE.md

The following topics are currently mixed into CLAUDE.md (476 lines):

| Topic | Lines | Should Be | Target Spoke |
|-------|-------|-----------|---------------|
| Architecture Overview | ~30 | Essential | docs/architecture/OVERVIEW.md |
| Core Components | ~10 | Reference | docs/architecture/CORE_COMPONENTS.md |
| Data Format | ~5 | Reference | docs/architecture/DATA_FORMAT.md |
| Network Architecture | ~20 | Reference | docs/architecture/network.md |
| Development Setup | ~10 | Reference | docs/development/SETUP.md |
| Testing Commands | ~15 | Reference | docs/development/COMMANDS.md |
| Data Collection Patterns | ~30 | Guide | docs/guides/DATA_COLLECTION.md |
| Python API Examples | ~50 | Guide | docs/guides/python-api.md |
| Validation Architecture | ~150 | Detailed Spec | docs/validation/OVERVIEW.md |
| Other (CLI, auth, etc) | ~75 | Mixed | Various spokes |

### Proposed Hub Structure (CLAUDE.md - 50-70 lines)

```markdown
# CLAUDE.md

## Project Overview
- 1-sentence description
- 3-5 key value propositions
- Link to README.md

## Quick Start
- Installation (UV)
- Installation (pip)
- Basic Python example
- Links to docs/api/quick-start.md

## Navigation Hub (Spokes)
- Architecture & Design
- Data Collection
- Gap Filling
- Validation & Quality
- API Reference
- Development
- Publishing & Releases

## Development (Quick Reference)
- Essential commands
- Link to docs/development/COMMANDS.md
```

### Proposed Spoke Categories

#### 1. Architecture & Design (`docs/architecture/`)
- **OVERVIEW.md** - High-level system design, data flow
- **CORE_COMPONENTS.md** - Detailed component specifications
- **DATA_FORMAT.md** - 11-column microstructure format
- **network.md** - Network architecture, CDN optimization

#### 2. Data Collection (`docs/guides/`)
- **DATA_COLLECTION.md** - Collection workflow, symbols, timeframes
- **python-api.md** - API usage patterns and examples

#### 3. Gap Filling (`docs/guides/`)
- **GAP_FILLING.md** - Detection algorithm, filling operations

#### 4. Validation & Quality (`docs/validation/`)
- **OVERVIEW.md** - Validation pipeline, DuckDB architecture
- **STORAGE.md** - ValidationStorage specification, schema
- **QUERY_PATTERNS.md** - SQL queries, AI agent patterns

#### 5. API Reference (`docs/api/`)
- **quick-start.md** - (Already exists, enhance)
- **reference.md** - Complete function reference

#### 6. Development (`docs/development/`)
- **SETUP.md** - Environment setup
- **COMMANDS.md** - Complete command reference
- **TESTING.md** - Testing strategy and patterns

---

## Progressive Disclosure Levels

### Level 1: Essentials (CLAUDE.md)
- Project purpose (1-2 sentences)
- Core features (3-5 bullets)
- Quick start (2-3 code examples)
- Navigation links to detailed docs
- **Audience**: New users, quick reference
- **Target Readers**: Minutes to scan

### Level 2: Quick Start (docs/api/quick-start.md)
- Installation instructions
- Basic usage examples
- Common use cases
- Links to detailed guides
- **Audience**: Users wanting immediate utility
- **Target Readers**: 5-10 minutes

### Level 3: Detailed Guides (docs/guides/, docs/architecture/)
- Complete workflows
- Configuration options
- Edge cases and error handling
- Performance characteristics
- **Audience**: Power users, integrators
- **Target Readers**: 30-60 minutes

### Level 4: Implementation Details (docs/architecture/CORE_COMPONENTS.md)
- Component design rationale
- Algorithm descriptions
- Optimization opportunities
- **Audience**: Contributors, maintainers
- **Target Readers**: 1-2 hours

### Level 5: Research & Analysis (docs/research/)
- Performance benchmarks
- Design trade-off studies
- Future optimization paths
- **Audience**: Researchers, architects
- **Target Readers**: 2+ hours

---

## Version Tracking Strategy

### Hub Version (CLAUDE.md)

```markdown
<!-- Version: v1.0.0 (2025-10-20) -->
```

**Increment Rules**:
- **PATCH**: Link target changes, typo fixes
- **MINOR**: New navigation link, new spoke category
- **MAJOR**: Restructuring spoke organization

### Spoke Versioning

Each spoke document includes version header:

```yaml
---
version: "1.0.0"
last_updated: "2025-10-20"
canonical_source: true
supersedes: []
---
```

**Properties**:
- `version`: Semantic version (MAJOR.MINOR.PATCH)
- `last_updated`: ISO 8601 date
- `canonical_source`: Is this the authoritative source?
- `supersedes`: Previous versions this replaces

---

## Language & Tone Standards

### Principle
Neutral, technical language. No promotional or marketing terms.

### Prohibited Terms

| Prohibited | Use Instead |
|-----------|------------|
| "enhanced" | "improved" or "added" |
| "production-graded" | "production-ready" |
| "corrected" | "fixed" |
| "state-of-the-art (SOTA)" | specific capability name |
| "innovative" | describe what it does |
| "intelligent" | describe the algorithm |

### Approved Terms
- "fast", "faster", "fastest" (with benchmarks)
- "efficient" (with metrics)
- "reliable", "robust" (with test coverage %)
- "atomic", "transaction", "ACID" (technical terms)
- "zero-gap guarantee" (measurable property)
- "22x faster than API" (with measurement context)

---

## Implementation Roadmap

### Phase 1: Planning (Current - 1 week)
- ✅ Survey project structure
- ✅ Sample documentation patterns
- ✅ Create SSoT planning (THIS DOCUMENT)
- [ ] Identify gaps and opportunities

### Phase 2: Spoke Creation (1-2 weeks)
- Create directory structure
- Extract content from CLAUDE.md
- Add version headers
- Add cross-links between spokes

### Phase 3: Hub Reorganization (3-5 days)
- Reduce CLAUDE.md to 50-70 lines
- Convert to navigation hub
- Create spoke links
- Test all references

### Phase 4: Validation (3-5 days)
- Verify all links resolve
- Check for dead references
- Test progressive disclosure
- Update scripts that reference docs

### Phase 5: Publishing (1-2 days)
- Update pyproject.toml URLs
- Update GitHub organization settings
- Announce documentation restructuring

---

## Success Metrics

- [ ] CLAUDE.md reduced from 476 → 50-70 lines
- [ ] All detailed topics have dedicated spoke documents
- [ ] 100% of CLAUDE.md content moved to appropriate spoke
- [ ] All spokes have version tracking
- [ ] Zero broken links in documentation
- [ ] Progressive disclosure tested with new users
- [ ] Language audit completed (no promotional terms)
- [ ] All spokes linked from CLAUDE.md hub

---

## Current Documentation Audit

### Existing Documents (Good State)
- ✅ `docs/README.md` - Navigation guide
- ✅ `README.md` (project root) - Marketing overview
- ✅ `docs/CURRENT_ARCHITECTURE_STATUS.yaml` - Architecture source
- ✅ `docs/CLI_MIGRATION_GUIDE.md` - CLI changes
- ✅ `docs/PUBLISHING.md` - Publishing guide
- ✅ `docs/milestones/` - Release history
- ✅ `docs/diagrams/` - Architecture diagrams

### Documents Needing Reorganization
- ⚠️ `CLAUDE.md` - Too comprehensive, needs hub conversion
- ⚠️ Various scattered API docs - Need consolidation

---

## Maintenance Strategy

### Hub Maintenance (CLAUDE.md)
- **Frequency**: Quarterly review minimum
- **Process**: Review for outdated links, add new spokes if needed
- **Versioning**: Semantic version in header comment

### Spoke Maintenance
- **Frequency**: When content changes
- **Process**: Update content, increment version, update timestamp
- **Commits**: `docs: update [spoke-name] (v[version])`

### Link Validation
- **Frequency**: Monthly
- **Process**: Run link checker, fix broken references

### Language Audit
- **Frequency**: Quarterly
- **Process**: Search for prohibited terms, verify neutrality

---

## Reference Documents

- **Full Specification**: `docs/SSOT_DOCUMENTATION_ARCHITECTURE.yaml` (OpenAPI format with x-* extensions)
- **This Summary**: `docs/SSOT_PLANNING_SUMMARY.md` (Current document)

---

## Next Steps

1. **Review & Approval** (This week)
   - Review plan with team
   - Gather feedback
   - Make adjustments

2. **Phase 2 Begin** (Next week)
   - Create directory structure
   - Start extracting and organizing content

3. **Communicate Plan** (Ongoing)
   - Update project documentation status
   - Announce timeline to users

---

## Questions & Considerations

- Should we keep CLAUDE.md as-is during transition, with deprecation notice?
- How should we handle cross-project references to CLAUDE.md sections?
- What's the threshold for creating a new spoke vs. expanding existing one?
- Should spoke documents be part of PyPI published docs?

---

**Created**: 2025-10-20
**Last Updated**: 2025-10-20
**Version**: 1.0.0
