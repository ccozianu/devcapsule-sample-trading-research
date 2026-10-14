# CLI Engines Workstream

Start date: `2026-10-13`

Goal: Organize a rotated debate whose engines are command-line coding
clients, `claude`, `codex` and the Antigravity CLI, reached through the
sign-in already present in the environment, instead of LangChain chat
models reached through API keys. The debate protocol, the transcript and
the reported state stay as the invocation specification defines them; only
the access route changes.

State: `active; design first, then the first engine`

Definition read: WORKFLOW.md@c3c0722d6cd5, WORKFLOW-LOCAL.md@426b1fa5ef12

Branch prefix: `ws-cli-engines/`

Initial branch: `ws-cli-engines/v0`

Integration target: `main`

Delivery method: `direct-main` under the project-wide owner decision
recorded in the project-management handoff: rebase the clean branch onto
current `main`, validate, fast-forward local `main`, push normally. Never
force-push `main`; stop for semantic conflicts or genuine divergence. The
owner may instead ask for pull requests reviewed by a second agent pair, the
scheme described in the intake item `project-management` received on
2026-10-12 from the DevCapsule repository.

Branch synchronization: fork from current `main`; rebase while unpublished
and merge `main` in once the branch is shared.

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
- The protocol's engine contract is `ChatFn`, a function from the message
  list to a string; `build_engines` in `engines.py` is the only place
  providers are touched, and `resolve_model_id` is the alias resolution the
  specification binds.

Next resumable task: the owner answers the open questions; then the first
slice, a `claude`-backed engine with pinned model, usage accounting and the
sign-in check, with tests that run a fake client script and never the real
one.

## Open Questions, for the owner

1. The invocation form. A new provider prefix in the existing grammar,
   `cli-claude:<model>`, `cli-codex:<model>`, `cli-antigravity:<model>`,
   keeps `--engines` and the alias rules unchanged. The alternative is a
   separate flag naming the route. The prefix is recommended.
2. The pinned models. The specification pins the model behind a vendor
   alias in code. For a client the model is what `--model` or `-m` selects;
   the clients' own defaults are not auditable. Pin them in code as today,
   or accept the client's default and record what the client reports?
   Pinning is recommended.
3. Browsing. `claude -p` can be allowed its web search tool; `codex exec`
   has its own web search. Map `--browse` onto those, or keep `--browse`
   off for client engines in the first slice? Off first is recommended, so
   the first transcripts compare like for like with the API route.
4. Usage and cost. The clients report tokens and, for `claude`, a cost in
   dollars under a subscription. Record what each reports, in the same
   usage sink, with the client named as the source?
5. The Antigravity client. Its non-interactive invocation and its usage
   report are unverified here, since the client is absent on this capsule.
   Take it as the third slice, after `claude` and `codex`, verified in this
   project's own capsule?
6. Delivery. Direct to main as this project does today, or stacked pull
   requests with a second agent pair's review as in the DevCapsule
   repository?

## Workstream Document Index

- `intake/`: empty; `intake-dispositions.md` holds the decision log.
- The access-route decision this extends:
  [LangChain as the engine access layer](../../decisions/engineering/2026-08-23-langchain-engine-access.md).
- The binding contract:
  [debate invocation surfaces](../../specifications/debate-invocation.md),
  section 1.
- The process record from DevCapsule, acknowledged 2026-10-14 as design
  input: it is kept verbatim inside the decision log's entry source,
  `intake-dispositions.md`, and the original is at `project-management`'s
  commit `2a03886`. Its open question on delivery is question 6 above.
