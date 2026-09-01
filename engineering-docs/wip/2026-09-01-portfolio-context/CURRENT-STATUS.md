# Portfolio Context Workstream

Start date: `2026-09-01`

Goal: Settle the user capabilities, UX contract, and derived design for the
deterministic, repository-aware portfolio context capability, then implement
`python -m portfolio context` only after the owner explicitly accepts the
requirements and design.

State: `active`

Branch prefix: `portfolio-context/`

Initial branch: `portfolio-context/design`

Integration target: `main`

Delivery method: `direct-main` under the project-wide owner decision recorded
in the project-management handoff. Rebase the clean integration branch onto
current `main`, validate, fast-forward local `main`, and push normally. Never
force-push `main`; stop for semantic conflicts or genuine divergence.

Branch synchronization: fork from current `main`; rebase while unpublished
and merge `main` if the branch becomes shared.

## Scope And Boundaries

- This workstream owns the context capability and the surrounding user journey
  needed to define it. `portfolio debate` and `sweep` remain separate future
  workstreams in that order.
- **No coding begins until the owner accepts the requirements, UX, and derived
  design.** The current phase is an interview and specification exercise.
- Existing accepted constraints are inputs, not an excuse to skip discovery:
  context generation is deterministic and has no LLM calls; it regenerates
  `portfolio/CONTEXT.md`; it refuses rather than silently truncating; and no
  command may write under the human-only `portfolio/decisions/` boundary.
- The broader portfolio capability may be discussed to make the context UX
  coherent, but implementation scope must not absorb portfolio debate, sweep,
  resolve, accept, or alerting behavior.

## Current Task

Conduct a design interview with the owner, beginning from user goals and
capabilities rather than the existing file schema. Settle, in order:

1. the primary user job and command-level capability;
2. the normal interaction and output UX;
3. source authority, freshness, validation, and missing-data behavior;
4. token-budget and refusal/degradation behavior;
5. generated-versus-authored mutation boundaries; and
6. the contract the later portfolio-debate workstream may rely on.

Record accepted requirements and unresolved choices before deriving the
technical design. Do not implement during this phase.

First slice opened 2026-09-01: the owner identified broker-export
reconciliation as the first concrete user journey. A proposed preview/apply UX
and its capability requirements are recorded in `requirements-and-ux.md`.
The privacy posture and preview/apply interaction are accepted; reconciliation
report contents and detailed error behavior remain proposed.

Second slice opened 2026-09-01: the owner accepted the preview/apply and
public-origin acknowledgement UX and identified the portfolio data contract as
the next GIGO risk to settle before design. `data-contract.md` now proposes
authority layers, core identities, provenance/value semantics, and validation
invariants for review; no storage schema is chosen.

Session checkpoint 2026-09-01: the owner provisionally accepted a consolidated
multi-account portfolio, holdings at account + instrument granularity, and
analytic positions that may group multiple holdings or instruments. The owner
also fixed the modeling order: user capabilities first, conceptual model
second, physical layout last. The conceptual model remains incomplete and no
storage or file-layout decision has been made.

## Established Inputs

- `engineering-docs/session-records/2026-08-22-vision-interview.md`: the
  portfolio application is a files-as-UI, auditable knowledge repository;
  commands mutate knowledge state and tests only verify.
- `engineering-docs/sketch-of-a-project/INFORMATION_MODEL.md` §5: the proposed
  generated packet contains snapshot state, criteria, calendar triggers,
  disputes, pending decisions, settled matters, and routing reminders within
  roughly 3,000 tokens.
- `engineering-docs/specifications/debate-invocation.md` §2: the accepted v0
  command is `portfolio context`, deterministic, and refuses silent
  truncation.
- `engineering-docs/requirements/R-PORT-001.md`: one context read should answer
  current state, prior commitments, and what can change the answer and when.
- `portfolio/` already contains 17 position skeletons, one draft thesis and
  factor, routing and dispute files, calendar/evals stubs, and a placeholder
  `CONTEXT.md`; these are evidence for the interview, not a completed design.

## Open Threads

- Accepted (owner, 2026-09-01): this public demo uses test/sanitized data only.
  The general product may ingest exact data; when it detects that `origin` is
  public it warns before apply, but the user may persist a local,
  remote-specific acknowledgement to suppress repeats.
- Accepted (owner, 2026-09-01): preview is non-mutating and warning-free;
  `--apply` is explicit; the first apply to a detected public origin refuses
  until `--acknowledge-public-origin` records local, remote-specific consent.
- Accepted for the current conceptual model (owner, 2026-09-01): one repository
  portfolio may consolidate multiple accounts; holdings retain account +
  instrument identity; separately authored analytic positions may group
  multiple holdings or instruments. Physical representation remains open.
- Awaiting the human: inventory the recurring capabilities and user outcomes
  after broker reconciliation. Use them to validate or reject the remaining
  proposed data layers before discussing schemas or file layout.
- Weighed and unresolved: whether the existing ~3,000-token single-file packet
  remains the accepted UX or becomes one generated view among several.
- Deliberately not preserved: implementation choices before requirements and
  UX are accepted.

## External State And Risks

- The committed snapshot is sanitized and dated 2026-08-22; it must not be
  mistaken for current brokerage state during design or validation.
- Position files are mostly skeletons with missing theses, criteria, dates,
  and factor assignments. The UX must distinguish absent knowledge from a
  valid empty value.
- Provider keys are irrelevant to this deterministic workstream and must not
  become a dependency.

## Local Document Index

- [Requirements and UX discovery](requirements-and-ux.md)
- [Portfolio data contract discovery](data-contract.md)
- [Intake queue instructions](intake/README.md)
- [Intake disposition log](intake-dispositions.md)

## Next Resumable Task

Resume with a capability inventory: what questions the user expects answered,
what decisions the application should prepare, and what recurring maintenance
it should perform after reconciliation. Derive the remaining conceptual model
from those jobs, then return to timestamp semantics, blocking-error behavior,
and the human-versus-machine context-view question. Physical layout and coding
remain explicitly premature.
