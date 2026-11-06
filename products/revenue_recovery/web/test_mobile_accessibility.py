"""Execute Node keyboard/mobile static checks within existing product CI."""
from pathlib import Path
import subprocess
import unittest


class MobileAccessibilityContractTests(unittest.TestCase):
    def test_node_static_keyboard_contract(self):
        suite = Path(__file__).with_name("mobile_accessibility.test.cjs")
        self.assertTrue(suite.is_file(), "Mobile accessibility contract missing")
        try:
            run = subprocess.run(
                ["node", "--test", str(suite)], cwd=suite.parent,
                capture_output=True, text=True, timeout=20, check=False,
            )
        except (OSError, subprocess.TimeoutExpired) as exc:
            self.fail(f"Node accessibility suite unavailable: {exc}")
        self.assertEqual(run.returncode, 0,
                         "Node accessibility tests failed:\n" + run.stdout + "\n" + run.stderr)


if __name__ == "__main__":
    unittest.main()
