"""Market type enum for Binance data sources.

Supports both Spot and USDT-M Futures markets from Binance Vision.

Usage:
    from gapless_crypto_data.market_types import MarketType

    # Use enum values
    market = MarketType.SPOT
    market = MarketType.FUTURES

    # Create from string
    market = MarketType("spot")
    market = MarketType("futures")

    # Access properties
    path = market.base_path       # "spot" or "futures/um"
    prefix = market.filename_prefix  # "binance_spot_" or "binance_futures_"
"""

from enum import Enum


class MarketType(str, Enum):
    """Binance market type for data collection.

    Attributes:
        SPOT: Binance spot market (BTCUSDT, ETHUSDT, etc.)
        FUTURES: Binance USDT-M futures market (perpetual contracts)

    Properties:
        base_path: Path segment for Binance Vision URLs
        filename_prefix: Prefix for output filenames
    """

    SPOT = "spot"
    FUTURES = "futures"

    def __str__(self) -> str:
        """Return the string value of the enum."""
        return self.value

    @property
    def base_path(self) -> str:
        """Return the base path segment for Binance Vision URLs.

        Returns:
            str: "spot" for spot market, "futures/um" for USDT-M futures
        """
        if self == MarketType.SPOT:
            return "spot"
        return "futures/um"

    @property
    def filename_prefix(self) -> str:
        """Return the prefix for output filenames.

        Returns:
            str: "binance_spot_" or "binance_futures_"
        """
        return f"binance_{self.value}_"
