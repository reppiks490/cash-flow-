# Portrait layout production

C12 is a bounded creative-kit improvement for the existing $149 pilot. The
incumbent deliverables remain three 1080×1920 PNGs with editable SVGs, three
captions/CTA options, a caption-led 15-second motion preview and one revision.
The 48-hour clock still requires accepted scope, verified payment and approved
assets. No filming, voiceover, publishing or performance promise is added.

## Contract and design decision

Set an optional `layout` on each card. Existing jobs default to `statement`.

| Layout | Intended composition |
|---|---|
| `statement` | Dark grid, outlined frame and large typography |
| `editorial` | Light paper tone, vertical accent and subdued card number |
| `split` | Dark frame with an accent headline panel |

PNG and SVG share the same positioned text and shapes. SVG text stays editable;
rendering software needs DejaVu Sans or an acceptable substitute. The proof PDF
embeds DejaVu regular/bold and fits its company title using measured width.
This addresses the repeated-layout criticism recorded by Atlas without changing
price, output count or production scope. Marketability is a hypothesis until
real customer responses support it.

Long unbroken words wrap within the measured column. Unknown layouts, invalid
or transparent accent colors, multiline/oversized CTAs and excessive headline
or body copy fail before that card is exported. Accent-panel headlines and CTAs
select the light or dark foreground with greater luminance contrast. Brand-color
matching and accessibility still require final human inspection; arbitrary
images, logo placement, font uploads and unsupported glyphs are outside this
renderer. A later card failure can leave earlier files in a kit directory:
render into a fresh private directory and treat incomplete kits as failed.

## Customer-facing proof brand

Proof jobs now accept an optional top-level `brand`. The compatibility rule is
deliberate:

- A historical job with no `brand` keeps the legacy `MONEYFALL` proof header so
  old inputs can be reproduced without a silent identity change.
- New Vellumflare customer-facing jobs should set
  `"brand": "Vellumflare Studio"` explicitly. The public fictional example does
  this now.
- Brand values are trimmed, must be non-empty single-line text and are capped at
  64 characters. Invalid values fail before production output is created.
- The validated brand is written into `manifest.json` so the identity used for a
  proof is part of its provenance.

The brand parameter changes the customer-facing proof PDF title/header and
manifest metadata. It does not change the fixed pilot scope, historical order
state, customer claims, payment evidence or asset-permission requirements. Do
not bulk rewrite old private manifests merely for cosmetic consistency; rerender
only when the underlying private workflow actually requires a new artifact.

## Reproducible fictional specimen

The example contains only an invented studio and original demonstration copy.
It is not a real prospect, customer or conversion result. It explicitly selects
Vellumflare Studio so a fresh demonstration no longer inherits the legacy
MONEYFALL proof header.

```bash
PYTHONPATH=src python scripts/render_proof.py \
  config/examples/creative_layouts.json /PRIVATE/FRESH_OUTPUT
```

The output must be outside the public checkout. Pillow, ReportLab, the DejaVu
font files and FFmpeg are production dependencies; see LAUNCH.md. `--no-video`
is acceptable for local card iteration, but is not a complete paid deliverable.
Commissioned production still requires `--commissioned-order`, private order
state, verified payment, approved asset permissions and full video output.

Inspect all three cards, escaped SVG copy, PDF, captions and the video. Confirm
portrait dimensions, 15-second duration, specimen/client labels, the intended
proof brand and manifest hashes. Confirm approved brand claims and permissions
separately. No specimen or generated manifest is evidence of payment, delivery
or commercial success.

## Verification checkpoint

Nine original C12 regression tests cover wrapping, layout selection/defaults,
editable SVG copy, escaping/client labels, failure behavior, dark-accent
visibility, embedded PDF fonts and a wide company title. The later proof-brand
contract adds standard-library tests for legacy compatibility, explicit
Vellumflare selection, validation, renderer wiring, manifest provenance and the
fresh public example. Standard CI exercises those contracts even when optional
media dependencies are absent.

The original C12 local checkpoint reported 55 main-baseline-plus-feature tests
with media/PDF dependencies installed. A local compatibility snapshot combining
C04 receipt changes, C11 audit production and C12 passed 77 tests; rank,
synthetic demo and whitespace checks also passed. Those figures are historical
publication evidence, not the current branch test count.

The fictional C12 kit was previously rendered with full FFmpeg output and
visually checked. `ffprobe` reported 1080×1920 and 15.000000 seconds. That earlier
visual check predates the Vellumflare proof-brand parameter. Therefore a freshly
branded private production artifact still requires the normal PDF/video visual
inspection before any real send. Optional-media tests skip when their dependencies
are absent; a standard-library-only CI result does not replace production QA.

Latest independent review and combined integration: [Atlas checkpoint](research/atlas/2026-10-13-immersion-and-integration.md). The preceding paragraphs preserve the original publication evidence.
