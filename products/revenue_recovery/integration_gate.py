"""Explicit local, non-Codex regression gate for the synthetic RRE product.

Run from any directory: python products/revenue_recovery/integration_gate.py
No provider calls, deployment, customer records, or network service startup.
"""
from __future__ import annotations

import os
import signal
from pathlib import Path
import shutil
import subprocess
import sys
import unittest

COMMAND_TIMEOUT_SECONDS = 600  # Bound hung tests without skipping any checks.

ROOT = Path(__file__).resolve().parent
REPO = ROOT.parent.parent


def run_bounded(argv: list[str], env: dict[str, str], timeout: int = COMMAND_TIMEOUT_SECONDS) -> int:
    """Run a test in its own process group and terminate its descendants on timeout.

    This is local regression tooling, not a sandbox for untrusted executables.
    """
    options = {"cwd": REPO, "env": env}
    if os.name == "nt":
        options["creationflags"] = subprocess.CREATE_NEW_PROCESS_GROUP
    else:
        options["start_new_session"] = True
    process = subprocess.Popen(argv, **options)
    try:
        return process.wait(timeout=timeout)
    except subprocess.TimeoutExpired:
        cleanup_error = None
        try:
            if os.name == "nt":
                # A nonzero taskkill exit must not be silently treated as cleanup.
                result = subprocess.run(
                    ["taskkill", "/PID", str(process.pid), "/T", "/F"],
                    check=False, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
                    timeout=15,
                )
                if result.returncode != 0:
                    cleanup_error = RuntimeError(f"taskkill failed: exit {result.returncode}")
            else:
                try:
                    os.killpg(process.pid, signal.SIGKILL)
                except ProcessLookupError:
                    pass
        except (OSError, subprocess.TimeoutExpired) as exc:
            cleanup_error = RuntimeError(f"process-tree cleanup failed: {exc}")
        finally:
            # Reap the direct process even if group/tree cleanup failed.
            if process.poll() is None:
                try:
                    process.kill()
                except ProcessLookupError:
                    # Child exited between poll and kill; still reap it below.
                    pass
                except OSError as exc:
                    cleanup_error = RuntimeError(f"direct process kill failed: {exc}")
            try:
                process.wait(timeout=15)
            except subprocess.TimeoutExpired as exc:
                cleanup_error = RuntimeError(f"direct process did not exit: {exc}")
        if cleanup_error is not None:
            raise cleanup_error
        raise


def main() -> int:
    if not (ROOT / "backend" / "app.py").is_file():
        print("FAIL: expected RRE source tree missing", flush=True)
        return 2
    if shutil.which("node") is None:
        print("FAIL: Node.js required; refusing to silently skip JS regressions", flush=True)
        return 2
    env = os.environ.copy()
    env["PYTHONPATH"] = str(ROOT)
    web = ROOT / "web"
    js_sources = sorted([*web.glob("*.js"), *web.glob("*.mjs")])
    js_tests = sorted({*web.glob("*.test.cjs"), *web.glob("test_*.cjs"), *web.glob("*.test.mjs"), *web.glob("test_*.mjs")})
    if not js_sources or not js_tests:
        print("FAIL: expected browser source and JS regression tests missing", flush=True)
        return 2
    # A zero-test unittest discovery exits successfully; never treat it as coverage.
    try:
        suite = unittest.TestLoader().discover(str(ROOT), pattern="test_*.py", top_level_dir=str(ROOT))
        python_count = suite.countTestCases()
    except Exception as exc:
        print(f"FAIL: Python test discovery: {exc}", flush=True)
        return 2
    if python_count == 0:
        print("FAIL: Python test discovery found zero tests", flush=True)
        return 2
    print(f"DISCOVERED: {python_count} Python test cases and {len(js_tests)} JavaScript test files", flush=True)
    commands = [
        ("Python product regressions", [sys.executable, "-m", "unittest", "discover", "-s", str(ROOT), "-p", "test_*.py", "-v"]),
        *[(f"JavaScript syntax: {path.name}", ["node", "--check", str(path)]) for path in js_sources],
        ("JavaScript interaction regressions", ["node", "--test", *map(str, js_tests)]),
    ]
    acceptance = ROOT / "backend" / "operator_acceptance.py"
    if acceptance.exists():
        commands.extend([
            ("HTTP operator acceptance", [sys.executable, "-m", "backend.operator_acceptance"]),
            ("Optimized HTTP operator acceptance", [sys.executable, "-O", "-m", "backend.operator_acceptance"]),
        ])
    else:
        print("NOTE: optional operator acceptance runner not present on this branch", flush=True)
    for label, argv in commands:
        print(f"RUN: {label}", flush=True)
        try:
            returncode = run_bounded(argv, env)
        except subprocess.TimeoutExpired:
            print(f"FAIL: {label}: exceeded {COMMAND_TIMEOUT_SECONDS}s timeout", flush=True)
            return 2
        except (OSError, RuntimeError) as exc:
            print(f"FAIL: {label}: {exc}", flush=True)
            return 2
        if returncode != 0:
            print(f"FAIL: {label}: exit {returncode}", flush=True)
            return 1
        print(f"PASS: {label}", flush=True)
    print("PASS: local synthetic regression gate; NOT production certification", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
