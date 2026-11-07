"""Synthetic-only HTTP JSON parser adversarial regression tests (RRE-05).

Uses an ephemeral loopback server, no customer records or external services.
"""
import http.client
import json
import threading
import unittest
from http.server import ThreadingHTTPServer

from backend.app import DemoStore, make_handler


class StrictJsonParserTests(unittest.TestCase):
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

    def post_raw(self, raw):
        conn = http.client.HTTPConnection("127.0.0.1", self.server.server_port, timeout=5)
        try:
            conn.request("POST", "/api/demo/leads", body=raw, headers={
                "Host": "127.0.0.1",
                "Content-Type": "application/json",
            })
            response = conn.getresponse()
            data = json.loads(response.read())
            return response.status, data
        finally:
            conn.close()

    def test_duplicate_fields_rejected_at_any_depth(self):
        samples = (
            b'{"synthetic":true,"synthetic":true,"external_ref":"QA-DUP","source":"web","need":"repair"}',
            b'{"synthetic":true,"external_ref":"QA-DUP","source":"web","need":"repair","nested":{"a":1,"a":2}}',
        )
        for raw in samples:
            with self.subTest(raw=raw):
                status, data = self.post_raw(raw)
                self.assertEqual(status, 400)
                self.assertIn("error", data)

    def test_nonstandard_numeric_constants_rejected(self):
        for token in ("NaN", "Infinity", "-Infinity"):
            with self.subTest(token=token):
                raw = ('{"synthetic":true,"external_ref":"QA-NUM",'
                       '"source":"web","need":"repair","extra":' + token + '}').encode()
                status, data = self.post_raw(raw)
                self.assertEqual(status, 400)
                self.assertIn("error", data)

    def test_non_object_root_fails_closed(self):
        for raw in (b'[]', b'null', b'true', b'123'):
            with self.subTest(raw=raw):
                status, data = self.post_raw(raw)
                self.assertEqual(status, 400)
                self.assertIn("error", data)


if __name__ == "__main__":
    unittest.main()
