# Workstream Current Status: Maintenance

Name: `maintenance`

Start date: `2026-10-12`

State: active; permanent maintenance

Definition read: stamped by `devcapsule workflow publish`

Branch association: `ws-maintenance/`; no branch yet

## Goal

Own the defects that no open workstream covers, on `main` and on maintained
release lines, and drive maintenance releases, while this repository uses
multiple-streams mode.

## Queue

Read from `main`, not from this file: the bug records under
`engineering-docs/bugs/` whose `owner` is `maintenance` and whose `status` is
neither `closed` nor `retired`. See *Bug Intake* in `WORKFLOW.md`.

## Current State

The reserved workstream is registered as part of adopting DevCapsule workflow
`0.2.16.dev0` on 2026-10-12. Adoption exception: its start date is later than
the project's original multiple-stream initialization because the earlier
definition did not require this reserved workstream.

The integration review found no bug records on `main` beyond the template,
so there are no open maintenance-owned bugs. The owner authorized integration
of the existing `three-provider-formation` branch directly into `main`, using
merge commits without rewriting published history. The adoption preserves
`main`'s portfolio-context and cost-review records and supplies the local
validation commands. The next product task remains portfolio-context design.

Validation on 2026-10-12: `.venv/bin/nox` passed all 43 unit tests,
compilation, and lint; CLI help, TOML parsing, workflow-version consistency,
documentation links, and whitespace checks passed. No live provider runs or
container rebuild were performed for this integration.

## Planned Next Step

Triage any bug whose `severity` is `untriaged`, then take the highest-severity
open bug on the current release line.

## Open Threads

- None recorded yet.

## Local Document Index

- [Intake queue](intake/README.md)
- [Intake decisions](intake-dispositions.md)
