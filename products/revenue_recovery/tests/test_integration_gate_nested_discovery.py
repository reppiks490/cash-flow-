"""Regression contract for recursive browser-test discovery (synthetic fixtures only).

Expected RED until principal-owned integration_gate.py discovers nested JS tests.
No network, providers, customer data, or external side effects.
"""
import importlib.util
import tempfile
import unittest
from pathlib import Path
from unittest import mock

GATE_PATH = Path(__file__).resolve().parents[1] / "integration_gate.py"
spec = importlib.util.spec_from_file_location("rre_integration_gate_nested_qa", GATE_PATH)
gate = importlib.util.module_from_spec(spec)
spec.loader.exec_module(gate)


class NestedBrowserDiscoveryTests(unittest.TestCase):
    def test_nested_js_regression_is_executed(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            (root / "backend").mkdir()
            (root / "backend" / "app.py").write_text("# synthetic\n", encoding="utf-8")
            web = root / "web"
            (web / "regressions").mkdir(parents=True)
            (web / "app.js").write_text("// synthetic browser entrypoint\n", encoding="utf-8")
            (web / "top.test.cjs").write_text("// synthetic top-level test\n", encoding="utf-8")
            nested = web / "regressions" / "nested.test.cjs"
            nested.write_text("// synthetic nested test\n", encoding="utf-8")
            calls = []
            def fake_runner(argv, env, timeout=gate.COMMAND_TIMEOUT_SECONDS):
                calls.append(tuple(map(str, argv)))
                return 0
            suite = unittest.TestSuite([unittest.FunctionTestCase(lambda: None)])
            with mock.patch.object(gate, "ROOT", root), \
                 mock.patch.object(gate, "REPO", root), \
                 mock.patch.object(gate.shutil, "which", return_value="/usr/bin/node"), \
                 mock.patch.object(gate.unittest.TestLoader, "discover", return_value=suite), \
                 mock.patch.object(gate, "run_bounded", side_effect=fake_runner):
                self.assertEqual(gate.main(), 0)
            node_tests = [argv for argv in calls if len(argv) >= 2 and argv[:2] == ("node", "--test")]
            self.assertEqual(len(node_tests), 1, "node --test must be invoked exactly once")
            self.assertIn(str(nested), node_tests[0],
                          "nested browser regression must not be silently skipped")

    def test_missing_app_entrypoint_fails_closed(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            (root / "backend").mkdir()
            (root / "backend" / "app.py").write_text("# synthetic\n", encoding="utf-8")
            (root / "web").mkdir()
            with mock.patch.object(gate, "ROOT", root), \
                 mock.patch.object(gate.shutil, "which", return_value="/usr/bin/node"), \
                 mock.patch.object(gate, "run_bounded") as runner:
                self.assertEqual(gate.main(), 2)
                runner.assert_not_called()


if __name__ == "__main__":
    unittest.main()
