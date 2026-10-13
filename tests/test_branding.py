import unittest

from moneyfall.branding import proof_brand


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


if __name__ == "__main__":
    unittest.main()
