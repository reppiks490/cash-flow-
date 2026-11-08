import unittest

try:
    from .pilot_gate import _REQUIRED, assess_pilot_controls
except ImportError:
    from pilot_gate import _REQUIRED, assess_pilot_controls


class PilotGateTests(unittest.TestCase):
    def test_empty_controls_fail_closed(self):
        result = assess_pilot_controls({k: False for k in _REQUIRED})
        self.assertFalse(result.eligible_for_live_pilot)
        self.assertEqual(len(result.missing_controls), len(_REQUIRED))

    def test_all_self_attested_still_not_authorized(self):
        result = assess_pilot_controls({k: True for k in _REQUIRED})
        self.assertEqual(result.classification, "unverified_self_attestation")
        self.assertFalse(result.eligible_for_live_pilot)
        self.assertEqual(result.missing_controls, ())

    def test_reject_extra_personal_data(self):
        with self.assertRaises(ValueError):
            assess_pilot_controls({**{k: False for k in _REQUIRED}, "email": "person@example.test"})

    def test_reject_missing_fields(self):
        with self.assertRaises(ValueError):
            assess_pilot_controls({})

    def test_reject_truthy_non_boolean(self):
        for value in (1, "true", None, [], {}):
            with self.subTest(value=value):
                payload = {k: True for k in _REQUIRED}
                payload["qa_signoff"] = value
                with self.assertRaises(ValueError):
                    assess_pilot_controls(payload)


if __name__ == "__main__":
    unittest.main()
