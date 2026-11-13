"""Synthetic filesystem regression: browser entrypoint must not be a symlink."""
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
import integration_gate as gate


class BrowserEntrypointContainment(unittest.TestCase):
    def test_symlinked_app_js_fails_before_runner(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "backend").mkdir()
            (root / "backend" / "app.py").write_text("# synthetic\n")
            (root / "web").mkdir()
            outside = root / "outside.js"
            outside.write_text("// synthetic outside source\n")
            try:
                (root / "web" / "app.js").symlink_to(outside)
            except (OSError, NotImplementedError):
                self.skipTest("symlink creation not permitted on this host")
            with patch.object(gate, "ROOT", root), patch.object(
                gate.shutil, "which", return_value="node"
            ), patch.object(gate, "run_bounded") as runner:
                self.assertEqual(gate.main(), 2)
                runner.assert_not_called()

    def test_symlinked_web_root_fails_before_runner(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "backend").mkdir()
            (root / "backend" / "app.py").write_text("# synthetic\n")
            outside = root / "outside_web"
            outside.mkdir()
            (outside / "app.js").write_text("// synthetic\n")
            try:
                (root / "web").symlink_to(outside, target_is_directory=True)
            except (OSError, NotImplementedError):
                self.skipTest("symlink creation not permitted on this host")
            with patch.object(gate, "ROOT", root), patch.object(
                gate.shutil, "which", return_value="node"
            ), patch.object(gate, "run_bounded") as runner:
                self.assertEqual(gate.main(), 2)
                runner.assert_not_called()
