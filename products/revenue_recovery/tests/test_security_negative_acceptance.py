"""Adversarial release-gate tests. All payloads synthetic; no live integrations.

These tests intentionally document missing production capabilities by verifying
that the demo does not expose authenticated tenant, send, or payment endpoints.
Passing is NOT proof of tenant isolation or production security.
"""
import http.client
import json
import threading
import unittest
from http.server import ThreadingHTTPServer

from backend.app import DemoStore, make_handler


class SecurityNegativeAcceptanceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.server = ThreadingHTTPServer(("127.0.0.1", 0), make_handler(DemoStore()))
        cls.worker = threading.Thread(target=cls.server.serve_forever, daemon=True)
        cls.worker.start()

    @classmethod
    def tearDownClass(cls):
        cls.server.shutdown()
        cls.server.server_close()
        cls.worker.join(timeout=5)

    def request(self, method, path, payload=None, headers=None):
        conn = http.client.HTTPConnection("127.0.0.1", cls_port(self), timeout=5)
        h = dict(headers or {})
        if payload is not None and not isinstance(payload, bytes):
            payload = json.dumps(payload).encode("utf-8")
            h.setdefault("Content-Type", "application/json")
        try:
            conn.request(method, path, body=payload, headers=h)
            response = conn.getresponse()
            return response.status, dict(response.getheaders()), response.read()
        finally:
            conn.close()

    def test_rejects_pii_and_unbounded_categories(self):
        base = {"synthetic": True, "external_ref": "DEMO-QA-SEC-01",
                "source": "website", "need": "repair"}
        for mutation in (
            {"email": "nobody@example.invalid"},
            {"phone": "5550001111"},
            {"customer_name": "Synthetic Person"},
            {"need": "call me at 5550001111"},
            {"source": "customer-supplied"},
            {"external_ref": "5550001111"},
            {"external_ref": "DEMO-QA-SEC-01@example.invalid"},
            {"synthetic": False},
        ):
            with self.subTest(mutation=mutation):
                code, _, _ = self.request("POST", "/api/demo/leads", {**base, **mutation})
                self.assertEqual(code, 400)

    def test_replay_is_idempotent_and_conflicting_replay_is_409(self):
        row = {"synthetic": True, "external_ref": "DEMO-QA-REPLAY-02",
               "source": "phone", "need": "heating issue"}
        code, _, body = self.request("POST", "/api/demo/leads", row)
        self.assertEqual(code, 201)
        self.assertTrue(json.loads(body)["created"])
        code, _, body = self.request("POST", "/api/demo/leads", row)
        self.assertEqual(code, 200)
        self.assertFalse(json.loads(body)["created"])
        code, _, _ = self.request("POST", "/api/demo/leads", {**row, "need": "repair"})
        self.assertEqual(code, 409)
        code, _, body = self.request("GET", "/api/demo/leads")
        self.assertEqual(code, 200)
        matches = [x for x in json.loads(body)["leads"] if x["external_ref"] == row["external_ref"]]
        self.assertEqual(len(matches), 1)
        self.assertEqual(matches[0]["need"], "heating issue")

    def test_untrusted_host_origin_and_non_json_writes_are_blocked(self):
        lead = {"synthetic": True, "external_ref": "DEMO-QA-HOST-03",
                "source": "website", "need": "repair"}
        self.assertEqual(self.request("GET", "/api/demo/leads",
                                     headers={"Host": "evil.example"})[0], 403)
        self.assertEqual(self.request("POST", "/api/demo/leads", lead,
                                     headers={"Origin": "https://evil.example"})[0], 403)
        self.assertEqual(self.request("POST", "/api/demo/leads", b"{}",
                                     headers={"Content-Type": "text/plain"})[0], 415)
        self.assertEqual(self.request("POST", "/api/demo/leads", b"{broken",
                                     headers={"Content-Type": "application/json"})[0], 400)

    def test_no_tenant_admin_send_payment_webhook_or_approval_endpoints(self):
        # Missing routes must not be misrepresented as implemented authorization.
        forbidden = ("/api/tenants", "/api/tenants/demo/records",
                     "/api/auth/login", "/api/demo/send",
                     "/api/demo/approve", "/api/demo/book",
                     "/api/payments", "/api/webhooks/payments",
                     "/api/attribution/verify")
        for route in forbidden:
            with self.subTest(route=route):
                self.assertEqual(self.request("GET", route)[0], 404)
                self.assertEqual(self.request("POST", route, {})[0], 404)

    def test_recovery_preview_has_no_verified_consent_or_financial_evidence(self):
        lead = {"synthetic": True, "external_ref": "DEMO-QA-REVIEW-04",
                "source": "website", "need": "AC not cooling"}
        self.assertEqual(self.request("POST", "/api/demo/leads", lead)[0], 201)
        code, _, raw = self.request("GET", "/api/demo/recovery/DEMO-QA-REVIEW-04")
        self.assertEqual(code, 200)
        result = json.loads(raw)["preview"]
        self.assertFalse(result["qualification"]["consent_verified"])
        self.assertFalse(result["qualification"]["qualified"])
        self.assertFalse(result["followup"]["approved"])
        self.assertFalse(result["followup"]["transmitted"])
        self.assertTrue(result["crm"]["dry_run"])
        self.assertFalse(result["crm"]["transmitted"])
        self.assertFalse(result["appointment"]["confirmed"])
        self.assertEqual(result["attribution"]["verified_payment_receipts"], 0)
        self.assertEqual(result["attribution"]["verified_recovered_revenue_cents"], 0)
        self.assertFalse(result["attribution"]["business_subscription_revenue_verified"])

    def test_security_headers_and_unknown_paths(self):
        code, headers, _ = self.request("GET", "/demo/")
        self.assertEqual(code, 200)
        self.assertEqual(headers["Cache-Control"], "no-store")
        self.assertEqual(headers["X-Content-Type-Options"], "nosniff")
        self.assertEqual(headers["X-Frame-Options"], "DENY")
        self.assertIn("default-src 'none'", headers["Content-Security-Policy"])
        for route in ("/.env", "/demo/../backend/app.py", "/api/demo/unknown"):
            self.assertEqual(self.request("GET", route)[0], 404)


def cls_port(test):
    return test.server.server_port


if __name__ == "__main__":
    unittest.main()
