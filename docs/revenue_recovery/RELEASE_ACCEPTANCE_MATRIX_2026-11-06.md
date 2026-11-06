# RRE release acceptance / next-task matrix — 2026-11-06

**Ownership:** Principal integration + QA handoff. **Current status:** integration-only synthetic demonstration, not a customer pilot. See draft PR #33 and its stacked follow-up from `feature/rre-pipeline-evidence-hardening-20261106`. Do not merge based solely on an unrelated MONEYFALL green check. All code work uses regular ChatGPT/GitHub tools, not Codex.

## Evidence-driven acceptance matrix

| Requirement | Actual implementation | Test class | Release grade |
|---|---|---|---|
| Local lead intake, synthetic categorical data, idempotent ref | `backend/app.py` | `backend/test_app.py`, `tests/test_http_contract.py` | Local demo only |
| Offline rubric and source evidence | `backend/qualification.py` + `ai_providers.py` | `backend/test_ai_systems.py` | Mock/synthetic |
| Unsent draft gated by review/unknown consent | `backend/followups.py` | AI and HTTP integration tests | No sending capability |
| Same-origin browser and local example seeding | `web/`, `backend/app.py` | Python HTTP tests and Node VM interaction tests | No real customer data |
| CRM mapped preview | `backend/crm.py` | `web/test_experience.py` | No CRM write or vendor auth |
| Appointment/closed-job scenario timeline | `backend/demo_evidence.py` | `test_demo_evidence.py`, `test_evidence_http.py` | Pure fixture; no appointment/job evidence |
| Financial scorecard | `backend/demo_evidence.py` + `web/app.js` | Same tests and Node VM | No authenticated receipts, real customer count unknown |
| Raw URL logging suppression | `backend/app.py` | `test_evidence_http.py` | Local PII minimization, not production audit |
| Hypothetical subscription economics | `commercial/economics.py` | `commercial/test_economics.py` | Not actual income |
| No-Codex CI | `verify-revenue-recovery.yml` | GitHub Actions evidence and job logs | Must verify exact PR commit |

## Critical blockers for a real pilot (not waived by demo tests)

**P0: no real customer ingestion until all are complete.**

1. **Security / tenancy:** Choose a production hosting and private datastore; build authenticated organization-scoped sessions, authorization roles, encrypted state and backups. Threat-model IDOR, CSRF, tokens, XSS, browser content security policy, rate limits, and redacted immutable audit access.
2. **Consent/suppression:** Implement channel-specific consent/provenance, revocation handling, updated contact eligibility at send time, lawful-purpose classification and operator approval. Review FCC, FTC, state-level laws and provider terms with qualified counsel; see `docs/revenue_recovery/PARALLEL_MARKET_COMPLIANCE_RESEARCH_2026-11-06.md`.
3. **Actual provider contracts:** Integrate one approved CRM/calendar/telephony/email/SMS provider in a private environment using its documented API; store credentials only in secrets management. Never claim real bookings based on fixture events.
4. **Receipt-based attribution:** Use signed/authenticated payment source, tenant-scoped immutable event IDs, stable refund linkage, deduplication, invoice/booking state reconciliation and expense/labor accounting. Cross-platform attribution must explicitly represent uncertainty and competing causes.
5. **Customer validation:** Owner-approved business discovery, actual buyer willingness to pay, written agreement, operating-hours/service commitments and truthful pitch. `$700/month` is a hypothesis, not established market value.
6. **Ops hardening:** Monitoring, retention/deletion, incident response, backups and restore drills, billing reversals, human override, load/security/visual-browser tests, accessibility, and vendor-specific integration failure handling.
7. **Approval gate:** Owner must authorize any live external contact, customer-data import, paid service spend, payment activation or deployment **separately**. No blanket authorization is implied by an active GitHub PR.

## Ordered tickets for next engineering sessions

- **RRE-P1:** QA reviews latest integration stack and added evidence/JS CI, verifies exact head SHA and test logs, signs off **only on synthetic M1 demo**, not commercial release.
- **RRE-P2:** Principal designs tenant+identity contracts, private storage and migration plan in a separate branch; maintain synthetic-only service until production controls pass.
- **RRE-P3:** AI and Experience expand exception review and opt-out simulation under explicit no-send controls. Any public route must remain read-only unless synthetic and safe.
- **RRE-P4:** Commercial validates CRM incumbent feature overlap against actual customer plan/tier; record discovery only with owner authorization, not in public repo.
- **RRE-P5:** QA implements browser accessibility/visual testing and adversarial tenancy/suppression coverage before any real pilot.
- **RRE-P6:** Approved pilot agreement, lawful contact basis, source-of-truth audit, and provider credentials stored privately; **blocked pending authorization**.

**No action here sends outreach, provisions a production service, starts billing, grants Claude permissions, or makes any changes outside this project.**
