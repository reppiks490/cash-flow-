# Revenue Recovery — Unit economics and measurement specification

**All figures are scenarios, not actual sales or forecasts.** Objective: verified recurring **$2,500/month net**, not gross billed.

## Scenario arithmetic
Let P = monthly subscription price; N = paying customers; C = per-customer monthly variable cost; F = fixed monthly costs (hosting, software, support base, insurance and overhead as applicable); A = monthly amortized acquisition/onboarding expense; R = refunds/chargebacks and payment fees. Define pretax operating net = N × (P − C) − F − A − R. Define after-tax net separately; never label pretax as after-tax.

| Hypothetical case | N | P | C/customer | F | A | R | Pretax operating net |
|---|---:|---:|---:|---:|---:|---:|---:|
| Lean | 5 | $700 | $75 | $350 | $150 | $125 | $2,500 |
| Cost pressure | 5 | $700 | $150 | $500 | $250 | $150 | $1,850 |
| Lower adoption | 4 | $700 | $75 | $350 | $150 | $100 | $1,900 |
| Six customers | 6 | $700 | $100 | $500 | $300 | $150 | $2,650 |

All inputs are invented modeling assumptions, not vendor quotes or measured cost. Five customers at $700 is **$3,500 gross billed**, not $3,500 collected and not $2,500 net automatically.

## Data dictionary and event provenance
- `lead_received`: accepted unique inbound lead, with tenant ID, source ID and immutable event ID.
- `lead_qualified`: qualified by documented rule, with rule version, evidence and unknowns; not a booked job.
- `draft_approved`: authorized operator approval with identity and timestamp; **not** proof of sending.
- `followup_sent`: verified provider delivery attempt with provider message ID, consent/suppression evidence and send timestamp; do not count drafts as sends.
- `appointment_booked`: verified calendar/CRM booking ID; a suggested slot is not booked.
- `job_closed`: verified completed work order, not a quote or booking.
- `payment_collected`: reconciled receipt ID, amount, currency, refunds and customer/work-order linkage.
- `recovered_revenue`: conservatively attributed *collected* job receipts with documented baseline and intervention linkage; distinguish correlation from causal uplift.
- `subscription_net`: actual subscription receipts less refunds, processing, infrastructure, support, acquisition and other included costs; report coverage and exclusions.

Deduplicate by tenant + immutable source event key, and by provider receipt ID for financial events. A stage transition must not create a second revenue entry. Reject cross-tenant references, unverified provider outcomes, missing currency and unmatched receipts.

## KPI definitions
- Inquiry qualification rate = qualified unique leads / eligible unique leads (report exclusions).
- Draft approval rate = approved drafts / drafts presented.
- Verified send rate = provider-confirmed sends / approved drafts; 0 when no delivery integration.
- Booking conversion = verified booked appointments / eligible leads, within fixed attribution window.
- Paid-job conversion = verified paid jobs / eligible leads; do not substitute estimates.
- Gross retention = retained subscription revenue / opening recurring subscription revenue; cohort-defined.
- Refund-adjusted subscription receipts = settled receipts − refunds − chargebacks.
- Operating margin = pretax operating net / collected subscription revenue; undefined when denominator 0.
- Payback = fully loaded acquisition expense / measured monthly contribution margin per retained customer; undefined without measured inputs.

Every dashboard metric must show measurement window, numerator, denominator, provenance, synthetic/live classification and missing-data status. **Current actual paying-customer count, payments and net profit are unverified/unknown because no commercial source-of-truth is connected. Synthetic ledgers contain no authenticated receipts.**

## Release and billing gates
Do not enable payment processor, invoicing, recurring charges, email/SMS or customer data collection until owner authorization, signed terms, QA approval and production security controls. Never place secrets or personal data in this public repository.
