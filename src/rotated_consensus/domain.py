"""Small, provider-independent domain contracts.

LLM transport and prompt concerns deliberately do not belong in this module. The
final adjudication layer must remain deterministic and independently testable.
"""

from dataclasses import dataclass
from enum import StrEnum


class Verdict(StrEnum):
    ASSERT = "ASSERT"
    DENY = "DENY"
    UNCERTAIN = "UNCERTAIN"


class ClaimStatus(StrEnum):
    CONVERGED = "CONVERGED"
    MAJORITY = "MAJORITY"
    DIVERGED = "DIVERGED"
    UNCONTESTED = "UNCONTESTED"


@dataclass(frozen=True, slots=True)
class ClaimVerdict:
    verdict: Verdict
    confidence: float
    rationale: str = ""

    def __post_init__(self) -> None:
        if not 0.0 <= self.confidence <= 1.0:
            raise ValueError("confidence must be between 0 and 1")


@dataclass(frozen=True, slots=True)
class EnginePosition:
    engine: str
    verdicts: dict[str, ClaimVerdict]
