# TASKS: tebra-content-os

**Status:** Draft v0.1 · April 21, 2026 **Depends on:** PRD.md,
ARCHITECTURE.md, DATA_CONTRACTS.md **Audience:** Claude Code build
sessions. Read this sequentially. Do not skip milestones.

## How to read this file

Each milestone has four fields:

- **Goal:** what\'s true when the milestone is done.

- **Verification:** the specific, runnable test that proves the goal.

- **Stop point:** commit, run the verification, report back, wait for
  sign-off before starting the next milestone.

- **Scope discipline:** what NOT to build in this milestone, even if
  tempted.

Stop points exist because long-horizon agent runs drift. The AMIE build
proved the pattern works: sequential milestones with explicit halts
produce cleaner output than one-shot builds. Trust the pattern.

Estimated effort per milestone is intentionally omitted. Quality over
speed.

Order matters. Milestone N depends on N-1. Do not parallelize unless a
milestone explicitly says \"can run in parallel with N+1.\"

## Milestone 0: Repository bootstrap

**Goal:** Empty repository has correct directory structure, license,
gitignore, Python tooling, and CI scaffold. No Claude Code configuration
yet.

**Build:**

- Initialize git repo at project root.

- Create all directories per ARCHITECTURE.md section 3 (.claude/agents,
  .claude/skills, .claude/commands, .claude/hooks, briefs, drafts,
  blocks, sources, audit, scripts, tests, docs, .github/workflows).

- Add .gitkeep to every empty directory so git tracks them.

- Write pyproject.toml with: Python 3.11+, deps (httpx, pydantic,
  PyYAML, anthropic), dev deps (ruff, pytest, pytest-asyncio).

- Write .gitignore covering: \_\_pycache\_\_, .venv, .env, \*.pyc,
  .DS_Store, secrets patterns, compiled artifacts.

- Write LICENSE (MIT or Apache 2.0; defer to operator preference;
  default MIT if not specified).

- Write .github/workflows/ci.yml with three jobs: ruff check, pytest,
  and schema-validate (stubbed --- implementation comes in Milestone 5).

- Write a minimal README.md with repo name, one-sentence description,
  and \"See docs/ for full specification.\" Expand in Milestone 9.

**Verification:**

ls -la \# All directories present

ruff check . \# Passes (no Python files yet, should no-op cleanly)

pytest \# Passes (no tests yet, should no-op cleanly)

git status \# Clean

**Stop point:** Commit as chore: milestone 0 bootstrap. Report
completion. Wait.

**Scope discipline:** Do not write any CLAUDE.md, AGENTS.md, hooks,
skills, agents, or .mcp.json content yet. Just the shell.

## Milestone 1: Pydantic schemas for all data contracts

**Goal:** Every schema in DATA_CONTRACTS.md has a corresponding Pydantic
v2 model in scripts/schemas.py, with unit tests that roundtrip example
fixtures.

**Build:**

- scripts/schemas.py containing Pydantic models for: Brief, Draft
  (frontmatter portion), Source, CitationRecord, AuditEvent,
  SubagentResponse.

- All enums from DATA_CONTRACTS.md as Literal types or Enum classes:
  AssetType, BuyerStage, SourceType, AuthorityTier, ClaimType,
  DraftStatus, AuthorType, EventType, SubagentStatus.

- All validation rules from DATA_CONTRACTS.md implemented as Pydantic
  validators (e.g., \"every proof_points\[\].source_id MUST resolve to
  an entry in sources\[\]\").

- tests/test_schemas.py with: one valid-example fixture per schema, one
  deliberately-invalid fixture per schema per validation rule.

- scripts/migrations/ directory with \_\_init\_\_.py and a placeholder
  README.md explaining the migration convention.

**Verification:**

pytest tests/test_schemas.py -v \# All pass

ruff check scripts/ tests/ \# Passes

python -c \"from scripts.schemas import Brief;
print(Brief.model_json_schema())\" \# Prints JSON schema

**Stop point:** Commit as feat(schemas): pydantic models for all data
contracts. Report coverage (number of models, number of validation rules
tested). Wait.

**Scope discipline:** Do not write any actual briefs, drafts, or sources
yet. Only the validation layer.

## Milestone 2: The compliance hook (the non-negotiable quality gate)

**Goal:** A working PreToolUse hook at
.claude/hooks/pre-tool-use-compliance.sh that blocks commits to /drafts/
containing unsourced medical claims, logs decisions to
/audit/compliance.jsonl.

Built BEFORE any subagent or skill because it\'s the single most
important primitive in the system. Every other component is built with
the hook already in place.

**Build:**

- scripts/compliance_check.py --- Python module containing the
  claim-detection logic, source-registry validation, and Citations API
  verification. Importable by both the hook (via CLI invocation) and the
  compliance-qa subagent (via Python import) and CI.

- .claude/hooks/pre-tool-use-compliance.sh --- Shell script that reads
  the hook input JSON from stdin, calls compliance_check.py, returns
  hookSpecificOutput.permissionDecision JSON per Claude Code hook spec.

- Claim detection: regex patterns for common medical claim shapes
  (percentages, dosages, outcomes, diagnoses) plus Haiku 4.5 second-pass
  for nuanced detection. The regex catches the obvious; the LLM
  second-pass catches \"results may vary\" style hedged claims.

- Source validation: load /sources/registry.json, verify every detected
  claim has a source_id reference in draft frontmatter, verify that
  source_id is approved for that claim type per
  Source.approved_for_claims.

- Audit logging: every decision (allow, ask, deny) appends one JSONL
  line to /audit/compliance.jsonl using AuditEvent schema from Milestone
  1.

- tests/test_compliance_check.py --- Comprehensive test suite:
  known-good drafts pass, known-bad drafts (missing sources, wrong claim
  type, expired source) fail with correct reason codes.

- scripts/migrations/seed_registry.py --- Helper that seeds
  /sources/registry.json with one example source record for testing.
  Real sources added by operator in Milestone 7.

**Verification:**

pytest tests/test_compliance_check.py -v

\# Simulate a blocked commit

echo \'{\"tool_input\": {\"file_path\": \"drafts/test.md\", \"content\":
\"This drug reduces mortality by 50%.\"}}\' \| \\

.claude/hooks/pre-tool-use-compliance.sh

\# Should output JSON with permissionDecision: \"deny\"

\# Check audit log

cat audit/compliance.jsonl \| jq \'.\[-1\]\'

\# Should show the deny event

**Stop point:** Commit as feat(compliance): pre-tool-use hook with
source validation. Report test coverage and example allow/ask/deny
decisions. Wait.

**Scope discipline:** Do not build the compliance-qa subagent yet. The
hook calls the Python module directly for v1. The subagent is a later
optimization for nuanced cases. Do not build other hooks yet either.

## Milestone 3: The first subagent (citation-auditor)

**Goal:** Working citation-auditor subagent at
.claude/agents/citation-auditor.md that takes a URL, uses Chrome
DevTools MCP to render and inspect the page, scores it against the
extractability rubric, writes result to /audit/citation-scores.jsonl.

This is the subagent built first because it\'s what runs on day one for
proof-of-work. The whole Tebra-application value proposition of this
repo --- \"clone it, run /audit tebra.com/any-url, get a structured
report\" --- depends on this subagent working cleanly.

**Build:**

- .claude/agents/citation-auditor.md --- Subagent definition with YAML
  frontmatter per DATA_CONTRACTS.md section 9. Model: Sonnet 4.6. Tools:
  mcp\_\_chrome-devtools\_\_\*, Read, Write.

- scripts/citation_score.py --- The rubric implementation. Five
  dimensions from PRD.md section 5 and DATA_CONTRACTS.md draft
  frontmatter (schema_present, semantic_hierarchy, qa_patterns,
  proof_attribution, answer_first_structure), each scored 0-5 with
  explicit criteria. Total is weighted average.

- The subagent prompt (in the .md body) describes the scoring workflow:
  render URL via Chrome DevTools MCP, extract schema/structured data,
  inspect header hierarchy, detect Q&A patterns, check attribution,
  analyze answer-first structure, then invoke citation_score.py to
  produce the numeric rubric output.

- Output contract: writes JSONL entry to /audit/citation-scores.jsonl
  using AuditEvent schema with event_type: \"citation_score\", AND
  returns structured SubagentResponse JSON with markdown report in
  summary_for_user.

- tests/test_citation_score.py --- Unit tests for the rubric scorer
  against synthetic page fixtures (known-good structure → high score,
  known-bad → low score).

- .claude/commands/audit.md --- The /audit \<url\> slash command that
  dispatches to the subagent.

**Verification:**

pytest tests/test_citation_score.py -v

\# Manual verification in a Claude Code session:

\# 1. Start Claude Code in the repo

\# 2. Run: /audit https://www.tebra.com/features

\# 3. Verify: markdown report returned, audit log appended, score
between 0-5

Live URL verification is manual for v1 because automating Chrome
DevTools MCP in CI is out of scope for this milestone.

**Stop point:** Commit as feat(citation-auditor): sonnet 4.6 subagent
with extractability rubric. Report on one real Tebra URL scored
end-to-end. Wait.

**Scope discipline:** Do not build other subagents yet. Do not connect
to Search Console, GA4, or any other MCP server. Only Chrome DevTools.
This milestone proves the subagent pattern end-to-end on the most
user-visible piece.

## Milestone 4: Remaining subagents (brief-author, draft-writer, refresh-auditor)

**Goal:** Three more subagents built, each with the same discipline as
citation-auditor. After this milestone, the /brief, /draft, /refresh
slash commands all work end-to-end.

**Build (in this order within the milestone):**

1.  **brief-author** (.claude/agents/brief-author.md):

    - Model: Sonnet 4.6. Tools: Search Console MCP, GA4 MCP, Firecrawl
      MCP, Exa MCP, Asana MCP, Read, Write.

    - Input: query cluster string. Output: /briefs/\<slug\>.json
      validated against Brief schema + Asana task created.

    - .claude/commands/brief.md slash command.

2.  **draft-writer** (.claude/agents/draft-writer.md):

    - Model: Opus 4.7 with xhigh effort. Tools: Read, Write, plus all
      seven skills via auto-invocation.

    - Input: brief slug or path. Output: /drafts/\<slug\>.md validated
      against Draft frontmatter schema.

    - CRITICAL: the PreToolUse compliance hook from Milestone 2 fires on
      the Write-to-drafts action. The subagent MUST handle deny
      decisions gracefully (revise draft, retry) rather than treating
      them as failures.

    - .claude/commands/draft.md slash command.

3.  **refresh-auditor** (.claude/agents/refresh-auditor.md):

    - Model: Sonnet 4.6. Tools: Chrome DevTools MCP, Firecrawl MCP, Exa
      MCP, Read, Write.

    - Input: URL or glob. Output: appends recommended_changes\[\] to
      existing draft frontmatter AND writes a refresh event to
      /audit/compliance.jsonl with event_type: \"refresh_triggered\".

    - .claude/commands/refresh.md slash command.

- tests/test_subagent_contracts.py --- Validates that each subagent\'s
  output matches SubagentResponse schema.

**Verification:**

pytest tests/test_subagent_contracts.py -v

\# Manual in a Claude Code session:

\# 1. /brief \"tebra vs athenahealth for independent practices\" → brief
JSON exists and validates

\# 2. /draft tebra-vs-athenahealth → draft MD exists and validates,
compliance hook ran

\# 3. /refresh https://www.tebra.com/features → refresh event logged

**Stop point:** Commit as feat(subagents): brief-author, draft-writer,
refresh-auditor. Demo all three in one session. Wait.

**Scope discipline:** Do not build compliance-qa, product-truth, or the
citation-reporter subagent yet. Do not build ANY skills yet --- the
draft-writer in this milestone uses inline prompting until Milestone 6.
Do not build the remaining hooks yet.

## Milestone 5: MCP server configuration

**Goal:** .mcp.json wired for all 13 MCP servers from ARCHITECTURE.md
section 6. MCP Tool Search enabled. Streamable HTTP used everywhere
available. All credentials referenced from env vars.

**Build:**

- .mcp.json at repo root with all 13 server configs.

- .env.example at repo root documenting every required env var with a
  comment describing acquisition.

- scripts/validate_mcp_config.py that parses .mcp.json, verifies every
  referenced env var is present (without reading its value), warns on
  any SSE transport (migration target for post-June-30-2026).

- tests/test_mcp_config.py validating the JSON schema of .mcp.json.

- Addition to .github/workflows/ci.yml: invoke validate_mcp_config.py in
  CI.

- Update .claude/settings.json with ENABLE_TOOL_SEARCH=true and explicit
  1h cache_control TTL pinning for the brand-voice block (to be created
  in Milestone 6).

**Verification:**

python scripts/validate_mcp_config.py

\# Should: pass, print any SSE warnings, list missing env vars if any

pytest tests/test_mcp_config.py

\# Manual: run /audit in a session, verify Tool Search activates (check
/mcp output shows deferred tools)

**Stop point:** Commit as feat(mcp): configure 13 servers with tool
search enabled. Report any SSE-transport flags. Wait.

**Scope discipline:** Do not actually authenticate the MCP servers
during build --- credential setup is Milestone 11 (RUNBOOK
operationalization). Configure only. If credentials are missing, the
subagents from Milestones 3-4 will error cleanly, which is correct
behavior.

## Milestone 6: The seven skills

**Goal:** All seven skills from ARCHITECTURE.md section 7 built as
SKILL.md files with proper YAML frontmatter, optional references/
directories, and auto-invocation descriptions.

**Build (in this order within the milestone):**

1.  **tebra-brand-voice** --- Always auto-invokes on content tasks.
    Contains: tone guidance, cadence rules, banned words,
    healthcare-specific language constraints. References folder: none
    (single SKILL.md sufficient).

2.  **citation-block-library** --- The seven modular blocks. Main
    SKILL.md describes when to invoke (whenever another BOFU skill is
    active). references/ directory contains one template file per block
    type: quick-answer.md, comparison-table.md, proof.md,
    roi-snippet.md, faq-schema.md, implementation-steps.md,
    testimonial.md. Each template matches the format in
    DATA_CONTRACTS.md section 4.

3.  **healthcare-compliance** --- Auto-invokes on any draft-writer or
    product-truth run. Contains: medical claim detection patterns, PHI
    scrub rules, FDA/AMA/HIPAA guardrails summary. references/ contains:
    approved-sources-policy.md, banned-claim-patterns.md,
    phi-detection-rules.md. Note: the PreToolUse hook uses
    scripts/compliance_check.py directly. This skill is for the
    draft-writer\'s in-flight self-check to avoid generating claims that
    will later be blocked.

4.  **bofu-comparison-page** --- Auto-invokes when brief.asset_type ==
    \"comparison\". Feature-parity table structure, pricing block
    schema, honest-tradeoff paragraph pattern. references/ contains one
    complete example comparison page from a non-healthcare SaaS
    (anonymized) as a reference implementation.

5.  **bofu-roi-calculator** --- Auto-invokes when brief.asset_type ==
    \"roi_calculator\". React artifact patterns, auto-generated
    schema-tagged FAQ, \"how this calculator works\" block for LLM
    extraction.

6.  **bofu-case-study** --- Auto-invokes when brief.asset_type ==
    \"case_study\". 650-1050 word structure, problem/solution/outcome,
    quantified outcomes, PII/PHI scrub checklist.

7.  **bofu-implementation-guide** --- Auto-invokes when brief.asset_type
    == \"implementation_guide\". Step-numbered structure, Citations API
    block-indexing for every procedural step.

**Verification:**

\# Structural

ls .claude/skills/\*/SKILL.md \# All 7 exist

python scripts/validate_skills.py \# Validates YAML frontmatter (write
this script as part of the milestone)

\# Functional

\# In a Claude Code session, run: /draft \<existing-brief-slug\>

\# Verify in the session output that the right skills auto-invoke based
on brief.asset_type

**Stop point:** Commit as feat(skills): seven skills for brand voice,
block library, compliance, four BOFU types. Wait.

**Scope discipline:** Skills are procedural knowledge, not templates for
every possible case. Keep each SKILL.md under 200 lines. Move examples
to references/. Resist the urge to enumerate every edge case; skills
degrade at length.

## Milestone 7: Source registry seeding

**Goal:** /sources/registry.json and at least five real source records
exist, covering the authority tiers and claim types needed for a first
real draft.

**Build:**

- /sources/registry.json --- master index with entries for each source
  below.

- At least five source records across these categories:

  - 1× internal_doc authority tier 1 (a Tebra product overview or
    equivalent)

  - 1× third_party_research authority tier 2 (KLAS, Gartner, or
    peer-reviewed study)

  - 1× customer_interview authority tier 1 (redacted; can be synthetic
    for v1)

  - 1× regulatory_document authority tier 2 (HIPAA, FDA guidance
    excerpt)

  - 1× any additional real source at operator\'s discretion

- Every source record validates against Source Pydantic model from
  Milestone 1.

- Each source\'s binary (PDF or markdown) lives in the appropriate
  /sources/\<subdir\>/ path.

- scripts/validate_sources.py --- validates the registry matches on-disk
  files, checks expires_at for any already-expired sources, verifies
  claim_type alignment.

- Addition to CI: validate_sources.py runs as part of the
  schema-validate job.

**Verification:**

python scripts/validate_sources.py \# Passes with zero warnings

\# Test compliance hook against a real source

echo \'\<test-draft-with-cited-claim\>\' \|
.claude/hooks/pre-tool-use-compliance.sh

\# Should: decision=allow for properly cited claims

**Stop point:** Commit as feat(sources): seed registry with 5 example
sources across authority tiers. Report which sources were used and any
expiry-date considerations. Wait.

**Scope discipline:** Real Tebra internal docs for Tebra\'s actual use
of this system come later; for v1 (which is the proof-of-work repo),
synthetic-but-realistic sources are acceptable. If using real
third-party sources, respect their licensing.

## Milestone 8: Remaining hooks and remaining subagents

**Goal:** The three remaining hooks (SessionStart, PostToolUse, Stop)
and the two remaining subagents (compliance-qa, product-truth,
citation-reporter) are built.

Deliberately later in the build because each of these depends on earlier
pieces: SessionStart hook loads brand-voice and source registry
(requires Milestones 6 and 7), citation-reporter needs
HubSpot/Profound/Peec AI MCP working (Milestone 5 + auth setup),
compliance-qa is a speed optimization over scripts/compliance_check.py.

**Build (in this order within the milestone):**

1.  **SessionStart hook** (.claude/hooks/session-start-load-context.sh):

    - Outputs to stdout: current brand-voice version, source registry
      count + any expiring-soon, current refresh backlog count,
      compliance rule version.

    - Claude Code captures stdout into session context.

    - Pinned 1h cache_control TTL via .claude/settings.json block
      configuration.

2.  **Stop hook** (.claude/hooks/stop-run-linters.sh):

    - Runs ruff on any changed Python, prettier on markdown,
      scripts/validate_drafts.py on anything in /drafts/.

    - Non-blocking async if feasible per async: true flag.

3.  **PostToolUse hook** (.claude/hooks/post-commit-changelog.sh):

    - Async. Appends to /audit/publish.jsonl on every git commit
      touching /drafts/.

    - Feeds the refresh-velocity KPI.

4.  **compliance-qa subagent** (.claude/agents/compliance-qa.md):

    - Model: Haiku 4.5. Tools: Read, source-registry access.

    - Called by the PreToolUse hook for nuanced cases (hedged claims,
      ambiguous attribution).

    - Same deny/allow/ask contract as the Python-only check.

5.  **product-truth subagent** (.claude/agents/product-truth.md):

    - Model: Opus 4.7. Tools: Google Drive MCP, Read, Write. Uses
      Citations API natively.

    - Only invoked by draft-writer when asset_type ==
      \"implementation_guide\".

    - Every procedural step output carries Citations API block-index
      grounding.

6.  **citation-reporter subagent**
    (.claude/agents/citation-reporter.md):

    - Model: Sonnet 4.6. Tools: Profound MCP, Peec AI MCP, Search
      Console MCP, GA4 MCP, HubSpot MCP, Slack MCP.

    - Weekly report runner.

    - .claude/commands/citation-report.md slash command.

**Verification:**

\# Structural

ls .claude/hooks/\*.sh \# 4 hooks present

ls .claude/agents/\*.md \# 6 subagents present

\# Functional (in a Claude Code session)

\# 1. Start new session, verify SessionStart output in initial Claude
context

\# 2. Run /citation-report → verify Slack posted, Artifact created

\# 3. Commit a draft with hedged medical claim (\"results may vary\") →
verify compliance-qa subagent invoked

\# 4. /draft \<implementation-guide-brief\> → verify product-truth
subagent engaged

**Stop point:** Commit as feat: complete hook and subagent layer. Demo
each in a session. Wait.

**Scope discipline:** After this milestone, the acceptance criteria in
PRD.md section 6 items 1-7 should all pass. Run them explicitly as part
of the verification.

## Milestone 9: CLAUDE.md, AGENTS.md, PROMPT_TO_PASTE

**Goal:** The three entry-point files that humans and Claude Code read
first. Written LAST because they codify what actually got built, not
what was planned.

**Build:**

- **CLAUDE.md** (\~250 lines, hard ceiling): universally applicable
  agent-behavior rules. References AGENTS.md, points to docs/ for
  everything else. Reserved for Claude Code-specific behaviors
  (@imports, /init).

- **AGENTS.md**: cross-tool-standard version of the same content.
  Compatible with Codex CLI, Cursor, Gemini CLI. Per the Linux
  Foundation standard.

- **PROMPT_TO_PASTE_IN_CLAUDE_CODE.md**: a kickoff prompt for someone
  cloning this repo and running it for the first time. Tells Claude
  Code: read CLAUDE.md, read AGENTS.md, skim docs/PRD.md, then wait for
  instruction.

- **README.md**: expand from Milestone 0 stub. Human-facing: what this
  is, install command (/plugin install \<repo-path\>), quickstart
  (/audit \<url\> as the day-one demo), links to docs/.

**Verification:**

wc -l CLAUDE.md \# Under 300 lines

wc -l AGENTS.md \# No hard limit, but target similar density

\# Manual: new Claude Code session in this repo, paste PROMPT_TO_PASTE
content, verify it orients correctly

**Stop point:** Commit as docs: entry-point files (CLAUDE.md, AGENTS.md,
README). Wait.

**Scope discipline:** Code style rules live in ruff/prettier, not
CLAUDE.md. Per the April 2026 research: models reliably follow \~150
instructions; exceeding the budget degrades ALL rules, not just the new
ones.

## Milestone 10: End-to-end dry run

**Goal:** Full happy-path runtime flow from ARCHITECTURE.md section 2
executes cleanly in a single Claude Code session.

**Build:** No new files. This is verification.

**Verification:** Run the following in a single Claude Code session and
capture the output as docs/E2E_DRY_RUN.md:

1\. (new session) → SessionStart hook fires, context loaded

2\. /brief \"tebra vs athenahealth for independent practices\"

3\. Review /briefs/tebra-vs-athenahealth.json

4\. /draft tebra-vs-athenahealth

5\. Review /drafts/tebra-vs-athenahealth.md

6\. Verify PreToolUse hook fired and all claims are sourced

7\. /audit \<any Tebra URL\>

8\. /refresh \<same URL\>

9\. /citation-report

10\. Verify /audit/\*.jsonl files all have appended entries

**Stop point:** Commit the E2E doc as docs: e2e dry run transcript.
Wait.

**Scope discipline:** If any step fails, return to the corresponding
milestone and fix. Do not paper over failures with retries; fix root
causes.

## Milestone 11: Operational setup (RUNBOOK completion)

**Goal:** docs/RUNBOOK.md is complete and a new operator can go from git
clone to a working /audit in under 30 minutes following only the
RUNBOOK.

**Build:**

- Complete RUNBOOK.md per the separate doc (comes in v0.2 of the spec).

- Every env var from .env.example documented with acquisition URL and
  auth flow.

- MCP server-by-server setup walkthrough with screenshots placeholder.

- Known-issue callouts: cache TTL regression (pin to 1h), SSE
  deprecation (June 30, 2026), Opus 4.7 tokenizer (35% more tokens for
  identical text --- benchmark cost on your prompts).

**Verification:** Fresh clone, follow RUNBOOK, achieve first successful
/audit without asking questions outside the doc.

**Stop point:** Commit as docs: complete RUNBOOK.md. Wait.

## Milestone 12: Plugin packaging and distribution

**Goal:** The repo is installable as a Claude Code plugin via /plugin
install \<repo-path\> and, once installed, gives a freelancer parity
with internal team capabilities.

**Build:**

- Plugin manifest per Claude Code plugin spec (April 2026).

- scripts/package_plugin.sh builds the distributable.

- docs/FREELANCER_ONBOARDING.md --- 10-minute quickstart for external
  contributors.

- Version pinning in .mcp.json and .claude/settings.json.

**Verification:** Second operator, fresh machine, runs the install
command, runs /draft against an existing brief, verifies output matches
internal-team output.

**Stop point:** Commit as feat: plugin distribution v1.0. Tag release
v1.0.0.

## After v1.0

Post-launch work (NOT part of v1):

- Real-time citation monitoring (currently weekly).

- Multi-language support.

- Additional MCP servers as Tebra\'s actual stack is revealed.

- Scheduled automation via GitHub Actions cron.

- Migration to AGENTS.md as primary entry point once Claude Code reads
  it natively (tracked in issues anthropics/claude-code#34235 and
  #6235).

These are intentionally deferred. v1 ships when Milestones 0-12 are
complete.

## One rule for the build

At every stop point, the build pauses for review. Do not batch
milestones. Do not skip stop points. Do not assume a milestone is
\"close enough.\" The AMIE pattern worked because the stops were
honored. Trust the pattern.
