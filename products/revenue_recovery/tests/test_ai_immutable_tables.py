"""Synthetic-only regression: offline rubric and draft tables reject in-place edits."""
import unittest

from backend import qualification, followups
from backend.ai_providers import preview_offline_bundle


LEAD = {
    "synthetic": True,
    "external_ref": "DEMO-IMMUTABLE-01",
    "source": "website",
    "need": "repair",
    "status": "received",
}


class ImmutableDemoTablesTests(unittest.TestCase):
    def test_rule_table_cannot_change_scoring(self):
        original = qualification.RULES["repair"]
        with self.assertRaises(TypeError):
            qualification.RULES["repair"] = ("urgent_service", 100, "forged")
        self.assertEqual(qualification.RULES["repair"], original)

    def test_draft_tables_cannot_change_wording(self):
        for table, key in (
            (followups.MESSAGES, "repair"),
            (followups.OBJECTION_TEMPLATES, "price"),
        ):
            original = table[key]
            with self.subTest(key=key):
                with self.assertRaises(TypeError):
                    table[key] = "Forged discount and confirmed appointment."
                self.assertEqual(table[key], original)

    def test_clean_preview_remains_internal_and_deterministic(self):
        first = preview_offline_bundle(LEAD, objection="price")
        self.assertEqual(first, preview_offline_bundle(LEAD, objection="price"))
        self.assertEqual(first["qualification"]["priority_score"], 75)
        self.assertFalse(first["send_enabled"])
        self.assertFalse(first["sent"])
        self.assertTrue(first["requires_human_approval"])
        self.assertIn("no price", first["followup"]["draft"].lower())

    def test_suppression_remains_no_draft(self):
        result = preview_offline_bundle(LEAD, opted_out=True)
        self.assertEqual(result["followup"]["status"], "suppressed")
        self.assertIsNone(result["followup"]["draft"])
        self.assertFalse(result["send_enabled"])


if __name__ == "__main__":
    unittest.main()
