---
description: Generate weekly citation performance report across all Tebra content assets
argument-hint: "[YYYY-MM-DD to YYYY-MM-DD]"
---

> **Status: dormant in pre-hire mode.** This command requires Search Console, GA4, HubSpot, and Slack MCPs to run. Restore path: `docs/OPERATING_MODES.md`.

Generate a weekly citation performance report using the citation-reporter subagent.

$ARGUMENTS

Dispatch the `citation-reporter` subagent with the following task:

> Generate the weekly citation performance report. Date range: $ARGUMENTS (if provided) or trailing 7 days from today.

The subagent will:
1. Pull ranking and traffic data from Search Console and GA4
2. Query HubSpot for organic-influenced pipeline deals
3. Check the citation-scores audit log for pages below the 3.5 extractability threshold
4. Write a markdown report to `audit/citation-report-<date>.md`
5. Post a summary to the `#content-performance` Slack channel

When complete, display the SubagentResponse summary and confirm the report artifact path.
