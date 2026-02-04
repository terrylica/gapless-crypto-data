"""Tests for BinancePublicDataCollector market_type parameter.

TDD tests for Task 3: Adding market_type parameter to BinancePublicDataCollector.
"""

import pytest

from gapless_crypto_data.collectors.binance_public_data_collector import (
    BinancePublicDataCollector,
)
from gapless_crypto_data.market_types import MarketType


class TestBinanceCollectorMarketType:
    """Tests for market_type parameter in BinancePublicDataCollector."""

    def test_spot_base_url(self) -> None:
        """Verify base_url contains 'data/spot/monthly/klines' for SPOT market."""
        collector = BinancePublicDataCollector(
            market_type=MarketType.SPOT,
            symbol="BTCUSDT",
            start_date="2024-01-01",
            end_date="2024-01-31",
        )

        assert "data/spot/monthly/klines" in collector.base_url

    def test_futures_base_url(self) -> None:
        """Verify base_url contains 'data/futures/um/monthly/klines' for FUTURES market."""
        collector = BinancePublicDataCollector(
            market_type=MarketType.FUTURES,
            symbol="BTCUSDT",
            start_date="2024-01-01",
            end_date="2024-01-31",
        )

        assert "data/futures/um/monthly/klines" in collector.base_url

    def test_market_type_required(self) -> None:
        """Verify TypeError when market_type is missing."""
        with pytest.raises(TypeError):
            BinancePublicDataCollector(
                symbol="BTCUSDT",
                start_date="2024-01-01",
                end_date="2024-01-31",
            )

    def test_market_type_stored(self) -> None:
        """Verify market_type is stored on instance."""
        collector = BinancePublicDataCollector(
            market_type=MarketType.SPOT,
            symbol="BTCUSDT",
            start_date="2024-01-01",
            end_date="2024-01-31",
        )

        assert collector.market_type == MarketType.SPOT

    def test_market_type_futures_stored(self) -> None:
        """Verify FUTURES market_type is stored correctly."""
        collector = BinancePublicDataCollector(
            market_type=MarketType.FUTURES,
            symbol="ETHUSDT",
            start_date="2024-01-01",
            end_date="2024-01-31",
        )

        assert collector.market_type == MarketType.FUTURES


class TestBinanceCollectorFilenames:
    """Tests for market-type-aware filename generation."""

    def test_spot_filename_prefix(self) -> None:
        """Spot files have 'binance_spot_' prefix."""
        collector = BinancePublicDataCollector(
            market_type=MarketType.SPOT,
            symbol="BTCUSDT",
            start_date="2024-01-01",
            end_date="2024-01-31",
        )
        assert collector.market_type.filename_prefix == "binance_spot_"

    def test_futures_filename_prefix(self) -> None:
        """Futures files have 'binance_futures_' prefix."""
        collector = BinancePublicDataCollector(
            market_type=MarketType.FUTURES,
            symbol="BTCUSDT",
            start_date="2024-01-01",
            end_date="2024-01-31",
        )
        assert collector.market_type.filename_prefix == "binance_futures_"
