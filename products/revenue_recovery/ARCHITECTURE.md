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


## Integration contract v0.2 — 2026-11-06 (supersedes v0.1 limitations above)

**Implementation proof:** isolated integration commit a7d692f13c3d69e25e033c6d1473f2faa8e1fb2b passed 24/24 RRE tests on GitHub Actions run 42250319834 (Python 3.11). Existing MONEYFALL tests passed separately. These are synthetic-only tests, **not a production/pilot qualification**.

- `GET /` or `GET /demo` -> redirects to `/demo/`.
- `GET /demo/`, `GET /demo/app.js`, `GET /demo/styles.css` -> exact-allowlist static UI served from `web/` on the same loopback origin. No directory listing, arbitrary file access, public CDN, external dependency or CORS.
- `GET /api/demo/recovery/{external_ref}` -> read-only preview for an already-ingested synthetic lead. Returns explicit `manual_review_required` qualification, `qualified=false`, `consent_verified=false`, an **UNSENT** draft (`approved=false`, `transmitted=false`), mock CRM preview (`dry_run=true`, `transmitted=false`), unbooked appointment (`confirmed=false`) and zero authenticated revenue receipts. It is a **deterministic placeholder**, not AI qualification.
- `POST /api/demo/leads` still accepts only the exact v0.1a schema. A duplicate with identical fields returns HTTP 200 unchanged, but reusing a reference with conflicting `source` or `need` now returns HTTP 409. No record is overwritten.
- Reject nonloopback `Host`, cross-origin `Origin` for mutations, and non-JSON content types. Serve `no-store`, CSP, no-sniff, denied framing. This is defense-in-depth **for a loopback synthetic demo**, not production authentication or tenant isolation.

**Browser demonstration (on operator's own computer only):**
```bash
PYTHONPATH=products/revenue_recovery python -m backend.app --port 8765
```
Open http://127.0.0.1:8765/demo/ and use a separate terminal to POST a synthetic lead; refresh the browser to see the lead in the pipeline and prepare a local unsent preview. Access the read-only recovery preview at `/api/demo/recovery/DEMO-001` after creating that synthetic record. There is no API for sending, billing, booking or signed receipts.

**Integration dependency:** The browser Draft action now fetches the read-only recovery-preview endpoint on the same local origin and explicitly falls back to an offline synthetic example. The AI Systems lane now provides deterministic evidence-labeled rule decisions and internal-only drafts (not actual LLM inference). Experience owns future customer-facing UX refinements. QA owns end-to-end security regression and release gates. Do not promote M1 to fully complete until these interfaces and negative tests converge.


### Five-lane synthetic integration v0.3

- The read-only `GET /api/demo/recovery/{ref}` now composes `backend.qualification.qualify_lead`, `backend.followups.prepare_followup`, `backend.ai_providers.get_provider("offline")`, and `backend.crm.preview_crm_record`.
- Qualification rubric v1 returns synthetic source/need evidence, rule category, non-calibrated priority score, explicit unknowns including consent/suppression, and `outreach_allowed=false`. The public preview stays `result=manual_review_required`, `qualified=false` because an internal rubric cannot verify real consent or buying intent.
- Draft contract v1 is internal only: `status=pending_human_review`, `sent=false`, `send_enabled=false`, `requires_human_approval=true`. The HTTP envelope retains `unsent_unapproved_draft` for browser compatibility. No outbound network adapters are configured.
- UI's **Load synthetic examples** uses only three fixed DEMO-HVAC references and enumerated local category fields; it posts to the same localhost synthetic API. Duplicate replay returns 200, conflicting fields 409.
- Reference identifiers now require `DEMO-` or `QA-` style prefixes; prefix checks reduce accidental PII insertion but do not establish data privacy or authorize real data ingestion.
- Browser static assets and active same-origin preview are regression-tested. GitHub Actions tests Python modules and `node --check` for JavaScript syntax; these are **not** headless visual/browser-interaction tests and cannot prove production quality.
- Latest completed exact-source verification as of this addendum: `fac3d74dbf2011d109266ecc336673580435ce41`, **35/35 RRE tests passed**, run 42252156846. Follow-up commit validation must be checked before any merge. All results are synthetic with no external services.
