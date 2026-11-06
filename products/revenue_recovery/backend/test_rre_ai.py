"""Run: python -m unittest discover -s products/revenue_recovery/backend -p 'test_rre_ai.py'"""
import unittest
from qualification import qualify
from followups import draft_followup
from ai_providers import provider_from_config

class QualificationTests(unittest.TestCase):
    def lead(self, **kw):
        return dict({"tenant_id":"demo-tenant","source":"synthetic-form","external_id":"sample-1","message":"Furnace stopped; need repair quote","synthetic":True}, **kw)
    def test_qualified_with_provenance(self):
        result = qualify(self.lead())
        self.assertEqual(result["status"], "qualified")
        self.assertTrue(result["evidence"])
        self.assertEqual(result["evidence"][0]["source"], "lead.message")
    def test_idempotent_and_tenant_scoped(self):
        a = qualify(self.lead())
        self.assertEqual(a["idempotency_key"], qualify(self.lead())["idempotency_key"])
        b = self.lead()
        b["tenant_id"] = "other-tenant"
        self.assertNotEqual(a["idempotency_key"], qualify(b)["idempotency_key"])
    def test_opt_out_blocks_draft(self):
        lead = self.lead()
        lead["message"] = "No heat, stop contacting me"
        assessment = qualify(lead)
        self.assertEqual(assessment["status"], "suppressed")
        self.assertEqual(draft_followup(assessment, approved_contact=True)["status"], "blocked")
    def test_unknown_does_not_invent_confidence(self):
        lead = self.lead()
        lead["message"] = "Hello"
        result = qualify(lead)
        self.assertEqual(result["status"], "needs_review")
        self.assertEqual(result["confidence"], "unknown")
    def test_draft_never_sends(self):
        a = qualify(self.lead())
        self.assertEqual(draft_followup(a)["reason"], "contact_permission_unverified")
        d = draft_followup(a, approved_contact=True)
        self.assertEqual(d["status"], "pending_human_review")
        self.assertFalse(d["auto_send"])
        self.assertEqual(d["draft_id"], draft_followup(a, approved_contact=True)["draft_id"])
    def test_mock_only(self):
        self.assertTrue(provider_from_config().generate("test").simulated)
        with self.assertRaises(ValueError):
            provider_from_config("remote")
    def test_missing_provenance_rejected(self):
        with self.assertRaises(ValueError):
            qualify({"message":"repair"})

    def test_no_substring_false_positive_for_service(self):
        lead = self.lead()
        lead["message"] = "We are researching priceless options"
        result = qualify(lead)
        self.assertEqual(result["status"], "needs_review")
        self.assertEqual(result["score"], 0)
        self.assertEqual(result["objections"], [])

    def test_complete_opt_out_phrase_still_suppresses(self):
        lead = self.lead()
        lead["message"] = "Please REMOVE ME from your list; furnace stopped"
        result = qualify(lead)
        self.assertEqual(result["status"], "suppressed")
        self.assertTrue(result["opt_out"])

    def test_word_boundaries_preserve_normal_hvac_matches(self):
        lead = self.lead()
        lead["message"] = "Need an AC repair estimate; price is a concern"
        result = qualify(lead)
        self.assertEqual(result["status"], "qualified")
        self.assertIn("price", result["objections"])

if __name__ == "__main__":
    unittest.main()
