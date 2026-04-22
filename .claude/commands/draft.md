---
description: Write a compliant draft markdown file from a brief JSON using Opus 4.7
---

Dispatch the draft-writer subagent to write a draft from this brief: $ARGUMENTS

The subagent will:
1. Load the brief from `briefs/<slug>.json`
2. Write a structured draft to `drafts/<slug>.md` with valid YAML frontmatter
3. Handle compliance hook deny decisions by revising flagged claims (max 3 retries)
4. Return a markdown summary with the draft path and compliance status

After the subagent returns, surface its `summary_for_user` field as your response. If the subagent returns `status: "partial_success"`, surface the `warnings[]` content explaining why the compliance hook blocked the draft and ask the operator to review the flagged claims before retrying.
