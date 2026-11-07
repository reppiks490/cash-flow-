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

## Current-main QA evidence checkpoint — 2026-11-07 (supersedes historical source snapshot)

- **Inspected main:** `418a6bc1747fcff654b5621fae896531895ec5ca` (2026-11-07 06:24 UTC). The original opening snapshot in this ledger predates the merged synthetic M1 baseline and must not be interpreted as the current tree.
- **PR #121** (compound HTTP Host/framing rejection): exact head `39e502a58b0a67666fe7b787c4301b3fbd53e5cc`; product workflow [42348693465](https://github.com/reppiks490/cash-flow-/actions/runs/42348693465) and independent MONEYFALL workflow [42348693455](https://github.com/reppiks490/cash-flow-/actions/runs/42348693455) both report `completed/success`. This is **CI PASS** for that commit only, not independent review or production sign-off. The PR is still draft/unmerged at inspection.
- **Security coverage represented in #121:** duplicate Host + ambiguous framing, invalid port + Transfer-Encoding, duplicate/malformed Content-Length, rejection without synthetic store mutation, canonical intake and replay. The tests use loopback-only ephemeral HTTP and standard-library tooling. CI success does not prove full HTTP request-smuggling resistance under reverse proxies or production server stacks.
- **Current source review:** `backend/app.py` continues to define a process-local `DemoStore`, bounded synthetic enum inputs, an unsent offline draft preview and zero verified payment receipts. None of these are authenticated customer records, confirmed appointments, or financial receipts.
- **Open PR inventory:** numerous historical stacked/draft RRE PRs remain. Green checks on a historical head do not establish current-main merge safety; require current diff, conflict and independent-review assessment before reconciliation. Preserve all source branches and unique commits.
- **M2 release gate:** **HOLD / NOT PILOT READY**. Production tenant authentication/authorization, durable private storage, real consent and suppression, external integration safety, verified receipt attribution, privacy/legal review, operational response/rollback and explicit owner authorization remain unverified. No claim of $2,500/month net profit or customer revenue is supported.
- **QA next:** independently review exact-head #121 and its interaction with current main, then add adversarial multi-request connection/framing tests and authenticated tenant isolation tests when the corresponding production contracts exist. No live traffic, PII, outreach, spending or deployment.
