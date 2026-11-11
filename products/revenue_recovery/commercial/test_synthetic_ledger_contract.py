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

    def test_rejects_noncanonical_or_unbounded_money(self):
        for amount in ("1e2", "01.00", "+1.00", " 1.00", "1.00 ", ".50", "1.", "100000000", "-0.00", "0.000", "", True, None):
            with self.subTest(amount=amount), self.assertRaises(ValueError):
                reconcile([receipt("sub", "saas", amount)])
        for expense in ("1e2", "0001.00", "100000000", "-0.00", True):
            with self.subTest(expense=expense), self.assertRaises(ValueError):
                reconcile([], expenses_complete=True, expenses=[expense])

    def test_rejects_nonfinite_event_and_expense_containers(self):
        for events in (None, {}, "events", (item for item in [])):
            with self.subTest(events=type(events).__name__), self.assertRaises(ValueError):
                reconcile(events)
        for expenses in (None, {}, "expenses", (item for item in [])):
            with self.subTest(expenses=type(expenses).__name__), self.assertRaises(ValueError):
                reconcile([], expenses=expenses)

    def test_rejects_oversized_synthetic_batches(self):
        with self.assertRaisesRegex(ValueError, "bounded batch size"):
            reconcile([receipt("x", "saas", "1.00")] * 10001)
        with self.assertRaisesRegex(ValueError, "bounded batch size"):
            reconcile([], expenses=["0.01"] * 10001, expenses_complete=True)

    def test_malformed_adjustment_parent_ids_fail_with_value_error(self):
        for parent in (None, [], {}, 42, True, "../escape", "x/y", "x" * 129, "é"):
            with self.subTest(parent=repr(parent)), self.assertRaises(ValueError):
                reconcile([receipt("sub", "saas", "10.00"),
                           adjustment("refund", "saas", parent, "1.00")])
        self.assertEqual(reconcile([receipt("sub", "saas", "10.00"),
                                    adjustment("refund", "saas", "sub", "1.00")])["saas_collected_usd"], "9.00")

    def test_rejects_unbounded_or_unsafe_event_identifiers(self):
        for ident in ("", " ", "../escape", "x/y", "line\nfeed", "x" * 129, "é", "\\u0000", "x\\ty"):
            with self.subTest(ident=repr(ident)), self.assertRaises(ValueError):
                reconcile([receipt(ident, "saas", "1.00")])
        valid = "A" * 128
        self.assertEqual(reconcile([receipt(valid, "saas", "1.00")])["saas_collected_usd"], "1.00")
        with self.assertRaises(ValueError):
            reconcile([receipt("ok", "saas", "1.00"), adjustment("bad/id", "saas", "ok", "0.01")])

    def test_rejects_unmodeled_event_fields_and_contact_data(self):
        for key, value in (("email", "synthetic@example.invalid"),
                           ("provider_receipt", "forged"),
                           ("tenant_id", "another-tenant"),
                           ("contact_phone", "5550100"),
                           (42, "invalid-key")):
            event = receipt("sub", "saas", "10.00")
            event[key] = value
            with self.subTest(key=key), self.assertRaisesRegex(ValueError, "unsupported synthetic event field"):
                reconcile([event])
        self.assertEqual(reconcile([receipt("sub", "saas", "10.00")])["saas_collected_usd"], "10.00")

if __name__ == "__main__":
    unittest.main()
