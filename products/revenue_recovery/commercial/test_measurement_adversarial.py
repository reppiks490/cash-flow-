"""Adversarial synthetic financial-measurement contract tests (no I/O)."""
import unittest
from decimal import Decimal

from commercial.measurement_guards import MeasurementError, SyntheticMonthlySnapshot, usd


class MeasurementAdversarialTests(unittest.TestCase):
    def test_reject_unicode_and_noncanonical_currency(self):
        for value in ("７００", "٧٠٠", "1_000", "1,000", "+1", " 1",
                      "1 ", "1\n", "01", "00.01", ".5", "1.",
                      "1e3", "1E+999999", "0x10", "1\x000", "1\u200b0"):
            with self.subTest(value=repr(value)), self.assertRaises(MeasurementError):
                usd(value)

    def test_reject_nonstring_and_oversize_currency(self):
        for value in (True, False, 0, 1, 1.0, Decimal("1"), None,
                      [], {}, "99999999.99", "10000000.01", "9" * 10000):
            with self.subTest(value=repr(value)[:80]), self.assertRaises(MeasurementError):
                usd(value)

    def test_money_is_exact_at_two_decimal_places(self):
        self.assertEqual(usd("0"), Decimal("0.00"))
        self.assertEqual(usd("0.1"), Decimal("0.10"))
        self.assertEqual(usd("9999999.99"), Decimal("9999999.99"))
        self.assertEqual(usd("10000000.00"), Decimal("10000000.00"))

    def test_subscription_count_is_strictly_bounded(self):
        for count in (-1, True, False, 1.0, "1", None, 1000001):
            with self.subTest(count=repr(count)), self.assertRaises(MeasurementError):
                SyntheticMonthlySnapshot(count, "700", "0", "0", "0").evaluate()

    def test_profit_never_becomes_verified_receipts(self):
        for count, price, refund, direct, overhead in (
            (0, "700", "0", "0", "0"),
            (5, "700", "0", "400", "600"),
            (6, "700", "100", "500", "1000"),
            (1000000, "10000000", "0", "0", "0"),
        ):
            with self.subTest(count=count):
                result = SyntheticMonthlySnapshot(count, price, refund, direct, overhead).evaluate()
                self.assertIs(result["synthetic"], True)
                self.assertIs(result["verified"], False)
                for key in ("verified_receipts_usd", "verified_net_profit_usd",
                            "customer_recovered_revenue_usd"):
                    self.assertIsNone(result[key])
                self.assertEqual(
                    result["target_met_in_scenario"],
                    Decimal(result["net_profit_scenario_usd"]) >= Decimal("2500.00"),
                )


if __name__ == "__main__":
    unittest.main()
