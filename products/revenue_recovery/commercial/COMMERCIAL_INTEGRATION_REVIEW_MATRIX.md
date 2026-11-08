# RRE-04 commercial integration review matrix — 2026-11-08

**Classification:** synthetic-only integration decision aid; not independent approval, QA signoff, pilot authorization, verified revenue, or production readiness. Base `main`: `660149782e55e2b4286ce45f65b9f33da87d3ab1`. Source of truth for project boundaries: `../PROJECT_LEDGER.md`. Tracks #26.

## Review queue and contract dependencies

| Draft PR | Proposed change | Exact-head dependency / integration concern |
| --- | --- | --- |
| #145 | Pilot KPI definitions | Rename ambiguous “attributed recovered revenue” to observational **associated settled contractor receipts**; keep estimated incremental effect separately unavailable without causal design. |
| #150 | Attribution and accounting rules | Agree on stable tenant-scoped receipt IDs, refund revisions and vendor-vs-contractor cash separation before adopting KPI vocabulary. |
| #152 | Synthetic receipt association classifier | Classification is **association only**, never proof of incremental recovered revenue. Cross-tenant, duplicate, unverified and confounded cases must fail closed. |
| #158 | Synthetic vendor cash/economic net calculator | Inputs are **vendor** collections, not contractor receipts. Define whether settlement fields are gross or already net of fees/refunds; do not subtract twice. Imputed owner labor excludes paid hours. |
| #161 | Crosswalk of #145/#150/#152/#158 | Proposed vocabulary and ten acceptance cases are a coordination contract, **not** automatically implemented checks or independent approval. |
| #154 | Synthetic pilot self-attestation | A passing synthetic checklist cannot authorize production, contact, billing or collection of real data. |
| #163 | Synthetic onboarding checklist | Six strict booleans are self-attested; no operator identity or independent evidence. Never upgrade demo-ready to live-ready. |
| #164 | Offline buyer discovery protocol | Future interviews require owner approval; evidence grades H/D/I/O/F/C are **not** interchangeable; $700 remains a hypothesis. |

## Safe integration sequence (proposal, not permission)

1. Independent QA/Principal review of #161 terminology, with explicit decisions on the KPI label in #145 and accounting inputs in #158. Authors preserve original branches and make any corrections on their own PR heads.
2. Review #150 and #152 together against the approved vocabulary. Re-run the *exact updated head* non-Codex workflows and negative cases for duplicate receipts, cross-tenant joins, unknown evidence, refunds, and confounding.
3. Review #158 against the agreed gross/net settlement and labor allocation rules; require independent test of noncanonical inputs and synthetic-only verification flags.
4. Review #154 and #163 as **two separate** fail-closed self-attestation interfaces; do not treat either as a release authorization or infer that they are integrated with authenticated operators.
5. Review #164 and #145 as offline documents; no interviews, prospect contact, real-data collection, or activation from documentation.
6. Only after scope review, independent approval, conflict review, and successful non-Codex CI on the **actual integration commit** may an authorized integrator merge eligible nonproduction changes. Green PR-head CI alone is insufficient.

## Explicit unresolved acceptance evidence

- No independent reviews were recorded on #164 when inspected on 2026-11-08. Other PR review state must be refreshed at integration time.
- Existing GitHub Actions success on PR heads is **not** proof of cross-PR integration tests, actual browser/mobile QA, authenticated tenant boundaries, operational CRM/calendar/email, or merchant billing.
- Future financial claims require authenticated private subscription settlements, refunds/chargebacks, operating costs and period-specific reconciliation; contractor job receipts are separate. Causal recovery claims require defensible comparisons, not merely workflow-linked jobs.
- No verified paying customers, outreach, live sends, production deployment, receipts, or $2,500/month net profit are established by this matrix.

**Stop conditions:** Any missing independent approval, ambiguous financial terminology, live integration, customer PII, payment activation, outbound send, production deploy, or prohibited automation means HOLD. Preserve all original PR branches and commits; no force push or automatic review bot.
