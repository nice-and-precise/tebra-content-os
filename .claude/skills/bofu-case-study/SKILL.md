---
name: bofu-case-study
description: Use when writing a customer case study, success story, or outcome narrative featuring a healthcare practice using Tebra products.
---

# BOFU Case Study

## Overview

Case studies convert because they are the buyer's proxy — a reader sees a practice like theirs achieving outcomes they want. The structure enforces credibility: problem first, then mechanism, then quantified outcome. Every number must be sourced.

## Required Word Count and Structure

**Target:** 650–1,050 words (body, excluding frontmatter and block markup)

| Section | Word target | Purpose |
|---------|-------------|---------|
| Practice profile | 40–60 | Who the customer is (specialty, size, region) |
| The problem | 100–150 | What was failing and the cost of failure |
| Why Tebra | 60–80 | The decision — not a feature list, one core reason |
| The solution | 150–200 | What changed operationally (mechanism, not marketing) |
| The outcome | 150–250 | Quantified results with source citations |
| Quote | 30–50 | One customer quote that proves the outcome |
| CTA | 30–50 | One specific next step |

## PHI / PII Scrub Checklist

Before writing the outcome section, confirm:

- [ ] Practice name is approved for attribution (check brief's `sources[]` for a `customer_interview` source)
- [ ] No patient names, ages, diagnoses, or encounter data appear in the draft
- [ ] Geographic detail is no more specific than state-level unless practice approved city mention
- [ ] Provider name is only used if provider is the named spokesperson for the case study
- [ ] All statistics cited are aggregate (practice-level), not patient-level

See `healthcare-compliance` skill for full PHI detection rules.

## Quantified Outcomes Rule

Every outcome statement must include:

1. A specific number or percentage (not "significantly improved")
2. A timeframe ("within 90 days", "in the first billing cycle")
3. A source — either the customer_interview source or a corroborating third-party source

```html
<!-- block:proof id="proof-denial-reduction" cite="{customer_interview_source_id}" -->
Claim denial rate dropped from 9.2% to 3.8% within the first billing cycle after 
implementation — a 59% reduction in denied revenue.
<!-- /block -->
```

If the customer provided the data verbally in an interview, cite the interview source. If the practice won't provide numbers, use a benchmark from a registered third-party source and note it as representative.

## Testimonial Block

One customer quote per case study. The quote must:

- Come from the named spokesperson in the brief's `customer_interview` source
- Prove the outcome (not just express satisfaction)
- Be approved for use (confirmed in the source record's `approved_for_claims` field)

```html
<!-- block:testimonial id="testimonial-{practice-name}" cite="{customer_interview_source_id}" -->
"{Direct quote from customer}"
— {Name}, {Title}, {Practice Name}
<!-- /block -->
```

## Specialty and Persona Accuracy

- Use the correct specialty terminology for the practice (family medicine ≠ internal medicine ≠ primary care)
- Do not generalize outcomes to "all practices" — scope claims to the practice's specialty and size
- If the practice is multi-location, note whether the outcome applies to one location or all

## Common Mistakes

| Mistake | Fix |
|---------|-----|
| Outcome without a timeframe | Always specify when the result was measured |
| "Significantly" or "dramatically" | Replace with the actual number |
| Quote that expresses satisfaction only | Find a quote that names a specific outcome |
| Patient-level detail in the problem section | Rephrase to practice-level aggregate |
| Practice size omitted | Practice size is required in the profile — it sets the buyer's self-selection |
