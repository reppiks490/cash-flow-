"""Versioned, offline-only review adapter contract over synthetic HVAC cases."""
import unittest
from unittest.mock import patch

from backend import ai_providers
from backend.contracts import SOURCES, NEEDS


def synthetic_lead(source="website", need="repair"):
    return {
        "synthetic": True,
        "external_ref": "QA-OFFLINE-ENVELOPE-1",
        "source": source,
        "need": need,
        "status": "received",
    }


class OfflineReviewEnvelopeTests(unittest.TestCase):
    def _build(self, lead=None, **kwargs):
        builder = getattr(ai_providers, "build_offline_review_envelope", None)
        self.assertIsNotNone(builder, "Versioned offline review adapter is missing")
        return builder(synthetic_lead() if lead is None else lead, **kwargs)

    def test_schema_and_no_send_properties_across_all_bounded_fixtures(self):
        for source in SOURCES:
            for need in NEEDS:
                for opted_out in (None, False, True):
                    for objection in (None, "price", "timing", "competitor"):
                        with self.subTest(source=source, need=need,
                                          opted_out=opted_out, objection=objection):
                            row = synthetic_lead(source, need)
                            with patch("socket.socket", side_effect=AssertionError("network attempted")):
                                result = self._build(row, opted_out=opted_out, objection=objection)
                            self.assertEqual(result["schema_version"], "rre-offline-review-v1")
                            self.assertIs(result["synthetic"], True)
                            self.assertEqual(result["provider_id"], "offline-deterministic-rules-v1")
                            self.assertEqual(result["generation_kind"], "deterministic_rules_not_ai_inference")
                            self.assertIs(result["uses_model"], False)
                            self.assertIs(result["external_calls"], False)
                            self.assertIs(result["outreach_enabled"], False)
                            self.assertIs(result["requires_human_approval"], True)
                            q, draft = result["qualification"], result["followup"]
                            self.assertEqual(draft["qualification"], q)
                            self.assertEqual(q["external_ref"], row["external_ref"])
                            self.assertIsNone(q["confidence"])
                            self.assertIs(q["outreach_allowed"], False)
                            self.assertIs(draft["sent"], False)
                            self.assertIs(draft["send_enabled"], False)
                            self.assertIs(draft["requires_human_approval"], True)
                            self.assertEqual(row, synthetic_lead(source, need))
                            if opted_out is True:
                                self.assertEqual(draft["status"], "suppressed")
                                self.assertIsNone(draft["draft"])
                            else:
                                self.assertEqual(draft["status"], "pending_human_review")
                                self.assertIsInstance(draft["draft"], str)

    def test_repeatable_replay_and_mock_revocation_are_distinct(self):
        lead = synthetic_lead()
        early = self._build(lead, opted_out=False, objection="price")
        replay = self._build(dict(lead), opted_out=False, objection="price")
        revoked = self._build(lead, opted_out=True, objection="price")
        self.assertEqual(early, replay)
        self.assertNotEqual(early["followup"]["idempotency_key"],
                            revoked["followup"]["idempotency_key"])
        self.assertIsNone(revoked["followup"]["draft"])

    def test_rejects_remote_provider_unbounded_objections_and_live_data(self):
        for kwargs in ({"provider_name": "remote"}, {"provider_name": None},
                       {"objection": "email me"}, {"objection": 1}):
            with self.subTest(kwargs=kwargs), self.assertRaises(ValueError):
                self._build(**kwargs)
        for unsafe in ({"synthetic": False}, {"email": "not-a-real-address@example.invalid"}):
            with self.subTest(unsafe=unsafe), self.assertRaises(ValueError):
                self._build({**synthetic_lead(), **unsafe})



    def test_rejects_forged_provider_outputs_despite_safe_declared_flags(self):
        real_provider = ai_providers.get_provider("offline")

        class ForgedOfflineProvider:
            provider_id = "offline-deterministic-rules-v1"
            uses_model = False
            external_calls = False

            def __init__(self, defect):
                self.defect = defect

            def qualify(self, lead, *, opted_out=None):
                result = real_provider.qualify(lead, opted_out=opted_out)
                if self.defect == "confidence":
                    result["confidence"] = 0.99  # uncalibrated model claim
                if self.defect == "reference":
                    result["external_ref"] = "QA-OTHER-LEAD"
                return result

            def draft(self, lead, *, opted_out=None, objection=None):
                result = real_provider.draft(
                    lead, opted_out=opted_out, objection=objection
                )
                if self.defect == "no_draft":
                    result["draft"] = None  # falsely marked pending review
                if self.defect == "confidence":
                    result["qualification"]["confidence"] = 0.99
                if self.defect == "reference":
                    result["qualification"]["external_ref"] = "QA-OTHER-LEAD"
                    result["external_ref"] = "QA-OTHER-LEAD"
                return result

        for defect in ("no_draft", "confidence", "reference"):
            with self.subTest(defect=defect):
                with patch.object(ai_providers, "get_provider",
                                  return_value=ForgedOfflineProvider(defect)):
                    with self.assertRaises(ValueError):
                        self._build()

if __name__ == "__main__":
    unittest.main()
