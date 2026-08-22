# Requirements Register

This file is the project-level overview and index for accepted requirements.
Canonical detailed records belong under `engineering-docs/requirements/`.
This overview does not replace the active task list in `README.md`; it gives
tasks, bugs, and engineering notes stable requirement IDs to reference.

## Status Values

- `proposed`: captured, but not yet accepted as a project requirement.
- `accepted`: accepted, but not yet implemented.
- `implemented`: code or docs exist, but validation is incomplete.
- `repo-validated`: static checks, smoke tests, or automated checks passed.
- `manually validated`: the user or agent validated behavior in the running
  product.
- `deferred`: accepted direction, but intentionally outside the current target.
- `rejected`: considered and intentionally not pursued.

## Priority Bands

- `MVP`: required for the first useful version.
- `current stabilization`: required before closing the current stabilization
  pass.
- `later`: useful, but not required for the current target.

## Requirement Template

```markdown
### R-AREA-000: Short Name

Statement: ...

Priority: MVP | current stabilization | later
Status: proposed | accepted | implemented | repo-validated | manually validated | deferred | rejected

Implementation:
- ...

Validation:
- ...

Related:
- ...
```

Every active task, bug, or completed-task record should include a
`Requirements:` line when it materially implements, validates, changes, defers,
or reinterprets a requirement.

## Current Requirements

### R-BOOT-001: Define Initial Requirements

Statement: Replace the bootstrap placeholder with the project's purpose,
validation path, accepted initial requirements, and resumable next task.

Priority: current stabilization
Status: repo-validated

Implementation:
- `README.md`
- `REQUIREMENTS.md`
- `pyproject.toml`

Validation:
- The README names the purpose, validation commands, current state, and next task.
- Active implementation work maps to stable requirement records.

Related:
- `engineering-docs/sketch-of-a-project/DESIGN.md`

### R-EVAL-001: Calibration-First Evaluation Harness

Statement: Measure correctness conditional on each reported epistemic state
before implementing debate orchestration.

Priority: MVP
Status: repo-validated

Implementation and validation:
- `engineering-docs/requirements/R-EVAL-001.md`

### R-MERGE-001: Deterministic Claim Classification

Statement: Keep final claim classification deterministic, structured,
strict-majority based, and independent of LLM calls.

Priority: MVP
Status: repo-validated

Implementation and validation:
- `engineering-docs/requirements/R-MERGE-001.md`

Note: whether this deterministic merge remains the *final* adjudicator, or
becomes the baseline a synthesizer meta-chat is measured against, is
deliberately deferred (OQ-1,
`engineering-docs/design-notes/open-q-convergence-declaration.md`). The
module stays either way.

### R-PROTO-001: Rotated-Debate Protocol as a Standalone Package

Statement: Deliver the rotated ANSWERER/CRITIC/SYNTHESIZER debate protocol
as a domain-agnostic Python package, with per-topic role constraints for
conflicted engines and honestly reported epistemic states.

Priority: MVP
Status: accepted

Implementation and validation:
- `engineering-docs/requirements/R-PROTO-001.md`

### R-PORT-001: Portfolio Knowledge Repository

Statement: Instantiate the INFORMATION_MODEL substrate in this repository as
the living, auditable knowledge base for the sanitized demo portfolio, driven
from an IDE via Markdown files and terminal commands.

Priority: MVP
Status: accepted

Implementation and validation:
- `engineering-docs/requirements/R-PORT-001.md`

### R-REFRESH-001: Daily Knowledge-Refresh Debate

Statement: At least daily, all three engines — with browsing enabled — debate
whether and how portfolio knowledge must be updated on intervening news;
concrete mechanics deliberately deferred.

Priority: MVP
Status: accepted

Implementation and validation:
- `engineering-docs/requirements/R-REFRESH-001.md`

### R-ACCEPT-001: Reflexive Acceptance Criterion

Statement: The demo is accepted by user happiness plus an engine-converged
verdict grounded in this repo's own scoreable usage records — never by
returns — and only after two months of live usage crossing one earnings
season.

Priority: MVP
Status: accepted

Implementation and validation:
- `engineering-docs/requirements/R-ACCEPT-001.md`
