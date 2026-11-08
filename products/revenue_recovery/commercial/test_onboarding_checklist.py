"""Synthetic-only onboarding checklist regressions."""
import unittest

from products.revenue_recovery.commercial.onboarding_checklist import assess_demo_onboarding

KEYS = (
    "demo_workspace_created", "synthetic_fixture_loaded",
    "operator_review_walkthrough", "no_send_verified",
    "billing_disabled_verified", "crm_dry_run_verified",
)


class OnboardingChecklistTests(unittest.TestCase):
    def test_empty_is_not_ready(self):
        result = assess_demo_onboarding({key: False for key in KEYS})
        self.assertFalse(result.demo_ready)
        self.assertEqual(len(result.missing), 6)

    def test_complete_is_demo_only(self):
        result = assess_demo_onboarding({key: True for key in KEYS})
        self.assertTrue(result.demo_ready)
        self.assertFalse(result.live_pilot_authorized)
        self.assertFalse(result.payment_enabled)
        self.assertFalse(result.outreach_enabled)

    def test_partial_is_not_ready(self):
        payload = {key: True for key in KEYS}
        payload["no_send_verified"] = False
        self.assertEqual(assess_demo_onboarding(payload).missing, ("no_send_verified",))

    def test_extra_field_fails_closed(self):
        with self.assertRaises(ValueError):
            assess_demo_onboarding(dict.fromkeys((*KEYS, "customer_email"), True))

    def test_missing_field_fails_closed(self):
        with self.assertRaises(ValueError):
            assess_demo_onboarding(dict.fromkeys(KEYS[:-1], True))

    def test_non_boolean_fails_closed(self):
        for invalid in (1, "true", None, [], {}):
            with self.subTest(invalid=invalid):
                payload = dict.fromkeys(KEYS, True)
                payload["no_send_verified"] = invalid
                with self.assertRaises(ValueError):
                    assess_demo_onboarding(payload)

    def test_wrong_container_fails_closed(self):
        for invalid in (None, [], "ready", True):
            with self.subTest(invalid=invalid):
                with self.assertRaises(ValueError):
                    assess_demo_onboarding(invalid)


if __name__ == "__main__":
    unittest.main()
