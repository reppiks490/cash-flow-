# Revenue Recovery Engine — Unit economics v0.1

All values below are **hypotheses for planning**, not current invoices, verified costs, revenue, customer counts, or profit. USD per month unless stated.

## Accounting model

`gross_MRR = active_paying_customers * realized_monthly_price`

`pre_tax_operating_profit = gross_MRR - hosting - messaging - model_inference - CRM_integrations - payment_fees - support_labor - onboarding_labor_amortized - acquisition_cost_amortized - refunds - other_direct_and_fixed_expenses`

Use actual provider invoices and time logs to replace assumptions. Exclude sales tax from revenue when collected as tax. Distinguish gross billed, settled cash, refunded cash, and bank-available payouts. Net profit here is **pre-income-tax** and only valid if *all* operating expenses, including owner labor, are counted.

## Illustrative sensitivity table

| Scenario | Paying customers | Realized price | Gross MRR | All-in operating expenses | Pre-tax profit |
|---|---:|---:|---:|---:|---:|
| Conservative | 2 | $500 | $1,000 | $1,200 | -$200 |
| Base | 5 | $700 | $3,500 | $1,000 | $2,500 |
| Higher scale | 10 | $700 | $7,000 | $2,500 | $4,500 |
| Stretch | 40 | $700 | $28,000 | $3,000 | $25,000 |

The **stretch row is particularly aggressive**: $75 total operating cost/customer/month before tax would be unrealistic for many human-supported deployments. It is arithmetic, not a credible forecast. At 40 customers, $25,000 profit would require expenses <=$3,000/month; test labor and acquisition carefully.

## Break-even thresholds at $700 realized price

- With $1,000 fixed/all-in costs, two customers yield $1,400 gross and $400 pre-tax profit; five yield $2,500.
- If variable costs are $150/customer and fixed costs $500/month, contribution/customer = $550; five customers yield $2,250, six yield $2,800.
- If variable costs are $250/customer and fixed costs $500/month, contribution/customer = $450; seven customers yield $2,650.
- These are illustrative; costs may be nonlinear (support, onboarding, compliance, CRM licenses).

## Cost ledger to verify

1. Hosting/database/backups/monitoring and incident response.
2. LLM model inference including retry/token spend and safety review.
3. Email/SMS/telephony charges; usage volume and deliverability costs.
4. CRM API and integration/vendor charges.
5. Payment processing, refunds, disputes and chargebacks.
6. Customer onboarding and support hours at an explicit labor rate.
7. Sales/discovery/outreach hours and acquisition costs, amortized over observed retention.
8. Legal/privacy/security and insurance where applicable.
9. Taxes (separate from pre-tax net), accounting and administrative overhead.
10. Churn, discounts, uncollected invoices, and seasonal HVAC demand.

## Validation gates

- First 10 discovery conversations: record real objections and willingness-to-pay, no invented percentages.
- First 1–3 paying pilots: measure actual implementation hours, support hours, provider bills, time-to-value and confirmed outcomes.
- First 5 paying accounts: calculate realized gross margin and fully burdened pre-tax profit from reconciled evidence.
- Do not announce a $2,500 milestone unless the accounting period has verified payments, refunds, expenses, labor and reconciled attributable results.
