"""
Gapless Crypto Data - Binance USDT spot market OHLCV collection with gap-free guarantee.

Scope:
    - USDT spot pairs only (BTCUSDT, ETHUSDT, SOLUSDT, etc.)
    - No futures, perpetuals, derivatives, or margin data

Capabilities:
    - Bulk historical data via Binance Public Data Repository
    - Microstructure-enriched kline format (OHLCV + order flow metrics)
    - Gap detection and API-based filling
    - All Binance spot kline intervals supported

Data Source:
    https://data.binance.vision/data/spot/monthly/klines/

Usage:
    import gapless_crypto_data as gcd

    # Fetch data
    df = gcd.fetch_data("BTCUSDT", timeframe="1h", limit=1000)
    df = gcd.download("ETHUSDT", timeframe="4h", start="2024-01-01", end="2024-06-30")

    # Discovery
    symbols = gcd.get_supported_symbols()
    timeframes = gcd.get_supported_timeframes()

    # Gap filling
    results = gcd.fill_gaps("./data")

    # Class-based API
    from gapless_crypto_data import BinancePublicDataCollector, UniversalGapFiller
    collector = BinancePublicDataCollector()
    result = collector.collect_timeframe_data("1h")
"""

__version__ = "5.0.2"
__author__ = "Eon Labs"
__email__ = "terry@eonlabs.com"

# Core classes (advanced/power-user API)
# Enhanced DataFrame for domain-specific operations
# Convenience functions (simple/intuitive API)
# API-only probe hooks for AI coding agents
from . import __probe__
from .api import (
    download,
    fetch_data,
    fill_gaps,
    get_info,
    get_supported_intervals,
    get_supported_symbols,
    get_supported_timeframes,
    load_parquet,
    save_parquet,
)
from .collectors.binance_public_data_collector import BinancePublicDataCollector
from .exceptions import (
    DataCollectionError,
    GapFillingError,
    GaplessCryptoDataError,
    NetworkError,
    ValidationError,
)
from .gap_filling.safe_file_operations import AtomicCSVOperations, SafeCSVMerger
from .gap_filling.universal_gap_filler import UniversalGapFiller

__all__ = [
    # Simple function-based API (recommended for most users)
    "fetch_data",
    "download",
    "get_supported_symbols",
    "get_supported_timeframes",
    "get_supported_intervals",  # Legacy compatibility
    "fill_gaps",
    "get_info",
    "save_parquet",
    "load_parquet",
    # Advanced class-based API (for complex workflows)
    "BinancePublicDataCollector",
    "UniversalGapFiller",
    "AtomicCSVOperations",
    "SafeCSVMerger",
    # Structured exception hierarchy (v3.2.0)
    "GaplessCryptoDataError",
    "DataCollectionError",
    "ValidationError",
    "NetworkError",
    "GapFillingError",
    # AI agent probe hooks
    "__probe__",
]
