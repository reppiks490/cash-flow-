"""RRE-05 QA regression: bounded synthetic in-memory intake under saturation.

No real customer records, third-party calls, messages, receipts, or deployment.
These are characterization tests for existing DemoStore behavior, not evidence
of production rate-limiting, account authorization, or tenant isolation.

Run from repository root:
    PYTHONPATH=products/revenue_recovery python -m unittest discover \
      -s products/revenue_recovery/tests -p 'test_store_capacity.py' -v
"""
import concurrent.futures
import unittest
from unittest.mock import patch

from backend.app import DemoStore, LeadConflictError


def lead(index, *, need="repair"):
    return {
        "synthetic": True,
        "external_ref": "QA-CAPACITY-" + str(index).zfill(3),
        "source": "website",
        "need": need,
    }


class StoreCapacityTests(unittest.TestCase):
    def setUp(self):
        self.store = DemoStore()

    def test_capacity_is_a_hard_bound_without_partial_overflow(self):
        with patch("backend.app.MAX_LEADS", 3):
            for index in range(3):
                row, created = self.store.add(lead(index))
                self.assertTrue(created)
                self.assertEqual(row["external_ref"], lead(index)["external_ref"])
            with self.assertRaisesRegex(ValueError, "Demo capacity reached"):
                self.store.add(lead(3))
            self.assertEqual(len(self.store.list()), 3)
            self.assertIsNone(self.store.get(lead(3)["external_ref"]))

    def test_replay_and_conflicting_replay_do_not_bypass_capacity(self):
        with patch("backend.app.MAX_LEADS", 2):
            original, created = self.store.add(lead(0))
            self.assertTrue(created)
            self.store.add(lead(1))
            replay, created = self.store.add(lead(0))
            self.assertFalse(created)
            self.assertEqual(replay, original)
            with self.assertRaises(LeadConflictError):
                self.store.add(lead(0, need="maintenance"))
            self.assertEqual(self.store.get(lead(0)["external_ref"]), original)
            self.assertEqual(len(self.store.list()), 2)

    def test_concurrent_distinct_submissions_respect_capacity_limit(self):
        def attempt(index):
            try:
                row, created = self.store.add(lead(index))
            except ValueError as exc:
                return "rejected", type(exc).__name__
            return "accepted", (row["external_ref"], created)

        with patch("backend.app.MAX_LEADS", 7):
            with concurrent.futures.ThreadPoolExecutor(max_workers=12) as pool:
                outcomes = list(pool.map(attempt, range(25)))
        accepted = [detail for state, detail in outcomes if state == "accepted"]
        rejected = [detail for state, detail in outcomes if state == "rejected"]
        self.assertEqual(len(accepted), 7)
        self.assertEqual(len(rejected), 18)
        self.assertEqual(set(rejected), {"ValueError"})
        self.assertEqual(len({ref for ref, _ in accepted}), 7)
        self.assertTrue(all(created is True for _, created in accepted))
        self.assertEqual(len(self.store.list()), 7)


if __name__ == "__main__":
    unittest.main()
