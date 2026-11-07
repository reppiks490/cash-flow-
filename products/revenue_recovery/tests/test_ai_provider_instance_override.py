"""Synthetic-only regression: reject instance-level provider overrides before invocation."""
import unittest
from unittest.mock import patch

from backend import ai_providers

LEAD = {
    "synthetic": True,
    "external_ref": "QA-INSTANCE-OVERRIDE-1",
    "source": "website",
    "need": "repair",
    "status": "received",
}


class ProviderInstanceOverrideTests(unittest.TestCase):
    def test_overridden_qualify_never_invoked(self):
        provider = ai_providers.OfflineRulesProvider()
        called = []
        def untrusted(*args, **kwargs):
            called.append("qualify")
            raise AssertionError("untrusted method executed")
        provider.qualify = untrusted
        with patch.object(ai_providers, "get_provider", return_value=provider):
            for entry in (ai_providers.build_offline_review_envelope,
                          ai_providers.preview_offline_bundle):
                with self.subTest(entry=entry.__name__):
                    with self.assertRaisesRegex(ValueError, "instance overrides"):
                        entry(LEAD)
        self.assertEqual(called, [])

    def test_overridden_draft_never_invoked(self):
        provider = ai_providers.OfflineRulesProvider()
        called = []
        def untrusted(*args, **kwargs):
            called.append("draft")
            raise AssertionError("untrusted method executed")
        provider.draft = untrusted
        with patch.object(ai_providers, "get_provider", return_value=provider):
            with self.assertRaisesRegex(ValueError, "instance overrides"):
                ai_providers.build_offline_review_envelope(LEAD)
        self.assertEqual(called, [])

    def test_clean_provider_still_returns_inert_snapshot(self):
        envelope = ai_providers.build_offline_review_envelope(LEAD)
        self.assertIs(envelope["external_calls"], False)
        self.assertIs(envelope["followup"]["sent"], False)
        self.assertIs(envelope["followup"]["send_enabled"], False)


if __name__ == "__main__":
    unittest.main()
