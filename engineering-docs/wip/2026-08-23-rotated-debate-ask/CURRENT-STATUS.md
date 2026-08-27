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

First live run in progress (2026-08-27). The owner runs the e2e in their
own terminal (API keys are not visible to Claude's shell in this
container). Three launch bugs found and fixed on `main`:

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

- **Progress reporting (owner feedback, 2026-08-27):** the CLI is silent
  for minutes during a live run; emit progress to stderr (per-rotation /
  per-role-call lines). Deferred until the in-flight e2e finishes — the
  package is installed `-e`, so editing `src/` would affect the running
  process.
- Keys are exported only in the owner's terminal, not in the container
  profile; owner will set up shared access later. Until then, live runs
  are owner-executed.
- Prompt templates are first-cut; iterate against real transcripts.
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
