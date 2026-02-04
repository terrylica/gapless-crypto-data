# Futures Support Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Add required `market_type` parameter to gapless-crypto-data, supporting "spot" and "futures" (USDT-M) markets.

**Architecture:** Add `MarketType` enum, thread it through URL generator → collector → API layer. Breaking change requires v6.0.0.

**Tech Stack:** Python 3.9+, pytest, pandas

---

## Task 1: Create MarketType Enum

**Files:**
- Create: `src/gapless_crypto_data/market_types.py`
- Test: `tests/test_market_types.py`

**Step 1: Write the failing test**

Create `tests/test_market_types.py`:

```python
"""Tests for MarketType enum."""

import pytest

from gapless_crypto_data.market_types import MarketType


class TestMarketType:
    """Tests for MarketType enum and properties."""

    def test_spot_value(self):
        """Spot market type has correct string value."""
        assert MarketType.SPOT.value == "spot"

    def test_futures_value(self):
        """Futures market type has correct string value."""
        assert MarketType.FUTURES.value == "futures"

    def test_spot_base_path(self):
        """Spot market returns 'spot' base path."""
        assert MarketType.SPOT.base_path == "spot"

    def test_futures_base_path(self):
        """Futures market returns 'futures/um' base path."""
        assert MarketType.FUTURES.base_path == "futures/um"

    def test_spot_filename_prefix(self):
        """Spot market has correct filename prefix."""
        assert MarketType.SPOT.filename_prefix == "binance_spot_"

    def test_futures_filename_prefix(self):
        """Futures market has correct filename prefix."""
        assert MarketType.FUTURES.filename_prefix == "binance_futures_"

    def test_string_conversion_spot(self):
        """Can create MarketType from 'spot' string."""
        assert MarketType("spot") == MarketType.SPOT

    def test_string_conversion_futures(self):
        """Can create MarketType from 'futures' string."""
        assert MarketType("futures") == MarketType.FUTURES

    def test_invalid_market_type_raises(self):
        """Invalid market type raises ValueError."""
        with pytest.raises(ValueError):
            MarketType("invalid")
```

**Step 2: Run test to verify it fails**

```bash
cd /Users/james/dev/gapless-crypto-data && uv run pytest tests/test_market_types.py -v
```

Expected: FAIL with `ModuleNotFoundError: No module named 'gapless_crypto_data.market_types'`

**Step 3: Write minimal implementation**

Create `src/gapless_crypto_data/market_types.py`:

```python
"""Market type definitions for Binance data sources."""

from enum import Enum


class MarketType(str, Enum):
    """Binance market types supported by gapless-crypto-data.

    Attributes:
        SPOT: Binance spot market data
        FUTURES: Binance USDT-M perpetual futures data

    Examples:
        >>> MarketType.SPOT.base_path
        'spot'
        >>> MarketType.FUTURES.base_path
        'futures/um'
        >>> MarketType("futures") == MarketType.FUTURES
        True
    """

    SPOT = "spot"
    FUTURES = "futures"

    @property
    def base_path(self) -> str:
        """Return the Binance Vision URL path segment.

        Returns:
            URL path segment for this market type.

        Examples:
            >>> MarketType.SPOT.base_path
            'spot'
            >>> MarketType.FUTURES.base_path
            'futures/um'
        """
        if self == MarketType.SPOT:
            return "spot"
        return "futures/um"

    @property
    def filename_prefix(self) -> str:
        """Return prefix for output filenames.

        Returns:
            Filename prefix string.

        Examples:
            >>> MarketType.SPOT.filename_prefix
            'binance_spot_'
            >>> MarketType.FUTURES.filename_prefix
            'binance_futures_'
        """
        return f"binance_{self.value}_"
```

**Step 4: Run test to verify it passes**

```bash
cd /Users/james/dev/gapless-crypto-data && uv run pytest tests/test_market_types.py -v
```

Expected: All 9 tests PASS

**Step 5: Commit**

```bash
cd /Users/james/dev/gapless-crypto-data && git add src/gapless_crypto_data/market_types.py tests/test_market_types.py && git commit -m "feat: add MarketType enum with spot and futures support"
```

---

## Task 2: Update HybridUrlGenerator

**Files:**
- Modify: `src/gapless_crypto_data/collectors/hybrid_url_generator.py`
- Test: `tests/test_hybrid_url_generator.py` (create new)

**Step 1: Write the failing test**

Create `tests/test_hybrid_url_generator.py`:

```python
"""Tests for HybridUrlGenerator market type support."""

import pytest
from datetime import datetime

from gapless_crypto_data.collectors.hybrid_url_generator import HybridUrlGenerator
from gapless_crypto_data.market_types import MarketType


class TestHybridUrlGeneratorMarketType:
    """Tests for market_type parameter in HybridUrlGenerator."""

    def test_spot_base_url(self):
        """Spot market type generates correct base URL."""
        generator = HybridUrlGenerator(market_type=MarketType.SPOT)
        assert generator.base_url == "https://data.binance.vision/data/spot"

    def test_futures_base_url(self):
        """Futures market type generates correct base URL."""
        generator = HybridUrlGenerator(market_type=MarketType.FUTURES)
        assert generator.base_url == "https://data.binance.vision/data/futures/um"

    def test_market_type_required(self):
        """market_type parameter is required (no default)."""
        with pytest.raises(TypeError):
            HybridUrlGenerator()  # Missing required market_type

    def test_spot_monthly_url_generation(self):
        """Spot market generates correct monthly klines URL."""
        generator = HybridUrlGenerator(market_type=MarketType.SPOT)
        tasks = generator.generate_download_tasks(
            symbol="BTCUSDT",
            timeframe="1h",
            start_date=datetime(2023, 1, 1),
            end_date=datetime(2023, 1, 31),
        )
        # Check first task URL contains spot path
        assert "/spot/monthly/klines/BTCUSDT/1h/" in tasks[0].url

    def test_futures_monthly_url_generation(self):
        """Futures market generates correct monthly klines URL."""
        generator = HybridUrlGenerator(market_type=MarketType.FUTURES)
        tasks = generator.generate_download_tasks(
            symbol="BTCUSDT",
            timeframe="1h",
            start_date=datetime(2023, 1, 1),
            end_date=datetime(2023, 1, 31),
        )
        # Check first task URL contains futures/um path
        assert "/futures/um/monthly/klines/BTCUSDT/1h/" in tasks[0].url
```

**Step 2: Run test to verify it fails**

```bash
cd /Users/james/dev/gapless-crypto-data && uv run pytest tests/test_hybrid_url_generator.py -v
```

Expected: FAIL - tests fail because market_type parameter doesn't exist yet

**Step 3: Write minimal implementation**

Modify `src/gapless_crypto_data/collectors/hybrid_url_generator.py`:

At the top, add import:
```python
from gapless_crypto_data.market_types import MarketType
```

Modify `__init__` method (around line 84-100):

```python
def __init__(
    self,
    market_type: MarketType,  # REQUIRED - no default
    daily_lookback_days: int = 30,
    max_concurrent_per_batch: int = 13,
):
    """
    Initialize hybrid URL generator with configuration.

    Args:
        market_type: Market type (MarketType.SPOT or MarketType.FUTURES). REQUIRED.
        daily_lookback_days: Number of days to use daily files for recent data
        max_concurrent_per_batch: Maximum concurrent downloads per batch (13 for ZIP files)
    """
    self.market_type = market_type
    self.daily_lookback_days = daily_lookback_days
    self.max_concurrent_per_batch = max_concurrent_per_batch

    # Compute base_url from market_type
    self.base_url = f"https://data.binance.vision/data/{market_type.base_path}"

    # Calculate cutoff date for monthly vs daily strategy
    self.cutoff_date = datetime.now() - timedelta(days=daily_lookback_days)
```

**Step 4: Run test to verify it passes**

```bash
cd /Users/james/dev/gapless-crypto-data && uv run pytest tests/test_hybrid_url_generator.py -v
```

Expected: All 5 tests PASS

**Step 5: Commit**

```bash
cd /Users/james/dev/gapless-crypto-data && git add src/gapless_crypto_data/collectors/hybrid_url_generator.py tests/test_hybrid_url_generator.py && git commit -m "feat: add market_type parameter to HybridUrlGenerator"
```

---

## Task 3: Update BinancePublicDataCollector

**Files:**
- Modify: `src/gapless_crypto_data/collectors/binance_public_data_collector.py`
- Test: `tests/test_binance_collector_market_type.py` (create new)

**Step 1: Write the failing test**

Create `tests/test_binance_collector_market_type.py`:

```python
"""Tests for BinancePublicDataCollector market type support."""

import pytest

from gapless_crypto_data.collectors.binance_public_data_collector import (
    BinancePublicDataCollector,
)
from gapless_crypto_data.market_types import MarketType


class TestBinanceCollectorMarketType:
    """Tests for market_type parameter in BinancePublicDataCollector."""

    def test_spot_base_url(self):
        """Spot market type sets correct base URL."""
        collector = BinancePublicDataCollector(
            symbol="BTCUSDT",
            market_type=MarketType.SPOT,
        )
        assert "data/spot/monthly/klines" in collector.base_url

    def test_futures_base_url(self):
        """Futures market type sets correct base URL."""
        collector = BinancePublicDataCollector(
            symbol="BTCUSDT",
            market_type=MarketType.FUTURES,
        )
        assert "data/futures/um/monthly/klines" in collector.base_url

    def test_market_type_required(self):
        """market_type parameter is required (no default)."""
        with pytest.raises(TypeError):
            BinancePublicDataCollector(symbol="BTCUSDT")  # Missing market_type

    def test_market_type_stored(self):
        """market_type is stored on collector instance."""
        collector = BinancePublicDataCollector(
            symbol="BTCUSDT",
            market_type=MarketType.FUTURES,
        )
        assert collector.market_type == MarketType.FUTURES
```

**Step 2: Run test to verify it fails**

```bash
cd /Users/james/dev/gapless-crypto-data && uv run pytest tests/test_binance_collector_market_type.py -v
```

Expected: FAIL - tests fail because market_type parameter doesn't exist yet

**Step 3: Write minimal implementation**

Modify `src/gapless_crypto_data/collectors/binance_public_data_collector.py`:

At the top, add import:
```python
from gapless_crypto_data.market_types import MarketType
```

Find the `__init__` method and modify its signature and body. The key changes:

1. Add `market_type: MarketType` as required parameter (no default)
2. Store `self.market_type = market_type`
3. Update `self.base_url` to use market_type:
   ```python
   self.base_url = f"https://data.binance.vision/data/{market_type.base_path}/monthly/klines"
   ```

Also update any places where `HybridUrlGenerator` is instantiated to pass `market_type`.

**Step 4: Run test to verify it passes**

```bash
cd /Users/james/dev/gapless-crypto-data && uv run pytest tests/test_binance_collector_market_type.py -v
```

Expected: All 4 tests PASS

**Step 5: Commit**

```bash
cd /Users/james/dev/gapless-crypto-data && git add src/gapless_crypto_data/collectors/binance_public_data_collector.py tests/test_binance_collector_market_type.py && git commit -m "feat: add market_type parameter to BinancePublicDataCollector"
```

---

## Task 4: Update Collector Filename Generation

**Files:**
- Modify: `src/gapless_crypto_data/collectors/binance_public_data_collector.py`
- Test: `tests/test_binance_collector_market_type.py` (add tests)

**Step 1: Write the failing test**

Add to `tests/test_binance_collector_market_type.py`:

```python
class TestBinanceCollectorFilenames:
    """Tests for market-type-aware filename generation."""

    def test_spot_filename_prefix(self):
        """Spot files have 'binance_spot_' prefix."""
        collector = BinancePublicDataCollector(
            symbol="BTCUSDT",
            market_type=MarketType.SPOT,
        )
        # The filename generation uses market_type.filename_prefix
        expected_prefix = "binance_spot_"
        assert collector.market_type.filename_prefix == expected_prefix

    def test_futures_filename_prefix(self):
        """Futures files have 'binance_futures_' prefix."""
        collector = BinancePublicDataCollector(
            symbol="BTCUSDT",
            market_type=MarketType.FUTURES,
        )
        expected_prefix = "binance_futures_"
        assert collector.market_type.filename_prefix == expected_prefix
```

**Step 2: Run test to verify it passes**

```bash
cd /Users/james/dev/gapless-crypto-data && uv run pytest tests/test_binance_collector_market_type.py::TestBinanceCollectorFilenames -v
```

Expected: PASS (this tests the enum property, which already works)

**Step 3: Update filename generation in collector**

Find the filename generation code in `binance_public_data_collector.py` (search for `binance_spot_` or the output filename pattern) and update it to use:

```python
f"{self.market_type.filename_prefix}{self.symbol}-{timeframe}_..."
```

**Step 4: Verify existing tests still pass**

```bash
cd /Users/james/dev/gapless-crypto-data && uv run pytest tests/test_binance_collector_market_type.py -v
```

Expected: All tests PASS

**Step 5: Commit**

```bash
cd /Users/james/dev/gapless-crypto-data && git add src/gapless_crypto_data/collectors/binance_public_data_collector.py tests/test_binance_collector_market_type.py && git commit -m "feat: use market_type for filename prefix in collector"
```

---

## Task 5: Update API Layer - fetch_data()

**Files:**
- Modify: `src/gapless_crypto_data/api.py`
- Test: `tests/test_api_market_type.py` (create new)

**Step 1: Write the failing test**

Create `tests/test_api_market_type.py`:

```python
"""Tests for API market_type parameter."""

import pytest

from gapless_crypto_data import fetch_data
from gapless_crypto_data.market_types import MarketType


class TestFetchDataMarketType:
    """Tests for market_type parameter in fetch_data()."""

    def test_market_type_required(self):
        """fetch_data raises TypeError when market_type is missing."""
        with pytest.raises(TypeError) as exc_info:
            fetch_data(symbol="BTCUSDT", timeframe="1h")
        assert "market_type is required" in str(exc_info.value)

    def test_market_type_spot_accepted(self):
        """fetch_data accepts market_type='spot'."""
        # This will fail at data fetch, but should not raise on validation
        # We mock or use a very short date range to avoid actual download
        try:
            fetch_data(
                symbol="BTCUSDT",
                market_type="spot",
                timeframe="1d",
                start="2024-01-01",
                end="2024-01-01",
            )
        except Exception as e:
            # Should not be a market_type validation error
            assert "market_type" not in str(e).lower()

    def test_market_type_futures_accepted(self):
        """fetch_data accepts market_type='futures'."""
        try:
            fetch_data(
                symbol="BTCUSDT",
                market_type="futures",
                timeframe="1d",
                start="2024-01-01",
                end="2024-01-01",
            )
        except Exception as e:
            # Should not be a market_type validation error
            assert "market_type" not in str(e).lower()

    def test_invalid_market_type_raises(self):
        """fetch_data raises ValueError for invalid market_type."""
        with pytest.raises(ValueError):
            fetch_data(
                symbol="BTCUSDT",
                market_type="invalid",
                timeframe="1h",
            )
```

**Step 2: Run test to verify it fails**

```bash
cd /Users/james/dev/gapless-crypto-data && uv run pytest tests/test_api_market_type.py -v
```

Expected: FAIL - market_type parameter doesn't exist yet

**Step 3: Write minimal implementation**

Modify `src/gapless_crypto_data/api.py`:

1. Add import at top:
```python
from .market_types import MarketType
```

2. Update `fetch_data()` signature (around line 357):
```python
def fetch_data(
    symbol: Union[str, SupportedSymbol],
    market_type: str,  # REQUIRED - no default
    timeframe: Optional[Union[str, SupportedTimeframe]] = None,
    limit: Optional[int] = None,
    start: Optional[str] = None,
    end: Optional[str] = None,
    output_dir: Optional[Union[str, Path]] = None,
    index_type: Optional[Literal["datetime", "range", "auto"]] = None,
    auto_fill_gaps: bool = True,
    *,
    interval: Optional[Union[str, SupportedTimeframe]] = None,
) -> pd.DataFrame:
```

3. Add validation at start of function body:
```python
    # Validate market_type (required parameter)
    if market_type is None:
        raise TypeError(
            "market_type is required. Use 'spot' or 'futures'."
        )

    # Convert string to enum (raises ValueError if invalid)
    market_type_enum = MarketType(market_type)
```

4. Update collector instantiation to pass market_type:
```python
    collector = BinancePublicDataCollector(
        symbol=symbol,
        market_type=market_type_enum,
        start_date=start,
        end_date=end,
        output_dir=str(output_dir) if output_dir else None,
    )
```

**Step 4: Run test to verify it passes**

```bash
cd /Users/james/dev/gapless-crypto-data && uv run pytest tests/test_api_market_type.py -v
```

Expected: All 4 tests PASS

**Step 5: Commit**

```bash
cd /Users/james/dev/gapless-crypto-data && git add src/gapless_crypto_data/api.py tests/test_api_market_type.py && git commit -m "feat: add required market_type parameter to fetch_data()"
```

---

## Task 6: Update API Layer - download()

**Files:**
- Modify: `src/gapless_crypto_data/api.py`
- Test: `tests/test_api_market_type.py` (add tests)

**Step 1: Write the failing test**

Add to `tests/test_api_market_type.py`:

```python
from gapless_crypto_data import download


class TestDownloadMarketType:
    """Tests for market_type parameter in download()."""

    def test_market_type_required(self):
        """download raises TypeError when market_type is missing."""
        with pytest.raises(TypeError) as exc_info:
            download(symbol="BTCUSDT", timeframe="1h")
        assert "market_type is required" in str(exc_info.value)

    def test_market_type_passed_to_fetch_data(self):
        """download passes market_type to fetch_data."""
        # This tests that download() correctly passes market_type through
        try:
            download(
                symbol="BTCUSDT",
                market_type="futures",
                timeframe="1d",
                start="2024-01-01",
                end="2024-01-01",
            )
        except Exception as e:
            # Should not be a market_type validation error
            assert "market_type" not in str(e).lower()
```

**Step 2: Run test to verify it fails**

```bash
cd /Users/james/dev/gapless-crypto-data && uv run pytest tests/test_api_market_type.py::TestDownloadMarketType -v
```

Expected: FAIL - download() doesn't have market_type yet

**Step 3: Write minimal implementation**

Find the `download()` function in `api.py` and update it similarly to `fetch_data()`:

1. Add `market_type: str` as required parameter
2. Pass it through to `fetch_data()`

**Step 4: Run test to verify it passes**

```bash
cd /Users/james/dev/gapless-crypto-data && uv run pytest tests/test_api_market_type.py -v
```

Expected: All tests PASS

**Step 5: Commit**

```bash
cd /Users/james/dev/gapless-crypto-data && git add src/gapless_crypto_data/api.py tests/test_api_market_type.py && git commit -m "feat: add required market_type parameter to download()"
```

---

## Task 7: Update Exports and Deprecate get_supported_symbols

**Files:**
- Modify: `src/gapless_crypto_data/__init__.py`
- Modify: `src/gapless_crypto_data/api.py`

**Step 1: Update __init__.py exports**

Add `MarketType` to the exports in `__init__.py`:

```python
from .market_types import MarketType

__all__ = [
    "fetch_data",
    "download",
    "fill_gaps",
    "get_supported_timeframes",
    "get_supported_symbols",  # Deprecated
    "MarketType",
]
```

**Step 2: Deprecate get_supported_symbols**

In `api.py`, update `get_supported_symbols()`:

```python
def get_supported_symbols() -> List[str]:
    """Get list of supported trading pairs.

    .. deprecated::
        This function is deprecated and will be removed in v7.0.0.
        Symbol validation is no longer performed. Use any valid Binance symbol.

    Returns:
        Empty list (function deprecated)
    """
    import warnings

    warnings.warn(
        "get_supported_symbols() is deprecated and will be removed in v7.0.0. "
        "Symbol validation is no longer performed. Use any valid Binance symbol.",
        DeprecationWarning,
        stacklevel=2,
    )
    return []
```

**Step 3: Run tests**

```bash
cd /Users/james/dev/gapless-crypto-data && uv run pytest tests/test_market_types.py tests/test_api_market_type.py -v
```

Expected: All tests PASS

**Step 4: Commit**

```bash
cd /Users/james/dev/gapless-crypto-data && git add src/gapless_crypto_data/__init__.py src/gapless_crypto_data/api.py && git commit -m "feat: export MarketType, deprecate get_supported_symbols()"
```

---

## Task 8: Fix Existing Tests

**Files:**
- Modify: Multiple test files that call API without market_type

**Step 1: Find all test files that need updating**

```bash
cd /Users/james/dev/gapless-crypto-data && grep -r "fetch_data\|download\|BinancePublicDataCollector" tests/ --include="*.py" | grep -v market_type | head -20
```

**Step 2: Update each test file**

For each test that instantiates `BinancePublicDataCollector` or calls `fetch_data`/`download`, add `market_type=MarketType.SPOT` or `market_type="spot"`.

Common patterns to update:
- `BinancePublicDataCollector(symbol="BTCUSDT")` → `BinancePublicDataCollector(symbol="BTCUSDT", market_type=MarketType.SPOT)`
- `fetch_data("BTCUSDT", "1h")` → `fetch_data("BTCUSDT", market_type="spot", timeframe="1h")`

**Step 3: Run full test suite**

```bash
cd /Users/james/dev/gapless-crypto-data && uv run pytest tests/ -v --ignore=tests/test_integration.py
```

Expected: All tests PASS

**Step 4: Commit**

```bash
cd /Users/james/dev/gapless-crypto-data && git add tests/ && git commit -m "fix: update existing tests for required market_type parameter"
```

---

## Task 9: Integration Test

**Files:**
- Create: `tests/test_futures_integration.py`

**Step 1: Write integration test**

Create `tests/test_futures_integration.py`:

```python
"""Integration tests for futures data fetching."""

import pytest

from gapless_crypto_data import fetch_data


@pytest.mark.integration
class TestFuturesIntegration:
    """Integration tests for USDT-M futures data."""

    def test_fetch_futures_btcusdt_1d(self):
        """Fetch 1 day of BTCUSDT futures data."""
        df = fetch_data(
            symbol="BTCUSDT",
            market_type="futures",
            timeframe="1d",
            start="2024-01-01",
            end="2024-01-07",
        )

        assert len(df) > 0
        assert "close" in df.columns
        assert "volume" in df.columns

    def test_fetch_spot_btcusdt_1d(self):
        """Fetch 1 day of BTCUSDT spot data."""
        df = fetch_data(
            symbol="BTCUSDT",
            market_type="spot",
            timeframe="1d",
            start="2024-01-01",
            end="2024-01-07",
        )

        assert len(df) > 0
        assert "close" in df.columns
```

**Step 2: Run integration test**

```bash
cd /Users/james/dev/gapless-crypto-data && uv run pytest tests/test_futures_integration.py -v -m integration
```

Expected: All tests PASS (requires network)

**Step 3: Commit**

```bash
cd /Users/james/dev/gapless-crypto-data && git add tests/test_futures_integration.py && git commit -m "test: add futures integration tests"
```

---

## Task 10: Update Version and Documentation

**Files:**
- Modify: `pyproject.toml`
- Modify: `src/gapless_crypto_data/__init__.py` (docstring)

**Step 1: Bump version to 6.0.0**

In `pyproject.toml`, update version:
```toml
version = "6.0.0"
```

**Step 2: Update module docstring**

In `src/gapless_crypto_data/__init__.py`, update the docstring to reflect new API:

```python
"""
gapless-crypto-data: Zero-gaps cryptocurrency OHLCV data from Binance.

Supports both Spot and USDT-M Futures markets.

Examples:
    # Fetch spot data
    import gapless_crypto_data as gcd
    df = gcd.fetch_data("BTCUSDT", market_type="spot", timeframe="1h")

    # Fetch futures data
    df = gcd.fetch_data("BTCUSDT", market_type="futures", timeframe="1h")

Breaking change in v6.0.0: market_type parameter is now required.
"""
```

**Step 3: Commit**

```bash
cd /Users/james/dev/gapless-crypto-data && git add pyproject.toml src/gapless_crypto_data/__init__.py && git commit -m "chore: bump version to 6.0.0, update documentation"
```

---

## Task 11: Final Validation

**Step 1: Run full test suite**

```bash
cd /Users/james/dev/gapless-crypto-data && uv run pytest tests/ -v
```

Expected: All tests PASS

**Step 2: Run integration tests**

```bash
cd /Users/james/dev/gapless-crypto-data && uv run pytest tests/ -v -m integration
```

Expected: Integration tests PASS

**Step 3: Test manual usage**

```bash
cd /Users/james/dev/gapless-crypto-data && uv run python -c "
from gapless_crypto_data import fetch_data, MarketType
print('MarketType.SPOT:', MarketType.SPOT)
print('MarketType.FUTURES:', MarketType.FUTURES)
print('SPOT base_path:', MarketType.SPOT.base_path)
print('FUTURES base_path:', MarketType.FUTURES.base_path)
"
```

Expected: Prints enum values and base paths correctly

---

## Summary

| Task | Description | Tests |
|------|-------------|-------|
| 1 | Create MarketType enum | 9 tests |
| 2 | Update HybridUrlGenerator | 5 tests |
| 3 | Update BinancePublicDataCollector | 4 tests |
| 4 | Update filename generation | 2 tests |
| 5 | Update fetch_data() | 4 tests |
| 6 | Update download() | 2 tests |
| 7 | Update exports, deprecate symbols | - |
| 8 | Fix existing tests | - |
| 9 | Integration tests | 2 tests |
| 10 | Version bump and docs | - |
| 11 | Final validation | - |

**Total new tests:** ~28 tests
**Estimated implementation time:** 2-3 hours
