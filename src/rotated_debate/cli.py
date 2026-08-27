"""`python -m rotated_debate ask ...` — the stateless invocation surface.

Contract: engineering-docs/specifications/debate-invocation.md section 1.
Reads nothing but --context files; writes nothing but --out. The epistemic
state is data (one stdout line and frontmatter), never an exit code.
"""

from __future__ import annotations

import argparse
import datetime as dt
import sys
from pathlib import Path

from rotated_debate.model import DebateSettings


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="rotated_debate")
    sub = parser.add_subparsers(dest="command", required=True)
    ask = sub.add_parser("ask", help="run one rotated debate on a question")
    ask.add_argument("question")
    ask.add_argument("--context", action="append", default=[], metavar="FILE")
    ask.add_argument("--engines", default="claude,gemini,chatgpt")
    ask.add_argument("--rotations", type=int, default=3)
    ask.add_argument("--rounds", type=int, default=1)
    ask.add_argument(
        "--browse", action=argparse.BooleanOptionalAction, default=False
    )
    ask.add_argument(
        "--add-last-synthesizer",
        metavar="MODEL",
        default=None,
        help="add a final text-only synthesis over the rotation syntheses, "
        "produced by MODEL (same forms as --engines items); never browses",
    )
    ask.add_argument(
        "--temperature",
        type=float,
        default=None,
        help="sampling temperature; omit for provider defaults (newer models "
        "reject an explicit value)",
    )
    ask.add_argument("--out", metavar="FILE")
    return parser


def _read_context(paths: list[str]) -> str | None:
    if not paths:
        return None
    sections = []
    for raw in paths:
        path = Path(raw)
        sections.append(f"--- {path.name} ---\n{path.read_text(encoding='utf-8')}")
    return "\n\n".join(sections)


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)

    from rotated_debate import engines as engine_mod
    from rotated_debate import protocol, transcript

    settings = DebateSettings(
        rotations=args.rotations,
        rounds=args.rounds,
        browse=args.browse,
        temperature=args.temperature,
    )
    specs = engine_mod.parse_engine_args(args.engines)
    usage_sink: engine_mod.UsageSink = {}
    chat_engines = engine_mod.build_engines(
        specs, args.temperature, usage_sink, browse=args.browse
    )
    context = _read_context(args.context)

    def report(message: str) -> None:
        print(message, file=sys.stderr, flush=True)

    last_synthesizer = None
    last_spec = None
    if args.add_last_synthesizer:
        (last_spec,) = engine_mod.parse_engine_args(args.add_last_synthesizer)
        last_label = engine_mod.engine_labels([last_spec])[last_spec.alias]
        if last_label in engine_mod.engine_labels(specs).values():
            last_label = f"{last_label} (last-synthesizer)"
        # The last synthesizer judges only the text at hand - never browses.
        last_synthesizer = (
            last_label,
            engine_mod.build_chat_fn(
                engine_mod.resolve_model_id(last_spec),
                args.temperature,
                browse=False,
                usage_sink=usage_sink,
                label=last_label,
            ),
        )

    result = protocol.run_debate(
        args.question,
        chat_engines,
        settings,
        context,
        on_progress=report,
        last_synthesizer=last_synthesizer,
    )

    now = dt.datetime.now(dt.UTC)
    out = Path(args.out) if args.out else Path(f"debate-{now:%Y%m%d-%H%M%S}.md")
    labels = engine_mod.engine_labels(specs)
    engine_models = {
        labels[spec.alias]: engine_mod.resolve_model_id(spec) for spec in specs
    }
    if last_synthesizer is not None and last_spec is not None:
        engine_models[last_synthesizer[0]] = engine_mod.resolve_model_id(last_spec)
    out.write_text(
        transcript.render(
            result, now.isoformat(timespec="seconds"), engine_models, usage_sink
        ),
        encoding="utf-8",
    )
    print(f"state={result.provisional_state} transcript={out}")
    return 0
