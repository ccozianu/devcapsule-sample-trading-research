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
