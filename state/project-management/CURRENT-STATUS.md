# Project Management Workstream

Start date: `2026-08-21`

Goal: Maintain project-wide priorities, sequencing, dependencies, workstream
lifecycle decisions, and routing while this repository uses multiple-stream
mode.

State: `active; permanent coordination`

Definition read: WORKFLOW.md@c3c0722d6cd5, WORKFLOW-LOCAL.md@f584a2788421

Branch prefix: `ws-project-management/`

Branch association: `ws-project-management/coordination`

Forked from `main` on 2026-10-13. The pre-adoption branches
`project-management/coordination` and `project-management/outbox` held
nothing `main` lacks (verified by patch identity) and were deleted on the
owner's direction on 2026-10-14; the outbox was retired by definition 0.2.14.

Integration target: `main`

Delivery method: `pull-request`, reviewed by a second agent pair, by
project-owner decision on 2026-10-14; see *Delivery And Review* in
`WORKFLOW-LOCAL.md`. This supersedes the `direct-main` default of 2026-08-21
for every workstream; each updates its own status file when it next touches
it. Only the owner merges to `main`, as a merge commit. Never force-push
`main`.

Branch synchronization: fork from current `main`; rebase while unpublished
and merge `main` in once the branch is shared.

## Current Task

Track `cli-engines` and `portfolio-context` through their design phases; the
delivery decision is settled and recorded.

Latest action, 2026-10-13: the owner opened `cli-engines` in another checkout
on `ws-cli-engines/v0` and published it. Its goal is a second engine access
route, the `claude`, `codex` and Antigravity command-line clients through
ambient sign-in, beside the LangChain route. Its status file holds six open
questions for the owner; design precedes implementation.

The same day this workstream took its first mail, the DevCapsule process
record of 2026-10-12, and delivered it onward to `cli-engines` as design
input, keeping only the delivery-method question here. The original text is
retained at commit `2a03886` under this directory's `intake/`, and in full
inside the item sent to `cli-engines`.

Portfolio sequence unchanged: `portfolio-context` design, then
`portfolio debate`, then `sweep`. `cli-engines` runs beside it and does not
reorder it.

## Coordination Decisions

- 2026-08-21: the owner reprioritized migration to multiple-stream mode
  ahead of the labeled-fixture slice; initialization created only the
  reserved workstream; `direct-main` chosen as the default delivery method;
  pre-existing uncommitted changes routed through `repository-foundation`,
  integrated and archived. Details in the dated record below.
- 2026-09-01: the owner confirmed the portfolio sequence as context, then
  debate, then sweep, and directed design before coding.
- 2026-10-12: the owner adopted DevCapsule workflow 0.2.16.dev0 and the
  reserved `maintenance` workstream.
- 2026-10-13: the owner opened `cli-engines` as an ordinary workstream.
  This workstream's first working branch takes the `ws-` form; the
  pre-adoption branches were deleted on the owner's direction, 2026-10-14.
- 2026-10-13: the DevCapsule process record was assigned onward to
  `cli-engines`; see the decision log.
- 2026-10-14: the owner chose pull-request delivery with a second agent
  pair's review, the loop in the DevCapsule record, over direct-main and
  over unreviewed pull requests. Reason: the only reviewer under direct-main
  was the owner reading the diff after the fact; the loop's cost, twenty to
  forty minutes a round, was judged worth it from the first engine slice
  on. Recorded under *Delivery And Review* in `WORKFLOW-LOCAL.md`, which is
  this workstream's deliverable for its next integration.
- 2026-10-14: the owner directed that `cli-engines` continue in this
  checkout after the other session's worktree was removed; its claim was
  taken over.
- 2026-10-15: at the owner's direction, sent DevCapsule's
  `project-management` a capability request for a signed-in GitHub CLI in
  the capsule, by mail on that repository's coordination branch (item
  `2026-10-15-trading-research-project-management-github-cli-capability.md`,
  delivered at `bddec8f` there), with two observations attached: codex's
  sandbox cannot run inside the capsule, and codex reads its home
  `AGENTS.md` regardless of switches. The need is recorded under *Host
  Capabilities* in `WORKFLOW-LOCAL.md`. Found on sending: DevCapsule's own
  `project-management` had already routed "the GitHub CLI as a component"
  to its `component-catalog` workstream on 2026-10-09, naming the sign-in
  design as the real work; our item is corroboration from a project that
  ran the reviewer loop without it. Where it stands is read from that
  repository's coordination branch and decision logs.

## Prioritized Next Work

1. Deliver this branch's change to `WORKFLOW-LOCAL.md` through the first
   reviewed pull request, so the delivery rule itself reaches `main`.
   Done means: the pull request is merged by the owner as a merge commit.
   Verification: `main` carries *Delivery And Review*.
   Reopen if: a workstream integrates by a method the record does not name.
2. Complete the design-first `portfolio-context` workstream; then open
   `portfolio debate`, then `sweep`.
3. Retain the first human-reviewed labeled fixture set as later evaluation
   work. Capture R-EVAL-002 when fixture scope is chosen.

## Open Threads

- Awaiting the human: nothing.
- Weighed and unresolved: fixture subject scope and grading still shape
  R-EVAL-002, sequenced behind the portfolio path on 2026-09-01.
- Observed, not ours to act on: DevCapsule's GitHub CLI component is in
  its `component-catalog` queue since 2026-10-09; until it ships, pull
  requests here are opened and merged by the owner by hand.
- Observed, not edited: `devcapsule workflow status` shows an empty branch
  column for `cli-engines`; its status file says `Initial branch:` where the
  tool reads a `Branch association:` line. That workstream's own record to fix.
- Deliberately not preserved: conversational chronology before migration.

## External State And Risks

- GitHub SSH fetch and push succeeded on 2026-10-13 from this checkout.
- The `coordination` branch on the remote exists since 2026-10-12 and
  carries the live state of `cli-engines` and `project-management`.
- `main` is at `85c4a0d`, the 0.2.16.dev0 adoption; this branch adds only
  records to it.

## Local Document Index

- [Intake queue](intake/README.md)
- [Decision log](intake-dispositions.md)
- [Record: carried-forward state at migration](2026-10-13-record-migration-state.md),
  for retrospection only.

## Next Resumable Task

Open the reviewed pull request for this branch once a reviewer pair is set
up (item 1). Meanwhile track `portfolio-context` and `cli-engines` through
their design phases without reordering the portfolio sequence.
