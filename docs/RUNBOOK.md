# RUNBOOK: tebra-content-os

**Status:** v1.0 · April 21, 2026
**Depends on:** `PRD.md`, `ARCHITECTURE.md`, `DATA_CONTRACTS.md`, `TASKS.md`
**Audience:** Operator installing the repo for the first time, or returning to run day-two ops. Written so a Claude Code user who has never touched this repo can go from `git clone` to a successful `/audit` in under 30 minutes.

---

## 1. What this runbook is, and isn't

This is the operator's manual. Every env var the system reads, every MCP server it connects to, every hook it fires, every known regression and how to work around it. If it's operational, it's in here. If it's conceptual, it's in `PRD.md`, `ARCHITECTURE.md`, or `DATA_CONTRACTS.md`.

This is **not** a tutorial for Claude Code itself. If you've never run `claude` before, start with Anthropic's Claude Code quickstart, then come back here. This runbook assumes you know what a slash command, a subagent, an MCP server, and a hook are.

This is also **not** a list of open questions. Open questions live in `RESEARCH_GAPS_AND_DECISIONS.md`. If a section below says "confirm with vendor," it means the vendor-facing detail (exact auth flow, exact env var spelling) should be verified against live docs before the first production credential is provisioned. The system's design does not depend on those details.

---

## 2. Prerequisites

| Tool | Version | Why |
|---|---|---|
| Claude Code CLI | 2.1.111 or later | Skill auto-invocation, MCP Tool Search, 21-event hook lifecycle — all April 2026 primitives |
| Python | 3.11 or later | Pydantic v2, modern `typing` features used in `scripts/schemas.py` |
| Node.js | 20 LTS or later | A handful of MCP servers ship as npm packages; required only for those |
| `uv` or `pip` | current | Python dep install |
| `git` | 2.40 or later | Hook integration with `git commit` |
| Bash-compatible shell | `bash` 5+, `zsh`, or WSL2 / Git Bash on Windows | Hooks in `.claude/hooks/` are `.sh` files |
| `jq` | 1.6 or later | Audit log inspection, not runtime-required but assumed in troubleshooting commands below |

**Windows-specific.** The hooks ship as `.sh`. Operate under WSL2 (recommended), Git Bash, or a POSIX-compatible shell environment. Native PowerShell is not supported — duplicating every hook into `.ps1` was considered and rejected (double maintenance, divergence risk). If a Windows-native path matters for a given Tebra deployment, raise it in `RESEARCH_GAPS_AND_DECISIONS.md`; it is a v1.1 consideration.

**Hardware expectations.** The repo builds and runs cleanly on any machine that meets Claude Code's own minimums. Three workloads are RAM-sensitive and worth naming: Chrome DevTools MCP (2–4 GB during active page rendering), the Claude Code CLI session with realistic context loaded (1–2 GB), and any Node-based MCP server spawned via `npx` (200–500 MB each). For development, the debug-and-test cycle, and the Section 3 proof-of-work demo, 8 GB system RAM is tight but workable if Slack and a few browser tabs are closed; 16 GB is comfortable. Apple Silicon (M1 and later) and modern x86-64 perform well; older Intel Macs run everything, but expect Chrome DevTools MCP renders to take 20–40 seconds per `/audit` instead of the 5–10 seconds on M-series hardware. If the operator machine is the bottleneck for a live demo, pre-record the `/audit` run on a better machine and present the recording alongside the repo.

**Network.** The system makes outbound HTTPS to Anthropic's API, every configured MCP server endpoint, and whatever local services the Chrome DevTools MCP inspects. No inbound ports. No webhook listener. Nothing binds a local port except Chrome DevTools MCP's own stdio bridge.

**Accounts needed.** An Anthropic API account with billing enabled. Accounts for each MCP server you plan to wire (full list in Section 4). For the initial `/audit` proof-of-work run, only Anthropic + Chrome DevTools are strictly required; everything else can be deferred.

---

## 3. Zero to first `/audit`: the 30-minute path

This is the minimum viable install. It exists to make the Milestone 3 proof-of-work demo reproducible by anyone cloning the repo. Everything beyond Section 3 is either expanded setup for more subagents, or day-two ops.

### 3.1 Clone and install

```bash
git clone https://github.com/nice-and-precise/tebra-content-os.git
cd tebra-content-os

# Python environment
python3.11 -m venv .venv
source .venv/bin/activate           # Windows WSL2: same; Git Bash: same
pip install -e ".[dev]"             # Installs deps from pyproject.toml

# Verify scaffolding
python3 -m ruff check .              # Passes
python3 -m pytest -x -q              # Passes (Milestone 1+ tests present)
```

### 3.2 Provide Anthropic credentials

```bash
cp .env.example .env
# Edit .env and set at minimum:
#   ANTHROPIC_API_KEY=sk-ant-...
```

Source the env file into your shell session before starting Claude Code:

```bash
set -a && source .env && set +a
```

The hooks and scripts read from the process environment, not from `.env` directly. This is deliberate — it keeps secrets out of any file the hook process might accidentally log or cache.

### 3.3 Start Claude Code in the repo

```bash
claude
```

On session start, the SessionStart hook (`session-start-load-context.sh`, built in Milestone 8) injects brand voice, source registry state, refresh backlog count, and compliance rule version into initial context. For a fresh clone with no briefs or sources yet, the hook output will show zero-state values. That is correct.

### 3.4 Run the first audit

At the Claude Code prompt:

```
/audit https://www.tebra.com/features
```

The `citation-auditor` subagent (Milestone 3) spawns with Sonnet 4.6, uses Chrome DevTools MCP to render and inspect the URL, scores it against the extractability rubric, writes a JSONL entry to `audit/citation-scores.jsonl`, and returns a markdown report in the chat.

Verify the audit landed:

```bash
tail -n 1 audit/citation-scores.jsonl | jq .
```

If that JSON prints with a five-dimension score and a `total` field, the zero-to-first-audit path is complete. This is the same demo used for the Tebra application proof-of-work.

### 3.5 What you haven't set up yet

Steps 3.1–3.4 give you `/audit`. They do not give you:

- `/brief` (needs Search Console, GA4, Firecrawl, Exa MCP — Section 4 and Milestone 4)
- `/draft` (needs the skills layer — Milestone 6)
- `/refresh` (needs Chrome DevTools + Firecrawl + Exa — Section 4 and Milestone 4)
- `/citation-report` (needs Profound, Peec AI, HubSpot, Slack MCP — Section 4 and Milestone 8)
- Compliance gating on actual drafts (needs source registry seeded — Milestone 7)

For each of those, continue through Sections 4–7 below.

---

## 4. Environment variables

Canonical list. Every variable the system reads at any point. `.env.example` ships with every name present and values blank. Nothing is read from process-only defaults; if a server needs an env var that isn't in this table, it's a bug.

| Variable | Required for | How to obtain | Notes |
|---|---|---|---|
| `FIRECRAWL_API_KEY` | Firecrawl MCP | firecrawl.dev → Dashboard → API Keys | Competitor SERP crawling; respect robots.txt in all configured endpoints. |
| `EXA_API_KEY` | Exa MCP | exa.ai → Dashboard → API Keys | LLM consensus answer retrieval. |
| `SEARCH_CONSOLE_MCP_URL` | Search Console MCP | URL of vendor-hosted or self-hosted GSC MCP endpoint | Set to the full `https://` URL the `search-console` server block in `.mcp.json` points to. |
| `SEARCH_CONSOLE_API_KEY` | Search Console MCP | API key or bearer token for the GSC MCP endpoint | Passed as `Authorization: Bearer` header. |
| `GA4_MCP_URL` | GA4 MCP | URL of vendor-hosted or self-hosted GA4 MCP endpoint | Same pattern as `SEARCH_CONSOLE_MCP_URL`. |
| `GA4_API_KEY` | GA4 MCP | API key or bearer token for the GA4 MCP endpoint | Passed as `Authorization: Bearer` header. |
| `ASANA_MCP_URL` | Asana MCP | URL of Asana MCP endpoint | Typically `https://mcp.asana.com/mcp`; verify against current Asana developer docs. |
| `ASANA_API_KEY` | Asana MCP | Asana → My Profile Settings → Apps → Manage Developer Apps → Personal Access Token | Personal Access Token is fine for v1; OAuth is a v1.1 enhancement. |
| `HUBSPOT_MCP_URL` | HubSpot MCP | URL of HubSpot MCP endpoint | Typically `https://mcp.hubspot.com/mcp`; verify against current HubSpot developer docs. |
| `HUBSPOT_API_KEY` | HubSpot MCP | HubSpot → Settings → Integrations → Private Apps → scopes for CRM, Content, Reporting | Private app token, not OAuth, for simplicity. Rotate every 90 days. |

**claude.ai connectors (no env vars required).** Slack, Google Drive, Webflow, and Chrome DevTools are provisioned as claude.ai native connectors and do not require env vars or `.mcp.json` entries. Credentials are managed in the claude.ai connector settings UI.

**v1.1 planned vars (not active).** `PROFOUND_API_KEY` (share-of-citation tracking) and `PEEC_AI_API_KEY` (secondary citation tracking) are commented out in `.env.example` pending vendor endpoint confirmation. Do not set them until the MCP blocks are added to `.mcp.json`.

**Secrets handling.** Never commit `.env`. The `.gitignore` already excludes it. Never paste secrets into `.mcp.json` — that file is git-tracked and reads env vars by name. Never log secrets from hooks; the `post-commit-changelog.sh` hook explicitly redacts any stringified env var value before writing to `audit/publish.jsonl`.

**Rotation cadence.** 90 days for HubSpot, Slack, Webflow, Asana, and the Google service account JSON. Anthropic API keys rotate on suspected exposure, not on a schedule. Firecrawl, Exa, Profound, Peec AI: follow the vendor's recommendation (typically 90 days). A rotation-reminder entry for each is a v1.1 idea tracked in `RESEARCH_GAPS_AND_DECISIONS.md`.

---

## 5. MCP server configuration

The full `.mcp.json` is built in Milestone 5. This section documents the shape, the transport decisions, and the per-server authentication notes.

### 5.1 Transport policy

Every MCP server uses **Streamable HTTP transport** where the vendor supports it, per MCP spec 2025-11-25. SSE is accepted only where no HTTP endpoint exists. Any SSE dependency is a v1.1 migration target and is flagged in `RESEARCH_GAPS_AND_DECISIONS.md`.

Why this matters: the MCP spec deprecated SSE in 2025-11-25. Atlassian's sunset is June 30, 2026. Other vendors are on similar timelines. The system is built to outlive SSE without rewiring.

### 5.2 Canonical `.mcp.json` shape

```json
{
  "mcpServers": {
    "firecrawl": {
      "command": "npx",
      "args": ["-y", "firecrawl-mcp"],
      "env": {
        "FIRECRAWL_API_KEY": "${FIRECRAWL_API_KEY}"
      }
    },
    "exa": {
      "command": "npx",
      "args": ["-y", "exa-mcp-server"],
      "env": {
        "EXA_API_KEY": "${EXA_API_KEY}"
      }
    },
    "search-console": {
      "type": "http",
      "url": "${SEARCH_CONSOLE_MCP_URL}",
      "headers": {
        "Authorization": "Bearer ${SEARCH_CONSOLE_API_KEY}"
      }
    },
    "ga4": {
      "type": "http",
      "url": "${GA4_MCP_URL}",
      "headers": {
        "Authorization": "Bearer ${GA4_API_KEY}"
      }
    },
    "asana": {
      "type": "http",
      "url": "${ASANA_MCP_URL}",
      "headers": {
        "Authorization": "Bearer ${ASANA_API_KEY}"
      }
    },
    "hubspot": {
      "type": "http",
      "url": "${HUBSPOT_MCP_URL}",
      "headers": {
        "Authorization": "Bearer ${HUBSPOT_API_KEY}"
      }
    }
  }
}
```

Six servers total: two stdio (firecrawl, exa via npx) and four HTTP (search-console, ga4, asana, hubspot). Slack, Google Drive, Webflow, and Chrome DevTools are claude.ai native connectors and do not appear in `.mcp.json`. Run `scripts/validate_mcp_config.py` after any change to verify env var coverage.

### 5.3 Verifying MCP servers are alive

Inside Claude Code:

```
/mcp
```

The output lists every configured server, its transport, its connection status, and the number of tools it exposes. If a server shows as "failed" or "unauthorized," check the env var spelling against Section 4, confirm the token hasn't expired, and re-source `.env`.

Outside Claude Code:

```bash
python scripts/validate_mcp_config.py
```

Parses `.mcp.json`, confirms every referenced env var is set in the current environment (without reading its value), warns on any SSE transport, and flags URLs that return a non-2xx status on a lightweight HEAD probe.

### 5.4 Tool Search

MCP Tool Search is enabled via `CLAUDE_CODE_ENABLE_TOOL_SEARCH=true`. With 6 configured servers and dozens of tools total, loading every tool into every subagent's context would burn budget on tools the subagent never calls. Tool Search defers that — subagents search for tools by keyword and load only what matches.

To verify Tool Search is active:

```
/mcp
```

Look for the `deferred` flag on tools. If no tools are deferred, the env var didn't apply. Check the Claude Code settings loader: `claude doctor` reports which config layers are active.

---

## 6. `.claude/settings.json` configuration

The project-level settings file controls cache behavior, Tool Search, permission rules, model routing, and hook registration. Below are the non-obvious fields.

### 6.1 Cache TTL pinning (non-negotiable)

```json
{
  "cacheControl": {
    "defaultTtl": "1h",
    "blocks": {
      "brand-voice": { "ttl": "1h" },
      "source-registry": { "ttl": "1h" },
      "compliance-rules": { "ttl": "1h" }
    }
  }
}
```

**Why this is non-negotiable.** In March 2026, the Anthropic API silently switched the default `cache_control` TTL from 1 hour to 5 minutes. Developers on long-lived cached prompts paid 17–32% more for identical workloads until they noticed. The fix is to pin the TTL explicitly in every `cache_control` block the system emits. This setting does that at the config layer; the SessionStart hook also pins `"ttl": "1h"` inline when it writes brand voice and source registry to context.

The keepalive thread in `scripts/cache_keepalive.py` (optional, enabled via `CACHE_KEEPALIVE=true`) pings the cached brand-voice block every 50 minutes to keep it warm across idle operator periods. Not required for v1; a cost optimization.

### 6.2 Permission rules

```json
{
  "permissions": {
    "tools": {
      "Read": "allow",
      "Write": "allow",
      "Edit": "allow",
      "Bash": "ask",
      "mcp__*": "allow"
    },
    "bashAllowlist": [
      "git status",
      "git diff",
      "git log",
      "ruff check",
      "pytest",
      "npm run *",
      "python scripts/*"
    ],
    "bashDenylist": [
      "rm -rf *",
      "sudo *",
      "curl * | sh",
      "wget * | sh"
    ]
  }
}
```

Bash defaults to `ask` because a content-ops agent doesn't need to run arbitrary commands. The allowlist covers the commands the subagents legitimately need. The denylist is defense in depth — it exists even though `ask` already gates everything, because a tired operator clicking "allow" on the wrong thing is a failure mode worth a second layer.

### 6.3 Model routing

```json
{
  "models": {
    "default": "claude-opus-4-7",
    "subagents": {
      "brief-author": "claude-sonnet-4-6",
      "draft-writer": "claude-opus-4-7",
      "citation-auditor": "claude-sonnet-4-6",
      "refresh-auditor": "claude-sonnet-4-6",
      "compliance-qa": "claude-haiku-4-5-20251001",
      "product-truth": "claude-opus-4-7",
      "citation-reporter": "claude-sonnet-4-6"
    }
  }
}
```

The routing follows `ARCHITECTURE.md` section 9. The full dated string for Haiku is used because Haiku 4.5 currently pins to a specific release; Sonnet and Opus use aliases because their alias behavior has been stable across the 4.x line.

**Opus 4.7 tokenizer note.** Opus 4.7 tokenizes roughly 35% more tokens than Sonnet 4.6 for the same English text. Before pushing a draft-writer run at scale, benchmark per-brief cost on five representative briefs and set a monthly budget alert in the Anthropic console. This is not a regression, it's a deliberate tokenization change tied to Opus's training — flagged here because the cost surprise is predictable.

### 6.4 Hook registration

```json
{
  "hooks": {
    "SessionStart": [".claude/hooks/session-start-load-context.sh"],
    "PreToolUse": [".claude/hooks/pre-tool-use-compliance.sh"],
    "PostToolUse": [".claude/hooks/post-commit-changelog.sh"],
    "Stop": [".claude/hooks/stop-run-linters.sh"]
  }
}
```

Hook paths are relative to repo root. Every hook must be executable (`chmod +x .claude/hooks/*.sh`). On Windows under WSL2, mode bits persist; under Git Bash, verify with `ls -la .claude/hooks/` before the first session.

---

## 7. Hook verification

Hooks fail silently by default — Claude Code does not surface hook errors prominently, which is exactly what you want in production and exactly what bites you during first setup. Three verification paths:

### 7.1 Is the hook registered?

```
/hooks
```

Inside Claude Code. Lists every registered hook by lifecycle event and file path. If your hook isn't there, it isn't registered; revisit `.claude/settings.json`.

### 7.2 Is the hook firing?

```bash
# In another terminal, tail the relevant audit log
tail -f audit/compliance.jsonl    # PreToolUse
tail -f audit/publish.jsonl       # PostToolUse
```

Trigger the hook (for example, write a draft and commit it), and watch the log. No line appended = hook didn't fire or errored. Check:

```bash
# Run the hook manually with a canned input to test in isolation
echo '{"tool_input": {"file_path": "drafts/test.md", "content": "Lorem ipsum"}}' \
  | .claude/hooks/pre-tool-use-compliance.sh
```

Expected output: a JSON object with `hookSpecificOutput.permissionDecision` set to `allow`, `ask`, or `deny`. If the script errors, the stderr output tells you why (most commonly: Python import failure, missing `scripts/compliance_check.py`, or a permissions issue on the hook file).

### 7.3 Does the hook decide correctly?

The `tests/test_compliance_check.py` suite covers allow / ask / deny paths with known-good and known-bad fixtures. Run after any compliance rule change:

```bash
python3 -m pytest tests/test_compliance_check.py -v
```

For a live-in-session verification, try to commit a draft containing an unsourced medical claim. The commit should fail with the deny reason written to `audit/compliance.jsonl`. If it succeeds, the hook isn't wired correctly.

---

## 8. Audit logs

Three append-only JSONL files under `audit/`. Never edited. Rotation by month when any file exceeds 100 MB (rotation is manual for v1; GitHub Actions cron is a v1.1 target).

### 8.1 Reviewing compliance decisions

```bash
# Last 10 deny decisions
jq 'select(.decision == "deny")' audit/compliance.jsonl | tail -n 10

# Count decisions by type for the current month
jq -r '.decision' audit/compliance.jsonl | sort | uniq -c
```

Healthcare compliance review consumes this file. The current expectation is a weekly export to the compliance reviewer; the delivery channel (Slack DM, email digest, dashboard) is still open — tracked in `RESEARCH_GAPS_AND_DECISIONS.md`.

### 8.2 Reviewing publish velocity

```bash
# Count publish events this month
jq 'select(.timestamp >= "2026-04-01")' audit/publish.jsonl | jq -s length
```

Feeds the refresh-velocity KPI. A month showing fewer than 40 publish events in steady state is a signal to investigate — either the pipeline is blocked somewhere upstream, or Tebra's content demand has shifted.

### 8.3 Reviewing citation scores

```bash
# Average extractability score across the library
jq -s 'map(.metadata.total) | add / length' audit/citation-scores.jsonl

# URLs scoring below 3.5 (refresh candidates)
jq 'select(.metadata.total < 3.5) | .metadata.url' audit/citation-scores.jsonl
```

### 8.4 Log rotation

```bash
# Manual monthly rotation
cd audit
for f in compliance.jsonl publish.jsonl citation-scores.jsonl; do
  if [ $(stat -f%z "$f" 2>/dev/null || stat -c%s "$f") -gt 104857600 ]; then
    mv "$f" "${f%.jsonl}-$(date +%Y-%m).jsonl"
    touch "$f"
  fi
done
```

Rotated files are committed to git. This is deliberate — the audit trail is the compliance defense, and git is the durable store. If size becomes a problem, v1.1 moves rotated logs to an external object store via a scheduled job.

---

## 9. Known gotchas

Explicit enumeration of things that have already bitten people or will bite people soon, with workarounds.

### 9.1 Cache TTL regression (March 2026)

**Symptom.** Cached prompts that used to cost $X now cost $X × 1.17 to $X × 1.32 for the same workload. No error, no warning, no changelog entry from Anthropic at the time of the change.

**Cause.** The API's default `cache_control` TTL flipped from 1 hour to 5 minutes. Short-lived caches invalidate more often, each invalidation rewrites the cache, and write amplification hits the bill.

**Fix.** Pin `"ttl": "1h"` explicitly in every `cache_control` block the system emits. Section 6.1 above sets this at the config layer. The SessionStart hook and the subagent prompt builders also inline the pin.

**Verification.** `jq 'select(.metadata.cache_ttl != "1h")' audit/compliance.jsonl` should return zero results after a week of operation.

### 9.2 SSE transport sunset

**Timeline.** MCP spec 2025-11-25 deprecated SSE. Atlassian's SSE endpoints sunset June 30, 2026. Other vendors following through 2026.

**Impact on this system.** All 6 servers are configured in Section 5.2 (firecrawl and exa use stdio; search-console, ga4, asana, and hubspot use Streamable HTTP). If a vendor's HTTP endpoint isn't available at install time and SSE is the only option, the `scripts/validate_mcp_config.py` helper warns and logs the server as a v1.1 migration target in `RESEARCH_GAPS_AND_DECISIONS.md`.

### 9.3 Opus 4.7 tokenizer cost surprise

**Symptom.** First Opus 4.7 bill arrives roughly 35% higher than the pre-flight estimate based on Sonnet 4.6 token counts.

**Cause.** Opus 4.7 tokenizes English text more densely; identical prose consumes more tokens. This is a deliberate training-side decision, not a bug.

**Fix.** Benchmark the draft-writer subagent on five representative briefs before the first production run. Set a monthly budget alert in the Anthropic console at 1.5× the Sonnet-estimated baseline. Revisit after the first 30 days of real use.

### 9.4 CLAUDE.md instruction budget

**Symptom.** After adding the twentieth rule to CLAUDE.md, the agent starts ignoring older rules. Adding more rules makes it worse.

**Cause.** April 2026 research confirms models reliably follow roughly 150 instructions in a system-level prompt. Past that, *all* rules degrade, not just the new ones.

**Fix.** CLAUDE.md is reserved for agent-behavior rules only. Code style (line length, quote style, import order) lives in ruff and prettier, invoked by the Stop hook. Workflow specifics live in skills. Data contracts live in `DATA_CONTRACTS.md`. CLAUDE.md is the last place to add a rule, not the first.

### 9.5 Hook files executable bit

**Symptom.** Hook doesn't fire. `/hooks` shows it registered. No errors anywhere.

**Cause.** `chmod +x` wasn't run after clone. Happens especially on fresh Windows WSL2 environments, or after a repo is extracted from a zip.

**Fix.**

```bash
chmod +x .claude/hooks/*.sh
```

Add a sanity check in `scripts/validate_repo.py` that asserts mode bits on every hook file; CI runs it.

### 9.6 AGENTS.md vs CLAUDE.md precedence

**Symptom.** Rules written in AGENTS.md (expecting cross-tool compatibility with Cursor, Codex CLI, Gemini CLI) aren't applied in Claude Code sessions.

**Cause.** Claude Code as of April 2026 reads `CLAUDE.md` natively but does not yet read `AGENTS.md` natively. The Linux Foundation standard is real; Claude Code native support is tracked in issues `anthropics/claude-code#34235` and `#6235`.

**Fix for now.** The build pattern is: author rules in one place, then `@import` into CLAUDE.md so Claude Code picks them up while the other tools read AGENTS.md directly. When Claude Code ships native AGENTS.md support, the `@import` becomes redundant and gets removed — tracked in `RESEARCH_GAPS_AND_DECISIONS.md`.

### 9.7 Chrome DevTools MCP and headless browsers

**Symptom.** `/audit` returns a score but the extracted schema shows empty. The page under audit is single-page-app heavy.

**Cause.** Chrome DevTools MCP renders the page via an actual Chrome instance. If the page's schema markup is injected only after a hydration event the MCP isn't waiting for, the extracted data is incomplete.

**Fix.** In the citation-auditor subagent prompt, instruct it to wait for `networkidle` before extracting. If the issue persists, bump the wait timeout. Document the specific URL and the wait threshold in `audit/notes/<url-slug>.md` for future runs.

### 9.8 Anthropic API rate limits under Citations API load

**Symptom.** Product-truth subagent errors with 429 during an implementation-guide draft.

**Cause.** Citations API grounds every procedural step against source documents, which means multiple retrieval calls per draft. At scale this can hit Anthropic's per-minute rate limit for the key.

**Fix.** Two levers: (1) request a rate-limit increase from Anthropic for the production key; (2) throttle the product-truth subagent via an explicit delay between Citations API calls in its prompt. The second is cheaper to implement and sufficient for v1 volumes.

---

## 10. Freelancer installation

Freelancers get parity with the internal team via the Claude Code plugin system. This is what the Milestone 12 packaging targets.

### 10.1 First-time install for a freelancer

```bash
# On the freelancer's machine
claude
# Then inside Claude Code:
/plugin install /path/to/tebra-content-os
```

The plugin install bundles the skills, the block library, the compliance rules, and the brand voice. Freelancer machines do not need:

- The full `.env` with every env var (freelancers don't publish to Webflow or post to Slack directly; those integrations are internal-team only).
- The source registry (freelancers reference sources by ID in drafts; the internal team's compliance hook validates on commit).
- The MCP server credentials the internal team uses (freelancer MCP setup covers Chrome DevTools for local verification and Anthropic for the LLM calls).

What freelancers do get:

- Auto-invocation of `tebra-brand-voice` on every content task.
- Access to the seven block-library templates via `citation-block-library` skill.
- Local draft verification via `scripts/compliance_check.py` before push.
- The same slash commands (`/audit`, `/draft`, `/refresh`) their tooling already understands.

### 10.2 Plugin version pinning

Version is declared in `.claude-plugin/plugin.json` under the `version` field. The current release is `1.0.0`. Claude Code reads this at install time and surfaces it in `/plugins`.

npm-based stdio servers (`firecrawl-mcp`, `exa-mcp-server`) are pinned to specific versions in `.mcp.json` using the `@<version>` suffix in the npx args. Update the pins here when upgrading, then run `scripts/package_plugin.sh` to build a new archive.

Freelancers who need to update: reinstall from the new archive via `/plugin install <path>`.

### 10.3 Freelancer onboarding doc

The ten-minute freelancer quickstart is `docs/FREELANCER_ONBOARDING.md`.

---

## 11. Day-two operations

Things to do monthly, quarterly, and on events.

### 11.1 Monthly

- Rotate any token approaching its 90-day mark (Section 4 table).
- Run `python scripts/validate_sources.py` and address any `expires_at` warnings.
- Review `audit/compliance.jsonl` deny rate; if above 10% of total decisions, the draft-writer prompt needs tightening, not the hook.
- Review `audit/publish.jsonl` velocity against the 40-asset target.
- Check the Anthropic monthly bill against the benchmark; investigate any month above 1.25× baseline.

### 11.2 Quarterly

- Review `RESEARCH_GAPS_AND_DECISIONS.md` for deferred items that should now ship in v1.x.
- Reconfirm every MCP vendor's transport status. Any that moved from HTTP to a new auth flow need their block in Section 5.2 updated.
- Run a full end-to-end dry run (Milestone 10) to confirm no regression from recent changes.
- Refresh the extractability rubric against current LLM citation patterns; Profound and Peec AI signal where patterns are shifting.
- Audit `CLAUDE.md` line count against the 150-instruction ceiling (Section 9.4). Move any rule that belongs in ruff, prettier, or a skill out of CLAUDE.md.

### 11.3 On specific events

- **Vendor auth change (new OAuth flow, new token format):** update the server block in Section 5.2, run `scripts/validate_mcp_config.py`, commit the change with a note in `RESEARCH_GAPS_AND_DECISIONS.md`.
- **Suspected credential exposure:** rotate immediately, grep `audit/*.jsonl` for any activity during the exposure window, file an incident note in `docs/incidents/<date>.md`.
- **Schema change in `DATA_CONTRACTS.md`:** bump `schema_version`, write the migration script in `scripts/migrations/`, run against every existing `briefs/*.json` and `drafts/*.md`, log the change in `RESEARCH_GAPS_AND_DECISIONS.md`.
- **Anthropic model release (new Opus, new Sonnet, new Haiku):** benchmark the draft-writer and citation-auditor on five representative briefs each BEFORE updating `.claude/settings.json` model routing. Cost surprises live on the other side of unbenchmarked upgrades.
- **MCP vendor deprecation announcement:** move the affected server to the v1.1 migration list, schedule the swap before the sunset date, not after.

---

## 12. Troubleshooting

The failure modes that show up in practice. If your problem isn't listed here, grep `audit/*.jsonl` first — most issues leave a trail.

### 12.1 "My hook isn't firing"

In order:

1. `/hooks` inside Claude Code — is it registered?
2. `ls -la .claude/hooks/` — is the executable mode bit set? (Section 9.5)
3. Run the hook manually with canned input (Section 7.2). Does it error?
4. Check `.claude/settings.json` — is the lifecycle event spelled correctly? (`PreToolUse`, not `preToolUse` or `pre-tool-use`.)

### 12.2 "MCP server won't connect"

1. `python scripts/validate_mcp_config.py` — does it flag the server?
2. Is the env var set in the shell that launched Claude Code? `echo $HUBSPOT_ACCESS_TOKEN` (redact before sharing).
3. Has the token expired? Check the vendor dashboard.
4. Is the vendor's endpoint up? A simple `curl -I <endpoint>` tells you.
5. For Chrome DevTools MCP specifically: is Chrome or Chromium actually installed? The MCP expects a local binary.

### 12.3 "Tool Search loaded the wrong tools"

1. `/mcp` — does it show `deferred` on tools? If not, Tool Search isn't active (Section 5.4).
2. Is the subagent's description specific enough? A brief-author with `description: "writes content"` will match too broadly.
3. Do the subagent's allowed-tools patterns in its frontmatter cover what the task needs?

### 12.4 "/audit hangs or times out"

1. Is the URL actually reachable? `curl -I <url>`.
2. Is the page JavaScript-heavy? The citation-auditor waits for `networkidle`; sites with long-running analytics or chat widgets can delay this indefinitely. Bump the wait threshold in the subagent prompt, or add a hard timeout.
3. Is Chrome DevTools MCP already running from a previous session and locked? `pkill -f chrome-devtools` and retry.

### 12.5 "Compliance hook blocks a legitimate claim"

This is the hook doing its job, but here's how to make it do its job more precisely:

1. Check `audit/compliance.jsonl` — what was the deny reason?
2. If "no source_id referenced": add the source to the draft frontmatter. Correct answer. Don't bypass.
3. If "source_id not approved for claim type": either update `Source.approved_for_claims` for that source (if the approval is legitimate and just wasn't recorded), or cite a different source that is approved for this claim type.
4. If the hook keeps denying what you believe are false positives: the claim detector (`scripts/compliance_check.py`) may need tuning. Don't weaken it in isolation — add a test fixture for the false-positive case in `tests/test_compliance_check.py` first, then tune to make both that test and existing tests pass.

Never disable the hook. The compliance posture is the one piece of this system that is genuinely non-negotiable. The whole "no AI slop" signal to Tebra collapses the minute the hook becomes optional.

**Known limitation — multi-pattern overlap:** A phrase like "reduces mortality by 50%" triggers two separate regex patterns: the percentage-outcome pattern AND the bare `mortality` keyword. Each match must be independently cited. Authors who cite the full phrase will still receive a denial for the bare keyword unless they also add a separate `claim: "mortality"` citation entry (semantically awkward). A future fix will treat a detected claim as sourced by transitivity if it is fully contained within an already-sourced longer match. Until then: if the hook denies with `unsourced: 'mortality'` for content that does cite a mortality-percentage claim, add a second citation entry with `claim: "mortality"` pointing to the same source.


### 12.6 "Draft-writer generates the same intro for every brief"

1. Is `tebra-brand-voice` over-prescriptive on opening patterns? A skill that says "every page opens with <specific sentence structure>" produces exactly that failure mode.
2. Is the brief's `target_intent.query_cluster` diverse enough? Same intent cluster → similar drafts is expected; the fix is upstream in brief-author.
3. Is Opus 4.7's temperature pinned too low? Content generation benefits from temperature 0.7–1.0; lower than that produces same-y output.

### 12.7 "Cache cost is higher than expected"

1. Section 9.1 — are all `cache_control` blocks pinned to `"ttl": "1h"`?
2. Is the cache keepalive running? `ps aux | grep cache_keepalive`.
3. Is the cached content actually stable? A brand-voice block that changes on every session isn't cacheable; cache it once per brand-voice version, not once per session.

### 12.8 "Opus 4.7 bill is 35% higher than the Sonnet baseline"

Not a bug. Section 9.3. Benchmark before, budget alert after, revisit after 30 days.

---

## 13. When in doubt

This runbook is exhaustive by design. In practice, most issues land in Section 12 and resolve in under 10 minutes. The rest are genuinely novel, and the right response is:

1. Capture the symptom and context in `audit/incidents/<date>-<slug>.md`.
2. Reproduce it in a minimal test case if possible.
3. Add an entry to `RESEARCH_GAPS_AND_DECISIONS.md` with the symptom, current workaround, and decision criteria for a permanent fix.
4. Don't paper over the problem with a local workaround that lives only in your head. Every uncommitted workaround is an institutional liability.

The runbook, the spec docs, the decision log, and the audit logs together are the system's memory. Anything the operator learns that isn't in one of those files is something the next operator will have to learn again.