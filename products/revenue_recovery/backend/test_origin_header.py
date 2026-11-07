"""Synthetic loopback-only HTTP Origin ambiguity regression (no external calls)."""
import http.client
import json
import threading
import unittest
from http.server import ThreadingHTTPServer

from backend.app import DemoStore, make_handler


class OriginHeaderTests(unittest.TestCase):
    def test_duplicate_origin_rejected_before_intake(self):
        store = DemoStore()
        server = ThreadingHTTPServer(("127.0.0.1", 0), make_handler(store))
        thread = threading.Thread(target=server.serve_forever, daemon=True)
        thread.start()
        try:
            authority = f"127.0.0.1:{server.server_port}"
            payload = json.dumps({
                "synthetic": True, "external_ref": "QA-origin-ambiguity",
                "source": "demo", "need": "repair"
            }).encode()
            connection = http.client.HTTPConnection("127.0.0.1", server.server_port, timeout=5)
            try:
                connection.putrequest("POST", "/api/demo/leads", skip_host=True)
                connection.putheader("Host", authority)
                connection.putheader("Content-Type", "application/json")
                connection.putheader("Content-Length", str(len(payload)))
                connection.putheader("Origin", "http://" + authority)
                connection.putheader("Origin", "https://example.invalid")
                connection.endheaders(payload)
                response = connection.getresponse()
                response.read()
                self.assertEqual(response.status, 403)
            finally:
                connection.close()
            self.assertEqual(store.list(), [])
        finally:
            server.shutdown()
            server.server_close()
            thread.join(timeout=5)


if __name__ == "__main__":
    unittest.main()
