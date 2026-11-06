"""Zero-dependency smoke and negative-case checks for the experience lane."""

import unittest
from pathlib import Path
from backend.crm import preview_crm_record


class ExperienceTests(unittest.TestCase):
    def test_crm_preview_has_no_side_effects(self):
        preview = preview_crm_record({
            "synthetic": True, "external_ref": "DEMO-1",
            "source": "website", "need": "repair", "status": "received"
        })
        self.assertTrue(preview.dry_run)
        self.assertFalse(preview.transmitted)
        self.assertEqual(preview.proposed_stage, "new_inquiry")

    def test_crm_rejects_live_and_contact_fields(self):
        for row in [
            {"synthetic": False, "external_ref": "x", "source": "s", "need": "n"},
            {"synthetic": True, "external_ref": "x", "source": "s", "need": "n", "phone": "123"},
            {"synthetic": True, "external_ref": "x", "source": "s", "need": "n", "status": "paid"},
        ]:
            with self.subTest(row=row), self.assertRaises(ValueError):
                preview_crm_record(row)

    def test_static_app_is_same_origin_and_synthetic(self):
        js = (Path(__file__).parent / "app.js").read_text(encoding="utf-8")
        self.assertIn('fetch("/api/demo/leads"', js)
        self.assertIn("SYNTHETIC", (Path(__file__).parent / "index.html").read_text(encoding="utf-8"))
        self.assertNotIn("innerHTML", js)
        self.assertNotIn("localStorage", js)


if __name__ == "__main__":
    unittest.main()
