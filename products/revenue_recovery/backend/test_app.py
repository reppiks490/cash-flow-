"""Pure standard-library checks for the synthetic-only backend contracts."""

import unittest

from backend.app import DemoStore


class DemoStoreTests(unittest.TestCase):
    def test_accepts_and_deduplicates_synthetic_lead(self):
        store = DemoStore()
        row = {"synthetic": True, "external_ref": "demo-01", "source": "website", "need": "AC not cooling"}
        self.assertEqual(store.add(row)[1], True)
        self.assertEqual(store.add(row)[1], False)
        self.assertEqual(store.list()[0]["status"], "received")
        self.assertEqual(len(store.list()), 1)

    def test_rejects_live_data_and_unknown_fields(self):
        store = DemoStore()
        for row in (
            {"synthetic": False, "external_ref": "x", "source": "s", "need": "n"},
            {"synthetic": True, "external_ref": "x", "source": "s", "need": "n", "email": "sample@example.com"},
            {"synthetic": True, "external_ref": "x", "source": "s", "need": ""},
        ):
            with self.subTest(row=row), self.assertRaises(ValueError):
                store.add(row)
        self.assertEqual(store.list(), [])

    def test_response_is_a_copy(self):
        store = DemoStore()
        data, _ = store.add({"synthetic": True, "external_ref": "a", "source": "demo", "need": "HVAC"})
        data["status"] = "paid"
        self.assertEqual(store.list()[0]["status"], "received")


if __name__ == "__main__":
    unittest.main()
