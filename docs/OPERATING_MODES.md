# Operating Modes

This repo ships two operating modes. Which mode is active is determined by which commits are on `main` and which MCP credentials are populated in `.env`.

## pre-hire mode (current, as of 2026-04-22)

Active when the session runs without Tebra-internal MCP credentials (Search Console, GA4, Asana, HubSpot). The pipeline still produces validated briefs and drafts using Firecrawl and Exa for research. **To restore post-hire mode, see [Restoration path](#restoration-path) below.**

### What is removed

- `.mcp.json`: `search-console`, `ga4`, `asana`, `hubspot` entries
- `.claude/agents/brief-author.md`: the 4 MCP tool names and the workflow steps that used them (Search Console / GA4 sub-queries; Asana task creation)
- `.claude/commands/brief.md`: the command description no longer advertises the removed steps
- `.env.example`: inline comments mark the removed-server blocks

### What is NOT removed

- Skills, hooks, schemas, validators, compliance gate
- `citation-auditor`, `refresh-auditor`, `citation-reporter` subagents (all still present — they gain useful context post-hire but don't block pre-hire)
- `.env.example` still lists every variable for reference

### Restoration path

- Git anchor: tag `pre-hire-mode-v1` marks the HEAD of pre-hire-mode work.
- To restore post-hire mode: `git revert 6e5dad1` (the pre-hire trim commit), resolve any conflicts with subsequent edits, populate the Tebra credentials in `.env`, re-run `python3 -m pytest -x`.
- Alternative: hand-restore using the file list above. The change surface is small and `git log -- .mcp.json .claude/agents/brief-author.md` shows the prior full-MCP versions of each file.

**Why git-reversible rather than stubbed:** stubs would require mocks in the test suite and subagent-level branching on credential presence, adding complexity that pays off only if we expect to toggle modes repeatedly. We don't — the transition is one-way and happens exactly once when Tebra provisions access.

## post-hire mode (target)

Active when Tebra credentials are provisioned. Search Console and GA4 inform `brief-author` retrieval alongside Firecrawl and Exa. Asana task creation runs at the end of `/brief`. HubSpot informs `/citation-report` pipeline attribution.

No code change required beyond the restoration path above.
