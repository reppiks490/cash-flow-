"""Standalone stdlib tests: python -m unittest discover -s commercial -p 'test_*.py'."""
import unittest
from commercial.scenario_calculator import Scenario, ScenarioError, calculate_scenario


def scenario(**changes):
    data = dict(customers=5, price_usd="700.00", variable_cost_per_customer_usd="75.00",
                fixed_cost_usd="350.00", acquisition_cost_usd="150.00",
                refunds_and_fees_usd="125.00")
    data.update(changes)
    return Scenario(**data)


class ScenarioCalculatorTests(unittest.TestCase):
    def test_lean_scenario(self):
        result = calculate_scenario(scenario())
        self.assertEqual(result["gross_billed_scenario_usd"], "3500.00")
        self.assertEqual(result["pretax_net_scenario_usd"], "2500.00")
        self.assertEqual(result["minimum_customers_for_target_scenario"], 5)
        self.assertIsNone(result["actual_net_profit_usd"])
        self.assertIsNone(result["verified_receipts"])

    def test_zero_customers_is_not_zero_actual_revenue(self):
        result = calculate_scenario(scenario(customers=0))
        self.assertEqual(result["pretax_net_scenario_usd"], "-625.00")
        self.assertIsNone(result["actual_net_profit_usd"])

    def test_zero_target_with_zero_overhead_is_met_at_zero_customers(self):
        for unit_cost in ("0", "0.01"):
            with self.subTest(unit_cost=unit_cost):
                result = calculate_scenario(scenario(
                    customers=0, price_usd="0",
                    variable_cost_per_customer_usd=unit_cost,
                    fixed_cost_usd="0", acquisition_cost_usd="0",
                    refunds_and_fees_usd="0", target_pretax_net_usd="0"))
                self.assertEqual(result["minimum_customers_for_target_scenario"], 0)
                self.assertFalse(result["break_even_unreachable_at_assumed_unit_margin"])

    def test_scenario_minimum_beyond_supported_range_is_explicit(self):
        result = calculate_scenario(scenario(
            customers=0, price_usd="0.01", variable_cost_per_customer_usd="0",
            fixed_cost_usd="0", acquisition_cost_usd="0",
            refunds_and_fees_usd="0", target_pretax_net_usd="2500"))
        self.assertEqual(result["minimum_customers_for_target_scenario"], 250000)
        self.assertTrue(result["minimum_customers_outside_supported_range"])
        self.assertFalse(calculate_scenario(scenario())["minimum_customers_outside_supported_range"])

    def test_nonpositive_margin_unreachable(self):
        result = calculate_scenario(scenario(price_usd="50", variable_cost_per_customer_usd="75"))
        self.assertIsNone(result["minimum_customers_for_target_scenario"])
        self.assertTrue(result["break_even_unreachable_at_assumed_unit_margin"])

    def test_round_up_customer_count(self):
        result = calculate_scenario(scenario(fixed_cost_usd="351"))
        self.assertEqual(result["minimum_customers_for_target_scenario"], 6)

    def test_reject_noncanonical_usd_strings(self):
        # Canonical dollars only; do not silently accept Decimal exponent,
        # underscore separators, explicit plus signs or leading zeros.
        for bad in ("1e0", "1E+4", "+1", "0001", "1_000", "0e0"):
            with self.subTest(amount=bad), self.assertRaises(ScenarioError):
                calculate_scenario(scenario(price_usd=bad))

    def test_invalid_inputs_fail_closed(self):
        for bad in ("NaN", "Infinity", "-1", "1.001", "1e10", "", " 1", 12):
            with self.subTest(bad=bad):
                with self.assertRaises(ScenarioError):
                    calculate_scenario(scenario(price_usd=bad))
        for bad in (True, 1.2, -1, 10001):
            with self.subTest(customers=bad):
                with self.assertRaises(ScenarioError):
                    calculate_scenario(scenario(customers=bad))


if __name__ == "__main__":
    unittest.main()
