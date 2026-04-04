#!/usr/bin/env bash
set -euo pipefail

# Run tests with pytest

# Allow PYTEST_EXTRA_ARGS to be passed through
ARGS="${PYTEST_EXTRA_ARGS:-}"

echo "Running tests with pytest..."
poetry run pytest $ARGS
