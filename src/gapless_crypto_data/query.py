"""
QuestDB query interface for gapless-crypto-data v4.0.0.

SQL query abstraction returning pandas DataFrames for backward compatibility.
Provides high-level methods for common OHLCV queries with automatic connection management.

Architecture:
- PostgreSQL wire protocol (port 8812) for queries
- pandas DataFrame return type for compatibility with v3.x API
- SQL-based filtering and aggregation

Error Handling:
- Raise and propagate query failures (no fallbacks)
- Raise and propagate connection failures (no retries)
- Invalid parameters raise ValueError

SLOs:
- Availability: Query failures propagate to caller
- Correctness: Zero-gap guarantee via SQL timestamp validation
- Observability: Query execution logged at DEBUG level
- Maintainability: Standard SQL queries, pandas DataFrame output

Usage:
    from gapless_crypto_data.query import OHLCVQuery
    from gapless_crypto_data.questdb import QuestDBConnection

    with QuestDBConnection() as conn:
        query = OHLCVQuery(conn)

        # Get latest 100 bars
        df = query.get_latest("BTCUSDT", "1h", limit=100)

        # Get date range
        df = query.get_range(
            "ETHUSDT", "1h",
            start="2024-01-01",
            end="2024-12-31"
        )

        # Multi-symbol comparison
        df = query.get_multi_symbol(
            ["BTCUSDT", "ETHUSDT", "SOLUSDT"],
            "1h",
            start="2024-01-01",
            end="2024-01-31"
        )
"""

import logging
from typing import Any, List, Optional, Tuple

import pandas as pd
import psycopg

from .questdb.connection import QuestDBConnection

logger = logging.getLogger(__name__)


class OHLCVQuery:
    """
    High-level query interface for OHLCV data in QuestDB.

    Provides pandas DataFrame-based API for querying time-series OHLCV data
    with automatic connection management and SQL query construction.

    Attributes:
        connection: QuestDB connection for PostgreSQL queries

    Error Handling:
        - Connection failures raise ConnectionError
        - Query failures raise psycopg.Error
        - Invalid parameters raise ValueError
        - No retries, no fallbacks

    Performance:
        - Query latency: <1s for typical OHLCV ranges (1M rows)
        - Result set: Materialized to pandas DataFrame
        - Memory: Entire result loaded into memory

    Examples:
        # Get latest data
        with QuestDBConnection() as conn:
            query = OHLCVQuery(conn)
            df = query.get_latest("BTCUSDT", "1h", limit=1000)
            print(f"Latest close: {df.iloc[-1]['close']}")

        # Date range query
        with QuestDBConnection() as conn:
            query = OHLCVQuery(conn)
            df = query.get_range(
                "ETHUSDT", "1h",
                start="2024-01-01",
                end="2024-12-31"
            )
            print(f"Total bars: {len(df)}")

        # Multi-symbol query
        with QuestDBConnection() as conn:
            query = OHLCVQuery(conn)
            df = query.get_multi_symbol(
                ["BTCUSDT", "ETHUSDT"],
                "1h",
                start="2024-01-01",
                end="2024-01-31"
            )
            print(df.groupby("symbol")["close"].mean())
    """

    def __init__(self, connection: QuestDBConnection) -> None:
        """
        Initialize OHLCV query interface.

        Args:
            connection: Active QuestDB connection

        Raises:
            ValueError: If connection is invalid
        """
        if not isinstance(connection, QuestDBConnection):
            raise ValueError(f"Expected QuestDBConnection, got {type(connection).__name__}")

        self.connection = connection
        logger.debug("OHLCVQuery interface initialized")

    def get_latest(self, symbol: str, timeframe: str, limit: int = 1000) -> pd.DataFrame:
        """
        Get latest N bars for a symbol and timeframe.

        Args:
            symbol: Trading pair symbol (e.g., "BTCUSDT")
            timeframe: Timeframe string (e.g., "1h")
            limit: Number of bars to retrieve (default: 1000)

        Returns:
            pandas DataFrame with OHLCV data, sorted by timestamp (oldest first)

        Raises:
            ValueError: If parameters are invalid
            psycopg.Error: If query fails
            ConnectionError: If database connection fails

        Example:
            df = query.get_latest("BTCUSDT", "1h", limit=100)
            print(df.columns)
            # ['timestamp', 'symbol', 'timeframe', 'open', 'high', 'low',
            #  'close', 'volume', 'close_time', 'quote_asset_volume',
            #  'number_of_trades', 'taker_buy_base_asset_volume',
            #  'taker_buy_quote_asset_volume', 'data_source']
        """
        # Validate inputs
        if not symbol:
            raise ValueError("Symbol cannot be empty")
        if not timeframe:
            raise ValueError("Timeframe cannot be empty")
        if limit <= 0:
            raise ValueError(f"Limit must be positive, got {limit}")

        symbol = symbol.upper()

        sql = """
            SELECT
                timestamp,
                symbol,
                timeframe,
                open,
                high,
                low,
                close,
                volume,
                close_time,
                quote_asset_volume,
                number_of_trades,
                taker_buy_base_asset_volume,
                taker_buy_quote_asset_volume,
                data_source
            FROM ohlcv
            WHERE symbol = %s AND timeframe = %s
            ORDER BY timestamp DESC
            LIMIT %s
        """

        logger.debug(f"Querying latest {limit} bars for {symbol} {timeframe}")

        try:
            # Execute query
            pg_conn = self.connection.get_pg_connection()
            df = pd.read_sql_query(sql, pg_conn, params=(symbol, timeframe, limit))

            # Reverse to chronological order (oldest first)
            df = df.iloc[::-1].reset_index(drop=True)

            logger.info(f"Retrieved {len(df)} bars for {symbol} {timeframe}")
            return df

        except psycopg.Error as e:
            raise psycopg.Error(f"Query failed for {symbol} {timeframe}: {e}") from e

    def get_range(self, symbol: str, timeframe: str, start: str, end: str) -> pd.DataFrame:
        """
        Get OHLCV data for a specific date range.

        Args:
            symbol: Trading pair symbol (e.g., "BTCUSDT")
            timeframe: Timeframe string (e.g., "1h")
            start: Start date in "YYYY-MM-DD" or "YYYY-MM-DD HH:MM:SS" format
            end: End date in "YYYY-MM-DD" or "YYYY-MM-DD HH:MM:SS" format

        Returns:
            pandas DataFrame with OHLCV data, sorted by timestamp

        Raises:
            ValueError: If parameters are invalid
            psycopg.Error: If query fails
            ConnectionError: If database connection fails

        Example:
            df = query.get_range(
                "ETHUSDT", "1h",
                start="2024-01-01",
                end="2024-01-31"
            )
            print(f"Total bars: {len(df)}")
            print(f"First: {df.iloc[0]['timestamp']}")
            print(f"Last: {df.iloc[-1]['timestamp']}")
        """
        # Validate inputs
        if not symbol:
            raise ValueError("Symbol cannot be empty")
        if not timeframe:
            raise ValueError("Timeframe cannot be empty")

        symbol = symbol.upper()

        # Parse dates (validate format)
        try:
            start_dt = pd.to_datetime(start)
            end_dt = pd.to_datetime(end)
        except Exception as e:
            raise ValueError(
                f"Invalid date format. Expected 'YYYY-MM-DD' or 'YYYY-MM-DD HH:MM:SS', got start='{start}', end='{end}'"
            ) from e

        if start_dt >= end_dt:
            raise ValueError(f"Start date must be before end date, got start={start}, end={end}")

        sql = """
            SELECT
                timestamp,
                symbol,
                timeframe,
                open,
                high,
                low,
                close,
                volume,
                close_time,
                quote_asset_volume,
                number_of_trades,
                taker_buy_base_asset_volume,
                taker_buy_quote_asset_volume,
                data_source
            FROM ohlcv
            WHERE symbol = %s
              AND timeframe = %s
              AND timestamp >= %s
              AND timestamp <= %s
            ORDER BY timestamp ASC
        """

        logger.debug(f"Querying {symbol} {timeframe} from {start} to {end}")

        try:
            pg_conn = self.connection.get_pg_connection()
            df = pd.read_sql_query(sql, pg_conn, params=(symbol, timeframe, start, end))

            logger.info(f"Retrieved {len(df)} bars for {symbol} {timeframe} ({start} to {end})")
            return df

        except psycopg.Error as e:
            raise psycopg.Error(
                f"Query failed for {symbol} {timeframe} {start} to {end}: {e}"
            ) from e

    def get_multi_symbol(
        self, symbols: List[str], timeframe: str, start: str, end: str
    ) -> pd.DataFrame:
        """
        Get OHLCV data for multiple symbols in a date range.

        Useful for multi-symbol analysis and comparison.

        Args:
            symbols: List of trading pair symbols (e.g., ["BTCUSDT", "ETHUSDT"])
            timeframe: Timeframe string (e.g., "1h")
            start: Start date in "YYYY-MM-DD" or "YYYY-MM-DD HH:MM:SS" format
            end: End date in "YYYY-MM-DD" or "YYYY-MM-DD HH:MM:SS" format

        Returns:
            pandas DataFrame with OHLCV data for all symbols, sorted by symbol then timestamp

        Raises:
            ValueError: If parameters are invalid
            psycopg.Error: If query fails
            ConnectionError: If database connection fails

        Example:
            df = query.get_multi_symbol(
                ["BTCUSDT", "ETHUSDT", "SOLUSDT"],
                "1h",
                start="2024-01-01",
                end="2024-01-31"
            )

            # Group by symbol for analysis
            summary = df.groupby("symbol").agg({
                "close": ["mean", "min", "max"],
                "volume": "sum"
            })
            print(summary)
        """
        # Validate inputs
        if not symbols:
            raise ValueError("Symbols list cannot be empty")
        if not timeframe:
            raise ValueError("Timeframe cannot be empty")

        symbols = [s.upper() for s in symbols]

        # Parse dates
        try:
            start_dt = pd.to_datetime(start)
            end_dt = pd.to_datetime(end)
        except Exception as e:
            raise ValueError(
                f"Invalid date format. Expected 'YYYY-MM-DD', got start='{start}', end='{end}'"
            ) from e

        if start_dt >= end_dt:
            raise ValueError(f"Start date must be before end date, got start={start}, end={end}")

        # Construct IN clause with placeholders
        placeholders = ",".join(["%s"] * len(symbols))

        sql = f"""
            SELECT
                timestamp,
                symbol,
                timeframe,
                open,
                high,
                low,
                close,
                volume,
                close_time,
                quote_asset_volume,
                number_of_trades,
                taker_buy_base_asset_volume,
                taker_buy_quote_asset_volume,
                data_source
            FROM ohlcv
            WHERE symbol IN ({placeholders})
              AND timeframe = %s
              AND timestamp >= %s
              AND timestamp <= %s
            ORDER BY symbol ASC, timestamp ASC
        """

        logger.debug(
            f"Querying {len(symbols)} symbols ({', '.join(symbols)}) {timeframe} from {start} to {end}"
        )

        try:
            pg_conn = self.connection.get_pg_connection()
            params = (*symbols, timeframe, start, end)
            df = pd.read_sql_query(sql, pg_conn, params=params)

            logger.info(f"Retrieved {len(df)} bars for {len(symbols)} symbols ({start} to {end})")
            return df

        except psycopg.Error as e:
            raise psycopg.Error(
                f"Multi-symbol query failed for {timeframe} {start} to {end}: {e}"
            ) from e

    def execute_sql(self, sql: str, params: Optional[Tuple[Any, ...]] = None) -> pd.DataFrame:
        """
        Execute raw SQL query and return results as DataFrame.

        For advanced queries not covered by high-level methods.

        Args:
            sql: SQL query string (use %s placeholders for parameters)
            params: Query parameters tuple (optional)

        Returns:
            pandas DataFrame with query results

        Raises:
            ValueError: If SQL is empty
            psycopg.Error: If query fails
            ConnectionError: If database connection fails

        Security:
            Always use parameterized queries (%s placeholders) to prevent SQL injection.
            NEVER concatenate user input directly into SQL strings.

        Example:
            # Parameterized query (SAFE)
            df = query.execute_sql(
                "SELECT * FROM ohlcv WHERE symbol = %s AND close > %s LIMIT 10",
                ("BTCUSDT", 50000.0)
            )

            # Direct string concatenation (UNSAFE - don't do this)
            # df = query.execute_sql(f"SELECT * FROM ohlcv WHERE symbol = '{user_input}'")
        """
        if not sql or not sql.strip():
            raise ValueError("SQL query cannot be empty")

        logger.debug(f"Executing raw SQL query: {sql[:100]}...")

        try:
            pg_conn = self.connection.get_pg_connection()
            df = pd.read_sql_query(sql, pg_conn, params=params)

            logger.info(f"Raw SQL query returned {len(df)} rows")
            return df

        except psycopg.Error as e:
            raise psycopg.Error(f"Raw SQL query failed: {e}") from e

    def detect_gaps(self, symbol: str, timeframe: str, start: str, end: str) -> pd.DataFrame:
        """
        Detect timestamp gaps in OHLCV data using SQL sequence analysis.

        Uses QuestDB's timestamp arithmetic to find missing bars based on
        expected timeframe intervals.

        Args:
            symbol: Trading pair symbol (e.g., "BTCUSDT")
            timeframe: Timeframe string (e.g., "1h")
            start: Start date in "YYYY-MM-DD" format
            end: End date in "YYYY-MM-DD" format

        Returns:
            pandas DataFrame with gap information:
            - gap_start: Timestamp where gap starts
            - gap_end: Timestamp where gap ends
            - expected_bars: Number of missing bars in gap

        Raises:
            ValueError: If parameters are invalid
            psycopg.Error: If query fails

        Example:
            gaps = query.detect_gaps("BTCUSDT", "1h", "2024-01-01", "2024-12-31")
            if gaps.empty:
                print("No gaps found!")
            else:
                print(f"Found {len(gaps)} gaps:")
                print(gaps)
        """
        # Map timeframe to interval
        timeframe_to_interval = {
            "1s": "1 second",
            "1m": "1 minute",
            "3m": "3 minutes",
            "5m": "5 minutes",
            "15m": "15 minutes",
            "30m": "30 minutes",
            "1h": "1 hour",
            "2h": "2 hours",
            "4h": "4 hours",
            "6h": "6 hours",
            "8h": "8 hours",
            "12h": "12 hours",
            "1d": "1 day",
        }

        if timeframe not in timeframe_to_interval:
            raise ValueError(f"Unsupported timeframe for gap detection: {timeframe}")

        interval = timeframe_to_interval[timeframe]
        symbol = symbol.upper()

        # SQL to detect gaps using LAG window function
        sql = f"""
            WITH gaps AS (
                SELECT
                    timestamp AS gap_end,
                    LAG(timestamp) OVER (ORDER BY timestamp) AS gap_start,
                    DATEDIFF('millisecond', LAG(timestamp) OVER (ORDER BY timestamp), timestamp) / (INTERVAL '{interval}' TO MILLISECONDS) AS bars_diff
                FROM ohlcv
                WHERE symbol = %s
                  AND timeframe = %s
                  AND timestamp >= %s
                  AND timestamp <= %s
                ORDER BY timestamp
            )
            SELECT
                gap_start,
                gap_end,
                bars_diff - 1 AS expected_bars
            FROM gaps
            WHERE bars_diff > 1
        """

        logger.debug(f"Detecting gaps for {symbol} {timeframe} from {start} to {end}")

        try:
            pg_conn = self.connection.get_pg_connection()
            df = pd.read_sql_query(sql, pg_conn, params=(symbol, timeframe, start, end))

            if df.empty:
                logger.info(f"No gaps found for {symbol} {timeframe}")
            else:
                logger.warning(
                    f"Found {len(df)} gaps for {symbol} {timeframe} "
                    f"(total missing bars: {df['expected_bars'].sum()})"
                )

            return df

        except psycopg.Error as e:
            raise psycopg.Error(f"Gap detection query failed for {symbol} {timeframe}: {e}") from e
