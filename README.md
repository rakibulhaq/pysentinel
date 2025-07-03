# PySentinel
![pysentinel logo](https://raw.githubusercontent.com/rakibulhaq/pysentinel/main/logo.png)
[![PyPI version](https://img.shields.io/pypi/v/pysentinel.svg)](https://pypi.org/project/pysentinel/)
[![Python versions](https://img.shields.io/pypi/pyversions/pysentinel.svg)](https://pypi.org/project/pysentinel/)
[![Codecov](https://codecov.io/gh/rakibulhaq/pysentinel/branch/main/graph/badge.svg)](https://codecov.io/gh/rakibulhaq/pysentinel)
[![Snyk](https://snyk.io/test/github/rakibulhaq/pysentinel/badge.svg)](https://snyk.io/test/github/rakibulhaq/pysentinel)
[![PyPI - Downloads](https://img.shields.io/pypi/dm/pysentinel.svg?label=PyPI%20downloads)](https://pypistats.org/packages/pysentinel)
[![Downloads](https://pepy.tech/badge/pysentinel)](https://pepy.tech/project/pysentinel)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)



PySentinel is a Python package for threshold-based alerting using simple configuration. It scans data sources and raises alerts when specified thresholds are crossed.


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

## CLI Installation & Usage

### Install from PyPI (Recommended)

```bash


```bash
# Install PySentinel with CLI support
pip install pysentinel

# Or using Poetry
poetry add pysentinel
```

After installation, the `pysentinel` command will be available in your terminal.

## CLI Usage

PySentinel provides a command-line interface for running the scanner with configuration files.

### Basic Usage

```bash
# Run scanner synchronously (blocking)
pysentinel config.yml

# Run scanner asynchronously (non-blocking)
pysentinel config.yml --async

# Use JSON configuration
pysentinel /path/to/config.json

# Show help
pysentinel --help

# Show version
pysentinel --version
```

### CLI Examples

```bash
# Start monitoring with 30-second intervals
pysentinel production-config.yml

# Run in background mode (async)
pysentinel monitoring.yml --async

# Use absolute path to config
pysentinel /etc/pysentinel/config.yml

# Quick help
pysentinel -h
```

### Exit Codes

- `0` - Success or user interrupted (Ctrl+C)
- `1` - Configuration or scanner error

## Docker Usage

### Running PySentinel CLI in Docker

You can run PySentinel inside a Docker container for isolated execution and easy deployment.

**Create a Dockerfile:**

```dockerfile
FROM python:3.11-slim

# Install PySentinel
RUN pip install pysentinel

# Create app directory
WORKDIR /app

# Copy configuration file
COPY config.yml /app/config.yml

# Run PySentinel CLI
CMD ["pysentinel", "config.yml"]
```
### Build and Run the Docker Container

```bash
# Build the Docker image
docker build -t pysentinel-app .

# Run synchronously
docker run --rm pysentinel-app

# Run asynchronously
docker run --rm pysentinel-app pysentinel config.yml --async

# Mount external config file
docker run --rm -v /path/to/your/config.yml:/app/config.yml pysentinel-app

# Run with environment variables for database connections
docker run --rm \
  -e DB_HOST=host.docker.internal \
  -e DB_PORT=5432 \
  -v /path/to/config.yml:/app/config.yml \
  pysentinel-app
```

### Docker Compose Example
create a `docker-compose.yml` file to run PySentinel with a PostgreSQL database:

```yaml
version: '3.8'

services:
  pysentinel:
    image: python:3.11-slim
    command: >
      sh -c "pip install pysentinel && 
             pysentinel /app/config.yml --async"
    volumes:
      - ./config.yml:/app/config.yml
      - ./logs:/app/logs
    environment:
      - DB_HOST=postgres
      - DB_USER=sentinel_user
      - DB_PASSWORD=sentinel_pass
    depends_on:
      - postgres
    restart: unless-stopped

  postgres:
    image: postgres:15
    environment:
      POSTGRES_DB: monitoring
      POSTGRES_USER: sentinel_user
      POSTGRES_PASSWORD: sentinel_pass
    volumes:
      - postgres_data:/var/lib/postgresql/data

volumes:
  postgres_data:
```
This `docker-compose.yml` sets up a PySentinel service that connects to a PostgreSQL database, allowing you to run the scanner with persistent data storage.

### Run with Docker Compose:

```bash
# Start the monitoring stack
docker-compose up -d

# View logs
docker-compose logs pysentinel

# Stop the stack
docker-compose down
```

### Production Docker Setup
Multi-sage Dockerfile for production use:

```dockerfile
FROM python:3.11-slim as builder

# Install dependencies
RUN pip install --no-cache-dir pysentinel

FROM python:3.11-slim

# Copy installed packages
COPY --from=builder /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages
COPY --from=builder /usr/local/bin/pysentinel /usr/local/bin/pysentinel

# Create non-root user
RUN useradd --create-home --shell /bin/bash sentinel

# Set working directory
WORKDIR /app

# Change ownership
RUN chown -R sentinel:sentinel /app

# Switch to non-root user
USER sentinel

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
  CMD pysentinel --version || exit 1

# Default command
CMD ["pysentinel", "config.yml", "--async"]
```

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