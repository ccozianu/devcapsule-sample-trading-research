"""Role prompt templates, v0. Deliberately plain; iterate against real runs.

Marked unspecified-in-detail by the invocation spec (§5). Keep templates
free of any application domain.
"""

from __future__ import annotations

Message = tuple[str, str]  # (role, content); role in {"system", "user", "assistant"}


def _context_block(context: str | None) -> str:
    if not context:
        return ""
    return (
        "\n\nSupplied context (treat as the questioner's material, "
        f"not ground truth):\n{context}"
    )


def answerer_messages(question: str, context: str | None) -> list[Message]:
    return [
        (
            "system",
            "You are the ANSWERER in a structured multi-model debate. Answer the "
            "question directly and thoroughly. State your key claims explicitly and "
            "note your confidence and main assumptions. Do not hedge into vacuity.",
        ),
        ("user", f"Question: {question}{_context_block(context)}"),
    ]


def critic_messages(question: str, answer: str, context: str | None) -> list[Message]:
    return [
        (
            "system",
            "You are the CRITIC in a structured multi-model debate. Find faults in "
            "the answer: factual errors, weak or missing reasoning, unstated "
            "assumptions, and the strongest counterarguments. Be specific; quote the "
            "claims you attack. Do not manufacture disagreement where none exists — "
            "say so when the answer holds. End your reply with a fenced ```json block:"
            ' {"stance": "agree|disagree|partial|cannot_verify",'
            ' "objections": ["..."]}',
        ),
        (
            "user",
            f"Question: {question}{_context_block(context)}\n\nAnswer under critique:\n{answer}",
        ),
    ]


def rebuttal_messages(
    question: str, answer: str, critique: str, context: str | None
) -> list[Message]:
    return [
        (
            "system",
            "You are the ANSWERER responding to a critique of your answer. Concede "
            "points where the critic is right — and every concession MUST state the "
            "reason you now believe you were wrong; a concession without a reason is "
            "recorded as capitulation. Defend the points where the critic is wrong. "
            "End your reply with a fenced ```json block: "
            '{"concessions": [{"point": "...", "reason": "..."}], "maintained": ["..."]}',
        ),
        (
            "user",
            f"Question: {question}{_context_block(context)}\n\n"
            f"Your original answer:\n{answer}\n\nCritique:\n{critique}",
        ),
    ]


def last_synthesizer_messages(
    question: str, syntheses: list[tuple[str, str]]
) -> list[Message]:
    """The final, text-only synthesis over the rotation syntheses.

    The last synthesizer is a judge of the record, not a participant:
    anything it added on its own would enter the record unrebutted, so it
    is explicitly confined to the text at hand.
    """
    presented = "\n\n".join(
        f"--- SYNTHESIS by {engine} ---\n{text}" for engine, text in syntheses
    )
    return [
        (
            "system",
            "You are the LAST SYNTHESIZER in a structured multi-model debate. "
            "Several engines debated the question and independent synthesizers "
            "each produced a synthesis; those syntheses are the ONLY material "
            "before you. Base your judgment solely on the text at hand: do not "
            "research, do not add facts, figures, estimates, or outside "
            "knowledge — anything you added yourself would enter the record "
            "unrebutted. Compare the syntheses and report, separately, where "
            "they agree and disagree ON FACTS and where they agree and "
            "disagree ON REASONING. Agreement is an observation, not a "
            "correctness score. End your reply with a fenced ```json block: "
            '{"verdict": "converged|diverged", "factual_agreements": ["..."], '
            '"factual_disputes": ["..."], "reasoning_agreements": ["..."], '
            '"reasoning_disputes": ["..."]}',
        ),
        ("user", f"Question: {question}\n\nThe syntheses:\n\n{presented}"),
    ]


def synthesizer_messages(
    question: str, answer: str, exchange: str, context: str | None
) -> list[Message]:
    return [
        (
            "system",
            "You are the SYNTHESIZER, a third engine that did not take part in the "
            "dispute below. Produce the best available synthesis: what stands, what "
            "fell, what remains genuinely contested. Report the state of the dispute "
            "honestly — agreement is an observation, not a correctness score. End "
            "your reply with a fenced ```json block: "
            '{"verdict": "converged|diverged", "contested_points": ["..."]}',
        ),
        (
            "user",
            f"Question: {question}{_context_block(context)}\n\n"
            f"Original answer:\n{answer}\n\nDispute exchange:\n{exchange}",
        ),
    ]
