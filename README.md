# tebra-content-os

> **GEO is the new SEO. The zero-click era rewards content engineered for citation, not written and published on hope.**

tebra-content-os is a Claude Code-native content operations pipeline built for Tebra's GEO era: content engineered for LLM citation, gated for healthcare compliance at commit time, human-approved on every BOFU asset before publish.

Two delivered artifacts demonstrate the system end-to-end:

- **Day 1 — LLM extractability audit** (`audit/tebra_citation_audit_2026-04-22.pdf`): Scored 16 tebra.com URLs across five extractability dimensions. Zero pages passed the 3.5 threshold. Three template-level fixes identified that move 8 of 9 blog posts past threshold in one sprint.
- **Day 2 — `/brief` → `/draft` pipeline dry run** (`docs/E2E_DRY_RUN.md`): Research brief (`briefs/tebra-vs-advancedmd-for-solo-practices.json`, 7 proof points, 11 registry-backed sources) produced by `brief-author` subagent; ~1,400-word BOFU comparison draft (`drafts/tebra-vs-advancedmd-for-solo-practices.md`) gated through the compliance hook and allowed on first write.

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
`scripts/compliance_check.py`. The runtime hook verifies:

1. Every percentage or clinical-outcome claim detected by the medical-claim regex has a
   matching citation in the draft frontmatter's `sources[].claims_cited[]`.
2. Every cited source exists in `sources/registry.json`, is not past its `expires_at`, and
   is not authority tier 4.

Denial blocks the write. The hook cannot be bypassed.

`approved_for_claims[]` is declared on every source in the registry. Validator-time
enforcement (`python3 -m scripts.validate_drafts`) checks alignment for any `ClaimCited`
entry where `claim_type` is set. Runtime hook enforcement of `approved_for_claims[]` is a
tracked gap — see `docs/RESEARCH_GAPS_AND_DECISIONS.md`.

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
