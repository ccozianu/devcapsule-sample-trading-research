---
kind: work-order
recipient: cli-engines
issued: 2026-10-14
issued-by: product owner
status: open
requirements: [R-PROTO-001]
decisions:
  - engineering-docs/decisions/engineering/2026-08-23-langchain-engine-access.md
  - engineering-docs/wip/2026-10-13-cli-engines/CURRENT-STATUS.md#decisions-2026-10-14
delivery: pull-request, reviewed; see Delivery And Review in WORKFLOW-LOCAL.md
---

# Work Order: `cli-engines` slice 1, the `claude` client engine

## Goal

Let a debate run with an engine reached through the signed-in `claude`
command-line client instead of an API key, with the protocol, transcript
and reported state unchanged. A user types `cli-claude-fable-5-1` in
`--engines` and gets that model through `claude`; the transcript says so.

This is the first of three client slices (`claude`, then `codex`, then
`antigravity`), each its own work order and pull request.

## Scope

In scope:

1. **Grammar.** An `--engines` item of the form `cli-<model>` denotes the
   model `<model>`, by its vendor's full id, reached through that vendor's
   default client. The vendor is inferred from `<model>` by the patterns
   bare names already use (`claude-*` is Anthropic, `gemini-*` Google,
   `gpt-*` and `o<digit>*` OpenAI); the client per vendor is one table:
   Anthropic `claude`, OpenAI `codex`, Google `antigravity`. The explicit
   `name=` binding form may name such an item too. In this slice only the
   `claude` client is implemented; a `cli-` item resolving to another
   client stops before any call with a message naming the slice that will
   add it. The API route, its aliases, pins and environment overrides are
   untouched; routes mix freely in one debate.
2. **The engine.** A `ChatFn` that runs `claude` as a chat engine: the
   protocol's system message becomes the whole system prompt, the user
   message the prompt; print mode, JSON output, the model pinned to the
   typed id, no tools, no session persistence, no repository access. The
   probed flag set of 2026-10-14 in the status file is the starting point;
   the implementor confirms it against the installed version and records
   the exact command line in the pull request.
3. **The sign-in check.** Before the first call, each `cli-` engine's
   client is asked whether it is signed in, by its own status command and
   without a model call. If any is not, nothing runs and the refusal names
   the client and the user who must sign in. No key is read, written or
   mentioned.
4. **Browse refusal.** `--browse` with any `cli-` engine stops before any
   call, naming the engine; see decision 3.
5. **Usage.** What the client reports is folded into the existing usage
   sink under the engine's key as reported: token fields, the dollar cost
   where present, the turn count, with the client named as the source.
   Nothing is normalized or scored.
6. **Reporting.** The engine's label in progress lines, the transcript and
   the usage map is the item as typed, so the same model by API and by
   client in one debate stay distinct. The transcript's `engines` map
   records, for a client engine, the client and the model.
7. **User documentation.** The `--engines` section of
   `docs/rotated-debate.md` gains the `cli-` form, the sign-in
   precondition and the browse limit, in the same pull request, since the
   slice reaches `main` on its own.
8. **Tests.** A fake `claude` script on `PATH` that answers the status
   command and the print command with recorded JSON, so the suite runs
   with no sign-in, no network and no real client. Tests cover: grammar
   parsing and vendor inference for `cli-` items; the not-signed-in
   refusal; the browse refusal; the other-client refusal; the command line
   built; usage capture; the label; a full debate with scripted client
   engines through the CLI.

Out of scope, do not widen:

- The `codex` and `antigravity` clients beyond the refusal in item 1.
- Browsing through any client.
- Running clients as agents with tools or repository access.
- Any change to the protocol, parsing, prompts, transcript layout or the
  specification's role rules.
- A model through a client other than its vendor's default, or a private
  endpoint; deferred by the owner.

## Judgments left to the implementor, to be listed in the pull request

- Where the vendor-to-client table and the client runner live: inside
  `engines.py` beside the LangChain path, or a sibling module that
  `engines.py` dispatches to. Prefer whichever keeps the core modules
  dependency-free and `engines.py` the only module that touches a
  mechanism.
- The exact representation of a client engine in the transcript's
  `engines` map, and whether the client's version is recorded.
- Timeout per client call and what a timeout or non-zero exit records.

## Validation

From the repository root, as `WORKFLOW-LOCAL.md` says:

```text
.venv/bin/nox
.venv/bin/nox -s tests
.venv/bin/python -m rotated_debate --help
```

The gate must pass with no provider keys and no client sign-in in the
environment. One owner-executed live run with a real `cli-claude-...`
engine beside two API engines is the acceptance evidence; its transcript
is retained under `tests/resources/test-debates/` with the usage map
intact, and the pull request records its counts.

## Delivery

Per *Delivery And Review* in `WORKFLOW-LOCAL.md`: the implementor pair
opens the pull request from `ws-cli-engines/v0` against `main`, writes the
reviewer's brief, and the reviewer pair, on the `codex` client unless the
owner says otherwise, reviews as a stacked pull request. At most three
rounds; the owner merges as a merge commit. Commits end with the
co-authorship trailer the implementor's agent uses.

## Finish Criteria

Done means all of:

- `python -m rotated_debate ask --engines cli-claude-fable-5-1,gemini,chatgpt`
  runs a debate in the owner's environment and the transcript names the
  client engine as typed with its usage.
- With `claude` signed out, or absent, the same command refuses before any
  call and names what to do.
- `--browse` with that lineup refuses, naming the client engine.
- The gate passes offline with the fake client; the test count in the pull
  request is higher than before by the tests in item 8.
- The user documentation shows the `cli-` form.
- The reviewed pull request is merged by the owner.

Reopen if a later `claude` client version changes the print-mode flags or
the JSON shape; the fake client must then be re-recorded from the real one.
