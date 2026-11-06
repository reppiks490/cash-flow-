# Revenue Recovery Engine — local operator runbook

**Status:** strictly synthetic, loopback-only demonstration. No production or pilot authorization. User/customer records, payment credentials, real emails, texts, business phone numbers, CRM keys and other PII must never be entered. The browser reports mock workflow events, not actual outcomes.

## Check out the isolated working candidate

For an existing local clone (PowerShell or Git Bash):

```bash
git fetch origin
git switch --create rre-local-demo --track origin/feature/rre-pipeline-evidence-hardening-20261106
```

If a local branch named `rre-local-demo` already exists, choose a fresh branch name instead; never overwrite or reset unique local commits. The branch is a **follow-up to draft integration PR #33**, not a release merged into `main`.

## Windows PowerShell (Python 3.11+)

From the repository root, in PowerShell window A:

```powershell
$env:PYTHONPATH = "products/revenue_recovery"
py -3 -m unittest discover -s products/revenue_recovery -p "test_*.py" -v
py -3 -m backend.app --port 8765
```

The service binds **127.0.0.1:8765 only**. Open http://127.0.0.1:8765/demo/ on the *same computer*. Press **Load synthetic examples** and select one of the three fictitious HVAC leads. Select a lead to inspect its review-required internal draft; optionally inspect read-only `review`, `appointment_mock`, or `closed_job_mock` timeline examples.

To check API responses in a second PowerShell window:

```powershell
Invoke-RestMethod "http://127.0.0.1:8765/health"
$lead = @{ synthetic=$true; external_ref="DEMO-LOCAL-01"; source="website"; need="AC not cooling" } | ConvertTo-Json -Compress
Invoke-RestMethod "http://127.0.0.1:8765/api/demo/leads" -Method Post -Body $lead -ContentType "application/json"
Invoke-RestMethod "http://127.0.0.1:8765/api/demo/recovery/DEMO-LOCAL-01"
Invoke-RestMethod "http://127.0.0.1:8765/api/demo/scenarios/DEMO-LOCAL-01/closed_job_mock"
Invoke-RestMethod "http://127.0.0.1:8765/api/demo/scorecard"
```

If port 8765 is occupied by another local service, use `--port 8766` and change URLs correspondingly. Avoid killing unrelated processes.

## Git Bash / Linux

```bash
PYTHONPATH=products/revenue_recovery python -m unittest discover -s products/revenue_recovery -p 'test_*.py' -v
PYTHONPATH=products/revenue_recovery python -m backend.app --port 8765
```

## What a passing demo proves

- HTTP synthetic intake, enum-only values and idempotent references.
- Human-review-required offline rules and internal unsent draft generation.
- Browser-to-local-API read-only preview and synthetic scorecard.
- Mock event lineage for hypothetical appointment and closed job stages, with **zero** verified payment receipts.
- No actual communication, scheduling, CRM update, bill, customer record, or paid inference.

## Never infer

- Mock appointment == booked appointment? **No.**
- Mock closed job == paid job? **No.**
- `verified_* = 0` means no verified financial data in the prototype; it is not proof a business received no payments.
- A test suite passing == production safe? **No.** Real data needs authenticated tenant isolation, encrypted private persistence, consent/suppression, signed provider receipts, legally reviewed messaging, audit and disaster recovery, approval and independently verified acceptance testing.

### Operational safeguards

Keep on loopback, not public IP, LAN binding, Cloudflare tunnel or Tailscale exposure. There is **no login**, and demo-only fixture data exists in process memory until stopped. Default HTTP request logging is suppressed to avoid reflecting accidental user-supplied URLs; this is not a substitute for a production-grade redacted audit facility. Stop with Ctrl+C; all process-local lead records are lost.

To test JavaScript behavior locally using the included no-install Node tests:

```bash
node --check products/revenue_recovery/web/app.js
node --test products/revenue_recovery/web/test_app.mjs
```

**Release posture:** prototype, not a paid-customer pilot. All non-Codex CI logs and evidence must be attached to the follow-up PR, and existing Everbloom, ICARUS and MONEYFALL ZERO components are out of scope.
