"""Deterministic negative-case tests for the synthetic pilot checklist."""
import unittest

try:
    from .pilot_readiness import (
        REQUIRED_GATES, ReadinessError, assess_demo_pilot_readiness,
    )
except ImportError:
    from pilot_readiness import (
        REQUIRED_GATES, ReadinessError, assess_demo_pilot_readiness,
    )


def payload(value=False):
    return {"synthetic": True, "industry": "hvac", **{k: value for k in REQUIRED_GATES}}


class PilotReadinessTests(unittest.TestCase):
    def test_empty_checklist_fails_closed(self):
        result = assess_demo_pilot_readiness(payload())
        self.assertFalse(result["checklist_complete"])
        self.assertEqual(result["unmet_checklist_gates"], list(REQUIRED_GATES))
        self.assertFalse(result["pilot_authorized"])

    def test_all_true_never_authorizes(self):
        result = assess_demo_pilot_readiness(payload(True))
        self.assertTrue(result["checklist_complete"])
        self.assertFalse(result["independent_evidence_verified"])
        for field in ("pilot_authorized", "production_ready", "outreach_enabled",
                      "billing_enabled", "provider_connections_enabled"):
            self.assertIs(result[field], False)

    def test_unknown_fields_rejected(self):
        for extra in ({"email": "test@example.invalid"}, {"api_key": "secret"},
                      {"notes": "free text"}):
            with self.subTest(extra=extra):
                with self.assertRaises(ReadinessError):
                    assess_demo_pilot_readiness({**payload(), **extra})

    def test_missing_or_invalid_gates_rejected(self):
        for invalid in (1, 0, None, "true", [], {}):
            with self.subTest(invalid=invalid):
                p = payload()
                p[REQUIRED_GATES[0]] = invalid
                with self.assertRaises(ReadinessError):
                    assess_demo_pilot_readiness(p)
        p = payload()
        del p[REQUIRED_GATES[0]]
        with self.assertRaises(ReadinessError):
            assess_demo_pilot_readiness(p)

    def test_non_synthetic_or_wrong_industry_rejected(self):
        for changed in ({"synthetic": 1}, {"synthetic": False},
                        {"industry": "plumbing"}, {"industry": ["hvac"]}):
            with self.subTest(changed=changed):
                with self.assertRaises(ReadinessError):
                    assess_demo_pilot_readiness({**payload(), **changed})


if __name__ == "__main__":
    unittest.main()
