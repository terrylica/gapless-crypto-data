"""Tests for market_type parameter in fetch_data() API."""

import pytest


class TestMarketTypeParameter:
    """Tests for the required market_type parameter in fetch_data()."""

    def test_market_type_required(self):
        """Verify TypeError when market_type is missing."""
        from gapless_crypto_data.api import fetch_data

        # fetch_data without market_type should raise TypeError
        with pytest.raises(TypeError) as exc_info:
            fetch_data("BTCUSDT", timeframe="1h", limit=10)

        # Verify error message mentions market_type is required
        assert "market_type" in str(exc_info.value).lower()

    def test_market_type_spot_accepted(self):
        """Verify 'spot' is accepted as market_type (validation passes)."""
        from gapless_crypto_data.api import fetch_data

        # This should not raise ValueError for invalid market_type
        # It may fail later in the fetch process, but market_type validation should pass
        try:
            # Use very short date range to minimize actual fetching
            fetch_data(
                "BTCUSDT",
                "spot",
                timeframe="1h",
                start="2024-01-01",
                end="2024-01-01",
                limit=1,
            )
        except ValueError as e:
            # If ValueError is raised, it should NOT be about invalid market_type
            assert "market_type" not in str(e).lower() or "invalid" not in str(e).lower()
        except Exception:
            # Other exceptions (network, etc.) are acceptable - we're only testing validation
            pass

    def test_market_type_futures_accepted(self):
        """Verify 'futures' is accepted as market_type (validation passes)."""
        from gapless_crypto_data.api import fetch_data

        # This should not raise ValueError for invalid market_type
        try:
            fetch_data(
                "BTCUSDT",
                "futures",
                timeframe="1h",
                start="2024-01-01",
                end="2024-01-01",
                limit=1,
            )
        except ValueError as e:
            # If ValueError is raised, it should NOT be about invalid market_type
            assert "market_type" not in str(e).lower() or "invalid" not in str(e).lower()
        except Exception:
            # Other exceptions (network, etc.) are acceptable - we're only testing validation
            pass

    def test_invalid_market_type_raises(self):
        """Verify ValueError for invalid market_type value."""
        from gapless_crypto_data.api import fetch_data

        with pytest.raises(ValueError) as exc_info:
            fetch_data("BTCUSDT", "invalid", timeframe="1h", limit=10)

        # The error should mention the invalid value
        error_msg = str(exc_info.value).lower()
        assert "invalid" in error_msg or "market" in error_msg
