"""Evidence-aware commercial KPI regression tests; synthetic inputs only."""
import unittest
from commercial.kpi_ratios import conversion_rate


class ConversionRateTests(unittest.TestCase):
    def test_normal(self):
        self.assertEqual(conversion_rate(3, 8), {"status": "calculated_from_supplied_counts_not_verified", "percent": "37.50"})

    def test_zero_numerator(self):
        self.assertEqual(conversion_rate(0, 5)["percent"], "0.00")

    def test_missing_is_unknown(self):
        for pair in ((None, 5), (0, None), (None, None)):
            with self.subTest(pair=pair):
                self.assertEqual(conversion_rate(*pair)["status"], "unknown_missing_evidence")
                self.assertIsNone(conversion_rate(*pair)["percent"])

    def test_zero_denominator_is_undefined(self):
        self.assertEqual(conversion_rate(0, 0), {"status": "undefined_zero_denominator", "percent": None})

    def test_reject_inconsistent_counts(self):
        for pair in ((6, 5), (-1, 2), (True, 2), (1.0, 2), ("1", 2), (1, -2)):
            with self.subTest(pair=pair), self.assertRaises(ValueError):
                conversion_rate(*pair)

    def test_exact_rounding(self):
        self.assertEqual(conversion_rate(1, 3)["percent"], "33.33")


if __name__ == "__main__":
    unittest.main()
