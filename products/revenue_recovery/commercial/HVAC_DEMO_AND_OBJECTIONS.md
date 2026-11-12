# RRE-04 — HVAC synthetic demo, objections and pilot decision gate

**Issue:** #88 · **Classification:** internal operator packet / unvalidated hypothesis · **Updated:** 2026-11-12

**Hard stop:** No outreach, real prospect intake, customer data, provider authentication, billing, public deployment or real appointment booking is authorized. This is a local-only synthetic demonstration. All outcomes shown are fixtures, not verified customers, conversions, receipts or recovered revenue.

## Preconditions (operator checks before demonstration)

- Use only the existing product local-run instructions in `products/revenue_recovery/RUNBOOK_LOCAL.md`; bind to loopback only. If instructions, server or fixtures are missing, stop and record the blocker rather than improvising a hosted demo.
- Check that every record is explicitly synthetic, no live connector credentials are configured, and any outbound/charging controls remain disabled.
- Open the merged dashboard and available synthetic workflow. If a screen or API is absent on the current checkout, mark that step **not demonstrated**, not passed.
- Consult [pilot offer](PILOT_OFFER_AND_DISCOVERY.md) and [competitor evidence](COMPETITOR_EVIDENCE.md); this packet supplements rather than supersedes either.

## Twelve-minute internal walkthrough (timeboxes are targets, not observed execution)

| Time | Operator action | Evidence to show | Stop / caveat |
|---|---|---|---|
| 0:00–1:00 | State the synthetic-only disclaimer and operator approval requirement | Visible synthetic markers; local-only URL | Do not imply live customers or AI autonomy |
| 1:00–3:00 | Load bundled HVAC fixture inquiries | Fixture identifiers and provenance | Never paste a genuine name, phone or email |
| 3:00–4:30 | Replay a fixture and show idempotency/deduplication | Same input does not create a second lead | If duplicate control fails, stop and log failure |
| 4:30–6:30 | Inspect qualification evidence, unknowns and suppression case | Rule rationale; unknown consent and revoked-consent handling | No consent fixture authorizes real contact |
| 6:30–8:00 | Inspect unsent follow-up and mock CRM path | Review-required draft; dry-run result | Never click/send a live communication |
| 8:00–9:30 | Inspect mock appointment and attributed pipeline stages | Appointment unverified; synthetic closure distinguished from receipt | Never label estimated value as collected |
| 9:30–11:00 | Show financial assumptions and operating costs | Hypothetical $700/month and buyer break-even, where available | No combined ROI or verified net claim |
| 11:00–12:00 | Explain missing production gates and collect **internal** evaluation notes | QA checklist and decision record without PII | No prospect outreach or paid offer |

If a feature exists only in a draft PR, do not demonstrate it as merged. The operator must identify the checkout SHA and feature source before claiming execution.

## Objections and evidence-bounded responses

| Buyer objection (hypothetical, not a recorded interview) | Responsible response | What would falsify the offer |
|---|---|---|
| “Jobber already reminds customers about quotes.” | Check the buyer's existing tier and enabled automations first; configure their incumbent where sufficient. | Existing features solve the workflow with lower total cost |
| “Housecall Pro/ServiceTitan already has pipeline tools.” | RRE is not a CRM replacement. Test whether cross-tool leakage and operator-review evidence are genuinely missing. | No measurable gap remains after proper configuration |
| “Hatch already offers AI follow-up.” | Do not claim novel AI or superior performance. Compare permission controls, operator workload and verified incremental value. | Incumbent handles consent and follow-up more effectively |
| “Will this book more jobs?” | No guarantee. A future approved pilot must separately measure actual bookings, completed jobs and paid receipts. | No attributable improvement over baseline |
| “Can it message customers without us?” | No. Drafts remain unsent; even human approval is insufficient without channel-specific lawful consent and suppression checks. | Buyer requires unattended outreach without legal controls |
| “Why $700 monthly?” | It is an unvalidated managed-service hypothesis, not a quoted or accepted price. Establish incremental contribution and measured operating cost first. | Buyer value below fee or provider/staff costs erase margin |
| “Is customer data safe?” | Current demo accepts only synthetic fixtures. No claim of production tenant security or compliance certification. | Security, retention, provider and QA gates cannot be satisfied |

Competitor references and vendor-source links are in [COMPETITOR_EVIDENCE.md](COMPETITOR_EVIDENCE.md); features and prices must be reverified before owner-authorized external use.

## KPI definitions and anti-double-counting rules

- **Eligible inquiries:** distinct, provenance-backed inbound events after deduplication; denominator excludes suppressed/ineligible cases.
- **Draft approval rate:** human-approved drafts / drafts presented for review; draft approval is **not** delivery.
- **Confirmed delivery rate:** provider-confirmed deliveries / owner-authorized sends; synthetic previews count as zero.
- **Booked rate:** provider-confirmed bookings / eligible inquiries; mock appointments count as zero verified bookings.
- **Paid conversion rate:** distinct jobs with reconciled payment receipts / eligible inquiries; synthetic job closures count as zero.
- **Attributed net contribution:** reconciled incremental paid revenue less refunds, variable job costs and attribution overlap, with a documented baseline; do not count gross invoice estimates.
- **Product monthly net:** actual collected subscription receipts minus refunds, processor fees, infrastructure, AI usage, support, acquisition and other recorded operating expenses (tax treatment stated separately). A $2,500 target is not a verified result.

Never add inquiry, draft, appointment and job-stage counts together as separate wins. Unknown denominator, absent receipt or unverified provenance => report **unknown**, not zero performance or inferred success.

## Pilot decision rubric (internal; no pilot authorized)

**No-go** until QA signs off on tenant isolation, durable private storage, audit/consent/suppression, retention/deletion, approved provider adapters, reliability and legal review; owner approves contracts, outreach and expenditure separately. **Discovery hypothesis only** until qualified buyer interviews establish incumbent gaps and willingness to pay. **Go for a further synthetic demo** only when the exact checkout passes non-Codex product CI, an operator executes the walkthrough, records its SHA and defects, and no side effects occur. This is not production or pilot approval.

For a future *authorized* pilot, define baseline and intervention cohorts, documented attribution windows, cost accounting and refund reconciliation before any ROI claim. Reconcile unique receipt IDs and jobs to prevent double counting.

## Internal demo evidence record (blank template; never prefill with fabricated passes)

- Checkout commit SHA:
- Local execution date and operator:
- Product CI URL and exact tested SHA:
- Steps actually observed / skipped:
- Suppression and disabled-side-effect evidence:
- Failures, screenshots with synthetic data only:
- QA signoff reference:
- Owner authorization reference (if any):
- Result: **not executed** until evidence is recorded.

**Current status of this document:** prepared for review; no walkthrough executed by creating this packet. No customer discovery, real revenue, paid pilot or $2,500/month net profit established.
