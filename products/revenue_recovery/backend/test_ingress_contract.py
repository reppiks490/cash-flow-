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


    def test_nested_ambiguous_json_field_is_rejected(self):
        status, body = self.post(
            '{"synthetic":true,"external_ref":"QA-NEST1","source":"website",'
            '"need":"repair","ignored":{"x":1,"x":2}}'
        )
        self.assertEqual(status, 400)
        self.assertEqual(body["error"], "Duplicate JSON field")
        self.assertEqual(self.store.list(), [])

    def test_positive_and_negative_infinity_are_rejected(self):
        for constant in ("Infinity", "-Infinity"):
            status, body = self.post(
                '{"synthetic":true,"external_ref":"QA-INF1","source":"website",'
                '"need":' + constant + '}'
            )
            self.assertEqual(status, 400)
            self.assertEqual(body["error"], "Nonstandard JSON numeric constant")
            self.assertEqual(self.store.list(), [])

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
