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

- make check (aliases: make ci, make quality)
  - Runs exactly what CI runs: `black --check`, lint, typecheck, and tests with coverage. Stops on the first failure.

- make format-check / make lint-fix
  - Check formatting without changing files / apply ruff's safe autofixes.

- make doctor
  - Checks that Poetry, the virtualenv and the dev tools are usable, and prints the fix if not (for example after a Homebrew Python upgrade leaves the virtualenv pointing at a missing interpreter).

- make hooks
  - Installs the pre-commit git hooks.

- make test
  - Runs the test suite with pytest. You can pass additional pytest args with the `PYTEST_EXTRA_ARGS` environment variable; for example:

    PYTEST_EXTRA_ARGS="-k fast -q" make test

- make coverage
  - Runs tests with coverage enabled and writes an HTML report to `htmlcov/index.html`.

- make test-file TEST=tests/pysentinel/core / make test-k K=interval
  - Run a single test file or directory, or tests matching a keyword.

- make test-flaky RUNS=50
  - Runs the suite repeatedly and stops at the first failure. Leaked, never-awaited coroutines are treated as errors so they can't hide behind a random test.

- make run CONFIG=path/to/config.yml
  - Runs the scanner with the given config file.

- make build
  - Builds source and wheel distributions (uses `poetry build`). Artifacts are placed in `dist/`.

- make publish
  - Builds and publishes to PyPI. Refuses to run unless the working tree is clean and HEAD is tagged `v<version>` (as created by `make release`). Set `SKIP_RELEASE_CHECK=1` to bypass.

- make publish-test
  - Builds and publishes to TestPyPI (no tag check). Requires a TestPyPI token: `poetry config pypi-token.testpypi <token>`.

- make clean
  - Removes build artifacts and caches (dist, build, egg-info, htmlcov, coverage files, tool caches, `__pycache__`, and the local `alerts.db`).

Releasing

1. `make version` shows the current version.
2. `make bump PART=patch|minor|major|<x.y.z>` only changes the version in `pyproject.toml`.
3. `make release PART=minor` requires a clean working tree, runs `make check`, bumps the version, commits it as `Release: <version>` and creates the annotated tag `v<version>`. Add `PUSH=1` to push the branch and tag; otherwise it prints the push command.
4. `make publish` uploads the tagged release to PyPI.

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
6. Before pushing: `make check`
7. Release: `make release PART=patch` then `make publish`
