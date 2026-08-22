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
  `data/snapshots/FORMAT.md`. Raw brokerage exports live untracked under
  `tests/resources/` (now gitignored).

## Open Threads

- OQ-1 convergence declaration — deferred until real debate transcripts
  exist (see design note).
- OQ-2 freshness mechanics inside a debate (packet-only vs. engine
  retrieval) — must be settled before debate-engine contracts are written.
- OQ-4 engine lineup and access route; API keys to be injected into the
  environment by the owner; code stays provider-flexible.
- OQ-5 export of prior claude.ai webapp debate transcripts into `debates/`
  and backfill of already-made engine predictions into the evals ledger.
- Interview questions pending owner answers: the concrete end-to-end
  acceptance scenario for the demo ("the pudding"), and the trigger taxonomy
  for convening debates (calendar events, snapshot thresholds, explicit
  command; news deliberately excluded for now unless the owner pushes back).

## Relationship To Prior Work

The labeled-fixture slice (R-EVAL-002 in the project-management workstream's
priorities) is superseded in priority by this consolidation; it remains valid
for the debate-protocol half later. The existing deterministic modules under
`src/rotated_consensus/` stay untouched and remain the comparison baseline
regardless of OQ-1's outcome.

## Next Resumable Task

Resume the interview at the pending questions above; when closed, rewrite
README/REQUIREMENTS and capture new requirement records for both halves
(debate protocol package; portfolio application per
`engineering-docs/sketch-of-a-project/INFORMATION_MODEL.md`).
