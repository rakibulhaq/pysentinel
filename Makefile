# Makefile for pysentinel
# Provides convenience targets for common developer tasks.

.DEFAULT_GOAL := help

PART ?= patch
RUNS ?= 20
TEST ?= tests
CONFIG ?= config.yml

.PHONY: help install hooks doctor format format-check lint lint-fix typecheck \
	quality check ci test test-file test-k test-flaky coverage run \
	version bump release build publish publish-test clean

help:
	@echo "Setup:"
	@echo "  install      - Install project dependencies (poetry install)"
	@echo "  hooks        - Install the pre-commit git hooks"
	@echo "  doctor       - Check the development environment is usable"
	@echo ""
	@echo "Code quality:"
	@echo "  format       - Format code using black"
	@echo "  format-check - Check formatting without changing files"
	@echo "  lint         - Run a linter (ruff or flake8 if available)"
	@echo "  lint-fix     - Run ruff and apply safe fixes"
	@echo "  typecheck    - Run type checks (mypy if available)"
	@echo "  check        - Run everything CI runs: format-check, lint, typecheck, tests (alias: ci, quality)"
	@echo ""
	@echo "Testing:"
	@echo "  test         - Run test suite with pytest"
	@echo "  test-file    - Run one test file or directory: make test-file TEST=tests/pysentinel/core"
	@echo "  test-k       - Run tests matching a keyword: make test-k K=interval"
	@echo "  test-flaky   - Run the suite repeatedly to catch flaky tests: make test-flaky RUNS=50"
	@echo "  coverage     - Run tests with coverage report"
	@echo "  run          - Run the scanner: make run CONFIG=path/to/config.yml"
	@echo ""
	@echo "Release:"
	@echo "  version      - Print the current package version"
	@echo "  bump         - Bump the version: make bump PART=patch|minor|major|<x.y.z>"
	@echo "  release      - Check, bump, commit and tag a release: make release PART=minor [PUSH=1]"
	@echo "  build        - Build distribution packages (sdist + wheel)"
	@echo "  publish      - Publish the tagged release to PyPI"
	@echo "  publish-test - Publish to TestPyPI"
	@echo "  clean        - Remove build artifacts and caches"

install:
	poetry install

hooks:
	poetry run pre-commit install

doctor:
	bash scripts/doctor.sh

format:
	bash scripts/format.sh

format-check:
	poetry run black --check .

lint:
	bash scripts/lint.sh

lint-fix:
	poetry run ruff check --fix .

typecheck:
	bash scripts/typecheck.sh

check:
	bash scripts/check.sh

ci: check

quality: check

test:
	bash scripts/test.sh

test-file:
	poetry run pytest $(TEST)

test-k:
	@test -n "$(K)" || (echo "Usage: make test-k K=<keyword>" && exit 1)
	poetry run pytest -k "$(K)"

test-flaky:
	RUNS=$(RUNS) TEST=$(TEST) bash scripts/test-flaky.sh

coverage:
	bash scripts/coverage.sh

run:
	poetry run pysentinel $(CONFIG)

version:
	@poetry version -s

bump:
	PART=$(PART) bash scripts/bump.sh

release:
	PART=$(PART) PUSH=$(PUSH) bash scripts/release.sh

build:
	bash scripts/build.sh

publish:
	bash scripts/publish.sh

publish-test:
	POETRY_REPOSITORY=testpypi \
	POETRY_REPOSITORIES_TESTPYPI_URL=https://test.pypi.org/legacy/ \
	bash scripts/publish.sh

clean:
	@echo "Cleaning build artifacts..."
	rm -rf build/ dist/ *.egg-info htmlcov .pytest_cache .mypy_cache .ruff_cache \
		.coverage coverage.xml alerts.db
	find . -type d -name __pycache__ -not -path "./.venv/*" -prune -exec rm -rf {} +
