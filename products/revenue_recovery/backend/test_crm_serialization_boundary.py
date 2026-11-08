"""JSON-boundary and side-effect regression tests for synthetic CRM previews.

No live CRM, network access, customer data, or provider credentials.
Run: PYTHONPATH=products/revenue_recovery python -m unittest discover -s products/revenue_recovery/backend -p 'test_crm_serialization_boundary.py'
"""
import json
import unittest
from dataclasses import asdict
from unittest.mock import patch

from backend.crm import preview_crm_envelope, preview_crm_record


LEAD = {
    "synthetic": True,
    "external_ref": "DEMO-HVAC-001",
    "source": "website",
    "need": "repair",
    "status": "received",
}


class CRMSerializationBoundaryTests(unittest.TestCase):
    def test_envelope_round_trips_as_plain_json_without_provider_claims(self):
        payload = json.loads(json.dumps(preview_crm_envelope(LEAD), allow_nan=False))
        self.assertEqual(payload["schema_version"], "rre.crm.preview.v1")
        self.assertIs(payload["synthetic"], True)
        self.assertIs(payload["dry_run"], True)
        self.assertIs(payload["transmitted"], False)
        self.assertIsNone(payload["provider"])
        self.assertIsNone(payload["provider_record_id"])
        self.assertIs(payload["appointment_confirmed"], False)
        self.assertEqual(payload["verified_recovered_revenue_cents"], 0)
        self.assertNotIn("tenant_id", payload)
        self.assertNotIn("recipient", payload)

    def test_record_is_frozen_and_explicitly_untransmitted(self):
        record = preview_crm_record(LEAD)
        self.assertEqual(record.proposed_stage, "new_inquiry")
        self.assertIs(record.dry_run, True)
        self.assertIs(record.transmitted, False)
        self.assertEqual(asdict(record)["external_ref"], "DEMO-HVAC-001")
        with self.assertRaises((AttributeError, TypeError)):
            record.transmitted = True

    def test_mutating_returned_envelope_cannot_poison_future_preview(self):
        first = preview_crm_envelope(LEAD)
        first["transmitted"] = True
        first["provider_record_id"] = "FORGED"
        second = preview_crm_envelope(LEAD)
        self.assertIs(second["transmitted"], False)
        self.assertIsNone(second["provider_record_id"])
        self.assertEqual(LEAD["status"], "received")

    def test_preview_does_not_open_network_connections(self):
        with patch("socket.create_connection", side_effect=AssertionError("network attempted")), \
             patch("socket.socket.connect", side_effect=AssertionError("network attempted")):
            result = preview_crm_envelope(LEAD)
        self.assertIs(result["transmitted"], False)


if __name__ == "__main__":
    unittest.main()
