"""Synthetic-only stdlib regression tests; no outbound side effects."""
import unittest

from products.revenue_recovery.commercial.demo_trace_gate import (
    DemoEvidence, REQUIRED_STEPS, assess_demo_trace,
)


def trace(run_id="demo_1"):
    return [DemoEvidence(step, True, True, run_id) for step in REQUIRED_STEPS]


class DemoTraceGateTests(unittest.TestCase):
    def test_complete_trace_is_only_shape_valid(self):
        result = assess_demo_trace(trace())
        self.assertTrue(result["synthetic_trace_shape_valid"])
        self.assertFalse(result["execution_independently_verified"])
        self.assertFalse(result["pilot_ready"])
        self.assertFalse(result["outreach_authorized"])
        self.assertFalse(result["billing_authorized"])
        self.assertIsNone(result["verified_revenue_cents"])

    def test_missing_duplicate_and_extra_steps_fail(self):
        for records in (trace()[:-1], trace() + trace()[:1], trace()[:-1] + trace()[:1]):
            with self.subTest(records=records):
                self.assertFalse(assess_demo_trace(records)["synthetic_trace_shape_valid"])

    def test_mixed_run_and_failed_step_fail(self):
        records = trace()
        records[-1] = DemoEvidence(records[-1].step, True, True, "other")
        self.assertFalse(assess_demo_trace(records)["synthetic_trace_shape_valid"])
        records = trace()
        records[0] = DemoEvidence(records[0].step, False, True, "demo_1")
        self.assertFalse(assess_demo_trace(records)["synthetic_trace_shape_valid"])

    def test_nonsynthetic_and_forged_boolean_fail(self):
        records = trace()
        records[0] = DemoEvidence(records[0].step, True, False, "demo_1")
        self.assertFalse(assess_demo_trace(records)["synthetic_trace_shape_valid"])
        records[0] = DemoEvidence(records[0].step, 1, True, "demo_1")
        with self.assertRaises(ValueError):
            assess_demo_trace(records)

    def test_invalid_types_and_run_ids_rejected(self):
        with self.assertRaises(ValueError):
            assess_demo_trace("fake")
        for bad in ("has spaces", "", "../unsafe", "é"):
            records = trace()
            records[0] = DemoEvidence(records[0].step, True, True, bad)
            with self.subTest(bad=bad), self.assertRaises(ValueError):
                assess_demo_trace(records)


if __name__ == "__main__":
    unittest.main()
