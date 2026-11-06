"""QA fail-closed HTTP length parsing regressions (synthetic loopback only).

This test intentionally starts RED against the old generic ValueError handler,
which may reflect the malformed Content-Length input in a JSON error response.
Only synthetic marker text is used; no real data or external services.
"""
import http.client
import json
import threading
import unittest
from http.server import ThreadingHTTPServer

from backend.app import DemoStore, MAX_BODY_BYTES, make_handler


class ContentLengthSafetyTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.store = DemoStore()
        cls.server = ThreadingHTTPServer(("127.0.0.1", 0), make_handler(cls.store))
        cls.thread = threading.Thread(target=cls.server.serve_forever, daemon=True)
        cls.thread.start()

    @classmethod
    def tearDownClass(cls):
        cls.server.shutdown()
        cls.server.server_close()
        cls.thread.join(timeout=5)

    def setUp(self):
        self.store._leads.clear()

    def post_with_length(self, length, body=b"", *, extra_lengths=(), transfer_encoding=None):
        conn = http.client.HTTPConnection("127.0.0.1", self.server.server_port, timeout=4)
        try:
            conn.putrequest("POST", "/api/demo/leads")
            conn.putheader("Content-Type", "application/json")
            if length is not None:
                conn.putheader("Content-Length", length)
            for additional_length in extra_lengths:
                conn.putheader("Content-Length", additional_length)
            if transfer_encoding is not None:
                conn.putheader("Transfer-Encoding", transfer_encoding)
            conn.endheaders(body)
            response = conn.getresponse()
            return response.status, json.loads(response.read())
        finally:
            conn.close()

    def test_malformed_lengths_fail_closed_without_echoing_input(self):
        for raw in ("SYNTHETIC-NONSECRET-MARKER", "1e3", "+0", "9" * 150):
            with self.subTest(length=raw[:25]):
                status, result = self.post_with_length(raw)
                self.assertEqual(status, 400)
                self.assertEqual(result, {"error": "Invalid request framing"})
                self.assertNotIn(raw, json.dumps(result))
                self.assertEqual(self.store.list(), [])

    def test_ambiguous_framing_headers_cannot_create_synthetic_leads(self):
        body = json.dumps({
            "synthetic": True,
            "external_ref": "QA-CL-CONFLICT-001",
            "source": "website",
            "need": "repair",
        }).encode("utf-8")
        length = str(len(body))
        cases = (
            ("different duplicate lengths", (str(len(body) + 1),), None),
            ("identical duplicate lengths", (length,), None),
            ("content length plus chunked", (), "chunked"),
        )
        for label, extra, transfer in cases:
            with self.subTest(case=label):
                status, result = self.post_with_length(
                    length, body, extra_lengths=extra, transfer_encoding=transfer)
                self.assertEqual(status, 400)
                self.assertEqual(result, {"error": "Invalid request framing"})
                self.assertEqual(self.store.list(), [])

    def test_missing_or_oversized_length_cannot_create_leads(self):
        for length in (None, str(MAX_BODY_BYTES + 1)):
            with self.subTest(length=length):
                status, result = self.post_with_length(length)
                self.assertEqual(status, 413)
                self.assertEqual(result["error"], "Invalid or oversized request")
                self.assertEqual(self.store.list(), [])

    def test_valid_decimal_length_still_allows_synthetic_intake(self):
        body = json.dumps({
            "synthetic": True,
            "external_ref": "QA-LENGTH-001",
            "source": "website",
            "need": "repair",
        }).encode("utf-8")
        status, result = self.post_with_length(str(len(body)), body)
        self.assertEqual(status, 201)
        self.assertTrue(result["created"])
        self.assertEqual(self.store.get("QA-LENGTH-001")["need"], "repair")


if __name__ == "__main__":
    unittest.main()
