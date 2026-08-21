# Repository Foundation Workstream

Start date: `2026-08-21`

Goal: Recover, validate, and integrate the pre-migration developer-tooling,
packaging, licensing, and related documentation changes without mixing them
into project-management coordination.

State: `active; ready for direct-main integration`

Branch prefix: `repository-foundation/`

Integration branch: `repository-foundation/recovery`

Integration target: `main`

Delivery method: `direct-main`; rebase onto current `main`, validate,
fast-forward local `main`, and push normally without force.

Branch synchronization: rebase while unpublished.

## Current Task

Restore the pre-migration recovery state onto this registered branch, verify
the Nox validation and Apache-2.0 packaging/documentation changes, then
integrate the bounded result.

Status: recovery is complete on `repository-foundation/recovery`. The default
Nox sessions and package-build session pass on the recovered tree.

Done means: the recovered changes are committed on this branch, shared checks
pass, the workstream is finalized, and remote `main` contains the final tree.

Verification: run the default Nox sessions and the package build session.

## Recovery Boundary

The recovery state predates multiple-stream initialization and was present as
unstaged and untracked files on `main`. It is being transferred intact to this
branch immediately after registration. This one-time transfer is recovery of
existing state, not authorization to mix future workstreams in a dirty
checkout.

## Validation Evidence

- `.venv/bin/nox`: 8 tests passed; compile and Ruff sessions passed.
- `.venv/bin/nox -s build`: wheel and source distribution built successfully,
  and both include the Apache-2.0 license.
- Generated `.nox/`, `build/`, `dist/`, and `*.egg-info/` state remains ignored.

## Local Document Index

- [Intake queue instructions](intake/README.md)
- [Intake disposition log](intake-dispositions.md)

## Next Resumable Task

Commit the validated recovery checkpoint, finalize this bounded workstream,
rerun required checks on the final tree, then fast-forward and publish `main`.
