# Local Workflow: DevCapsule Sample: Trading Research

This is the project's own half of the workflow. `WORKFLOW.md` beside it is the
installed generic definition and binds wherever it speaks; this file governs
wherever it is silent. The headings below are the topics a project usually
needs to settle for itself. Fill the ones that apply, delete the ones that do
not, and add any this project needs that were not foreseen. Bootstrap wrote
this file once and will not touch it again. See *The Project's Local
Workflow* in `WORKFLOW.md`.

## Integration Branch

Fill in only if it is not `main`. `WORKFLOW.md` says `main` throughout and
means the project's integration branch, whatever its name; state the name
here if it differs, for example `master` or `trunk`.

## Version Scheme

How the source names itself between releases and at a release, and the
command that sets it. For example: a Python project carries `X.Y.Z.dev0`
between releases and `X.Y.Z` at the release; a Maven project carries
`X.Y.Z-SNAPSHOT`. The marker must order before the release in the
ecosystem's tooling.

## Release Policy

The ref spelling if it differs from `release-<version>` and `v<version>`; how
a candidate is built and published; what the candidate gate checks and how a
documented exception is recorded; what acceptance evidence is required; and
where the acceptance record lives.

## Validation Commands

Run all commands from the repository root.

- **Environment**: Python 3.12 or newer. Create the local environment with
  `python3.12 -m venv .venv`, then run
  `.venv/bin/python -m pip install -r dev-requirements.txt`.
- **Unit tests**: `.venv/bin/nox -s tests`; the suite uses scripted engines
  and requires no provider keys or live network calls.
- **Integration tests**: no separate automated integration suite exists.
- **End-to-end tests**: owner-executed live debates require the `engines`
  extra (`.venv/bin/python -m pip install '.[engines]'`) and provider keys.
  Follow `docs/rotated-debate.md`; retained evidence lives in
  `tests/resources/test-debates/`. These paid runs are not a routine gate.
- **Smoke test**: `.venv/bin/python -m rotated_debate --help` must exit
  successfully and list the `ask` command; this checks CLI startup only.
- **Build**: `.venv/bin/nox -s build` produces the wheel and source archive.
- **Gate**: `.venv/bin/nox` runs tests, compilation, and lint before code
  checkpoints and integration. For documentation-only checkpoints, check
  `git diff --check`, links, and configuration consistency. Run the build
  when packaging changes; live validation is required for provider behavior
  that the offline tests cannot establish.

## Delivery And Review

Owner decision of 2026-10-14, recorded by `project-management`. The
definition's default, pull-request delivery with a merge commit, applies to
every workstream; the earlier `direct-main` default of 2026-08-21 is
withdrawn. What the definition leaves open, who reviews and how, is settled
here:

- **Two agent pairs per slice.** An implementor pair builds one slice on
  the workstream branch and opens its pull request, PRn, against `main`; a
  further slice stacks on the first branch. The pull-request body carries
  what changed, the judgments taken for the owner's review, and the
  validation run with counts and limits.
- **The reviewer gets a written brief.** The implementor writes it: the
  goal, what to read first and in which order, what the change does, what
  to look for, what not to widen, the validation commands verbatim, the
  commit authorship rule, the delivery commands. The reviewer runs in its
  own checkout with its own environment and never touches the
  implementor's.
- **The review is a pull request against the slice.** PRn.1 is a branch off
  PRn's branch with small commits, and a body with findings grouped by
  kind, the validation it ran with counts, and proposals it did not
  implement. The reviewer runs the gate itself and reports what it could
  not run.
- **The implementor reads the diff**, not only the summary, posts an
  assessment comment on the pull request labeled by pair, and merges PRn.1
  into PRn's branch or pushes back with a new brief. At most three rounds
  per pull request; then the owner is asked. Accepting without a round and
  pushing back are both decisions with reasons, both recorded.
- **Only the owner merges to `main`**, as a merge commit, after the
  implementor has run the full gate on the merged branch and recorded the
  counts in the pull request.
- **Stacked branches are kept consistent by merge commits**, never by
  rebasing a published base.

Records travel as the definition says: status file and decision log inside
the slice's pull request, never in one of their own.

## Host Capabilities

What the project needs from the machine and the hosting service that the
generic workflow cannot assume: branch permissions, runners, credentials, and
the justification for each.

- **Signed-in agent clients.** `claude`, `codex` and `antigravity`, signed
  in once by the owner, are the `cli-` engine route's whole credential;
  no API key is read on that route. Declared in the manifest's
  `[capabilities] need` list.
- **A signed-in GitHub CLI: needed, not available.** *Delivery And Review*
  runs on pull requests, assessment comments and platform merges, which an
  agent in the capsule cannot perform without `gh` and a sign-in. Until
  the capsule provides one, the implementor writes the pull-request body
  into a note in the workstream directory and the owner opens, retargets
  and merges by hand. Requested from DevCapsule as a capability on
  2026-10-15 by mail from `project-management`.
- **Push access over SSH** to the integration remote and to the
  coordination branch, which the capsule already carries.

## Exceptions

Every recorded departure from `WORKFLOW.md`, each with its reason and, where
one exists, the condition that ends it. Empty means none.

For example, a project that integrates by squash merge instead of the
definition's merge commit records it here, with the consequence: records
cite pull requests and tags, never branch commits.
