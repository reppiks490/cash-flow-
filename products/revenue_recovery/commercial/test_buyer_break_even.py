"""Synthetic-only buyer-value sensitivity acceptance tests (no real buyers)."""
import unittest
from commercial.buyer_break_even import BuyerValueInputs, calculate_buyer_break_even, BuyerValueError

class BuyerBreakEvenTests(unittest.TestCase):
    def scenario(self, **overrides):
        values = dict(monthly_price_usd="700.00", incremental_job_contribution_usd="250.00", loaded_labor_hour_cost_usd="50.00")
        values.update(overrides)
        return BuyerValueInputs(**values)

    def test_separate_job_and_labor_break_even(self):
        result = calculate_buyer_break_even(self.scenario())
        self.assertEqual(result["jobs_required_to_cover_subscription_scenario"], 3)
        self.assertEqual(result["staff_hours_equivalent_to_subscription_scenario"], "14.00")
        self.assertEqual(result["monthly_price_usd"], "700.00")

    def test_rounds_thresholds_up_not_down(self):
        result = calculate_buyer_break_even(self.scenario(monthly_price_usd="701.00", incremental_job_contribution_usd="350", loaded_labor_hour_cost_usd="33.33"))
        self.assertEqual(result["jobs_required_to_cover_subscription_scenario"], 3)
        self.assertEqual(result["staff_hours_equivalent_to_subscription_scenario"], "21.04")

    def test_zero_contribution_cannot_support_job_break_even(self):
        result = calculate_buyer_break_even(self.scenario(incremental_job_contribution_usd="0"))
        self.assertIsNone(result["jobs_required_to_cover_subscription_scenario"])
        self.assertIsNotNone(result["staff_hours_equivalent_to_subscription_scenario"])

    def test_zero_labor_rate_cannot_support_hours_break_even(self):
        result = calculate_buyer_break_even(self.scenario(loaded_labor_hour_cost_usd="0.00"))
        self.assertIsNone(result["staff_hours_equivalent_to_subscription_scenario"])

    def test_no_live_or_verified_claims_or_combined_roi(self):
        result = calculate_buyer_break_even(self.scenario())
        self.assertTrue(result["synthetic"])
        self.assertEqual(result["classification"], "unvalidated_buyer_value_hypothesis")
        self.assertIsNone(result["verified_incremental_jobs"])
        self.assertIsNone(result["verified_staff_time_saved_hours"])
        self.assertIsNone(result["verified_customer_recovered_revenue_usd"])
        self.assertIsNone(result["verified_rre_net_profit_usd"])
        self.assertFalse(result["outreach_enabled"])
        self.assertFalse(result["billing_enabled"])
        self.assertNotIn("combined_roi_usd", result)

    def test_invalid_formats_fail_closed(self):
        for value in ("NaN", "Infinity", "1e4", "-1", "+1", "01", "1.234", " 1", "1 ", "10000000000", "é", "0x10", "", "1\n2", 4, True, None, 3.5):
            with self.subTest(value=value), self.assertRaises(BuyerValueError):
                calculate_buyer_break_even(self.scenario(incremental_job_contribution_usd=value))

    def test_invalid_monthly_price_fail_closed(self):
        for value in ("0", "0.00", "10000.01", "99999", "1e6", 700, True):
            with self.subTest(value=value), self.assertRaises(BuyerValueError):
                calculate_buyer_break_even(self.scenario(monthly_price_usd=value))

    def test_invalid_input_type_fail_closed(self):
        for value in (None, {}, [], True, "700"):
            with self.subTest(value=value), self.assertRaises(BuyerValueError):
                calculate_buyer_break_even(value)

if __name__ == "__main__":
    unittest.main()
