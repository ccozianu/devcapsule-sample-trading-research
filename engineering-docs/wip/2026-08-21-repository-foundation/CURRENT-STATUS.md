# Repository Foundation Workstream

Start date: `2026-08-21`

Goal: Recover, validate, and integrate the pre-migration developer-tooling,
packaging, licensing, and related documentation changes without mixing them
into project-management coordination.

State: `active; recovering pre-migration state`

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

Done means: the recovered changes are committed on this branch, shared checks
pass, the workstream is finalized, and remote `main` contains the final tree.

Verification: run the default Nox sessions and the package build session.

## Recovery Boundary

The recovery state predates multiple-stream initialization and was present as
unstaged and untracked files on `main`. It is being transferred intact to this
branch immediately after registration. This one-time transfer is recovery of
existing state, not authorization to mix future workstreams in a dirty
checkout.

## Local Document Index

- [Intake queue instructions](intake/README.md)
- [Intake disposition log](intake-dispositions.md)

## Next Resumable Task

Restore the recovery state, inspect and validate it, then checkpoint the
result before beginning direct-main finalization.
