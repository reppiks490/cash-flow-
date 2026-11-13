# RRE QA and release gate — 2026-11-06

**Release classification: NOT PILOT READY.** This ledger documents the available source and evidence, not a claim that the entire system has been integrated.

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


## QA checkpoint — 2026-11-13: browser source symlink-directory negative control

- **Main baseline:** `660149782e55e2b4286ce45f65b9f33da87d3ab1` (GitHub branch read on 2026-11-13). This ledger change does not modify the runtime or existing MONEYFALL verification.
- **Unmerged QA test:** [draft PR #272](https://github.com/reppiks490/cash-flow-/pull/272), exact head `d47e411f886a7c6f0660afbce0534bb2d05fa024`, stacked on QA #268 and Principal #266. A synthetic temporary-directory regression requires symlinked browser-source directories to fail closed with gate exit 2 before subprocess execution; the test explicitly skips if the OS forbids symlink creation.
- **Observed RED:** [Revenue Recovery Actions run 43476786786](https://github.com/reppiks490/cash-flow-/actions/runs/43476786786) failed its Python-test step: 312 tests, 1 failure, 3 skipped. Assertion: `0 != 2 : Symlinked browser-source directories must be rejected, not silently pruned from validation`. Browser syntax and interaction steps were skipped after the Python failure. This is a **reproduced regression failure**, not a green acceptance result.
- **Independent foundation check:** [MONEYFALL foundation run 43476786822](https://github.com/reppiks490/cash-flow-/actions/runs/43476786822) succeeded at the same PR head. That success does not clear the Revenue Recovery gate.
- **Reviews:** GitHub returned zero submitted reviews on PRs #266, #268 and #272 at this checkpoint. Do not merge the stack until a separate reviewer approves the exact combined head and all checks are green.
- **Principal follow-up:** [PR #273](https://github.com/reppiks490/cash-flow-/pull/273) addresses separate test-fixture module-name collisions from #271; it does **not** resolve the symlink-directory RED on #272. Do not conflate these defects.
- **Remaining release blockers:** reject unsafe symlinked source directories; demonstrate RED-to-GREEN exact-head CI; invoke the actual integration gate and real Node tests on the combined tree; independently verify native Windows process-tree containment; reconcile stacked branches without discarding unique commits; complete security and end-to-end pilot acceptance. **PILOT HOLD.** No verified customers, receipts, attributable revenue or $2,500/month net profit.
