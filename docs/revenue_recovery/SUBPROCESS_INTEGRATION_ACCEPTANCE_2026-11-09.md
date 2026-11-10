# RRE subprocess integration acceptance — 2026-11-09

Status: **proposed integration procedure**, not executed or approved. Scope: synthetic offline regression tooling only. Source of truth for releases remains `products/revenue_recovery/PROJECT_LEDGER.md` and RRE-01 issue #23.

## Current source dependencies

- PR #197 changes `integration_gate.py` to tolerate `ProcessLookupError` between direct-child `poll()` and `kill()`; parent is a principal process-tree branch, **not main**.
- PR #183 adds QA timeout tests that patch `subprocess.run`; the current runner executes test commands using `subprocess.Popen` and `process.wait(timeout=600)`. These tests cannot prove the current contract without revision by QA.
- PR #198 and PR #199 overlap on POSIX race regressions; select one reviewed implementation, not both. QA's #198 is the proposed canonical source.
- PR #201 adds native Windows child/grandchild negative control; PR #203 adds its `finally` cleanup. Both require real Windows execution. Linux workflow success does not execute Windows-only assertions.

## Integration order and pass/fail checks

1. Fetch current main and all PR exact head SHAs immediately before preparing a new isolated integration branch. Compare file paths and ancestry; never reset or force-push source branches.
2. Ask QA to revise #183 on its owned branch: patch `Popen`, supply a process double with `wait(timeout=...)`, `poll()`, `kill()`, `pid`, and context-specific cleanup, and assert that the first timeout stops subsequent commands. Verify `wait(timeout=COMMAND_TIMEOUT_SECONDS)` rather than a nonexistent `subprocess.run(timeout=...)` invocation. Include success and failure paths.
3. Integrate #197's source fix, exactly one of #198/#199, reconciled #183, and the Windows test plus cleanup from #201/#203. Record provenance of each copied commit/file. Do not combine until source overlap and duplicate assertions are reviewed.
4. On the **combined exact SHA**, run `python products/revenue_recovery/integration_gate.py` from repository root on Linux or macOS; independently run `python -m unittest discover -s products/revenue_recovery -p 'test_*.py' -v` with `PYTHONPATH=products/revenue_recovery`, and run the product's existing non-Codex GitHub Actions and MONEYFALL foundation checks. Record actual commands, exit status, test count, SHA and run URLs. The gate is not a security sandbox.
5. On native Windows (not Wine or a Linux skip), run `cd products/revenue_recovery && python -m unittest -v test_windows_process_tree_containment`. Confirm **not skipped**, child and grandchild termination, and no surviving process IDs. Run the full local gate in PowerShell and capture exit codes. If process inspection is unavailable or fails, classify as **blocked**, never passed.
6. Require independent QA review of the exact combined diff and all CI outcomes; only then consider a scope-limited, nonproduction merge. Check that unrelated MONEYFALL, ICARUS and Everbloom files remain untouched.

## Hard stops

Do not merge if native Windows coverage is skipped/unverified, if the combined head lacks checks, if QA mocks do not exercise `Popen`, or if independent review is outstanding. No public deployment, customer PII, outreach, paid services, billing, trading, Codex, or production claims. CI success on a parent or stacked branch is **not** combined-head evidence.

## Completion record template

Combined SHA: **pending**. Source PRs/SHAs: **pending**. Linux gate and CI: **not run on combined head**. Windows-native negative control: **not verified**. Independent QA: **pending**. Merge: **not authorized until gates pass**. Customer revenue and $2,500/month net: **unverified**.
