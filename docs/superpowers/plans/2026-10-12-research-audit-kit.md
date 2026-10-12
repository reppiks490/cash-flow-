# Research Audit Kit Implementation Plan

> For agentic workers: use superpowers:executing-plans to implement natively, task by task; independent whole-branch review follows.

Goal:produce an evidence-linked research-audit sample as an adjacent offer capability.

Architecture:offline schema validator and escaped document renderer in one module; a small private-output CLI. Optional PDF uses existing ReportLab tooling. No source fetching or sales state change.

Tech stack:Python3.11+, standard library; optional ReportLab.

Spec:../specs/2026-10-12-research-audit-kit.md

## Global constraints
-10 sources,8 findings,8 limitations,500000 input bytes.
-Output outside public checkout, no overwrite,0600 files/0700 directory on POSIX.
-Explicit specimen/review labels; supplied evidence and untested hypotheses remain distinct.
-No new price, sender, network request, account, live record or performance guarantee.

## Review focus
-Malicious text/URLs must not create active HTML or PDF markup.
-Unknown/mismatched evidence must fail before file creation.
-Symlink destinations inside checkout must be rejected.
-Existing output must survive a rerun unchanged.
-Long text must remain legible and bounded; optional dependency failure must not leave a half-finished output.

## Task1:validated document producer
Files:src/moneyfall/audits.py; tests/test_audits.py; scripts/render_audit.py; config/examples/research_audit.json.
Interfaces:validate_audit(payload)->dict; render_markdown(report)->str; render_html(report)->str; write_audit(payload,output,repo,pdf=False,source_bytes=None)->dict summary with mode,findings,files.
-[ ] Write schema/evidence/escaping/privacy/no-overwrite/hash/CLI regressions first; run unittest discover -s tests -p test_audits.py and observe missing capability failures.
-[ ] Implement strict validation, escaped readable documents and atomic new-private-directory export; lazy optional PDF support. No third-party import for core mode.
-[ ] Run targeted/full unittest suite; run actual CLI specimen in a private directory, validate manifest hashes and PDF extractable text.
-[ ] Render PDF PNGs and inspect every page; correct layout defects before publishing.
-[ ] Publish source, fixture and docs in isolated branch with observed tests.

## Task2:commercial handoff and review
Files:docs/RESEARCH_AUDIT.md; scoped README/CONTINUATION/own board/task index; immutable Atlas message.
-[ ] Document exact commands, private boundaries, capability limits and unadopted pricing/offer status.
-[ ] Verify Markdown routes and whitespace; independently review code/schema/rendering.
-[ ] Send exact-head review request and fictional production evidence; retain incumbent/cohort unchanged until buyer evidence.

Pre-flight:CLI consumes the validator/renderer's exact signatures. PDF flag lazy-loads dependencies; validation/import/glyph validation completes before output-directory creation. Native execution chosen under user's autonomous reversible-work instruction; no repeated approval question. A separate reviewer/Atlas reviews the result before integration.

## Execution ledger

Task1 complete locally:64-test full suite exit0, CLI specimen exports, exact source/file hashes checked, three-page final PDF visually inspected. Initial missing-module RED established new capability absence. Independent review found Important Unicode corruption and inaccurate source hash; explicit glyph rejection and CLI original-byte provenance each reproduced RED then GREEN. Missing-dependency and exporter-cleanup cases now covered. No reviewed findings were left unresolved.

Ruling:add source_bytes optional interface and label canonical-payload basis for direct callers; otherwise normalization could misrepresent provenance. Cost if wrong:incorrect production source traceability. Ruling:require embedded DejaVu and reject unsupported PDF glyphs; HTML/Markdown remains available. Cost if wrong:limited PDF language coverage, explicitly documented.

Task2:docs/routing and remote publication complete; Atlas commercial/exact-head review requested on PR9. Integration remains pending. Independent author-external code review completed; source price/demand still unvalidated. No new core send/order/account activity.
