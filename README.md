# tebra-content-os

> **GEO is the new SEO. The zero-click era rewards content engineered
> for citation, not written and published on hope.**

tebra-content-os is a Claude Code-native repository that turns a content
brief into a compliance-checked, source-grounded, LLM-extractable draft
through typed subagents, deterministic hooks, and portable skills. It is
scoped for Tebra\'s Senior AI Content Marketing Manager role, where \"no
AI slop\" is the stated filter and share-of-citation is a stated KPI. It
demonstrates an operating architecture for the GEO era: content
engineered for citation, gated for healthcare compliance at commit time,
and human-approved on every BOFU asset before publish.

## Status

Specification complete (seven documents under docs/). Implementation in
progress per docs/TASKS.md.

## Quickstart

Follow docs/RUNBOOK.md for environment setup. The 30-minute path from
git clone to a working /audit \<url\> is Section 3. Full subsystem
walkthroughs are in Sections 4--11.

git clone https://github.com/nice-and-precise/tebra-content-os.git

cd tebra-content-os

\# then follow RUNBOOK.md Section 3

## What the repo contains

  -----------------------------------------------------------------------
  **Layer**               **Location**            **Role**
  ----------------------- ----------------------- -----------------------
  Subagents               .claude/agents/         Brief author, draft
                                                  writer, citation
                                                  auditor, refresh
                                                  auditor, compliance QA,
                                                  product truth

  Skills                  .claude/skills/         Brand voice, block
                                                  library, healthcare
                                                  compliance, four BOFU
                                                  asset types

  Hooks                   .claude/hooks/          Deterministic quality
                                                  gates, session context
                                                  injection, audit
                                                  logging

  Slash commands          .claude/commands/       /audit, /brief, /draft,
                                                  /refresh,
                                                  /citation-report

  MCP config              .mcp.json               13 external services
                                                  (Search Console, GA4,
                                                  HubSpot, Webflow,
                                                  Asana, Slack, Chrome
                                                  DevTools, Firecrawl,
                                                  Exa, Profound, Peec AI,
                                                  Google Drive, Figma)

  Data                    briefs/, drafts/,       Git-tracked content
                          sources/, audit/        state and append-only
                                                  audit logs

  Glue                    scripts/                Python validators,
                                                  rubric scorers,
                                                  compliance checkers
  -----------------------------------------------------------------------

## Documentation

All seven specification documents live under docs/:

- PRD.md --- problem, users, goals, acceptance criteria

- ARCHITECTURE.md --- subagent, hook, skill, and MCP server wiring using
  April 2026 Claude Code primitives

- DATA_CONTRACTS.md --- Pydantic schemas for briefs, drafts, sources,
  citations, audit events

- TASKS.md --- thirteen sequential build milestones with enforced stop
  points

- RUNBOOK.md --- operator\'s manual covering environment setup, MCP
  auth, troubleshooting, day-two operations

- RESEARCH_GAPS_AND_DECISIONS.md --- decision log, open questions,
  version pinning, migration targets

- REPO_PRINCIPLES_EXTRACTED.md --- design lineage from related
  production systems (squti, amie, lli-saas)

## Design principles

Five that define the repo. Full detail in
docs/REPO_PRINCIPLES_EXTRACTED.md.

1.  **Git is the database.** Every brief, draft, source, and audit event
    lives in version-controlled files. No separate service, no cloud
    database.

2.  **Compliance is architecture.** The PreToolUse hook blocks unsourced
    medical claims at commit time. Policy enforced by the system, not by
    a checklist.

3.  **Retrieval before generation.** Briefs are built from Search
    Console, GA4, Firecrawl, and Exa signal before any draft is
    generated. No content is written from whole cloth.

4.  **Human-in-the-loop where it matters.** Citation audits automate.
    Draft publication does not; every BOFU asset routes through PMM
    approval before Webflow publish.

5.  **Cross-tool portability.** Skills follow the Agent Skills Standard
    so they work in Cursor, Codex CLI, and Gemini CLI. MCP servers use
    Streamable HTTP, not deprecated SSE.

## Author

Jordan Damhof.
[[github.com/nice-and-precise]{.underline}](https://github.com/nice-and-precise).

Built as the proof-of-work artifact for a Senior AI Content Marketing
Manager application at Tebra. The repository is simultaneously an
architecture proposal and a runnable demonstration that the proposal
holds.

## License

MIT. See LICENSE.
