"""RRE-02 synthetic-only AI-lane contract and adversarial checks."""
import unittest
from unittest.mock import patch
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

    def test_idempotency_fingerprint_binds_validated_content(self):
        original = sample(ref="DEMO-KEY-1")
        baseline = qualify_lead(original)
        replay = qualify_lead(dict(original))
        self.assertEqual(baseline["idempotency_key"], replay["idempotency_key"])
        different_need = qualify_lead({**original, "need": "maintenance"})
        different_source = qualify_lead({**original, "source": "phone"})
        self.assertNotEqual(baseline["idempotency_key"], different_need["idempotency_key"])
        self.assertNotEqual(baseline["idempotency_key"], different_source["idempotency_key"])
        self.assertNotIn(original["external_ref"], baseline["idempotency_key"])
        self.assertNotEqual(prepare_followup(original)["idempotency_key"],
                            prepare_followup({**original, "need": "maintenance"})["idempotency_key"])

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

    def test_offline_provider_does_not_open_network_socket(self):
        # Verify behavior, not just the provider.external_calls metadata.
        with patch("socket.socket", side_effect=AssertionError("unexpected socket call")):
            provider = get_provider("offline")
            result = provider.qualify(sample())
            draft = provider.draft(sample())
        self.assertFalse(result["outreach_allowed"])
        self.assertFalse(draft["send_enabled"])
        self.assertFalse(draft["sent"])

    def test_all_hvac_templates_are_unsent_and_inputs_unchanged(self):
        provider = get_provider("offline")
        for need in NEEDS:
            with self.subTest(need=need):
                lead = sample(need=need)
                before = dict(lead)
                draft = provider.draft(lead, opted_out=False)
                self.assertEqual(lead, before)
                self.assertEqual(draft["status"], "pending_human_review")
                self.assertIn("internal synthetic preview only", draft["draft"].lower())
                self.assertFalse(draft["sent"])
                self.assertFalse(draft["send_enabled"])
                self.assertTrue(draft["requires_human_approval"])

    def test_reference_namespace_matches_local_intake(self):
        # The principal store only accepts explicit DEMO/QA synthetic tokens.
        for ref in ("DEMO-123", "QA-abc", "demo_token", "qa-XYZ_9"):
            with self.subTest(ref=ref):
                self.assertEqual(validate_lead(sample(ref=ref))["external_ref"], ref)
        for ref in ("JohnDoe", "Jane_Doe", "ref123", "DEMO-", "QA-", "DEMO-a@b", "QA-a/b", "DEMO-a b"):
            with self.subTest(ref=ref), self.assertRaises(ValueError):
                validate_lead(sample(ref=ref))

    def test_invalid_suppression_types_fail_closed_for_drafts(self):
        for flag in (0, 1, "", "false", [], {}):
            with self.subTest(flag=repr(flag)), self.assertRaises(ValueError):
                prepare_followup(sample(), opted_out=flag)

    def test_suppressed_qualified_input_has_no_draft_or_contact_permission(self):
        result = prepare_followup(sample("heating issue"), opted_out=True)
        self.assertIsNone(result["draft"])
        self.assertEqual(result["qualification"]["decision"], "suppressed")
        self.assertFalse(result["qualification"]["outreach_allowed"])
        self.assertFalse(result["sent"])
        self.assertFalse(result["send_enabled"])
        self.assertTrue(result["requires_human_approval"])

    def test_structured_hvac_objections_generate_distinct_unsent_drafts(self):
        # Approved mock categories, not real message inference.
        expected = {
            "price": "pricing questions",
            "timing": "timing concerns",
            "competitor": "comparing providers",
        }
        base = sample("estimate follow-up")
        default = prepare_followup(base)
        keys = {default["idempotency_key"]}
        for objection, phrase in expected.items():
            with self.subTest(objection=objection):
                d = prepare_followup(base, objection=objection)
                self.assertIn(phrase, d["draft"].lower())
                self.assertEqual(d["objection_source"], "synthetic_operator_enum")
                self.assertEqual(d["objection_category"], objection)
                self.assertFalse(d["sent"])
                self.assertFalse(d["send_enabled"])
                self.assertTrue(d["requires_human_approval"])
                self.assertNotIn(d["idempotency_key"], keys)
                keys.add(d["idempotency_key"])
        self.assertEqual(len(keys), 4)

    def test_objection_validation_and_opt_out_remain_fail_closed(self):
        for invalid in ("", "other", "please call 555-0000", 1, False, [], {}):
            with self.subTest(invalid=repr(invalid)), self.assertRaises(ValueError):
                prepare_followup(sample(), objection=invalid)
        for objection in ("price", "timing", "competitor"):
            with self.subTest(objection=objection):
                d = prepare_followup(sample(), opted_out=True, objection=objection)
                self.assertIsNone(d["draft"])
                self.assertFalse(d["sent"])
                self.assertFalse(d["send_enabled"])

    def test_offline_provider_accepts_bounded_objection_without_external_calls(self):
        provider = get_provider("offline")
        d = provider.draft(sample("repair"), objection="price")
        self.assertIn("pricing questions", d["draft"].lower())
        self.assertFalse(provider.uses_model)
        self.assertFalse(provider.external_calls)
        self.assertFalse(d["send_enabled"])

    def test_draft_is_not_false_appointment_or_price(self):
        d = prepare_followup(sample("estimate follow-up"))
        self.assertIn("No pricing or prior quote has been verified", d["draft"])
        self.assertNotIn("confirmed appointment", d["draft"].lower())

if __name__ == "__main__":
    unittest.main()
