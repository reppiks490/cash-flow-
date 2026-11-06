"""Contract tests for inert CRM previews; no provider, network or customer records."""
import unittest

from backend.crm import preview_crm_envelope, preview_crm_record


VALID = {
    "synthetic": True,
    "external_ref": "DEMO-HVAC-001",
    "source": "website",
    "need": "AC not cooling",
}


class CRMPreviewBoundaryTests(unittest.TestCase):
    def test_preview_is_only_a_dry_run(self):
        result = preview_crm_envelope(VALID)
        self.assertEqual(result["schema_version"], "rre.crm.preview.v1")
        self.assertEqual(result["external_ref"], VALID["external_ref"])
        self.assertTrue(result["synthetic"])
        self.assertTrue(result["dry_run"])
        self.assertFalse(result["transmitted"])
        self.assertFalse(result["appointment_confirmed"])
        self.assertEqual(result["verified_recovered_revenue_cents"], 0)
        self.assertIsNone(result["provider"])
        self.assertIsNone(result["provider_record_id"])
        self.assertEqual(set(result), {
            "schema_version", "synthetic", "dry_run", "transmitted",
            "external_ref", "source", "need", "proposed_stage",
            "provider", "provider_record_id", "appointment_confirmed",
            "verified_recovered_revenue_cents",
        })

    def test_input_not_mutated_when_status_is_defaulted(self):
        original = dict(VALID)
        preview = preview_crm_record(original)
        self.assertEqual(original, VALID)
        self.assertEqual(preview.proposed_stage, "new_inquiry")
        self.assertEqual(preview.external_ref, VALID["external_ref"])

    def test_explicit_received_status_is_allowed(self):
        preview = preview_crm_envelope({**VALID, "status": "received"})
        self.assertFalse(preview["transmitted"])

    def test_rejects_contact_and_vendor_fields(self):
        for key, value in (
            ("email", "private@example.invalid"),
            ("phone", "555-0000"),
            ("tenant_id", "other-tenant"),
            ("provider", "external"),
            ("appointment_confirmed", True),
            ("verified_recovered_revenue_cents", 100000),
        ):
            with self.subTest(key=key), self.assertRaises(ValueError):
                preview_crm_envelope({**VALID, key: value})

    def test_rejects_false_synthetic_and_claimed_paid_status(self):
        for change in (
            {"synthetic": False},
            {"synthetic": "true"},
            {"status": "paid"},
            {"status": "booked"},
            {"external_ref": "CUSTOMER-123"},
            {"source": "unknown-provider"},
            {"need": "call 555-0000"},
        ):
            with self.subTest(change=change), self.assertRaises(ValueError):
                preview_crm_envelope({**VALID, **change})

    def test_rejects_non_mapping(self):
        for value in (None, [], "DEMO-HVAC-001", 5):
            with self.subTest(value=value), self.assertRaises(ValueError):
                preview_crm_envelope(value)


if __name__ == "__main__":
    unittest.main()
