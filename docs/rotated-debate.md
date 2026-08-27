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

Anything that fits none of these is an error naming the accepted forms.
A debate needs at least three engines.

In transcripts and progress output, engines are always reported by their
**model name** (`claude-fable-5`), not the alias you typed — reports name
what actually ran.

## Other flags

| Flag | Default | Meaning |
|---|---|---|
| `--context FILE` | none | Prepend file(s) as shared context for every role; repeatable. |
| `--rotations N` | 3 | Role-assignment triples to run. With 3 engines, 3 = every engine plays every role once (balanced); 6 = all permutations. |
| `--rounds N` | 1 | Critique→rebuttal exchanges per rotation before synthesis. |
| `--browse` | off | Not implemented in v0; exits with an error. |
| `--temperature T` | provider default | Only sent when set. Current Anthropic and OpenAI models reject an explicit temperature — leave unset unless you know the model accepts it. |
| `--out FILE` | `debate-<timestamp>.md` | Transcript path. The only file the command writes. |

## The transcript

One Markdown file: YAML frontmatter, then the answers, then every
rotation's full exchange and synthesis. Frontmatter worth knowing:

- `engines` — reporting label → `provider:model` actually used.
- `usage` — per-engine consumption totals as reported by the provider
  (token counts for all current bindings) plus a `calls` counter. This is
  where you read what a debate cost.
- `outcome_state` — reserves `deterministic_tally` (future) alongside the
  `synthesizer_meta` verdict aggregation; when both exist, divergence
  between them is a finding, not an error.
- `concessions` — reasoned concessions vs. capitulations (a concession
  without a stated reason).
- `parse_errors` — engines whose structured JSON block could not be
  extracted; the run continues and records the failure instead of dying.

Real example transcripts live in
[`tests/resources/test-debates/`](../tests/resources/test-debates/).
