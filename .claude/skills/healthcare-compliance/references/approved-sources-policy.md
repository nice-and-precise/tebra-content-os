# Approved Sources Policy

## Authority Tiers

Every source in `/sources/registry.json` is assigned one of four authority tiers. The tier determines what claims the source can support.

| Tier | Source types | What it can support |
|------|-------------|---------------------|
| **Tier 1 — Primary** | Tebra internal docs, signed customer interview transcripts | Product capabilities, customer-attested outcomes |
| **Tier 2 — Research** | KLAS reports, MGMA data, peer-reviewed studies, CMS/FDA publications | Industry benchmarks, regulatory facts, clinical claims |
| **Tier 3 — Secondary** | Trade press (Modern Healthcare, Health Affairs), analyst commentary | Context, framing, trend statements only — not clinical claims |
| **Tier 4 — Excluded** | Competitor marketing materials, Wikipedia, anonymous forums | Never use for any claim |

## Source Vetting Criteria (before registration)

A source may be registered in `/sources/registry.json` only if:

1. **Retrievable.** The source has a stable URL, DOI, or file path that can be fetched and verified.
2. **Dated.** The source has a clear publication or last-updated date.
3. **Not expired.** Clinical and regulatory sources expire after 3 years unless the underlying guidance has not changed. Check `expires_at` in the source record.
4. **Scope-matched.** The source's geographic scope matches the claim (a US CMS rule cannot source a claim about UK practices).
5. **PHI-free.** The source does not contain un-redacted patient data.

## Claim-Source Matching Rules

- A **Tier 1 internal doc** can support product capability claims ("Tebra processes X in Y steps") but not clinical outcome claims.
- A **Tier 2 research source** is required for any claim about clinical outcomes, denial rates, revenue cycle benchmarks, or regulatory compliance.
- A **customer interview** supports only what the customer personally attested. If the customer says "we reduced denials," that is attested. If they say "all practices reduce denials with Tebra," that is not attested.
- A **CTA or case study testimonial** is not a source. Testimonials are supported by their underlying interview source.

## Source Expiry and Refresh

Check `expires_at` before using any source in a new draft. Sources expired at draft time will cause the compliance hook to fail.

If a source is expired but the underlying data is still accurate, update the source record with a new `expires_at` (add 1 year) and add a `notes` field explaining why the refresh was approved without a new document.
