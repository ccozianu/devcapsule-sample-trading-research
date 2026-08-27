"""The rotated-debate orchestration. Dependency-free; engines are injected.

An engine is any callable taking a list of (role, content) message tuples and
returning the reply text. Real LangChain-backed engines are built in
`engines.py`; tests inject scripted fakes.
"""

from __future__ import annotations

from collections.abc import Callable, Mapping, Sequence
from itertools import permutations

from rotated_debate import parsing, prompts
from rotated_debate.model import (
    Concession,
    Critique,
    DebateResult,
    DebateSettings,
    ExchangeRound,
    Rebuttal,
    RotationRecord,
    Synthesis,
)

ChatFn = Callable[[list[prompts.Message]], str]
# Called with a short human-readable line before each engine call; the core
# never writes to stdout/stderr itself, so reporting stays a caller concern.
ProgressFn = Callable[[str], None]


def build_rotations(aliases: Sequence[str], count: int) -> list[tuple[str, str, str]]:
    """Ordered (answerer, critic, synthesizer) triples, balanced-first.

    The cyclic shifts come first: with N engines they give N rotations in
    which every engine plays every role exactly once (fairness before
    redundancy). The remaining permutations follow in deterministic order.
    """
    engines = list(aliases)
    if len(engines) < 3:
        raise ValueError("a rotated debate needs at least three engines")
    n = len(engines)
    cyclic = [(engines[i], engines[(i + 1) % n], engines[(i + 2) % n]) for i in range(n)]
    rest = [p for p in permutations(engines, 3) if p not in set(cyclic)]
    ordered = cyclic + rest
    if not 1 <= count <= len(ordered):
        raise ValueError(
            f"rotations must be between 1 and {len(ordered)} for {n} engines, got {count}"
        )
    return ordered[:count]


def _parse_critique(engine: str, text: str) -> Critique:
    data, error = parsing.extract_json_block(text)
    if data is None:
        return Critique(engine=engine, text=text, parse_error=error)
    stance = data.get("stance")
    return Critique(
        engine=engine,
        text=text,
        stance=str(stance) if isinstance(stance, str) else None,
        objections=parsing.string_list(data.get("objections")),
    )


def _parse_rebuttal(engine: str, text: str) -> Rebuttal:
    data, error = parsing.extract_json_block(text)
    if data is None:
        return Rebuttal(engine=engine, text=text, parse_error=error)
    concessions: list[Concession] = []
    raw = data.get("concessions")
    if isinstance(raw, list):
        for item in raw:
            if isinstance(item, dict) and "point" in item:
                reason = item.get("reason")
                concessions.append(
                    Concession(
                        point=str(item["point"]),
                        reason=str(reason) if isinstance(reason, str) else None,
                    )
                )
    return Rebuttal(
        engine=engine,
        text=text,
        concessions=tuple(concessions),
        maintained=parsing.string_list(data.get("maintained")),
    )


def _parse_synthesis(engine: str, text: str) -> Synthesis:
    data, error = parsing.extract_json_block(text)
    if data is None:
        return Synthesis(engine=engine, text=text, parse_error=error)
    verdict = data.get("verdict")
    verdict = verdict if verdict in ("converged", "diverged") else None
    return Synthesis(
        engine=engine,
        text=text,
        verdict=verdict,
        contested_points=parsing.string_list(data.get("contested_points")),
    )


def run_debate(
    question: str,
    engines: Mapping[str, ChatFn],
    settings: DebateSettings,
    context: str | None = None,
    on_progress: ProgressFn | None = None,
) -> DebateResult:
    """Run the full bounded debate and return its structured record.

    Answers are memoized per engine: an engine answering in several
    rotations answers once (DESIGN reuse rule). The exchange itself is
    per-rotation, since it depends on who criticizes.
    """
    if settings.browse:
        raise NotImplementedError(
            "browsing is not implemented in v0 (invocation spec section 5)"
        )
    aliases = list(engines)
    triples = build_rotations(aliases, settings.rotations)

    def note(message: str) -> None:
        if on_progress is not None:
            on_progress(message)

    answers: dict[str, str] = {}

    def answer_of(alias: str) -> str:
        if alias not in answers:
            note(f"{alias} answering")
            answers[alias] = engines[alias](prompts.answerer_messages(question, context))
        return answers[alias]

    rotations: list[RotationRecord] = []
    for index, (answerer, critic, synthesizer) in enumerate(triples, start=1):
        tag = f"rotation {index}/{len(triples)}"
        answer = answer_of(answerer)
        rounds: list[ExchangeRound] = []
        exchange_text = ""
        latest_position = answer
        for round_no in range(1, settings.rounds + 1):
            round_tag = f"{tag} round {round_no}/{settings.rounds}"
            note(f"{round_tag}: {critic} critiquing {answerer}")
            critique_text = engines[critic](
                prompts.critic_messages(question, latest_position, context)
            )
            note(f"{round_tag}: {answerer} rebutting")
            rebuttal_text = engines[answerer](
                prompts.rebuttal_messages(question, latest_position, critique_text, context)
            )
            rounds.append(
                ExchangeRound(
                    critique=_parse_critique(critic, critique_text),
                    rebuttal=_parse_rebuttal(answerer, rebuttal_text),
                )
            )
            exchange_text += (
                f"\n--- CRITIQUE by {critic} ---\n{critique_text}"
                f"\n--- REBUTTAL by {answerer} ---\n{rebuttal_text}\n"
            )
            latest_position = rebuttal_text
        note(f"{tag}: {synthesizer} synthesizing")
        synthesis_text = engines[synthesizer](
            prompts.synthesizer_messages(question, answer, exchange_text, context)
        )
        rotations.append(
            RotationRecord(
                answerer=answerer,
                critic=critic,
                synthesizer=synthesizer,
                rounds=tuple(rounds),
                synthesis=_parse_synthesis(synthesizer, synthesis_text),
            )
        )

    return DebateResult(
        question=question,
        engines=tuple(aliases),
        settings=settings,
        answers=answers,
        rotations=tuple(rotations),
        context_note=context if context is None else f"{len(context)} chars supplied",
    )
