"""Synthetic in-memory intake concurrency invariants (no network or external services)."""

from concurrent.futures import ThreadPoolExecutor
import unittest

from backend.app import DemoStore, LeadConflictError


def lead(ref: str, need: str = "AC not cooling") -> dict:
    return {"synthetic": True, "external_ref": ref, "source": "website", "need": need}


class DemoStoreConcurrencyTests(unittest.TestCase):
    def test_simultaneous_identical_replays_create_once(self):
        store = DemoStore()
        with ThreadPoolExecutor(max_workers=16) as pool:
            results = list(pool.map(lambda _: store.add(lead("QA-CONCURRENT-1")), range(64)))
        self.assertEqual(sum(created for _, created in results), 1)
        self.assertEqual(len(store.list()), 1)
        self.assertTrue(all(row["external_ref"] == "QA-CONCURRENT-1" for row, _ in results))

    def test_simultaneous_conflicting_replays_do_not_overwrite(self):
        store = DemoStore()
        store.add(lead("QA-CONCURRENT-2"))
        variants = ["AC not cooling", "Heating not working"] * 32

        def attempt(need):
            try:
                return store.add(lead("QA-CONCURRENT-2", need))[1]
            except LeadConflictError:
                return "conflict"

        with ThreadPoolExecutor(max_workers=16) as pool:
            outcomes = list(pool.map(attempt, variants))
        self.assertEqual(outcomes.count(False), 32)
        self.assertEqual(outcomes.count("conflict"), 32)
        self.assertEqual(store.get("QA-CONCURRENT-2")["need"], "AC not cooling")
        self.assertEqual(len(store.list()), 1)

    def test_returned_rows_cannot_mutate_store(self):
        store = DemoStore()
        row, created = store.add(lead("QA-CONCURRENT-3"))
        self.assertTrue(created)
        row["need"] = "tampered"
        listed = store.list()
        listed[0]["source"] = "tampered"
        retrieved = store.get("QA-CONCURRENT-3")
        retrieved["status"] = "paid"
        self.assertEqual(store.get("QA-CONCURRENT-3"), {
            "synthetic": True, "external_ref": "QA-CONCURRENT-3",
            "source": "website", "need": "AC not cooling", "status": "received",
        })


if __name__ == "__main__":
    unittest.main()
