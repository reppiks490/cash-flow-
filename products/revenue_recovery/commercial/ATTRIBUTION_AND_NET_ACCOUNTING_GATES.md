# RRE-04 — Attribution and vendor-net accounting decision gates

**Status:** proposed synthetic-only contract for review; not production accounting, legal advice, or evidence of customer revenue. Complements draft PR #145 rather than modifying its branch. No customer records, outreach, payment processing, or live integrations.

## 1. Paid job is not necessarily recovered revenue

A completed paid HVAC job is **not** by itself evidence that RRE caused an incremental sale. Keep three distinct values:

1. **Verified contractor receipts:** money settled and reconciled to a job, less refunds/chargebacks, with private provider evidence.
2. **RRE-associated receipts:** verified receipts linked by immutable inquiry/job identifiers to an RRE-reviewed workflow, without a causal claim.
3. **Incremental recovered receipts:** only a defensible estimate or verified causal effect under a preregistered comparison design. Do not relabel associated receipts as incremental recovery.

**Deterministic classification, applied in order:**

| Condition | Outcome | Permitted claim |
| --- | --- | --- |
| Synthetic event, missing receipt, missing tenant-safe join, duplicate payment, or unreconciled refund | `unverified` | No verified revenue |
| Reconciled settled receipt but no valid RRE event linkage | `paid_unattributed` | Verified paid contractor job only |
| Reconciled receipt and linkage, but pre-existing booking, prior active negotiation, competing campaign, or ambiguous timeline | `associated_confounded` | Associated receipt, **not** recovered |
| Reconciled receipt and linkage, documented RRE review before subsequent action, no identified conflicting touch | `associated_observed` | Observational association only |
| Pre-registered randomized/credible comparison with appropriate denominator, contamination and uncertainty review | `incremental_estimate_reviewed` | Explicitly labeled estimated incremental effect, not an individual sale guarantee |

The default is **unverified**. No category is automatically upgraded by a salesperson, AI model, draft approval, mock CRM status, appointment, or invoice alone. Attribution must retain the rule version, event timestamps/timezone, cohort window, identity of the private evidence source, adjustment history and review decision. Deduplicate by stable tenant-scoped payment/event IDs; never sum stages of one job. Refunds and chargebacks reduce previously reported settled receipts, and revisions preserve prior as-of snapshots. If payment reconciliation cannot be performed, show `unavailable`, not an invented zero.

**Causal design:** Before pilot collection, freeze treatment definition (e.g., operator-approved follow-up), eligible inquiry denominator, assignment mechanism, primary outcome (net settled job receipts within a fixed follow-up window), censoring, seasonality controls, and handling of cross-channel touches. Randomized holdout requires owner/legal approval and must not withhold legally required communications. Without credible comparison, the product may report associated paid jobs, never a numerical incremental recovery claim.

## 2. RRE vendor net is separate from contractor outcomes

Use calendar-month cash-basis management reporting for the **$2,500/month pretax operating-net objective**, with an explicit reconciliation to accrual revenue when financial records become available. No figures are verified until private receipts and expenses are authenticated.

`vendor_pretax_operating_net_cash = settled_subscription_collections - customer_refunds - chargebacks - payment_processing_fees - infrastructure - AI/provider_usage - support_labor - sales_and_marketing - allocated_shared_overhead - other_operating_costs`

Treat disputed, failed, trial, billed-but-uncollected, or pending payments as **not collected**. Separate sales tax collected for remittance from revenue and costs. Do not subtract sales tax remittances twice. Exclude income taxes from the **pretax** metric, but report an after-income-tax estimate separately only with documented assumptions; never call pretax net take-home pay. Include founder/owner labor at a disclosed fair-value rate for **economic net** alongside cash operating net; disclose unpaid owner labor hours even when cash expense is zero. Record one-time setup, refunds, customer acquisition and shared overhead using documented allocation policies; do not hide them to meet the target. Recognize prepaid subscription revenue over service periods in the separate accrual view; deferred revenue is not earned revenue. Never mix contractor job receipts into RRE subscription collections.

**Sensitivity, hypothetical only:** 5 accounts × $700 billed = $3,500 billed monthly. If every dollar settles with no refunds, $1,000 total operating cash cost gives $2,500 pretax cash operating net. This is a mathematical scenario, not a customer count, price validation, or income claim. Economic net may be lower after owner labor allocation.

## 3. Release and evidence gates

For any real report require authenticated tenant ownership, private retention and deletion policy, approved integration/consent basis, source-of-truth reconciliation, deduplication and immutable adjustment logs, operator approval of outbound messages, reviewer signoff on attribution methodology, and QA review of exact code/test head. Report source coverage, unknown counts, zero denominators as N/A, and each figure's as-of time. No public GitHub prospect identities or payment receipts.

**Synthetic acceptance cases to implement before release:** duplicate settled receipt counts once; invoice without settlement yields unverified; refunded payment restates cohort; a job booked before follow-up is confounded; an RRE-linked paid job without a comparison is associated only; missing denominator yields N/A; collected subscription is not billed revenue; owner labor and shared overhead affect economic net; cross-tenant identifiers cannot join.

**Coordination:** RRE-04 issue #26 and PR #145 review findings. Principal owns shared schemas, QA owns release tests; this document is commercial methodology only. The demo remains nonproduction and must not initiate contact or charges.
