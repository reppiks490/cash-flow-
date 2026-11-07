"""Pure synthetic buyer-threshold regression checks; no network or billing."""
import unittest

from products.revenue_recovery.commercial.buyer_thresholds import BuyerThreshold, calculate_buyer_threshold
from products.revenue_recovery.commercial.scenario_calculator import ScenarioError


class BuyerThresholdTests(unittest.TestCase):
    def test_rounding_and_separate_paths(self):
        result = calculate_buyer_threshold(BuyerThreshold("700.00", "240.00", "35.00", 8))
        self.assertEqual(result["minimum_incremental_paid_jobs_to_cover_fee"], 3)
        self.assertEqual(result["minimum_staff_hours_to_cover_fee"], 20)
        self.assertEqual(result["staff_labor_value_scenario_usd"], "280.00")
        self.assertIsNone(result["actual_buyer_roi_usd"])
        self.assertTrue(result["paths_are_alternatives_not_additive"])

    def test_zero_denominators_unknown(self):
        result = calculate_buyer_threshold(BuyerThreshold("700.00", "0", "0", 0))
        self.assertIsNone(result["minimum_incremental_paid_jobs_to_cover_fee"])
        self.assertIsNone(result["minimum_staff_hours_to_cover_fee"])
        self.assertTrue(result["jobs_threshold_unknown"])
        self.assertTrue(result["hours_threshold_unknown"])

    def test_no_false_verification_even_zero_fee(self):
        result = calculate_buyer_threshold(BuyerThreshold("0", "1", "1", 0))
        self.assertEqual(result["minimum_incremental_paid_jobs_to_cover_fee"], 0)
        self.assertIsNone(result["verified_incremental_paid_jobs"])

    def test_reject_pii_and_invalid_types(self):
        invalid = ("john@example.com", "1e3", "NaN", "-1", "700.001", "1,000", " 700", "1000001")
        for value in invalid:
            with self.subTest(value=value), self.assertRaises(ScenarioError):
                calculate_buyer_threshold(BuyerThreshold(value, "1", "1", 0))
        for hours in (True, 1.5, -1, 10001, "4"):
            with self.subTest(hours=hours), self.assertRaises(ScenarioError):
                calculate_buyer_threshold(BuyerThreshold("700", "1", "1", hours))

    def test_outside_supported_range(self):
        result = calculate_buyer_threshold(BuyerThreshold("1000000", "0.01", "0.01", 0))
        self.assertTrue(result["jobs_threshold_outside_supported_range"])
        self.assertTrue(result["hours_threshold_outside_supported_range"])
        self.assertIsNone(result["minimum_incremental_paid_jobs_to_cover_fee"])


if __name__ == "__main__":
    unittest.main()
