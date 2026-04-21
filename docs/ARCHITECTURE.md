# ARCHITECTURE: tebra-content-os

**Status:** Draft v0.1 · April 21, 2026 **Depends on:** PRD.md (problem,
users, acceptance criteria) **Target runtime:** Claude Code CLI 2.1.111+
· Opus 4.7 and Sonnet 4.6 · MCP spec 2025-11-25

## 1. System overview

The system is a single repository that, when cloned, boots a complete
content-operations workspace inside Claude Code. The repository is the
product. There are no external services to deploy, no containers to run,
no databases to provision. State lives in git-tracked markdown and JSON;
ephemeral state lives in the Claude Code session; durable external state
(published pages, CRM records, analytics) stays in the systems that
already own it, accessed via MCP.

The system has five primitive layers, each with a specific
responsibility and a specific lifecycle event it owns. Confusing these
layers is the most common architectural mistake; the table below is the
canonical decision tree.

  --------------------------------------------------------------------------
  **Layer**         **Responsibility**   **When it runs**  **Can it block?**
  ----------------- -------------------- ----------------- -----------------
  **Skills**        Procedural           Auto-invoked by   No
                    knowledge: how to    Claude when the   
                    write a comparison   task matches the  
                    page, what the brand skill\'s          
                    voice sounds like,   description       
                    what compliance                        
                    rules apply                            

  **Subagents**     Isolated-context     Spawned by the    No
                    workers: brief       main agent,       
                    author, draft        either via slash  
                    writer, compliance   command or by     
                    auditor, refresh     Claude\'s         
                    auditor, citation    judgment          
                    reporter                               

  **Slash           Explicit             Only when the     No
  commands**        user-invoked         user types them   
                    workflows: /audit                      
                    \<url\>, /brief                        
                    \<query\>, /draft                      
                    \<slug\>, /refresh                     
                    \<url\>,                               
                    /citation-report                       

  **Hooks**         Deterministic gates  Lifecycle events  **Yes**
                    and context          (SessionStart,    (PreToolUse only)
                    injection:           PreToolUse,       
                    compliance           PostToolUse,      
                    enforcement, source  Stop)             
                    validation, session                    
                    setup                                  

  **MCP servers**   External system      On-demand via MCP No
                    access: Search       Tool Search       
                    Console, GA4,                          
                    HubSpot, Webflow,                      
                    Asana, Slack, Chrome                   
                    DevTools, Firecrawl,                   
                    Exa, Profound, Peec                    
                    AI                                     
  --------------------------------------------------------------------------

**Decision tree for where new logic goes:**

1.  If it must happen regardless of what Claude decides → **hook**.

2.  If it needs to access an external system → **MCP server**.

3.  If it\'s a multi-step workflow that needs its own context window →
    **subagent**.

4.  If it\'s procedural knowledge Claude should apply when relevant →
    **skill**.

5.  If it\'s user-invoked only and one-shot → **slash command**.

Getting this wrong is what produces AI slop. \"Brand voice\" as a prompt
in every request = inconsistent output. \"Brand voice\" as a skill
auto-invoked on content tasks = consistent output. \"Medical claim
gating\" as a prompt = sometimes works. \"Medical claim gating\" as a
PreToolUse hook = always works.

## 2. Runtime flow (happy path: publish a new comparison page)

User: /brief \"tebra vs athenahealth for independent practices\"

↓

SessionStart hook already fired → brand voice, source registry,
compliance rules in context

↓

Slash command \`/brief\` dispatches → brief-author subagent

↓

Subagent: MCP Tool Search → loads search-console, ga4, firecrawl, exa
tools only

↓

Subagent: pulls query-cluster signal (Search Console), buyer-intent
(GA4), competitor SERP (Firecrawl), LLM consensus answer (Exa)

↓

Subagent: writes /briefs/tebra-vs-athenahealth.json using the brief
schema

↓

Subagent: creates Asana task via Asana MCP, status = \"brief ready\"

↓

Returns structured summary to main agent → user sees: \"Brief ready at
briefs/tebra-vs-athenahealth.json, Asana task #1234\"

↓

User: /draft tebra-vs-athenahealth

↓

Slash command \`/draft\` dispatches → draft-writer subagent

↓

Subagent: reads brief JSON, auto-invokes \`bofu-comparison-page\`
skill + \`tebra-brand-voice\` skill

↓

Subagent: writes /drafts/tebra-vs-athenahealth.md using block library
(comparison table, proof block, FAQ schema, testimonial)

↓

PreToolUse hook on git-commit: scan for medical claims → cross-check
/sources/ registry → BLOCK if any unsourced

↓

If blocked: log to /audit/compliance.jsonl, return flagged blocks to
subagent for citation or removal

↓

If passed: commit /drafts/tebra-vs-athenahealth.md, update Asana task to
\"draft ready for PMM review\"

↓

Slack MCP posts to #content-review with link

↓

PMM approves in Asana → Asana webhook (via Asana MCP) triggers Webflow
publish via Webflow MCP

↓

PostToolUse hook logs publish event to /audit/publish.jsonl (feeds
refresh-velocity KPI)

This is the full loop. Every arrow is a specific Claude Code primitive;
no step is \"prompt engineering\" and no step is handwaved.

## 3. Directory layout

tebra-content-os/

├── CLAUDE.md \# Entry point. \~250 lines. Agent-behavior rules only.

├── AGENTS.md \# Cross-tool standard (Cursor, Codex, Gemini CLI compat)

├── README.md \# Human-facing: what this is, install, quickstart

├── PROMPT_TO_PASTE_IN_CLAUDE_CODE.md \# Kickoff prompt for first-time
build sessions

│

├── docs/

│ ├── PRD.md \# Problem, users, goals, acceptance

│ ├── ARCHITECTURE.md \# This file

│ ├── DATA_CONTRACTS.md \# Schemas for brief, block, citation, audit

│ ├── TASKS.md \# Implementation milestones with stop points

│ ├── RUNBOOK.md \# Env vars, local dev, operational notes

│ ├── RESEARCH_GAPS_AND_DECISIONS.md \# Decisions log + open questions

│ └── REPO_PRINCIPLES_EXTRACTED.md \# IP mined from squti/amie/lli-saas,
attributed

│

├── .claude/

│ ├── settings.json \# Project-level config: permissions, hook
registration

│ ├── agents/ \# Subagent definitions (.md with YAML frontmatter)

│ │ ├── brief-author.md

│ │ ├── draft-writer.md

│ │ ├── citation-auditor.md \# The piece that runs on day one

│ │ ├── refresh-auditor.md

│ │ ├── compliance-qa.md

│ │ └── product-truth.md \# Implementation-guide sub-agent with
Citations API

│ ├── skills/ \# Agent Skills Standard (SKILL.md + optional references/)

│ │ ├── tebra-brand-voice/

│ │ │ └── SKILL.md

│ │ ├── bofu-comparison-page/

│ │ │ ├── SKILL.md

│ │ │ └── references/ \# Template fragments, examples

│ │ ├── bofu-roi-calculator/

│ │ │ └── SKILL.md

│ │ ├── bofu-case-study/

│ │ │ └── SKILL.md

│ │ ├── bofu-implementation-guide/

│ │ │ └── SKILL.md

│ │ ├── citation-block-library/ \# Modular blocks: QuickAnswer,
Comparison Table, etc.

│ │ │ ├── SKILL.md

│ │ │ └── references/

│ │ └── healthcare-compliance/

│ │ ├── SKILL.md

│ │ └── references/ \# Compliance rules, approved-sources policy

│ ├── commands/ \# Slash commands (legacy directory; still works
alongside skills)

│ │ ├── audit.md

│ │ ├── brief.md

│ │ ├── draft.md

│ │ ├── refresh.md

│ │ └── citation-report.md

│ └── hooks/ \# Deterministic lifecycle handlers

│ ├── session-start-load-context.sh

│ ├── pre-tool-use-compliance.sh \# The non-negotiable quality gate

│ ├── post-commit-changelog.sh

│ └── stop-run-linters.sh

│

├── .mcp.json \# MCP server config (Streamable HTTP transport)

│

├── briefs/ \# Committed structured briefs (JSON)

├── drafts/ \# Committed content drafts (markdown with frontmatter)

├── blocks/ \# Reusable block instances (markdown fragments)

├── sources/ \# Approved-sources registry: PDFs, docs, attributions

├── audit/ \# Append-only audit logs (JSONL)

│ ├── compliance.jsonl \# Every PreToolUse hook decision

│ ├── publish.jsonl \# Every Webflow publish event

│ └── citation-scores.jsonl \# Extractability scores over time

│

├── scripts/ \# Thin Python glue (not where logic lives)

│ ├── compliance_check.py \# CI-invokable version of the PreToolUse
logic

│ ├── citation_score.py \# Rubric scorer called by citation-auditor
subagent

│ └── refresh_diff.py \# Diff helper for refresh-auditor subagent

│

├── pyproject.toml \# Python deps: httpx, pydantic, ruff, pytest

├── tests/ \# pytest

└── .github/workflows/ \# GitHub Actions: ruff + pytest +
compliance_check

Total directory count: manageable. Total novelty: low. The directory
layout mirrors AMIE\'s proven pattern, with .claude/ replacing .agents/
to match Claude Code\'s conventions.

## 4. The five subagents

Each subagent is a markdown file in .claude/agents/ with YAML
frontmatter (name, description, tools, model). Subagents inherit the
main agent\'s CLAUDE.md but run in their own context window. Exact
schemas are in DATA_CONTRACTS.md.

**brief-author** (model: Sonnet 4.6, tools: search-console, ga4,
firecrawl, exa, filesystem). Takes a query cluster as input. Produces a
structured JSON brief: target intent, must-cite proof points, required
internal links, BOFU CTA, schema hints, sources list. Posts Asana task.

**draft-writer** (model: Opus 4.7, tools: filesystem, Read, Write, plus
the relevant skills). Takes a brief JSON path as input. Auto-invokes the
right BOFU skill (comparison, ROI, case study, implementation guide)
based on brief.asset_type. Auto-invokes brand-voice skill and
block-library skill. Writes /drafts/\<slug\>.md with YAML frontmatter
containing source citations in Citations API format.

**citation-auditor** (model: Sonnet 4.6, tools: chrome-devtools,
filesystem). Takes a URL as input. Uses Chrome DevTools MCP to render
the page, extract structured data, schema, headers, Q&A patterns. Scores
against the extractability rubric. Writes result to
/audit/citation-scores.jsonl and returns a markdown report. This is the
subagent that runs on day one for proof-of-work.

**refresh-auditor** (model: Sonnet 4.6, tools: chrome-devtools,
firecrawl, exa, filesystem). Takes a URL or glob. Diffs the live URL
against current SERP and LLM consensus answers. Flags staleness, missing
competitor coverage, citation drift. Writes recommended-changes block to
the corresponding /drafts/\<slug\>.md frontmatter.

**compliance-qa** (model: Haiku 4.5 for speed, tools: filesystem,
sources registry). Not user-invoked. Called by the PreToolUse hook when
a commit contains candidate medical claims. Uses Citations API to verify
each claim has a source in /sources/. Returns {allow \| deny \| ask}
with reason. Deny decisions get logged to /audit/compliance.jsonl.

**product-truth** (model: Opus 4.7, tools: google-drive, filesystem,
Citations API native). Only invoked for implementation-guide drafts.
Reads Tebra product documentation via Google Drive MCP (or equivalent
internal docs MCP). Writes procedural steps with Citations API
block-index grounding so every step has verifiable doc attribution.

## 5. Hooks: the quality gate

Four hooks, each with one job. Hooks are the non-negotiable layer
because PreToolUse is the only primitive that can deterministically
block.

**SessionStart: session-start-load-context.sh** Injects into context:
Tebra brand voice (cached, 1h TTL), approved-sources registry path,
current refresh backlog count, compliance rule version. Output is
stdout; Claude Code captures it into the session. Pinned 1h TTL on the
cache_control block to avoid the March 2026 regression.

**PreToolUse: pre-tool-use-compliance.sh** Fires on git commit, Write to
/drafts/, and Bash commands that publish. Parses the target content for
medical claims using the healthcare-compliance skill\'s claim-detection
regex + LLM second-pass. For each claim, validates against /sources/
registry using Citations API. Returns
hookSpecificOutput.permissionDecision:

- allow if all claims have verified sources

- ask if borderline (claim is factual but source attribution ambiguous)

- deny if any claim lacks source; appends reason to
  /audit/compliance.jsonl

This is the single piece of the system that makes \"no AI slop\" a hard
guarantee rather than a hope.

**PostToolUse: post-commit-changelog.sh** Async, non-blocking. Fires
after every git commit to /drafts/. Appends to /audit/publish.jsonl:
timestamp, slug, author, asset type, extractability score, citation
count. Feeds the refresh-velocity KPI and the monthly cost report.

**Stop: stop-run-linters.sh** Runs ruff on any Python changes, prettier
on markdown, and a custom block-library linter that validates every
/drafts/\*.md file has the required YAML frontmatter fields. Code style
lives here, not in CLAUDE.md, per the instruction-budget research.

## 6. MCP servers: the external surface

All servers use Streamable HTTP transport where available, per the
2025-11-25 spec. SSE is used only where no HTTP endpoint exists; each
such dependency is flagged in RESEARCH_GAPS_AND_DECISIONS.md as a v1.1
migration target. MCP Tool Search is enabled by default
(ENABLE_TOOL_SEARCH=true) so only the 3-5 relevant tools per task hit
the context window, not all 140+ across the 13 servers below.

  --------------------------------------------------------------------------------------
  **Server**     **Transport**   **Scope**      **Used by**          **Notes**
  -------------- --------------- -------------- -------------------- -------------------
  Google Search  HTTP            project        brief-author,        Query-cluster
  Console                                       refresh-auditor      signal

  GA4            HTTP            project        brief-author,        Buyer intent,
                                                citation-reporter    traffic data

  HubSpot        HTTP            project        citation-reporter,   Pipeline
                                                draft-writer         attribution,
                                                                     customer
                                                                     testimonials

  Webflow        HTTP            project        draft-writer         CMS target
                                                (publish step)       

  Asana          HTTP            project        all subagents (task  Workflow
                                                creation, updates)   orchestration

  Slack          HTTP            project        citation-reporter,   Notifications, team
                                                draft-writer         digest

  Google Drive   HTTP            project        product-truth,       Product docs,
                                                case-study           interview
                                                                     transcripts

  Figma          HTTP            project        draft-writer         Product screenshots
                                                (optional)           for implementation
                                                                     guides

  Chrome         stdio (local)   project        citation-auditor,    Live URL
  DevTools                                      refresh-auditor      rendering +
                                                                     inspection

  Firecrawl      HTTP            project        brief-author,        Competitor SERP
                                                refresh-auditor      crawling

  Exa            HTTP            project        brief-author         LLM consensus
                                                                     answer retrieval

  Profound       HTTP            project        citation-reporter    Share-of-citation
                                                                     across LLMs

  Peec AI        HTTP            project        citation-reporter    Secondary citation
                                                                     tracking
  --------------------------------------------------------------------------------------

Auth model: each MCP server\'s credentials live in shell env vars, never
in .mcp.json (which is git-committed). RUNBOOK.md enumerates the full
env var list with acquisition instructions.

## 7. Skills: the procedural knowledge layer

Seven skills ship in v1. Each is a SKILL.md with YAML frontmatter (name,
description for auto-invocation matching) plus optional references/
directory for templates and examples.

**tebra-brand-voice** (always auto-invokes on content tasks): tone,
cadence, banned words, healthcare-specific language rules.

**bofu-comparison-page**: feature-parity table structure, pricing block
schema, honest-tradeoff paragraph pattern, testimonial block placement.
Auto-invokes when brief.asset_type == \"comparison\".

**bofu-roi-calculator**: calculator UX patterns (React artifact),
auto-generated schema-tagged FAQ, \"how this calculator works\" block
for LLM extraction. Auto-invokes when brief.asset_type ==
\"roi_calculator\".

**bofu-case-study**: 650-1050 word structure, problem → solution →
outcome, quantified outcomes in hero and summary, PII/PHI scrub.
Auto-invokes when brief.asset_type == \"case_study\".

**bofu-implementation-guide**: step-numbered structure, Citations API
block-indexing for every procedural step, \"before you start\"
prerequisites, \"if you get stuck\" troubleshooting. Auto-invokes when
brief.asset_type == \"implementation_guide\".

**citation-block-library**: the seven modular blocks (QuickAnswer,
Comparison Table, Proof Block, ROI Snippet, FAQ Schema, Implementation
Steps, Testimonial) as markdown templates. Auto-invokes whenever another
BOFU skill is active.

**healthcare-compliance**: medical claim detection patterns, PHI scrub
rules, FDA/AMA/HIPAA guardrails, approved-sources validation logic.
Auto-invokes on any draft-writer or product-truth run. Also called
directly by the PreToolUse hook.

## 8. Data contracts (summary; full schemas in DATA_CONTRACTS.md)

- **Brief** (/briefs/\<slug\>.json): slug, asset_type, target_intent,
  proof_points\[\], required_internal_links\[\], bofu_cta,
  schema_hints\[\], sources\[\], created_at, created_by.

- **Draft** (/drafts/\<slug\>.md): YAML frontmatter with slug,
  asset_type, status, sources\[\], extractability_score,
  last_refreshed_at. Body is markdown with embedded block-library
  instances.

- **Citation record** (Citations API format): type: \"document\",
  source: {type, data}, citations: true, title, context. Inlined into
  draft YAML frontmatter.

- **Audit event** (/audit/\*.jsonl): timestamp, event_type, slug, actor,
  decision, reason, metadata.

## 9. Model routing

- **Opus 4.7** (xhigh effort): draft-writer, product-truth. Where output
  quality compounds.

- **Sonnet 4.6**: brief-author, citation-auditor, refresh-auditor. Where
  quality matters but the task is more retrieval + analysis than
  generation.

- **Haiku 4.5**: compliance-qa. Where speed of the blocking decision
  matters and the task is classification-shaped.

All cache_control blocks pin \"ttl\": \"1h\" explicitly. No reliance on
defaults.

## 10. What\'s intentionally *not* in this architecture

- **No plugin marketplace.** The repo is the plugin. Freelancers install
  via /plugin install \<repo-path\> directly.

- **No custom database.** Git is the database for briefs, drafts, and
  audit logs. Anything that needs query shape beyond grep lives in an
  MCP-connected system.

- **No scheduled jobs running locally.** The weekly citation-report is
  triggered by the operator running /citation-report, not cron. If Tebra
  wants true scheduling, GitHub Actions on a cron schedule is the v1.1
  path.

- **No prompts in the main agent\'s CLAUDE.md.** CLAUDE.md is rules
  about agent behavior; prompts live in skills and subagents where they
  can be versioned, tested, and reused.

The architecture is deliberately boring where it can be and opinionated
where it matters. The opinions are: deterministic quality gates via
hooks, cross-tool-portable skills, MCP for external systems, git for
state, Citations API for source grounding, Tool Search for context
hygiene.
