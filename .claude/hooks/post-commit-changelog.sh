#!/usr/bin/env bash
# PostToolUse hook: appends a publish event to audit/publish.jsonl when a
# git commit touches drafts/. Runs asynchronously to avoid blocking the session.

REPO_ROOT="$(git rev-parse --show-toplevel 2>/dev/null)"
[[ -z "$REPO_ROOT" ]] && exit 0

if ! command -v jq &>/dev/null; then
    echo "[post-commit-changelog] WARNING: jq not found — audit record skipped" \
        >> /tmp/tebra-hooks-warnings.log
    exit 0
fi

input=$(cat)

# Only fire on Bash tool use (git commits arrive via Bash)
read -r tool_name command_str < <(echo "$input" | jq -r '[.tool_name // "", .tool_input.command // ""] | @tsv' 2>/dev/null)
[[ "$tool_name" != "Bash" ]] && exit 0

# Only fire when command is a git commit (anchored to avoid matching echo, git commit-tree, etc.)
if ! echo "$command_str" | grep -qE '^git commit\b'; then
    exit 0
fi

(
    cd "$REPO_ROOT" || {
        echo "=== post-commit-changelog ERROR: cd to $REPO_ROOT failed ===" \
            >> /tmp/tebra-hooks-warnings.log
        exit 1
    }

    # Check if the most recent commit touches drafts/
    DRAFTS_CHANGED=$(git diff-tree --no-commit-id -r --name-only HEAD 2>/dev/null | grep '^drafts/' || true)
    [[ -z "$DRAFTS_CHANGED" ]] && exit 0

    AUDIT_FILE="$REPO_ROOT/audit/publish.jsonl"
    mkdir -p "$(dirname "$AUDIT_FILE")"

    COMMIT_HASH=$(git rev-parse --short HEAD 2>/dev/null || echo "unknown")
    TIMESTAMP=$(date -u +%Y-%m-%dT%H:%M:%SZ)

    while IFS= read -r draft_path; do
        status=$(grep -m1 '^status:' "$draft_path" 2>/dev/null | sed 's/status:[[:space:]]*//' | tr -d '[:space:]"')
        status="${status:-unknown}"
        printf '{"event":"draft_commit","timestamp":"%s","commit":"%s","path":"%s","status":"%s"}\n' \
            "$TIMESTAMP" "$COMMIT_HASH" "$draft_path" "$status" >> "$AUDIT_FILE"
    done <<< "$DRAFTS_CHANGED"
) &

exit 0
