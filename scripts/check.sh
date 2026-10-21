#!/usr/bin/env bash
set -euo pipefail

# Run the same checks as CI: formatting, lint, typecheck and tests with coverage.

echo "Checking formatting with black..."
poetry run black --check .

bash scripts/lint.sh
bash scripts/typecheck.sh

echo "Running tests with coverage..."
poetry run pytest --cov=pysentinel --cov-report=xml --cov-report=term-missing -q
