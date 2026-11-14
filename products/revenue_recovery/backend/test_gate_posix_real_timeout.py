"""Real POSIX timeout regression for the synthetic local integration gate.

No vendors, network calls, PII or external services. Windows is tested separately.
"""
import importlib.util
import os
from pathlib import Path
import signal
import subprocess
import sys
import tempfile
import time
import unittest

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location("rre_gate_posix_timeout", ROOT / "integration_gate.py")
gate = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(gate)


@unittest.skipUnless(os.name == "posix", "POSIX process groups required")
class RealPosixTimeout(unittest.TestCase):
    def test_hung_parent_and_descendant_are_terminated(self):
        with tempfile.TemporaryDirectory() as temp:
            pid_file = Path(temp) / "child.pid"
            parent_script = (
                "import pathlib,subprocess,sys,time\n"
                "child=subprocess.Popen([sys.executable,'-c','import time; time.sleep(120)'])\n"
                "pathlib.Path(sys.argv[1]).write_text(str(child.pid))\n"
                "time.sleep(120)\n"
            )
            # Give the parent time to spawn and record its descendant before timing out.
            # A failure to spawn is a test failure, not an acceptable timeout result.
            with self.assertRaises(subprocess.TimeoutExpired):
                gate.run_bounded([sys.executable, "-c", parent_script, str(pid_file)],
                                 os.environ.copy(), timeout=2)
            self.assertTrue(pid_file.exists(), "parent never recorded its descendant")
            child_pid = int(pid_file.read_text())
            # A killed descendant can briefly remain a zombie until init reaps it.
            # /proc status (Linux only) distinguishes zombie from running processes.
            if sys.platform.startswith("linux"):
                deadline = time.monotonic() + 3
                while time.monotonic() < deadline:
                    status = Path(f"/proc/{child_pid}/status")
                    if not status.exists() or "\nState:\tZ" in "\n" + status.read_text():
                        break
                    time.sleep(0.05)
                else:
                    self.fail(f"descendant {child_pid} still running after timeout cleanup")


if __name__ == "__main__":
    unittest.main()
