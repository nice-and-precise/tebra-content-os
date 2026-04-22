# tebra-content-os

> **GEO is the new SEO. The zero-click era rewards content engineered for citation, not written and published on hope.**

tebra-content-os is a Claude Code-native repository that turns a content brief into a
compliance-checked, source-grounded, LLM-extractable draft through typed subagents,
deterministic hooks, and portable skills. Scoped for Tebra's Senior AI Content Marketing
Manager role — where "no AI slop" is the stated filter and share-of-citation is a stated
KPI — it demonstrates an operating architecture for the GEO era: content engineered for
citation, gated for healthcare compliance at commit time, and human-approved on every BOFU
asset before publish.

## Quickstart

```bash
git clone https://github.com/nice-and-precise/tebra-content-os.git
cd tebra-content-os
```

Environment setup (MCP auth, Python venv, env vars): `docs/RUNBOOK.md` Section 3.

Day-one demo in Claude Code — paste `PROMPT_TO_PASTE_IN_CLAUDE_CODE.md`, then:

```
/audit https://www.tebra.com/features
```

Returns an LLM extractability score with dimension breakdown and recommendations.

## Architecture

Five primitive layers, one responsibility each:

| Layer | Location | Role |
|---|---|---|
| Skills | `.claude/skills/` | Reusable cross-tool knowledge: brand voice, healthcare compliance, 4 BOFU asset types, citation block library |
| Subagents | `.claude/agents/` | Isolated workers: brief-author, draft-writer, citation-auditor, refresh-auditor, compliance-qa, product-truth, citation-reporter |
| Hooks | `.claude/hooks/` | Deterministic gates: compliance pre-check, session context injection, async linting, audit logging |
| Commands | `.claude/commands/` | User workflows: `/audit`, `/brief`, `/draft`, `/refresh`, `/citation-report` |
| MCP servers | `.mcp.json` | External access: Firecrawl (page render) + Exa (search). Post-hire: Search Console, GA4, Asana, HubSpot restore via `docs/OPERATING_MODES.md` |

Decision tree: must block → hook; external data → MCP; multi-step → subagent; reusable knowledge → skill; one-shot workflow → command.

## Content pipeline

```
/brief <query>          # brief-author subagent: retrieval → structured brief
  ↓
/draft <slug>           # draft-writer subagent: brief → compliance-checked draft
  ↓                     # (PreToolUse hook blocks unsourced medical claims)
PMM review              # human approval required before publish
  ↓
Webflow publish         # operator action only (manual in pre-hire mode; see docs/OPERATING_MODES.md)
```

## Compliance model

Every write or edit to `drafts/` passes through `pre-tool-use-compliance.sh`, which calls
`scripts/compliance_check.py`. The check verifies:

1. No percentage or clinical outcome claims without a source ID in the draft frontmatter
2. Every cited source exists in `sources/registry.json` and is not expired
3. The cited source's `approved_for_claims[]` includes the relevant claim type

Denial blocks the write. The hook cannot be bypassed.

## Documentation

All specification documents under `docs/`:

| File | Contents |
|---|---|
| `PRD.md` | Problem, users, goals, acceptance criteria |
| `ARCHITECTURE.md` | Five-primitive wiring using April 2026 Claude Code primitives |
| `DATA_CONTRACTS.md` | Pydantic schemas for briefs, drafts, sources, citations, audit events |
| `TASKS.md` | Thirteen sequential build milestones with enforced stop points |
| `RUNBOOK.md` | Environment setup, MCP auth, troubleshooting, day-two operations |
| `RESEARCH_GAPS_AND_DECISIONS.md` | Decision log, open questions, version pinning |
| `REPO_PRINCIPLES_EXTRACTED.md` | Design lineage from related production systems |

## Design principles

1. **Git is the database.** Every brief, draft, source, and audit event lives in
   version-controlled files. No separate service, no cloud database.

2. **Compliance is architecture.** The PreToolUse hook blocks unsourced medical claims at
   commit time. Policy enforced by the system, not by a checklist.

3. **Retrieval before generation.** Briefs are built from Search Console, GA4, Firecrawl,
   and Exa signal before any draft is generated.

4. **Human-in-the-loop where it matters.** Citation audits automate. BOFU asset publication
   does not — every asset routes through PMM approval before Webflow publish.

5. **Cross-tool portability.** Skills follow the Agent Skills Standard and work in Cursor,
   Codex CLI, and Gemini CLI. MCP servers use Streamable HTTP transport, not deprecated SSE.

## Author

Jordan Damhof. [github.com/nice-and-precise](https://github.com/nice-and-precise).

Built as the proof-of-work artifact for a Senior AI Content Marketing Manager application at
Tebra. The repository is simultaneously an architecture proposal and a runnable demonstration
that the proposal holds.

## License

MIT. See `LICENSE`.
