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

v0 implemented, repo-validated, and **published to remote `main` at
`7ea6651`** (2026-08-23). The workstream branch `rotated-debate/ask-v0` was
fast-forward-integrated per `direct-main`. Session closed here; resume at
"Next Resumable Task" below. What shipped:

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

- Live three-engine run blocked on the owner injecting API keys; on first
  run, revisit the v0 default model bindings in `engines.DEFAULT_MODELS`.
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
