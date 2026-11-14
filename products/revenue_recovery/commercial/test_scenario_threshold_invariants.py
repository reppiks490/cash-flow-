"""Synthetic-only threshold and evidence-separation regression tests.

No receipts, external integrations, customer records, billing or outreach.
"""
import unittest
from decimal import Decimal

from commercial.scenario_calculator import Scenario, ScenarioError, calculate_scenario


class ScenarioThresholdRegressionTests(unittest.TestCase):
    def test_exact_target_crossing_across_cost_and_price_grid(self):
        for price in ("1.00", "7.00", "700.00"):
            for fixed in ("0.00", "100.00", "1000.00"):
                with self.subTest(price=price, fixed=fixed):
                    baseline = Scenario(0, price, "0.00", fixed, "0.00", "0.00")
                    result = calculate_scenario(baseline)
                    threshold = result["minimum_customers_for_target_scenario"]
                    self.assertIsNotNone(threshold)
                    def profit(count):
                        scenario = Scenario(count, price, "0.00", fixed, "0.00", "0.00")
                        return Decimal(calculate_scenario(scenario)["pretax_net_scenario_usd"])
                    if threshold <= 10000:
                        self.assertGreaterEqual(profit(threshold), Decimal("2500.00"))
                        self.assertLess(profit(threshold - 1), Decimal("2500.00"))
                    else:
                        self.assertTrue(result["minimum_customers_outside_supported_range"])

    def test_nonpositive_contribution_never_claims_reachable_target(self):
        for price, variable in (("1.00", "1.00"), ("1.00", "2.00"), ("0.00", "0.00")):
            with self.subTest(price=price, variable=variable):
                result = calculate_scenario(
                    Scenario(5, price, variable, "0.00", "0.00", "0.00")
                )
                self.assertIsNone(result["minimum_customers_for_target_scenario"])
                self.assertTrue(result["break_even_unreachable_at_assumed_unit_margin"])
                self.assertIsNone(result["actual_net_profit_usd"])

    def test_synthetic_hypotheses_never_become_verified_revenue(self):
        for count in (0, 1, 5, 100, 10000):
            with self.subTest(count=count):
                result = calculate_scenario(
                    Scenario(count, "700.00", "25.00", "500.00", "100.00", "50.00")
                )
                self.assertEqual(result["classification"], "hypothetical_scenario_only")
                self.assertIs(result["synthetic"], True)
                self.assertIsNone(result["verified_receipts"])
                self.assertIsNone(result["actual_net_profit_usd"])
                self.assertIsNone(result["after_tax_net"])
                self.assertEqual(
                    Decimal(result["gross_billed_scenario_usd"])
                    - Decimal(result["total_cost_scenario_usd"]),
                    Decimal(result["pretax_net_scenario_usd"]),
                )

    def test_out_of_range_and_ambiguous_customer_counts_fail_closed(self):
        for count in (-1, 10001, True, False, 5.0, "5", None):
            with self.subTest(count=repr(count)), self.assertRaises(ScenarioError):
                calculate_scenario(
                    Scenario(count, "700.00", "0.00", "0.00", "0.00", "0.00")
                )


if __name__ == "__main__":
    unittest.main()
