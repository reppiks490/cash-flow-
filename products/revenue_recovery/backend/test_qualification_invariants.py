"""Synthetic-only invariants for deterministic HVAC qualification and draft review."""
import unittest

from backend.qualification import qualify_lead
from backend.followups import prepare_followup, recheck_followup_for_review

LEAD = {
    "synthetic": True,
    "external_ref": "QA-INVARIANT-001",
    "source": "website",
    "need": "repair",
    "status": "received",
}


class QualificationInvariantTests(unittest.TestCase):
    def test_replay_stable_and_input_unchanged(self):
        original = dict(LEAD)
        first = qualify_lead(LEAD)
        self.assertEqual(first, qualify_lead(dict(LEAD)))
        self.assertEqual(LEAD, original)
        self.assertIsNone(first["confidence"])
        self.assertEqual(first["confidence_kind"], "not_model_calibrated")
        self.assertIn("suppression_status", first["unknowns"])
        self.assertFalse(first["outreach_allowed"])

    def test_suppression_changes_replay_identity_not_evidence(self):
        unknown = qualify_lead(LEAD)
        clear = qualify_lead(LEAD, opted_out=False)
        suppressed = qualify_lead(LEAD, opted_out=True)
        self.assertEqual(len({unknown["idempotency_key"], clear["idempotency_key"],
                              suppressed["idempotency_key"]}), 3)
        self.assertEqual(unknown["evidence"], clear["evidence"])
        self.assertEqual(clear["evidence"], suppressed["evidence"])
        self.assertEqual(suppressed["decision"], "suppressed")
        self.assertFalse(suppressed["outreach_allowed"])

    def test_objection_changes_draft_identity_without_sending(self):
        standard = prepare_followup(LEAD)
        price = prepare_followup(LEAD, objection="price")
        timing = prepare_followup(LEAD, objection="timing")
        keys = {item["idempotency_key"] for item in (standard, price, timing)}
        self.assertEqual(len(keys), 3)
        for item in (standard, price, timing):
            self.assertFalse(item["sent"])
            self.assertFalse(item["send_enabled"])
            self.assertTrue(item["requires_human_approval"])
            self.assertEqual(item["status"], "pending_human_review")

    def test_recheck_suppression_never_reuses_old_draft(self):
        prior = prepare_followup(LEAD, opted_out=False, objection="price")
        refreshed = recheck_followup_for_review(LEAD, prior, opted_out=True)
        self.assertEqual(refreshed["review_status"], "suppressed")
        self.assertTrue(refreshed["replay_changed"])
        self.assertIsNone(refreshed["followup"]["draft"])
        self.assertFalse(refreshed["sent"])
        self.assertFalse(refreshed["outreach_enabled"])

    def test_reject_nonboolean_suppression(self):
        for invalid in (0, 1, "false", [], {}):
            with self.subTest(value=repr(invalid)):
                with self.assertRaises(ValueError):
                    prepare_followup(LEAD, opted_out=invalid)


    def test_recheck_rejects_tampered_cached_snapshot(self):
        prior = prepare_followup(LEAD, opted_out=False, objection="price")
        for mutation in ("draft", "sent", "qualification", "objection_category"):
            with self.subTest(mutation=mutation):
                changed = dict(prior)
                if mutation == "draft":
                    changed["draft"] = "Forged customer-facing content"
                elif mutation == "sent":
                    changed["sent"] = True
                elif mutation == "qualification":
                    changed["qualification"] = dict(prior["qualification"], outreach_allowed=True)
                else:
                    changed["objection_category"] = "competitor"
                with self.assertRaises(ValueError):
                    recheck_followup_for_review(LEAD, changed, opted_out=False)

    def test_recheck_rejects_different_lead_reference(self):
        prior = prepare_followup(LEAD, opted_out=False)
        other = dict(LEAD, external_ref="QA-INVARIANT-002")
        with self.assertRaises(ValueError):
            recheck_followup_for_review(other, prior, opted_out=False)

    def test_unapproved_objection_categories_fail_closed(self):
        for invalid in ("discount", "safety", "", 0, True):
            with self.subTest(objection=repr(invalid)):
                with self.assertRaises(ValueError):
                    prepare_followup(LEAD, objection=invalid)


    def test_source_and_need_changes_invalidate_replay_identity(self):
        baseline = qualify_lead(LEAD)
        changed_source = qualify_lead(dict(LEAD, source="phone"))
        changed_need = qualify_lead(dict(LEAD, need="maintenance"))
        self.assertEqual(len({baseline["idempotency_key"],
                              changed_source["idempotency_key"],
                              changed_need["idempotency_key"]}), 3)
        self.assertNotEqual(baseline["evidence"], changed_source["evidence"])
        self.assertNotEqual(baseline["category"], changed_need["category"])
        self.assertFalse(changed_source["outreach_allowed"])
        self.assertFalse(changed_need["outreach_allowed"])

    def test_suppressed_objections_never_generate_draft(self):
        for objection in (None, "price", "timing", "competitor"):
            with self.subTest(objection=objection):
                result = prepare_followup(LEAD, opted_out=True, objection=objection)
                self.assertEqual(result["status"], "suppressed")
                self.assertIsNone(result["draft"])
                self.assertFalse(result["sent"])
                self.assertFalse(result["send_enabled"])
                self.assertTrue(result["requires_human_approval"])


    def test_recheck_unknown_to_clear_still_requires_fresh_review(self):
        prior = prepare_followup(LEAD, opted_out=None, objection="timing")
        refreshed = recheck_followup_for_review(LEAD, prior, opted_out=False)
        self.assertEqual(refreshed["review_status"], "fresh_human_review_required")
        self.assertTrue(refreshed["replay_changed"])
        self.assertFalse(refreshed["outreach_enabled"])
        self.assertFalse(refreshed["followup"]["send_enabled"])
        self.assertTrue(refreshed["followup"]["requires_human_approval"])
        self.assertNotIn("suppression_status", refreshed["followup"]["qualification"]["unknowns"])
        self.assertIn("contact_consent", refreshed["followup"]["qualification"]["unknowns"])

    def test_recheck_rejects_tampered_nested_evidence_and_unknowns(self):
        prior = prepare_followup(LEAD, opted_out=None)
        for field in ("evidence", "unknowns"):
            with self.subTest(field=field):
                tampered = dict(prior)
                qualification = dict(prior["qualification"])
                qualification[field] = list(qualification[field])
                if field == "evidence":
                    qualification[field][0] = dict(qualification[field][0], provenance="verified_customer")
                else:
                    qualification[field].remove("contact_consent")
                tampered["qualification"] = qualification
                with self.assertRaises(ValueError):
                    recheck_followup_for_review(LEAD, tampered, opted_out=False)

if __name__ == "__main__":
    unittest.main()
