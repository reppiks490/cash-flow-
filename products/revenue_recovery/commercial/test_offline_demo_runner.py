"""Offline runner regression tests; no live providers or communications."""
import unittest
from unittest.mock import patch

from products.revenue_recovery.commercial.offline_demo_runner import (
    LEAD, execute_offline_demo,
)


class OfflineDemoRunnerTests(unittest.TestCase):
    def test_six_product_assertions_execute_without_claiming_verified_execution(self):
        result = execute_offline_demo()
        self.assertEqual(result["asserted_steps"], 6)
        self.assertTrue(result["synthetic_trace_shape_valid"])
        self.assertFalse(result["execution_independently_verified"])
        self.assertFalse(result["pilot_ready"])
        self.assertFalse(result["outreach_authorized"])
        self.assertFalse(result["billing_authorized"])
        self.assertIsNone(result["verified_revenue_cents"])

    def test_offline_runner_never_opens_socket_transport(self):
        """Fail immediately if a future dependency attempts a socket connection."""
        import socket

        attempts = []

        def deny(*args, **kwargs):
            attempts.append((args, kwargs))
            raise AssertionError("Outbound socket transport attempted")

        with patch.object(socket.socket, "connect", side_effect=deny), \
             patch.object(socket.socket, "connect_ex", side_effect=deny), \
             patch.object(socket, "create_connection", side_effect=deny):
            result = execute_offline_demo()

        self.assertEqual(attempts, [])
        self.assertTrue(result["synthetic_trace_shape_valid"])
        self.assertFalse(result["execution_independently_verified"])

    def test_offline_runner_rejects_unapproved_draft_send_flag(self):
        from backend.followups import prepare_followup
        unsafe = prepare_followup(LEAD)
        unsafe["send_enabled"] = True
        with patch(
            "products.revenue_recovery.commercial.offline_demo_runner.prepare_followup",
            return_value=unsafe,
        ):
            with self.assertRaises(AssertionError):
                execute_offline_demo()

    def test_revocation_failure_prevents_passing_trace(self):
        with patch(
            "products.revenue_recovery.commercial.offline_demo_runner.simulate_contact_policy",
            return_value={"suppressed": False, "draft": "unsafe",
                          "actual_message_sent": False, "may_contact_real_person": False},
        ):
            with self.assertRaises(AssertionError):
                execute_offline_demo()

    def test_crm_transmission_failure_prevents_passing_trace(self):
        with patch(
            "products.revenue_recovery.commercial.offline_demo_runner.preview_crm_envelope",
            return_value={"synthetic": True, "dry_run": True, "transmitted": True,
                          "provider_record_id": None, "appointment_confirmed": False},
        ):
            with self.assertRaises(AssertionError):
                execute_offline_demo()

    def test_receipt_forgery_prevents_passing_trace(self):
        from backend.demo_evidence import simulate_evidence_path
        forged = simulate_evidence_path(LEAD, "closed_job_mock")
        forged["metrics"]["verified_payment_receipts"] = 1
        with patch(
            "products.revenue_recovery.commercial.offline_demo_runner.simulate_evidence_path",
            return_value=forged,
        ):
            with self.assertRaises(AssertionError):
                execute_offline_demo()


if __name__ == "__main__":
    unittest.main()
