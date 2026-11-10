"""Synthetic commercial unit-economics negative controls (stdlib only)."""
import json
import unittest
from commercial.unit_economics import Scenario, evaluate


class UnitEconomicsTests(unittest.TestCase):
    def test_default_assumptions_are_not_profit_evidence(self):
        result = evaluate(Scenario())
        self.assertEqual(result["hypothetical_gross_usd"], "3500.00")
        self.assertEqual(result["hypothetical_costs_usd"], "875.00")
        self.assertEqual(result["hypothetical_contribution_usd"], "2625.00")
        self.assertEqual(result["minimum_customers_for_target_under_assumptions"], 5)
        self.assertIsNone(result["verified_net_profit_usd"])
        self.assertFalse(result["target_is_verified"])
        self.assertFalse(result["billing_enabled"])

    def test_no_receipts_cannot_establish_verified_zero(self):
        for count in (0, 5, 100):
            result = evaluate(Scenario(customers=count))
            self.assertIsNone(result["verified_revenue_usd"])
            self.assertIsNone(result["verified_net_profit_usd"])
            self.assertEqual(result["classification"], "hypothetical_not_verified")
            self.assertFalse(result["target_is_verified"])

    def test_zero_customers_still_incur_fixed_costs(self):
        result = evaluate(Scenario(customers=0))
        self.assertEqual(result["hypothetical_contribution_usd"], "-500.00")

    def test_nonpositive_unit_margin_has_no_break_even_solution(self):
        result = evaluate(Scenario(monthly_price_usd="100.00", monthly_cost_per_customer_usd="100.00"))
        self.assertIsNone(result["minimum_customers_for_target_under_assumptions"])

    def test_target_ceil_rounding(self):
        result = evaluate(Scenario(monthly_price_usd="700.00", monthly_fixed_cost_usd="0.00", monthly_cost_per_customer_usd="0.00", monthly_target_net_usd="2500.00"))
        self.assertEqual(result["minimum_customers_for_target_under_assumptions"], 4)

    def test_zero_target_with_zero_fixed_cost_requires_no_customers(self):
        result = evaluate(Scenario(customers=0, monthly_fixed_cost_usd="0.00", monthly_target_net_usd="0.00"))
        self.assertEqual(result["minimum_customers_for_target_under_assumptions"], 0)
        self.assertEqual(result["hypothetical_contribution_usd"], "0.00")
        self.assertFalse(result["target_is_verified"])

    def test_boundary_counts_and_large_bounded_amounts(self):
        result = evaluate(Scenario(customers=100000, monthly_price_usd="99999999.99", monthly_fixed_cost_usd="99999999.99", monthly_cost_per_customer_usd="0.00"))
        self.assertEqual(result["hypothetical_gross_usd"], "9999999999000.00")
        self.assertEqual(result["hypothetical_costs_usd"], "99999999.99")
        self.assertFalse(result["billing_enabled"])

    def test_unmodeled_refunds_are_not_inferred_as_zero(self):
        result = evaluate(Scenario())
        self.assertIn("refunds", result["excluded_costs"])
        self.assertIn("payment_fees", result["excluded_costs"])
        self.assertIn("owner_compensation", result["excluded_costs"])
        self.assertEqual(result["classification"], "hypothetical_not_verified")
        self.assertIsNone(result["verified_revenue_usd"])
        self.assertFalse(result["target_is_verified"])

    def test_nullable_evidence_survives_json_round_trip(self):
        result = evaluate(Scenario(customers=5))
        restored = json.loads(json.dumps(result, allow_nan=False))
        self.assertIsNone(restored["verified_revenue_usd"])
        self.assertIsNone(restored["verified_net_profit_usd"])
        self.assertEqual(restored["classification"], "hypothetical_not_verified")
        self.assertFalse(restored["target_is_verified"])
        self.assertFalse(restored["billing_enabled"])

    def test_reject_invalid_cost_and_target_fields(self):
        for field in ("monthly_fixed_cost_usd", "monthly_cost_per_customer_usd", "monthly_target_net_usd"):
            for value in ("NaN", "-0.01", "1e2", "999999999", None, True):
                with self.subTest(field=field, value=value), self.assertRaises(ValueError):
                    evaluate(Scenario(**{field: value}))

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
