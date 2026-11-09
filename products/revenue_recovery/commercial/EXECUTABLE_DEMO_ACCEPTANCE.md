# HVAC synthetic demo — executable evidence acceptance contract

Status: **proposed nonproduction acceptance criteria**, not an executed demonstration. Tracks RRE-04 #26 and draft PR #177. The PR #177 gate accepts caller-authored `DemoEvidence` assertions; it does **not** authenticate execution.

## Required independent test trace

A future local-only runner must invoke the actual checked-out product entry points and emit a machine-readable result **only after each assertion executes**. It must not accept prepopulated `passed=true` flags from a client or fixture as proof.

| Step | Required observable assertion | Prohibited inference |
| --- | --- | --- |
| synthetic_intake | A DEMO-/QA-prefixed, enum-only HVAC lead is accepted and duplicate replay is idempotent. | No real lead collected. |
| qualification_preview | The same reference produces deterministic, provenance-labeled qualification with unknowns preserved. | No model accuracy or conversion claim. |
| unsent_followup_draft | A review-required draft exists, with no outbound transport invocation. | No message was sent. |
| crm_dry_run | Preview is synthetic and has no external CRM mutation. | No CRM record created. |
| consent_revocation_rejection | Revoked mock consent suppresses the draft; negative control must fail if draft survives. | No legally verified consent. |
| zero_verified_receipts | Synthetic closure and appointment events leave authenticated paid receipts absent/unknown. | No actual collections, recovered revenue, or profit. |

## Reproducibility and failure handling

- Pin the repository commit SHA, Python/Node versions, exact invocation, exit code, and test log or CI run URL. Identify the fixture IDs, never real contact details.
- Bind the six results to **one invocation** with a generated local run ID. A caller cannot supply an already-passing trace.
- A nonzero exit, missing dependency, skipped step, mixed run, missing assertion, or unobserved outbound side-effect boundary must fail the acceptance gate.
- Execute negative controls for duplicate/missing trace steps, suppression failure, simulated outbound call, and forged `passed` flags.
- Keep the runner in a non-Codex, no-cost, offline environment; network-deny or instrument external transport entry points. Never enable billing or external communications.
- A green unit-test suite is not a browser visual audit, security certification, consent authorization, customer validation, or production readiness.

## Commercial acceptance and release classification

The demonstration is an **M1 synthetic demonstration** until the runner and exact-head integration tests are independently reviewed. M2 pilot candidacy additionally requires tenant isolation, private persistence, authenticated operator approvals, consent audit, secure provider adapters, legal review, and QA release signoff. M3/M4 require separate owner authorization.

The hypothetical $700/month price and five-customer/$3,500 gross scenario are not verified sales. The $2,500/month net target requires authenticated customer receipts, refunds, direct and allocated costs, and a specified accounting period. Unknown inputs must produce **unknown**, never $0 profit or a success claim.

## Coordination

Principal/QA should implement and verify the runner against current integration contracts; Commercial will review the buyer-facing claim classification and the exact evidence packet. Do not merge draft #177 merely because its structural validator passes. Preserve all original PR branches and histories.
