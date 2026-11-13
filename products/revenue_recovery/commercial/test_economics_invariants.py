"""Property-style deterministic invariants for hypothetical subscription economics.

No customer records, receipts, vendor calls, billing or outreach.
"""
import unittest

from commercial.economics import model_subscription_scenario


class EconomicsInvariantTests(unittest.TestCase):
    def test_accounting_identity_and_target_threshold(self):
        for price in ("0.01", "1.00", "700.00"):
            for variable in ("0.00", "0.01", "800.00"):
                for customers in (0, 1, 5, 100):
                    with self.subTest(price=price, variable=variable, customers=customers):
                        result = model_subscription_scenario(
                            customers=customers,
                            monthly_price_usd=price,
                            fixed_monthly_cost_usd="10.00",
                            variable_monthly_cost_per_customer_usd=variable,
                            processor_rate_bps=290,
                            processor_flat_fee_usd="0.30",
                        )
                        self.assertEqual(
                            result["gross_mrr_cents"] - result["estimated_total_costs_cents"],
                            result["estimated_pre_tax_profit_cents"],
                        )
                        self.assertEqual(
                            result["estimated_total_costs_cents"],
                            result["fixed_costs_cents"]
                            + result["variable_costs_cents"]
                            + result["processor_fees_cents"],
                        )
                        self.assertEqual(
                            result["scenario_meets_target"],
                            result["estimated_pre_tax_profit_cents"] >= result["target_profit_cents"],
                        )
                        self.assertIsNone(result["verified_net_profit_cents"])
                        self.assertIsNone(result["verified_gross_revenue_cents"])

    def test_minimum_customer_count_is_exact_crossing_when_reachable(self):
        for fixed in ("0.00", "1.00", "1000.00"):
            for price in ("1.00", "700.00"):
                result = model_subscription_scenario(
                    customers=0,
                    monthly_price_usd=price,
                    fixed_monthly_cost_usd=fixed,
                    variable_monthly_cost_per_customer_usd="0.00",
                    processor_rate_bps=290,
                    processor_flat_fee_usd="0.30",
                )
                minimum = result["minimum_customers_for_target"]
                self.assertIsNotNone(minimum)
                self.assertGreater(minimum, 0)
                def profit(count):
                    return model_subscription_scenario(
                        customers=count,
                        monthly_price_usd=price,
                        fixed_monthly_cost_usd=fixed,
                        variable_monthly_cost_per_customer_usd="0.00",
                        processor_rate_bps=290,
                        processor_flat_fee_usd="0.30",
                    )["estimated_pre_tax_profit_cents"]
                self.assertGreaterEqual(profit(minimum), result["target_profit_cents"])
                self.assertLess(profit(minimum - 1), result["target_profit_cents"])


if __name__ == "__main__":
    unittest.main()
