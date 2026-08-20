"""Pure deterministic classification functions; this module must never call an LLM."""

from collections import Counter
from collections.abc import Iterable

from rotated_consensus.domain import ClaimStatus, ClaimVerdict, Verdict


def strict_majority_floor(engine_count: int) -> int:
    if engine_count < 2:
        raise ValueError("consensus classification requires at least two engines")
    return engine_count // 2 + 1


def classify(
    verdicts: Iterable[ClaimVerdict],
    *,
    expected_engine_count: int,
    historical_dissent_confidences: Iterable[float] = (),
    tau: float = 0.66,
) -> ClaimStatus:
    """Classify one claim from aligned engine verdicts.

    Missing positions are treated as degraded coverage and can never be called
    converged. Strong dissent in the debate transcript downgrades an otherwise
    unanimous final position to MAJORITY.
    """
    votes = list(verdicts)
    if expected_engine_count < 2:
        raise ValueError("expected_engine_count must be at least two")
    if not 0.0 <= tau <= 1.0:
        raise ValueError("tau must be between 0 and 1")
    if not votes:
        return ClaimStatus.DIVERGED

    counts = Counter(vote.verdict for vote in votes)
    largest = max(counts.values())
    complete = len(votes) == expected_engine_count

    if complete and largest == expected_engine_count:
        strongest_dissent = max(historical_dissent_confidences, default=0.0)
        return ClaimStatus.CONVERGED if strongest_dissent < tau else ClaimStatus.MAJORITY
    if largest >= strict_majority_floor(expected_engine_count):
        return ClaimStatus.MAJORITY
    return ClaimStatus.DIVERGED


def flat_majority(votes: Iterable[Verdict]) -> Verdict | None:
    """Baseline whole-item vote; ties are reported rather than broken opaquely."""
    counts = Counter(votes)
    if not counts:
        return None
    ordered = counts.most_common()
    if len(ordered) > 1 and ordered[0][1] == ordered[1][1]:
        return None
    return ordered[0][0]
