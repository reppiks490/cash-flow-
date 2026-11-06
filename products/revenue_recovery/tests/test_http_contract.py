"""Network-loopback contract tests for the synthetic-only HTTP prototype.

All requests use a fresh ephemeral loopback server and synthetic fixture IDs.
"""
import http.client
import json
import threading
import unittest
from http.server import ThreadingHTTPServer

from backend.app import DemoStore, MAX_BODY_BYTES, make_handler


class HttpContractTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.server = ThreadingHTTPServer(("127.0.0.1", 0), make_handler(DemoStore()))
        cls.thread = threading.Thread(target=cls.server.serve_forever, daemon=True)
        cls.thread.start()

    @classmethod
    def tearDownClass(cls):
        cls.server.shutdown()
        cls.server.server_close()
        cls.thread.join(timeout=5)

    def request(self, method, path, body=None):
        conn = http.client.HTTPConnection("127.0.0.1", self.server.server_port, timeout=5)
        headers = {}
        if body is not None:
            if isinstance(body, dict):
                body = json.dumps(body).encode("utf-8")
            headers["Content-Type"] = "application/json"
        try:
            conn.request(method, path, body=body, headers=headers)
            response = conn.getresponse()
            raw = response.read()
            return response.status, dict(response.getheaders()), json.loads(raw)
        finally:
            conn.close()

    def test_health_is_explicitly_synthetic(self):
        status, headers, body = self.request("GET", "/health")
        self.assertEqual(status, 200)
        self.assertTrue(body["synthetic_only"])
        self.assertEqual(headers.get("Cache-Control"), "no-store")

    def test_post_duplicate_is_idempotent_and_readable(self):
        lead = {"synthetic": True, "external_ref": "qa-http-1", "source": "demo", "need": "AC maintenance"}
        code, _, first = self.request("POST", "/api/demo/leads", lead)
        self.assertEqual(code, 201)
        self.assertTrue(first["created"])
        code, _, second = self.request("POST", "/api/demo/leads", lead)
        self.assertEqual(code, 200)
        self.assertFalse(second["created"])
        self.assertEqual(first["lead"], second["lead"])
        code, _, result = self.request("GET", "/api/demo/leads")
        self.assertEqual(code, 200)
        self.assertEqual(sum(x["external_ref"] == "qa-http-1" for x in result["leads"]), 1)

    def test_non_synthetic_and_unexpected_pii_field_are_rejected(self):
        for patch in ({"synthetic": False}, {"email": "synthetic@example.invalid"},
                      {"phone": "000-000-0000"}, {"status": "paid"}):
            with self.subTest(patch=patch):
                lead = {"synthetic": True, "external_ref": "qa-invalid", "source": "demo", "need": "repair"}
                lead.update(patch)
                code, _, _ = self.request("POST", "/api/demo/leads", lead)
                self.assertEqual(code, 400)

    def test_invalid_json_and_oversize_rejected(self):
        code, _, _ = self.request("POST", "/api/demo/leads", b"{broken")
        self.assertEqual(code, 400)
        code, _, _ = self.request("POST", "/api/demo/leads", b" " * (MAX_BODY_BYTES + 1))
        self.assertEqual(code, 413)

    def test_unimplemented_external_actions_not_exposed(self):
        for endpoint in ("/api/send", "/api/billing", "/api/payments", "/api/appointments"):
            with self.subTest(endpoint=endpoint):
                code, _, _ = self.request("POST", endpoint, {})
                self.assertEqual(code, 404)


if __name__ == "__main__":
    unittest.main()
