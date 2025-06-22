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

## Usage Examples

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


**Blocking usage with `start()`:**

```python
from pysentinel.core.scanner import Scanner

config = { ... }  # your configuration dictionary

scanner = Scanner(config)
scanner.start()  # This will block and run the scanner loop
```

**Async usage with `start_async()`:**

```python
import asyncio
from pysentinel.core.scanner import Scanner

config = { ... }  # your configuration dictionary

async def main():
    scanner = Scanner(config)
    await scanner.start_async()
    # Optionally, do other async tasks here

asyncio.run(main())
```

Replace `{ ... }` with your actual configuration.  
`start()` runs the scanner in the main thread and blocks, while `start_async()` allows integration with other async code.

## FastAPI Integration Example

```python
from fastapi import FastAPI
from pysentinel.core.scanner import Scanner

app = FastAPI()

config = {
    # ... your pysentinel configuration ...
}

scanner = Scanner(config)

@app.on_event("startup")
async def start_scanner():
    # Start the scanner in the background when FastAPI starts
    import asyncio
    await asyncio.create_task(scanner.start_async())

@app.get("/")
async def root():
    return {"message": "pysentinel FastAPI integration running"}
```
**This example shows how to integrate pysentinel with FastAPI, starting the scanner in the background when the application starts.**

## Configuration
Here’s how to use the `load_config()` function from `pysentinel.config.loader` to load your YAML config and start the scanner.  
This approach works for both YAML and JSON config files.

```python
import pysentinel.config.loader as loader
from pysentinel.core.scanner import Scanner

config = loader.load_config("config.yml")
scanner = Scanner(config)
scanner.start_background()
```

This will load your configuration from `config.yml` and start the scanner in the background.
## Example Configuration File in yml format
Here is an example `config.yml`:

See the full example config at [`tests/pysentinel/fixtures/config.yml`](tests/pysentinel/fixtures/config.yml).

This can be used as a reference for creating your own configuration in YAML format for `pysentinel`:

```yaml
global:
  alert_cooldown_minutes: 5

datasources:
  my_postgres:
    type: postgresql
    enabled: true
    host: localhost
    port: 5432
    database: mydb
    user: user
    password: pass

alert_channels:
  email_alerts:
    type: email
    enabled: true
    recipients:
      - admin@example.com
    smtp_server: smtp.example.com

alert_groups:
  critical_metrics:
    enabled: true
    alerts:
      - name: High CPU Usage
        metrics: cpu_usage
        query: SELECT cpu_usage FROM metrics WHERE time > now() - interval '1 minute'
        datasource: my_postgres
        threshold: 90
        severity: CRITICAL
        interval: 300  # seconds between checks
        alert_channels:
          - email_alerts
        description: CPU usage is above 90% for the last minute
```

This YAML config can be loaded using `load_config("config.yml")` and passed to the `Scanner`.
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