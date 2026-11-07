"""Synthetic demo evidence gate regressions (stdlib only)."""
import unittest
from .demo_evidence_gate import CHECKS, evaluate_demo_evidence

HEAD = "a" * 40


def record(status="PASS"):
    return {
        "synthetic": True,
        "commit": HEAD,
        "checks": {
            key: {"status": status, "evidence_commit": HEAD if status == "PASS" else None}
            for key in CHECKS
        },
    }


class DemoEvidenceGateTests(unittest.TestCase):
    def test_complete_synthetic_pass_is_not_pilot_approval(self):
        result = evaluate_demo_evidence(record())
        self.assertEqual(result["internal_rehearsal"], "PASS")
        self.assertIs(result["production_pilot_authorized"], False)
        self.assertIsNone(result["verified_net_profit_cents"])

    def test_not_run_is_no_go(self):
        result = evaluate_demo_evidence(record("NOT_RUN"))
        self.assertEqual(result["internal_rehearsal"], "NO_GO")
        self.assertEqual(len(result["not_run_checks"]), len(CHECKS))

    def test_fail_is_no_go(self):
        result = evaluate_demo_evidence(record("FAIL"))
        self.assertEqual(result["failed_checks"], CHECKS)

    def test_missing_check_rejected(self):
        r = record()
        del r["checks"]["draft_unsent"]
        with self.assertRaises(ValueError):
            evaluate_demo_evidence(r)

    def test_unexpected_fields_and_pii_rejected(self):
        r = record()
        r["customer_email"] = "synthetic@example.invalid"
        with self.assertRaises(ValueError):
            evaluate_demo_evidence(r)

    def test_false_synthetic_rejected(self):
        r = record()
        r["synthetic"] = False
        with self.assertRaises(ValueError):
            evaluate_demo_evidence(r)

    def test_wrong_head_evidence_rejected(self):
        r = record()
        r["checks"]["draft_unsent"]["evidence_commit"] = "b" * 40
        with self.assertRaises(ValueError):
            evaluate_demo_evidence(r)

    def test_nonpass_cannot_claim_evidence(self):
        r = record("NOT_RUN")
        r["checks"]["intake_dedupe"]["evidence_commit"] = HEAD
        with self.assertRaises(ValueError):
            evaluate_demo_evidence(r)

    def test_invalid_sha_rejected(self):
        r = record()
        r["commit"] = "main"
        with self.assertRaises(ValueError):
            evaluate_demo_evidence(r)


if __name__ == "__main__":
    unittest.main()
