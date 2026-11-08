"""Explicit local, non-Codex regression gate for the synthetic RRE product.

Run from any directory: python products/revenue_recovery/integration_gate.py
No provider calls, deployment, customer records, or network service startup.
"""
from __future__ import annotations

import os
from pathlib import Path
import shutil
import subprocess
import sys

ROOT = Path(__file__).resolve().parent
REPO = ROOT.parent.parent


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
            result = subprocess.run(argv, cwd=REPO, env=env, check=False)
        except OSError as exc:
            print(f"FAIL: {label}: {exc}", flush=True)
            return 2
        if result.returncode != 0:
            print(f"FAIL: {label}: exit {result.returncode}", flush=True)
            return 1
        print(f"PASS: {label}", flush=True)
    print("PASS: local synthetic regression gate; NOT production certification", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
