"""Adversarial structural-gate tests. Synthetic assertions are never proof of execution."""
import unittest

from products.revenue_recovery.commercial.demo_trace_gate import (
    DemoEvidence, REQUIRED_STEPS, assess_demo_trace,
)


class AdversarialDemoTraceTests(unittest.TestCase):
    def test_forged_all_pass_trace_is_not_execution_evidence(self):
        forged = [DemoEvidence(step, True, True, "forged_1") for step in REQUIRED_STEPS]
        result = assess_demo_trace(forged)
        self.assertTrue(result["synthetic_trace_shape_valid"])
        self.assertFalse(result["execution_independently_verified"])
        self.assertFalse(result["pilot_ready"])
        self.assertFalse(result["outreach_authorized"])
        self.assertFalse(result["billing_authorized"])
        self.assertIsNone(result["verified_revenue_cents"])

    def test_each_step_must_be_present(self):
        for omitted in REQUIRED_STEPS:
            with self.subTest(omitted=omitted):
                records = [DemoEvidence(s, True, True, "run_1")
                           for s in REQUIRED_STEPS if s != omitted]
                self.assertFalse(assess_demo_trace(records)["synthetic_trace_shape_valid"])

    def test_each_failed_or_nonsynthetic_step_rejected(self):
        for step in REQUIRED_STEPS:
            for passed, synthetic in ((False, True), (True, False)):
                with self.subTest(step=step, passed=passed, synthetic=synthetic):
                    records = [DemoEvidence(s, passed if s == step else True,
                                            synthetic if s == step else True, "run_1")
                               for s in REQUIRED_STEPS]
                    self.assertFalse(assess_demo_trace(records)["synthetic_trace_shape_valid"])

    def test_mixed_run_in_any_position_rejected(self):
        for step in REQUIRED_STEPS:
            with self.subTest(step=step):
                records = [DemoEvidence(s, True, True,
                                        "other" if s == step else "run_1")
                           for s in REQUIRED_STEPS]
                self.assertFalse(assess_demo_trace(records)["synthetic_trace_shape_valid"])

    def test_unknown_step_and_subclass_rejected(self):
        records = [DemoEvidence(s, True, True, "run_1") for s in REQUIRED_STEPS]
        records[0] = DemoEvidence("outbound_sent", True, True, "run_1")
        with self.assertRaises(ValueError):
            assess_demo_trace(records)

        class ForgedEvidence(DemoEvidence):
            pass

        records[0] = ForgedEvidence(REQUIRED_STEPS[0], True, True, "run_1")
        with self.assertRaises(ValueError):
            assess_demo_trace(records)


if __name__ == "__main__":
    unittest.main()
