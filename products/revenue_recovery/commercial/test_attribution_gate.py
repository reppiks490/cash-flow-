"""Dependency-free negative tests for synthetic commercial attribution."""
import unittest

from products.revenue_recovery.commercial.attribution_gate import classify_attribution


class AttributionGateTests(unittest.TestCase):
    def event(self, **changes):
        event = dict(event_type="closed_job_mock", synthetic=True,
                     amount_usd="1200.00", evidence="offline_fixture")
        event.update(changes)
        return event

    def test_mock_closed_is_not_receipt(self):
        result = classify_attribution(self.event())
        self.assertEqual(result["estimated_pipeline_usd"], "1200.00")
        self.assertIsNone(result["verified_collected_revenue_usd"])
        self.assertIsNone(result["verified_net_profit_usd"])
        self.assertFalse(result["receipt_verified"])

    def test_nonclosed_monetary_value_rejected(self):
        for stage in ("inquiry", "draft", "appointment_mock"):
            with self.subTest(stage=stage), self.assertRaises(ValueError):
                classify_attribution(self.event(event_type=stage))

    def test_no_real_events_or_receipts(self):
        for change in (dict(synthetic=False), dict(evidence="payment_receipt"),
                       dict(event_type="paid"), dict(customer_email="x@example.test")):
            with self.subTest(change=change), self.assertRaises(ValueError):
                classify_attribution(self.event(**change))

    def test_bad_money_rejected(self):
        for amount in ("NaN", "Infinity", "1e9", "-1", "01", "1.234", " 1", "100000001", 5, True):
            with self.subTest(amount=amount), self.assertRaises(ValueError):
                classify_attribution(self.event(amount_usd=amount))

    def test_zero_value_stage(self):
        self.assertIsNone(classify_attribution(self.event(event_type="draft", amount_usd="0"))["estimated_pipeline_usd"])


if __name__ == "__main__":
    unittest.main()
