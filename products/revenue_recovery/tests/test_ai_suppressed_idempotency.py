"""Regression: suppressed draft replay keys must identify distinct objection variants."""
import unittest
from backend.followups import prepare_followup


LEAD = {
    "synthetic": True,
    "external_ref": "DEMO-OBJECTION-01",
    "source": "website",
    "need": "repair",
    "status": "received",
}


class SuppressedDraftIdempotencyTests(unittest.TestCase):
    def test_distinct_suppressed_objections_have_distinct_keys(self):
        variants = [None, "price", "timing", "competitor"]
        drafts = [prepare_followup(LEAD, opted_out=True, objection=value)
                  for value in variants]
        self.assertEqual(len({item["idempotency_key"] for item in drafts}), len(variants))
        for item in drafts:
            self.assertEqual(item["status"], "suppressed")
            self.assertIsNone(item["draft"])
            self.assertFalse(item["sent"])
            self.assertFalse(item["send_enabled"])

    def test_replay_is_stable(self):
        first = prepare_followup(LEAD, opted_out=True, objection="price")
        second = prepare_followup(dict(LEAD), opted_out=True, objection="price")
        self.assertEqual(first, second)


if __name__ == "__main__":
    unittest.main()
