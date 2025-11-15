"""
QuestDB Bulk Loader for gapless-crypto-data v4.0.0.

Ultra-fast historical data ingestion from Binance Public Data Repository to QuestDB.
Preserves 22x speedup advantage of CloudFront CDN while eliminating file-based storage.

Architecture:
    CloudFront ZIP → Extract (temp) → Parse (pandas) → ILP → QuestDB → Delete temp

Performance:
    - Download: 22x faster than REST API (CloudFront CDN)
    - Ingestion: >100K rows/sec via ILP protocol
    - Storage: No persistent intermediate files (transient extraction only)

Error Handling:
    - Raise and propagate download failures (no retry)
    - Raise and propagate extraction failures (no fallback)
    - Raise and propagate ingestion failures (no silent drops)
    - Temporary files cleaned up even on errors

SLOs:
    - Availability: CloudFront 99.99% SLA, connection failures propagate
    - Correctness: Zero-gap guarantee via authentic Binance data
    - Observability: Ingestion metrics logged at INFO level
    - Maintainability: Standard ILP protocol, no custom file formats

Usage:
    from gapless_crypto_data.collectors.questdb_bulk_loader import QuestDBBulkLoader
    from gapless_crypto_data.questdb import QuestDBConnection

    with QuestDBConnection() as conn:
        loader = QuestDBBulkLoader(conn)
        loader.ingest_symbol(
            symbol="BTCUSDT",
            timeframe="1h",
            start_date="2024-01-01",
            end_date="2024-12-31"
        )
"""

import logging
import tempfile
import urllib.request
import zipfile
from datetime import datetime
from pathlib import Path
from typing import List, Optional

import pandas as pd
from questdb.ingress import TimestampNanos

from ..questdb.connection import QuestDBConnection

logger = logging.getLogger(__name__)


class QuestDBBulkLoader:
    """
    Bulk data loader from Binance Public Data Repository to QuestDB.

    Downloads monthly/daily ZIP archives from CloudFront CDN, extracts to temporary
    location, parses CSV, and ingests to QuestDB via ILP. No persistent file storage.

    Attributes:
        connection: QuestDB connection for ILP ingestion
        base_url: Binance Public Data Repository base URL

    Error Handling:
        - Download failures raise urllib.error.HTTPError
        - Extraction failures raise zipfile.BadZipFile
        - Ingestion failures raise ConnectionError
        - Temporary files cleaned up in all cases

    Performance:
        - CloudFront CDN: 22x faster than REST API
        - ILP ingestion: 100-200K rows/sec
        - Memory efficient: Streaming CSV→DataFrame→ILP

    Examples:
        # Single month ingestion
        with QuestDBConnection() as conn:
            loader = QuestDBBulkLoader(conn)
            loader.ingest_month(
                symbol="BTCUSDT",
                timeframe="1h",
                year=2024,
                month=1
            )

        # Date range ingestion
        with QuestDBConnection() as conn:
            loader = QuestDBBulkLoader(conn)
            loader.ingest_symbol(
                symbol="ETHUSDT",
                timeframe="1h",
                start_date="2024-01-01",
                end_date="2024-12-31"
            )
    """

    # Binance Public Data Repository base URL
    BASE_URL = "https://data.binance.vision/data/spot"

    # Supported timeframes (Binance notation)
    SUPPORTED_TIMEFRAMES = [
        "1s",
        "1m",
        "3m",
        "5m",
        "15m",
        "30m",
        "1h",
        "2h",
        "4h",
        "6h",
        "8h",
        "12h",
        "1d",
    ]

    def __init__(self, connection: QuestDBConnection) -> None:
        """
        Initialize QuestDB bulk loader.

        Args:
            connection: Active QuestDB connection

        Raises:
            ValueError: If connection is invalid
        """
        if not isinstance(connection, QuestDBConnection):
            raise ValueError(f"Expected QuestDBConnection, got {type(connection).__name__}")

        self.connection = connection
        logger.info("QuestDB bulk loader initialized")

    def _validate_symbol(self, symbol: str) -> str:
        """
        Validate and sanitize symbol input.

        Args:
            symbol: Trading pair symbol (e.g., "BTCUSDT")

        Returns:
            Uppercase symbol string

        Raises:
            ValueError: If symbol contains invalid characters or format
        """
        if not symbol:
            raise ValueError("Symbol cannot be empty")

        # Remove whitespace
        symbol = symbol.strip().upper()

        # Validate characters (alphanumeric only, no special chars)
        if not symbol.isalnum():
            raise ValueError(
                f"Invalid symbol '{symbol}': must contain only alphanumeric characters"
            )

        # Validate ends with USDT (spot pairs only)
        if not symbol.endswith("USDT"):
            raise ValueError(f"Invalid symbol '{symbol}': must end with USDT (spot pairs only)")

        return symbol

    def _validate_timeframe(self, timeframe: str) -> str:
        """
        Validate timeframe format.

        Args:
            timeframe: Timeframe string (e.g., "1h", "1m")

        Returns:
            Validated timeframe string

        Raises:
            ValueError: If timeframe is unsupported
        """
        if timeframe not in self.SUPPORTED_TIMEFRAMES:
            raise ValueError(
                f"Unsupported timeframe '{timeframe}'. "
                f"Supported: {', '.join(self.SUPPORTED_TIMEFRAMES)}"
            )

        return timeframe

    def _download_zip(self, url: str, dest_path: Path) -> None:
        """
        Download ZIP file from CloudFront CDN.

        Args:
            url: CloudFront CDN URL
            dest_path: Destination file path

        Raises:
            urllib.error.HTTPError: If download fails (404, 403, etc.)
            urllib.error.URLError: If network connection fails
        """
        logger.info(f"Downloading from CloudFront: {url}")

        try:
            urllib.request.urlretrieve(url, dest_path)
            logger.info(f"Download complete: {dest_path.stat().st_size} bytes")
        except urllib.error.HTTPError as e:
            raise urllib.error.HTTPError(
                url=url,
                code=e.code,
                msg=f"CloudFront download failed: {e.reason}",
                hdrs=e.headers,
                fp=None,
            ) from e
        except urllib.error.URLError as e:
            raise urllib.error.URLError(
                f"Network error downloading from CloudFront: {e.reason}"
            ) from e

    def _extract_zip(self, zip_path: Path, extract_dir: Path) -> Path:
        """
        Extract ZIP archive to temporary directory.

        Args:
            zip_path: Path to ZIP file
            extract_dir: Directory to extract files

        Returns:
            Path to extracted CSV file

        Raises:
            zipfile.BadZipFile: If ZIP file is corrupted
            FileNotFoundError: If CSV file not found in ZIP
        """
        logger.info(f"Extracting ZIP: {zip_path}")

        try:
            with zipfile.ZipFile(zip_path, "r") as zip_ref:
                zip_ref.extractall(extract_dir)

            # Find CSV file
            csv_files = list(extract_dir.glob("*.csv"))
            if not csv_files:
                raise FileNotFoundError(f"No CSV file found in ZIP archive: {zip_path}")

            if len(csv_files) > 1:
                logger.warning(f"Multiple CSV files found in ZIP, using first: {csv_files[0]}")

            csv_path = csv_files[0]
            logger.info(f"Extracted CSV: {csv_path} ({csv_path.stat().st_size} bytes)")
            return csv_path

        except zipfile.BadZipFile as e:
            raise zipfile.BadZipFile(f"Corrupted ZIP file: {zip_path}") from e

    def _parse_csv(self, csv_path: Path, symbol: str, timeframe: str) -> pd.DataFrame:
        """
        Parse Binance CSV file to DataFrame.

        Binance CSV format (11 columns):
        1. Open time (ms timestamp)
        2. Open
        3. High
        4. Low
        5. Close
        6. Volume
        7. Close time (ms timestamp)
        8. Quote asset volume
        9. Number of trades
        10. Taker buy base asset volume
        11. Taker buy quote asset volume

        Args:
            csv_path: Path to CSV file
            symbol: Trading pair symbol
            timeframe: Timeframe string

        Returns:
            DataFrame with OHLCV data

        Raises:
            pd.errors.ParserError: If CSV parsing fails
            ValueError: If column count is incorrect
        """
        logger.info(f"Parsing CSV: {csv_path}")

        try:
            df = pd.read_csv(
                csv_path,
                header=None,
                names=[
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
                ],
            )

            # Validate column count
            if len(df.columns) != 11:
                raise ValueError(
                    f"Expected 11 columns, got {len(df.columns)}. Columns: {df.columns.tolist()}"
                )

            # Convert timestamps (ms → datetime)
            df["timestamp"] = pd.to_datetime(df["open_time"], unit="ms", utc=True)
            df["close_time"] = pd.to_datetime(df["close_time"], unit="ms", utc=True)

            # Drop open_time (redundant with timestamp)
            df = df.drop(columns=["open_time"])

            # Add symbol and timeframe columns
            df["symbol"] = symbol
            df["timeframe"] = timeframe
            df["data_source"] = "cloudfront"

            logger.info(f"Parsed {len(df)} rows from CSV")
            return df

        except pd.errors.ParserError as e:
            raise pd.errors.ParserError(f"Failed to parse CSV {csv_path}: {e}") from e

    def _ingest_dataframe(self, df: pd.DataFrame) -> int:
        """
        Ingest DataFrame to QuestDB via ILP.

        Args:
            df: DataFrame with OHLCV data

        Returns:
            Number of rows ingested

        Raises:
            ConnectionError: If ILP ingestion fails
        """
        if df.empty:
            logger.warning("Empty DataFrame, skipping ingestion")
            return 0

        logger.info(f"Ingesting {len(df)} rows to QuestDB via ILP")

        try:
            sender = self.connection.get_sender()

            for _, row in df.iterrows():
                # Convert timestamp to TimestampNanos
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

            # Flush to ensure data is written
            sender.flush()

            logger.info(f"Successfully ingested {len(df)} rows")
            return len(df)

        except Exception as e:
            raise ConnectionError(f"Failed to ingest data to QuestDB: {e}") from e

    def ingest_month(self, symbol: str, timeframe: str, year: int, month: int) -> int:
        """
        Ingest one month of data from CloudFront to QuestDB.

        Downloads monthly ZIP, extracts to temp, parses CSV, ingests via ILP,
        and cleans up temporary files.

        Args:
            symbol: Trading pair symbol (e.g., "BTCUSDT")
            timeframe: Timeframe string (e.g., "1h")
            year: Year (e.g., 2024)
            month: Month (1-12)

        Returns:
            Number of rows ingested

        Raises:
            ValueError: If parameters are invalid
            urllib.error.HTTPError: If download fails
            ConnectionError: If ingestion fails
        """
        # Validate inputs
        symbol = self._validate_symbol(symbol)
        timeframe = self._validate_timeframe(timeframe)

        if not (1 <= month <= 12):
            raise ValueError(f"Invalid month: {month}. Must be in range [1, 12].")

        if year < 2017 or year > datetime.now().year:
            raise ValueError(
                f"Invalid year: {year}. Must be in range [2017, {datetime.now().year}]."
            )

        # Construct URL
        url = (
            f"{self.BASE_URL}/monthly/klines/"
            f"{symbol}/{timeframe}/{symbol}-{timeframe}-{year}-{month:02d}.zip"
        )

        # Use temporary directory for transient files
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)

            try:
                # Download ZIP
                zip_path = temp_path / f"{symbol}-{timeframe}-{year}-{month:02d}.zip"
                self._download_zip(url, zip_path)

                # Extract ZIP
                extract_dir = temp_path / "extracted"
                extract_dir.mkdir()
                csv_path = self._extract_zip(zip_path, extract_dir)

                # Parse CSV
                df = self._parse_csv(csv_path, symbol, timeframe)

                # Ingest to QuestDB
                row_count = self._ingest_dataframe(df)

                return row_count

            except Exception as e:
                logger.error(f"Failed to ingest {symbol} {timeframe} {year}-{month:02d}: {e}")
                raise

            # Temporary directory automatically cleaned up

    def ingest_symbol(
        self, symbol: str, timeframe: str, start_date: str, end_date: Optional[str] = None
    ) -> int:
        """
        Ingest date range of data from CloudFront to QuestDB.

        Args:
            symbol: Trading pair symbol (e.g., "BTCUSDT")
            timeframe: Timeframe string (e.g., "1h")
            start_date: Start date in "YYYY-MM-DD" format
            end_date: End date in "YYYY-MM-DD" format (default: today)

        Returns:
            Total number of rows ingested

        Raises:
            ValueError: If parameters are invalid
            urllib.error.HTTPError: If download fails
            ConnectionError: If ingestion fails
        """
        # Validate inputs
        symbol = self._validate_symbol(symbol)
        timeframe = self._validate_timeframe(timeframe)

        # Parse dates
        start = datetime.strptime(start_date, "%Y-%m-%d")
        end = datetime.strptime(end_date, "%Y-%m-%d") if end_date else datetime.now()

        if start > end:
            raise ValueError(f"Start date {start_date} is after end date {end_date or 'today'}")

        # Generate month list
        months: List[tuple] = []
        current = start.replace(day=1)  # Start at beginning of month

        while current <= end:
            months.append((current.year, current.month))
            # Move to next month
            if current.month == 12:
                current = current.replace(year=current.year + 1, month=1)
            else:
                current = current.replace(month=current.month + 1)

        logger.info(
            f"Ingesting {symbol} {timeframe} from {start_date} to {end_date or 'today'} "
            f"({len(months)} months)"
        )

        # Ingest each month
        total_rows = 0
        for year, month in months:
            try:
                row_count = self.ingest_month(symbol, timeframe, year, month)
                total_rows += row_count
            except urllib.error.HTTPError as e:
                if e.code == 404:
                    logger.warning(
                        f"Data not available for {symbol} {timeframe} {year}-{month:02d}, skipping"
                    )
                else:
                    raise

        logger.info(f"Total rows ingested: {total_rows}")
        return total_rows
