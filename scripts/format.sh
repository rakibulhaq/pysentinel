#!/usr/bin/env bash
set -euo pipefail

# Format code using black

echo "Formatting code with black..."
poetry run black .
