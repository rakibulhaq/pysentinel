#!/usr/bin/env bash
set -euo pipefail

# Bump the package version in pyproject.toml.
# PART may be a bump rule (patch, minor, major, prepatch, preminor, premajor,
# prerelease) or an explicit version such as 1.2.3.
# Example: PART=minor ./scripts/bump.sh

PART="${PART:-patch}"

OLD_VERSION="$(poetry version -s)"
poetry version "$PART" >/dev/null
NEW_VERSION="$(poetry version -s)"

echo "Bumped version: $OLD_VERSION -> $NEW_VERSION"
