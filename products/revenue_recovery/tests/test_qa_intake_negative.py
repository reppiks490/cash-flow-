"""Synthetic-only intake security regressions; no network or external side effects.

Run from products/revenue_recovery:
    python -m unittest discover -s tests -p 'test_qa_intake_negative.py' -v
"""
import json
import unittest

from backend.app import (
    DemoStore,
    LeadConflictError,
    _reject_duplicate_json_fields,
    _reject_nonstandard_json_constant,
)


class IntakeNegativeContractTests(unittest.TestCase):
    def setUp(self):
        self.store = DemoStore()
        self.lead = {
            "synthetic": True,
            "external_ref": "QA-NEGATIVE-1",
            "source": "demo",
            "need": "repair",
        }

    def test_nested_duplicate_json_keys_fail_closed(self):
        payload = '{"synthetic":true,"metadata":{"x":1,"x":2}}'
        with self.assertRaises(ValueError):
            json.loads(payload, object_pairs_hook=_reject_duplicate_json_fields)

    def test_nonfinite_json_numbers_fail_closed(self):
        for token in ("NaN", "Infinity", "-Infinity"):
            with self.subTest(token=token):
                with self.assertRaises(ValueError):
                    json.loads('{"value":' + token + '}',
                               parse_constant=_reject_nonstandard_json_constant)

    def test_duplicate_reference_cannot_change_source_or_need(self):
        first, created = self.store.add(self.lead)
        self.assertTrue(created)
        self.assertEqual(first["status"], "received")
        for change in ({"source": "website"}, {"need": "maintenance"}):
            with self.subTest(change=change):
                with self.assertRaises(LeadConflictError):
                    self.store.add({**self.lead, **change})
        self.assertEqual(len(self.store.list()), 1)

    def test_replay_and_reads_return_defensive_copies(self):
        self.store.add(self.lead)
        replay, created = self.store.add(self.lead)
        self.assertFalse(created)
        replay["status"] = "paid"
        self.store.list()[0]["status"] = "paid"
        self.store.get(self.lead["external_ref"])["status"] = "paid"
        self.assertEqual(self.store.get(self.lead["external_ref"])["status"], "received")

    def test_synthetic_flag_cannot_authorize_arbitrary_customer_fields(self):
        for field, value in (
            ("email", "private@example.invalid"),
            ("phone", "0000000000"),
            ("customer_name", "Private Person"),
            ("tenant_id", "other-tenant"),
            ("paid_amount", 999999),
        ):
            with self.subTest(field=field):
                with self.assertRaises(ValueError):
                    self.store.add({**self.lead, field: value})
        self.assertEqual(self.store.list(), [])

    def test_noncanonical_reference_and_unicode_lookalikes_rejected(self):
        for ref in ("QA-\u212a", "QA-\u0131", "QA-\u00e9", "REAL-123", "QA-../x", "QA-"):
            with self.subTest(ref=ref):
                with self.assertRaises(ValueError):
                    self.store.add({**self.lead, "external_ref": ref})


if __name__ == "__main__":
    unittest.main()
