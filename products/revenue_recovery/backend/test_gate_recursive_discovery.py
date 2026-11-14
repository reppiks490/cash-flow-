"""Principal-owned, filesystem-only recursive JavaScript discovery contracts.

Synthetic temporary files only; no Node execution, network, vendors, or PII.
"""
from pathlib import Path
import tempfile
import unittest

from integration_gate import discover_js_tests


class RecursiveDiscoveryContracts(unittest.TestCase):
    def test_nested_tests_are_found_sorted_and_deduplicated(self):
        with tempfile.TemporaryDirectory() as directory:
            web = Path(directory) / "web"
            (web / "nested" / "deeper").mkdir(parents=True)
            expected = [
                web / "a.test.cjs",
                web / "nested" / "deeper" / "test_z.mjs",
                web / "nested" / "test_b.js",
            ]
            for path in expected:
                path.write_text("// synthetic test fixture\n")
            (web / "nested" / "ordinary.js").write_text("// not a test\n")
            self.assertEqual(discover_js_tests(web), sorted(path.resolve() for path in expected))

    def test_generated_and_vendor_trees_are_excluded(self):
        with tempfile.TemporaryDirectory() as directory:
            web = Path(directory) / "web"
            web.mkdir()
            good = web / "test_allowed.js"
            good.write_text("// synthetic\n")
            for excluded in ("node_modules", "vendor", "vendors", "dist", "build", "coverage", ".cache"):
                folder = web / excluded / "deep"
                folder.mkdir(parents=True)
                (folder / "test_should_not_run.js").write_text("// synthetic\n")
            self.assertEqual(discover_js_tests(web), [good.resolve()])

    def test_symlinked_test_file_fails_closed(self):
        with tempfile.TemporaryDirectory() as directory:
            base = Path(directory)
            web = base / "web"
            outside = base / "outside"
            web.mkdir()
            outside.mkdir()
            external = outside / "test_external.js"
            external.write_text("// synthetic\n")
            try:
                (web / "test_link.js").symlink_to(external)
            except (OSError, NotImplementedError):
                self.skipTest("symlinks unavailable on this platform")
            with self.assertRaisesRegex(ValueError, "unsafe JavaScript test file"):
                discover_js_tests(web)

    def test_symlinked_test_directory_fails_closed(self):
        with tempfile.TemporaryDirectory() as directory:
            base = Path(directory)
            web = base / "web"
            outside = base / "outside"
            web.mkdir()
            outside.mkdir()
            (outside / "test_external.js").write_text("// synthetic\n")
            try:
                (web / "linked").symlink_to(outside, target_is_directory=True)
            except (OSError, NotImplementedError):
                self.skipTest("symlinks unavailable on this platform")
            with self.assertRaisesRegex(ValueError, "unsafe symlinked JavaScript test directory"):
                discover_js_tests(web)

    def test_excluded_symlinked_vendor_directory_is_ignored(self):
        with tempfile.TemporaryDirectory() as directory:
            base = Path(directory)
            web = base / "web"
            outside = base / "outside"
            web.mkdir()
            outside.mkdir()
            (outside / "test_external.js").write_text("// synthetic\n")
            try:
                (web / "vendor").symlink_to(outside, target_is_directory=True)
            except (OSError, NotImplementedError):
                self.skipTest("symlinks unavailable on this platform")
            self.assertEqual(discover_js_tests(web), [])

    def test_missing_and_symlinked_web_root_fail_closed(self):
        with tempfile.TemporaryDirectory() as directory:
            base = Path(directory)
            missing = base / "missing"
            self.assertEqual(discover_js_tests(missing), [])
            real = base / "real"
            real.mkdir()
            (real / "test_outside.js").write_text("// synthetic\n")
            link = base / "web"
            try:
                link.symlink_to(real, target_is_directory=True)
            except (OSError, NotImplementedError):
                self.skipTest("symlinks unavailable on this platform")
            self.assertEqual(discover_js_tests(link), [])


if __name__ == "__main__":
    unittest.main()
