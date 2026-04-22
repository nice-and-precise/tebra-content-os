---
description: Score a URL against the extractability rubric using the citation-auditor subagent
---

Dispatch the citation-auditor subagent to score this URL: $ARGUMENTS

The subagent will:
1. Render the page via Chrome DevTools MCP
2. Extract structured signals (JSON-LD schema, header counts, Q&A pairs, citations, answer-first structure)
3. Score each extractability dimension 0–5 using `scripts/citation_score.py`
4. Append the result to `audit/citation-scores.jsonl`
5. Return a markdown report with scores and improvement recommendations

After the subagent returns, surface its `summary_for_user` field as your response. If the subagent returns `status: "failure"`, surface the `errors[]` content and ask the user to verify the URL is reachable.
