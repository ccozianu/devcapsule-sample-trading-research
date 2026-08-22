# Decisions — human-only

No engine or tool ever writes here. One file per decision:
`YYYY-MM-DD-<slug>.md`, frontmatter per INFORMATION_MODEL §4.5:

```yaml
date: YYYY-MM-DD
positions: [POS-xxx, ...]
action: what was done, concretely
basis: criterion-fired | override | reallocation
criterion_ref: null        # required if basis is criterion-fired or override
arrival_order: thesis-before-trade | trade-before-thesis
alternatives_considered: [...]
tradeoffs_acknowledged:
  - ...
engines_consulted: [debate transcript refs]
```

Standing rule (from the NFLX episode): no position is closed
"discretionarily." Every close states which applies: (a) a criterion fired,
(b) an override with reasons, or (c) a reallocation with named destination
and the comparison written down.

Known backlog: the standing acceptance for the quantum-race basket
(`factors/quantum-race.md`) requires its decision entry.
