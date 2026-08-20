"""Calibration-oriented evaluation that is independent of model providers."""

from collections import defaultdict
from dataclasses import dataclass
from typing import Any

from rotated_consensus.domain import ClaimStatus


@dataclass(frozen=True, slots=True)
class EvaluationRecord:
    item_id: str
    reported_status: ClaimStatus
    correct: bool
    llm_calls: int
    capitulations: int = 0
    reasoned_concessions: int = 0
    metadata: dict[str, Any] | None = None

    def __post_init__(self) -> None:
        if self.llm_calls < 0 or self.capitulations < 0 or self.reasoned_concessions < 0:
            raise ValueError("count fields cannot be negative")


@dataclass(frozen=True, slots=True)
class StatusCalibration:
    status: ClaimStatus
    samples: int
    correct: int

    @property
    def accuracy(self) -> float:
        return self.correct / self.samples


@dataclass(frozen=True, slots=True)
class EvaluationReport:
    by_status: tuple[StatusCalibration, ...]
    total_items: int
    total_llm_calls: int
    capitulation_rate: float


def evaluate(records: list[EvaluationRecord]) -> EvaluationReport:
    if not records:
        raise ValueError("at least one evaluation record is required")

    buckets: dict[ClaimStatus, list[bool]] = defaultdict(list)
    for record in records:
        buckets[record.reported_status].append(record.correct)

    calibration = tuple(
        StatusCalibration(status, len(results), sum(results))
        for status, results in sorted(buckets.items(), key=lambda item: item[0].value)
    )
    capitulations = sum(record.capitulations for record in records)
    concessions = capitulations + sum(record.reasoned_concessions for record in records)
    return EvaluationReport(
        by_status=calibration,
        total_items=len(records),
        total_llm_calls=sum(record.llm_calls for record in records),
        capitulation_rate=capitulations / concessions if concessions else 0.0,
    )
