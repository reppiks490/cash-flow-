"""CI-discoverable, real-process POSIX timeout containment regression.

Runs only local Python subprocesses; no network, credentials or customer data.
"""
from __future__ import annotations

import os
from pathlib import Path
import subprocess
import sys
import unittest


ROOT = Path(__file__).resolve().parent


@unittest.skipIf(os.name == "nt", "POSIX process-group check; Windows requires native validation")
class ProcessTreeContainmentTest(unittest.TestCase):
    def test_real_child_and_grandchild_terminated_on_timeout(self) -> None:
        result = subprocess.run(
            [sys.executable, str(ROOT / "process_tree_negative_control.py")],
            cwd=ROOT,
            capture_output=True,
            text=True,
            timeout=25,
            check=False,
        )
        self.assertEqual(
            result.returncode,
            0,
            f"negative control failed (exit {result.returncode}):\n"
            f"stdout={result.stdout}\nstderr={result.stderr}",
        )
        self.assertIn("PASS: child and grandchild exited after real timeout", result.stdout)
        self.assertIn("PASS: nonzero exit propagated", result.stdout)


if __name__ == "__main__":
    unittest.main()
