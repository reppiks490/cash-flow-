# RRE-04 — HVAC pilot demo and operator acceptance script

**Classification:** synthetic, offline sales-enablement artifact. **Not:** a validated offer, an approved outreach script, a production readiness certificate, or evidence of revenue. Use only with owner-authorized internal reviewers until legal/privacy and outreach approvals exist.

## Positioning and disqualification

**Hypothesis:** HVAC operators may benefit from a review queue that identifies stalled inbound requests and prepares follow-up drafts for a human to approve. The product does **not** promise recovered jobs, send messages, verify consent, schedule real appointments, or reconcile real payments in this build.

Before presenting a subscription, ask an *authorized internal reviewer* to check whether the operator's existing CRM already offers the required intake, reminders and follow-up workflow. Recommend configuring the incumbent instead of duplicating a working capability. Do not claim competitor feature gaps without current, verified product-plan evidence. No real buyer interviews or prospect contact are authorized.

## Demonstration — local synthetic environment only

1. Follow `products/revenue_recovery/RUNBOOK_LOCAL.md` on loopback only. Do not expose a tunnel or load real contact details. If the local app cannot be started, record **NOT RUN** rather than describing it as observed.
2. Load the labeled synthetic HVAC examples. Identify the lead source, permitted synthetic fields and deduplication behavior. **Pass evidence:** screenshots or test logs from the current commit showing rejected unknown/raw customer fields; otherwise **NOT VERIFIED**.
3. Open a recovery preview. Read the qualification rule, source/evidence and unknowns. Verify that the follow-up is an **unsent draft** and cannot be delivered through this interface.
4. Show the consent/policy fixture with unknown consent and the revoked mock. Verify revoked state suppresses the draft and no fixture asserts verified consent or real operator authorization.
5. Open CRM dry-run and mock appointment state. Confirm neither represents an actual CRM write, booked appointment, or customer notification.
6. Open the pipeline/scorecard. Confirm synthetic lifecycle events are distinguishable from independently authenticated receipts, and verified revenue remains zero/unknown rather than inferred from a mock closed job.
7. Open the hypothetical commercial calculator. Enter `700.00` monthly price and clearly distinguish modeled break-even jobs or labor hours from actual return on investment, subscriptions, collections and profit.
8. Demonstrate rejection of billing activation and outbound send via the existing disabled onboarding ports in a test-only environment. Never provide real credentials or invoke vendor endpoints.

**Stop conditions:** any real recipient identifier, non-loopback exposure, actual send/payment capability, unexplained positive verified-revenue figure, or missing synthetic/provenance label. Stop the demo, record the failing step and commit, and escalate to RRE-05/RRE-01. Do not improvise a workaround.

## Evidence capture worksheet (blank; no customer information)

| Field | Required entry |
|---|---|
| Exact Git commit and PR | `NOT RUN` until observed |
| Local command and environment | `NOT RUN` until observed |
| Synthetic intake / dedupe | PASS / FAIL / NOT RUN, with test or screenshot reference |
| Qualification source and unknowns | PASS / FAIL / NOT RUN |
| Draft unsent / suppression | PASS / FAIL / NOT RUN |
| CRM and appointment mock labels | PASS / FAIL / NOT RUN |
| Receipt-backed verified revenue = 0 or unknown | PASS / FAIL / NOT RUN |
| Billing and outbound disabled | PASS / FAIL / NOT RUN |
| Reviewer, QA signoff and date | PENDING (private approval record; no PII in public repo) |

Do not interpret a green unit test as visual acceptance, tenant security, compliance clearance or production deployment approval.

## Proposed controlled pilot — approval required, not yet offered

**Scope hypothesis:** one HVAC operator, one approved intake source, one staff reviewer, synthetic rehearsal first; no automated outbound messaging, no payment processing, no real CRM/calendar writes. Before real records are considered, require documented owner authorization, privacy and legal review, tenant isolation, authenticated operator identity, private storage and retention, consent/suppression evidence, integration sandbox tests, incident/rollback plan, and QA signoff. A future live pilot is a separate authorization decision.

**Service boundaries:** the operator owns accuracy of its job records, consent and human send decisions; RRE may only draft or stage a recommendation until specifically authorized integrations exist. No guaranteed response times, appointment volume, conversion rate, or recovered revenue. Escalate failures to a human rather than silently retrying external side effects.

## KPIs and attribution definitions

| KPI | Numerator | Denominator / evidence gate |
|---|---|---|
| Eligible-lead rate | Permissioned, deduplicated, policy-eligible inbound leads | All unique inbound leads; provenance and permission must be independently established |
| Draft review acceptance | Human-approved drafts | All drafts presented to authenticated reviewers; an approval is **not** a send |
| Confirmed follow-up rate | Provider-confirmed sent follow-ups | Approved drafts; requires authorized send receipts and suppression check |
| Confirmed appointment rate | Provider-confirmed booked appointments | Eligible leads; never count mock appointments |
| Paid-job conversion | Receipt-backed paid jobs with attributable lead lineage | Eligible leads; deduplicate jobs and refunds |
| Attributed net collected revenue | Collected attributed payments less refunds | Payment evidence and documented attribution window; do not substitute quote value |
| RRE monthly pretax net profit | Actual collected RRE subscription/service revenue minus refunds, processor fees, hosting, support, acquisition and other relevant monthly operating costs | Month-matched ledger and authenticated receipts; no synthetic data |

**Financial scenario, not forecast:** five subscriptions × $700/month = $3,500 *hypothetical gross billings*. $2,500 pretax monthly net requires total relevant monthly costs **at most $1,000**, assuming the $3,500 is actually collected with no refunds; taxes and owner labor treatment must be explicitly documented. No verified subscribers, collections, or net profit are established.

## Research and go/no-go

Use `commercial/BUYER_DISCOVERY_SCORECARD_CONTRACT.md` only after owner approval for real discovery. Ten independent interviews are a proposed falsification target, not completed interviews or statistical validation. Keep any future identities, consent, transcripts, private authorization and billing evidence outside public GitHub. Report refusals and missing responses; do not convert willingness-to-pay into a sale.

**Current gate:** internal synthetic demonstration candidate only. **No-go** for outreach, customer onboarding, real integrations, billing, public deployment and revenue claims. Release requires independently recorded QA and owner decisions, not this document alone.
