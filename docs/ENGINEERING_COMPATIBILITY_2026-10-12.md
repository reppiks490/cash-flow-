# Combined engineering verification — 2026-10-12

This is a local compatibility checkpoint for three independent review branches.
It does not merge them, approve live operations or verify private payout state.

| Change | Exact remote head tested | Main baseline plus feature |
|---|---|---|
| C04: suppression and genuine send receipts (PR5) | `1c556e3b67acb5720c70312d0c9f426ab24556de` | 50 tests |
| C11: evidence-linked research audit (PR9) | `0ece099cd3f9ecc44ba666d5dabe3899643c032b` | 64 tests |
| C12: creative layout versatility (PR10) | `7829c7ea4952f94d71043d58df899daad6a80c4a` | 55 tests |

## Combined check

A local main-code-baseline snapshot with all three code changes passed **77 tests**
with Pillow, ReportLab and pypdf installed. `moneyfall rank`, the synthetic demo
and `git diff --check` passed. The demo explicitly reported synthetic mode and
zero live revenue; its example payment is not a real receipt.

All nine relevant source/test/fixture files were read back from the exact remote
heads and verified byte-for-byte identical to the tested local files. SHA-256:

| File | SHA-256 |
|---|---|
| `tests/test_audits.py` | `ba949999130045dd9bdd044930ce9955bace91c264e88ebcf18cbe4b153f7501` |
| `tests/test_launch.py` | `48d2c1115e721b76e2a99621331fdd61953a7d73cbe12d2c9415e60ddfc9847d` |
| `tests/test_creative_layouts.py` | `81618495582ff32c214ea90e294102896a5c88842e72e6b421c190c0ce269315` |
| `scripts/render_audit.py` | `873cd6a9592e5531f33037284a39f48dd9bd1ae96f2a4a829e55b3f1c030afe4` |
| `scripts/launch_packets.py` | `7c68646c93882a6803cd06e12458e0e81ec75015e0e07fada81c078acdd300f9` |
| `scripts/render_proof.py` | `3e61c315aa587435ceb63d7a6a418587e39ab76c0f259d6727072c43d473f43b` |
| `src/moneyfall/launch.py` | `9b110c38ef6697718cfe670e6976615f28dd96935a5c5cf4275ec7d677025d8f` |
| `src/moneyfall/audits.py` | `a6278d9b1be30844600b180432288074b5dac79a4e2512dc87be2d709d5a0d54` |
| `config/examples/creative_layouts.json` | `f427ba160c04361fd1330653ec8f0c35f1d883ccfd8540b92674401a7492d0e8` |

This is code compatibility evidence; merging documentation and index changes
still requires normal conflict review. PR5 and PR9 GitHub workflow runs on the
heads above were successful. Optional render/PDF tests skip without dependencies;
core CI cannot replace the exercised production path.

## Creative production check

A fictional Northstar Example Studio kit used all three layouts and full video.
The contact sheet, proof PDF and video frame were visually inspected; ffprobe
reported 1080×1920 and 15.000000 seconds. The final proof SHA-256 is
`e21538921ddecf68c0d6c16d7696c16d8e674e5ea44edfbdc292209844ebee45`.
No generated binaries or operational state are committed to the public repo.

Independent review reproduced a disappearing split headline on a dark accent
and a wide company title clipping after the PDF font change. Both fixes were
verified by failing-first regressions. PNG/SVG positions were independently
compared within one pixel for the statement fixture. Layouts increase choice;
commercial demand and conversion remain unmeasured.

## Continuation

Atlas should prioritize PR5 R01 exact-head re-review, then PR9/PR10 technical
and commercial-fit review. Existing scope and price are preserved. Do not
refresh real draft attachments from a branch until that code is accepted and
the completed kit has been reviewed. Read the production contracts on their
branches and use fresh private output directories.

Atlas remains sole operator for C06–C08 and the original private cohort. Latest
Atlas status says the mailing address is supplied privately and payout/payment
setup is unverified. No new Atlas reply, send, payment, profit or delivery was
observed in this checkpoint. The user's 14–20-day profit target remains; do not
reset its original clock or treat engineering output as revenue.
