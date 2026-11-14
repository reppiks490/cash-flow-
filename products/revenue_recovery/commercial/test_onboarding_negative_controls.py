"""Additional synthetic-only onboarding boundary regressions (stdlib unittest).

Run from products/revenue_recovery with:
python -m unittest discover -s commercial -p 'test_*.py'
"""
import unittest

from backend.onboarding import (
    OnboardingError, activate_billing, draft_subscription_quote,
    prepare_demo_workspace, send_followup,
)


class OnboardingNegativeControlTests(unittest.TestCase):
    def setUp(self):
        self.valid = {
            "workspace_id": "demo-hvac-001",
            "industry": "hvac",
            "synthetic": True,
            "consent_mode": "manual_review_only",
        }

    def test_reject_malformed_workspace_identifiers(self):
        for identifier in (
            "demo-", "demo-../secret", "demo-abc/def", "demo-abc\\def",
            "demo-abc def", "demo-é", "demo-💳", "demo-" + "a" * 60,
            "demo-abc\n", 123, None,
        ):
            with self.subTest(identifier=repr(identifier)):
                with self.assertRaises(OnboardingError):
                    prepare_demo_workspace({**self.valid, "workspace_id": identifier})

    def test_reject_unexpected_private_or_live_fields(self):
        for field in ("email", "phone", "customer_name", "api_key",
                      "provider_token", "billing_enabled", "send_enabled"):
            with self.subTest(field=field):
                with self.assertRaises(OnboardingError):
                    prepare_demo_workspace({**self.valid, field: "synthetic-placeholder"})

    def test_reject_nonboolean_synthetic_and_unapproved_modes(self):
        for value in (1, "true", None, False):
            with self.subTest(synthetic=repr(value)):
                with self.assertRaises(OnboardingError):
                    prepare_demo_workspace({**self.valid, "synthetic": value})
        for mode in ("auto_send", "consent_verified", "", None):
            with self.subTest(mode=repr(mode)):
                with self.assertRaises(OnboardingError):
                    prepare_demo_workspace({**self.valid, "consent_mode": mode})

    def test_price_parser_rejects_coercion_and_out_of_bounds(self):
        for price in (True, 700, 700.0, None, "1e2", "00.01", "+1",
                      "0", "0.00", "10000.01", "100000", "1.234",
                      "NaN", "Infinity", " 700", "700\n", "７００"):
            with self.subTest(price=repr(price)):
                with self.assertRaises(OnboardingError):
                    draft_subscription_quote(price)

    def test_quote_never_grants_payment_or_send_permission(self):
        for price in ("0.01", "700", "10000.00"):
            with self.subTest(price=price):
                quote = draft_subscription_quote(price)
                self.assertTrue(quote["synthetic"])
                self.assertTrue(quote["nonbinding"])
                self.assertEqual(quote["billing_status"], "disabled")
                self.assertIsNone(quote["invoice_id"])
                self.assertIsNone(quote["payment_receipt"])
                self.assertIs(quote["send_enabled"], False)

    def test_external_side_effect_entrypoints_always_deny(self):
        for operation in (activate_billing, send_followup):
            with self.subTest(operation=operation.__name__):
                with self.assertRaises(PermissionError):
                    operation("demo-hvac-001", amount="700", approved=True)


if __name__ == "__main__":
    unittest.main()
