"""Dependency-free CRM preview contract regression tests (synthetic only)."""
import unittest

from products.revenue_recovery.backend.crm import preview_crm_record
from backend.contracts import SOURCES, NEEDS


class CRMPreviewContractTests(unittest.TestCase):
    def setUp(self):
        self.lead = dict(synthetic=True, external_ref="DEMO-HVAC-001",
                         source="website", need="AC not cooling", status="received")

    def test_non_mapping_is_controlled_value_error(self):
        for payload in (None, [], "synthetic", 123):
            with self.subTest(payload=payload), self.assertRaises(ValueError):
                preview_crm_record(payload)

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

    def test_all_intake_contract_categories_preview_without_transmission(self):
        # Consume the canonical contract; avoid drift-prone local copies.
        for source in SOURCES:
            for need in NEEDS:
                with self.subTest(source=source, need=need):
                    result = preview_crm_record({**self.lead, "source": source, "need": need})
                    self.assertEqual((result.source, result.need), (source, need))
                    self.assertTrue(result.dry_run)
                    self.assertFalse(result.transmitted)

    def test_reference_must_match_local_demo_prefix(self):
        for ref in ("CONTACT-123", "client", "DEMO-", "QA-a@b", "DEMO-" + "A" * 57):
            with self.subTest(ref=ref), self.assertRaises(ValueError):
                preview_crm_record({**self.lead, "external_ref": ref})
        for ref in ("DEMO-A", "QA-123", "demo-a", "QA_1"):
            with self.subTest(ref=ref):
                self.assertEqual(preview_crm_record({**self.lead, "external_ref": ref}).external_ref, ref)


if __name__ == "__main__":
    unittest.main()
