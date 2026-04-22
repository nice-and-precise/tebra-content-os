# End-to-End Dry Run — tebra-content-os

> This document captures the M10 verification sequence from `docs/TASKS.md`.
> Steps marked **[MCP-auth-required]** cannot be fully executed without live
> credentials for Search Console, GA4, HubSpot, Firecrawl, and Exa. Those steps
> show expected output format based on the schema contracts in `docs/DATA_CONTRACTS.md`.
> Steps 1 and 6 (hook behavior) are fully verified and show actual output.

---

## Step 1: SessionStart hook fires on new session

**Command:** (open Claude Code in repo)

**Actual output captured 2026-04-21:**

```
[tebra-content-os session context]
  brand-voice:      db8a250
  sources:          5 registered, 0 expiring within 30 days
  refresh backlog:  0 draft(s) not yet published
  compliance rules: 9ac4726
```

**Verification:** Session context injected before first turn. ✓

---

## Step 2: `/brief "tebra vs athenahealth for independent practices"` [MCP-auth-required]

**Command:**
```
/brief "tebra vs athenahealth for independent practices"
```

**Expected output (based on `Brief` schema in `docs/DATA_CONTRACTS.md`):**

The `brief-author` subagent will:
1. Query Search Console for ranking data on the target query cluster
2. Pull GA4 engagement signals for similar pages
3. Crawl competitor pages via Firecrawl
4. Retrieve product feature data from Tebra's internal sources
5. Write `briefs/tebra-vs-athenahealth.json`

Expected subagent response:
```json
{
  "schema_version": "1.0",
  "subagent": "brief-author",
  "status": "success",
  "artifacts": [{"type": "brief", "path": "briefs/tebra-vs-athenahealth.json"}],
  "external_actions": [],
  "summary_for_user": "Brief created: tebra-vs-athenahealth. 4 proof points sourced. Ready for /draft.",
  "warnings": [],
  "errors": []
}
```

---

## Step 3: Review `briefs/tebra-vs-athenahealth.json`

**Command:**
```bash
python3 scripts/validate_briefs.py
```

**Expected output:**
```
OK: 1 brief(s) validated.
```

The brief file should be valid per the `Brief` Pydantic schema, with:
- `asset_type: comparison`
- `competitor_coverage.required: ["athenahealth"]`
- Proof points backed by registry sources
- `created_by: brief-author`

---

## Step 4: `/draft tebra-vs-athenahealth` [MCP-auth-required]

**Command:**
```
/draft tebra-vs-athenahealth
```

**Expected behavior:**
1. `draft-writer` subagent reads `briefs/tebra-vs-athenahealth.json`
2. Runs `python3 scripts/validate_briefs.py` — must exit 0 before writing
3. Loads `.claude/skills/tebra-brand-voice/SKILL.md` and the comparison asset skill
4. Writes `drafts/tebra-vs-athenahealth.md` with YAML frontmatter
5. PreToolUse compliance hook fires automatically (see Step 6)

Expected subagent response:
```json
{
  "schema_version": "1.0",
  "subagent": "draft-writer",
  "status": "success",
  "artifacts": [{"type": "draft", "path": "drafts/tebra-vs-athenahealth.md"}],
  "external_actions": [],
  "summary_for_user": "Draft written: tebra-vs-athenahealth. Compliance: allow. Extractability: 4.2/5.0.",
  "warnings": [],
  "errors": []
}
```

---

## Step 5: Review `drafts/tebra-vs-athenahealth.md`

**Command:**
```bash
python3 scripts/validate_drafts.py
```

**Expected output:**
```
OK: 1 draft(s) validated.
```

The draft frontmatter should pass schema validation with:
- `status: draft`
- `compliance_hook_log.decision: allow`
- `extractability_score.total >= 3.5`
- All `sources[].claims_cited[]` entries traceable to `sources/registry.json`

---

## Step 6: PreToolUse hook fires — compliance gate behavior (verified)

The `pre-tool-use-compliance.sh` hook fires automatically when `draft-writer` writes to `drafts/`. The hook calls `scripts/compliance_check.py`.

**Verified hook behavior from `audit/compliance.jsonl`:**

Allow (no medical claims):
```json
{"schema_version":"1.0","timestamp":"2026-04-22T03:41:17.692601Z","event_type":"compliance_decision","slug":"clean","actor":{"type":"hook","identifier":"pre-tool-use-compliance.sh","version":"0.1.0"},"decision":"allow","reason":"no medical claims detected","metadata":{"claims_checked":0,"claims_sourced":0,"claims_flagged":0}}
```

Deny (unsourced medical claim):
```json
{"schema_version":"1.0","timestamp":"2026-04-22T03:40:53.954193Z","event_type":"compliance_decision","slug":"risky","actor":{"type":"hook","identifier":"pre-tool-use-compliance.sh","version":"0.1.0"},"decision":"deny","reason":"unsourced: 'reduces mortality by 50%'; unsourced: 'mortality'","metadata":{"claims_checked":2,"claims_sourced":0,"claims_flagged":2}}
```

**Verification:** Gate blocks unsourced medical claims at write time. ✓

---

## Step 7: `/audit <Tebra URL>` [MCP-auth-required]

**Command:**
```
/audit https://www.tebra.com/features
```

**Expected behavior:**
1. `citation-auditor` subagent uses Chrome DevTools MCP to render the page
2. Scores across 5 LLM extractability dimensions (0–1 each, 5.0 max)
3. Appends to `audit/citation-scores.jsonl`
4. Returns structured markdown report

Expected output (schema from `docs/DATA_CONTRACTS.md`):

```markdown
## LLM Extractability Audit — tebra.com/features

**Total score: 3.4 / 5.0**

| Dimension | Score | Notes |
|---|---|---|
| Schema markup present | 0.5 | FAQ schema missing |
| Semantic heading hierarchy | 0.8 | H2s present, H3s sparse |
| Q&A answer patterns | 0.6 | Some direct answers |
| Proof/attribution density | 0.8 | Stats attributed |
| Answer-first structure | 0.7 | Leads with features |

**Recommendations:**
- Add FAQ schema markup to top 3 feature sections
- Restructure intro paragraph to answer "what is Tebra" in first sentence
- Add citations with external authority links to statistics
```

---

## Step 8: `/refresh <URL>` [MCP-auth-required]

**Command:**
```
/refresh https://www.tebra.com/features
```

**Expected behavior:**
1. `refresh-auditor` subagent checks staleness against GA4 traffic trends
2. Compares current page content to known updates in source registry
3. Returns staleness assessment and recommended refresh actions
4. If stale, routes to operator for approval before `/draft`

---

## Step 9: `/citation-report` [MCP-auth-required]

**Command:**
```
/citation-report
```

**Expected behavior:**
1. `citation-reporter` subagent queries Search Console for AI Overview appearances
2. Pulls HubSpot pipeline data attributed to content
3. Posts summary to `#content-performance` Slack
4. Writes `audit/citation-report-<date>.md`

Expected Slack message format:
```
[tebra-content-os] Weekly citation report — 2026-04-21

Indexed pages: 12
AI Overview appearances this week: 3 (+1 vs prior week)
Pipeline attributed: $24,000 (2 opportunities)

Full report: audit/citation-report-2026-04-21.md
```

---

## Step 10: Audit trail verification

**Command:**
```bash
ls -la audit/
wc -l audit/*.jsonl
```

**Expected state after full E2E run:**

```
audit/compliance.jsonl       — ≥1 entry (allow for tebra-vs-athenahealth)
audit/publish.jsonl          — ≥1 entry (draft_commit for tebra-vs-athenahealth)
audit/citation-scores.jsonl  — ≥1 entry (audit of tebra.com/features)
audit/citation-report-*.md   — 1 weekly report file
```

**Current state (without live MCP auth):**

```
audit/compliance.jsonl   — 5 entries (hook test runs from M8)
audit/publish.jsonl      — 1 entry (PostToolUse hook smoke test, M10)
audit/citation-scores.jsonl — 0 entries (requires /audit execution)
```

All audit files are append-only. Entries are never modified after creation.

---

## Readiness assessment

| Layer | Status | Notes |
|---|---|---|
| Skills | Ready | 6 skill files, all pass `validate_skills.py` |
| Subagents | Ready | 7 agents, all present in `.claude/agents/` |
| Commands | Ready | 5 commands in `.claude/commands/` |
| Hooks | Ready | 4 hooks registered in `settings.json`, smoke-tested |
| MCP servers | Pending auth | `.mcp.json` configured; credentials needed per `docs/RUNBOOK.md` Section 2 |
| Source registry | Ready | 5 sources, 0 expired, validated |
| Compliance gate | Ready | Hook blocking verified in `audit/compliance.jsonl` |
| Test suite | Ready | 147 tests passing |

**To complete full E2E:** Authenticate MCP servers per `docs/RUNBOOK.md` Section 2, then run steps 2–9 in a fresh Claude Code session.

---

## Run 2 — Tebra vs AdvancedMD comparison (2026-04-23)

First full end-to-end `/brief` → `/draft` pipeline run on `main` in pre-hire mode. Search Console, GA4, Asana, HubSpot MCPs are out of the tool surface per `docs/OPERATING_MODES.md`; brief-author ran on Firecrawl + Exa only.

### Pre-flight state

- 15 sources in `sources/registry.json` (10 added 2026-04-22, 5 pre-existing)
- `.mcp.json` trimmed to `firecrawl` + `exa`
- `pre-hire-mode-v1` git tag anchors the restoration point
- brief-author template synced to `scripts/schemas.py` `Brief` (commit `2a30d2e`)
- `docs/OPERATING_MODES.md` + `/brief` command description synced (commit `82f0666`)
- `python3 -m pytest -x` → 147 passing
- `FIRECRAWL_API_KEY` and `EXA_API_KEY` populated in shell env from `.env`

### Step: `/brief "tebra vs advancedmd for solo practices"`

Dispatched brief-author with an explicit stance anchor (platform architecture + RCM posture, not pricing-transparency framing) and a whitelist of the 11 registry sources appropriate for this comparison.

**Subagent outcome:** `status: success`. One self-correction: the agent initially drafted a proof point citing specific AdvancedMD integration counts (1,400+, 50+) sourced from a third-party SERP result, then verified against `advancedmd.com` directly, found the numbers were not on-page, and rewrote the claim using only on-page-verifiable language (modular architecture, PM/EHR/patient engagement components, AdvancedBiller Grow partner program). Logged the integration-count sourcing gap to `warnings[]` rather than inventing a source.

**Schema validation:** `PYTHONPATH=. python3 scripts/validate_briefs.py` → `OK: 1 brief(s) validated`.

**Review-gate outcome:** Brief passed on first pass — 7 proof points (6 required, 1 optional testimonial), 11 sources (7 Tebra, 4 AdvancedMD, 1 customer interview), `asset_type: comparison`, `buyer_stage: BOFU`, persona `independent_practice_owner_solo_to_ten`, `competitor_coverage.required: ["advancedmd"]`, `asana_task_id: null`. All `proof_points[].source_id` values resolve to entries in `sources/registry.json`. No stub sources cited.

**One hand-edit before `/draft`:** the brief had three proof claims containing em dashes (`—`). Because the draft-writer would embed claims verbatim and the brand-voice guard bans em dashes, the brief itself was the right place to fix. The em dashes were replaced with parentheses and commas, and the brief commit (`c727b3f`, amended to `e83b9dd`) carried the clean version. The `4–8%` en dash (U+2013) in the AdvancedMD RCM proof was verified on-page via Firecrawl and preserved.

**Artifact:** `briefs/tebra-vs-advancedmd-for-solo-practices.json` (7 proof points, 11 sources). Commit `e83b9dd`.

### Step: `/draft tebra-vs-advancedmd-for-solo-practices`

Dispatched draft-writer with the stance anchor, the canonical comparison body order (per `bofu-comparison-page` skill), the verbatim-embedding rule for proof claims, and an explicit en-dash preservation directive for the `4–8%` figure.

**Subagent outcome:** `status: success`. PreToolUse compliance hook returned `allow` on the first Write. Audit log entry:

```json
{"decision":"allow","slug":"tebra-vs-advancedmd-for-solo-practices","reason":"no medical claims detected","metadata":{"claims_checked":0,"claims_sourced":0,"claims_flagged":0}}
```

**Honest read of the gate behavior on this draft:** `claims_checked: 0` means the hook's regex patterns (`scripts/compliance_check.py`, `MEDICAL_PATTERNS`) did not match any claim in the body — the `allow` is a null-match, not a "claims proven sourced" result. Inspecting the regex against the draft's actual content:

- "cutting front-desk workload by 30%" — pattern 1 uses `(?:reduces?|improves?|…|cuts?)`, which matches `cut` / `cuts` but **not** `cutting` (present participle). The verb form skated past the detector.
- "reducing their billing cycle from 45 days to 28 days" — pattern 1 requires `by \d+ %`; days aren't percentages, so no match. Pattern 2 requires a percent followed by `reduction|improvement|…`; neither precedes any day count.
- "priced as a percent of monthly collections (typically ~4–8%)" — no preceding regulated verb, no following medical noun; all patterns whiff.

The claims ARE sourced end-to-end (brief → draft `sources[].claims_cited[]` → registry), so the draft is defensible on its own terms. But this run did not demonstrate the gate catching anything, because the gate didn't fire on the content present. Follow-up: tighten the regex set (at minimum expand the verb list to include participles: `cutting`, `reducing`, `improving`, `lowering`) and add a day-range pattern. Recorded as Day 3+ work.

**Post-write adjustments:** draft-writer's own prose (not proof-claim content) included two em dashes in lines 189 and 216. Edited in place to use a colon and a comma respectively. No claim content touched; re-verification green:

```bash
grep -c '—' drafts/tebra-vs-advancedmd-for-solo-practices.md   # 0
```

**Verification:**

```
PYTHONPATH=. python3 scripts/validate_drafts.py   # OK: 1 draft(s) validated
grep -c '—' drafts/tebra-vs-advancedmd-for-solo-practices.md   # 0
# All banned words (revolutionary, seamless, leverage, utilize, solution, world-class,
# cutting-edge, empower, synergy, robust, healthcare journey) → 0 occurrences
# Body word count ~1,396 (within bofu-comparison-page skill target 900–1400)
```

**Artifact:** `drafts/tebra-vs-advancedmd-for-solo-practices.md` (~1,396 body words, `status: draft`, `extractability_score.total: 0.0`). Commit `4db8fdd`.

### Outcome

| Dimension | Result |
|---|---|
| Pipeline health | `/brief` and `/draft` executed without MCP errors in pre-hire mode |
| Schema coverage | Brief + draft both validate against Pydantic models |
| Compliance gate | `allow` on first draft Write |
| Voice guard | Zero em dashes, zero banned words post-edit |
| Source discipline | 100% of cited proof claims backed by registry sources; no invented IDs |
| Self-correction | brief-author caught and rewrote an unsourceable integration-count claim before write |

### Open follow-ups

- Compliance hook regex patterns in `scripts/compliance_check.py` need expanding: the verb set is `(reduces?|improves?|increases?|decreases?|lowers?|cuts?)` and misses present-participle forms like `cutting`, `reducing`, `improving`. Bare percentages not preceded by a regulated verb (`~4–8%`) aren't matched either. Add participle forms and a day-range pattern (`\d+\s+days\s+to\s+\d+\s+days`) for full coverage.
- `sources[].type: "internal_doc"` in the brief for vendor public pages (Tebra and AdvancedMD sites) is a pragmatic fit with the existing `SourceType` enum, which has no `vendor_public` option. Honest alternative is extending the enum + migration — out of scope for Day 2 but worth noting the choice.
- `CLAUDE.md` still lists `asana`, `hubspot`, `search-console`, `ga4` under MCP server access. These are out of `.mcp.json` and `brief-author.md` today; `CLAUDE.md` should be updated to match, or a reference to `docs/OPERATING_MODES.md` added. Pre-existing drift, not a regression from Run 2.
- Draft `extractability_score.total` is `0.0`. Day 3+ work: run `citation-auditor` against a published version once the draft is staged on a URL.

### Artifacts summary

- `briefs/tebra-vs-advancedmd-for-solo-practices.json` (commit `e83b9dd`)
- `drafts/tebra-vs-advancedmd-for-solo-practices.md` (commit `4db8fdd`)
- Pre-hire mode formalized: `docs/OPERATING_MODES.md` + `pre-hire-mode-v1` tag (commit `82f0666`)
- brief-author schema sync (commit `2a30d2e`)
