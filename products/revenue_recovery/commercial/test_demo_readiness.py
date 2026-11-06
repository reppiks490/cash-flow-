"""Negative and positive checks for synthetic-only commercial readiness."""
import unittest

from backend.onboarding import OnboardingError
from commercial.demo_readiness import REQUIRED_CHECKS, evaluate_demo_readiness, preview_demo_offer

WORKSPACE = {
    "workspace_id": "demo-hvac-001",
    "industry": "hvac",
    "synthetic": True,
    "consent_mode": "manual_review_only",
}


class DemoReadinessTests(unittest.TestCase):
    def test_complete_checklist_still_disables_every_external_action(self):
        result = preview_demo_offer(WORKSPACE, dict.fromkeys(REQUIRED_CHECKS, True))
        self.assertEqual(result["readiness"], "offline_demo_ready")
        self.assertFalse(result["billing_enabled"])
        self.assertFalse(result["outreach_enabled"])
        self.assertFalse(result["crm_writes_enabled"])
        self.assertEqual(result["quote"]["billing_status"], "disabled")
        self.assertIsNone(result["quote"]["payment_receipt"])

    def test_missing_approval_blocks_demo(self):
        checks = dict.fromkeys(REQUIRED_CHECKS, True)
        checks["human_approval_policy_reviewed"] = False
        result = evaluate_demo_readiness(WORKSPACE, checks)
        self.assertEqual(result.status, "blocked")
        self.assertEqual(result.missing_checks, ("human_approval_policy_reviewed",))

    def test_missing_or_extra_checks_rejected(self):
        for checks in ({}, dict.fromkeys(REQUIRED_CHECKS[:-1], True),
                       {**dict.fromkeys(REQUIRED_CHECKS, True), "send_enabled": True}):
            with self.subTest(checks=checks), self.assertRaises(OnboardingError):
                evaluate_demo_readiness(WORKSPACE, checks)

    def test_truthy_strings_and_numbers_are_not_approvals(self):
        for value in ("true", 1, None):
            checks = dict.fromkeys(REQUIRED_CHECKS, True)
            checks["human_approval_policy_reviewed"] = value
            with self.subTest(value=value), self.assertRaises(OnboardingError):
                evaluate_demo_readiness(WORKSPACE, checks)

    def test_real_data_and_unknown_industry_rejected(self):
        for patch in ({"synthetic": False}, {"industry": "roofing"},
                      {"customer_email": "person@example.invalid"}):
            with self.subTest(patch=patch), self.assertRaises(OnboardingError):
                evaluate_demo_readiness({**WORKSPACE, **patch},
                                        dict.fromkeys(REQUIRED_CHECKS, True))

    def test_invalid_price_rejected(self):
        with self.assertRaises(OnboardingError):
            preview_demo_offer(WORKSPACE, dict.fromkeys(REQUIRED_CHECKS, True), "NaN")


if __name__ == "__main__":
    unittest.main()
