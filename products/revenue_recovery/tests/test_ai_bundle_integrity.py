"""Cross-adapter integrity regression: offline bundle must reject forged providers."""
import unittest
from unittest.mock import patch

from backend import ai_providers

LEAD = {
    "synthetic": True, "external_ref": "QA-BUNDLE-INTEGRITY-1",
    "source": "website", "need": "repair", "status": "received",
}


class BundleIntegrityTests(unittest.TestCase):
    def test_bundle_and_envelope_agree_on_safe_output(self):
        for flag in (None, False, True):
            for objection in (None, "price", "timing", "competitor"):
                with self.subTest(flag=flag, objection=objection):
                    bundle = ai_providers.preview_offline_bundle(
                        LEAD, opted_out=flag, objection=objection
                    )
                    envelope = ai_providers.build_offline_review_envelope(
                        LEAD, opted_out=flag, objection=objection
                    )
                    self.assertEqual(bundle["qualification"], envelope["qualification"])
                    self.assertEqual(bundle["followup"], envelope["followup"])
                    self.assertIs(bundle["send_enabled"], False)
                    self.assertIs(bundle["sent"], False)
                    self.assertIs(bundle["external_calls"], False)

    def test_bundle_rejects_forged_offline_provider(self):
        real = ai_providers.OfflineRulesProvider()

        class Forged:
            provider_id = "offline-deterministic-rules-v1"
            uses_model = False
            external_calls = False

            def __init__(self, defect):
                self.defect = defect

            def qualify(self, lead, *, opted_out=None):
                result = real.qualify(lead, opted_out=opted_out)
                if self.defect == "confidence":
                    result["confidence"] = 0.99
                return result

            def draft(self, lead, *, opted_out=None, objection=None):
                result = real.draft(lead, opted_out=opted_out, objection=objection)
                if self.defect == "content":
                    result["draft"] = "Appointment confirmed."
                elif self.defect == "extra":
                    result["recipient_email"] = "fake@example.invalid"
                elif self.defect == "confidence":
                    result["qualification"]["confidence"] = 0.99
                return result

        for defect in ("confidence", "content", "extra"):
            with self.subTest(defect=defect):
                with patch.object(ai_providers, "get_provider", return_value=Forged(defect)):
                    with self.assertRaises(ValueError):
                        ai_providers.preview_offline_bundle(LEAD, opted_out=False)

    def test_bundle_rejects_unsafe_provider_selection_and_input(self):
        with self.assertRaises(ValueError):
            ai_providers.preview_offline_bundle({**LEAD, "synthetic": False})
        with self.assertRaises(ValueError):
            ai_providers.preview_offline_bundle(LEAD, objection="custom free text")


if __name__ == "__main__":
    unittest.main()
