# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Gapless Crypto Data is a high-performance cryptocurrency data collection tool providing authentic Binance data with zero-gap guarantee. 22x faster than API-only approaches via Binance Public Data Repository (CloudFront CDN).

**Core Capability**: Collect complete historical OHLCV data with microstructure metrics (11-column format) for 13 timeframes (1s to 1d) across 400+ trading pairs.

## Quick Navigation

### Architecture

- [Architecture Overview](./docs/architecture/OVERVIEW.md) - Core components, data flow, SLOs
- [Data Format Specification](./docs/architecture/DATA_FORMAT.md) - 11-column microstructure format

### Usage Guides

- [Data Collection Guide](./docs/guides/DATA_COLLECTION.md) - CLI usage, dual data source strategy, troubleshooting
- [Python API Reference](./docs/guides/python-api.md) - Function-based and class-based APIs, complete examples

### Validation System

- [Validation Overview](./docs/validation/OVERVIEW.md) - 5-layer validation pipeline, DuckDB persistence
- [ValidationStorage Specification](./docs/validation/STORAGE.md) - Database schema, API methods
- [AI Agent Query Patterns](./docs/validation/QUERY_PATTERNS.md) - Common patterns for validation analysis

### Development

- [Development Setup](./docs/development/SETUP.md) - Environment setup, IDE configuration, troubleshooting
- [Development Commands](./docs/development/COMMANDS.md) - Testing, code quality, build, CI/CD
- [CLI Migration Guide](./docs/development/CLI_MIGRATION_GUIDE.md) - v2.x to v3.x migration
- [Publishing Guide](./docs/development/PUBLISHING.md) - PyPI publishing workflow

## SDK Quality Standards

**Primary Use Case**: Programmatic API consumption (`import gapless_crypto_data`) by downstream packages and AI coding agents

**Specification**: [`docs/SDK_QUALITY_STANDARDS.yaml`](./docs/SDK_QUALITY_STANDARDS.yaml) - Machine-readable standards

**Key Abstractions**:

- **Type Safety**: PEP 561 compliance via py.typed marker
- **AI Discoverability**: **probe** module, llms.txt
- **Structured Exceptions**: Machine-parseable error context
- **Coverage Strategy**: SDK entry points (85%+) > Core engines (70%+)

## Network Architecture

**CRITICAL - Empirically Validated (2025-01-19)**: DO NOT modify network implementation

- **Data Source**: AWS S3 + CloudFront CDN (400+ edge locations, 99.99% SLA)
- **Performance**: urllib is 2x faster than httpx for CDN downloads
- **NO connection pooling** (CloudFront uses different edge servers per request)
- **NO retry logic** (CloudFront handles failover, 0% failure rate in production)

**Single improvement worth making**: ETag-based caching for bandwidth optimization

## Authentication

**No authentication required** for primary data collection (public Binance data repository). Gap filling uses public Binance API endpoints (rate-limited but no auth required).

## Current Architecture

**Version**: v4.0.1 (validation v3.3.0+ with DuckDB persistence)

**Canonical Reference**: `docs/CURRENT_ARCHITECTURE_STATUS.yaml`

**Production-Ready**: Core collection, intelligent resume (JSON checkpointing), CSV and Parquet output formats, zero-gap guarantee via dual-source validation
