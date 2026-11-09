# RRE-04 — 12-minute HVAC buyer demonstration (synthetic only)

**Status:** operator rehearsal, NOT a production demo, live pilot, customer testimonial, or validated offer. **Ticket:** #88. **Evidence snapshot:** 2026-11-09. No external contact, payment, CRM write, or provider connection is authorized.

## Operator prerequisites and safety stop

Use a clean checkout of the PR's exact reviewed commit and follow `products/revenue_recovery/RUNBOOK_LOCAL.md` for Python 3.11+ and loopback-only startup. The runbook contains a historical candidate-branch instruction: **do not assume that branch is the latest main or the PR head**. Before a rehearsal, record the commit SHA and run the product unittest suite. Use the following commands from the repository root **after checking out the exact reviewed PR commit**, not a historical runbook branch:

```bash
git rev-parse HEAD
PYTHONPATH=products/revenue_recovery python -m unittest discover -s products/revenue_recovery -p 'test_*.py' -v
PYTHONPATH=products/revenue_recovery python -m backend.smoke
PYTHONPATH=products/revenue_recovery python -m backend.app --port 8765
```

For PowerShell, set `$env:PYTHONPATH = "products/revenue_recovery"` and replace `python` with `py -3`; run the same modules. In a **separate terminal** with the server running, record the response to `curl http://127.0.0.1:8765/health` and POST the following **fictional** payload twice, recording both HTTP status codes and response bodies:

```bash
curl -i -X POST http://127.0.0.1:8765/api/demo/leads -H 'Content-Type: application/json' -d '{"synthetic":true,"external_ref":"DEMO-001","source":"website","need":"AC not cooling"}'
curl -i -X POST http://127.0.0.1:8765/api/demo/leads -H 'Content-Type: application/json' -d '{"synthetic":true,"external_ref":"DEMO-001","source":"website","need":"AC not cooling"}'
curl -i http://127.0.0.1:8765/api/demo/recovery/DEMO-001
```

PowerShell users may use `curl.exe` for the commands above. Record **observed** status codes rather than assuming them; the replay is expected to be idempotent, but an expectation is not a result. Record the process exit code, timestamp, Python version, SHA, and sanitized console output. A green unit test or smoke run does not substitute for browser rehearsal. Open `http://127.0.0.1:8765/demo/` on the same computer only. If the route is absent, stop and record a blocker; do not invent a working screen. Never use a public tunnel, LAN bind, real contacts, CRM credentials, or customer examples.

**Opening statement, read aloud:** “Everything shown is fictional test data. We have not verified recovered revenue, live customer results, booked appointments, payments, or a deployed integration. This is an operator-supervised workflow demonstration, not a promise of business results.”

## Timed operator walkthrough (12 minutes)

| Clock | Action / screen | Observable evidence and explicit limitation |
|---|---|---|
| 00:00–01:00 | Show local-only address, recorded commit and synthetic banner. | Local browser does not establish authenticated tenant security or production readiness. |
| 01:00–02:30 | Click **Load synthetic examples**, select one of the three HVAC fixtures. | Fictional intake only; no prospect information. |
| 02:30–04:00 | Submit a synthetic lead through the local demo API, then repeat the same reference; show the idempotent result. | In-memory duplicate handling only, not durable or concurrent production guarantees. Use the runbook's allowed `source`, `need` and synthetic flag. |
| 04:00–05:30 | Inspect qualification, cited rule evidence and unknown fields. | Deterministic offline classification, not demonstrated live model inference or a conversion prediction. |
| 05:30–07:00 | Open recovery preview and review the proposed follow-up. | Draft is **unsent**. Operator approval, lawful consent and suppression checks would be required independently before any future delivery. |
| 07:00–08:00 | Inspect mock CRM and appointment preview. | No external CRM record, calendar booking, message, or provider confirmation. |
| 08:00–09:30 | Show synthetic scorecard and optional `closed_job_mock` timeline. | Mock closure is **not** paid revenue. No authenticated receipt or attributed closed-revenue proof. |
| 09:30–10:30 | Explain current boundaries and proposed $700/month managed-service hypothesis. | Unvalidated willingness to pay; no invoice, accepted quote, or actual margin. |
| 10:30–11:30 | Discuss incumbent tools and alternatives. | First check already-paid-for CRM automation before recommending a new subscription. |
| 11:30–12:00 | Capture **anonymous internal rehearsal** observations and gate decision. | No buyer identities, contact details, outreach, or CRM data recorded. |

If a step fails, mark **FAIL / not demonstrated** and continue with a clearly labeled static explanation, not a fabricated success. A screenshot, local run, or CI result must be independently recorded before claiming that specific evidence.

## Buyer objections: factual boundaries

- **“Jobber already follows up on quotes.”** Correct: Jobber documents quote automations on eligible plans. Ask whether the existing feature is enabled and adequate. Do not sell duplicate reminders as unique.
- **“Housecall Pro already handles our pipeline.”** Its plans and optional features overlap. The proposed wedge is an independently measured gap audit and operator review, not a replacement CRM.
- **“ServiceTitan or Hatch has AI follow-up.”** Both advertise relevant capabilities. Cross-tool reconciliation and traceable evidence would require a verified gap and authorized integration, neither demonstrated here.
- **“Will this make us $X?”** No forecast or guarantee. Synthetic counts and mock closed jobs cannot establish incremental paid jobs.
- **“Can it text customers or charge my card today?”** No. Delivery, billing, live connectors and collection are disabled or not integrated; any future activation needs owner authorization, legal/security review and QA signoff.
- **“Is $700 justified?”** Unknown. Compare actual incremental contribution and staff-time savings against all-in subscription, support and integration costs; avoid adding overlapping benefits twice.

Competitor source links and caveats: [COMPETITOR_EVIDENCE.md](COMPETITOR_EVIDENCE.md). Original offer and interview protocol: [PILOT_OFFER_AND_DISCOVERY.md](PILOT_OFFER_AND_DISCOVERY.md). The competitor evidence is vendor-published and time-sensitive, not independent performance validation.

## Outreach and compliance boundary

**Internal rehearsal only — do not send this script to prospects.** A human may *draft* a proposed future message for legal and owner review, but must not transmit it. Prior to any B2B email, review FTC CAN-SPAM requirements (including truthful headers, identification, a valid postal address and opt-out procedures) and any applicable state/channel-specific rules; a business recipient is not a blanket exemption. For calls/texts, independently assess TCPA, consent, suppression and vendor terms with counsel. Official FTC overview: https://www.ftc.gov/business-guidance/resources/can-spam-act-compliance-guide-business . This is a checklist, not legal advice or permission to contact anyone.

## Measurable decision gates (future, authorized study only)

**Rehearsal gate:** every planned step is demonstrated at a pinned commit with pass/fail notes, zero external side effects, and QA review. **Security gate:** authenticated tenant boundaries, private retention/deletion, audit trails, durable idempotency, consent/suppression and provider contract review pass independent tests. **Commercial discovery gate:** owner-authorized interviews document current CRM feature use, an actual unserved gap, staff time baseline, explicit willingness-to-pay, support burden and cancellation triggers; count only independently recorded interviews, never invented prospects. **Controlled pilot gate:** signed terms, channel permissions, written owner approval, QA signoff and verified costs precede real records. **Financial gate:** only authenticated paid receipts net of refunds, processor fees, hosting, support and acquisition costs count toward the $2,500/month recurring net-profit objective; mock events and verbal estimates count as zero verified receipts.

### Internal rehearsal scorecard (blank; do not prefill)

| Metric | Definition | Result |
|---|---|---|
| Steps executed | Count of the 10 timed segments with observed evidence | NOT RUN |
| Synthetic HTTP replay | Same reference returns idempotent result without second stored lead | NOT RUN |
| Outbound attempts | Any observed email/SMS/CRM write or payment request; target 0 | NOT RUN |
| Human-review draft | Draft clearly unsent and approval-gated | NOT RUN |
| Verified paid outcomes | Authenticated receipts and refund reconciliation; demo expected 0 verified | NOT RUN |
| Buyer interviews / willingness to pay | Only separately authorized, documented discovery | NOT AUTHORIZED |
| Independent QA signoff | Named reviewer and exact commit | PENDING |

**Release decision:** NOT PILOT-READY. The $700 price and $2,500/month net objective are hypotheses, not achieved results.
