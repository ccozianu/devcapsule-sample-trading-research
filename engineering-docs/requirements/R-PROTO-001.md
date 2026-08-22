# R-PROTO-001: Rotated-Debate Protocol as a Standalone Package

Statement: The rotated-debate protocol — ANSWERER answers a prompt, CRITIC
finds faults and counterarguments, the two exchange bounded rebuttals, and a
SYNTHESIZER produces the synthesis, with N engines rotating through the roles
to yield 3–6 independent syntheses depending on the user's token budget —
must be delivered as a domain-agnostic Python package usable on arbitrary
questions (e.g., a medical question), independent of the portfolio
application. Role rotation must accept per-topic constraints so that an
engine conflicted on a topic (per the routing table) never holds the
synthesizer role for it. The debate outcome is reported honestly as an
observed epistemic state, never as confidence or correctness.

Priority: MVP
Status: accepted

Implementation:
- Not yet started; the deterministic primitives in `src/rotated_consensus/`
  predate this record and remain the comparison baseline.

Validation:
- Deferred: per the pudding principle (session record S2), the protocol is
  declared successful only after satisfying results on real portfolio
  positions (see R-ACCEPT-001).

Related:
- `engineering-docs/session-records/2026-08-22-vision-interview.md` (S2, S7)
- `engineering-docs/sketch-of-a-project/DESIGN.md`
- `engineering-docs/design-notes/open-q-convergence-declaration.md` (OQ-1:
  who declares convergence is deliberately deferred)
