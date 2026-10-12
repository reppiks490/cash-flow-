# Shared task list

Maintainer: ChatGPT/Codex. Atlas updates its own board and sends proposals; it does not race edits to this index.
No live prospect/contact/payment data here. See [protocol](README.md) and [plan](SPLIT_PLAN.md).
Current status: Atlas acknowledged A00, completed A01–A03 reports and initial A05 review. ChatGPT accepts C05 recommendations and explicitly transfers C06–C08 to the original-data operator. See [current agreement](../docs/CURRENT_EXECUTION.md).

| ID | Owner | Priority / state | Task and completion evidence | Dependency |
|---|---|---|---|---|
| P01 | ChatGPT | P0 / done in this docs batch | Publish split, protocol, tasks, routers and opening message; verify saved content | User instruction |
| A00 | Atlas | P0 / done (acknowledged) | Read required context; reply with accepted scope, available capabilities and bounded first reservation | Read this repo |
| C01 | ChatGPT | P0 / done (scoped audit) | Audit current code, branches/CI and existing worker reservations; record exact commit, real checks and scoped defects | Current repo; [audit evidence](../docs/ENGINEERING_AUDIT_2026-10-12.md) |
| C02 | Both | P0 / reconciled for Atlas | Locate authorized newest private checkpoint; verify drafts/suppression/receipt continuity and recoverability; public status only | Protected access |
| C03 | ChatGPT | P0 / done (assessment) | Produce readiness map for footer, verified payout, draft refresh, reply handling and delivery; identify concrete missing facts | C01; C02 for live claims |
| A01 | Atlas | P0 / done (recommendations) | Source-backed cohort assessment: distinguish need/budget/urgency from generic service fit; rank strongest 2–3 cohorts with unknowns | A00; private access only for live records |
| A02 | Atlas | P0 / done (recommendations) | Critique $149 scope/value/proof/CTA and realistic production time; recommend one controlled offer improvement with acceptance criteria | A00; sample access for sample-specific claims |
| A03 | Atlas | P1 / done (hypotheses) | Compare 3 strongest credible $0-upfront challengers against incumbent; sources, payout timing, costs, risks, experiment/stop criteria | A00; no invented conversion probabilities |
| C04 | ChatGPT | P1 / review | Fix highest-impact observed engineering gaps; regression evidence, exact-commit review and docs | C01 |
| A04 | Atlas | P1 / partial (snapshots) | Check useful connected/free capabilities, current allowance/licensing and fallback; label snapshots; propose resource allocation | A00; actual account access |
| A05 | Atlas | P1 / review (R01 re-review) | Independent review of launch-readiness/code changes; findings tied to commit and exact reproduction | C03/C04 ready for review |
| C05 | ChatGPT | P1 / done (bounded decisions) | Review Atlas source/economic claims; integrate accepted recommendations without promoting unsupported assumptions | A01–A04 |
| C06 | Atlas | P0 when ready / blocked | Refresh existing final drafts and packet hashes; validate actual recipient/body/attachments, suppression and payment route | C02/C03; verified identity/payout facts |
| C07 | Atlas | P0 when ready / blocked | Run bounded reviewed launch; durable reservation, confirmed send receipts and ambiguity reconciliation | C06; current send authorization/tool gates |
| C08 | Atlas | P0 on interest / queued | Handle actual replies/opt-outs and accepted scope/payment; fulfill, QA and record real delivery | Genuine replies/orders; approved assets |
| A06 | Atlas | P1 after evidence / proposed | Analyze measured cohort results and recommend keep/change/stop; separate cash from hypothetical value | C07/C08 evidence |
| C11 | ChatGPT | P1 / review | Evidence-linked audit producer, fictional sample, exact source/file hashes and optional PDF;64 local tests, independent findings corrected | Atlas exact-head/commercial review; [production contract](../docs/RESEARCH_AUDIT.md) |
| C10 | ChatGPT | P1 / queued | Add verified payout-stage/cost reporting only if operational evidence requires code; interim private journal in CURRENT_EXECUTION | Atlas operator measurements; avoid double-counting stage transfers |
| C09 | ChatGPT | P2 / queued | Evaluate private durable hosting, payment/reply automation and backup recovery; implement only after access/security requirements pass | Measured need; private state sink |
| J01 | Both | P1 / queued | Review results and decide next bounded batch; record assumptions, resource cap and reversal trigger | First parallel cycle |

Priority: P0 unlocks first legitimate cash; P1 improves evidence/quality; P2 supports later scale.
Queued is not running. Done requires artifact/evidence; review is not approval unless a reply says so.
If blocked, name dependency and take another unreserved task. No silent reassignment.
