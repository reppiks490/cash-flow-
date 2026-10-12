# MONEYFALL ZERO operating contract

## Data flow and boundaries

`sources.py` fetches public Greenhouse/Lever job boards with 20-second timeouts,
a 5 MB response ceiling, fixed HTTPS hosts, validated tokens and no redirects.
`store.py` deduplicates signals and records timestamped evidence events in
private SQLite. `scoring.py` rejects invalid/unknown inputs and provides heuristic
ranking. `offers.py` generates internal $149 scope experiments with unresolved
evidence explicitly marked. `__main__.py` connects these modules without sending
email, submitting applications, buying services or charging customers.

Greenhouse `updated_at` is labeled updated, never newly posted. Lever `createdAt`
is converted from milliseconds to UTC; retrieval time is separate. Hiring title
matching is a discovery filter, not evidence of budget size or a content defect.
The queue is not a universe of qualified buyers, and old closed roles can remain
in historical state; re-check availability before using a signal.

Official references checked 2026-10-12:
- https://docs.greenhouse.io/job-board.html — public GET job-board endpoints.
- https://github.com/lever/postings-api — JSON posting endpoint and fields.

## Qualification and opportunity allocation

Prospect readiness is 100 times the product of six evidence-backed fractions.
Any missing dimension blocks qualification. Opportunity ranking instead combines
explicit scenario fractions with a seven-day speed factor; upfront capital >0
makes a candidate infeasible. This is a prioritization heuristic, not dollar EV,
validated probability or proof a business model is superior.

The initial research-audit scenario scores above B2B service, but does not replace
the incumbent: no paid cohort exists. `promote` requires three paid conversions
and >15% score improvement; it is a decision helper, not a background allocator.
Catalog assumptions must be replaced with measured cohorts. Do not tune scenario
numbers to force the preferred strategy to win.

## Cash and suppression accounting

Payment/refund/cost events require positive integer cents and observed receipt
references. Duplicate event IDs replay safely; conflicting IDs or duplicate
financial receipts are rejected. Refunds cannot exceed collected cash for that
signal. Metrics count normalized company labels as prospects rather than jobs,
and historical paid companies separately from net cash after refunds.

Company-label identity is a first implementation; different aliases must be
reviewed and normalized before cross-provider/cohort comparisons. Suppression
and bounced events conservatively suppress all signals with that company label.
A production send adapter must additionally enforce contact-level suppression
and real-send gates immediately before any transmission.

Gross profit here means net collected cash minus recorded direct costs; it
excludes unrecorded labor, tax and fees. Record actual payment fees/fulfillment
costs to improve it. Credit totals are recorded units, not dollars; providers'
credits are not interchangeable. Receipt evidence is supplied by the operator;
automated signature-verified webhooks and order reconciliation are future work.

Brief generation persists opportunity/offer/hypothesis/asset-hash linkage on the
signal. Every subsequent event snapshots that linkage; later changes cannot
move existing cash to another opportunity. `metrics --opportunity ID` filters
event cash and cohort companies; its signal count remains the overall queue
size. Always prepare/link the brief before recording experiment events. Events
recorded without attribution remain in total metrics and no attributed cohort.
Ordinary source refresh preserves qualification, but a changed title, company
or source URL invalidates qualification until the observations are checked again.

## Privacy and reliability

The repository is public. No live queues, customer data, inbox content, receipts,
credentials or protected analytics may be committed or uploaded to public CI.
State paths resolve outside the checkout; .gitignore covers database/environment
files as a second guard, not a substitute for review. SQLite file permissions
are 0600; use a private directory and encrypted persistent host for deployment.
This is a single-process CLI, not a multi-worker service. No concurrent event
writers or webhook receiver should be deployed until atomic receipt constraints
and concurrency tests are added.

GitHub Actions intentionally performs only code/synthetic checks. An ephemeral
runner cannot retain the private sales queue. Scheduled production research must
wait for a configured private state sink; never commit the queue to make it
durable. Preserve provider errors rather than silently calling paid alternatives.

Capability balances in config are historical snapshots, not spend authorizations
or current quotas. One Runway workspace is one pool even with two connectors.
No new trial or paid fallback was activated in this implementation.

## Verification procedure

Run `PYTHONPATH=src python -m unittest discover -s tests -v`, then `rank` and
`demo`. For live checks, fetch known current board tokens into a private state
path, repeat a successful board to prove deduplication, and prepare one internal
brief. Re-read current continuation state before resuming so failures are not
mistaken for unfinished code. Documentation review is inline: verify README and
AGENTS link every new operational artifact. Akinator's installed package lacks
the referenced `akinator_coverage.py`/ledger/wiki helper scripts; no claim that
those mechanical knowledge gates ran successfully is made.

## Launch suppression integration, 2026-10-12

The launch builder and reservation now consult contact suppression AND the existing linked signal/company suppression events, including bounces. Reservation rechecks current state rather than trusting only saved packet gates. Confirm signal linkage privately; unknown IDs are not verified company identities. record_sent imports confirmed historical receipts even after a stop reply, preserving an accurate record; it does not authorize or transmit another send. See [audit and readiness](ENGINEERING_AUDIT_2026-10-12.md) for three failing-first regressions, local49-pass verification and unresolved account/state access.
