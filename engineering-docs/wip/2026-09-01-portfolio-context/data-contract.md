# Portfolio Data Contract — Discovery

Status: conceptual proposal for owner review; not an accepted schema or
storage design.

## Why This Contract Exists

The portfolio functionality must not turn a parseable broker export into
false knowledge. A broker positions CSV is a dated observation of holdings,
not a transaction ledger, investment thesis, decision history, or complete
explanation of how the account changed. Every downstream capability must be
able to distinguish observed facts, human-authored meaning, unresolved
reconciliation, and generated views.

## Proposed Data Layers

1. **Source artifact** — the exact raw broker export, transient and private.
   It supplies bytes and provenance but never becomes committed portfolio
   knowledge.
2. **Import observation** — immutable metadata about the source: content
   fingerprint, broker/adapter, account identity or alias, broker observation
   time when available, download/import time, schema version, and parse
   diagnostics.
3. **Normalized holding snapshot** — broker-observed account state in a stable
   broker-neutral vocabulary. It contains instruments, quantities, basis,
   marks, cash, and source-field provenance without inferred intent.
4. **Identity registry** — stable identities for accounts and instruments, and
   explicit mappings from broker symbols. Identity is not guessed from display
   descriptions when the symbol is ambiguous.
5. **Reconciliation** — the classified difference between accepted snapshots,
   including unresolved mappings and explanations. It records observations
   such as “quantity changed” without fabricating “bought,” “sold,” or
   “rolled.”
6. **Authored portfolio knowledge** — analytic positions, theses, criteria,
   factors, disputes, observations, and human decisions. These interpret
   broker reality and have their own authority and provenance.
7. **Generated views** — `CONTEXT.md`, terminal digests, and reports. They are
   reproducible projections, never independent sources of truth.

The direction of authority is one-way: source → observation → normalized
snapshot → reconciliation; authored knowledge refers to those facts; generated
views project them. A generated view must never be parsed back as canonical
input.

## Proposed Core Distinctions

- **Instrument:** a security or contract independent of any account or thesis,
  such as GOOG common stock or one specific OCC option contract.
- **Holding:** an account's observed ownership of an instrument at a snapshot
  time. The same instrument in two accounts is two holdings.
- **Lot:** an acquisition-level subdivision only when the broker source
  actually supplies reliable lot data. A positions export must not invent
  lots.
- **Analytic position:** the human's decision-relevant grouping. It may map to
  one holding, combine the same instrument across accounts, combine multiple
  option legs, or link a roll lineage. This relationship is authored or
  confirmed, not inferred from a CSV delta.
- **Portfolio:** the repository-level decision context containing one or more
  accounts and analytic positions.

This separation exposes a weakness in the current skeleton: `POS-nnn` mostly
means one broker row today. Treat that as seed data, not proof that holding and
analytic-position identity should remain the same concept.

## Proposed Anti-GIGO Invariants

### Provenance and time

- Preserve the raw source fingerprint and original row/field location for
  every normalized broker fact.
- Keep distinct timestamps for broker observation, file acquisition, import,
  and apply. Never substitute one silently for another.
- A mark without a trustworthy as-of time is stale/unknown, not “current.”
- Corrections supersede immutable observations; they do not rewrite history.

### Value semantics

- `0`, unknown, absent from export, not applicable, and failed-to-parse are
  different states.
- Currency and units are explicit. Options distinguish contracts, shares per
  contract, per-share prices, and total market value.
- Signed quantity and option type are normalized without relying on display
  description text alone.
- Derived values identify their formula and inputs; they are never mistaken
  for independently reported broker facts.

### Identity and reconciliation

- Account identity remains part of a holding key even if account labels are
  sanitized.
- Instruments use type-appropriate stable identity: a ticker alone is not
  sufficient for options, renamed securities, or corporate actions.
- Ambiguous identity blocks automatic mapping; it does not select the nearest
  string.
- A positions snapshot can establish presence or absence in that export, not
  the transaction or intention that caused the change.
- Same-file re-import is idempotent; out-of-order snapshots are preserved but
  never silently made current.

### Validation and usability

- Validation reports separately: parse failures, violated accounting
  invariants, implausible cross-snapshot changes, missing knowledge, and stale
  data.
- Blocking errors prevent apply; warnings may apply only when the resulting
  uncertainty remains explicit and visible in context.
- No normalizer silently drops an unrecognized row or column. Unsupported data
  is reported with source location and retained in diagnostics.
- A generated context packet must disclose snapshot freshness, unresolved
  reconciliation, and material missing knowledge before presenting analysis.

## First Decision: Account And Position Granularity

Recommended contract:

- One repository portfolio may contain **multiple brokerage accounts**.
- The normalized snapshot preserves holdings at **account + instrument**
  granularity, optionally lot-level only when supplied.
- Human-authored analytic positions may group holdings across accounts or
  instruments, but every grouping is explicit and traceable.
- v0 may parse Fidelity only, but the normalized contract must not encode
  Fidelity column names or semantics as the domain model.

This costs more than treating every CSV row as a `POS-nnn`, but it prevents
account aggregation, option strategies, transfers, and rolls from becoming
irrecoverably ambiguous later.

## Questions For The Owner

1. Should one repository represent a consolidated portfolio across multiple
   brokerage accounts, while preserving account membership as recommended?
2. Should an analytic position be allowed to group multiple instruments (for
   example an option spread or stock-plus-hedge), or should v0 require one
   instrument per position and add strategies later?
3. Is account-level tax treatment (taxable, IRA, margin, etc.) decision-relevant
   context in v0, or merely broker metadata retained for future use?
4. Do we explicitly defer transaction-history and tax-lot ingestion, treating
   state transitions as unexplained unless the user supplies confirmation?
