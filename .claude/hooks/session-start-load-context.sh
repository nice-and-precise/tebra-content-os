#!/usr/bin/env bash
# SessionStart hook: emits session context summary to stdout.
# Claude Code captures this output and injects it into the session.

set -uo pipefail

REPO_ROOT="$(git rev-parse --show-toplevel 2>/dev/null)"
if [[ -z "$REPO_ROOT" ]]; then
    echo "[tebra-content-os] WARNING: could not determine repo root"
    exit 0
fi

# Brand-voice version: git short-hash of the skill file
BV_SKILL="$REPO_ROOT/.claude/skills/tebra-brand-voice/SKILL.md"
if [[ -f "$BV_SKILL" ]]; then
    BV_VERSION=$(git log -1 --format="%h" -- "$BV_SKILL" 2>/dev/null)
    BV_VERSION="${BV_VERSION:-untracked}"
else
    BV_VERSION="missing"
fi

# Source registry: total count + sources expiring within 30 days
REGISTRY="$REPO_ROOT/sources/registry.json"
if command -v jq &>/dev/null && [[ -f "$REGISTRY" ]]; then
    SOURCE_COUNT=$(jq 'length' "$REGISTRY" 2>/dev/null || echo "?")
    TODAY=$(python3 -c "from datetime import datetime,timezone; print(datetime.now(timezone.utc).strftime('%Y-%m-%d'))" 2>/dev/null)
    WARN_DATE=$(python3 -c "from datetime import datetime,timedelta,timezone; print((datetime.now(timezone.utc)+timedelta(days=30)).strftime('%Y-%m-%d'))" 2>/dev/null)
    if [[ -z "$TODAY" || -z "$WARN_DATE" ]]; then
        EXPIRING="? (python3 unavailable — expiry check skipped)"
    else
        EXPIRING=$(jq --arg today "$TODAY" --arg warn "$WARN_DATE" '
            [to_entries[] | select(
                .value.expires_at[0:10] >= $today and
                .value.expires_at[0:10] <= $warn
            )] | length
        ' "$REGISTRY" 2>/dev/null || echo "?")
    fi
else
    SOURCE_COUNT="?"
    EXPIRING="?"
fi

# Refresh backlog: draft .md files whose frontmatter status != published
DRAFTS_DIR="$REPO_ROOT/drafts"
BACKLOG=0
if [[ -d "$DRAFTS_DIR" ]]; then
    while IFS= read -r -d '' f; do
        status=$(grep -m1 '^status:' "$f" 2>/dev/null | sed 's/status:[[:space:]]*//' | tr -d '[:space:]"')
        if [[ "$status" != "published" ]]; then
            BACKLOG=$((BACKLOG + 1))
        fi
    done < <(find "$DRAFTS_DIR" -maxdepth 2 -name '*.md' -print0 2>/dev/null)
fi

# Compliance rule version: git short-hash of the compliance hook
COMPLIANCE_HOOK="$REPO_ROOT/.claude/hooks/pre-tool-use-compliance.sh"
if [[ -f "$COMPLIANCE_HOOK" ]]; then
    COMPLIANCE_VERSION=$(git log -1 --format="%h" -- "$COMPLIANCE_HOOK" 2>/dev/null)
    COMPLIANCE_VERSION="${COMPLIANCE_VERSION:-untracked}"
else
    COMPLIANCE_VERSION="missing"
fi

echo "[tebra-content-os session context]"
echo "  brand-voice:      $BV_VERSION"
echo "  sources:          $SOURCE_COUNT registered, $EXPIRING expiring within 30 days"
echo "  refresh backlog:  $BACKLOG draft(s) not yet published"
echo "  compliance rules: $COMPLIANCE_VERSION"
