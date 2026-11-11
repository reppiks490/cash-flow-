"""Negative controls for the synthetic dual-ledger commercial contract."""
import unittest
from commercial.synthetic_ledger_contract import reconcile

def receipt(ident, ledger, amount, attribution=None):
    item = {"id": ident, "ledger": ledger, "kind": "receipt", "amount": amount, "synthetic": True}
    if attribution is not None:
        item["attribution"] = attribution
    return item

def adjustment(ident, ledger, parent, amount, kind="refund"):
    return {"id": ident, "ledger": ledger, "kind": kind, "parent_id": parent, "amount": amount, "synthetic": True}

class DualLedgerContractTests(unittest.TestCase):
    def test_separate_contractor_and_saas_receipts(self):
        result = reconcile([receipt("job1", "contractor", "500.00", "confirmed"), receipt("sub1", "saas", "700.00")], expenses_complete=True, expenses=["100.00"])
        self.assertEqual(result["contractor_collected_usd"], "500.00")
        self.assertEqual(result["contractor_attributable_usd"], "500.00")
        self.assertEqual(result["saas_collected_usd"], "700.00")
        self.assertEqual(result["synthetic_saas_contribution_usd"], "600.00")
        self.assertIsNone(result["verified_net_profit_usd"])
        self.assertFalse(result["target_is_verified"])

    def test_partial_refund_and_chargeback_are_not_double_counted(self):
        events = [receipt("sub", "saas", "700.00"), adjustment("r1", "saas", "sub", "100.00"), adjustment("cb1", "saas", "sub", "200.00", "chargeback")]
        self.assertEqual(reconcile(events)["saas_collected_usd"], "400.00")

    def test_ambiguous_contractor_attribution_never_claimed(self):
        result = reconcile([receipt("job", "contractor", "900.00", "ambiguous")])
        self.assertEqual(result["contractor_collected_usd"], "900.00")
        self.assertEqual(result["contractor_attributable_usd"], "0.00")

    def test_missing_expense_completeness_does_not_infer_profit(self):
        result = reconcile([receipt("sub", "saas", "700.00")], expenses=["100.00"])
        self.assertIsNone(result["synthetic_saas_contribution_usd"])
        self.assertIsNone(result["verified_net_profit_usd"])

    def test_duplicates_and_cross_ledger_refunds_fail_closed(self):
        cases = [
            [receipt("x", "saas", "100.00"), receipt("x", "saas", "100.00")],
            [receipt("x", "saas", "100.00"), adjustment("r", "contractor", "x", "10.00")],
            [receipt("x", "saas", "100.00"), adjustment("r", "saas", "x", "101.00")],
            [adjustment("r", "saas", "missing", "10.00")],
            [receipt("x", "contractor", "100.00")],
        ]
        for events in cases:
            with self.subTest(events=events), self.assertRaises(ValueError):
                reconcile(events)

    def test_rejects_non_synthetic_and_malformed_amounts(self):
        for amount in ("NaN", "Infinity", "-1", "1.001", "not-money", 100):
            with self.subTest(amount=amount), self.assertRaises(ValueError):
                reconcile([receipt("sub", "saas", amount)])
        event = receipt("sub", "saas", "100.00")
        event["synthetic"] = False
        with self.assertRaises(ValueError):
            reconcile([event])

if __name__ == "__main__":
    unittest.main()
