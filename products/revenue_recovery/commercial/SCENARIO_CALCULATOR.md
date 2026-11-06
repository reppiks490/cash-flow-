# Hypothetical subscription scenario calculator

This offline, standard-library-only model computes illustrative HVAC subscription economics. It does **not** retrieve actual receipts, payments, customer counts, expenses, tax data or verified profit. All numbers are user-supplied assumptions, never financial evidence.

From the repository root with `PYTHONPATH=products/revenue_recovery`, run `python -m unittest discover -s products/revenue_recovery -p 'test_*.py' -v` (Python 3.11+). Import `Scenario` and `calculate_scenario` from `commercial.scenario_calculator`. Do not expose this function to a public endpoint or pass live customer data.

The function models `customers × (price − variable cost) − fixed cost − acquisition cost − refunds/fees`. It rounds up the minimum customer count required to reach the **pretax** target under constant assumed costs. If per-customer contribution is nonpositive, the target is unreachable under the model. The minimum-customer calculation assumes fixed refunds/fees and acquisition costs; it is not a forecast, break-even guarantee, or after-tax estimate.

The output explicitly sets actual net profit and verified receipts to `null` because there is no connected financial source of truth. Before commercial release, replace hypothetical inputs with authenticated, reconciled private accounting evidence under separate approval; do not write receipts or personal data to GitHub. No billing, sending, CRM write or vendor integration is enabled by this calculator.
