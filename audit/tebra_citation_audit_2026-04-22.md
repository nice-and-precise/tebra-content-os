# Tebra.com Citation Extractability Audit

**Date:** April 22, 2026
**Scope:** 16 tebra.com URLs across product pages, positioning pages, case study, and The Intake blog
**Method:** Each page rendered via headless Chrome, scored on five extractability dimensions (schema markup, semantic hierarchy, Q&A patterns, proof attribution, answer-first structure) 0 to 5 each, total as arithmetic mean. Passing threshold: 3.5.
**Prepared by:** Jordan Damhof

---

## Headline

Not a single page in the audited set passes the 3.5 extractability threshold. The strongest pages cluster at 3.2. The weakest positioning pages score 0.4 and 0.8. The blog ships one generic schema type for every piece regardless of content format, and the product pages carry Q&A schema that does not match what appears in the DOM.

Fixing this does not require new content. The failures are structural: schema-type selection, DOM-to-schema parity, and a simple citation convention on long-form posts. All three are template-level fixes that propagate across the catalog.

---

## Scores

| URL | Total | Top gap |
|---|---|---|
| /features | 1.8 | No FAQ/QA/HowTo schema; answer pushed below first h2 |
| /ehr-software | 2.8 | Zero Q&A patterns in DOM, no FAQPage schema despite clearly asked questions in copy |
| /why-tebra/automate-practice | 0.4 | Zero JSON-LD of any kind; no h3s; no citations |
| /billing-payments | 3.2 | FAQPage schema present but 0 DOM Q&A pairs (schema/DOM disconnect) |
| /patient-experience | 3.2 | Same FAQPage-in-schema-but-not-DOM pattern |
| /pricing | 2.8 | No FAQPage or HowTo despite pricing tier comparison lending itself to both |
| /case-studies/psychiatrist-reduces-burnout... | 1.8 | No summary paragraph; h2 appears before first substantive paragraph; no outcome schema |
| /why-tebra | 0.8 | Zero JSON-LD; no proof citations; answer-first structure absent |
| /theintake/.../a-complete-beginners-guide-how-to-start-automating... | 3.2 | NewsArticle only, should be HowTo or FAQPage given step structure |
| /theintake/.../steps-to-start-a-new-medical-billing-company | 2.6 | Zero DOM Q&A pairs despite being a step guide; schema is NewsArticle, should be HowTo |
| /theintake/.../physician-burnout-by-specialty | 2.6 | Data-heavy piece with only 1 detected citation; no Dataset/MedicalWebPage schema |
| /theintake/.../nurse-practitioner-laws-by-state | 3.2 | 6,312 words, state-by-state reference, still NewsArticle; should be Dataset/Table/HowTo |
| /theintake/.../em-code-updates-what-you-need-to-know | 3.2 | No FAQPage schema despite 4 DOM questions and clear Q&A format |
| /theintake/.../tips-to-improve-patient-experience | 3.2 | HowTo fit perfect for "12 strategies" list; marked NewsArticle |
| /theintake/.../5-steps-every-medical-practice-must-take-now | 3.2 | Same HowTo miss |
| /theintake/.../medical-billing-upcoding | 3.2 | Compliance piece with 5 DOM questions, missed FAQPage schema |
| /theintake/.../what-multi-specialty-groups-expect-from-rcm-vendors | 3.2 | Same FAQPage miss |

---

## Findings

**1. No page passes the 3.5 threshold.** Only the two product pages carrying FAQPage schema reach 3.2. Every blog post on The Intake caps at 3.2 because they ship one generic NewsArticle type and nothing else.

**2. FAQPage schema is inverted on product pages.** /billing-payments and /patient-experience declare FAQPage in JSON-LD but render zero DOM paragraph, definition, or summary elements ending in a question mark. The questions exist only inside the schema blob. The on-page Q&A experience and the schema are disconnected: if an LLM or SERP parser trusts the DOM, it sees no Q&A; if it trusts the schema, the answer text may not match what a human reader sees.

**3. Answer-first structure is strong (80% of blog posts score 5/5) but proof attribution is universally weak.** Every single URL scored 0 or 1 on citation/reference count. Long-form pieces about physician burnout, EM code updates, and NP practice authority laws carry quantitative claims that beg for cite tags, footnotes, or reference anchors, and ship with none. This is the cheapest dimension to fix and the most valuable for LLM trust signals.

**4. The blog uses exactly one schema type (NewsArticle) for everything.** Step-by-step guides, state-by-state reference tables, multi-speaker Q&A pieces, and category pages all emit the same single @type. HowTo, FAQPage, Dataset, and MedicalWebPage are entirely absent from The Intake.

**5. Tebra has non-trivial content rot at the URL level.** /practice-management, /resources, and /resources/customer-stories all return a 404 shell (title "Page not found - Tebra", 186 words of boilerplate). A site-wide 404 sweep tied to external backlinks and internal nav would recover lost extractability at zero content cost.

**6. Hero positioning pages (/why-tebra, /why-tebra/automate-practice) are the weakest in the set** at 0.4 and 0.8. They carry no JSON-LD at all, no h3 hierarchy, and zero citations. These are the pages most likely to appear in a "what is Tebra" LLM query and they render as thin marketing shells to a parser.

---

## Three highest-leverage recommendations

**1. Add FAQPage JSON-LD plus matching DOM details/summary blocks to the top 5 product pages** (/features, /ehr-software, /billing-payments, /patient-experience, /pricing). /billing-payments and /patient-experience already declare FAQPage in schema. The fix there is to render the same questions and answers in the DOM as details elements so the schema matches visible content. That single change takes the two 3.2 product pages past 3.5, and cloning the pattern to the other three reaches 4.0 for the entire product nav in one sprint.

**2. Emit the correct schema type per blog template on The Intake.** Step guides (start-a-medical-billing-company, 12-patient-experience-strategies, 5-steps-value-based-payment, how-to-start-automating) should emit HowTo. The state-by-state NP laws piece should emit a Dataset with itemListElement per state. Compliance pieces with DOM questions (em-code-updates, upcoding, rcm-vendors) should carry FAQPage alongside NewsArticle. The blog uses a CMS: this is a template-level fix, not a per-post fix. Estimated effect: moves 8 of the 9 blog posts in this sample from 3.2 to 4.0+ simultaneously.

**3. Introduce a citation convention in long-form content and apply it to the 5 most data-heavy existing posts first.** Physician burnout by specialty, EM code updates, NP practice authority laws, 5 steps for value-based payment, and the upcoding piece all make quantitative claims with zero citation anchors, footnote elements, or reference containers. Adding 3 to 5 inline superscript footnote anchors with a references section at the bottom of each post takes proof attribution from 1.0 to 3.0 on those five pieces, and establishes a pattern for every new post going forward. This is the dimension LLMs explicitly search for when deciding whether to cite a source in an AI Overview.

---

## Failures and edge cases

- `tebra.com/practice-management` returned a 404 shell. Substituted `/why-tebra/automate-practice` as the closest topical equivalent.
- `tebra.com/billing` resolves to `/billing-payments` (audited the final URL).
- `tebra.com/patient-engagement` resolves to `/patient-experience` (audited the final URL).
- `tebra.com/ehr` 301 redirects to `/ehr-software`.
- `tebra.com/resources` and `tebra.com/resources/customer-stories` return 404 shells. The blog lives at `/theintake` and case studies at `/case-studies`; the `/resources` slug is dead across the nav.
- `tebra.com/blog` 301 redirects to `/theintake`.
- No direct competitor comparison page surfaces from the homepage nav or the first page of The Intake. The closest positioning asset is `/why-tebra`, used here as the comparison surrogate.

---

## Method note

The scorer was not modified for this audit. Dimensions and scoring rules are defined in `scripts/citation_score.py` in the source repo. Raw signal extraction and per-URL JSONL results are in `audit/citation-scores.jsonl`. Re-running the audit requires only the URL: `/audit <url>` invokes the pipeline end to end.
