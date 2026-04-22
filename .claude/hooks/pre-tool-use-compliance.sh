#!/usr/bin/env bash
# PreToolUse hook: blocks writes to drafts/ containing unsourced medical claims.
# Input:  JSON from stdin with .tool_name and .tool_input.*
# Output: hookSpecificOutput JSON on stderr + exit 2 to block; exit 0 to allow.

set -uo pipefail

input=$(cat)

file_path=$(echo "$input" | jq -r '.tool_input.file_path // empty')

# Only fire on writes to the drafts/ directory
if [[ "$file_path" != drafts/* ]]; then
    exit 0
fi

# Accept content from Write (.content) or Edit (.new_string)
content=$(echo "$input" | jq -r '.tool_input.content // .tool_input.new_string // empty')

if [[ -z "$content" ]]; then
    exit 0
fi

slug=$(basename "$file_path" .md)
repo_root="$(git rev-parse --show-toplevel 2>/dev/null || pwd)"

registry="$repo_root/sources/registry.json"
audit="$repo_root/audit/compliance.jsonl"

# Capture both stdout (JSON result) and exit code.
# Exit 0 = allow, 2 = deny/ask, anything else = script failure (fail open).
py_exit=0
result=$(echo "$content" | python "$repo_root/scripts/compliance_check.py" "$slug" "$registry" "$audit" 2>/dev/null) || py_exit=$?

case $py_exit in
    0)
        exit 0
        ;;
    2)
        decision=$(echo "$result" | jq -r '.decision // "deny"')
        reason=$(echo "$result" | jq -r '.reason // ""')
        msg=$(jq -cn --arg dec "$decision" --arg r "$reason" \
            '{"hookSpecificOutput": {"permissionDecision": $dec}, "systemMessage": ("Compliance: " + $r)}')
        echo "$msg" >&2
        exit 2
        ;;
    *)
        # compliance_check.py itself failed to run — fail open to avoid blocking all writes
        exit 0
        ;;
esac
