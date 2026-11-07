"""Adversarial synthetic-only consent, provenance, and revenue API acceptance.

Run from repository root with the product PYTHONPATH:
    PYTHONPATH=products/revenue_recovery python -m unittest discover -s products/revenue_recovery/tests -p 'test_policy_attribution_negative.py' -v

These tests establish LOCAL DEMO invariants, not tenant auth, legally valid
consent, authenticated receipts, or production readiness. No external calls.
"""
import http.client
import json
import threading
import unittest
from http.server import ThreadingHTTPServer

from backend.app import DemoStore, make_handler


class PolicyAttributionNegativeTests(unittest.TestCase):
    def setUp(self):
        self.store = DemoStore()
        self.server = ThreadingHTTPServer(("127.0.0.1", 0), make_handler(self.store))
        self.worker = threading.Thread(target=self.server.serve_forever, daemon=True)
        self.worker.start()
        self.addCleanup(self.close_server)

    def close_server(self):
        self.server.shutdown()
        self.server.server_close()
        self.worker.join(timeout=5)

    def request(self, method, path, body=None, headers=None):
        connection = http.client.HTTPConnection(
            "127.0.0.1", self.server.server_port, timeout=5
        )
        http_headers = dict(headers or {})
        if body is not None and not isinstance(body, bytes):
            body = json.dumps(body).encode("utf-8")
            http_headers.setdefault("Content-Type", "application/json")
        try:
            connection.request(method, path, body=body, headers=http_headers)
            response = connection.getresponse()
            payload = response.read()
            return response.status, json.loads(payload)
        finally:
            connection.close()

    @staticmethod
    def sample():
        return {
            "synthetic": True,
            "external_ref": "QA-POLICY-NEG-01",
            "source": "website",
            "need": "repair",
        }

    def seed(self):
        status, data = self.request("POST", "/api/demo/leads", self.sample())
        self.assertEqual(status, 201)
        self.assertTrue(data["created"])

    def test_unknown_mock_consent_and_revoked_never_authorize_contact(self):
        self.seed()
        for mode in ("unknown", "consent_record_mock", "revoked_mock"):
            with self.subTest(mode=mode):
                code, response = self.request(
                    "GET", "/api/demo/policy/QA-POLICY-NEG-01/" + mode
                )
                self.assertEqual(code, 200)
                policy = response["policy"]
                self.assertTrue(response["synthetic"])
                self.assertTrue(policy["synthetic"])
                self.assertEqual(policy["mode"], mode)
                self.assertFalse(policy["consent_verified"])
                self.assertFalse(policy["operator_authorized"])
                self.assertFalse(policy["may_contact_real_person"])
                self.assertFalse(policy["actual_message_sent"])
                self.assertIsNone(policy["recipient_address"])
                self.assertTrue(policy["review_required"])
                self.assertIn("prototype_transport_disabled", policy["reasons"])
                if mode == "revoked_mock":
                    self.assertTrue(policy["suppressed"])
                    self.assertIsNone(policy["draft"])
                    self.assertEqual(policy["draft_status"], "suppressed")
                else:
                    self.assertFalse(policy["suppressed"])
                    self.assertEqual(policy["draft_status"], "pending_human_review")

    def test_revocation_is_fixture_scoped_not_persisted_approval(self):
        self.seed()
        status, result = self.request(
            "GET", "/api/demo/policy/QA-POLICY-NEG-01/revoked_mock"
        )
        self.assertEqual(status, 200)
        self.assertIsNone(result["policy"]["draft"])
        # A separate preview is still an UNSENT fixture. Revocation is NOT
        # stored; this gap must block all production contact workflows.
        status, result = self.request(
            "GET", "/api/demo/recovery/QA-POLICY-NEG-01"
        )
        self.assertEqual(status, 200)
        preview = result["preview"]
        self.assertFalse(preview["followup"]["approved"])
        self.assertFalse(preview["followup"]["transmitted"])
        self.assertFalse(preview["qualification"]["consent_verified"])
        self.assertTrue(preview["crm"]["dry_run"])
        self.assertFalse(preview["appointment"]["confirmed"])
        self.assertEqual(preview["attribution"]["verified_payment_receipts"], 0)

    def test_unauthorized_mutations_and_fake_payment_routes_are_absent(self):
        self.seed()
        before = self.request("GET", "/api/demo/scorecard")[1]
        for route in (
            "/api/demo/policy/QA-POLICY-NEG-01/consent_record_mock",
            "/api/demo/scenarios/QA-POLICY-NEG-01/closed_job_mock",
            "/api/demo/scorecard",
            "/api/demo/send",
            "/api/demo/approve",
            "/api/demo/book",
            "/api/payments",
            "/api/webhooks/payments",
            "/api/attribution/verify",
        ):
            with self.subTest(route=route):
                status, _ = self.request(
                    "POST", route, {
                        "synthetic": True,
                        "verified_payment_receipts": 9,
                        "verified_recovered_revenue_cents": 999999,
                    }
                )
                self.assertEqual(status, 404)
        after = self.request("GET", "/api/demo/scorecard")[1]
        self.assertEqual(after, before)
        self.assertEqual(after["verified"]["payment_receipts"], 0)
        self.assertIsNone(after["counts"]["real_customers"])

    def test_mock_closed_job_never_becomes_payment_or_appointment(self):
        self.seed()
        status, result = self.request(
            "GET", "/api/demo/scenarios/QA-POLICY-NEG-01/closed_job_mock"
        )
        self.assertEqual(status, 200)
        scenario = result["scenario"]
        self.assertTrue(scenario["synthetic"])
        self.assertEqual(scenario["metrics"]["mock_closed_jobs"], 1)
        for metric in (
            "actual_messages_sent",
            "actual_bookings_confirmed",
            "actual_jobs_closed",
            "verified_contractor_collections_cents",
            "verified_recovered_revenue_cents",
            "verified_rre_subscription_revenue_cents",
            "verified_payment_receipts",
        ):
            with self.subTest(metric=metric):
                self.assertEqual(scenario["metrics"][metric], 0)
        self.assertFalse(scenario["attribution"]["authenticated_payment_evidence"])
        self.assertFalse(scenario["gates"]["human_approval_authenticated"])
        for event in scenario["events"]:
            self.assertIsNone(event["provider_receipt"])
            self.assertFalse(event["source_evidence_verified"])
            self.assertFalse(event["timestamp_verified"])
            self.assertFalse(event["external_side_effect"])

    def test_malformed_policy_paths_and_tenant_claims_fail_closed(self):
        self.seed()
        for path in (
            "/api/demo/policy/QA-POLICY-NEG-01/approved",
            "/api/demo/policy/QA-POLICY-NEG-01/revoked_mock/extra",
            "/api/demo/policy/QA-POLICY-NEG-01/paid",
            "/api/demo/policy/QA-NONEXISTENT/revoked_mock",
            "/api/demo/scenarios/QA-POLICY-NEG-01/verified_payment",
            "/api/tenants/demo/records",
            "/api/auth/login",
        ):
            with self.subTest(path=path):
                self.assertEqual(self.request("GET", path)[0], 404)
        malicious_tenant = {**self.sample(), "tenant_id": "other-tenant"}
        self.assertEqual(self.request("POST", "/api/demo/leads", malicious_tenant)[0], 400)
        # No auth model exists; an unauthenticated GET returning demo fixtures
        # is deliberately classified as a production blocker, NOT auth proof.
        self.assertEqual(self.request("GET", "/api/demo/leads")[0], 200)
        self.assertEqual(len(self.store.list()), 1)

    def test_rejected_pii_and_forged_receipts_do_not_persist_or_echo(self):
        for patch in (
            {"email": "qa-fixture@example.invalid"},
            {"phone": "5550109999"},
            {"receipt_id": "fake-provider-receipt"},
            {"paid_cents": 250000},
            {"need": "call 5550109999"},
            {"synthetic": False},
        ):
            with self.subTest(patch=patch):
                status, response = self.request(
                    "POST", "/api/demo/leads", {**self.sample(), **patch}
                )
                self.assertEqual(status, 400)
                self.assertNotIn("qa-fixture@example.invalid", json.dumps(response))
                self.assertNotIn("5550109999", json.dumps(response))
                self.assertEqual(self.store.list(), [])


if __name__ == "__main__":
    unittest.main()
