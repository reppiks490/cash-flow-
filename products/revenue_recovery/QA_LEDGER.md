# RRE QA and release gate — 2026-11-06

**Release classification: NOT PILOT READY.** This ledger documents the available source and evidence, not a claim that the entire system has been integrated.

## Current release gate — 2026-11-06 (supersedes historical snapshots below)

**Overall: NOT PILOT READY.** Scope is a *local-only synthetic HVAC demonstration*.
This section is a time-stamped snapshot of `main` at `d8ab6c9bb8fc891cb2bd451e519b2508804d4c76`;
reinspect `main` for subsequent concurrent merges before making a release decision.
This update records repository/CI evidence, not production approval.

| Gate | Exact source and measured outcome | Disposition |
| --- | --- | --- |
| Current `main` synthetic integration | `d8ab6c9bb8fc891cb2bd451e519b2508804d4c76`, after strict JSON ingress and financial input guard integration; [RRE Actions 42284340962](https://github.com/reppiks490/cash-flow-/actions/runs/42284340962) **123/123 Python**, **11/11 Node**, JS syntax passed; [MONEYFALL foundation 42284340896](https://github.com/reppiks490/cash-flow-/actions/runs/42284340896) passed separately. | PASS — synthetic demo only |
| Strict JSON ingress | `main` now rejects duplicate JSON keys and NaN/Infinity, with new Principal smoke/ingress tests. This was **merged by the Principal lane**, not a QA authorization for external data. | PASS — demo ingress |
| ASCII reference validation | QA draft [#63](https://github.com/reppiks490/cash-flow-/pull/63), test-only SHA `fc3b416c6d8556e10742293d8cfbd3aa4b28429f`; [RRE 42283741728](https://github.com/reppiks490/cash-flow-/actions/runs/42283741728) **RED** (95 Python tests executed, eight failed subtests): `re.I` allows U+212A, U+0130, U+0131, U+017F despite ASCII-token contract; HTTP returns 201 and persists them. | FAIL — Principal owns regex fix; do not merge red QA alone |
| Offline commercial calculator | Commercial draft [#60](https://github.com/reppiks490/cash-flow-/pull/60), revised SHA `58010c4ecb701b936fa9300aad2e7fcda6082500`; [RRE 42283657685](https://github.com/reppiks490/cash-flow-/actions/runs/42283657685) **98/98 Python**, **11/11 Node**, JS syntax passed. Earlier SHA `8e230f1` failed product CI on test import and was corrected. | PASS — branch-only synthetic economics; no authenticated receipts |
| Commercial onboarding forward-port | [#58](https://github.com/reppiks490/cash-flow-/pull/58) was merged by another contributor; its last inspected branch head `66d9105104860ee9df6ce9285919410eff6de082` passed [RRE 42284002373](https://github.com/reppiks490/cash-flow-/actions/runs/42284002373) **119/119 Python** and **11/11 Node**. The later `main` head above is independently green; mock onboarding has no external activation. | PASS — merged synthetic-only code; not a pilot release |
| Opt-out, authentication, tenancy | Consent revocation is a *stateless mock fixture*; no production verified suppression source, identity provider, tenant row-level authorization, or private persistent storage. HTTP 404 for missing auth/tenant routes is not a security test of an implemented system. | BLOCKED |
| CRM, bookings and communications | No authorized live provider, authenticated human review/send, real appointment confirmation or reliable audit pipeline. | BLOCKED |
| Attributed receipts and $2,500/month NET target | No authenticated receipts, actual subscriber counts, refunds, expense reconciliation or verified net profit. A hypothetical 5×$700 scenario is not customer revenue evidence. | BLOCKED |
| Real browser, threat model, operations | No full browser visual/accessibility/security signoff, secure deployment review, incident response/rollback, retention or deletion process. | BLOCKED |

**Outstanding QA actions:** (1) replay unchanged #63 regressions against a
Principal-owned ASCII regex correction; (2) review/merge only safe, green,
scope-limited PRs after owner-approved gates, preserving all branches; (3)
build negative-path auth/tenant/consent/receipt tests when real contracts
arrive; (4) maintain exact-head Python/Node/MONEYFALL evidence separately.

**Boundaries:** no Codex; no secrets or customer PII in public GitHub; no live
outreach, billing, CRM/calendar actions, deployment, expenditures or trading.
Do not translate a green synthetic suite into pilot or commercial readiness.

## Historical evidence (retained for provenance)

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
