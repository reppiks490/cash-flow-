"""Synthetic-only regression matrix for the offline review envelope.

Run from products/revenue_recovery with:
    python -m unittest backend.test_offline_envelope_matrix -v
No network, vendor SDK, customer records, or outreach.
"""
import unittest

from backend.ai_providers import build_offline_review_envelope, preview_offline_bundle


class OfflineEnvelopeMatrixTests(unittest.TestCase):
    def lead(self, need, ref):
        return {
            "synthetic": True, "external_ref": ref, "source": "website",
            "need": need, "status": "received",
        }

    def test_all_hvac_needs_are_deterministic_and_never_send(self):
        needs = (
            "AC not cooling", "heating issue", "repair",
            "estimate follow-up", "AC maintenance", "maintenance",
        )
        for index, need in enumerate(needs):
            with self.subTest(need=need):
                lead = self.lead(need, f"QA-MATRIX-{index}")
                first = build_offline_review_envelope(lead)
                second = build_offline_review_envelope(dict(lead))
                self.assertEqual(first, second)
                self.assertTrue(first["synthetic"])
                self.assertFalse(first["uses_model"])
                self.assertFalse(first["external_calls"])
                self.assertFalse(first["outreach_enabled"])
                self.assertTrue(first["requires_human_approval"])
                q, draft = first["qualification"], first["followup"]
                self.assertIsNone(q["confidence"])
                self.assertIn("contact_consent", q["unknowns"])
                self.assertIn("suppression_status", q["unknowns"])
                self.assertFalse(q["outreach_allowed"])
                self.assertEqual(draft["status"], "pending_human_review")
                self.assertFalse(draft["sent"])
                self.assertFalse(draft["send_enabled"])
                self.assertTrue(draft["requires_human_approval"])
                self.assertEqual(draft["qualification"], q)
                self.assertIn("internal synthetic preview", draft["draft"])

    def test_suppression_dominates_each_objection(self):
        lead = self.lead("repair", "QA-MATRIX-OPT")
        for objection in (None, "price", "timing", "competitor"):
            with self.subTest(objection=objection):
                result = build_offline_review_envelope(
                    lead, opted_out=True, objection=objection
                )
                self.assertEqual(result["qualification"]["decision"], "suppressed")
                self.assertEqual(result["followup"]["status"], "suppressed")
                self.assertIsNone(result["followup"]["draft"])
                self.assertFalse(result["followup"]["send_enabled"])
                self.assertFalse(result["followup"]["sent"])

    def test_bundle_preserves_same_inert_result(self):
        lead = self.lead("estimate follow-up", "QA-MATRIX-BUNDLE")
        envelope = build_offline_review_envelope(
            lead, opted_out=False, objection="price"
        )
        bundle = preview_offline_bundle(
            lead, opted_out=False, objection="price"
        )
        self.assertEqual(bundle["qualification"], envelope["qualification"])
        self.assertEqual(bundle["followup"], envelope["followup"])
        self.assertFalse(bundle["outreach_allowed"])
        self.assertFalse(bundle["send_enabled"])
        self.assertFalse(bundle["sent"])

    def test_unsupported_provider_fails_closed(self):
        with self.assertRaises(ValueError):
            build_offline_review_envelope(
                self.lead("repair", "QA-MATRIX-PROVIDER"),
                provider_name="external",
            )


if __name__ == "__main__":
    unittest.main()
