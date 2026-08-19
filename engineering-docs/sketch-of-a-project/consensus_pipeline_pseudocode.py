"""
================================================================================
ROTATED-DEBATE CONSENSUS PIPELINE  —  PSEUDOCODE (not runnable)
================================================================================
Goal: improve answer reliability by running N engines through a bounded debate,
then adjudicating with a DETERMINISTIC merge (no LLM in the final step).

Division of labor (the core idea):
  - LLMs do what they're good at: answering, critiquing, and synthesizing
    natural-language disputes.
  - The FINAL adjudication is deterministic and auditable: it only tallies
    verdicts over a shared claim-id namespace. No LLM "chairman".

Key design decisions, flagged inline as [D#]:
  [D1] Claims carry a shared, canonical id namespace fixed in Stage 0 so that
       every later stage can be aligned BY ID — no embedding/fuzzy matching,
       which is what keeps the merge deterministic.
  [D2] Only CONTESTED claims enter the debate machinery (cost lever). Most of a
       typical answer is uncontested and bypasses the expensive path.
  [D3] Before the deterministic merge, each ENGINE collapses to ONE final
       claim-structured position. The merge runs over N engine-positions
       (maps cleanly to converged / majority / diverged). The 6 per-permutation
       syntheses are transcript+evidence, NOT merge inputs.
  [D4] "Convergence" is a REPORTED STATE, never a confidence/correctness score.
       Debate manufactures agreement regardless of truth, so we also instrument
       WHO conceded and WHETHER they gave a reason (concession vs capitulation).
  [D5] Debate depth is capped (default 1 round). More rounds => more convergence
       AND more FALSE convergence.

NOTE on N: at N=3 the role rotation buys fairness (every engine plays every
role) but NOT synthesis redundancy — each dispute is synthesized exactly once
by the single remaining engine. For redundant synthesis (same dispute judged by
>1 engine), use N >= 4.
================================================================================
"""

from itertools import permutations
from math import ceil

# ------------------------------------------------------------------------------
# TYPES
# ------------------------------------------------------------------------------

EngineId = str          # e.g. "gpt", "claude", "gemini"
ClaimId  = str          # canonical, stable across all stages  [D1]

enum Verdict       = { ASSERT, DENY, UNCERTAIN }
enum ClaimType     = { FACT, JUDGMENT, RECOMMENDATION, DEFINITION }
enum ClaimStatus   = { CONVERGED, MAJORITY, DIVERGED, UNCONTESTED }
enum Stance        = { AGREE, DISAGREE, PARTIAL, CANNOT_VERIFY }

struct Claim:
    id: ClaimId
    text: str                       # one atomic, checkable assertion
    type: ClaimType
    verdict: Verdict
    confidence: float               # self-reported; treat skeptically
    evidence: list[Evidence]
    origin_engine: EngineId

struct Evidence:
    source: str                     # url | doc id
    locator: str                    # page / line / span

struct ClaimRegistry:
    """Append-only canonical claim namespace.  [D1]"""
    claims: dict[ClaimId, Claim]
    contested_ids: set[ClaimId]     # filled by the Stage-0 divergence gate  [D2]

    def register(self, claim) -> ClaimId:
        # deterministic id assignment (hash of normalized text, or running int)
        # idempotent: identical normalized text -> same id
        ...

struct EnginePosition:
    """An engine's FINAL stance after debate — one verdict per contested id. [D3]"""
    engine: EngineId
    verdicts: dict[ClaimId, ClaimVerdict]

struct ClaimVerdict:
    verdict: Verdict
    confidence: float
    rationale: str

struct Critique:
    critic: EngineId
    target: EngineId                       # whose answer is being critiqued
    assessments: list[Assessment]

struct Assessment:
    claim_ref: ClaimId                     # references shared namespace  [D1]
    stance: Stance
    confidence: float
    rationale: str
    proposed_correction: Claim | None      # may register a NEW claim

struct Rebuttal:
    answerer: EngineId
    saw_critic: EngineId
    revised: dict[ClaimId, ClaimVerdict]
    concessions: list[Concession]          # instrumentation for [D4]

struct Concession:
    claim_id: ClaimId
    conceded: bool
    reason: str | None                     # None  => CAPITULATION (no reason)
                                           # text  => reasoned concession

struct Synthesis:
    synthesizer: EngineId
    dispute: tuple[EngineId, EngineId]     # (answerer, critic)
    resolved_view: dict[ClaimId, ClaimVerdict]
    still_contested: set[ClaimId]

struct DebateRecord:
    answerer: EngineId
    critic: EngineId
    synthesizer: EngineId
    critique: Critique
    rebuttal: Rebuttal
    synthesis: Synthesis

struct MergeResult:
    per_claim_status: dict[ClaimId, ClaimStatus]
    consensus: list[Claim]                 # CONVERGED + UNCONTESTED
    majority:  list[ClaimGroup]            # 2-of-3 (records the dissenter)
    contested: list[ClaimGroup]            # DIVERGED (full spread)
    transcript: list[DebateRecord]         # everything, for user / downstream LLM
    metrics: Metrics

struct ClaimGroup:
    claim_id: ClaimId
    per_engine: dict[EngineId, ClaimVerdict]
    dissenters: list[EngineId]

struct Metrics:
    agreement_rate: float
    n_converged: int
    n_majority: int
    n_diverged: int
    capitulations: list[(EngineId, ClaimId)]   # reason-less concessions  [D4]
    reasoned_concessions: list[(EngineId, ClaimId)]
    llm_calls: int
    degraded_quorum: bool                       # an engine dropped mid-run


# ------------------------------------------------------------------------------
# CONFIG
# ------------------------------------------------------------------------------

config = {
    engines: [E1, E2, E3],          # N = len(engines); default 3
    tau: 0.66,                       # disagreement-confidence threshold for CONVERGED
    max_debate_rounds: 1,            # [D5] keep shallow
    require_evidence_for: [FACT],
    majority_floor: ceil(N/2) + (1 if N is even else 0),  # N=3 -> 2 ; N=4 -> 3
    on_invalid_json: "retry_once_then_drop",
}


# ==============================================================================
# STAGE 0 — independent answers + deterministic divergence gate
# ==============================================================================

def stage0(question, context, engines) -> (raw_answers, registry):
    # 0.1  Independent answers, in parallel. These are REUSED in the debate. [D2]
    raw_answers = parallel_map(engines, lambda e:
        e.answer(question, context, contract=CLAIM_CONTRACT))   # LLM call

    # 0.2  Decompose each answer into atomic claims and assign CANONICAL ids. [D1]
    #      (Decomposition is an LLM step per engine; id assignment is deterministic
    #       and idempotent, so identical claims across engines collapse to one id.)
    registry = ClaimRegistry()
    for e in engines:
        for claim in raw_answers[e].claims:
            cid = registry.register(claim)        # idempotent normalize+hash
            record (engine=e, cid, claim.verdict, claim.confidence)

    # 0.3  Divergence gate — deterministic. A claim is CONTESTED if engines
    #      disagree on its verdict, OR some engines never asserted it at all. [D2]
    for cid in registry.claims:
        verdicts_present = { verdict_of(e, cid) for e in engines if asserted(e, cid) }
        coverage        = count(e for e in engines if asserted(e, cid))
        if len(verdicts_present) > 1 or coverage < N:
            registry.contested_ids.add(cid)

    return raw_answers, registry
    # Everything NOT in contested_ids is already agreed -> straight to consensus.


# ==============================================================================
# ROUND 1 — rotated debate, ONLY over contested claims
# ==============================================================================

def round1_debate(question, raw_answers, registry, engines) -> transcript:
    contested = registry.contested_ids
    if contested is empty:
        return []                              # nothing to debate; skip cost

    memo = {}   # reuse: never recompute an identical (role-tuple -> output) call

    def answer(e):
        # REUSE Stage-0 answer, restricted to contested claims
        return restrict(raw_answers[e], contested)

    @memoize(memo)
    def critique(answerer, critic):            # LLM call
        return critic.critique(
            question, answer(answerer), contested_ids=contested)

    @memoize(memo)
    def rebuttal(answerer, critic):            # LLM call
        # answerer sees ONE critic's critique, revises, and logs concessions [D4]
        return answerer.rebut(
            question, answer(answerer), critique(answerer, critic),
            must_log_concessions=True)

    @memoize(memo)
    def synthesize(answerer, critic, synthesizer):   # LLM call
        return synthesizer.synthesize_dispute(
            question,
            answer(answerer),
            critique(answerer, critic),
            rebuttal(answerer, critic))

    transcript = []
    # All ordered assignments of 3 DISTINCT roles to engines.
    # N=3 -> 6 permutations. Role triple = (answerer, critic, synthesizer). [D3 note]
    for (answerer, critic, synthesizer) in permutations(engines, 3):
        rec = DebateRecord(
            answerer, critic, synthesizer,
            critique   = critique(answerer, critic),
            rebuttal   = rebuttal(answerer, critic),
            synthesis  = synthesize(answerer, critic, synthesizer),
        )
        transcript.append(rec)

    # New claims raised during debate (via proposed_correction / claim_refs) get
    # registered append-only, keeping alignment id-based and deterministic. [D1]
    register_new_claims(registry, transcript)

    return transcript
    # Cost with reuse (N=3): 6 critiques + 6 rebuttals + 6 syntheses = 18 new
    # LLM calls (+3 reused Stage-0 answers). High-assurance mode, not default.


# ==============================================================================
# COLLAPSE — each ENGINE emits ONE final claim-structured position   [D3]
# ==============================================================================

def collapse(question, transcript, registry, engines) -> positions:
    # Each engine reads the FULL debate transcript and returns a verdict for
    # EVERY contested canonical id. Output is aligned purely by shared id, so the
    # downstream merge needs no semantic matching.
    return parallel_map(engines, lambda e:                      # N LLM calls
        e.final_position(
            question,
            transcript,
            required_ids = registry.contested_ids))             # must cover all
    # -> list[EnginePosition], one per engine.


# ==============================================================================
# ROUND 2 — DETERMINISTIC merge (NO LLM)
# ==============================================================================

def classify(verdicts: list[ClaimVerdict], tau, N, majority_floor) -> ClaimStatus:
    groups = group_by(verdicts, key = v -> v.verdict)          # ASSERT/DENY/UNCERTAIN
    largest = max(groups, key=size)

    if size(largest) == N:
        # unanimous verdict; require no strong dissent recorded in transcript
        max_dissent_conf = max((v.confidence for v in dissenting_views), default=0)
        return CONVERGED if max_dissent_conf < tau else MAJORITY
    elif size(largest) >= majority_floor:
        return MAJORITY
    else:
        return DIVERGED


def deterministic_merge(positions, registry, raw_answers, config) -> MergeResult:
    N = len(positions)
    status = {}
    consensus, majority, contested = [], [], []

    # 1) Uncontested claims from Stage 0 -> straight into consensus.
    for cid in registry.claims:
        if cid not in registry.contested_ids:
            status[cid] = UNCONTESTED
            consensus.append(registry.claims[cid])

    # 2) Contested claims -> tally engine positions by shared id. Pure counting.
    for cid in registry.contested_ids:
        verdicts = [ p.verdicts[cid] for p in positions if cid in p.verdicts ]
        st = classify(verdicts, config.tau, N, config.majority_floor)
        status[cid] = st
        group = build_claim_group(cid, positions)
        if   st == CONVERGED: consensus.append(canonical_claim(cid, group))
        elif st == MAJORITY:  majority.append(group)         # records dissenter(s)
        else:                 contested.append(group)        # full spread retained

    metrics = compute_metrics(status, positions, transcript_concessions)  # [D4]
    return MergeResult(status, consensus, majority, contested,
                       transcript=current_transcript, metrics=metrics)


def compute_metrics(status, positions, concessions) -> Metrics:
    # Separate reasoned concessions (error-correction) from reason-less
    # capitulations (agreeableness drift). Both come straight from the
    # transcript's concession logs — no inference needed.  [D4]
    capit   = [ (c.engine, c.claim_id) for c in concessions if c.reason is None ]
    reasoned= [ (c.engine, c.claim_id) for c in concessions if c.reason is not None ]
    return Metrics(
        agreement_rate = count(CONVERGED) / count(contested_total),
        n_converged=..., n_majority=..., n_diverged=...,
        capitulations=capit, reasoned_concessions=reasoned,
        llm_calls=..., degraded_quorum=...,
    )


# ==============================================================================
# OUTPUT — status banner + user-selected view; transcript always available
# ==============================================================================

def present(merge: MergeResult, user_pref):
    # Banner reports the STATE honestly — never relabel convergence as confidence. [D4]
    banner = summarize_status(merge.metrics)   # e.g. "8 converged / 2 majority / 1 diverged"

    if user_pref.show == "synthesized":
        # Deterministic assembly: consensus stated plainly; majority items flagged
        # with their dissenter; diverged items shown as an explicit spread.
        # This is string assembly by status bucket — STILL no LLM.
        body = render_by_status(merge)
    elif user_pref.show == "full_debate":
        body = render_transcript(merge.transcript)

    # Always attach, regardless of view:
    #   - per-claim status table
    #   - capitulation vs reasoned-concession log  [D4]
    #   - raw transcript handle for a downstream reasoning LLM (optional consumer)
    return Output(banner, body,
                  attachments=[merge.per_claim_status,
                               merge.metrics.capitulations,
                               merge.transcript])


# ==============================================================================
# ORCHESTRATOR
# ==============================================================================

def run(question, context, config) -> Output:
    engines = healthy(config.engines)          # drop unreachable; track quorum
    if len(engines) < 2:
        return single_model_fallback(question, context)

    raw, registry = stage0(question, context, engines)            # Stage 0

    if registry.contested_ids is empty:                          # fast path [D2]
        merge = deterministic_merge(
            positions = positions_from_raw(raw, registry),
            registry=registry, raw_answers=raw, config=config)
        return present(merge, config.user_pref)

    transcript = round1_debate(question, raw, registry, engines)  # Round 1 [D5]
    positions  = collapse(question, transcript, registry, engines)# Collapse [D3]
    merge      = deterministic_merge(positions, registry, raw, config)  # Round 2
    return present(merge, config.user_pref)


# ==============================================================================
# VALIDATION / EVAL HARNESS (the metric that actually matters)
# ==============================================================================
#
# The headline number is NOT accuracy — it's CALIBRATION OF THE CONVERGENCE
# SIGNAL: when the system reports CONVERGED, how often is it actually correct?
# If "3/3" isn't calibrated to truth, the convergence display is theater and the
# single best model would be the better product.
#
#   for item in labeled_set:
#       out = run(item.question, item.context, config)
#       log(reported_status = out.metrics, correct = (out matches item.gold))
#
#   report:
#     - calibration curve: P(correct | CONVERGED), P(correct | MAJORITY), ...
#     - capitulation rate, and accuracy delta when capitulations are excluded
#     - head-to-head vs: single-best-model, llm-council chairman, flat majority
#     - cost (llm_calls) per item
# ==============================================================================
