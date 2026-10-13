# Launch and fulfillment

The $149 white-label pilot has a concrete scope: three portrait graphics and
editable SVGs, one 15-second caption-led motion preview, three captions/CTA
options and one revision. Delivery starts after scope acceptance, confirmed
payment and approved assets. Filming, voiceover, publishing, account management,
ad spend and promised leads/revenue are excluded.

## Screening and coverage

```bash
export PYTHONPATH=src
python scripts/run_radar.py /PRIVATE/company-candidates.json \
  --state /PRIVATE/state.sqlite --fetched /PRIVATE/fetched --limit 100 --workers 4
```

Candidates are a JSON array with `domain` and optional `organization`. Imported
pages are private JSON files named DOMAIN.json containing `domain`, `url`,
`html`, `fetched_at` and `provider`. Source URLs must match the candidate domain;
imports are bounded to 2 MB. Direct reads validate and pin public DNS addresses,
use TLS, constrain redirects and respect robots.txt. Direct arbitrary-domain DNS
was blocked in the execution environment; licensed Firecrawl imports worked.
Resume skips successful screens and retries failed reads. Failures remain visible.

The classifier suggests an offer route from public service text. It never marks
a company send-ready or proves buying intent, ability to pay or future revenue.
Human/source review must confirm actual fit and an appropriate business contact.
The provider's initial 9,140 match count was broader than the pilot criteria;
pagination repeated the first page. Separate Apollo organization pages expanded
the private deduplicated candidate set to 291. Do not claim a complete export.

## Private proof and packets

```bash
python scripts/render_proof.py /PRIVATE/proof-jobs.json /PRIVATE/asset-kits
python scripts/launch_packets.py --profile /PRIVATE/profile.json \
  --prospects /PRIVATE/reviewed-prospects.json --state /PRIVATE/state.sqlite \
  --output /PRIVATE/packets
```

For new Vellumflare outreach, the private sender profile may explicitly set
`"brand": "Vellumflare Studio"`. That validated one-line brand is added to the
new packet's provenance, subject and signature. A profile that omits `brand`
keeps the historical packet shape, subject and signature unchanged; do not add
the field merely to rewrite old drafts or evidence. Brand values are trimmed,
must be non-empty one-line text and are capped at 64 characters. This identity
field does not bypass payment, proof, contact, suppression or send gates.

Check `--help` for renderer options. Media generation additionally requires
Pillow, ReportLab, FFmpeg and DejaVu fonts. Core CLI and tests use the standard
library. Proof jobs include original copy, company, source URL, observed service,
hypothesis and three cards. Specimens remain explicitly uncommissioned; no
company photos, logos, testimonials or invented results are used. Private output
paths, including symlink destinations, cannot be inside this public checkout.

Packets require reviewed fit, source-backed verified business contact, reviewed
proof hash, sender identity/email, valid sender postal address, verified payment
destination and suppression checks. The first five Gmail drafts were read back
as DRAFT with actual PDF attachments; private packet hashes bind those compact
PDF bytes. Draft IDs persist so continuation does not duplicate provider drafts.

Sending is a connector operation, not an unattended process in this repository.
Refresh evidence and the footer, update the existing Gmail draft, re-review its
actual recipient/body/attachment, save the final packet revision and reserve it
before sending. `LaunchStore.reserve` atomically prevents another initial attempt
to the same recipient/offer even when a body changes. Recheck suppression at send
time. Record an actual sent-message receipt only after confirmed provider success.
On an ambiguous timeout, inspect the existing draft/sent thread; never blindly
retry. Draft IDs are not sends. Import stop replies into contact/company
suppression immediately. No mailing-address placeholder may be sent.

## Accepted orders and actual cash

```bash
python scripts/orders.py --state /PRIVATE/state.sqlite create ORDER_ID SIGNAL_ID \
  --scope 'Client-accepted scope' --price-cents 14900
python scripts/orders.py --state /PRIVATE/state.sqlite payment ORDER_ID \
  --receipt VERIFIED_RECEIPT --amount-cents 14900
python scripts/orders.py --state /PRIVATE/state.sqlite assets ORDER_ID \
  --approved-reference APPROVED_BRIEF_AND_RIGHTS_REFERENCE
python scripts/orders.py --state /PRIVATE/state.sqlite status ORDER_ID
```

Manual receipt references require authenticated provider evidence, not invoices
or promises. Attribution is fixed at scope acceptance. Exact payment amount and
receipt uniqueness are checked; payment/refund writes are atomic. Refunds track
individual orders so one order cannot borrow another order's balance.

`stripe-import` validates the untouched raw webhook bytes, timestamp, HMAC,
live mode, paid USD status and order reference using the private environment
variable `MONEYFALL_STRIPE_WEBHOOK_SECRET`. Test fixtures do not count as cash.
This is a tested importer, not a hosted webhook endpoint or connected Stripe
account. A verified payout destination and private receiver still need setup.

## Production and delivery

Commissioned rendering requires a single ready paid order and approved assets;
use `render_proof.py --help` for `--commissioned-order ORDER_ID` and `--state`.
Validate the complete kit with `orders.py fulfill ORDER_ID /PRIVATE/KIT`. Manifest
order ID, accepted-scope hash, actual file hashes and media types are checked.
Another customer's specimen/kit cannot be substituted. Validation records
production only. After actual customer delivery, record `orders.py delivered
ORDER_ID --receipt ACTUAL_DELIVERY_RECEIPT`. Do not mark a local export delivered.
Visually inspect the PDF/cards and inspect video duration/dimensions before sending.

## Current 14–20 day execution goal

1. Activate the verified footer and payment route, then send the five reviewed
   attached pilots through existing Gmail drafts. Record actual sends.
2. Review replies and stop requests; answer scope questions and collect accepted
   briefs/payment. Never treat silence as a purchase or buying-intent proof.
3. Fulfill paid approved pilots within the defined 48-hour clock, verify exports,
   deliver and record receipt; offer another kit only after actual feedback.
4. Continue bounded source screening and contact review. One specific follow-up
   after several business days is reasonable only for an unsuppressed recipient;
   stop if declined. Record its separate stage and receipt.
5. Compare observed replies, orders, net cash, direct costs and delivery effort.
   Expand a measured winning cohort; keep challenger opportunities active.

The current goal is legitimate attributable profit within 14–20 days, not a
guarantee. It does not reset the original project-start clock; that clock's exact
timestamp remains unverified and must not be invented. Earlier seven-day language
is historical. First payment, processor availability, bank cash and completed
profitable fulfillment remain distinct outcomes. No continuous sender, reply
monitor or scheduled background business runs after a session ends.
