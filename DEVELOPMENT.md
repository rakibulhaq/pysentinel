Development tasks and commands

This project provides a Makefile with convenient targets for common development tasks. Use `make` to run them. Targets are implemented as small scripts in the `scripts/` directory and use `poetry run` so they operate inside the project's virtual environment.

Common targets

- make install
  - Installs project dependencies (including dev dependencies) using Poetry.

- make format
  - Formats the code base with black.

- make lint
  - Runs a linter. The scripts try `ruff` first, then `flake8` if `ruff` is not installed.

- make typecheck
  - Runs `mypy` against the `pysentinel` package (if `mypy` is installed).

- make quality
  - Runs `make lint`, `make typecheck`, and `make test` in sequence. The command stops on the first failing step (so you can fix the earliest failure before continuing).

- make test
  - Runs the test suite with pytest. You can pass additional pytest args with the `PYTEST_EXTRA_ARGS` environment variable; for example:

    PYTEST_EXTRA_ARGS="-k fast -q" make test

- make coverage
  - Runs tests with coverage enabled and writes an HTML report to `htmlcov/index.html`.

- make build
  - Builds source and wheel distributions (uses `poetry build`). Artifacts are placed in `dist/`.

- make publish
  - Publishes the built package to PyPI using `poetry publish --build`.
  - To publish to TestPyPI or another configured repository, set `POETRY_REPOSITORY` before running, for example:

    POETRY_REPOSITORY=testpypi make publish

- make clean
  - Removes common build artifacts (dist, build, egg-info, htmlcov, .pytest_cache).

Notes

- The Makefile invokes scripts with `bash` so files don't need to be executable for the targets to work.
- The dev tooling (black, ruff, mypy, flake8) was added to the poetry dev group so `make install` installs them into the environment.
- Because this repository is a published package, these developer instructions are kept in `DEVELOPMENT.md` rather than the main `README.md` to avoid cluttering user-facing docs.

Recommended workflow

1. Install dependencies: `make install`
2. Format: `make format`
3. Lint: `make lint` (or run `make quality` to do lint, typecheck and tests together)
4. Typecheck: `make typecheck`
5. Run tests: `make test` and `make coverage` for coverage
6. Build and publish: `make build` then `make publish` (or `make publish` which builds + publishes)
