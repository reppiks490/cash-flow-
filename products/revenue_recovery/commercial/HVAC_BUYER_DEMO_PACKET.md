# HVAC buyer demonstration and objection handling — synthetic only

**Evidence classification:** operator training material, not buyer validation. **No outreach authorized, no pilot or production use.** Linked source documents: [pilot offer](PILOT_OFFER_AND_DISCOVERY.md) and [competitor evidence](COMPETITOR_EVIDENCE.md). This packet does not supersede either document.

## Twelve-minute local-only demonstration

| Clock | Operator action | Verifiable observation | Do not claim |
|---|---|---|---|
| 00:00–01:00 | Identify audience and say “All records are synthetic. This is a local, disconnected prototype.” | Explicit provenance and no real customer data | Live deployment, paying customers |
| 01:00–02:30 | Open the local dashboard using the project's existing runbook; show three bundled HVAC examples. | Synthetic inquiry categories and provenance | Real leads |
| 02:30–04:00 | Demonstrate duplicate-idempotency and invalid input rejection using documented test fixtures only. | Accepted/rejected outcomes in local workflow | Guaranteed production deduplication |
| 04:00–05:30 | Inspect rule-backed qualification, supporting facts and unknowns. | Deterministic recommendation with limitations | Actual AI accuracy or improved conversion |
| 05:30–07:00 | Open unsent follow-up draft and review its human-approval status. | Draft preview; no delivery mechanism | Email/SMS sent |
| 07:00–08:30 | Inspect mock CRM and appointment scenarios. | Explicit dry-run/unbooked status | CRM synchronized or booking confirmed |
| 08:30–10:00 | Display stage and attribution scorecard; separate mock closed-job events from authenticated receipts. | Zero verified collected revenue | Revenue recovered or profit earned |
| 10:00–11:00 | Show revocation/unknown-consent mock scenario and fail-closed suppression. | No permission to contact real people | Legal compliance certification |
| 11:00–12:00 | Compare existing CRM features, disclose price hypothesis and collect *offline, anonymous* internal evaluation notes. | Gaps and unverified assumptions | Signed demand or validated $700/month price |

**Preflight:** Use the existing `RUNBOOK_LOCAL.md` and product tests on an isolated local machine. Never expose the local server via public tunnel, enter prospect details, enable external connectors, or run this with real credentials. If a menu or endpoint differs from the installed revision, stop that step and mark it “not demonstrated”; do not improvise a live workflow.

## Buyer objections — answer without unsupported promises

| Buyer question | Evidence-bounded response | Qualification decision |
|---|---|---|
| “Jobber already reminds customers about quotes.” | Jobber advertises quote follow-up automation; check whether the buyer's plan and configuration already solve the problem. See competitor evidence. | If solved, **do not pitch duplicate functionality**. |
| “Housecall Pro has pipeline tools.” | Its features and add-ons may overlap; RRE is not a replacement CRM. | Only pursue a measured gap that incumbent tooling cannot close. |
| “ServiceTitan/Hatch already automate messaging.” | Both advertise follow-up and campaign functionality. RRE currently sends nothing. | Demonstrate operator review and evidence traceability only; require integration authorization later. |
| “Will this recover $10,000?” | No forecast or guaranteed outcome is supported. Synthetic events and modeled thresholds are not collections. | Require verified paid-job receipts and attribution controls before any performance claim. |
| “Why $700 per month?” | $700 is a hypothesis for a managed service, not validated willingness to pay. Existing software may be cheaper. | Compare incremental contribution, staff burden and actual costs; no commitment before discovery. |
| “Can you contact my customers now?” | No. Messaging, consent verification, authenticated tenant storage and production approval are not established. | **Decline live access and sending.** |

## Operator-only no-outreach script

“This is a synthetic workflow demonstration. We have not accessed your customer records, sent communications, connected your CRM, booked appointments or processed payments. Any follow-up you see is a draft for hypothetical human review. We cannot activate real outreach or import your data without separate owner authorization, privacy/security review, appropriate legal permissions and signed operating terms.”

## Measurement contract for a future authorized pilot

Define the baseline window and intervention cohort **before** exposure. Count eligible inbound inquiries once by tenant-scoped deduplication key. Track lead source and timestamp, qualification outcome, reviewer decision, approved draft, provider-confirmed delivery, provider-confirmed appointment, completed job, authenticated paid receipt, refunds, direct operating expenses and attributable net contribution as **separate stages**. Record denominator and unknown/missing values for every conversion rate. Do not divide by zero, infer delivery from a draft, infer booking from a mock appointment, or infer collections from a closed-job label. Report revenue only from authenticated receipts and profit only after reconciled costs and refunds.

**Hypothetical unit-economics illustration, not a prediction:** Five subscriptions at $700/month would produce $3,500 gross billed *if* five paying customers existed. Reaching $2,500 monthly pretax net would require total monthly expenses and adjustments below $1,000; acquisition, support, payment fees, refunds, hosting and taxes may change the result. Currently **no verified subscription revenue or net profit**.

## Decision gates

1. **Demo acceptance:** operator completes all observable local-only steps and records reproducible evidence; any failed step is labeled failed, not silently skipped.
2. **Commercial discovery:** owner separately authorizes outreach; independent interviews establish existing tools, measured leakage, willingness to pay and objections. No real contact data in GitHub.
3. **Pilot readiness:** QA signs off tenant isolation, private durable storage, consent/suppression audit, approvals, provider integration and data retention; counsel reviews applicable communications rules; owner signs scope and spend.
4. **Paid commercialization:** contracts, pricing, refunds, support boundaries, authorized billing and receipt reconciliation are independently verified. Until then: **prototype only**.

**Explicit limitations:** This is documentation, not a test execution record, compliance opinion, approved offer, customer testimonial or live commercial deployment.
