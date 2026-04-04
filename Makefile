# Makefile for pysentinel
# Provides convenience targets for common developer tasks.

.PHONY: help install format lint typecheck test coverage build publish clean quality

help:
	@echo "Available targets:"
	@echo "  install    - Install project dependencies (poetry install)"
	@echo "  format     - Format code using black"
	@echo "  lint       - Run a linter (ruff or flake8 if available)"
	@echo "  typecheck  - Run type checks (mypy if available)"
	@echo "  quality    - Run lint, typecheck and tests (stops on first failure)"
	@echo "  test       - Run test suite with pytest"
	@echo "  coverage   - Run tests with coverage report"
	@echo "  build      - Build distribution packages (sdist + wheel)"
	@echo "  publish    - Publish package to PyPI (uses poetry publish --build)"
	@echo "  clean      - Remove build/artifacts"

install:
	poetry install

format:
	bash scripts/format.sh

lint:
	bash scripts/lint.sh

typecheck:
	bash scripts/typecheck.sh

quality:
	@echo "Running quality checks: lint, typecheck, tests"
	bash scripts/lint.sh
	bash scripts/typecheck.sh
	bash scripts/test.sh

test:
	bash scripts/test.sh

coverage:
	bash scripts/coverage.sh

build:
	bash scripts/build.sh

publish:
	bash scripts/publish.sh

clean:
	@echo "Cleaning build artifacts..."
	rm -rf build/ dist/ *.egg-info htmlcov .pytest_cache
