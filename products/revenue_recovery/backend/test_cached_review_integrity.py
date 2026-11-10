"""Synthetic cached-review integrity and suppression transition regression tests.

No network, recipient data, model inference, or outbound communications.
"""
import copy
import unittest

from backend.followups import prepare_followup, recheck_followup_for_review


LEAD = {
    "synthetic": True,
    "external_ref": "QA-RECHECK-INTEGRITY-001",
    "source": "website",
    "need": "repair",
    "status": "received",
}


class CachedReviewIntegrityTests(unittest.TestCase):
    def test_unknown_to_revoked_suppresses_cached_draft(self):
        prior = prepare_followup(LEAD, objection="price")
        result = recheck_followup_for_review(LEAD, prior, opted_out=True)
        self.assertEqual(result["review_status"], "suppressed")
        self.assertTrue(result["replay_changed"])
        self.assertIsNone(result["followup"]["draft"])
        self.assertEqual(result["followup"]["objection_category"], "price")
        self.assertFalse(result["outreach_enabled"])
        self.assertFalse(result["sent"])
        self.assertTrue(result["requires_human_approval"])

    def test_revoked_to_unknown_never_grants_outreach(self):
        prior = prepare_followup(LEAD, opted_out=True, objection="timing")
        result = recheck_followup_for_review(LEAD, prior, opted_out=None)
        self.assertEqual(result["review_status"], "fresh_human_review_required")
        self.assertTrue(result["replay_changed"])
        self.assertEqual(result["followup"]["status"], "pending_human_review")
        self.assertFalse(result["followup"]["send_enabled"])
        self.assertFalse(result["followup"]["qualification"]["outreach_allowed"])
        self.assertIn("suppression_status", result["followup"]["qualification"]["unknowns"])

    def test_repeated_review_is_deterministic_and_unsent(self):
        prior = prepare_followup(LEAD, opted_out=False, objection="competitor")
        first = recheck_followup_for_review(LEAD, prior, opted_out=False)
        second = recheck_followup_for_review(LEAD, prior, opted_out=False)
        self.assertEqual(first, second)
        self.assertFalse(first["replay_changed"])
        self.assertFalse(first["sent"])
        self.assertFalse(first["outreach_enabled"])

    def test_mutated_cached_snapshot_rejected_without_republishing_text(self):
        prior = prepare_followup(LEAD, objection="price")
        mutations = (
            ("draft", "Forged outreach content"),
            ("send_enabled", True),
            ("sent", True),
            ("idempotency_key", "forged"),
            ("objection_source", "verified_customer"),
        )
        for field, value in mutations:
            with self.subTest(field=field):
                tampered = copy.deepcopy(prior)
                tampered[field] = value
                with self.assertRaises(ValueError):
                    recheck_followup_for_review(LEAD, tampered, opted_out=None)

    def test_forged_prior_suppression_and_lead_mismatch_rejected(self):
        prior = prepare_followup(LEAD, opted_out=True)
        tampered = copy.deepcopy(prior)
        tampered["qualification"]["opted_out"] = False
        with self.assertRaises(ValueError):
            recheck_followup_for_review(LEAD, tampered, opted_out=False)
        other_lead = dict(LEAD, external_ref="QA-RECHECK-INTEGRITY-002")
        with self.assertRaises(ValueError):
            recheck_followup_for_review(other_lead, prior, opted_out=True)


if __name__ == "__main__":
    unittest.main()
