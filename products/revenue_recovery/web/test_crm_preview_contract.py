"""Dependency-free CRM preview contract regression tests (synthetic only)."""
import unittest

from products.revenue_recovery.backend.crm import preview_crm_record


class CRMPreviewContractTests(unittest.TestCase):
    def setUp(self):
        self.lead = dict(synthetic=True, external_ref="DEMO-HVAC-001",
                         source="website", need="AC not cooling", status="received")

    def test_preview_never_transmits(self):
        result = preview_crm_record(self.lead)
        self.assertTrue(result.synthetic)
        self.assertTrue(result.dry_run)
        self.assertFalse(result.transmitted)
        self.assertEqual(result.proposed_stage, "new_inquiry")

    def test_rejects_free_text_pii_in_each_field(self):
        for field, value in (("external_ref", "customer@example.com"),
                             ("source", "customer@example.com"),
                             ("need", "Call Jane at 555-0100")):
            with self.subTest(field=field), self.assertRaises(ValueError):
                preview_crm_record({**self.lead, field: value})

    def test_rejects_non_synthetic_and_unknown_fields(self):
        for change in ({"synthetic": False}, {"email": "private@example.com"},
                       {"status": "closed"}):
            with self.subTest(change=change), self.assertRaises(ValueError):
                preview_crm_record({**self.lead, **change})

    def test_all_demo_fixture_variants(self):
        for source, need in (("website", "AC not cooling"),
                             ("phone", "estimate follow-up"),
                             ("referral", "AC maintenance")):
            with self.subTest(source=source):
                result = preview_crm_record({**self.lead, "source": source, "need": need})
                self.assertFalse(result.transmitted)


if __name__ == "__main__":
    unittest.main()
