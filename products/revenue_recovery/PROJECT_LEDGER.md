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


## Principal engineering checkpoint — 2026-11-06 10:00 America/Chicago

- **Verified GitHub artifacts:** principal bootstrap draft PR #31, QA stacked PR #30, Experience draft PR #28, Commercial draft PR #29. AI Systems #24 is not yet verified as a PR.
- **Principal changes on #31:** local loopback-only HTTP intake, in-memory idempotent queue, v0.1a allowed-value restrictions to reduce accidental PII in demo input, and REUSE_AND_INTEGRATION_AUDIT.md with rights and acceptance boundaries.
- **Security status:** synthetic flag is not proof that data is synthetic. Allowed-value restrictions are a demo safeguard only. No public deployment, live records, customer contact or billing. No authenticated tenancy or private storage.
- **Test status:** source changes committed, but **new allowed-value validation has not yet been executed in RRE CI**. QA #30 was branched from an earlier principal commit and must be reconciled with current PR #31 before any merge; no RRE green claim until tested against exact integration SHA.
- **Licensing:** ICARUS LICENSE.md states proprietary/all rights reserved; no ICARUS code or market/trading data reused. MONEYFALL modules inspected at directory level only, no imports or copies.
- **Critical path:** QA integrate latest principal commit and run isolated RRE tests; AI define pure qualification/draft functions; Experience wire same-origin synthetic API; Commercial keep payments/outreach hard disabled; Principal coordinate integration without merging unverified branches.
- **Financial status:** no verified paying customers, no verified product revenue, no verified monthly net profit.


## Integration checkpoint — 2026-11-06 10:13 America/Chicago (supersedes earlier test-status note)

- **Integration branch:** `integration/rre-synthetic-m1-20261106`, based on QA's stacked bootstrap; pulls source snapshots from principal PR #31, QA PR #30, Experience PR #28 and Commercial PR #29 without mutating any original source branch. Own product files only plus existing product-specific non-Codex CI; no changes to MONEYFALL or ICARUS modules.
- **Combined test evidence:** commit `483dd202023bca2d04498eac99e1b04fb118a6b9` passed 19/19 RRE tests in GitHub Actions run 42249477317. Subsequent commit `a7d692f13c3d69e25e033c6d1473f2faa8e1fb2b` passed **24/24 RRE tests** in run 42250319834, and MONEYFALL foundation verification also passed on exact head. Includes same-origin HTTP browser route, a deterministic review-required read-only recovery preview, CRM dry-run, no real appointments/payment, conflicting-idempotency and host/origin safety tests.
- **Actual feature state:** synthetic lead intake, enumerated data categories, idempotent replay, dashboard serving, browser local draft, CRM preview, explicit missing appointment verification, $0 verified revenue display and hypothetical commercial models. Browser draft still local and not connected to backend recovery-preview route; AI qualification not yet integrated, no actual customer-facing SaaS.
- **Remaining M1 work:** approved AI qualification/draft interface; frontend fetch of backend preview and UI status; dynamic CRM/appointment placeholder only, no false confirmed outcomes; end-to-end CI on final integration head; upstream PR attribution/review/merge coordination.
- **Remaining M2/M3/M4 gates:** authentication, tenant isolation, private durable state, consent/suppression audit, real integrations, legal review, validated pilot demand, signed contracts, explicit authorizations and real signed financial receipts. Not pilot-ready or commercially deployable.
- **Business evidence:** no verified paying customers, real product payments, recurring revenue or net profit.
- **Next priority for Principal:** hold all branch merges until QA reviews exact integration SHA; request cross-lane API wiring and coordinate incremental integration PR with no Codex involvement.


## Five-lane integration checkpoint — 2026-11-06 (supersedes older PR/run counts)

- **Draft PR:** https://github.com/reppiks490/cash-flow-/pull/33 on `integration/rre-synthetic-m1-20261106` (not merged to main). Source snapshots now include *all five* engineers, including offline rule-based AI PR #32. Independent PR branches #28–#32 remain preserved for attribution and review.
- **Verified CI:** Python 3.11, `35/35` product unittest checks passed on exact commit `fac3d74dbf2011d109266ecc336673580435ce41`, https://github.com/reppiks490/cash-flow-/actions/runs/42252156846 . Node's `--check` also passed for the dashboard JS; MONEYFALL foundation workflow passed separately. Subsequent documentation commits need their own exact-head checks.
- **Synthetic M1 features:** same-origin local dashboard, three click-to-load synthetic HVAC leads, idempotent intake, rejection of raw customer fields/unknown IDs, read-only recovery preview composed from deterministic qualification, rule source/evidence/unknowns, unsent follow-up, CRM dry-run, fake appointment explicitly unbooked, no authenticated revenue. Browser falls back to labeled offline fixtures.
- **What is not established:** Actual LLM/AI inference, authenticated multi-tenancy, encrypted private persistence, CRM/calendar/telephony/SMS/email connections, genuine human approval identity, safe consent capture, signed receipts, payments, accurate recovered-revenue attribution, customer contracts, verified income, production hosting or security assurance. End-to-end browser automation/visual QA has not been executed.
- **Next critical gate:** QA reviews exact integration PR head, browser visual/functional verification, and owner/QA approval before any merge. Then implement authenticated tenant data boundaries and consent audit; only after those may authorized real pilot records be considered.
