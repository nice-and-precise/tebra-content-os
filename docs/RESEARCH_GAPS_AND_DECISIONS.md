# RESEARCH_GAPS_AND_DECISIONS: tebra-content-os

**Status:** Draft v0.1 · April 21, 2026
**Depends on:** `PRD.md`, `ARCHITECTURE.md`, `DATA_CONTRACTS.md`, `TASKS.md`, `RUNBOOK.md`
**Audience:** Future-Jordan (or any future operator) trying to remember *why* something was built a certain way, or trying to figure out what is still undecided.

---

## 1. How this file is used

Three jobs:

1. **Decision log.** Every non-trivial design decision gets one row. Date, decision, rationale. If a decision gets revisited later, the old row stays (crossed out or annotated) and a new row is added. Nothing is deleted. The log is the institutional memory.

2. **Open questions.** Things that are genuinely undecided and need operator input before they can be resolved. Organized by whether they block v1 or not. If a question has been sitting unanswered for more than 30 days, it either needs to be resolved or explicitly deferred to v1.1.

3. **Version-pinning reference.** One place to check what version of what is currently pinned, so an upgrade doesn't silently break four other things.

**When to update:** any time a decision is made (however small), any time a new open question surfaces, any time a pinned version is considered for upgrade. Treat this file the way a mature engineering team treats an ADR directory — it is cheap to add to, expensive to let go stale.

**How to update:** add rows, don't rewrite history. Every entry has a date so the timeline is readable. If a decision is reversed, add a new row marking the reversal and cross-reference the superseded row. Decisions don't disappear; they get overridden explicitly.

---

## 2. Decision log

### 2.1 Architectural decisions (the spine)

| Date | Decision | Rationale | Status |
|---|---|---|---|
| 2026-04-21 | **Repo is the product.** No external services, no containers, no databases. State lives in git-tracked markdown and JSON. | Keeps the system auditable and clonable. A hiring team can inspect every decision in one directory tree. Also the only way freelancers get parity with the internal team without managing infrastructure. | Active |
| 2026-04-21 | **AMIE docs pattern adopted** (PRD / ARCHITECTURE / DATA_CONTRACTS / TASKS / RUNBOOK / RESEARCH_GAPS / REPO_PRINCIPLES). | Proven in production on a shipped system. Reusing what works is cheaper than reinventing. The April 2026 Claude Code primitives slot into this doc structure cleanly. | Active |
| 2026-04-21 | **Five primitive layers** with one responsibility each: skills (procedural knowledge), subagents (isolated-context workers), slash commands (user workflows), hooks (deterministic gates), MCP servers (external access). Confusing layers is the most common architectural mistake. | Matches the April 2026 Claude Code primitives. The decision tree ("if it must happen → hook; if external → MCP; if multi-step → subagent; if reusable knowledge → skill; if one-shot user action → command") is the rule of thumb that makes future decisions fast. | Active |
| 2026-04-21 | **PreToolUse hook is the compliance gate.** Not a prompt, not a skill, not a subagent. | PreToolUse is the only Claude Code primitive that can deterministically block. The "no AI slop" claim requires a deterministic gate; anything softer is hope. | Active |
| 2026-04-21 | **Skills carry cross-tool-portable knowledge.** Subagents are Claude Code-only. If Tebra's actual workflow uses Cursor, Codex CLI, Gemini CLI, or anything else, skills still work because of the Agent Skills Standard. | Portability insurance. Doesn't cost anything up front and de-risks every "what if they don't use Claude Code for this piece" scenario. | Active |
| 2026-04-21 | **Git is the database.** Briefs, drafts, sources, audit logs all live as files in git. No SQLite, no Postgres, no cloud database. | Auditability. Every change is a commit with an author and a diff. If query shape ever exceeds what `grep` and `jq` can do, that's a v2 signal to consider an index — not a v1 justification to adopt a database. | Active |
| 2026-04-21 | **Bash hooks, not Python hooks.** Hook scripts are `.sh` files that shell out to Python via CLI invocation. | Two reasons: (1) universal — any POSIX shell runs them, no Python startup cost in the blocking path; (2) the Claude Code hook spec expects stdin JSON in, stdout JSON out, and shells do that natively. Python hooks exist and work, but add a runtime dep to the blocking path for no benefit here. | Active |
| 2026-04-21 | **JSONL for audit logs, not SQLite.** One event per line, append-only, rotated monthly when >100 MB. | Append-only is the auditability property that matters. JSONL is greppable and reviewable by humans. A database would let us do richer queries, but those queries aren't the bottleneck — the regulatory review is, and reviewers read text better than they read SQL. | Active |

### 2.2 Technology and tooling decisions

| Date | Decision | Rationale | Status |
|---|---|---|---|
| 2026-04-21 | **Streamable HTTP transport default** for all MCP servers; SSE only where no HTTP endpoint exists. | MCP spec 2025-11-25 deprecated SSE. Atlassian sunsets June 30, 2026. Other vendors following. Building on SSE now is building on a deprecated transport. | Active |
| 2026-04-21 | **Cache TTL pinned `"ttl": "1h"` explicitly** in every `cache_control` block the system emits. | March 2026 silent API regression (1h default → 5-minute default) cost developers 17–32% on identical workloads. Explicit pinning is cheap insurance against a repeat. | Active |
| 2026-04-21 | **Pydantic v2** for all data-contract schemas. Not v1, not msgspec, not dataclasses. | Pydantic v2 is the current stable version with the best validator ergonomics for the contract complexity here (conditional required fields, cross-field validation, enum handling). Msgspec is faster but its ecosystem is narrower; dataclasses don't give us validation. | Active |
| 2026-04-21 | **Python 3.11 minimum.** | `typing` ergonomics, `tomllib` in the standard library, performance improvements that matter for the CLI tooling. Python 3.10 works for most of the code but adds friction for no meaningful gain. | Active |
| 2026-04-21 | **MIT license** as default. | Most permissive reasonable choice for a portfolio/proof-of-work repo. If Tebra later forks for internal use, MIT doesn't create friction. Apache 2.0 was considered for its patent grant; MIT preferred for simplicity absent a specific patent concern. | Active; operator can override |
| 2026-04-21 | **No .ps1 hook duplicates for Windows.** Windows operators use WSL2 or Git Bash. | Double maintenance + divergence risk. Every hook would need to be kept in sync across two shell dialects. WSL2 is the current Windows standard for POSIX workflows; mandating it eliminates a whole class of "works on one shell, breaks on the other" bugs. | Active |
| 2026-04-21 | **No plugin marketplace.** The repo is the plugin. Freelancers install via `/plugin install <repo-path>` directly. | Adding a marketplace layer introduces hosting, versioning, and distribution overhead for no v1 benefit. The repo-as-plugin model works for the Tebra scope (one internal team + freelancers). A marketplace can be a v2 consideration if the plugin gets adopted by external teams. | Active |
| 2026-04-21 | **CitationSource model simplified (all fields optional) in Milestone 1.** `CitationSource` accepts `type: base64|url|text|content` with all source-type-specific fields (`media_type`, `data`, `url`) declared optional rather than using a discriminated union per type. | Discriminated union is the tighter design — `base64` should require `media_type`+`data`; `url` should require `url`. Deferred to Milestone 3 (citation-auditor subagent) when the actual API call shape is validated end-to-end. A discriminated union now would add ~40 lines of boilerplate for a constraint that won't be exercised until M3. Revisit when `scripts/compliance_check.py` starts building `CitationSource` objects from real document paths. | Active; tighten at M3 |
| 2026-04-21 | **No scheduled jobs running locally.** Weekly citation-report triggered by operator running `/citation-report`, not by cron on the operator's machine. | Local cron is fragile (machine sleeping, user logged out, battery-saver throttling). If real scheduling is needed, GitHub Actions on a cron schedule is the v1.1 path — runs in a known environment, leaves an audit trail, doesn't depend on any one operator's laptop being awake. | Active |
| 2026-04-21 | **Credential rotation reminders in v1.** SessionStart hook reads `audit/credential-metadata.json` and warns on any credential older than 75 days. Operator records rotations via `scripts/record_rotation.py <credential_name>`, which updates the metadata file with today's date. | Token expiration in production is a silent failure mode — a pipeline breaks at 2am for a reason that takes 30 minutes to diagnose. A 75-day warning (15 days before the 90-day rotation cadence) gives the operator a forcing function at session start. Cheap to implement, high downside if skipped. Promoted from "deferred" (Section 5.3) after review. | Active v1 |
| 2026-04-21 | **Asana authentication: PAT for v1, OAuth required before production deployment.** v1 proof-of-work uses Personal Access Token (simpler, no OAuth flow in the hook path). Tebra production deployment requires OAuth upgrade — this is a hard gate, not a nice-to-have. | PAT unblocks the v1 proof-of-work immediately without building an OAuth implementation. OAuth becomes a v1.1 must-have because healthcare SaaS security reviews will not accept shared per-machine tokens for systems adjacent to PHI workflows. Framing OAuth as "required before production" rather than "if required" removes the ambiguity that causes security items to slip. | Active v1; OAuth migration is v1.1 must-have (not optional) |

### 2.3 Model routing decisions (reviewable each model release)

| Date | Decision | Rationale | Reconsideration trigger |
|---|---|---|---|
| 2026-04-21 | **Opus 4.7 for draft-writer and product-truth** subagents. | These are the generation-quality compounding surfaces. Draft quality upstream affects extractability downstream affects citation downstream affects pipeline. Worth the token cost. | Any new Opus release; benchmark before switching. |
| 2026-04-21 | **Sonnet 4.6 for brief-author, citation-auditor, refresh-auditor, citation-reporter.** | These are retrieval + analysis shaped tasks where quality matters but the task is structured. Sonnet 4.6 hits the cost/quality balance. | Any new Sonnet release. |
| 2026-04-21 | **Haiku 4.5 for compliance-qa.** Dated string pin: `claude-haiku-4-5-20251001`. | Compliance-qa runs in the blocking path of every draft commit. Speed matters, and the task is classification-shaped (good-fit for Haiku). Dated string because Haiku 4.5's behavior was calibrated against this specific release. | Any new Haiku release, but pin only updates after benchmark against compliance test suite. |
| 2026-04-21 | **Opus 4.7 tokenizer surprise documented but accepted.** ~35% more tokens for identical English text vs Sonnet 4.6. | The quality premium is real; the cost premium is the price of that premium. Budget for it explicitly rather than switching models to avoid it. | Reconsider if Anthropic ships a future Opus that narrows the gap at the tokenizer level. |

### 2.4 Proof-of-work scope decisions

| Date | Decision | Rationale | Status |
|---|---|---|---|
| 2026-04-21 | **Proof-of-work shifted** from hand-executed 10-URL citation audit PDF to full spec package + runnable citation-auditor subagent. | The role's JD is an agentic-system specification. A hand-executed audit proves "I can do the work once." A runnable system proves "I can operate the role's system design responsibility." Different signal, higher ceiling. | Active (supersedes v1 plan) |
| 2026-04-21 | **Minimum viable proof-of-work is Milestones 0–4** of TASKS.md: scaffolding, schemas, compliance hook, citation-auditor subagent, brief-author + draft-writer + refresh-auditor. | If the remaining milestones slip past Day 7, the repo still demonstrates competence through M4. Anything beyond M4 is upside. | Active |
| 2026-04-21 | **Half-built spec reads as overreach, not ambition.** Hard discipline on M0–M4 completion before attempting M5+. | Hiring signal reverses if the repo looks abandoned mid-milestone. Tight scope with completion beats ambitious scope with holes. | Active |

### 2.5 Documentation and style decisions

| Date | Decision | Rationale | Status |
|---|---|---|---|
| 2026-04-21 | **CLAUDE.md ~250 line hard ceiling.** Code style rules live in ruff/prettier invoked by Stop hook; workflow specifics live in skills; data contracts live in DATA_CONTRACTS.md. | April 2026 research: models reliably follow ~150 instructions in a system-level prompt. Past that, all rules degrade, not just new ones. CLAUDE.md is the last place to add a rule, not the first. | Active |
| 2026-04-21 | **AGENTS.md mirrors CLAUDE.md** for cross-tool standard compatibility (Cursor, Codex CLI, Gemini CLI). | Tebra's actual tooling isn't known pre-interview. AGENTS.md works across the field; CLAUDE.md works in Claude Code specifically. Mirroring costs one file; not mirroring costs portability. | Active until Claude Code ships native AGENTS.md support (tracked anthropics/claude-code#34235, #6235). |
| 2026-04-21 | **Em dashes kept in spec docs** (PRD, ARCHITECTURE, DATA_CONTRACTS, TASKS, RUNBOOK, this file). | Matches authorial voice; em dashes are a prose preference for the Jordan-Claude working relationship. Not a blanket requirement for all published docs — README.md and freelancer-facing docs should use more neutral punctuation. | Active |

---

## 3. Version pinning reference

Single source of truth for "what version of what are we on." Every field here should match what's actually in code/config. Drift between this table and reality is a bug — when spotted, update both.

### 3.1 Runtime and language pins

| Component | Pinned version | Where enforced | Upgrade risk |
|---|---|---|---|
| Claude Code CLI | 2.1.111 or later | RUNBOOK prereqs; `scripts/validate_repo.py` checks at install | Low — CLI has been backward-compatible through 2.x |
| MCP spec | 2025-11-25 | `.mcp.json` transport declarations | Medium — spec still evolving through 2026 |
| Python | 3.11 or later | `pyproject.toml` `requires-python = ">=3.11"`; CI matrix pins 3.11 and 3.12 | Low — 3.12 already tested |
| Node.js | 20 LTS or later | Required only for MCP servers shipping as npm packages; not enforced in `package.json` since there isn't one | Low |
| Pydantic | v2.x | `pyproject.toml` dep spec | Medium — v3 when it arrives will require migration |

### 3.2 Model aliases and dated strings

| Use | Pin | Why this shape |
|---|---|---|
| draft-writer, product-truth | `claude-opus-4-7` (alias) | Alias-based because Opus 4.x behavior has been stable across dot releases |
| brief-author, citation-auditor, refresh-auditor, citation-reporter | `claude-sonnet-4-6` (alias) | Same reasoning |
| compliance-qa | `claude-haiku-4-5-20251001` (dated string) | Dated string because compliance-qa's test suite was calibrated against this specific release; any behavior drift in a later Haiku needs benchmark-then-accept |

Upgrade policy: aliases auto-advance on dot releases; dated string requires manual bump + re-run of `tests/test_compliance_check.py`. If any test fails post-bump, investigate before accepting.

### 3.3 Schema versions (DATA_CONTRACTS.md)

| Entity | Schema version | Migration script path |
|---|---|---|
| Brief | 1.0 | `scripts/migrations/` (empty for v1; populate at v1→v2 boundary) |
| Draft (frontmatter) | 1.0 | same |
| Source | 1.0 | same |
| CitationRecord (Anthropic API format, not owned by us) | Anthropic spec as of April 2026 | Vendor-controlled; migration is their problem |
| AuditEvent | 1.0 | same |
| SubagentResponse | 1.0 | same |

Every breaking schema change = version bump + migration script + dual-read support in consumers for at least one minor version + entry in Section 2 of this doc.

### 3.4 Plugin and package versions

| Component | Pin | Notes |
|---|---|---|
| `tebra-content` plugin | 1.0.0 (target at M12 release) | Semver: major on schema breaks, minor on feature add, patch on fix |
| `.mcp.json` format | Claude Code settings spec as of April 2026 | Vendor-controlled |
| `.claude/settings.json` format | Claude Code settings spec as of April 2026 | Vendor-controlled |

---

## 4. Open questions — blocking

These need resolution before v1 is production-ready. Each one has a default answer in case the operator doesn't respond before v1 ship; the default is what the system does today.

### 4.0 Resolutions — 2026-04-21

All six blocking questions resolved on the day this file was drafted. Summary below; full reasoning preserved in each question's original text for the record.

- **4.1** → Wire **both** Profound and Peec AI for v1. Revisit after **10 days** of real usage data (tightened from the initial 60-day recommendation — a faster feedback loop on which source actually moves decisions).
- **4.2** → **Slack DM digest** for v1 compliance review. Dashboard is a v1.1 external build and lives outside this repo.
- **4.3** → Build Webflow MCP to the **standard Collections API with a clean adapter interface**, so a Tebra-specific variant is a swap, not a rewrite.
- **4.4** → Capture cost per brief during Milestone 10 dry run, project to 40 briefs, document in `docs/cost-model.md`. See note below on cost vs. impact.
- **4.5** → Ship with placeholder env var names now (`PROFOUND_API_KEY`, `PEEC_API_KEY`). At Milestone 5, read the real vendor docs and update RUNBOOK Section 4 and `.mcp.json`. If either vendor doesn't ship a native MCP server, build a thin stdio MCP adapter in `scripts/mcp_adapters/<vendor>/`.
- **4.6** → At Milestone 5, check Google's current MCP story AND enable whatever official Google Cloud APIs are available (Search Console API v1, Analytics Data API v1beta at minimum). If Google has shipped official MCP endpoints by then, use them. If not, write a minimal FastAPI shim wrapping the client libraries — throwaway code the moment Google ships native MCP.

**Note on 4.4 — cost vs. impact are not the same metric.** Cost envelope answers "what does it cost to run this system?" — API calls, cache, vendor fees. Business impact answers "what value does well-executed content drive?" — pipeline influence, revenue, savings. Both matter for the Tebra application but belong in different docs.

Jordan's concrete example — a maintenance-tech document he authored at Bayer Built that saved $252,000 per year by catching a misinterpretation of specialized equipment manuals — is an **impact** data point, not a cost data point. It is the caliber of quantified business outcome that belongs in the interview stories bank (Phase 6 per the plan) and in any cover-letter framing of "translate complexity into reliable delivery." Captured here as a cross-reference so it doesn't get lost between the spec work and the application work.

The cost-model doc tracks: $X per brief at Opus 4.7 draft-writer, $Y per audit at Sonnet 4.6 citation-auditor, total monthly run cost at 40-asset volume.

The stories bank tracks: $252K/year savings from a maintenance-tech document. BoreReady's DLI statutory approval as a regulated-content track record. AMIE's Iowa farmland pipeline. Each is an impact data point with a specific number and a specific outcome.

---

### 4.1 Primary citation tracking source: Profound, Peec AI, or both?

**Status:** Open.
**Owner:** Jordan (as operator of the Tebra submission), then Tebra's actual content team if the role is offered.
**Deadline:** Before first production `/citation-report` run. Non-blocking for Milestones 0–7; blocking for Milestone 8.
**Default if unresolved:** Wire both. Redundancy costs extra API calls but protects against single-vendor dropout (either vendor changing pricing, pivoting, or getting acquired).
**What changes with the answer:** If "Profound primary," the citation-reporter subagent queries Profound first and only falls back to Peec AI on error. If "both primary," results are merged and conflicts logged. The merged case is strictly more work but more defensible against single-point-of-failure.
**Recommendation:** Default to both for v1. Revisit after 60 days of real usage data on which source actually moves decisions.

### 4.2 Compliance reviewer delivery channel for `audit/compliance.jsonl`

**Status:** Open.
**Owner:** Tebra's healthcare compliance reviewer, via the eventual interview or first-week-in-role conversation.
**Deadline:** First production draft cycle. Blocking for any Tebra-internal rollout; non-blocking for portfolio proof-of-work.
**Options:**
- **Slack DM digest.** Reviewer gets a daily or weekly DM with new deny decisions. Pro: lowest friction. Con: easy to miss in Slack noise.
- **Email digest.** Same content, email format. Pro: persistent, searchable. Con: yet another inbox.
- **Dashboard.** A simple read-only web UI over `audit/compliance.jsonl`. Pro: purpose-built, filterable. Con: infrastructure overhead — this is a service, and v1 explicitly rejects running services.
**Default if unresolved:** Weekly Slack DM digest posted to the reviewer's DM. Uses Slack MCP, no new infrastructure.
**Recommendation:** Slack DM for v1. If the reviewer wants a dashboard, that's a v1.1 external build and lives outside this repo.

### 4.3 Webflow MCP compatibility with Tebra's actual Webflow instance

**Status:** Open — depends on Tebra's Webflow plan and configuration.
**Owner:** Tebra web team, once that conversation opens.
**Deadline:** Before first Webflow publish. Non-blocking for Milestones 0–11; blocking for Milestone 12.
**Risk:** If Tebra's Webflow instance is on a plan that doesn't expose the Collections API, or has custom publish flows that don't route through MCP, we need a stub adapter that simulates Webflow publish for local testing and routes actual publishes through whatever Tebra's real mechanism is.
**Default if unresolved:** Build the Webflow MCP integration against the standard Collections API. Mark it "unverified against Tebra's actual site" until Tebra's web team confirms compatibility.
**Recommendation:** Build to the standard API. Write a clean adapter interface so a Tebra-specific variant is a swap, not a rewrite.

### 4.4 Cost envelope at 40-asset monthly volume

**Status:** Open — needs real benchmark data.
**Owner:** Jordan, before claiming cost efficiency to Tebra.
**Deadline:** Before any resume/cover-letter language that mentions cost per asset. Specifically blocking for Phase 3 (resume surgery).
**What the answer depends on:** Opus 4.7 vs Sonnet 4.6 split (Section 2.3), cache hit rate (should be high with 1h TTL pinning), Citations API call count per draft (varies by asset type), MCP server request costs (mostly zero; a few vendors charge per call).
**Default if unresolved:** Do not make specific cost claims in application materials. Use directional framing ("cost-efficient at steady state") rather than numeric claims.
**Recommendation:** Run five representative briefs end-to-end in the M10 dry run. Capture cost per brief as a data point. Project to 40 briefs. Document the projection in a separate `docs/cost-model.md` once the data exists.

### 4.5 Profound and Peec AI exact API conventions

**Status:** Open — vendor docs need to be read against the `.mcp.json` stub.
**Owner:** Jordan, before Milestone 5.
**Deadline:** Milestone 5 (MCP server configuration).
**What's uncertain:** Exact env var names, endpoint URLs, auth header format, whether each vendor actually ships an MCP server or just a REST API that needs an MCP adapter built on top.
**Default if unresolved:** Use the placeholder env var names from RUNBOOK Section 4 (`PROFOUND_API_KEY`, `PEEC_API_KEY`). If either vendor doesn't ship a native MCP server, build a thin stdio MCP adapter that wraps their REST API.
**Recommendation:** Read the actual docs during Milestone 5. Update RUNBOOK Section 4 and `.mcp.json` with the real names. If an adapter is needed, it lives in `scripts/mcp_adapters/<vendor>/`.

### 4.6 Google Search Console and GA4 MCP hosting

**Status:** Open — Google may or may not have shipped official HTTP MCP endpoints by install time.
**Owner:** Jordan, before Milestone 5.
**Deadline:** Milestone 5.
**What's uncertain:** Whether the current `.mcp.json` stubs point to real Google-hosted HTTP MCP endpoints, a third-party hosted adapter, or a self-hosted shim.
**Default if unresolved:** Self-hosted shim using a minimal FastAPI wrapper around the Search Console and GA4 client libraries, exposed as stdio MCP. Adds modest operational complexity but keeps the system functional regardless of Google's MCP timeline.
**Recommendation:** Check Google's current MCP story during Milestone 5. If official endpoints exist, use them. If not, write the shim and keep it minimal — it's throwaway code the moment Google ships.

---

## 5. Open questions — non-blocking

These are real questions that deserve eventual answers, but nothing is stuck waiting on them.

### 5.0 Resolutions — 2026-04-21

- **5.1** → Deferred (not addressed this round); carried forward.
- **5.2** → **Decision made:** PAT for v1 proof-of-work. OAuth is a **v1.1 must-have before any Tebra production deployment**, not a nice-to-have. Healthcare SaaS security reviews will not accept shared per-machine tokens for systems touching PHI-adjacent content workflows. Added to Section 2.2 as a formal decision and to Section 8.2 migration targets with "required before production" status.
- **5.3** → **Decision made:** Credential rotation reminders ship in v1, not deferred. Implementation: `audit/credential-metadata.json` tracks `{credential_name: last_rotated_iso_date}`; the SessionStart hook reads it and warns on any credential older than 75 days (giving 15 days of buffer before the 90-day rotation cadence); operator records a fresh rotation via `scripts/record_rotation.py <credential_name>`. Added to Section 2.2 as a formal decision. Removed from Section 7 deferred list.
- **5.4** → Accepted as written. Defer until 500 draft commits of agreement data between the Python compliance check and the Haiku compliance-qa subagent.
- **5.5** → Accepted. Defer migration-strategy decisions until the first actual schema bump provides real pain signal.
- **5.6** → Accepted. Defer until Claude Code ships native AGENTS.md support (issues `anthropics/claude-code#34235` and `#6235`).
- **5.7** → Accepted. Defer until an external-adoption signal exists.
- **5.8** → **Not pursued.** Multi-tenant isolation is explicitly out of scope for this system and the operator is not interested in building a multi-customer SaaS from this codebase. Moved from "deferred" (could come back) to "not pursued" (intentionally closed). If a future direction changes this, it is a new system, not this one.

---

### 5.1 Freelancer credential scope

**Question:** Should freelancers running `/plugin install` get any MCP credentials (even read-only GA4 for self-check), or strictly none?
**Current answer:** Strictly none. Freelancers work against local drafts, internal team validates on push.
**Why it might get revisited:** If freelancers regularly ask "did my draft hit the target intent?" and the only way to answer is to wait for the internal team's check, that's a workflow bottleneck.
**Deferred until:** First 30 days of freelancer usage generates signal.

### 5.2 Asana OAuth vs Personal Access Token

**Question:** Should Asana auth be OAuth (per-user, refreshable) or PAT (per-machine, manually rotated)?
**Current answer:** PAT for v1. Simpler, no OAuth flow to implement in a hook script.
**Why it might get revisited:** If Tebra's security team requires OAuth for all integrations (not unreasonable for regulated healthcare SaaS).
**Deferred until:** Tebra security review surfaces a requirement, or 90-day rotation burden becomes real friction.

### 5.3 Credential rotation reminder system

**Question:** Should the system actively remind the operator to rotate 90-day tokens, or is that the operator's responsibility?
**Current answer:** Operator's responsibility. RUNBOOK Section 11.1 lists monthly rotation checks.
**Why it might get revisited:** If tokens expire unnoticed in production and a pipeline breaks at midnight.
**Deferred until:** First token expires unnoticed — then build the reminder. Premature tooling is worse than reactive tooling here.

### 5.4 compliance-qa subagent vs pure Python compliance check

**Question:** Is the Haiku-4.5-based compliance-qa subagent actually necessary, or is the Python claim detector sufficient?
**Current answer:** Both. Python catches obvious claims (regex-detectable shapes), Haiku catches hedged claims ("results may vary," "in some cases"). Python is the first pass, Haiku is the nuanced second pass.
**Why it might get revisited:** If Haiku's decisions turn out to be 99% aligned with Python's on real drafts, the subagent is redundant and adds latency to the blocking path.
**Deferred until:** 500 draft commits of real data. Measure agreement rate. If >99%, deprecate compliance-qa in favor of Python-only.

### 5.5 Schema version migration strategy at v1→v2

**Question:** When we bump any schema to 2.0, do we require every existing file to be migrated immediately, or do we support dual-read indefinitely?
**Current answer (from DATA_CONTRACTS section 10):** Dual-read for at least one minor version, then migration required.
**Why it might get revisited:** If dual-read complexity accumulates across multiple schemas changing at different rates.
**Deferred until:** First actual schema bump — real migration pain informs the policy better than speculation.

### 5.6 CLAUDE.md vs AGENTS.md primacy post-native-support

**Question:** When Claude Code ships native AGENTS.md reading (tracked in `anthropics/claude-code#34235` and `#6235`), do we remove CLAUDE.md entirely and treat AGENTS.md as the single source?
**Current answer:** Likely yes, but wait for the feature to actually ship and stabilize.
**Why it might get revisited:** Native support lands.
**Deferred until:** Feature ships + 30 days stable.

### 5.7 Plugin marketplace listing

**Question:** Does this repo ever get listed in a public Claude Code plugin marketplace (if/when one exists)?
**Current answer:** No for v1. Repo-as-plugin installed via direct path. Marketplace is a distribution layer, not an architectural layer.
**Why it might get revisited:** If the plugin sees external adoption beyond Tebra (unlikely but possible).
**Deferred until:** External adoption signal exists. Until then, a marketplace listing is solving a problem nobody has.

### 5.8 Multi-tenant isolation

**Question:** If this system is ever generalized to serve multiple customers (not just Tebra), how does tenant isolation work for sources, briefs, drafts, audit logs?
**Current answer:** Not applicable for v1. v1 is scoped to Tebra's stack.
**Why it might get revisited:** Only if v2 goes general-purpose.
**Deferred until:** A concrete second-customer conversation. Designing multi-tenancy on speculation is a common way to ship worse single-tenant software.

---

## 6. Vendor-specific caveats

Risks and dependencies that originate outside the system but constrain it.

### 6.1 SSE transport sunsets (2026)

| Vendor | Sunset date | Impact | Action |
|---|---|---|---|
| Atlassian (Jira, Confluence MCP) | June 30, 2026 | Not in v1 dependency list | Monitor, don't add SSE-only Atlassian integrations |
| Other MCP vendors on SSE | Rolling through 2026 | Any SSE-only vendor is a v1.1 migration target | `scripts/validate_mcp_config.py` warns on any SSE transport in `.mcp.json` |

No v1 servers currently require SSE per the Section 5.2 config in RUNBOOK. If a vendor forces SSE during Milestone 5, it gets logged here with a migration plan.

### 6.2 Anthropic API behavior shifts

| Event | Date | Impact | Mitigation |
|---|---|---|---|
| Cache TTL default change (1h → 5m) | March 2026 | 17–32% cost surprise on long-lived caches | Pinned `"ttl": "1h"` in every `cache_control`; keepalive thread optional |
| Opus 4.7 tokenizer density | April 2026 release | ~35% more tokens per English text vs Sonnet 4.6 | Documented in RUNBOOK Section 9.3; budget alert at 1.5× Sonnet baseline |
| Citations API rate limits | Ongoing | 429s on implementation-guide drafts at scale | Throttle product-truth subagent via prompt delay; request rate-limit increase |
| Future silent regressions | Unknown | Unknown | Monitor Anthropic status page, subscribe to changelog, include post-incident review in monthly ops (Section 11.1) |

### 6.3 Third-party MCP vendor risk

| Vendor | Risk | Mitigation |
|---|---|---|
| Profound | New company, pricing/auth could shift | Redundancy with Peec AI; adapter layer keeps swap cost low |
| Peec AI | Same | Same |
| Firecrawl | Established but small | Exa as fallback for some queries; monitor pricing |
| Exa | Established but small | Firecrawl overlap; monitor pricing |
| HubSpot | Enterprise-stable | Token rotation cadence (90d); monitor API deprecations in HubSpot's changelog |
| Webflow | Stable | Same |
| Google (Search Console, GA4, Drive) | Stable at the API level; MCP hosting status unclear | Self-hosted shim as fallback if official MCP unavailable |

### 6.4 Claude Code CLI feature maturity

Four features this system depends on that are still evolving:

- **MCP Tool Search.** Works today. Behavior could shift as the feature matures.
- **21 lifecycle hook events.** Works today. Subset is used (SessionStart, PreToolUse, PostToolUse, Stop). Additional events are optional expansion.
- **Agent Skills Standard auto-invocation.** Works today. Cross-tool portability claim depends on Cursor, Codex CLI, Gemini CLI honoring the same standard — monitor each.
- **`/plugin install` from local path.** Works today. Behavior when repo is a submodule vs a symlink is not fully documented.

If any of these shifts in ways that break this system, the fix gets logged here and migration is planned.

---

## 7. Deferred from v1

Explicitly cut from v1 scope. Each item has a reconsideration trigger — the condition under which it gets reconsidered for v1.1 or v2.

| Item | Why deferred | Reconsideration trigger |
|---|---|---|
| Real-time citation monitoring | Weekly is sufficient for steady-state operations; real-time adds infrastructure cost (polling, webhooks) for minimal incremental decision value | Citation landscape starts changing inside a weekly window often enough that decisions are delayed |
| Multi-language content | English-only simplifies every extractability rule, brand voice, and compliance check | Tebra expands to a non-English market |
| Video or interactive content | Scope beyond what the block library covers; needs different extractability rubric | A specific Tebra content type requires it |
| Scheduled automation (cron) | Local cron is fragile; GitHub Actions cron is the right answer but adds CI complexity | Operator-triggered `/citation-report` creates friction at scale |
| Plugin marketplace distribution | Repo-as-plugin is enough for Tebra scope | External adoption signal |
| Multi-tenant generalization | **Not pursued — decision 2026-04-21.** v1 is Tebra-specific by design and the operator has no interest in building a multi-customer SaaS from this codebase. | None. If a future direction changes this, it is a new system, not a generalization of this one. |
| compliance-qa subagent deprecation | Retained for nuanced claim detection | >99% agreement rate with Python-only over 500 commits |
| Dashboard for `audit/*.jsonl` | A service = out of scope for this repo | Compliance reviewer explicitly requests a dashboard and a team commits to maintaining it (built outside this repo, per 4.2 resolution) |
| Migration to AGENTS.md primary | Awaiting Claude Code native support | Feature ships |
| PowerShell hook duplicates | Double maintenance | A specific Tebra deployment requires Windows-native without WSL2 |
| Per-freelancer credential provisioning | Freelancers work without credentials | Workflow bottleneck surfaces |
| OAuth for Asana (v1.1 must-have, not optional) | v1 ships with PAT for proof-of-work; OAuth is required before any PHI-adjacent production use | Any Tebra production deployment — OAuth must ship first, not after |

---

## 8. Migration targets

Where the system is expected to evolve. Not a roadmap — a set of anticipated upgrades with the trigger conditions above in Section 7.

### 8.1 v1.x (minor iterations during Tebra usage)

- Add the compliance reviewer's actual delivery preference (Section 4.2) once known
- Swap Google MCP self-hosted shim for official endpoints if they ship
- Swap Profound/Peec AI placeholder env vars for real ones post-Milestone 5
- Refine the extractability rubric based on first 90 days of real citation data
- Benchmark and possibly consolidate Profound + Peec AI to one primary source after 60 days

### 8.2 v1.1 (targeted feature adds)

- **Asana OAuth — required before production deployment, not optional.** Ships as a v1.1 milestone gating any PHI-adjacent production use.
- GitHub Actions cron for scheduled `/citation-report` (lifts operator-triggered friction once real-world usage patterns justify it).
- Real-time citation monitoring (if weekly cadence becomes insufficient — 4.1 resolution sets a 10-day review window that will inform this).
- Public-facing compliance dashboard (if the reviewer requests one per 4.2 resolution — built outside this repo).
- Windows PowerShell hook variants (only if specifically required by a Tebra deployment).

### 8.3 v2 (architectural shifts)

- Multi-language content support
- Video/interactive content extractability
- Multi-tenant architecture (with the careful warning that designing this on speculation is wrong)
- Dashboard layer over audit logs
- Plugin marketplace distribution
- AGENTS.md-primary, CLAUDE.md-deprecated

---

## 9. How to contribute a new decision or question

For future-Jordan, or any future operator reading this.

### 9.1 Adding a decision

1. Identify the category: architectural (Section 2.1), technology (2.2), model routing (2.3), proof-of-work scope (2.4), documentation/style (2.5).
2. Add a row to the relevant table with today's date, the decision, the rationale, and status.
3. If the decision reverses or supersedes an earlier one, don't delete the old row. Add a new row marking the reversal and cross-reference the superseded row.
4. If the decision changes what's pinned (Section 3), update that table too.
5. Commit with a message like `decision: <short description>`.

### 9.2 Adding an open question

1. Decide whether it's blocking (Section 4) or non-blocking (Section 5). Blocking means v1 can't ship without an answer.
2. Write the status, owner, deadline, options/default, and recommendation.
3. If unresolved for more than 30 days, either resolve it or explicitly move it to deferred (Section 7) with a reconsideration trigger.
4. Commit with `question: <short description>`.

### 9.3 Closing a question

1. Don't delete the question. Add an "RESOLVED (date): <how>" annotation.
2. If the resolution is itself a decision, add it to Section 2 as well so the decision log is complete on its own.
3. If the resolution just eliminates the question (e.g., "vendor shipped official MCP, self-hosted shim removed"), note that and move on.

### 9.4 Retiring a deferred item

1. If a deferred item gets built in a later version, move it from Section 7 to the relevant Section 2 category as an active decision.
2. Cross-reference the deferral entry so the history reads cleanly.
3. If a deferred item becomes permanently irrelevant (e.g., multi-tenancy after confirming v2 will stay single-tenant), annotate and leave in place. Deleted context is lost context.

---

## 10. Parting note

This file's value compounds. A single entry might look like overhead the day it's written; six months later it's the reason a returning operator doesn't re-litigate a decision that was already made carefully.

The rule: if you made a non-trivial decision, log it here. If something is uncertain, log it here. If you looked up a vendor detail that took more than ten minutes, log it here. The alternative is rediscovering the same answers repeatedly — which is the default failure mode of any codebase with more than one maintainer and any amount of vendor exposure.

Cheap to add to. Expensive to let go stale. Keep it close.