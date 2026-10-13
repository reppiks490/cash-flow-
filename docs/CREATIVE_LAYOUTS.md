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

## Reproducible fictional specimen

The example contains only an invented studio and original demonstration copy.
It is not a real prospect, customer or conversion result.

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
portrait dimensions, 15-second duration, specimen/client labels and manifest
hashes. Confirm approved brand claims and permissions separately. No specimen
or generated manifest is evidence of payment, delivery or commercial success.

## Verification checkpoint

Nine new regression tests cover wrapping, layout selection/defaults, editable
SVG copy, escaping/client labels, failure behavior, dark-accent visibility,
embedded PDF fonts and a wide company title. Main baseline plus C12: 55 tests
passed locally with media/PDF dependencies installed. A local compatibility
snapshot combining C04 receipt changes, C11 audit production and C12 passed
77 tests; rank, synthetic demo and whitespace checks also passed. This is
compatibility evidence, not a claim that the branches are merged.

The fictional kit was rendered with full FFmpeg output and visually checked.
`ffprobe` reported 1080×1920 and 15.000000 seconds. Optional-media tests skip
when their dependencies are absent; a standard-library-only CI result does not
replace production QA. Atlas exact-head/commercial review remains separate.

Latest independent review and combined integration: [Atlas checkpoint](research/atlas/2026-10-13-immersion-and-integration.md). The preceding paragraphs preserve the original publication evidence.
