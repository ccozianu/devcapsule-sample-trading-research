# Portfolio Repository — Information Model v0.1

**Purpose.** Make any engine (Claude / Gemini / ChatGPT) maximally effective in a
portfolio-decision conversation with near-zero context reconstruction, and make
every claim, prediction, and decision scoreable after the fact.

**Origin.** Drafted 2026-08-20 from one month of live sessions. Every element
below exists because its absence cost us something concrete (a wasted retrieval,
a relitigated concession, an unfalsifiable claim, an unlogged override).

---

## 1. Design principles

1. **Everything dated, everything tiered.** No claim enters the repo without a
   date and an evidence tier (T1 audited/filed, T2 credibly reported,
   T3 posited/modeled/practitioner-observed). Tier-laundering is a schema
   violation, not just a debate foul.
2. **Machine front, human body.** Every file: YAML frontmatter for what engines
   must parse reliably (criteria, dates, status, links), prose for reasoning.
   Engines read frontmatter as ground truth; prose as argument.
3. **Generated vs. authored, hard separation.** Generated blocks are fenced
   (`BEGIN/END GENERATED`) and never hand-edited (existing rule — keep it).
   `decisions/` stays human-only (existing rule — keep it).
4. **One source of truth per fact.** Basis, quantity, marks live only in the
   snapshot. Criteria live only in position files. Everything else links.
   Duplication is how the SMCI-as-active error class happens.
5. **Criteria must be evaluable from public observables.** A kill criterion an
   engine can't check against a filing, a dated announcement, or a price is a
   sentiment, not a criterion.
6. **Arrival-order metadata.** Decisions record whether the supporting thesis
   was written *before* or *after* the trade idea. This is the cheapest
   structural defense against conclusion-first reasoning, and it fired twice
   this week.
7. **Context fits in one read.** A generated `CONTEXT.md` under a fixed token
   budget is the entry point for every session. If it doesn't fit, the model is
   too fat, not the budget too small.

---

## 2. Directory layout

```
repo/
├── CONTEXT.md              # GENERATED — session entry point (see §5)
├── AGENTS.md               # engine roles, debate protocol (exists)
├── WORKFLOW.md             # cadences, sweep checklist (exists)
├── ROUTING.md              # conflict-of-interest routing table (see §4.8)
├── DISPUTES.md             # open inter-engine disagreements (see §4.7)
├── data/snapshots/         # Fidelity CSVs + generated snapshot tables (exists)
├── positions/              # one file per instrument (see §4.1)
├── theses/                 # one file per thesis, claim-graph body (see §4.2)
├── factors/                # factor definitions + standing acceptances (see §4.3)
├── calendar/               # dated external events wired to criteria (see §4.4)
├── decisions/              # human-only decision log (see §4.5)
├── debates/                # engine transcripts, frontmattered (exists)
├── evals/                  # prediction ledger + scoring (see §4.6)
├── observations/           # practitioner observations, dated T3 (see §4.9)
└── tools/                  # ingest_fidelity.py, build_context.py, check_calendar.py
```

---

## 3. The three questions every session actually needs answered

A month of sessions reduces to three recurring information needs. The model is
organized so each is answerable from one file:

1. **"What is the current state?"** → snapshot + `CONTEXT.md`
   (positions, basis, marks, % of premium, expiry clusters, factor loads).
2. **"What did we already commit to?"** → position frontmatter + `decisions/`
   (criteria verbatim, standing acceptances, prior concessions — so nothing is
   relitigated and no engine re-derives what's settled).
3. **"What can change the answer, and when?"** → `calendar/` + falsifier fields
   (dated events wired to the specific criteria they can fire).

If a proposed schema element doesn't serve one of these, leave it out.

---

## 4. Schemas

### 4.1 Position file — `positions/pos-NNN-<slug>.md`

```yaml
id: POS-003
ticker: GOOG
instrument: call
strike: 300
expiry: 2028-12-15
contracts: 3
entry_date: 2026-08-XX
entry_price: null            # per share; snapshot holds live marks
basis_source: snapshot       # never duplicated here
status: open                 # open | closed | evaluated-not-entered
regime: generalist-macro     # practitioner-edge | generalist-macro
thesis: [TH-004]             # position may load on several theses
factor: [ai-capex]
supersedes: POS-00X          # for rolls: preserves lineage + P&L continuity
kill_criteria:
  - id: KC-1
    statement: >
      Cloud YoY growth < 55% AND capex guidance raised again in same or
      adjacent quarter, before 2026-12-31.
    observable: quarterly filing + guidance call
    check_on: [earnings:GOOG]
  - id: KC-2
    statement: >
      No decisive close above $410 by 2027-09-30.
    observable: price
    check_on: [monthly-sweep]
profit_criteria:             # MANDATORY — absence was a named gap (MU, GOOG)
  - id: PC-1
    statement: >
      Mark-to-market ≥ 2.0x basis with thesis intact → trim 50%, log rationale.
    observable: snapshot mark
override_protocol: >
  Acting against a fired criterion, or exiting with none fired, requires a
  decisions/ entry citing this ID and explicit reasons, scoreable in evals/.
reviews:
  - date: 2026-10-27         # next GOOG earnings
    trigger: earnings
month_18: 2027-XX-XX         # mandatory optionality-decision date (18/6 rule)
```

Body prose: thesis summary in three sentences, known weaknesses, and — for
rolls — what the roll bought and what it did not (e.g., "durability and 11
months; NOT a lower breakeven bar: expiry breakeven ~unchanged at ~$410").

**Rule from the NFLX exit:** a position may not be closed "discretionarily"
without a decision entry stating which of these applies: (a) criterion fired,
(b) override with reasons, (c) reallocation with named destination and the
comparison written down.

### 4.2 Thesis file — `theses/th-NNN-<slug>.md`

Theses are separate from positions (many-to-many). Body is a claim graph:

```yaml
id: TH-004
title: GOOG price-performance corridor
regime: generalist-macro
status: draft                # draft | registered | contradicted | resolved
registered: null             # date it became falsifiable; drafts can't size positions
arrival_order: after-trade   # before-trade | after-trade  ← honesty field
author_engine: human         # human | claude | gemini | chatgpt
coi_flags: [gemini:google, claude:anthropic]   # see ROUTING.md
claims:
  - id: C1
    statement: >
      Latency/cost is a first-class competitive dimension the market
      underweights relative to frontier-capability rankings.
    tier: T3
    falsifiers:
      - >
        By 2027-06-30, no T1/T2 evidence of enterprise procurement
        decisions citing cost/latency over capability.
    known_weakness: >
      Latency is weak evidence for unit cost (over-provisioning, routing,
      speculative decoding all confound it). Silicon/TPU integration is the
      defensible version.
  - id: C2
    statement: DeepMind reorg is net positive within 2–4 quarters.
    tier: T3
    falsifiers:
      - Gemini 3.5 Pro / 4 fails promised cadence through 2027-Q1.
      - Senior research departures cluster within 90 days of 2026-08-05.
    confirmers:
      - Flagship ships within defined benchmark band of GPT/Mythos class.
    monitoring: observations/ (practitioner channel, monthly)
shared_falsifiers: [hyperscaler-capex-deceleration]   # links to factors/
```

**Rules encoded from live failures:**
- A thesis whose original mechanism is contradicted (Gemini-parity edge) is
  marked `contradicted`; successor reasoning gets a **new** thesis file with its
  own regime tag. No inheritance of credibility or sizing (motte-and-bailey
  firewall, structural form).
- Every claim carries `tier` and at least one falsifier or it can't leave
  `draft`.

### 4.3 Factor file — `factors/<slug>.md`

```yaml
id: ai-capex
positions: [MU-jun28-400c, GOOG-jan28-350c, GOOG-dec28-250c,
            NVDA-dec28-180c, QCOM-jan28-125c]
beta_notes: NVDA highest-beta expression; circular-financing risk concentrates there.
shared_falsifiers:
  - hyperscaler capex deceleration (sequential guidance cuts across ≥2 majors)
standing_acceptance:
  decision: decisions/2026-08-XX-ai-concentration.md   # REQUIRED, currently missing
  ceiling: null      # e.g. "≤60% of premium"; reviewed quarterly
  review: quarterly
```

**Rule:** "willing to go to town" is legal only as a `standing_acceptance` with
a ceiling, a review date, and a human-signed decision entry. Then future
drawdowns are scored against a choice, not relitigated mid-selloff.

### 4.4 Calendar — `calendar/events.yaml`

The daily-sweep backbone. Each event is wired to what it can fire:

```yaml
- id: earnings:NVDA:2026Q2
  date: 2026-08-26            # verify
  type: earnings
  fires: [POS-nvda.KC-*, TH-ai-capex]
  notes: watch robotics→Edge Computing reclassification
- id: listing:AEM-jan29-leaps
  date: 2026-09-14
  type: market-structure
  fires: [decision:aem-entry]
  constraints: [no-entry-on-spike-IV, jan28-cluster]
- id: cadence:gemini-flagship
  date: 2026-11-30            # from public cadence promise; restate per news
  type: product
  fires: [TH-004.C2]
```

`tools/check_calendar.py` emits "what fires in the next N days" into
`CONTEXT.md`. This converts the daily sweep from memory to mechanism.

### 4.5 Decision entry — `decisions/YYYY-MM-DD-<slug>.md` (human-only)

```yaml
date: 2026-08-20
positions: [POS-001, POS-goog-350, POS-003]
action: close POS-001; roll 4x GOOG jan28-350c → 3x dec28-300c
basis: reallocation            # criterion-fired | override | reallocation
criterion_ref: null            # required if criterion-fired/override
arrival_order: trade-before-thesis   # be honest; it's scoreable, not shameful
alternatives_considered: [hold both, roll to dec28-320, close 350s outright]
tradeoffs_acknowledged:
  - AI-factor concentration rises; NFLX was non-factor exposure.
  - Expiry breakeven bar unchanged (~$410); bought time+delta, not a lower bar.
engines_consulted: [claude-critic 2026-08-19/20]
```

### 4.6 Evals ledger — `evals/ledger.yaml`

```yaml
- id: EV-2026-08-20-a
  engine: claude
  claim: "Reorg-positive thesis discriminates on shipping cadence by 2027-Q1"
  origin: original            # original | adopted-from:<engine>  ← convergence tracking
  tier_at_registration: T3
  resolves: 2027-03-31
  resolution: null
  score: null
```

`origin` exists specifically to catch convergence-by-adoption: an engine
repeating another's unverified estimate is `adopted-from`, and adopted claims
never count as independent confirmation.

### 4.7 Disputes — `DISPUTES.md`

One table: claim, engines' positions, tier of each, the observable that
resolves it, resolution date. (Current example: Anthropic share of GCP
revenue/backlog — disputed, resolves on any quantifying disclosure.)

### 4.8 Routing — `ROUTING.md` (conflict-of-interest table)

| Node | Recused engine | Reason | Route to |
|---|---|---|---|
| Anthropic viability, scale, "winning" | Claude | maker | Gemini + ChatGPT |
| Google/DeepMind internal state, Gemini quality, GOOG theses | **Gemini** | maker | Claude + ChatGPT |
| OpenAI IPO, finances, model claims | ChatGPT | maker | Claude + Gemini |
| Cross-lab comparisons (any pair) | both parties | parties | third engine + human T3 observation |

**Standing implication:** every engine in the triad is conflicted on one of the
three largest nodes in the AI thesis space. Synthesizer role for a name must
never be held by that name's conflicted engine. Historical note: a substantial
share of GOOG debate history ran through Gemini — re-weight accordingly when
citing it.

### 4.9 Observations — `observations/YYYY-MM.md`

Dated, T3, first-person practitioner readings ("Gemini latency vs. Fable 5 on
task class X, 2026-08-20: ..."). These are the raw material of interpretive
edge — the 170 GOOG entry came from exactly this channel. Logging them makes
the next edge claim *provable in advance* instead of narrated in hindsight,
and feeds TH-004.C2's monitoring channel.

---

## 5. CONTEXT.md — the generated session packet

Built by `tools/build_context.py`; target ≤ ~3,000 tokens. Contents, in order:

1. **Snapshot digest** (generated): positions, basis, mark, %-of-premium,
   factor, expiry; expiry-cluster table; concentration vs. standing ceilings.
   Freshness stamp of underlying CSV.
2. **Open criteria** verbatim (kill + profit), each with next check date.
3. **Next 30 days** from calendar, with what each event can fire.
4. **Open disputes** (one line each).
5. **Active decisions pending** (e.g., "GOOG roll decided 2026-08-20, awaiting
   execution; AEM entry gated on 2026-09-14 listing").
6. **Settled matters** — one-liners of concessions/conclusions no engine should
   relitigate ("SMCI never entered"; "350s' pathway = exit-or-roll, drafted
   2026-07-22"; "AI-concentration accepted per decision X").
7. **Routing reminders** relevant to today's topic.

Session protocol: paste `CONTEXT.md` (or have the engine read it) as message
one. Engines cite element IDs (POS-003.KC-1, TH-004.C2) instead of prose
paraphrase — IDs are what make the evals ledger joinable.

---

## 6. Gap list — fill in this order

1. **Profit-exit criteria for MU and both GOOG positions** (flagged 2026-08-05;
   still missing; the NFLX episode shows exits without criteria default to mood).
2. **`decisions/` entry for the AI-concentration standing acceptance**, with a
   numeric ceiling ("go to town" → a number).
3. **NFLX close + GOOG roll decision entry** using §4.5, including
   `arrival_order` honestly.
4. **TH-004 (corridor + reorg thesis) as a fresh registration**, generalist
   regime, after one outside-engine Critic pass (per ROUTING.md, that pass is
   ChatGPT, not Gemini).
5. **`ROUTING.md`** — small file, large standing value.
6. **`calendar/events.yaml`** seeded with: NVDA earnings, AEM Jan-29 listing,
   GOOG Oct 27 earnings, Gemini cadence checkpoints, month-18 dates for every
   open position.
7. Backfill `evals/` with this month's already-made engine predictions before
   they're forgotten (ATH-recovery verdicts of 2026-08-05 are scoreable).

---

## 7. What this buys, concretely

- Retrieval cost → one file read (today burned four tool calls reconstructing it).
- Relitigation → impossible by default (settled matters travel in the packet).
- Sycophancy → harder (criteria verbatim in-context beat vibes; overrides leave scars in evals).
- Motte-and-bailey → structural firewall (contradicted theses die; successors re-register).
- Convergence-by-adoption → visible (`origin` field).
- Conflict routing → mechanical, symmetric, and no longer dependent on anyone remembering.
- Your interpretive edge → pre-logged and therefore claimable, instead of retrofitted.