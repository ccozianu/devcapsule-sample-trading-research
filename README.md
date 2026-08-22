# Rotated-Debate Portfolio Research

**What this is, in one paragraph.** A demo project showing how a developer and
multiple LLMs together manage knowledge and make timely decisions about real
stock and option positions. It is built from **two equal, co-developed
halves**: (1) a domain-agnostic **rotated-debate protocol** — for any prompt,
one LLM answers, a second criticizes, they exchange bounded rebuttals, and a
third synthesizes; rotating N engines through the ANSWERER / CRITIC /
SYNTHESIZER roles yields 3–6 independent syntheses, and the outcome is
reported honestly as converged or diverged; and (2) a **portfolio
application** that uses the protocol to maintain a living, auditable
knowledge repository about the positions in a (sanitized) real brokerage
portfolio. This repository *is* that knowledge repository: the demo dataset,
the debates, the decisions, and the code all live here together.

**What this is not.** Not a trading bot, not investment advice, not a product
with a polished UI. The user interface is deliberately an IDE: Markdown files
are read and written, Python commands are run from a terminal. Commands
mutate knowledge state; tests only verify. Agreement between engines is
reported as an **observed state, never as confidence or correctness** — and
returns are explicitly **not** the success metric (see Acceptance below).

## The loop

```
 portfolio repo state (positions, theses, criteria, calendar, disputes)
        │
        ▼
 generated context packet (one read, token-budgeted)
        │
        ▼
 rotated debate on a live question          ┌─ daily: knowledge-refresh
 (ANSWERER / CRITIC / SYNTHESIZER,          │  debate over intervening news,
  roles rotate across engines;              │  all engines, browsing enabled
  conflicted engines never synthesize       └─ on demand / on calendar or
  their own maker's topics)                    threshold triggers
        │
        ▼
 structured write-back: claims → evals ledger, disagreements → disputes,
 concessions logged (reasoned vs. capitulation)
        │
        ▼
 the HUMAN alone writes the decision log; time passes; calendar and
 market events fire; the next debate starts from the updated state
```

Opinions are expected to be **time-varying and scoreable after the fact**:
registered claims carry resolution dates, get scored when reality arrives,
and an engine repeating another's unverified estimate is marked as adopted,
never as independent confirmation.

## Acceptance ("the pudding")

Portfolio returns are rejected as the success metric — single-period returns
are luck-confounded. The demo is accepted **reflexively**: the human user is
happy, *and* the engines — debating over this repo's own accumulated,
scoreable usage records (resolved predictions, disputes settled by
observables, criteria that fired before outcomes) — converge that the setup
acceptably helps a real user gain knowledge about the positions they hold.
That acceptance debate may not be convened before **two months of live usage
crossing at least one earnings season**. Because the human triggers it only
when provisionally satisfied, its real job is to veto false satisfaction.

## Where the authority lives

Read these in order; they are deliberately non-overlapping:

1. `engineering-docs/session-records/2026-08-22-vision-interview.md` —
   **the authoritative statement of the project**: settled decisions S1–S9
   and open questions OQ-1–OQ-5.
2. `engineering-docs/sketch-of-a-project/INFORMATION_MODEL.md` — the
   portfolio knowledge substrate: schemas for positions, theses, factors,
   calendar, decisions, disputes, evals, routing, observations.
3. `engineering-docs/sketch-of-a-project/DESIGN.md` — the debate
   micro-structure and its rationale. One caveat: its claim that final
   adjudication is LLM-free is **deliberately contested and deferred**, see
   `engineering-docs/design-notes/open-q-convergence-declaration.md`.
4. `REQUIREMENTS.md` — the requirements register and index.

The sanitized demo portfolio lives at `data/snapshots/` (format documented
there). Raw brokerage exports are never committed: sanitize, then delete.

## Development

Requires Python 3.12 or newer. Bootstrap a repository-local developer
environment; do not install the toolchain into the global Python environment:

```bash
python3.12 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -r dev-requirements.txt
```

Nox provides the development commands and creates an isolated environment for
each task:

```bash
nox                 # tests, compilation check, and lint
nox -s tests        # unit tests only
nox -s build        # wheel and source distribution in dist/
```

`setuptools.build_meta` remains the PEP 517 package build backend; Nox invokes
that backend through `python -m build`. The package uses a `src/` layout.
Provider adapters, prompts, credentials, and network calls do not belong in the
deterministic domain, merge, or evaluation modules. Engine access is
provider-flexible by design; the engine lineup is Claude, Gemini, and ChatGPT,
and API keys are injected by the owner, never committed.

## License

Repository-authored code and documentation are licensed under the
[Apache License 2.0](LICENSE). Externally sourced evaluation fixtures retain
their source licenses and must record their provenance and redistribution terms.

## Project Status

The open-workstream registry lives in
[`CURRENT-STATUS.md`](CURRENT-STATUS.md). Detailed handoffs and planned next
tasks live under `engineering-docs/wip/`. The reusable collaboration protocol
lives separately in [`WORKFLOW.md`](WORKFLOW.md).
