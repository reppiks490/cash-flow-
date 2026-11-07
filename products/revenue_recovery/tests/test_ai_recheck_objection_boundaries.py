"""Synthetic-only cached follow-up objection and suppression boundary tests."""
import copy
import unittest

from backend.followups import prepare_followup, recheck_followup_for_review

LEAD = {
    "synthetic": True,
    "external_ref": "QA-OBJECTION-BOUNDARY-1",
    "source": "website",
    "need": "estimate follow-up",
    "status": "received",
}


class RecheckObjectionBoundaries(unittest.TestCase):
    def test_each_objection_preserved_without_sending(self):
        for objection in ("price", "timing", "competitor"):
            with self.subTest(objection=objection):
                prior = prepare_followup(LEAD, opted_out=False, objection=objection)
                result = recheck_followup_for_review(LEAD, prior, opted_out=None)
                draft = result["followup"]
                self.assertEqual(draft["objection_category"], objection)
                self.assertEqual(result["review_status"], "fresh_human_review_required")
                self.assertTrue(result["replay_changed"])
                self.assertIs(draft["sent"], False)
                self.assertIs(draft["send_enabled"], False)
                self.assertIs(result["outreach_enabled"], False)

    def test_opt_out_suppresses_each_objection_and_removes_text(self):
        for objection in ("price", "timing", "competitor"):
            with self.subTest(objection=objection):
                prior = prepare_followup(LEAD, opted_out=None, objection=objection)
                result = recheck_followup_for_review(LEAD, prior, opted_out=True)
                self.assertEqual(result["review_status"], "suppressed")
                self.assertIsNone(result["followup"]["draft"])
                self.assertEqual(result["followup"]["objection_category"], objection)
                self.assertIs(result["followup"]["sent"], False)

    def test_forged_objection_provenance_is_rejected(self):
        prior = prepare_followup(LEAD, opted_out=False, objection="price")
        forged = copy.deepcopy(prior)
        forged["objection_source"] = "verified_customer"
        with self.assertRaisesRegex(ValueError, "Cached synthetic draft"):
            recheck_followup_for_review(LEAD, forged, opted_out=False)

    def test_forged_objection_category_is_rejected(self):
        prior = prepare_followup(LEAD, opted_out=False, objection="price")
        forged = copy.deepcopy(prior)
        forged["objection_category"] = "competitor"
        with self.assertRaisesRegex(ValueError, "Cached synthetic draft"):
            recheck_followup_for_review(LEAD, forged, opted_out=False)

    def test_invalid_current_suppression_flag_fails_closed(self):
        prior = prepare_followup(LEAD, opted_out=False, objection="timing")
        for invalid in ("false", 0, [], {}):
            with self.subTest(invalid=invalid):
                with self.assertRaises(ValueError):
                    recheck_followup_for_review(LEAD, prior, opted_out=invalid)


if __name__ == "__main__":
    unittest.main()
