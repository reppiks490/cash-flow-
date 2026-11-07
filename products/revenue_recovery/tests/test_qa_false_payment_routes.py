"""Synthetic-only HTTP regression: forged financial outcomes cannot enter the scorecard.

Uses only ephemeral loopback sockets and fictional QA identifiers. No external
provider, customer information, payment, or communication is involved.
"""
import http.client
import json
import threading
import unittest
from http.server import ThreadingHTTPServer

from backend.app import DemoStore, make_handler


class FalsePaymentRouteTests(unittest.TestCase):
    def setUp(self):
        self.store = DemoStore()
        self.server = ThreadingHTTPServer(("127.0.0.1", 0), make_handler(self.store))
        self.thread = threading.Thread(target=self.server.serve_forever, daemon=True)
        self.thread.start()

    def tearDown(self):
        self.server.shutdown()
        self.server.server_close()
        self.thread.join(timeout=5)

    def request(self, method, path, payload=None):
        connection = http.client.HTTPConnection(
            "127.0.0.1", self.server.server_port, timeout=5
        )
        body = json.dumps(payload).encode("utf-8") if payload is not None else None
        headers = {"Content-Type": "application/json"} if body is not None else {}
        try:
            connection.request(method, path, body=body, headers=headers)
            response = connection.getresponse()
            return response.status, json.loads(response.read())
        finally:
            connection.close()

    def test_forged_payment_endpoints_cannot_change_attribution(self):
        lead = {
            "synthetic": True, "external_ref": "QA-FIN-ROUTE-1",
            "source": "demo", "need": "repair",
        }
        status, _ = self.request("POST", "/api/demo/leads", lead)
        self.assertEqual(status, 201)
        status, before = self.request("GET", "/api/demo/scorecard")
        self.assertEqual(status, 200)
        self.assertEqual(before["counts"]["received_demo_leads"], 1)
        forged = {
            "synthetic": True, "external_ref": lead["external_ref"],
            "status": "paid", "verified_payment_receipts": 1,
            "amount_cents": 250000, "receipt_id": "QA-NOT-A-RECEIPT",
        }
        for route in (
            "/api/payments", "/api/billing", "/api/receipts",
            "/api/demo/payments", "/api/demo/scorecard",
        ):
            with self.subTest(route=route):
                status, _ = self.request("POST", route, forged)
                self.assertEqual(status, 404)
        status, after = self.request("GET", "/api/demo/scorecard")
        self.assertEqual(status, 200)
        self.assertEqual(after, before)
        self.assertTrue(after["synthetic"])
        for metric in (
            "rre_monthly_profit_cents", "rre_subscription_revenue_cents",
            "contractor_recovered_revenue_cents", "payment_receipts",
            "business_subscription_customers",
        ):
            self.assertEqual(after["verified"][metric], 0)

    def test_forged_paid_field_rejected_without_creating_lead(self):
        lead = {
            "synthetic": True, "external_ref": "QA-FIN-ROUTE-2",
            "source": "demo", "need": "repair",
            "paid": True, "receipt_id": "QA-NOT-A-RECEIPT",
        }
        status, _ = self.request("POST", "/api/demo/leads", lead)
        self.assertEqual(status, 400)
        self.assertEqual(self.store.list(), [])


if __name__ == "__main__":
    unittest.main()
