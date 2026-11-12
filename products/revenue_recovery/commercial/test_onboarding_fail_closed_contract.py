"""Regression checks for the synthetic-only onboarding and billing boundary.

Run with PYTHONPATH=products/revenue_recovery python -m unittest
products/revenue_recovery/commercial/test_onboarding_fail_closed_contract.py
No network, secrets, customer records or external services.
"""
import unittest

from backend.onboarding import (
    OnboardingError,
    activate_billing,
    draft_subscription_quote,
    prepare_demo_workspace,
    send_followup,
)


class OnboardingFailClosedContractTests(unittest.TestCase):
    def test_synthetic_workspace_is_inert(self):
        workspace = prepare_demo_workspace({
            "workspace_id": "demo-hvac_01",
            "industry": "hvac",
            "synthetic": True,
            "consent_mode": "manual_review_only",
        })
        self.assertTrue(workspace.synthetic)
        self.assertEqual(workspace.billing_status, "disabled")
        self.assertEqual(workspace.consent_mode, "manual_review_only")

    def test_workspace_rejects_live_or_contact_fields(self):
        base = {
            "workspace_id": "demo-hvac_01",
            "industry": "hvac",
            "synthetic": True,
            "consent_mode": "manual_review_only",
        }
        mutations = (
            {"synthetic": False},
            {"industry": "plumbing"},
            {"consent_mode": "auto_send"},
            {"workspace_id": "demo-"},
            {"workspace_id": "demo-abc@example.com"},
            {"workspace_id": "demo-ＡＢＣ"},
            {"email": "prospect@example.com"},
            {"tenant_id": "real-customer"},
        )
        for mutation in mutations:
            with self.subTest(mutation=mutation), self.assertRaises(OnboardingError):
                prepare_demo_workspace({**base, **mutation})

    def test_price_quote_has_no_payment_or_send_capability(self):
        quote = draft_subscription_quote("700")
        self.assertEqual(quote["monthly_price_usd"], "700.00")
        self.assertIs(quote["synthetic"], True)
        self.assertIs(quote["nonbinding"], True)
        self.assertEqual(quote["billing_status"], "disabled")
        self.assertIsNone(quote["invoice_id"])
        self.assertIsNone(quote["payment_receipt"])
        self.assertIs(quote["send_enabled"], False)

    def test_noncanonical_prices_fail_closed(self):
        invalid = (None, True, 700, 700.0, "-1", "+1", " 1", "1 ", "01",
                   "1.001", "1e2", "NaN", "Infinity", "0", "0.00",
                   "10000.01", "１", "1,000", "1\n")
        for value in invalid:
            with self.subTest(value=repr(value)), self.assertRaises(OnboardingError):
                draft_subscription_quote(value)

    def test_billing_and_outbound_are_unconditionally_disabled(self):
        for action in (activate_billing, send_followup):
            with self.subTest(action=action.__name__), self.assertRaises(PermissionError):
                action()
            with self.subTest(action=action.__name__ + "_args"), self.assertRaises(PermissionError):
                action("demo-hvac_01", enabled=True)


if __name__ == "__main__":
    unittest.main()
