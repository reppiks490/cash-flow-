"""Fail-closed regression for duplicate Origin headers on synthetic intake.

Only ephemeral loopback traffic and enumerated synthetic fixture values.
The current application reads the first Origin via headers.get(), so this
test is expected to expose a security-contract gap until backend is fixed.
"""
import http.client
import json
import threading
import unittest
from http.server import ThreadingHTTPServer

from backend.app import DemoStore, make_handler


class DuplicateOriginContractTests(unittest.TestCase):
    def test_duplicate_origin_rejected_without_store_mutation(self):
        store = DemoStore()
        server = ThreadingHTTPServer(("127.0.0.1", 0), make_handler(store))
        worker = threading.Thread(target=server.serve_forever, daemon=True)
        worker.start()
        try:
            authority = f"127.0.0.1:{server.server_port}"
            payload = json.dumps({
                "synthetic": True,
                "external_ref": "QA-duplicate-origin-20261107",
                "source": "demo",
                "need": "repair",
            }).encode("utf-8")
            conn = http.client.HTTPConnection("127.0.0.1", server.server_port, timeout=5)
            try:
                conn.putrequest("POST", "/api/demo/leads", skip_host=True)
                conn.putheader("Host", authority)
                conn.putheader("Content-Type", "application/json")
                conn.putheader("Content-Length", str(len(payload)))
                conn.putheader("Origin", "http://" + authority)
                conn.putheader("Origin", "https://example.invalid")
                conn.endheaders(payload)
                response = conn.getresponse()
                response.read()
                self.assertEqual(response.status, 403, "Ambiguous Origin must fail closed")
            finally:
                conn.close()
            self.assertEqual(store.list(), [], "Rejected intake must not create a lead")
        finally:
            server.shutdown()
            server.server_close()
            worker.join(timeout=5)


if __name__ == "__main__":
    unittest.main()
