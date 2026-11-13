"""Real subprocess acceptance for the synthetic-only RRE integration gate.

Unlike mocked discovery tests, this runs actual Python and Node child processes
against temporary fixtures. No network, customer records, or external services.
"""
from __future__ import annotations

import contextlib
import io
import shutil
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import integration_gate as gate


@unittest.skipUnless(shutil.which("node"), "Node.js required for real subprocess acceptance")
class RealSubprocessGateAcceptance(unittest.TestCase):
    def make_fixture(self, root: Path, malformed: bool = False) -> None:
        (root / "backend").mkdir()
        (root / "backend" / "app.py").write_text("# synthetic fixture\n", encoding="utf-8")
        # Give each temporary fixture a distinct import name: unittest caches modules.
        # Reusing test_smoke across directories makes later discovery fail.
        fixture_module = "test_smoke_" + "".join(
            char if char.isalnum() else "_" for char in root.name
        )
        (root / f"{fixture_module}.py").write_text(
            "import unittest\nclass Smoke(unittest.TestCase):\n"
            "    def test_synthetic(self): self.assertTrue(True)\n",
            encoding="utf-8",
        )
        web = root / "web"
        (web / "modules").mkdir(parents=True)
        (web / "app.js").write_text("const synthetic = true;\n", encoding="utf-8")
        (web / "modules" / "helper.mjs").write_text(
            "export const answer = ;\n" if malformed else "export const answer = 42;\n",
            encoding="utf-8",
        )
        (web / "modules" / "nested.test.cjs").write_text(
            "const test = require('node:test');\n"
            "const assert = require('node:assert/strict');\n"
            "test('synthetic', () => assert.equal(2 + 2, 4));\n",
            encoding="utf-8",
        )

    def run_fixture(self, root: Path) -> tuple[int, str]:
        output = io.StringIO()
        with patch.object(gate, "ROOT", root), contextlib.redirect_stdout(output):
            result = gate.main()  # Real run_bounded: no subprocess mock.
        return result, output.getvalue()

    def test_real_python_node_and_nested_syntax_pass(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.make_fixture(root)
            status, log = self.run_fixture(root)
            self.assertEqual(status, 0, log)
            self.assertIn("PASS: JavaScript interaction regressions", log)
            self.assertIn("PASS: local synthetic regression gate", log)

    def test_real_node_rejects_malformed_nested_module_before_interactions(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.make_fixture(root, malformed=True)
            status, log = self.run_fixture(root)
            self.assertEqual(status, 1, log)
            self.assertIn("FAIL: JavaScript syntax: helper.mjs", log)
            self.assertNotIn("RUN: JavaScript interaction regressions", log)

    def test_real_nested_node_failure_blocks_acceptance(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.make_fixture(root)
            (root / "web" / "modules" / "nested.test.cjs").write_text(
                "const test = require('node:test');\n"
                "test('synthetic negative', () => { throw Error('expected synthetic failure'); });\n",
                encoding="utf-8",
            )
            status, log = self.run_fixture(root)
            self.assertEqual(status, 1, log)
            self.assertIn("FAIL: JavaScript interaction regressions", log)
            self.assertNotIn("PASS: local synthetic regression gate", log)

    def test_missing_entrypoint_fails_closed_without_child_process(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.make_fixture(root)
            (root / "web" / "app.js").unlink()
            status, log = self.run_fixture(root)
            self.assertEqual(status, 2, log)
            self.assertIn("expected app.js browser entrypoint missing", log)


if __name__ == "__main__":
    unittest.main()
