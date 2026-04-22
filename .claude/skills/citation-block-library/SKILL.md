---
name: citation-block-library
description: Use when inserting any modular content block into a Tebra draft — quick-answers, comparison tables, proof blocks, ROI snippets, FAQ schema, implementation steps, or testimonials. Invoke whenever another BOFU skill is active.
---

# Citation Block Library

## Overview

Seven modular block types form the structural vocabulary of every Tebra content draft. Each block is a self-contained unit with a unique ID, an HTML-comment delimiter, and one or more cite attributes. Blocks are composable: a single draft may use all seven.

## Block Types and When to Use

| Block | When to insert | Required cite? |
|-------|---------------|----------------|
| `quick-answer` | Always first — 2-4 sentence direct answer to the primary query | No |
| `comparison-table` | Comparison asset types; one or more feature-parity tables | No |
| `proof` | After any assertion that needs a source; one block per claim | **Yes** |
| `roi-snippet` | ROI calculator assets; after any quantified value calculation | **Yes** |
| `faq-schema` | Second-to-last block in every BOFU asset | No |
| `implementation-steps` | Implementation guides; every numbered procedural sequence | **Yes** (per step) |
| `testimonial` | Optional; use when a customer quote directly proves a claim | **Yes** |

## Canonical Ordering Rule

For comparison assets, blocks MUST appear in this order:

1. `quick-answer` (top of page)
2. `comparison-table`
3. `proof` blocks (interleaved after relevant table rows)
4. `roi-snippet` (if applicable)
5. `testimonial` (if applicable)
6. `faq-schema` (second-to-last)
7. CTA (last — plain prose, not a block)

## Block ID Naming

IDs must be unique within a draft. Use kebab-case with a type prefix:

```
quick-answer-1
comparison-table-main
proof-claim-denial-rate
roi-snippet-annual-savings
faq-schema-1
implementation-step-1
testimonial-dr-smith
```

## Block Delimiter Format

```html
<!-- block:{type} id="{id}" schema="{SchemaType}" cite="{source_id}" -->

## {Section heading}

{Block content}

<!-- /block -->
```

- `schema` attribute is required for `comparison-table` (use `"Product"`) and `faq-schema` (use `"FAQPage"`)
- `cite` attribute is required for `proof`, `roi-snippet`, `implementation-steps`, and `testimonial`
- `source_id` must match a registered source in `/sources/registry.json`

## Templates

Template files live in `references/` alongside this SKILL.md:

- `references/quick-answer.md`
- `references/comparison-table.md`
- `references/proof.md`
- `references/roi-snippet.md`
- `references/faq-schema.md`
- `references/implementation-steps.md`
- `references/testimonial.md`

## Common Mistakes

| Mistake | Fix |
|---------|-----|
| Missing `cite` on a proof block | Every proof block requires `cite="{source_id}"` |
| Duplicate block IDs | Append `-2`, `-3` suffixes; IDs must be unique per draft |
| `faq-schema` placed first | FAQ always second-to-last; quick-answer always first |
| Inline `source_id` not in registry | Run `python scripts/compliance_check.py` before commit |
| CTA in a block wrapper | CTAs are plain prose — no block delimiter |
