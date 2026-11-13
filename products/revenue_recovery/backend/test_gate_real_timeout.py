"""Real local timeout negative control for the synthetic integration gate.

Uses only a sleeping Python child; no network, customer records or vendors.
Windows process-tree containment still requires independent native validation.
"""
import os
import subprocess
import sys
import time
import unittest

from integration_gate import run_bounded


class RealTimeoutNegativeControl(unittest.TestCase):
    @unittest.skipIf(os.name == "nt", "Windows process-tree containment requires native QA")
    def test_hung_local_child_is_bounded_and_reaped(self):
        started = time.monotonic()
        with self.assertRaises(subprocess.TimeoutExpired):
            run_bounded(
                [sys.executable, "-c", "import time; time.sleep(30)"],
                os.environ.copy(),
                timeout=0.2,
            )
        self.assertLess(
            time.monotonic() - started, 8,
            "timeout cleanup must not wait for the sleeping child to finish",
        )


if __name__ == "__main__":
    unittest.main()
