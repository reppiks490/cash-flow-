"""Synthetic-only commercial classification regression checks."""
import unittest
from dataclasses import replace

try:
    from .attribution_classifier import SyntheticReceipt, classify_receipt
except ImportError:
    from attribution_classifier import SyntheticReceipt, classify_receipt


class AttributionClassifierTests(unittest.TestCase):
    def setUp(self):
        self.valid = SyntheticReceipt(True, True, True, False, True, True, True, False)

    def test_observational_not_incremental(self):
        self.assertEqual(classify_receipt(self.valid), "associated_observed")

    def test_unverified_fail_closed(self):
        for key, value in (
            ("synthetic", False), ("settled", False),
            ("tenant_join_valid", False), ("duplicate", True),
            ("refund_reconciled", False),
        ):
            with self.subTest(key=key):
                self.assertEqual(classify_receipt(replace(self.valid, **{key: value})), "unverified")

    def test_unlinked_payment(self):
        self.assertEqual(classify_receipt(replace(self.valid, rre_linked=False)), "paid_unattributed")

    def test_confounded_and_missing_review(self):
        for changes in ({"confounding_touch": True}, {"reviewed_before_action": False}):
            with self.subTest(changes=changes):
                self.assertEqual(classify_receipt(replace(self.valid, **changes)), "associated_confounded")

    def test_reject_nonboolean_and_untyped(self):
        with self.assertRaises(ValueError):
            classify_receipt(replace(self.valid, settled=1))
        with self.assertRaises(TypeError):
            classify_receipt({})


if __name__ == "__main__":
    unittest.main()
