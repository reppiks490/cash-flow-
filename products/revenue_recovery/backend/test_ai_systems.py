"""RRE-02 synthetic-only AI-lane contract and adversarial checks."""
import unittest
from backend.qualification import qualify_lead, validate_lead, NEEDS
from backend.followups import prepare_followup
from backend.ai_providers import get_provider

def sample(need="AC not cooling", ref="DEMO-123"):
    return {"synthetic": True, "external_ref": ref, "source": "website", "need": need, "status": "received"}

class AISystemsTests(unittest.TestCase):
    def test_each_need_explainable(self):
        for need in NEEDS:
            with self.subTest(need=need):
                q = qualify_lead(sample(need))
                self.assertEqual(q["decision"], "qualified_for_human_review")
                self.assertEqual(q["evidence"][0]["value"], need)
                self.assertIsNone(q["confidence"])
                self.assertFalse(q["outreach_allowed"])

    def test_deterministic_idempotency(self):
        self.assertEqual(qualify_lead(sample()), qualify_lead(sample()))
        self.assertEqual(prepare_followup(sample()), prepare_followup(sample()))
        self.assertEqual(prepare_followup(sample())["status"], "pending_human_review")

    def test_opt_out_suppresses(self):
        d = prepare_followup(sample(), opted_out=True)
        self.assertEqual(d["status"], "suppressed")
        self.assertIsNone(d["draft"])
        self.assertFalse(d["send_enabled"])

    def test_unknown_consent_never_allows_send(self):
        d = prepare_followup(sample())
        self.assertIn("suppression_status", d["qualification"]["unknowns"])
        self.assertFalse(d["sent"])
        self.assertFalse(d["send_enabled"])
        self.assertTrue(d["requires_human_approval"])

    def test_rejects_pii_fields_and_arbitrary_strings(self):
        for change in ({"email": "someone@example.invalid"}, {"synthetic": False},
                       {"source": "someone@example.invalid"}, {"need": "please call 555-0000"},
                       {"external_ref": "5551234567"}, {"status": "paid"}):
            with self.subTest(change=change), self.assertRaises(ValueError):
                validate_lead({**sample(), **change})

    def test_no_unknown_provider_or_network(self):
        p = get_provider()
        self.assertFalse(p.external_calls)
        self.assertFalse(p.uses_model)
        self.assertEqual(p.qualify(sample()), qualify_lead(sample()))
        with self.assertRaises(ValueError):
            get_provider("remote")

    def test_invalid_opt_out_type_rejected(self):
        with self.assertRaises(ValueError):
            qualify_lead(sample(), opted_out="false")

    def test_draft_is_not_false_appointment_or_price(self):
        d = prepare_followup(sample("estimate follow-up"))
        self.assertIn("No pricing or prior quote has been verified", d["draft"])
        self.assertNotIn("confirmed appointment", d["draft"].lower())

if __name__ == "__main__":
    unittest.main()
