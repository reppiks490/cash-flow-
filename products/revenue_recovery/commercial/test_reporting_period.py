"""Regression tests for synthetic reporting boundaries (stdlib only)."""
import unittest
from commercial.reporting_period import reporting_window


class ReportingPeriodTests(unittest.TestCase):
    def test_normal_chicago_day(self):
        window = reporting_window("2026-11-10", "2026-11-11", "America/Chicago")
        self.assertEqual(window["start_utc_inclusive"], "2026-11-10T06:00:00+00:00")
        self.assertEqual(window["end_utc_exclusive"], "2026-11-11T06:00:00+00:00")
        self.assertIn("not_revenue_evidence", window["classification"])

    def test_spring_forward_is_23_hours(self):
        window = reporting_window("2026-03-08", "2026-03-09", "America/Chicago")
        self.assertEqual(window["start_utc_inclusive"], "2026-03-08T06:00:00+00:00")
        self.assertEqual(window["end_utc_exclusive"], "2026-03-09T05:00:00+00:00")

    def test_fall_back_is_25_hours(self):
        window = reporting_window("2026-11-01", "2026-11-02", "America/Chicago")
        self.assertEqual(window["start_utc_inclusive"], "2026-11-01T05:00:00+00:00")
        self.assertEqual(window["end_utc_exclusive"], "2026-11-02T06:00:00+00:00")

    def test_reject_unsafe_dates_and_zones(self):
        invalid = [
            ("2026-02-30", "2026-03-01", "America/Chicago"),
            ("2026-11-10", "2026-11-10", "America/Chicago"),
            ("2026-11-11", "2026-11-10", "America/Chicago"),
            ("2026-01-01", "2027-01-03", "America/Chicago"),
            ("2026-11-10 ", "2026-11-11", "America/Chicago"),
            ("2026-11-10", "2026-11-11", "../etc/passwd"),
            ("2026-11-10", "2026-11-11", "Invalid/Nowhere"),
            ("2026-11-10", "2026-11-11", "UTC"),
            ("2026-11-10", "2026-11-11", None),
        ]
        for args in invalid:
            with self.subTest(args=args), self.assertRaises(ValueError):
                reporting_window(*args)


    def test_leap_day_and_maximum_interval(self):
        window = reporting_window("2024-02-29", "2024-03-01", "America/Chicago")
        self.assertEqual(window["start_utc_inclusive"], "2024-02-29T06:00:00+00:00")
        self.assertEqual(window["end_utc_exclusive"], "2024-03-01T06:00:00+00:00")
        maximum = reporting_window("2024-01-01", "2025-01-01", "America/Chicago")
        self.assertEqual(maximum["start_local_date"], "2024-01-01")
        self.assertEqual(maximum["end_local_date_exclusive"], "2025-01-01")

    def test_reject_nonstring_and_noncanonical_dates(self):
        invalid = [
            (20261110, "2026-11-11", "America/Chicago"),
            ("2026-11-10", ["2026-11-11"], "America/Chicago"),
            ("2026-11-10", "2026-11-11", 7),
            ("2026-1-10", "2026-11-11", "America/Chicago"),
            ("2026-11-10", "2026-11-11", "America/Chicago/../../etc"),
        ]
        for args in invalid:
            with self.subTest(args=args), self.assertRaises(ValueError):
                reporting_window(*args)

if __name__ == "__main__":
    unittest.main()
