# Hypothetical subscription scenario calculator

This offline, standard-library-only model computes illustrative HVAC subscription economics. It does **not** retrieve actual receipts, payments, customer counts, expenses, tax data or verified profit. All numbers are user-supplied assumptions, never financial evidence.

From the repository root with `PYTHONPATH=products/revenue_recovery`, run `python -m unittest discover -s products/revenue_recovery -p 'test_*.py' -v` (Python 3.11+). Import `Scenario` and `calculate_scenario` from `commercial.scenario_calculator`. Do not expose this function to a public endpoint or pass live customer data.

The function models `customers × (price − variable cost) − fixed cost − acquisition cost − refunds/fees`. It rounds up the minimum customer count required to reach the **pretax** target under constant assumed costs. If per-customer contribution is nonpositive, the target is unreachable under the model. The minimum-customer calculation assumes fixed refunds/fees and acquisition costs; it is not a forecast, break-even guarantee, or after-tax estimate.

When the modeled target and all overhead are zero, the mathematical minimum is **zero customers**, even if added subscriptions would have a nonpositive contribution. When a theoretical minimum exceeds the calculator's 10,000-customer input range, `minimum_customers_outside_supported_range=true` explicitly flags that the estimate is outside its supported evaluation domain, not a viable customer forecast.

The existing `commercial.economics.model_subscription_scenario` calculator uses a separate 100,000-customer scenario limit; its `minimum_customers_outside_supported_range` field has the same disclosure meaning. It models processor fees while this calculator models fixed assumed acquisition/refunds separately. These are **alternative planning views**, not two independent revenue streams. Do not sum their profit outputs or double-count acquisition, support, owner labor or payment fees.

The output explicitly sets actual net profit and verified receipts to `null` because there is no connected financial source of truth. Before commercial release, replace hypothetical inputs with authenticated, reconciled private accounting evidence under separate approval; do not write receipts or personal data to GitHub. No billing, sending, CRM write or vendor integration is enabled by this calculator.
