# Design: the user states intent, the program resolves the mechanism

Status: rejected by the owner on 2026-10-14, the day it was written, in
favor of the simpler `cli-<full model name>` form recorded as decision 1 in
the status file: an access policy and per-mechanism pins made the user
configure a mechanism. Kept for the reasoning; nothing below is current.

## The problem with the first framing

The six open questions all asked the user to name a mechanism: a prefix
per client, a pin per client alias, a browse mapping per client. A user
running a debate has three intentions and none of them is "which binary":

1. **Which engines debate.** A lineup, by vendor or by model.
2. **What pays for it.** API keys in the environment, or the subscriptions
   the signed-in clients carry. Usually the honest answer is "whatever is
   available here", because the keys live only in the owner's terminal.
3. **That the record is exact.** Whatever ran, the transcript says so.

## The proposal

**`--engines` keeps meaning the lineup and nothing else.** Aliases, bare
model names and `name=provider:model` bindings stay as the specification
binds them. No client prefix, no suffix, no new alias family.

**One new setting names the access policy, not the client.**
`--access auto|api|client`, default `auto`, with the existing per-alias
environment pattern for a per-engine override, `ROTATED_DEBATE_ACCESS_<ALIAS>`,
so no new grammar enters `--engines`:

- `api`: every engine through LangChain with keys, exactly as today.
- `client`: every engine through a signed-in command-line client.
- `auto`: per engine, the first mechanism that can serve it, in a fixed
  order: an API key for its vendor, then a signed-in client that serves the
  model. Keys first because a key is a deliberate act in the environment
  and a sign-in is ambient; the order is one line in code and is recorded
  in the transcript either way.

**A resolver turns (alias, model, policy) into a mechanism before the
debate starts.** It knows, in one table, which mechanisms can serve which
vendor: Anthropic models by `ANTHROPIC_API_KEY` or the `claude` client;
OpenAI models by `OPENAI_API_KEY` or the `codex` client; Gemini models by
`GOOGLE_API_KEY` or the `antigravity` client, which also serves Claude
Opus and Sonnet 5.5 and GPT-OSS and so is a second choice for those.
Availability is checked without a model call: the key's presence, the
client's own sign-in status command.

**The resolver prints its table and refuses whole.** One line per engine
on stderr before the first call, `claude -> claude-fable-5 via api` or
`gemini -> gemini-3.8-flash-high via antigravity`. If any engine cannot be
served, nothing runs and the refusal names, per engine, the key to export
or the client to sign in to. This is the sign-in check the status file
asked for, and it is the same check for every mechanism.

**Pinning stays, per alias and per mechanism.** A curated alias pins the
model in code as decided on 2026-08-27, and a mechanism that spells or
serves the model differently has its own pin beside it, in the same
table, in the same commit discipline. Concretely: `claude` is
`claude-fable-5` by API and `claude-fable-5-1` by the `claude` client;
`chatgpt` is `gpt-5.6-sol` by API and `gpt-6-astra` by `codex`; `gemini`
is `gemini-3.1-pro-preview` by API and `gemini-3.8-flash-high` by
`antigravity`, the only Gemini it serves. A bare model name or explicit
binding is passed through unchanged, and a mechanism that does not serve
it is simply not a candidate. The user never sees the second column
unless they read the transcript, where it always appears.

**Effort is part of the pin where the mechanism has it.** Antigravity
names effort in the model id; the pin chooses `high`. The API route has
no equivalent knob, and the transcript's model id carries the difference.

**The transcript records the mechanism as an observed fact.** The
`engines` frontmatter map gains the mechanism beside the model id, and
`usage` records what each mechanism reports, under the same per-engine
key: tokens for all, `costUSD` where the `claude` client reports it,
reasoning tokens where `codex` does. Nothing is normalized into a score.

**Browsing keeps its meaning and refuses where it cannot be honored.**
`--browse` means "every engine may search the web"; by API it is the
vendor's server-side tool as today. In the first slice a client
mechanism cannot honor it and the resolver refuses the combination,
naming the engine; mapping it onto the clients' own web tools is a later
slice. Under `auto`, browsing therefore prefers the API where a key
exists and refuses otherwise, which is the honest outcome.

**Clients are called as chat engines, not agents.** Each call carries
the engine prompt as the whole system prompt, no tools, no session, no
repository access: `claude -p` with the probed flags, `codex exec` with
`--ephemeral`, `antigravity --print` with its print flags. A transcript
made through a client and one made by API are comparable. The agentic
use of the clients stays out of scope, as the status file says.

## What this settles among the six questions

- Question 1, the invocation form: no new grammar; `--access` and the
  environment override replace the prefix and the client aliases.
- Question 2, pinning: per alias and per mechanism, in code.
- Question 3, browsing: refused on client mechanisms in the first slice.
- Question 4, usage: recorded as reported, keyed by engine, mechanism
  named.
- Question 5, Antigravity: verified present and signed in on this capsule
  on 2026-10-14; it becomes the Gemini mechanism, third slice after
  `claude` and `codex` once its print-mode usage report is probed.
- Question 6, delivery: already settled project-wide.

## Slices, if accepted

1. The resolver with the availability table and the refusal, the
   `--access` setting, the transcript fields, and the `claude` mechanism;
   tests drive a fake client script, never the real one.
2. The `codex` mechanism.
3. The `antigravity` mechanism, after probing its print-mode usage.
4. Browsing through the clients, if the owner wants it.

## Rejected while writing this

- A client prefix family in `--engines` (decision 1 of 2026-10-14): it
  makes the user name the binary and leaks the mechanism into the lineup.
- Client aliases such as `claude-code` and `antigravity`: same reason,
  and `antigravity` is not a vendor.
- Accepting a client's default model: unauditable; contradicts the
  2026-08-27 pinning reading.
- Clients first under `auto`: a sign-in is ambient and easy to forget,
  while a key is placed on purpose; the cheaper-by-subscription argument
  is real and is why `--access client` exists as one word.
