# Revenue Recovery Engine architecture — contract rre.v1

**Status:** proposed isolated synthetic MVP, not production-ready. Python 3.11+ standard library only. HVAC first.

## Boundary and data flow

Synthetic JSON lead -> `backend.app.intake` -> SQLite leads with unique ID -> deterministic consent/service gate -> pending human-review draft -> mock CRM/appointment events -> tenant-scoped aggregate report. No sender, external network, payment gateway, or production credentials. In-memory DB by default. Any persistent DB must be private and excluded from Git.

## Frozen integration contract rre.v1

Input lead fields: `id`, `tenant_id`, `source`, `service` (nonempty strings), `consent` (boolean), `synthetic` (literal true). Allowed qualifying HVAC services: repair, maintenance, installation. `intake(db, lead)` returns `{id,status,schema}` with status `qualified|suppressed|new`; duplicate ID raises ValueError. `connect(path=':memory:')` enables foreign keys. `mock_event(db,event_id,lead_id,kind)` accepts only `appointment_mock|crm_mock` for qualified leads. `report(db,tenant_id)` returns scoped counts, mock event counts and null verified revenue/profit. `demo()` returns deterministic synthetic result. No production receipt can be inferred from a mock event.

## Ownership / lane interfaces

Principal owns this contract, `backend/app.py`, storage and ledger. AI lane owns `backend/qualification.py`, `followups.py`, `ai_providers.py`: adapters must not send messages; return evidence-based suggestions, not permission. Experience owns `web/`, `backend/crm.py`: consume report DTO; no direct external CRM writes. Commercial owns `commercial/`, `backend/onboarding.py`: no billing activation. QA owns `tests/`, `QA_LEDGER.md`: assert suppression, duplicate IDs, tenant scoping, absence of outbound/verified revenue. Contract changes require RRE-01 review and version bump.

## Security and release gates

Prototype only. No authentication, production tenant authorization, migrations, encryption-at-rest, real consent verification, rate limits, production audit trail, external scheduling/CRM or payment receipt reconciliation. SQLite tenant filtering is not an authorization boundary. Production requires explicit identity/tenant enforcement, privacy review, secret management, durable migrations, backup/restore, immutable evidence/audit log, human approval and opt-out policy, integration contract tests, independent QA and owner authorization.

## Reuse provenance and license audit

`cash-flow-` README describes standard-library evidence-backed qualification, private SQLite and receipt event handling; these are conceptual patterns, **not imported code**. MONEYFALL ZERO is untouched. `Icarus` README identifies proprietary all-rights-reserved trading infrastructure; **no code, assets, vendor data, secrets or runtime reused**. Third-party dependencies in this scaffold: none. Additional modules require file-level license and compatibility review before reuse.

## Acceptance

Run `python products/revenue_recovery/backend/app.py demo` from repo root. Expected: one synthetic qualified lead, one pending draft, one mock CRM event, `outbound_sent=false`, null verified revenue and profit. QA should independently run tests for duplicate, suppression, tenant filtering, no outbound and invalid inputs. No test execution is claimed merely by committing this document.
