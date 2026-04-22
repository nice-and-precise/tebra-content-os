---
name: bofu-implementation-guide
description: Use when writing a step-by-step implementation or onboarding guide for a Tebra product feature, integration, or workflow change.
---

# BOFU Implementation Guide

## Overview

Implementation guides convert BOFU prospects who have mentally bought in but are worried about the implementation burden. The goal is to make the path from decision to live-in-production feel short, concrete, and supported.

## Required Structure

1. **quick-answer block** — "Here's what implementation looks like: {X steps, Y days, Z prerequisites}."
2. **Prerequisites section** — What the practice needs before starting (systems, access, roles). No fluff.
3. **Step-numbered implementation blocks** — One `implementation-steps` block per major phase.
4. **Estimated time per step** — Every step includes a realistic time estimate.
5. **faq-schema block** — Four Q&A pairs on support, rollback, data migration, and training.
6. **CTA** — One specific next step (book an implementation call, start free trial, contact support).

## Step-Numbered Block Pattern

Each step in an `implementation-steps` block must:

- Be a complete action in the imperative ("Configure your billing profile" not "Billing profile configuration")
- Include an estimated time
- Cite a source if it references a product capability or a compliance requirement

```html
<!-- block:implementation-steps id="implementation-step-{n}" cite="{source_id}" -->
## Step {n}: {Action in imperative}

**Time:** {estimate}

{What the user does. One clear action per step. If there are sub-steps, 
use a numbered list inside the block.}

**What to expect:** {What happens after this step — the feedback signal 
that tells the user they did it right.}
<!-- /block -->
```

## Step Count and Phase Grouping

- **Total steps:** 5–10. More than 10 suggests the guide should be split into two guides.
- **Phase grouping:** If steps span more than two roles (e.g., IT + billing + clinical), group steps by phase with a phase heading between blocks.
- **Prerequisites are not steps.** Prerequisites live in their own section before the first implementation block.

## Citations API Block-Indexing Rule

Every `implementation-steps` block must have a `cite` attribute pointing to a registered internal_doc source that verifies the described product behavior. This is not optional — the product-truth subagent uses these citations to verify accuracy during refresh audits.

If the step describes a UI interaction and no source exists yet, use the placeholder `source_id: "pending-source-registration"` and flag in the draft's `warnings[]` field.

## Time Estimates

Use realistic estimates from the brief's source material or from customer_interview sources. If no data exists:

- Simple configuration step: "5–10 minutes"
- Data import or migration: "1–4 hours depending on record volume"
- Training a staff member: "30–60 minutes per role"

Do not use vague timeframes ("quickly", "soon", "a few minutes"). Do not underestimate to make implementation seem easier than it is — that creates churn.

## FAQ Pattern for Implementation Guides

Four Q&A pairs covering:

1. "What happens to our existing data during migration?"
2. "What if something goes wrong mid-implementation?"
3. "Do we need IT support to complete this?"
4. "How long until the team is fully trained?"

## Common Mistakes

| Mistake | Fix |
|---------|-----|
| Steps in passive voice | Rewrite in imperative: "Import your patient records" |
| No time estimate per step | Every step needs a realistic time estimate |
| Prerequisites buried in step 1 | Pull prerequisites into their own section before the steps |
| Steps exceeding 10 | Split into two guides by phase or audience |
| Missing `cite` attribute on a step | Use `"pending-source-registration"` and add to warnings |
