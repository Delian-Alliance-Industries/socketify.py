#!/usr/bin/env bash
set -euo pipefail

# Local build + TestPyPI upload for development/testing.
# Production releases are handled by .github/workflows/release.yml via cibuildwheel.

# Build wheel (runs native compilation) and sdist
uv build

# Upload to TestPyPI
uv run twine upload -r testpypi dist/* --verbose
