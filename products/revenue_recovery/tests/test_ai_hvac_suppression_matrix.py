"""Exhaustive synthetic HVAC category/suppression invariants; no outbound I/O."""
import unittest

from backend.contracts import NEEDS, SOURCES
from backend.followups import OBJECTION_TEMPLATES, prepare_followup
from backend.qualification import qualify_lead


class HVACSuppressionMatrixTests(unittest.TestCase):
    def test_all_need_source_objection_and_suppression_combinations(self):
        """6 needs x 4 sources x 4 objection states x 3 suppression states."""
        for need in sorted(NEEDS):
            for source in sorted(SOURCES):
                lead = {
                    "synthetic": True,
                    "external_ref": "QA-MATRIX-001",
                    "source": source,
                    "need": need,
                    "status": "received",
                }
                for objection in (None, *sorted(OBJECTION_TEMPLATES)):
                    for opted_out in (None, False, True):
                        with self.subTest(need=need, source=source,
                                          objection=objection, opted_out=opted_out):
                            first = prepare_followup(
                                lead, opted_out=opted_out, objection=objection
                            )
                            second = prepare_followup(
                                lead, opted_out=opted_out, objection=objection
                            )
                            self.assertEqual(first, second)
                            self.assertIs(first["synthetic"], True)
                            self.assertIs(first["sent"], False)
                            self.assertIs(first["send_enabled"], False)
                            self.assertIs(first["requires_human_approval"], True)
                            self.assertEqual(first["external_ref"], lead["external_ref"])
                            qualification = first["qualification"]
                            self.assertEqual(
                                qualification, qualify_lead(lead, opted_out=opted_out)
                            )
                            self.assertIs(qualification["outreach_allowed"], False)
                            self.assertIsNone(qualification["confidence"])
                            self.assertEqual(
                                {e["provenance"] for e in qualification["evidence"]},
                                {"synthetic_intake"},
                            )
                            self.assertIn("contact_consent", qualification["unknowns"])
                            if opted_out is True:
                                self.assertEqual(first["status"], "suppressed")
                                self.assertIsNone(first["draft"])
                            else:
                                self.assertEqual(first["status"], "pending_human_review")
                                self.assertIsInstance(first["draft"], str)
                                self.assertIn("internal synthetic preview", first["draft"])
                            if objection is None:
                                self.assertNotIn("objection_category", first)
                            else:
                                self.assertEqual(first["objection_category"], objection)
                                if opted_out is not True:
                                    self.assertIn(OBJECTION_TEMPLATES[objection], first["draft"])

    def test_opt_out_and_objection_change_replay_identity(self):
        lead = {
            "synthetic": True, "external_ref": "QA-MATRIX-002",
            "source": "demo", "need": "repair", "status": "received",
        }
        keys = {
            prepare_followup(lead, opted_out=flag, objection=objection)["idempotency_key"]
            for flag in (None, False, True)
            for objection in (None, *sorted(OBJECTION_TEMPLATES))
        }
        self.assertEqual(len(keys), 12)


if __name__ == "__main__":
    unittest.main()
