# PRD: tebra-content-os

**Status:** Draft v0.1 · April 21, 2026 **Owner:** Jordan Damhof
(github.com/nice-and-precise) **Context:** Portfolio + proof-of-work
asset for Tebra Senior AI Content Marketing Manager application. Also a
durable content-operations reference architecture that outlives any
single job outcome.

## 1. Problem

B2B SaaS content operations in 2026 have a visibility problem that older
SEO and content-ops playbooks cannot solve. The shift: buyers now ask
ChatGPT, Claude, Gemini, Perplexity, and Google AI Overviews *before*
they click a single SERP result. A page that ranks #3 on Google but is
never cited in an LLM answer is a page the modern buyer never sees.

This creates three concrete operational failures in typical B2B SaaS
marketing teams:

1.  **Extractability gap.** Content is written for human readers, not
    for LLM retrieval. Answer-first structure, schema, Q&A blocks, and
    proof attribution are absent or inconsistent, so LLMs skip the page
    when synthesizing answers.

2.  **BOFU asset gap.** MOFU/BOFU asset types that convert (competitor
    comparisons, ROI calculators, product-led case studies,
    implementation guides) are produced inconsistently, reviewed
    inconsistently, and refreshed on no defined cadence.

3.  **Workflow gap.** AI tools are used ad-hoc by individual marketers
    and freelancers, with no shared brief format, no compliance gating,
    no citation enforcement, and no auditability. The output quality is
    whatever the operator\'s personal prompting skill happens to produce
    that day.

The job description for Tebra\'s Senior AI Content Marketing Manager
role is a near-perfect problem statement for this system: *\"enforce
AI-first workflows to automate content planning, briefing, drafting, and
approval\"* on *\"structured content that is modular, semantically rich,
and optimized for AI/LLM extraction,\"* measured by *\"share of
citation, pipeline influence, and refresh velocity.\"* The named BOFU
asset types in the ATS screener (comparison pages, ROI calculators, case
studies, implementation guides) match the four highest-converting
categories in B2B SaaS. The hiring manager\'s explicit framing, *\"not
pumping out low-quality AI content at scale,\"* rules out prompt-only
approaches and creates room for a system with deterministic quality
gates.

## 2. Users

**Primary:** Senior AI Content Marketing Manager (the operator). Runs
the system day-to-day, reviews briefs, approves drafts, resolves flagged
compliance issues, and reports on KPIs.

**Secondary:**

- **Freelance writers.** Install the same skill bundle the operator
  uses, so brand voice, source requirements, and block templates are
  enforced at their terminal rather than in a Google Doc checklist.

- **Product marketing managers (PMM).** Approve drafts via Asana before
  publish. Receive Slack notifications when a draft is ready for their
  review.

- **SEO lead.** Feeds Search Console and GA4 signals into brief
  generation; reviews refresh priorities.

- **Customer marketing.** Supplies case study interview transcripts and
  testimonial blocks that the case-study sub-agent consumes.

- **Engineering / web.** Forks the ROI calculator artifact into
  production; implements Webflow publish hooks.

- **Healthcare compliance reviewer.** The PreToolUse hook is their last
  line of defense for PHI and unapproved claims; they review flagged
  blocks.

## 3. Goals

Ranked by impact on the operator\'s KPIs.

1.  **Ship content that gets cited** (share-of-citation KPI). Every
    published page is extractability-graded before publish. Schema, Q&A
    structure, and answer-first patterns are enforced by skills, not
    hoped for.

2.  **Ship BOFU assets on demand** (pipeline-influence KPI). Comparison
    pages, ROI calculators, case studies, and implementation guides each
    have a dedicated sub-agent and skill bundle. Producing one is a
    single slash command, not a three-week project.

3.  **Refresh the existing library at defined velocity**
    (refresh-velocity KPI). git log over /drafts/ is the report. A
    weekly refresh-auditor sub-agent diffs published URLs against
    current SERP and LLM answers and flags staleness.

4.  **Enforce \"no AI slop\"** (quality gate, non-negotiable).
    PreToolUse hooks block commits containing unapproved medical claims,
    PHI, or content without a Citations-API-verified source. Every
    medical claim has a verifiable source before it leaves the repo.

5.  **Run at freelancer scale** (distribution goal). The editorial
    guidelines, brand voice, compliance rules, and block library ship as
    one installable skill bundle (tebra-content plugin). Freelancers get
    parity with the internal team via /plugin install.

## 4. Non-goals

Explicit exclusions, following the AMIE PRD pattern.

- **This is not a CMS.** Webflow (or whatever Tebra runs) remains the
  source of truth for published pages. This system drafts, gates, and
  publishes *through* MCP; it does not own page hosting.

- **This is not a replacement for PMM judgment.** Every BOFU asset and
  every case study is gated by human Asana approval before publish. The
  system accelerates, it does not autonomize.

- **No automated Reddit or paid-social posting.** Following the AMIE
  principle: channels where brand voice is fragile stay in a manual
  approval queue.

- **No medical claim generation outside retrieved source material.** The
  product-truth sub-agent uses Citations API grounded in retrieved docs;
  it does not speculate.

- **No scraping of competitor content beyond what Firecrawl and Exa
  expose respecting robots.txt.** No CAPTCHA bypass, fingerprint
  spoofing, or residential proxies. Mirrors the AMIE compliance posture.

- **No analytics dashboarding.** The weekly citation-report sub-agent
  posts to Slack and writes a Claude Artifact. GA4/HubSpot dashboards
  remain where they live.

- **Not a pure prompt library.** If the answer to \"how do we get Claude
  to do X\" is \"write a better prompt,\" that answer does not ship
  here. Hooks, skills, and sub-agents ship; prompts are implementation
  detail.

## 5. Success metrics

Measured monthly. The first three map directly to Tebra\'s named role
KPIs.

  -----------------------------------------------------------------------
  **Metric**              **Definition**          **Target
                                                  (steady-state)**
  ----------------------- ----------------------- -----------------------
  Share of citation       \% of tracked buyer     Baseline + 15 points
                          queries across ChatGPT, over 6 months
                          Claude, Gemini,         
                          Perplexity, Google AIO  
                          where Tebra is cited or 
                          linked                  

  Pipeline influence      HubSpot-attributed      Measurable attribution
                          pipeline sourced to     on 100% of published
                          cited pages             BOFU assets

  Refresh velocity        Git commits to /drafts/ 40+ fresh assets +
                          per month, weighted by  refreshes / month
                          asset type              

  Extractability score    Average rubric score    4.0+ out of 5.0
                          (schema, Q&A,           
                          answer-first, proof)    
                          across the library      

  Compliance hit rate     \% of drafts blocked by 90%+ true positive
                          PreToolUse hook that    
                          were genuine policy     
                          violations (vs false    
                          positives)              

  Freelancer parity       Variance in             \<0.3 points
                          extractability score    
                          between internal and    
                          freelance-authored      
                          assets                  
  -----------------------------------------------------------------------

## 6. Acceptance criteria for v1

The system is v1-acceptable when every statement below is demonstrably
true.

1.  Someone clones the repo, runs claude, and the SessionStart hook
    loads the Tebra brand voice, approved-sources registry, and
    compliance rules into context automatically.

2.  /audit \<url\> runs the citation-auditor sub-agent against a live
    URL via Chrome DevTools MCP and returns a structured JSON score plus
    a markdown report.

3.  /brief \"\<query cluster\>\" runs the brief-author sub-agent using
    Search Console MCP + GA4 MCP + Firecrawl MCP and commits a
    structured brief to /briefs/\<slug\>.json plus an Asana task.

4.  /draft \<brief-slug\> runs the draft-writer sub-agent using the
    appropriate BOFU skill (comparison, ROI, case-study,
    implementation-guide) and the brand-voice skill. Output lands in
    /drafts/\<slug\>.md.

5.  Any attempt by the draft-writer (or a human committer) to publish a
    medical claim without a Citations-API-backed source is blocked by
    the PreToolUse compliance hook. The block is logged to
    /audit/compliance.jsonl.

6.  /refresh \<url\> runs the refresh-auditor sub-agent, which diffs the
    live URL against current SERP + LLM answers and writes a
    recommended-changes block.

7.  /citation-report runs the weekly report sub-agent using Profound
    MCP + Peec AI MCP + Search Console MCP + HubSpot MCP and writes both
    a Claude Artifact and a Slack digest.

8.  The complete skill bundle is installable via /plugin install
    tebra-content@\<repo-path\> and, once installed, gives a freelancer
    parity with the internal team\'s brand voice, block library, and
    compliance rules.

9.  All MCP servers use Streamable HTTP transport where supported; SSE
    is used only where no HTTP endpoint exists.

10. Cache TTL is explicitly set to 1h in cache_control for the brand
    voice and compliance rule blocks, to avoid the March 2026 5-minute
    default regression.

11. Repository passes its own CI: ruff + pytest on any glue code, plus a
    compliance-check script that validates every draft in /drafts/ has
    Citations-API-verified sources for medical claims.

12. README, AGENTS.md, and CLAUDE.md are readable in under five minutes
    by someone who has never used Claude Code. A senior engineering
    leader cloning the repo can understand what each directory does from
    the top-level docs alone.

## 7. Out of scope for v1

- Real-time citation monitoring (weekly is fine for v1; real-time is
  v2).

- Multi-language content. English only for v1.

- Video or interactive content formats. Text + structured data only for
  v1.

- Non-Tebra customer deployments. This is scoped to Tebra\'s stack;
  generalizing is v2.

## 8. Key risks and mitigations

  ---------------------------------------------------------------------------------
  **Risk**                **Likelihood**          **Mitigation**
  ----------------------- ----------------------- ---------------------------------
  Anthropic changes       Medium                  Explicit \"ttl\": \"1h\" in every
  default cache TTL again                         cache_control block; keepalive
  (March 2026 precedent)                          thread for always-on caches.

  MCP server deprecation  Certain                 Default to Streamable HTTP in
  (SSE transport                                  .mcp.json; flag any SSE
  sunsetting June 30,                             dependency as a v1.1 migration.
  2026)                                           

  CLAUDE.md               High if not disciplined Code style offloaded to ruff +
  instruction-budget                              linter invoked via Stop hook.
  overflow (\>150 net                             CLAUDE.md reserved for
  instructions)                                   agent-behavior rules only.

  Third-party MCP server  Medium                  Each MCP dependency gets a
  quality (e.g. Profound,                         1-sentence fallback note in
  Peec AI, Firecrawl)                             RESEARCH_GAPS_AND_DECISIONS.md.
  changing auth models or                         
  pricing                                         

  PHI leak in a cached    Low but catastrophic    Brand voice cache is
  brand voice or source                           content-only, no customer data.
  registry                                        Source registry is public-URL
                                                  allowlist, no customer records.

  Freelancer installs     Medium                  Plugin version pinned in
  outdated plugin version                         .mcp.json; freelancer /plugin
                                                  update documented in RUNBOOK.md.
  ---------------------------------------------------------------------------------

## 9. Open questions (deferred to RESEARCH_GAPS_AND_DECISIONS.md)

- Whether Profound MCP or Peec AI MCP is the primary citation-tracking
  source, or both.

- Whether Tebra\'s existing Webflow instance supports the Webflow MCP,
  or if we need a stub adapter.

- How healthcare compliance reviewers prefer to consume the
  compliance.jsonl audit log (Slack, email digest, or dashboard).

- Cost envelope: first-month estimate at typical 40-asset volume,
  including cache write amplification.

## 10. What this PRD intentionally does not specify

Architecture (sub-agent topology, hook wiring, MCP server list) lives in
ARCHITECTURE.md. Schemas for briefs, blocks, citations, and audit
records live in DATA_CONTRACTS.md. Implementation order lives in
TASKS.md. Env vars and deploy commands live in RUNBOOK.md.

This PRD is the frozen *why* and *what*. The *how* is intentionally
deferred and versioned separately so architectural decisions can iterate
without rewriting the problem statement.
