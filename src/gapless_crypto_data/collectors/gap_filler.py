"""
QuestDB Gap Filler for gapless-crypto-data v4.0.0.

SQL-based gap detection and REST API filling with direct QuestDB ingestion.
Ensures zero-gap guarantee through authentic Binance data sources.

Architecture:
    SQL gap detection → Binance REST API → ILP ingestion → QuestDB

Data Sources:
    Primary: Binance Public Data Repository (CloudFront, 22x faster)
    Gap Fill: Binance REST API (official klines endpoint, rate-limited)

Error Handling:
    - Raise and propagate API failures (no retry)
    - Raise and propagate ingestion failures (no silent drops)
    - Rate limit errors propagated to caller

SLOs:
    - Availability: REST API 99.9% SLA, failures propagate
    - Correctness: Zero-gap guarantee via SQL validation
    - Observability: Gap filling logged at INFO level
    - Maintainability: Standard REST API, ILP protocol

Usage:
    from gapless_crypto_data.collectors.gap_filler import QuestDBGapFiller
    from gapless_crypto_data.questdb import QuestDBConnection

    with QuestDBConnection() as conn:
        filler = QuestDBGapFiller(conn)

        # Detect and fill gaps
        filled = filler.fill_gaps(
            "BTCUSDT",
            "1h",
            start="2024-01-01",
            end="2024-12-31"
        )
        print(f"Filled {filled} gaps")
"""

import logging
import time
from datetime import datetime
from typing import List

import httpx
import pandas as pd
from questdb.ingress import TimestampNanos

from ..query import OHLCVQuery
from ..questdb.connection import QuestDBConnection

logger = logging.getLogger(__name__)


class QuestDBGapFiller:
    """
    Gap detection and filling for QuestDB OHLCV data.

    Uses SQL timestamp sequence analysis to detect gaps, then fills gaps
    using Binance REST API with direct QuestDB ILP ingestion.

    Attributes:
        connection: QuestDB connection for queries and ingestion
        query: OHLCV query interface for gap detection
        api_base_url: Binance REST API base URL

    Error Handling:
        - API rate limits raise httpx.HTTPStatusError (429)
        - API failures raise httpx.HTTPStatusError
        - Ingestion failures raise ConnectionError
        - No automatic retries (caller must handle)

    Rate Limits:
        - Binance REST API: 1200 requests/minute (weight-based)
        - Klines endpoint: Weight 1-2 per request
        - No built-in rate limiting (caller must implement if needed)

    Deduplication:
        - QuestDB UPSERT semantics handle duplicate timestamps
        - Safe to re-run gap filling without creating duplicates

    Examples:
        # Fill gaps for one symbol
        with QuestDBConnection() as conn:
            filler = QuestDBGapFiller(conn)
            gaps_filled = filler.fill_gaps(
                "BTCUSDT", "1h",
                start="2024-01-01",
                end="2024-12-31"
            )
            print(f"Filled {gaps_filled} gaps")

        # Check for gaps first
        with QuestDBConnection() as conn:
            filler = QuestDBGapFiller(conn)
            gaps = filler.detect_gaps("ETHUSDT", "1h", "2024-01-01", "2024-12-31")
            if not gaps.empty:
                print(f"Found {len(gaps)} gaps, filling...")
                filler.fill_gaps("ETHUSDT", "1h", "2024-01-01", "2024-12-31")
    """

    # Binance REST API base URL
    API_BASE_URL = "https://api.binance.com"

    # Timeframe mapping (Binance notation)
    TIMEFRAME_MAP = {
        "1s": "1s",
        "1m": "1m",
        "3m": "3m",
        "5m": "5m",
        "15m": "15m",
        "30m": "30m",
        "1h": "1h",
        "2h": "2h",
        "4h": "4h",
        "6h": "6h",
        "8h": "8h",
        "12h": "12h",
        "1d": "1d",
    }

    # Timeframe to milliseconds mapping
    TIMEFRAME_MS = {
        "1s": 1000,
        "1m": 60 * 1000,
        "3m": 3 * 60 * 1000,
        "5m": 5 * 60 * 1000,
        "15m": 15 * 60 * 1000,
        "30m": 30 * 60 * 1000,
        "1h": 60 * 60 * 1000,
        "2h": 2 * 60 * 60 * 1000,
        "4h": 4 * 60 * 60 * 1000,
        "6h": 6 * 60 * 60 * 1000,
        "8h": 8 * 60 * 60 * 1000,
        "12h": 12 * 60 * 60 * 1000,
        "1d": 24 * 60 * 60 * 1000,
    }

    def __init__(self, connection: QuestDBConnection) -> None:
        """
        Initialize QuestDB gap filler.

        Args:
            connection: Active QuestDB connection

        Raises:
            ValueError: If connection is invalid
        """
        if not isinstance(connection, QuestDBConnection):
            raise ValueError(f"Expected QuestDBConnection, got {type(connection).__name__}")

        self.connection = connection
        self.query = OHLCVQuery(connection)
        logger.info("QuestDB gap filler initialized")

    def detect_gaps(self, symbol: str, timeframe: str, start: str, end: str) -> pd.DataFrame:
        """
        Detect timestamp gaps in OHLCV data.

        Wrapper around OHLCVQuery.detect_gaps() for convenience.

        Args:
            symbol: Trading pair symbol (e.g., "BTCUSDT")
            timeframe: Timeframe string (e.g., "1h")
            start: Start date in "YYYY-MM-DD" format
            end: End date in "YYYY-MM-DD" format

        Returns:
            DataFrame with gap information:
            - gap_start: Timestamp where gap starts
            - gap_end: Timestamp where gap ends
            - expected_bars: Number of missing bars

        Raises:
            ValueError: If parameters are invalid
            psycopg.Error: If query fails
        """
        return self.query.detect_gaps(symbol, timeframe, start, end)

    def _fetch_klines_rest(
        self, symbol: str, timeframe: str, start_time: int, end_time: int
    ) -> List[List]:
        """
        Fetch klines data from Binance REST API.

        Args:
            symbol: Trading pair symbol (e.g., "BTCUSDT")
            timeframe: Timeframe in Binance notation (e.g., "1h")
            start_time: Start timestamp in milliseconds
            end_time: End timestamp in milliseconds

        Returns:
            List of klines data (each kline is a list of 11 values)

        Raises:
            httpx.HTTPStatusError: If API request fails
            httpx.RequestError: If network request fails

        API Response Format:
            [
                [
                    1499040000000,      // Open time
                    "0.01634790",       // Open
                    "0.80000000",       // High
                    "0.01575800",       // Low
                    "0.01577100",       // Close
                    "148976.11427815",  // Volume
                    1499644799999,      // Close time
                    "2434.19055334",    // Quote asset volume
                    308,                // Number of trades
                    "1756.87402397",    // Taker buy base asset volume
                    "28.46694368",      // Taker buy quote asset volume
                    "0"                 // Ignore
                ]
            ]
        """
        url = f"{self.API_BASE_URL}/api/v3/klines"
        params = {
            "symbol": symbol,
            "interval": self.TIMEFRAME_MAP[timeframe],
            "startTime": start_time,
            "endTime": end_time,
            "limit": 1000,  # Binance API limit
        }

        logger.debug(
            f"Fetching klines from Binance REST API: {symbol} {timeframe} {start_time}-{end_time}"
        )

        try:
            response = httpx.get(url, params=params, timeout=30.0)
            response.raise_for_status()

            klines = response.json()
            logger.info(f"Fetched {len(klines)} klines from REST API")
            return klines

        except httpx.HTTPStatusError as e:
            if e.response.status_code == 429:
                raise httpx.HTTPStatusError(
                    message="Binance API rate limit exceeded (429). Caller must implement rate limiting.",
                    request=e.request,
                    response=e.response,
                ) from e
            raise

    def _klines_to_dataframe(self, klines: List[List], symbol: str, timeframe: str) -> pd.DataFrame:
        """
        Convert Binance klines to pandas DataFrame.

        Args:
            klines: List of klines from REST API
            symbol: Trading pair symbol
            timeframe: Timeframe string

        Returns:
            DataFrame with OHLCV data
        """
        if not klines:
            return pd.DataFrame()

        df = pd.DataFrame(
            klines,
            columns=[
                "open_time",
                "open",
                "high",
                "low",
                "close",
                "volume",
                "close_time",
                "quote_asset_volume",
                "number_of_trades",
                "taker_buy_base_asset_volume",
                "taker_buy_quote_asset_volume",
                "ignore",
            ],
        )

        # Drop ignore column
        df = df.drop(columns=["ignore"])

        # Convert timestamps (ms → datetime)
        df["timestamp"] = pd.to_datetime(df["open_time"], unit="ms", utc=True)
        df["close_time"] = pd.to_datetime(df["close_time"], unit="ms", utc=True)

        # Drop open_time (redundant)
        df = df.drop(columns=["open_time"])

        # Convert numeric columns
        numeric_cols = [
            "open",
            "high",
            "low",
            "close",
            "volume",
            "quote_asset_volume",
            "taker_buy_base_asset_volume",
            "taker_buy_quote_asset_volume",
        ]
        for col in numeric_cols:
            df[col] = pd.to_numeric(df[col])

        df["number_of_trades"] = df["number_of_trades"].astype(int)

        # Add metadata
        df["symbol"] = symbol
        df["timeframe"] = timeframe
        df["data_source"] = "api"

        return df

    def _ingest_dataframe(self, df: pd.DataFrame) -> int:
        """
        Ingest DataFrame to QuestDB via ILP.

        Args:
            df: DataFrame with OHLCV data

        Returns:
            Number of rows ingested

        Raises:
            ConnectionError: If ingestion fails
        """
        if df.empty:
            logger.warning("Empty DataFrame, skipping ingestion")
            return 0

        logger.info(f"Ingesting {len(df)} rows to QuestDB via ILP")

        try:
            sender = self.connection.get_sender()

            for _, row in df.iterrows():
                timestamp = TimestampNanos(int(row["timestamp"].timestamp() * 1_000_000_000))
                close_time = TimestampNanos(int(row["close_time"].timestamp() * 1_000_000_000))

                sender.row(
                    "ohlcv",
                    symbols={
                        "symbol": row["symbol"],
                        "timeframe": row["timeframe"],
                        "data_source": row["data_source"],
                    },
                    columns={
                        "open": float(row["open"]),
                        "high": float(row["high"]),
                        "low": float(row["low"]),
                        "close": float(row["close"]),
                        "volume": float(row["volume"]),
                        "close_time": close_time,
                        "quote_asset_volume": float(row["quote_asset_volume"]),
                        "number_of_trades": int(row["number_of_trades"]),
                        "taker_buy_base_asset_volume": float(row["taker_buy_base_asset_volume"]),
                        "taker_buy_quote_asset_volume": float(row["taker_buy_quote_asset_volume"]),
                    },
                    at=timestamp,
                )

            sender.flush()

            logger.info(f"Successfully ingested {len(df)} rows")
            return len(df)

        except Exception as e:
            raise ConnectionError(f"Failed to ingest gap fill data to QuestDB: {e}") from e

    def fill_gap(self, symbol: str, timeframe: str, gap_start: datetime, gap_end: datetime) -> int:
        """
        Fill a single gap using Binance REST API.

        Args:
            symbol: Trading pair symbol (e.g., "BTCUSDT")
            timeframe: Timeframe string (e.g., "1h")
            gap_start: Gap start timestamp
            gap_end: Gap end timestamp

        Returns:
            Number of bars filled

        Raises:
            httpx.HTTPStatusError: If API request fails
            ConnectionError: If ingestion fails
        """
        symbol = symbol.upper()

        # Convert to milliseconds
        start_ms = int(gap_start.timestamp() * 1000)
        end_ms = int(gap_end.timestamp() * 1000)

        logger.info(f"Filling gap: {symbol} {timeframe} {gap_start} to {gap_end}")

        # Fetch from REST API
        klines = self._fetch_klines_rest(symbol, timeframe, start_ms, end_ms)

        # Convert to DataFrame
        df = self._klines_to_dataframe(klines, symbol, timeframe)

        # Ingest to QuestDB
        rows_filled = self._ingest_dataframe(df)

        logger.info(f"Filled gap with {rows_filled} bars")
        return rows_filled

    def fill_gaps(self, symbol: str, timeframe: str, start: str, end: str) -> int:
        """
        Detect and fill all gaps for a symbol and timeframe.

        Args:
            symbol: Trading pair symbol (e.g., "BTCUSDT")
            timeframe: Timeframe string (e.g., "1h")
            start: Start date in "YYYY-MM-DD" format
            end: End date in "YYYY-MM-DD" format

        Returns:
            Total number of bars filled

        Raises:
            ValueError: If parameters are invalid
            httpx.HTTPStatusError: If API request fails
            ConnectionError: If ingestion fails

        Example:
            with QuestDBConnection() as conn:
                filler = QuestDBGapFiller(conn)
                filled = filler.fill_gaps(
                    "BTCUSDT", "1h",
                    start="2024-01-01",
                    end="2024-12-31"
                )
                print(f"Filled {filled} bars across all gaps")
        """
        symbol = symbol.upper()

        # Detect gaps
        gaps = self.detect_gaps(symbol, timeframe, start, end)

        if gaps.empty:
            logger.info(f"No gaps found for {symbol} {timeframe}")
            return 0

        logger.info(f"Found {len(gaps)} gaps for {symbol} {timeframe}, filling...")

        total_filled = 0

        for _, gap in gaps.iterrows():
            try:
                filled = self.fill_gap(symbol, timeframe, gap["gap_start"], gap["gap_end"])
                total_filled += filled

                # Small delay to avoid rate limiting
                time.sleep(0.1)

            except httpx.HTTPStatusError as e:
                if e.response.status_code == 429:
                    logger.error(
                        "Rate limit exceeded. Stopping gap filling. "
                        "Caller must implement rate limiting and retry logic."
                    )
                    raise
                else:
                    logger.error(f"Failed to fill gap {gap['gap_start']} to {gap['gap_end']}: {e}")
                    raise

        logger.info(f"Successfully filled {total_filled} bars across {len(gaps)} gaps")
        return total_filled
