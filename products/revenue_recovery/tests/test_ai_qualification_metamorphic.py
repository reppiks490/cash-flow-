"""Synthetic-only qualification metamorphic regression checks (RRE-02)."""
import unittest

from backend.qualification import qualify_lead
from backend.followups import prepare_followup


def fixture(ref="DEMO-001", source="web", need="repair"):
    return {"synthetic": True, "external_ref": ref, "source": source,
            "need": need, "status": "received"}


class QualificationMetamorphicTests(unittest.TestCase):
    def test_identical_inputs_replay_exactly(self):
        lead = fixture()
        self.assertEqual(qualify_lead(lead), qualify_lead(dict(lead)))
        self.assertEqual(prepare_followup(lead), prepare_followup(dict(lead)))

    def test_suppression_is_fail_closed(self):
        lead = fixture()
        for flag in (None, False, True):
            with self.subTest(flag=flag):
                q = qualify_lead(lead, opted_out=flag)
                draft = prepare_followup(lead, opted_out=flag)
                self.assertIs(q["outreach_allowed"], False)
                self.assertIs(draft["send_enabled"], False)
                self.assertIs(draft["sent"], False)
                self.assertIs(draft["requires_human_approval"], True)
                self.assertEqual(draft["qualification"], q)
                if flag is True:
                    self.assertIsNone(draft["draft"])
                    self.assertEqual(draft["status"], "suppressed")
                else:
                    self.assertEqual(draft["status"], "pending_human_review")

    def test_opt_out_transitions_change_replay_identity(self):
        lead = fixture()
        keys = [qualify_lead(lead, opted_out=flag)["idempotency_key"]
                for flag in (None, False, True)]
        self.assertEqual(len(set(keys)), 3)

    def test_ref_and_source_changes_change_replay_identity(self):
        original = qualify_lead(fixture())["idempotency_key"]
        for variant in (fixture(ref="DEMO-002"), fixture(source="phone")):
            with self.subTest(variant=variant):
                self.assertNotEqual(original, qualify_lead(variant)["idempotency_key"])

    def test_evidence_is_explicitly_synthetic_not_model_confidence(self):
        result = qualify_lead(fixture())
        self.assertIs(result["synthetic"], True)
        self.assertIsNone(result["confidence"])
        self.assertEqual(result["confidence_kind"], "not_model_calibrated")
        self.assertTrue(result["evidence"])
        self.assertTrue(all(item["provenance"] == "synthetic_intake"
                            for item in result["evidence"]))
        self.assertIn("contact_consent", result["unknowns"])
        self.assertIn("suppression_status", result["unknowns"])

    def test_malformed_suppression_flags_rejected(self):
        for flag in (0, 1, "", "false", [], {}):
            with self.subTest(flag=flag):
                with self.assertRaises(ValueError):
                    qualify_lead(fixture(), opted_out=flag)
                with self.assertRaises(ValueError):
                    prepare_followup(fixture(), opted_out=flag)


if __name__ == "__main__":
    unittest.main()
