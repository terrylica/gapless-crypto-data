# Gapless Crypto Data

[![PyPI version](https://img.shields.io/pypi/v/gapless-crypto-data.svg)](https://pypi.org/project/gapless-crypto-data/)
[![GitHub release](https://img.shields.io/github/v/release/terrylica/gapless-crypto-data.svg)](https://github.com/terrylica/gapless-crypto-data/releases/latest)
[![Python Versions](https://img.shields.io/pypi/pyversions/gapless-crypto-data.svg)](https://pypi.org/project/gapless-crypto-data/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

Binance cryptocurrency data collection with zero-gap guarantee. Provides microstructure format through Binance public data repository with intelligent monthly-to-daily fallback.

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

# Fetch data with date range
df = gcd.download("BTCUSDT", timeframe="1h", start="2024-01-01", end="2024-06-30")

# Fetch data with limit
df = gcd.fetch_data("ETHUSDT", timeframe="4h", limit=1000)

# Get available symbols and timeframes
symbols = gcd.get_supported_symbols()
timeframes = gcd.get_supported_timeframes()

# Fill gaps in existing data
results = gcd.fill_gaps("./data")
```

## Data Format

Returns pandas DataFrames with microstructure columns. See [DATA_FORMAT.md](docs/architecture/DATA_FORMAT.md) for specification.

```python
df = gcd.download("BTCUSDT", timeframe="1h", start="2024-01-01", end="2024-06-30")
print(df.columns.tolist())
# ['date', 'open', 'high', 'low', 'close', 'volume',
#  'close_time', 'quote_asset_volume', 'number_of_trades',
#  'taker_buy_base_asset_volume', 'taker_buy_quote_asset_volume']
```

## Supported Timeframes

All Binance spot timeframes supported:

| Category | Timeframes |
|----------|------------|
| Sub-minute | `1s` |
| Minutes | `1m`, `3m`, `5m`, `15m`, `30m` |
| Hours | `1h`, `2h`, `4h`, `6h`, `8h`, `12h` |
| Daily | `1d` |

Query programmatically: `gcd.get_supported_timeframes()`

## API Reference

### Function-based API

```python
import gapless_crypto_data as gcd

# Data collection
df = gcd.download(symbol, timeframe, start, end)  # Date range
df = gcd.fetch_data(symbol, timeframe, limit)     # Recent data

# Discovery
symbols = gcd.get_supported_symbols()
timeframes = gcd.get_supported_timeframes()

# Gap management
results = gcd.fill_gaps(directory, symbols=None)
```

### Class-based API

```python
from gapless_crypto_data import BinancePublicDataCollector, UniversalGapFiller

# Custom collection
collector = BinancePublicDataCollector(
    symbol="BTCUSDT",
    start_date="2024-01-01",
    end_date="2024-06-30"
)
result = collector.collect_timeframe_data("1h")

# Gap filling
gap_filler = UniversalGapFiller()
gaps = gap_filler.detect_all_gaps(csv_file, "1h")
```

See [Python API Guide](docs/guides/python-api.md) for complete reference.

## AI Agent Integration

Probe hooks for programmatic discovery:

```python
import gapless_crypto_data
probe = gapless_crypto_data.__probe__

probe.discover_api()      # Function signatures
probe.get_capabilities()  # Symbols, timeframes
probe.get_task_graph()    # Workflow dependencies
```

See [llms.txt](/llms.txt) for AI agent instructions.

## Documentation

| Topic | Location |
|-------|----------|
| Architecture | [docs/architecture/OVERVIEW.md](docs/architecture/OVERVIEW.md) |
| Data Format | [docs/architecture/DATA_FORMAT.md](docs/architecture/DATA_FORMAT.md) |
| Python API | [docs/guides/python-api.md](docs/guides/python-api.md) |
| Data Collection | [docs/guides/DATA_COLLECTION.md](docs/guides/DATA_COLLECTION.md) |
| Validation | [docs/validation/OVERVIEW.md](docs/validation/OVERVIEW.md) |
| Development | [docs/development/SETUP.md](docs/development/SETUP.md) |

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

| Task | Command |
|------|---------|
| Test | `uv run pytest` |
| Format | `uv run ruff format .` |
| Lint | `uv run ruff check --fix .` |
| Type check | `uv run mypy src/` |
| Build | `uv build` |

See [Development Commands](docs/development/COMMANDS.md) for complete reference.

## Architecture

**Data Sources**:
- Binance Public Data Repository (primary)
- Binance API (gap filling)

**Core Components**:
- `BinancePublicDataCollector`: Data collection engine
- `UniversalGapFiller`: Gap detection and filling
- `AtomicCSVOperations`: Corruption-proof file operations

See [Architecture Overview](docs/architecture/OVERVIEW.md) for details.

## Requirements

- Python 3.9+
- pandas >= 2.0.0
- httpx >= 0.28.0

## License

MIT License - see [LICENSE](LICENSE).

## Specifications

Machine-readable specifications:

- [SDK_QUALITY_STANDARDS.yaml](docs/SDK_QUALITY_STANDARDS.yaml)
- [CURRENT_ARCHITECTURE_STATUS.yaml](docs/CURRENT_ARCHITECTURE_STATUS.yaml)
- [SSOT_DOCUMENTATION_ARCHITECTURE.yaml](docs/SSOT_DOCUMENTATION_ARCHITECTURE.yaml)
