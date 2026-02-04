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

__version__ = "6.0.0"
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
from .market_types import MarketType

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
    # Market type enum (v6.0.0)
    "MarketType",
]
