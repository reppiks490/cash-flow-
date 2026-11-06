# Revenue Recovery Engine — synthetic integration candidate

This is an isolated HVAC lead-recovery prototype. No actual customer data, public deployment, automatic sending, billing, CRM writes, authenticated revenue, or client subscriptions are implemented or claimed.

## Local usage (Python 3.11+; no paid dependencies)

From repository root:

```bash
PYTHONPATH=products/revenue_recovery python -m unittest discover -s products/revenue_recovery -p 'test_*.py' -v
PYTHONPATH=products/revenue_recovery python -m backend.app --port 8765
curl -s http://127.0.0.1:8765/health
curl -s -X POST http://127.0.0.1:8765/api/demo/leads -H 'Content-Type: application/json' -d '{"synthetic":true,"external_ref":"DEMO-001","source":"website","need":"AC not cooling"}'
curl -s http://127.0.0.1:8765/api/demo/leads
```

With the local service running, open **http://127.0.0.1:8765/demo/**. The server now serves the static UI from the same origin as the synthetic lead API; refresh the dashboard after a synthetic POST. The browser's Draft action now reads a deterministic, unsent, review-required preview from the same local API (and uses an explicitly labeled synthetic offline fallback). Click **Load synthetic examples** to populate three permitted HVAC demo leads in process memory. A separate read-only backend workflow response is available at `/api/demo/recovery/DEMO-001` after ingesting `DEMO-001`; it explicitly requires human review and does not book/send/collect anything. No full AI qualification or real customer interaction is connected. GitHub Actions ran 35/35 product tests on integration commit `fac3d74` (run 42252156846), including the offline qualification module; JavaScript syntax also passed. This is not a production or browser-automation acceptance run, and release gates remain outstanding. See `ARCHITECTURE.md`, `PROJECT_LEDGER.md`, `QA_LEDGER.md` and the commercial measurement protocol.

This branch combines source snapshots from principal PR #31, QA PR #30, experience PR #28, and commercial PR #29. The original contributor PRs remain open and untouched; this integration candidate does not contain AI agent qualifications yet. All new financial numbers are scenarios, never verified cash.


## Current five-lane contract

All five engineering source lanes are assembled in draft integration PR #33 (other branches and PRs retained). The qualification provider is a **deterministic offline rules engine**, not a paid API or LLM. Workflow previews expose explicit source evidence, non-calibrated priority scores, unknown consent, unsent draft text, dry-run CRM, no confirmed appointment, and no authenticated revenue. Do not connect a public tunnel or enter real customer information.


## Principal v0.3.1: exact-head synthetic intake and smoke acceptance

This main-derived update preserves the existing shared lead vocabulary in `backend.contracts` and adds fail-closed parsing of duplicate JSON keys and invalid `NaN`/`Infinity` tokens. Six HTTP regression cases prove the parser rejects ambiguous requests before the in-memory store is modified. Input is still a fixed **synthetic-only** four-field payload; this does **not** authorize real customer information.

Run from repository root (Python 3.11+), no paid dependencies or outside network:

```bash
PYTHONPATH=products/revenue_recovery python -m backend.smoke
PYTHONPATH=products/revenue_recovery python -m unittest discover -s products/revenue_recovery -p 'test_*.py' -v
```

PowerShell:

```powershell
$env:PYTHONPATH = "products/revenue_recovery"
python -m backend.smoke
python -m unittest discover -s products/revenue_recovery -p 'test_*.py' -v
```

The smoke spins up `127.0.0.1` on an ephemeral port and performs 12 assertions for synthetic intake/idempotency, ambiguous JSON rejection, review-only unsent draft, CRM dry-run, mock job closure (zero real jobs/payments), synthetic opt-out revocation, evidence-honest scorecard, and disabled send/billing routes. It closes its listener and exits nonzero when an assertion fails. No real consent, authenticated tenant isolation, durable private storage, genuine external integration or payment receipt is established.

**Evidence:** on the main-derived code commit `1f16400fadf6a275592ea59f12401503a5c8ad4e`, GitHub Actions RRE [run 42283740015](https://github.com/reppiks490/cash-flow-/actions/runs/42283740015) passed **99 Python + 11 Node** tests; separate MONEYFALL [run 42283739905](https://github.com/reppiks490/cash-flow-/actions/runs/42283739905) passed. This is a *synthetic prototype* acceptance result, not production certification or proof of customers, revenue or profit.
