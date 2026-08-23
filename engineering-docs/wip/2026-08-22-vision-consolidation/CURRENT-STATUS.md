# Vision Consolidation Workstream

Start date: `2026-08-22`

Goal: Interview the project owner to a settled, unambiguous project vision;
record decisions and open questions; produce the sanitized demo portfolio
dataset; then rewrite the project-front documents (README, REQUIREMENTS,
entry points) so a fresh comparable LLM cannot miss what the project is.
Implementation is intentionally paused until this workstream says the design
is on solid footing (owner instruction, 2026-08-22).

State: `deliverables complete; ready to archive` (2026-08-23 — interview
closed at S1–S9, front docs rewritten, skeleton cut, UX settled and bound as
the v0 spec; archive per WORKFLOW.md when convenient)

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

Front docs are owner-approved. The portfolio knowledge skeleton is cut under
`portfolio/` (deviation from INFORMATION_MODEL §2 — nested, not repo-root —
recorded in `portfolio/README.md`): 17 position files generated from the
committed snapshot, TH-001 quantum-race thesis and factor seeded from the
owner's stated basket rationale (draft; falsifiers TODO), ROUTING.md,
DISPUTES.md, calendar/evals stubs with verified-dates-only and OQ-5 backlog
notes, and a CONTEXT.md placeholder awaiting its generator.

The UX outline is settled (owner, 2026-08-22): digest-plus-transcripts,
command names approved, sweep is watermark-based catch-up with cadence owned
by an external trigger, no alert channel. The binding contract is
`engineering-docs/specifications/debate-invocation.md` (v0), and
R-REFRESH-001 carries the watermark refinement.

Implementation unpaused 2026-08-23: the owner picked `rotated_debate ask`
first, on LangChain (decision recorded), and that build shipped in the
`rotated-debate-ask` workstream. The owner-confirmed order for what follows:
`portfolio context`, then `portfolio debate`, then `sweep` — each to be
opened as its own ordinary workstream from current `main`. Nothing remains
in this workstream itself; it is ready to archive.
