# Rotated-Debate Ask Workstream

Start date: `2026-08-23`

Goal: Implement `python -m rotated_debate ask` — the stateless,
domain-agnostic invocation surface of the debate protocol — per
`engineering-docs/specifications/debate-invocation.md` §1, using LangChain
for provider flexibility (owner decision,
`engineering-docs/decisions/engineering/2026-08-23-langchain-engine-access.md`).

State: `active`

Branch prefix: `rotated-debate/`

Integration target: `main` (`direct-main`).

## Current Task

**First live run succeeded (2026-08-27):** three engines, 3 rotations,
1 round, on a real question (GOOG valuation). `state=converged`,
`parse_errors: []` across all nine structured outputs, 15 reasoned
concessions / 0 capitulations — the D4 distinction and the reflexive
teardown behavior both showed up in practice (Gemini's synthesis records
the original answerer accepting a full teardown of its valuation
framework). Owner ran it in their terminal (keys are not visible to
Claude's shell in this container). Three launch bugs found and fixed on
`main` beforehand:

- `22a8702` — explicit `temperature=0.3` default removed; current
  Anthropic and OpenAI models 400 on any explicit sampling parameter.
  Temperature is now opt-in end to end (None = provider default).
- `576f0cb` — Gemini default rebound to `gemini-3.1-pro-preview`
  (`gemini-2.5-pro` 404s for new users).
- `1934938` — ChatGPT default rebound to `gpt-5.6-sol` (owner request,
  verified available on the API from usage Tier 1; staggered-rollout
  fallback: `ROTATED_DEBATE_MODEL_CHATGPT=openai:gpt-5.5-pro`).

All three provider keys authenticate in the owner's environment.

v0 itself was implemented, repo-validated, and **published to remote
`main` at `7ea6651`** (2026-08-23). The workstream branch
`rotated-debate/ask-v0` was fast-forward-integrated per `direct-main`.
What shipped:

- `src/rotated_debate/`: dependency-free core — `model` (settings, records,
  concession/capitulation distinction, reserved outcome fields), `parsing`
  (lenient JSON-block extraction that records failures instead of raising),
  `prompts` (v0 role templates, marked iterable), `protocol` (balanced
  cyclic-first rotations, per-engine answer memoization, bounded rounds),
  `transcript` (self-contained Markdown with YAML frontmatter reserving
  both OQ-1 outcome fields side by side) — plus `engines` (the only module
  touching LangChain, lazily imported) and `cli`/`__main__`.
- 19 new unit tests with scripted fake engines (27 total pass); full `nox`
  (tests, compile, lint) green. No network or keys needed for validation.
- `--browse` intentionally exits with an error naming spec §5.
- `pyproject.toml` gains the `engines` optional extra
  (langchain + anthropic/openai/google-genai providers).

## Open Threads

- **Done — progress reporting (owner feedback, 2026-08-27):**
  `protocol.run_debate` takes an optional `on_progress` callback (core
  stays print-free); the CLI wires it to one-line stderr messages before
  every engine call.
- **Live-run evidence for OQ-2/S9:** all three synthesizers independently
  flagged that a "right now" valuation question cannot be answered
  defensibly without live data (figures mixed 2023/2024/2025, no dated
  price snapshot) — direct support for browsing (or injected context) in
  decision-focused debates.
- **`--browse` implemented (2026-08-27, spec §5 amendment):** each engine
  gets its vendor's server-executed web-search tool bound via LangChain
  `bind_tools` (Anthropic web_search_20260209 max_uses=5, OpenAI
  web_search on the Responses API, Google Search grounding); protocol
  stays tool-unaware. **Not yet live-tested.** First-run checks: the
  Anthropic tool-version variant against claude-fable-5 (fall back to
  web_search_20250305 on a 400), the OpenAI Responses-v1 content shape
  through `_normalize_content`, and whether Gemini/OpenAI expose search
  counts anywhere we can meter (only Anthropic's
  usage.server_tool_use shape is folded into `usage` so far). Plan: run
  the same GOOG question with `--browse` for a browse/no-browse
  transcript pair on identical input (OQ-2 evidence).
- Prompt iteration items from the first transcript: the critic misread
  the true system date as a hallucinated one; consider telling roles the
  run date is authoritative.
- Keys are exported only in the owner's terminal, not in the container
  profile; owner will set up shared access later. Until then, live runs
  are owner-executed.
- OQ-1 unchanged: transcript frontmatter records `deterministic_tally: null`
  and the provisional `synthesizer_meta` aggregation, ready for comparison.

## Next Resumable Task

Blocked on the owner injecting API keys (ANTHROPIC_API_KEY, OPENAI_API_KEY,
GOOGLE_API_KEY) into the environment — not yet done as of session close
2026-08-23. Then: `pip install -e .[engines]`; run
`python -m rotated_debate ask "<harmless question>"`; verify the v0 default
model bindings in `engines.DEFAULT_MODELS` against what the keys can
actually reach; read the transcript and iterate the prompt templates. Then
proceed per the settled order in new workstreams: `portfolio context`, then
`portfolio debate`, then `sweep`
(contract: `engineering-docs/specifications/debate-invocation.md`).
