"""Capacity-boundary regression for the synthetic, process-local demo store.

Run from products/revenue_recovery:
    python -m unittest backend.test_store_capacity -v
No live services, PII, network calls, or production state.
"""
import unittest
from unittest.mock import patch

from backend import app
from backend.contracts import SOURCES, NEEDS


class DemoStoreCapacityTests(unittest.TestCase):
    def setUp(self):
        self.store = app.DemoStore()
        self.source = sorted(SOURCES)[0]
        self.need = sorted(NEEDS)[0]

    def lead(self, ref):
        return {
            "synthetic": True,
            "external_ref": ref,
            "source": self.source,
            "need": self.need,
        }

    def test_capacity_boundary_is_atomic_and_existing_replays_still_work(self):
        with patch.object(app, "MAX_LEADS", 2):
            first, created = self.store.add(self.lead("QA-CAPACITY-1"))
            self.assertTrue(created)
            self.assertEqual(first["external_ref"], "QA-CAPACITY-1")
            _, created = self.store.add(self.lead("QA-CAPACITY-2"))
            self.assertTrue(created)

            with self.assertRaisesRegex(ValueError, "Demo capacity reached"):
                self.store.add(self.lead("QA-CAPACITY-3"))

            replay, created = self.store.add(self.lead("QA-CAPACITY-1"))
            self.assertFalse(created)
            self.assertEqual(replay["external_ref"], "QA-CAPACITY-1")
            self.assertEqual(len(self.store.list()), 2)
            self.assertIsNone(self.store.get("QA-CAPACITY-3"))

    def test_rejected_capacity_insert_does_not_corrupt_existing_records(self):
        with patch.object(app, "MAX_LEADS", 1):
            self.store.add(self.lead("QA-CAPACITY-4"))
            with self.assertRaisesRegex(ValueError, "Demo capacity reached"):
                self.store.add(self.lead("QA-CAPACITY-5"))
            self.assertEqual(
                [row["external_ref"] for row in self.store.list()],
                ["QA-CAPACITY-4"],
            )


if __name__ == "__main__":
    unittest.main()
