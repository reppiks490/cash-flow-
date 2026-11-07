"""Loopback Host authority contract for synthetic-only RRE HTTP.

Runs against an ephemeral 127.0.0.1 server; no external network, customers,
credentials, payments, or production endpoints.  See RRE-05 (#27).
"""
import http.client
import threading
import unittest
from http.server import ThreadingHTTPServer

from backend.app import DemoStore, make_handler


class HostAuthorityContractTests(unittest.TestCase):
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

    def status_for_host(self, host):
        conn = http.client.HTTPConnection("127.0.0.1", self.server.server_port, timeout=5)
        try:
            conn.putrequest("GET", "/health", skip_host=True)
            conn.putheader("Host", host)
            conn.endheaders()
            response = conn.getresponse()
            response.read()
            return response.status
        finally:
            conn.close()

    def test_canonical_loopback_authorities_accepted(self):
        for host in ("localhost", "127.0.0.1", "localhost:80",
                     "127.0.0.1:8080", "LOCALHOST:65535"):
            with self.subTest(host=host):
                self.assertEqual(self.status_for_host(host), 200)

    def test_non_loopback_and_injected_authorities_rejected(self):
        for host in ("evil.example", "localhost.evil.example",
                     "127.0.0.1.evil.example", "localhost@evil.example",
                     "localhost:abc", "127.0.0.1:80,evil.example",
                     "localhost:80:90", "0.0.0.0", "[::1]"):
            with self.subTest(host=host):
                self.assertEqual(self.status_for_host(host), 403)


if __name__ == "__main__":
    unittest.main()
