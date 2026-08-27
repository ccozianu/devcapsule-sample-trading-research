# Real debate transcripts

Verbatim transcripts from live `python -m rotated_debate ask` runs, kept as
reference material and as fixtures for tests against real engine output.
Filenames carry the transcript's own `generated_at` timestamp
(`YYYYMMDD-HHMMSS-...`), matching the CLI's default naming convention.

- `20260827-100828-debate.md` — first successful live run (2026-08-27):
  GOOG valuation question, engines claude-sonnet-5 /
  gemini-3.1-pro-preview / gpt-5.6-sol, 3 rotations, `state=converged`,
  zero parse errors.
- `20260827-102644-GOOG-debate.md` — same question rerun with
  claude-fable-5 and the `usage:` frontmatter feature: all three engines
  reported token counts (claude 22.0k / gemini 18.5k / chatgpt 13.6k
  total tokens over 4 calls each), `state=converged`, zero parse errors.
- `20260827-111059-GOOG-browse-debate.md` — same question with
  `--browse` (the no-browse counterpart pair for OQ-2). All engines
  cite live Aug-2026 data; the debate caught and settled real factual
  errors against primary sources (Gemini's "$85B equity raise" ruled
  false vs. the SEC 10-Q's $49.6B; Fable's 17.4x P/E exposed as a $99B
  one-off-gain artifact). Fable made 19 web searches and 471k input
  tokens (~$6 of the ~$7.50 total). `state=converged`, zero parse errors.
- `20260827-143057-GOOG-browse-2rounds-debate.md` — same question,
  `--browse --rounds 2` (~$13.5, 1.8x the 1-round browse run). Round 2
  audits the rebuttals' reasoning rather than rehashing round 1: caught
  anchoring on an unrevised probability estimate (forced 60-65% down to
  55-60%), independently re-verified figures against EDGAR, reconciled
  the $85B/$49.6B dispute (a $90B upsized program: $49.6B completed +
  $40B unused ATM), and surfaced net-new facts (capped calls, Berkshire's
  Aug +$17B). Verdict direction unchanged from all prior runs.
  38 reasoned concessions / 0 capitulations, `state=converged`.
