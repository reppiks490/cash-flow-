"""Regression: callers cannot mutate synthetic queue state through returned records.

Run from products/revenue_recovery: python -m unittest discover -s tests -p 'test_qa_store_defensive_copy.py'
"""
import unittest

from backend.app import DemoStore, LeadConflictError
from backend.contracts import SOURCES, NEEDS


class StoreDefensiveCopyTests(unittest.TestCase):
    def setUp(self):
        self.store = DemoStore()
        self.payload = {
            "synthetic": True,
            "external_ref": "QA-DEFENSIVE-COPY-1",
            "source": sorted(SOURCES)[0],
            "need": sorted(NEEDS)[0],
        }

    def test_add_result_cannot_mutate_stored_record(self):
        returned, created = self.store.add(self.payload)
        self.assertTrue(created)
        returned["status"] = "paid"
        returned["synthetic"] = False
        self.assertEqual(self.store.get(self.payload["external_ref"])["status"], "received")
        self.assertTrue(self.store.get(self.payload["external_ref"])["synthetic"])

    def test_get_and_list_results_cannot_mutate_stored_record(self):
        self.store.add(self.payload)
        self.store.get(self.payload["external_ref"])["status"] = "closed"
        self.store.list()[0]["status"] = "paid"
        self.assertEqual(self.store.get(self.payload["external_ref"])["status"], "received")

    def test_duplicate_result_is_copy_and_does_not_create_second_row(self):
        self.store.add(self.payload)
        replay, created = self.store.add(dict(self.payload))
        self.assertFalse(created)
        replay["source"] = "tampered"
        self.assertEqual(len(self.store.list()), 1)
        self.assertEqual(self.store.get(self.payload["external_ref"])["source"], self.payload["source"])

    def test_conflicting_replay_rejected_without_mutation(self):
        self.store.add(self.payload)
        other = next((v for v in sorted(NEEDS) if v != self.payload["need"]), None)
        if other is None:
            self.skipTest("Contract has fewer than two need categories")
        with self.assertRaises(LeadConflictError):
            self.store.add({**self.payload, "need": other})
        self.assertEqual(self.store.get(self.payload["external_ref"])["need"], self.payload["need"])


if __name__ == "__main__":
    unittest.main()
