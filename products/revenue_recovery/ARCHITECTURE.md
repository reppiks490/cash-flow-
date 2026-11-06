# Revenue Recovery Engine: initial contracts (v0.1)

This is an isolated, synthetic-only bootstrap. Existing MONEYFALL and ICARUS applications are unaffected. No actual contact information, billing, external communications, CRM secrets or prospect lists may enter this prototype.

## Vertical and scope

HVAC: qualify an incoming inquiry, identify pending requests or estimates, draft an owner-approved follow-up, link a scheduling/CRM acknowledgment and attribute actual closed work only against authenticated receipts once those later capabilities exist. The initial code proves lead intake only. AI, UI, CRM, payment and tenant handling are future modules, not completed functionality.

## Running locally

From repo root: PYTHONPATH=products/revenue_recovery python -m backend.app --port 8765
Only 127.0.0.1 binding is supported. Process-local records disappear on stop. No dependency except Python 3.11+.

## API v0.1

- GET /health -> {"service":"revenue-recovery-demo","status":"ok","synthetic_only":true}
- POST /api/demo/leads JSON {"synthetic":true,"external_ref":"demo-01","source":"website","need":"AC not cooling"} -> 201 when created or 200 when duplicate; {"lead": {..., "status":"received"}, "created": boolean}. Keys are restricted to the four documented fields; real names, phone numbers, email and addresses are rejected.
- GET /api/demo/leads -> {"synthetic":true,"leads":[...records...]}

No customer contact or personal data, real sends, money movements, live CRM integration or persistent state is supported.

## Integration strategy and ownership

- Principal owns these v0.1 contracts, backend HTTP entrypoint and data persistence roadmap. Change public contracts through issue RRE-01; do not assume v0.1 is a production API.
- AI owns deterministic qualification.py, followups.py, ai_providers.py. Initially expose pure functions consuming the documented lead dict and returning explicit synthetic/evidence fields; no outbound side effects.
- Experience owns web/ and crm.py. Can initially render fixture records and point to the local demo endpoints. No cross-origin CORS or public deployment yet.
- Commercial owns commercial/ and non-charging onboarding stubs; clearly label price and conversion assumptions.
- QA owns tests/, the QA ledger and optional non-Codex scoped CI. Validate duplicate behavior, synthetic-only enforcement, absent auth and no receipt claims.

## Production gates

No production deployment until authentication and tenant isolation, private durable storage with encryption/backup policy, consent/opt-out procedures, outbound transport reviews, approved integration credentials, auditing, rate limits, security tests, compliance review, and operator approval. The in-memory demo service is intentionally not appropriate for public access.
