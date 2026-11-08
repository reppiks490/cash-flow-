# HVAC buyer discovery and pilot decision protocol (offline only)

**Status:** research instrument / hypothesis; no interviews conducted, prospects contacted, contracts signed, or prices validated. **Owner approval required before any external use.** RRE-04 / issue #26.

## Target buyer and job-to-be-done
Owner/operator or service manager at a small-to-mid-size residential HVAC contractor who handles inbound service inquiries and unsold estimates. Hypothesis: slow callbacks and unreviewed estimates create avoidable missed opportunities; an auditable, consent-aware queue of *draft* next actions may reduce administrative delay. This is not evidence of incremental recovered revenue. Do not imply the product makes calls, sends messages, books appointments, or proves incremental jobs.

## Discovery interview (30 minutes; conduct only after explicit owner authorization)
Use a private, approved research environment. Do not enter interviewee names, phone numbers, customer records, raw transcripts, or company-identifying notes in public GitHub.

1. Workflow (5 min): Walk through the most recent *anonymized* inbound request, from intake to disposition. Which tools and staff roles touch it?
2. Baseline (5 min): For a defined historical period, how many inbound inquiries and quotes were received? What fraction had an acknowledged callback? Which counts are actually exportable?
3. Failure modes (5 min): What causes delayed or missing follow-up? What happens when customers opt out? How are duplicates recognized?
4. Buying process (5 min): Who approves software, security, messaging templates, integrations, and monthly expenditure? What contracts and vendor reviews apply?
5. Value and cost (5 min): What is the present cost of staff follow-up, missed opportunities, and existing software? Ask for price sensitivity *without* claiming $700/month is validated.
6. Pilot constraints (5 min): What would a safe synthetic-only demonstration need to prove? Which data sources, consent records, security controls, and authorized personnel would be required for a later controlled pilot?

## Evidence grading and decision gates
| Grade | Meaning | Permitted claim |
|---|---|---|
| H | Internal hypothesis or arithmetic | "Hypothetical" only |
| D | Synthetic reproducible demonstration | "Demo works on synthetic inputs" only |
| I | Authorized interview, privately recorded with consent | "Interviewee reported" with sample size and caveats |
| O | Independently verifiable operational event | Report observed event, not causal lift |
| F | Authenticated, reconciled subscription receipts and operating expenses | Period-specific realized net; do not extrapolate recurring net |
| C | Controlled, pre-registered causal comparison with defensible confounder treatment | Qualified incremental impact estimate with uncertainty |

No grade can be upgraded solely by an AI-generated summary. A signed quote is not a paid job; a booked appointment is not collected revenue; contractor receipts are not RRE subscription receipts.

## Pilot acceptance (not authorization)
- **Demo:** repeatable synthetic lead -> dedupe -> qualification evidence -> unsent draft -> mock CRM/calendar -> stage-specific dashboard; explicit $0 verified receipts.
- **Security:** authenticated tenant isolation, private durable storage, access audit, deletion/retention and recovery independently tested before real records.
- **Compliance:** documented consent source, suppression and revocation, approved message templates, counsel-reviewed channel rules, operator identity and human approval for every send.
- **Integration:** provider-specific mock-contract tests, error/idempotency/replay tests, no real vendor tokens in repository.
- **Finance:** separately reconcile vendor collections, refunds, chargebacks, direct costs, allocated overhead and owner labor. Define accounting period and attribution before measurement.
- **Release:** QA signoff plus separate explicit owner approval; this document does not enable outreach, customer intake, billing, or deployment.

## Pricing hypothesis and break-even sensitivity
Assume $700 per paying account per month, with no discounts, taxes or payment failures. Five accounts would yield $3,500 **gross billings**; $2,500 pretax cash operating net requires **no more than $1,000** of total monthly cash expenses including processing, hosting, support, acquisition and overhead. At four accounts, gross billings are $2,800 and the same target permits only $300 expenses. These are arithmetic thresholds, not customer forecasts. Economic net must additionally account for uncompensated owner labor without double counting paid labor.

## Measurement worksheet (private, after authorized pilot)
Record time window and denominator definitions before observation: eligible inbound requests; consent-known requests; qualified requests; drafts approved; sends confirmed by provider; appointments confirmed; closed jobs supported by receipts; refunds/chargebacks; and actual RRE subscription settlements. Track unknown/missing as unknown, not zero. Link each event with tenant-scoped opaque identifiers and provenance, stored outside public GitHub. Compare observational outcomes without describing them as causally recovered revenue.

## Stop rules
Do not start interviews or outreach without owner authorization. Never ingest real customer details into demo fixtures. Do not activate CRM/email/calendar writes or payments. If an authorization, consent, evidence, or tenant boundary is missing, remain synthetic and log the blocker privately.
