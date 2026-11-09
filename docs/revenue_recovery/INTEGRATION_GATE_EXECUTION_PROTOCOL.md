# RRE synthetic integration gate — exact-head execution protocol

Scope: local synthetic test execution only. No customer data, vendor credentials, external messaging, payments, deployment or production certification. Do not invoke Codex or any Codex-powered workflow.

## Preconditions

1. Check out the exact proposed integration commit and record `git rev-parse HEAD`. Do not test one branch and claim another passed.
2. Use Python 3.11+ and Node.js with built-in `node --test` support. Run from the repository root, without network-dependent installs.
3. Confirm the combined tree includes principal gate PR #172, timeout PR #181, QA PRs #175/#183 as applicable, and any intended web contract tests. Preserve original branches; reconcile on a separate integration branch.
4. Use a non-Codex runner. Do not run production integrations.

## Required executable checks

```sh
git rev-parse HEAD
python products/revenue_recovery/integration_gate.py
python -m unittest discover -s products/revenue_recovery/tests -p 'test_integration_gate*.py' -v
node --test products/revenue_recovery/web/*.test.cjs
```

Record each command's exit code, captured output, commit SHA, and workflow run/job URL. A green workflow that never invokes `integration_gate.py` does **not** satisfy the first check.

## Negative controls

- Missing Node.js: in a disposable environment where `node` is absent from PATH, the gate must fail with exit code 2, not silently skip JavaScript tests.
- Injected failing regression: on a disposable branch, add a deterministic failing `test_*.py`; the gate must return nonzero and identify the failing suite. Revert the injection before integration.
- Timeout handler: QA tests should exercise `subprocess.TimeoutExpired` -> exit code 2 and positive timeout arguments on every launched command.
- **Real timeout:** run a short-lived synthetic subprocess which deliberately exceeds a 0.2-second timeout. This verifies Python subprocess timeout behavior, not the RRE gate's 600-second path or process-tree cleanup:

```sh
python -c "import subprocess,sys; p=[sys.executable,'-c','import time;time.sleep(5)']; exec('try:\\n subprocess.run(p,timeout=0.2,check=True)\\n raise SystemExit(1)\\nexcept subprocess.TimeoutExpired:\\n print(\"PASS: real subprocess timeout observed\")')"
```

- **Descendant cleanup is separately unverified.** `subprocess.run(timeout=...)` kills and waits for its direct child; do not infer that grandchildren are terminated. A platform-specific process-group containment change and real descendant test require their own scoped implementation and review.

## Merge acceptance

Require exact-head green product and foundation CI, direct runner output, negative controls, independent QA review, and no overlapping unresolved source changes. Keep stacked drafts unmerged until their bases are reconciled. Do not auto-enable any prohibited review bot. The result is a synthetic regression-gate claim only, not security certification, pilot approval, authenticated revenue, or verified net profit.
