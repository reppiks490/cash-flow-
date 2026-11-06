# Synthetic UI async request-state contract

Status: Experience Engineering draft change, 2026-11-06. This note documents
behavior in the isolated local demo only, not any production authorization.

## Bug reproduced

A user could select synthetic lead A, request a simulated scenario/policy,
switch to B, and back to A before the first response completed. An older
response for A passed the prior `selectedReference === ref` guard and
overwrote the newer A review, making the evidence panel stale.

## Resolution

Each scenario and consent-policy fetch captures both the selected-lead revision
(`selectionSequence`) and its own request sequence. Response and failure UI
updates are accepted only if the selected reference, selection revision and
request sequence all still match. Switching leads also clears the previous
consent detail immediately. Draft fetching already had a selection counter.

`view_races.test.cjs` uses deliberately reordered and rejected promise
responses. The product-only Node CI workflow runs `view_races.test.cjs` directly, so
standalone Python unittest does not require Node as a subprocess dependency. No new endpoints, libraries, credential
behavior, transmissions, storage, or paid services are introduced.

## Remaining

The UI is still a same-origin, localhost-only synthetic process demonstration.
Real customer data, consent, bookings, production auth, verified paid outcomes,
and live integrations remain prohibited/unverified. No claim of actual browser
screen-reader acceptance is made; the independent mobile QA checklist resides
in `web/ACCESSIBILITY_REVIEW.md` on draft PR #64.

This is the canonical Experience-owned async-state decision record; no change
to principal-owned `PROJECT_LEDGER.md` was attempted.
