# Session Record — Project Vision Interview (2026-08-22)

Distilled from an interactive interview between the user (Costin) and Claude
(Fable 5) conducted to fix the project's identity before further
implementation. The user's standing instruction from this session: **do not
start implementing until the design is clarified enough to be on solid
footing; Claude's job is to interrogate critically and keep the project on
task.**

## What this project is (as settled in this session)

A **demo project** showcasing how a developer and multiple LLMs together
manage knowledge and make timely decisions on stock-market positions. It has
**two equal, co-developed halves**:

1. **The rotated-debate protocol** — a domain-agnostic Python package. For a
   given prompt, one LLM is ANSWERER, a second is CRITIC (faults,
   counterarguments), they exchange for bounded rounds, and a third LLM is
   SYNTHESIZER. Rotating N engines through the roles yields 3–6 synthesized
   answers depending on how much the user pays in tokens. The debate outcome
   is reported honestly as converged/diverged. The package must be usable on
   arbitrary questions (the user's example: a medical question), independent
   of the portfolio application.
2. **The portfolio application** — managing the developer's (shuffled)
   brokerage portfolio of stocks and options, built on the information model
   in `engineering-docs/sketch-of-a-project/INFORMATION_MODEL.md`: dated,
   evidence-tiered claims; kill/profit criteria checkable against public
   observables; a human-only decisions log; a predictions/evals ledger;
   persistent disputes; conflict-of-interest routing; a generated
   `CONTEXT.md` session packet.

The two halves connect in a loop: repo state → generated context packet →
rotated debate on a live decision → structured outputs written back (claims
to the evals ledger, disagreements to disputes, human decision to the
decisions log) → time passes, calendar/market events fire → the next debate
starts from the updated state. Opinions are expected to be **time-varying and
scoreable after the fact** (motivating example: two engines disagreed on the
debasement trade in mid-2026; the passage of time adjudicated).

## Decisions settled in this session

- **S1 — Demo, not product.** No end-user polish. The audience is developers;
  success is a convincing, honest showcase.
- **S2 — Two equal halves; pudding principle.** The debate protocol is a
  standalone deliverable, but victory on it is declared **only after** we are
  satisfied with results on real portfolio positions. Neither half strictly
  precedes the other; contracts between them are designed early.
- **S3 — Files-as-UI.** The user drives everything from an IDE: reading and
  writing Markdown, running Python commands from a terminal. Deliberately
  minimal but substantially functional. **Commands mutate knowledge state;
  tests verify.** Tests never mutate the knowledge repo.
- **S4 — This repo is the portfolio repo.** The living demo dataset is a
  **shuffled** derivative of the user's real brokerage export
  (quantities and identifying details altered; verifiable world facts such as
  symbols and option pricing kept). The raw export stays untracked and must
  never be committed.
- **S5 — Orchestration owns freshness.** The debate-orchestration layer
  (Python) is responsible for finding suitable triggers to refresh knowledge
  and reconcile it with real-world evolving facts. The human can terminate
  any thread of spending (e.g., liquidating a position moots further token
  spend on it).
- **S6 — Engine access.** API keys for the engines will be injected into this
  environment. Code stays provider-flexible (adapter seam; OpenRouter vs.
  direct SDKs not yet chosen).
- **S7 — Conflict-of-interest routing constrains rotation.** Per
  INFORMATION_MODEL.md §4.8: the synthesizer role for a topic must never be
  held by that topic's conflicted engine, so role rotation is pruned per
  topic. (Carried from the information model; treated as accepted.)

## Open questions (deliberately deferred)

- **OQ-1 — Who declares convergence?** See
  `engineering-docs/design-notes/open-q-convergence-declaration.md`. The
  user's current inclination is a meta-level chat between synthesizers rather
  than the purely deterministic tally of DESIGN.md; deferred until real
  debate transcripts exist.
- **OQ-2 — Freshness mechanics inside a debate.** Whether debating engines
  retrieve live data themselves or argue strictly from a curated packet is
  not yet fixed; S5 assigns responsibility (orchestration) but not mechanism.
- **OQ-3 — CSV shuffle specification.** *Resolved later the same session:*
  the sanitized demo snapshot lives at `data/snapshots/portfolio-2026-08-22.csv`
  with format documentation in `data/snapshots/FORMAT.md`; raw exports stay
  untracked under `tests/resources/` (gitignored).
- **OQ-4 — Engine lineup and access route** (which three models; OpenRouter
  vs. direct).
- **OQ-5 — Prior-art webapp history.** The originating manual sessions live
  in a claude.ai project Claude cannot access from this environment
  (https://claude.ai/cowork/project/019f5d6e-a605-74d7-9bbc-5829265422bc).
  Valuable transcripts (debate-formatted ones; the debasement-trade exchange)
  should be exported into `debates/` and this month's engine predictions
  backfilled into the evals ledger per INFORMATION_MODEL.md §6.7.

## Relationship to pre-existing documents

- `engineering-docs/sketch-of-a-project/DESIGN.md` — earlier design for a
  claim-atomized, deterministically merged consensus pipeline. Its
  micro-structure (roles, bounded rounds, honest epistemic states,
  capitulation instrumentation) stands; its insistence that the final merge
  is LLM-free is now **contested** by OQ-1 rather than settled.
- `engineering-docs/sketch-of-a-project/INFORMATION_MODEL.md` — the
  asynchronous macro-structure (what persists between debates). Endorsed by
  the user in this session as the model to pursue.
- The existing `src/rotated_consensus/` modules (domain, merge, evaluation)
  implement DESIGN.md's deterministic primitives and remain valid regardless
  of OQ-1's outcome: even a synthesizer-declared state benefits from a
  deterministic tally to compare against.
