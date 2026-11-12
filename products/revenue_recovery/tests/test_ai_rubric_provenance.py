"""Offline HVAC rubric provenance and uncertainty regression contracts.

Synthetic enums only. No recipient data, model calls or outbound actions.
"""
import unittest

from backend.qualification import RULES, RUBRIC_VERSION, qualify_lead
from backend.ai_providers import build_offline_review_envelope


EXPECTED = {
    "AC not cooling": ("urgent_service", 90, "cooling_failure"),
    "heating issue": ("urgent_service", 90, "heating_failure"),
    "repair": ("service", 75, "repair_request"),
    "estimate follow-up": ("estimate_follow_up", 80, "estimate_follow_up"),
    "AC maintenance": ("maintenance", 65, "maintenance_request"),
    "maintenance": ("maintenance", 65, "maintenance_request"),
}


class RubricProvenanceTests(unittest.TestCase):
    def test_every_hvac_need_has_explainable_stable_rubric(self):
        self.assertEqual(RUBRIC_VERSION, "hvac-demo-v1")
        self.assertEqual(RULES, EXPECTED)
        for need, (category, score, rule) in EXPECTED.items():
            with self.subTest(need=need):
                lead = {
                    "synthetic": True, "external_ref": "QA-RUBRIC-001",
                    "source": "website", "need": need, "status": "received",
                }
                first = qualify_lead(lead)
                self.assertEqual(first, qualify_lead(dict(lead)))
                self.assertEqual((first["category"], first["priority_score"]), (category, score))
                self.assertEqual(first["evidence"][0], {
                    "field": "need", "value": need,
                    "rule": rule, "provenance": "synthetic_intake",
                })
                self.assertEqual(first["evidence"][1], {
                    "field": "source", "value": "website",
                    "rule": "accepted_source_category",
                    "provenance": "synthetic_intake",
                })
                self.assertIsNone(first["confidence"])
                self.assertEqual(first["confidence_kind"], "not_model_calibrated")
                self.assertIn("contact_consent", first["unknowns"])
                self.assertIn("suppression_status", first["unknowns"])
                self.assertFalse(first["outreach_allowed"])

    def test_provider_cannot_present_rules_as_model_inference(self):
        lead = {
            "synthetic": True, "external_ref": "QA-RUBRIC-002",
            "source": "demo", "need": "repair", "status": "received",
        }
        for opted_out in (None, False, True):
            with self.subTest(opted_out=opted_out):
                result = build_offline_review_envelope(lead, opted_out=opted_out)
                self.assertEqual(result["generation_kind"], "deterministic_rules_not_ai_inference")
                self.assertIs(result["uses_model"], False)
                self.assertIs(result["external_calls"], False)
                self.assertIs(result["outreach_enabled"], False)
                self.assertIs(result["requires_human_approval"], True)
                self.assertIsNone(result["qualification"]["confidence"])
                self.assertIs(result["followup"]["sent"], False)
                self.assertIs(result["followup"]["send_enabled"], False)
                if opted_out is True:
                    self.assertIsNone(result["followup"]["draft"])
                    self.assertEqual(result["followup"]["status"], "suppressed")
                else:
                    self.assertEqual(result["followup"]["status"], "pending_human_review")


if __name__ == "__main__":
    unittest.main()
