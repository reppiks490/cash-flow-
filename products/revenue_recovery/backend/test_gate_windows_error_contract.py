"""Cross-platform simulated Windows cleanup failures for the synthetic integration gate.

No Windows OS claims: these tests exercise the Windows branch with mocks on Linux.
"""
import importlib.util
from pathlib import Path
import subprocess
import types
import unittest
from unittest.mock import Mock, patch

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location("rre_gate_windows_errors", ROOT / "integration_gate.py")
gate = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(gate)


class WindowsCleanupErrorContracts(unittest.TestCase):
    def _exercise(self, side_effect, expected_message):
        child = Mock()
        child.pid = 76543
        child.wait.side_effect = [subprocess.TimeoutExpired(["python"], 0.1), 0]
        child.poll.return_value = None
        with patch.object(gate, "os", types.SimpleNamespace(name="nt")), \
             patch.object(gate.subprocess, "CREATE_NEW_PROCESS_GROUP", 0x200, create=True), \
             patch.object(gate.subprocess, "Popen", return_value=child) as popen, \
             patch.object(gate.subprocess, "run", side_effect=side_effect) as taskkill:
            with self.assertRaisesRegex(RuntimeError, expected_message):
                gate.run_bounded(["python"], {}, timeout=0.1)
        self.assertEqual(popen.call_args.kwargs["creationflags"], 0x200)
        self.assertEqual(taskkill.call_args.args[0], ["taskkill", "/PID", "76543", "/T", "/F"])
        self.assertEqual(taskkill.call_args.kwargs["timeout"], 15)
        child.kill.assert_called_once()
        self.assertEqual(child.wait.call_count, 2)

    def test_taskkill_spawn_failure_fails_closed_and_reaps(self):
        self._exercise(OSError("taskkill missing"), "process-tree cleanup failed")

    def test_taskkill_timeout_fails_closed_and_reaps(self):
        self._exercise(subprocess.TimeoutExpired(["taskkill"], 15), "process-tree cleanup failed")


if __name__ == "__main__":
    unittest.main()
