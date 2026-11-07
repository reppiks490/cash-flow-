"""Compound Host/framing regressions against local synthetic HTTP only.

No external network destinations, real leads, credentials or paid services.
Run: PYTHONPATH=products/revenue_recovery python -m unittest discover -s products/revenue_recovery/tests -p 'test_qa_compound_http_framing.py' -v
"""
import http.client
import json
import threading
import unittest
from http.server import ThreadingHTTPServer

from backend.app import DemoStore, make_handler


class CompoundFramingTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.store = DemoStore()
        cls.server = ThreadingHTTPServer(("127.0.0.1", 0), make_handler(cls.store))
        cls.worker = threading.Thread(target=cls.server.serve_forever, daemon=True)
        cls.worker.start()

    @classmethod
    def tearDownClass(cls):
        cls.server.shutdown()
        cls.server.server_close()
        cls.worker.join(timeout=5)

    def setUp(self):
        with self.store._lock:
            self.store._leads.clear()

    def request(self, hosts, lengths, transfer=None):
        body = json.dumps({
            "synthetic": True,
            "external_ref": "QA-COMPOUND-001",
            "source": "website",
            "need": "repair",
        }).encode("ascii")
        conn = http.client.HTTPConnection("127.0.0.1", self.server.server_port, timeout=4)
        try:
            conn.putrequest("POST", "/api/demo/leads", skip_host=True)
            for host in hosts:
                conn.putheader("Host", host)
            conn.putheader("Content-Type", "application/json")
            for length in lengths:
                conn.putheader("Content-Length", length if length != "VALID" else str(len(body)))
            if transfer is not None:
                conn.putheader("Transfer-Encoding", transfer)
            conn.endheaders(body)
            response = conn.getresponse()
            return response.status, json.loads(response.read())
        finally:
            conn.close()

    def test_compound_ambiguous_headers_never_mutate_store(self):
        cases = (
            (("localhost", "127.0.0.1"), ("VALID",), None, 403),
            (("localhost", "evil.example"), ("VALID", "VALID"), None, 403),
            (("localhost:65536",), ("VALID",), "chunked", 403),
            (("localhost",), ("VALID", "VALID"), None, 400),
            (("127.0.0.1",), ("VALID",), "chunked", 400),
            (("localhost",), ("not-a-length",), "chunked", 400),
            (("localhost",), ("VALID", "VALID"), "chunked", 400),
        )
        for hosts, lengths, transfer, expected in cases:
            with self.subTest(hosts=hosts, lengths=lengths, transfer=transfer):
                status, payload = self.request(hosts, lengths, transfer)
                self.assertEqual(status, expected)
                self.assertIn("error", payload)
                self.assertNotIn("QA-COMPOUND-001", json.dumps(payload))
                self.assertEqual(self.store.list(), [])

    def test_valid_request_still_creates_one_synthetic_lead(self):
        status, payload = self.request(("localhost",), ("VALID",))
        self.assertEqual(status, 201)
        self.assertTrue(payload["created"])
        self.assertEqual(len(self.store.list()), 1)
        status, payload = self.request(("localhost",), ("VALID",))
        self.assertEqual(status, 200)
        self.assertFalse(payload["created"])
        self.assertEqual(len(self.store.list()), 1)


if __name__ == "__main__":
    unittest.main()
