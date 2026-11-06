# Synthetic evidence viewer: fail-closed display contract

Scope: local-only HVAC demonstration; implementation in `web/app.js`.
No actual customer records, outreach, signed receipts, provider connections,
consent records, or production release authorizations are accepted.

## Problem / source contracts

`backend/demo_evidence.py` emits numbered fixture events (up to seven) with
ASCII underscore-separated `event_type` codes, not contact details or
attested real-world outcomes. `backend/consent_simulation.py` emits
underscore-separated internal `reasons` and a `suppressed` boolean that is
true only for `revoked_mock`, in which case `draft` must be null.

Before the browser patch, a forged same-origin JSON response could put a
free-text contact-like value into an event type or consent reason and have it
rendered as if it were trusted fixture evidence. It could also report
suppressed consent while retaining an unsent draft for `unknown` policy.

## Experience-only defense in depth

The browser now accepts only bounded lowercase ASCII underscore-delimited
event/reason codes (`^[a-z][a-z0-9_]{0,95}$`). Scenario event arrays have a
seven-event cap; sequence numbers must be safe integers from 1 through 7.
Consent reasons are capped at 16 entries. Suppression must match the chosen
mock case; revoked cases require a null draft, other cases a bounded string.
Existing zero-verified-receipt, no-send, no-booking, and synthetic checks remain.

A malformed response produces an *unavailable* message and no new evidence
details; there is no attempt to sanitize the data into a valid customer event.
This is not a substitute for validation by the server or real authentication,
tenant isolation, consent and approval.

## Repeatable validation

From repository root with Node.js:

```sh
node --test products/revenue_recovery/web/test_app.mjs
```

The existing product-only GitHub Actions workflow also executes that suite.
The three negative regression cases target event-label free text, policy
reason free text and contradictory suppression. Their test-only commit
`efa1364d` recorded **RED** in RRE workflow run `42303387655`
(15/18 Node checks passed, three intentionally failed). A passing full run
on the implementation/merge head must be recorded separately before merge.

## Coordination and rollback

This change is owned by Experience Engineering and touches only `web/`.
The earlier independent PR #68 adds stale-result ordering guards in the
same `web/app.js` functions, so the two diffs require deliberate integration
on the latest `main` after QA review. Do not force-push either source branch.
Reverting this PR affects browser-side rendering validation only and does
not turn on external services.
