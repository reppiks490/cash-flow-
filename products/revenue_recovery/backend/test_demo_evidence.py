"""Regression checks for strictly synthetic, non-monetizing evidence timelines."""
import unittest

from backend.demo_evidence import (
    SCENARIOS, aggregate_synthetic_scorecard, simulate_evidence_path,
)


def sample(ref="DEMO-EVIDENCE-01", need="AC not cooling"):
    return {"synthetic": True, "external_ref": ref, "source": "website",
            "need": need, "status": "received"}


class EvidenceSimulationTests(unittest.TestCase):
    def test_valid_scenarios_are_deterministic_and_provenance_labeled(self):
        for name, length in (("review", 3), ("appointment_mock", 6),
                             ("closed_job_mock", 7)):
            with self.subTest(name=name):
                first = simulate_evidence_path(sample(), name)
                self.assertEqual(first, simulate_evidence_path(sample(), name))
                self.assertTrue(first["synthetic"])
                self.assertEqual(first["source"], "local_fixture_only")
                self.assertEqual(len(first["events"]), length)
                self.assertEqual([e["sequence"] for e in first["events"]],
                                 list(range(1, length + 1)))
                self.assertTrue(all(e["synthetic"] for e in first["events"]))
                self.assertTrue(all(not e["source_evidence_verified"]
                                    for e in first["events"]))
                self.assertTrue(all(not e["external_side_effect"]
                                    for e in first["events"]))
                self.assertEqual(len({e["event_id"] for e in first["events"]}), length)

    def test_mock_close_never_claims_actual_revenue_or_booking(self):
        report = simulate_evidence_path(sample(), "closed_job_mock")
        metrics = report["metrics"]
        self.assertEqual(metrics["mock_closed_jobs"], 1)
        self.assertEqual(metrics["actual_jobs_closed"], 0)
        self.assertEqual(metrics["actual_bookings_confirmed"], 0)
        self.assertEqual(metrics["actual_messages_sent"], 0)
        self.assertEqual(metrics["verified_recovered_revenue_cents"], 0)
        self.assertEqual(metrics["verified_contractor_collections_cents"], 0)
        self.assertEqual(metrics["verified_rre_subscription_revenue_cents"], 0)
        self.assertEqual(metrics["verified_payment_receipts"], 0)
        self.assertFalse(report["attribution"]["authenticated_payment_evidence"])
        self.assertFalse(report["gates"]["real_outreach_enabled"])
        self.assertFalse(report["gates"]["human_approval_authenticated"])

    def test_invalid_scenarios_rejected_including_boolean_or_pii(self):
        for scenario in ("paid", "verified", "sent", "refund_mock",
                         "DEMO/../secrets", True, 2, None, ""):
            with self.subTest(scenario=scenario), self.assertRaises(ValueError):
                simulate_evidence_path(sample(), scenario)

    def test_invalid_lead_does_not_enter_evidence_path(self):
        for change in ({"synthetic": False}, {"email": "sample@example.invalid"},
                       {"external_ref": "1234567890"}, {"need": "custom free text"},
                       {"status": "paid"}):
            with self.subTest(change=change), self.assertRaises(ValueError):
                simulate_evidence_path({**sample(), **change})

    def test_scorecard_counts_no_leads_and_never_fabricates_payments(self):
        for leads in ([], [sample()]):
            score = aggregate_synthetic_scorecard(leads)
            self.assertTrue(score["synthetic"])
            self.assertEqual(score["counts"]["received_demo_leads"], len(leads))
            self.assertEqual(score["counts"]["real_customers"], 0)
            self.assertEqual(score["verified"]["payment_receipts"], 0)
            self.assertEqual(score["verified"]["rre_subscription_revenue_cents"], 0)
            self.assertEqual(score["verified"]["rre_monthly_profit_cents"], 0)
            self.assertEqual(score["verified"]["contractor_recovered_revenue_cents"], 0)

    def test_scorecard_rejects_duplicates_untrusted_status_and_non_list(self):
        for leads in (
            [sample("DEMO-REPEAT"), sample("DEMO-REPEAT")],
            [sample("DEMO-OK"), {**sample("DEMO-BAD"), "status": "verified"}],
            [sample("DEMO-OK"), {**sample("DEMO-BAD"), "name": "person"}],
            {"leads": [sample()]},
        ):
            with self.subTest(leads=leads), self.assertRaises(ValueError):
                aggregate_synthetic_scorecard(leads)

    def test_scenario_registry_is_strict(self):
        self.assertEqual(SCENARIOS, {"review", "appointment_mock", "closed_job_mock"})


if __name__ == "__main__":
    unittest.main()
