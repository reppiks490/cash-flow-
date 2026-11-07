"""Regression checks for local synthetic HTTP authority validation.

Run from repository root:
PYTHONPATH=products/revenue_recovery python -m unittest backend.test_host_header
"""
import http.client
import threading
import unittest
from http.server import ThreadingHTTPServer

from backend.app import DemoStore, make_handler


class HostHeaderBoundaryTests(unittest.TestCase):
    def setUp(self):
        self.server = ThreadingHTTPServer(("127.0.0.1", 0), make_handler(DemoStore()))
        self.worker = threading.Thread(target=self.server.serve_forever, daemon=True)
        self.worker.start()

    def tearDown(self):
        self.server.shutdown()
        self.server.server_close()
        self.worker.join(timeout=3)

    def request(self, host_values):
        conn = http.client.HTTPConnection("127.0.0.1", self.server.server_port, timeout=3)
        conn.putrequest("GET", "/health", skip_host=True)
        for value in host_values:
            conn.putheader("Host", value)
        conn.endheaders()
        response = conn.getresponse()
        status = response.status
        response.read()
        conn.close()
        return status

    def test_valid_authorities(self):
        for host in ("localhost", "127.0.0.1", "localhost:8765", "127.0.0.1:65535"):
            with self.subTest(host=host):
                self.assertEqual(self.request([host]), 200)

    def test_rejects_invalid_ports(self):
        for host in ("localhost:0", "localhost:65536", "localhost:99999", "localhost:-1"):
            with self.subTest(host=host):
                self.assertEqual(self.request([host]), 403)

    def test_rejects_duplicate_and_missing_host(self):
        self.assertEqual(self.request(["localhost", "evil.example"]), 403)
        self.assertEqual(self.request([]), 403)

    def test_rejects_non_loopback_authorities(self):
        for host in ("evil.example", "127.0.0.2", "localhost.evil.example"):
            with self.subTest(host=host):
                self.assertEqual(self.request([host]), 403)


if __name__ == "__main__":
    unittest.main()
