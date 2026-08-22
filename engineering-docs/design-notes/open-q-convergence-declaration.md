# Open Question — Who Declares "Converged"? (OQ-1)

Status: **open, deliberately deferred** (user decision, 2026-08-22).
Revisit when real multi-engine debate transcripts exist to test both options
against. Origin: 2026-08-22 vision interview
(`engineering-docs/session-records/2026-08-22-vision-interview.md`).

## The question

At the end of a rotated debate, something must declare the outcome state
(converged / diverged, possibly majority). The two source documents disagree:

- **DESIGN.md position (deterministic tally).** Each engine files a final
  claim-structured position; deterministic, LLM-free code tallies verdicts
  per claim id. Auditable, reproducible, and the design's claimed
  contribution over prior art (llm-council, MoA), which all end in an LLM
  aggregator. Implemented today in `src/rotated_consensus/merge.py`.
- **Synthesizer-declared (LLM meta-chat).** The user's current inclination:
  after the rotated syntheses, hold a short chat **between the synthesizers**
  at the meta level. If they cannot agree even on whether the debate
  converged or diverged, our confidence in the engines acting in this setting
  takes a justified hit — that failure is itself signal. Even then, a
  meaningful synthesis of the state of facts is produced for the user and
  fed back into the knowledge repo.

## Why it is deferred, not decided

Both options are defensible; a mushy middle is not. The honest way to choose
is empirical: once debates run for real, compare the deterministic tally
against the synthesizers' meta-verdict on the same transcripts. Divergence
between the two adjudicators is itself a finding worth surfacing.

## Constraints that hold regardless of the outcome

- The reported state is an **observed state, never a confidence or
  correctness score** (DESIGN.md D4). This survives either mechanism.
- Concessions must be instrumented (reasoned vs. capitulation), whichever
  layer declares the state.
- If the synthesizer meta-chat declares the state, the docs must **drop the
  claim that final adjudication is LLM-free** — honesty about the mechanism
  outranks the marketing of determinism.
- The existing deterministic merge stays in the codebase either way, at
  minimum as the comparison baseline the meta-chat is measured against.
