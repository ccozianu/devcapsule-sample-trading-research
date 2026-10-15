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

## GitHub CLI

Pull requests, review comments and merges go through the GitHub CLI, `gh`,
which the owner installed by hand on 2026-10-15 until the capsule provides
it as a capability (requested from DevCapsule the same day). The rule:

- **Where it is.** In the conda environment `gh` under
  `/opt/xtras/miniconda3`. Every shell that needs it runs, first:

  ```text
  source /opt/xtras/miniconda3/etc/profile.d/conda.sh && conda activate gh
  ```

  An agent's tool shells do not persist state between commands, so the
  line is repeated in each command that calls `gh`. Nothing in the
  repository depends on the environment otherwise; leave the project
  `.venv` as it is.
- **Whose sign-in.** The owner's, made once with `gh auth login` over the
  web flow with the `repo` scope; the token lives in the owner's home
  under `.config/gh/`, outside the repository, and is never copied into
  configuration or records. `gh auth status` is the check at session
  start; a signed-out `gh` is a blocker to report, not a reason to find
  another route.
- **What an agent does with it.** Opens the pull request for a slice with
  the body from the workstream's pull-request note; opens the reviewer's
  stacked pull request or, when the review branch is already merged,
  posts the reviewer's report as a comment; posts each round's assessment
  as a comment labeled by pair; reads review comments; retargets a stacked
  pull request after its base merges; records pull-request numbers in the
  status file. All of this is ordinary agent work under *Delivery And
  Review*.
- **What stays with the owner.** The merge to `main`, as a merge commit,
  unless the owner directs the agent to merge in a given case. An agent
  never squashes, rebases through the platform, deletes a branch the
  workflow names, or changes repository settings.
- **Ends when** the capsule carries a `github-cli` capability with its own
  sign-in binding; this section is then rewritten for it.

## Host Capabilities

What the project needs from the machine and the hosting service that the
generic workflow cannot assume: branch permissions, runners, credentials, and
the justification for each.

## Exceptions

Every recorded departure from `WORKFLOW.md`, each with its reason and, where
one exists, the condition that ends it. Empty means none.

For example, a project that integrates by squash merge instead of the
definition's merge commit records it here, with the consequence: records
cite pull requests and tags, never branch commits.
