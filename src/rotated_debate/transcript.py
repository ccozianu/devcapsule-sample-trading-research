"""Render a DebateResult as one self-contained Markdown transcript. No deps.

Frontmatter is YAML written through json.dumps for every value (JSON is a
YAML subset), so no YAML library is needed and escaping is never wrong.
"""

from __future__ import annotations

import json

from rotated_debate.model import DebateResult


def _fm(key: str, value: object, indent: int = 0) -> str:
    return f"{' ' * indent}{key}: {json.dumps(value)}"


def render(
    result: DebateResult,
    generated_at: str,
    engine_models: dict[str, str],
    usage: dict[str, dict[str, int]] | None = None,
) -> str:
    reasoned = sum(1 for c in result.concessions if not c.capitulation)
    capitulations = sum(1 for c in result.concessions if c.capitulation)
    parse_errors = [
        f"{record.synthesis.engine}:synthesis"
        for record in result.rotations
        if record.synthesis.parse_error
    ] + [
        f"{who.engine}:{kind}"
        for record in result.rotations
        for exchange in record.rounds
        for kind, who in (("critique", exchange.critique), ("rebuttal", exchange.rebuttal))
        if who.parse_error
    ]

    lines = ["---"]
    lines.append(_fm("question", result.question))
    lines.append(_fm("generated_at", generated_at))
    lines.append(_fm("engines", engine_models))
    # Provider-reported consumption per engine; units are whatever the
    # provider uses (tokens today), summed by engines.record_usage.
    lines.append(_fm("usage", usage))
    lines.append(_fm("rotations", result.settings.rotations))
    lines.append(_fm("rounds", result.settings.rounds))
    lines.append(_fm("browse", result.settings.browse))
    lines.append(_fm("temperature", result.settings.temperature))
    lines.append(_fm("context_note", result.context_note))
    lines.append("role_assignments:")
    for record in result.rotations:
        triple = {
            "answerer": record.answerer,
            "critic": record.critic,
            "synthesizer": record.synthesizer,
        }
        lines.append(f"  - {json.dumps(triple)}")
    lines.append("outcome_state:")
    lines.append(_fm("deterministic_tally", None, indent=2))
    lines.append(_fm("synthesizer_meta", result.provisional_state, indent=2))
    lines.append(_fm("synthesizer_verdicts", result.synthesizer_verdicts, indent=2))
    lines.append("concessions:")
    lines.append(_fm("reasoned", reasoned, indent=2))
    lines.append(_fm("capitulations", capitulations, indent=2))
    lines.append(_fm("parse_errors", parse_errors))
    lines.append("---")

    lines.append("\n# Rotated Debate Transcript\n")
    lines.append(f"**Question.** {result.question}\n")
    lines.append(
        f"**Reported state (provisional, pending OQ-1): "
        f"{result.provisional_state.upper()}.** Agreement is an observed state, "
        "never a correctness score.\n"
    )

    lines.append("## Answers\n")
    for alias, answer in result.answers.items():
        lines.append(f"### Answer — {alias}\n\n{answer}\n")

    for i, record in enumerate(result.rotations, 1):
        lines.append(
            f"## Rotation {i}: {record.answerer} answers, "
            f"{record.critic} criticizes, {record.synthesizer} synthesizes\n"
        )
        for j, exchange in enumerate(record.rounds, 1):
            lines.append(f"### Round {j} — critique by {record.critic}\n")
            lines.append(exchange.critique.text + "\n")
            lines.append(f"### Round {j} — rebuttal by {record.answerer}\n")
            lines.append(exchange.rebuttal.text + "\n")
            for concession in exchange.rebuttal.concessions:
                label = "CAPITULATION" if concession.capitulation else "reasoned concession"
                lines.append(f"> [{label}] {concession.point}\n")
        lines.append(f"### Synthesis by {record.synthesizer}\n")
        lines.append(record.synthesis.text + "\n")

    lines.append("## Outcome\n")
    lines.append(
        f"Synthesizer verdicts: {json.dumps(result.synthesizer_verdicts)}. "
        f"Concessions: {reasoned} reasoned, {capitulations} capitulation(s).\n"
    )
    return "\n".join(lines)
