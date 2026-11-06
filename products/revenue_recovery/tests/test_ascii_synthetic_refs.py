"""RRE-05 RED security gate: synthetic references must be ASCII-only.

Expected RED on main until the Principal-owned shared REF and HTTP ingress
regular expressions reject Unicode case-fold lookalikes. No production edits.

Run:
  PYTHONPATH=products/revenue_recovery python -m unittest discover \
    -s products/revenue_recovery/tests -p 'test_ascii_synthetic_refs.py' -v
"""
import http.client
import json
import threading
import unittest
from http.server import ThreadingHTTPServer

from backend.app import DemoStore, make_handler


class AsciiSyntheticReferenceTests(unittest.TestCase):
    def payload(self, ref):
        return {"synthetic": True, "external_ref": ref,
                "source": "website", "need": "repair"}

    def test_demo_store_rejects_unicode_casefold_lookalikes(self):
        store = DemoStore()
        # re.I + [A-Za-z] also matches four Unicode special casefolds
        # unless the regex is explicitly ASCII restricted.
        for ref in ("QA-\u212a", "QA-\u0130", "QA-\u0131", "QA-\u017f"):
            with self.subTest(ref=ref):
                with self.assertRaises(ValueError):
                    store.add(self.payload(ref))
                self.assertEqual(store.list(), [])

    def test_http_rejects_unicode_casefold_refs_without_persistence(self):
        store = DemoStore()
        server = ThreadingHTTPServer(("127.0.0.1", 0), make_handler(store))
        worker = threading.Thread(target=server.serve_forever, daemon=True)
        worker.start()
        try:
            for ref in ("QA-\u212a", "QA-\u0130", "QA-\u0131", "QA-\u017f"):
                with self.subTest(ref=ref):
                    raw = json.dumps(self.payload(ref)).encode("utf-8")
                    conn = http.client.HTTPConnection(
                        "127.0.0.1", server.server_port, timeout=4)
                    try:
                        conn.request("POST", "/api/demo/leads", body=raw,
                                     headers={"Content-Type": "application/json"})
                        response = conn.getresponse()
                        status = response.status
                        response.read()
                    finally:
                        conn.close()
                    self.assertEqual(status, 400)
                    self.assertEqual(store.list(), [])
        finally:
            server.shutdown()
            server.server_close()
            worker.join(timeout=5)

    def test_legitimate_ascii_synthetic_reference_still_works(self):
        store = DemoStore()
        row, created = store.add(self.payload("QA-ASCII-001"))
        self.assertTrue(created)
        self.assertEqual(row["external_ref"], "QA-ASCII-001")
        self.assertEqual(store.get("QA-ASCII-001")["need"], "repair")


if __name__ == "__main__":
    unittest.main()
