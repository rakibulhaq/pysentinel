#!/usr/bin/env bash
set -euo pipefail

# Run tests and produce coverage report (html + console)
ARGS="${PYTEST_EXTRA_ARGS:-}"

echo "Running tests with coverage..."
poetry run pytest --cov=pysentinel --cov-report=term-missing --cov-report=html $ARGS

echo "HTML coverage written to htmlcov/index.html"
