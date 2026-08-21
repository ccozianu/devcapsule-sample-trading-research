# Project Management Workstream

Start date: `2026-08-21`

Goal: Maintain project-wide priorities, sequencing, dependencies, workstream
lifecycle decisions, and routing while this repository uses multiple-stream
mode.

State: `active; permanent coordination`

Branch prefix: `project-management/`

Initial branch: `project-management/coordination`

Integration target: `main`

Delivery method: `direct-main` by project-owner decision on 2026-08-21. For a
conflict-free integration, rebase the workstream branch onto current local
`main`, fast-forward local `main`, and push it normally. Never force-push
`main`; stop for semantic conflicts or genuine remote divergence.

Branch synchronization: fork from current `main`; rebase unpublished branches
and merge `main` into branches that may be shared.

## Current Task

Initialize multiple-stream mode and preserve the former single-stream handoff
as durable portfolio context.

Status: completed by the initialization checkpoint that creates this
workstream. Publication remains pending until GitHub authentication succeeds.

## Carried-Forward Project State

At the last committed single-stream baseline:

- The evaluation-first package scaffold and its initial requirements existed.
- Provider-independent verdict and status contracts, strict-majority
  classification, a flat-vote baseline, and calibration reporting were
  implemented with eight passing repository tests.
- No provider integration, debate orchestration, real labeled dataset, or
  canonical claim registry existed.
- The next product slice was the first small, human-reviewed labeled fixture
  set with provenance, gold atomic claims, and an explicit grading rule.

The migration checkout also contained pre-existing, uncommitted tooling,
licensing, documentation, and handoff changes. Those files remain uncommitted
and are recovery state, not part of the workflow initialization commit. In
particular, the working tree records Nox-based validation and an Apache-2.0
licensing decision that must be routed and checkpointed before ordinary
workstream development resumes.

## Coordination Decisions

- The project owner explicitly reprioritized migration to multiple-stream mode
  ahead of the recorded labeled-fixture slice; that slice remains the leading
  product priority.
- Initialization creates only this reserved workstream. An ordinary workstream
  for the fixture effort should be opened separately when that work is taken up.
- The project owner selected `direct-main` as the repository's default delivery
  method to keep integration low-ceremony until a later decision changes it.
  Agents may perform conflict-free local integration and push `main` directly;
  the synchronization, validation, fast-forward, and no-force safeguards in
  `WORKFLOW.md` still apply.
- Procedural exception: initialization began with pre-existing uncommitted
  changes on `main`, although `WORKFLOW.md` assumes a clean checkout. Committing
  or moving those unrelated changes first would have contradicted the owner's
  instruction to switch modes before doing anything else. The initialization
  was therefore isolated in its own commit without discarding or staging those
  changes.

## Prioritized Next Work

1. Route and checkpoint the pre-migration dirty-tree recovery state without
   mixing it into this coordination workstream's implementation scope.
2. Open an ordinary workstream for the first human-reviewed labeled fixture
   set. Capture R-EVAL-002 when fixture scope is chosen.
   Done means: the harness loads the fixtures and reports at least the
   single-best and flat-majority baselines without live model calls.
   Verification: run the unit suite and a local fixture-evaluation command.
   Reopen if: results cannot be reproduced from committed fixture data.

## Open Threads

- Awaiting the human: fixture subject scope, source selection and provenance,
  and the grading rule; these choices shape R-EVAL-002 and the fixture
  workstream.
- Weighed and unresolved: the correct ordinary-workstream routing for the
  pre-migration tooling and licensing recovery state.
- Deliberately not preserved: conversational chronology before migration; the
  repository records above retain the state needed to resume.

## External State And Risks

- Local `main` and the cached `origin/main` both pointed to `f058c8c` before
  initialization.
- GitHub host verification succeeds, but the 2026-08-21 publication check
  failed because `~/.ssh/devcapsule_githubkey` was absent in this environment.
  The project owner reports the GitHub issue solved; recheck immediately before
  publication rather than assuming the cached remote ref is current.
- Pre-existing working-tree changes remain outside the initialization commit.

## Local Document Index

- [Intake queue instructions](intake/README.md)
- [Intake disposition log](intake-dispositions.md)

## Next Resumable Task

From a clean checkout on `project-management/coordination`, determine and
record the workstream routing for the pre-migration recovery state, then open
the ordinary fixture workstream when the project owner is ready to settle its
scope.
