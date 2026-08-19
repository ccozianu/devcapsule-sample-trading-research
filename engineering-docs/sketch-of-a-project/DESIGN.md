                  1,1           Top

# Rotated-Debate Consensus Pipeline — Design & Intent

> **Purpose of this document.** This is a handoff brief written to carry a browser-based
> design discussion into a proper development effort (Claude Code / CLI). It captures the
> *intent*, the *design as settled*, and — critically — the *reasoning and the rejected
> alternatives*, so that whoever picks this up (human or a fresh Claude instance) does not
> relitigate settled questions or accidentally discard a load-bearing constraint.
>
> Status: design converged, not yet implemented. Companion file:
> `consensus_pipeline_pseudocode.py`.

---

## 1. What we are building (one paragraph)

A system that improves the reliability of answers shown to a human by submitting a question
to **N independent LLM engines** (default N=3), running them through a **bounded, role-rotated
debate**, and then adjudicating the result with a **deterministic, LLM-free merge**. The output
is not a single forced answer but an **honestly reported epistemic state** — full convergence,
majority (2-of-3), or divergence — with the entire back-and-forth preserved and available to
the user or a downstream reasoning model. The intent is *calibrated reliability*, not the
illusion of authority.

## 2. Why it exists / the problem

A single LLM gives you one model's blind spots, biases, and hallucinations with no
cross-check. The obvious fix — ask several models and take a majority vote — is weaker than
it looks, for reasons that shaped this entire design (see §4). The goal is to capture the
genuine value of multi-model cross-examination **without** inheriting the failure modes of
naïve voting or of an LLM "chairman" that re-introduces a single point of unauditable
judgment.

## 3. The core idea (what makes this different from prior art)

Existing open-source systems already do multi-model answer→critique→synthesize. They all
end in an **LLM aggregator**. Our distinguishing commitments:

1. **The final adjudication is deterministic.** No LLM in the merge step. The merge only
   tallies verdicts over a shared claim-id namespace. It is auditable and reproducible.
2. **Adjudication happens at the level of atomic claims, not whole answers.** You cannot
   "vote" on three paragraphs of prose; you can vote on decomposed, individually checkable
   assertions.
3. **The output reports a state, not a number.** Converged / majority / diverged are
   surfaced honestly. We never relabel "the models agreed" as "the answer is correct."
4. **An LLM still does the hard semantic work** — answering, critiquing, and synthesizing
   disputes — because that is what LLMs are good at. We split the labor: **LLMs reconcile
   language; deterministic code renders the verdict.**

### Relationship to prior art (do not rebuild the orchestration)
- **Karpathy `llm-council`** (open source, OpenRouter-based): answer → anonymized peer
  review/ranking → **LLM chairman** synthesis. This is almost exactly our *flow*. Clone it
  to see the loop working, then **replace the chairman with our deterministic merge.** It is
  explicitly an unsupported "weekend hack," so treat it as reference, not dependency.
- **Together `Mixture-of-Agents` (MoA)**: layered proposers → **LLM aggregator**. Same
  structural shape, benchmarked, also an LLM merge.
- **`swarms`, `AgentVerse`**: ship MixtureOfAgents-style aggregator-agent patterns.
- **Access layer:** build on **OpenRouter** for multi-vendor access rather than wiring three
  vendor SDKs.
- **Supporting literature:** "Beyond Majority Voting" (higher-order aggregation beats naïve
  majority vote in the large majority of ensembles tested) and "The Consensus Trap"
  (response-level voting collapses under correlated/contextual corruption). Both validate the
  decision to move below the whole-answer level and to treat unanimity with suspicion.

**The gap we fill:** no existing open-source tool does deterministic, LLM-free aggregation
over **atomically decomposed claims with cross-model claim-id referencing** and explicit
**contested-vs-consensus spread-surfacing**. That is the contribution.

## 4. Decisions and the reasoning (the part that's easy to lose)

These are tagged `[D1]`–`[D5]` in the pseudocode. Each includes the alternative we rejected.

- **[D1] Shared, canonical claim-id namespace, fixed in Stage 0.**
  Every later stage references claims *by id*. This is what keeps the merge deterministic.
  *Rejected alternative:* matching claims across models with embeddings/fuzzy similarity at
  merge time — reintroduces exactly the stochastic judgment we are trying to remove from the
  final step.

- **[D2] Only contested claims enter the debate machinery (divergence gate).**
  Most of a typical answer is uncontested; it flows straight to consensus. The expensive
  debate path runs only on claims where engines actually disagree or coverage is incomplete.
  This is the primary cost lever.

- **[D3] Per-engine "collapse" step before the deterministic merge.**
  After debate, **each engine emits one final claim-structured position.** The merge then runs
  over **N engine-positions**, which maps cleanly onto converged / 2-of-3 / diverged.
  *Why this is non-negotiable:* the six per-permutation syntheses are mutually contaminated
  (each already blends all engines' views) and, post-debate, deliberately less independent
  than they started. Running a "2-of-3" statistic directly over six non-independent,
  non-comparable artifacts is statistically meaningless. The syntheses demote to
  transcript/evidence; they are **not** merge inputs.

- **[D4] Convergence is a *reported state*, never a confidence or correctness score.**
  Multi-agent debate manufactures agreement regardless of truth — weaker models tend to
  capitulate to more confident framing. So we additionally **instrument who changed their
  mind and whether they gave a reason**: a concession backed by new evidence is
  error-correction; a reason-less concession is capitulation (agreeableness drift). The
  transcript already contains this signal; we surface it rather than hide it.

- **[D5] Debate depth capped (default 1 round).**
  More rounds drive more convergence *and* more **false** convergence. Round-1-then-stop is
  the default; only the narrow set of still-contested claims should ever justify a further
  round.

### A note on N (don't silently assume it's safe at 3)
At N=3 the role rotation buys **fairness** (every engine plays answerer, critic, and
synthesizer, cancelling identity and position bias) but **not synthesis redundancy** — each
dispute is synthesized exactly once by the single remaining engine. If you want the same
dispute adjudicated by more than one engine, you need **N ≥ 4**. Document this wherever N is
configured; it's an easy thing to get wrong.

### Terminology correction carried over from the discussion
The original worry was "infinite recursion." That was a misnomer — the pipeline is a
**bounded DAG** (answer → critique → rebuttal → synthesis → collapse → merge) that terminates
at fixed depth. The real constraint is narrower and should be stated as such: **no LLM in the
final merge step.** Generation, critique, and synthesis are *necessarily* LLM steps; only
aggregation/display is deterministic.

## 5. Pipeline (as settled)

```
Stage 0   independent answers (parallel)  ->  decompose to atomic claims
          ->  assign canonical ids  ->  deterministic divergence gate
                |
                |  (only CONTESTED claims continue)
                v
Round 1   rotated debate over contested claims:
          for each ordered role triple (answerer, critic, synthesizer):
              critique  ->  one rebuttal (answerer sees that critic; logs concessions)
              ->  synthesis of the (answerer, critic) dispute by the third engine
          N=3 -> 6 permutations.  Reuse memoizes identical sub-calls.
                |
                v
Collapse  each ENGINE reads the full transcript and emits ONE final
          claim-structured position (verdict per contested id)        [D3]
                |
                v
Round 2   DETERMINISTIC merge (no LLM): tally engine-positions by id
          ->  per-claim status: CONVERGED / MAJORITY / DIVERGED
          ->  fold uncontested Stage-0 claims into consensus
                |
                v
Output    status banner (honest state)  +  user-selected view
          (synthesized | full debate)  +  always-attached transcript,
          per-claim status, and capitulation-vs-reasoned-concession log
```

### Cost envelope (so this is entered eyes-open)
With reuse at N=3, Round 1 is ≈ 3 reused answers + 6 critiques + 6 rebuttals + 6 syntheses,
plus 3 for collapse ≈ **~24 LLM calls**, on a 4-deep sequential dependency chain that limits
parallel speedup. That's roughly **3–5× `llm-council`** and **~5× MoA**. This is a
**high-assurance mode, not a default**. The divergence gate ([D2]) is what keeps it
affordable: only genuinely contested claims pay the full price.

## 6. Interface contracts (summary; full shapes in the pseudocode)

- **Claim**: `{id, text, type(FACT|JUDGMENT|RECOMMENDATION|DEFINITION), verdict(ASSERT|DENY|UNCERTAIN), confidence, evidence[], origin_engine}`. Atomicity rule is load-bearing: **one checkable idea per claim.**
- **Critique assessment**: references a peer claim **by id**; `{claim_ref, stance(AGREE|DISAGREE|PARTIAL|CANNOT_VERIFY), confidence, rationale, proposed_correction?}`.
- **Rebuttal**: `{revised verdicts, concessions[{claim_id, conceded, reason|null}]}` — `reason: null` ⇒ capitulation.
- **EnginePosition** (collapse output): `{engine, verdicts: {claim_id -> {verdict, confidence, rationale}}}`.
- **MergeResult**: `{per_claim_status, consensus[], majority[](records dissenter), contested[](full spread), transcript, metrics}`.
- **Validation**: strict schema check, one structured-repair retry, then drop the engine
  (and surface degraded quorum in metrics). **Never let prose leak into the merge.**

## 7. Failure modes to design against (carry these into tests)

1. **Correlated errors.** Frontier models share corpora/architecture/RLHF lineage; they are
   often wrong *together*. Unanimity is therefore a **yellow flag for correlated error**, not
   a green light. (Concrete example from the originating conversation: an over-optimistic
   claim about a drug class that multiple models would plausibly share.)
2. **Manufactured convergence / capitulation** — see [D4]. Instrument it; don't trust it.
3. **Quorum degradation.** If one engine returns invalid JSON and is dropped, "2-of-3"
   silently becomes "2-of-2 = unanimity." Decide behavior explicitly and surface it.
4. **Judgment masquerading as fact.** `type=JUDGMENT` claims must **never** be auto-voted into
   a single answer; emit the spread. (The motivating example: "is radiation *standard*?" —
   legitimately depends on context; collapsing it to one verdict is a bug, not a feature.)
5. **Determinism vs. diversity tension.** Temperature 0 gives reproducibility but kills the
   answer diversity that makes cross-examination meaningful. Prefer low-but-nonzero generation
   temperature (or pinned seeds where the vendor allows) and accept the trade.

## 8. How we'll know it works (build this first)

The headline metric is **not** task accuracy — it is **calibration of the convergence
signal**: when the system reports CONVERGED, how often is the answer actually correct? If
"3/3" is not calibrated to truth, the convergence display is theater and the single best model
is the better product.

Eval harness should report, against a labeled set:
- calibration curve: `P(correct | CONVERGED)`, `P(correct | MAJORITY)`, `P(correct | DIVERGED)`
- capitulation rate, and the accuracy delta when capitulations are excluded
- head-to-head vs **single-best-model**, **llm-council chairman**, and **flat majority vote**
- cost (LLM calls) per item

**Build the harness before the debate machinery.** If the convergence signal doesn't
calibrate, nothing downstream earns its cost.

## 9. Suggested build order (for the Claude Code phase)

1. **Eval harness + labeled fixtures + baselines** (single-best, flat-majority). Establish the
   measuring stick first.
2. **Stage 0**: parallel answers, claim decomposition, canonical id registry, divergence gate.
   This alone, plus the deterministic merge over Stage-0 positions, is a shippable v0 (no
   debate yet) and already beats flat voting on the contested subset.
3. **Deterministic merge + `classify()`** with the `tau` downgrade rule.
4. **Collapse step** (per-engine final position).
5. **Round-1 rotated debate** with memoized reuse. Add last; it's the most expensive and the
   least certain to pay off — measure it against the v0 baseline before trusting it.
6. **Prompt templates** for critique / rebuttal / synthesis / collapse (iterate against real
   OpenRouter calls; these will need tuning).
7. **`register_new_claims()`** — claims raised mid-debate. The fiddliest deterministic piece;
   prototype in isolation. Alignment of new claims still rides the `claim_ref`-by-id mechanism.

## 10. Open questions / not yet decided

- Exact normalization for canonical id assignment (idempotent hash of normalized claim text vs.
  a registered running id with an explicit dedup pass).
- Per-engine weighting in `classify()` (flat vote vs. up-weighting a domain specialist). Left
  as a config knob; default flat. Revisit only if calibration data justifies it.
- Whether `JUDGMENT`-type claims get a *structured spread schema* of their own rather than
  being lumped into "contested."
- Anonymization of authorship during critique (llm-council does this to cut identity bias) —
  likely worth adopting; not yet integrated into the contracts above.