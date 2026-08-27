"""CLI and transcript tests; no network, no LangChain."""

import io
import unittest
from contextlib import redirect_stderr

from test_debate_protocol import make_engines

from rotated_debate.cli import build_parser, main
from rotated_debate.engines import (
    EngineSpec,
    parse_engine_args,
    record_usage,
    resolve_model_id,
)
from rotated_debate.model import DebateSettings
from rotated_debate.protocol import run_debate
from rotated_debate.transcript import render


class EngineSpecTests(unittest.TestCase):
    def test_aliases_and_explicit_bindings_parse(self) -> None:
        specs = parse_engine_args("claude, mistral=mistralai:mistral-large, gemini")
        self.assertEqual(
            specs[1], EngineSpec(alias="mistral", provider_model="mistralai:mistral-large")
        )

    def test_duplicate_aliases_are_rejected(self) -> None:
        with self.assertRaises(ValueError):
            parse_engine_args("claude,claude")

    def test_unknown_alias_without_binding_is_an_error(self) -> None:
        with self.assertRaises(ValueError):
            resolve_model_id(EngineSpec(alias="mystery"))

    def test_explicit_binding_wins_over_defaults(self) -> None:
        spec = EngineSpec(alias="claude", provider_model="anthropic:claude-opus-5")
        self.assertEqual(resolve_model_id(spec), "anthropic:claude-opus-5")

    def test_default_claude_binding_is_fable_5(self) -> None:
        self.assertEqual(
            resolve_model_id(EngineSpec(alias="claude")), "anthropic:claude-fable-5"
        )


class UsageTests(unittest.TestCase):
    def test_integer_fields_accumulate_and_calls_are_counted(self) -> None:
        sink: dict[str, dict[str, int]] = {}
        record_usage(sink, "claude", {"input_tokens": 10, "output_tokens": 5})
        record_usage(
            sink,
            "claude",
            {"input_tokens": 7, "output_tokens": 3, "input_token_details": {"cache": 2}},
        )
        self.assertEqual(
            sink["claude"], {"calls": 2, "input_tokens": 17, "output_tokens": 8}
        )

    def test_missing_usage_still_counts_the_call(self) -> None:
        sink: dict[str, dict[str, int]] = {}
        record_usage(sink, "gemini", None)
        self.assertEqual(sink["gemini"], {"calls": 1})


class CliTests(unittest.TestCase):
    def test_defaults_match_the_specification(self) -> None:
        args = build_parser().parse_args(["ask", "q?"])
        self.assertEqual(
            (args.engines, args.rotations, args.rounds, args.browse),
            ("claude,gemini,chatgpt", 3, 1, False),
        )

    def test_browse_exits_with_error_before_touching_providers(self) -> None:
        stderr = io.StringIO()
        with redirect_stderr(stderr):
            code = main(["ask", "q?", "--browse"])
        self.assertEqual(code, 2)
        self.assertIn("not implemented", stderr.getvalue())


class TranscriptTests(unittest.TestCase):
    def test_transcript_reserves_both_outcome_fields(self) -> None:
        result = run_debate("q?", make_engines(), DebateSettings(rotations=3))
        text = render(result, "2026-08-23T00:00:00+00:00", {"alpha": "x", "beta": "y"})
        self.assertIn('deterministic_tally: null', text)
        self.assertIn('synthesizer_meta: "converged"', text)
        self.assertIn("role_assignments:", text)
        self.assertTrue(text.startswith("---"))

    def test_transcript_labels_capitulations(self) -> None:
        engines = make_engines(
            beta='{"concessions": [{"point": "gave up", "reason": null}], "maintained": []}'
        )
        result = run_debate("q?", engines, DebateSettings(rotations=3))
        text = render(result, "t", {})
        self.assertIn("[CAPITULATION] gave up", text)
        self.assertIn("capitulations: 1", text)

    def test_transcript_records_usage_metadata(self) -> None:
        result = run_debate("q?", make_engines(), DebateSettings(rotations=3))
        usage = {"alpha": {"calls": 4, "input_tokens": 17, "output_tokens": 8}}
        text = render(result, "t", {}, usage)
        self.assertIn(
            'usage: {"alpha": {"calls": 4, "input_tokens": 17, "output_tokens": 8}}',
            text,
        )
        self.assertIn("usage: null", render(result, "t", {}))


if __name__ == "__main__":
    unittest.main()
