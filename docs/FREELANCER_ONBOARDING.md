# Freelancer Onboarding — tebra-content-os

**Time to first draft: ~10 minutes**
**Requires:** Claude Code CLI 2.1.111+, Python 3.11+, Node 18+

---

## What you get

Once installed, every Claude Code session automatically loads:

- **Tebra brand voice** — direct, evidence-forward, written for independent practice operators
- **Seven content skills** — comparison pages, case studies, ROI calculators, implementation guides, citation blocks, compliance rules
- **Five slash commands** — `/brief`, `/draft`, `/audit`, `/refresh`, `/citation-report`
- **Compliance gate** — blocks unsourced medical claims before any file is written

You do **not** need: Webflow credentials, Slack access, HubSpot tokens, or the source registry. Those are internal-team integrations. Your role is brief-to-draft.

---

## Step 1: Install the plugin

```bash
# Option A — install directly from the repo path (if you have it locally)
# Inside Claude Code:
/plugin install /path/to/tebra-content-os

# Option B — unpack the archive the internal team sent you
mkdir -p ~/tebra-content-os
tar -xzf tebra-content-os-1.0.0.tar.gz -C ~/tebra-content-os
# Inside Claude Code:
/plugin install ~/tebra-content-os
```

Verify installation:
```
/plugins
```
Expected: `tebra-content-os 1.0.0` appears in the list.

---

## Step 1b: Enable Chrome DevTools connector (for /audit)

`/audit` uses the Chrome DevTools MCP, which is provided by the `chrome-devtools-mcp` claude.ai native connector — not configured in `.mcp.json`.

Enable it in claude.ai → Settings → Connectors → Chrome DevTools. Once enabled, it auto-loads in Claude Code sessions and the `citation-auditor` subagent can use it for page rendering.

If you only plan to use `/draft` and not `/audit`, you can skip this step.

---

## Step 2: Set environment variables

Create `~/tebra-content-os/.env` (this file is gitignored — never commit it):

```bash
# Required for all LLM calls
ANTHROPIC_API_KEY=sk-ant-...

# Required for competitor research (the internal team may pre-fill these)
FIRECRAWL_API_KEY=fc-...
EXA_API_KEY=...
```

Source it before starting Claude Code:
```bash
source ~/tebra-content-os/.env
```

Or add to your shell profile. Claude Code inherits the shell environment.

---

## Step 3: Verify the plugin loaded

Open Claude Code in the `tebra-content-os` directory. The SessionStart hook should print:

```
[tebra-content-os session context]
  brand-voice:      <git hash>
  sources:          N registered, 0 expiring within 30 days
  refresh backlog:  0 draft(s) not yet published
  compliance rules: <git hash>
```

If the session context block does not appear, check that hook files are executable:
```bash
chmod +x ~/tebra-content-os/.claude/hooks/*.sh
```

---

## Step 4: Run your first audit

Test that Firecrawl and the citation-auditor are working:

```
/audit https://www.tebra.com/features
```

Expected: a markdown table with 5 extractability dimensions scored 0–1 each. If it errors, confirm `FIRECRAWL_API_KEY` is set.

---

## Step 5: Draft from a brief

The internal team writes briefs; you turn them into drafts.

```bash
# Confirm the brief exists and passes validation
python3 -m scripts.validate_briefs

# Write the draft
/draft <slug>
```

Replace `<slug>` with the brief's filename without `.json` (e.g., `/draft tebra-vs-athenahealth`).

The `draft-writer` subagent will:
1. Read `briefs/<slug>.json`
2. Load brand voice and the relevant asset-type skill
3. Write `drafts/<slug>.md` with YAML frontmatter
4. Compliance gate fires automatically — if it blocks, surface the flagged claim to the internal team

---

## Compliance rules you must follow

- **Never invent statistics.** Every number in a draft must come from the brief's `proof_points[]` array.
- **No unsourced medical claims.** "Reduces mortality", "improves outcomes", "clinically proven" — any of these require a source in the brief. If one isn't there, note it as a gap rather than writing around it.
- **If the compliance gate blocks 3 times in a row**, stop and email the internal team with the flagged claim rather than trying to rephrase indefinitely.

---

## Slash command reference

| Command | What it does |
|---|---|
| `/brief <query>` | Research a query and create a content brief (requires Search Console + GA4 auth — internal team only) |
| `/draft <slug>` | Write a draft from an approved brief |
| `/audit <url>` | Score a URL for LLM extractability (0–5 scale) |
| `/refresh <url>` | Check if a published page is stale and needs updating |
| `/citation-report` | Generate weekly citation-performance report (internal team only) |

As a freelancer you will primarily use `/draft` and `/audit`.

---

## Getting help

- Compliance gate blocked unexpectedly → check `audit/compliance.jsonl` for the deny reason
- Draft validation fails → run `python3 -m scripts.validate_drafts` and read the error
- Plugin not loading → run `chmod +x .claude/hooks/*.sh` and restart Claude Code
- Anything else → contact the internal team; do not modify `sources/registry.json` or `.claude/settings.json`
