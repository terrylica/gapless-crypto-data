"""Tests for HybridUrlGenerator with MarketType support.

Tests verify:
- market_type parameter is required (no default)
- base_url is computed from market_type.base_path
- URL generation includes correct market path segments
"""

from datetime import datetime

import pytest

from gapless_crypto_data.collectors.hybrid_url_generator import HybridUrlGenerator
from gapless_crypto_data.market_types import MarketType


class TestHybridUrlGeneratorBaseUrl:
    """Test base_url computation from market_type."""

    def test_spot_base_url(self):
        """Test SPOT market_type produces correct base_url."""
        generator = HybridUrlGenerator(market_type=MarketType.SPOT)
        assert generator.base_url == "https://data.binance.vision/data/spot"

    def test_futures_base_url(self):
        """Test FUTURES market_type produces correct base_url."""
        generator = HybridUrlGenerator(market_type=MarketType.FUTURES)
        assert generator.base_url == "https://data.binance.vision/data/futures/um"

    def test_market_type_stored(self):
        """Test market_type is stored on the instance."""
        generator = HybridUrlGenerator(market_type=MarketType.SPOT)
        assert generator.market_type == MarketType.SPOT

        generator_futures = HybridUrlGenerator(market_type=MarketType.FUTURES)
        assert generator_futures.market_type == MarketType.FUTURES


class TestHybridUrlGeneratorMarketTypeRequired:
    """Test that market_type parameter is required."""

    def test_market_type_required(self):
        """Test TypeError when market_type is missing."""
        with pytest.raises(TypeError) as exc_info:
            HybridUrlGenerator()  # type: ignore[call-arg]
        assert "market_type" in str(exc_info.value)


class TestHybridUrlGeneratorUrlGeneration:
    """Test URL generation for different market types."""

    def test_spot_monthly_url_generation(self):
        """Test monthly URLs contain '/spot/monthly/klines/'."""
        generator = HybridUrlGenerator(
            market_type=MarketType.SPOT,
            daily_lookback_days=0,  # Force all to monthly
        )
        tasks = generator.generate_download_tasks(
            symbol="BTCUSDT",
            timeframe="1h",
            start_date=datetime(2024, 1, 1),
            end_date=datetime(2024, 1, 31),
        )

        assert len(tasks) > 0
        for task in tasks:
            assert "/spot/monthly/klines/" in task.url

    def test_futures_monthly_url_generation(self):
        """Test monthly URLs contain '/futures/um/monthly/klines/'."""
        generator = HybridUrlGenerator(
            market_type=MarketType.FUTURES,
            daily_lookback_days=0,  # Force all to monthly
        )
        tasks = generator.generate_download_tasks(
            symbol="BTCUSDT",
            timeframe="1h",
            start_date=datetime(2024, 1, 1),
            end_date=datetime(2024, 1, 31),
        )

        assert len(tasks) > 0
        for task in tasks:
            assert "/futures/um/monthly/klines/" in task.url

    def test_spot_daily_url_generation(self):
        """Test daily URLs contain '/spot/daily/klines/'."""
        generator = HybridUrlGenerator(
            market_type=MarketType.SPOT,
            daily_lookback_days=365 * 10,  # Force all to daily
        )
        tasks = generator.generate_download_tasks(
            symbol="BTCUSDT",
            timeframe="1h",
            start_date=datetime(2024, 1, 1),
            end_date=datetime(2024, 1, 3),
        )

        assert len(tasks) > 0
        for task in tasks:
            assert "/spot/daily/klines/" in task.url

    def test_futures_daily_url_generation(self):
        """Test daily URLs contain '/futures/um/daily/klines/'."""
        generator = HybridUrlGenerator(
            market_type=MarketType.FUTURES,
            daily_lookback_days=365 * 10,  # Force all to daily
        )
        tasks = generator.generate_download_tasks(
            symbol="BTCUSDT",
            timeframe="1h",
            start_date=datetime(2024, 1, 1),
            end_date=datetime(2024, 1, 3),
        )

        assert len(tasks) > 0
        for task in tasks:
            assert "/futures/um/daily/klines/" in task.url


class TestHybridUrlGeneratorOptionalParams:
    """Test optional parameters still work with market_type."""

    def test_daily_lookback_days_param(self):
        """Test daily_lookback_days parameter is accepted."""
        generator = HybridUrlGenerator(
            market_type=MarketType.SPOT,
            daily_lookback_days=45,
        )
        assert generator.daily_lookback_days == 45

    def test_max_concurrent_per_batch_param(self):
        """Test max_concurrent_per_batch parameter is accepted."""
        generator = HybridUrlGenerator(
            market_type=MarketType.SPOT,
            max_concurrent_per_batch=10,
        )
        assert generator.max_concurrent_per_batch == 10
