"""Ensure browser synthetic-only safety gate runs under RRE Python CI."""
from pathlib import Path
import subprocess
import unittest


class BrowserSyntheticGateTests(unittest.TestCase):
    def test_node_synthetic_gate(self):
        suite = Path(__file__).with_name("synthetic_gate.test.cjs")
        self.assertTrue(suite.is_file(), "Synthetic browser gate suite missing")
        try:
            result = subprocess.run(
                ["node", "--test", str(suite)],
                cwd=suite.parent,
                text=True, capture_output=True,
                timeout=20, check=False,
            )
        except (OSError, subprocess.TimeoutExpired) as exc:
            self.fail(f"Node.js synthetic browser gate unavailable: {exc}")
        self.assertEqual(
            result.returncode, 0,
            "Node synthetic browser gate failed:\n" + result.stdout + "\n" + result.stderr,
        )


if __name__ == "__main__":
    unittest.main()
