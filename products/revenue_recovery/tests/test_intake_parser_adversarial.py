"""Adversarial JSON parsing regressions for synthetic-only RRE intake.

No external services, live identities, or production state are used.
"""
import http.client
import json
import threading
import unittest
from http.server import ThreadingHTTPServer

from backend.app import DemoStore, make_handler


class IntakeParserAdversarialTests(unittest.TestCase):
    def setUp(self):
        self.store = DemoStore()
        self.server = ThreadingHTTPServer(("127.0.0.1", 0), make_handler(self.store))
        self.thread = threading.Thread(target=self.server.serve_forever, daemon=True)
        self.thread.start()

    def tearDown(self):
        self.server.shutdown()
        self.server.server_close()
        self.thread.join(timeout=5)

    def post_raw(self, payload):
        connection = http.client.HTTPConnection("127.0.0.1", self.server.server_port, timeout=5)
        try:
            connection.request(
                "POST", "/api/demo/leads", body=payload,
                headers={"Content-Type": "application/json"},
            )
            response = connection.getresponse()
            return response.status, json.loads(response.read())
        finally:
            connection.close()

    def test_duplicate_top_level_fields_fail_closed_without_store_mutation(self):
        payloads = [
            b'{"synthetic":true,"synthetic":false,"external_ref":"QA-DUP-1","source":"demo","need":"repair"}',
            b'{"synthetic":false,"synthetic":true,"external_ref":"QA-DUP-2","source":"demo","need":"repair"}',
            b'{"synthetic":true,"external_ref":"QA-DUP-3","external_ref":"QA-DUP-4","source":"demo","need":"repair"}',
        ]
        for payload in payloads:
            with self.subTest(payload=payload):
                status, _ = self.post_raw(payload)
                self.assertEqual(status, 400)
                self.assertEqual(self.store.list(), [])

    def test_nonfinite_json_constants_fail_closed_without_store_mutation(self):
        for token in (b"NaN", b"Infinity", b"-Infinity"):
            with self.subTest(token=token):
                payload = (b'{"synthetic":true,"external_ref":"QA-NONFINITE",'
                           b'"source":"demo","need":"repair","untrusted":' + token + b"}")
                status, _ = self.post_raw(payload)
                self.assertEqual(status, 400)
                self.assertEqual(self.store.list(), [])

    def test_rejected_duplicate_does_not_poison_valid_followup(self):
        invalid = (b'{"synthetic":true,"synthetic":false,'
                   b'"external_ref":"QA-RETRY","source":"demo","need":"repair"}')
        self.assertEqual(self.post_raw(invalid)[0], 400)
        valid = {"synthetic": True, "external_ref": "QA-RETRY",
                 "source": "demo", "need": "repair"}
        status, body = self.post_raw(json.dumps(valid).encode("utf-8"))
        self.assertEqual(status, 201)
        self.assertTrue(body["created"])
        self.assertEqual(len(self.store.list()), 1)


if __name__ == "__main__":
    unittest.main()
