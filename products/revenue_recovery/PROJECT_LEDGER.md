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


## Follow-up integration batch — 2026-11-06 (Principal + Parallel; follow-up branch)

- **Branch:** `feature/rre-pipeline-evidence-hardening-20261106`, stacked on draft integration PR #33. This batch does not alter other agents' branches and is confined to `products/revenue_recovery/`, `docs/revenue_recovery/` and the product-specific non-Codex test workflow.
- **Implemented:** `backend/demo_evidence.py` with deterministic mock lifecycle events for review, appointment, and synthetic job closure. Every event is marked `synthetic=true`, has no authenticated actor or provider receipt, and cannot send a message or transfer money. Scorecard shows zero *verified* receipts and unknown real customer count when disconnected.
- **HTTP:** read-only `GET /api/demo/scorecard` and `GET /api/demo/scenarios/{DEMO_OR_QA_REF}/{review|appointment_mock|closed_job_mock}`; invalid scenarios and mutation attempts fail closed. Nothing writes a CRM or books appointments.
- **UX:** same-origin scenario viewer and evidence timeline, and synthetic scorecard; no value shown as real revenue. Added Node VM interaction tests (not headless Chromium visual tests) and CI job to run `node --test` with Python suite.
- **Privacy:** local `http.server` default raw request-line logging disabled so accidental identifiers in invalid paths do not echo to console. This is a demo mitigation, **not** authenticated production audit logging.
- **Commercial/compliance research:** Parallel-search primary-source comparison confirms incumbent features in Jobber, Hatch and Housecall Pro and points to legal review of consent/opt-outs under FCC and FTC rules. Research is documented in `docs/revenue_recovery/PARALLEL_MARKET_COMPLIANCE_RESEARCH_2026-11-06.md`. This is neither a completed compliance assessment nor validated customer demand.
- **Verified code checks:** `46/46` product Python tests and `6/6` JavaScript VM interaction tests passed at code head `977b64f3c0eb5143393fe7c985488f02e764bd96` in GitHub Actions run [42256492252](https://github.com/reppiks490/cash-flow-/actions/runs/42256492252); MONEYFALL foundation tests passed separately on the same code commit. One earlier new JS harness run failed on a mock DOM selector setup and was repaired; no production implementation was implicated.
- **Runbook:** Windows PowerShell and Git Bash local-only commands and explicit no-public-tunnel restrictions are documented in `products/revenue_recovery/RUNBOOK_LOCAL.md`.
- **Remaining blocked:** signed receipts, actual bookings/CRM writes, real customer communications, accounts/auth/tenant boundaries, private durable storage, legal review and approved outreach, pricing and paying pilots. No customer or net-profit milestone is verified.
- **Release classification:** working *synthetic integration candidate*, not pilot-ready or commercially deployed. Use `docs/revenue_recovery/RELEASE_ACCEPTANCE_MATRIX_2026-11-06.md` for next unblocked tickets.

## Additional consent/suppression integration — 2026-11-06

- **Read-only endpoint** `GET /api/demo/policy/{ref}/{unknown|revoked_mock|consent_record_mock}` computes strictly local consent fixture outcomes. **No recipient data**, actual communications, API tokens or contacts. This is not lawful consent or operator authentication.
- **Fail-closed behavior:** revoked mock returns `draft=null`, `suppressed=true`; unknown consent and mock-record scenarios may create internal-only draft text but never enable outreach or send. No mock record can turn `consent_verified`, `operator_authorized` or `may_contact_real_person` true.
- **Browser:** explicit policy viewer lets a human inspect the outcome of revocation vs unknown/mock consent. UI never posts a real follow-up.
- **Exact code head verification:** commit `d68574ad89c700165ae5188f9a99c69a515960ef` passed **52/52 Python product tests**, **7/7 Node VM tests**, JavaScript syntax, and separately existing MONEYFALL foundation checks. See GitHub Actions [42257493614](https://github.com/reppiks490/cash-flow-/actions/runs/42257493614). The Node VM validates logic but is **not a visual browser accessibility/security audit**.
- **Release safety:** all customer consent/real contact states are unverified. A simulated revocation handler does **not** satisfy actual TCPA/CAN-SPAM processing, authenticated revocation audit, tenant isolation, lawful permission, or telecom provider terms. Zero verified revenue and no paying customers have been demonstrated.


## Principal ingress security checkpoint — 2026-11-06 (PR #46, stacked on #37)

- **Concrete regression fixed:** default `json.loads` accepts duplicate JSON object field names and silently uses the last one. The HTTP `POST /api/demo/leads` endpoint now uses a duplicate-key rejector and disallows nonstandard numeric constants (`NaN`/`Infinity`). This closes ambiguous synthetic-flag ingestion without adding dependencies, API endpoints or permitted customer data.
- **Principal-owned artifacts:** `backend/app.py`, `backend/test_ingress_contract.py`, and this contract checkpoint in `ARCHITECTURE.md`. Four new local loopback HTTP tests cover two duplicate-field cases, invalid numeric input, and valid 201/200 replay.
- **Observed execution:** exact code head `867902cff4cf3977c33ce8b36334ee1c9df656f9` passed GitHub Actions RRE workflow [42278232414](https://github.com/reppiks490/cash-flow-/actions/runs/42278232414) — **80 Python tests passed and 11 Node tests passed**, along with JavaScript syntax. Separate unchanged MONEYFALL foundation workflow [42278232481](https://github.com/reppiks490/cash-flow-/actions/runs/42278232481) passed. The later documentation and ledger commits require exact-head revalidation.
- **Branch structure:** `principal/rre-strict-json-ingress-20261106` -> `feature/rre-pipeline-evidence-hardening-20261106` (#37) -> `integration/rre-synthetic-m1-20261106` (#33) -> `main`. All remain isolated draft PRs. **No merges performed**; require QA/security review and exact-head CI for each integration step.
- **Compatibility blocker:** standalone #38 uses incompatible `rre.v1` SQLite semantics vs this HTTP contract v0.3.1. Do not merge both backends blindly; choose one explicit API version and preserve branches. #36/#44 QA tests and #40 CRM hardening remain separately stacked and require controlled integration.
- **Outcome classification:** measured synthetic validation only; no public serving, customer contact, SaaS payments, signed revenue receipts, production identity/tenant authorization, compliant consent, verified recurring profit, or pilot release clearance. **Next critical path:** QA inspect PR #46, reconcile QA #36/#44 and Experience #40 with #37, verify integrated head, then consider staged merge.


## Principal executable M1 smoke checkpoint — 2026-11-06 (PR #46)

- **New executable acceptance artifact:** `backend/smoke.py` launches a loopback-only ephemeral HTTP server, asserts 12 reproducible synthetic workflow conditions, prints machine-readable results and closes its listener. `backend/test_smoke.py` adds the complete flow to CI; `README.md` provides Git Bash and PowerShell invocation. No vendor services, secrets, paid integrations, real recipients, customer records, billing or live deployment.
- **Covered steps:** synthetic intake 201, repeat 200, malformed duplicate-key rejection with no persistence, GET recovery preview with unapproved unsent draft and CRM `dry_run`, synthetic closed-job fixture with zero actual jobs/receipts and no external side effects, revoked mock consent suppressing the draft, scorecard treating real customers as unknown, and 404 for send/billing POST routes.
- **Observed exact-head CI:** code SHA `d0d53a319651288b6321689d36112c15b2784be2` passed `81/81` Python tests, `11/11` Node VM tests plus JavaScript syntax in [RRE workflow 42279300959](https://github.com/reppiks490/cash-flow-/actions/runs/42279300959), and unchanged MONEYFALL checks passed in run 42279300963. README SHA `53b06a1c06ab52586aa3488a5d90bfdf1984e579` separately passed both [RRE 42279371511](https://github.com/reppiks490/cash-flow-/actions/runs/42279371511) and [MONEYFALL 42279371540](https://github.com/reppiks490/cash-flow-/actions/runs/42279371540). This subsequent ledger commit requires its own exact-head checks.
- **Cross-lane review:** principal recorded a blocking contract-drift/invalid-type concern on Experience PR #40 (review 5805752610), which is not mergeable against #37 as currently reported. QA PR #36/#44 carry additional security/store tests and must be reconciled with #37 before staging all code on #33. Original branches/PRs untouched; no merges conducted.
- **Release state:** reproducible offline **synthetic** M1 path exists and is CI-tested; production auth, tenant security, real consent evidence, external CRM/calendar operations, payment receipt verification, customer revenue and recurring net profit are all **not demonstrated**. Do not advance M2 or commercial readiness without owner/QA clearance.
