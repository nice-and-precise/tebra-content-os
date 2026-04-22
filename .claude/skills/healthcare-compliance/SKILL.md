---
name: healthcare-compliance
description: Use when drafting or reviewing any Tebra content that mentions clinical outcomes, treatment efficacy, patient data, competitor medical claims, PHI, or FDA/AMA/HIPAA-regulated subject matter.
---

# Healthcare Compliance

## Overview

This skill guides in-flight self-checking during draft writing. The PreToolUse hook (`scripts/compliance_check.py`) enforces the same rules deterministically at commit time — this skill helps avoid generating claims that will be blocked there.

## Medical Claim Detection

A medical claim is any statement that asserts, implies, or quantifies a health outcome. Flag any sentence matching these patterns before writing:

- Percentage + clinical metric: "reduces A1C by X%", "lowers readmission rate"
- Mortality or morbidity language: "reduces deaths", "prevents complications"
- Diagnostic accuracy: "detects X% of cases", "misses fewer diagnoses"
- Survival or prognosis framing: "improves survival", "extends life"
- Regulatory body name + product: "FDA-approved", "CMS-compliant" (must be sourced)

**Every medical claim requires a registered source.** Check `/sources/registry.json` before writing. If no source exists, write around the claim or request source registration.

## PHI Scrub Rules

Remove or redact any content matching these patterns before committing a draft:

| Category | Examples | Action |
|----------|----------|--------|
| Patient names | Full name, initials + DOB combination | Delete or replace with `[PATIENT]` |
| MRN / encounter IDs | Any numeric ID pattern from a clinical system | Delete |
| DOB or age + diagnosis | "65-year-old with diabetes" | Generalize: "older adult patient" |
| Geographic identifiers | ZIP, city + condition combination | Drop geographic detail |
| Provider name + patient | Any provider linked to a specific patient record | Redact provider name |

See `references/phi-detection-rules.md` for full regex patterns.

## FDA / AMA / HIPAA Guardrails Summary

| Rule | What it means in practice |
|------|--------------------------|
| **FDA off-label claims** | Do not claim a Tebra product treats, diagnoses, or monitors a specific condition unless that claim appears in an FDA-cleared source |
| **AMA clinical guidelines** | Do not paraphrase AMA guidelines as Tebra recommendations without an explicit citation |
| **HIPAA safe harbor** | Use only the 18 de-identification categories from `references/phi-detection-rules.md`; do not invent "anonymized" redactions |
| **No testimonial-as-outcome** | A customer quote ("we saw improvement") is not a clinical claim; a statistic derived from it is |

## Self-Check Before Writing a Claim

1. Does this sentence make a health-outcome assertion?
2. Is there a source in `/sources/registry.json` that supports it exactly?
3. Does the draft's `claims_cited[]` block reference that source_id?

If any answer is no — rephrase as a practice-efficiency claim, or omit and flag for source registration.

## References

- `references/approved-sources-policy.md` — authority tiers and source vetting criteria
- `references/banned-claim-patterns.md` — regex list of patterns that will trigger the compliance hook
- `references/phi-detection-rules.md` — HIPAA safe harbor categories and regex patterns

## Common Mistakes

| Mistake | Fix |
|---------|-----|
| Citing a source not in registry | Register source first; source_id in draft must resolve |
| Using a customer quote as a clinical stat | Quotes prove sentiment; statistics need a study source |
| Writing "HIPAA-compliant" without a source | Link to a registered regulatory document or remove |
| Borrowing competitor's FDA claim for Tebra | Tebra's clearance is independent; source Tebra's own |
