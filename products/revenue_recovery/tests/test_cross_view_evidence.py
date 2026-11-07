"""Cross-view QA acceptance: mock HVAC workflow never becomes operational evidence.

This is a local, synthetic-only characterization suite. The policy endpoint
does NOT persist consent/revocation, and the HTTP demo has NO authenticated
tenant boundary. Passing tests must never be interpreted as pilot authorization.

Run from repository root:
    PYTHONPATH=products/revenue_recovery python -m unittest discover \
      -s products/revenue_recovery/tests -p 'test_cross_view_evidence.py' -v
"""
import http.client
import json
import threading
import unittest
from http.server import ThreadingHTTPServer

from backend.app import DemoStore, make_handler


def synthetic_lead(ref, need="repair"):
    return {
        "synthetic": True, "external_ref": ref,
        "source": "website", "need": need,
    }


class CrossViewEvidenceTests(unittest.TestCase):
    def setUp(self):
        self.store = DemoStore()
        self.server = ThreadingHTTPServer(("127.0.0.1", 0), make_handler(self.store))
        self.worker = threading.Thread(target=self.server.serve_forever, daemon=True)
        self.worker.start()

    def tearDown(self):
        self.server.shutdown()
        self.server.server_close()
        self.worker.join(timeout=5)

    def request(self, method, route, data=None, headers=None):
        client = http.client.HTTPConnection(
            "127.0.0.1", self.server.server_port, timeout=5
        )
        options = dict(headers or {})
        if data is not None:
            data = json.dumps(data).encode("utf-8")
            options.setdefault("Content-Type", "application/json")
        try:
            client.request(method, route, body=data, headers=options)
            response = client.getresponse()
            self.assertIn("no-store", response.getheader("Cache-Control", ""))
            return response.status, json.loads(response.read())
        finally:
            client.close()

    def test_mock_job_closure_never_changes_authoritative_scorecard(self):
        ref = "QA-CROSS-CLOSE"
        self.assertEqual(self.request("POST", "/api/demo/leads", synthetic_lead(ref))[0], 201)
        before = self.request("GET", "/api/demo/scorecard")[1]
        code, response = self.request(
            "GET", f"/api/demo/scenarios/{ref}/closed_job_mock"
        )
        self.assertEqual(code, 200)
        scenario = response["scenario"]
        self.assertTrue(scenario["synthetic"])
        self.assertEqual(scenario["metrics"]["mock_closed_jobs"], 1)
        self.assertEqual(scenario["metrics"]["actual_jobs_closed"], 0)
        self.assertEqual(scenario["metrics"]["actual_bookings_confirmed"], 0)
        self.assertEqual(scenario["metrics"]["verified_payment_receipts"], 0)
        self.assertFalse(scenario["attribution"]["authenticated_payment_evidence"])
        for event in scenario["events"]:
            with self.subTest(event=event["event_type"]):
                self.assertFalse(event["external_side_effect"])
                self.assertFalse(event["source_evidence_verified"])
                self.assertFalse(event["operator_action_authenticated"])
                self.assertIsNone(event["provider_receipt"])
        after = self.request("GET", "/api/demo/scorecard")[1]
        self.assertEqual(after, before)
        self.assertEqual(after["verified"]["rre_monthly_profit_cents"], 0)
        self.assertEqual(after["verified"]["payment_receipts"], 0)
        self.assertIsNone(after["counts"]["real_customers"])

    def test_revocation_mock_is_read_only_and_does_not_authorize_recovery(self):
        ref = "QA-CROSS-REVOKE"
        self.assertEqual(self.request("POST", "/api/demo/leads", synthetic_lead(ref))[0], 201)
        code, policy_response = self.request(
            "GET", f"/api/demo/policy/{ref}/revoked_mock"
        )
        self.assertEqual(code, 200)
        policy = policy_response["policy"]
        self.assertTrue(policy["suppressed"])
        self.assertIsNone(policy["draft"])
        self.assertEqual(policy["draft_status"], "suppressed")
        self.assertFalse(policy["consent_verified"])
        self.assertFalse(policy["operator_authorized"])
        self.assertFalse(policy["may_contact_real_person"])
        self.assertFalse(policy["actual_message_sent"])
        self.assertIsNone(policy["recipient_address"])
        # The policy is a stateless fixture, NOT a durable suppression record.
        code, recovery_response = self.request("GET", f"/api/demo/recovery/{ref}")
        self.assertEqual(code, 200)
        recovery = recovery_response["preview"]
        self.assertFalse(recovery["followup"]["approved"])
        self.assertFalse(recovery["followup"]["transmitted"])
        self.assertFalse(recovery["qualification"]["consent_verified"])
        self.assertFalse(recovery["crm"]["transmitted"])
        self.assertFalse(recovery["appointment"]["confirmed"])
        self.assertEqual(self.store.get(ref)["status"], "received")

    def test_replay_and_conflict_cannot_mint_mock_cash_or_extra_leads(self):
        ref = "QA-CROSS-REPLAY"
        row = synthetic_lead(ref, "estimate follow-up")
        self.assertEqual(self.request("POST", "/api/demo/leads", row)[0], 201)
        status, result = self.request("POST", "/api/demo/leads", row)
        self.assertEqual(status, 200)
        self.assertFalse(result["created"])
        self.assertEqual(
            self.request("POST", "/api/demo/leads", {**row, "need": "repair"})[0],
            409,
        )
        self.assertEqual(
            self.request("GET", f"/api/demo/scenarios/{ref}/closed_job_mock")[0],
            200,
        )
        score = self.request("GET", "/api/demo/scorecard")[1]
        self.assertEqual(score["counts"]["received_demo_leads"], 1)
        self.assertEqual(score["verified"]["payment_receipts"], 0)
        self.assertEqual(score["verified"]["contractor_recovered_revenue_cents"], 0)
        self.assertEqual(len(self.store.list()), 1)
        self.assertEqual(self.store.get(ref)["need"], "estimate follow-up")

    def test_forged_payment_fields_and_auth_headers_cannot_change_demo_state(self):
        ref = "QA-CROSS-FORGE"
        base = synthetic_lead(ref)
        for mutation in (
            {"payment_receipt": "mock"},
            {"verified_collected_revenue_usd": "999.00"},
            {"status": "paid"},
            {"tenant_id": "DEMO-TENANT-OTHER"},
            {"recipient_address": "not-a-recipient"},
        ):
            with self.subTest(mutation=mutation):
                self.assertEqual(
                    self.request("POST", "/api/demo/leads", {**base, **mutation})[0],
                    400,
                )
        self.assertEqual(self.store.list(), [])
        for route in (
            f"/api/demo/recovery/{ref}",
            f"/api/demo/scenarios/{ref}/closed_job_mock",
            f"/api/demo/policy/{ref}/revoked_mock",
        ):
            with self.subTest(route=route):
                self.assertEqual(self.request("GET", route)[0], 404)
        forged = {"Authorization": "Bearer synthetic-not-a-token"}
        for route in ("/api/tenants", "/api/demo/send", "/api/payments"):
            with self.subTest(route=route):
                self.assertEqual(self.request("POST", route, {}, headers=forged)[0], 404)
        self.assertEqual(self.request("GET", "/api/demo/scorecard")[1]["verified"]["payment_receipts"], 0)


if __name__ == "__main__":
    unittest.main()
