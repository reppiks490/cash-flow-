"""Synthetic-only regression of the local gate's JavaScript test discovery.

No actual subprocess, network, customer records, or external provider is used.
This suite is stacked on principal PR #244; it does not certify production.
"""
import importlib.util
from pathlib import Path
import tempfile
import unittest
from unittest.mock import Mock, patch

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location("rre_js_discovery_gate", ROOT / "integration_gate.py")
gate = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(gate)


class JavaScriptGateDiscoveryTests(unittest.TestCase):
    def _fixture(self, directory, filenames):
        root = Path(directory)
        (root / "backend").mkdir()
        (root / "backend" / "app.py").write_text("# synthetic fixture\n")
        (root / "web").mkdir()
        (root / "web" / "dashboard.js").write_text("// synthetic source\n")
        for name in filenames:
            (root / "web" / name).write_text("// synthetic test\n")
        return root

    def _invoke(self, root):
        fake_suite = Mock()
        fake_suite.countTestCases.return_value = 1
        fake_loader = Mock()
        fake_loader.discover.return_value = fake_suite
        with patch.object(gate, "ROOT", root), patch.object(gate.shutil, "which", return_value="node"), \
             patch.object(gate.unittest, "TestLoader", return_value=fake_loader), \
             patch.object(gate, "run_bounded", return_value=0) as runner:
            result = gate.main()
        return result, runner.call_args_list

    def test_discovers_both_javascript_naming_conventions(self):
        with tempfile.TemporaryDirectory() as directory:
            root = self._fixture(directory, ["test_intake.js", "policy.test.js", "test_legacy.cjs"])
            result, calls = self._invoke(root)
        self.assertEqual(result, 0)
        node_commands = [call.args[0] for call in calls if call.args[0][:2] == ["node", "--test"]]
        self.assertEqual(len(node_commands), 1)
        self.assertEqual({Path(name).name for name in node_commands[0][2:]},
                         {"test_intake.js", "policy.test.js", "test_legacy.cjs"})

    def test_zero_javascript_tests_fails_closed_without_execution(self):
        with tempfile.TemporaryDirectory() as directory:
            root = self._fixture(directory, [])
            result, calls = self._invoke(root)
        self.assertEqual(result, 2)
        self.assertEqual(calls, [])

    def test_only_javascript_source_is_not_mistaken_for_a_test(self):
        with tempfile.TemporaryDirectory() as directory:
            root = self._fixture(directory, ["helper.js"])
            result, calls = self._invoke(root)
        self.assertEqual(result, 2)
        self.assertEqual(calls, [])


if __name__ == "__main__":
    unittest.main()
