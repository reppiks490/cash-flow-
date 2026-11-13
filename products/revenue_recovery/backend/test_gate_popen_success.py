"""Principal-owned Popen success-path contract for the local synthetic gate.

Run with PYTHONPATH=products/revenue_recovery:
python -m unittest backend.test_gate_popen_success -v
No real subprocesses, network calls, or customer data.
"""
import os
import unittest
from unittest.mock import Mock, patch

from integration_gate import run_bounded


class PopenSuccessContractTests(unittest.TestCase):
    def test_success_returns_exact_exit_code_and_propagates_timeout(self):
        process = Mock()
        process.wait.return_value = 0
        with patch("integration_gate.subprocess.Popen", return_value=process) as spawn:
            result = run_bounded(["python", "-V"], {"RRE_TEST": "1"}, timeout=7)
        self.assertEqual(result, 0)
        process.wait.assert_called_once_with(timeout=7)
        args, kwargs = spawn.call_args
        self.assertEqual(args[0], ["python", "-V"])
        self.assertEqual(kwargs["env"], {"RRE_TEST": "1"})
        self.assertIn("cwd", kwargs)
        if os.name == "nt":
            self.assertTrue(kwargs["creationflags"])
        else:
            self.assertIs(kwargs["start_new_session"], True)

    def test_nonzero_child_exit_is_not_rewritten_as_success(self):
        process = Mock()
        process.wait.return_value = 23
        with patch("integration_gate.subprocess.Popen", return_value=process):
            self.assertEqual(run_bounded(["synthetic-test"], {}, timeout=3), 23)
        process.wait.assert_called_once_with(timeout=3)

    def test_spawn_failure_propagates_without_fabricating_pass(self):
        with patch("integration_gate.subprocess.Popen", side_effect=OSError("spawn refused")):
            with self.assertRaisesRegex(OSError, "spawn refused"):
                run_bounded(["synthetic-test"], {}, timeout=3)


if __name__ == "__main__":
    unittest.main()
