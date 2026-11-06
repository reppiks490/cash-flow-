"""Standard-library unit tests for commercial safety gates."""
import unittest

from backend.onboarding import (
    OnboardingError, activate_billing, draft_subscription_quote,
    prepare_demo_workspace, send_followup,
)


class CommercialOnboardingTests(unittest.TestCase):
    def test_demo_workspace_accepts_synthetic_only(self):
        row = {"workspace_id": "demo-hvac-001", "industry": "hvac",
               "synthetic": True, "consent_mode": "manual_review_only"}
        workspace = prepare_demo_workspace(row)
        self.assertEqual(workspace.billing_status, "disabled")
        for patch in ({"synthetic": False}, {"consent_mode": "auto_send"},
                      {"workspace_id": "customer-live"}, {"email": "example@invalid.test"}):
            with self.subTest(patch=patch), self.assertRaises(OnboardingError):
                prepare_demo_workspace({**row, **patch})

    def test_quote_is_never_a_payment(self):
        quote = draft_subscription_quote()
        self.assertTrue(quote["synthetic"])
        self.assertEqual(quote["monthly_price_usd"], "700.00")
        self.assertIsNone(quote["payment_receipt"])
        self.assertFalse(quote["send_enabled"])
        for bad in ("0", "-1", "nan", "inf", "1.001", "invalid"):
            with self.subTest(bad=bad), self.assertRaises(OnboardingError):
                draft_subscription_quote(bad)

    def test_billing_and_outbound_remain_disabled(self):
        with self.assertRaises(PermissionError):
            activate_billing()
        with self.assertRaises(PermissionError):
            send_followup()


if __name__ == "__main__":
    unittest.main()
