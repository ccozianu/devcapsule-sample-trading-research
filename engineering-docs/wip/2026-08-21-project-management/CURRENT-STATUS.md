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

Maintain project-wide sequencing and route newly authorized workstreams.

Latest action: the owner selected the portfolio application as the next
product focus on 2026-09-01. The `portfolio-context` workstream was opened for
a requirements-and-UX interview followed by design. Coding is explicitly
deferred until the owner accepts those artifacts.

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

The migration checkout also contained pre-existing tooling, licensing, and
documentation changes. They were routed through the bounded
`repository-foundation` workstream, validated, integrated, and archived at
`engineering-docs/archive/2026-08-21-repository-foundation/`.

## Coordination Decisions

- The project owner explicitly reprioritized migration to multiple-stream mode
  ahead of the recorded labeled-fixture slice.
- On 2026-09-01 the owner confirmed the portfolio sequence as `portfolio
  context`, then `portfolio debate`, then `sweep`, and directed that the first
  workstream settle capabilities and UX and derive the design before coding.
  This supersedes the labeled-fixture slice as the current priority without
  rejecting or erasing that evaluation work.
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
- The recovered state was assigned to `repository-foundation`, transferred to
  its registered branch, validated, integrated through `direct-main`, and
  concluded on 2026-08-21.

## Prioritized Next Work

1. Complete the design-first `portfolio-context` workstream: settle user
   capabilities and UX, derive an accepted design, then implement only after
   the owner authorizes that phase.
2. After portfolio context, open separate workstreams for `portfolio debate`
   and then `sweep`; do not mix their unfinished state into the context
   checkout.
3. Retain the first human-reviewed labeled fixture set as later evaluation
   work. Capture R-EVAL-002 when fixture scope is chosen.
   Done means: the harness loads the fixtures and reports at least the
   single-best and flat-majority baselines without live model calls.
   Verification: run the unit suite and a local fixture-evaluation command.
   Reopen if: results cannot be reproduced from committed fixture data.

## Open Threads

- Weighed and unresolved: fixture subject scope, source selection, provenance,
  and grading still shape R-EVAL-002, but the owner sequenced that work behind
  the portfolio path on 2026-09-01.
- Deliberately not preserved: conversational chronology before migration; the
  repository records above retain the state needed to resume.

## External State And Risks

- GitHub SSH authentication, fetch, and push succeeded on 2026-08-21.
- Local and remote `main` were verified identical at `54e70c9` after migration
  and repository-foundation publication.
- The migrated repository foundation passes the default Nox sessions and the
  package-build session; see its archived status for evidence.

## Local Document Index

- [Intake queue instructions](intake/README.md)
- [Intake disposition log](intake-dispositions.md)

## Next Resumable Task

Track the `portfolio-context` design interview and preserve the confirmed
sequence. When that workstream finishes, route the next bounded effort to
`portfolio debate`; the labeled-fixture slice remains later work unless the
owner reprioritizes it.
