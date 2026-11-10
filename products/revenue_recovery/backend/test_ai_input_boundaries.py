"""Synthetic-only negative input boundaries for the RRE-02 pure AI lane.

These tests exercise deterministic local functions only; they do not assert
production privacy, verified consent, or external model safety.
"""
import unittest

from backend.qualification import qualify_lead
from backend.followups import prepare_followup
from backend.ai_providers import build_offline_review_envelope


GOOD = {
    "synthetic": True,
    "external_ref": "DEMO-INPUT-01",
    "source": "website",
    "need": "repair",
    "status": "received",
}


class InputBoundaryTests(unittest.TestCase):
    def test_rejects_freeform_contact_fields_at_all_entrypoints(self):
        for field, value in (
            ("email", "someone@example.invalid"),
            ("phone", "555-0100"),
            ("notes", "freeform text"),
        ):
            with self.subTest(field=field):
                lead = {**GOOD, field: value}
                for fn in (
                    qualify_lead,
                    prepare_followup,
                    build_offline_review_envelope,
                ):
                    with self.subTest(entrypoint=fn.__name__):
                        with self.assertRaises(ValueError):
                            fn(lead)

    def test_rejects_invalid_synthetic_markers_and_unapproved_categories(self):
        cases = (
            {"synthetic": 1},
            {"synthetic": False},
            {"status": "qualified"},
            {"source": "direct_message"},
            {"need": "urgent: call this number"},
            {"external_ref": "LIVE-123"},
            {"external_ref": "DEMO-abc@example.invalid"},
        )
        for override in cases:
            with self.subTest(override=override):
                with self.assertRaises(ValueError):
                    build_offline_review_envelope({**GOOD, **override})

    def test_rejects_ambiguous_opt_out_and_objection_values(self):
        for flag in (0, 1, "false", [], {}):
            with self.subTest(flag=repr(flag)):
                with self.assertRaises(ValueError):
                    build_offline_review_envelope(GOOD, opted_out=flag)
        for objection in ("discount", "call me", "", 1, False, []):
            with self.subTest(objection=repr(objection)):
                with self.assertRaises(ValueError):
                    build_offline_review_envelope(GOOD, objection=objection)

    def test_valid_unknown_suppression_is_internal_only(self):
        envelope = build_offline_review_envelope(GOOD)
        self.assertIsNone(envelope["qualification"]["confidence"])
        self.assertIn("suppression_status", envelope["qualification"]["unknowns"])
        self.assertFalse(envelope["outreach_enabled"])
        self.assertFalse(envelope["followup"]["sent"])
        self.assertFalse(envelope["followup"]["send_enabled"])
        self.assertTrue(envelope["followup"]["requires_human_approval"])


if __name__ == "__main__":
    unittest.main()
