# RRE pilot measurement and evidence protocol (v0.1)

**Status: planning protocol only.** No live leads, sent communications, booked appointments, customer payments or operational profit are claimed. Records and authentic receipts remain in a private, tenant-isolated store after production controls are approved; GitHub may contain only explicitly synthetic fixtures or anonymized aggregate reports approved for publication.

## Funnel event definitions

| Event | Minimum proof | Not equivalent to |
|---|---|---|
| inquiry_observed | Source system + stable permitted identifier + capture time | Qualified buyer |
| qualification_reviewed | Explicit rubric/evidence, reviewer and review time | Permission to contact |
| followup_draft_created | Versioned draft record linked to source | Message sent |
| followup_approved | Human reviewer approval with scope and consent check | Message sent |
| followup_sent_confirmed | Provider message ID / audited response, not draft ID | Delivered or read |
| appointment_confirmed | CRM/calendar confirmation linked to inquiry | Closed job |
| job_closed_confirmed | CRM/invoice state and operator confirmation | Collected payment |
| payment_collected_verified | Authenticated unique payment receipt, amount, currency, settled state | Profit or bank payout |
| refund_verified | Authenticated unique refund linked to payment | New payment |
| expense_verified | Actual bill/receipt and time cost allocated once | Revenue |
| opt_out | Confirmed opt-out / suppression event | Eligible future outreach |

**Event lineage:** every event must carry an opaque tenant-scoped event ID, opaque inquiry/workspace IDs, timestamps, actual source system, source event reference, ingestion time, event type, evidence reference and actor. Preserve updates without mutating previously captured facts. No external address/name/phone/email in public evidence. Distinguish test fixtures using a mandatory synthetic=true flag. A placeholder or model-produced text is not an authenticated receipt.

## Attribution safeguards

1. Agree in advance on which previously received inquiry and subsequent confirmed actions qualify as a *recoverable* missed inquiry or open estimate. Exclude work already committed or tracked as won before treatment.
2. Fix a consistent attribution window and operator-verified baseline, including competing campaigns, seasonality, staff actions and pre-existing automation. Report counts and denominators; do not claim causality from correlation.
3. Deduplicate by tenant + external inquiry reference and by receipt identity; a payment may not count twice after updates or across campaigns. Multiple appointments are not multiple jobs or multiple payments.
4. Actual recovered collections require matched authenticated payment + eligible closed-job evidence and evidence that the relevant follow-up fell within the agreed experiment. Otherwise classify as *unattributed* or *claimed/unverified*, never verified recovered cash.
5. Refunds, processor fees and costs reduce profit; bank-pending and bank-available are stages of the same cash, not separate revenue.
6. Revenue attributable to the **HVAC operator** is not subscription revenue earned by **our software business**. Never combine the two. RRE subscription MRR requires our own verified active paid contracts and payment receipts.
7. Labor and support time must be captured, including owner work, to calculate realistic net operating profit.

## Pilot scorecard (private, not in GitHub)

Report weekly: eligible inquiries (N), followed-up inquiries (n/N), approved but unsent drafts, provider-confirmed sends, confirmed appointments, closed jobs, receipts linked to qualified follow-up, collected operator revenue, refunds, direct costs, operator contribution, provider subscription cash, RRE operational costs, and RRE **verified** pretax net margin. A missing denominator is unknown, not zero. Synthetic rows must appear in a visually separate demo-only panel.

## Demonstration and economics

Use economics.py for clearly hypothetical subscription math. It **never** produces verified profit. Base scenario: 5 assumed customers x $700 = $3,500 gross MRR; $1,000 in assumed all-in monthly expenses = $2,500 illustrative pretax operating profit. Processor fees, acquisition, owner labor and support must be included in the all-in assumptions or the scenario overstates profit.

**Pilot pass condition:** a real pilot requires signed terms, security/QA sign-off, authentic source and consent records, approved integration, operational incident procedure and independently reconciled outcome receipts. No automation or simulation can substitute for a real customer.
