# RRE-04 — Anonymous HVAC discovery scorecard contract

**Classification:** proposed offline research instrument, not a completed survey, approved outreach, production data model, or evidence of demand. **Status:** HOLD for owner-approved research and privacy review. This document supplements `PILOT_OFFER_AND_DISCOVERY.md` and `COMPETITOR_EVIDENCE.md`; it does not replace either.

## Purpose and permitted workflow

Use a blank copy for a future *authorized* operator interview, without collecting names, phone numbers, email addresses, company names, URLs, addresses, job identifiers, customer details, quotations, transcripts, or free-text notes in public GitHub. Until outreach authorization, populate only invented examples explicitly marked `synthetic`. Keep any future consent and source records in an approved private system, not this repository. Do not store hashed contact identifiers here: hashes can still enable reidentification.

A completed interview must have an independently recorded private authorization reference; the public research summary may contain only aggregate, disclosure-reviewed counts. A missing authorization reference means the observation cannot be used to substantiate buyer validation. No automated follow-up or sending is permitted.

## Controlled fields (offline form design, not a live endpoint)

| Field | Allowed values | Interpretation |
|---|---|---|
| `record_class` | `synthetic`, `authorized_research` | Only synthetic records may be committed to this repository |
| `buyer_segment` | `solo`, `2_10_staff`, `11_plus_staff`, `unknown` | Rough size, not identity |
| `crm_family` | `jobber`, `housecall_pro`, `servicetitan`, `hatch`, `other`, `none`, `unknown` | Do not infer paid feature availability from brand |
| `existing_automation` | `enabled`, `disabled`, `unknown` | Buyer report, not provider verification |
| `unresolved_gap` | `none`, `missed_inquiry`, `quote_followup`, `cross_tool`, `unknown` | A reported gap is not proven lost revenue |
| `evidence_quality` | `self_report`, `redacted_process_demo`, `verified_private_audit`, `unknown` | Audit requires independent authorized review |
| `preferred_offer` | `existing_crm_configuration`, `one_time_audit`, `managed_service`, `software_only`, `none`, `unknown` | Do not force product preference |
| `700_usd_willingness` | `reject`, `consider`, `written_nonbinding`, `unknown` | None means signed sale or payment |
| `blocking_reason` | `no_gap`, `price`, `security`, `consent`, `integration`, `staffing`, `unknown` | One primary reason, no free text |
| `authorization_state` | `not_authorized`, `private_approval_verified` | Public summary must not contain approval tokens |
| `outcome` | `hypothesis_only`, `research_observation` | No sales or revenue status |

Reject unknown enum values, additional fields, real-world identifiers, and records that claim `authorized_research` without independently verified private approval. Never convert `consider` into a signed subscription. Treat missing fields as `unknown`, not as zero, no objection, or affirmative consent.

## Evidence and decision gates

**Gate A — research authorization:** owner signs off on contact method, legal basis, approved script, private storage, retention and suppression. Until then, no prospect contact and no real observations.

**Gate B — minimum falsification sample:** propose ten independent authorized interviews spanning CRM-equipped and CRM-light operators; this is a *research design target*, not a statistical guarantee or evidence that interviews happened. Report both denominator and refusals, with missing responses explicit.

**Gate C — incumbent displacement:** where a buyer's existing CRM already addresses the gap, recommend configuration before selling a duplicative service. Distinguish buyer self-report from independently demonstrated workflow evidence.

**Gate D — offer viability:** track separately (i) reported operational gap, (ii) buyer willingness to pay, (iii) authenticated signed terms, (iv) processor-confirmed collections, and (v) attributable paid jobs. Do not promote any earlier stage to a later one.

**Gate E — unit economics:** at the hypothetical $700/month, five active paid subscriptions imply $3,500 gross monthly billing before refunds, fees, hosting, support, acquisition, taxes and other costs. To reach $2,500/month *pretax net*, aggregate monthly relevant costs must be at most $1,000; verify actual cash receipts and expenses, not survey intent. No subscription count, costs or profit have been verified.

## Aggregation and release constraints

Publish only disclosure-reviewed aggregate counts with denominators, missing-value counts, sample-selection caveats and interview dates at month granularity. Suppress small cells that could identify an operator; default to no public reporting until privacy review approves a threshold. No automated customer-facing dashboard should consume research observations as proof of revenue. Keep this contract independent of runtime onboarding and billing ports.

## Review checklist

- No outreach, real records, secrets, private identifiers or provider calls were introduced.
- Every claim is tagged hypothesis, self-report, verified private evidence, or actual receipt.
- The demo remains synthetic and unsent; customer discovery is gated by owner authorization.
- QA/Principal review enum semantics and private retention before any real interview.
- Independent review and exact-head non-Codex CI required before merge.

**Current measured state:** zero verified interviews, zero authenticated customer receipts, zero verified recurring net profit. These are evidence-status statements, not forecasts.
