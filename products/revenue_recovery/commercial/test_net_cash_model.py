"""Regression tests for synthetic-only vendor net reporting."""
import unittest

try:
    from .net_cash_model import FIELDS, calculate_synthetic_net
except ImportError:
    from net_cash_model import FIELDS, calculate_synthetic_net


class NetCashModelTests(unittest.TestCase):
    def setUp(self):
        self.data = {name: "0" for name in FIELDS}
        self.data["settled_collections"] = "3500.00"
        self.data["infrastructure"] = "1000.00"

    def test_hypothetical_target_is_never_verified(self):
        result = calculate_synthetic_net(self.data)
        self.assertEqual(result.pretax_cash_operating_net_cents, 250000)
        self.assertFalse(result.target_met_verified)
        self.assertFalse(result.verified_profit)
        self.assertTrue(result.synthetic)

    def test_owner_labor_changes_economic_not_cash_net(self):
        self.data["owner_labor_imputed"] = "400.00"
        result = calculate_synthetic_net(self.data)
        self.assertEqual(result.pretax_cash_operating_net_cents, 250000)
        self.assertEqual(result.pretax_economic_net_cents, 210000)

    def test_refunds_and_fees_reduce_net(self):
        self.data["refunds"] = "50.25"
        self.data["processing_fees"] = "10.01"
        self.assertEqual(calculate_synthetic_net(self.data).pretax_cash_operating_net_cents, 243974)

    def test_negative_net_is_preserved(self):
        self.data["settled_collections"] = "0"
        self.assertEqual(calculate_synthetic_net(self.data).pretax_cash_operating_net_cents, -100000)

    def test_reject_unsafe_amounts(self):
        for bad in (1, 1.0, True, None, "-1", "1e3", "NaN", "1.234", "01", " 1", "1.", "9999999999999"):
            with self.subTest(bad=bad):
                self.data["refunds"] = bad
                with self.assertRaises(ValueError):
                    calculate_synthetic_net(self.data)

    def test_reject_missing_extra_or_unexpected_fields(self):
        with self.assertRaises(ValueError):
            calculate_synthetic_net({})
        with self.assertRaises(ValueError):
            calculate_synthetic_net({**self.data, "customer_email": "private"})
