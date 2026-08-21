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

## Project Status

The resumable project handoff and planned next task live in
[`CURRENT-STATUS.md`](CURRENT-STATUS.md). The reusable collaboration protocol
lives separately in [`WORKFLOW.md`](WORKFLOW.md).
