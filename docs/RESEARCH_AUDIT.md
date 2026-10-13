# Evidence-linked audit production

Implementation is present in this tree. Exact-head Atlas review and combined integration evidence are recorded in the [2026-10-13 checkpoint](research/atlas/2026-10-13-immersion-and-integration.md). This local producer is not an automatically deployed service.

This adds a complementary research deliverable to the existing content-kit capability. It is an offline producer, not a website scanner, conversion optimizer, paid order, new price or replacement incumbent. Atlas owns commercial/source review; ChatGPT owns the implementation.

Useful formats include a website/CTA clarity review, a source-based content-opportunity brief or white-label client research. Each requires real source review and separately agreed scope. No analytics, buying intent, complete-page absence or revenue improvement is inferred from a small supplied excerpt.

## Generate the fictional specimen

From the checkout, with Python3.11+:

```bash
PYTHONPATH=src python scripts/render_audit.py config/examples/research_audit.json /PRIVATE/new-audit
# Optional PDF, in a different new directory:
PYTHONPATH=src python scripts/render_audit.py config/examples/research_audit.json /PRIVATE/new-audit-pdf --pdf
```

Replace /PRIVATE with an actual private location outside the checkout. Existing output directories are refused, including a rerun against the same path. HTML/Markdown need only the standard library. PDF additionally needs ReportLab and DejaVuSans.ttf / DejaVuSans-Bold.ttf under /usr/share/fonts/truetype/dejavu or MONEYFALL_FONT_DIR. These are renderer fonts, not a promise to support arbitrary client brand-font imports. Unsupported glyphs fail clearly before output; use HTML/Markdown rather than silently corrupting evidence.

Outputs:audit.md, audit.html, optional audit.pdf and a private manifest. CLI stdout contains only mode, finding count and filenames. All files are0600; the new directory is0700 on POSIX. Do not commit live source excerpts, companies, reports or hashes tied to private clients. The public JSON fixture is entirely fictional and uses example.org.

## Input contract

Use the fixture as a schema example. The required fields are schema_version1, mode(specimen/review), reviewed:true, company, objective, sources, findings and limitations.

Each source has unique simple id, public HTTPS URL, timezone-aware observed_at and an excerpt. Each finding has title, priority(P1/P2/P3), known source_id, evidence_quote that literally appears in the supplied excerpt, observation, impact_hypothesis, recommended_action and counter_evidence.

Limit:10 sources,8 findings,8 limitations; CLI reads at most500000 bytes. Source excerpts max8000 characters, evidence quotes1600, finding fields1600, company200, objective1600. Required content must be nonempty. Priority is human action order, not expected profit. Human reviewed:true is an operator attestation, not authenticated evidence or a substitute for checking claims.

Specimen mode explicitly labels fictional/uncommissioned work; review mode labels supplied observations without claiming commissioned delivery. Every format states that business impact is not measured. Do not use reviewed mode to imply an independent live website read or permission to charge/deliver.

The manifest hashes exported files. The CLI input_sha256 binds exact original JSON bytes with input_hash_basis=exact_source_bytes. Direct Python calls without source_bytes instead bind canonical supplied payload JSON and label that basis. normalized_report_sha256 separately hashes the validated report. None is a provider send, payment or customer-delivery receipt.

## Commercial use and handoff

Prepare one source-backed real example only when a concrete issue is demonstrable. Ask the buyer whether the scoped research/action deliverable is useful before expanding production. Preserve counter-evidence and unknown impact; do not fabricate a defect to create demand. No new audit price/license/deadline is adopted by this feature. Current149-dollar creative scope remains unchanged.

Atlas may generate a private example with its actual source observations and critique the report for buyer fit. Do not add a duplicate outreach cohort or modify existing drafts without the agreed operator's frozen test. Real payment, approved scope/rights and actual delivery evidence remain separate.

## Verification and decisions

Native isolated implementation; no paid calls or network acquisition. Initial tests failed because the new module/CLI did not exist. Independent review reproduced two important findings:base-font Unicode corruption and normalized-report hash masquerading as source-input hash. Both corrected with failing-first regressions; exporter cleanup and missing optional dependency have checks. All64 main-baseline-plus-audit tests pass locally; PDF optional cases exercised with installed ReportLab. Runner environments lacking PDF tooling skip its two optional cases; core remains dependency-free.

The final fictional sample is three A4 pages; all pages rendered and visually reviewed, readable text extracted and file/input hashes checked. DejaVu fonts are embedded; missing glyphs are rejected. No profit, buyer demand, live source collection or paid order is established.

Design:[spec](superpowers/specs/2026-10-12-research-audit-kit.md). Execution:[plan](superpowers/plans/2026-10-12-research-audit-kit.md). Current commercial roles/objective:[agreement](CURRENT_EXECUTION.md).

Offer-page source now introduces a separately scoped research option and clarifies current typography/motion versus special-asset/native-format requirements. The existing149-dollar creative price is preserved. Source changes are not a deployment or update to the owner-private Sites preview; Atlas must review commercial fit before publication.
