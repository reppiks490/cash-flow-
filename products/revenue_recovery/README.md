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

With the local service running, open **http://127.0.0.1:8765/demo/**. The server now serves the static UI from the same origin as the synthetic lead API; refresh the dashboard after a synthetic POST. The browser's draft remains a client-side unsent preview. A separate read-only backend workflow response is available at `/api/demo/recovery/DEMO-001` after ingesting `DEMO-001`; it explicitly requires human review and does not book/send/collect anything. No full AI qualification or real customer interaction is connected. GitHub Actions ran 24/24 product tests on integration commit `a7d692f` (run 42250319834), but release gates are still outstanding. See `ARCHITECTURE.md`, `PROJECT_LEDGER.md`, `QA_LEDGER.md` and the commercial measurement protocol.

This branch combines source snapshots from principal PR #31, QA PR #30, experience PR #28, and commercial PR #29. The original contributor PRs remain open and untouched; this integration candidate does not contain AI agent qualifications yet. All new financial numbers are scenarios, never verified cash.
