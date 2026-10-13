# Project Management Workstream

Start date: `2026-08-21`

Goal: Maintain project-wide priorities, sequencing, dependencies, workstream
lifecycle decisions, and routing while this repository uses multiple-stream
mode.

State: `active; permanent coordination`

Definition read: WORKFLOW.md@c3c0722d6cd5, WORKFLOW-LOCAL.md@426b1fa5ef12

Branch prefix: `ws-project-management/`

Branch association: `ws-project-management/coordination`

Forked from `main` on 2026-10-13. The pre-adoption branches
`project-management/coordination` and `project-management/outbox` hold
nothing `main` lacks; the outbox was retired by definition 0.2.14. Deleting
both awaits the owner's direction.

Integration target: `main`

Delivery method: `direct-main` by project-owner decision on 2026-08-21: bring
the clean branch up to `main`, validate, merge, push normally. Never
force-push `main`; stop for semantic conflicts or genuine remote divergence.
Definition 0.2.16.dev0 requires one merge commit per delivery, never a
fast-forward; the earlier rebase-and-fast-forward wording is superseded by
that rule, and whether to move to pull requests is the open decision below.

Branch synchronization: fork from current `main`; rebase while unpublished
and merge `main` in once the branch is shared.

## Current Task

Route and record the `cli-engines` workstream, and settle the project-wide
delivery decision.

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
  pre-adoption branches are left in place until the owner directs deletion.
- 2026-10-13: the DevCapsule process record was assigned onward to
  `cli-engines`; see the decision log.

## Prioritized Next Work

1. Record the owner's delivery decision: keep `direct-main` with merge
   commits, or move to pull requests reviewed by a second agent pair as in
   the DevCapsule record. `cli-engines` asks the same as its open question 6.
   Done means: the decision is recorded here and, if it departs from the
   definition, under *Exceptions* in `WORKFLOW-LOCAL.md`; every open
   workstream's status file names the method that applies to it.
   Verification: `devcapsule workflow status` shows no row contradicting it.
   Reopen if: a workstream integrates by a method the record does not name.
2. Complete the design-first `portfolio-context` workstream; then open
   `portfolio debate`, then `sweep`.
3. Retain the first human-reviewed labeled fixture set as later evaluation
   work. Capture R-EVAL-002 when fixture scope is chosen.

## Open Threads

- Awaiting the human: the delivery decision above, and whether to delete
  the drained pre-adoption branches.
- Weighed and unresolved: fixture subject scope and grading still shape
  R-EVAL-002, sequenced behind the portfolio path on 2026-09-01.
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

Take the owner's delivery decision and record it as item 1 above. Then track
`portfolio-context` and `cli-engines` through their design phases without
reordering the portfolio sequence.
