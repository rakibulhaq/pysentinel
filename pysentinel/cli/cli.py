#!/usr/bin/env python3
"""
PySentinel CLI - Command line interface for running the scanner
"""
import argparse
import asyncio
import sys
from pathlib import Path

from pysentinel.core.scanner import Scanner
from pysentinel.config.loader import load_config


def start_scanner_sync(config_path: str) -> None:
    """Start the scanner synchronously (blocking)"""
    try:
        config = load_config(config_path)
        scanner = Scanner(config)
        print(f"Starting PySentinel scanner with config: {config_path}")
        scanner.start()
    except KeyboardInterrupt:
        print("\nScanner stopped by user")
        sys.exit(0)
    except Exception as e:
        print(f"Error starting scanner: {e}")
        sys.exit(1)


async def start_scanner_async(config_path: str) -> None:
    """Start the scanner asynchronously"""
    try:
        config = load_config(config_path)
        scanner = Scanner(config)
        print(f"Starting PySentinel scanner (async) with config: {config_path}")
        await scanner.start_async()
    except KeyboardInterrupt:
        print("\nScanner stopped by user")
        sys.exit(0)
    except Exception as e:
        print(f"Error starting scanner: {e}")
        sys.exit(1)


def validate_config_file(config_path: str) -> str:
    """Validate that the config file exists"""
    path = Path(config_path)
    if not path.exists():
        raise argparse.ArgumentTypeError(f"Config file '{config_path}' does not exist")
    if not path.is_file():
        raise argparse.ArgumentTypeError(f"'{config_path}' is not a file")
    return str(path)


def main() -> None:
    """Main CLI entry point"""
    parser = argparse.ArgumentParser(
        description="PySentinel - Threshold-based alerting scanner",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  pysentinel config.yml                 # Run synchronously
  pysentinel config.yml --async         # Run asynchronously
  pysentinel /path/to/config.json       # Use JSON config
        """,
    )

    parser.add_argument(
        "config",
        type=validate_config_file,
        help="Path to configuration file (YAML or JSON)",
    )

    parser.add_argument(
        "--async",
        dest="run_async",
        action="store_true",
        help="Run scanner asynchronously (non-blocking)",
    )

    parser.add_argument("--version", action="version", version="PySentinel CLI 0.1.0")

    # Additional validation for async mode
    if len(sys.argv) > 1 and "--async" in sys.argv and sys.version_info < (3, 7):
        parser.error("Asynchronous mode requires Python 3.7 or higher")

    args = parser.parse_args()

    if args.run_async:
        asyncio.run(start_scanner_async(args.config))
    else:
        start_scanner_sync(args.config)


if __name__ == "__main__":
    main()
