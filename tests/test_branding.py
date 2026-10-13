import json
from pathlib import Path
import unittest

from moneyfall.branding import proof_brand


ROOT = Path(__file__).resolve().parents[1]


class ProofBrandingTests(unittest.TestCase):
    def test_legacy_jobs_keep_moneyfall_by_default(self):
        self.assertEqual(proof_brand({}), "MONEYFALL")

    def test_vellumflare_can_be_selected_explicitly(self):
        self.assertEqual(
            proof_brand({"brand": "Vellumflare Studio"}),
            "Vellumflare Studio",
        )

    def test_brand_is_trimmed_but_not_rewritten(self):
        self.assertEqual(
            proof_brand({"brand": "  Vellumflare Studio  "}),
            "Vellumflare Studio",
        )

    def test_invalid_brand_values_fail_closed(self):
        invalid = [
            None,
            "",
            "   ",
            "Vellumflare\nStudio",
            "Vellumflare\rStudio",
            "Vellumflare\tStudio",
            "x" * 65,
        ]
        for value in invalid:
            with self.subTest(value=value):
                with self.assertRaises(ValueError):
                    proof_brand({"brand": value})

    def test_renderer_uses_validated_brand_in_visible_header_and_manifest(self):
        source = (ROOT / "scripts" / "render_proof.py").read_text(encoding="utf-8")
        self.assertIn("from moneyfall.branding import proof_brand", source)
        self.assertIn("brand=proof_brand(job)", source)
        self.assertIn("f'{brand.upper()} / ORIGINAL SPECIMEN'", source)
        self.assertIn("f'{brand.upper()} / CLIENT CONTENT KIT'", source)
        self.assertNotIn("'MONEYFALL / ORIGINAL SPECIMEN'", source)
        self.assertIn("brand=brand", source)

    def test_fresh_public_layout_example_uses_vellumflare_brand(self):
        jobs = json.loads(
            (ROOT / "config" / "examples" / "creative_layouts.json").read_text(
                encoding="utf-8"
            )
        )
        self.assertEqual(jobs[0]["brand"], "Vellumflare Studio")


if __name__ == "__main__":
    unittest.main()
