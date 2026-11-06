"""Offline bundle contract: qualification and draft are one coherent synthetic snapshot."""
import unittest
from backend.ai_providers import get_provider, preview_offline_bundle

LEAD = {"synthetic": True, "external_ref": "DEMO-BUNDLE-1",
        "source": "website", "need": "repair", "status": "received"}


class OfflineBundleTests(unittest.TestCase):
    def test_bundle_is_deterministic_and_never_authorizes_send(self):
        first = preview_offline_bundle(LEAD, objection="price")
        self.assertEqual(first, preview_offline_bundle(dict(LEAD), objection="price"))
        self.assertEqual(first["provider_id"], get_provider().provider_id)
        self.assertFalse(first["uses_model"])
        self.assertFalse(first["external_calls"])
        self.assertFalse(first["outreach_allowed"])
        self.assertFalse(first["sent"])
        self.assertFalse(first["send_enabled"])
        self.assertTrue(first["requires_human_approval"])
        self.assertEqual(first["qualification"], first["followup"]["qualification"])
        self.assertEqual(first["qualification"]["external_ref"], first["followup"]["external_ref"])
        self.assertEqual(first["followup"]["status"], "pending_human_review")

    def test_revocation_drops_draft_and_never_leaks_message(self):
        for objection in (None, "price", "timing", "competitor"):
            with self.subTest(objection=objection):
                item = preview_offline_bundle(LEAD, opted_out=True, objection=objection)
                self.assertIsNone(item["followup"]["draft"])
                self.assertEqual(item["followup"]["status"], "suppressed")
                self.assertFalse(item["outreach_allowed"])
                self.assertFalse(item["send_enabled"])

    def test_unknown_suppression_does_not_become_consent(self):
        item = preview_offline_bundle(LEAD)
        self.assertIn("suppression_status", item["qualification"]["unknowns"])
        self.assertFalse(item["outreach_allowed"])

    def test_invalid_inputs_fail_closed(self):
        for kwargs in ({"opted_out": "false"}, {"objection": "call me"},
                       {"objection": False}):
            with self.subTest(kwargs=kwargs), self.assertRaises(ValueError):
                preview_offline_bundle(LEAD, **kwargs)
        with self.assertRaises(ValueError):
            preview_offline_bundle({**LEAD, "email": "someone@example.invalid"})


if __name__ == "__main__":
    unittest.main()
