"""Boundary and disclosure regressions for synthetic attribution; no external I/O."""
import unittest

from products.revenue_recovery.commercial.attribution_gate import classify_attribution


def fixture(**overrides):
    event = {
        "event_type": "closed_job_mock",
        "synthetic": True,
        "amount_usd": "0",
        "evidence": "offline_fixture",
    }
    event.update(overrides)
    return event


class AttributionBoundaryTests(unittest.TestCase):
    def test_upper_limit_inclusive_and_cent_precision(self):
        result = classify_attribution(fixture(amount_usd="100000000.00"))
        self.assertEqual(result["estimated_pipeline_usd"], "100000000.00")
        self.assertIsNone(result["verified_collected_revenue_usd"])
        self.assertIsNone(result["verified_net_profit_usd"])
        self.assertIs(result["receipt_verified"], False)
        self.assertIs(result["external_actions_enabled"], False)

    def test_over_limit_rejected_even_by_one_cent(self):
        for amount in ("100000000.01", "999999999", "100000001.00"):
            with self.subTest(amount=amount), self.assertRaises(ValueError):
                classify_attribution(fixture(amount_usd=amount))

    def test_noncanonical_amounts_rejected(self):
        for amount in (
            "", ".50", "00", "00.00", "01.00", "1.", "1.000",
            "+1", "-0", "1,000", "1_000", "1e2", "1E2",
            "NaN", "Infinity", " 1", "1 ", "\n1", "1\n",
            "１２", "١٢", None, False, 1, 1.0,
        ):
            with self.subTest(amount=repr(amount)), self.assertRaises(ValueError):
                classify_attribution(fixture(amount_usd=amount))

    def test_no_monetary_claim_at_earlier_funnel_stages(self):
        for stage in ("inquiry", "draft", "appointment_mock"):
            for zero in ("0", "0.00"):
                with self.subTest(stage=stage, amount=zero):
                    result = classify_attribution(fixture(event_type=stage, amount_usd=zero))
                    self.assertIsNone(result["estimated_pipeline_usd"])
                    self.assertIsNone(result["verified_collected_revenue_usd"])
                    self.assertIsNone(result["verified_net_profit_usd"])
                    self.assertIs(result["receipt_verified"], False)

    def test_unknown_receipts_and_identifiers_never_accepted(self):
        for override in (
            {"event_type": "payment_collected_verified"},
            {"event_type": "refund_verified"},
            {"evidence": "receipt_verified"},
            {"synthetic": 1},
            {"synthetic": "true"},
            {"receipt_id": "example"},
            {"tenant_id": "example"},
            {"contact": "example"},
        ):
            with self.subTest(override=override), self.assertRaises(ValueError):
                classify_attribution(fixture(**override))


if __name__ == "__main__":
    unittest.main()
