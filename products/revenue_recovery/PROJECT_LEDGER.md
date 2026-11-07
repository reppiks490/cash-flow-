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

## Consolidated M1 synthetic baseline — 2026-11-06 (latest checkpoint)

- **Integration PR #33 head:** `8a32d84286192462f79b02df9e0af3e9f6a67148`; PR #45 merged into branch #37 as `c004cb4a9e2f6fc5a96bd91ebab2f9d993d94640`, then #37 merged into this integration branch. Both merges preserve contributor branch history; the original upstream draft PRs remain intact.
- **Verified exact-head GitHub Actions:** `76/76` RRE Python tests and `11/11` Node behavior/DOM tests passed; browser syntax and separate MONEYFALL verification passed. RRE run https://github.com/reppiks490/cash-flow-/actions/runs/42278062611. This is a **synthetic demo release gate only**; not a production certification.
- **Consolidated contracts:** `backend/contracts.py` is the source for enum-only synthetic source/need categories and DEMO-/QA-prefixed references, used by local intake, offline qualification and CRM dry-run. This corrected an actual risk of UX/CRM accepting fewer categories than the intake API.
- **Synthetic features:** local-only demo dashboard, lead intake/dedup, deterministic review-only qualification, no-send follow-up drafts, dry-run CRM, simulated consent revocation, evidence-labeled mock appointment/job timeline, explicit unverified revenue and planning-only profit. External SMS/email, billing, calendars, CRM writes and live credentials remain **disabled/unimplemented**.
- **Open launch blockers:** authenticated multi-tenant access, private durable encrypted storage, real consent/suppression records, approvals and transmission audit, vendor/contract legal review, real CRM/calendar and financial receipts, browser visual/accessibility QA, monitoring/backups and authorized pilot customers. No real revenue or profit verified.
- **Release decision:** source can be merged into `main` only as an **inert prototype baseline**, never construed as approval for public deployment or customer data processing; keep implementation branches and audit history intact. Product CI and QA checks must be green on final merger commit.

## Commercial-readiness consolidation — 2026-11-06

- **Source work:** unique docs from commercial draft PR #35 and fail-closed `commercial/demo_readiness.py` plus tests from stacked PR #41 were reviewed and brought to `feature/rre-commercial-pilot-gate-20261106`, preserving original branches. These are independent of PR #43's measurement guards, which were integrated earlier.
- **Products:** `commercial/PILOT_OFFER_AND_DISCOVERY.md` and `UNIT_ECONOMICS_AND_KPIS.md` define an HVAC-only, owner-gated pilot discussion script, hypothetical $700/mo pricing sensitivity, and provenance for inquiry/draft/booking/job/receipt stages. They **do not** authorize outreach or claim customer traction.
- **Synthetic onboarding:** a complete internal demo checklist can return `offline_demo_ready` but **never** enables payments, CRM writes or customer contact. Missing/extra/nonboolean checks fail closed.
- **Evidence distinction:** actual paying customer count, authenticated receipts and real net profit remain **unverified/unknown** without connected private sources. This is not proof of zero business activity, nor permission to claim forecasted profit.
- **Exact source verification:** code/documentation head `4d8493d35a60dd6a7add0e3838b0b56d8d3223bf` passed **92/92 RRE Python tests**, **11/11 Node tests**, browser JS syntax, and independent MONEYFALL foundation checks (RRE Actions run https://github.com/reppiks490/cash-flow-/actions/runs/42279877940). This is still a no-live-data synthetic baseline.

## Principal security reconciliation — 2026-11-06 (new branch from main)

- The `main` synthetic baseline prior to this branch was `20c8a797be2592c5d31edb9bd9409e48a9e2ad46` after commercial PR #55.
- Old principal PR #46 contained a valid strict JSON ingress defense and a synthetic integration smoke, but its branch was stacked on an outdated parent. Ported only its owned files to fresh isolated branch `principal/rre-json-parsing-smoke-main-20261106`, preserving PR #46 source history and all unrelated files.
- **Superpowers-style RED→GREEN evidence:** at test-only commit `9e4216a246d0448fa56b445eaa96876e5a300b04`, RRE CI run 42283403050 failed as intended (three failing duplicate/NaN acceptance cases and the smoke error). Following parser repair, commit `a04731499bb19ab8a28536c4337adb7f02743a49` passed **97/97 Python and 11/11 Node** tests in [42283504628](https://github.com/reppiks490/cash-flow-/actions/runs/42283504628); MONEYFALL foundation also passed on the exact code commit.
- Added dependency-free `backend/smoke.py`, `test_smoke.py`, `test_ingress_contract.py`, and fail-closed `json.loads` hooks for duplicate members/nonstandard numeric constants. No live customer data, external network calls, paid services or production deployment.
- **Still blocked for pilot:** real identity and tenant RLS, private durable records, legally validated consent and opt-out, customer approvals, CRM/calendar integrations and signed financial receipts. Tests are strictly synthetic.

## Financial input release gate — 2026-11-06

- **Base:** `main` post-PR #62 synthetic parser hardening, commit `2acfe6a342bad39c1f156d6964c839be1c0a7449`. QA/Commercial owner files were ported from their isolated branches to `integration/rre-financial-input-guards-20261106`; source branches left untouched.
- **RED proof:** test-only commit `47fe733a6a8c40b1651e87c007c6ae65635add2f` introduced commercial price/measurement checks. GitHub Actions run [42283982355](https://github.com/reppiks490/cash-flow-/actions/runs/42283982355) failed **10 assertions and 8 errors**, exposing acceptance of noncanonical amounts, unbounded values and a raw `decimal.InvalidOperation` exception on extreme exponents.
- **GREEN proof:** source hardening commit `cd9df35798a0fb20a42d7be2b4c6e892ba42ee2e` passed **106/106 Python, 11/11 Node and JS syntax**, with separate MONEYFALL CI green in [42284105908](https://github.com/reppiks490/cash-flow-/actions/runs/42284105908). Syntax and maximum amounts are checked before constructing Decimal; unsupported/unsafe price and measurement inputs now raise domain-specific errors.
- **What this does not prove:** These remain synthetic planning values. There is no authenticated billing/processor receipt, verified paid customer count, or actual net profit; no live payment account or financial data was accessed. Production rollout/PII/messaging remain forbidden pending separate gates.

## Offline commercial tool consolidation — 2026-11-06

- **Base:** `main` `d8ab6c9bb8fc891cb2bd451e519b2508804d4c76` after PR #65, which already contains the offline demo CLI and mock port plan through upstream commercial integration. This follow-up adds the *previously missing* hypothetical calculator from corrected commercial PR #60 and aligns documentation; it does not claim ownership of the already-merged CLI. All source branches remain intact.
- **Functionality:** `commercial.demo_cli` prints a JSON mock/disabled integration plan from a demo workspace; five operator checklist flags can allow **offline demo preview only**. No actual provider connections, credentials, customer information, paid service, sending, bookings, invoicing or charging. `commercial.scenario_calculator` computes labeled *hypothetical* contribution, expense and minimum-customer math, always with actual receipts/profit `null`.
- **Verification:** `1fffe7f257ae7883631d02ac6072c2d91da2ef92` passed **129/129 product Python tests, 11/11 Node tests and JavaScript syntax** in [RRE Actions run 42284503399](https://github.com/reppiks490/cash-flow-/actions/runs/42284503399). Separate MONEYFALL foundation CI passed. Documentation-only amendments need exact-head rerun before merge.
- **Release gates remain closed:** production authentication, tenant RLS/private storage, real consent/suppression, signed CRM/calendar/financial receipts, legal/commercial approval, customer willingness to pay and recurring net profit are unknown/unverified. A `$700` assumption is not validated pricing.

## AI review and CRM interoperability contract reconciliation — 2026-11-06

- **Base:** current `main` at `c658064f3b8420d0705d17d79d8822307ce07206` after calculator PR #70. Clean integration branch `integration/rre-review-draft-crm-contract-20261106` incorporates compatible source-reviewed code/tests from existing AI PR #54 and Experience PR #51 without touching their original branches.
- **Idempotency:** qualification fingerprint now hashes validated reference+source+need+rubric version, avoiding raw references in the key and making changed categories produce distinct deterministic keys; HTTP intake separately prevents conflicting replay. Consent/opt-out remains a separate fail-closed gate.
- **Drafts:** three bounded synthetic objections (price, timing, competitor) generate distinct *UNSENT*, human-review-only templates. Unknown/free-text objection inputs reject. Offline provider contract supports only deterministic local processing; no LLM call, vendor connection or send enabled.
- **CRM:** inert `preview_crm_envelope` returns a vendor-neutral, enum-validated JSON preview with `dry_run=true`, `transmitted=false`, no provider ID/recipient/actual appointment/verified revenue. Not a real CRM connector.
- **Verification:** exact source commit `43c7d8e475e848e158a0b4dce7f9d8c37101dd62` passed **144/144 Python tests and 11/11 Node tests** plus JS syntax, and MONEYFALL foundation CI passed (RRE run https://github.com/reppiks490/cash-flow-/actions/runs/42285139847). Subsequent documentation-only head requires recheck.
- **Open:** true customer/tenant authentication, consent persistence and sender eligibility, secure provider credentials, signed actual appointment/payment receipts, legal review and live pilot approval remain unimplemented.

## Browser synthetic feed trust boundary — 2026-11-06

- **Source work:** Experience PR #50 had a targeted fix for browser-side synthetic intake contract drift. A separate `integration/rre-browser-synthetic-gate-20261106` branch forwards only `web/app.js` plus the dependency-free Node negative suite and existing product-only Node CI command. The original Experience branch stays untouched. We intentionally did **not** add a Python unittest subprocess wrapper requiring Node for local Python-only tests.
- **RED proof:** at commit `6fd6a85b3e2de662c72bfa6bcd009a86af59fa89`, GitHub Actions [42285573441](https://github.com/reppiks490/cash-flow-/actions/runs/42285573441) failed **3/15 Node checks**, exposing display of malformed/PII-bearing synthetic rows and oversized feed acceptance.
- **GREEN proof:** after exact-contract validation, commit `c59ae6de9c6b56c1e3059dd0e5b7635afa4ce56e` passed **144/144 Python and 15/15 Node tests**, JS syntax, plus independent MONEYFALL checks in [42285686595](https://github.com/reppiks490/cash-flow-/actions/runs/42285686595).
- **Contract:** UI accepts only five stored lead fields, exact validated DEMO/QA references, shared source and need enums, `status=received`, `synthetic=true` and maximum 2,000 rows. Any invalid row rejects the entire response and shows clearly labeled offline synthetic fixtures, never a mixture with user content.
- **Not proven:** real PII detection, authentication, tenant ownership, legal consent, production confidentiality or real customer import. This is a local prototype boundary only.

## Browser request-race regression — 2026-11-06

- **Scope:** UI-only isolated branch `integration/rre-ui-response-race-hardening-20261106` based on main `ff76773caaacae0717f5e53bbbf295f5a6974d1e` after security PR #84. Unique tests/logic are forward-ported from Experience draft PR #68; original branch preserved. Deliberately avoid Python subprocess Node dependency by executing the new Node suite directly in product CI.
- **RED:** before implementation, workflow-registered browser async race tests failed **5/20 Node cases** on commit `2fa36f63edc18b86d2bc5d76374564c61abe1238` (RRE run https://github.com/reppiks490/cash-flow-/actions/runs/42304063535). Older A→B→A and rejected promises overwrote newer synthetic evidence or consent status.
- **GREEN:** code commit `aede876b73db83caff7b03c8bd8ba75f6fc89f05` passed **160 Python / 20 Node** and JS syntax in https://github.com/reppiks490/cash-flow-/actions/runs/42304191417; independent MONEYFALL workflow passed at exact head. Browser uses lead selection generation plus per-route request revision; no network/send/backend contract changed.
- **Limits:** Node VM tests do not establish real browser screenshots, accessibility, production authentication, consent validity or customer revenue. Demo is localhost-only with synthetic fixtures.


## Principal integrated security/evidence checkpoint — 2026-11-06 (post-main PR #95)

- **Current verified source scope:** the existing HVAC synthetic-only, loopback HTTP demo; CRM and booking remain dry-run/preview only, operator draft approval is not real outbound authorization, and simulated jobs are not authenticated collections.
- **Main merges performed with expected head SHA checks:** [#77](https://github.com/reppiks490/cash-flow-/pull/77) CRM dry-run contract tests, merge `b3898183fe2d5b9017d0e56638df11a7a4945b50`; [#78](https://github.com/reppiks490/cash-flow-/pull/78) financial attribution classifier, merge `5f28043357343bfc912f9545eb2ef5a9306312db`; [#84](https://github.com/reppiks490/cash-flow-/pull/84) canonical ASCII identifier fix plus original QA tests, merge `ff76773caaacae0717f5e53bbbf295f5a6974d1e`; [#93](https://github.com/reppiks490/cash-flow-/pull/93) canonical USD input guard, merge `29f3ab7bb9eb272fa79901d198d1fb0ac00b9bd4`; [#95](https://github.com/reppiks490/cash-flow-/pull/95) source-preserving QA queue-capacity and JSON parser regressions, merge `5b8d13896cf693698caeb63b6fcfbf94685caf5c`. Original contributing PRs/branches remain untouched; no force-pushes, private customer data, live connections or unrelated product edits.
- **RED→GREEN security evidence:** QA's Unicode lookalike tests initially failed 8 subtests on integrated SHA `66b7d7f` ([RRE 42303375402](https://github.com/reppiks490/cash-flow-/actions/runs/42303375402)); same tests then passed at SHA `5aac883` (**160/160 Python, 15/15 Node**, [RRE 42303502554](https://github.com/reppiks490/cash-flow-/actions/runs/42303502554)), plus independent MONEYFALL. Shared `backend.contracts.REF` now uses ASCII-restricted Unicode casefold semantics.
- **RED→GREEN monetary-input evidence:** commercial USD grammar red run [42303922729](https://github.com/reppiks490/cash-flow-/actions/runs/42303922729) failed 39 subtests accepting noncanonical Decimal strings; corrected SHA `c60a257` passed **161/161 Python and 15/15 Node** ([RRE 42304024165](https://github.com/reppiks490/cash-flow-/actions/runs/42304024165)) and separate MONEYFALL.
- **Additional integrated test evidence:** #95 combined source-preserved capacity/concurrency tests (3) with nested duplicate/±Infinity JSON tests (2); exact PR head `b06b87a` passed **166/166 Python and 15/15 Node** in [RRE 42304349614](https://github.com/reppiks490/cash-flow-/actions/runs/42304349614), plus MONEYFALL [42304349625](https://github.com/reppiks490/cash-flow-/actions/runs/42304349625). These are PR-head reports; **merged-head pipeline verification is a separate release requirement** and must not be invented.
- **Release contract:** `RELEASE_BOUNDARY_CONTRACT.md`, forward-ported from older draft #71, defines RB-01 through RB-13 and cites primary-source FTC and Python documentation. It is a design-only checklist. Most production RB gates remain incomplete; no production identity, tenant-bound authenticated RLS, encryption/backup policy, legally reviewed consent and suppression records, auditable per-draft approvals, externally verified CRM/calendar/payment receipts, monitoring, billing, or approved pilot.
- **Owner boundaries:** Principal owns common contract/HTTP entry, security architecture and this ledger; QA's source tests were copied unchanged into reviewed integration branches, and Commercial's existing USD negative test was copied unchanged. Five Revenue automations preserve their separate responsibilities and no-Codex prohibition.
- **Commercial outcome:** actual customers, real closed-work collections, monthly revenue, true costs and net profit remain **unverified/unknown**. The $2,500/month NET target is an evaluation goal, not a claim or guarantee. Next critical path: complete and independently validate RB-04 through RB-11 trust/consent/receipts gates with explicit owner authorization before any pilot, while maintaining an offline demo.


## Principal post-merge reconciliation — 2026-11-07 13:04 America/Chicago

- **Observed main:** `660149782e55e2b4286ce45f65b9f33da87d3ab1` (merge of PR #139). This replaces the older `418a6bc...` and `9765e489...` baselines referenced in earlier checkpoints.
- **Merged and source-inspected:** PR #136 (duplicate-Origin fail-closed backend + two loopback regressions), #134 (offline provider identity/bundle integrity), #139 (consolidated dashboard concurrency tests), #140 (inert onboarding preview), and #133 (synthetic evidence classification). GitHub reported `merged=true` for each. Do **not** re-merge predecessor/overlapping drafts (#131/#132 and earlier Experience variants).
- **Security source check on main:** `backend/app.py` rejects more than one `Origin` header before parsing or storing a lead. `_valid_host()` rejects missing/duplicate Host headers and non-loopback authorities. This is source inspection, **not** a fresh local runtime test or production penetration test.
- **Outstanding principal PR #127:** draft ledger-only reconciliation based on an obsolete main snapshot; reconcile or supersede, never blindly merge stale ledger text.
- **Test-evidence boundary:** historical green exact-head workflows for predecessor PRs do not prove the newly merged combined main has passed fresh integration tests. Run product Python tests, dashboard Node regressions, and MONEYFALL foundation verification against the current combined SHA; capture run IDs and failure details before asserting a combined-tree green state.
- **Next critical path:** QA review combined main, test synthetic end-to-end intake -> qualification -> unsent draft -> CRM/scheduling mock -> scorecard and evidence classifier; then address remaining M2 tenant-safe persistence, consent/audit, operator onboarding, and deployment approval gates. No live external actions authorized.
- **Business evidence:** zero authenticated receipts demonstrated; no verified paying customers or $2,500/month net profit. Demo/synthetic PASS must not be presented as commercial validation.


## Combined-main CI verification — 2026-11-07 13:58 America/Chicago

- **Exact combined `main` SHA:** `660149782e55e2b4286ce45f65b9f33da87d3ab1`.
- **Newly verified push workflow results (not predecessor PR runs):** `Verify Revenue Recovery synthetic prototype` GitHub Actions run [42399450848](https://github.com/reppiks490/cash-flow-/actions/runs/42399450848) = `completed/success`; `Verify MONEYFALL foundation` run [42399450969](https://github.com/reppiks490/cash-flow-/actions/runs/42399450969) = `completed/success`. Both runs report the exact combined-main SHA. This resolves the earlier *missing combined-main CI evidence* blocker; it does not imply penetration testing, browser visual QA, or production readiness.
- **Integration queue:** draft #142 is this ledger-only update; #143 (AI provider instance overrides), #144 (stale scenario/consent UI responses), #145 (commercial KPI protocol), and #146 (QA ledger) remain separate review/CI candidates. Do not merge overlapping old draft #127 or superseded security/Experience branches.
- **Next critical path:** obtain independent non-Codex review and exact-head CI on #143/#144, verify the combined synthetic end-to-end operator path, and keep RB-04 through RB-11 production gates on HOLD pending explicit authorization. No verified customers, receipts or $2,500/month net profit.


## Principal review checkpoint — 2026-11-07 14:55 America/Chicago

- **Latest observed main:** `660149782e55e2b4286ce45f65b9f33da87d3ab1`; no newer main commit returned by GitHub fetch at this checkpoint. Shared RRE-01 issue #23 and current ledger read before edit.
- **Independent source inspection:** PR #143 (`5413d1882597e38020c45586a7f2d09077f9802a`) modifies only AI-owned `backend/ai_providers.py` and `backend/test_provider_instance_override.py`; rejects nonempty provider instance attributes before `qualify`/`draft` calls and adds three synthetic regression tests. PR #144 (`5a81ab5b59424b70193d77fbfe346e9ee5a66f7b`) modifies only Experience-owned `web/app.js` and `web/view_races.test.cjs`; prevents stale scenario/policy success or failure from replacing state after the selected choice changes, with four Node regressions. Their changed paths are disjoint; this is source review, **not** a combined-tree execution.
- **Exact-head non-Codex CI independently queried:** #143 Revenue Recovery run [42404724568](https://github.com/reppiks490/cash-flow-/actions/runs/42404724568) and MONEYFALL [42404724579](https://github.com/reppiks490/cash-flow-/actions/runs/42404724579) both `completed/success`; #144 Revenue Recovery [42405961471](https://github.com/reppiks490/cash-flow-/actions/runs/42405961471) and MONEYFALL [42405961498](https://github.com/reppiks490/cash-flow-/actions/runs/42405961498) both `completed/success`. GitHub review listings returned **zero submitted reviews** for each PR.
- **Integration decision:** HOLD both drafts. Request independent non-Codex QA approval and combined-tree regression on a new reviewed integration head before merging; never activate prohibited automatic review or merge production functionality. Do not infer real browser, tenant security, legal consent, customer receipts or verified income from these tests.
- **Next principal work:** close end-to-end synthetic operator acceptance with reproducible CLI/HTTP evidence, preserve source-lane ownership, and keep release-boundary RB-04–RB-11 on HOLD pending explicit authorization. No real revenue, customers or $2,500/month NET profit verified.


## Principal exact-head verification — 2026-11-07 15:58 America/Chicago

- **Ledger PR #142 exact head:** `84c69bcdaf1866f5d251fd79e90e0c6ac36c2d35` has successful Revenue Recovery workflow `42413404057` and MONEYFALL workflow `42413404094`, both reported `completed/success` by GitHub. This verifies the ledger branch head before this documentation-only update; the new commit requires its own check.
- **Reviewed open scoped fixes:** #143 rejects instance-level overrides of the deterministic offline provider before method invocation; #144 discards stale dashboard scenario/consent responses when the selected workflow changes. Both remain draft; GitHub review queries returned **zero submitted reviews** for each. Their file changes are in different owner lanes and must be independently reviewed before integration.
- **Acceptance boundary:** workflow success on individual PRs is not proof of a newly merged combined tree, browser visual QA, real integration or customer revenue. No merge, production activation, outreach, or billing authorized by this checkpoint. Next: obtain independent reviews, test exact integrated tree and run end-to-end synthetic operator acceptance. Verified paying customers and net profit remain unknown.
