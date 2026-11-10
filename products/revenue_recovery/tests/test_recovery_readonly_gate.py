"""Synthetic recovery-preview safety invariants; no external integrations.

Run with PYTHONPATH=products/revenue_recovery:
python -m unittest products/revenue_recovery/tests/test_recovery_readonly_gate.py -v
"""
import http.client
import json
import threading
import unittest
from http.server import ThreadingHTTPServer

from backend.app import DemoStore, make_handler


class RecoveryReadOnlyGateTests(unittest.TestCase):
    def setUp(self):
        self.store = DemoStore()
        self.server = ThreadingHTTPServer(("127.0.0.1", 0), make_handler(self.store))
        self.thread = threading.Thread(target=self.server.serve_forever, daemon=True)
        self.thread.start()

    def tearDown(self):
        self.server.shutdown()
        self.server.server_close()
        self.thread.join(timeout=5)

    def request(self, method, path, payload=None):
        conn = http.client.HTTPConnection("127.0.0.1", self.server.server_port, timeout=5)
        headers = {"Host": "127.0.0.1"}
        body = None
        if payload is not None:
            body = json.dumps(payload).encode("utf-8")
            headers["Content-Type"] = "application/json"
        try:
            conn.request(method, path, body=body, headers=headers)
            response = conn.getresponse()
            return response.status, json.loads(response.read())
        finally:
            conn.close()

    def test_recovery_preview_does_not_mutate_store_or_claim_money(self):
        lead = {"synthetic": True, "external_ref": "QA-READONLY-1",
                "source": "demo", "need": "repair"}
        code, created = self.request("POST", "/api/demo/leads", lead)
        self.assertEqual(code, 201)
        self.assertTrue(created["created"])
        before = self.store.list()
        for _ in range(3):
            status, body = self.request("GET", "/api/demo/recovery/QA-READONLY-1")
            self.assertEqual(status, 200)
            preview = body["preview"]
            self.assertTrue(body["synthetic"])
            self.assertFalse(preview["followup"]["approved"])
            self.assertFalse(preview["followup"]["transmitted"])
            self.assertFalse(preview["appointment"]["confirmed"])
            self.assertFalse(preview["appointment"]["transmitted"])
            self.assertEqual(preview["attribution"]["verified_payment_receipts"], 0)
            self.assertEqual(preview["attribution"]["verified_recovered_revenue_cents"], 0)
            self.assertFalse(preview["attribution"]["revenue_source_connected"])
            self.assertEqual(self.store.list(), before)

    def test_invalid_preview_and_external_action_routes_do_not_mutate(self):
        lead = {"synthetic": True, "external_ref": "QA-READONLY-2",
                "source": "demo", "need": "repair"}
        self.assertEqual(self.request("POST", "/api/demo/leads", lead)[0], 201)
        before = self.store.list()
        for method, path, payload, expected in (
            ("GET", "/api/demo/recovery/QA-NOT-FOUND", None, 404),
            ("GET", "/api/demo/recovery/QA-READONLY-2?approved=true", None, 404),
            ("POST", "/api/demo/recovery/QA-READONLY-2", {}, 404),
            ("POST", "/api/send", {}, 404),
            ("POST", "/api/payments", {}, 404),
            ("POST", "/api/appointments", {}, 404),
        ):
            with self.subTest(method=method, path=path):
                status, _ = self.request(method, path, payload)
                self.assertEqual(status, expected)
                self.assertEqual(self.store.list(), before)


if __name__ == "__main__":
    unittest.main()
