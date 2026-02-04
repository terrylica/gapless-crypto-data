"""Integration tests for futures data fetching."""

import pytest

from gapless_crypto_data import fetch_data


@pytest.mark.integration
class TestFuturesIntegration:
    """Integration tests for USDT-M futures data."""

    def test_fetch_futures_btcusdt_1d(self):
        """Fetch 1 week of BTCUSDT futures data."""
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
        """Fetch 1 week of BTCUSDT spot data for comparison."""
        df = fetch_data(
            symbol="BTCUSDT",
            market_type="spot",
            timeframe="1d",
            start="2024-01-01",
            end="2024-01-07",
        )

        assert len(df) > 0
        assert "close" in df.columns
