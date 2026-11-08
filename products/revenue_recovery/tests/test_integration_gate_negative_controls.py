"""Negative controls for the local-only RRE regression runner (PR #172).

No customer records, vendor integrations, network access, or paid services.
"""
import importlib.util
from pathlib import Path
import subprocess
import unittest
from unittest.mock import patch


ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location("rre_integration_gate", ROOT / "integration_gate.py")
gate = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(gate)


class IntegrationGateNegativeControls(unittest.TestCase):
    def test_missing_node_fails_closed_before_any_child_process(self):
        with patch.object(gate.shutil, "which", return_value=None), patch.object(
            gate.subprocess, "run"
        ) as runner:
            self.assertEqual(gate.main(), 2)
            runner.assert_not_called()

    def test_first_failed_command_stops_runner(self):
        with patch.object(gate.shutil, "which", return_value="/usr/bin/node"), patch.object(
            gate.subprocess, "run", return_value=subprocess.CompletedProcess([], 17)
        ) as runner:
            self.assertEqual(gate.main(), 1)
            self.assertEqual(runner.call_count, 1)
            self.assertIn("unittest", runner.call_args.args[0])

    def test_os_error_fails_closed(self):
        with patch.object(gate.shutil, "which", return_value="/usr/bin/node"), patch.object(
            gate.subprocess, "run", side_effect=OSError("synthetic runner failure")
        ) as runner:
            self.assertEqual(gate.main(), 2)
            self.assertEqual(runner.call_count, 1)


if __name__ == "__main__":
    unittest.main()
