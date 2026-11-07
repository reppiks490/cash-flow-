"""Regression: replay identity must track the latest synthetic suppression fixture.

This does not establish genuine consent, a real opt-out audit, or permission
to contact anyone. Every draft remains an internal-only human-review preview.
"""
import unittest

from backend.qualification import qualify_lead
from backend.followups import prepare_followup


SYNTHETIC_LEAD = {
    "synthetic": True,
    "external_ref": "QA-SUPPRESSION-STATE-01",
    "source": "website",
    "need": "repair",
    "status": "received",
}


class QualificationPolicyIdentityTests(unittest.TestCase):
    def test_qualification_replay_identity_changes_on_mock_revocation(self):
        unknown = qualify_lead(SYNTHETIC_LEAD, opted_out=None)
        not_revoked = qualify_lead(SYNTHETIC_LEAD, opted_out=False)
        revoked = qualify_lead(SYNTHETIC_LEAD, opted_out=True)

        # A cached earlier answer must not shadow a later revocation fixture.
        self.assertEqual(len({
            unknown["idempotency_key"],
            not_revoked["idempotency_key"],
            revoked["idempotency_key"],
        }), 3)
        self.assertEqual(revoked["decision"], "suppressed")
        self.assertIn("suppression_status", unknown["unknowns"])
        self.assertFalse(not_revoked["outreach_allowed"])
        self.assertFalse(revoked["outreach_allowed"])
        self.assertEqual(
            revoked["idempotency_key"],
            qualify_lead(dict(SYNTHETIC_LEAD), opted_out=True)["idempotency_key"],
        )

    def test_rechecking_mock_revocation_never_reuses_a_sendable_draft(self):
        before = prepare_followup(SYNTHETIC_LEAD, opted_out=False)
        after = prepare_followup(SYNTHETIC_LEAD, opted_out=True)
        self.assertNotEqual(
            before["qualification"]["idempotency_key"],
            after["qualification"]["idempotency_key"],
        )
        self.assertNotEqual(before["idempotency_key"], after["idempotency_key"])
        self.assertIsNone(after["draft"])
        self.assertEqual(after["status"], "suppressed")
        self.assertIs(after["sent"], False)
        self.assertIs(after["send_enabled"], False)
        self.assertIs(after["requires_human_approval"], True)


if __name__ == "__main__":
    unittest.main()
