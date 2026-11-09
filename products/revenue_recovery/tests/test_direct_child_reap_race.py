"""Deterministic subprocess timeout/reap race controls (synthetic-only, no network)."""
import os
import subprocess
import unittest
from unittest.mock import Mock, patch

from integration_gate import run_bounded


@unittest.skipIf(os.name == "nt", "POSIX process-group control; Windows requires native tests")
class DirectChildReapRaceTests(unittest.TestCase):
    def _process(self, kill_error):
        process = Mock()
        process.pid = 87654
        process.wait.side_effect = [subprocess.TimeoutExpired(["synthetic"], 1), 0]
        process.poll.return_value = None
        process.kill.side_effect = kill_error
        return process

    def test_exited_between_poll_and_kill_is_reaped_and_timeout_propagates(self):
        process = self._process(ProcessLookupError("already exited"))
        with patch("integration_gate.subprocess.Popen", return_value=process), \
             patch("integration_gate.os.killpg") as killpg:
            with self.assertRaises(subprocess.TimeoutExpired):
                run_bounded(["synthetic"], {}, timeout=1)
        killpg.assert_called_once()
        process.kill.assert_called_once()
        self.assertEqual(process.wait.call_count, 2)

    def test_unexpected_direct_kill_failure_fails_closed_after_reap(self):
        process = self._process(PermissionError("denied"))
        with patch("integration_gate.subprocess.Popen", return_value=process), \
             patch("integration_gate.os.killpg"):
            with self.assertRaisesRegex(RuntimeError, "direct process kill failed"):
                run_bounded(["synthetic"], {}, timeout=1)
        process.kill.assert_called_once()
        self.assertEqual(process.wait.call_count, 2)


if __name__ == "__main__":
    unittest.main()
