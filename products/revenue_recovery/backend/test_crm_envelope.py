"""No-network CRM envelope contract tests (stdlib only)."""
import unittest
from backend.crm import preview_crm_envelope


class CRMEnvelopeTests(unittest.TestCase):
    def setUp(self):
        self.lead = {
            "synthetic": True, "external_ref": "DEMO-HVAC-001",
            "source": "website", "need": "AC not cooling", "status": "received",
        }

    def test_canonical_preview_is_inert(self):
        result = preview_crm_envelope(self.lead)
        self.assertEqual(result["schema_version"], "rre.crm.preview.v1")
        self.assertTrue(result["synthetic"])
        self.assertTrue(result["dry_run"])
        self.assertFalse(result["transmitted"])
        self.assertIsNone(result["provider"])
        self.assertIsNone(result["provider_record_id"])
        self.assertFalse(result["appointment_confirmed"])
        self.assertEqual(result["verified_recovered_revenue_cents"], 0)
        self.assertEqual(result["proposed_stage"], "new_inquiry")
        self.assertEqual(self.lead["status"], "received")

    def test_optional_stored_status(self):
        row = dict(self.lead)
        del row["status"]
        self.assertEqual(preview_crm_envelope(row)["proposed_stage"], "new_inquiry")

    def test_rejects_customer_contact(self):
        for field in ("email", "phone", "customer_name", "tenant_id", "provider"):
            with self.subTest(field=field), self.assertRaises(ValueError):
                preview_crm_envelope({**self.lead, field: "private"})

    def test_rejects_fake_paid_stage(self):
        with self.assertRaises(ValueError):
            preview_crm_envelope({**self.lead, "status": "paid"})

    def test_rejects_unsynthetic(self):
        with self.assertRaises(ValueError):
            preview_crm_envelope({**self.lead, "synthetic": False})

    def test_rejects_wrong_shape(self):
        with self.assertRaises(ValueError):
            preview_crm_envelope(["not", "a", "lead"])


if __name__ == "__main__":
    unittest.main()
