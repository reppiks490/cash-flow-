"""Negative contract tests for the synthetic HVAC qualification/draft boundary.

Run with: python -m unittest discover -s products/revenue_recovery/tests -p 'test_ai_negative_contract.py'
No network, recipients, credentials, or customer data are used.
"""
import copy
import pathlib
import sys
import unittest

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))
from backend.qualification import qualify_lead
from backend.followups import prepare_followup
from backend.ai_providers import build_offline_review_envelope

LEAD = {
    "synthetic": True, "external_ref": "DEMO-001",
    "source": "web", "need": "repair", "status": "received",
}


class NegativeContractTests(unittest.TestCase):
    def test_reject_extra_contact_fields_before_qualification_or_draft(self):
        for field, value in (
            ("email", "not-a-real-recipient@example.invalid"),
            ("phone", "0000000000"),
            ("name", "SYNTHETIC"),
            ("notes", "synthetic free text"),
        ):
            with self.subTest(field=field):
                lead = {**LEAD, field: value}
                for operation in (
                    lambda: qualify_lead(lead),
                    lambda: prepare_followup(lead),
                    lambda: build_offline_review_envelope(lead),
                ):
                    with self.assertRaises(ValueError):
                        operation()

    def test_reject_ambiguous_opt_out_types_everywhere(self):
        for flag in (0, 1, "", "false", "true", [], {}):
            with self.subTest(flag=repr(flag)):
                for operation in (
                    lambda: qualify_lead(LEAD, opted_out=flag),
                    lambda: prepare_followup(LEAD, opted_out=flag),
                    lambda: build_offline_review_envelope(LEAD, opted_out=flag),
                ):
                    with self.assertRaises(ValueError):
                        operation()

    def test_unknown_provider_rejected_without_downgrading_to_mock(self):
        for name in ("", "local", "openai", "OFFLINE", None, 0):
            with self.subTest(name=repr(name)):
                with self.assertRaises(ValueError):
                    build_offline_review_envelope(LEAD, provider_name=name)

    def test_input_unchanged_and_no_send_for_all_suppression_states(self):
        for flag in (None, False, True):
            with self.subTest(flag=flag):
                lead = copy.deepcopy(LEAD)
                original = copy.deepcopy(lead)
                envelope = build_offline_review_envelope(lead, opted_out=flag)
                self.assertEqual(lead, original)
                self.assertIs(envelope["synthetic"], True)
                self.assertIs(envelope["external_calls"], False)
                self.assertIs(envelope["uses_model"], False)
                self.assertIs(envelope["outreach_enabled"], False)
                self.assertIs(envelope["followup"]["send_enabled"], False)
                self.assertIs(envelope["followup"]["sent"], False)
                self.assertIs(envelope["followup"]["requires_human_approval"], True)
                self.assertIsNone(envelope["followup"]["draft"] if flag is True else None)


if __name__ == "__main__":
    unittest.main()
