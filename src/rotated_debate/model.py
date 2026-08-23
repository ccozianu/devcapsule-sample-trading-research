"""Data contracts for a rotated debate. Dependency-free."""

from __future__ import annotations

from dataclasses import dataclass, field

PROVISIONAL_STATES = ("converged", "diverged", "unreported")


@dataclass(frozen=True, slots=True)
class EngineSpec:
    """An engine alias plus an optional explicit provider:model binding."""

    alias: str
    provider_model: str | None = None


@dataclass(frozen=True, slots=True)
class DebateSettings:
    rotations: int = 3
    rounds: int = 1
    browse: bool = False
    temperature: float = 0.3

    def __post_init__(self) -> None:
        if self.rotations < 1:
            raise ValueError("rotations must be >= 1")
        if self.rounds < 1:
            raise ValueError("rounds must be >= 1")


@dataclass(frozen=True, slots=True)
class Concession:
    point: str
    reason: str | None

    @property
    def capitulation(self) -> bool:
        """A concession without a stated reason is capitulation (DESIGN D4)."""
        return self.reason is None or not self.reason.strip()


@dataclass(frozen=True, slots=True)
class Critique:
    engine: str
    text: str
    stance: str | None = None
    objections: tuple[str, ...] = ()
    parse_error: str | None = None


@dataclass(frozen=True, slots=True)
class Rebuttal:
    engine: str
    text: str
    concessions: tuple[Concession, ...] = ()
    maintained: tuple[str, ...] = ()
    parse_error: str | None = None


@dataclass(frozen=True, slots=True)
class ExchangeRound:
    critique: Critique
    rebuttal: Rebuttal


@dataclass(frozen=True, slots=True)
class Synthesis:
    engine: str
    text: str
    verdict: str | None = None
    contested_points: tuple[str, ...] = ()
    parse_error: str | None = None


@dataclass(frozen=True, slots=True)
class RotationRecord:
    answerer: str
    critic: str
    synthesizer: str
    rounds: tuple[ExchangeRound, ...]
    synthesis: Synthesis


@dataclass(frozen=True, slots=True)
class DebateResult:
    question: str
    engines: tuple[str, ...]
    settings: DebateSettings
    answers: dict[str, str]
    rotations: tuple[RotationRecord, ...]
    context_note: str | None = None

    @property
    def concessions(self) -> tuple[Concession, ...]:
        return tuple(
            concession
            for rotation in self.rotations
            for exchange in rotation.rounds
            for concession in exchange.rebuttal.concessions
        )

    @property
    def synthesizer_verdicts(self) -> dict[str, str | None]:
        """Latest verdict per synthesizer engine (an engine may synthesize twice)."""
        verdicts: dict[str, str | None] = {}
        for rotation in self.rotations:
            verdicts[rotation.synthesizer] = rotation.synthesis.verdict
        return verdicts

    @property
    def provisional_state(self) -> str:
        """Provisional aggregation of synthesizer verdicts, pending OQ-1.

        Converged only if every synthesizer that reported a verdict said
        converged and at least one did. Any dissent or silence downgrades.
        """
        verdicts = [v for v in self.synthesizer_verdicts.values() if v is not None]
        if not verdicts:
            return "unreported"
        if all(v == "converged" for v in verdicts) and len(verdicts) == len(
            self.synthesizer_verdicts
        ):
            return "converged"
        return "diverged"


@dataclass(frozen=True, slots=True)
class OutcomeState:
    """Both adjudication fields reserved by the invocation spec, pending OQ-1."""

    deterministic_tally: str | None = None
    synthesizer_meta: str | None = None
    detail: dict[str, str | None] = field(default_factory=dict)
