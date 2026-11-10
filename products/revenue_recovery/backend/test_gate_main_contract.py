"""Fail-closed main() orchestration contracts for the local synthetic gate.

No child process, external service, customer data, or network access is used.
Tests deliberately mock the public run_bounded boundary, not subprocess.run.
"""
import subprocess
import unittest
from unittest.mock import patch

import integration_gate as gate


class GateMainContractTests(unittest.TestCase):
    def test_first_timeout_returns_two_and_stops(self):
        timeout = subprocess.TimeoutExpired(cmd=["synthetic-test"], timeout=gate.COMMAND_TIMEOUT_SECONDS)
        with patch.object(gate.shutil, "which", return_value="node"), patch.object(
            gate, "run_bounded", side_effect=timeout
        ) as runner:
            self.assertEqual(gate.main(), 2)
        runner.assert_called_once()
        self.assertEqual(runner.call_args.args[2], gate.COMMAND_TIMEOUT_SECONDS)

    def test_success_runs_all_discovered_commands_with_bounded_timeout(self):
        with patch.object(gate.shutil, "which", return_value="node"), patch.object(
            gate, "run_bounded", return_value=0
        ) as runner:
            self.assertEqual(gate.main(), 0)
        self.assertGreater(runner.call_count, 1)
        for call in runner.call_args_list:
            self.assertEqual(call.args[2], gate.COMMAND_TIMEOUT_SECONDS)
            self.assertGreater(call.args[2], 0)

    def test_nonzero_exit_stops_before_next_command(self):
        with patch.object(gate.shutil, "which", return_value="node"), patch.object(
            gate, "run_bounded", return_value=17
        ) as runner:
            self.assertEqual(gate.main(), 1)
        runner.assert_called_once()

    def test_spawn_failure_fails_closed(self):
        with patch.object(gate.shutil, "which", return_value="node"), patch.object(
            gate, "run_bounded", side_effect=OSError("synthetic spawn failure")
        ) as runner:
            self.assertEqual(gate.main(), 2)
        runner.assert_called_once()


if __name__ == "__main__":
    unittest.main()
