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
