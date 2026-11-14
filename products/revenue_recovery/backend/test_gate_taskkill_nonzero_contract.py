"""Cross-platform mock contract for nonzero Windows process-tree cleanup.

Synthetic local test only. Does not establish native Windows containment.
"""
import importlib.util
from pathlib import Path
import subprocess
import types
import unittest
from unittest.mock import Mock, patch

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location("rre_gate_taskkill_nonzero", ROOT / "integration_gate.py")
gate = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(gate)


class TaskkillNonzeroContracts(unittest.TestCase):
    def test_nonzero_taskkill_fails_closed_and_reaps_direct_child(self):
        child = Mock()
        child.pid = 76543
        child.wait.side_effect = [subprocess.TimeoutExpired(["python"], 0.1), 0]
        child.poll.return_value = None
        with patch.object(gate, "os", types.SimpleNamespace(name="nt")), \
             patch.object(gate.subprocess, "CREATE_NEW_PROCESS_GROUP", 0x200, create=True), \
             patch.object(gate.subprocess, "Popen", return_value=child) as popen, \
             patch.object(gate.subprocess, "run", return_value=subprocess.CompletedProcess(["taskkill"], 5)) as taskkill:
            with self.assertRaisesRegex(RuntimeError, "taskkill failed: exit 5"):
                gate.run_bounded(["python"], {}, timeout=0.1)
        self.assertEqual(popen.call_args.kwargs["creationflags"], 0x200)
        self.assertEqual(taskkill.call_args.args[0], ["taskkill", "/PID", "76543", "/T", "/F"])
        self.assertEqual(taskkill.call_args.kwargs["timeout"], 15)
        child.kill.assert_called_once()
        self.assertEqual(child.wait.call_count, 2)


if __name__ == "__main__":
    unittest.main()
