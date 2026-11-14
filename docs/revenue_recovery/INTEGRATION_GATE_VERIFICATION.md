# RRE integration-gate verification protocol (synthetic-only)

Tracking: [RRE-01 #253](https://github.com/reppiks490/cash-flow-/issues/253). This document is a **procedure, not test evidence**. Do not merge the stacked security integration PR based on this document.

## Source pin and scope

Use a clean, disposable checkout of `reppiks490/cash-flow-` at the **exact candidate PR head SHA**, currently `9156cc271912a4fe674dc004581d205a87c7fb13` for draft PR #286. Reconfirm SHA and compare against latest main before running; do not substitute a branch name that may move. Do not modify or delete existing branches. Only synthetic fixtures; no vendors, customers, outreach, paid services, production deploy, or trading.

## Direct gate — POSIX or Windows

Prerequisites: Python 3.11+, Node.js, standard-library unittest. From the repository root:

```sh
git rev-parse HEAD
python products/revenue_recovery/integration_gate.py
```

Record the actual commit SHA, host OS, Python/Node versions, command exit code, full stdout/stderr, start/end timestamps and any skipped tests. Require exit code 0, explicit final `PASS: local synthetic regression gate; NOT production certification`, nonzero discovered Python and JS test counts, and successful Python, JS syntax, Node interaction and operator-acceptance stages (where present). A green workflow without this exact command does **not** satisfy the gate.

## Negative controls (disposable checkout only)

- Temporarily rename `products/revenue_recovery/web/app.js` to a safe temporary name, run the gate, require nonzero exit and `expected app.js browser entrypoint missing`; restore it in a `finally`/trap before any other test.
- Add a syntactically invalid nested file `products/revenue_recovery/web/__gate_probe__/test_probe.cjs` and run the gate; require nonzero exit from Node regression execution. Remove the fixture afterward. Do not rely solely on discovery unit mocks.
- Add a symlinked JS test file and a symlinked JS test directory under `web/` targeting a harmless disposable fixture; require explicit discovery failure, not silent skip. If symlinks cannot be created due to Windows privileges, mark **blocked**, not passed.
- Verify excluded `node_modules` and `vendor` trees remain excluded; never introduce external dependencies to run these probes.

## Native Windows process-tree requirement

On a **real Windows host** (not Wine or Linux), execute:

```powershell
py -3 -m unittest products.revenue_recovery.backend.test_gate_windows_native_tree -v
```

If package import resolution prevents this command, execute the same test file directly:

```powershell
py -3 products/revenue_recovery/backend/test_gate_windows_native_tree.py -v
```

Require an actual executed test (not `skipped`) and evidence that both parent and grandchild PIDs are absent after timeout. Record `taskkill` and `tasklist` availability, platform version, command output, and exit code. A Linux skip does not prove Windows containment.

## Release reconciliation

Before any merge: independent QA review on the **exact combined head**, both non-Codex product/foundation CI successes on that SHA, direct gate and negative-control evidence, native Windows containment, and a per-file/per-commit ancestry reconciliation from current main. PR #286 currently contains 42 commits / 19 added RRE files; a narrow change must not inadvertently merge the whole stack. Preserve every original contributor branch and commit. No force-push. Explicitly record each gate as PASS / FAIL / BLOCKED with linked logs in #253 and update `PROJECT_LEDGER.md` only with verified measurements.

This protocol is not production, security, pilot, or commercial certification. No authenticated customer revenue or monthly net profit has been verified.
