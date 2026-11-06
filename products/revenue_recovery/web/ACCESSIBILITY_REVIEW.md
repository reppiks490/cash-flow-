# Revenue Recovery demo — keyboard/mobile review checklist

**Scope:** `products/revenue_recovery/web/` on the isolated synthetic HVAC demo.
**Status:** Static automated checks added. Manual Chromium/mobile VoiceOver/TalkBack
inspection is **not complete**. No actual customer data or production authorization.

## Implemented (2026-11-06)

- Focusable horizontal table region with a descriptive accessible name and
  on-screen arrow-key guidance; wide table remains horizontally scrollable.
- Focusable, individually named scroll regions for the mock event trail and
  synthetic consent/suppression details.
- Explicit keyboard focus outline and mobile buttons with at least 44px
  specified minimum height; no external fonts or frontend build dependencies.
- `mobile_accessibility.test.cjs` enforces the contract. The
  `test_mobile_accessibility.py` bridge makes existing product Python CI
  execute it; no modification of QA-owned workflows.

## Manual QA still required

At **320, 375, 768, 1024, and 1440 CSS pixels**, inspect the *actual served*
`http://127.0.0.1:8765/demo/` page, not a mock-up, using Chromium plus mobile
browser keyboard/assistive technology where possible. Record viewport,
browser/version, OS, exact Git SHA, screenshots, console errors, and whether
buttons/regions are reachable and usable.

Keyboard traverse: skip link → navigation → seed/refresh → pipeline table
→ Draft → copy → scenario and consent controls. Verify horizontal arrow-key
scroll, visible focus, 200% zoom/reflow, contrast, screen-reader announcements,
no trapped focus, and reduced-motion behavior.

**Do not** claim WCAG conformance from regex/VM checks. Real browser and mobile
assistive-technology results, live integrations, operator authorization,
authenticated tenants, consent evidence and signed receipts are unverified.

## Rollback / contract notes

Changes are limited to HTML/CSS and test files; no API changes or send paths.
Undo by reverting this isolated PR after review. The API continues to use
`backend/contracts.py` for its synthetic-only allowlists.

**Knowledge delta:** new keyboard navigation and scoped manual verification
requirements reside here; the principal project ledger remains principal-owned.

## Forward-port provenance (2026-11-06)

This copy preserves the substantive Experience PR #64 checklist and its
original branch/commits. New draft PR #94 is based on `main` at
`ff76773caaacae0717f5e53bbbf295f5a6974d1e` and ports only
the owned HTML/CSS behavior. Three new checks were appended to the
existing `web/dom_contract.test.cjs`, which the standard non-Codex
GitHub Actions workflow already executes; the old optional Python-to-Node
bridge and extra static Node suite were intentionally not duplicated.

Test-first evidence: RRE run 42303904058 on test-only commit
`c3360451` failed exactly three Node accessibility assertions (15/18
Node tests passed; Python suite 160 tests executed). This shows the
requirements were not already satisfied on the current baseline. This
document does **not** claim a passing implementation run or real-browser
screen-reader certification.
