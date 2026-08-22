# R-REFRESH-001: Daily Knowledge-Refresh Debate

Statement: At least once a day, the three major engines (Claude, Gemini,
ChatGPT) debate whether and how the portfolio knowledge — theses,
confirmations, infirmations, and future events to watch — must be updated in
light of intervening news, with browsing/research tools enabled for every
participating engine. The likely shape is two-stage — first a
browsing-enabled debate on which news are relevant, then a debate on what the
news mean, including whether the user should be alerted to exit positions —
but concrete orchestration mechanics are deliberately unspecified until the
substrate and protocol exist (session record S9). The orchestration layer
owns freshness triggers generally, and the human can terminate any thread of
spending (e.g., a liquidated position warrants no further token spend).

Refinement (owner, 2026-08-22, UX round): the tool owns no cadence. The
sweep's contract is "update knowledge with what is new since the latest
recorded knowledge update" — watermark-based catch-up, resumable from the
last covered interval — and the daily rhythm comes from an external trigger
the owner provisions (or a human on demand). Output is a one-screen digest;
full transcripts on disk; no alert channel.

Priority: MVP
Status: accepted

Implementation:
- Not started. Contract: `engineering-docs/specifications/debate-invocation.md` §3.

Validation:
- Deferred until orchestration mechanics are specified.

Related:
- `engineering-docs/session-records/2026-08-22-vision-interview.md` (S5, S9)
- Consequence for engine access: the access route must expose each vendor's
  web-search/browse tooling (session record OQ-4).
