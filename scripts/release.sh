#!/usr/bin/env bash
set -euo pipefail

# Cut a release: run all checks, bump the version, commit and tag it.
# Nothing is pushed unless PUSH=1 is set.
# Example: PART=minor PUSH=1 ./scripts/release.sh

PART="${PART:-patch}"
PUSH="${PUSH:-0}"

if [ -n "$(git status --porcelain)" ]; then
  echo "Working tree is not clean. Commit or stash your changes before releasing."
  exit 1
fi

echo "Running checks before release..."
bash scripts/check.sh

PART="$PART" bash scripts/bump.sh
VERSION="$(poetry version -s)"
TAG="v$VERSION"

if git rev-parse -q --verify "refs/tags/$TAG" >/dev/null; then
  echo "Tag $TAG already exists. Reverting version bump."
  git checkout -- pyproject.toml
  exit 1
fi

git add pyproject.toml
git commit -m "Release: $VERSION"
git tag -a "$TAG" -m "Release $VERSION"
echo "Created release commit and tag $TAG"

if [ "$PUSH" = "1" ]; then
  git push origin HEAD --follow-tags
  echo "Pushed $(git rev-parse --abbrev-ref HEAD) and $TAG"
else
  echo "Next steps:"
  echo "  git push origin HEAD --follow-tags"
  echo "  make publish"
fi
