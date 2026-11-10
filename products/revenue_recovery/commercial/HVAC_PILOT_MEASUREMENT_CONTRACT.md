# HVAC recovery pilot — measurement and approval contract

**Classification:** proposed, synthetic-only commercial operating specification. No customers, receipts, messages, integrations, or proven conversion uplift. Owner approval is required before outreach or pilot activation. Tracks RRE-04 (#26).

## Offer and boundaries

Hypothesis: an HVAC service business may benefit from identifying missed *inbound* quote/service inquiries, preparing reviewable follow-up drafts, and reconciling outcomes against its existing CRM. This is not a promise of incremental jobs or recovered revenue. Pricing hypothesis: $700 per tenant per month, not an accepted offer. Trial length, support hours, response SLA, data-retention period, refund terms, and subscription cancellation policy remain **unapproved** and must be signed off before any customer-facing pilot. No automated contact, dispatch, appointment booking, or payment processing is included in the synthetic demo.

## Buyer discovery (questions only; no solicitation authorized)

Interview the owner or operations manager **only after explicit authorization** about missed-call/inquiry volume, existing CRM, response delays, quote follow-up responsibility, consent evidence, job-value distribution, operational staffing, and current monthly software spend. Record aggregate answers only in an approved private system after a privacy review; never put prospect names, contact details, transcripts, or CRM exports in public GitHub. Do not assert a market size or willingness-to-pay without actual consented discovery evidence.

## Measurement dictionary

All event counts are tenant-scoped, period-scoped, unique by stable idempotency key, and accompanied by source, timestamp, synthetic flag, and evidence status. Missing or unverifiable evidence yields **unknown**, not zero or success.

| Metric | Numerator / definition | Required evidence | Do not infer |
| --- | --- | --- | --- |
| Inbound inquiries | Unique received inquiry IDs within period | Approved source receipt | Reachable or permissioned |
| Eligible leads | Unique inquiries with recorded qualification basis and contact-permission decision | Qualification + consent/suppression evidence | Contact permission from score alone |
| Drafts generated | Unique draft IDs with provenance | Local draft audit | Sent messages |
| Drafts approved | Unique drafts approved by identified authorized operator | Approval audit with timestamp | Delivery |
| Follow-ups delivered | Unique provider-confirmed deliveries, excluding failures | Provider delivery acknowledgement | Delivery from draft/approval |
| Appointments booked | Unique confirmed appointment IDs | Calendar/CRM confirmation | Booking from proposed slot |
| Jobs closed | Unique completed jobs with distinct job IDs | Authorized CRM job-state record | Payment |
| Collected attributable revenue | Sum of nonduplicated, settled receipt amounts minus linked refunds, with documented attribution window and source | Payment processor or reconciled ledger receipt and attribution evidence | Receipts from booked jobs or quoted amounts |
| Subscription net profit | Recognized collected subscription revenue minus refunds, processing fees, hosting, inference, support labor, acquisition, taxes where applicable, and other period expenses | Reconciled accounting records | Profit from modeled contribution |

**Attribution policy:** specify window and matching rule before any real pilot; maintain source lead ID -> job ID -> receipt ID chain, prohibit double counting, record competing channels, and classify ambiguous receipts as unattributed. No causal uplift claim without a defensible comparison design. Report sample size, observation dates, missingness, and denominators alongside conversion rates; avoid ratios with zero denominators.

## Approval and activation gates

1. Product QA: isolated synthetic end-to-end test, tenant separation, authorization, suppression/consent, idempotency, recovery, and audit evidence signed off. Browser rehearsal must be independently executed; CI alone does not prove it.
2. Legal/privacy review: purpose limitation, lawful contact basis, applicable marketing rules, retention/deletion, security, and written service agreement. No imported customer data before approval.
3. Owner approval: explicit named authorization for each vendor, expenditure, deployment, data source, outreach channel, and billing activation. Default for every integration is **disabled**.
4. Pilot contract: agreed scope, SLA, operator responsibilities, pricing, cancellation, support limits, security terms, and no-results-guarantee language.
5. Financial proof: actual settled subscription receipts and complete period costs; otherwise display **verified net profit: not established**.

## Synthetic demo script (no external effects)

Use only bundled synthetic HVAC fixture IDs. Demonstrate local intake -> deduplication -> qualification evidence -> unsent draft -> explicit human-review state -> CRM dry-run -> appointment *unconfirmed* -> zero verified receipts. Show the provenance/status fields at every stage. Do not call an outbound provider, schedule an actual appointment, activate a subscription, or show hypothetical recovered job value as cash.

## Economics sensitivity (assumptions only)

At $700 per tenant/month and $75 variable monthly expense per tenant plus $500 fixed expense, five *hypothetical* tenants imply $3,500 gross and $2,625 operating contribution **before excluded expenses**. This is neither verified net profit nor a forecast. Customer acquisition, refunds, payment fees, taxes, owner compensation and other costs require separate evidence. The independent calculator proposed in draft PR #205 is not yet merged and must not be treated as an operational billing system.

## Open blockers and evidence labels

- **Verified:** this document specifies metrics and approval gates; no customer-facing action is authorized.
- **Unverified:** buyer demand, price acceptance, consented interviews, pilot contracts, provider integrations, confirmed bookings, settled receipts, net profit, and production readiness.
- **Blocked:** real outreach, real customer records, paid vendors, payments, and deployment until owner authorization and release approvals.
