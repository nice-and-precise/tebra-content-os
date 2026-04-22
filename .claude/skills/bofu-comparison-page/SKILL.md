---
name: bofu-comparison-page
description: Use when writing a competitor comparison page, feature-parity table, or side-by-side analysis of Tebra versus another EHR or practice management platform.
---

# BOFU Comparison Page

## Overview

Comparison pages are the highest-converting BOFU asset type for independent practice buyers. They work because buyers at this stage are already evaluating alternatives — a well-structured comparison page meets them where they are and answers their decision criteria directly.

## Required Structure

Every comparison page must include these blocks in this order:

1. **quick-answer block** — The direct answer: "Tebra is better for X because Y." One to four sentences. Written for LLM extraction.
2. **comparison-table block** — Feature-parity table with Tebra as the left column.
3. **proof blocks** — One per sourced differentiator. Each links to a registered source.
4. **honest-tradeoff paragraph** — One paragraph acknowledging where the competitor is stronger. See below.
5. **faq-schema block** — Four to six Q&A pairs that address the real objections.
6. **CTA** — One specific next step. No stacked CTAs.

## Comparison Table Rules

```markdown
| Feature | Tebra | {Competitor} |
|---------|-------|--------------|
| {Feature} | {Tebra capability} | {Competitor capability} |
```

- Use `✓`, `✗`, or a specific value — never "Yes/No" text.
- Limit to 8–12 rows. More rows dilute the differentiators.
- Every Tebra `✓` that is a medical claim must have a `proof` block with `cite=`.
- `schema="Product"` is required on the `<!-- block:comparison-table -->` delimiter.

## Honest-Tradeoff Paragraph

Every comparison page includes one paragraph that acknowledges a competitor strength:

> "If your practice needs [specific competitor strength], [competitor] may be a better fit. Tebra's strength is [differentiator] — for practices prioritizing [outcome], that difference matters."

This is not weakness — it is credibility. Buyers who see no tradeoffs trust the page less. Include the honest-tradeoff paragraph between the proof blocks and the FAQ.

## Pricing Block (when applicable)

If pricing data is available in `/sources/registry.json`:

```html
<!-- block:roi-snippet id="pricing-comparison" cite="{source_id}" -->
## Cost comparison
{Tebra pricing context vs competitor}
<!-- /block -->
```

Do not include pricing data that is not sourced. If no pricing source exists, omit this block.

## FAQ Pattern

Four to six questions drawn from the brief's `target_intent.query_cluster`. For comparison pages, these typically address:

- "Which is easier to implement?"
- "What does migration look like?"
- "How do support models compare?"
- "Is there a long-term contract?"

See `references/comparison-example.md` for a full annotated example page.

## Word Count and Tone

- **Target:** 900–1400 words (body, excluding block markup)
- **Lead with outcomes, not features.** "Independent practices reduce claim denials" before "Tebra's PM module."
- **Avoid the word "better."** Show the data; let readers conclude.
- **Competitor respect rule.** Never mock or editorialize. State the facts of the comparison.

## Common Mistakes

| Mistake | Fix |
|---------|-----|
| Missing honest-tradeoff paragraph | Add one — it improves conversion and credibility |
| Comparison table with >12 rows | Cut to the 8 rows that matter most to the buyer persona |
| Pricing block without a source | Omit pricing or register the source first |
| FAQ questions the buyer wouldn't ask | Pull questions from the brief's query_cluster |
| CTA before the FAQ | FAQ goes second-to-last; CTA is always last |
