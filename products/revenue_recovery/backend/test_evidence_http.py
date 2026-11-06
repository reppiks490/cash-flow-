"""Read-only scenario HTTP integration: fixtures never become verified business facts."""
import http.client
import json
import io
from contextlib import redirect_stderr
import threading
import unittest
from http.server import ThreadingHTTPServer

from backend.app import DemoStore, make_handler


class ScenarioHttpTests(unittest.TestCase):
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

    def call(self, method, path, data=None, headers=None):
        conn = http.client.HTTPConnection("127.0.0.1", self.server.server_port, timeout=5)
        hs = dict(headers or {})
        if data is not None:
            data = json.dumps(data).encode("utf-8")
            hs["Content-Type"] = "application/json"
        try:
            conn.request(method, path, data, hs)
            response = conn.getresponse()
            raw = response.read()
            return response.status, json.loads(raw) if response.getheader("Content-Type", "").startswith("application/json") else raw
        finally:
            conn.close()

    def test_read_only_scorecard_has_no_verified_revenue_or_customers(self):
        code, before = self.call("GET", "/api/demo/scorecard")
        self.assertEqual(code, 200)
        self.assertTrue(before["synthetic"])
        base_count = before["counts"]["received_demo_leads"]
        self.assertEqual(before["verified"]["payment_receipts"], 0)
        self.assertEqual(before["verified"]["rre_monthly_profit_cents"], 0)
        code, _ = self.call("POST", "/api/demo/leads", {"synthetic": True,
            "external_ref": "DEMO-HTTP-42", "source": "website", "need": "repair"})
        self.assertEqual(code, 201)
        code, after = self.call("GET", "/api/demo/scorecard")
        self.assertEqual(code, 200)
        self.assertEqual(after["counts"]["received_demo_leads"], base_count + 1)
        self.assertEqual(after["counts"]["real_customers"], 0)
        self.assertEqual(after["verified"]["rre_subscription_revenue_cents"], 0)
        self.assertEqual(after["verified"]["contractor_recovered_revenue_cents"], 0)

    def test_synthetic_scenarios_show_mock_outcomes_never_sends_or_cash(self):
        for scenario, count in (("review", 3), ("appointment_mock", 6),
                                ("closed_job_mock", 7)):
            with self.subTest(scenario=scenario):
                status, data = self.call("GET", "/api/demo/scenarios/DEMO-HTTP-42/" + scenario)
                self.assertEqual(status, 200)
                result = data["scenario"]
                self.assertTrue(result["synthetic"])
                self.assertEqual(len(result["events"]), count)
                self.assertEqual(result["metrics"]["actual_messages_sent"], 0)
                self.assertEqual(result["metrics"]["verified_payment_receipts"], 0)
                self.assertEqual(result["metrics"]["verified_recovered_revenue_cents"], 0)
                self.assertTrue(all(not row["external_side_effect"] for row in result["events"]))

    def test_missing_unsafe_scenarios_and_mutations_fail(self):
        for path in ("/api/demo/scenarios/DEMO-HTTP-42/paid",
                     "/api/demo/scenarios/DEMO-HTTP-42/sent",
                     "/api/demo/scenarios/DEMO-HTTP-42/../app.py",
                     "/api/demo/scenarios/DEMO-UNKNOWN/review"):
            self.assertEqual(self.call("GET", path)[0], 404)
        for path in ("/api/demo/scorecard", "/api/demo/scenarios/DEMO-HTTP-42/closed_job_mock"):
            self.assertEqual(self.call("POST", path, {"synthetic": True})[0], 404)

    def test_invalid_url_cannot_leak_to_server_access_logs(self):
        capture = io.StringIO()
        with redirect_stderr(capture):
            status, _ = self.call("GET", "/private?email=do-not-log@example.invalid")
        self.assertEqual(status, 404)
        self.assertNotIn("do-not-log@example.invalid", capture.getvalue())

    def test_mock_browser_section_exists_and_never_submits_money(self):
        code, html = self.call("GET", "/demo/")
        self.assertEqual(code, 200)
        page = html.decode("utf-8")
        self.assertIn("Recovery process simulator", page)
        self.assertIn('id="auditEvents"', page)
        self.assertIn("Mock job close (unverified)", page)
        code, js = self.call("GET", "/demo/app.js")
        self.assertEqual(code, 200)
        src = js.decode("utf-8")
        self.assertIn('"/api/demo/scorecard"', src)
        self.assertIn('"/api/demo/scenarios/"', src)
        self.assertIn('credentials:"omit"', src)
        self.assertNotIn('fetch("/api/payments"', src)


if __name__ == "__main__":
    unittest.main()
