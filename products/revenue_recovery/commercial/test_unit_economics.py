"""Synthetic commercial unit-economics negative controls (stdlib only)."""
import unittest
from commercial.unit_economics import Scenario, evaluate


class UnitEconomicsTests(unittest.TestCase):
    def test_default_assumptions_are_not_profit_evidence(self):
        result = evaluate(Scenario())
        self.assertEqual(result["hypothetical_gross_usd"], "3500.00")
        self.assertEqual(result["hypothetical_costs_usd"], "875.00")
        self.assertEqual(result["hypothetical_contribution_usd"], "2625.00")
        self.assertEqual(result["minimum_customers_for_target_under_assumptions"], 5)
        self.assertEqual(result["verified_net_profit_usd"], "0.00")
        self.assertFalse(result["target_is_verified"])
        self.assertFalse(result["billing_enabled"])

    def test_zero_customers_still_incur_fixed_costs(self):
        result = evaluate(Scenario(customers=0))
        self.assertEqual(result["hypothetical_contribution_usd"], "-500.00")

    def test_nonpositive_unit_margin_has_no_break_even_solution(self):
        result = evaluate(Scenario(monthly_price_usd="100.00", monthly_cost_per_customer_usd="100.00"))
        self.assertIsNone(result["minimum_customers_for_target_under_assumptions"])

    def test_target_ceil_rounding(self):
        result = evaluate(Scenario(monthly_price_usd="700.00", monthly_fixed_cost_usd="0.00", monthly_cost_per_customer_usd="0.00", monthly_target_net_usd="2500.00"))
        self.assertEqual(result["minimum_customers_for_target_under_assumptions"], 4)

    def test_reject_unsafe_money(self):
        for value in ("NaN", "Infinity", "-1", "1e3", " 700", "700.000", "00700", "100000000", 700, 700.0, None, True):
            with self.subTest(value=value), self.assertRaises(ValueError):
                evaluate(Scenario(monthly_price_usd=value))

    def test_reject_invalid_counts(self):
        for count in (-1, 100001, True, 1.5, "5", None):
            with self.subTest(count=count), self.assertRaises(ValueError):
                evaluate(Scenario(customers=count))


if __name__ == "__main__":
    unittest.main()
