"""Exercise out-of-order browser response regression via dependency-free Node VM."""
from pathlib import Path
import subprocess
import unittest


class ViewSelectionRaceTests(unittest.TestCase):
    def test_pending_read_only_responses_do_not_overwrite_newer_selection(self):
        suite = Path(__file__).with_name("view_races.test.cjs")
        self.assertTrue(suite.is_file(), "Browser response race suite missing")
        try:
            result = subprocess.run(
                ["node", "--test", str(suite)],
                cwd=suite.parent, capture_output=True, text=True,
                timeout=20, check=False,
            )
        except (OSError, subprocess.TimeoutExpired) as exc:
            self.fail(f"Node browser race suite unavailable: {exc}")
        self.assertEqual(result.returncode, 0,
                         "Browser race tests failed:\n" + result.stdout + "\n" + result.stderr)


if __name__ == "__main__":
    unittest.main()
