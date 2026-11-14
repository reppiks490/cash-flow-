# RRE-04 — Closed-revenue and net-profit evidence contract (design only)

**Status:** proposed acceptance contract, not a live integration or verified financial report. **Data:** no customer records, payment events, or actual receipts. **Authority:** no billing, outreach, CRM writes, or deployment authorized. Tracks [RRE-04 #26](https://github.com/reppiks490/cash-flow-/issues/26).

## Two distinct economic perspectives

1. **RRE vendor subscription P&L:** customer subscription collections less refunds, chargebacks, processor fees, hosting, model inference, support, acquisition amortization and other attributable operating costs. The $2,500/month objective is **verified recurring net profit**, not billed revenue, estimated recovered HVAC jobs, bookings, or a tax-adjusted guarantee. The existing `scenario_calculator.py` is hypothetical arithmetic and never evidence of collections.
2. **HVAC buyer recovery attribution:** completed paid jobs that can be linked to an existing inquiry and a permitted, operator-approved follow-up. This is a *buyer outcome*, not RRE subscription revenue; never sum it into RRE profit or treat an invoice as a paid job. The buyer-side calculator is likewise hypothetical.

## Minimum evidence before any nonzero *verified* metric

| Metric | Required private evidence | Exclude |
|---|---|---|
| RRE subscription collections | Authenticated payment processor settled transaction, currency, tenant, immutable transaction ID, settlement time | Quote, invoice, authorization, test-mode transaction |
| RRE net profit | Above settlements minus reconciled refunds/chargebacks, processing fees, hosting, model, support, acquisition and other defined expenses for same month | Gross billings, unallocated or missing costs |
| HVAC completed paid job | Privately authenticated job completion + settled payment with refund status | CRM stage, scheduled appointment, signed estimate, synthetic fixture |
| Recovered job attribution | Unique lead source, consent/suppression decision, human-approved communication event, provider delivery proof, job/payment link and defensible comparison rule | Draft creation, send request, model suggestion, unverified correlation |

No proof of an event is not proof the event did not happen. Represent missing coverage as **unknown**, not zero. Zero is valid only for a defined, complete, reconciled observation window. Never expose identifiers, addresses, phone numbers, free-text messages, tokens or receipt payloads in public GitHub, logs or demo exports.

## Proposed private reconciliation rules (not implemented)

- Use one explicitly named accounting period, timezone, currency and cash-versus-accrual policy; for the initial goal use calendar-month **cash-settled, pretax operating net** with separately disclosed tax treatment. Do not silently compare a partial month to a full-month target.
- De-duplicate settlements/refunds by processor + immutable event ID; reverse a settlement through a linked refund/chargeback rather than overwriting history. Idempotent replay must not increase revenue.
- Link each subscription settlement to exactly one RRE tenant and period. Record refunds, processing fees and costs with their own evidence/provenance and effective dates. If cost coverage is incomplete, `verified_net_profit_usd = null`, not a positive estimate.
- A job may have multiple touchpoints but at most one credited paid-job amount in an attributed total. Reversals must adjust the same job. Distinguish `assisted` from `incremental`: neither a follow-up nor temporal association proves causality.
- Maintain separate **gross collections**, **net collections**, **operating expenses**, **pretax operating net**, **refunds**, **verified recovered buyer revenue**, and **unattributed/unknown** columns. Never aggregate buyer recovery into RRE vendor income.
- Enforce tenant isolation, immutable audit events, authenticated roles, retention/deletion policy, access logging and explicit owner/QA approval before real data collection or provider integration. Public synthetic dashboards must display `verified_receipts: null` until an authorized private evidence pipeline exists.

## Release acceptance cases for future implementation

1. A synthetic quote and mock booking produce **no** verified receipt, job revenue or profit.
2. Duplicate settlement events count once; a linked partial refund reduces net collections once; an unmatched refund is quarantined.
3. Two follow-ups to the same job cannot double-credit a paid job; a payment reversal retracts attribution.
4. Cross-tenant event links fail closed; missing processor signature, unknown currency or untrusted source never create verified revenue.
5. Missing operating-cost evidence prevents a positive verified profit claim even when collections are authenticated.
6. A zero-transaction month with incomplete provider coverage returns unknown, not zero.
7. Full-month, fully reconciled synthetic fixtures can prove arithmetic only, never establish actual profit.
8. Every external communication remains disabled until separate human approval, lawful consent and suppression checks.

**Current gate:** synthetic-only; no live customer onboarding, processor/CRM/email connections, outreach, or $2,500/month verified net profit. Implementation of these rules belongs in an owner-approved private production architecture and requires independent QA, not a public sample receipt database.
