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
from pysentinel.core.scanner import Scanner

# Example configuration
config = {
    "global": {
        "alert_cooldown_minutes": 5
    },
    "datasources": {
        "my_postgres": {
            "type": "postgresql",
            "enabled": True,
            "host": "localhost",
            "port": 5432,
            "database": "mydb",
            "user": "user",
            "password": "pass"
        }
    },
    "alert_channels": {
        "email_alerts": {
            "type": "email",
            "enabled": True,
            "recipients": ["admin@example.com"],
            "smtp_server": "smtp.example.com"
        }
    },
    "alert_groups": {
        "critical_metrics": {
            "enabled": True,
            "alerts": [
                {
                    "name": "High CPU Usage",
                    "metrics": "cpu_usage",
                    "query": "SELECT cpu_usage FROM metrics WHERE time > now() - interval '1 minute'",
                    "datasource": "my_postgres",
                    "threshold": 90,
                    "severity": "CRITICAL",
                    "interval": 300,  # seconds between checks
                    "alert_channels": ["email_alerts"],
                    "description": "CPU usage is above 90% for the last minute"
                }
            ]
        }
    }
}

scanner = Scanner(config)
scanner.start_background()

# The scanner will now run in the background, checking alerts at configured intervals.
# Alert evaluation intervals and last run times are persisted in a local SQLite database (alerts.db).
```
This example shows how to configure and start the scanner, with alert intervals and persistent runtime tracking.

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