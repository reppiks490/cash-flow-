# RRE release boundary contract — v0.1 (2026-11-06)

Status: **design and acceptance contract only**, not an implemented production security boundary. Scope: HVAC Revenue Recovery Engine; all demo records synthetic. This document does not authorize customer data, outreach, deployment, billing or external integration.

## Non-negotiable deployment invariants

1. Demo endpoints must bind to loopback only. An external network interface, tunnel, reverse proxy or public host is not an approved configuration.
2. The `synthetic` boolean and DEMO-/QA- identifiers are **not** proof of non-PII. No real lead/customer data is permitted.
3. All real-world mutations (send, calendar booking, CRM write, charge, refund) are unavailable until separate explicit owner authorization, authenticated operator identity, tenant authorization, consent and suppression evidence, provider permission, idempotency and durable audit are implemented and independently reviewed.
4. Draft generation never implies consent, operator approval, transmission, appointment confirmation, completed job or paid receipt.
5. Hypothetical pricing and synthetic job values must not enter verified revenue/profit totals. Without authenticated receipts and reconciled costs, verified net profit is **unknown**, not $2,500 and not a calculated estimate.
6. Never import ICARUS trading code/data or modify MONEYFALL ZERO or Everbloom. No Codex agents, workflows, CLI, review or tokens.

## Proposed v1 boundary (not implemented)

Every future persisted record is scoped by an authenticated `tenant_id` derived **server-side** from the session, never trusted from request JSON or URL alone. The data layer must enforce tenant filtering independently of the HTTP handler. Authorization checks are required for reads, writes, exports and background jobs. Deny on missing, invalid, expired or cross-tenant identity. Private persistence requires encryption at rest, encrypted transport, backup/restore tests, retention and deletion policies, least-privilege credentials and incident response.

Outbound action gate: `operator_authenticated && tenant_authorized && approval_bound_to_exact_draft_revision && lawful_channel_consent_verified && !suppressed && recipient_verified && idempotency_key_unique && provider_enabled_by_owner`. A failure or unknown for any predicate **must deny**. Approval and consent are separate events, each with actor, source, timestamp, purpose, channel and immutable audit reference. This is a specification, not a claim of legal compliance.

Revenue attribution requires a real provider receipt identifier, verified settlement/status, tenant, job, currency, refund/chargeback reconciliation and an explicit attribution rule. Count a receipt once; never sum a pipeline estimate with a settled payment. Net profit requires validated recurring revenue less documented operating costs, fees, refunds and taxes according to a declared accounting convention.

## Executable acceptance checks to implement before pilot consideration

| ID | Test | Required result |
| --- | --- | --- |
| RB-01 | Start demo with a non-loopback bind | Process refuses to start |
| RB-02 | POST raw email/phone/name or unknown JSON fields | 4xx, no storage, no raw sensitive logging |
| RB-03 | Reuse same idempotency ref with conflicting payload | 409, original unchanged |
| RB-04 | Cross-tenant read/write/export/background task with valid other-tenant credentials | Denied at handler **and** storage boundary |
| RB-05 | Missing/expired/forged session, spoofed tenant header | Denied; no fallback tenant |
| RB-06 | Draft without consent, suppressed contact, or revoked consent | No send; immutable denial audit |
| RB-07 | Human approves revision A, text changes to revision B | Approval invalidated; no send |
| RB-08 | Retry provider action with identical idempotency key | At most one external side effect; durable evidence |
| RB-09 | Simulated booking or job closure without provider proof | Display as mock only; zero verified receipts |
| RB-10 | Duplicate/refunded/failed/unsettled receipts | Never counted as net realized revenue |
| RB-11 | Database backup/restore and tenant deletion | Documented recovery and erasure tests |
| RB-12 | CI exact PR head and merged head | Python + Node + MONEYFALL regression green; no Codex |
| RB-13 | Browser desktop/mobile keyboard and accessibility smoke | Recorded real-browser results, not Node VM alone |

## Gate owners

Principal: identity/data architecture, common contracts, ingress, and this release boundary. AI: reviewable drafts and no-send enforcement. Experience: UI evidence, CRM dry-run and accessibility. Commercial: receipts/cost provenance and owner-controlled onboarding. QA: negative tests, threat model and exact-head release verdict. Cross-lane contract changes require review through RRE-01.

**Current status:** the integrated M1 synthetic demo is already on main; this document does not recreate it. Existing Python/Node checks demonstrate bounded synthetic behavior only. RB-04 through RB-11 and RB-13 remain unverified as production controls. No verified customers, receipts or net profit.


## External communications compliance research boundary (not implemented)

Before any prospective U.S. commercial-email pilot, obtain counsel and documented sender/recipient/channel approval. The FTC's [CAN-SPAM Act compliance guide](https://www.ftc.gov/business-guidance/resources/can-spam-act-compliance-guide-business) states that commercial messages are covered, including business-to-business email; sender identification, truthful messaging and functioning opt-out handling require separate implementation and legal review. The [FTC's statute overview](https://www.ftc.gov/legal-library/browse/statutes/controlling-assault-non-solicited-pornography-marketing-act-2003-can-spam-act) is a primary source. These references do not cover all telephone/SMS, state privacy, consumer-protection, recordkeeping, or service-provider requirements. Never infer that a synthetic consent flag, mock revocation or offline approval template authorizes contacting a real person. No outbound adapters are added by this document.

The ASCII reference contract uses Python `re.IGNORECASE | re.ASCII` because the [official Python regular expression reference](https://docs.python.org/3/library/re.html) documents that `IGNORECASE` with `[A-Z]` also matches several non-ASCII Unicode letters unless `ASCII` is specified. This is an internal demo-identifier validation constraint, **not** a privacy guarantee.
