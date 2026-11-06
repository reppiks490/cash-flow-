"""Synthetic-only store integrity regression tests; no external systems or PII.

Run from products/revenue_recovery:
    python -m unittest discover -s tests -p 'test_store_integrity.py' -v
These checks are NOT authenticated multi-tenant isolation tests.
"""
import concurrent.futures
import unittest

from backend.app import DemoStore, LeadConflictError


class StoreIntegrityTests(unittest.TestCase):
    def setUp(self):
        self.store = DemoStore()

    def lead(self, ref="QA-STORE-001", need="repair"):
        return {"synthetic": True, "external_ref": ref,
                "source": "website", "need": need}

    def test_instances_have_independent_data(self):
        other = DemoStore()
        self.store.add(self.lead())
        self.assertEqual(other.list(), [])
        self.assertIsNone(other.get("QA-STORE-001"))

    def test_returned_objects_cannot_mutate_internal_state(self):
        created, flag = self.store.add(self.lead())
        self.assertTrue(flag)
        created["need"] = "maintenance"
        fetched = self.store.get("QA-STORE-001")
        fetched["need"] = "maintenance"
        listed = self.store.list()
        listed[0]["need"] = "maintenance"
        self.assertEqual(self.store.get("QA-STORE-001")["need"], "repair")

    def test_parallel_duplicate_intake_creates_exactly_one_record(self):
        payload = self.lead("QA-PARALLEL-001")
        with concurrent.futures.ThreadPoolExecutor(max_workers=12) as pool:
            results = list(pool.map(self.store.add, [payload] * 40))
        self.assertEqual(sum(created for _, created in results), 1)
        self.assertEqual(len(self.store.list()), 1)
        self.assertTrue(all(row["need"] == "repair" for row, _ in results))

    def test_conflicting_duplicate_does_not_replace_original(self):
        self.store.add(self.lead())
        with self.assertRaises(LeadConflictError):
            self.store.add(self.lead(need="maintenance"))
        self.assertEqual(self.store.get("QA-STORE-001")["need"], "repair")

    def test_rejected_payloads_do_not_persist(self):
        for payload in (
            {**self.lead(), "synthetic": False},
            {**self.lead(), "email": "synthetic@example.invalid"},
            {**self.lead(), "external_ref": "person@example.invalid"},
            {**self.lead(), "need": "contact 555-0100"},
        ):
            with self.subTest(payload=payload):
                with self.assertRaises(ValueError):
                    self.store.add(payload)
                self.assertEqual(self.store.list(), [])


if __name__ == "__main__":
    unittest.main()
