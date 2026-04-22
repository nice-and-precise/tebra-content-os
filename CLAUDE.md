# tebra-content-os — Agent Behavior Rules

> This file governs how Claude Code behaves in this repository.
> It references specs rather than duplicating them. Read docs/ for the full system context.
> Hard ceiling: ~250 lines. Adding rules here degrades all rules — use docs/ instead.

---

## What this repo does

Turns a content brief into a compliance-checked, source-grounded, LLM-extractable draft.
Five primitive layers: **skills** (reusable knowledge), **subagents** (isolated workers),
**commands** (user workflows), **hooks** (deterministic gates), **MCP** (external access).

Decision tree for new capabilities:
- Must block unconditionally → hook
- Requires external data → MCP server
- Multi-step isolated task → subagent
- Reusable cross-tool knowledge → skill
- One-shot user workflow → slash command

Full architecture: `docs/ARCHITECTURE.md`. Data contracts: `docs/DATA_CONTRACTS.md`.

---

## Content generation rules

**Source every factual claim.** Every percentage, clinical outcome, regulatory assertion,
and product specification must appear in `sources[].claims_cited[]` in the draft frontmatter,
backed by a source in `sources/registry.json` with the matching claim type in
`approved_for_claims[]`.

**Never invent statistics.** Proof points must come verbatim from the brief's
`proof_points[]` array. Do not paraphrase statistics; do not generate numbers from training
data.

**No hedged medical claims without source.** "May help", "results may vary", "some studies
show" — these require the same sourcing discipline as direct claims. Hedged claims that
cannot be sourced must be removed, not softened further.

**BOFU asset types only.** This repo produces: `comparison`, `roi_calculator`, `case_study`,
`implementation_guide`, `quick_answer`, `refresh`. Each has a skill file that governs
structure. Read the relevant skill before writing content.

**Brand voice.** Always load `.claude/skills/tebra-brand-voice/SKILL.md` before drafting.
Tebra's voice is direct, evidence-forward, written for independent practice operators.
Not academic. Not consumer-facing.

---

## Source citation rules

1. Load `sources/registry.json` to verify source availability before citing.
2. Verify `expires_at` is in the future. Expired sources cannot be cited.
3. Verify the claim type appears in the source's `approved_for_claims[]`.
4. Verify the source's `path` file exists on disk if `path` is non-null.
5. Use `cite_as` as the display citation string — not the title or URL.
6. Run `python3 -m scripts.validate_sources` if you modify the registry.

---

## Hook behavior

**PreToolUse (Write or Edit to drafts/):** `pre-tool-use-compliance.sh` fires on every Write or Edit to
`drafts/`. It calls `scripts/compliance_check.py`. If it returns `permissionDecision: "deny"`,
revise the flagged claim and retry. Maximum 3 retries before surfacing to operator.
Never bypass with `--no-verify` or any equivalent.

**SessionStart:** `session-start-load-context.sh` outputs brand-voice version, source count,
refresh backlog, and compliance rule version. This runs once at session start; the output is
already in your context.

**Stop:** `stop-run-linters.sh` runs ruff, prettier, and `validate_drafts.py` in the
background after each session turn. It does not block.

**PostToolUse (Bash):** `post-commit-changelog.sh` appends to `audit/publish.jsonl` on git
commits that touch `drafts/`. This runs automatically — do not manually append to that file.

---

## Subagent invocation

Subagents live in `.claude/agents/`. Invoke them for scoped, isolated tasks:

| Subagent | When to invoke |
|---|---|
| `brief-author` | `/brief <query>` or operator asks for a brief |
| `draft-writer` | `/draft <slug>` after brief is approved |
| `citation-auditor` | `/audit <url>` for extractability score |
| `refresh-auditor` | `/refresh <url>` for staleness check |
| `compliance-qa` | When draft contains hedged claims before Write |
| `product-truth` | draft-writer auto-invokes for `implementation_guide` only |
| `citation-reporter` | `/citation-report` for weekly performance report |

Do not call subagents in a chain within the same context window — each subagent is designed
to run in an isolated context. Call one, review the SubagentResponse, then decide next step.

---

## MCP server access

MCP servers are defined in `.mcp.json`. Use them only for the data they own:

**Live (pre-hire mode):**
- `firecrawl` — page rendering and search; prefer over raw web browsing
- `exa` — semantic search; prefer over raw web browsing

**Post-hire MCPs (dormant — restore via `docs/OPERATING_MODES.md`):**
- `search-console` / `ga4` — ranking and traffic signal for brief-author and citation-reporter
- `hubspot` — pipeline data; never write CRM records without operator approval
- `asana` — task management; read operations only in this repo

**Claude.ai native connectors (not in `.mcp.json`, available when connected in claude.ai):**
- `google-drive` — product-truth subagent only (implementation guide sourcing)
- `chrome-devtools` — citation-auditor only (page render and extraction)
- `slack` — citation-reporter only; confirm channel before posting

Never use an MCP server outside its designated subagent or workflow. MCP auth credentials
live in environment variables — never read, log, or echo credential values.

---

## Audit trail rules

- `audit/compliance.jsonl` — written by `pre-tool-use-compliance.sh` only
- `audit/publish.jsonl` — written by `post-commit-changelog.sh` only
- `audit/citation-scores.jsonl` — written by `citation-auditor` subagent only
- `audit/citation-report-*.md` — written by `citation-reporter` subagent only

Audit files are append-only. Never truncate, overwrite, or delete entries.
Never manually append to an audit file — all entries come from the hook or subagent that
owns that file.

---

## Forbidden patterns

- **Do not invent claims.** If a required proof point has no source, surface it as a gap
  rather than filling it with a plausible-sounding claim.
- **Do not commit drafts with unresolved compliance denials.** If the hook denies 3 times,
  stop and ask the operator.
- **Do not modify `sources/registry.json` without operator approval.** Source additions
  change the compliance perimeter.
- **Do not use `git push --force`** on main. All work lands via commits.
- **Do not read credential values.** Environment variables hold secrets; reference them by
  name only.
- **Do not bypass hooks** with `--no-verify`, skip-ci flags, or any equivalent mechanism.

---

## Key file locations

| Purpose | Path |
|---|---|
| Full spec | `docs/PRD.md`, `docs/ARCHITECTURE.md`, `docs/DATA_CONTRACTS.md` |
| Build milestones | `docs/TASKS.md` |
| Operator manual | `docs/RUNBOOK.md` |
| Decision log | `docs/RESEARCH_GAPS_AND_DECISIONS.md` |
| Source registry | `sources/registry.json` |
| Compliance check | `scripts/compliance_check.py` |
| Schema definitions | `scripts/schemas.py` |
| Test suite | `tests/` |

---

## Cross-tool portability

This file is Claude Code-specific. For Codex CLI, Cursor, and Gemini CLI, read `AGENTS.md`.
Skills in `.claude/skills/` follow the Agent Skills Standard and work across all four tools.

See `AGENTS.md` for the cross-tool-portable rule set.
