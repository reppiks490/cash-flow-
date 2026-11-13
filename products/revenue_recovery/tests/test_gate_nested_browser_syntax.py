"""QA negative control: nested browser syntax must be checked before a green gate.

This test uses only temporary synthetic files and mocked subprocess execution.
"""
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import integration_gate as gate


class NestedBrowserSyntaxGate(unittest.TestCase):
    def test_nested_invalid_js_cannot_escape_syntax_stage(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "backend").mkdir()
            (root / "backend" / "app.py").write_text("# synthetic\n")
            web = root / "web"
            (web / "modules").mkdir(parents=True)
            (web / "app.js").write_text("// synthetic entrypoint\n")
            (web / "modules" / "invalid.js").write_text("function ( {\n")
            (web / "top.test.cjs").write_text("// synthetic test\n")
            (root / "test_synthetic.py").write_text(
                "import unittest\nclass Smoke(unittest.TestCase):\n"
                "    def test_ok(self): self.assertTrue(True)\n"
            )
            observed = []

            def fake_run(argv, env, timeout=gate.COMMAND_TIMEOUT_SECONDS):
                observed.append(argv)
                if len(argv) >= 3 and argv[0] == "node" and argv[1] == "--check":
                    if Path(argv[2]).name == "invalid.js":
                        return 1  # deterministic simulated Node syntax rejection
                return 0

            with patch.object(gate, "ROOT", root), patch.object(
                gate.shutil, "which", return_value="node"
            ), patch.object(gate, "run_bounded", side_effect=fake_run):
                result = gate.main()

            self.assertEqual(result, 1, "Nested invalid browser module must fail the gate")
            self.assertTrue(
                any(argv[:2] == ["node", "--check"] and Path(argv[2]).name == "invalid.js"
                    for argv in observed),
                "Gate must syntax-check nested .js sources, not only web/*.js",
            )
            self.assertFalse(
                any(argv[:2] == ["node", "--test"] for argv in observed),
                "Invalid browser syntax must block the interaction-test stage",
            )


if __name__ == "__main__":
    unittest.main()
