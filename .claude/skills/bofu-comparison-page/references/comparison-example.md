# Annotated Comparison Page Example

This is a stripped-down reference implementation using an anonymized non-healthcare SaaS comparison. It shows the block structure, honest-tradeoff paragraph placement, and canonical ordering. Replace the placeholder content with Tebra-specific data.

---

<!-- block:quick-answer id="quick-answer-1" -->
## The short answer

Acme is the better choice for small independent service businesses because it includes built-in scheduling, billing, and client management in one platform — without requiring three separate integrations. Rival charges for each module separately and requires a third-party payroll integration that small teams frequently misconfigure.

<!-- /block -->

<!-- block:comparison-table id="comparison-table-main" schema="Product" -->
## Feature comparison: Acme vs. Rival

| Feature | Acme | Rival |
|---------|------|-------|
| Scheduling | ✓ Included | ✗ Add-on ($29/mo) |
| Client billing | ✓ Included | ✓ Included |
| Payroll | ✓ Included | ✗ Third-party integration required |
| Mobile app | ✓ iOS + Android | ✓ iOS only |
| Onboarding support | ✓ Dedicated specialist | ✗ Self-serve only |
| Contract required | ✗ Month-to-month | ✓ 12-month minimum |
| Starting price | $99/mo | $79/mo |

<!-- /block -->

<!-- block:proof id="proof-onboarding-support" cite="src-acme-internal-2025" -->
Acme assigns every new account a dedicated onboarding specialist for the first 60 days. According to Acme's 2025 customer success report, practices using the onboarding program reach full operational use in an average of 14 days — compared to the 31-day industry average for self-serve SaaS onboarding.

<!-- /block -->

<!-- HONEST TRADEOFF — Plain prose, not a block -->
## Where Rival has an edge

Rival's starting price is $20/month lower than Acme's base plan. For a solo operator who doesn't need payroll or a mobile app, Rival's lower price is a legitimate reason to choose it. Acme's value is in eliminating the integration burden — if you already have a payroll tool you trust and don't mind maintaining the connection, Rival's price advantage is real.

<!-- block:testimonial id="testimonial-owner" cite="src-acme-interview-2025" -->
"We switched from Rival when our payroll integration broke for the third time during a busy period. The switch took two weeks and we haven't had a payroll issue since."

— Sarah K., Owner, Eastside Services
<!-- /block -->

<!-- block:faq-schema id="faq-schema-1" schema="FAQPage" -->
## Frequently asked questions

### How long does it take to switch from Rival to Acme?

Most businesses complete the switch in two to four weeks. Acme's onboarding team handles data migration from Rival's standard export format. The migration itself takes one business day; the remaining time is staff training.

### Is there a long-term contract with Acme?

No. Acme is month-to-month on all plans. You can cancel at the end of any billing period.

### Does Acme integrate with QuickBooks?

Yes. Acme connects to QuickBooks Online via a native integration. Setup takes about 20 minutes and does not require a third-party connector.

### What happens to our data if we cancel?

You can export your full client and billing history in CSV and PDF formats at any time. Acme retains your data for 90 days after cancellation in case you change your mind.

<!-- /block -->

**Ready to see if Acme fits your workflow?** [Start a 14-day free trial — no credit card required.]

---

## Structural Notes (for Tebra implementation)

- The honest-tradeoff paragraph is **plain prose**, not wrapped in a block.
- It appears **between proof blocks and the testimonial** — after you've established credibility.
- The FAQ questions mirror real buyer search queries, not internal FAQs.
- The CTA is a single sentence. No stacked CTAs.
- Total word count in this example: ~480 words. A real Tebra comparison page should target 900–1,400 words.
