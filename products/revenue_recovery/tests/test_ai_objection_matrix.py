"""Synthetic-only regression matrix for offline HVAC objection handling.

Run from products/revenue_recovery: python -m unittest discover -s tests
"""
import unittest

from backend.ai_providers import get_provider
from backend.followups import OBJECTION_TEMPLATES
from backend.qualification import RULES


class OfflineObjectionMatrixTests(unittest.TestCase):
    def setUp(self):
        self.provider = get_provider("offline")

    def lead(self, need):
        return {
            "synthetic": True,
            "external_ref": "QA-OBJECTION01",
            "source": "demo",
            "need": need,
            "status": "received",
        }

    def test_every_need_and_objection_is_internal_only(self):
        for need in RULES:
            for objection in OBJECTION_TEMPLATES:
                with self.subTest(need=need, objection=objection):
                    lead = self.lead(need)
                    first = self.provider.draft(lead, opted_out=None, objection=objection)
                    self.assertEqual(first, self.provider.draft(lead, opted_out=None, objection=objection))
                    self.assertEqual(first["status"], "pending_human_review")
                    self.assertTrue(first["requires_human_approval"])
                    self.assertFalse(first["sent"])
                    self.assertFalse(first["send_enabled"])
                    self.assertFalse(first["qualification"]["outreach_allowed"])
                    self.assertIn("contact_consent", first["qualification"]["unknowns"])
                    self.assertIn("suppression_status", first["qualification"]["unknowns"])
                    self.assertIn(OBJECTION_TEMPLATES[objection], first["draft"])
                    self.assertEqual(first["objection_source"], "unverified_caller_supplied_synthetic_enum")

    def test_revocation_suppresses_every_combination(self):
        for need in RULES:
            for objection in (None, *OBJECTION_TEMPLATES):
                with self.subTest(need=need, objection=objection):
                    result = self.provider.draft(self.lead(need), opted_out=True, objection=objection)
                    self.assertEqual(result["status"], "suppressed")
                    self.assertIsNone(result["draft"])
                    self.assertFalse(result["sent"])
                    self.assertFalse(result["send_enabled"])
                    self.assertFalse(result["qualification"]["outreach_allowed"])

    def test_objection_changes_draft_identity_but_not_qualification(self):
        lead = self.lead("repair")
        plain = self.provider.draft(lead, objection=None)
        price = self.provider.draft(lead, objection="price")
        timing = self.provider.draft(lead, objection="timing")
        self.assertEqual(plain["qualification"], price["qualification"])
        self.assertEqual(price["qualification"], timing["qualification"])
        self.assertEqual(len({plain["idempotency_key"], price["idempotency_key"], timing["idempotency_key"]}), 3)

    def test_invalid_objections_fail_before_draft(self):
        for objection in ("", "PRICE", "customer says call me", 0, False, [], {}):
            with self.subTest(objection=objection):
                with self.assertRaises(ValueError):
                    self.provider.draft(self.lead("repair"), objection=objection)

    def test_no_external_provider_fallback(self):
        for name in ("remote", "openai", "", None):
            with self.subTest(name=name):
                with self.assertRaises(ValueError):
                    get_provider(name)
        self.assertFalse(self.provider.uses_model)
        self.assertFalse(self.provider.external_calls)


if __name__ == "__main__":
    unittest.main()
