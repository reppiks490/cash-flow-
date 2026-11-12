"""Regression: a replaced offline provider factory must never execute.

Synthetic fixtures only. This is defense in depth, not hostile-runtime isolation.
"""
import unittest
from unittest.mock import patch

from backend import ai_providers


LEAD = {
    "synthetic": True,
    "external_ref": "QA-FACTORY-GUARD-001",
    "source": "website",
    "need": "repair",
    "status": "received",
}


class OfflineFactoryIntegrityTests(unittest.TestCase):
    def test_substituted_factory_is_rejected_before_invocation(self):
        invoked = []
        def replacement(name="offline"):
            invoked.append(name)
            raise AssertionError("substituted factory must not execute")
        with patch.object(ai_providers, "get_provider", replacement):
            with self.assertRaisesRegex(ValueError, "provider factory"):
                ai_providers.build_offline_review_envelope(LEAD)
        self.assertEqual(invoked, [])

    def test_bundle_rejects_factory_replacement_before_invocation(self):
        invoked = []
        def replacement(name="offline"):
            invoked.append(name)
            raise AssertionError("substituted factory must not execute")
        with patch.object(ai_providers, "get_provider", replacement):
            with self.assertRaisesRegex(ValueError, "provider factory"):
                ai_providers.preview_offline_bundle(LEAD)
        self.assertEqual(invoked, [])

    def test_clean_offline_factory_remains_inert(self):
        envelope = ai_providers.build_offline_review_envelope(LEAD)
        self.assertEqual(envelope["generation_kind"],
                         "deterministic_rules_not_ai_inference")
        self.assertIs(envelope["external_calls"], False)
        self.assertIs(envelope["uses_model"], False)
        self.assertIs(envelope["outreach_enabled"], False)
        self.assertIs(envelope["followup"]["sent"], False)
        self.assertIs(envelope["followup"]["send_enabled"], False)

    def test_unknown_provider_rejected_without_external_fallback(self):
        with self.assertRaises(ValueError):
            ai_providers.build_offline_review_envelope(
                LEAD, provider_name="remote"
            )


    def test_instance_method_override_rejected_by_original_factory(self):
        """Exercise the instance guard without replacing the trusted factory."""
        invoked = []
        def attach_override(instance):
            def unsafe_qualify(*args, **kwargs):
                invoked.append("qualify")
                raise AssertionError("override must not execute")
            instance.qualify = unsafe_qualify
        with patch.object(ai_providers.OfflineRulesProvider, "__init__", attach_override):
            with self.assertRaisesRegex(ValueError, "instance overrides"):
                ai_providers.build_offline_review_envelope(LEAD)
        self.assertEqual(invoked, [])

    def test_instance_draft_override_rejected_by_original_factory(self):
        """Both provider methods remain protected after the factory guard."""
        invoked = []
        def attach_override(instance):
            def unsafe_draft(*args, **kwargs):
                invoked.append("draft")
                raise AssertionError("override must not execute")
            instance.draft = unsafe_draft
        with patch.object(ai_providers.OfflineRulesProvider, "__init__", attach_override):
            with self.assertRaisesRegex(ValueError, "instance overrides"):
                ai_providers.preview_offline_bundle(LEAD)
        self.assertEqual(invoked, [])

if __name__ == "__main__":
    unittest.main()
