"""Regression tests for the current run_bounded-based local RRE gate.

Synthetic-only; no subprocesses, external services, customer data or deployment.
The earlier QA #183 tests target an obsolete subprocess.run orchestration API.
"""
import importlib.util
from pathlib import Path
import subprocess
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location("rre_gate_current_contract", ROOT / "integration_gate.py")
gate = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(gate)


class GateRunBoundedContractTests(unittest.TestCase):
    def _run(self, side_effect=None, return_value=0):
        # Keep genuine source discovery and prerequisites, but never execute commands.
        with patch.object(gate.shutil, "which", return_value="/usr/bin/node"), patch.object(
            gate, "run_bounded", side_effect=side_effect, return_value=return_value
        ) as runner:
            result = gate.main()
            return result, list(runner.call_args_list)

    def test_first_timeout_fails_closed_without_running_remaining_commands(self):
        timeout = subprocess.TimeoutExpired(cmd=["synthetic-test"], timeout=gate.COMMAND_TIMEOUT_SECONDS)
        result, calls = self._run(side_effect=timeout)
        self.assertEqual(result, 2)
        self.assertEqual(len(calls), 1)
        self.assertGreater(gate.COMMAND_TIMEOUT_SECONDS, 0)

    def test_success_runs_all_discovered_commands_through_bounded_runner(self):
        result, calls = self._run()
        self.assertEqual(result, 0)
        self.assertGreater(len(calls), 1)
        for call in calls:
            self.assertEqual(len(call.args), 2)
            self.assertIsInstance(call.args[0], list)
            self.assertIsInstance(call.args[1], dict)
            self.assertEqual(call.kwargs, {})

    def test_nonzero_command_stops_gate_before_following_commands(self):
        result, calls = self._run(return_value=7)
        self.assertEqual(result, 1)
        self.assertEqual(len(calls), 1)

    def test_process_cleanup_failure_is_not_reported_as_success(self):
        result, calls = self._run(side_effect=RuntimeError("synthetic process-tree cleanup failed"))
        self.assertEqual(result, 2)
        self.assertEqual(len(calls), 1)


if __name__ == "__main__":
    unittest.main()
