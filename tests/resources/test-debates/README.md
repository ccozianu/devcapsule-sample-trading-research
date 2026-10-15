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
- `20260827-180434-GOOG-browse-2rounds-xtrasynth-debate.md` — same
  configuration plus `--add-last-synthesizer gemini-3.7-flash`. First
  live last-synthesis: flash's text-only discipline held (every cited
  figure traces to the three syntheses; spot-checked), facts/reasoning
  axes cleanly separated (`factual_disputes: []`, two real reasoning
  disputes surfaced), verdict converged, flash leg cost ~$0.01 on 6.8k
  tokens. Total ~$9.9 — cheaper than the 14:30 run despite the extra
  role (large run-to-run variance in Fable's search volume).
- `20261014-214924-cli-claude-91-prime-debate.md` — first live run through a
  command-line client (2026-10-14, cli-engines slice 1): three engines all
  reached through the signed-in `claude` client, `cli-claude-fable-5-1` /
  `cli-claude-sonnet-5` / `cli-claude-opus-5`, on a trivial arithmetic
  question, 3 rotations, 1 round. `state=converged`, zero parse errors,
  6 reasoned concessions / 0 capitulations, 12 client calls in 3m47s.
  Usage as the client reports it: 28,360 input tokens (nearly all
  cache creation), 14,926 output tokens, $0.69 at list
  price under the subscription (fable-5-1 $0.35, sonnet-5 $0.11, opus-5 $0.23). Implementor validation; the
  owner's mixed-route acceptance run is still to come.
- `20261015-074404-cli-three-clients-91-prime-debate.md` — first live run across all
  three command-line clients (2026-10-15, cli-engines slices 2 and 3):
  `cli-claude-fable-5-1` through `claude`, `cli-gpt-6-astra` through
  `codex`, `cli-gemini-3.8-flash` through `antigravity` (effort `high`
  added by the engine), same trivial question as the slice-1 run, 3
  rotations, 1 round. `state=converged`, zero parse errors, 2 reasoned
  concessions / 0 capitulations, 12 client calls. Usage as each client
  reports it: claude 3.6k input tokens over 4 calls at $0.15 estimated;
  codex 53.0k input (32.5k cached, its own tool descriptions each call);
  antigravity 60.2k input (its own agent prompt each call) and 8.4k
  thinking tokens. The two clients without a price report none. This is
  the acceptance evidence the slices 2 and 3 work order names.
- `20261015-101604-NEM-gold-debasement-cli-debate.md` — first substantive question
  through the three command-line clients (2026-10-15, owner's proposition:
  the gold debasement trade still has legs and NEM will make new all-time
  highs because the US deficit keeps dollar rates lagging the dollar's
  depreciation). Engines `cli-claude-fable-5-1` / `cli-gpt-6-astra` /
  `cli-gemini-4-argon-high`, no browsing (the client route cannot yet),
  3 rotations, 1 round, 15m08s. `state=diverged`: two synthesizers report
  converged, the codex one diverged. 22 reasoned concessions / 0
  capitulations, zero parse errors. Usage as the clients report it: claude
  18.9k output tokens at $1.25 estimated; codex 30.2k input / 3.1k output;
  antigravity 78.1k input / 27.6k output with 17.2k thinking. Also the first
  run after codex's tools were switched off in full: the first attempt was
  rejected by the tool guard when the codex critic searched the web.
