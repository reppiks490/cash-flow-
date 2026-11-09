"""Loopback-only HTTP replay contract checks for the synthetic commercial demo.

These tests use an ephemeral local port and never contact external services.
They do not establish production idempotency, durability, or network isolation.
"""
import http.client
import json
import threading
import unittest
from http.server import ThreadingHTTPServer

from backend.app import DemoStore, make_handler


class SyntheticHTTPReplayTests(unittest.TestCase):
    def setUp(self):
        self.store = DemoStore()
        self.server = ThreadingHTTPServer(("127.0.0.1", 0), make_handler(self.store))
        self.thread = threading.Thread(target=self.server.serve_forever, daemon=True)
        self.thread.start()

    def tearDown(self):
        self.server.shutdown()
        self.thread.join(timeout=5)
        self.server.server_close()

    def request(self, payload):
        connection = http.client.HTTPConnection("127.0.0.1", self.server.server_port, timeout=3)
        try:
            body = json.dumps(payload).encode("utf-8")
            connection.request(
                "POST", "/api/demo/leads", body=body,
                headers={
                    "Host": "127.0.0.1:%d" % self.server.server_port,
                    "Origin": "http://127.0.0.1:%d" % self.server.server_port,
                    "Content-Type": "application/json",
                },
            )
            response = connection.getresponse()
            return response.status, json.loads(response.read())
        finally:
            connection.close()

    def test_http_replay_is_idempotent_and_does_not_duplicate_pipeline(self):
        payload = {
            "synthetic": True, "external_ref": "DEMO-HTTP-COMMERCIAL-1",
            "source": "website", "need": "repair",
        }
        first_status, first = self.request(payload)
        replay_status, replay = self.request(payload)
        self.assertEqual((first_status, replay_status), (201, 200))
        self.assertEqual((first["created"], replay["created"]), (True, False))
        self.assertEqual(first["lead"], replay["lead"])
        self.assertEqual(len(self.store.list()), 1)

    def test_http_conflicting_replay_fails_without_mutating_original(self):
        payload = {
            "synthetic": True, "external_ref": "DEMO-HTTP-COMMERCIAL-2",
            "source": "website", "need": "repair",
        }
        self.assertEqual(self.request(payload)[0], 201)
        conflicting = dict(payload, need="maintenance")
        status, result = self.request(conflicting)
        self.assertEqual(status, 409)
        self.assertIn("error", result)
        self.assertEqual(self.store.list()[0]["need"], "repair")
        self.assertEqual(len(self.store.list()), 1)

    def test_http_rejects_live_fields_without_storing(self):
        payload = {
            "synthetic": True, "external_ref": "DEMO-HTTP-COMMERCIAL-3",
            "source": "website", "need": "repair",
            "email": "not-a-real-contact@example.invalid",
        }
        status, result = self.request(payload)
        self.assertEqual(status, 400)
        self.assertIn("error", result)
        self.assertEqual(self.store.list(), [])


if __name__ == "__main__":
    unittest.main()
