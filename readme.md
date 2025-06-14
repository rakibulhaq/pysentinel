# pysentinel

pysentinel is a Python package for threshold-based alerting using simple configuration. It scans data sources and raises alerts when specified thresholds are crossed.

## Features

- Scan data sources for threshold violations
- Simple configuration for thresholds and alerts
- Easy integration into existing Python projects

## Installation

You can install pysentinel using [Poetry](https://python-poetry.org/) or `pip`.

### Using Poetry

```bash
poetry add pysentinel
```

### Using pip

```bash
pip install pysentinel
```

## Usage

```python
from pysentinel import Sentinel

# Example configuration
config = {
    "data_source": "path/to/data.csv",
    "thresholds": {
        "column1": 100,
        "column2": 50
    }
}

sentinel = Sentinel(config)
alerts = sentinel.scan()

if alerts:
    for alert in alerts:
        print(f"Alert: {alert}")
```

## Requirements

- Python >= 3.9, < 4.0

## Development

To set up the development environment:

```bash
poetry install
```

To run tests:

```bash
poetry run pytest
```

## License

MIT