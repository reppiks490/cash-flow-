"""Security response-header regression for the local-only synthetic HTTP demo.

No external network calls, customer records, or production auth assumptions.
"""
import http.client
import json
import threading
import unittest
from http.server import ThreadingHTTPServer

from backend.app import DemoStore, make_handler


class ResponseHeaderSecurityTests(unittest.TestCase):
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

    def request(self, method, path, body=None, host=None):
        connection = http.client.HTTPConnection("127.0.0.1", self.server.server_port, timeout=5)
        headers = {}
        if host is not None:
            headers["Host"] = host
        if body is not None:
            headers["Content-Type"] = "application/json"
        try:
            connection.request(method, path, body=body, headers=headers)
            response = connection.getresponse()
            payload = response.read()
            return response.status, response.headers, payload
        finally:
            connection.close()

    def assert_security_headers(self, headers):
        self.assertEqual(headers.get("Cache-Control"), "no-store")
        self.assertEqual(headers.get("X-Content-Type-Options"), "nosniff")
        self.assertEqual(headers.get("X-Frame-Options"), "DENY")
        self.assertEqual(headers.get("Referrer-Policy"), "no-referrer")
        policy = headers.get("Content-Security-Policy", "")
        for required in ("default-src 'none'", "script-src 'self'",
                         "connect-src 'self'", "form-action 'none'",
                         "frame-ancestors 'none'"):
            with self.subTest(directive=required):
                self.assertIn(required, policy)

    def test_security_headers_survive_success_and_denial_paths(self):
        cases = [
            ("GET", "/health", None, None, 200),
            ("GET", "/api/demo/leads", None, None, 200),
            ("GET", "/api/demo/missing", None, None, 404),
            ("POST", "/api/demo/leads", b"{bad", None, 400),
            ("GET", "/health", None, "evil.example", 403),
        ]
        for method, path, body, host, expected in cases:
            with self.subTest(method=method, path=path, host=host):
                status, headers, payload = self.request(method, path, body, host)
                self.assertEqual(status, expected)
                self.assert_security_headers(headers)
                self.assertEqual(int(headers["Content-Length"]), len(payload))
                self.assertNotIn("synthetic@example.invalid", payload.decode("utf-8"))

    def test_denied_host_cannot_read_synthetic_lead_list(self):
        status, headers, payload = self.request(
            "GET", "/api/demo/leads", host="outside.example"
        )
        self.assertEqual(status, 403)
        self.assert_security_headers(headers)
        self.assertNotIn("leads", json.loads(payload))


if __name__ == "__main__":
    unittest.main()
