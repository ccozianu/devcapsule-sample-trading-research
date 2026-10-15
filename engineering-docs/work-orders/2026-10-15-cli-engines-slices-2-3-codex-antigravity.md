---
kind: work-order
recipient: cli-engines
issued: 2026-10-15
issued-by: product owner
status: open
requirements: [R-PROTO-001]
decisions:
  - engineering-docs/wip/2026-10-13-cli-engines/CURRENT-STATUS.md#decisions-2026-10-14
  - engineering-docs/work-orders/2026-10-14-cli-engines-slice-1-claude-client.md
delivery: pull-request, reviewed; stacked on slice 1
---

# Work Order: `cli-engines` slices 2 and 3, the `codex` and `antigravity` clients

## Goal

Every `cli-<model>` item works: `cli-gpt-6-astra` through `codex`,
`cli-gemini-3.8-flash` through `antigravity`, beside `cli-claude-*`
through `claude`. The owner pulled both slices forward on 2026-10-15
("I expect the program to select the default CLI for that model"), so
they ship together, stacked on the slice-1 branch.

## Scope

In scope, for each of the two clients, what slice 1 established for
`claude`: the exact non-interactive call, probed and recorded as fixtures;
the sign-in check through the client's own report, refusing an API-key
sign-in; the key-variable scrub for that vendor; the empty working
directory; usage recorded as reported; the fake client on PATH for the
gate; the user documentation. Specific to each:

- `codex`: the system prompt through a replacement instructions file;
  `-s read-only`, `--ephemeral`, `--skip-git-repo-check`; the JSON event
  stream parsed for the agent message and the turn's usage.
- `antigravity`: no instruction flag exists, so the system prompt is
  prepended to the prompt; an id without an effort suffix gets `--effort
  high`; an id the client does not list is refused with the list.

Out of scope: agentic use, and any change to the protocol, prompts,
parsing or transcript layout.

Addendum, 2026-10-15, owner direction after the browsing research:
browsing through the clients is in scope and on by default, each client
through its own switch (`claude` web tools allowed, `codex`
`web_search="live"`, `antigravity` grounding plus URL reads), with the
evidence each client can give recorded as usage. The command-line switch
to turn client browsing off is a separate, later slice.

## Validation

As slice 1. Acceptance evidence: one real debate with all three clients,
`cli-claude-fable-5-1,cli-gpt-6-astra,cli-gemini-3.8-flash`, retained
under `tests/resources/test-debates/`, run by the implementor on this
capsule, where all three clients are signed in.

## Finish Criteria

- That lineup runs a debate end to end on this capsule and the
  transcript names all three client engines with their usage.
- Each client refuses before any call when signed out or signed in with
  a key, naming the client.
- The gate passes offline with the three fakes.
- The user documentation describes all three.
- The reviewed pull request is merged by the owner.
