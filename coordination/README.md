# MONEYFALL: ChatGPT/Codex + Atlas

User authorized this cash-flow collaboration on 2026-10-12. Atlas is the other ChatGPT account; ChatGPT/Codex is this account. These identities are labels, not authenticated account IDs. Neither may impersonate the other. Claude is not assigned cash-flow work by this plan. ICARUS assignments and inboxes remain separate.

## Start each session
1. Read [AGENTS](../AGENTS.md), [CODEX_START_HERE](../CODEX_START_HERE.md), and both mandatory handoffs in their specified order.
2. Read [current continuation](../docs/CONTINUATION.md), OPERATIONS, LAUNCH and CONTINUATION_POLICY under docs.
3. Read [split plan](SPLIT_PLAN.md), [task list](TASKS.md), both [ChatGPT](board/chatgpt.md) and [Atlas](board/atlas.md) boards, and your inbox.
4. Inspect current main, open branches/PRs and private state availability. Public documentation may be stale; verify operational facts privately.
5. Acknowledge messages with a new reply; reserve a bounded task before implementation. Do not infer acknowledgment from delivery.

## Communication and reservations
Use immutable Markdown messages in `coordination/inbox/to-atlas/` and `coordination/inbox/to-chatgpt/`.
Filename: UTC timestamp including seconds, sender, short subject. Never overwrite a peer message.
Required headers: From, To, Date (UTC), Subject, Task IDs, Reply-needed, Re (exact original path or none).
Body: observed facts vs reported facts; requested decision; owned paths; dependencies; evidence/commit; next step.
Replies are new files with exact Re. Inbox paths carry messages; boards summarize status, not message contents.

Each agent edits only its own board and outgoing messages. Task-list/plan edits are owned by ChatGPT; Atlas requests changes by message.
A reservation names task ID, exact paths, branch, base SHA, start time and scope; a peer collision requires agreement before edits.
A reservation persists until completion/release or explicit transfer, not a guessed timeout. If a peer is absent, continue unreserved independent work.
No automatic locks or identity enforcement are implemented: coordination is manual and reviewable.
Before a shared-file change, ask its owner through the inbox and receive an explicit scope agreement. Never reset, overwrite or force-push peer work.
Use separate branches for implementation and review the current commit before integration. Routine reversible docs integration is authorized.

## Private information and account boundaries
This repo is PUBLIC. Messages may contain task IDs, aggregate counts, public methodology, code refs and generic offer scope.
Never include recipients, customer/prospect lists, draft bodies, private attachment links, payment details, secrets or operational checkpoint bytes.
Each account has its own connector access. Historical connection/credit snapshots do not prove Atlas has access.
Do not copy passwords/tokens between accounts or assume their quotas are additive. Deduplicate by underlying provider workspace.
Use an owner-approved protected store for operational handoffs; verify access and freshness first. Record only a sanitized access status here.
If private state is unavailable, continue generic research, synthetic verification and public-methodology work; do not recreate existing drafts or launch a parallel sender.

## Checkpoint / review procedure
Publish task ID, branch + exact commit, changed paths, observed checks, known gaps, next step and reservation release.
Reviewer records findings against that commit; subsequent code changes require review of the changed scope.
States: proposed -> accepted -> in_progress -> review -> done; blocked identifies dependency. Proposed assignment is not Atlas acceptance.
Evidence classes: reported / independently verified / synthetic / unknown. A draft is not a send, invoice is not payment, output is not delivery.
Send only from the designated operational owner, with current suppression, durable reservation, actual provider confirmation and verified identity/payment facts.
No continuous background execution, inbox polling or scheduler exists merely because these files exist.
