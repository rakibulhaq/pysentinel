#!/usr/bin/env bash
set -euo pipefail

# Try to run ruff if available, otherwise fallback to flake8 if installed.
# This project currently lists only development tools like black in pyproject, so
# users can install ruff/flake8 themselves.

if poetry run ruff --version >/dev/null 2>&1; then
  echo "Running ruff..."
  poetry run ruff check .
elif poetry run flake8 --version >/dev/null 2>&1; then
  echo "Running flake8..."
  poetry run flake8 .
else
  echo "No linter (ruff or flake8) found in the environment. Install one to enable lint target."
  exit 1
fi
