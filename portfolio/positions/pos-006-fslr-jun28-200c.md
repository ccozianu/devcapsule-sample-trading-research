---
id: POS-006
ticker: FSLR
instrument: call
strike: 200
expiry: 2028-06-16
contracts: 1
entry_date: null          # unknown; recover from records when possible
basis_source: snapshot    # quantities, bases, marks live ONLY in data/snapshots/
status: open
regime: null              # practitioner-edge | generalist-macro — to be assigned
thesis: []
factor: []
kill_criteria: []         # TODO — must be evaluable from public observables
profit_criteria: []       # TODO — mandatory per INFORMATION_MODEL 4.1
override_protocol: >
  Acting against a fired criterion, or exiting with none fired, requires a
  decisions/ entry citing this ID and explicit reasons, scoreable in evals/.
reviews: []
month_18: null            # set once entry_date is known (18/6 rule)
---

FSLR JUN 16 2028 $200 CALL.

Seeded from `data/snapshots/portfolio-2026-08-22.csv`. Thesis summary, known
weaknesses, and kill/profit criteria are not yet written; this position file
is a skeleton awaiting its first review debate.
