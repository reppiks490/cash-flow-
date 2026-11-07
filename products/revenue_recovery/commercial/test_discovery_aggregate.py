"""No-network regression checks for synthetic discovery guard."""
import unittest

from products.revenue_recovery.commercial.discovery_aggregate import (
    FIELDS, summarize_synthetic, validate_synthetic_record,
)


def fixture():
    return {name: sorted(values)[0] for name, values in FIELDS.items()}


class DiscoveryAggregateTests(unittest.TestCase):
    def test_empty_is_not_buyer_validation(self):
        result = summarize_synthetic([])
        self.assertEqual(result["sample_size"], 0)
        self.assertFalse(result["research_validated"])
        self.assertEqual(result["verified_net_profit_usd"], 0)

    def test_synthetic_count_only(self):
        record = fixture()
        record["unresolved_gap"] = "quote_followup"
        record["700_usd_willingness"] = "consider"
        result = summarize_synthetic([record, record.copy()])
        self.assertEqual(result["gap_counts"]["quote_followup"], 2)
        self.assertEqual(result["willingness_counts"]["consider"], 2)
        self.assertEqual(result["verified_customers"], 0)

    def test_reject_identifier_or_extra_field(self):
        record = fixture()
        record["email"] = "synthetic@example.invalid"
        with self.assertRaises(ValueError):
            validate_synthetic_record(record)

    def test_reject_real_research_even_if_claimed_approved(self):
        record = fixture()
        record["record_class"] = "authorized_research"
        record["authorization_state"] = "private_approval_verified"
        with self.assertRaises(ValueError):
            summarize_synthetic([record])

    def test_reject_missing_or_unexpected_values(self):
        record = fixture()
        del record["blocking_reason"]
        with self.assertRaises(ValueError):
            validate_synthetic_record(record)
        record = fixture()
        record["buyer_segment"] = "Big Contractor LLC"
        with self.assertRaises(ValueError):
            validate_synthetic_record(record)

    def test_reject_nonstring_and_unbounded_inputs(self):
        record = fixture()
        record["700_usd_willingness"] = True
        with self.assertRaises(ValueError):
            validate_synthetic_record(record)
        with self.assertRaises(ValueError):
            summarize_synthetic([fixture()] * 1001)
        with self.assertRaises(ValueError):
            summarize_synthetic("not records")


if __name__ == "__main__":
    unittest.main()
