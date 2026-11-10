"""Synthetic-only HVAC objection matrix: no recipient, sending, or model I/O."""
import unittest

from backend.followups import OBJECTION_TEMPLATES, prepare_followup
from backend.ai_providers import build_offline_review_envelope


def lead(need="repair"):
    return {"synthetic": True, "external_ref": "QA-OBJECTION-MATRIX",
            "source": "website", "need": need, "status": "received"}


class ObjectionMatrixTests(unittest.TestCase):
    def test_each_approved_objection_is_deterministic_and_review_only(self):
        for objection in sorted(OBJECTION_TEMPLATES):
            with self.subTest(objection=objection):
                first = prepare_followup(lead(), objection=objection)
                second = prepare_followup(lead(), objection=objection)
                self.assertEqual(first, second)
                self.assertEqual(first["objection_category"], objection)
                self.assertEqual(first["objection_source"],
                                 "unverified_caller_supplied_synthetic_enum")
                self.assertIn(OBJECTION_TEMPLATES[objection], first["draft"])
                self.assertEqual(first["status"], "pending_human_review")
                self.assertIs(first["sent"], False)
                self.assertIs(first["send_enabled"], False)
                self.assertIs(first["requires_human_approval"], True)
                self.assertIs(first["qualification"]["outreach_allowed"], False)
                self.assertIsNone(first["qualification"]["confidence"])

    def test_objections_change_replay_identity_without_changing_qualification(self):
        baseline = prepare_followup(lead())
        keys = {baseline["idempotency_key"]}
        for objection in sorted(OBJECTION_TEMPLATES):
            draft = prepare_followup(lead(), objection=objection)
            self.assertEqual(draft["qualification"], baseline["qualification"])
            self.assertNotIn(draft["idempotency_key"], keys)
            keys.add(draft["idempotency_key"])
        self.assertEqual(len(keys), len(OBJECTION_TEMPLATES) + 1)

    def test_opt_out_suppresses_every_objection_and_never_exposes_text(self):
        for objection in (None, *sorted(OBJECTION_TEMPLATES)):
            with self.subTest(objection=objection):
                result = build_offline_review_envelope(
                    lead("estimate follow-up"), opted_out=True, objection=objection)
                self.assertIsNone(result["followup"]["draft"])
                self.assertEqual(result["followup"]["status"], "suppressed")
                self.assertEqual(result["qualification"]["decision"], "suppressed")
                self.assertIs(result["outreach_enabled"], False)
                self.assertIs(result["external_calls"], False)
                self.assertIs(result["uses_model"], False)

    def test_unknown_consent_never_becomes_outreach_permission(self):
        for objection in sorted(OBJECTION_TEMPLATES):
            with self.subTest(objection=objection):
                result = build_offline_review_envelope(lead(), objection=objection)
                self.assertIn("suppression_status",
                              result["qualification"]["unknowns"])
                self.assertIs(result["qualification"]["outreach_allowed"], False)
                self.assertIs(result["outreach_enabled"], False)
                self.assertIs(result["followup"]["send_enabled"], False)

    def test_free_text_or_non_string_objections_fail_closed(self):
        for invalid in ("other", "please call 555-0100", "", 0, True, [], {}):
            with self.subTest(invalid=repr(invalid)):
                with self.assertRaises(ValueError):
                    prepare_followup(lead(), objection=invalid)
                with self.assertRaises(ValueError):
                    build_offline_review_envelope(lead(), objection=invalid)


if __name__ == "__main__":
    unittest.main()
