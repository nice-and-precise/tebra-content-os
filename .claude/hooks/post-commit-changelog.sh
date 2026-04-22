#!/usr/bin/env bash
# PostToolUse hook: appends a publish event to audit/publish.jsonl when a
# git commit touches drafts/. Runs asynchronously to avoid blocking the session.

REPO_ROOT="$(git rev-parse --show-toplevel 2>/dev/null)"
[[ -z "$REPO_ROOT" ]] && exit 0

input=$(cat)

# Only fire on Bash tool use (git commits arrive via Bash)
read -r tool_name command_str < <(echo "$input" | jq -r '[.tool_name // "", .tool_input.command // ""] | @tsv' 2>/dev/null)
[[ "$tool_name" != "Bash" ]] && exit 0

# Only fire when command looks like a git commit
if ! echo "$command_str" | grep -qE 'git commit'; then
    exit 0
fi

(
    cd "$REPO_ROOT" || exit 0

    # Check if the most recent commit touches drafts/
    DRAFTS_CHANGED=$(git diff-tree --no-commit-id -r --name-only HEAD 2>/dev/null | grep '^drafts/' || true)
    [[ -z "$DRAFTS_CHANGED" ]] && exit 0

    AUDIT_FILE="$REPO_ROOT/audit/publish.jsonl"
    mkdir -p "$(dirname "$AUDIT_FILE")"

    COMMIT_HASH=$(git rev-parse --short HEAD 2>/dev/null || echo "unknown")
    TIMESTAMP=$(date -u +%Y-%m-%dT%H:%M:%SZ)

    while IFS= read -r draft_path; do
        # Extract status from frontmatter if available
        status=$(grep -m1 '^status:' "$draft_path" 2>/dev/null | sed 's/status:[[:space:]]*//' | tr -d '[:space:]"' || echo "unknown")
        printf '{"event":"draft_commit","timestamp":"%s","commit":"%s","path":"%s","status":"%s"}\n' \
            "$TIMESTAMP" "$COMMIT_HASH" "$draft_path" "$status" >> "$AUDIT_FILE"
    done <<< "$DRAFTS_CHANGED"
) &

exit 0
