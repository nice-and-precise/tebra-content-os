---
description: Research a query cluster and produce a validated Brief JSON with Asana task
---

Dispatch the brief-author subagent to research this query cluster and produce a brief: $ARGUMENTS

The subagent will:
1. Query Search Console and GA4 for performance and intent signals
2. Scrape top SERP results via Firecrawl for competitor structure
3. Query Exa for LLM-consensus answers to the cluster
4. Synthesize a Brief JSON validated against the Brief schema
5. Write the brief to `briefs/<slug>.json`
6. Create an Asana task in the Content Pipeline project
7. Return a markdown summary with the brief path and Asana task ID

After the subagent returns, surface its `summary_for_user` field as your response. If the subagent returns `status: "failure"`, surface the `errors[]` content and ask the user to verify MCP server connectivity (M5 wires these up).
