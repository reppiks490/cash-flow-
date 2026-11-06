"""Unit tests for synthetic-only measurement, using Python standard library."""
import unittest
from commercial.measurement_guards import MeasurementError, SyntheticMonthlySnapshot, usd

def scenario(**changes):
    payload = dict(subscriptions=5, price_usd="700.00", refunds_usd="0.00",
                   direct_costs_usd="400.00", overhead_usd="600.00")
    payload.update(changes)
    return SyntheticMonthlySnapshot(**payload)

class MeasurementTests(unittest.TestCase):
    def test_target_is_only_hypothetical(self):
        result = scenario().evaluate()
        self.assertEqual(result["net_profit_scenario_usd"], "2500.00")
        self.assertTrue(result["target_met_in_scenario"])
        self.assertFalse(result["verified"])
        self.assertIsNone(result["verified_receipts_usd"])
    def test_refund_and_cost_sensitivity(self):
        result = scenario(refunds_usd="100.00").evaluate()
        self.assertEqual(result["net_profit_scenario_usd"], "2400.00")
        self.assertFalse(result["target_met_in_scenario"])
    def test_negative_profit_is_not_clamped(self):
        self.assertEqual(scenario(subscriptions=0).evaluate()["net_profit_scenario_usd"], "-1000.00")
    def test_reject_live_accounting(self):
        with self.assertRaises(MeasurementError):
            scenario(synthetic=False).evaluate()
    def test_reject_boolean_count(self):
        with self.assertRaises(MeasurementError):
            scenario(subscriptions=True).evaluate()
    def test_reject_refund_over_gross(self):
        with self.assertRaises(MeasurementError):
            scenario(refunds_usd="3500.01").evaluate()
    def test_reject_unsafe_amounts(self):
        for amount in ("NaN", "Infinity", "-1", "1.001", "abc", ""):
            with self.subTest(amount=amount), self.assertRaises(MeasurementError):
                usd(amount)
    def test_reject_numeric_float(self):
        with self.assertRaises(MeasurementError):
            usd(1.23)

if __name__ == "__main__":
    unittest.main()
