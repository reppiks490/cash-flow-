# MONEYFALL payment rail + fulfillment handoff

Date: 2026-10-18

## State

The repository already contains a hardened Stripe event verifier and order ledger in `src/moneyfall/orders.py`. It accepts only confirmed USD checkout payments, rejects test-mode events by default, requires `client_reference_id` for reconciliation, rejects wrong amounts/replayed receipts, and does not start fulfillment until payment plus approved client assets/inputs are present.

The eight prompt-derived pilot offers are now declared in `config/payment_catalog.json`. No live Stripe product IDs, price IDs, payment-link URLs, webhook secrets, customer data, or private operational records belong in this public repository.

Live Stripe object creation is currently blocked only by authenticated Stripe account access in this ChatGPT session. When the Stripe connector is connected, create the objects below in the authenticated account and record the returned object IDs/URLs only in private operational state, not this repo.

## Live Stripe object creation

For every entry in `config/payment_catalog.json`:

1. Create a one-time Stripe Product using `product_name`.
2. Create a USD one-time Price equal to `price_cents`.
3. Create a hosted Payment Link for that Price.
4. Put only non-sensitive catalog metadata on the link, such as `offer_id` and `prompt_id`.
5. For every actual prospect/order, append a unique `client_reference_id` to the Payment Link URL before sending it. Use the format in the catalog (`moneyfall_<offer_id>_<order_nonce>`); never put a name, email, secret, credential or other sensitive value into the reference ID.
6. The exact accepted scope and expected amount must already exist in private order state before the payment link is sent.

Stripe documents that a Payment Link can carry a `client_reference_id` URL parameter and that the resulting Checkout Session includes that value for webhook reconciliation. Payment Link metadata is copied to Checkout Sessions created by the link.

## Webhook / cash gate

Current code accepts only:

- `checkout.session.completed`
- `checkout.session.async_payment_succeeded`

and requires:

- valid Stripe webhook HMAC signature
- timestamp within the verifier tolerance
- `livemode=true` unless an explicit test harness opts into test mode
- `payment_status=paid`
- `currency=usd`
- positive integer `amount_total`
- non-empty Checkout Session `id`
- non-empty `client_reference_id`

After verification, the private order ledger must still match the exact accepted order price before cash is recorded. A Checkout draft, invoice, unpaid session, test event, or mismatched amount is not revenue.

## Paid-order handoff

The paid-order lifecycle is:

`accepted scope -> private order -> prospect-specific Payment Link + client_reference_id -> verified Stripe event -> payment receipt bound to order -> required client inputs / permissions -> fulfillment ready -> produce deliverable -> validate bundle -> actual delivery receipt -> delivered`

Do not start a promised 24/48-hour clock until the product's stated start conditions are met. For products that require no client assets, the approved-input reference can be the buyer's written acceptance of the scoped research inputs and target context.

## Document fulfillment profile

The eight new prompt-derived products use `document-v1` initially. A delivery folder contains:

- `deliverable.pdf`
- `manifest.json`

`manifest.json` must contain at minimum:

```json
{
  "order_id": "moneyfall_example_order_001",
  "scope_sha256": "<sha256 of exact accepted scope text>",
  "profile": "document-v1",
  "specimen": false,
  "files": {
    "deliverable.pdf": "<sha256 of final PDF bytes>"
  }
}
```

`src/moneyfall/fulfillment_profiles.py` validates that:

- the order is ready for fulfillment before recording production;
- the manifest belongs to the exact order;
- the manifest is bound to the exact accepted scope;
- the profile is `document-v1`;
- a specimen cannot be delivered as commissioned work;
- the PDF exists inside the delivery folder;
- its SHA-256 still matches the manifest;
- it has a basic valid PDF header/trailer;
- only after validation is the produced-reference hash written to the private order record.

Actual delivery still requires a separate delivery receipt. Production is not delivery, and delivery is not payout/bank receipt.

## Offer routing

| Offer ID | Price | Initial fulfillment |
|---|---:|---|
| `dispatcher-overflow-starter` | $149 | PDF operating kit |
| `no-show-recovery-pack` | $49 | PDF operating kit |
| `reinspection-evidence-binder` | $79 | PDF evidence binder |
| `revenue-leak-audit` | $199 | PDF audit / recovery blueprint |
| `permit-readiness-research` | $149 | PDF research pack |
| `rfp-submission-control` | $249 | PDF submission-control pack |
| `hiring-signal-lead-brief` | $99 | PDF signal brief |
| `reinspection-readiness-brief` | $149 | PDF readiness brief |

## Activation gate

Before tomorrow's outbound uses a payment URL:

- connect the Stripe plugin/account in ChatGPT;
- confirm the Stripe account is capable of receiving live payments;
- create the eight Product/Price/Payment Link objects;
- verify the link for each intended order carries its unique `client_reference_id`;
- run one Stripe test-mode checkout through the webhook path without recording it as live revenue;
- then switch the order path to the live links only after the authenticated account is ready.
