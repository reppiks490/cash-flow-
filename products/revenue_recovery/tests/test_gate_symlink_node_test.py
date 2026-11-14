"""Negative control: linked Node regression files must not be silently omitted.

Synthetic local-only fixture. Expected RED until the integration gate rejects
symlinked .test.cjs candidates before invoking subprocesses.
"""
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import integration_gate as gate


class SymlinkedNodeTestGate(unittest.TestCase):
    def test_symlinked_node_test_rejected_even_with_valid_test_present(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "backend").mkdir()
            (root / "backend" / "app.py").write_text("# synthetic\n")
            web = root / "web"
            web.mkdir()
            (web / "app.js").write_text("// synthetic\n")
            (web / "valid.test.cjs").write_text("// synthetic test\n")
            (root / "test_smoke.py").write_text(
                "import unittest\nclass Smoke(unittest.TestCase):\n"
                "    def test_ok(self): self.assertTrue(True)\n"
            )
            target = web / "test_fixture.txt"
            target.write_text("synthetic\n")
            linked = web / "omitted.test.cjs"
            try:
                linked.symlink_to(target)
            except (OSError, NotImplementedError) as exc:
                self.skipTest(f"symlink creation unavailable: {exc}")

            commands = []
            def fake_run(argv, env, timeout=gate.COMMAND_TIMEOUT_SECONDS):
                commands.append(argv)
                return 0

            with patch.object(gate, "ROOT", root), patch.object(
                gate.shutil, "which", return_value="node"
            ), patch.object(gate, "run_bounded", side_effect=fake_run):
                status = gate.main()

            self.assertEqual(status, 2, "Linked Node test must fail closed")
            self.assertEqual(commands, [], "Reject before executing any tests")


if __name__ == "__main__":
    unittest.main()
