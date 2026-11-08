# RRE-04 — Pilot KPI / attribution / vendor net reconciliation crosswalk

**Status:** review proposal, synthetic only; not evidence of customers, receipts, causal uplift, or production readiness. Owner: Commercial. Related draft PRs: #145 (pilot KPI), #150 (attribution and accounting), #152 (receipt classifier), #158 (synthetic net model). Source-of-truth changes require independent review and integration by the responsible owners.

## Single vocabulary for reporting

| Label | Definition | Evidence gate | Allowed use |
| --- | --- | --- | --- |
| `contractor_settled_net_receipts` | Unique tenant/job-linked settled contractor payments less reconciled refunds and chargebacks | Authenticated private provider evidence; stable tenant-scoped payment IDs; complete adjustments | Contractor paid-job receipts, **never** RRE vendor income |
| `rre_associated_receipts` | Subset of settled contractor receipts with valid RRE workflow linkage | Linkage and chronological event audit; competing touches disclosed | Observational association, not incremental recovery |
| `estimated_incremental_recovery` | Cohort-level causal estimate from a preregistered credible comparison | Eligible denominator, assignment, contamination, uncertainty and reviewer signoff | Estimate with uncertainty, **never** guaranteed recovered jobs |
| `vendor_collected_subscription_cash` | RRE vendor's actually settled subscription cash, excluding pass-through sales taxes | Private payment reconciliation; pending/uncollected invoices excluded | Cash-basis vendor receipts only |
| `vendor_pretax_cash_operating_net` | Collected subscription cash minus refunds, chargebacks, fees, cash operating costs and allocated cash overhead | Reconciled vendor receipts and expense evidence; allocation policy | Pretax cash operating result, not take-home pay |
| `vendor_pretax_economic_net` | Pretax cash operating net less **unpaid** owner labor opportunity cost | Disclosed hours and fair-value rate, no duplication of already-paid labor | Separate economic sensitivity; not cash net |

Do not call `rre_associated_receipts` “recovered revenue.” PR #145's row labeled “Attributed recovered revenue” should be split into **associated settled contractor receipts** and **estimated incremental recovery**, with the latter unavailable until credible comparison review. PR #150 supplies the distinctions; PR #152 implements only receipt association categories. The classifier must not upgrade observational association into causal recovery.

## Metric contracts

- Every cohort KPI includes tenant-safe cohort definition, timezone, observation window, as-of timestamp, numerator, denominator, unknown count, evidence source, classification version and revision ID. Zero denominator -> `N/A`; absent evidence -> `unavailable`, not a verified zero.
- Count each inquiry once per stage and each settled payment once per tenant-scoped payment ID. A single inquiry can progress through multiple stages, but stage totals are **not additive revenue**.
- Provider-confirmed delivery, booked appointment, settled contractor receipt, and vendor subscription collection are four different event types. A draft or simulated event satisfies none of those real-world gates.
- Late refunds and chargebacks restate prior cohort snapshots, preserving immutable adjustments and original as-of values. Cross-tenant joins fail closed.
- Pre-existing bookings, prior negotiation, other campaigns, or uncertain event ordering remain `associated_confounded`. A clean timeline remains `associated_observed` unless credible comparison establishes incremental impact.

## Accounting bridge to PR #158

The calculator's `settled_collections` is **vendor** subscription collections, not contractor job payments. `allocated_overhead` must include documented cash shared-overhead allocation; `support_labor` includes **paid** support labor only. `owner_labor_imputed` includes only unpaid owner labor not already counted as paid support or another operating expense. Otherwise economic net double-counts labor.

For a cash-basis month:

`vendor_pretax_cash_operating_net = settled_collections - refunds - chargebacks - processing_fees - infrastructure - provider_usage - support_labor - sales_marketing - allocated_overhead - other_operating_costs`

`vendor_pretax_economic_net = vendor_pretax_cash_operating_net - owner_labor_imputed`

The formula assumes refunds/chargebacks are not already netted from `settled_collections` or other cost fields. If the source ledger reports net-of-refund collections, normalize to gross settled collections first; never subtract the same adjustment twice. Likewise do not double count payment fees included in settlement net. Record acquisition costs, one-time setup, and shared overhead using explicit allocation policies. Sales tax collected on behalf of authorities is excluded from vendor receipts and is not an income tax expense. Pretax net excludes income tax. Prepaid subscriptions require a **separate accrual/deferred-revenue bridge**, not an implicit claim that collected cash is earned revenue.

**Synthetic arithmetic only:** five hypothetical accounts at $700 billed/month = $3,500 billed. If all $3,500 settles, no refunds occur and all operating cash costs total $1,000, pretax cash operating net is $2,500. Actual verified net and customer count remain **unknown**. Owner labor may reduce economic net.

## Release reconciliation acceptance tests

1. Invoice without settlement -> no verified vendor collection or contractor paid receipt.
2. Same tenant-scoped payment repeated -> one settled receipt; conflicting payload -> reject.
3. Cross-tenant job/payment join -> reject.
4. Refund after reporting -> revision with lower settled amount and preserved previous snapshot.
5. RRE-linked paid job with no comparison -> associated only, no numeric incremental recovery.
6. Zero eligible denominator -> N/A; no source -> unavailable.
7. Paid support labor and imputed owner labor refer to different hours; double allocation rejected at the evidence layer.
8. Net-of-fee or net-of-refund processor settlements require normalization; double subtraction rejected.
9. Sales tax pass-through excluded; accrual/deferred revenue shown separately from cash.
10. Synthetic financial calculator outputs `verified_profit=false` and `target_met_verified=false` regardless of hypothetical amounts.

## Integration ownership and blockers

Commercial proposes terminology and accounting. Principal owns shared API/schema contracts, QA owns release evidence, and each PR author owns corrections to their own branches. Do **not** merge #145/#150/#152/#158 merely because individual CI checks pass: reconcile terminology and confirm exact integration-head tests and independent approval. Real receipt authentication, expense ledger reconciliation, tenant-private audit storage, approved provider integrations, legal review, and owner-authorized pilots remain blocked. No outreach, payments, customer records, live deployment, or Codex are authorized.
