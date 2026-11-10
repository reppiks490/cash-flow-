"""Synthetic-only regression checks for cached follow-up re-review.

No customer records, network calls, or outbound messages.
"""
import copy
import unittest

from backend.followups import prepare_followup, recheck_followup_for_review


LEAD = {
    "synthetic": True,
    "external_ref": "DEMO-RECHECK-01",
    "source": "demo",
    "need": "estimate follow-up",
    "status": "received",
}


class ReviewRecheckInvariants(unittest.TestCase):
    def test_unknown_to_opt_out_suppresses_and_discards_draft(self):
        old = prepare_followup(LEAD, opted_out=None, objection="price")
        result = recheck_followup_for_review(LEAD, old, opted_out=True)
        self.assertEqual(result["review_status"], "suppressed")
        self.assertTrue(result["replay_changed"])
        self.assertIsNone(result["followup"]["draft"])
        self.assertFalse(result["outreach_enabled"])
        self.assertFalse(result["sent"])
        self.assertFalse(result["followup"]["send_enabled"])

    def test_opt_out_to_false_never_authorizes_send(self):
        old = prepare_followup(LEAD, opted_out=True, objection="timing")
        result = recheck_followup_for_review(LEAD, old, opted_out=False)
        self.assertEqual(result["review_status"], "fresh_human_review_required")
        self.assertTrue(result["replay_changed"])
        self.assertTrue(result["requires_human_approval"])
        self.assertFalse(result["outreach_enabled"])
        self.assertFalse(result["followup"]["send_enabled"])
        self.assertFalse(result["sent"])

    def test_unchanged_recheck_is_deterministic(self):
        old = prepare_followup(LEAD, opted_out=False, objection="competitor")
        a = recheck_followup_for_review(LEAD, old, opted_out=False)
        b = recheck_followup_for_review(LEAD, old, opted_out=False)
        self.assertEqual(a, b)
        self.assertFalse(a["replay_changed"])

    def test_tampered_cached_body_is_rejected(self):
        old = prepare_followup(LEAD, opted_out=False)
        tampered = copy.deepcopy(old)
        tampered["draft"] = "A confirmed appointment has been booked."
        with self.assertRaises(ValueError):
            recheck_followup_for_review(LEAD, tampered, opted_out=False)

    def test_tampered_cached_consent_metadata_is_rejected(self):
        old = prepare_followup(LEAD, opted_out=None)
        tampered = copy.deepcopy(old)
        tampered["qualification"]["outreach_allowed"] = True
        with self.assertRaises(ValueError):
            recheck_followup_for_review(LEAD, tampered, opted_out=False)

    def test_invalid_current_suppression_type_rejected(self):
        old = prepare_followup(LEAD, opted_out=False)
        for invalid in ("false", 0, [], {}):
            with self.subTest(invalid=invalid):
                with self.assertRaises(ValueError):
                    recheck_followup_for_review(LEAD, old, opted_out=invalid)


if __name__ == "__main__":
    unittest.main()
