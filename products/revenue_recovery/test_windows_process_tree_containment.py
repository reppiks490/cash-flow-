"""Native Windows process-tree termination negative control for the local RRE gate.

This test runs only synthetic local Python children. It never sends messages,
opens a vendor connection, or exercises a production integration.
Windows-native CI execution is required before claiming this control passes.
"""
from __future__ import annotations

import ctypes
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import time
import unittest

from integration_gate import run_bounded


@unittest.skipUnless(os.name == "nt", "Windows-native process-tree control")
class WindowsProcessTreeContainmentTests(unittest.TestCase):
    def test_timeout_terminates_child_and_grandchild(self):
        with tempfile.TemporaryDirectory(prefix="rre_win_tree_") as directory:
            root = Path(directory)
            child_pid_file = root / "child.pid"
            grandchild_pid_file = root / "grandchild.pid"
            grandchild_code = (
                "import os,time,pathlib;"
                "pathlib.Path(os.environ['RRE_GRANDCHILD_PID']).write_text(str(os.getpid()));"
                "time.sleep(60)"
            )
            child_code = (
                "import os,sys,time,pathlib,subprocess;"
                "pathlib.Path(os.environ['RRE_CHILD_PID']).write_text(str(os.getpid()));"
                f"subprocess.Popen([sys.executable,'-c',{grandchild_code!r}]);"
                "time.sleep(60)"
            )
            env = dict(
                os.environ,
                RRE_CHILD_PID=str(child_pid_file),
                RRE_GRANDCHILD_PID=str(grandchild_pid_file),
            )
            with self.assertRaises(subprocess.TimeoutExpired):
                run_bounded([sys.executable, "-c", child_code], env, timeout=5)
            self.assertTrue(child_pid_file.is_file(), "child did not initialize")
            self.assertTrue(grandchild_pid_file.is_file(), "grandchild did not initialize")
            pids = [int(child_pid_file.read_text()), int(grandchild_pid_file.read_text())]

            kernel32 = ctypes.WinDLL("kernel32", use_last_error=True)
            kernel32.OpenProcess.argtypes = [ctypes.c_ulong, ctypes.c_int, ctypes.c_ulong]
            kernel32.OpenProcess.restype = ctypes.c_void_p
            kernel32.WaitForSingleObject.argtypes = [ctypes.c_void_p, ctypes.c_ulong]
            kernel32.WaitForSingleObject.restype = ctypes.c_ulong
            kernel32.CloseHandle.argtypes = [ctypes.c_void_p]
            kernel32.CloseHandle.restype = ctypes.c_int

            def exited(pid):
                # SYNCHRONIZE access allows waiting on a process handle.
                handle = kernel32.OpenProcess(0x00100000, 0, pid)
                if not handle:
                    # A vanished PID may be inaccessible; absence is not
                    # enough to prove termination, so fail closed.
                    raise AssertionError(
                        f"cannot inspect process {pid}; Windows error {ctypes.get_last_error()}"
                    )
                try:
                    result = kernel32.WaitForSingleObject(handle, 0)
                    if result == 0:  # WAIT_OBJECT_0: process has exited.
                        return True
                    if result == 0x102:  # WAIT_TIMEOUT: still running.
                        return False
                    raise AssertionError(f"unexpected process wait status {result} for {pid}")
                finally:
                    kernel32.CloseHandle(handle)

            for _ in range(30):
                if all(exited(pid) for pid in pids):
                    break
                time.sleep(0.1)
            self.assertTrue(all(exited(pid) for pid in pids), f"surviving process IDs: {pids}")

    def test_nonzero_exit_code_preserved(self):
        self.assertEqual(
            run_bounded(
                [sys.executable, "-c", "import sys;sys.exit(7)"],
                dict(os.environ),
                timeout=5,
            ),
            7,
        )


if __name__ == "__main__":
    unittest.main()
