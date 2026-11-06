"""Tests for side-effect-free, planning-only subscription economics."""
import unittest

from commercial.economics import ScenarioError, model_subscription_scenario


def scenario(**changes):
    values = {
        "customers": 5,
        "monthly_price_usd": "700.00",
        "fixed_monthly_cost_usd": "1000.00",
        "variable_monthly_cost_per_customer_usd": "0.00",
    }
    values.update(changes)
    return model_subscription_scenario(**values)


class SubscriptionScenarioTests(unittest.TestCase):
    def test_base_hypothesis_and_nonverified_fields(self):
        report = scenario()
        self.assertEqual(report["gross_mrr_cents"], 350000)
        self.assertEqual(report["estimated_pre_tax_profit_cents"], 250000)
        self.assertEqual(report["minimum_customers_for_target"], 5)
        self.assertTrue(report["scenario_meets_target"])
        self.assertTrue(report["planning_only"])
        self.assertIsNone(report["verified_customers"])
        self.assertIsNone(report["verified_gross_revenue_cents"])
        self.assertIsNone(report["verified_net_profit_cents"])

    def test_variable_costs_change_required_customer_count(self):
        report = scenario(
            fixed_monthly_cost_usd="500.00",
            variable_monthly_cost_per_customer_usd="150.00",
        )
        self.assertEqual(report["estimated_pre_tax_profit_cents"], 225000)
        self.assertEqual(report["minimum_customers_for_target"], 6)
        self.assertFalse(report["scenario_meets_target"])

    def test_processing_fee_is_budgeted_conservatively(self):
        report = scenario(
            customers=1,
            fixed_monthly_cost_usd="0.00",
            processor_rate_bps=290,
            processor_flat_fee_usd="0.30",
        )
        self.assertEqual(report["processor_fees_cents"], 2060)
        self.assertEqual(report["estimated_pre_tax_profit_cents"], 67940)

    def test_unprofitable_contribution_never_claims_reachable_target(self):
        report = scenario(
            customers=10,
            fixed_monthly_cost_usd="100.00",
            variable_monthly_cost_per_customer_usd="700.00",
        )
        self.assertIsNone(report["minimum_customers_for_target"])
        self.assertFalse(report["scenario_meets_target"])

    def test_all_usd_fields_reject_noncanonical_notation(self):
        for key in ("monthly_price_usd", "fixed_monthly_cost_usd",
                    "variable_monthly_cost_per_customer_usd",
                    "target_profit_usd", "processor_flat_fee_usd"):
            for invalid in ("1e0", "+1", "0001", "1_000", ".50", "1.", "0e0", "9" * 1024):
                with self.subTest(field=key, value=invalid[:20]):
                    with self.assertRaises(ScenarioError):
                        scenario(**{key: invalid})

    def test_rejects_unsafe_numbers_and_unexpected_types(self):
        for patch in (
            {"customers": True}, {"customers": -1}, {"customers": 100001},
            {"monthly_price_usd": "0.00"}, {"monthly_price_usd": "nan"},
            {"monthly_price_usd": "inf"}, {"monthly_price_usd": 700.0},
            {"monthly_price_usd": "1.001"}, {"fixed_monthly_cost_usd": "-1"},
            {"target_profit_usd": "-1"}, {"processor_rate_bps": True},
            {"processor_rate_bps": 10001}, {"processor_flat_fee_usd": "0.001"},
        ):
            with self.subTest(patch=patch), self.assertRaises(ScenarioError):
                scenario(**patch)


if __name__ == "__main__":
    unittest.main()
