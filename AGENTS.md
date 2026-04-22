# tebra-content-os — Agent Behavior Rules (Cross-Tool)

> Cross-tool standard per the Linux Foundation Agent Skills Standard.
> Compatible with Codex CLI, Cursor, Gemini CLI, and Claude Code.
> For Claude Code-specific behavior (hooks, @imports, /init), read `CLAUDE.md`.

---

## Repository purpose

Turns a content brief into a compliance-checked, source-grounded, LLM-extractable draft.
Target output: GEO-era content engineered for AI citation in healthcare SaaS.

Five layers: **skills** (reusable knowledge), **subagents** (isolated workers),
**commands** (user workflows), **hooks** (deterministic gates), **MCP** (external access).

Decision tree for new capabilities:
- Must block unconditionally → hook
- Requires external data → MCP server
- Multi-step isolated task → subagent
- Reusable cross-tool knowledge → skill
- One-shot user workflow → slash command

Full spec: `docs/ARCHITECTURE.md`. Data contracts: `docs/DATA_CONTRACTS.md`.

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
show" — these require the same sourcing discipline as direct claims.

**BOFU asset types only.** This repo produces: `comparison`, `roi_calculator`, `case_study`,
`implementation_guide`, `quick_answer`, `refresh`. Each has a skill file governing structure.
Read the relevant skill before writing content.

**Brand voice.** Load `.claude/skills/tebra-brand-voice/SKILL.md` before drafting.
Tebra's voice is direct, evidence-forward, written for independent practice operators.

---

## Source citation rules

1. Load `sources/registry.json` to verify source availability before citing.
2. Verify `expires_at` is in the future. Expired sources cannot be cited.
3. Verify the claim type appears in the source's `approved_for_claims[]`.
4. Use `cite_as` as the display citation string.
5. Run `python3 -m scripts.validate_sources` if you modify the registry.

---

## Workflow: brief → draft

1. **Brief** (`briefs/<slug>.json`) created by `brief-author` subagent or operator.
   Must pass `python3 -m scripts.validate_briefs` before draft starts.
2. **Draft** (`drafts/<slug>.md`) written by `draft-writer` subagent.
   Compliance gate fires automatically on every write. Max 3 retries before escalation.
3. **Review** — PMM approval before any Webflow publish action.
4. **Publish** — operator action only; never automated.

---

## Subagent roles

| Subagent | File | When |
|---|---|---|
| brief-author | `.claude/agents/brief-author.md` | Creating new content brief |
| draft-writer | `.claude/agents/draft-writer.md` | Writing a draft from approved brief |
| citation-auditor | `.claude/agents/citation-auditor.md` | Scoring a URL for LLM extractability |
| refresh-auditor | `.claude/agents/refresh-auditor.md` | Checking content staleness |
| compliance-qa | `.claude/agents/compliance-qa.md` | Nuanced second-pass on hedged claims |
| product-truth | `.claude/agents/product-truth.md` | Grounding implementation guides in Drive docs |
| citation-reporter | `.claude/agents/citation-reporter.md` | Weekly citation performance report |

Each subagent runs in isolated context. Do not chain subagent calls within the same context.

---

## Compliance rules

The PreToolUse hook (`pre-tool-use-compliance.sh`) blocks writes to `drafts/` that contain:
- Unsourced percentage claims
- Unsourced clinical outcome language
- Medical claims without a registry source approved for that claim type
- Expired source citations

**Never bypass this gate** via `--no-verify`, skip-ci, or any equivalent.
If denied 3 times, stop and surface the specific flagged claim to the operator.

---

## Audit trail

All audit files are append-only:
- `audit/compliance.jsonl` — every compliance hook decision
- `audit/publish.jsonl` — every draft commit touching `drafts/`
- `audit/citation-scores.jsonl` — every URL extractability score
- `audit/citation-report-*.md` — weekly citation performance reports

Never truncate, overwrite, or manually append to these files.

---

## Key file locations

| Purpose | Path |
|---|---|
| Full specification | `docs/PRD.md`, `docs/ARCHITECTURE.md`, `docs/DATA_CONTRACTS.md` |
| Build milestones | `docs/TASKS.md` |
| Operator manual | `docs/RUNBOOK.md` |
| Decision log | `docs/RESEARCH_GAPS_AND_DECISIONS.md` |
| Source registry | `sources/registry.json` |
| Compliance check | `scripts/compliance_check.py` |
| Pydantic schemas | `scripts/schemas.py` |

---

## Forbidden patterns

- Do not invent claims. Surface gaps rather than filling them.
- Do not commit drafts with unresolved compliance denials.
- Do not modify `sources/registry.json` without operator approval.
- Do not read or log credential values from environment variables.
- Do not use `git push --force` on main.
- Do not bypass compliance hooks.

---

## Testing

```bash
python3 -m pytest -x -q                    # full suite (bare pytest resolves to 3.9 shim)
python3 -m scripts.validate_sources        # source registry check
python3 -m scripts.validate_briefs         # brief schema check
python3 -m scripts.validate_drafts         # draft frontmatter check
python3 -m scripts.validate_skills         # skill frontmatter check
python3 -m scripts.validate_mcp_config     # MCP config check
python3 -m ruff check .                    # lint
```

All four must pass before any commit to main.
