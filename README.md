# Rotated-Debate Consensus Research

An evaluation-first Python research project for testing whether multiple LLMs,
aligned around atomic claims and followed by deterministic adjudication, produce
useful and calibrated epistemic states: `CONVERGED`, `MAJORITY`, and `DIVERGED`.

The design deliberately separates semantic work from adjudication. LLMs may
answer, decompose, critique, rebut, and synthesize; the final claim-level merge
must be deterministic, auditable, and free of model calls. Agreement is reported
as an observed state, never presented as confidence or correctness.

The source design and settled constraints are in
`engineering-docs/sketch-of-a-project/DESIGN.md`. The companion pseudocode is a
design artifact, not executable production code.

## Development

Requires Python 3.12 or newer. The current validation has no third-party runtime
dependencies:

```bash
PYTHONPATH=src python -m unittest discover -s tests -v
PYTHONPATH=src python -m compileall -q src tests
```

The package uses a `src/` layout. Provider adapters, prompts, credentials, and
network calls do not belong in the deterministic domain, merge, or evaluation
modules.

## Current State And Next Step

This section is the project handoff point. Update it when completing a stage,
changing project state materially, retiring a task, or ending a session.

Current stage: Evaluation scaffold and deterministic primitives.

Current status:

- Project purpose and initial requirements are recorded.
- Python packaging and a dependency-free validation path are established.
- Provider-independent verdict/status contracts, strict-majority classification,
  flat-vote baseline behavior, and calibration reporting are implemented.
- Eight repository tests pass.
- No LLM provider integration, debate orchestration, real labeled dataset, or
  canonical claim registry exists yet.
- Git status and history work normally in the restored submodule checkout.

When resuming the project, read these files in order:

1. `README.md`
2. `REQUIREMENTS.md`
3. `engineering-docs/sketch-of-a-project/DESIGN.md`
4. `engineering-docs/requirements/R-EVAL-001.md`
5. `engineering-docs/requirements/R-MERGE-001.md`
6. `engineering-docs/bugs/` and `engineering-docs/implementation-notes/`, if relevant

Planned next item:

1. Define and load the first small, human-reviewed labeled fixture set, including
   source/license metadata, gold atomic claims, and an explicit grading rule.
   Requirements: R-EVAL-002 (to be captured when fixture scope is chosen).
   Done means: the harness can load the fixtures and report at least the
   single-best and flat-majority baselines without making live model calls.
   Verification: run the unit suite and a local fixture-evaluation command.
   Reopen if: results cannot be reproduced from committed fixture data.
