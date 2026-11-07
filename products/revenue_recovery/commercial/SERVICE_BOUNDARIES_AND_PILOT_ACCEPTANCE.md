# HVAC pilot service boundaries and acceptance contract (draft)

**Classification:** unvalidated internal proposal; synthetic demonstration only. Supports RRE-04 #26. This is not a signed agreement, SLA, production authorization, customer offer, or legal advice. No prospect contact or real customer data is permitted.

## Scope and responsibility matrix

| Capability | Current synthetic demo | Proposed controlled pilot prerequisite | Responsible party |
| --- | --- | --- | --- |
| Intake and deduplication | Enum-only fixture intake | Authenticated tenant, lawful data access, durable private storage and replay protection | Product operator |
| Qualification and follow-up | Deterministic rule evidence and **unsent** drafts | Rule acceptance, consent provenance, operator review and suppression audit | Product drafts; contractor approves |
| Scheduling | Mock appointment only | Approved calendar sandbox, least-privilege credentials, reconciliation and rollback | Contractor owns actual booking |
| CRM | Dry-run preview only | Vendor contract, tenant mapping, scoped permissions, idempotency and error recovery | Contractor owns CRM source of truth |
| Email/SMS | **Disabled** | Counsel-reviewed channel rules, lawful permission, verified opt-outs, authenticated per-message approval | Contractor controls recipient and final authorization |
| Payments | **Disabled** | Owner-signed terms, verified merchant configuration, cancellation/refund policy, reconciliation | Merchant/owner; no prototype charges |
| Attribution | Synthetic stages, zero authenticated receipts | Settled unique receipts, refund ledger, declared baseline/window and collision policy | Contractor supplies source records; operator reconciles |

**No autonomous sends, guarantees of incremental jobs, payment collection, or production-grade support are included.** Human approval alone never substitutes for lawful consent. Any failed prerequisite means HOLD, not degraded live operation.

## Proposed pilot boundaries (not activated)

A future 30-day evaluation would define a single HVAC business/location and authorized channels in signed scope. Start with a zero-real-data walkthrough. Before introducing real data, obtain separate owner approval, privacy/security review, data-processing terms, vendor rights, tenant isolation proof and QA release acceptance. Agree on intake volume cap, supported hours, staff review capacity, allowed record categories, source-of-truth systems, exclusions, deletion and incident response. No unlimited ingestion, implied 24/7 coverage, automated dispatch, or promise of uptime.

The $700/location/month figure is a **pricing hypothesis**, not a quote or charge. Proposed commercial terms must separately specify billing start, invoicing cadence, taxes, service credits if any, renewal, cancellation notice, refund eligibility, data export/deletion and responsibility for third-party provider fees. All are **UNSET** until signed owner-approved terms; never silently choose defaults. No billing integration may be activated by this document.

## Service-level and incident decision gates

| Item | Current commitment | Required before production |
| --- | --- | --- |
| Availability / uptime | None | Measurable SLO, monitoring, maintenance window, exclusions, escalation |
| Support response | None | Named hours/timezone, severity definitions, measured response objective and contact route |
| Incident response | Not operational | Private escalation channel, breach assessment, notification duties reviewed by counsel, tabletop exercise |
| Backup / restore | Not established | Encrypted backup, retention and tested restore with RPO/RTO evidence |
| Consent / suppression | Synthetic fixture only | Durable source and revocation audit, race/idempotency tests, channel-specific legal review |
| Data deletion | Not established | Documented retention schedule, access-controlled deletion and verified audit |
| Billing dispute | Charging disabled | Signed cancellation/refund policy, processor reconciliation and chargeback ownership |

No response-time or uptime number is advertised before operational measurement. The pilot must have a documented stop switch: on consent ambiguity, cross-tenant access, unknown recipient, duplicate provider send, unauthorized charge or receipt provenance failure, **stop external action**, preserve private audit evidence, notify the authorized operator through an approved channel and require manual remediation.

## Acceptance evidence and measurement

Record each acceptance decision against an immutable source revision, QA run and reviewer. For a future authorized pilot, pre-register cohort, eligibility, observation window, review labor, verified send and booking IDs, paid-job receipts, refunds, acquisition costs and support hours. Deduplicate financial events by tenant and settlement ID; keep contractor collections separate from RRE subscription receipts. Compare with baseline cautiously; observational attribution is not causal proof. Missing records are **unknown**, never zero sales or successful outcomes.

Commercial go/no-go requires: (1) buyer confirms an uncovered workflow gap after existing CRM features are checked; (2) operator can review drafts within a measured capacity; (3) legal/security/provider and QA gates pass; (4) cancellation/support terms are signed; (5) owner explicitly approves each external action and any spend. Until all pass, the only permitted use is offline synthetic demonstration.

## Related source of truth

Read [PILOT_OFFER_AND_DISCOVERY.md](PILOT_OFFER_AND_DISCOVERY.md), [UNIT_ECONOMICS_AND_KPIS.md](UNIT_ECONOMICS_AND_KPIS.md), [MEASUREMENT_PROTOCOL.md](MEASUREMENT_PROTOCOL.md), and [PROJECT_LEDGER.md](../PROJECT_LEDGER.md). The demo packet in draft PR #90 and decision matrix in draft PR #105 require independent reconciliation; this document does not supersede or merge either.

**Current evidence:** no authorized live pilot, authenticated commercial receipts, verified paying customers, or verified $2,500 monthly net profit. No emails, charges, vendor calls, customer records or deployment were performed to prepare this document.
