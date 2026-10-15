# `rotated_debate` — user guide

`rotated_debate ask` runs one **rotated debate**: three (or more) LLM
engines take turns as ANSWERER, CRITIC, and SYNTHESIZER on a single
question, and the run is written out as one self-contained Markdown
transcript. Agreement between engines is an *observed state*, never a
correctness score. The binding contract is
[`engineering-docs/specifications/debate-invocation.md`](../engineering-docs/specifications/debate-invocation.md).

## Setup

```bash
pip install -e .[engines]
export ANTHROPIC_API_KEY=...
export OPENAI_API_KEY=...
export GOOGLE_API_KEY=...        # or GEMINI_API_KEY
```

Only the keys for the engines you actually select are needed.

## Quick start

```bash
python -m rotated_debate ask "Is X true?" --out debate.md
```

While it runs, one progress line per engine call goes to stderr
(`rotation 2/3 round 1/1: gemini-3.1-pro-preview critiquing claude-fable-5`).
When it finishes, stdout prints exactly one line:

```
state=converged transcript=debate.md
```

`state` is `converged`, `diverged`, or `unreported` — the provisional
aggregation of the synthesizers' verdicts. The exit code reports only
whether the run itself succeeded; the epistemic state is data, never an
exit code.

## Choosing engines: `--engines`

`--engines` takes a comma-separated list (default `claude,gemini,chatgpt`).
Each item can be, in order of resolution priority:

1. **An environment override** — `ROTATED_DEBATE_MODEL_<ITEM>` (item
   uppercased) always wins when set, e.g.
   `ROTATED_DEBATE_MODEL_CLAUDE=anthropic:claude-sonnet-5`.
2. **An explicit binding** — `name=provider:model` in LangChain's
   `init_chat_model` format, e.g. `mistral=mistralai:mistral-large`.
   Works for any provider LangChain supports; `name` is only a handle.
3. **A vendor alias** — `claude`, `gemini`, or `chatgpt`. Each alias is
   the project's *curated pick of that vendor's most capable model*,
   pinned in `engines.DEFAULT_MODELS` and changed only by a deliberate
   commit — never discovered or upgraded at runtime, so `git log` always
   answers "what model did this alias mean on that date". Current picks:

   | Alias | Model |
   |---|---|
   | `claude` | `claude-fable-5` |
   | `gemini` | `gemini-3.1-pro-preview` |
   | `chatgpt` | `gpt-5.6-sol` |

4. **A bare model name** — accepted directly when it matches a known
   shape; the provider is inferred:

   | Pattern | Provider |
   |---|---|
   | `claude-*` | Anthropic |
   | `gemini-*` | Google |
   | `gpt-*`, `o<digit>*` | OpenAI |

   Example: `--engines claude-sonnet-5,gemini-3.1-pro-preview,gpt-5.5-pro`.

5. **A model through its vendor's command-line client** — `cli-` in front
   of a full model name: `cli-claude-fable-5-1`. No API key is involved;
   the model is reached through the client you are already signed in to,
   and billed to that subscription. The vendor is inferred from the name
   exactly as for a bare model name, and each vendor has one client:

   | Name shape | Client | Signed in through | Sign-in check |
   |---|---|---|---|
   | `cli-claude-*` | `claude` | claude.ai | `claude auth status` |
   | `cli-gpt-*`, `cli-o<digit>*` | `codex` | ChatGPT | `codex login status` |
   | `cli-gemini-*` | `antigravity` | Google | `antigravity models` |

   The name after `cli-` is passed to the client unchanged, so it must be
   an id the client accepts; a wrong id fails at the client with its own
   message. `chatgpt` is an API-route alias, not a model id: the client
   form is `cli-gpt-6-astra`. Antigravity's ids end in an effort level
   (`gemini-3.8-flash-high`); an id without one (`cli-gemini-3.8-flash`)
   gets `high`, and an id it does not list is refused with the list, since
   that client also serves Claude and GPT-OSS models. A handle bound with
   `name=cli-...` still honors `ROTATED_DEBATE_MODEL_<NAME>` like any
   handle.

   Before the debate starts, each client is asked whether it is signed in
   through its vendor's sign-in; if one is not, nothing runs and the
   message names the client to sign in to. `claude` and `codex` report
   how they are signed in, and a key-based sign-in refuses: this route is
   the subscription. `antigravity` reports no sign-in method; its model
   listing establishes that it is signed in, not how. Each client is called
   as a chat engine that may search the web and nothing else, in an empty
   working directory, with every vendor's key variables
   (`ANTHROPIC_API_KEY`, `OPENAI_API_KEY`, `GEMINI_API_KEY`,
   `GOOGLE_API_KEY`, their token and cloud-route variants) removed from
   its environment, so an exported key cannot take over the billing.

   **Client engines browse by default.** Unlike the API route, where
   `--browse` turns searching on, a `cli-` engine always has its client's
   web access; a later slice adds the switch to turn it off. `--browse`
   therefore concerns the API engines in the lineup only. What each
   client does, and what the transcript records as evidence:

   - `claude`: the role prompt replaces its system prompt; exactly its
     `WebSearch` and `WebFetch` tools, allowed without prompts; no other
     built-in tools, no MCP servers, no settings files, no saved session.
     Evidence: `web_search_requests` summed from the client's per-model
     report, and `num_turns`, since fetches have no counter.
   - `codex`: the role prompt replaces its built-in instructions through
     an instructions file; read-only sandbox; ephemeral; no rules; hosted
     web search set to `live`; every other built-in tool switched off, the
     shell included; a private home holding only a link to your sign-in
     file, so your global `AGENTS.md`, config and MCP servers do not reach
     the engine. Evidence: `web_search_requests`, one per search item in
     its event stream. Any other tool item fails the call.
   - `antigravity`: no instruction flag, so the role prompt is prepended
     to the prompt; a private home holding a link to your sign-in token
     and the engine's own permissions, which allow URL reads and deny
     commands, MCP servers and writes, whatever your own settings allow;
     `--sandbox` restricts its terminal. Its web search is Google Search
     grounding, a model-side feature governed by an account-level setting
     in the client, not by any flag or permission: it browses when that
     setting is on. Evidence: `grounding_links`, the count of grounding
     redirect links in the answer, plus `num_turns`.

   Managed organization settings, if a client has any, still apply. If
   `TMPDIR` points inside a project, the engine refuses rather than let a
   client read that project's instructions. `--browse`
   and `--temperature` are not available on this route and refuse, naming
   the engine. Routes mix freely:
   `--engines cli-claude-fable-5-1,gemini,chatgpt` is a normal debate. One
   client call may take up to ten minutes (`ROTATED_DEBATE_CLIENT_TIMEOUT`
   seconds overrides).

Anything that fits none of these is an error naming the accepted forms.
A debate needs at least three engines.

In transcripts and progress output, engines are always reported by their
**model name** (`claude-fable-5`), not the alias you typed — reports name
what actually ran. A client engine is reported as typed, `cli-claude-fable-5-1`,
so the same model by API and by client in one debate stay distinct.

## Other flags

| Flag | Default | Meaning |
|---|---|---|
| `--context FILE` | none | Prepend file(s) as shared context for every role; repeatable. |
| `--rotations N` | 3 | Role-assignment triples to run. With 3 engines, 3 = every engine plays every role once (balanced); 6 = all permutations. |
| `--rounds N` | 1 | Critique→rebuttal exchanges per rotation before synthesis. |
| `--browse` | off | Give every API engine its vendor's server-side web-search tool (Anthropic web search, OpenAI web search via the Responses API, Google Search grounding). Search runs on the provider's servers and is billed per search, on top of tokens; Anthropic searches are capped at 5 per call. Only works for providers with a known browse tool (currently the three above) — others error. `cli-` engines browse by default and ignore the flag. |
| `--temperature T` | provider default | Only sent when set. Current Anthropic and OpenAI models reject an explicit temperature — leave unset unless you know the model accepts it. Client engines refuse this flag, including a client used as the last synthesizer; omit it to use the client's default. |
| `--add-last-synthesizer MODEL` | off | Add a final synthesis over the rotation syntheses, produced by `MODEL` (any form `--engines` items accept, e.g. `gemini-3.7-flash`). The last synthesizer is a judge of the record, not a participant: it **never browses**, is instructed to use only the text at hand, and reports agreement/disagreement on facts and on reasoning separately. Its verdict is recorded alongside the others in `outcome_state` — it does not change the reported `state=` line. |
| `--out FILE` | `debate-<timestamp>.md` | Transcript path. The only file the command writes. |

## The transcript

One Markdown file: YAML frontmatter, then the answers, then every
rotation's full exchange and synthesis. Frontmatter worth knowing:

- `engines` — reporting label → `provider:model` actually used; a client
  engine reads `cli-claude:claude-fable-5-1`, the client and the model.
- `usage` — per-engine consumption totals as reported by the provider
  (token counts for all current bindings) plus a `calls` counter, and —
  on browsing runs, where the provider reports it — server-side search
  counts (e.g. `web_search_requests`). A client engine adds what its
  client reports: for `claude`, `total_cost_usd`, `num_turns` and
  `web_search_requests`; for `codex`, cached and reasoning token counts
  and `web_search_requests`; for `antigravity`, thinking tokens,
  `num_turns` and `grounding_links`. The dollar value is the `claude` client's
  reported estimate, not a measurement of subscription charges or
  remaining plan allowance; the other two report no price. See
  [Claude Code's cost documentation](https://code.claude.com/docs/en/costs).
- `outcome_state` — reserves `deterministic_tally` (future) alongside the
  `synthesizer_meta` verdict aggregation and, when
  `--add-last-synthesizer` was used, the `last_synthesizer_verdict` with
  its facts/reasoning agreement lists; the candidates are recorded side
  by side, and divergence between them is a finding, not an error. The
  last synthesis also appears as the first section of the transcript
  body — it is the digest to read first.
- `concessions` — reasoned concessions vs. capitulations (a concession
  without a stated reason).
- `parse_errors` — engines whose structured JSON block could not be
  extracted; the run continues and records the failure instead of dying.

Real example transcripts live in
[`tests/resources/test-debates/`](../tests/resources/test-debates/).
