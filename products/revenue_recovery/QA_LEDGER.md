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


## QA checkpoint — 2026-11-06, negative-path acceptance refresh

- **Scope:** QA-owned `tests/test_security_negative_acceptance.py` on isolated branch `qa/rre-negative-security-gates-20261106`, based on exact integration head `d13100cee849519d2c056df7bb9861b572389d58`. No changes to MONEYFALL or other products.
- **New checks:** reject unexpected contact fields and free-form categories, idempotent replay and 409 conflict, invalid JSON, untrusted Host/Origin, content type, absent send/booking/payment/tenant routes, no false appointment/payment claims, security response headers and traversal attempts.
- **Evidence:** New tests committed, CI outcome must be verified at the exact final head before asserting a pass. These tests do not exercise a real tenant authorization system because none exists. Passing 404 tests is **not** proof of tenant isolation.
- **Current product integration evidence:** CI run 42254916493 on separate feature commit `befbb5b4057c128dd2810257b128ce8fa893d07e` passed 46 tests and Node syntax check, but does not validate this QA branch.
- **Release status:** **NOT PILOT READY**. Authenticated tenant isolation, consent provenance, verified opt-out enforcement across integrations, real CRM/calendar receipts, external human approval audit, provider payment verification, secure private persistence, browser automation and deployment operations remain unimplemented or unverified.
- **Security limitation:** Allowlisted demo categories mitigate accidental input but are not a complete PII classifier or a production data protection mechanism.
- **Next QA gate:** confirm CI at this QA head; review draft integration PR #33 and new commercial PR #35; keep all PRs unmerged until complete review and production-gate evidence.
