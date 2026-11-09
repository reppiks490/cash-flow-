"""Negative-control contracts for synthetic-only onboarding and disabled billing.

No provider, network, real customer or payment is used.
"""
import unittest

from backend.onboarding import (
    OnboardingError, activate_billing, draft_subscription_quote,
    prepare_demo_workspace, send_followup,
)


class OnboardingDenialTests(unittest.TestCase):
    def setUp(self):
        self.valid = {
            "workspace_id": "demo-hvac_01",
            "industry": "hvac",
            "synthetic": True,
            "consent_mode": "manual_review_only",
        }

    def test_synthetic_workspace_is_not_billable(self):
        workspace = prepare_demo_workspace(self.valid)
        self.assertTrue(workspace.synthetic)
        self.assertEqual(workspace.billing_status, "disabled")
        self.assertEqual(workspace.consent_mode, "manual_review_only")

    def test_unexpected_contact_fields_rejected(self):
        for field in ("email", "phone", "customer_name", "api_key"):
            with self.subTest(field=field):
                with self.assertRaises(OnboardingError):
                    prepare_demo_workspace({**self.valid, field: "example"})

    def test_real_workspace_and_consent_escalation_rejected(self):
        for mutation in (
            {"synthetic": False},
            {"industry": "plumbing"},
            {"consent_mode": "auto_send"},
            {"workspace_id": "customer-123"},
            {"workspace_id": "demo-a@example.com"},
        ):
            with self.subTest(mutation=mutation):
                with self.assertRaises(OnboardingError):
                    prepare_demo_workspace({**self.valid, **mutation})

    def test_malformed_payload_rejected(self):
        for payload in (None, [], "demo", {}, {"workspace_id": "demo-ok"}):
            with self.subTest(payload=payload):
                with self.assertRaises(OnboardingError):
                    prepare_demo_workspace(payload)

    def test_quote_is_explicitly_nonbinding_and_disabled(self):
        quote = draft_subscription_quote("700.00")
        self.assertEqual(quote["monthly_price_usd"], "700.00")
        self.assertTrue(quote["synthetic"])
        self.assertTrue(quote["nonbinding"])
        self.assertEqual(quote["billing_status"], "disabled")
        self.assertIsNone(quote["invoice_id"])
        self.assertIsNone(quote["payment_receipt"])
        self.assertIs(quote["send_enabled"], False)

    def test_quote_rejects_unbounded_and_noncanonical_prices(self):
        for price in (0, 700.0, True, None, "", "0", "0.00", "10000.01",
                      "1e3", "NaN", "Infinity", "-1", "+1", " 700",
                      "700.000", "00700", "700 USD", "１"):
            with self.subTest(price=price):
                with self.assertRaises(OnboardingError):
                    draft_subscription_quote(price)

    def test_billing_cannot_be_activated_by_arguments(self):
        for args, kwargs in (((), {}), (("approved",), {}), ((), {"owner_approved": True})):
            with self.subTest(args=args, kwargs=kwargs):
                with self.assertRaises(PermissionError):
                    activate_billing(*args, **kwargs)

    def test_followup_cannot_be_sent_by_arguments(self):
        for args, kwargs in (((), {}), (("synthetic",), {}), ((), {"approved": True})):
            with self.subTest(args=args, kwargs=kwargs):
                with self.assertRaises(PermissionError):
                    send_followup(*args, **kwargs)


if __name__ == "__main__":
    unittest.main()
