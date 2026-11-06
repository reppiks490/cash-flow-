# Revenue Recovery Engine — isolated HVAC prototype

No-cost offline synthetic demonstration. Python 3.11+; no packages, credentials or network access required.

From the repository root:

```bash
python products/revenue_recovery/backend/app.py demo
```

This prints one synthetic HVAC repair lead, a human-review-only draft, one mock CRM event and a tenant-scoped report. It does not send messages, schedule real appointments, collect customers or verify any revenue. All money fields are null. The SQLite connection is in-memory by default; do not store customer information in the repository.

See [ARCHITECTURE.md](ARCHITECTURE.md) for the frozen `rre.v1` interface, acceptance criteria and production blockers. See [PROJECT_LEDGER.md](PROJECT_LEDGER.md) for owner coordination.
