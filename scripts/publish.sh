#!/usr/bin/env bash
set -euo pipefail

# Publish package to PyPI using poetry. By default this publishes to PyPI.
# Set POETRY_REPOSITORY to a different repository alias if needed (e.g., testpypi)
# Example: POETRY_REPOSITORY=testpypi ./scripts/publish.sh

REPO_ARG=""
if [ -n "${POETRY_REPOSITORY:-}" ]; then
  REPO_ARG="--repository $POETRY_REPOSITORY"
fi

echo "Building and publishing package using poetry $REPO_ARG"
poetry publish --build $REPO_ARG
