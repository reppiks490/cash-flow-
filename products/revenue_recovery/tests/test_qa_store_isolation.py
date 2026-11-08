"""QA-owned synthetic store isolation and concurrency regression tests.

No network access, real leads, customer data, or external side effects.
"""
import concurrent.futures
import unittest

from backend.app import DemoStore


def lead(ref="QA-STORE-001", need="repair"):
    return {"synthetic": True, "external_ref": ref, "source": "demo", "need": need}


class StoreIsolationTests(unittest.TestCase):
    def test_add_get_and_list_return_defensive_copies(self):
        store = DemoStore()
        original = lead()
        stored, created = store.add(original)
        self.assertTrue(created)
        original["need"] = "maintenance"
        stored["need"] = "maintenance"
        fetched = store.get("QA-STORE-001")
        self.assertEqual(fetched["need"], "repair")
        fetched["need"] = "maintenance"
        listing = store.list()
        listing[0]["need"] = "maintenance"
        listing.clear()
        self.assertEqual(store.get("QA-STORE-001")["need"], "repair")
        self.assertEqual(len(store.list()), 1)

    def test_parallel_identical_replays_create_exactly_one_lead(self):
        store = DemoStore()
        with concurrent.futures.ThreadPoolExecutor(max_workers=12) as pool:
            results = list(pool.map(lambda _: store.add(lead()), range(48)))
        self.assertEqual(sum(1 for _, created in results if created), 1)
        self.assertEqual(len(store.list()), 1)
        self.assertTrue(all(row["external_ref"] == "QA-STORE-001"
                            for row, _ in results))

    def test_conflicting_reference_never_overwrites_original(self):
        from backend.app import LeadConflictError
        store = DemoStore()
        store.add(lead())
        with self.assertRaises(LeadConflictError):
            store.add(lead(need="maintenance"))
        self.assertEqual(store.get("QA-STORE-001")["need"], "repair")
        self.assertEqual(len(store.list()), 1)


if __name__ == "__main__":
    unittest.main()
