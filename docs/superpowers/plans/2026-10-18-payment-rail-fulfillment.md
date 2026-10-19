# Payment Rail + Document Fulfillment Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Make the eight new MONEYFALL offers Stripe-ready and add a safe document-delivery fulfillment profile without weakening the existing creative-kit order controls.

**Architecture:** Preserve the existing `Orders` / Stripe webhook verification path. Add a public, secret-free payment catalog and a standalone document-bundle validator for PDF-based research/admin offers. Live Stripe product/price/payment-link creation remains an external account action and must not be claimed until the Stripe connector/account is authorized.

**Tech Stack:** Python 3, stdlib `hashlib/json/pathlib`, existing MONEYFALL SQLite/order model, Stripe hosted checkout/payment links.

**Spec:** `docs/CURRENT_EXECUTION.md` plus the eight prompt execution assets created 2026-10-18.

## Global Constraints

- $0 upfront; no paid service activation without user authorization.
- Public repository: no API keys, webhook secrets, customer data, prospect lists, payment data, or private operational state.
- Never count a draft, invoice, test event, or unpaid checkout as revenue.
- Fulfillment begins only after verified payment and required client inputs/permissions.
- Do not weaken existing creative-kit validation.

## Review Focus

- Wrong-price or replayed payment must not count as new cash.
- Test-mode Stripe events must not count as live revenue.
- A document bundle must be bound to the accepted order and exact accepted scope.
- Specimen/proof assets must never be deliverable as commissioned work.
- A changed/missing/invalid PDF must fail validation.

---

### Task 1: Stripe-ready offer catalog

**Files:**
- Create: `config/payment_catalog.json`

**Interfaces:**
- Produces: stable `offer_id`, public product name, price in cents, fulfillment profile, and delivery window for each of the eight prompt-derived offers.

- [ ] Add all active pilot offers with USD integer-cent prices.
- [ ] Keep Stripe object IDs and live payment URLs absent until created in the authenticated Stripe account.
- [ ] Verify every offer maps to a fulfillment profile.

### Task 2: Document fulfillment validator

**Files:**
- Create: `tests/test_fulfillment_profiles.py`
- Create: `src/moneyfall/fulfillment_profiles.py`

**Interfaces:**
- Produces: `validate_bundle(folder, *, order_id: str, scope: str) -> str` returning the manifest SHA-256 after validation.

- [ ] Write tests for a valid `document-v1` PDF bundle.
- [ ] Run tests and verify they fail before implementation because the module is absent.
- [ ] Implement order/scope binding, specimen rejection, file hash validation, and PDF signature checks.
- [ ] Run the focused tests and verify they pass.

### Task 3: Operator handoff documentation

**Files:**
- Create: `docs/PAYMENT_RAIL_AND_FULFILLMENT.md`

**Interfaces:**
- Consumes: existing `verify_stripe`/`Orders.payment` protections and `config/payment_catalog.json`.
- Produces: exact live-account activation checklist and paid-order handoff sequence.

- [ ] Document Stripe product/price/link creation fields and required `client_reference_id` reconciliation.
- [ ] Document webhook events accepted by the current code.
- [ ] Document document-bundle manifest format and the payment -> inputs -> validate -> deliver -> receipt sequence.
- [ ] Explicitly mark Stripe connection/account activation as the only remaining external gate for live links.
