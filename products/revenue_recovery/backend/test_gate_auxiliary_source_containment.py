"""Synthetic regression for auxiliary JavaScript source containment."""
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
import integration_gate as gate


class AuxiliaryJavaScriptContainment(unittest.TestCase):
    def test_symlinked_auxiliary_source_is_rejected_before_commands(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "backend").mkdir()
            (root / "backend" / "app.py").write_text("# synthetic\n")
            web = root / "web"
            web.mkdir()
            (web / "app.js").write_text("// synthetic\n")
            (web / "top.test.cjs").write_text("// synthetic\n")
            outside = root / "outside.js"
            outside.write_text("// outside\n")
            try:
                (web / "helper.js").symlink_to(outside)
            except (OSError, NotImplementedError):
                self.skipTest("symlink creation unavailable")
            with patch.object(gate, "ROOT", root), patch.object(
                gate.shutil, "which", return_value="node"
            ), patch.object(gate, "run_bounded") as runner:
                self.assertEqual(gate.main(), 2)
                runner.assert_not_called()


if __name__ == "__main__":
    unittest.main()
