# Current Status

Workflow type: `single-stream`

## Current Stage

Evaluation scaffold and deterministic primitives.

## Current State

- Project purpose and initial requirements are recorded.
- Python packaging and a dependency-free validation path are established.
- Provider-independent verdict/status contracts, strict-majority classification,
  flat-vote baseline behavior, and calibration reporting are implemented.
- Eight repository tests pass.
- The reusable DevCapsule `WORKFLOW.md` and generic agent entry point are
  installed; this file, rather than README, is the project-owned live handoff.
- No LLM provider integration, debate orchestration, real labeled dataset, or
  canonical claim registry exists yet.
- Git status and history work normally in the restored submodule checkout.

## Resume Context

Read these files in order:

1. `README.md`
2. `REQUIREMENTS.md`
3. `engineering-docs/sketch-of-a-project/DESIGN.md`
4. `engineering-docs/requirements/R-EVAL-001.md`
5. `engineering-docs/requirements/R-MERGE-001.md`
6. `engineering-docs/bugs/` and `engineering-docs/implementation-notes/`, if relevant

## Planned Next Step

1. Define and load the first small, human-reviewed labeled fixture set, including
   source/license metadata, gold atomic claims, and an explicit grading rule.
   Requirements: R-EVAL-002 (to be captured when fixture scope is chosen).
   Done means: the harness can load the fixtures and report at least the
   single-best and flat-majority baselines without making live model calls.
   Verification: run the unit suite and a local fixture-evaluation command.
   Reopen if: results cannot be reproduced from committed fixture data.

## Open Threads

- Fixture scope, source licensing, and the explicit grading rule await an
  interactive project discussion.
