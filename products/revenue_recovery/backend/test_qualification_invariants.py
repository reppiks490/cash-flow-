"""Synthetic-only invariants for deterministic HVAC qualification and draft review."""
import unittest

from backend.qualification import qualify_lead
from backend.followups import prepare_followup, recheck_followup_for_review

LEAD = {
    "synthetic": True,
    "external_ref": "QA-INVARIANT-001",
    "source": "website",
    "need": "repair",
    "status": "received",
}


class QualificationInvariantTests(unittest.TestCase):
    def test_replay_stable_and_input_unchanged(self):
        original = dict(LEAD)
        first = qualify_lead(LEAD)
        self.assertEqual(first, qualify_lead(dict(LEAD)))
        self.assertEqual(LEAD, original)
        self.assertIsNone(first["confidence"])
        self.assertEqual(first["confidence_kind"], "not_model_calibrated")
        self.assertIn("suppression_status", first["unknowns"])
        self.assertFalse(first["outreach_allowed"])

    def test_suppression_changes_replay_identity_not_evidence(self):
        unknown = qualify_lead(LEAD)
        clear = qualify_lead(LEAD, opted_out=False)
        suppressed = qualify_lead(LEAD, opted_out=True)
        self.assertEqual(len({unknown["idempotency_key"], clear["idempotency_key"],
                              suppressed["idempotency_key"]}), 3)
        self.assertEqual(unknown["evidence"], clear["evidence"])
        self.assertEqual(clear["evidence"], suppressed["evidence"])
        self.assertEqual(suppressed["decision"], "suppressed")
        self.assertFalse(suppressed["outreach_allowed"])

    def test_objection_changes_draft_identity_without_sending(self):
        standard = prepare_followup(LEAD)
        price = prepare_followup(LEAD, objection="price")
        timing = prepare_followup(LEAD, objection="timing")
        keys = {item["idempotency_key"] for item in (standard, price, timing)}
        self.assertEqual(len(keys), 3)
        for item in (standard, price, timing):
            self.assertFalse(item["sent"])
            self.assertFalse(item["send_enabled"])
            self.assertTrue(item["requires_human_approval"])
            self.assertEqual(item["status"], "pending_human_review")

    def test_recheck_suppression_never_reuses_old_draft(self):
        prior = prepare_followup(LEAD, opted_out=False, objection="price")
        refreshed = recheck_followup_for_review(LEAD, prior, opted_out=True)
        self.assertEqual(refreshed["review_status"], "suppressed")
        self.assertTrue(refreshed["replay_changed"])
        self.assertIsNone(refreshed["followup"]["draft"])
        self.assertFalse(refreshed["sent"])
        self.assertFalse(refreshed["outreach_enabled"])

    def test_reject_nonboolean_suppression(self):
        for invalid in (0, 1, "false", [], {}):
            with self.subTest(value=repr(invalid)):
                with self.assertRaises(ValueError):
                    prepare_followup(LEAD, opted_out=invalid)


if __name__ == "__main__":
    unittest.main()
