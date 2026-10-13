# Vellumflare draft refresh and source comparison

Atlas, 2026-10-13. Scope: C06 private operations and independent review of the new core-owned branding and offer-page work. User asked to continue the immersive build and begin the next commercial work. The 14–20-day profit objective and zero-upfront constraint remain; no guaranteed result.

Related planning records: [original launch implementation](../../superpowers/plans/2026-10-12-launch.md) and [repository Vellumflare refinement](../../superpowers/plans/2026-10-12-vellumflare-site-refinement.md). Their historical assumptions do not supersede [CURRENT_EXECUTION](../../CURRENT_EXECUTION.md) or the dated operational observations below.

## Operational result

Five accepted original-cohort Gmail drafts were updated in place with the reviewed conditional CTA, exact $149 pilot scope, Vellumflare Studio identity and owner-supplied commercial mailing footer. No new provider drafts were created. Five original proof PDFs were regenerated into fresh private paths using the reviewed embedded-font renderer; the existing cards and researched copy were retained. All five PDFs were visually inspected.

Provider raw MIME readback verified each sender, recipient, reply-to, subject, exact HTML body, attachment filename and attachment SHA-256; all five remained DRAFT. New packet hashes were saved, prior message/draft lineage retained, and old packet versions marked superseded. Contact/company suppression and send reservations were preserved. Current private packet state: ten drafts and ten superseded historical revisions. Zero sends, paid orders or collected revenue. The remaining factual activation gate is the verified user-owned payment destination.

Historical prepared-only notes describe earlier checkpoints. This report supersedes them for the five-packet refresh, without deleting their provenance. No private identities, contacts, draft text or account details belong in this public report.

## Current source and verification

- Deployed Site source: `c6c3e8720155a7e1ebf3a9a24de6a89aa2996fdb`, version 5. Authenticated Site read confirms active, owner-private, one allowed user and no external visitors. The deployment was not replaced during this review.
- Core review tree: main `75262a3d036389a04aff7a65cd37a25485188c87`, containing PR13 head `55249bd35083b5f3a8775c85dfb39f2a6a55a9f4`, PR14 head `8e987bae8b4956e684a6bb667e7ba6da966a1179` and PR15 head `795de4fcfc69082ef1130dcddef8ab6c35d9039b`.
- All 93 repository tests passed locally with optional Pillow/ReportLab available. JavaScript syntax, rank and synthetic demo passed. Synthetic money remains distinct from operational revenue.
- The deployed Site has a raymarched 3D scene, continuous fold/light controls, one canvas moved into immersive view, still-image fallback and a configured local brief handoff. The repository page is an independent self-contained reconstruction with multiple renderers and different controls/shader behavior. It is not a byte-identical source or an established functional superset.
- Real browser/mobile-device QA is unavailable in this session. The deployed source's prior GLES rendering and DOM-contract checks remain their stated evidence, not device verification.

## Findings on the repository reconstruction

The existing tests check static contracts and do not catch these reproduced runtime defects. [The isolated DOM/WebGL-call reproducer](fixtures/vellumflare-source-review.cjs) uses the public source, mocked browser APIs and deterministic frame scheduling; it is not a browser test. Run it with `node docs/research/atlas/fixtures/vellumflare-source-review.cjs`. It checks desired behavior and currently reports four failures.

1. **Reduced-motion blank state.** Renderer initialization hides fallback artwork and schedules the first frame. The final global-pause call cancels that frame on reduced-motion startup. No frame is drawn and no fallback remains visible. Draw a still frame before pausing; manual controls also need a still redraw.
2. **Immersive state reset.** The dialog renderer starts at default Hybrid/fold/light settings regardless of the selected material and changed lighting. Copy the current state before its first draw.
3. **Closed-dialog rendering.** Closing pauses the dialog, but a later visibility/observer synchronization can restart it because the pause predicate omits `immersiveDialog.open`. Include dialog visibility in that predicate.
4. **False clipboard success.** When the legacy `execCommand('copy')` fallback returns false, the page still reports that the brief was copied. Check the return value and present a truthful selection/download fallback.

These findings concern the reconstructed repository page, not regressions observed in the deployed Site. Core corrections were requested on PR13. Import remains deferred until a focused corrected-head review and explicit source comparison. The working authenticated deployment is preserved.

## Branding review

Explicit `brand` selection in the new proof and outreach helpers preserves the omitted-brand legacy behavior. Atlas acknowledges the future-job/profile usage rules in all three peer messages. Future Vellumflare render jobs and legitimate newly built packets can set `brand` explicitly; existing provider drafts will not be rewritten solely to adopt a new internal field.

One general-input PDF issue was measured and reported on PR14: a valid 64-character all-W brand plus the specimen suffix occupies 831.94 points at the configured font size, exceeding the 532-point header width. Fit or reject the complete measured header before drawing. The actual Vellumflare Studio label fits and the five private proofs passed visual review.

## Ownership and next action

Atlas retains C06–C08 for the original cohort. Core code, shared task state and the reconstructed offer-page fixes remain with ChatGPT/Codex; there is no silent ownership transfer or parallel sender. Payment activation and any change to the Site's audience require the respective real account facts/user choice. No unattended scheduler was created.

Knowledge delta: this report, the outgoing acknowledgment and Atlas board. New executable content is only the isolated review reproducer in this owned report directory. Existing coordination and launch rules supply the repeated procedure; no new skill, dependency or enforcement rule is introduced. Inline business/product/ops review preserved scope, ownership, lineage, privacy and honest revenue distinctions. Librarian review checks that the report, reproducer and exact peer replies are reachable from the existing Atlas board/router. Akinator ledger/scope/conflict helpers are available again in this resumed environment; their results are recorded in the publication conversation rather than treating historical unavailability as current truth. No framework migration or shared-router rewrite is part of this review.

The initial strict coverage check found two previously unindexed related plans; the contextual links above correct their reachability without editing core-owned routers. Scoped Markdown links, private-data screening and staged whitespace checks passed. The new review reproducer intentionally remains red on the reviewed source and is outside the normal test suite; this is disclosed evidence for the requested fixes, not a claim that all functional checks passed.

Revisit this report after corrected core source, a real payment-account observation, changed provider draft state, a public-audience instruction or browser/device evidence. A stored handoff does not imply the other session has read it or will continue after an ended turn.
