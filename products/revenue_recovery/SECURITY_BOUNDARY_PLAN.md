# RRE tenant and authentication release architecture — 2026-11-06

**Status: design + synthetic policy exercises only. No authenticated users, real customer data, production infrastructure, database, key material or approved provider.**

The current local `backend/app.py` has no authentication and deliberately accepts only categorical synthetic demo records. It MUST remain loopback-bound. The new `backend/tenant_scope.py` module is an *unconnected mock*, not an auth server or an SDK to trust in production. Any test can construct a `DemoPrincipal`: its fields are **not cryptographic identity evidence**.

## Production boundary (not yet implemented)

```text
Browser / operator
  -> HTTPS reverse proxy (TLS termination, rate limits and request ID)
  -> identity provider (OIDC login; MFA policy and signed session validation)
  -> API authorization middleware (verified issuer/audience/expiry + session)
  -> tenant membership check (server-side subject-to-org binding)
  -> service commands (per-object action authorization)
  -> private PostgreSQL role with row-level security (RLS), NO BYPASSRLS
  -> provider-specific CRM/calendar and consent adapters (opt-in approved)
  -> immutable append-only audit + financial receipt reconciliation (private)
```

**Never** treat an HTTP `tenant_id` supplied by a client, a `role` JSON field, a homemade session cookie, or `DemoPrincipal` as proof of access. The server obtains tenant membership from its own verified identity/member store, not request parameters. A forged valid-looking tenant identifier must be insufficient.

## Minimum secure design decisions (owner and QA approval required)

1. Select an OIDC provider and domain/redirect routes; confirm token issuer and audience, signing algorithm/key rotation, expirations, revocation/session lifecycle, MFA, session cookies, CSRF protection and account recovery. No IdP or authentication material has been chosen yet.
2. Select a **private**, tenant-aware PostgreSQL deployment. Use per-request database roles / scoped RLS policies and explicit tenant memberships; never use a superuser, table owner bypass, or `BYPASSRLS` role for ordinary API traffic. Consider `FORCE ROW LEVEL SECURITY` for tenant tables. Test cross-tenant reads/writes using real DB connections, not Python dictionaries.
3. Design `organizations`, `memberships`, `inquiries`, `consent_records`, `message_reviews`, `appointment_events`, `payment_evidence`, `refunds`, and `audit_events` with mandatory tenant FK and unique external IDs scoped per tenant. Define legal and contractual retention/deletion requirements before ingesting PII.
4. Every endpoint must check both **function-level permissions** and **per-object tenant ownership**; no inference from opaque IDs. Never let roles silently escalate or use permissive default actions.
5. Store authentic provider webhooks in a private inbox with signature validation, replay window checks, idempotency and provider-origin evidence. A generated PDF, CRM 'closed' state, quote, or local mock is not a payment receipt.
6. Real SMS/email requires source consent, suppression history, communication purpose classification, current revocation check *at send time*, approved template, attributable sender, signed provider delivery receipt and owner-controlled kill switch. Legal review required.
7. Test SSRF/URL allowlisting in provider adapters, injection, secrets protection, webhook replays, audit tampering, object-level authorization, tenant enumeration, abusive resource consumption and network incidents.
8. Only then add production endpoints under `/api/v1/` in a separate authenticated service. Do not add a 'test auth bypass' or reuse the current `/api/demo/` routes for real client records.

## Acceptance cases required before ANY pilot

- Unauthenticated requests to tenant APIs: denied.
- Authenticated organization A subject requesting org B resource by guessing an ID: denied at controller and DB RLS.
- Revoked subject/session or revoked consent: denied even with a previously generated draft.
- Viewer cannot submit or approve messages, create bookings, change finances or view another tenant's records.
- Organization operator cannot grant themselves privileged roles; roles come from verified membership only.
- Missing/invalid provider signature and replayed webhook: rejected, not counted as revenue.
- PII never enters public GitHub logs, CI artifacts, uncensored browser errors, model prompts or email/SMS before privacy review.
- Backup restore and deletion requests preserve tenant boundaries; migration and incident drills pass.

## What today's added code actually verifies

The pure, dependency-free `tenant_scope.py` tests partition **synthetic in-memory fixtures** by a demo tenant identifier and deny simulated unauthorized actions. The module cannot validate OIDC, JWT signatures, sessions, MFA, RLS, real customer identity, durable storage, network transports, consent law or payment authenticity. It intentionally exposes no HTTP routes and is not used by the live local demo.

### Sources (reviewed 2026-11-06)

- OWASP API Top 10 2023: https://api-security.owasp.org/editions/2023/en/0x11-t10/
- OWASP broken object-level authorization: https://api-security.owasp.org/editions/2023/en/0xa1-broken-object-level-authorization/
- OWASP authentication guidance: https://cheatsheetseries.owasp.org/cheatsheets/Authentication_Cheat_Sheet.html
- PostgreSQL row security policies: https://www.postgresql.org/docs/current/ddl-rowsecurity.html

**Commercial release status remains BLOCKED.** Passing local mock tests does not satisfy tenant authentication or external financial verification. No Codex was invoked and no real data/services were added.
