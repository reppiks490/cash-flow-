"""Synthetic-only cross-component HTTP integration checks.

No network traffic leaves ephemeral local loopback. Tests never send messages,
process payments, book appointments, or use customer records.
"""
import http.client
import json
import threading
import unittest
from http.server import ThreadingHTTPServer

from backend.app import DemoStore, make_handler


class IntegratedDemoContractTests(unittest.TestCase):
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
        connection = http.client.HTTPConnection("127.0.0.1", self.server.server_port, timeout=5)
        headers = dict(headers or {})
        if payload is not None:
            if isinstance(payload, dict):
                payload = json.dumps(payload).encode("utf-8")
            headers.setdefault("Content-Type", "application/json")
        try:
            connection.request(method, path, body=payload, headers=headers)
            response = connection.getresponse()
            return response.status, dict(response.getheaders()), response.read()
        finally:
            connection.close()

    @staticmethod
    def sample(ref="DEMO-M1-1", need="AC not cooling"):
        return {"synthetic": True, "external_ref": ref, "source": "website", "need": need}

    def test_local_browser_is_served_same_origin_without_filesystem_access(self):
        status, headers, html = self.request("GET", "/demo/")
        self.assertEqual(status, 200)
        self.assertIn("text/html", headers["Content-Type"])
        self.assertIn("SYNTHETIC DATA ONLY", html.decode("utf-8"))
        self.assertEqual(headers["X-Frame-Options"], "DENY")
        self.assertIn("default-src 'none'", headers["Content-Security-Policy"])
        self.assertEqual(headers["Cache-Control"], "no-store")
        for path, kind in (("/demo/app.js", "application/javascript"),
                           ("/demo/styles.css", "text/css")):
            code, hdr, data = self.request("GET", path)
            self.assertEqual(code, 200)
            self.assertIn(kind, hdr["Content-Type"])
            self.assertTrue(data)
        for forbidden in ("/demo/../backend/app.py", "/demo/../commercial/economics.py",
                          "/demo/.env", "/api/payments"):
            code, _, _ = self.request("GET", forbidden)
            self.assertEqual(code, 404)

    def test_lead_to_review_draft_crm_and_revenue_preview(self):
        lead = self.sample("DEMO-M1-RECOVERY")
        code, _, raw = self.request("POST", "/api/demo/leads", lead)
        self.assertEqual(code, 201)
        self.assertTrue(json.loads(raw)["created"])
        code, _, raw = self.request("GET", "/api/demo/recovery/DEMO-M1-RECOVERY")
        self.assertEqual(code, 200)
        preview = json.loads(raw)["preview"]
        self.assertTrue(preview["synthetic"])
        self.assertEqual(preview["qualification"]["result"], "manual_review_required")
        self.assertFalse(preview["qualification"]["qualified"])
        self.assertFalse(preview["qualification"]["consent_verified"])
        self.assertEqual(preview["followup"]["status"], "unsent_unapproved_draft")
        self.assertFalse(preview["followup"]["transmitted"])
        self.assertIn("SYNTHETIC UNSENT DRAFT", preview["followup"]["message"])
        self.assertTrue(preview["crm"]["dry_run"])
        self.assertFalse(preview["crm"]["transmitted"])
        self.assertFalse(preview["appointment"]["confirmed"])
        self.assertEqual(preview["attribution"]["verified_recovered_revenue_cents"], 0)
        self.assertFalse(preview["attribution"]["business_subscription_revenue_verified"])
        code, _, raw = self.request("GET", "/api/demo/leads")
        self.assertEqual(code, 200)
        self.assertIn("DEMO-M1-RECOVERY", [r["external_ref"] for r in json.loads(raw)["leads"]])

    def test_conflicting_idempotency_ref_cannot_silently_rewrite_lead(self):
        ref = "DEMO-M1-IDEMPOTENCY"
        self.assertEqual(self.request("POST", "/api/demo/leads", self.sample(ref))[0], 201)
        self.assertEqual(self.request("POST", "/api/demo/leads", self.sample(ref))[0], 200)
        code, _, raw = self.request("POST", "/api/demo/leads", self.sample(ref, "repair"))
        self.assertEqual(code, 409)
        self.assertIn("conflicting", json.loads(raw)["error"])
        _, _, raw = self.request("GET", "/api/demo/leads")
        self.assertEqual(
            [r["need"] for r in json.loads(raw)["leads"] if r["external_ref"] == ref],
            ["AC not cooling"]
        )

    def test_nonloopback_host_origin_and_nonjson_are_blocked(self):
        code, _, _ = self.request("GET", "/health", headers={"Host": "attacker.example"})
        self.assertEqual(code, 403)
        code, _, _ = self.request(
            "POST", "/api/demo/leads", self.sample("DEMO-M1-ORIGIN"),
            headers={"Origin": "https://attacker.example"}
        )
        self.assertEqual(code, 403)
        code, _, _ = self.request(
            "POST", "/api/demo/leads", json.dumps(self.sample("DEMO-M1-TEXT")).encode("utf-8"),
            headers={"Content-Type": "text/plain"}
        )
        self.assertEqual(code, 415)
        code, _, _ = self.request(
            "POST", "/api/demo/leads", {**self.sample("DEMO-M1-PII"), "email": "nobody@example.invalid"}
        )
        self.assertEqual(code, 400)

    def test_dashboard_queries_read_only_preview_and_preserves_unsent_fallback(self):
        code, _, raw = self.request("GET", "/demo/app.js")
        self.assertEqual(code, 200)
        js = raw.decode("utf-8")
        self.assertIn('"/api/demo/recovery/"', js)
        self.assertIn('credentials:"omit"', js)
        self.assertIn("OFFLINE SYNTHETIC FALLBACK", js)
        self.assertIn("manual_review_required", js)
        self.assertIn("unsent_unapproved_draft", js)
        self.assertIn("verified_recovered_revenue_cents", js)
        self.assertNotIn('fetch("/api/send"', js)
        self.assertNotIn("innerHTML", js)

    def test_unknown_reference_never_creates_external_actions(self):
        for path in ("/api/demo/recovery/DEMO-UNKNOWN", "/api/demo/recovery/a@b",
                     "/api/demo/recovery/../../backend/app.py"):
            code, _, _ = self.request("GET", path)
            self.assertEqual(code, 404)
        for path in ("/api/appointments", "/api/communications", "/api/billing"):
            code, _, _ = self.request("POST", path, {"synthetic": True})
            self.assertEqual(code, 404)


if __name__ == "__main__":
    unittest.main()
