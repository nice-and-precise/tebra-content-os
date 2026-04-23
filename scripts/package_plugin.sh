#!/usr/bin/env bash
# Build a distributable plugin archive from the repo root.
# Output: dist/tebra-content-os-<version>.tar.gz
# Usage: bash scripts/package_plugin.sh

set -euo pipefail

REPO_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
VERSION="$(python3 -c "import json; print(json.load(open('.claude-plugin/plugin.json'))['version'])")"
DIST_DIR="$REPO_ROOT/dist"
ARCHIVE_NAME="tebra-content-os-$VERSION.tar.gz"

mkdir -p "$DIST_DIR"

# Validate before packing
python3 -m scripts.validate_sources
python3 -m scripts.validate_skills
python3 -m scripts.validate_mcp_config

tar -czf "$DIST_DIR/$ARCHIVE_NAME" \
  --exclude='.git' \
  --exclude='.venv' \
  --exclude='__pycache__' \
  --exclude='*.pyc' \
  --exclude='.pytest_cache' \
  --exclude='.ruff_cache' \
  --exclude='dist' \
  --exclude='.env' \
  --exclude='briefs/*' \
  --exclude='drafts/*' \
  --exclude='audit/*.jsonl' \
  --exclude='audit/*.md' \
  -C "$REPO_ROOT" .

echo "Packaged: $DIST_DIR/$ARCHIVE_NAME"
echo "Install on target machine:"
echo "  mkdir -p ~/tebra-content-os && tar -xzf $ARCHIVE_NAME -C ~/tebra-content-os"
echo "  Then inside Claude Code: /plugin install ~/tebra-content-os"
