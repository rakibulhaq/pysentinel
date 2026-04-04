#!/usr/bin/env bash
set -euo pipefail

# Build distribution packages using poetry

echo "Building package (sdist + wheel)..."
poetry build

echo "Built packages are in the dist/ directory"
