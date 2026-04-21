# REPO_PRINCIPLES_EXTRACTED: tebra-content-os

**Status:** Draft v0.1 · April 21, 2026
**Depends on:** `PRD.md`, `ARCHITECTURE.md`, `DATA_CONTRACTS.md`, `TASKS.md`, `RUNBOOK.md`, `RESEARCH_GAPS_AND_DECISIONS.md`
**Audience:** Engineering reviewer asking "where did these patterns come from? Are they speculative, or have they shipped elsewhere?"

---

## 1. Purpose

This file documents the **design lineage** of `tebra-content-os`: which architectural, operational, and editorial patterns were imported from prior shipped systems versus invented here. The goal is auditability, not credit-claiming. A reviewer evaluating this repo should be able to distinguish a pattern that's been proven in production from one that's being tried for the first time.

Three source systems are mined:

- **`squti`** — Production backend for BoreReady (github.com/nice-and-precise/squti), a B2B SaaS certification platform operating under Minn. Stat. § 326B.198 with two paying clients and Minnesota DLI statutory approval. Shipped and live.
- **`amie`** — Autonomous Marketing & Intelligence Engine (github.com/nice-and-precise/amie), a $20K engagement built for Whitaker Marketing Group covering Iowa farmland listings. Shipped v1, operational.
- **`lli-saas`** — Land Lead Intelligence SaaS (github.com/nice-and-precise/lli-saas), a monorepo platform with Kubernetes deployment. Scaffolded, deployable, not yet in production use.

For each repo, the subsections below pull out specific principles — architectural decisions, operational patterns, or editorial stances — and map each one to the place in `tebra-content-os` where it transfers. Where a pattern is novel to this repo, it is noted.

**How to read this file:** treat the principles as load-bearing assertions. Each one is either inherited from a shipped system (where it has evidence of working), adapted with noted modifications, or flagged as untested. The cross-cutting themes in Section 5 surface what's consistent across all three source systems — those are the design invariants worth trusting the most.

---

## 2. Principles inherited from `squti` (BoreReady)

Context: `squti` is a Frappe-based backend that turns authored curriculum into typed LMS records, delivers DLI packets under statutory constraints, and integrates LLM-assisted generation with a master-switch fallback. Because BoreReady operates under Minn. Stat. § 326B.198 with a DLI-approved curriculum, the repo is engineered under actual regulatory constraint — not a hypothetical one.

### 2.1 Typed content records with stable IDs

**Source.** The curriculum importer (`squti_core/curriculum/importer.py`) turns authored markdown into typed Course, Chapter, Lesson, Quiz, and Question records, each with a stable ID. Downstream systems — quiz rendering, completion tracking, certificate generation — reference by ID, never by text match.

**Transfer to `tebra-content-os`.** `DATA_CONTRACTS.md` defines typed records with stable identifiers at every layer: `slug` on briefs and drafts, `source_id` on registry entries, `block_id` on every citation-bearing block, `event_type` on audit events. The compliance hook resolves claims to sources by `source_id`, not by substring matching claim text against source text. This is the squti pattern applied to content operations.

### 2.2 Deterministic fallback for LLM-assisted operations

**Source.** The Squti Settings DocType carries a master switch for LLM-assisted content generation. When enabled, an LLM handles the flagged step; when disabled, a deterministic path handles the same step. The system never has "LLM required or the whole thing breaks."

**Transfer to `tebra-content-os`.** The PreToolUse compliance hook (`.claude/hooks/pre-tool-use-compliance.sh`) runs a Python regex-based claim detector first and escalates to the Haiku-4.5 `compliance-qa` subagent only for nuanced cases. If Anthropic's API is down or rate-limited, the deterministic Python path still enforces the gate; the LLM layer is optimization, not requirement. Same principle, narrower scope.

### 2.3 Encrypted API key storage with per-environment model override

**Source.** The Squti Settings DocType stores encrypted API keys and supports per-environment model overrides (dev vs staging vs prod can use different models without code changes).

**Transfer to `tebra-content-os`.** `.env` carries credentials; `.claude/settings.json` carries model routing; both are referenced by name, never hard-coded. `RUNBOOK.md` Section 4 enumerates every env var, and Section 6.3 documents model routing as config, not code. An operator can swap Opus 4.7 for a future model release by editing one settings file; no subagent definition changes required.

### 2.4 Version-controlled authoritative content, reused across every output

**Source.** The curriculum bundle PDF is generated once per curriculum version and reused across every adopter packet. Authoritative content is versioned; it is not regenerated per use.

**Transfer to `tebra-content-os`.** The `tebra-brand-voice` skill is the brand-voice source of truth; every draft inherits from it via auto-invocation. Source documents in `/sources/` carry `expires_at` dates and are version-controlled via git. Drafts cite source IDs, not inline re-statements of source content. Same principle: author once, reuse everywhere, and when the authoritative version changes, every downstream output traces the change through git.

### 2.5 Infrastructure-constraint awareness baked into the content pipeline

**Source.** The DLI packet delivery system auto-splits packets across multiple emails when the total payload exceeds 15 MB, because email gateways reject larger attachments. The system understands its delivery channel's limits and adapts the content pipeline accordingly.

**Transfer to `tebra-content-os`.** Cache TTL is pinned `"ttl": "1h"` explicitly everywhere because the March 2026 Anthropic API default changed silently (RUNBOOK Section 9.1). MCP Tool Search is enabled because the context budget is real and 140+ tools in context would burn it. Audit logs rotate at 100 MB because grep and jq slow down past that. The pipeline respects the constraints of the platforms it runs on, rather than assuming they are infinite.

### 2.6 Regulatory compliance as an architectural property, not a checklist

**Source.** BoreReady's Minnesota DLI statutory compliance is not a banner on the marketing site — it is a property the system produces because the architecture forces it. Typed curriculum records, stable IDs, versioned content bundles, and audit trails exist because a DLI reviewer can request any of them at any time.

**Transfer to `tebra-content-os`.** The PreToolUse hook is the architectural gate that makes "no unsourced medical claims" a deterministic property, not a policy note. Every deny decision writes to `audit/compliance.jsonl` with an immutable event. The source registry's `approved_for_claims` field enforces claim-type alignment at the schema level. A healthcare compliance reviewer can audit any draft and trace every claim back to a source — by architecture, not by goodwill. This is the squti regulatory posture translated into healthcare content ops.

### 2.7 End-to-end Claude Code integration as a first-class capability

**Source.** squti integrates Claude Code directly using `claude-sonnet-4-6` as the production model for LLM-assisted steps. Claude Code is a shipped component of BoreReady's backend, not an internal developer tool.

**Transfer to `tebra-content-os`.** The entire repo is designed to run inside Claude Code sessions. Subagents live in `.claude/agents/`, skills in `.claude/skills/`, hooks in `.claude/hooks/`, config in `.claude/settings.json`. Claude Code is the runtime, not an IDE; the system is an application built on top of it.

---

## 3. Principles inherited from `amie` (Whitaker Marketing)

Context: `amie` is a Python/FastAPI autonomous content pipeline that monitors Iowa farmland listing sources, normalizes and enriches records, drafts localized blog and social content, and routes high-risk outputs through Telegram approval. v1 shipped as a $20K engagement. Because amie is a content-ops system specifically — not a general backend — its principles transfer most directly.

### 3.1 Brief-to-publish as a full pipeline, not a presentation

**Source.** amie implements every stage from source monitoring through publish: listing ingestion → normalization → enrichment → draft generation → channel-specific routing → publish via WordPress REST API. Nothing is handwaved; every stage is observable and testable.

**Transfer to `tebra-content-os`.** The runtime flow in `ARCHITECTURE.md` Section 2 is a full pipeline: SessionStart hook loads context → `/brief` runs the brief-author subagent with retrieval across GSC/GA4/Firecrawl/Exa → `/draft` runs the draft-writer with appropriate BOFU skill → PreToolUse hook gates on compliance → Slack notification → PMM Asana approval → Webflow publish → PostToolUse hook logs to `audit/publish.jsonl`. Every arrow is a specific Claude Code primitive. Milestone 10 is the end-to-end dry run that validates the pipeline works in one session.

### 3.2 Channel-specific approval routing

**Source.** amie's Telegram approval workflow doesn't apply uniformly. WordPress drafts (low risk, brand-controlled surface) auto-publish. Reddit and any other "brand voice is fragile" channel route to human approval. The approval threshold varies by channel because the risk varies by channel.

**Transfer to `tebra-content-os`.** BOFU drafts (comparison pages, ROI calculators, case studies, implementation guides) route to PMM Asana approval before Webflow publish because the brand voice and claim accuracy matter at publish time. Citation audit runs (`/audit <url>`) require no approval — they read existing pages and write to an audit log, never publish. The citation-report (`/citation-report`) writes to Slack and a Claude Artifact without approval because it is a report, not content going live on Tebra's site. Same principle: approval threshold follows channel risk.

### 3.3 Explicit exclusions as architectural decisions, not omissions

**Source.** amie's PRD explicitly lists what the system will not do: no automated Reddit posting, no CAPTCHA bypass, no fingerprint spoofing, no moderation evasion. These are architectural decisions, not "we didn't get to that yet." The exclusion list is what makes amie's posture defensible in a professional context.

**Transfer to `tebra-content-os`.** `PRD.md` Section 4 (Non-goals) and Section 7 (Out of scope for v1) make equivalent declarations: this is not a CMS replacement, not a substitute for PMM judgment, no automated Reddit posting, no medical claim generation outside retrieved source material, no scraping beyond what Firecrawl and Exa expose respecting robots.txt. Each exclusion is a deliberate stance. The hiring manager's framing — *"not pumping out low-quality AI content at scale"* — is validated by the exclusion list, not by the marketing copy.

### 3.4 Enrichment as a separate observable stage

**Source.** amie's pipeline separates: raw listing → normalized record → enriched record (with county and soil context) → draft. Enrichment is not a step inside generation; it is its own stage, with its own inputs and outputs, observable and testable independently. A draft that references county soil data is not writing from whole cloth — it is writing from retrieved facts.

**Transfer to `tebra-content-os`.** The brief-author subagent retrieves signal from Search Console (query cluster), GA4 (buyer intent), Firecrawl (competitor SERP), and Exa (LLM consensus answer) BEFORE any draft is generated. The brief is a structured record with proof points, source IDs, and competitor coverage; the draft-writer consumes that brief, it does not re-discover its facts. This enforces amie's separation between retrieval and generation.

### 3.5 Retrieval before generation, always

**Source.** amie never generates first and retrieves later. Every amie output is grounded in a retrieval stage that precedes it; this is why the outputs hold up under editorial scrutiny rather than reading as generic AI copy.

**Transfer to `tebra-content-os`.** The Citations API integration in the `product-truth` subagent grounds every procedural step in retrieved product documentation. The source registry is consulted before compliance-qa approves any medical claim. The citation-auditor reads the actual live URL via Chrome DevTools MCP before scoring. Generation is always downstream of retrieval; nothing is generated first and verified later. "Retrieval before generation" is the single most transferable pattern amie carries.

### 3.6 Scheduling as an in-application service (eventually)

**Source.** amie uses APScheduler inside the FastAPI app rather than /etc/crontab. This makes scheduling observable (logs appear in the same place as the rest of the app's logs), testable (scheduled jobs run in CI on synthetic triggers), and restart-aware (scheduled state survives app restarts cleanly).

**Transfer to `tebra-content-os`.** Not directly inherited in v1 — RESEARCH_GAPS_AND_DECISIONS.md Section 7 defers scheduled automation to v1.1, and the chosen path is GitHub Actions cron (external scheduler) rather than APScheduler (in-app). Trade-off: GitHub Actions is simpler for a repo-as-product distribution model because it doesn't require an always-on process. The amie pattern would be right if this system ever runs as a hosted service; for v1's operator-triggered model, external scheduling is cleaner.

### 3.7 Editorial posture under AI assistance

**Source.** amie's PRD and operational decisions embed a specific editorial posture: AI assistance is used where it accelerates the work, human judgment is preserved where voice or brand is fragile. The system makes this explicit rather than letting it drift into "ship whatever the LLM produces."

**Transfer to `tebra-content-os`.** PMM Asana approval before publish is the human-in-the-loop checkpoint. The `tebra-brand-voice` skill auto-invokes so brand voice is enforced, not hoped for. The compliance-qa subagent and PreToolUse hook together ensure no medical claim ships without source attribution. AI assistance accelerates the draft; editorial judgment remains the gate.

---

## 4. Principles inherited from `lli-saas`

Context: `lli-saas` is a fresh-start monorepo with three services (FastAPI lead-engine, Express CRM adapter, Vite React user-portal), Helm-based Kubernetes deployment, and infrastructure-as-code throughout. Scaffolded and deployable, not yet in production use. The lessons here are about repo discipline and multi-service architecture, not production runtime behavior.

### 4.1 Scope discipline enforced in the repo itself

**Source.** `.planning/PROJECT.md` in lli-saas explicitly lists what is out of scope. The scope doc is inside the repo, committed to git, and updated when scope decisions change. A scope statement that lives only in someone's head doesn't constrain behavior; one in the repo does.

**Transfer to `tebra-content-os`.** `PRD.md` Section 4 (Non-goals), Section 7 (Out of scope for v1), and `TASKS.md`'s per-milestone "Scope discipline" sections carry this pattern. Every milestone lists what NOT to build, not just what to build. The `RESEARCH_GAPS_AND_DECISIONS.md` Section 7 deferred-items table is the long-form version: what was considered, what was cut, and what would trigger reconsideration.

### 4.2 Rejecting naming drift from prior projects

**Source.** lli-saas deliberately rejects naming conventions from older adjacent projects. New project = new vocabulary, even when patterns are reused. This prevents legacy concepts from leaking in and confusing future readers who don't share the historical context.

**Transfer to `tebra-content-os`.** `tebra-content-os` is its own vocabulary. There are no references to AMIE's "listing normalizer" or squti's "DocType" bleeding in. The docs use Tebra-specific framing — BOFU asset types, extractability rubric, citation share — that a Tebra hiring reviewer recognizes. Patterns are reused; naming is not. The AMIE docs pattern is applied (PRD/ARCH/CONTRACTS/TASKS/RUNBOOK/RESEARCH_GAPS) but the content is written fresh.

### 4.3 Infrastructure-as-code at every layer

**Source.** lli-saas declares infrastructure via Helm charts, Kubernetes CronJob, persistent volume claims, autoscaling config, GHCR registry integration. Nothing is clicked in a console; everything is a committed artifact.

**Transfer to `tebra-content-os`.** `.claude/settings.json` declares hooks, permissions, model routing, cache TTL. `.mcp.json` declares every MCP server, transport, and credential reference. `pyproject.toml` declares Python deps. `.github/workflows/ci.yml` declares CI. `.env.example` declares every required secret name. The repo is fully declarative — an operator cloning it gets a reproducible environment, not a "follow these 14 steps" setup guide. This is the lli-saas IaC posture applied to a Claude Code repo.

### 4.4 Pattern generalization with care

**Source.** lli-saas applies AMIE's brief-to-publish pipeline pattern to a different vertical (land leads instead of farmland listings). The lesson from the exercise: the pattern is reusable, but the domain layer must be rewritten domain-specifically. Copy-pasting AMIE's enrichment logic would have produced a worse lli-saas.

**Transfer to `tebra-content-os`.** The AMIE docs pattern (six-file docs/ structure) is inherited wholesale because it's proven. The AMIE pipeline pattern (brief → draft → approval → publish) is inherited structurally but the domain is completely rewritten: BOFU asset types instead of property listings, extractability rubric instead of location enrichment, healthcare compliance instead of farmland sensitivity. Reuse the scaffolding; rewrite the substance. lli-saas validated this approach; tebra-content-os follows the same rule.

### 4.5 Multi-service separation of concerns

**Source.** lli-saas separates the lead-engine (intelligence layer) from the CRM adapter (integration layer) from the user-portal (presentation layer). Each service has one responsibility, talks to the others via documented contracts, and can be replaced independently.

**Transfer to `tebra-content-os`.** The five-layer primitive decomposition (skills, subagents, slash commands, hooks, MCP servers) in `ARCHITECTURE.md` Section 1 is the equivalent. Each layer has one responsibility. Each subagent can be replaced without rewriting the others. Each MCP server can be swapped for a different vendor. The separation of concerns is preserved by matching each Claude Code primitive to one job; mixing responsibilities across primitives is the architectural mistake to avoid.

### 4.6 Tight requirements discipline as editorial judgment

**Source.** lli-saas's `.planning/PROJECT.md` explicitly lists what it will not do, rejects naming drift, and states scope boundaries. This is editorial judgment applied to a codebase — the same judgment that applies to writing a comparison page also applies to scoping a software project.

**Transfer to `tebra-content-os`.** Editorial judgment runs through the spec: PRD non-goals, TASKS scope-discipline sections, RESEARCH_GAPS deferred list, the insistence on stop points between milestones. A content-ops system built without editorial discipline about its own scope cannot be trusted to enforce editorial discipline on the content it produces. The repo walks the talk.

---

## 5. Cross-cutting themes

Principles that appear consistently across all three source systems. These are the design invariants with the strongest evidence — if the same decision was reached independently in three different domains (curriculum certification, farmland content marketing, lead intelligence), it is probably load-bearing.

### 5.1 Git is the durable store

All three repos treat git as the source of truth for state that matters. squti commits curriculum versions; amie commits brief records and draft outputs; lli-saas commits infrastructure declarations. `tebra-content-os` continues this: briefs, drafts, sources, audit logs, and configuration all live in git. No separate database for v1. Auditability follows from append-only commit history that humans can read.

### 5.2 Explicit non-goals as architectural statements

Every source repo explicitly documents what it will not do. `tebra-content-os` inherits this discipline in `PRD.md` Section 4 and `RESEARCH_GAPS_AND_DECISIONS.md` Section 7. Non-goals are not omissions; they are decisions, and they read as competence to any reviewer who understands scope.

### 5.3 Observable stages with typed contracts between them

Each source repo separates concerns into observable stages with typed data flowing between them. amie's listing→normalized→enriched→draft. squti's markdown→Course/Chapter/Lesson/Quiz. lli-saas's three-service boundary. `tebra-content-os` applies this at the subagent level: brief-author produces a typed `Brief`, draft-writer consumes the `Brief` and produces a typed `Draft`, citation-auditor produces typed `AuditEvent`s. Pipeline stages are never freeform prose passed between actors; they are structured contracts.

### 5.4 Human-in-the-loop where it matters, automated everywhere else

amie routes fragile-voice channels to Telegram approval. squti routes curriculum changes through DLI review cycles. lli-saas separates user-portal interactions from automated lead processing. `tebra-content-os` routes BOFU drafts through PMM Asana approval while auto-running citation audits. Each system answers the same question (where does automation stop?) with the same principle (at the boundary where editorial judgment or brand voice is the product).

### 5.5 Compliance as architecture, not paperwork

squti's DLI posture, amie's no-Reddit/no-CAPTCHA-bypass exclusion list, lli-saas's scope boundaries — each is a compliance or governance decision expressed in code and config rather than in a policy document. `tebra-content-os` does the same with the PreToolUse hook and source registry. Policy that lives only in a Google Doc is policy that slips; policy enforced at the architectural layer holds.

### 5.6 Cross-tool portability where possible

amie's WordPress/Mixpost/Telegram split doesn't lock to one vendor; lli-saas's service separation enables independent replacement; squti's model-override pattern supports multi-provider LLM use. `tebra-content-os` uses the Agent Skills Standard for cross-tool portability (Cursor, Codex CLI, Gemini CLI) and Streamable HTTP for MCP portability across future transports. Vendor lock-in is treated as a liability, not a feature.

### 5.7 Regulated-content track record

squti operates under Minn. Stat. § 326B.198. amie operates within explicit ethical exclusions. lli-saas maintains documented scope boundaries. Each source system has shipped under real constraint — legal, ethical, or governance. `tebra-content-os` applies the same posture to healthcare content: HIPAA-adjacent, FDA/AMA-claim-sensitive, PHI-scrubbing. The operator is not new to regulated content; the repo is not the first time this kind of discipline has been asked of this operator.

---

## 6. What this document is not

This file is not a portfolio pitch. The goal is to let a reviewer verify that the patterns in `tebra-content-os` are inherited from shipped systems, not invented from scratch. If a principle above reads as promotional rather than attributional, it needs rewriting; flag it in `RESEARCH_GAPS_AND_DECISIONS.md` and fix it.

This file is also not exhaustive. Principles from `manufacturing-scanner` (Bayer Built PWA), from operational experience at Bayer Built Woodworks (battle-card library, market intelligence pipelines), and from Ames Fire Department training operations are all relevant design inputs that aren't mined here. They are mentioned in adjacent docs (the resume, the repo inventory, the thesis doc) and they may surface in cover-letter framing or interview conversations, but this file is scoped specifically to repo-level IP transfer from the three systems listed in Section 1.

If a pattern in `tebra-content-os` cannot be traced to one of these three source repos or explicitly marked as novel, that is a gap — either the pattern should be traced, or the novelty should be acknowledged honestly.

---

## 7. Novel to this repo (no external inheritance)

Completeness requires naming what is new here, because "inherited from shipped systems" is only a useful claim if the scope of inheritance is bounded.

- **Five-primitive decomposition** (skills / subagents / slash commands / hooks / MCP servers) as the explicit framing. The primitives themselves are Claude Code's; treating them as a decision tree for "where does new logic go?" is this repo's framing.
- **Citation API integration specifically for medical claim grounding** in the `product-truth` subagent. squti uses LLMs for curriculum generation; amie uses LLMs for drafting; neither wires Citations API as a primary grounding mechanism because neither has the medical-claim-grounding requirement.
- **Extractability rubric** as a five-dimension scoring system (schema, semantic hierarchy, Q&A patterns, proof attribution, answer-first structure). The dimensions are drawn from public writing about LLM retrieval patterns; the rubric composition is novel here.
- **MCP Tool Search enabled by default** with the implication that subagent descriptions drive tool loading. This is a April 2026 Claude Code feature; treating it as a first-class architectural concern is this repo's posture.

Each of these is untested in production and carries correspondingly more risk than the inherited patterns above. Treated honestly, they are the parts of `tebra-content-os` that need the closest scrutiny during Milestones 0–10 and that would get revised first if early usage surfaces problems.

---

The rest of the spec is in the other five docs under `docs/`. This file's job is to make the design lineage explicit; the decision log, the runbook, the architecture, the data contracts, and the task milestones are where the system itself lives.