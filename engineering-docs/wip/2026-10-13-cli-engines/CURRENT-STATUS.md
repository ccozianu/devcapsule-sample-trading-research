# CLI Engines Workstream

Start date: `2026-10-13`

Goal: Organize a rotated debate whose engines are command-line coding
clients, `claude`, `codex` and the Antigravity CLI, reached through the
sign-in already present in the environment, instead of LangChain chat
models reached through API keys. The debate protocol, the transcript and
the reported state stay as the invocation specification defines them; only
the access route changes.

State: `active; slice 1 in review, round 2`

Definition read: WORKFLOW.md@c3c0722d6cd5, WORKFLOW-LOCAL.md@426b1fa5ef12

Branch prefix: `ws-cli-engines/`

Branch association: `ws-cli-engines/v0`

Integration target: `main`

Delivery method: `pull-request`, reviewed by a second agent pair and merged
by the owner as a merge commit, by the project-wide owner decision of
2026-10-14 recorded by `project-management` under *Delivery And Review* in
`WORKFLOW-LOCAL.md` (on its branch until its first integration). Never
force-push `main`; stop for semantic conflicts or genuine divergence.

Branch synchronization: fork from current `main`; rebase while unpublished
and merge `main` in once the branch is shared.

Custody: opened 2026-10-13 in a worktree checkout since removed; continued
2026-10-14 in the main checkout on the owner's direction, with the claim
taken over.

## Brief from the owner, 2026-10-13

"Let's start a workstream where we will implement first organizing a
debate where instead of LangChain with API key authentication, we will be
using command line clients like claude and antigravity and codex to call
the endpoints via SSO authentication that is assumed to be ambient in the
environment."

## Scope And Boundaries

- In scope: a second engine access route beside LangChain. An engine
  backed by a command-line client is a `ChatFn` like every other: it takes
  the message list and returns the text. The protocol, parsing, transcript
  and reporting modules do not change for it.
- In scope: the invocation form for such engines in `--engines`, the
  curated pinned model behind each client alias, usage accounting from what
  each client reports, and the browse setting mapped onto each client's own
  web tooling.
- In scope: the sign-in check at start, with a plain refusal naming the
  client that is not signed in, since no key is handled anywhere.
- Out of scope: changing what a debate is, the portfolio application, and
  any provider reached by key. The LangChain route stays as it is.
- Out of scope until the owner says otherwise: running the clients as
  agents with tools over this repository. The first slice calls them as
  chat engines on the prompt alone, so a transcript made through a client
  and one made through an API are comparable.

## Current Task

Slice 1, the `claude` client engine, implemented on 2026-10-14 under the
[work order](../../work-orders/2026-10-14-cli-engines-slice-1-claude-client.md)
and in review.

What landed on the branch, commit `36b026d`: `clients.py`, new, the client
route; `engines.py` dispatches `cli-<model>` items to it and widens the
usage sink to numeric fields; `docs/rotated-debate.md` documents the form;
`tests/test_client_engines.py`, 19 tests on a fake `claude` script. Gate:
62 tests (43 before), compile and lint clean, offline. Refusals exercised
against the real environment with no model call: `--browse`, the `codex`
and `antigravity` placeholders, an unrecognized name, a missing client.

Live validation, commit after this one: a real debate with three engines
through the signed-in `claude` client, retained as
`tests/resources/test-debates/20261014-214924-cli-claude-91-prime-debate.md`.
`state=converged`, zero parse errors, 12 client calls, 3m47s,
$0.69 at list price as the client reports it. Two probes of the
client preceded it (stdin prompt, JSON shape), 403 input tokens each.

Judgments taken, for the owner's review in the pull request:

- The route lives in a sibling module, `clients.py`; `engines.py` stays
  the only module callers go through and dispatches by the `cli-` prefix.
- A client engine's transcript entry reads `cli-claude:<model>`, the
  client and the model in the existing `provider:model` slot; the client
  version is not recorded.
- The usage sink's value type widened from `int` to `int | float` so the
  client's dollar cost is recorded as reported; `record_usage` now sums
  floats too.
- One client call is bounded by a 600 s timeout, overridable by
  `ROTATED_DEBATE_CLIENT_TIMEOUT`; a timeout or non-zero exit raises with
  the engine named, as an API failure would.
- The prompt travels on stdin; the system prompt on the command line.
  `--setting-sources ""` keeps the repository's own agent configuration
  out of the engine; `--tools ""` leaves it no tools.
- A handle's environment override keeps its documented precedence over a
  `cli-` binding, and an override in the `cli-` form resolves like any
  `cli-` item; a bare `cli-` item has no usable variable name.
- The client's environment loses `ANTHROPIC_API_KEY` and
  `ANTHROPIC_AUTH_TOKEN`, and the call runs in an empty temporary directory
  with `--strict-mcp-config`, so neither an exported key nor this
  repository's agent configuration reaches the engine. Managed
  organization settings are outside these flags' reach; documented.

Review round 1 done 2026-10-14, merged as `3c4d186`, resolved in the
commit after it; see the
[round-1 record](2026-10-14-record-review-round-1.md): nine findings,
four fixes merged from the reviewer, four resolved by the implementor (key
variables scrubbed from the client's environment, client run in an empty
directory with MCP off, override rule stated, fixtures recorded), one
noted. Gate after the round: 71 tests, compile and lint clean. Round 2 asks
the reviewer to verify those resolutions only.

Pull request: the GitHub CLI is not installed in the capsule and no token
is present, so the pull request against `main` is opened by the owner
from the pushed branch; its body is drafted by the implementor.

Mail taken 2026-10-14: `project-management` forwarded the DevCapsule
process record as design input; acknowledged, see the decision log. The
record's suggestions enter the design as follows: the client-backed engine
kind is this workstream's goal; bounded rounds, attributed assessments and
"proposals not implemented" shape how reviews of this work are written if
the owner chooses pull-request delivery; the delivery choice itself is
question 6.

Design, for the owner's decisions before any implementation. The questions
are under *Open Questions*. The facts found so far:

- `claude` 2.1.283 and `codex` 0.157.1 are installed and signed in on this
  capsule, through claude.ai and ChatGPT respectively. The Antigravity CLI
  is a need of this project's own formation (`antigravity-agent` in its
  manifest) and absent only on the DevCapsule capsule this was written in.
- `claude -p` prints a response and exits; `--output-format json` returns
  the text with usage; `--model` pins the model; `--json-schema` gives
  structured output; `--allowedTools` and `--no-session-persistence` bound
  what a call may do.
- `codex exec` runs one turn and exits; `-m` pins the model; `--json`
  streams events including token usage; `-o` writes the last message to a
  file.
- Probed 2026-10-14 with one trivial prompt each, from the DevCapsule
  capsule. `claude -p --output-format json --model claude-fable-5-1
  --no-session-persistence --system-prompt "<engine prompt>" --tools ""`
  returns `result`, `usage` (input, output, cache tokens,
  `server_tool_use`), `modelUsage` with `costUSD`, and `num_turns`; with
  its own system prompt replaced and no tools the call is 408 input tokens
  for 4 output tokens. Without that, the client's own agent prompt costs
  about 20,000 cached tokens per call. `--bare` disables the sign-in and
  is not usable. `codex exec --json --ephemeral --skip-git-repo-check -m
  gpt-6-astra` streams `thread.started`, `turn.started`,
  `item.completed` with the `agent_message` text, and `turn.completed`
  with usage (input, cached input, output, reasoning tokens); its own
  instructions cost about 14,000 input tokens per call and cannot be
  replaced from the command line. Outside a git repository the check must
  be skipped; inside a trusted one it runs as is.
- Verified 2026-10-14 on this project's own capsule: `claude` 2.1.261
  signed in through claude.ai, `codex` 0.153.4 signed in through ChatGPT,
  `antigravity` 1.1.24 signed in. Antigravity has a print mode:
  `--print` with `--output-format json`, `--model`, `--json-schema`,
  `--sandbox` and a `--print-timeout` (default five minutes). It is a
  multi-vendor router, not a Gemini client: `antigravity models` lists
  Gemini 3.8 Flash, Claude Opus 5.5, Claude Sonnet 5.5 and GPT-OSS 120B,
  each at low, medium and high effort, and no Gemini Pro. Its usage report
  in print mode is still unprobed.
- The protocol's engine contract is `ChatFn`, a function from the message
  list to a string; `build_engines` in `engines.py` is the only place
  providers are touched, and `resolve_model_id` is the alias resolution the
  specification binds.

Next resumable task: review round 2, confined to the round-1
resolutions; assess, merge or push back; rerun the gate on the merged
branch; hand the pull request to the owner with the counts; then the
owner's mixed-route acceptance run. The original scope, for the
record: in `engines.py`, recognize a `cli-<model>`
item, infer the vendor from the model name, build a `ChatFn` that runs the
vendor's client as a chat engine (for `claude`: `-p`, JSON output, the
engine prompt as the whole system prompt, no tools, no session
persistence, the model pinned to the typed name), check sign-in before the
debate starts and refuse plainly if absent, refuse `--browse` for such an
engine, record the client's usage report as-is, and label the engine as
typed in the transcript. Tests run a fake client script, never the real
one. Deliver as a reviewed pull request per *Delivery And Review*.

## Decisions, 2026-10-14

Taken by the owner one question at a time; each entry names the options
that were rejected so they are not re-proposed.

1. **Invocation form: `cli-<full model name>`.** An `--engines` item
   `cli-XXXX` means the model `XXXX`, by its vendor's full name, reached
   through that vendor's default command-line client: `cli-claude-fable-5-1`
   through `claude`, `cli-gpt-6-astra` through `codex`,
   `cli-gemini-3.8-flash-high` through `antigravity`. The vendor is
   inferred from the name's shape by the same patterns bare names use
   today; the client per vendor is a one-line table. No client aliases and
   no client pins: the user types the real model id, which the clients can
   list, and the transcript records it. The API route and its curated
   aliases are unchanged, and routes mix freely in one debate. Reporting
   label for a client engine is the item as typed, so the same model by
   API and by client in one debate stay distinct. Deferred, much later:
   reaching a model through a different client or endpoint than its
   vendor's default, such as a Claude model through Antigravity or a
   private deployment.
   Superseded on the same day: the client-prefix-plus-aliases form and
   the intent-resolution proposal
   ([design](2026-10-14-design-intent-resolution.md)), both rejected by the
   owner as making the user name or configure a mechanism. Also rejected:
   a whole-debate route flag and a per-engine `@cli` suffix.
2. **Pinned models: none for client engines.** Follows from 1: the full
   name typed is the pin, auditable in the transcript. The 2026-08-27 pins
   for the API aliases are untouched.
3. **Browsing: refused on client engines in the first slices.** `--browse`
   with a `cli-` engine stops before any call, naming the engine. Mapping
   it onto each client's own web tool is a later slice, if wanted.
   Rejected for now: allowing the `claude` client's web search in slice 1,
   so that the first client transcripts compare like for like with API
   transcripts without browsing.
4. **Usage: recorded as the client reports it**, under the engine's key in
   the same usage sink, with the client named as the source; the `claude`
   client's dollar cost and `codex`'s reasoning tokens included, nothing
   normalized.
5. **Order: `claude`, then `codex`, then `antigravity`**, one slice each,
   Antigravity after its print-mode usage report is probed on this
   capsule. Rejected: all three clients in one slice.
6. **Delivery: reviewed pull requests**, settled project-wide; see the
   delivery method above.

## Open Threads

- Awaiting the human: opening the pull request from the pushed branch,
  and the mixed-route acceptance run (`cli-claude-fable-5-1,gemini,chatgpt`)
  with the API keys only the owner holds.
- Weighed and unresolved: nothing; the six questions are decided above.
- Deliberately not preserved: the chat in which the questions were asked.

## Workstream Document Index

- [Design: intent resolution](2026-10-14-design-intent-resolution.md),
  a proposal of 2026-10-14, rejected the same day in favor of the `cli-`
  form; kept for the reasoning it records. Read only to see what was not
  chosen.

- `intake/`: empty; `intake-dispositions.md` holds the decision log.
- [Work order: slice 1, the `claude` client](../../work-orders/2026-10-14-cli-engines-slice-1-claude-client.md),
  the scope and finish criteria of the current task; open until merged.
- [Record: review round 1](2026-10-14-record-review-round-1.md), the
  implementor's assessment of every finding and what was merged; read
  when a finding is reopened.
- [Note: pull-request body](2026-10-14-note-pull-request-body.md), the
  text the owner pastes when opening the pull request; counts filled in
  after round 2.
- The access-route decision this extends:
  [LangChain as the engine access layer](../../decisions/engineering/2026-08-23-langchain-engine-access.md).
- The binding contract:
  [debate invocation surfaces](../../specifications/debate-invocation.md),
  section 1.
- The process record from DevCapsule, acknowledged 2026-10-14 as design
  input: it is kept verbatim inside the decision log's entry source,
  `intake-dispositions.md`, and the original is at `project-management`'s
  commit `2a03886`. Its open question on delivery is question 6 above.
