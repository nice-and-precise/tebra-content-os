# DATA_CONTRACTS: tebra-content-os

**Status:** Draft v0.1 · April 21, 2026 **Depends on:** PRD.md (what the
system does), ARCHITECTURE.md (how it\'s wired) **Audience:** Claude
Code build sessions, human contributors, freelancers writing against the
schemas

## 1. Why schemas matter here

Every subagent writes structured output that another subagent or hook
will consume. If the brief schema drifts, the draft-writer breaks. If
the draft frontmatter drifts, the compliance hook fails silently and
lets bad content through. If the citation record doesn\'t match
Anthropic\'s Citations API format, source grounding degrades.

These contracts are the single point of coordination. Every change to a
schema is a breaking change and gets logged in
RESEARCH_GAPS_AND_DECISIONS.md with a migration note.

All schemas validated with Pydantic v2 in scripts/schemas.py. CI runs
schema validation on every /briefs/\*.json and every /drafts/\*.md
frontmatter.

## 2. Brief (/briefs/\<slug\>.json)

The brief-author subagent\'s output. The draft-writer subagent\'s input.
Human-readable enough to review in a PR.

{

\"schema_version\": \"1.1\",

\"slug\": \"tebra-vs-athenahealth\",

\"asset_type\": \"comparison\",

\"target_intent\": {

\"primary_query\": \"tebra vs athenahealth for independent practices\",

\"query_cluster\": \[

\"tebra vs athenahealth pricing\",

\"athenahealth alternatives for small practices\",

\"ehr comparison independent physician\"

\],

\"buyer_stage\": \"BOFU\",

\"persona\": \"independent_practice_owner\"

},

\"proof_points\": \[

{

\"claim\": \"Tebra\'s all-in-one EHR+PM+billing reduces vendor sprawl\",

\"source_id\": \"src_tebra_product_overview_2026\",

\"source_type\": \"internal_doc\",

\"required\": true

},

{

\"claim\": \"Independent practices spend average \$X/month on
athenahealth\",

\"source_id\": \"src_klas_ehr_pricing_2026\",

\"source_type\": \"third_party_research\",

\"required\": false

}

\],

\"required_internal_links\": \[

\"/ehr-for-independent-practices\",

\"/pricing\"

\],

\"bofu_cta\": {

\"primary\": \"Book a demo\",

\"secondary\": \"Download comparison PDF\"

},

\"schema_hints\": \[

\"FAQPage\",

\"Product\",

\"ComparisonTable\"

\],

\"competitor_coverage\": {

\"required\": \[\"athenahealth\"\],

\"optional\": \[\"eClinicalWorks\", \"NextGen\"\]

},

\"sources\": \[

{

\"id\": \"src_tebra_product_overview_2026\",

\"type\": \"internal_doc\",

\"path\": \"sources/internal/tebra-product-overview-2026.pdf\",

\"cite_as\": \"Tebra Product Overview 2026\"

},

{

\"id\": \"src_klas_ehr_pricing_2026\",

\"type\": \"third_party_research\",

\"url\": \"https://klasresearch.com/\...\",

\"cite_as\": \"KLAS Research, EHR Pricing Trends 2026\"

}

\],

\"asana_task_id\": \"1234567890\",

\"created_at\": \"2026-04-21T14:30:00Z\",

\"created_by\": \"brief-author-subagent\",

\"created_by_version\": \"0.1.0\"

}

**Asset types enum:** comparison, roi_calculator, case_study,
implementation_guide, refresh, quick_answer. **Buyer stage enum:** TOFU,
MOFU, BOFU. **Source type enum:** internal_doc, customer_interview,
third_party_research, regulatory_document, peer_reviewed.

Validation rules:

- schema_version MUST match current version; migration scripts live in
  scripts/migrations/.

- Every proof_points\[\].source_id MUST resolve to an entry in
  sources\[\].

- If asset_type == \"comparison\", competitor_coverage.required MUST be
  non-empty.

- If asset_type == \"case_study\", sources\[\] MUST contain at least one
  customer_interview source.

- If asset_type == \"implementation_guide\", sources\[\] MUST contain at
  least one internal_doc source for product truth grounding.

## 3. Draft (/drafts/\<slug\>.md)

YAML frontmatter + markdown body. The draft-writer subagent\'s output.
The PreToolUse compliance hook\'s input.

\-\--

schema_version: \"1.1\"

slug: \"tebra-vs-athenahealth\"

asset_type: \"comparison\"

status: \"draft\" \# draft \| pmm_review \| approved \| published \|
archived

brief_path: \"briefs/tebra-vs-athenahealth.json\"

author:

type: \"subagent\" \# subagent \| freelancer \| internal

identifier: \"draft-writer\"

version: \"0.1.0\"

extractability_score:

total: 4.2

schema_present: 5

semantic_hierarchy: 4

qa_patterns: 4

proof_attribution: 5

answer_first_structure: 3

scored_at: \"2026-04-21T15:45:00Z\"

scored_by: \"citation-auditor-subagent\"

sources:

\- id: \"src_tebra_product_overview_2026\"

claims_cited:

\- block_id: \"comparison-table-row-3\"

claim: \"Tebra\'s all-in-one EHR+PM+billing reduces vendor sprawl\"

citation_api_format:

type: \"document\"

source:

type: \"base64\"

media_type: \"application/pdf\"

data: \"\<base64-encoded-pdf\>\"

citations: true

title: \"Tebra Product Overview 2026\"

context: \"Internal product documentation\"

\- id: \"src_klas_ehr_pricing_2026\"

claims_cited:

\- block_id: \"comparison-table-row-5\"

claim: \"Independent practices spend average \$X/month on athenahealth\"

citation_api_format:

type: \"document\"

source:

type: \"url\"

url: \"https://klasresearch.com/\...\"

citations: true

title: \"KLAS Research, EHR Pricing Trends 2026\"

compliance_hook_log:

last_run: \"2026-04-21T15:47:12Z\"

decision: \"allow\"

claims_checked: 2

claims_sourced: 2

claims_flagged: 0

publish:

webflow_collection_id: null

webflow_item_id: null

published_url: null

published_at: null

refresh:

last_refreshed_at: \"2026-04-21T15:45:00Z\"

next_refresh_due: \"2026-07-21T00:00:00Z\"

refresh_cadence_days: 91

recommended_changes: \[\]

\-\--

\# Tebra vs AthenaHealth for Independent Practices

\<!\-- block:quick-answer id=\"quick-answer-1\" \--\>

\## The short answer

For independent practices prioritizing an all-in-one platform with
transparent pricing, Tebra typically wins on simplicity and total cost
of ownership. AthenaHealth\'s strengths are enterprise-scale
interoperability and a mature marketplace. Below is a feature-by-feature
comparison and honest tradeoff guidance.

\<!\-- /block \--\>

\<!\-- block:comparison-table id=\"comparison-table-main\" \--\>

\## Feature comparison

\| Feature \| Tebra \| AthenaHealth \|

\|\-\--\|\-\--\|\-\--\|

\| All-in-one EHR + PM + Billing \| Yes \| Add-on modules \|

\| Pricing model \| Transparent monthly \| Percentage of collections \|

\| \... \| \... \| \... \|

\<!\-- /block \--\>

\<!\-- block:proof id=\"proof-1\"
cite=\"src_tebra_product_overview_2026\" \--\>

Tebra\'s all-in-one platform eliminates the three-vendor stack most
independent practices run today.

\<!\-- /block \--\>

\<!\-- additional blocks: FAQ schema, testimonial, honest tradeoffs, CTA
\--\>

**Status enum:** draft, pmm_review, approved, published, archived.
**Author type enum:** subagent, freelancer, internal.

Validation rules:

- Every \<!\-- block:\... cite=\"\...\" \--\> MUST have a matching
  sources\[\].claims_cited\[\].block_id.

- extractability_score.total MUST be ≥ 3.5 for status to advance past
  draft.

- compliance_hook_log.decision MUST be allow for status to advance past
  draft.

- If status == \"published\", publish.published_url and
  publish.published_at MUST be set.

## 4. Block library (/blocks/\<block_type\>/\<variant\>.md)

The seven modular block types from the citation-block-library skill.
Each block is a template with slot variables filled at draft-writer
time.

**Seven block types:**

1.  quick-answer --- 2-4 sentence direct answer to the primary query.
    Lives at top of page for LLM extraction.

2.  comparison-table --- Feature-parity table. Renders with explicit
    column headers and schema-tagged cells.

3.  proof --- Short prose block citing a specific source. Must carry
    cite=\"\<source_id\>\" attribute.

4.  roi-snippet --- Quantified value calculation. Tied to calculator
    artifacts when asset_type == \"roi_calculator\".

5.  faq-schema --- Question-and-answer pairs formatted for FAQPage
    schema markup.

6.  implementation-steps --- Numbered procedural list. Used in
    implementation_guide assets; each step must carry
    cite=\"\<source_id\>\" with Citations API block-index.

7.  testimonial --- Customer quote with attribution. Drawn from HubSpot
    via MCP or from /sources/customer-interviews/.

**Block template format** (/blocks/comparison-table/default.md):

\<!\-- block:comparison-table id=\"{id}\" schema=\"Product\" \--\>

\## {title}

\| Feature \| {subject_name} \| {competitor_name} \|

\|\-\--\|\-\--\|\-\--\|

{rows}

\<!\-- /block \--\>

Slot variables ({id}, {title}, {subject_name}, {competitor_name},
{rows}) are filled by the draft-writer subagent using brief data.

Validation rules:

- Every block instance MUST have a unique id attribute within its draft.

- Every proof and implementation-steps block MUST have a cite attribute.

- Blocks MUST appear in a canonical order in comparison assets:
  quick-answer first, comparison-table second, proof blocks interleaved,
  faq-schema second-to-last, CTA last.

## 5. Source registry (/sources/\*.json + binary files)

The approved-sources registry. Every source the system can cite from
must be registered here. The compliance-qa subagent uses this registry
to verify every claim in a draft.

**Directory structure:**

/sources/

├── registry.json \# Master index

├── internal/

│ ├── tebra-product-overview-2026.pdf

│ ├── tebra-product-overview-2026.json \# Metadata record

│ └── \...

├── third-party/

│ ├── klas-ehr-pricing-2026.pdf

│ └── klas-ehr-pricing-2026.json

├── customer-interviews/

│ ├── acme-family-practice-2026-03-15.md

│ └── acme-family-practice-2026-03-15.json

└── regulatory/

├── hipaa-164-306.pdf

└── hipaa-164-306.json

**Registry entry schema** (/sources/\<subdir\>/\<slug\>.json):

{

\"schema_version\": \"1.1\",

\"id\": \"src_tebra_product_overview_2026\",

\"type\": \"internal_doc\",

\"title\": \"Tebra Product Overview 2026\",

\"authority_tier\": 1,

\"cite_as\": \"Tebra Product Overview 2026\",

\"path\": \"sources/internal/tebra-product-overview-2026.pdf\",

\"url\": null,

\"added_at\": \"2026-04-15T00:00:00Z\",

\"added_by\": \"jordan@boreready.com\",

\"approved_for_claims\": \[

\"product_feature\",

\"pricing\",

\"integration_capability\"

\],

\"not_approved_for_claims\": \[

\"clinical_outcome\",

\"regulatory_compliance\"

\],

\"expires_at\": \"2027-04-15T00:00:00Z\",

\"citation_api_ready\": true

}

**Authority tier enum:**

- 1: Primary source (internal docs, customer interviews, direct product
  observation)

- 2: Authoritative third-party (KLAS, Gartner, peer-reviewed research,
  regulatory documents)

- 3: Secondary (reputable industry press, analyst blogs)

- 4: Not citable; reference only

**Claim type enum:** product_feature, pricing, integration_capability,
clinical_outcome, regulatory_compliance, customer_testimonial,
market_statistic, implementation_procedure.

Validation rules:

- Every source MUST have expires_at set; compliance-qa refuses to
  validate against expired sources.

- Every source MUST declare approved_for_claims. Drafts attempting to
  cite a source for a claim type not in its approved list are flagged.

- authority_tier: 4 sources MUST NOT appear in any claims_cited\[\]
  block. CI check enforces this.

## 6. Citation record (inline in draft frontmatter)

Matches Anthropic\'s Citations API format exactly. Lives inside
drafts/\<slug\>.md YAML frontmatter under
sources\[\].claims_cited\[\].citation_api_format.

citation_api_format:

type: \"document\"

source:

type: \"base64\" \# base64 \| url \| text \| content

media_type: \"application/pdf\"

data: \"\<base64-encoded-content\>\"

citations: true

title: \"Tebra Product Overview 2026\"

context: \"Internal product documentation, approved for product_feature
and pricing claims\"

Supported source types per Anthropic spec as of April 2026: base64, url,
text, content. The compliance-qa subagent enforces that all documents in
a single verification request use the same citation-enabled flag, per
Anthropic\'s uniformity rule.

## 7. Audit event (/audit/\*.jsonl)

Append-only event log. One event per line. Never edited, never deleted;
rotation by month if the file exceeds 100MB.

**Three log files:**

- /audit/compliance.jsonl --- Every PreToolUse hook decision.

- /audit/publish.jsonl --- Every publish event (Webflow or equivalent).

- /audit/citation-scores.jsonl --- Every extractability scoring run.

**Event schema:**

{

\"schema_version\": \"1.1\",

\"timestamp\": \"2026-04-21T15:47:12.342Z\",

\"event_type\": \"compliance_decision\",

\"slug\": \"tebra-vs-athenahealth\",

\"actor\": {

\"type\": \"hook\",

\"identifier\": \"pre-tool-use-compliance.sh\",

\"version\": \"0.1.0\"

},

\"decision\": \"allow\",

\"reason\": \"all 2 medical claims have approved sources\",

\"metadata\": {

\"claims_checked\": 2,

\"claims_sourced\": 2,

\"claims_flagged\": 0,

\"source_ids\": \[\"src_tebra_product_overview_2026\",
\"src_klas_ehr_pricing_2026\"\],

\"tool_call\": \"git commit -m \'draft: tebra vs athenahealth v0.1\'\"

}

}

**Event type enum:**

- compliance_decision --- PreToolUse hook allow/ask/deny.

- publish_success, publish_failure --- Webflow publish outcomes.

- citation_score --- Extractability scoring run.

- refresh_triggered --- Refresh-auditor subagent run.

- brief_created, draft_created --- Creation events for velocity
  tracking.

- source_added, source_expired --- Source registry lifecycle events.

Validation rules:

- Every event MUST have schema_version, timestamp (ISO 8601 with
  milliseconds, UTC), event_type, actor.type, actor.identifier.

- compliance_decision events MUST include metadata.claims_checked,
  metadata.claims_sourced, metadata.claims_flagged.

- publish_success events MUST include metadata.published_url,
  metadata.webflow_item_id.

## 8. Subagent output contract

Every subagent returns a structured response to the main agent. Format
is JSON inside a fenced code block, parsed by the main agent to surface
a clean summary to the user.

{

\"schema_version\": \"1.1\",

\"subagent\": \"brief-author\",

\"status\": \"success\",

\"artifacts\": \[

{

\"type\": \"brief\",

\"path\": \"briefs/tebra-vs-athenahealth.json\"

}

\],

\"external_actions\": \[

{

\"type\": \"asana_task_created\",

\"id\": \"1234567890\",

\"url\": \"https://app.asana.com/0/\...\"

}

\],

\"summary_for_user\": \"Brief ready at
briefs/tebra-vs-athenahealth.json. Asana task #1234 created and assigned
to PMM for review. Ready for /draft tebra-vs-athenahealth.\",

\"warnings\": \[\],

\"errors\": \[\]

}

**Status enum:** success, partial_success, failure, blocked_by_hook.

The summary_for_user field is what the user sees; everything else is for
programmatic chaining. Failure responses MUST populate errors\[\] with
actionable information.

## 9. Configuration contracts

**.mcp.json** --- Streamable HTTP servers and stdio servers. Secrets are
NEVER in this file; they\'re in shell env vars referenced by server
config. Full example in RUNBOOK.md.

**.claude/settings.json** --- Project-level Claude Code config: hook
registration, permission rules, default model, cache TTL pinning. Hook
paths are relative to repo root. Permission rules follow the Claude Code
settings spec; all tool use within the repo is auto-allowed, Bash
commands outside the repo default to ask.

**Skill frontmatter** (SKILL.md YAML):

\-\--

name: bofu-comparison-page

description: \|

Writing a BOFU competitor comparison page for B2B SaaS, with
feature-parity table,

pricing comparison, honest tradeoffs section, testimonials. Invoke when
the user or

the draft-writer subagent references asset_type=comparison, or when
creating

competitor comparison content.

version: \"0.1.0\"

disable-model-invocation: false

\-\--

**Subagent frontmatter** (\<subagent\>.md YAML):

\-\--

name: brief-author

description: \|

Generates structured content briefs from query clusters. Pulls signal
from Search

Console, GA4, Firecrawl, Exa. Writes JSON brief and creates Asana task.
Invoke via

/brief slash command or when the main agent needs a brief for downstream
drafting.

tools:

\- mcp\_\_search-console\_\_\*

\- mcp\_\_ga4\_\_\*

\- mcp\_\_firecrawl\_\_\*

\- mcp\_\_exa\_\_\*

\- mcp\_\_asana\_\_\*

\- Read

\- Write

model: claude-sonnet-4-6

\-\--

## 10. Schema evolution

Every schema in this document carries schema_version. Breaking changes
require:

1.  New schema version (e.g., 1.0 → 2.0).

2.  Migration script in scripts/migrations/v1_to_v2\_\<entity\>.py that
    transforms old-format files to new format.

3.  Dual-read support in consumers for at least one minor version.

4.  Entry in RESEARCH_GAPS_AND_DECISIONS.md documenting the change,
    rationale, and migration guidance for freelancers.

No silent schema changes. No \"just update the field and everything will
work.\" Every touch of these contracts is a deliberate, auditable event.

This is the full set of data contracts v1 requires. If you can serialize
it, validate it with Pydantic, and roundtrip it through git, it\'s in
this file. If it\'s not in this file, it\'s not part of v1.
