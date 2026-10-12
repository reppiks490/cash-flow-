# MONEYFALL ZERO

Evidence-backed B2B revenue capture with $0 upfront. Start with
[CODEX_START_HERE.md](CODEX_START_HERE.md), both mandatory handoff documents,
and [current continuation state](docs/CONTINUATION.md).

## Run locally

Python 3.11+; no third-party packages, API keys or paid services required for the
implemented public hiring sources. From this checkout:

```bash
export PYTHONPATH=src
python -m unittest discover -s tests -v
python -m moneyfall rank
python -m moneyfall demo
python -m moneyfall collect greenhouse COMPANY_BOARD_TOKEN
python -m moneyfall collect lever COMPANY_BOARD_TOKEN
python -m moneyfall queue
python -m moneyfall brief SIGNAL_ID
python -m moneyfall metrics
python -m moneyfall metrics --opportunity signal-driven-b2b
```

`demo` uses disposable synthetic records; its money is not real revenue.
`rank` labels all initial numbers as planning assumptions. The incumbent remains
unchanged without observed conversion evidence. `collect` is GET-only and fails
explicitly for retired boards/network errors. Source tokens come from companies'
current public career pages; an old token returning 404 is not a provider outage.

Operational state defaults to `~/.local/share/moneyfall/state.sqlite`, with file
permissions 0600. Override using `MONEYFALL_STATE` or `--state /PRIVATE/path.sqlite`.
State inside the checkout is rejected, even through symlinks. Back up this file
to private persistent storage; do not put it in git or public Actions artifacts.
CLI queue/brief output is private operational material: do not paste it into CI.

## Qualify and attribute

`qualify SIGNAL_ID PRIVATE_EVIDENCE_FILE` accepts JSON with `dimensions` (budget,
deficiency, value, reachability, demonstrability, speed, each 0–1 or null) and an
`evidence` object mapping each non-null dimension to supporting observations or
URLs. Missing evidence yields no qualified score. Human review is still needed
to validate the observations; a score is not permission to send.

```bash
python -m moneyfall event UNIQUE_RECEIPT_ID SIGNAL_ID payment --amount 14900 --evidence VERIFIED_RECEIPT_REFERENCE
python -m moneyfall event UNIQUE_REFUND_ID SIGNAL_ID refund --amount 4900 --evidence VERIFIED_REFUND_REFERENCE
python -m moneyfall event OPT_OUT_ID SIGNAL_ID suppressed --evidence OPT_OUT_REFERENCE
```

Amounts are integer cents; `credit_spend` uses integer credits. References belong
in private state only. Events are manually recorded observed facts, not live
email/payment integrations. Never record invoices as payments or drafts as sends.

## Architecture and operating knowledge

- [Operations, privacy, attribution and source references](docs/OPERATIONS.md)
- [Continuation / verification / first experiment](docs/CONTINUATION.md)
- [Implementation plan and audit decisions](docs/superpowers/plans/2026-10-12-foundation.md)
- [Opportunity scenario catalog](config/opportunities.json)
- [Capability ledger and historical balances](config/capabilities.json)

Implemented: public hiring ingestion, private signal queue, qualification scoring,
scenario ranking, draft proof briefs and receipt-based event accounting. CI runs
synthetic verification only. Outreach, billing, fulfillment, unattended private
hosting and dashboard deployment remain separate integration work.
