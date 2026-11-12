"""Synthetic HVAC consent/objection cross-product regression.

Run: PYTHONPATH=products/revenue_recovery python -m unittest discover
     -s products/revenue_recovery/tests -p 'test_ai_consent_matrix.py' -v
No live consent, model inference, recipient lookup, or outbound operation.
"""
import copy
import unittest

from backend.qualification import qualify_lead, RULES
from backend.followups import prepare_followup, recheck_followup_for_review
from backend.ai_providers import build_offline_review_envelope


class SyntheticConsentMatrixTests(unittest.TestCase):
    def lead(self, need):
        return {"synthetic": True, "external_ref": "QA-MATRIX-001",
                "source": "website", "need": need, "status": "received"}

    def test_all_need_objection_suppression_combinations_fail_closed(self):
        for need in RULES:
            for objection in (None, "price", "timing", "competitor"):
                for opted_out in (None, False, True):
                    with self.subTest(need=need, objection=objection, opted_out=opted_out):
                        lead = self.lead(need)
                        result = build_offline_review_envelope(
                            lead, opted_out=opted_out, objection=objection)
                        qualification = result["qualification"]
                        draft = result["followup"]
                        self.assertEqual(result["generation_kind"],
                                         "deterministic_rules_not_ai_inference")
                        self.assertIs(result["uses_model"], False)
                        self.assertIs(result["external_calls"], False)
                        self.assertIs(result["outreach_enabled"], False)
                        self.assertIs(result["requires_human_approval"], True)
                        self.assertIs(qualification["outreach_allowed"], False)
                        self.assertIsNone(qualification["confidence"])
                        self.assertIs(draft["sent"], False)
                        self.assertIs(draft["send_enabled"], False)
                        self.assertIs(draft["requires_human_approval"], True)
                        self.assertEqual(draft["qualification"], qualification)
                        self.assertEqual(
                            draft, prepare_followup(lead, opted_out=opted_out,
                                                    objection=objection))
                        self.assertEqual(
                            qualification, qualify_lead(lead, opted_out=opted_out))
                        if opted_out is True:
                            self.assertEqual(draft["status"], "suppressed")
                            self.assertIsNone(draft["draft"])
                        else:
                            self.assertEqual(draft["status"], "pending_human_review")
                            self.assertIsInstance(draft["draft"], str)
                        self.assertEqual(
                            "suppression_status" in qualification["unknowns"],
                            opted_out is None)
                        if objection is not None:
                            self.assertEqual(draft["objection_category"], objection)
                            self.assertEqual(
                                draft["objection_source"],
                                "unverified_caller_supplied_synthetic_enum")

    def test_recheck_transitions_are_inert_and_do_not_mutate_prior(self):
        lead = self.lead("estimate follow-up")
        for objection in (None, "price", "timing", "competitor"):
            for old in (None, False, True):
                for new in (None, False, True):
                    with self.subTest(objection=objection, old=old, new=new):
                        prior = prepare_followup(
                            lead, opted_out=old, objection=objection)
                        snapshot = copy.deepcopy(prior)
                        checked = recheck_followup_for_review(
                            lead, prior, opted_out=new)
                        expected = prepare_followup(
                            lead, opted_out=new, objection=objection)
                        self.assertEqual(prior, snapshot)
                        self.assertEqual(checked["followup"], expected)
                        self.assertEqual(
                            checked["replay_changed"],
                            prior["idempotency_key"] != expected["idempotency_key"])
                        self.assertEqual(
                            checked["review_status"],
                            "suppressed" if new is True
                            else "fresh_human_review_required")
                        self.assertIs(checked["outreach_enabled"], False)
                        self.assertIs(checked["sent"], False)
                        self.assertIs(checked["requires_human_approval"], True)

    def test_deep_snapshot_detects_nested_qualification_mutation(self):
        prior = prepare_followup(self.lead("repair"), opted_out=None)
        shallow = dict(prior)
        deep = copy.deepcopy(prior)
        # Negative control: demonstrate why a shallow snapshot is insufficient.
        self.assertIn("unknowns", prior["qualification"])
        prior["qualification"]["unknowns"].append("synthetic_mutation_probe")
        self.assertEqual(prior, shallow)
        self.assertNotEqual(prior, deep)

    def test_replay_identity_distinguishes_consent_and_objections(self):
        lead = self.lead("repair")
        keys = set()
        for opted_out in (None, False, True):
            for objection in (None, "price", "timing", "competitor"):
                first = prepare_followup(
                    lead, opted_out=opted_out, objection=objection)
                second = prepare_followup(
                    dict(lead), opted_out=opted_out, objection=objection)
                self.assertEqual(first, second)
                self.assertNotIn(first["idempotency_key"], keys)
                keys.add(first["idempotency_key"])
        self.assertEqual(len(keys), 12)


if __name__ == "__main__":
    unittest.main()
