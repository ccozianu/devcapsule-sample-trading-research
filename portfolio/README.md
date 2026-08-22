# Portfolio Knowledge Repository

This tree instantiates
`engineering-docs/sketch-of-a-project/INFORMATION_MODEL.md` for the sanitized
demo portfolio. It is the living knowledge base the human and the engines
maintain together; the software under `src/` exists to serve it.

**Deviation from INFORMATION_MODEL §2, recorded:** the model assumes the
knowledge repo is the repository root. This repository doubles as the
software project, so the knowledge tree is nested here under `portfolio/`.
Two further mappings: snapshots stay at the repo-root `data/snapshots/`
(committed there before this tree existed), and `AGENTS.md`/`WORKFLOW.md` at
the root serve the whole repository, not just this tree.

## Layout

| Path | Contents | Writer |
|---|---|---|
| `CONTEXT.md` | GENERATED session packet — entry point of every session | tool only |
| `ROUTING.md` | conflict-of-interest routing table | human |
| `DISPUTES.md` | open inter-engine disagreements | tool + human |
| `positions/` | one file per instrument, criteria in frontmatter | human + tool |
| `theses/` | one file per thesis, claim-graph body | human + engines |
| `factors/` | factor definitions and standing acceptances | human |
| `calendar/` | dated external events wired to the criteria they can fire | human + tool |
| `decisions/` | decision log — **human-only, no exceptions** | human only |
| `debates/` | engine debate transcripts, frontmattered | tool only |
| `evals/` | prediction ledger and scoring | tool + human |
| `observations/` | dated, first-person T3 practitioner readings | human |
| `../data/snapshots/` | sanitized position/basis/mark snapshots | tool (sanitized) |

## Standing rules (from the information model — do not relitigate)

1. Everything dated, everything evidence-tiered (T1 audited/filed,
   T2 credibly reported, T3 posited). Tier-laundering is a schema violation.
2. Basis, quantity, and marks live **only** in the snapshot; criteria live
   **only** in position files. Everything else links.
3. Criteria must be evaluable from public observables, or they are
   sentiments, not criteria.
4. Generated blocks are never hand-edited; `decisions/` is never
   machine-written.
5. A claim without a tier and at least one falsifier cannot leave `draft`.
6. Decisions record `arrival_order` (thesis before or after the trade idea)
   honestly — it is scoreable, not shameful.
