"""Enhanced DataFrame classes for cryptocurrency time series analysis.

This module provides domain-specific DataFrame subclasses that extend pandas
functionality with cryptocurrency-specific methods while maintaining full
backward compatibility.

Exception-only failure principle: All methods raise exceptions on error with
no fallbacks, defaults, retries, or silent handling.
"""

import warnings

import numpy as np
import pandas as pd


class GaplessDataFrame(pd.DataFrame):
    """Enhanced DataFrame for cryptocurrency data with time series capabilities.

    Extends pandas DataFrame with domain-specific methods for cryptocurrency
    time series analysis. Maintains full backward compatibility while providing
    convenient access to time series operations.

    Service Level Objectives:
    - Availability: 99.9% (successful method calls / total calls)
    - Correctness: 100% (data integrity validation pass rate)
    - Observability: 100% method coverage with type hints
    - Maintainability: Zero breaking changes, additive API evolution

    Exception-only failure: All methods raise exceptions on error conditions.
    No fallbacks, defaults, or silent error handling.
    """

    def __init__(self, data=None, index=None, columns=None, dtype=None, copy=None):
        """Initialize GaplessDataFrame with pandas DataFrame constructor signature."""
        super().__init__(data=data, index=index, columns=columns, dtype=dtype, copy=copy)

    @property
    def _constructor(self) -> type:
        """Ensure operations return GaplessDataFrame instances."""
        return GaplessDataFrame

    @property
    def timeseries(self) -> pd.DataFrame:
        """Convert to DatetimeIndex format for time series analysis.

        Returns a view with 'date' column set as DatetimeIndex while preserving
        the original date column. Optimized for time series operations like
        resampling, rolling windows, and temporal calculations.

        Returns:
            pd.DataFrame: DataFrame with DatetimeIndex, date column preserved

        Raises:
            KeyError: If 'date' column is missing
            ValueError: If 'date' column cannot be converted to datetime

        Examples:
            >>> df = GaplessDataFrame(data)
            >>> ts_df = df.timeseries
            >>> returns = ts_df['close'].pct_change()
        """
        if "date" not in self.columns:
            raise KeyError("DataFrame must contain 'date' column for time series operations")

        try:
            return self.set_index("date", drop=False)
        except Exception as e:
            raise ValueError(f"Failed to convert 'date' column to DatetimeIndex: {e}") from e

    def returns(self, column: str = "close", periods: int = 1) -> pd.Series:
        """Calculate percentage returns for specified column.

        Computes percentage change with automatic DatetimeIndex handling.
        Uses pandas pct_change() with exception-only failure principles.

        Args:
            column: Column name for return calculation (default: 'close')
            periods: Number of periods to shift for calculation (default: 1)

        Returns:
            pd.Series: Percentage returns with DatetimeIndex

        Raises:
            KeyError: If specified column does not exist
            ValueError: If column contains non-numeric data

        Examples:
            >>> df = GaplessDataFrame(ohlcv_data)
            >>> daily_returns = df.returns('close')
            >>> hourly_returns = df.returns('close', periods=1)
        """
        if column not in self.columns:
            raise KeyError(f"Column '{column}' not found in DataFrame")

        if not pd.api.types.is_numeric_dtype(self[column]):
            raise ValueError(f"Column '{column}' must contain numeric data for return calculation")

        ts_df = self.timeseries
        return ts_df[column].pct_change(periods=periods)

    def resample_ohlcv(self, rule: str, **kwargs) -> "GaplessDataFrame":
        """Resample OHLCV data using standard aggregation rules.

        Applies cryptocurrency-standard aggregation:
        - open: first value
        - high: maximum value
        - low: minimum value
        - close: last value
        - volume: sum of values
        - Other numeric columns: last value

        Args:
            rule: Frequency string (e.g., '1H', '1D', '1W')
            **kwargs: Additional arguments passed to pandas resample()

        Returns:
            GaplessDataFrame: Resampled data with same structure

        Raises:
            KeyError: If required OHLCV columns are missing
            ValueError: If rule is invalid or data cannot be resampled

        Examples:
            >>> df = GaplessDataFrame(minute_data)
            >>> hourly = df.resample_ohlcv('1H')
            >>> daily = df.resample_ohlcv('1D', label='right')
        """
        required_columns = ["open", "high", "low", "close", "volume"]
        missing_columns = [col for col in required_columns if col not in self.columns]
        if missing_columns:
            raise KeyError(f"Missing required OHLCV columns: {missing_columns}")

        try:
            ts_df = self.timeseries
            resampler = ts_df.resample(rule, **kwargs)

            # Standard OHLCV aggregation rules
            agg_dict = {
                "open": "first",
                "high": "max",
                "low": "min",
                "close": "last",
                "volume": "sum",
            }

            # Add other numeric columns with 'last' aggregation
            for col in self.select_dtypes(include=[np.number]).columns:
                if col not in agg_dict:
                    agg_dict[col] = "last"

            result = resampler.agg(agg_dict)
            return GaplessDataFrame(result.reset_index())

        except Exception as e:
            raise ValueError(f"Failed to resample data with rule '{rule}': {e}") from e

    def volatility(self, column: str = "close", window: int = 20, method: str = "std") -> pd.Series:
        """Calculate rolling volatility for specified column.

        Computes rolling volatility using standard pandas methods.
        Supports multiple volatility measures with exception-only failure.

        Args:
            column: Column name for volatility calculation (default: 'close')
            window: Rolling window size (default: 20)
            method: Volatility method - 'std' or 'var' (default: 'std')

        Returns:
            pd.Series: Rolling volatility with DatetimeIndex

        Raises:
            KeyError: If specified column does not exist
            ValueError: If method is invalid or calculation fails

        Examples:
            >>> df = GaplessDataFrame(price_data)
            >>> vol_20 = df.volatility('close', window=20)
            >>> vol_var = df.volatility('close', window=10, method='var')
        """
        if column not in self.columns:
            raise KeyError(f"Column '{column}' not found in DataFrame")

        if method not in ["std", "var"]:
            raise ValueError(f"Invalid volatility method '{method}'. Use 'std' or 'var'")

        if not isinstance(window, int) or window <= 0:
            raise ValueError(f"Window must be positive integer, got {window}")

        try:
            ts_df = self.timeseries
            if method == "std":
                return ts_df[column].rolling(window=window).std()
            else:  # method == 'var'
                return ts_df[column].rolling(window=window).var()

        except Exception as e:
            raise ValueError(f"Failed to calculate volatility: {e}") from e

    def drawdown(self, column: str = "close") -> pd.Series:
        """Calculate running maximum drawdown for specified column.

        Computes percentage drawdown from running maximum using pandas
        operations. Returns negative values indicating drawdown magnitude.

        Args:
            column: Column name for drawdown calculation (default: 'close')

        Returns:
            pd.Series: Running drawdown percentages with DatetimeIndex

        Raises:
            KeyError: If specified column does not exist
            ValueError: If column contains non-positive values

        Examples:
            >>> df = GaplessDataFrame(price_data)
            >>> dd = df.drawdown('close')
            >>> max_drawdown = dd.min()  # Most negative value
        """
        if column not in self.columns:
            raise KeyError(f"Column '{column}' not found in DataFrame")

        ts_df = self.timeseries
        prices = ts_df[column]

        if (prices <= 0).any():
            raise ValueError(
                f"Column '{column}' contains non-positive values unsuitable for drawdown"
            )

        try:
            running_max = prices.expanding().max()
            drawdown = (prices - running_max) / running_max
            return drawdown

        except Exception as e:
            raise ValueError(f"Failed to calculate drawdown: {e}") from e

    def validate_ohlcv(self) -> bool:
        """Validate OHLCV data integrity with comprehensive checks.

        Performs standard OHLCV validation:
        - Required columns present
        - High >= Low >= 0
        - Open, Close within [Low, High] range
        - Volume >= 0
        - No missing values in critical columns

        Returns:
            bool: True if all validations pass

        Raises:
            ValueError: If any validation fails with detailed error message

        Examples:
            >>> df = GaplessDataFrame(market_data)
            >>> is_valid = df.validate_ohlcv()  # True or raises ValueError
        """
        required_columns = ["open", "high", "low", "close", "volume"]
        missing_columns = [col for col in required_columns if col not in self.columns]
        if missing_columns:
            raise ValueError(f"Missing required OHLCV columns: {missing_columns}")

        # Check for missing values
        null_counts = self[required_columns].isnull().sum()
        if null_counts.any():
            null_cols = null_counts[null_counts > 0].to_dict()
            raise ValueError(f"Missing values found in critical columns: {null_cols}")

        # Validate price relationships
        invalid_high_low = (self["high"] < self["low"]).any()
        if invalid_high_low:
            raise ValueError("High prices must be >= Low prices")

        invalid_open = ((self["open"] < self["low"]) | (self["open"] > self["high"])).any()
        if invalid_open:
            raise ValueError("Open prices must be within [Low, High] range")

        invalid_close = ((self["close"] < self["low"]) | (self["close"] > self["high"])).any()
        if invalid_close:
            raise ValueError("Close prices must be within [Low, High] range")

        # Validate non-negative values
        invalid_prices = (self[["open", "high", "low", "close"]] < 0).any().any()
        if invalid_prices:
            raise ValueError("Price values must be non-negative")

        invalid_volume = (self["volume"] < 0).any()
        if invalid_volume:
            raise ValueError("Volume values must be non-negative")

        return True


def _deprecation_warning_index_type():
    """Issue deprecation warning for index_type parameter."""
    warnings.warn(
        "The 'index_type' parameter is deprecated and will be removed in v3.0.0. "
        "GaplessDataFrame provides .timeseries property for time series operations. "
        "Use df.timeseries instead of index_type='datetime'.",
        DeprecationWarning,
        stacklevel=3,
    )
