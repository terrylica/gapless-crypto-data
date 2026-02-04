# Futures Support Design

**Date:** 2026-02-05
**Status:** Draft
**Related Issue:** https://github.com/EonLabs-Spartan/alpha-forge/issues/128

## Summary

Add support for Binance USDT-M Futures to gapless-crypto-data, enabling 10-100x faster data loading for futures backtesting in Alpha Forge.

## Goals

- Support USDT-M futures from Binance Vision (`futures` as alias for `um`)
- Require explicit market type selection (no default - breaking change)
- Minimal API surface change (single new required parameter)
- Reuse existing gap detection/filling infrastructure

## Non-Goals

- Coin-M (CM) futures support (can add later if needed)
- Symbol validation per market type (let Binance be source of truth)
- Maintaining symbol lists (deprecated `get_supported_symbols()`)
- Supporting other exchanges (Binance only)

---

## Design Decisions

| Decision | Choice | Rationale |
|----------|--------|-----------|
| API parameter | `market_type` (required, no default) | Forces explicit choice, clearer intent |
| Market type values | `"spot"`, `"futures"` | Simple; `futures` = USDT-M (most common) |
| URL construction | Enum with `base_path` property | Type-safe, extensible |
| Filename convention | `binance_{market_type}_SYMBOL-...` | Clear, consistent |
| Symbol validation | None | Symbol lists change frequently |
| fill_gaps() behavior | Auto-detect from filename | Convenient, with explicit override |
| get_supported_symbols() | Deprecated | No validation means no need for lists |
| Breaking change handling | Major version bump to 6.0.0 | Clear migration path |

---

## Implementation

### 1. Core Data Types

**New file: `src/gapless_crypto_data/market_types.py`**

```python
from enum import Enum

class MarketType(str, Enum):
    """Binance market types supported by gapless-crypto-data."""

    SPOT = "spot"
    FUTURES = "futures"  # USDT-M perpetual futures (alias for "um")

    @property
    def base_path(self) -> str:
        """Return the Binance Vision URL path segment."""
        if self == MarketType.SPOT:
            return "spot"
        return "futures/um"  # USDT-M futures

    @property
    def filename_prefix(self) -> str:
        """Return prefix for output filenames."""
        return f"binance_{self.value}_"
```

### 2. HybridUrlGenerator Changes

**File: `src/gapless_crypto_data/collectors/hybrid_url_generator.py`**

```python
def __init__(
    self,
    daily_lookback_days: int = 30,
    market_type: MarketType,  # REQUIRED - no default
    max_concurrent_per_batch: int = 13,
):
    self.daily_lookback_days = daily_lookback_days
    self.market_type = market_type
    self.max_concurrent_per_batch = max_concurrent_per_batch

    # Compute base_url from market_type
    self.base_url = f"https://data.binance.vision/data/{market_type.base_path}"

    self.cutoff_date = datetime.now() - timedelta(days=daily_lookback_days)
```

URL generation methods remain unchanged - they already use `self.base_url`.

### 3. BinancePublicDataCollector Changes

**File: `src/gapless_crypto_data/collectors/binance_public_data_collector.py`**

```python
def __init__(
    self,
    symbol: str = "BTCUSDT",
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    market_type: MarketType,  # REQUIRED - no default
    ...
):
    self.symbol = symbol
    self.market_type = market_type

    # Compute base_url from market_type
    self.base_url = f"https://data.binance.vision/data/{market_type.base_path}/monthly/klines"
```

**Metadata generation:** `metadata["market_type"] = self.market_type.value`

**Filename generation:** `f"{self.market_type.filename_prefix}{self.symbol}-{timeframe}_..."`

### 4. API Layer Changes

**File: `src/gapless_crypto_data/api.py`**

```python
def fetch_data(
    symbol: str,
    market_type: str,  # REQUIRED - no default
    timeframe: str = "1h",
    limit: Optional[int] = None,
    start: Optional[str] = None,
    end: Optional[str] = None,
    output_dir: Optional[str] = None,
    auto_fill_gaps: bool = True,
    ...
) -> pd.DataFrame:
    """
    Fetch OHLCV data from Binance.

    Args:
        symbol: Trading pair (e.g., "BTCUSDT")
        market_type: Market type - "spot" or "futures" (USDT-M). REQUIRED.
        timeframe: Candlestick interval (default: "1h")

    Raises:
        TypeError: If market_type is not provided
        ValueError: If market_type is not "spot" or "futures"
    """
    if market_type is None:
        raise TypeError("market_type is required. Use 'spot' or 'futures'.")

    market_type_enum = MarketType(market_type)

    collector = BinancePublicDataCollector(
        symbol=symbol,
        market_type=market_type_enum,
        ...
    )
```

Same pattern for `download()`.

### 5. Gap Filling Changes

```python
def _detect_market_type_from_filename(filename: str) -> Optional[MarketType]:
    """Parse market type from filename pattern: binance_{market_type}_..."""
    for market_type in MarketType:
        if f"binance_{market_type.value}_" in filename:
            return market_type
    return None

def fill_gaps(
    directory: Optional[str] = None,
    symbols: Optional[List[str]] = None,
    market_type: Optional[str] = None,  # Optional - auto-detects from filename
) -> dict:
    # Auto-detect from filename, use override if provided
    # Raises error if cannot detect and no override provided
```

---

## Breaking Changes & Migration

### What Breaks

```python
# OLD (v5.x) - worked with implicit spot
fetch_data(symbol="BTCUSDT", timeframe="1h")

# NEW (v6.0) - requires explicit market_type
fetch_data(symbol="BTCUSDT", market_type="spot", timeframe="1h")
```

### Migration Path

1. **Version bump**: `5.x.x` → `6.0.0`
2. **Clear error message**: `TypeError: market_type is required. Use 'spot' or 'futures'.`
3. **Alpha Forge updates**: Update all plugins using gapless-crypto-data to pass explicit `market_type="spot"`

### Alpha Forge Plugins to Update

| Plugin | Change |
|--------|--------|
| `pypi_gapless_crypto_data_binance_spot` | Add `market_type="spot"` to fetch_data call |

---

## Test Plan

**New tests:**
- `test_market_types.py` - MarketType enum behavior
- URL generation tests for spot/futures paths
- Filename prefix tests
- Test that missing market_type raises TypeError

**Updated tests:**
- Add `market_type` parameter to ALL existing collector tests
- Test `fetch_data(market_type="futures")`
- Test auto-detection from filename in gap filler

**Integration test:**
```python
@pytest.mark.integration
def test_fetch_futures_data():
    df = fetch_data(
        symbol="BTCUSDT",
        market_type="futures",
        timeframe="1d",
        start="2024-01-01",
        end="2024-01-07"
    )
    assert len(df) > 0
```

---

## Files Changed

| File | Change Type | Estimated Lines |
|------|-------------|-----------------|
| `market_types.py` | New | ~20 |
| `hybrid_url_generator.py` | Modify | ~15 |
| `binance_public_data_collector.py` | Modify | ~30 |
| `api.py` | Modify | ~50 |
| `__init__.py` | Modify | ~10 |
| Tests | New + Modify | ~150 |
| **Total** | | **~275** |

---

## Usage Examples

**Fetch USDT-M Futures:**
```python
from gapless_crypto_data import fetch_data

df = fetch_data(
    symbol="BTCUSDT",
    market_type="futures",
    timeframe="1h",
    start="2024-01-01",
    end="2024-12-31"
)
```

**Fetch Spot data:**
```python
df = fetch_data(
    symbol="BTCUSDT",
    market_type="spot",
    timeframe="1h",
    start="2024-01-01",
    end="2024-12-31"
)
```

---

## Rollout Plan

1. Implement changes in feature branch of gapless-crypto-data
2. Run full test suite including integration tests
3. Create PR to gapless-crypto-data
4. After merge, release version **6.0.0** (breaking change)
5. Update Alpha Forge:
   - Update `pypi_gapless_crypto_data_binance_spot` to pass `market_type="spot"`
   - Create new plugin `pypi_gapless_crypto_data_binance_futures`
   - Update gapless-crypto-data dependency to `>=6.0.0`

---

## Open Questions

None - all design decisions resolved.
