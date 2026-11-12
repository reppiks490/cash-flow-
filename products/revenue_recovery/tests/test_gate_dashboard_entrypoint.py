"""Synthetic-only regression for the local dashboard entrypoint release gate.

No external commands are executed: runner and Node discovery are mocked.
"""
from __future__ import annotations

import importlib.util
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest import TestCase
from unittest.mock import patch


GATE_PATH = Path(__file__).resolve().parents[1] / "integration_gate.py"
SPEC = importlib.util.spec_from_file_location("rre_dashboard_gate_under_test", GATE_PATH)
assert SPEC is not None and SPEC.loader is not None
gate = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(gate)


class DashboardEntrypointGateTests(TestCase):
    def _tree(self, root: Path, dashboard: bool) -> None:
        (root / "backend").mkdir()
        (root / "backend" / "app.py").write_text("# synthetic stub\n", encoding="utf-8")
        web = root / "web"
        web.mkdir()
        (web / "test_smoke.cjs").write_text("/* synthetic test */\n", encoding="utf-8")
        (web / "helper.js").write_text("/* synthetic source */\n", encoding="utf-8")
        if dashboard:
            (web / "dashboard.js").write_text("/* synthetic entrypoint */\n", encoding="utf-8")

    def test_missing_dashboard_fails_closed_before_any_command(self):
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            self._tree(root, dashboard=False)
            with patch.object(gate, "ROOT", root), patch.object(
                gate.shutil, "which", return_value="/synthetic/node"
            ), patch.object(gate, "run_bounded") as runner, patch.object(
                gate.unittest.TestLoader, "discover"
            ) as discover:
                self.assertEqual(gate.main(), 2)
                runner.assert_not_called()
                discover.assert_not_called()

    def test_dashboard_present_executes_python_and_node_regressions(self):
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            self._tree(root, dashboard=True)
            with patch.object(gate, "ROOT", root), patch.object(
                gate.shutil, "which", return_value="/synthetic/node"
            ), patch.object(gate, "run_bounded", return_value=0) as runner, patch.object(
                gate.unittest.TestLoader, "discover"
            ) as discover:
                discover.return_value.countTestCases.return_value = 1
                self.assertEqual(gate.main(), 0)
                commands = [call.args[0] for call in runner.call_args_list]
                self.assertTrue(any(cmd[:2] == ["node", "--test"] for cmd in commands))
                self.assertTrue(any(cmd[:2] == ["node", "--check"] and cmd[-1].endswith("dashboard.js") for cmd in commands))
                self.assertTrue(any("-m" in cmd and "unittest" in cmd for cmd in commands))

    def test_missing_dashboard_does_not_depend_on_python_test_discovery(self):
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            self._tree(root, dashboard=False)
            with patch.object(gate, "ROOT", root), patch.object(
                gate.shutil, "which", return_value="/synthetic/node"
            ), patch.object(gate.unittest.TestLoader, "discover", side_effect=AssertionError(
                "discovery should never run"
            )), patch.object(gate, "run_bounded", side_effect=AssertionError(
                "runner should never run"
            )):
                self.assertEqual(gate.main(), 2)
