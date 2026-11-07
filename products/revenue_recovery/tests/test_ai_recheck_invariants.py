"""Synthetic-only cached draft review regression; no contact or I/O."""
import copy
import unittest

from backend.followups import prepare_followup, recheck_followup_for_review

LEAD = {
    "synthetic": True,
    "external_ref": "QA-RECHECK-20261107",
    "source": "website",
    "need": "repair",
    "status": "received",
}


class RecheckInvariantsTests(unittest.TestCase):
    def test_unknown_to_optout_suppresses_without_reusing_text(self):
        prior = prepare_followup(LEAD, opted_out=None, objection="price")
        original = copy.deepcopy(prior)
        result = recheck_followup_for_review(LEAD, prior, opted_out=True)
        self.assertEqual(prior, original)
        self.assertEqual(result["review_status"], "suppressed")
        self.assertTrue(result["replay_changed"])
        self.assertIsNone(result["followup"]["draft"])
        self.assertFalse(result["followup"]["sent"])
        self.assertFalse(result["outreach_enabled"])
        self.assertEqual(result["followup"]["objection_category"], "price")

    def test_same_fixture_replay_is_stable_but_never_authorized(self):
        for flag in (None, False, True):
            with self.subTest(flag=flag):
                prior = prepare_followup(LEAD, opted_out=flag)
                result = recheck_followup_for_review(LEAD, prior, opted_out=flag)
                self.assertFalse(result["replay_changed"])
                self.assertEqual(result["followup"], prior)
                self.assertFalse(result["outreach_enabled"])
                self.assertTrue(result["requires_human_approval"])

    def test_optout_to_unknown_does_not_restore_contact_permission(self):
        prior = prepare_followup(LEAD, opted_out=True)
        result = recheck_followup_for_review(LEAD, prior, opted_out=None)
        self.assertTrue(result["replay_changed"])
        self.assertEqual(result["review_status"], "fresh_human_review_required")
        self.assertFalse(result["followup"]["send_enabled"])
        self.assertFalse(result["followup"]["qualification"]["outreach_allowed"])
        self.assertIn("suppression_status", result["followup"]["qualification"]["unknowns"])

    def test_rejects_cached_draft_tampering(self):
        prior = prepare_followup(LEAD, opted_out=False)
        for field, value in (("draft", "Appointment confirmed."), ("sent", True),
                             ("send_enabled", True), ("recipient_email", "fake@example.invalid")):
            with self.subTest(field=field):
                changed = copy.deepcopy(prior)
                changed[field] = value
                with self.assertRaises(ValueError):
                    recheck_followup_for_review(LEAD, changed, opted_out=False)

    def test_rejects_replay_against_different_synthetic_lead(self):
        prior = prepare_followup(LEAD, opted_out=False)
        with self.assertRaises(ValueError):
            recheck_followup_for_review({**LEAD, "need": "maintenance"}, prior, opted_out=False)


if __name__ == "__main__":
    unittest.main()
