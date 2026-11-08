"""Regression: reject ambiguous duplicate Content-Type on synthetic intake.

Runs with Python stdlib only; no external network or customer data.
"""
import http.client
import json
import threading
import unittest
from http.server import ThreadingHTTPServer

from backend.app import DemoStore, make_handler


class DuplicateContentTypeTests(unittest.TestCase):
    def setUp(self):
        self.store = DemoStore()
        self.server = ThreadingHTTPServer(("127.0.0.1", 0), make_handler(self.store))
        self.thread = threading.Thread(target=self.server.serve_forever, daemon=True)
        self.thread.start()

    def tearDown(self):
        self.server.shutdown()
        self.server.server_close()
        self.thread.join(timeout=3)

    def _post(self, content_types):
        body = json.dumps({"synthetic": True, "external_ref": "QA-DUP-CTYPE",
                           "source": "website", "need": "AC not cooling"}).encode()
        connection = http.client.HTTPConnection("127.0.0.1", self.server.server_port, timeout=3)
        try:
            connection.putrequest("POST", "/api/demo/leads")
            for value in content_types:
                connection.putheader("Content-Type", value)
            connection.putheader("Content-Length", str(len(body)))
            connection.endheaders(body)
            response = connection.getresponse()
            response.read()
            return response.status
        finally:
            connection.close()

    def test_duplicate_identical_content_type_rejected_without_write(self):
        self.assertEqual(self._post(["application/json", "application/json"]), 400)
        self.assertEqual(self.store.list(), [])

    def test_duplicate_conflicting_content_type_rejected_without_write(self):
        self.assertEqual(self._post(["application/json", "text/plain"]), 400)
        self.assertEqual(self.store.list(), [])

    def test_single_content_type_remains_accepted(self):
        self.assertEqual(self._post(["application/json"]), 201)
        self.assertEqual(len(self.store.list()), 1)


if __name__ == "__main__":
    unittest.main()
