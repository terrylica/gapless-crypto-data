# Sample Data Versioning Policy

**Status**: Active
**Last Updated**: 2025-01-22
**Canonical Reference**: `docs/CURRENT_ARCHITECTURE_STATUS.yaml`

## Overview

This document explains the versioning policy for sample data files included in the
`gapless-crypto-data` package distribution.

## Policy Statement

**Sample data files are intentionally frozen at v2.10.0 generator version.**

All files in `src/gapless_crypto_data/sample_data/` report `"version": "v2.10.0"` in their
metadata, regardless of the current package version (e.g., v4.0.0). This is intentional and
documented behavior.

## Rationale

### Test Fixture Stability

Sample data serves as test fixtures for:
- Unit tests verifying data ingestion
- Integration tests validating format compatibility
- Documentation examples demonstrating API usage
- Regression tests ensuring backward compatibility

**Changing sample data breaks tests**: Regenerating sample data with new generator versions
creates different hash values, timestamps, and potentially different gap detection results,
causing test failures unrelated to code changes.

### Version Decoupling

Sample data generator version (v2.10.0) is decoupled from package version (v4.0.0) because:

1. **Format stability**: v2.10.0 established the stable 11-column microstructure format
2. **Backward compatibility**: Data format has not changed since v2.10.0
3. **Maintenance overhead**: Regenerating sample data for every package version is unnecessary
4. **Test reliability**: Frozen fixtures prevent spurious test failures

### Generator vs Package Version

- **Generator version** (v2.10.0): Version of `BinancePublicDataCollector` that created the file
- **Package version** (v4.0.0): Current release version of `gapless-crypto-data`

Generator version in metadata reflects the tool version that created the file, not the package
version that distributes it.

## Sample Data Files

All sample data files follow the naming convention:

```
binance_{market}_{symbol}-{timeframe}_{start}-{end}_v{generator_version}.{ext}
```

Example:
```
binance_spot_BTCUSDT-1d_20240101-20240102_v2.10.0.csv
binance_spot_BTCUSDT-1d_20240101-20240102_v2.10.0.metadata.json
```

### Current Sample Data Inventory

- `binance_spot_BTCUSDT-1d_20240101-20240102_v2.10.0.*`
- `binance_spot_BTCUSDT-1h_20240101-20240102_v2.10.0.*`
- `binance_spot_BTCUSDT-5m_20230323-20230325_v2.10.0.*`
- `binance_spot_ETHUSDT-1h_20240101-20240101_v2.10.0.*`

All files were generated with `BinancePublicDataCollector` v2.10.0 and frozen as test fixtures.

## When to Regenerate Sample Data

Sample data should only be regenerated when:

1. **Format change**: 11-column microstructure format is extended or modified
2. **Breaking change**: Data structure requires backward-incompatible changes
3. **Test requirement**: New test cases require different date ranges or symbols

**Do NOT regenerate for**:
- Package version bumps (v4.0.0 → v4.1.0)
- Code refactoring without format changes
- Documentation updates
- Dependency updates

## Regeneration Procedure

If sample data regeneration is required:

1. **Document decision**: Create ADR explaining format change necessity
2. **Update tests**: Modify test expectations for new hash values and timestamps
3. **Regenerate all files**: Use current `BinancePublicDataCollector` to regenerate all samples
4. **Update this document**: Document new generator version and regeneration rationale
5. **Update metadata**: All `.metadata.json` files will reflect new generator version

## Observability

Sample data metadata includes:

- **Generator version**: Version of tool that created the file
- **Generation timestamp**: UTC timestamp when file was created
- **Data hash**: SHA-256 hash for integrity verification
- **Compliance markers**: Format version and validation flags

All metadata is machine-readable and suitable for automated validation.

## References

- ADR-0012: v4.0.0 Documentation Alignment
- Canonical architecture: `docs/CURRENT_ARCHITECTURE_STATUS.yaml`
- Sample data location: `src/gapless_crypto_data/sample_data/`
- Generator implementation: `src/gapless_crypto_data/collectors/binance_public_data_collector.py`
