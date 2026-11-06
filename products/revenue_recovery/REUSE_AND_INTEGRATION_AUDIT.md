# RRE architecture and reuse audit — 2026-11-06

**Scope:** repository observation only, no code copied from MONEYFALL or ICARUS. The project remains a standalone Python 3.11+ standard-library demo. Do not construe source visibility as a redistribution license.

## Audited sources and reuse decisions

| Source | Observed | Decision |
|---|---|---|
| cash-flow-/src/moneyfall/discovery.py, scoring.py, sources.py | Existing modules in separate MONEYFALL application; APIs and rights have not been deeply audited | **No imports or code reuse** until tests, dependency graph, interface review and explicit authorization |
| cash-flow-/src/moneyfall/orders.py, store.py, private.py | Existing order/storage/private-boundary modules | **No imports or customer records**; cash-flow receipts are not evidence for RRE |
| cash-flow-/src/moneyfall/network.py, launch.py | Existing external/network/launch surfaces | **No reuse** in synthetic demo to prevent side effects |
| reppiks490/Icarus/LICENSE.md | Explicit proprietary/all-rights-reserved notice; public visibility does not grant reuse | **Read-only reference only**. No ICARUS runtime, market data, trading logic, vendor data, assets or secrets copied. |
| Python stdlib http.server, threading, json, unittest | Available under Python licensing, no third-party runtime dependencies | Suitable only for local synthetic prototype, **not** public-facing service |

The repository itself may contain third-party components and distinct license terms; no blanket licensing assertion is made. Prior to reuse, inspect exact files and dependency licenses, data redistribution terms, ownership, security impact and regression coverage. Prefer a clean interface instead of importing modules from another product.

## Contract freeze v0.1a (synthetic-only, not production API)

- GET /health -> synthetic-only status.
- POST /api/demo/leads accepts exactly synthetic=true, external_ref, source, need. external_ref is a short ASCII token, not a name/phone/email. source is one of demo, website, phone, referral. need is one of AC not cooling, AC maintenance, repair, maintenance, estimate follow-up, heating issue. Reject free text and unknown fields.
- Duplicate external_ref returns existing record without creating a new lead; GET /api/demo/leads lists process-local records. No auth, persistence, external action or revenue claim.
- All routes bind only 127.0.0.1. No customer data, deployment, or use over a public tunnel is authorized.
- No current routes for qualification, drafts, scheduling, CRM or payment. AI/Experience/Commercial must not assume such APIs exist.

**Breaking-change policy:** Freeze the above for QA #30. Additional workflow endpoints require contract review in #23 and corresponding negative/security tests. The existing browser UI PR #28 can consume GET /api/demo/leads but must not imply fixture fallback is real data.

## Highest-priority integration sequence

1. Principal bootstrap PR #31: review code, test allowed-value and PII-negative cases, then merge only after non-Codex RRE CI proves it. QA PR #30 is currently stacked on principal's branch; rebase/retarget only after verifying dependency and tests.
2. AI #24: define pure deterministic qualification/draft functions consuming v0.1a lead dictionaries. Return synthetic/evidence/consent flags, never send.
3. Experience #25 / PR #28: map synthetic lead queue to dashboard; avoid invented appointments, paid outcomes or verified cash.
4. Commercial #26 / PR #29: synthetic workspace only, nonbinding prices, billing and sending hard disabled.
5. QA #27 / PR #30: add test discovery for isolated RRE modules, contract security negatives and full end-to-end test. Record actual CI run ID and head SHA. Never use MONEYFALL's existing green workflow as RRE acceptance.

## Explicit M0/M1 acceptance gates

- M0: clean checkout, Python 3.11+, run PYTHONPATH=products/revenue_recovery python -m backend.app --port 8765, health 200, synthetic POST 201, duplicate POST 200, list shows one, forbidden PII/unknown fields rejected, tests pass on exact PR commit.
- M1: synthetic intake -> deterministic qualification with evidence -> reviewable unsent draft -> mock appointment/CRM acknowledgment -> dashboard -> clearly zero verified revenue. Requires integrated PR and end-to-end CI evidence, **not achieved yet**.
- M2: authenticated tenant separation, private durable storage, suppression and consent, audit logging, production provider contracts, legal review, signed receipts, incident response, approved spend and operator authorization. **Not achieved.**

**Business outcome:** verified subscription customers, payments and net profit remain unestablished. A $2,500/month target is not a guarantee or a test result.
