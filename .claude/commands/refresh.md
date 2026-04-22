---
description: Audit a live URL for content drift and append refresh recommendations to the draft
---

Dispatch the refresh-auditor subagent to audit this URL or draft for content drift: $ARGUMENTS

The subagent will:
1. Fetch and render the live page via Chrome DevTools MCP
2. Check competitor SERP content for structural drift via Firecrawl
3. Check LLM-consensus answer shifts via Exa
4. Append specific recommended changes to the draft's `refresh.recommended_changes[]`
5. Log a `refresh_triggered` event to `audit/compliance.jsonl`
6. Return a markdown summary with the change list and next refresh date

After the subagent returns, surface its `summary_for_user` field as your response. If the subagent returns `status: "failure"`, surface the `errors[]` content and ask the user to verify the URL is reachable and a matching draft exists in `drafts/`.
