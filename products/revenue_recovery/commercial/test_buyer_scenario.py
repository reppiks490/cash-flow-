"""Synthetic buyer model regression checks; no external side effects."""
import unittest
from commercial.buyer_scenario import BuyerScenario, calculate_buyer_scenario
from commercial.scenario_calculator import ScenarioError

class BuyerBreakEvenTests(unittest.TestCase):
    def make(self, **overrides):
        values = dict(subscription_usd="700.00", incremental_paid_job_contribution_usd="250.00",
                      staff_hours_opportunity_cost_usd="100.00", incremental_paid_jobs=3)
        values.update(overrides)
        return BuyerScenario(**values)

    def test_ceiling_and_buyer_net(self):
        r = calculate_buyer_scenario(self.make())
        self.assertEqual(r["minimum_incremental_paid_jobs_to_break_even"], 4)
        self.assertEqual(r["hypothetical_buyer_net_value_usd"], "-50.00")
        self.assertIsNone(r["verified_buyer_roi"])
        self.assertIsNone(r["seller_net_profit_usd"])

    def test_zero_contribution_is_unknown(self):
        r = calculate_buyer_scenario(self.make(incremental_paid_job_contribution_usd="0"))
        self.assertIsNone(r["minimum_incremental_paid_jobs_to_break_even"])
        self.assertTrue(r["break_even_unknown_due_to_zero_contribution"])

    def test_zero_cost_requires_zero_jobs(self):
        r = calculate_buyer_scenario(self.make(subscription_usd="0", staff_hours_opportunity_cost_usd="0"))
        self.assertEqual(r["minimum_incremental_paid_jobs_to_break_even"], 0)

    def test_rejects_noncanonical_or_personal_text(self):
        for bad in ("1e3", "01", "-1", "Jane Doe", "100.001", "１００", "1000001"):
            with self.subTest(bad=bad), self.assertRaises(ScenarioError):
                calculate_buyer_scenario(self.make(subscription_usd=bad))

    def test_rejects_bool_float_negative_and_oversize_counts(self):
        for bad in (True, 1.5, -1, 10001, "3"):
            with self.subTest(bad=bad), self.assertRaises(ScenarioError):
                calculate_buyer_scenario(self.make(incremental_paid_jobs=bad))

    def test_out_of_range_threshold_labeled(self):
        r = calculate_buyer_scenario(self.make(subscription_usd="1000000", incremental_paid_job_contribution_usd="0.01"))
        self.assertTrue(r["threshold_outside_supported_range"])
        self.assertGreater(r["minimum_incremental_paid_jobs_to_break_even"], 10000)

    def test_cent_level_ceiling_boundary(self):
        r = calculate_buyer_scenario(self.make(subscription_usd="0.03",
            staff_hours_opportunity_cost_usd="0", incremental_paid_job_contribution_usd="0.01",
            incremental_paid_jobs=2))
        self.assertEqual(r["minimum_incremental_paid_jobs_to_break_even"], 3)
        self.assertEqual(r["hypothetical_buyer_net_value_usd"], "-0.01")

    def test_maximum_supported_jobs_and_zero_jobs(self):
        for jobs in (0, 10000):
            with self.subTest(jobs=jobs):
                r = calculate_buyer_scenario(self.make(incremental_paid_jobs=jobs))
                self.assertEqual(r["assumed_incremental_paid_jobs"], jobs)
                self.assertTrue(r["synthetic"])
                self.assertIsNone(r["verified_paid_jobs"])
                self.assertIsNone(r["actual_net_profit_usd"])

    def test_zero_cost_and_zero_contribution_still_requires_zero_jobs(self):
        r = calculate_buyer_scenario(self.make(subscription_usd="0",
            staff_hours_opportunity_cost_usd="0", incremental_paid_job_contribution_usd="0"))
        self.assertEqual(r["minimum_incremental_paid_jobs_to_break_even"], 0)
        self.assertFalse(r["break_even_unknown_due_to_zero_contribution"])

    def test_rejects_unicode_and_non_string_monetary_inputs(self):
        for bad in ("١٠", "１０", "10\u200b", "10\n", None, 10, True):
            with self.subTest(bad=repr(bad)), self.assertRaises(ScenarioError):
                calculate_buyer_scenario(self.make(staff_hours_opportunity_cost_usd=bad))

if __name__ == "__main__":
    unittest.main()
