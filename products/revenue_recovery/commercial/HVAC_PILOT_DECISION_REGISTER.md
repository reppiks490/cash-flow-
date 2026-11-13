# HVAC pilot decision register — evidence and authorization gates

**Status:** Internal synthetic-only commercial evaluation; not a pilot approval, customer validation, legal advice, or evidence of revenue. **Owner approval required before any external action.**

**Scope:** RRE-04 (#26). Complements [pilot offer](PILOT_OFFER_AND_DISCOVERY.md) and draft [demo packet](https://github.com/reppiks490/cash-flow-/pull/254); does not supersede QA, architecture, or release signoff. This register can be filled with nonidentifying synthetic results in GitHub; actual customer/prospect records, secrets, contracts, and receipts must never be committed to this public repository.

## Decision states

Use `NOT_ASSESSED`, `BLOCKED`, `FAILED`, or `PASSED` for each gate. **Unknown is never passed.** A single blocked or failed mandatory gate means **NO-GO** for live pilot; a synthetic demo may continue locally. Record the exact evidence artifact and reviewer, not an unsupported assertion.

| Gate | Minimum evidence for PASS | Current state |
|---|---|---|
| Product integrity | QA-signed exact integrated commit; repeatable synthetic intake -> qualification -> unsent draft -> mock CRM/appointment -> attributed report; negative cases for duplicates, suppression, and false receipts | NOT_ASSESSED |
| Tenant security | Independent security review of authenticated isolation, private persistence, retention/deletion, access audit and recovery; no cross-tenant leakage | NOT_ASSESSED |
| Consent and communications | Counsel-reviewed channel policy, source of permission, revocation/suppression, human approver identity, and send audit; no implicit consent from a synthetic fixture | NOT_ASSESSED |
| Provider integration | Authorized CRM/email/calendar test tenant, scoped permissions, replay/idempotency and failure-mode evidence; no live action by default | NOT_ASSESSED |
| Commercial terms | Signed pilot scope, support hours, incident response, data rights, cancellation/refund terms, fees and limits; $700/month remains hypothetical | NOT_ASSESSED |
| Owner authorization | Explicit, separately recorded approval for each real-data access, outreach, payment activation, and public deployment | NOT_ASSESSED |
| Financial measurement | Defined source-of-truth for cleared subscription receipts, refunds, payment fees, hosting, model usage, support labor and acquisition costs | NOT_ASSESSED |

**Decision rule:** `GO` requires every mandatory gate `PASSED` with dated independent evidence and an explicit owner decision. Otherwise `NO-GO`. No automated status transition authorizes outreach, collection, charging or deployment.

## Synthetic operator acceptance run (no external side effects)

1. Record commit SHA, Python/Node versions, local-only execution instructions and exact test commands. Link CI job and independent reviewer.
2. Run three bundled synthetic HVAC cases. Verify unique intake IDs, duplicate rejection, qualification evidence/unknowns and unsent draft status.
3. Exercise consent unknown and revoked scenarios. Confirm no `may_contact_real_person` or provider send; verify CRM preview is a dry run and appointment is unbooked.
4. Verify mock closed-job scenarios never increase **verified** receipts or attributed paid revenue. Capture a redacted synthetic-only scorecard.
5. Check the commercial demo packet against the actual UI and CLI at the tested commit. Record discrepancies as scoped issues rather than marking them passed.
6. Capture an operator decision with timestamp, test artifact links and remaining blockers. No real contacts or prospect interviews.

## KPI measurement contract for an eventual authorized pilot

Each metric needs a fixed observation window, source system, deduplication key, and exclusion rule before interpretation.

| Metric | Numerator / denominator | Evidence and limitations |
|---|---|---|
| Qualified inquiry rate | Unique eligible qualified inquiries / unique eligible inquiries | Source-backed intake and exclusion audit; not conversion or sales |
| Draft approval rate | Distinct approved drafts / distinct drafts submitted for human review | Authenticated approver event; not proof of delivery |
| Follow-up delivery rate | Provider-confirmed delivered messages / approved send attempts | Only after authorized integration; approval alone is not delivery |
| Booking rate | Provider-confirmed bookings / unique eligible inquiries | Mock appointments excluded |
| Paid-job conversion | Unique paid jobs / unique eligible inquiries | Reconciled job and payment identifiers; refunds handled |
| Attributed collected revenue | Sum of cleared, attributable customer-job receipts minus linked refunds | Document attribution window, counterfactual uncertainty and no double counting; estimates excluded |
| Product recurring net contribution | Cleared subscription collections minus refunds, processor fees, direct support, hosting, model usage and attributable acquisition costs | Define accounting period and allocation method; distinguish contribution from full net profit |
| Verified product net profit | Cleared product collections minus all attributable operating costs under documented accounting policy | Target $2,500/month; cannot be inferred from synthetic jobs or hypothetical subscriptions |

**Attribution caution:** recovered jobs may have closed without intervention. Report observed associated outcomes separately from experimentally estimated incremental lift; do not label the entire receipt as caused by the product.

## Pricing sensitivity (illustrative only)

At a hypothetical $700/month, 5 customers imply $3,500 **gross billed**, not collections or profit. A $2,500 monthly net target would require **all-in monthly costs and refunds no greater than $1,000**, assuming all $3,500 is actually collected. At 4 customers, $2,800 gross billed leaves at most $300 for all costs/refunds; this is not a realistic operating forecast. Customer count, willingness to pay, churn, acquisition cost and labor burden are unvalidated.

## Decision record template (no PII)

- Assessment date / reviewer role:
- Exact integrated commit and CI links:
- Synthetic demo run and negative-case evidence:
- Gate states and blocker issue links:
- Financial accounting definition and source-of-truth readiness:
- Operator verdict: `NO-GO` unless every gate is independently passed
- Owner approvals: `NONE` until separately authorized; never paste signatures, credentials or customer details here
- Next review trigger:

**Current verdict: NO-GO for live pilot, real data, outreach, payments and deployment.** This is a gate definition, not evidence of an executed review.
