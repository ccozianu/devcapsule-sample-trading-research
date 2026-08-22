# Vision Consolidation Workstream

Start date: `2026-08-22`

Goal: Interview the project owner to a settled, unambiguous project vision;
record decisions and open questions; produce the sanitized demo portfolio
dataset; then rewrite the project-front documents (README, REQUIREMENTS,
entry points) so a fresh comparable LLM cannot miss what the project is.
Implementation is intentionally paused until this workstream says the design
is on solid footing (owner instruction, 2026-08-22).

State: `active`

Branch prefix: `vision-consolidation/`

Integration target: `main` (delivery method `direct-main` per the standing
project-management decision of 2026-08-21).

## Current Task

Continue the vision interview to closure. Interview state so far is recorded
in `engineering-docs/session-records/2026-08-22-vision-interview.md`
(authoritative statement of what the project is: settled decisions S1–S7,
open questions OQ-1–OQ-5).

Completed in this workstream:

- Session record and the deferred convergence-declaration question written
  (`engineering-docs/design-notes/open-q-convergence-declaration.md`).
- OQ-3 resolved: sanitized demo portfolio snapshot committed at
  `data/snapshots/portfolio-2026-08-22.csv` with format documentation in
  `data/snapshots/FORMAT.md`. The raw export was deleted by the owner after
  sanitizing; policy (raw exports are never committed, sanitize-then-delete)
  lives in `data/snapshots/FORMAT.md`.

## Open Threads

- OQ-1 convergence declaration — deferred until real debate transcripts
  exist (see design note).
- OQ-2 narrowed by S9: engines browse in the daily refresh debates; still
  open whether decision-focused debates browse or argue packet-only.
- OQ-4 narrowed: lineup is Claude/Gemini/ChatGPT; access route open, must
  support per-vendor browsing tools (S9). API keys to be injected by the
  owner; code stays provider-flexible.
- OQ-5 export of prior claude.ai webapp debate transcripts into `debates/`
  and backfill of already-made engine predictions into the evals ledger.
- Acceptance settled (S8, with owner refinements): reflexive acceptance —
  user happiness plus an engine-converged verdict grounded in the repo's
  own scoreable usage records; returns rejected as a metric; eligible only
  after ≥2 months of live usage crossing ≥1 earnings season. Triggers
  settled at high level (S9): daily knowledge-refresh debate with browsing;
  concrete orchestration mechanics deliberately deferred.

## Relationship To Prior Work

The labeled-fixture slice (R-EVAL-002 in the project-management workstream's
priorities) is superseded in priority by this consolidation; it remains valid
for the debate-protocol half later. The existing deterministic modules under
`src/rotated_consensus/` stay untouched and remain the comparison baseline
regardless of OQ-1's outcome.

## Next Resumable Task

The interview has converged on decisions S1–S9; remaining open questions are
either deliberately deferred (OQ-1, orchestration mechanics) or non-blocking
(access route, transcript export). Next: rewrite the project-front documents
(README, REQUIREMENTS, entry points) around S1–S9 so a fresh comparable LLM
cannot miss what the project is, and capture new requirement records for
both halves (debate protocol package; portfolio application per
`engineering-docs/sketch-of-a-project/INFORMATION_MODEL.md`).
