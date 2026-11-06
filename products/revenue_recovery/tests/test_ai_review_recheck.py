"""Pure review-time synthetic draft refresh; no recipient identity or real consent."""
import unittest

from backend import followups
from backend.followups import prepare_followup


LEAD = {
    "synthetic": True,
    "external_ref": "QA-RECHECK-01",
    "source": "referral",
    "need": "heating issue",
    "status": "received",
}


class ReviewRecheckTests(unittest.TestCase):
    def recheck(self, prior, *, opted_out):
        function = getattr(followups, "recheck_followup_for_review", None)
        self.assertIsNotNone(function, "Pure review-time recheck is missing")
        return function(LEAD, prior, opted_out=opted_out)

    def test_revocation_replaces_cached_internal_draft_with_suppression(self):
        for objection in (None, "price", "timing", "competitor"):
            with self.subTest(objection=objection):
                old = prepare_followup(LEAD, opted_out=False, objection=objection)
                old_copy = dict(old)
                result = self.recheck(old, opted_out=True)
                self.assertEqual(result["schema_version"], "rre-review-recheck-v1")
                self.assertIs(result["synthetic"], True)
                self.assertIs(result["replay_changed"], True)
                self.assertEqual(result["review_status"], "suppressed")
                self.assertIs(result["outreach_enabled"], False)
                self.assertIs(result["sent"], False)
                self.assertIs(result["requires_human_approval"], True)
                self.assertIsNone(result["followup"]["draft"])
                self.assertEqual(result["followup"]["status"], "suppressed")
                self.assertIs(result["followup"]["send_enabled"], False)
                self.assertEqual(old, old_copy)
                if objection is not None:
                    self.assertEqual(result["followup"]["objection_category"], objection)

    def test_unchanged_or_rescinded_mock_still_needs_new_human_review(self):
        unknown = prepare_followup(LEAD, opted_out=None)
        same = self.recheck(unknown, opted_out=None)
        self.assertIs(same["replay_changed"], False)
        self.assertEqual(same["review_status"], "fresh_human_review_required")
        self.assertIs(same["requires_human_approval"], True)
        self.assertIs(same["followup"]["send_enabled"], False)

        revoked = prepare_followup(LEAD, opted_out=True)
        rescinded_mock = self.recheck(revoked, opted_out=False)
        self.assertIs(rescinded_mock["replay_changed"], True)
        self.assertEqual(rescinded_mock["review_status"], "fresh_human_review_required")
        self.assertIsInstance(rescinded_mock["followup"]["draft"], str)
        self.assertIs(rescinded_mock["outreach_enabled"], False)
        self.assertIs(rescinded_mock["followup"]["sent"], False)

    def test_forged_or_mismatched_cached_snapshots_fail_closed(self):
        valid = prepare_followup(LEAD, opted_out=False, objection="price")
        forged = [
            None, [], "unsafe", {},
            {**valid, "sent": True},
            {**valid, "send_enabled": True},
            {**valid, "requires_human_approval": False},
            {**valid, "draft": "pretend appointment confirmed"},
            {**valid, "external_ref": "QA-OTHER"},
            {**valid, "customer_email": "none@example.invalid"},
            {**valid, "objection_source": "verified_customer"},
            {**valid, "qualification": {**valid["qualification"], "opted_out": True}},
        ]
        for bad in forged:
            with self.subTest(bad=repr(bad)[:80]), self.assertRaises(ValueError):
                self.recheck(bad, opted_out=True)

    def test_invalid_new_mock_suppression_flag_rejected(self):
        prior = prepare_followup(LEAD)
        for bad in ("false", 0, 1, [], {}, ""):
            with self.subTest(flag=repr(bad)), self.assertRaises(ValueError):
                self.recheck(prior, opted_out=bad)


if __name__ == "__main__":
    unittest.main()
