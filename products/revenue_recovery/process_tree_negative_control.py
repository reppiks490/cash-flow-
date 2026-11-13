"""POSIX real-process negative control for integration_gate.run_bounded.

Run from product root: python process_tree_negative_control.py
Windows is deliberately not certified by this POSIX-specific check.
"""
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import time

from integration_gate import run_bounded


def alive(pid: int) -> bool:
    try:
        os.kill(pid, 0)
    except ProcessLookupError:
        return False
    # Linux zombies have exited but can await reaping by container init.
    stat = Path(f"/proc/{pid}/stat")
    return not (stat.exists() and stat.read_text().split(") ", 1)[1].startswith("Z"))


def main() -> int:
    if os.name == "nt":
        print("SKIP: POSIX-only; Windows requires separate native negative control")
        return 0
    with tempfile.TemporaryDirectory() as directory:
        pid_file = Path(directory) / "pids"
        grandchild = (
            'import os,time; '
            'open(os.environ["RRE_PID_FILE"],"a").write(str(os.getpid())+"\\n"); '
            'time.sleep(60)'
        )
        child = (
            'import os,subprocess,sys,time; '
            'open(os.environ["RRE_PID_FILE"],"a").write(str(os.getpid())+"\\n"); '
            f'subprocess.Popen([sys.executable,"-c",{grandchild!r}]); time.sleep(60)'
        )
        env = dict(os.environ, RRE_PID_FILE=str(pid_file))
        try:
            run_bounded([sys.executable, "-c", child], env, timeout=2)
        except subprocess.TimeoutExpired:
            pass
        else:
            raise AssertionError("expected real subprocess timeout")
        pids = [int(value) for value in pid_file.read_text().splitlines()]
        assert len(pids) == 2, f"expected child and grandchild, got {pids}"
        for _ in range(20):
            if not any(alive(pid) for pid in pids):
                break
            time.sleep(0.1)
        assert not any(alive(pid) for pid in pids), f"surviving processes: {pids}"
        print("PASS: child and grandchild exited after real timeout")
    assert run_bounded(
        [sys.executable, "-c", "import sys;sys.exit(7)"], dict(os.environ), timeout=3
    ) == 7
    print("PASS: nonzero exit propagated")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
