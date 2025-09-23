"""Tests for GaplessDataFrame enhanced DataFrame functionality.

Tests cover exception-only failure principles, domain-specific methods,
and backward compatibility with pandas DataFrame operations.
"""

import warnings
from datetime import timedelta

import numpy as np
import pandas as pd
import pytest

from gapless_crypto_data.dataframes import GaplessDataFrame


@pytest.fixture(scope="module")
def sample_ohlcv_data():
    """Generate sample OHLCV data for testing."""
    dates = pd.date_range("2024-01-01", periods=100, freq="1h")
    np.random.seed(42)  # Reproducible test data

    # Generate realistic OHLCV data
    base_price = 50000.0
    price_changes = np.random.normal(0, 0.02, 100)  # 2% volatility
    closes = base_price * np.cumprod(1 + price_changes)

    data = {
        "date": dates,
        "open": closes * (1 + np.random.normal(0, 0.001, 100)),
        "high": closes * (1 + np.abs(np.random.normal(0, 0.005, 100))),
        "low": closes * (1 - np.abs(np.random.normal(0, 0.005, 100))),
        "close": closes,
        "volume": np.random.uniform(100, 1000, 100),
        "quote_asset_volume": closes * np.random.uniform(100, 1000, 100),
        "number_of_trades": np.random.randint(50, 500, 100),
        "taker_buy_base_asset_volume": np.random.uniform(50, 500, 100),
        "taker_buy_quote_asset_volume": closes * np.random.uniform(50, 500, 100),
        "close_time": dates + timedelta(minutes=59),
    }

    # Ensure OHLCV relationships are valid
    for i in range(100):
        data["high"][i] = max(data["open"][i], data["high"][i], data["low"][i], data["close"][i])
        data["low"][i] = min(data["open"][i], data["high"][i], data["low"][i], data["close"][i])

    return GaplessDataFrame(data)


class TestGaplessDataFrame:
    """Test suite for GaplessDataFrame enhanced functionality."""

    def test_sample_ohlcv_data_fixture(self, sample_ohlcv_data):
        """Test that fixture is properly accessible."""
        assert isinstance(sample_ohlcv_data, GaplessDataFrame)
        assert len(sample_ohlcv_data) == 100

    def test_dataframe_inheritance(self, sample_ohlcv_data):
        """Test that GaplessDataFrame maintains pandas DataFrame compatibility."""
        assert isinstance(sample_ohlcv_data, pd.DataFrame)
        assert isinstance(sample_ohlcv_data, GaplessDataFrame)

        # Test basic DataFrame operations work
        assert len(sample_ohlcv_data) == 100
        assert "close" in sample_ohlcv_data.columns
        assert sample_ohlcv_data["close"].dtype == np.float64

    def test_constructor_preserves_type(self, sample_ohlcv_data):
        """Test that operations return GaplessDataFrame instances."""
        # Test various pandas operations that should preserve type
        subset = sample_ohlcv_data.head(10)
        assert isinstance(subset, GaplessDataFrame)

        filtered = sample_ohlcv_data[sample_ohlcv_data["volume"] > 500]
        assert isinstance(filtered, GaplessDataFrame)

    def test_timeseries_property(self, sample_ohlcv_data):
        """Test .timeseries property for DatetimeIndex conversion."""
        ts_df = sample_ohlcv_data.timeseries

        # Verify DatetimeIndex is set
        assert isinstance(ts_df.index, pd.DatetimeIndex)

        # Verify date column is preserved
        assert "date" in ts_df.columns

        # Verify data integrity
        assert len(ts_df) == len(sample_ohlcv_data)
        assert all(ts_df.columns == sample_ohlcv_data.columns)

    def test_timeseries_missing_date_column(self):
        """Test .timeseries property raises exception when date column missing."""
        df = GaplessDataFrame({"price": [1, 2, 3], "volume": [100, 200, 300]})

        with pytest.raises(KeyError, match="DataFrame must contain 'date' column"):
            _ = df.timeseries

    def test_returns_calculation(self, sample_ohlcv_data):
        """Test .returns() method for percentage change calculation."""
        returns = sample_ohlcv_data.returns("close")

        # Verify return type and structure
        assert isinstance(returns, pd.Series)
        assert isinstance(returns.index, pd.DatetimeIndex)
        assert len(returns) == len(sample_ohlcv_data)

        # Verify first return is NaN (standard pct_change behavior)
        assert pd.isna(returns.iloc[0])

        # Verify calculation accuracy (spot check)
        manual_return = (
            sample_ohlcv_data["close"].iloc[1] / sample_ohlcv_data["close"].iloc[0]
        ) - 1
        calculated_return = returns.iloc[1]
        assert abs(manual_return - calculated_return) < 1e-10

    def test_returns_custom_periods(self, sample_ohlcv_data):
        """Test .returns() method with custom periods parameter."""
        returns_2 = sample_ohlcv_data.returns("close", periods=2)

        # First two returns should be NaN
        assert pd.isna(returns_2.iloc[0])
        assert pd.isna(returns_2.iloc[1])

        # Verify 2-period calculation
        manual_return = (
            sample_ohlcv_data["close"].iloc[2] / sample_ohlcv_data["close"].iloc[0]
        ) - 1
        calculated_return = returns_2.iloc[2]
        assert abs(manual_return - calculated_return) < 1e-10

    def test_returns_missing_column(self, sample_ohlcv_data):
        """Test .returns() raises exception for missing column."""
        with pytest.raises(KeyError, match="Column 'nonexistent' not found"):
            sample_ohlcv_data.returns("nonexistent")

    def test_returns_non_numeric_column(self):
        """Test .returns() raises exception for non-numeric data."""
        df = GaplessDataFrame(
            {"date": pd.date_range("2024-01-01", periods=5), "text": ["a", "b", "c", "d", "e"]}
        )

        with pytest.raises(ValueError, match="Column 'text' must contain numeric data"):
            df.returns("text")

    def test_resample_ohlcv(self, sample_ohlcv_data):
        """Test .resample_ohlcv() method for proper OHLCV aggregation."""
        # Resample hourly data to daily
        daily = sample_ohlcv_data.resample_ohlcv("1D")

        # Verify return type
        assert isinstance(daily, GaplessDataFrame)

        # Verify aggregation worked (should have fewer rows)
        assert len(daily) < len(sample_ohlcv_data)

        # Verify required columns are present
        required_cols = ["open", "high", "low", "close", "volume"]
        for col in required_cols:
            assert col in daily.columns

    def test_resample_ohlcv_missing_columns(self):
        """Test .resample_ohlcv() raises exception for missing OHLCV columns."""
        df = GaplessDataFrame(
            {
                "date": pd.date_range("2024-01-01", periods=5),
                "open": [1, 2, 3, 4, 5],
                "close": [1.1, 2.1, 3.1, 4.1, 5.1],
                # Missing high, low, volume
            }
        )

        with pytest.raises(KeyError, match="Missing required OHLCV columns"):
            df.resample_ohlcv("1D")

    def test_volatility_calculation(self, sample_ohlcv_data):
        """Test .volatility() method for rolling volatility calculation."""
        vol = sample_ohlcv_data.volatility("close", window=20)

        # Verify return type and structure
        assert isinstance(vol, pd.Series)
        assert isinstance(vol.index, pd.DatetimeIndex)
        assert len(vol) == len(sample_ohlcv_data)

        # First 19 values should be NaN (rolling window)
        assert pd.isna(vol.iloc[:19]).all()

        # 20th value onwards should have volatility
        assert not pd.isna(vol.iloc[19:]).any()

    def test_volatility_variance_method(self, sample_ohlcv_data):
        """Test .volatility() method with variance calculation."""
        vol_var = sample_ohlcv_data.volatility("close", window=10, method="var")
        vol_std = sample_ohlcv_data.volatility("close", window=10, method="std")

        # Variance should be square of standard deviation
        valid_mask = ~pd.isna(vol_var) & ~pd.isna(vol_std)
        np.testing.assert_array_almost_equal(
            vol_var[valid_mask], vol_std[valid_mask] ** 2, decimal=8
        )

    def test_volatility_invalid_method(self, sample_ohlcv_data):
        """Test .volatility() raises exception for invalid method."""
        with pytest.raises(ValueError, match="Invalid volatility method 'invalid'"):
            sample_ohlcv_data.volatility("close", method="invalid")

    def test_volatility_invalid_window(self, sample_ohlcv_data):
        """Test .volatility() raises exception for invalid window."""
        with pytest.raises(ValueError, match="Window must be positive integer"):
            sample_ohlcv_data.volatility("close", window=0)

        with pytest.raises(ValueError, match="Window must be positive integer"):
            sample_ohlcv_data.volatility("close", window=-5)

    def test_drawdown_calculation(self, sample_ohlcv_data):
        """Test .drawdown() method for maximum drawdown calculation."""
        dd = sample_ohlcv_data.drawdown("close")

        # Verify return type and structure
        assert isinstance(dd, pd.Series)
        assert isinstance(dd.index, pd.DatetimeIndex)
        assert len(dd) == len(sample_ohlcv_data)

        # First drawdown should be 0 (no previous high)
        assert dd.iloc[0] == 0.0

        # All drawdowns should be <= 0
        assert (dd <= 0).all()

    def test_drawdown_non_positive_values(self):
        """Test .drawdown() raises exception for non-positive values."""
        df = GaplessDataFrame(
            {
                "date": pd.date_range("2024-01-01", periods=5),
                "close": [1, 0, -1, 2, 3],  # Contains zero and negative
            }
        )

        with pytest.raises(ValueError, match="contains non-positive values"):
            df.drawdown("close")

    def test_validate_ohlcv_valid_data(self, sample_ohlcv_data):
        """Test .validate_ohlcv() returns True for valid data."""
        assert sample_ohlcv_data.validate_ohlcv() is True

    def test_validate_ohlcv_missing_columns(self):
        """Test .validate_ohlcv() raises exception for missing columns."""
        df = GaplessDataFrame(
            {
                "date": pd.date_range("2024-01-01", periods=5),
                "open": [1, 2, 3, 4, 5],
                # Missing other OHLCV columns
            }
        )

        with pytest.raises(ValueError, match="Missing required OHLCV columns"):
            df.validate_ohlcv()

    def test_validate_ohlcv_null_values(self):
        """Test .validate_ohlcv() raises exception for null values."""
        df = GaplessDataFrame(
            {
                "date": pd.date_range("2024-01-01", periods=5),
                "open": [1, 2, np.nan, 4, 5],  # Contains NaN
                "high": [1.1, 2.1, 3.1, 4.1, 5.1],
                "low": [0.9, 1.9, 2.9, 3.9, 4.9],
                "close": [1.05, 2.05, 3.05, 4.05, 5.05],
                "volume": [100, 200, 300, 400, 500],
            }
        )

        with pytest.raises(ValueError, match="Missing values found in critical columns"):
            df.validate_ohlcv()

    def test_validate_ohlcv_invalid_price_relationships(self):
        """Test .validate_ohlcv() raises exception for invalid price relationships."""
        df = GaplessDataFrame(
            {
                "date": pd.date_range("2024-01-01", periods=5),
                "open": [1, 2, 3, 4, 5],
                "high": [0.5, 2.1, 3.1, 4.1, 5.1],  # High < Low for first row
                "low": [0.9, 1.9, 2.9, 3.9, 4.9],
                "close": [1.05, 2.05, 3.05, 4.05, 5.05],
                "volume": [100, 200, 300, 400, 500],
            }
        )

        with pytest.raises(ValueError, match="High prices must be >= Low prices"):
            df.validate_ohlcv()

    def test_validate_ohlcv_negative_prices(self):
        """Test .validate_ohlcv() raises exception for negative prices."""
        df = GaplessDataFrame(
            {
                "date": pd.date_range("2024-01-01", periods=5),
                "open": [1, 2, 3, 4, 5],
                "high": [1.1, 2.1, 3.1, 4.1, 5.1],
                "low": [-0.1, 1.9, 2.9, 3.9, 4.9],  # Negative low price
                "close": [1.05, 2.05, 3.05, 4.05, 5.05],
                "volume": [100, 200, 300, 400, 500],
            }
        )

        with pytest.raises(ValueError, match="Price values must be non-negative"):
            df.validate_ohlcv()

    def test_validate_ohlcv_negative_volume(self):
        """Test .validate_ohlcv() raises exception for negative volume."""
        df = GaplessDataFrame(
            {
                "date": pd.date_range("2024-01-01", periods=5),
                "open": [1, 2, 3, 4, 5],
                "high": [1.1, 2.1, 3.1, 4.1, 5.1],
                "low": [0.9, 1.9, 2.9, 3.9, 4.9],
                "close": [1.05, 2.05, 3.05, 4.05, 5.05],
                "volume": [100, 200, -300, 400, 500],  # Negative volume
            }
        )

        with pytest.raises(ValueError, match="Volume values must be non-negative"):
            df.validate_ohlcv()


class TestDeprecationWarnings:
    """Test deprecation warnings for index_type parameter."""

    def test_index_type_deprecation_warning(self):
        """Test that using index_type parameter triggers deprecation warning."""
        import gapless_crypto_data as gcd

        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")

            # This should trigger a deprecation warning
            try:
                df = gcd.fetch_data("BTCUSDT", "1h", limit=1, index_type="datetime")
            except Exception:
                # Network errors are expected in tests, but warning should still be triggered
                pass

            # Check if deprecation warning was issued
            deprecation_warnings = [
                warning for warning in w if issubclass(warning.category, DeprecationWarning)
            ]
            assert len(deprecation_warnings) > 0
            assert "index_type" in str(deprecation_warnings[0].message)
            assert "deprecated" in str(deprecation_warnings[0].message).lower()


class TestBackwardCompatibility:
    """Test backward compatibility with existing pandas DataFrame operations."""

    def test_pandas_operations_work(self, sample_ohlcv_data):
        """Test that standard pandas operations work with GaplessDataFrame."""
        # Test statistical operations
        mean_close = sample_ohlcv_data["close"].mean()
        assert isinstance(mean_close, (float, np.floating))

        # Test groupby operations
        sample_ohlcv_data["hour"] = sample_ohlcv_data["date"].dt.hour
        grouped = sample_ohlcv_data.groupby("hour")["volume"].sum()
        assert isinstance(grouped, pd.Series)

        # Test sorting
        sorted_df = sample_ohlcv_data.sort_values("close")
        assert isinstance(sorted_df, GaplessDataFrame)

        # Test merging
        other_df = GaplessDataFrame(
            {"date": sample_ohlcv_data["date"][:10], "indicator": range(10)}
        )
        merged = sample_ohlcv_data.merge(other_df, on="date")
        assert isinstance(merged, GaplessDataFrame)

    def test_assignment_preserves_type(self, sample_ohlcv_data):
        """Test that column assignment preserves GaplessDataFrame type."""
        sample_ohlcv_data["new_column"] = sample_ohlcv_data["close"] * 2
        assert isinstance(sample_ohlcv_data, GaplessDataFrame)
        assert "new_column" in sample_ohlcv_data.columns


if __name__ == "__main__":
    pytest.main([__file__])
