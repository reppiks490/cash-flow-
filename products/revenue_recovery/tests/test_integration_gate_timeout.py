"""Fail-closed timeout regression for the synthetic local integration gate.

Only subprocess mocks are used; no vendors, customer data or network calls.
"""
import importlib.util
from pathlib import Path
import subprocess
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location("rre_gate_timeout_under_test", ROOT / "integration_gate.py")
gate = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(gate)


class IntegrationGateTimeoutTests(unittest.TestCase):
    def test_first_timed_out_command_fails_closed_and_stops(self):
        timeout = subprocess.TimeoutExpired(cmd=["synthetic-test"], timeout=gate.COMMAND_TIMEOUT_SECONDS)
        with patch.object(gate.shutil, "which", return_value="/usr/bin/node"), patch.object(
            gate.subprocess, "run", side_effect=timeout
        ) as runner:
            self.assertEqual(gate.main(), 2)
            self.assertEqual(runner.call_count, 1)
            self.assertEqual(runner.call_args.kwargs["timeout"], gate.COMMAND_TIMEOUT_SECONDS)
            self.assertGreater(gate.COMMAND_TIMEOUT_SECONDS, 0)

    def test_successful_command_is_also_bounded(self):
        with patch.object(gate.shutil, "which", return_value="/usr/bin/node"), patch.object(
            gate.subprocess, "run", return_value=subprocess.CompletedProcess([], 0)
        ) as runner:
            self.assertEqual(gate.main(), 0)
            self.assertGreater(runner.call_count, 1)
            for call in runner.call_args_list:
                self.assertEqual(call.kwargs["timeout"], gate.COMMAND_TIMEOUT_SECONDS)


if __name__ == "__main__":
    unittest.main()
