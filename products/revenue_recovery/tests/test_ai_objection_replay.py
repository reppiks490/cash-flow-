"""Synthetic HVAC objection replay and suppression regression contracts.

Stdlib-only: python -m unittest discover -s products/revenue_recovery/tests -p 'test_ai_objection_replay.py'
No recipient data, network access, or external actions.
"""
import copy
import pathlib
import sys
import unittest

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))

from backend.followups import prepare_followup, recheck_followup_for_review
from backend.ai_providers import build_offline_review_envelope


LEAD = {
    "synthetic": True,
    "external_ref": "DEMO-001",
    "source": "website",
    "need": "estimate follow-up",
    "status": "received",
}


class ObjectionReplayTests(unittest.TestCase):
    def test_each_objection_has_distinct_stable_review_identity(self):
        identities = set()
        for objection in (None, "price", "timing", "competitor"):
            with self.subTest(objection=objection):
                first = prepare_followup(LEAD, opted_out=None, objection=objection)
                second = prepare_followup(copy.deepcopy(LEAD), opted_out=None, objection=objection)
                self.assertEqual(first, second)
                self.assertEqual(first["status"], "pending_human_review")
                self.assertIs(first["sent"], False)
                self.assertIs(first["send_enabled"], False)
                self.assertIs(first["requires_human_approval"], True)
                self.assertIsNotNone(first["draft"])
                identities.add(first["idempotency_key"])
        self.assertEqual(len(identities), 4)

    def test_opt_out_recheck_removes_draft_for_every_objection(self):
        for objection in (None, "price", "timing", "competitor"):
            with self.subTest(objection=objection):
                prior = prepare_followup(LEAD, opted_out=False, objection=objection)
                original = copy.deepcopy(prior)
                reviewed = recheck_followup_for_review(
                    LEAD, prior, opted_out=True
                )
                self.assertEqual(prior, original)
                self.assertEqual(reviewed["review_status"], "suppressed")
                self.assertIs(reviewed["replay_changed"], True)
                self.assertIs(reviewed["outreach_enabled"], False)
                self.assertIs(reviewed["sent"], False)
                self.assertIs(reviewed["followup"]["draft"], None)
                self.assertIs(reviewed["followup"]["send_enabled"], False)
                self.assertEqual(reviewed["followup"]["status"], "suppressed")

    def test_offline_envelope_preserves_objection_provenance_without_send(self):
        for objection in ("price", "timing", "competitor"):
            with self.subTest(objection=objection):
                snapshot = build_offline_review_envelope(
                    LEAD, opted_out=None, objection=objection
                )
                followup = snapshot["followup"]
                self.assertEqual(followup["objection_category"], objection)
                self.assertEqual(
                    followup["objection_source"],
                    "unverified_caller_supplied_synthetic_enum",
                )
                self.assertIs(snapshot["uses_model"], False)
                self.assertIs(snapshot["external_calls"], False)
                self.assertIs(snapshot["outreach_enabled"], False)
                self.assertIs(followup["sent"], False)
                self.assertIs(followup["send_enabled"], False)
                self.assertIs(followup["requires_human_approval"], True)


if __name__ == "__main__":
    unittest.main()
