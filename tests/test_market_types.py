"""Tests for MarketType enum.

Tests verify:
- Enum values (SPOT, FUTURES)
- base_path property for both market types
- filename_prefix property for both market types
- String conversion (MarketType("spot") == MarketType.SPOT)
- Invalid value raises ValueError
"""

import pytest

from gapless_crypto_data.market_types import MarketType


class TestMarketTypeEnum:
    """Test MarketType enum values and string conversion."""

    def test_spot_value(self):
        """Test SPOT enum has correct string value."""
        assert MarketType.SPOT.value == "spot"

    def test_futures_value(self):
        """Test FUTURES enum has correct string value."""
        assert MarketType.FUTURES.value == "futures"

    def test_string_conversion_spot(self):
        """Test MarketType("spot") returns MarketType.SPOT."""
        assert MarketType("spot") == MarketType.SPOT

    def test_string_conversion_futures(self):
        """Test MarketType("futures") returns MarketType.FUTURES."""
        assert MarketType("futures") == MarketType.FUTURES

    def test_invalid_value_raises_error(self):
        """Test invalid market type raises ValueError."""
        with pytest.raises(ValueError):
            MarketType("invalid")

    def test_invalid_value_perpetual_raises_error(self):
        """Test 'perpetual' market type raises ValueError."""
        with pytest.raises(ValueError):
            MarketType("perpetual")


class TestMarketTypeBasePath:
    """Test base_path property for URL generation."""

    def test_spot_base_path(self):
        """Test SPOT base_path returns 'spot'."""
        assert MarketType.SPOT.base_path == "spot"

    def test_futures_base_path(self):
        """Test FUTURES base_path returns 'futures/um'."""
        assert MarketType.FUTURES.base_path == "futures/um"


class TestMarketTypeFilenamePrefix:
    """Test filename_prefix property for output files."""

    def test_spot_filename_prefix(self):
        """Test SPOT filename_prefix returns 'binance_spot_'."""
        assert MarketType.SPOT.filename_prefix == "binance_spot_"

    def test_futures_filename_prefix(self):
        """Test FUTURES filename_prefix returns 'binance_futures_'."""
        assert MarketType.FUTURES.filename_prefix == "binance_futures_"


class TestMarketTypeStringRepresentation:
    """Test string representation of MarketType enum."""

    def test_spot_str(self):
        """Test str(MarketType.SPOT) returns 'spot'."""
        assert str(MarketType.SPOT) == "spot"

    def test_futures_str(self):
        """Test str(MarketType.FUTURES) returns 'futures'."""
        assert str(MarketType.FUTURES) == "futures"
