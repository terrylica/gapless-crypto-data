"""
QuestDB integration for gapless-crypto-data v4.0.0.

Provides connection management, data ingestion, and query interfaces for QuestDB time-series database.

Modules:
    connection: QuestDB connection management with ILP and PostgreSQL support

Public API:
    QuestDBConnection: Managed connection with context manager support
    QuestDBConfig: Environment-based configuration
    questdb_connection: Context manager convenience function
"""

from .connection import QuestDBConfig, QuestDBConnection, questdb_connection

__all__ = [
    "QuestDBConnection",
    "QuestDBConfig",
    "questdb_connection",
]
