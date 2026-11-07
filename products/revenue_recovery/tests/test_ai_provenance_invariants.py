"""Synthetic HVAC qualification provenance invariants (offline, no external calls)."""
import unittest

from backend.ai_providers import get_provider
from backend.qualification import RULES, qualify_lead


def lead(ref="DEMO-001", source="website", need="repair"):
    return {"synthetic": True, "external_ref": ref, "source": source,
            "need": need, "status": "received"}


class QualificationProvenanceTests(unittest.TestCase):
    def test_all_rubric_categories_have_source_backed_evidence(self):
        from backend.contracts import SOURCES
        source = sorted(SOURCES)[0]
        for need, (category, priority, rule) in RULES.items():
            with self.subTest(need=need):
                result = qualify_lead(lead(source=source, need=need))
                self.assertEqual(result["category"], category)
                self.assertEqual(result["priority_score"], priority)
                self.assertEqual(result["confidence_kind"], "not_model_calibrated")
                self.assertIsNone(result["confidence"])
                self.assertFalse(result["outreach_allowed"])
                self.assertEqual(result["evidence"], [
                    {"field": "need", "value": need, "rule": rule,
                     "provenance": "synthetic_intake"},
                    {"field": "source", "value": source,
                     "rule": "accepted_source_category",
                     "provenance": "synthetic_intake"},
                ])

    def test_unknown_suppression_never_implies_consent(self):
        q = qualify_lead(lead(), opted_out=None)
        self.assertIn("suppression_status", q["unknowns"])
        self.assertIn("contact_consent", q["unknowns"])
        self.assertFalse(q["outreach_allowed"])
        draft = get_provider("offline").draft(lead(), opted_out=None)
        self.assertFalse(draft["sent"])
        self.assertFalse(draft["send_enabled"])
        self.assertTrue(draft["requires_human_approval"])

    def test_non_synthetic_and_extra_fields_rejected(self):
        for patch in ({"synthetic": False}, {"email": "not-allowed"},
                      {"status": "closed"}):
            with self.subTest(patch=patch):
                with self.assertRaises(ValueError):
                    qualify_lead({**lead(), **patch})

    def test_provider_is_explicitly_non_model(self):
        provider = get_provider("offline")
        self.assertFalse(provider.uses_model)
        self.assertFalse(provider.external_calls)
        with self.assertRaises(ValueError):
            get_provider("remote")


if __name__ == "__main__":
    unittest.main()
