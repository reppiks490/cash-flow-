"""Adversarial bounds tests for synthetic-only monthly measurement."""
import unittest
from decimal import Decimal

from commercial.measurement_guards import MeasurementError, SyntheticMonthlySnapshot, usd


class MeasurementBoundsTests(unittest.TestCase):
    def test_canonical_bounds_and_two_decimal_output(self):
        for text, value in (
            ("0", "0.00"),
            ("0.01", "0.01"),
            ("700", "700.00"),
            ("700.5", "700.50"),
            ("10000000.00", "10000000.00"),
        ):
            with self.subTest(text=text):
                self.assertEqual(usd(text), Decimal(value))

    def test_reject_extreme_exponents_and_unbounded_digits(self):
        for value in (
            "1E+999999999", "1e-999999999", "9" * 1000,
            "10000000.01", "99999999", "Infinity", "NaN",
        ):
            with self.subTest(value=value[:40]), self.assertRaises(MeasurementError):
                usd(value)

    def test_reject_noncanonical_and_non_decimal_types(self):
        for value in (
            "0001", ".50", "1.", "+1", "-1", " 1", "1 ", "1.001",
            "1_000", "1,000", "", 1, 1.0, True, None, Decimal("1.00"),
        ):
            with self.subTest(value=repr(value)), self.assertRaises(MeasurementError):
                usd(value)

    def test_reject_bad_scenario_cost_before_calculation(self):
        for key in ("price_usd", "refunds_usd", "direct_costs_usd", "overhead_usd"):
            payload = {
                "subscriptions": 5, "price_usd": "700.00",
                "refunds_usd": "0.00", "direct_costs_usd": "400.00",
                "overhead_usd": "600.00",
            }
            payload[key] = "1E+9999999"
            with self.subTest(key=key), self.assertRaises(MeasurementError):
                SyntheticMonthlySnapshot(**payload).evaluate()

    def test_planning_target_is_never_verified_revenue(self):
        result = SyntheticMonthlySnapshot(
            subscriptions=5,
            price_usd="700.00",
            refunds_usd="0.00",
            direct_costs_usd="400.00",
            overhead_usd="600.00",
        ).evaluate()
        self.assertEqual(result["net_profit_scenario_usd"], "2500.00")
        self.assertTrue(result["target_met_in_scenario"])
        self.assertFalse(result["verified"])
        self.assertIsNone(result["verified_receipts_usd"])
        self.assertIsNone(result["verified_net_profit_usd"])
        self.assertIsNone(result["customer_recovered_revenue_usd"])


if __name__ == "__main__":
    unittest.main()
