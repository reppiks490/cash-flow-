"""Deterministic direct-child timeout cleanup race contracts (synthetic tooling)."""
import subprocess
import unittest
from unittest.mock import Mock, patch

import integration_gate


class DirectChildReapRaceTests(unittest.TestCase):
    def _process(self, kill_error):
        process = Mock()
        process.pid = 43210
        process.wait.side_effect = [
            subprocess.TimeoutExpired(cmd=["synthetic-test"], timeout=1),
            0,
        ]
        process.poll.return_value = None
        process.kill.side_effect = kill_error
        return process

    def _exercise(self, process):
        with patch.object(integration_gate.subprocess, "Popen", return_value=process), \
             patch.object(integration_gate.os, "killpg", create=True) as killpg, \
             patch.object(integration_gate.os, "name", "posix"):
            try:
                integration_gate.run_bounded(["synthetic-test"], {}, timeout=1)
            finally:
                killpg.assert_called_once_with(process.pid, integration_gate.signal.SIGKILL)

    def test_child_exits_between_poll_and_kill(self):
        process = self._process(ProcessLookupError("already exited"))
        with self.assertRaises(subprocess.TimeoutExpired):
            self._exercise(process)
        process.kill.assert_called_once()
        self.assertEqual(process.wait.call_count, 2)

    def test_direct_kill_permission_error_fails_closed(self):
        process = self._process(PermissionError("denied"))
        with self.assertRaisesRegex(RuntimeError, "direct process kill failed"):
            self._exercise(process)
        process.kill.assert_called_once()
        self.assertEqual(process.wait.call_count, 2)


if __name__ == "__main__":
    unittest.main()
