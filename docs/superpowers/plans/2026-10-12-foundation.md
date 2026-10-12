# MONEYFALL ZERO foundation implementation plan

Execution: inline under the autonomous mandate in AGENTS.md.
Spec: docs/CODEX_HANDOFF_2026-10-12.md and its research appendix.

## Audit and design

Baseline e68c096 contains five Markdown files and one handoff issue; no executable
code, dependencies, CI, operational records or established conventions exist.
No conflicts with the handoff were found. The historical tool balances remain
snapshots, not available budget. No account-usage inspection interface is exposed.

Build a Python 3.11+ standard-library CLI, avoiding paid infrastructure and
dependencies. Keep SQLite operational state outside the checkout, permission
restricted. Public files contain code, configuration, synthetic fixtures and
aggregate technical findings only. Hiring indicates a need, not willingness to
buy, confirmed ad spend, or a proven marketing deficiency.

Use explicit human-supplied evidence for missing scoring dimensions. Initial
opportunity numbers are scenario assumptions; no automatic champion promotion
without a minimum sample of paid conversions and a material score advantage.
No network send or payment execution exists in this foundation.

## Tasks and knowledge delta

1. Tests first in tests/test_engine.py: invalid numbers, incomplete qualification,
   evidence-backed champion promotion, duplicate source ingestion, public ATS
   normalization, duplicate payment events, refunds, suppression and private paths.
   Run and observe missing implementation, then implement src/moneyfall modules.
2. CLI and config: public GET-only Greenhouse/Lever collection with source and
   retrieval timestamps; private deduplication; draft briefs linked to signals,
   offers and hypotheses; capability ledger with shared workspace accounting.
3. Verify deterministic tests, live source availability and CLI round trip.
4. README.md runbook, docs/OPERATIONS.md architecture/decisions, config ledgers,
   docs/CONTINUATION.md audit/results/next experiment; update AGENTS.md router.
   CI verifies synthetic code only, never publishes protected queue artifacts.
5. Review and commit a feature branch with a reviewable PR. Preserve handoffs.

## Review focus

- Unknown prospect dimensions cannot silently become positive scores.
- Stale source timestamps cannot be relabeled as posting dates.
- Duplicate/refunded payments must not inflate cash or profit.
- Private state cannot resolve inside the public checkout, including symlinks.
- Provider failure must be visible; no empty-success or accidental paid fallback.

## Decisions

SQLite rather than hosted CRM: reversible, $0, transactional deduplication; it
requires a persistent private host for unattended operation. GitHub Actions runs
CI only until a durable private state store is configured. Greenhouse/Lever use
official public job boards; no contact enrichment credits or trials are consumed.
An opportunity formula is a heuristic, not measured probability or financial EV.
Librarian review will verify every new path is reachable from README/AGENTS.
