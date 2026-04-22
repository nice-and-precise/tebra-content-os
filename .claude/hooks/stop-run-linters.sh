#!/usr/bin/env bash
# Stop hook: runs linters and draft validation in the background after each session turn.
# Uses background execution (command &) because Claude Code's Stop hook schema has no async flag.
# Output goes to /tmp/tebra-lint.log — not blocking.

REPO_ROOT="$(git rev-parse --show-toplevel 2>/dev/null)"
[[ -z "$REPO_ROOT" ]] && exit 0

(
    set -uo pipefail
    cd "$REPO_ROOT" || {
        echo "=== stop-run-linters $(date -u +%Y-%m-%dT%H:%M:%SZ) ERROR: cd to $REPO_ROOT failed ===" \
            >> /tmp/tebra-lint.log
        exit 1
    }
    LOG="/tmp/tebra-lint.log"
    {
        echo "=== stop-run-linters $(date -u +%Y-%m-%dT%H:%M:%SZ) ==="

        # Ruff on changed Python files (staged + unstaged vs HEAD)
        ALL_PY=$(git diff --name-only HEAD 2>/dev/null | grep '\.py$' || true)
        if [[ -n "$ALL_PY" ]]; then
            echo "--- ruff ---"
            # shellcheck disable=SC2086
            python3 -m ruff check $ALL_PY 2>&1 || true
        fi

        # Prettier on changed markdown files (best-effort — skips if prettier not installed)
        CHANGED_MD=$(git diff --name-only HEAD 2>/dev/null | grep '\.md$' || true)
        if [[ -n "$CHANGED_MD" ]] && command -v prettier &>/dev/null; then
            echo "--- prettier ---"
            # shellcheck disable=SC2086
            prettier --check $CHANGED_MD 2>&1 || true
        fi

        # validate_drafts.py on drafts/ if it exists
        if [[ -f "$REPO_ROOT/scripts/validate_drafts.py" && -d "$REPO_ROOT/drafts" ]]; then
            echo "--- validate_drafts ---"
            python3 scripts/validate_drafts.py 2>&1 || true
        fi

        echo "=== done ==="
    } >> "$LOG" 2>&1
) &

exit 0
