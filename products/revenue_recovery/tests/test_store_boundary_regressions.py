"""Offline adversarial tests for the synthetic DemoStore boundary.

No network, customer information, provider credentials, or live integrations.
"""
import unittest

from backend.app import DemoStore, LeadConflictError


def lead(ref="QA-STORE-BOUNDARY-1", **overrides):
    payload = {
        "synthetic": True,
        "external_ref": ref,
        "source": "demo",
        "need": "repair",
    }
    payload.update(overrides)
    return payload


class DemoStoreBoundaryTests(unittest.TestCase):
    def setUp(self):
        self.store = DemoStore()

    def test_caller_mutation_cannot_change_stored_identity_or_status(self):
        incoming = lead()
        created, is_new = self.store.add(incoming)
        self.assertTrue(is_new)
        incoming["need"] = "AC maintenance"
        created["status"] = "paid"
        created["source"] = "referral"
        fetched = self.store.get("QA-STORE-BOUNDARY-1")
        self.assertEqual(fetched["need"], "repair")
        self.assertEqual(fetched["status"], "received")
        self.assertEqual(fetched["source"], "demo")

    def test_readback_and_listing_return_defensive_copies(self):
        self.store.add(lead())
        fetched = self.store.get("QA-STORE-BOUNDARY-1")
        listed = self.store.list()
        fetched["status"] = "closed"
        listed[0]["status"] = "paid"
        self.assertEqual(self.store.get("QA-STORE-BOUNDARY-1")["status"], "received")
        self.assertEqual(self.store.list()[0]["status"], "received")

    def test_replay_preserves_original_and_rejects_conflicting_identity(self):
        first, created = self.store.add(lead())
        second, created_again = self.store.add(lead())
        self.assertTrue(created)
        self.assertFalse(created_again)
        self.assertEqual(first, second)
        with self.assertRaises(LeadConflictError):
            self.store.add(lead(need="AC maintenance"))
        self.assertEqual(len(self.store.list()), 1)

    def test_fake_payment_and_recipient_fields_are_rejected(self):
        for field, value in (
            ("status", "paid"),
            ("payment_receipt", "FAKE-RECEIPT"),
            ("email", "demo@example.invalid"),
            ("phone", "0000000000"),
            ("tenant_id", "other"),
            ("approved", True),
        ):
            with self.subTest(field=field):
                with self.assertRaises(ValueError):
                    self.store.add(lead(**{field: value}))
        self.assertEqual(self.store.list(), [])

    def test_invalid_synthetic_identity_and_scalar_values_fail_closed(self):
        cases = (
            {"synthetic": 1},
            {"synthetic": False},
            {"external_ref": "person@example.invalid"},
            {"external_ref": "QA-STORE-BOUNDARY-1/../escape"},
            {"source": "person@example.invalid"},
            {"need": "Call 000-000-0000"},
            {"need": None},
            {"source": ["demo"]},
        )
        for change in cases:
            with self.subTest(change=change):
                with self.assertRaises(ValueError):
                    self.store.add(lead(**change))
        self.assertEqual(self.store.list(), [])

    def test_missing_reference_does_not_create_record(self):
        self.assertIsNone(self.store.get("QA-NOT-PRESENT"))
        self.assertEqual(self.store.list(), [])


if __name__ == "__main__":
    unittest.main()
