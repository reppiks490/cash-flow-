"""Native Windows process-tree timeout acceptance (no mocks or external services).

This test must run on a real Windows host; Linux CI will report a skip, not a pass.
"""
import csv
import importlib.util
import io
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import time
import unittest

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location("rre_gate_windows_native", ROOT / "integration_gate.py")
gate = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(gate)


def pid_is_running(pid):
    """Use Windows' native process inventory; fail if inspection itself fails."""
    result = subprocess.run(
        ["tasklist", "/FI", f"PID eq {pid}", "/FO", "CSV", "/NH"],
        capture_output=True, text=True, timeout=10, check=True,
    )
    for row in csv.reader(io.StringIO(result.stdout)):
        if len(row) >= 2 and row[1].strip().isdigit() and int(row[1]) == pid:
            return True
    return False


@unittest.skipUnless(sys.platform == "win32", "requires native Windows taskkill/tasklist")
class NativeWindowsTreeTimeout(unittest.TestCase):
    def test_timeout_terminates_parent_and_grandchild(self):
        with tempfile.TemporaryDirectory() as temp:
            parent_pid_file = Path(temp) / "parent.pid"
            child_pid_file = Path(temp) / "child.pid"
            parent_script = (
                "import os,pathlib,subprocess,sys,time\n"
                "pathlib.Path(sys.argv[1]).write_text(str(os.getpid()))\n"
                "child=subprocess.Popen([sys.executable,'-c','import time; time.sleep(120)'])\n"
                "pathlib.Path(sys.argv[2]).write_text(str(child.pid))\n"
                "time.sleep(120)\n"
            )
            with self.assertRaises(subprocess.TimeoutExpired):
                gate.run_bounded(
                    [sys.executable, "-c", parent_script, str(parent_pid_file), str(child_pid_file)],
                    os.environ.copy(), timeout=3,
                )
            self.assertTrue(parent_pid_file.exists(), "parent PID was never recorded")
            self.assertTrue(child_pid_file.exists(), "grandchild PID was never recorded")
            pids = [int(parent_pid_file.read_text()), int(child_pid_file.read_text())]
            self.assertEqual(len(set(pids)), 2)
            deadline = time.monotonic() + 5
            while time.monotonic() < deadline:
                if not any(pid_is_running(pid) for pid in pids):
                    break
                time.sleep(0.1)
            self.assertFalse(pid_is_running(pids[0]), "parent survived timeout cleanup")
            self.assertFalse(pid_is_running(pids[1]), "grandchild survived timeout cleanup")


if __name__ == "__main__":
    unittest.main()
