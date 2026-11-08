"""Regression tests for offline commercial claim classification."""
import unittest

from products.revenue_recovery.commercial.claim_gate import classify_claim


class ClaimGateTests(unittest.TestCase):
    def test_synthetic_demo_is_displayable_but_not_verified(self):
        result = classify_claim("synthetic_demo")
        self.assertTrue(result.displayable)
        self.assertFalse(result.verified)
        self.assertFalse(result.live_action_authorized)

    def test_pricing_hypothesis_is_not_validated(self):
        result = classify_claim("pricing_hypothesis")
        self.assertTrue(result.displayable)
        self.assertFalse(result.verified)

    def test_financial_claims_fail_closed(self):
        for kind in ("verified_revenue", "verified_net_profit"):
            with self.subTest(kind=kind):
                result = classify_claim(kind)
                self.assertFalse(result.displayable)
                self.assertFalse(result.verified)
                self.assertFalse(result.live_action_authorized)

    def test_caller_cannot_supply_fake_receipt_or_authorization(self):
        for evidence in (True, {}, {"paid": True}, "receipt", 0):
            with self.subTest(evidence=evidence):
                with self.assertRaises(ValueError):
                    classify_claim("verified_net_profit", evidence)

    def test_unknown_and_malformed_claims_fail_closed(self):
        for kind in ("paid_customer", "recovered_revenue", "", None, True, 1, [], {}):
            with self.subTest(kind=kind):
                with self.assertRaises(ValueError):
                    classify_claim(kind)


if __name__ == "__main__":
    unittest.main()
