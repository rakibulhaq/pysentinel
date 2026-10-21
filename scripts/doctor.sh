#!/usr/bin/env bash
set -uo pipefail

# Check that the development environment is usable.

STATUS=0

if ! command -v poetry >/dev/null 2>&1; then
  echo "[x] poetry is not installed: https://python-poetry.org/docs/#installation"
  exit 1
fi
echo "[ok] $(poetry --version)"

ENV_PATH=""
if ENV_OUTPUT="$(poetry env info --path 2>&1)"; then
  ENV_PATH="$ENV_OUTPUT"
fi

if echo "$ENV_OUTPUT" | grep -q "No such file or directory: 'python'"; then
  echo "[x] poetry cannot find a 'python' executable on PATH (only python3 may exist)."
  echo "    Poetry needs an unversioned 'python' even for 'poetry env use'. With Homebrew:"
  echo "      echo 'export PATH=\"\$(brew --prefix)/opt/python@3/libexec/bin:\$PATH\"' >> ~/.zshrc"
  echo "    then open a new shell and recreate the virtualenv:"
  echo "      poetry env remove --all && poetry env use python3.12 && make install"
  STATUS=1
elif [ -z "$ENV_PATH" ]; then
  echo "[x] No poetry virtualenv for this project. Run: make install"
  STATUS=1
elif [ ! -x "$ENV_PATH/bin/python" ]; then
  echo "[x] Virtualenv at $ENV_PATH points to a Python that no longer exists"
  echo "    (common after a Homebrew Python upgrade). Recreate it with:"
  echo "      poetry env remove --all && poetry env use python3 && make install"
  STATUS=1
else
  echo "[ok] virtualenv: $ENV_PATH ($("$ENV_PATH/bin/python" --version))"
  for tool in black ruff mypy pytest pre-commit; do
    if [ -x "$ENV_PATH/bin/$tool" ]; then
      echo "[ok] $tool"
    else
      echo "[x] $tool missing. Run: make install"
      STATUS=1
    fi
  done
fi

if [ -f .git/hooks/pre-commit ]; then
  echo "[ok] pre-commit hook installed"
else
  echo "[!] pre-commit hook not installed. Run: make hooks"
fi

exit $STATUS
