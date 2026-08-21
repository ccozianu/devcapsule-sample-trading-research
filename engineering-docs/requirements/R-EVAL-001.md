# R-EVAL-001: Calibration-First Evaluation Harness

Statement: The project must measure correctness conditional on each reported
epistemic state (converged, majority, diverged) before implementing the debate
orchestration.

Priority: MVP
Status: repo-validated

Implementation:
- `src/rotated_consensus/evaluation.py`
- `tests/test_evaluation.py`
- `tests/fixtures/labeled/`

Validation:
- `nox -s tests`

Related:
- `engineering-docs/sketch-of-a-project/DESIGN.md`
