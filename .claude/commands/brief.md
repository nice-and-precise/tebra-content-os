---
description: Research a query cluster and produce a validated Brief JSON with Asana task
---

Dispatch the brief-author subagent to research this query cluster and produce a brief: $ARGUMENTS

The subagent will (pre-hire mode — see `docs/OPERATING_MODES.md`):
1. Read `sources/registry.json` and build a cite-allowed source index
2. Scrape top SERP results via Firecrawl for competitor structure
3. Query Exa for LLM-consensus answers to the cluster
4. Synthesize a Brief JSON validated against the Brief schema
5. Write the brief to `briefs/<slug>.json`
6. Return a markdown summary with the brief path and any sourcing gaps

Search Console / GA4 queries and Asana task creation are deferred to post-hire mode. Restore path documented in `docs/OPERATING_MODES.md`.

After the subagent returns, surface its `summary_for_user` field as your response. If the subagent returns `status: "failure"`, surface the `errors[]` content and ask the user to verify `FIRECRAWL_API_KEY` / `EXA_API_KEY` are set in the shell environment (sourced from `.env`).
