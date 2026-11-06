"""Test opt-out simulation and read-only policy route without external systems."""
import http.client
import json
import threading
import unittest
from http.server import ThreadingHTTPServer

from backend.app import DemoStore, make_handler
from backend.consent_simulation import POLICY_SCENARIOS, simulate_contact_policy


def lead(ref="DEMO-POLICY-01"):
    return {"synthetic": True, "external_ref": ref, "source": "website",
            "need": "estimate follow-up", "status": "received"}


class ConsentSimulationTests(unittest.TestCase):
    def test_unknown_consent_is_review_only_and_cannot_send(self):
        data = simulate_contact_policy(lead(), "unknown")
        self.assertFalse(data["consent_verified"])
        self.assertFalse(data["may_contact_real_person"])
        self.assertFalse(data["operator_authorized"])
        self.assertFalse(data["actual_message_sent"])
        self.assertTrue(data["review_required"])
        self.assertEqual(data["draft_status"], "pending_human_review")
        self.assertIn("consent_and_suppression_unknown", data["reasons"])

    def test_mock_revocation_suppresses_even_internal_draft(self):
        state = simulate_contact_policy(lead(), "revoked_mock")
        self.assertTrue(state["suppressed"])
        self.assertIsNone(state["draft"])
        self.assertEqual(state["draft_status"], "suppressed")
        self.assertIn("synthetic_opt_out_revocation", state["reasons"])
        self.assertFalse(state["may_contact_real_person"])

    def test_mock_consent_does_not_grant_real_outreach(self):
        state = simulate_contact_policy(lead(), "consent_record_mock")
        self.assertIsNotNone(state["draft"])
        self.assertFalse(state["consent_verified"])
        self.assertFalse(state["may_contact_real_person"])
        self.assertIsNone(state["recipient_address"])
        self.assertIn("mock_consent_record_not_verified", state["reasons"])
        self.assertFalse(state["actual_message_sent"])

    def test_invalid_modes_and_pii_rejected(self):
        self.assertEqual(POLICY_SCENARIOS, {"unknown", "revoked_mock", "consent_record_mock"})
        for mode in ("approved", "sent", "verified", "live", 0, None, True):
            with self.subTest(mode=mode), self.assertRaises(ValueError):
                simulate_contact_policy(lead(), mode)
        for patch in ({"email": "someone@example.invalid"}, {"synthetic": False},
                      {"external_ref": "real-5551234567"}):
            with self.subTest(patch=patch), self.assertRaises(ValueError):
                simulate_contact_policy({**lead(), **patch})

    def test_http_policy_is_read_only_and_unknown_modes_fail(self):
        server = ThreadingHTTPServer(("127.0.0.1", 0), make_handler(DemoStore()))
        worker = threading.Thread(target=server.serve_forever, daemon=True)
        worker.start()
        def request(method, path, payload=None):
            conn = http.client.HTTPConnection("127.0.0.1", server.server_port, timeout=5)
            headers = {}
            if payload is not None:
                headers["Content-Type"] = "application/json"
                payload = json.dumps(payload).encode("utf-8")
            try:
                conn.request(method, path, payload, headers)
                response = conn.getresponse()
                return response.status, json.loads(response.read())
            finally:
                conn.close()
        try:
            self.assertEqual(request("POST", "/api/demo/leads", {k:v for k,v in lead().items()
                              if k != "status"})[0], 201)
            for state in POLICY_SCENARIOS:
                code, data = request("GET", "/api/demo/policy/DEMO-POLICY-01/" + state)
                self.assertEqual(code, 200)
                self.assertTrue(data["policy"]["synthetic"])
                self.assertFalse(data["policy"]["may_contact_real_person"])
                self.assertFalse(data["policy"]["actual_message_sent"])
                if state == "revoked_mock":
                    self.assertIsNone(data["policy"]["draft"])
            for path in ("/api/demo/policy/DEMO-POLICY-01/approved",
                         "/api/demo/policy/DEMO-UNLISTED/revoked_mock",
                         "/api/demo/policy/DEMO-POLICY-01/revoked_mock/../../"):
                self.assertEqual(request("GET", path)[0], 404)
            self.assertEqual(request("POST",
                "/api/demo/policy/DEMO-POLICY-01/consent_record_mock",
                {"synthetic":True})[0], 404)
        finally:
            server.shutdown()
            server.server_close()
            worker.join(timeout=5)


if __name__ == "__main__":
    unittest.main()
