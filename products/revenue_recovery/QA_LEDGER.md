# RRE QA and release gate — 2026-11-06

**Release classification: NOT PILOT READY.** This ledger documents the available source and evidence, not a claim that the entire system has been integrated.


## Current QA checkpoint — 2026-11-06 (integration-follow-up PR #37)

**This section supersedes the historical source snapshot below.** Older
notes describe bootstrap conditions, not the current integration.

- **Integration head:** PR #37 commit 2782d4c569f56acaaa9c033c78929ae345985b30.
  Product GitHub Actions run https://github.com/reppiks490/cash-flow-/actions/runs/42257662573
  concluded success on that exact commit. Tests were synthetic-only; this is
  not production security or full browser evidence.
- **Separate QA stack:** PR #44 commit 252eb043e0d19fc057c66554559c00963c004900
  has a successful product run at
  https://github.com/reppiks490/cash-flow-/actions/runs/42274693872 .
  It does not validate PR #37's different branch tree.
- **This QA branch:** tests/test_policy_attribution_negative.py adds six tests:
  policy modes never authorize contact; mocked revocation suppresses its own
  draft; separate recovery stays unsent; fake payment/privileged POSTs return
  404 with unchanged scorecard; mock closed jobs do not have verified receipts;
  PII, forged receipt fields, invalid tenant claims and policy paths fail.
  **Execution on this branch: PENDING** until its workflow completes.
- **Consent blocker:** revoked_mock is read-only and not persisted. A separate
  GET /api/demo/recovery/{ref} still generates an UNSENT review draft after
  simulated revocation. Implement durable tenant-specific suppression plus
  authenticated human approval and fresh checks before any real transport.
- **Authorization blocker:** synthetic GET /api/demo/leads lacks auth;
  tenant_id is rejected and there is no tenant model. A missing tenant route
  proves absence of implementation, not isolation or authorization.
- **Attribution blocker:** mock appointments, closed jobs and subscription
  values are not authenticated provider receipts or recovered collections.
  Observed verified revenue/profit evidence remains absent.
- **Release classification:** NOT PILOT READY; no deployment, live data,
  messaging, billing, paid services, trading or Codex. Draft PRs must not
  merge solely on passing prototype tests.

## Historical source snapshot

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
