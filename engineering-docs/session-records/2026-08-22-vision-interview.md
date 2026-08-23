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
- **S8 — Acceptance criterion is reflexive, not financial (added
  2026-08-22, later the same session).** Portfolio returns are explicitly
  rejected as the success metric — the owner made ~+50% on a similar
  portfolio the prior year and named that number as a joke, precisely
  because return outcomes are luck-confounded. The demo is accepted when
  (a) the human user is happy, and (b) the engines, debating over the
  **repo's own usage records** (decisions log, evals-ledger resolutions,
  disputes and their observable resolutions, debate transcripts), converge
  on the claim that this setup is an acceptable way to help real users gain
  knowledge about the positions they hold. Guard, noted at acceptance time:
  that reflexive debate is exposed to sycophancy (engines judging a system
  whose transcripts they produced), so its evidence must be scoreable
  records — resolved predictions, criteria that fired before outcomes,
  capitulations caught — never impressions of the transcripts' quality.
  Owner refinement (same session): the acceptance debate is human-triggered —
  an owner who is losing money simply never convenes it — so the debate's
  real job is to catch **false satisfaction**: to veto a happy human whose
  records don't support the claim. Eligibility window, for the record: the
  acceptance debate may not be convened before **at least two months of live
  usage crossing at least one earnings season**, during which the shared
  knowledge on positions is updated against the market's evolution.
- **S9 — Daily knowledge-refresh debate (high level settled 2026-08-22;
  mechanics deliberately deferred).** At least once a day, the three major
  engines debate whether and how the portfolio knowledge — theses,
  confirmations, infirmations, future events to watch — needs updating in
  light of intervening news. All three engines participate **with
  browsing/research tools enabled**. Likely two-stage shape, to be
  validated in practice: first a browsing-enabled debate on *which news are
  relevant*, then a debate on *what the news mean* — including whether the
  user should be alerted to exit positions. Concrete orchestration details
  are explicitly premature; do not specify them yet.

## Open questions (deliberately deferred)

- **OQ-1 — Who declares convergence?** See
  `engineering-docs/design-notes/open-q-convergence-declaration.md`. The
  user's current inclination is a meta-level chat between synthesizers rather
  than the purely deterministic tally of DESIGN.md; deferred until real
  debate transcripts exist.
- **OQ-2 — Freshness mechanics inside a debate.** *Substantially resolved by
  S9:* engines do retrieve (browse) during the daily knowledge-refresh
  debates. Remaining detail: whether decision-focused debates also browse or
  argue strictly from the curated repo packet.
- **OQ-3 — CSV shuffle specification.** *Resolved later the same session:*
  the sanitized demo snapshot lives at `data/snapshots/portfolio-2026-08-22.csv`
  with format documentation in `data/snapshots/FORMAT.md`; the raw export
  was deleted after sanitizing (policy: raw exports are never committed).
- **OQ-4 — Engine lineup and access route.** *Resolved.* Lineup: the three
  major engines (Claude, Gemini, ChatGPT), as assumed throughout
  INFORMATION_MODEL.md. Access route (owner, 2026-08-23): LangChain
  chat-model abstractions, for future flexibility across LLMs and API
  endpoints — see
  `engineering-docs/decisions/engineering/2026-08-23-langchain-engine-access.md`.
  Browsing (S9) will ride LangChain's provider-native web-search tool
  bindings.
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
