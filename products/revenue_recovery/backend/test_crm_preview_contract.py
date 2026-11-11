"""Dependency-free safety regressions for the synthetic CRM preview adapter.

Run from products/revenue_recovery:
    python -m unittest discover -s backend -p 'test_crm_preview_contract.py'
No CRM vendor, credentials, network or real customer data are involved.
"""
import json
import unittest

from backend.crm import preview_crm_envelope, preview_crm_record


FIXTURE = {
    "synthetic": True,
    "external_ref": "DEMO-HVAC-001",
    "source": "website",
    "need": "AC not cooling",
}


class CRMPreviewContractTests(unittest.TestCase):
    def test_json_envelope_is_explicitly_dry_run_and_unverified(self):
        envelope = preview_crm_envelope(FIXTURE)
        self.assertEqual(envelope["schema_version"], "rre.crm.preview.v1")
        self.assertIs(envelope["synthetic"], True)
        self.assertIs(envelope["dry_run"], True)
        self.assertIs(envelope["transmitted"], False)
        self.assertIs(envelope["appointment_confirmed"], False)
        self.assertEqual(envelope["verified_recovered_revenue_cents"], 0)
        self.assertIsNone(envelope["provider"])
        self.assertIsNone(envelope["provider_record_id"])
        self.assertEqual(json.loads(json.dumps(envelope)), envelope)

    def test_preview_does_not_mutate_caller_record(self):
        lead = dict(FIXTURE)
        before = dict(lead)
        record = preview_crm_record(lead)
        self.assertEqual(lead, before)
        self.assertEqual(record.proposed_stage, "new_inquiry")
        self.assertFalse(record.transmitted)

    def test_rejects_realistic_contact_or_vendor_fields(self):
        for field, value in (
            ("email", "customer@example.invalid"),
            ("phone", "555-000-0000"),
            ("tenant_id", "tenant-1"),
            ("provider", "live-crm"),
            ("appointment_confirmed", True),
            ("verified_recovered_revenue_cents", 100),
        ):
            with self.subTest(field=field):
                with self.assertRaises(ValueError):
                    preview_crm_envelope({**FIXTURE, field: value})

    def test_rejects_non_synthetic_and_unverified_stage(self):
        for change in (
            {"synthetic": False},
            {"status": "paid"},
            {"status": "booked"},
            {"external_ref": "REAL-CUSTOMER-1"},
        ):
            with self.subTest(change=change):
                with self.assertRaises((ValueError, TypeError)):
                    preview_crm_envelope({**FIXTURE, **change})

    def test_rejects_non_mapping_input(self):
        for bad in (None, [], "DEMO-HVAC-001"):
            with self.subTest(bad=bad):
                with self.assertRaises(ValueError):
                    preview_crm_envelope(bad)


if __name__ == "__main__":
    unittest.main()
