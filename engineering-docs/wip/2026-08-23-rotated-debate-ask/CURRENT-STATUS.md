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
  stays tool-unaware. **Live-validated 2026-08-27**
  (`tests/resources/test-debates/20260827-111059-GOOG-browse-debate.md`,
  the browse/no-browse pair for OQ-2): web_search_20260209 works on
  claude-fable-5; OpenAI Responses-v1 content survives
  `_normalize_content`; zero parse errors; the debate caught and settled
  real factual errors against primary sources (Gemini's "$85B equity
  raise" ruled false vs. the SEC 10-Q's $49.6B). Remaining gaps:
  (a) Gemini reports no search counts and implausibly small input tokens
  (grounding invisible to usage_metadata), OpenAI reports no search
  count either — browse cost accounting is Anthropic-complete only;
  (b) Anthropic's citation annotations are flattened to quoted text by
  `_normalize_content`, losing its source URLs (Gemini/GPT inline
  markdown links survive) — relevant to the reserved browsing-evidence
  tier labeling. Cost: ~8x the no-browse baseline (~$7.50 vs ~$0.95),
  dominated by Fable's 19 searches / 471k input tokens; the max_uses=5
  per-call cap was nearly saturated (19 of 20).
- **`--add-last-synthesizer` implemented (2026-08-27, spec §5
  amendment):** optional final text-only synthesis over the rotation
  syntheses by a non-participant model; never browses; reports
  facts-vs-reasoning agreement separately; verdict recorded as a third
  OQ-1 candidate (`outcome_state.last_synthesizer_verdict`), never
  replacing the state line. Awaiting first live run.
- **Deferred design question (owner, 2026-08-27):** should the three
  rotation synthesizers also lose browse access? Rationale for yes:
  evidence introduced at synthesis is unrebutted (nobody criticizes the
  synthesizer) — the browse transcripts show synthesizers researching.
  Requires per-role tool binding (protocol currently uses one ChatFn per
  engine for all roles). Decide after transcript evidence accumulates.
- Prompt iteration items from the first transcript: the critic misread
  the true system date as a hallucinated one; consider telling roles the
  run date is authoritative.
- **OPEN owner task (2026-08-27):** verify the day's OpenAI and Google
  console spend against
  `engineering-docs/design-notes/2026-08-27-cost-model.md` and fill in
  its Verification table (agents remind until done — see that doc).
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
