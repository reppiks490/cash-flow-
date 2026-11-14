"""Mock-only Windows cleanup contract tests for the local synthetic gate.

These tests do not prove native Windows process-tree containment.
"""
import importlib.util
from pathlib import Path
import subprocess
import types
import unittest
from unittest.mock import Mock, patch

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location("rre_gate_windows_contract", ROOT / "integration_gate.py")
gate = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(gate)


class WindowsCleanupContractTests(unittest.TestCase):
    def _run_timeout(self, taskkill_code):
        child = Mock()
        child.pid = 43210
        child.wait.side_effect = [subprocess.TimeoutExpired(["python"], 0.1), 0]
        child.poll.return_value = None
        result = subprocess.CompletedProcess(["taskkill"], taskkill_code)
        fake_os = types.SimpleNamespace(name="nt")
        with patch.object(gate, "os", fake_os), patch.object(
            gate.subprocess, "Popen", return_value=child
        ) as popen, patch.object(
            gate.subprocess, "run", return_value=result
        ) as taskkill:
            if taskkill_code == 0:
                with self.assertRaises(subprocess.TimeoutExpired):
                    gate.run_bounded(["python"], {}, timeout=0.1)
            else:
                with self.assertRaisesRegex(RuntimeError, "taskkill failed"):
                    gate.run_bounded(["python"], {}, timeout=0.1)
        self.assertEqual(popen.call_args.kwargs["creationflags"], subprocess.CREATE_NEW_PROCESS_GROUP)
        self.assertEqual(taskkill.call_args.args[0], ["taskkill", "/PID", "43210", "/T", "/F"])
        self.assertEqual(taskkill.call_args.kwargs["timeout"], 15)
        child.kill.assert_called_once()
        self.assertEqual(child.wait.call_count, 2)

    @unittest.skipUnless(hasattr(subprocess, "CREATE_NEW_PROCESS_GROUP"), "Windows-only constant")
    def test_taskkill_success_still_reports_original_timeout(self):
        self._run_timeout(0)

    @unittest.skipUnless(hasattr(subprocess, "CREATE_NEW_PROCESS_GROUP"), "Windows-only constant")
    def test_taskkill_failure_fails_closed_and_reaps_direct_child(self):
        self._run_timeout(1)


if __name__ == "__main__":
    unittest.main()
