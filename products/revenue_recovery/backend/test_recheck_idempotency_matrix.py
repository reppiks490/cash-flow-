"""Synthetic-only recheck and idempotency negative-control matrix.

Run: python -m unittest backend.test_recheck_idempotency_matrix -v
No network, customer data, model calls, or outbound actions.
"""
import copy
import unittest

from backend.followups import prepare_followup, recheck_followup_for_review
from backend.qualification import qualify_lead


def lead(ref="QA-RECHECK-001", need="repair", source="website"):
    return {
        "synthetic": True, "external_ref": ref, "source": source,
        "need": need, "status": "received",
    }


class RecheckIdempotencyMatrixTests(unittest.TestCase):
    def test_replay_identity_and_provenance_are_stable(self):
        row = lead()
        original = qualify_lead(row, opted_out=None)
        self.assertEqual(original, qualify_lead(dict(reversed(list(row.items())))))
        self.assertEqual(original["confidence"], None)
        self.assertFalse(original["outreach_allowed"])
        self.assertTrue(all(e["provenance"] == "synthetic_intake" for e in original["evidence"]))
        for changed in (
            lead(ref="QA-RECHECK-002"),
            lead(need="maintenance"),
            lead(source="phone"),
        ):
            with self.subTest(changed=changed):
                self.assertNotEqual(
                    original["idempotency_key"],
                    qualify_lead(changed)["idempotency_key"],
                )
        for flag in (False, True):
            self.assertNotEqual(
                original["idempotency_key"],
                qualify_lead(row, opted_out=flag)["idempotency_key"],
            )

    def test_recheck_requires_new_human_review_and_never_sends(self):
        row = lead()
        prior = prepare_followup(row, opted_out=None, objection="price")
        same = recheck_followup_for_review(row, prior, opted_out=None)
        self.assertFalse(same["replay_changed"])
        self.assertEqual(same["review_status"], "fresh_human_review_required")
        self.assertEqual(same["followup"], prior)
        changed = recheck_followup_for_review(row, prior, opted_out=False)
        self.assertTrue(changed["replay_changed"])
        self.assertEqual(changed["review_status"], "fresh_human_review_required")
        for result in (same, changed):
            self.assertFalse(result["outreach_enabled"])
            self.assertFalse(result["sent"])
            self.assertTrue(result["requires_human_approval"])
            self.assertFalse(result["followup"]["send_enabled"])

    def test_opt_out_transition_suppresses_and_cannot_reuse_draft(self):
        row = lead()
        prior = prepare_followup(row, opted_out=False, objection="timing")
        refreshed = recheck_followup_for_review(row, prior, opted_out=True)
        self.assertTrue(refreshed["replay_changed"])
        self.assertEqual(refreshed["review_status"], "suppressed")
        self.assertIsNone(refreshed["followup"]["draft"])
        self.assertFalse(refreshed["followup"]["sent"])
        self.assertFalse(refreshed["followup"]["send_enabled"])

    def test_tampered_cache_is_rejected_before_reuse(self):
        row = lead()
        prior = prepare_followup(row, opted_out=None, objection="competitor")
        mutations = (
            ("draft", "forged message"),
            ("sent", True),
            ("send_enabled", True),
            ("idempotency_key", "forged"),
            ("external_ref", "QA-RECHECK-002"),
        )
        for field, value in mutations:
            with self.subTest(field=field):
                altered = copy.deepcopy(prior)
                altered[field] = value
                with self.assertRaises(ValueError):
                    recheck_followup_for_review(row, altered, opted_out=False)
        altered = copy.deepcopy(prior)
        altered["qualification"]["priority_score"] = 1000
        with self.assertRaises(ValueError):
            recheck_followup_for_review(row, altered, opted_out=False)
        with self.assertRaises(ValueError):
            recheck_followup_for_review(lead(ref="QA-RECHECK-002"), prior, opted_out=False)


if __name__ == "__main__":
    unittest.main()
