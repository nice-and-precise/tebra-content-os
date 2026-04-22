# Kickoff Prompt — tebra-content-os

Paste this entire file into Claude Code after cloning and running environment setup
(see `docs/RUNBOOK.md` Section 3). Claude Code will read the entry-point files and
orient itself before waiting for your first instruction.

---

## Prompt to paste

```
You are operating in the tebra-content-os repository.

Read these files in order before doing anything else:
1. CLAUDE.md — behavioral rules for this repo
2. AGENTS.md — cross-tool-portable rule set
3. docs/PRD.md — problem, users, goals, and acceptance criteria (skim)

Then confirm:
- How many sources are in sources/registry.json
- Which skills are available in .claude/skills/
- Which subagents are available in .claude/agents/
- Which slash commands are available in .claude/commands/

Then wait for my first instruction.
```

---

## Day-one verification sequence

After pasting the prompt and confirming orientation, run the day-one demo:

```
/audit https://www.tebra.com/features
```

This scores the Tebra features page against the LLM extractability rubric and returns a
structured markdown report. Expected output: total score 0–5, dimension breakdown,
specific recommendations for improving extractability.

If `/audit` runs cleanly, the core system is working.

---

## Common starting points

**Write a new brief:**
```
/brief "tebra vs athenahealth for independent practices"
```

**Draft from an existing brief:**
```
/draft tebra-vs-athenahealth
```

**Weekly citation report:**
```
/citation-report
```

**Refresh stale content:**
```
/refresh https://www.tebra.com/blog/ehr-vs-emr
```

---

## If something breaks

Read `docs/RUNBOOK.md` Section 5 (Troubleshooting). The most common issues:
- MCP auth expired → re-authenticate per RUNBOOK Section 2
- Source expired → update `sources/registry.json` and run `python3 scripts/validate_sources.py`
- Compliance hook denying a valid claim → add the claim to `sources[].claims_cited[]` in the
  draft frontmatter with the matching source ID
