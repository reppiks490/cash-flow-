# RRE-04 — HVAC pilot measurement specification (pre-authorization)
**State:** proposed measurement protocol, not a running pilot. All present examples are synthetic. No outreach, customer data, live integrations, or billing authorized.

## Observation unit and provenance
Use a unique inquiry ID within a tenant and a defined 30-day observation window. Preserve original inbound timestamp, channel, source, deduplication decision, qualification rule version, review decision and reviewer identity only in future authorized private storage. An inquiry can appear in multiple funnel stages but is counted **once per stage**, never as multiple sales. Keep an immutable event history and distinguish source observation from operator assertion. No public GitHub customer identifiers.

## Metric contract (future authorized pilot)
| Metric | Numerator | Denominator / window | Evidence and exclusions |
|---|---|---|---|
| Eligible inquiry rate | Distinct inquiries with documented eligibility | All distinct inbound inquiries in cohort | Exclude duplicates, opt-outs, unknown permission from eligible count; report unknown separately |
| Review coverage | Eligible inquiries reviewed by authenticated operator | Eligible inquiries | Draft generation alone is not review |
| Draft approval rate | Drafts explicitly approved by authenticated operator | Drafts presented for review | Approval is not sending; no autonomous sends |
| Confirmed follow-up rate | Provider-confirmed deliveries tied to approved drafts | Approved drafts eligible for delivery | Do not equate queued or attempted sends with delivery; suppression overrides approval |
| Confirmed appointment rate | Provider-verified unique booked appointments | Eligible inquiries | Mock appointments count as zero; cancellations shown separately |
| Paid-job conversion | Distinct eligible inquiries linked to completed paid jobs | Eligible inquiries | Requires reconciled invoice and payment; quotes and booked jobs do not qualify |
| Attributed recovered revenue | Net paid receipts with documented attribution and refund adjustments | Currency sum per cohort | Never infer from estimate face value or self-reported bookings |
| RRE recurring net | Collected RRE subscription receipts minus refunds, processing, infrastructure, support, acquisition and other explicitly defined costs | Calendar month | Separate contractor recovered revenue from RRE vendor revenue; tax treatment must be stated |

Each reported fraction requires numerator, denominator, cohort start/end, timezone, as-of timestamp, provenance source, unknown count and confidence/verification label. A zero denominator yields **N/A**, never 0% or 100%. Late-arriving refunds and chargebacks require restatement with a revision timestamp. An empty source is **unavailable**, not evidence of zero real-world activity.

## Evaluation design and decision gate
Before an approved pilot, freeze inclusion rules and define a comparable baseline cohort (seasonality, channel mix, service territory and staffing considered). Prefer contemporaneous comparison groups where lawful and feasible; otherwise explicitly label before/after findings observational and confounded. Report absolute counts, percentage-point changes and uncertainty, not guaranteed uplift. Never use synthetic fixtures as baseline conversion evidence.

Proposed go/no-go review: (1) QA confirms tenant isolation, opt-out enforcement, authenticated approval, private retention and integration audits; (2) owner authorizes specific customer, channels, costs and contracts; (3) the pilot's pre-registered primary metric has complete denominator and verifiable event evidence; (4) operational errors, complaints and suppression breaches are reviewed before any scale decision. **No numerical success threshold is validated yet**; set thresholds with the owner before collecting data.

## Financial separation and target sensitivity
At a hypothetical $700 monthly subscription, five paying accounts imply $3,500 billed **before** refunds, uncollected balances, fees and operating expenses. $2,500 monthly net requires at least $2,500 *actually collected less all defined costs*; with $3,500 collected and no refunds, allowable total monthly costs would be at most $1,000. This is arithmetic, **not** a forecast. Do not combine a contractor's recovered-job revenue with RRE subscription receipts. Track customer acquisition costs and support time even if initially unpaid; disclose owner labor valuation separately.

## Preflight evidence packet for future authorized pilot
Record only in approved private systems: written scope and DPA/privacy review; tenant owner and access permissions; consent/opt-out provenance; signed commercial terms and cancellation/refund policy; event-schema version; reconciliation method for provider delivery, booking and receipts; support escalation; retention/deletion controls; QA exact-head checks; owner release decision. Until these exist, demo only.

## Source boundaries
This document extends `commercial/PILOT_OFFER_AND_DISCOVERY.md` and issue #26. It does not supersede the product ledger or authorize outreach. PR #141 independently covers buyer demo messaging; keep both reviewable without combining branches.
