"""Cross-module synthetic commercial negative controls; no customer data or side effects."""
import json
import unittest

from commercial.kpi_ratios import conversion_rate
from commercial.reporting_period import reporting_window
from commercial.unit_economics import Scenario, evaluate


class CommercialIntegrationContractTests(unittest.TestCase):
    def test_missing_financial_evidence_survives_json_roundtrip(self):
        report = json.loads(json.dumps(evaluate(Scenario())))
        self.assertIsNone(report["verified_revenue_usd"])
        self.assertIsNone(report["verified_net_profit_usd"])
        self.assertFalse(report["target_is_verified"])
        self.assertFalse(report["billing_enabled"])
        self.assertEqual(report["classification"], "hypothetical_not_verified")

    def test_unknown_and_undefined_rates_do_not_become_zero(self):
        for counts, status in (
            ((None, 12), "unknown_missing_evidence"),
            ((4, None), "unknown_missing_evidence"),
            ((0, 0), "undefined_zero_denominator"),
        ):
            with self.subTest(counts=counts):
                result = json.loads(json.dumps(conversion_rate(*counts)))
                self.assertEqual(result["status"], status)
                self.assertIsNone(result["percent"])

    def test_spring_dst_half_open_boundaries(self):
        window = reporting_window("2026-03-08", "2026-03-09", "America/Chicago")
        self.assertEqual(window["start_utc_inclusive"], "2026-03-08T06:00:00+00:00")
        self.assertEqual(window["end_utc_exclusive"], "2026-03-09T05:00:00+00:00")

    def test_fall_dst_half_open_boundaries(self):
        window = reporting_window("2026-11-01", "2026-11-02", "America/Chicago")
        self.assertEqual(window["start_utc_inclusive"], "2026-11-01T05:00:00+00:00")
        self.assertEqual(window["end_utc_exclusive"], "2026-11-02T06:00:00+00:00")

    def test_modeled_contribution_not_verified_net_profit(self):
        report = evaluate(Scenario())
        self.assertEqual(report["hypothetical_gross_usd"], "3500.00")
        self.assertEqual(report["hypothetical_contribution_usd"], "2625.00")
        self.assertIsNone(report["verified_net_profit_usd"])
        self.assertIn("refunds", report["excluded_costs"])
        self.assertIn("payment_fees", report["excluded_costs"])
        self.assertIn("customer_acquisition", report["excluded_costs"])


    def test_invalid_funnel_counts_fail_closed(self):
        for numerator, denominator in ((True, 2), (1, False), (-1, 3), (4, 3), (1.5, 2)):
            with self.subTest(numerator=numerator, denominator=denominator):
                with self.assertRaises(ValueError):
                    conversion_rate(numerator, denominator)

    def test_zero_activity_is_not_verified_zero_profit(self):
        report = evaluate(Scenario(customers=0))
        self.assertEqual(report["hypothetical_gross_usd"], "0.00")
        self.assertIsNone(report["verified_revenue_usd"])
        self.assertIsNone(report["verified_net_profit_usd"])
        self.assertFalse(report["target_is_verified"])

    def test_reporting_window_rejects_ambiguous_or_invalid_intervals(self):
        for start, end, zone in (
            ("2026-11-01", "2026-11-01", "America/Chicago"),
            ("2026-11-02", "2026-11-01", "America/Chicago"),
            ("2026-01-01", "2027-02-01", "America/Chicago"),
            ("2026-11-01", "2026-11-02", "UTC"),
            ("2026-11-01", "2026-11-02", "../etc/passwd"),
        ):
            with self.subTest(start=start, end=end, zone=zone):
                with self.assertRaises(ValueError):
                    reporting_window(start, end, zone)

if __name__ == "__main__":
    unittest.main()
