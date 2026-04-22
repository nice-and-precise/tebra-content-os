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

# Fail closed if we can't determine the repo root — never run from an unknown context.
repo_root="$(git rev-parse --show-toplevel 2>/dev/null)"
if [[ -z "$repo_root" ]]; then
    echo '{"hookSpecificOutput":{"permissionDecision":"deny"},"systemMessage":"Compliance hook: could not locate git root — denying write to drafts/"}' >&2
    exit 2
fi

registry="$repo_root/sources/registry.json"
audit="$repo_root/audit/compliance.jsonl"

# Run compliance check. Capture stdout (JSON) and stderr (errors) separately.
py_exit=0
py_stderr_file=$(mktemp)
result=$(echo "$content" | python "$repo_root/scripts/compliance_check.py" "$slug" "$registry" "$audit" 2>"$py_stderr_file") || py_exit=$?
py_stderr=$(cat "$py_stderr_file")
rm -f "$py_stderr_file"

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
        # compliance_check.py crashed — fail closed to protect against bypassing the gate.
        err_detail="${py_stderr:-no stderr captured}"
        msg=$(jq -cn --arg d "$err_detail" \
            '{"hookSpecificOutput":{"permissionDecision":"deny"},"systemMessage":("Compliance hook crash (fail-closed): " + $d)}')
        echo "$msg" >&2
        exit 2
        ;;
esac
