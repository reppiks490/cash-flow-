"""Synthetic-only CRM preview contract regression tests (RRE-03).

Run with: PYTHONPATH=products/revenue_recovery python -m unittest discover -s products/revenue_recovery/backend -p 'test_crm_envelope_contract.py'
No network, vendor credentials, customer data, or external side effects.
"""
import unittest

from backend.crm import preview_crm_envelope, preview_crm_record


VALID = {
    "synthetic": True,
    "external_ref": "DEMO-HVAC-001",
    "source": "website",
    "need": "repair",
    "status": "received",
}


class CRMEnvelopeContractTests(unittest.TestCase):
    def test_exact_preview_contract_never_claims_provider_delivery_or_revenue(self):
        envelope = preview_crm_envelope(VALID)
        self.assertEqual(envelope, {
            "schema_version": "rre.crm.preview.v1",
            "synthetic": True,
            "dry_run": True,
            "transmitted": False,
            "external_ref": "DEMO-HVAC-001",
            "source": "website",
            "need": "repair",
            "proposed_stage": "new_inquiry",
            "provider": None,
            "provider_record_id": None,
            "appointment_confirmed": False,
            "verified_recovered_revenue_cents": 0,
        })
        self.assertEqual(VALID["status"], "received")

    def test_missing_status_defaults_only_to_received(self):
        without_status = {k: v for k, v in VALID.items() if k != "status"}
        self.assertEqual(preview_crm_record(without_status).proposed_stage, "new_inquiry")
        self.assertNotIn("status", without_status)

    def test_rejects_contact_data_and_fake_provider_evidence(self):
        for field, value in (
            ("phone", "555-0100"),
            ("email", "synthetic@example.invalid"),
            ("provider_record_id", "fake-id"),
            ("verified_recovered_revenue_cents", 250000),
            ("tenant_id", "other-tenant"),
        ):
            with self.subTest(field=field):
                with self.assertRaises(ValueError):
                    preview_crm_envelope({**VALID, field: value})

    def test_rejects_forged_outcomes_and_non_synthetic_leads(self):
        for mutation in (
            {"status": "paid"},
            {"status": "booked"},
            {"synthetic": False},
            {"external_ref": "CUSTOMER-001"},
        ):
            with self.subTest(mutation=mutation):
                with self.assertRaises((ValueError, TypeError)):
                    preview_crm_envelope({**VALID, **mutation})


if __name__ == "__main__":
    unittest.main()
