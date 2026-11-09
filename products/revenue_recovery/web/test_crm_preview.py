"""Fail-closed contract tests for the synthetic-only CRM preview.

Run from products/revenue_recovery:
    python -m unittest discover -s web -p 'test_crm_preview.py' -v

No vendor, network, authentication bypass, or real customer records.
"""
import unittest

from backend.crm import preview_crm_envelope, preview_crm_record


VALID = {
    "synthetic": True,
    "external_ref": "DEMO-HVAC-001",
    "source": "website",
    "need": "AC not cooling",
    "status": "received",
}


class CRMPreviewContractTests(unittest.TestCase):
    def test_vendor_neutral_envelope_is_explicitly_non_operational(self):
        envelope = preview_crm_envelope(VALID)
        self.assertEqual(envelope["schema_version"], "rre.crm.preview.v1")
        self.assertIs(envelope["synthetic"], True)
        self.assertIs(envelope["dry_run"], True)
        self.assertIs(envelope["transmitted"], False)
        self.assertIsNone(envelope["provider"])
        self.assertIsNone(envelope["provider_record_id"])
        self.assertIs(envelope["appointment_confirmed"], False)
        self.assertEqual(envelope["verified_recovered_revenue_cents"], 0)
        self.assertEqual(envelope["proposed_stage"], "new_inquiry")

    def test_envelope_has_only_approved_fields(self):
        self.assertEqual(
            set(preview_crm_envelope(VALID)),
            {
                "schema_version", "synthetic", "dry_run", "transmitted",
                "external_ref", "source", "need", "proposed_stage",
                "provider", "provider_record_id", "appointment_confirmed",
                "verified_recovered_revenue_cents",
            },
        )

    def test_missing_status_defaults_to_received_not_closed(self):
        payload = {key: value for key, value in VALID.items() if key != "status"}
        record = preview_crm_record(payload)
        self.assertEqual(record.proposed_stage, "new_inquiry")
        self.assertIs(record.transmitted, False)

    def test_untrusted_customer_fields_are_rejected(self):
        for field in ("email", "phone", "customer_name", "tenant_id", "api_key"):
            with self.subTest(field=field):
                with self.assertRaises(ValueError):
                    preview_crm_envelope({**VALID, field: "not-real"})

    def test_non_synthetic_or_fabricated_closed_outcome_rejected(self):
        for mutation in (
            {"synthetic": False},
            {"status": "paid"},
            {"status": "booked"},
            {"source": "unknown-provider"},
            {"external_ref": "real-customer-123"},
        ):
            with self.subTest(mutation=mutation):
                with self.assertRaises(ValueError):
                    preview_crm_envelope({**VALID, **mutation})


if __name__ == "__main__":
    unittest.main()
