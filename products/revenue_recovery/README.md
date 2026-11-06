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

The initial UI under `web/` is static and currently not hosted by `backend.app`; its offline fallback is labeled synthetic. No claim is made of browser-to-backend integration until a combined contract test passes. See `ARCHITECTURE.md`, `PROJECT_LEDGER.md`, `QA_LEDGER.md` and the commercial measurement protocol.

This branch combines source snapshots from principal PR #31, QA PR #30, experience PR #28, and commercial PR #29. The original contributor PRs remain open and untouched; this integration candidate does not contain AI agent qualifications yet. All new financial numbers are scenarios, never verified cash.
