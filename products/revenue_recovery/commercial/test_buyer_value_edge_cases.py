"""RRE-04: synthetic buyer-value boundary regressions; no external side effects."""
import unittest

from commercial.buyer_break_even import (
    BuyerValueError, BuyerValueInputs, calculate_buyer_break_even,
)


class BuyerThresholdBoundaryTests(unittest.TestCase):
    def case(self, price="700.00", contribution="250.00", labor="50.00"):
        return BuyerValueInputs(price, contribution, labor)

    def test_smallest_positive_values_round_up(self):
        result = calculate_buyer_break_even(self.case("0.01", "0.01", "0.03"))
        self.assertEqual(result["jobs_required_to_cover_subscription_scenario"], 1)
        self.assertEqual(result["staff_hours_equivalent_to_subscription_scenario"], "0.34")
        self.assertEqual(result["monthly_price_usd"], "0.01")

    def test_exact_division_has_no_extra_job_or_hour(self):
        result = calculate_buyer_break_even(self.case("700.00", "350.00", "70.00"))
        self.assertEqual(result["jobs_required_to_cover_subscription_scenario"], 2)
        self.assertEqual(result["staff_hours_equivalent_to_subscription_scenario"], "10.00")

    def test_maximum_allowed_assumptions_remain_bounded(self):
        result = calculate_buyer_break_even(self.case("10000.00", "1000000.00", "0.01"))
        self.assertEqual(result["jobs_required_to_cover_subscription_scenario"], 1)
        self.assertEqual(result["staff_hours_equivalent_to_subscription_scenario"], "1000000.00")
        self.assertIsNone(result["verified_rre_net_profit_usd"])

    def test_over_limit_and_noncanonical_values_rejected_for_every_field(self):
        bad = ("10000.01", "1000000.01", "0001", "1e2", "NaN", "1.000",
               "1\\n", "１", "", None, True, 1.0)
        for field in ("monthly_price_usd", "incremental_job_contribution_usd",
                      "loaded_labor_hour_cost_usd"):
            for value in bad:
                with self.subTest(field=field, value=repr(value)):
                    kwargs = dict(monthly_price_usd="700.00",
                                  incremental_job_contribution_usd="250.00",
                                  loaded_labor_hour_cost_usd="50.00")
                    kwargs[field] = value
                    with self.assertRaises(BuyerValueError):
                        calculate_buyer_break_even(BuyerValueInputs(**kwargs))

    def test_unknown_denominators_do_not_become_zero_value_claims(self):
        result = calculate_buyer_break_even(self.case("700", "0", "0"))
        self.assertIsNone(result["jobs_required_to_cover_subscription_scenario"])
        self.assertIsNone(result["staff_hours_equivalent_to_subscription_scenario"])
        self.assertFalse(result["billing_enabled"])
        self.assertFalse(result["outreach_enabled"])
        self.assertNotIn("roi", result)


if __name__ == "__main__":
    unittest.main()
