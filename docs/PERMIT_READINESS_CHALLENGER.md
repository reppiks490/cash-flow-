# MONEYFALL ZERO — Permit Readiness Challenger

Status: **source-backed challenger, not yet promoted over the incumbent**  
Pilot region: Chicagoland  
Public-data refresh date: 2026-10-18  
Capital constraint: $0 upfront

## Objective

Productize municipal licensing/permit-friction research for independent food vendors, especially operators moving between cities, public events, farmers markets and seasonal circuits.

The economic hypothesis is simple: a vendor loses more from one missed event, rejected application or late inspection than a concise, source-linked readiness map costs. We sell **research compression and sequencing**, not legal advice, permit filing, municipal influence or guaranteed approval.

Sprint target: **$3,200 in D1–D10**. This is a target, not a forecast or guarantee.

Scale target: **$24,000/month collected revenue** after paid demand is proven. Do not add fixed costs, paid data, paid ads or subscriptions before attributable revenue justifies them.

## Product ladder

| Product | Price | Best-fit trigger | Deliverable |
|---|---:|---|---|
| Single-City Permit Readiness Pack | $400 | One near-term city/event | Required / may-require / unknown map, sequence, deadlines, restrictions, document checklist, official source links |
| Three-City Expansion Permit Map | $800 | Vendor entering a nearby event circuit | Three municipality maps, comparison matrix, dependency sequence, deadline calendar, blockers and unresolved questions |
| Season / Multi-Jurisdiction Readiness Map | $1,600 | Multi-event operator, promoter, commissary or vendor collective | Prioritized season map across selected jurisdictions, reusable evidence matrix, recurring refresh checklist |

Initial revenue arithmetic:

- 4 x $800 = $3,200
- 8 x $400 = $3,200
- 15 x $1,600 = $24,000/month
- 30 x $800 = $24,000/month

The preferred scale path is not 30 bespoke reports. It is a reusable municipal evidence layer plus vendor-specific delta analysis, with human review before delivery.

## Who to target first

Prioritize independent food trucks, trailers, pop-ups and temporary-event vendors that show a **jurisdiction-change signal**:

1. advertising attendance at events outside their home city;
2. applying to or appearing on public vendor/festival/farmers-market rosters;
3. expanding from one municipality into multiple nearby municipalities;
4. launching a new truck/trailer or changing commissary/shared-kitchen arrangements;
5. asking public questions about permits, inspections, special events or licensing deadlines;
6. promoters or commissaries supporting multiple independent vendors.

Do not target businesses merely because they exist. A current operational trigger is the primary qualification signal.

## Municipal friction model

The engine ranks research markets using explicit 0–1 evidence-backed factors:

| Factor | Weight | What creates friction |
|---|---:|---|
| Agency handoffs | 15% | health, fire, zoning, licensing, event organizer, building or other departments |
| Sequential dependencies | 20% | A must be completed before B can be submitted/approved |
| Manual/offline steps | 15% | in-person, paper, phone/scheduling or non-self-service steps |
| Inspection dependencies | 15% | vehicle, kitchen, fire, sanitation or pre-operational inspections |
| Deadline pressure | 15% | submission windows, late fees, event cutoffs or non-approval risk |
| Geographic restrictions | 10% | street, school, park, event or fixed-location limitations |
| Fee complexity | 10% | different license classes, event paths, late/on-site fees |

A missing factor fails closed as **unranked**. No guessed value is substituted.

Offer routing:

- `<40`: skip until stronger evidence exists
- `40–59.99`: test Single-City Pack
- `60–79.99`: test Three-City Expansion Map
- `80–100`: test Season / Multi-Jurisdiction Map

These are sales-research heuristics, not legal/compliance risk scores.

## Pilot evidence already mapped

The repository dataset `config/permit_friction_chicagoland.json` contains seven source-backed pilot jurisdictions: Chicago, Evanston, Skokie, Elgin, Oak Park, Naperville and Cicero.

High-value examples include:

- Chicago special-event food workflows distinguish single-event and 180-day paths, route multi-event applications through BACP/CDPH, require a recently inspected commissary/restaurant/shared kitchen, and require applicable mobile-food and sanitation credentials before the special-event application.
- Evanston separates mobile-vendor, temporary and seasonal permissions; requests event applications at least ten business days in advance; and imposes mobile-vending location/time restrictions.
- Elgin's 2026 food-truck process adds pre-event fire inspection requirements and distinguishes temporary/seasonal/event dependencies.
- Oak Park requires a temporary food license for qualifying public-event food service and routes applicants through Public Health.
- Naperville requires food-vendor permits and prohibits food trucks from vending on public streets.
- Cicero's base business-license workflow involves zoning plus Fire, Building, Electrical and Health inspections; food-specific requirements remain explicitly unresolved until separately verified.

## Research-pack contract

Every client deliverable must contain:

1. vendor operating model and intended dates/locations;
2. jurisdiction and issuing authority map;
3. `required`, `may require`, and `unknown` items kept separate;
4. dependency sequence (what must happen before what);
5. documented fees and deadlines only when an official source supports them;
6. operational/location restrictions;
7. inspection and commissary/shared-kitchen dependencies;
8. missing-document checklist;
9. official source URLs and retrieval dates;
10. unresolved questions the vendor should confirm with the authority;
11. research-only disclaimer.

Never present an inference as a municipal requirement. Never imply the service files permits, represents the vendor before a municipality, guarantees approval, or replaces an attorney/licensing professional.

## Zero-cost acquisition engine

Use public sources before paid prospecting tools:

1. current festival/event vendor rosters and application pages;
2. farmers-market vendor lists;
3. food-truck associations/directories;
4. vendor websites and public social pages that announce cross-city events;
5. commissary/shared-kitchen public member directories where legitimately available;
6. event organizers/promoters that publish vendor calls.

Store actual prospect/contact data only in approved private state. **Never commit prospect PII into this public repository.**

Qualification formula:

`permit pain = current expansion signal x municipal friction x deadline proximity x reachable owner/operator x likely event value`

Only build a custom proof packet after the target shows a real signal.

## Proof-before-pitch workflow

For each high-fit target:

1. identify the next public event/city expansion signal;
2. map only the two or three most relevant municipal bottlenecks from official sources;
3. prepare a one-page private preview showing one documented blocker/deadline and the missing information needed to finish the map;
4. contact the owner/operator with the specific observed trigger and preview;
5. sell the fixed-scope research pack, not open-ended consulting;
6. after payment and scope confirmation, complete the source-linked pack and QA every claim;
7. log paid conversion, fulfillment time and any refund/correction separately.

No generic blast. No invented urgency. No fabricated event participation. No claim that a prospect is non-compliant.

## D1–D10 execution sequence

**D1–D2:** map and QA the highest-friction jurisdictions; assemble a private list of vendors with real cross-city/event signals.  
**D2–D3:** produce 10–20 micro-previews for the strongest targets.  
**D3–D6:** bounded, personalized owner outreach; prioritize $800 expansion-map candidates.  
**D4–D10:** close/fulfill the first paid packs, record objections and delivery time, and reallocate toward the municipality/vendor combination producing paid demand.

The $3,200 target is four $800 expansion maps. If observed demand instead clusters at $400, the equivalent target is eight single-city packs. Do not discount simply to force the target.

## Winner-selection rules

Track by cohort:

- qualified targets
- previews produced
- delivered outreach
- replies
- positive replies
- paid orders
- collected revenue
- refunds
- median fulfillment minutes
- correction rate
- revenue per 100 qualified targets

Promote a municipality/vendor segment only after paid conversions, not clicks or compliments. Reuse municipal research where legally/publicly permissible, while rebuilding the vendor-specific delta and re-checking source freshness before each paid delivery.

## $24k/month faceless engine

The scalable unit is a **municipal evidence graph**, not an AI-written report.

`official municipal page -> normalized requirement -> dependency -> restriction/deadline -> municipality friction score -> vendor delta -> reviewed readiness pack`

The brand can remain operator-light/faceless, but communications must not misrepresent identity, credentials or municipal affiliation. Every delivered conclusion remains traceable to a source and retrieval date.

Automation priority after paid proof:

1. source-change detection;
2. structured requirement extraction into `required / may_require / unknown`;
3. stale-source alerts;
4. vendor-intake normalization;
5. deterministic comparison and draft-pack assembly;
6. human claim review;
7. delivery/export and attribution.

Do not automate legal conclusions, final eligibility decisions, or unsupervised municipal representations.

## Current activation boundary

Research, market mapping, prospect qualification, preview production and private draft outreach can proceed at $0 upfront. Real outbound sends must follow the repository's existing commercial-email/identity/suppression gates and the actual connected provider's confirmation requirements. Payment must be verified before counting revenue. A processor link, invoice draft or synthetic receipt is not collected cash.
