# Gapless Crypto Data

[![PyPI version](https://img.shields.io/pypi/v/gapless-crypto-data.svg)](https://pypi.org/project/gapless-crypto-data/)
[![Python Versions](https://img.shields.io/pypi/pyversions/gapless-crypto-data.svg)](https://pypi.org/project/gapless-crypto-data/)
[![Downloads](https://img.shields.io/pypi/dm/gapless-crypto-data.svg)](https://pypi.org/project/gapless-crypto-data/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

Cryptocurrency OHLCV data collection with gap-free guarantee. Retrieves microstructure-enriched kline data from Binance Public Data Repository with automatic gap detection and filling.

## Installation

```bash
# UV (recommended)
uv add gapless-crypto-data

# pip
pip install gapless-crypto-data
```

## Quick Start

```python
import gapless_crypto_data as gcd

# Fetch historical data
df = gcd.download("BTCUSDT", timeframe="1h", start="2024-01-01", end="2024-06-30")

# Fetch recent data with limit
df = gcd.fetch_data("ETHUSDT", timeframe="4h", limit=1000)

# Get available symbols and timeframes
symbols = gcd.get_supported_symbols()
timeframes = gcd.get_supported_timeframes()

# Fill gaps in existing data directory
results = gcd.fill_gaps("./data")
```

## Data Format

Returns pandas DataFrames with microstructure columns:

| Column                         | Type       | Description              |
| ------------------------------ | ---------- | ------------------------ |
| `date`                         | datetime64 | Period open timestamp    |
| `open`, `high`, `low`, `close` | float64    | OHLC prices              |
| `volume`                       | float64    | Base asset volume        |
| `close_time`                   | datetime64 | Period close timestamp   |
| `quote_asset_volume`           | float64    | Quote asset volume       |
| `number_of_trades`             | int64      | Trade count              |
| `taker_buy_base_asset_volume`  | float64    | Taker buy volume (base)  |
| `taker_buy_quote_asset_volume` | float64    | Taker buy volume (quote) |

See [Data Format Specification](https://github.com/terrylica/gapless-crypto-data/blob/main/docs/architecture/DATA_FORMAT.md) for column semantics and constraints.

## Supported Timeframes

All Binance spot kline intervals. Query dynamically:

```python
import gapless_crypto_data as gcd
print(gcd.get_supported_timeframes())
```

## API Reference

### Function-based API

```python
import gapless_crypto_data as gcd

# Primary collection function
df = gcd.download(symbol, timeframe, start, end)
df = gcd.fetch_data(symbol, timeframe, limit=None, start=None, end=None)

# Gap filling
results = gcd.fill_gaps(directory, symbols=None)

# Discovery
symbols = gcd.get_supported_symbols()
timeframes = gcd.get_supported_timeframes()
```

### Class-based API

```python
from gapless_crypto_data import BinancePublicDataCollector, UniversalGapFiller

# Data collection with full control
collector = BinancePublicDataCollector(
    symbol="BTCUSDT",
    start_date="2024-01-01",
    end_date="2024-12-31"
)
result = collector.collect_timeframe_data("1h")
df = result["dataframe"]

# Gap detection and filling
gap_filler = UniversalGapFiller()
gaps = gap_filler.detect_all_gaps(csv_file, timeframe)
result = gap_filler.process_file(csv_file, timeframe)
```

Full API documentation: [Python API Reference](https://github.com/terrylica/gapless-crypto-data/blob/main/docs/guides/python-api.md)

## Data Sources

| Source                         | Method                     | Use Case                   |
| ------------------------------ | -------------------------- | -------------------------- |
| Binance Public Data Repository | Monthly/daily ZIP archives | Historical bulk collection |
| Binance REST API               | Per-request klines         | Gap filling, recent data   |

Collection strategy: Repository archives for bulk historical data, API for gaps and recent periods. See [Data Collection Guide](https://github.com/terrylica/gapless-crypto-data/blob/main/docs/guides/DATA_COLLECTION.md).

## AI Agent Integration

Programmatic discovery via `__probe__` module:

```python
import gapless_crypto_data
probe = gapless_crypto_data.__probe__

# API discovery
probe.discover_api()
probe.get_capabilities()
probe.get_task_graph()
```

See [Probe Usage](https://github.com/terrylica/gapless-crypto-data/blob/main/PROBE_USAGE_EXAMPLE.md) for AI agent integration patterns.

## Development

### Setup

```bash
git clone https://github.com/terrylica/gapless-crypto-data.git
cd gapless-crypto-data
uv venv && source .venv/bin/activate
uv sync --dev
uv run pre-commit install
```

### Commands

| Task       | Command                     |
| ---------- | --------------------------- |
| Run tests  | `uv run pytest`             |
| Format     | `uv run ruff format .`      |
| Lint       | `uv run ruff check --fix .` |
| Type check | `uv run mypy src/`          |
| Build      | `uv build`                  |

### Project Structure

```
src/gapless_crypto_data/
├── __init__.py          # Package exports
├── api.py               # Function-based API
├── __probe__.py         # AI agent discovery
├── collectors/          # Data collection
├── gap_filling/         # Gap detection/filling
└── validation/          # Data validation
```

Full development guide: [Development Setup](https://github.com/terrylica/gapless-crypto-data/blob/main/docs/development/SETUP.md)

## Architecture

- **BinancePublicDataCollector**: Bulk data retrieval from public repository
- **UniversalGapFiller**: Gap detection and API-based filling
- **AtomicCSVOperations**: Corruption-proof file operations
- **ValidationStorage**: DuckDB-backed validation persistence

Architecture documentation: [Overview](https://github.com/terrylica/gapless-crypto-data/blob/main/docs/architecture/OVERVIEW.md)

## License

MIT License - see [LICENSE](https://github.com/terrylica/gapless-crypto-data/blob/main/LICENSE)

## Links

- [PyPI Package](https://pypi.org/project/gapless-crypto-data/)
- [GitHub Repository](https://github.com/terrylica/gapless-crypto-data)
- [Issue Tracker](https://github.com/terrylica/gapless-crypto-data/issues)
- [Changelog](https://github.com/terrylica/gapless-crypto-data/blob/main/CHANGELOG.md)
