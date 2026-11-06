"""Regression tests for the principal-owned synthetic HTTP ingress parser.

All traffic is loopback-only and all fixtures are invented category values.
No customer information, external network, payments or outbound activity.
"""
import http.client
import json
import threading
import unittest
from http.server import ThreadingHTTPServer

from backend.app import DemoStore, make_handler


class StrictJSONIngressTests(unittest.TestCase):
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

    def post(self, raw: str):
        connection = http.client.HTTPConnection(
            "127.0.0.1", self.server.server_port, timeout=3
        )
        try:
            connection.request(
                "POST", "/api/demo/leads",
                body=raw.encode("utf-8"),
                headers={"Content-Type": "application/json"},
            )
            response = connection.getresponse()
            return response.status, json.loads(response.read())
        finally:
            connection.close()

    def test_duplicate_synthetic_key_is_rejected_before_record_creation(self):
        status, body = self.post(
            '{"synthetic":false,"synthetic":true,"external_ref":"QA-DUP1",'
            '"source":"website","need":"repair"}'
        )
        self.assertEqual(status, 400)
        self.assertEqual(body["error"], "Duplicate JSON field")
        self.assertEqual(self.store.list(), [])

    def test_duplicate_business_key_is_rejected(self):
        status, body = self.post(
            '{"synthetic":true,"external_ref":"QA-DUP2","source":"website",'
            '"need":"repair","need":"maintenance"}'
        )
        self.assertEqual(status, 400)
        self.assertEqual(body["error"], "Duplicate JSON field")
        self.assertEqual(self.store.list(), [])

    def test_nonstandard_numeric_constant_is_rejected(self):
        status, body = self.post(
            '{"synthetic":true,"external_ref":"QA-NAN1","source":"website",'
            '"need":NaN}'
        )
        self.assertEqual(status, 400)
        self.assertEqual(body["error"], "Nonstandard JSON numeric constant")
        self.assertEqual(self.store.list(), [])

    def test_unicode_casefold_tokens_rejected_before_storage(self):
        # re.IGNORECASE without ASCII also admits these four Unicode lookalikes.
        for ref in ("QA-" + chr(0x212A), "QA-" + chr(0x0130), "QA-" + chr(0x0131), "QA-" + chr(0x017F)):
            with self.subTest(ref=ref):
                raw = json.dumps({"synthetic": True, "external_ref": ref,
                                  "source": "website", "need": "repair"})
                status, body = self.post(raw)
                self.assertEqual(status, 400)
                self.assertIn("external_ref", body["error"])
                self.assertEqual(self.store.list(), [])

    def test_reference_contract_rejects_unicode_and_accepts_ascii(self):
        from backend.contracts import REF
        for ref in ("QA-" + chr(0x212A), "QA-" + chr(0x0130), "QA-" + chr(0x0131), "QA-" + chr(0x017F)):
            with self.subTest(ref=ref):
                self.assertIsNone(REF.fullmatch(ref))
        self.assertIsNotNone(REF.fullmatch("QA-ASCII-001"))
        self.assertIsNotNone(REF.fullmatch("demo-hvac_02"))

    def test_valid_synthetic_intake_and_idempotent_replay_still_work(self):
        raw = ('{"synthetic":true,"external_ref":"QA-OK1",'
               '"source":"website","need":"repair"}')
        first_status, first = self.post(raw)
        second_status, second = self.post(raw)
        self.assertEqual(first_status, 201)
        self.assertTrue(first["created"])
        self.assertEqual(second_status, 200)
        self.assertFalse(second["created"])
        self.assertEqual(len(self.store.list()), 1)


if __name__ == "__main__":
    unittest.main()
