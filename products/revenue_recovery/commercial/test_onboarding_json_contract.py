"""Offline onboarding JSON contract and nested-mutation regression checks.

Synthetic-only; no network, credentials, tenant provisioning or payments.
"""
import json
import unittest

from products.revenue_recovery.backend.onboarding import OnboardingError
from products.revenue_recovery.commercial.onboarding_preview import preview_demo_onboarding


def request_fixture():
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


class OnboardingJsonContractTests(unittest.TestCase):
    def test_round_trip_preserves_unknown_financial_evidence_and_no_activation(self):
        result = json.loads(json.dumps(preview_demo_onboarding(request_fixture())))
        self.assertTrue(result["synthetic"])
        self.assertIsNone(result["verified_customers"])
        self.assertIsNone(result["verified_net_profit_usd"])
        for key in ("outbound_enabled", "live_integrations_enabled",
                    "tenant_provisioned", "pilot_authorized"):
            self.assertIs(result[key], False)
        self.assertEqual(result["billing_status"], "disabled")
        self.assertEqual(result["quote"]["billing_status"], "disabled")
        self.assertEqual(result["ports"],
                         {"crm_port": "mock", "email_port": "disabled",
                          "calendar_port": "mock"})

    def test_nested_workspace_injection_fails_closed(self):
        for field, value in (
            ("email", "not-a-real-contact"),
            ("phone", "not-a-real-number"),
            ("api_key", "not-a-real-key"),
            ("tenant_id", "tenant-live"),
            ("payment_method", "card"),
            ("billing_enabled", True),
        ):
            with self.subTest(field=field):
                request = request_fixture()
                request["workspace"][field] = value
                with self.assertRaises(OnboardingError):
                    preview_demo_onboarding(request)

    def test_workspace_wrong_types_fail_closed(self):
        for value in (None, [], "", True, 42):
            with self.subTest(value=value):
                request = request_fixture()
                request["workspace"] = value
                with self.assertRaises(OnboardingError):
                    preview_demo_onboarding(request)


if __name__ == "__main__":
    unittest.main()
