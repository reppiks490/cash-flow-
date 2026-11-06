# RRE QA and release gate — 2026-11-06

**Release classification: NOT PILOT READY.** This ledger documents the available source and evidence, not a claim that the entire system has been integrated.

## Current QA reconciliation — 2026-11-06 16:27 America/Chicago

**Current disposition: GREEN only for synthetic nonproduction integration; NOT PILOT READY.** The source, CI and original ownership records below remain available.

- Main inspected at `4bf7f97817edb231699310c046bb5893b9aabbec`, including RRE #95 capacity+strict JSON regression merge and #96 browser async request-race fix. These were **merged by other contributors**; this QA branch has not merged anything.
- Because #95 merged `tests/test_store_capacity.py` into main with exactly the original source blob `3a318a529029859fd1bb79f8871d56b4a8996bc3`, the redundant identical file was removed from draft PR #85 with commit `0b869ae14c663f3b367f63f642790db19921eade`. Original PR #73, its branch, and all earlier commits remain preserved; **no current PR #85 diff changes capacity tests**.
- Active draft PR #85 now changes only `tests/test_cross_view_evidence.py` (four synthetic HTTP contract tests) and this QA ledger. GitHub-generated integration ref `a3d4d7b` merged source head `0b869ae14c663f3b367f63f642790db19921eade` into checked main `4bf7f97817edb231699310c046bb5893b9aabbec`. [RRE Actions run 42304740618](https://github.com/reppiks490/cash-flow-/actions/runs/42304740618), job `128191101790`: **170/170 Python, 20/20 Node, JavaScript syntax PASS**, [MONEYFALL foundation run 42304740529](https://github.com/reppiks490/cash-flow-/actions/runs/42304740529) SUCCESS. Logs examined, including all four new tests. This does not constitute a local test run, browser visual/security audit, or authorization for production.
- **Unresolved P0 pilot gates:** verified authenticated tenant identity, private durable storage and audited consent/opt-out/suppression rechecks, confirmed human approval before real communications, authenticated vendor receipts for bookings and collected revenue, rollback/incident controls and owner-granted legal/deployment permissions. An in-memory DemoStore, HTTP 404 on non-existent auth routes, and static revocation fixtures are not evidence of operational controls. The \$2,500/month net objective remains unverified.
- Keep PR #85 in **DRAFT** until independently reviewed; existing repo-level automatic forbidden review trigger makes transitioning to ready unsafe. Never invoke Codex or any external send/payment/deploy service.

## Historical verified QA release checkpoint — 2026-11-06 (for the cited commits)

**Release disposition: GREEN for local-only synthetic QA; BLOCKED / NOT PILOT READY for any live use.**
Historical notes below are retained for provenance and are NOT the current integration status.

- Latest main inspected: `ff76773caaacae0717f5e53bbbf295f5a6974d1e` (includes reviewed synthetic attribution evidence and the ASCII reference corrective merge #84). Exact main push workflow [RRE 42303708345](https://github.com/reppiks490/cash-flow-/actions/runs/42303708345) ran **160/160 Python and 15/15 Node tests** with JavaScript syntax green; separate MONEYFALL workflow [42303716269](https://github.com/reppiks490/cash-flow-/actions/runs/42303716269) completed SUCCESS. This records only that source snapshot; do not infer later heads are green.
- New QA-owned cross-view draft [PR #85](https://github.com/reppiks490/cash-flow-/pull/85), initial head `cb32806e888646813a5411d48bafe05047833c6e`, adds **four** loopback HTTP acceptance cases in `tests/test_cross_view_evidence.py`. Synthetic mock closure cannot change verified scorecard, mock revocation cannot send/authorize actions, duplicate/conflicting replays cannot inflate collections, forged payment/recipient/tenant and Authorization fields cannot enable missing real endpoints.
- On the PR's initial GitHub-generated integration ref `a2a2b3dcfe8be02c4f74f371cc3bc9551ced676c` (merged test head into then-main `5f28043357343bfc912f9545eb2ef5a9306312db`), [RRE 42303480605](https://github.com/reppiks490/cash-flow-/actions/runs/42303480605) ran **161/161 Python, 15/15 Node and JavaScript syntax PASS**. Independent MONEYFALL [42303480417](https://github.com/reppiks490/cash-flow-/actions/runs/42303480417) completed SUCCESS. A later main merge requires a fresh PR integration run; neither these checks nor main's checks prove production readiness.
- **Capacity handoff from old QA draft #73:** copied `tests/test_store_capacity.py` **byte-identically** from original QA branch blob `3a318a529029859fd1bb79f8871d56b4a8996bc3`; original branch/PR history preserved. The three tests check at-capacity rejection without partial insert, correct idempotent/conflicting replay, and safe concurrent distinct admission into a bounded DemoStore.
- **Seven QA test methods combined:** PR #85 branch source `d4e6f375a7882d5c88aefd235c9b4fecd976b1bc` checked out via GitHub PR integration `4882902376382d8c1768f4e9a7654adc1bb0467a` against main `ff76773caaacae0717f5e53bbbf295f5a6974d1e`. [RRE Actions run 42303941747](https://github.com/reppiks490/cash-flow-/actions/runs/42303941747) **167/167 Python PASS, 15/15 Node PASS and JS syntax PASS**, [MONEYFALL 42303941650](https://github.com/reppiks490/cash-flow-/actions/runs/42303941650) SUCCESS. That is a real latest-main generated-merge execution, not local validation; later commits require fresh exact-head checks. Still draft and not pilot-ready.
- Independent QA source/CI reviews: [PR #78](https://github.com/reppiks490/cash-flow-/pull/78) review `5807743400` (149 Python/15 Node on its historical exact head); [PR #73](https://github.com/reppiks490/cash-flow-/pull/73) review `5807743674` (132 Python/11 Node on historical head; requires forward-port because stale versus new main). Review comments are not production approvals.
- **Hard pilot blockers:** No authenticated customer/tenant identity or production row-level data isolation; demo `tenant_scope` remains forged fixture-only. Revocation policy is a stateless, read-only mock, not durable suppression or send-time recheck. No signed provider receipts, validated consent, human identity/approval, live CRM or calendar transaction, private operational storage, real customer collections or verified recurring net profit. Read-only mock evidence and green tests are not authorization to contact, charge, deploy or onboard customers.
- **Execution guardrail:** preserve draft PRs where necessary to avoid existing repository automatic prohibited review trigger; never invoke Codex. No real PII, external messages, trading, paid services, charges, live data or unrelated repository edits.

## Source snapshot

- Base: feature/rre-synthetic-bootstrap-20261106; QA branch: feature/rre-qa-http-contract-20261106.
- Principal prototype: backend/app.py (loopback HTTP intake, process-local DemoStore).
- Experience: draft PR #28 (web UI and CRM dry-run) is on a separate branch.
- Commercial: draft PR #29 (onboarding, hypothetical economics, agreement) is on a separate branch.
- No verified end-to-end integration between these branches.
- Existing GitHub verify.yml runs MONEYFALL tests, **not** RRE tests. A green MONEYFALL check is not RRE QA sign-off.

## Test matrix

| Gate | Evidence and status |
|---|---|
| HTTP synthetic health | Automated test in tests/test_http_contract.py; run result must be recorded separately |
| Lead intake, duplicate and readback | Automated test; no persistence across process restarts |
| Reject unexpected PII fields | Automated test; **free-text PII is NOT blocked**, see critical finding |
| Invalid JSON / oversized body | Automated test; no explicit request timeouts/rate limiting |
| No external send/billing routes | Automated negative test; production integrations not implemented |
| AI qualification, opt-out and draft human approval | BLOCKED: AI branch and contract not integrated |
| CRM / scheduling | BLOCKED: dry-run adapter only; no appointment source-of-truth |
| Tenant isolation and authenticated access | BLOCKED: no auth or tenant data model; must never expose prototype publicly |
| Real financial attribution | BLOCKED: no signed payment receipts or reconciled ledger |
| End-to-end browser acceptance | BLOCKED: frontend on PR #28 not integrated with app serving |
| Product CI | BLOCKED: existing verify.yml is unrelated; product-specific runner needed |

## Critical findings for Principal and QA

**SEC-01 — free-text personal data:** DemoStore.add validates allowed keys but permits arbitrary strings in need/source/external_ref, including real phone numbers and email addresses. Synthetic flag alone does not guarantee synthetic data. Before accepting ANY real input, implement privacy controls, retention, authenticated tenant boundary and logging policy. Do not attempt to use simple regexes as a complete PII compliance mechanism.

**SEC-02 — public access:** GET /api/demo/leads has no authentication; only 127.0.0.1 binding in main() makes this acceptable for synthetic local demonstration, not deployment. No auth bypass should be introduced.

**INT-01 — integration gap:** PR #28 and #29 are independent branches, and the backend prototype is another branch. No claim of end-to-end completion until reviewed integration branch has been built and its product tests pass.

**FIN-01 — zero verified revenue:** Hypothetical scenarios and synthetic UI must not appear as verified income. A verified payment requires signed provider or bank evidence, unique receipt IDs, refunds and expense reconciliation.

## Release criteria (all required)

1. Product-specific tests pass in non-Codex CI at the merged integration commit.
2. Tenant-safe authentication, authorization and private storage are implemented and adversarially tested.
3. Consent/suppression and human approval are enforced before every outbound action; no live sends in demo.
4. End-to-end test covers intake -> qualification -> reviewable draft -> approved CRM/appointment -> authenticated receipt attribution.
5. Financial reports distinguish estimated quote, confirmed job, collected cash, refunds, operating costs and our subscription profit.
6. Real integrations undergo vendor terms/security review; credentials remain in private secrets management.
7. Operator authorization for deployment, data processing, messaging, billing and expenses is explicit and documented.
8. Rollback, audit, deletion, incident response and support procedures exist.

**Next QA action:** run isolated tests, establish a product-only non-Codex workflow after review, and coordinate interface freeze with Principal Architect. Do not merge unverified work.

## Integrated synthetic QA checkpoint — 2026-11-06 (supersedes initial blocked source snapshot)

- **Consolidated PR:** #33, head `8a32d84286192462f79b02df9e0af3e9f6a67148`. QA/Experience/AI/Commercial/Principal files have been combined in a separate integration branch; original draft PRs remain preserved.
- **Verified:** Python standard-library product suite `76/76`, Node VM interaction/DOM suite `11/11`, Node syntax check and independent MONEYFALL verification all green on exact head; RRE run https://github.com/reppiks490/cash-flow-/actions/runs/42278062611. Tests cover synthetic lead intake, duplicate conflict/concurrency, narrow enums and PII-like invalid input, offline rule evidence, no-send draft, policy fixture revocation, CRM dry-run, mock evidence, no-verified-revenue accounting, HTTP negative routes and browser DOM/behavior checks.
- **Historical SEC-01 free-text risk:** mitigated for the *synthetic demo* by enumerated values and synthetic-prefixed references. Regex/enum allowlists are not a production PII filter or legal clearance. **No actual identity, authentication, tenancy, private store, verified consent or payment data controls are present.**
- **Not tested:** real browser layout/screenshots, threat-modeled auth/IDOR, production incident and audit handling, networked CRM/calendar/email/SMS systems, verified payment webhooks or full deployment. A green synthetic suite cannot clear a customer pilot.
- **Decision:** GREEN for *local-only synthetic baseline*; RED/BLOCKED for public hosting, paid customer onboarding, external messages, actual CRM/calendar writes or authenticated revenue attribution. Retain separate owner approvals for each live integration and expenditure.
