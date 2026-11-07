"""Regression coverage for inert synthetic onboarding previews."""
import unittest

from products.revenue_recovery.backend.onboarding import OnboardingError
from products.revenue_recovery.commercial.onboarding_preview import preview_demo_onboarding


def fixture():
    return {
        "workspace": {
            "workspace_id": "demo-hvac-01",
            "industry": "hvac",
            "synthetic": True,
            "consent_mode": "manual_review_only",
        },
        "monthly_price_usd": "700.00",
        "crm_port": "mock",
        "email_port": "disabled",
        "calendar_port": "mock",
    }


class OfflineOnboardingPreviewTests(unittest.TestCase):
    def test_preview_never_provisions_or_activates(self):
        result = preview_demo_onboarding(fixture())
        self.assertTrue(result["synthetic"])
        self.assertFalse(result["tenant_provisioned"])
        self.assertFalse(result["pilot_authorized"])
        self.assertFalse(result["outbound_enabled"])
        self.assertFalse(result["live_integrations_enabled"])
        self.assertEqual(result["billing_status"], "disabled")
        self.assertEqual(result["quote"]["billing_status"], "disabled")
        self.assertIsNone(result["verified_customers"])
        self.assertIsNone(result["verified_net_profit_usd"])

    def test_all_ports_disabled_allowed(self):
        request = fixture()
        for key in ("crm_port", "email_port", "calendar_port"):
            request[key] = "disabled"
        self.assertEqual(preview_demo_onboarding(request)["ports"]["crm_port"], "disabled")

    def test_live_port_values_denied(self):
        for key in ("crm_port", "email_port", "calendar_port"):
            for value in ("live", "smtp", "production", True, None, 1, "mock "):
                with self.subTest(key=key, value=value), self.assertRaises(OnboardingError):
                    request = fixture()
                    request[key] = value
                    preview_demo_onboarding(request)

    def test_unexpected_fields_and_missing_fields_denied(self):
        for extra in ("email", "phone", "customer_name", "api_key", "payment_receipt"):
            with self.subTest(extra=extra), self.assertRaises(OnboardingError):
                request = fixture()
                request[extra] = "example"
                preview_demo_onboarding(request)
        for missing in fixture():
            with self.subTest(missing=missing), self.assertRaises(OnboardingError):
                request = fixture()
                del request[missing]
                preview_demo_onboarding(request)

    def test_non_synthetic_workspace_denied(self):
        for value in (False, 1, "true", None):
            with self.subTest(value=value), self.assertRaises(OnboardingError):
                request = fixture()
                request["workspace"]["synthetic"] = value
                preview_demo_onboarding(request)

    def test_real_contact_workspace_metadata_denied(self):
        request = fixture()
        request["workspace"]["contact_email"] = "example"
        with self.assertRaises(OnboardingError):
            preview_demo_onboarding(request)

    def test_price_and_type_bounds_denied(self):
        for value in ("0", "-1", "NaN", "10000.01", "1e3", 700, True, None):
            with self.subTest(value=value), self.assertRaises(OnboardingError):
                request = fixture()
                request["monthly_price_usd"] = value
                preview_demo_onboarding(request)
        for value in (None, [], "hello", 5):
            with self.subTest(value=value), self.assertRaises(OnboardingError):
                preview_demo_onboarding(value)


if __name__ == "__main__":
    unittest.main()
