# Vellumflare Site Refinement Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Make the repository’s canonical offer page a self-contained, conversion-focused Vellumflare experience that preserves the deployed private Site’s known interactions, materially deepens immersion beyond CSS/SVG, and remains honest about the fixed $149 pilot and activation gates.

**Architecture:** Keep `apps/offer-page/index.html` as a zero-dependency, portable Sites-ready artifact with inline layout CSS, accessible HTML, WebGL shaders, and local-only interaction logic. Add standard-library Python contract tests that parse the page and pin business scope, accessibility controls, motion/fallback behavior, and the absence of automatic submission/checkout. The existing private ChatGPT Site remains untouched because this session exposes only a read-only Site projection; deployment/import is a separate authenticated Sites action.

**Tech Stack:** HTML5, CSS, vanilla JavaScript, WebGL/WebGL2-compatible GLSL, Python 3.11 `unittest`/`html.parser`.

**Spec:** `docs/research/atlas/2026-10-12-vellum-ui-and-resources.md` plus `docs/research/atlas/2026-10-13-immersion-and-integration.md`; current user-approved refinement direction in this conversation supersedes cosmetic limitations but not the commercial scope or privacy boundaries.

## Global Constraints

- Preserve the fixed $149 pilot: three portrait PNG graphics + editable SVGs, one caption-led 15-second motion preview, three captions + CTA options, one proof sheet, one consolidated revision.
- Preserve the 48-hour start condition: accepted scope, confirmed payment, approved inputs/assets, and available capacity.
- Do not promise leads, sales, revenue, campaign performance, or buying intent.
- Do not add custom 3D production to the $149 client scope; the WebGL sculpture is website identity artwork.
- Do not auto-send email, auto-submit form data, create a checkout, or imply payment is configured.
- No paid/external runtime dependency, downloaded model, texture, analytics script, or framework.
- Respect reduced motion, keyboard operation, visible focus, WebGL unavailability/context loss, hidden/offscreen throttling, and mobile pixel budgets.
- No prospect/customer/payment data, secrets, credentials, or protected operational state in the public repository.
- The private Sites audience and existing deployment must not be changed from this branch.

## Review Focus

- WebGL unavailable or context lost: the page must expose an original visual fallback and keep all commercial content usable.
- Reduced-motion or global pause: animated UI and shader time must stop without disabling controls or content.
- Keyboard-only use: nav, material controls, immersive dialog, specimen choices, motion study, FAQ, and brief composer must remain operable with visible focus.
- Brief data containing punctuation/newlines: generated copy/download/mailto must encode safely and must never submit automatically.
- Small screens/low GPU budget: rendering must cap resolution and avoid making the hero or CTA dependent on WebGL.

---

### Task 1: Pin the offer-page product contract with failing tests

**Files:**
- Create: `tests/test_offer_page.py`
- Read: `apps/offer-page/index.html`

**Interfaces:**
- Consumes: the existing static page at `apps/offer-page/index.html`.
- Produces: `OfferPageContractTests`, a standard-library regression suite that later tasks must satisfy.

- [ ] **Step 1: Write failing contract tests**

Create tests that assert:
- `Vellumflare Studio`, `$149`, `15-second`, `editable SVG`, `one consolidated revision`, `confirmed payment`, and a no-results-promise disclosure exist.
- unique IDs and controls exist for `atelier-canvas`, `immersive-dialog`, `motion-toggle`, `material-vellum`, `material-flare`, `material-hybrid`, `fold-toggle`, `light-toggle`, specimen selectors, and local brief actions.
- the document has a skip link, explicit labels, a global motion toggle, `prefers-reduced-motion`, and a visible WebGL fallback.
- JavaScript includes local `Blob` download, clipboard handling, URI-encoded `mailto:`, a 15-second motion bound, visibility/offscreen pausing, and WebGL context-loss handling.
- there is no form `action` to a remote endpoint, no `fetch(`, `XMLHttpRequest`, external `<script src>`, payment/checkout script, or automatic send language.

- [ ] **Step 2: Run the new test file and verify RED**

Run: `PYTHONPATH=src python -m unittest tests.test_offer_page -v`
Expected: FAIL because the current repository page lacks the Vellumflare/WebGL/local-brief contract.

- [ ] **Step 3: Commit the RED test**

Commit: `test: pin Vellumflare offer page contract`

### Task 2: Build the canonical immersive Vellumflare page

**Files:**
- Modify: `apps/offer-page/index.html`
- Test: `tests/test_offer_page.py`

**Interfaces:**
- Consumes: all stable IDs/behaviors pinned by Task 1.
- Produces: one self-contained Sites-ready HTML artifact with `VellumRenderer`, specimen state, 15-second motion-study state, global pause/reduced-motion state, and a local-only brief composer.

- [ ] **Step 1: Implement the semantic/conversion structure**

Use a sticky but lightweight nav, hero, atelier, concept room, deliverables, pilot/process, FAQ, brief composer, and footer. Preserve the exact commercial boundaries from Global Constraints and keep CTAs conversation/brief-oriented rather than checkout-oriented.

- [ ] **Step 2: Implement the immersive engine**

Add a dependency-free WebGL renderer using authored vertex/fragment shaders for folded vellum, emissive flare/core, fibers/noise, atmosphere and pointer-responsive light. Provide Vellum/Flare/Hybrid modes, fold and atmosphere controls, pointer/arrow rotation, adaptive DPR/pixel budget, visibility/offscreen pause, context-loss recovery, and a meaningful non-WebGL fallback.

- [ ] **Step 3: Implement cinematic but accessibility-safe UI motion**

Add scroll reveal/progress, layered ambient movement and section transitions that stop under `prefers-reduced-motion` or the global pause control. CSS/SVG may support layout/decorative polish but must not be the primary immersive engine.

- [ ] **Step 4: Implement functional specimens and 15-second motion study**

Specimen choices must update the live concept copy/CTA and the motion study. The motion player must support play/pause/restart, expose progress accessibly, stop exactly at 15 seconds, and remain usable while global motion is paused.

- [ ] **Step 5: Implement the local-only brief composer**

Validate required fields locally, render a human-readable brief preview, support copy-to-clipboard with fallback, `.txt` download using `Blob`, and an encoded `mailto:` handoff. Never submit automatically and never claim a message was sent.

- [ ] **Step 6: Run Task 1 tests and verify GREEN**

Run: `PYTHONPATH=src python -m unittest tests.test_offer_page -v`
Expected: all offer-page contract tests PASS.

- [ ] **Step 7: Run JavaScript syntax verification**

Run: extract inline script to a temporary file, then `node --check` it when Node is installed; otherwise record the environment limitation and rely on CI/static contract checks without claiming a Node check.
Expected when available: exit 0.

- [ ] **Step 8: Commit the implementation**

Commit: `feat: deepen Vellumflare immersive offer page`

### Task 3: Route the canonical site and verify the whole repository

**Files:**
- Create: `docs/VELLUMFLARE_SITE.md`
- Modify: `README.md`
- Modify: `docs/CONTINUATION.md`
- Modify: `coordination/board/chatgpt.md`
- Create: `coordination/inbox/to-atlas/<UTC>-chatgpt-vellumflare-canonical-source.md`
- Test: `tests/test_offer_page.py`

**Interfaces:**
- Consumes: the canonical page from Task 2 and the existing Atlas/private-Sites operator split.
- Produces: durable routing for the source/deployment boundary and a peer handoff that does not overwrite Atlas-owned private state.

- [ ] **Step 1: Document the source/deployment boundary**

Record that `apps/offer-page/index.html` is the canonical self-contained Vellumflare source for review/import, while the linked ChatGPT Site remains an owner-private deployment whose editable source is not exposed in this session. Include the exact known current Site project ID only where already public within owner-facing docs is appropriate; do not add private contact/payment state.

- [ ] **Step 2: Update README/CONTINUATION/own board and send Atlas a sanitized handoff**

Route the new page, test command, branch/commit evidence, preserved $149 scope, and the fact that no Site publication/payment/send occurred. Request that any eventual private Sites import be diffed against the current deployed source to avoid interaction regression.

- [ ] **Step 3: Run the full repository verification suite**

Run: `PYTHONPATH=src python -m unittest discover -s tests -v`
Expected: 0 failures.

Run: `PYTHONPATH=src python -m moneyfall rank`
Expected: exit 0 and no claim that assumptions are observed revenue.

Run: `PYTHONPATH=src python -m moneyfall demo`
Expected: exit 0 and synthetic/demo labeling retained.

- [ ] **Step 4: Commit documentation/routing**

Commit: `docs: route canonical Vellumflare site source`

- [ ] **Step 5: Open a pull request and inspect CI**

Create a PR from `codex/vellumflare-site-refinement` to `main`. Do not merge until current CI and final review are green. A passing repo PR does not imply the private ChatGPT Site was deployed or browser/device-tested.
