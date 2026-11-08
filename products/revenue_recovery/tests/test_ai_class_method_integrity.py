"""Synthetic-only defense-in-depth tests for class-level provider mutation."""
import unittest
from unittest.mock import patch
from backend import ai_providers

LEAD = {"synthetic": True, "external_ref": "QA-CLASS-GUARD-001",
        "source": "website", "need": "repair", "status": "received"}


class ClassMethodIntegrityTests(unittest.TestCase):
    def test_qualification_method_replacement_never_executes(self):
        invoked = []
        def hostile(self, lead, *, opted_out=None):
            invoked.append(True)
            raise AssertionError("must not run")
        with patch.object(ai_providers.OfflineRulesProvider, "qualify", hostile):
            with self.assertRaisesRegex(ValueError, "class methods"):
                ai_providers.build_offline_review_envelope(LEAD)
        self.assertEqual(invoked, [])

    def test_draft_method_replacement_never_executes(self):
        invoked = []
        def hostile(self, lead, *, opted_out=None, objection=None):
            invoked.append(True)
            raise AssertionError("must not run")
        with patch.object(ai_providers.OfflineRulesProvider, "draft", hostile):
            with self.assertRaisesRegex(ValueError, "class methods"):
                ai_providers.preview_offline_bundle(LEAD)
        self.assertEqual(invoked, [])

    def test_class_metadata_mutation_rejected(self):
        for name, value in (("provider_id", "forged"),
                            ("uses_model", True), ("external_calls", True)):
            with self.subTest(name=name):
                with patch.object(ai_providers.OfflineRulesProvider, name, value):
                    with self.assertRaises(ValueError):
                        ai_providers.build_offline_review_envelope(LEAD)

    def test_forged_metadata_rejected_before_provider_factory(self):
        for name, value in (("provider_id", "forged"),
                            ("uses_model", True), ("external_calls", True)):
            with self.subTest(name=name):
                calls = []
                def factory(_name="offline"):
                    calls.append(_name)
                    raise AssertionError("factory must not execute")
                with patch.object(ai_providers.OfflineRulesProvider, name, value):
                    with patch.object(ai_providers, "get_provider", factory):
                        with self.assertRaisesRegex(ValueError, "class metadata"):
                            ai_providers.build_offline_review_envelope(LEAD)
                self.assertEqual(calls, [])

    def test_clean_offline_provider_remains_inert(self):
        result = ai_providers.preview_offline_bundle(LEAD)
        self.assertIs(result["synthetic"], True)
        self.assertIs(result["external_calls"], False)
        self.assertIs(result["send_enabled"], False)
        self.assertIs(result["sent"], False)
        self.assertIs(result["requires_human_approval"], True)
