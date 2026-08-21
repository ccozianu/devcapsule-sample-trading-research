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

Requires Python 3.12 or newer. Bootstrap a repository-local developer
environment; do not install the toolchain into the global Python environment:

```bash
python3.12 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -r dev-requirements.txt
```

Nox provides the development commands and creates an isolated environment for
each task:

```bash
nox                 # tests, compilation check, and lint
nox -s tests        # unit tests only
nox -s build        # wheel and source distribution in dist/
```

`setuptools.build_meta` remains the PEP 517 package build backend; Nox invokes
that backend through `python -m build`. The package uses a `src/` layout.
Provider adapters, prompts, credentials, and network calls do not belong in the
deterministic domain, merge, or evaluation modules.

## License

Repository-authored code and documentation are licensed under the
[Apache License 2.0](LICENSE). Externally sourced evaluation fixtures retain
their source licenses and must record their provenance and redistribution terms.

## Project Status

The open-workstream registry lives in
[`CURRENT-STATUS.md`](CURRENT-STATUS.md). Detailed handoffs and planned next
tasks live under `engineering-docs/wip/`. The reusable collaboration protocol
lives separately in [`WORKFLOW.md`](WORKFLOW.md).
