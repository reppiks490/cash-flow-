"""Fail-closed commercial onboarding contracts; synthetic fixtures only.

Run: PYTHONPATH=products/revenue_recovery python -m unittest
     products/revenue_recovery/backend/test_onboarding_denials.py -v
"""
import unittest

from backend.onboarding import (
    OnboardingError,
    activate_billing,
    draft_subscription_quote,
    prepare_demo_workspace,
    send_followup,
)


class OnboardingDenialTests(unittest.TestCase):
    def test_only_allowlisted_synthetic_hvac_workspace(self):
        valid = dict(workspace_id="demo-hvac-001", industry="hvac",
                     synthetic=True, consent_mode="manual_review_only")
        workspace = prepare_demo_workspace(valid)
        self.assertTrue(workspace.synthetic)
        self.assertEqual(workspace.billing_status, "disabled")
        self.assertEqual(workspace.consent_mode, "manual_review_only")
        for patch in (
            {"synthetic": False},
            {"industry": "plumbing"},
            {"consent_mode": "automatic"},
            {"workspace_id": "customer-123"},
            {"workspace_id": "demo-../../private"},
            {"email": "synthetic@example.invalid"},
        ):
            with self.subTest(patch=patch), self.assertRaises(OnboardingError):
                prepare_demo_workspace({**valid, **patch})

    def test_quote_is_nonbinding_and_never_a_receipt(self):
        quote = draft_subscription_quote("700.00")
        self.assertEqual(quote["monthly_price_usd"], "700.00")
        self.assertIs(quote["synthetic"], True)
        self.assertIs(quote["nonbinding"], True)
        self.assertEqual(quote["billing_status"], "disabled")
        self.assertIsNone(quote["invoice_id"])
        self.assertIsNone(quote["payment_receipt"])
        self.assertIs(quote["send_enabled"], False)

    def test_quote_rejects_unbounded_or_noncanonical_prices(self):
        for value in ("0", "0.00", "10000.01", "1e3", "-1", "+1",
                      " 700", "700 ", "700.000", "NaN", "Infinity",
                      "01", "", 700, True, None, "9" * 10000):
            with self.subTest(value=str(value)[:30]), self.assertRaises(OnboardingError):
                draft_subscription_quote(value)

    def test_all_payment_and_outbound_entrypoints_deny(self):
        for operation in (activate_billing, send_followup):
            with self.subTest(operation=operation.__name__):
                with self.assertRaises(PermissionError):
                    operation()
                with self.assertRaises(PermissionError):
                    operation({"synthetic": True}, owner_approved=True)


if __name__ == "__main__":
    unittest.main()
