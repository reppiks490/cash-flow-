# Vellumflare Site source and deployment boundary

`apps/offer-page/index.html` is the repository’s canonical, self-contained Vellumflare Studio offer-page source for review and authenticated import into the owner’s private ChatGPT Site.

## What the canonical source includes

- Dependency-free authored WebGL/GLSL identity artwork with Vellum, Flare and Hybrid material states.
- Fold/unfold and dusk/golden-hour controls, pointer drag and keyboard arrow interaction.
- Adaptive pixel budget, approximately 30 fps render pacing, visibility/offscreen pausing, reduced-motion/global pause and WebGL context-loss fallbacks.
- Immersive dialog plus fallback artwork when WebGL is unavailable.
- Three fictional specimen modes and a bounded 15-second caption-led motion study.
- The fixed $149 pilot, exact scope/exclusions and non-performance-claim language.
- Browser-local brief preparation with copy, `.txt` download and encoded `mailto:` handoff. No remote form submit, automatic email, checkout or analytics runtime.

## Commercial boundary

The $149 pilot remains three portrait PNG graphics with editable SVGs, one caption-led 15-second motion preview, three captions + CTA options, one proof sheet and one consolidated revision. Production starts only after accepted scope, confirmed payment, approved inputs/assets and confirmed capacity. Filming, voiceover, paid stock, publishing, account management, ad spend, open-ended editing and custom 3D production are outside this pilot. The WebGL sculpture is website identity artwork, not a client 3D deliverable.

The page does not promise or guarantee leads, sales, revenue or campaign performance. Specimens are fictional and uncommissioned.

## Privacy and payment boundary

This repository is public. Do not add private contacts, prospect/customer data, payment credentials, receipts, secrets or owner-private operational state to this page. The repository source deliberately carries no automatic send or configured checkout. A deployed Site may supply an owner-approved public contact route through its private/authenticated deployment process without committing private account state here.

## ChatGPT Sites deployment status

The currently linked Vellumflare ChatGPT Site is an owner-private deployment. In the 2026-10-12 refinement session, the Site is readable as a Library Site projection but its editable HTML/GLSL source is not exposed through the available connector surface; the external Site URL also requires ChatGPT authentication. Therefore this branch does **not** claim to have overwritten, published or changed the private Site.

Before an eventual authenticated Site import, diff this canonical source against the then-current editable Site source. Preserve any private Site-only contact configuration and do not regress current interactions. Browser/device QA belongs to that authenticated deployment step; repository CI proves code/static contracts, not a successful private-Site publication.

## Verification

Primary contract test:

```bash
PYTHONPATH=src python -m unittest tests.test_offer_page -v
```

Whole repository verification:

```bash
PYTHONPATH=src python -m unittest discover -s tests -v
PYTHONPATH=src python -m moneyfall rank
PYTHONPATH=src python -m moneyfall demo
```

`tests/test_offer_page.py` pins identity/scope language, required interaction controls, keyboard/reduced-motion contracts, renderer initialization order, per-canvas WebGL fallbacks, the 15-second motion limit, local-only brief behavior and the absence of external runtime/checkout dependencies.

## Provenance

This source is a repository reconstruction/superset of the known deployed Vellumflare behavior documented in the Atlas Vellumflare and immersion checkpoints. It intentionally avoids claiming byte-for-byte identity with the private Site because this session cannot retrieve that editable source bundle.
