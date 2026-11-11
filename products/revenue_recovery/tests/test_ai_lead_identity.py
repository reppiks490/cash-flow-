"""Synthetic lead identity and provenance regressions (no external I/O)."""
import unittest

from backend.qualification import qualify_lead
from backend.followups import prepare_followup
from backend.ai_providers import build_offline_review_envelope


BASE = {
    "synthetic": True,
    "external_ref": "QA-IDENTITY-001",
    "source": "website",
    "need": "repair",
    "status": "received",
}


class LeadIdentityTests(unittest.TestCase):
    def test_each_validated_identity_dimension_changes_replay_key(self):
        variants = (
            BASE,
            {**BASE, "external_ref": "QA-IDENTITY-002"},
            {**BASE, "source": "demo"},
            {**BASE, "need": "maintenance"},
        )
        keys = [qualify_lead(row)["idempotency_key"] for row in variants]
        self.assertEqual(len(set(keys)), len(variants))
        for row in variants:
            result = qualify_lead(row)
            self.assertEqual(result["external_ref"], row["external_ref"])
            self.assertEqual(
                [(e["field"], e["value"], e["provenance"]) for e in result["evidence"]],
                [("need", row["need"], "synthetic_intake"),
                 ("source", row["source"], "synthetic_intake")],
            )
            self.assertIsNone(result["confidence"])
            self.assertFalse(result["outreach_allowed"])

    def test_source_and_need_changes_invalidate_cached_draft_identity(self):
        base_draft = prepare_followup(BASE, objection="price")
        for change in (
            {"source": "demo"},
            {"need": "maintenance"},
            {"external_ref": "QA-IDENTITY-002"},
        ):
            with self.subTest(change=change):
                changed = prepare_followup({**BASE, **change}, objection="price")
                self.assertNotEqual(base_draft["idempotency_key"], changed["idempotency_key"])
                self.assertFalse(changed["sent"])
                self.assertFalse(changed["send_enabled"])
                self.assertTrue(changed["requires_human_approval"])

    def test_provider_envelope_preserves_evidence_and_review_only_status(self):
        for source in ("website", "demo"):
            row = {**BASE, "source": source}
            envelope = build_offline_review_envelope(row, opted_out=None)
            self.assertEqual(envelope["qualification"], qualify_lead(row))
            self.assertEqual(envelope["followup"], prepare_followup(row))
            self.assertEqual(envelope["generation_kind"], "deterministic_rules_not_ai_inference")
            self.assertFalse(envelope["uses_model"])
            self.assertFalse(envelope["external_calls"])
            self.assertFalse(envelope["outreach_enabled"])


if __name__ == "__main__":
    unittest.main()
