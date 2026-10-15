# Record: review round 1 of slice 1, the `claude` client engine

Implementor pair: Claude Fable 5.1 with the owner, on `ws-cli-engines/v0`.
Reviewer pair: Codex (`gpt-6-astra`) in its own worktree on
`ws-cli-engines/v0-review`, from a written brief, no push. Reviewed
implementation commit `36b026d`. The reviewer's report, `REVIEW.md`, stayed
uncommitted in its worktree as the brief asked; this record is the
implementor's assessment of it, written after reading the diff, not only
the summary. Round merged as `3c4d186`; findings resolved in `f41380a`.

## Assessment, finding by finding

| # | Reviewer's finding | Decision | What was done |
|---|---|---|---|
| F1 | An exported `ANTHROPIC_API_KEY` could make the client bill the key, not the sign-in; `loggedIn` alone does not prove the route | Accepted, fixed | `ANTHROPIC_API_KEY` and `ANTHROPIC_AUTH_TOKEN` are removed from every client subprocess, status check included. Verified live: with a bogus key exported, the call through the code path succeeds, which it could not if the key were used. The user documentation now says so. The reviewer's further suggestion of rejecting auth methods was not taken: with the variables scrubbed the method the client reports is the sign-in's. |
| F2 | `--tools ""` and `--setting-sources ""` do not establish no-MCP and no-repository-context | Accepted in part, fixed | Measured: the same prompt costs 805 input tokens from this repository and 417 from an empty directory, so `CLAUDE.md` discovery follows the working directory regardless of setting sources. The client now runs in an empty temporary directory of its own, with `--strict-mcp-config` and no `--mcp-config`, so no MCP server loads. Managed organization settings remain outside the flags' reach and the documentation says so. The docstring's "writes nothing to disk" became "saves no session". |
| F3 | Pipe encoding followed the parent locale | Accepted, reviewer's fix merged | UTF-8 on both pipes, with a regression under an ASCII locale. |
| F4 | A timeout or launch failure of the status command escaped as a traceback | Accepted, reviewer's fix merged | Both become refusals naming the client and a step. The implementor added `stdin=DEVNULL` to the status check after the fake blocked on an inherited stdin; a real client could do the same. |
| F5 | `--temperature` was silently dropped for client engines while the transcript recorded it | Accepted, reviewer's fix merged | Client engines refuse an explicit temperature before the sign-in check, last-synthesizer path included; documented. |
| F6 | The dollar figure was described as subscription cost | Accepted, reviewer's fix merged | Described as the client's reported estimate at list price. |
| F7 | The docstring said no environment default applies to a `cli-` item, but a handle's override still won | Accepted, fixed by stating the rule | The documented contract stands: a handle's `ROTATED_DEBATE_MODEL_<NAME>` override wins, and an override written in the `cli-` form resolves like any `cli-` item (the first test exposed that it was returned raw). Docstring, guide and test agree. |
| F8 | The fake's provenance could not be checked; signed-out exit code wrong; parser failure paths uncovered | Accepted, fixed | Recorded, redacted output of `claude` 2.1.261 lives under `tests/fixtures/claude-client/` with a README; the fake builds its answers from it; signed out it exits 1. Parser and error-report paths have tests. |
| F9 | The triple-dot diff carried workstream records beyond the eight items | Noted, no change | Records travel the working branch by the workflow's rule; the implementation commit itself touched five files. |

Not merged from the review branch: its two edits to this status file
(`59e466e` in part, `1a3362e`). A workstream's status file is the pair's
own account; the reviewer's account is this record. The merge kept the
working branch's copy.

## Gate after the round

`.venv/bin/nox`: 71 tests (62 before the round, 66 after the reviewer's
fixes), compile and lint clean, offline, 5 seconds. One real call through
the code path with a bogus key exported: `pong`, 419 input tokens, cost as
the client reports it.

## Proposals the reviewer did not implement, and their status

- Auth-method validation: not taken; see F1.
- A controlled subprocess environment: taken, as the key scrub plus the
  empty working directory.
- Live verification with configured MCP and repository instructions:
  taken in the form above, measured by token count; a probe with a
  deliberately configured MCP server was not run.
- Override precedence: settled; see F7.

## Process notes

- Codex's own sandbox needs Linux user namespaces the capsule does not
  grant (`bwrap` refused); the reviewer ran with that sandbox bypassed, the
  capsule being the sandbox. First launch produced no review; the relaunch
  took about 25 minutes.
- The reviewer's gate found a Ruff B023 in its own test and fixed it before
  handing over, and reported its counts and limits; that is the behavior
  the DevCapsule record called trustworthy.
