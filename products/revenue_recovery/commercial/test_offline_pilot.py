"""Commercial-only regressions for offline onboarding; no third-party services."""
from __future__ import annotations

import json
import unittest

from backend.onboarding import OnboardingError, activate_billing, draft_subscription_quote, send_followup
from commercial.demo_readiness import REQUIRED_CHECKS
from commercial.offline_pilot import build_offline_pilot_plan

WORKSPACE = {
    "workspace_id": "demo-hvac-001",
    "industry": "hvac",
    "synthetic": True,
    "consent_mode": "manual_review_only",
}
APPROVED_DEMO_CHECKS = dict.fromkeys(REQUIRED_CHECKS, True)


class OfflinePilotTests(unittest.TestCase):
    def test_mock_ports_are_preview_only_with_no_connected_services(self):
        plan = build_offline_pilot_plan(WORKSPACE, APPROVED_DEMO_CHECKS)
        self.assertEqual(plan["demo_readiness"], "offline_demo_ready")
        self.assertTrue(plan["synthetic"])
        self.assertFalse(plan["pilot_ready"])
        self.assertTrue(plan["human_review_required"])
        for key in (
            "live_customer_onboarding_enabled", "outreach_enabled",
            "calendar_booking_enabled", "crm_writes_enabled", "billing_enabled",
        ):
            self.assertIs(plan[key], False, key)
        for adapter in plan["integrations"].values():
            self.assertEqual(adapter["port"], "mock")
            self.assertTrue(adapter["preview_available"])
            self.assertFalse(adapter["connected"])
            self.assertFalse(adapter["live_read_enabled"])
            self.assertFalse(adapter["live_write_enabled"])
        self.assertEqual(plan["quote"]["billing_status"], "disabled")
        self.assertIsNone(plan["quote"]["payment_receipt"])
        self.assertIsNone(plan["verified_customer_count"])
        self.assertIsNone(plan["verified_receipts_usd"])
        self.assertIsNone(plan["verified_monthly_net_profit_usd"])

    def test_disabled_ports_remain_unavailable(self):
        plan = build_offline_pilot_plan(
            WORKSPACE, APPROVED_DEMO_CHECKS,
            crm_port="disabled", email_port="disabled", calendar_port="disabled",
        )
        for port in plan["integrations"].values():
            self.assertFalse(port["preview_available"])
            self.assertFalse(port["connected"])

    def test_incomplete_demo_checklist_blocks_readiness(self):
        checks = {**APPROVED_DEMO_CHECKS, "human_approval_policy_reviewed": False}
        plan = build_offline_pilot_plan(WORKSPACE, checks)
        self.assertEqual(plan["demo_readiness"], "blocked")
        self.assertEqual(plan["missing_checks"], ["human_approval_policy_reviewed"])
        self.assertFalse(plan["outreach_enabled"])

    def test_reject_unknown_or_live_ports_and_config_objects(self):
        for value in ("smtp", "gmail", "stripe", "production", True, None, {}, 1):
            with self.subTest(value=value), self.assertRaises(OnboardingError):
                build_offline_pilot_plan(WORKSPACE, APPROVED_DEMO_CHECKS, email_port=value)

    def test_reject_real_data_or_extra_fields(self):
        for changes in (
            {"synthetic": False},
            {"industry": "plumbing"},
            {"customer_email": "not-real@example.invalid"},
            {"workspace_id": "acme-company"},
        ):
            with self.subTest(changes=changes), self.assertRaises(OnboardingError):
                build_offline_pilot_plan({**WORKSPACE, **changes}, APPROVED_DEMO_CHECKS)

    def test_reject_missing_or_truthy_checklist_approvals(self):
        with self.assertRaises(OnboardingError):
            build_offline_pilot_plan(WORKSPACE, {})
        with self.assertRaises(OnboardingError):
            build_offline_pilot_plan(
                WORKSPACE, {**APPROVED_DEMO_CHECKS, "human_approval_policy_reviewed": "yes"}
            )

    def test_reject_unbounded_and_noncanonical_quote_inputs(self):
        for value in (
            "1E+999999", "9" * 1024, "NaN", "Inf", "0", "-1", "+700",
            "000700", " 700.00", "700.000", "10000.01", 700, 700.0,
            None, True,
        ):
            with self.subTest(value=str(value)[:40]), self.assertRaises(OnboardingError):
                draft_subscription_quote(value)

    def test_valid_bounded_quotes_preserve_disabled_billing(self):
        for entered, expected in (
            ("0.01", "0.01"), ("700", "700.00"),
            ("700.5", "700.50"), ("10000.00", "10000.00"),
        ):
            with self.subTest(entered=entered):
                quote = draft_subscription_quote(entered)
                self.assertEqual(quote["monthly_price_usd"], expected)
                self.assertTrue(quote["nonbinding"])
                self.assertEqual(quote["billing_status"], "disabled")
                self.assertIsNone(quote["invoice_id"])

    def test_serializable_deterministic_safe_plan(self):
        first = build_offline_pilot_plan(WORKSPACE, APPROVED_DEMO_CHECKS)
        second = build_offline_pilot_plan(WORKSPACE, APPROVED_DEMO_CHECKS)
        self.assertEqual(first, second)
        data = json.dumps(first, sort_keys=True)
        self.assertNotIn("customer_email", data)
        self.assertNotIn("secret", data.lower())

    def test_external_actions_explicitly_denied(self):
        with self.assertRaises(PermissionError):
            activate_billing(plan={"synthetic": True})
        with self.assertRaises(PermissionError):
            send_followup(plan={"synthetic": True})


if __name__ == "__main__":
    unittest.main()
