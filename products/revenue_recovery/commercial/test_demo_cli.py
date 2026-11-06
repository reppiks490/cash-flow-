"""CLI-only offline HVAC onboarding tests. No network or stored inputs."""
import contextlib
import io
import json
import unittest

from commercial.demo_cli import main
from commercial.demo_readiness import REQUIRED_CHECKS


def invoke(args):
    out, err = io.StringIO(), io.StringIO()
    with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
        result = main(args)
    return result, out.getvalue(), err.getvalue()


class DemoCLIRegressionTests(unittest.TestCase):
    def test_unreviewed_by_default_and_never_live(self):
        status, output, err = invoke([])
        self.assertEqual(status, 0)
        self.assertEqual(err, "")
        plan = json.loads(output)
        self.assertEqual(plan["demo_readiness"], "blocked")
        self.assertEqual(set(plan["missing_checks"]), set(REQUIRED_CHECKS))
        self.assertFalse(plan["pilot_ready"])
        self.assertFalse(plan["billing_enabled"])
        self.assertFalse(plan["outreach_enabled"])
        self.assertFalse(plan["calendar_booking_enabled"])
        self.assertFalse(plan["crm_writes_enabled"])

    def test_checks_enable_only_offline_preview(self):
        reviewed = [x for name in REQUIRED_CHECKS for x in ("--check", name)]
        status, output, _ = invoke(reviewed)
        self.assertEqual(status, 0)
        plan = json.loads(output)
        self.assertEqual(plan["demo_readiness"], "offline_demo_ready")
        self.assertEqual(plan["missing_checks"], [])
        self.assertTrue(plan["human_review_required"])
        self.assertFalse(plan["pilot_ready"])
        self.assertFalse(plan["outreach_enabled"])
        self.assertFalse(plan["billing_enabled"])
        self.assertIsNone(plan["verified_receipts_usd"])

    def test_disabled_ports_preview_nothing(self):
        status, output, _ = invoke([
            "--crm-port", "disabled", "--email-port", "disabled",
            "--calendar-port", "disabled",
        ])
        self.assertEqual(status, 0)
        for value in json.loads(output)["integrations"].values():
            self.assertFalse(value["preview_available"])
            self.assertFalse(value["connected"])

    def test_invalid_mock_port_fails_without_echo(self):
        status, output, error = invoke(["--crm-port", "live-credentials"])
        self.assertEqual(status, 2)
        self.assertEqual(output, "")
        self.assertIn("Rejected", error)
        self.assertNotIn("live-credentials", error)

    def test_invalid_price_fails_without_echo(self):
        status, output, error = invoke(["--monthly-price", "1E999999"])
        self.assertEqual(status, 2)
        self.assertEqual(output, "")
        self.assertIn("Rejected", error)
        self.assertNotIn("1E999999", error)

    def test_invalid_workspace_id_fails_without_echo(self):
        status, output, error = invoke(["--workspace-id", "person@example.invalid"])
        self.assertEqual(status, 2)
        self.assertEqual(output, "")
        self.assertIn("Rejected", error)
        self.assertNotIn("person@example.invalid", error)

    def test_unknown_check_never_grants_approval(self):
        status, output, error = invoke(["--check", "approved_for_live_send"])
        self.assertEqual(status, 2)
        self.assertEqual(output, "")
        self.assertIn("unknown synthetic demo checklist", error)


if __name__ == "__main__":
    unittest.main()
