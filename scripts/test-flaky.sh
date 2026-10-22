#!/usr/bin/env bash
set -euo pipefail

# Run the test suite repeatedly to surface flaky tests. Stops at the first failure.
# Example: RUNS=50 TEST=tests/pysentinel/core ./scripts/test-flaky.sh

RUNS="${RUNS:-20}"
TEST="${TEST:-tests}"

for i in $(seq 1 "$RUNS"); do
  echo "Run $i/$RUNS"
  if ! poetry run pytest -q -p no:cacheprovider -W error::pytest.PytestUnraisableExceptionWarning "$TEST"; then
    echo "Failed on run $i of $RUNS"
    exit 1
  fi
done

echo "All $RUNS runs passed"
