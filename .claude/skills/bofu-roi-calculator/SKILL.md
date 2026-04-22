---
name: bofu-roi-calculator
description: Use when building an ROI calculator, cost-savings estimator, or any content that quantifies financial or operational efficiency outcomes for Tebra prospects.
---

# BOFU ROI Calculator

## Overview

ROI calculators convert because they make an abstract value claim concrete and personalized. The buyer enters their own numbers and sees their own potential gain — that's more persuasive than any stat Tebra could publish. The system produces a React artifact that the engineering team forks into production.

## Required Structure

Every ROI calculator page includes:

1. **quick-answer block** — The headline value proposition: "Practices using Tebra recover $X/month in previously denied claims."
2. **React calculator artifact** — The interactive widget. See artifact pattern below.
3. **roi-snippet block** — A static version of the calculation with a representative example. Required for LLM extraction (React artifacts are not crawlable by LLMs).
4. **"How this calculator works" block** — Explains the formula, data sources, and assumptions. Required for trust and LLM extractability.
5. **faq-schema block** — Four Q&A pairs addressing "how accurate is this?", "what does this include?", "what assumptions does it make?"
6. **CTA** — Single specific next step.

## React Artifact Pattern

```tsx
// ROI Calculator artifact
// Props: practiceSize (number), specialty (string)
// Returns: estimated annual savings

const inputs = {
  monthlyEncounters: 0,   // user fills
  avgClaimValue: 0,        // user fills
  currentDenialRate: 0,    // user fills (default: 7%)
};

const outputs = {
  recoveredPerMonth: inputs.monthlyEncounters * inputs.avgClaimValue * (inputs.currentDenialRate - 0.02),
  annualSavings: /* recoveredPerMonth */ * 12,
};
```

- Inputs must have sensible defaults derived from industry benchmarks in a registered source.
- Every default value must have a `cite` comment referencing a `source_id` in `/sources/registry.json`.
- Output formula must be disclosed in the "How this calculator works" block.

## ROI-Snippet Block (Static Version)

```html
<!-- block:roi-snippet id="roi-example" cite="{source_id}" -->
## Example: 3-physician independent practice

Monthly encounters: 450
Average claim value: $180
Industry average denial rate: 7% (source: {cite_as})
Tebra average denial rate: 4.1% (source: {cite_as})

Estimated monthly recovery: $2,511
Estimated annual recovery: $30,132

<!-- /block -->
```

The static roi-snippet uses representative (not personalized) values. It is not a guarantee.

## "How This Calculator Works" Block

Required for every ROI calculator page. Include:

- The formula used (plain language, then equation)
- The source for each input default
- What the calculator excludes (implementation costs, training time, etc.)
- A disclaimer: "Individual results vary. This estimate is based on industry benchmarks, not a guarantee."

## Schema-Tagged FAQ

Four required Q&A pairs for the `faq-schema` block:

1. "How accurate is this calculator?" — Address the data source and the margin of error.
2. "What does the ROI estimate include?" — List the included savings categories.
3. "What is not included?" — List excluded costs.
4. "How does Tebra reduce claim denials?" — Mechanism explanation; cite a registered source.

## Common Mistakes

| Mistake | Fix |
|---------|-----|
| Calculator with no static roi-snippet | LLMs cannot render React; always include the static version |
| Default values with no source citation | Every default needs a `cite` comment and a source in registry |
| No "how this works" section | Required for trust and LLM extraction |
| Outputs presented as guarantees | Always include the disclaimer in the "how this works" block |
| FAQ about calculator mechanics only | Include at least one FAQ about the underlying product claim |
