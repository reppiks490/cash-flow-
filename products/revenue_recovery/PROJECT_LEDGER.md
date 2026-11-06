# Revenue Recovery Engine — Shared Engineering Ledger

**Established:** 2026-11-06 (America/Chicago)  
**Status:** engineering kickoff; no verified product revenue or production deployment.  
**Repository:** `reppiks490/cash-flow-`  
**Isolated project root:** `products/revenue_recovery/`  
**Initial vertical:** HVAC service businesses.  
**Business objective:** work toward $2,500/month *verified recurring net profit* (not guaranteed, not the same as $2,500 billed).

## Non-negotiable boundaries

- This is a **new customer-facing product**, not a rename of MONEYFALL ZERO or ICARUS.
- Keep all changes in this isolated root, with product-only CI changes when justified and reviewed. Existing MONEYFALL, ICARUS, Everbloom, and other repositories/automations are out of scope.
- Absolutely **no OpenAI Codex** in any task, CLI, cloud agent, GitHub bot, workflow, or review. Use ordinary ChatGPT, available GitHub tools, Python/standard test tooling, and compatible non-Codex runners only.
- No API secrets, private prospect details, PII, customer datasets, paid credentials, real payment receipts or operational CRM records in this public repository.
- No unapproved spending, external outreach, billing activation, messaging, or production deployment. No invented claims about customers, tests, emails, income, or live integrations. Sample/demo records must be explicitly `synthetic`.
- All inbound leads, outbound drafts, CRM adapters, and financial events must be provenance-bound. Human approval and consent/suppression checks gate outbound communications.
- All engineers use dedicated branches, concise PRs and issue-backed changes. Protect existing branches, preserve unique commits, never force-push. Coordinate shared contracts through RRE-01. No unrelated edits.

## Mission and acceptance path

**M0 — Bootstrap:** Self-contained README/launch, backend contracts, mock data, minimal no-cost runnable flow. Acceptance: reproducible instructions, synthetic fixtures and passing tests.

**M1 — Sellable demo:** Synthetic lead intake -> deduplication -> source-backed qualification -> human-reviewable follow-up draft -> mock scheduling/CRM -> pipeline dashboard and attribution. Acceptance: end-to-end run with no external side effects, clear distinctions between estimates/appointments/paid outcomes.

**M2 — Controlled pilot candidate:** Tenant-safe auth/storage plan and implementation, opt-out and consent handling, audit logging, recovery/idempotency, approved provider integrations, operator playbook, credible demo, and regression tests. Do not mark pilot-ready until QA signs off.

**M3 — Customer validation:** Pilot offer and qualified prospects, with real outreach only when explicitly authorized and compliant; measure actual customer interest, payment confirmation and attributable financial performance. Revenue can only be claimed from authenticated receipts; revenue is not profit.

**M4 — Commercial release:** Secure onboarding, billing and production deployment after owner approvals, reliability monitoring, support and repeatable customer acquisition. Commercial release requires demonstrated function and real-world compliance review.

## Coordination and lane ownership

| Loop / start minute (Chicago) | Owner | Files and review scope | Ticket |
|---|---|---|---|
| Principal Architect (:00) | Contract architect + integrator | `PROJECT_LEDGER.md`, `ARCHITECTURE.md`, backend routes, persistence/contracts | [RRE-01](https://github.com/reppiks490/cash-flow-/issues/23) |
| AI Systems (:12) | Qualification and draft engine | `backend/qualification.py`, `backend/followups.py`, `backend/ai_providers.py` and own tests | [RRE-02](https://github.com/reppiks490/cash-flow-/issues/24) |
| Experience (:24) | UI and CRM | `web/`, `backend/crm.py` and own tests | [RRE-03](https://github.com/reppiks490/cash-flow-/issues/25) |
| Commercial (:36) | Pilot, offer, onboarding and unit economics | `commercial/`, `backend/onboarding.py`, approved test billing stubs | [RRE-04](https://github.com/reppiks490/cash-flow-/issues/26) |
| QA Release (:48) | Tests, security, release gate | `tests/`, `QA_LEDGER.md`, scoped safe CI | [RRE-05](https://github.com/reppiks490/cash-flow-/issues/27) |

Each task executes its **own hourly session**, not a continuously running daemon. If a connector/tool is unavailable, record precise blockers and do only source-backed work; do not claim that code ran or a PR merged. Tests and successful writes must be verified from real tool outputs.

## First business hypothesis

Offer: missed-inquiry and quote-follow-up recovery for HVAC contractors; the product surfaces stalled inbound opportunities and drafts next best actions. A hypothetical subscription of **$700/customer/month** implies 5 paying customers = $3,500 gross/month; reaching $2,500 pretax net would require operating expenses below $1,000/month. This is a pricing hypothesis to validate, not a sales forecast, signed contract or guaranteed profit.

Leading measures: leads received; permissioned/qualified leads; drafts approved; follow-ups actually sent (confirmed only); appointments booked (confirmed only); jobs closed (verified); revenue attributed (receipts), refunds, direct costs, and recurring net margin. Different stages must never be summed as if they are different customer payments.

## Initial project state — 2026-11-06

- Five dedicated engineering automations created and active, replacing the five previously active Everbloom loops (which were paused, not deleted).
- Five engineering GitHub issues created (RRE-01 through RRE-05).
- Existing repository contains reusable MONEYFALL discovery, qualification, orders and evidence modules; reusing anything requires interface, permission, safety and regression review.
- **Not yet verified:** runnable new product, integration tests, production provider connectivity, paying customers or recurring profit.
- Next action: create independent runnable skeleton and pass a synthetic end-to-end acceptance test. Engineering lanes should coordinate interfaces before integrating.

## Principal implementation checkpoint — 2026-11-06

- Isolated branch `rre/principal-mvp-scaffold-20261106` adds `backend/app.py`, `ARCHITECTURE.md`, `README.md` (all new files). No existing MONEYFALL or ICARUS files modified.
- Contract **rre.v1** frozen for review: synthetic lead DTO, deterministic consent gate, pending draft, mock events, tenant-filtered aggregates, null verified money. See ARCHITECTURE.md.
- **Observed:** GitHub file commits succeeded. **Not observed:** Python runtime execution, QA regression, integration with other lanes, external integration, revenue or profit. PR remains subject to review; do not merge without checks.
- Critical path: QA execute demo and negative tests; AI/Experience integrate against rre.v1; harden tenant auth, audit, consent and receipts before any pilot. No production readiness claim.
