"""Fail-closed synthetic onboarding boundary regressions (no external effects)."""
import unittest

from backend.onboarding import (
    OnboardingError, activate_billing, draft_subscription_quote,
    prepare_demo_workspace, send_followup,
)


class OnboardingBoundaryTests(unittest.TestCase):
    def setUp(self):
        self.valid = {
            "workspace_id": "demo-hvac-001",
            "industry": "hvac",
            "synthetic": True,
            "consent_mode": "manual_review_only",
        }

    def test_rejects_unexpected_contact_and_integration_fields(self):
        for field, value in (
            ("email", "person@example.invalid"),
            ("phone", "555-0100"),
            ("crm_token", "fake-secret"),
            ("billing_enabled", True),
            ("send_enabled", True),
            ("tenant_id", "demo-other"),
        ):
            with self.subTest(field=field), self.assertRaises(OnboardingError):
                prepare_demo_workspace({**self.valid, field: value})

    def test_rejects_unicode_lookalikes_and_unsafe_ids(self):
        for identifier in (
            "demo-", "demo-abc/def", "demo-abc.def",
            "demo-abc\n", "demo-é", "demo-K", "demo-ı",
            "demo-" + "a" * 60, "Demo-hvac", "demo-abc def",
        ):
            with self.subTest(identifier=repr(identifier)), self.assertRaises(OnboardingError):
                prepare_demo_workspace({**self.valid, "workspace_id": identifier})

    def test_rejects_nonobject_and_ambiguous_metadata(self):
        for payload in (None, [], "", 0, True, {"synthetic": True}):
            with self.subTest(payload=repr(payload)), self.assertRaises(OnboardingError):
                prepare_demo_workspace(payload)
        for patch in (
            {"synthetic": 1}, {"synthetic": "true"},
            {"industry": "plumbing"}, {"consent_mode": "auto_send"},
        ):
            with self.subTest(patch=patch), self.assertRaises(OnboardingError):
                prepare_demo_workspace({**self.valid, **patch})

    def test_quotes_are_hypotheses_and_never_receipts(self):
        for amount in ("0.01", "700", "700.00", "10000.00"):
            with self.subTest(amount=amount):
                quote = draft_subscription_quote(amount)
                self.assertTrue(quote["synthetic"])
                self.assertTrue(quote["nonbinding"])
                self.assertEqual(quote["billing_status"], "disabled")
                self.assertIsNone(quote["invoice_id"])
                self.assertIsNone(quote["payment_receipt"])
                self.assertFalse(quote["send_enabled"])
        for amount in (
            "0", "0.00", "10000.01", "01", "1e2", "NaN",
            "-1", "+1", "1.234", " 700", "700 ", "700\n",
            "７００", 700, 700.0, True, None, "9" * 10000,
        ):
            with self.subTest(amount=repr(amount)), self.assertRaises(OnboardingError):
                draft_subscription_quote(amount)

    def test_external_side_effect_entrypoints_always_deny(self):
        for fn in (activate_billing, send_followup):
            for args, kwargs in (((), {}), (("demo-hvac-001",), {}),
                                 ((), {"approved": True, "synthetic": True})):
                with self.subTest(fn=fn.__name__, args=args, kwargs=kwargs):
                    with self.assertRaises(PermissionError):
                        fn(*args, **kwargs)


if __name__ == "__main__":
    unittest.main()
