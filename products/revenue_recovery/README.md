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
