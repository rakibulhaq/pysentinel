#!/usr/bin/env bash
set -euo pipefail

# Run mypy if available. If not installed, print a helpful message.
if poetry run mypy --version >/dev/null 2>&1; then
  echo "Running mypy..."
  poetry run mypy pysentinel
else
  echo "mypy not found in the environment. Install mypy to enable typecheck target."
  exit 1
fi
