# Note: pull-request body (opened 2026-10-15 as #2) for slices 2 and 3

For the owner to paste when opening the stacked pull request. The base
is the slice-1 branch, so GitHub shows only this slice's diff while slice
1 is open; after slice 1 merges, retarget the base to `main`.

---

**Title:** cli-engines slices 2 and 3: the `codex` and `antigravity` clients, so every `cli-<model>` works

**Branch:** `ws-cli-engines/v0-clients` → `ws-cli-engines/v0` (retarget to
`main` once slice 1 is merged), merge commit. Review branch
`ws-cli-engines/v0-clients-review` is stacked on it.

## What changed

```text
--engines item               client        call
cli-gpt-6-astra          ->  codex         exec --json, prompt on stdin, system prompt as a
                                           replacement instructions file, read-only sandbox,
                                           ephemeral, web search off, no rules, private
                                           CODEX_HOME linking only the sign-in file
cli-gemini-3.8-flash     ->  antigravity   prompt on stdin, JSON result, --sandbox,
                                           --effort high added to an id without one,
                                           system prompt prepended (no instruction flag)
cli-claude-fable-5-1     ->  claude        unchanged from slice 1
```

Both clients get what slice 1 gave `claude`: sign-in checked through the
client's own report before any call, every vendor's key variables
scrubbed, an empty working directory, usage recorded as reported, a fake
client built from recorded fixtures for the gate, and user documentation.

Work order: `engineering-docs/work-orders/2026-10-15-cli-engines-slices-2-3-codex-antigravity.md`.

## Judgments taken, for the owner's review

1. `antigravity` gets `--effort high` when the id has no effort suffix,
   so `cli-gemini-3.8-flash` works as typed; the transcript records the id
   as typed. An id the client does not list is refused with the list.
2. `codex`'s system prompt goes through `model_instructions_file`. The
   client still read a planted `~/.codex/AGENTS.md` under every documented
   switch, so each call runs with a private `CODEX_HOME` holding one
   symlink to the real `auth.json`; the sign-in holds through the link and
   nothing else from the real home is read. The client's caches land in
   that private home and die with the engine.
3. Codex commands cannot be switched off. Any tool item in its event
   stream fails the call, so a tool-assisted answer is never recorded as a
   chat answer. Antigravity has no tools-off switch; `num_turns` is the
   evidence and the guide says so.
4. `antigravity` reports no sign-in method; its model listing establishes
   sign-in only. `claude` and `codex` refuse a key-based sign-in.

## Review

One round by the Codex pair: four findings, two fixes merged (strict
codex stream parsing, antigravity effort matching), two resolved as above.
Record: `engineering-docs/wip/2026-10-13-cli-engines/2026-10-15-record-review-round-3.md`.

## Validation

- Gate `.venv/bin/nox`: 98 tests (74 after slice 1), compile and lint
  clean, offline, no keys, no sign-in.
- Live: one real debate across all three clients,
  `cli-claude-fable-5-1,cli-gpt-6-astra,cli-gemini-3.8-flash`,
  `state=converged`, zero parse errors, 12 calls, 2m32s, usage per client
  in the transcript; retained as
  `tests/resources/test-debates/20261015-074404-cli-three-clients-91-prime-debate.md`.
  This is the acceptance evidence the work order names. One real codex
  call through the final code path after the review: answered, caches in
  the private home only.
