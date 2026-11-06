# HVAC pilot decision gate — evidence and approval matrix

**Status:** internal planning instrument, 2026-11-06. No pilot authorized. All demonstrated lead, appointment and closed-job events are **synthetic**. No verified customers, revenue, collections or net profit.

## Operator go/no-go record (complete before any external pilot)

| Gate | Required artifact | Current evidence | Decision |
| --- | --- | --- | --- |
| Local demonstration | Exact commit, green Python/Node CI, manual desktop/mobile observations | Synthetic M1 code and CI exist; current-head visual review not established | HOLD |
| Identity and tenant boundaries | Independent negative-case test proving cross-tenant read/write denial and durable tenant isolation | Not established for real customer records | HOLD |
| Lawful contact permissions | Counsel-reviewed channel/jurisdiction policy, documented consent origin, revocation, suppression and audit replay | Only synthetic mock policy | HOLD |
| Human authorization | Authenticated reviewer, explicit approval tied to exact draft/recipient/channel and expiry | Draft preview only; no real authenticated approval | HOLD |
| CRM/calendar/email | Provider-specific sandbox contracts, least-privilege credentials outside repo, replay/idempotency and rollback tests | Dry-run mocks only | HOLD |
| Billing | Owner-approved terms, refund/cancellation policy, disabled-by-default billing integration and verified receipts reconciliation | Hypothetical price only; charging disabled | HOLD |
| Privacy/security | Data map, retention/deletion, breach response, access logging, independent security review | Not established | HOLD |
| Buyer validation | Authorized, consent-compliant interviews and documented actual buying criteria | No verified interviews | HOLD |
| Unit economics | Receipted recurring collections minus documented hosting, provider, support, refunds, taxes as applicable, and acquisition costs under declared accounting policy | No actual collections or costs | HOLD |

**Hard rule:** a synthetic job closure, mock appointment, draft approval, proposed subscription, or CRM preview must never count as a paid outcome. A gate cannot be marked PASS by a mock. Any HOLD blocks live pilot, vendor activation, outreach, deployment and charging.

## Buyer-discovery protocol (planning only; do not contact prospects)

For a future **owner-approved** interview, ask an HVAC owner to describe their current inbound lead sources, seasonality, after-hours coverage, existing CRM, average quote latency, follow-up ownership, consent provenance, duplicate handling, staff review capacity, cancellation/refund expectations and the value of a recovered *paid* job after variable costs. Ask for objections to paying $700/month without guaranteeing recoveries. Capture only aggregated, consented findings in private approved storage; no identifiable customer/prospect information in GitHub. Do not imply interviews have occurred.

## Hypothesis testing and falsification

- **Pricing hypothesis:** $700 per location per month, not validated willingness to pay. At five paid locations, billed revenue would be $3,500/month *before* discounts, nonpayment, refunds, taxes and costs.
- **Seller net target:** $2,500/month. At the illustrative $3,500 billed level, total relevant monthly costs must be **below $1,000** to exceed $2,500 pretax net; equality yields exactly $2,500. Actual net cannot be calculated without receipts and complete costs.
- **Buyer break-even:** separately estimate incremental *paid-job contribution margin* needed to cover subscription; never add staff-time opportunity-cost savings to job contribution unless independently realized and nonoverlapping.
- **Falsification conditions:** buyers cannot evidence lawful follow-up permission; review burden exceeds time saved; CRM source attribution is ambiguous; incremental collections cannot be distinguished from business-as-usual; churn/refunds erase contribution; or acquisition/support costs make seller net target infeasible.

## Measurement contract for a future controlled pilot

Define reporting window and tenant first. Keep `lead_received`, `qualified`, `drafted`, `human_approved`, `provider_sent`, `provider_delivered`, `appointment_confirmed`, `job_completed`, `invoice_issued`, `payment_settled`, and `refund_settled` as **separate, deduplicated event types**. For each, require an immutable event ID, event time, tenant, source reference, provenance, and authenticated evidence pointer. Missing provider confirmation => unknown, not success. Refunds reduce settled collections. Attribute a paid job to a campaign only with an explicit declared attribution window, verified event chain, and collision rule; report unattributed collections separately. Report pipeline counts separately from cash.

For a future 30-day evaluation, pre-register eligibility, baseline period, cohort definition, channel, review SLA, exclusions, sample size, refund lag, and stopping rules. Do not interpret a tiny pilot as causal proof. Never report estimates or booked appointments as recovered cash.

## Owner approval checkpoint

Before any external action, owner must separately approve the precise pilot scope, lawful contact channel, identity/consent design, named provider sandbox, data-handling controls, terms, spend ceiling and deployment destination. Until then: **offline synthetic-only**. No messages sent, leads collected, subscriptions charged or customer records processed by this document.

**Coordination:** RRE-04 #26; review against the latest `PROJECT_LEDGER.md`, QA release matrix, and current-main commit before marking any gate PASS. This matrix is a decision aid, not a legal opinion or production readiness certification.
