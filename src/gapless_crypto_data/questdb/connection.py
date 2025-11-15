"""
QuestDB connection management for gapless-crypto-data v4.0.0.

Provides managed connections to QuestDB time-series database with environment-based configuration.
Supports both ILP (InfluxDB Line Protocol) for ingestion and PostgreSQL wire protocol for queries.

Architecture:
- ILP (port 9009): High-throughput data ingestion (>100K rows/sec)
- PostgreSQL (port 8812): SQL queries returning pandas DataFrames

Error Handling Policy:
- Raise and propagate all connection errors
- No fallbacks, no defaults, no retries
- Let callers handle connection failures explicitly

SLOs:
- Availability: Connection failures propagate to caller
- Correctness: No silent failures, explicit error states
- Observability: Connection context logged at DEBUG level
- Maintainability: Standard PostgreSQL wire protocol (psycopg3)

Usage:
    # Context manager (recommended)
    with QuestDBConnection() as conn:
        sender = conn.get_sender()
        sender.row('ohlcv', symbols={'symbol': 'BTCUSDT'}, columns={'open': 50000.0})
        sender.flush()

    # Manual connection management
    conn = QuestDBConnection()
    try:
        pg_conn = conn.get_pg_connection()
        df = pd.read_sql("SELECT * FROM ohlcv LIMIT 10", pg_conn)
    finally:
        conn.close()
"""

import logging
import os
from contextlib import contextmanager
from dataclasses import dataclass
from typing import Generator, Optional

import psycopg
from dotenv import load_dotenv
from questdb.ingress import Sender

# Load environment variables from .env file
load_dotenv()

logger = logging.getLogger(__name__)


@dataclass
class QuestDBConfig:
    """
    QuestDB connection configuration loaded from environment variables.

    Environment Variables:
        QUESTDB_HOST: QuestDB server hostname (default: localhost)
        QUESTDB_ILP_PORT: ILP protocol port (default: 9009)
        QUESTDB_HTTP_PORT: HTTP/Web Console port (default: 9000)
        QUESTDB_PG_PORT: PostgreSQL wire protocol port (default: 8812)
        QUESTDB_PG_USER: PostgreSQL username (default: admin)
        QUESTDB_PG_PASSWORD: PostgreSQL password (default: quest)
        QUESTDB_PG_DATABASE: PostgreSQL database name (default: qdb)

    Error Handling:
        - Missing environment variables use documented defaults
        - Invalid port numbers raise ValueError
        - No fallback mechanisms (fail fast)
    """

    host: str = os.getenv("QUESTDB_HOST", "localhost")
    ilp_port: int = int(os.getenv("QUESTDB_ILP_PORT", "9009"))
    http_port: int = int(os.getenv("QUESTDB_HTTP_PORT", "9000"))
    pg_port: int = int(os.getenv("QUESTDB_PG_PORT", "8812"))
    pg_user: str = os.getenv("QUESTDB_PG_USER", "admin")
    pg_password: str = os.getenv("QUESTDB_PG_PASSWORD", "quest")
    pg_database: str = os.getenv("QUESTDB_PG_DATABASE", "qdb")

    def __post_init__(self) -> None:
        """Validate configuration after initialization."""
        # Validate port ranges
        for port_name in ["ilp_port", "http_port", "pg_port"]:
            port_value = getattr(self, port_name)
            if not (1 <= port_value <= 65535):
                raise ValueError(f"Invalid {port_name}: {port_value}. Must be in range [1, 65535].")

        logger.debug(
            f"QuestDB config loaded: host={self.host}, "
            f"ilp_port={self.ilp_port}, pg_port={self.pg_port}"
        )

    @property
    def ilp_address(self) -> str:
        """ILP connection address in format 'tcp::host:port'."""
        return f"tcp::{self.host}:{self.ilp_port}"

    @property
    def pg_connection_string(self) -> str:
        """
        PostgreSQL connection string.

        Format: postgresql://user:password@host:port/database

        Security Note:
            Password is included in connection string. Ensure .env file
            has appropriate permissions (chmod 600 .env).
        """
        return (
            f"postgresql://{self.pg_user}:{self.pg_password}"
            f"@{self.host}:{self.pg_port}/{self.pg_database}"
        )


class QuestDBConnection:
    """
    Managed QuestDB connection providing ILP ingestion and PostgreSQL queries.

    Supports context manager protocol for automatic resource cleanup.

    Attributes:
        config: QuestDB connection configuration
        _sender: Cached ILP sender (created lazily)
        _pg_conn: Cached PostgreSQL connection (created lazily)

    Error Handling:
        - Connection failures raise ConnectionError
        - Invalid configuration raises ValueError
        - No automatic reconnection (caller must handle)

    SLO Compliance:
        - Availability: Failures propagate to caller for explicit handling
        - Correctness: No silent connection failures
        - Observability: Connection lifecycle logged at DEBUG level
        - Maintainability: Standard PostgreSQL protocol (psycopg3)

    Examples:
        # ILP ingestion
        with QuestDBConnection() as conn:
            sender = conn.get_sender()
            sender.row(
                'ohlcv',
                symbols={'symbol': 'BTCUSDT', 'timeframe': '1m'},
                columns={
                    'open': 50000.0,
                    'high': 50100.0,
                    'low': 49900.0,
                    'close': 50050.0,
                    'volume': 123.45
                },
                at=TimestampNanos.now()
            )
            sender.flush()

        # PostgreSQL query
        with QuestDBConnection() as conn:
            pg_conn = conn.get_pg_connection()
            with pg_conn.cursor() as cur:
                cur.execute("SELECT COUNT(*) FROM ohlcv")
                count = cur.fetchone()[0]
                print(f"Total rows: {count}")
    """

    def __init__(self, config: Optional[QuestDBConfig] = None) -> None:
        """
        Initialize QuestDB connection manager.

        Args:
            config: QuestDB configuration. If None, loads from environment.

        Raises:
            ValueError: If configuration is invalid
        """
        self.config = config or QuestDBConfig()
        self._sender: Optional[Sender] = None
        self._pg_conn: Optional[psycopg.Connection] = None

        logger.debug(f"QuestDB connection manager initialized: {self.config.host}")

    def get_sender(self) -> Sender:
        """
        Get ILP sender for high-throughput data ingestion.

        Sender is created lazily on first call and cached for reuse.

        Returns:
            questdb.ingress.Sender for ILP data ingestion

        Raises:
            ConnectionError: If ILP connection fails

        Performance:
            - Throughput: >100K rows/sec for OHLCV data
            - Protocol: InfluxDB Line Protocol over TCP
            - Buffering: Auto-flush on buffer full or explicit flush()

        Example:
            sender = conn.get_sender()
            sender.row(
                'ohlcv',
                symbols={'symbol': 'BTCUSDT'},
                columns={'open': 50000.0},
                at=TimestampNanos.now()
            )
            sender.flush()  # Explicit flush
        """
        if self._sender is None:
            try:
                self._sender = Sender.from_uri(self.config.ilp_address)
                logger.debug(f"ILP sender created: {self.config.ilp_address}")
            except Exception as e:
                raise ConnectionError(
                    f"Failed to create QuestDB ILP sender at {self.config.ilp_address}: {e}"
                ) from e

        return self._sender

    def get_pg_connection(self) -> psycopg.Connection:
        """
        Get PostgreSQL connection for SQL queries.

        Connection is created lazily on first call and cached for reuse.

        Returns:
            psycopg.Connection for SQL queries

        Raises:
            ConnectionError: If PostgreSQL connection fails

        Performance:
            - Query latency: <1s for typical OHLCV range queries
            - Protocol: PostgreSQL wire protocol (port 8812)
            - Cursor: Use context manager for automatic cleanup

        Example:
            pg_conn = conn.get_pg_connection()
            with pg_conn.cursor() as cur:
                cur.execute(
                    "SELECT * FROM ohlcv WHERE symbol = %s LIMIT 10",
                    ("BTCUSDT",)
                )
                rows = cur.fetchall()
        """
        if self._pg_conn is None or self._pg_conn.closed:
            try:
                self._pg_conn = psycopg.connect(
                    self.config.pg_connection_string,
                    autocommit=True,  # QuestDB doesn't use transactions
                )
                logger.debug(
                    f"PostgreSQL connection created: {self.config.host}:{self.config.pg_port}"
                )
            except Exception as e:
                raise ConnectionError(
                    f"Failed to connect to QuestDB PostgreSQL at "
                    f"{self.config.host}:{self.config.pg_port}: {e}"
                ) from e

        return self._pg_conn

    def close(self) -> None:
        """
        Close all connections (ILP sender and PostgreSQL).

        Idempotent - safe to call multiple times.

        Raises:
            Exception: Propagates any errors during connection closure
        """
        if self._sender is not None:
            try:
                self._sender.close()
                logger.debug("ILP sender closed")
            except Exception as e:
                logger.error(f"Error closing ILP sender: {e}")
                raise
            finally:
                self._sender = None

        if self._pg_conn is not None and not self._pg_conn.closed:
            try:
                self._pg_conn.close()
                logger.debug("PostgreSQL connection closed")
            except Exception as e:
                logger.error(f"Error closing PostgreSQL connection: {e}")
                raise
            finally:
                self._pg_conn = None

    def __enter__(self) -> "QuestDBConnection":
        """Context manager entry."""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        """Context manager exit - ensures connections are closed."""
        self.close()


@contextmanager
def questdb_connection(
    config: Optional[QuestDBConfig] = None,
) -> Generator[QuestDBConnection, None, None]:
    """
    Context manager for QuestDB connections with automatic cleanup.

    Convenience wrapper around QuestDBConnection context manager.

    Args:
        config: QuestDB configuration. If None, loads from environment.

    Yields:
        QuestDBConnection instance

    Raises:
        ConnectionError: If connection fails
        ValueError: If configuration is invalid

    Example:
        with questdb_connection() as conn:
            sender = conn.get_sender()
            sender.row('ohlcv', symbols={'symbol': 'BTCUSDT'}, columns={'open': 50000.0})
            sender.flush()
    """
    conn = QuestDBConnection(config)
    try:
        yield conn
    finally:
        conn.close()
