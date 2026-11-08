"""RRE-05: synthetic lifecycle transitions must never mint real financial evidence.

Pure deterministic tests; no customer data, network, provider credentials or paid calls.
"""
import copy
import unittest

from backend.demo_evidence import aggregate_synthetic_scorecard, simulate_evidence_path


def lead(ref="QA-HVAC-001", need="repair"):
    return {
        "synthetic": True, "external_ref": ref, "source": "website",
        "need": need, "status": "received",
    }


class EvidenceMetamorphicGate(unittest.TestCase):
    def test_lifecycle_progression_never_promotes_mock_outcomes_to_verified(self):
        for need in ("repair", "AC maintenance", "heating issue"):
            with self.subTest(need=need):
                previous = -1
                for scenario in ("review", "appointment_mock", "closed_job_mock"):
                    result = simulate_evidence_path(lead(need=need), scenario)
                    self.assertIs(result["synthetic"], True)
                    self.assertGreater(len(result["events"]), previous)
                    previous = len(result["events"])
                    self.assertTrue(all(event["synthetic"] is True for event in result["events"]))
                    self.assertTrue(all(event["provider_receipt"] is None for event in result["events"]))
                    self.assertTrue(all(event["external_side_effect"] is False for event in result["events"]))
                    self.assertTrue(all(event["operator_action_authenticated"] is False for event in result["events"]))
                    metrics = result["metrics"]
                    for key in (
                        "actual_messages_sent", "actual_bookings_confirmed",
                        "actual_jobs_closed", "verified_contractor_collections_cents",
                        "verified_recovered_revenue_cents",
                        "verified_rre_subscription_revenue_cents",
                        "verified_payment_receipts",
                    ):
                        self.assertEqual(metrics[key], 0, (scenario, key))
                    self.assertFalse(result["attribution"]["authenticated_payment_evidence"])
                    self.assertFalse(result["gates"]["real_outreach_enabled"])
                    self.assertFalse(result["gates"]["payment_verification_enabled"])
                    self.assertEqual(result["attribution"]["status"], "unverifiable_synthetic_only")

    def test_scorecard_never_converts_demo_volume_to_real_customers_or_profit(self):
        for count in (0, 1, 3):
            with self.subTest(count=count):
                rows = [lead(f"QA-HVAC-{i:03d}") for i in range(count)]
                score = aggregate_synthetic_scorecard(rows)
                self.assertEqual(score["counts"]["received_demo_leads"], count)
                self.assertIsNone(score["counts"]["real_customers"])
                self.assertTrue(all(value == 0 for value in score["verified"].values()))
                self.assertIs(score["synthetic"], True)
                self.assertEqual(rows, [lead(f"QA-HVAC-{i:03d}") for i in range(count)])

    def test_duplicate_or_spoofed_financial_evidence_rejected_without_mutation(self):
        original = lead()
        for candidate in (
            [original, copy.deepcopy(original)],
            [{**original, "payment_receipt": "FAKE"}],
            [{**original, "synthetic": False}],
        ):
            before = copy.deepcopy(candidate)
            with self.subTest(candidate=candidate):
                with self.assertRaises(ValueError):
                    aggregate_synthetic_scorecard(candidate)
                self.assertEqual(candidate, before)


if __name__ == "__main__":
    unittest.main()
