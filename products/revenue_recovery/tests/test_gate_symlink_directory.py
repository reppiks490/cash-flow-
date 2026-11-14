"""QA negative control: symlinked browser source directories must fail closed.

Only synthetic temporary files; no network, provider calls or customer records.
Symlink creation may require Windows developer mode/privileges: skip explicitly.
"""
import os
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import integration_gate as gate


class SymlinkedBrowserDirectoryGate(unittest.TestCase):
    def test_symlinked_browser_source_directory_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "backend").mkdir()
            (root / "backend" / "app.py").write_text("# synthetic\n")
            web = root / "web"
            web.mkdir()
            (web / "app.js").write_text("// synthetic entrypoint\n")
            (web / "smoke.test.cjs").write_text("// synthetic test\n")
            (root / "test_smoke.py").write_text(
                "import unittest\nclass Smoke(unittest.TestCase):\n"
                "    def test_ok(self): self.assertTrue(True)\n"
            )
            # A same-root link suffices: source discovery silently prunes it,
            # even though a browser can load /web/modules/invalid.js.
            target = web / "actual_modules"
            target.mkdir()
            (target / "invalid.js").write_text("function ( {\n")
            # Use a non-JS file in the target so the real JS syntax failure
            # cannot mask the symlink-directory discovery defect.
            (target / "invalid.js").unlink()
            (target / "asset.txt").write_text("synthetic\n")
            link = web / "modules"
            try:
                link.symlink_to(target, target_is_directory=True)
            except (OSError, NotImplementedError) as exc:
                self.skipTest(f"symlink creation unavailable: {exc}")
            observed = []

            def fake_run(argv, env, timeout=gate.COMMAND_TIMEOUT_SECONDS):
                observed.append(argv)
                return 0

            with patch.object(gate, "ROOT", root), patch.object(
                gate.shutil, "which", return_value="node"
            ), patch.object(gate, "run_bounded", side_effect=fake_run):
                result = gate.main()

            self.assertEqual(
                result, 2,
                "Symlinked browser-source directories must be rejected, "
                "not silently pruned from validation",
            )
            self.assertFalse(observed, "Reject unsafe source tree before subprocess execution")


if __name__ == "__main__":
    unittest.main()
