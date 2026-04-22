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
