# MONEYFALL ZERO

Evidence-backed B2B revenue capture with $0 upfront. Start with
[CODEX_START_HERE.md](CODEX_START_HERE.md), both mandatory handoff documents,
and [current continuation state](docs/CONTINUATION.md).

## Run locally

Python 3.11+; the core, tests and public hiring sources need no third-party
packages, API keys or paid services. Optional media rendering needs additional
local dependencies described in [launch operations](docs/LAUNCH.md). From this checkout:

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
- [Screening, outreach packets, orders and fulfillment](docs/LAUNCH.md)
- [Portrait layout production and fictional specimen](docs/CREATIVE_LAYOUTS.md)
- [Canonical Vellumflare Site source and deployment boundary](docs/VELLUMFLARE_SITE.md)
- [Continue independent work while activation is gated](docs/CONTINUATION_POLICY.md)
- [Implementation plan and audit decisions](docs/superpowers/plans/2026-10-12-foundation.md)
- [Opportunity scenario catalog](config/opportunities.json)
- [Capability ledger and historical balances](config/capabilities.json)

Implemented: public hiring ingestion, private company screening, qualification,
scenario ranking, original media rendering, gated outreach packets, duplicate-send
reservations, accepted orders, signed payment import, per-order refunds and
validated production/delivery records. CI runs synthetic verification only.
Gmail drafts and the private offer preview exist; sending, verified payout setup,
live payment hosting and unattended reply handling require operational activation.

The repository offer page is now the canonical self-contained Vellumflare source
for review/import. It contains dependency-free WebGL identity artwork, accessible
motion/fallback controls, fictional specimens, the unchanged $149 pilot and a
local-only brief composer. This does **not** mean the owner-private ChatGPT Site
was overwritten: the 2026-10-12 session exposed only a read-only Site projection,
so authenticated Site import and browser/device QA remain separate deployment work.

## Two-account cash-flow collaboration

Read [coordination startup and protocol](coordination/README.md), [split plan](coordination/SPLIT_PLAN.md) and [task list](coordination/TASKS.md) after the mandatory handoff reads. Atlas is the other account; ChatGPT/Codex is this account. Read both boards and your inbox, then reserve a bounded task. Keep this collaboration separate from ICARUS and private operational data out of public messages.

Current goal, operator and cohort decisions: [CURRENT_EXECUTION.md](docs/CURRENT_EXECUTION.md). Atlas operates the original private cohort; ChatGPT maintains core engineering and integrity review. Target:legitimate profit within14–20 days, with costs/payout availability disclosed. PR5 correction remains under review; no live launch is claimed.

PR5 adds linked-company suppression checks and signed/opaque draft-ID rejection. See [audit](docs/ENGINEERING_AUDIT_2026-10-12.md) for50-test local verification and pending peer review; core changes are not a live sender or proof of profit.
Complementary production capability: [evidence-linked research audits](docs/RESEARCH_AUDIT.md), with supplied source quotes, actions, counter-evidence and private Markdown/HTML/optional PDF exports. Fictional fixture only; no new charged scope or buyer demand is established.

Latest reviewed integration and website/launch evidence: [Atlas checkpoint](docs/research/atlas/2026-10-13-immersion-and-integration.md). Historical pending-review notes above are retained as dated checkpoints.
