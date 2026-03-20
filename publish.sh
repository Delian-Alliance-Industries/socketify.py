#!/usr/bin/env bash
set -euo pipefail

# Build wheel and sdist
uv build

# Upload to TestPyPI
uv run twine upload -r testpypi dist/* --verbose
