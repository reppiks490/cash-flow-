"""Offline provider provenance cannot be forged by a substituted adapter."""
import unittest
from unittest.mock import patch

from backend import ai_providers


LEAD = {
    "synthetic": True,
    "external_ref": "QA-PROVENANCE-1",
    "source": "website",
    "need": "repair",
    "status": "received",
}


class OfflineProviderProvenanceTests(unittest.TestCase):
    def test_builtin_provider_identity_is_attested(self):
        envelope = ai_providers.build_offline_review_envelope(LEAD)
        self.assertEqual(envelope["provider_id"], ai_providers.OfflineRulesProvider.provider_id)
        self.assertIs(envelope["uses_model"], False)
        self.assertIs(envelope["external_calls"], False)
        self.assertIs(envelope["requires_human_approval"], True)
        self.assertIs(envelope["followup"]["sent"], False)

    def test_forged_identity_rejected_before_provider_methods(self):
        class Forged:
            uses_model = False
            external_calls = False
            provider_id = "external-model-masquerading-as-offline"

            def qualify(self, *_args, **_kwargs):
                raise AssertionError("untrusted provider must not run")

            def draft(self, *_args, **_kwargs):
                raise AssertionError("untrusted provider must not run")

        with patch.object(ai_providers, "get_provider", return_value=Forged()):
            with self.assertRaisesRegex(ValueError, "Untrusted offline provider factory"):
                ai_providers.build_offline_review_envelope(LEAD)
            with self.assertRaisesRegex(ValueError, "Untrusted offline provider factory"):
                ai_providers.preview_offline_bundle(LEAD)

    def test_subclass_cannot_claim_trusted_provenance(self):
        class Substitute(ai_providers.OfflineRulesProvider):
            pass

        with patch.object(ai_providers, "get_provider", return_value=Substitute()):
            with self.assertRaisesRegex(ValueError, "Untrusted offline provider factory"):
                ai_providers.build_offline_review_envelope(LEAD)

    def test_modified_builtin_instance_identity_rejected(self):
        provider = ai_providers.OfflineRulesProvider()
        provider.provider_id = "forged-provider"
        with patch.object(ai_providers, "get_provider", return_value=provider):
            with self.assertRaisesRegex(ValueError, "Untrusted offline provider factory"):
                ai_providers.build_offline_review_envelope(LEAD)


if __name__ == "__main__":
    unittest.main()
