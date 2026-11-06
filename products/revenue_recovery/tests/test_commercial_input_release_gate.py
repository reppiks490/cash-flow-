"""QA contract gate for adversarial synthetic commercial inputs.

These tests intentionally expose a defect in the current main baseline.
Merge only together with independently reviewed commercial input guards.
No live records, payments, messages or integrations are involved.
"""
import unittest

from backend.onboarding import OnboardingError, draft_subscription_quote
from commercial.measurement_guards import MeasurementError, SyntheticMonthlySnapshot, usd


class CommercialInputReleaseGate(unittest.TestCase):
    def test_quote_must_reject_extreme_exponents_with_domain_error(self):
        with self.assertRaises(OnboardingError):
            draft_subscription_quote("1E+500")

    def test_quote_must_reject_numeric_nonstring(self):
        with self.assertRaises(OnboardingError):
            draft_subscription_quote(700)

    def test_measurement_must_reject_extreme_exponents_with_domain_error(self):
        with self.assertRaises(MeasurementError):
            usd("1E+500")

    def test_safe_scenario_remains_nonverified(self):
        result = SyntheticMonthlySnapshot(
            subscriptions=5, price_usd="700.00", refunds_usd="0.00",
            direct_costs_usd="400.00", overhead_usd="600.00",
        ).evaluate()
        self.assertEqual(result["net_profit_scenario_usd"], "2500.00")
        self.assertIs(result["verified"], False)
        self.assertIsNone(result["verified_receipts_usd"])
        self.assertIsNone(result["verified_net_profit_usd"])


if __name__ == "__main__":
    unittest.main()
