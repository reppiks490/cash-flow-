"""Synthetic HVAC rubric coverage and no-outreach invariants (stdlib only)."""
import unittest

from backend.qualification import RULES, qualify_lead
from backend.followups import MESSAGES, OBJECTION_TEMPLATES, prepare_followup


def lead(need, source="website"):
    return {"synthetic": True, "external_ref": "QA-RUBRIC-001",
            "source": source, "need": need, "status": "received"}


class RubricCoverageTests(unittest.TestCase):
    def test_every_supported_need_has_an_explainable_rule_and_template(self):
        self.assertEqual(set(RULES), set(MESSAGES))
        for need, (category, score, rule_id) in RULES.items():
            with self.subTest(need=need):
                self.assertTrue(category)
                self.assertTrue(rule_id)
                self.assertIs(type(score), int)
                self.assertGreaterEqual(score, 0)
                self.assertLessEqual(score, 100)
                q = qualify_lead(lead(need))
                self.assertEqual(q["category"], category)
                self.assertEqual(q["priority_score"], score)
                self.assertEqual(q["evidence"][0]["rule"], rule_id)
                self.assertEqual(q["evidence"][0]["value"], need)
                self.assertIsNone(q["confidence"])
                self.assertIs(q["outreach_allowed"], False)

    def test_all_needs_remain_inert_across_suppression_states(self):
        for need in RULES:
            for flag in (None, False, True):
                with self.subTest(need=need, opted_out=flag):
                    result = prepare_followup(lead(need), opted_out=flag)
                    self.assertIs(result["sent"], False)
                    self.assertIs(result["send_enabled"], False)
                    self.assertIs(result["requires_human_approval"], True)
                    self.assertEqual(result["qualification"]["opted_out"], flag)
                    if flag is True:
                        self.assertIsNone(result["draft"])
                        self.assertEqual(result["status"], "suppressed")
                    else:
                        self.assertEqual(result["status"], "pending_human_review")
                        self.assertIn("internal synthetic preview only", result["draft"])
                        self.assertIn("human approval", result["draft"])

    def test_objection_templates_are_bounded_and_never_override_opt_out(self):
        self.assertEqual(set(OBJECTION_TEMPLATES), {"price", "timing", "competitor"})
        for objection in OBJECTION_TEMPLATES:
            with self.subTest(objection=objection):
                result = prepare_followup(lead("repair"), objection=objection)
                self.assertIn(OBJECTION_TEMPLATES[objection], result["draft"])
                self.assertEqual(result["objection_source"],
                                 "unverified_caller_supplied_synthetic_enum")
                suppressed = prepare_followup(
                    lead("repair"), objection=objection, opted_out=True)
                self.assertIsNone(suppressed["draft"])
                self.assertIs(suppressed["send_enabled"], False)

    def test_evidence_does_not_claim_real_consent_or_model_calibration(self):
        for need in RULES:
            q = qualify_lead(lead(need))
            self.assertEqual(q["confidence_kind"], "not_model_calibrated")
            self.assertIn("contact_consent", q["unknowns"])
            self.assertIn("real_inquiry_provenance", q["unknowns"])
            self.assertTrue(all(e["provenance"] == "synthetic_intake"
                                for e in q["evidence"]))


if __name__ == "__main__":
    unittest.main()
