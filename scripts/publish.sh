#!/usr/bin/env bash
set -euo pipefail

# Build and publish the package using poetry. By default this publishes to PyPI.
# Set POETRY_REPOSITORY to a different repository alias if needed (e.g., testpypi)
# Example: POETRY_REPOSITORY=testpypi ./scripts/publish.sh
#
# Publishing to PyPI requires a clean working tree whose HEAD is tagged with
# v<version> (as created by `make release`). Set SKIP_RELEASE_CHECK=1 to bypass.

VERSION="$(poetry version -s)"
TAG="v$VERSION"

if [ -z "${POETRY_REPOSITORY:-}" ] && [ "${SKIP_RELEASE_CHECK:-0}" != "1" ]; then
  if [ -n "$(git status --porcelain)" ]; then
    echo "Working tree is not clean. Refusing to publish $VERSION."
    exit 1
  fi
  if [ "$(git tag --points-at HEAD | grep -cx "$TAG")" = "0" ]; then
    echo "HEAD is not tagged $TAG. Run 'make release' first."
    exit 1
  fi
fi

REPO_ARGS=()
if [ -n "${POETRY_REPOSITORY:-}" ]; then
  REPO_ARGS=(--repository "$POETRY_REPOSITORY")
fi

rm -rf dist/
echo "Building and publishing pysentinel $VERSION ${REPO_ARGS[*]:-to PyPI}"
poetry publish --build "${REPO_ARGS[@]+"${REPO_ARGS[@]}"}"
