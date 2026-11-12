# RRE integration-gate reconciliation — 2026-11-11

Scope: synthetic HVAC product only. Tracks principal issue #23 and QA issue #27. This is a source-backed integration decision, **not** evidence of a successful combined run or permission to merge.

## Anchors inspected

- `main`: `660149782e55e2b4286ce45f65b9f33da87d3ab1` (latest commit returned by GitHub commit search at inspection).
- QA PR #183: head `20868a02e89305c6645f06150896bebceb0ccf03`, draft, base `e6087174d685d896aee5368ad8967b7d1a00ad75`. Its two tests patch `gate.subprocess.run`, asserting a 600-second timeout argument and `TimeoutExpired` return 2.
- Principal Windows gate source on `principal/rre-windows-test-failsafe-cleanup-20261111`: `integration_gate.py` invokes `run_bounded(argv, env)`, which uses `subprocess.Popen(...).wait(timeout=...)` and process-tree cleanup. It calls `subprocess.run` only for Windows `taskkill` on timeout. Thus #183's mocks no longer intercept the normal command path.
- QA PR #234: head `7f7f286430ccee9200eb5c96103993a6c267ee57`, draft, stacked on #233. Its published exact-head Windows CI run 43032873312 reports 5 passed / 0 skipped and a second invocation of one existing acceptance test. This is **not** combined-main validation.

## Contract reconciliation required (QA-owned test change)

1. Rebase by **new isolated branch** from the accepted principal gate stack (do not rewrite or delete QA #183 or any predecessor). Keep the source branches intact.
2. Replace mocks of `gate.subprocess.run` with mocks of `gate.run_bounded` for `main()` orchestration. For the timeout case, raise `subprocess.TimeoutExpired` on the first invocation and assert `main() == 2` and exactly one invocation. For the successful case, return 0 and assert all expected commands are executed. `main()` no longer supplies the timeout kwarg; timeout enforcement belongs to `run_bounded`.
3. Separately exercise `run_bounded` using a short-lived synthetic hanging child and a **small explicit timeout**; verify timeout propagates, direct child is reaped and descendants are terminated where supported. Native Windows tree containment evidence from #234 must remain platform-specific and independently reviewed.
4. Run `python products/revenue_recovery/integration_gate.py` and relevant unittest discovery on the exact combined head. Confirm Node test discovery, no skipped critical tests, and foundation CI. Record SHA, command, exit code, job URLs and log excerpts.
5. Independent QA/security review is mandatory before integration. Never infer PID-reuse safety, production hardening, pilot readiness or customer financial outcomes from these checks.

## Current blocker and release decision

The main branch does not yet contain `products/revenue_recovery/integration_gate.py`; the gate exists on stacked principal branches. Direct Git clone in this runtime failed DNS lookup for github.com; ordinary GitHub connector reads and scoped writes work. Therefore no local combined-head execution was performed in this checkpoint. Do **not** merge #183 or #234 independently. No external services, live customer records, outreach, billing, production deployment, or Codex were used.

Next principal action: coordinate an isolated QA reconciliation branch and inspect the exact merged candidate; accept only a reviewed green combined tree. Verified revenue and monthly net profit remain unavailable.
