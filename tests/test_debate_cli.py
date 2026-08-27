"""CLI and transcript tests; no network, no LangChain."""

import unittest

from test_debate_protocol import make_engines

from rotated_debate.cli import build_parser
from rotated_debate.engines import (
    EngineSpec,
    browse_tools_for,
    engine_labels,
    parse_engine_args,
    record_server_tool_use,
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

    def test_bare_model_names_infer_their_provider(self) -> None:
        cases = {
            "claude-sonnet-5": "anthropic:claude-sonnet-5",
            "gemini-3.1-pro-preview": "google_genai:gemini-3.1-pro-preview",
            "gpt-5.5-pro": "openai:gpt-5.5-pro",
            "o4-mini": "openai:o4-mini",
        }
        for name, expected in cases.items():
            self.assertEqual(resolve_model_id(EngineSpec(alias=name)), expected)

    def test_explicit_binding_wins_over_defaults(self) -> None:
        spec = EngineSpec(alias="claude", provider_model="anthropic:claude-opus-5")
        self.assertEqual(resolve_model_id(spec), "anthropic:claude-opus-5")

    def test_default_claude_binding_is_fable_5(self) -> None:
        self.assertEqual(
            resolve_model_id(EngineSpec(alias="claude")), "anthropic:claude-fable-5"
        )

    def test_reporting_labels_are_bare_model_names(self) -> None:
        labels = engine_labels(parse_engine_args("claude,gemini,chatgpt"))
        self.assertEqual(
            labels,
            {
                "claude": "claude-fable-5",
                "gemini": "gemini-3.1-pro-preview",
                "chatgpt": "gpt-5.6-sol",
            },
        )

    def test_colliding_labels_fall_back_to_alias_qualified_form(self) -> None:
        labels = engine_labels(
            parse_engine_args("a=anthropic:claude-opus-5,b=anthropic:claude-opus-5,gemini")
        )
        self.assertEqual(len(set(labels.values())), 3)
        self.assertEqual(labels["a"], "a=claude-opus-5")


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

    def test_browse_flag_parses(self) -> None:
        self.assertTrue(build_parser().parse_args(["ask", "q?", "--browse"]).browse)


class BrowseToolTests(unittest.TestCase):
    def test_every_default_engine_has_vendor_browse_tooling(self) -> None:
        for spec in parse_engine_args("claude,gemini,chatgpt"):
            self.assertTrue(browse_tools_for(resolve_model_id(spec)))

    def test_unknown_provider_is_a_clear_error(self) -> None:
        with self.assertRaises(ValueError):
            browse_tools_for("mistralai:mistral-large")

    def test_server_tool_counts_fold_into_usage(self) -> None:
        sink: dict[str, dict[str, int]] = {"e": {"calls": 1}}
        record_server_tool_use(
            sink, "e", {"usage": {"server_tool_use": {"web_search_requests": 3}}}
        )
        record_server_tool_use(sink, "e", {"usage": {}})
        record_server_tool_use(sink, "e", None)
        self.assertEqual(sink["e"], {"calls": 1, "web_search_requests": 3})


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

    def test_transcript_records_last_synthesis(self) -> None:
        judge_reply = (
            'digest\n```json\n{"verdict": "converged", "factual_agreements": ["f"],'
            ' "factual_disputes": [], "reasoning_agreements": [],'
            ' "reasoning_disputes": ["r"]}\n```'
        )
        result = run_debate(
            "q?",
            make_engines(),
            DebateSettings(rotations=3),
            last_synthesizer=("flash", lambda messages: judge_reply),
        )
        text = render(result, "t", {})
        self.assertIn('last_synthesizer_verdict: "converged"', text)
        self.assertIn('factual_agreements: ["f"]', text)
        self.assertIn("## Last synthesis — flash (text-only judge)", text)

    def test_transcript_without_last_synthesis_records_null_verdict(self) -> None:
        result = run_debate("q?", make_engines(), DebateSettings(rotations=3))
        text = render(result, "t", {})
        self.assertIn("last_synthesizer_verdict: null", text)
        self.assertNotIn("## Last synthesis", text)

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
