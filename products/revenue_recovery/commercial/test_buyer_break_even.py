"""Synthetic buyer model regression checks; no external side effects."""
import unittest
from commercial.buyer_break_even import BuyerScenario, calculate_buyer_break_even
from commercial.scenario_calculator import ScenarioError

class BuyerBreakEvenTests(unittest.TestCase):
    def make(self, **overrides):
        values = dict(subscription_usd="700.00", incremental_paid_job_contribution_usd="250.00",
                      staff_hours_opportunity_cost_usd="100.00", incremental_paid_jobs=3)
        values.update(overrides)
        return BuyerScenario(**values)

    def test_ceiling_and_buyer_net(self):
        r = calculate_buyer_break_even(self.make())
        self.assertEqual(r["minimum_incremental_paid_jobs_to_break_even"], 4)
        self.assertEqual(r["hypothetical_buyer_net_value_usd"], "-50.00")
        self.assertIsNone(r["verified_buyer_roi"])
        self.assertIsNone(r["seller_net_profit_usd"])

    def test_zero_contribution_is_unknown(self):
        r = calculate_buyer_break_even(self.make(incremental_paid_job_contribution_usd="0"))
        self.assertIsNone(r["minimum_incremental_paid_jobs_to_break_even"])
        self.assertTrue(r["break_even_unknown_due_to_zero_contribution"])

    def test_zero_cost_requires_zero_jobs(self):
        r = calculate_buyer_break_even(self.make(subscription_usd="0", staff_hours_opportunity_cost_usd="0"))
        self.assertEqual(r["minimum_incremental_paid_jobs_to_break_even"], 0)

    def test_rejects_noncanonical_or_personal_text(self):
        for bad in ("1e3", "01", "-1", "Jane Doe", "100.001", "１００", "1000001"):
            with self.subTest(bad=bad), self.assertRaises(ScenarioError):
                calculate_buyer_break_even(self.make(subscription_usd=bad))

    def test_rejects_bool_float_negative_and_oversize_counts(self):
        for bad in (True, 1.5, -1, 10001, "3"):
            with self.subTest(bad=bad), self.assertRaises(ScenarioError):
                calculate_buyer_break_even(self.make(incremental_paid_jobs=bad))

    def test_out_of_range_threshold_labeled(self):
        r = calculate_buyer_break_even(self.make(subscription_usd="1000000", incremental_paid_job_contribution_usd="0.01"))
        self.assertTrue(r["threshold_outside_supported_range"])
        self.assertGreater(r["minimum_incremental_paid_jobs_to_break_even"], 10000)

if __name__ == "__main__":
    unittest.main()
