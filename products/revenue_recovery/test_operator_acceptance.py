"""Exercise the local synthetic HTTP acceptance in normal and optimized Python.

No vendors, customer records, outreach, or production operations.
"""
from __future__ import annotations

import os
from pathlib import Path
import subprocess
import sys
import unittest

from backend.operator_acceptance import run_acceptance


PROJECT_ROOT = Path(__file__).resolve().parent


class OperatorHTTPAcceptanceTests(unittest.TestCase):
    def test_local_synthetic_http_workflow(self) -> None:
        run_acceptance()

    def test_optimized_python_executes_full_http_acceptance(self) -> None:
        env = os.environ.copy()
        env["PYTHONPATH"] = str(PROJECT_ROOT)
        result = subprocess.run(
            [sys.executable, "-O", "-m", "backend.operator_acceptance"],
            cwd=PROJECT_ROOT,
            env=env,
            capture_output=True,
            text=True,
            timeout=35,
            check=False,
        )
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("PASS: local synthetic HTTP operator acceptance", result.stdout)

    def test_optimized_python_negative_control_fails_closed(self) -> None:
        env = os.environ.copy()
        env["PYTHONPATH"] = str(PROJECT_ROOT)
        result = subprocess.run(
            [sys.executable, "-O", "-c",
             "from backend.operator_acceptance import require; require(False, 'negative-control')"],
            cwd=PROJECT_ROOT,
            env=env,
            capture_output=True,
            text=True,
            timeout=10,
            check=False,
        )
        self.assertNotEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("Operator acceptance failed: negative-control", result.stderr)


if __name__ == "__main__":
    unittest.main()
