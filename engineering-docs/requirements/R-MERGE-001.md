# R-MERGE-001: Deterministic Claim Classification

Statement: Final claim-state classification must be deterministic, operate on
aligned structured verdicts, require a strict majority, surface degraded
coverage, and make no LLM calls.

Priority: MVP
Status: repo-validated

Implementation:
- `src/rotated_consensus/domain.py`
- `src/rotated_consensus/merge.py`
- `tests/test_merge.py`

Validation:
- `PYTHONPATH=src python -m unittest discover -s tests`

Related:
- Design decisions D1, D3, and D4 in `engineering-docs/sketch-of-a-project/DESIGN.md`
