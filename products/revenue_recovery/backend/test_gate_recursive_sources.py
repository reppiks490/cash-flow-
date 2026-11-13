"""Regression checks for recursive browser source syntax coverage."""
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import integration_gate as gate


class RecursiveBrowserSources(unittest.TestCase):
    def test_nested_sources_are_discovered_in_sorted_order(self):
        with tempfile.TemporaryDirectory() as tmp:
            web = Path(tmp) / "web"
            (web / "modules" / "nested").mkdir(parents=True)
            (web / "app.js").write_text("// synthetic\n")
            (web / "modules" / "nested" / "helper.mjs").write_text("// synthetic\n")
            (web / "vendor").mkdir()
            (web / "vendor" / "excluded.js").write_text("invalid\n")
            found = gate.discover_js_sources(web)
            self.assertEqual(
                [path.relative_to(web).as_posix() for path in found],
                ["app.js", "modules/nested/helper.mjs"],
            )

    def test_nested_symlinked_source_is_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            web = root / "web"
            (web / "modules").mkdir(parents=True)
            outside = root / "outside.js"
            outside.write_text("// synthetic\n")
            try:
                (web / "modules" / "helper.js").symlink_to(outside)
            except (OSError, NotImplementedError):
                self.skipTest("symlinks unavailable")
            with self.assertRaises(ValueError):
                gate.discover_js_sources(web)

    def test_nested_invalid_source_is_passed_to_syntax_check(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "backend").mkdir()
            (root / "backend" / "app.py").write_text("# synthetic\n")
            web = root / "web"
            (web / "modules").mkdir(parents=True)
            (web / "app.js").write_text("// synthetic\n")
            (web / "modules" / "bad.mjs").write_text("const = ;\n")
            (web / "basic.test.cjs").write_text("// synthetic\n")
            commands = []
            def runner(argv, env, timeout=gate.COMMAND_TIMEOUT_SECONDS):
                commands.append(argv)
                return 1 if argv[:2] == ["node", "--check"] and argv[-1].endswith("bad.mjs") else 0
            with patch.object(gate, "ROOT", root), patch.object(gate.shutil, "which", return_value="node"), patch.object(gate, "run_bounded", side_effect=runner), patch.object(gate.unittest.TestLoader, "discover") as discover:
                discover.return_value.countTestCases.return_value = 1
                self.assertEqual(gate.main(), 1)
            self.assertTrue(any(argv[:2] == ["node", "--check"] and argv[-1].endswith("bad.mjs") for argv in commands))
            self.assertFalse(any(argv[:2] == ["node", "--test"] for argv in commands))


if __name__ == "__main__":
    unittest.main()
