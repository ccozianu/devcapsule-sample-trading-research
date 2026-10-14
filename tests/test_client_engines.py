"""Command-line client engines, driven by a fake `claude` on PATH.

No sign-in, no network, no real client: the fake answers `auth status` and
the print command with recorded JSON shaped like claude 2.1.261's output of
2026-10-14. Re-record the fake if a client version changes the flags or the
shape.
"""

import json
import os
import stat
import subprocess
import tempfile
import unittest
from pathlib import Path

from rotated_debate import clients
from rotated_debate.cli import main
from rotated_debate.engines import (
    EngineSpec,
    build_chat_fn,
    build_engines,
    engine_labels,
    parse_engine_args,
    record_usage,
    resolve_model_id,
)

FAKE_CLAUDE = r'''#!/usr/bin/env python3
"""Fake `claude`: records its argv, answers like the real client."""
import json, os, sys
log = os.environ.get("FAKE_CLAUDE_LOG")
if log:
    with open(log, "a", encoding="utf-8") as fh:
        fh.write(json.dumps({"argv": sys.argv[1:], "stdin": sys.stdin.read()}) + "\n")
if sys.argv[1:3] == ["auth", "status"]:
    print(json.dumps({"loggedIn": os.environ.get("FAKE_CLAUDE_LOGGED_IN", "1") == "1",
                      "authMethod": "claude.ai", "subscriptionType": "max"}))
    sys.exit(0)
if os.environ.get("FAKE_CLAUDE_FAIL"):
    print("boom", file=sys.stderr)
    sys.exit(3)
model = sys.argv[sys.argv.index("--model") + 1]
reply = os.environ.get("FAKE_CLAUDE_REPLY", "answer from " + model)
print(json.dumps({
    "type": "result", "subtype": "success", "is_error": False, "num_turns": 1,
    "result": reply, "total_cost_usd": 0.005,
    "usage": {"input_tokens": 403, "output_tokens": 4,
              "cache_creation_input_tokens": 0, "cache_read_input_tokens": 0,
              "server_tool_use": {"web_search_requests": 0, "web_fetch_requests": 0},
              "service_tier": "standard"},
}))
'''

ENGINE_REPLY = (
    "A position.\n```json\n"
    '{"concessions": [], "maintained": ["the point"], "verdict": "converged", '
    '"agreements": ["a"], "disagreements": [], "claims": [], "critiques": []}'
    "\n```"
)


class FakeClientMixin:
    def setUp(self) -> None:
        self._tmp = tempfile.TemporaryDirectory()
        self.bin = Path(self._tmp.name) / "bin"
        self.bin.mkdir()
        fake = self.bin / "claude"
        fake.write_text(FAKE_CLAUDE, encoding="utf-8")
        fake.chmod(fake.stat().st_mode | stat.S_IEXEC)
        self.log = Path(self._tmp.name) / "calls.jsonl"
        self._env = dict(os.environ)
        os.environ["PATH"] = f"{self.bin}{os.pathsep}{self._env.get('PATH', '')}"
        os.environ["FAKE_CLAUDE_LOG"] = str(self.log)
        for key in ("FAKE_CLAUDE_LOGGED_IN", "FAKE_CLAUDE_FAIL", "FAKE_CLAUDE_REPLY"):
            os.environ.pop(key, None)

    def tearDown(self) -> None:
        os.environ.clear()
        os.environ.update(self._env)
        self._tmp.cleanup()

    def calls(self) -> list[dict]:
        if not self.log.exists():
            return []
        return [json.loads(line) for line in self.log.read_text().splitlines()]


class GrammarTests(unittest.TestCase):
    def test_cli_items_resolve_to_their_vendors_client(self) -> None:
        cases = {
            "cli-claude-fable-5-1": "cli-claude:claude-fable-5-1",
            "cli-gpt-6-astra": "cli-codex:gpt-6-astra",
            "cli-o4-mini": "cli-codex:o4-mini",
            "cli-gemini-3.8-flash-high": "cli-antigravity:gemini-3.8-flash-high",
        }
        for item, expected in cases.items():
            self.assertEqual(resolve_model_id(EngineSpec(alias=item)), expected)

    def test_cli_form_works_as_an_explicit_binding(self) -> None:
        spec = EngineSpec(alias="mine", provider_model="cli-claude-fable-5-1")
        self.assertEqual(resolve_model_id(spec), "cli-claude:claude-fable-5-1")

    def test_unknown_shape_after_the_prefix_is_an_error_naming_the_forms(self) -> None:
        for item in ("cli-", "cli-mistral-large", "cli-claude"):
            with self.assertRaises(ValueError) as ctx:
                resolve_model_id(EngineSpec(alias=item))
            self.assertIn("full model id", str(ctx.exception))

    def test_api_route_is_untouched(self) -> None:
        self.assertEqual(
            resolve_model_id(EngineSpec(alias="claude")), "anthropic:claude-fable-5"
        )
        self.assertEqual(
            resolve_model_id(EngineSpec(alias="claude-fable-5-1")),
            "anthropic:claude-fable-5-1",
        )

    def test_client_engines_are_labeled_as_typed(self) -> None:
        labels = engine_labels(parse_engine_args("cli-claude-fable-5-1,claude,gemini"))
        self.assertEqual(labels["cli-claude-fable-5-1"], "cli-claude-fable-5-1")
        self.assertEqual(labels["claude"], "claude-fable-5")

    def test_same_model_by_api_and_by_client_stay_distinct(self) -> None:
        labels = engine_labels(parse_engine_args("cli-claude-fable-5,claude,gemini"))
        self.assertEqual(len(set(labels.values())), 3)

    def test_binding_form_is_labeled_by_its_cli_item(self) -> None:
        labels = engine_labels(parse_engine_args("mine=cli-claude-fable-5-1,gemini,chatgpt"))
        self.assertEqual(labels["mine"], "cli-claude-fable-5-1")


class RefusalTests(FakeClientMixin, unittest.TestCase):
    def test_browse_is_refused_before_any_call_naming_the_engines(self) -> None:
        specs = parse_engine_args("cli-claude-fable-5-1,gemini,chatgpt")
        with self.assertRaises(SystemExit) as ctx:
            build_engines(specs, None, {}, browse=True)
        self.assertIn("cli-claude-fable-5-1", str(ctx.exception))
        self.assertIn("--browse", str(ctx.exception))
        self.assertEqual(self.calls(), [])

    def test_not_signed_in_is_refused_before_any_call(self) -> None:
        os.environ["FAKE_CLAUDE_LOGGED_IN"] = "0"
        with self.assertRaises(SystemExit) as ctx:
            build_chat_fn("cli-claude:claude-fable-5-1", None, label="cli-claude-fable-5-1")
        self.assertIn("not signed in", str(ctx.exception))
        self.assertEqual([c["argv"] for c in self.calls()], [["auth", "status"]])

    def test_missing_client_is_refused(self) -> None:
        os.environ["PATH"] = str(self.bin / "nowhere")
        with self.assertRaises(SystemExit) as ctx:
            build_chat_fn("cli-claude:claude-fable-5-1", None, label="x")
        self.assertIn("not on PATH", str(ctx.exception))

    def test_other_clients_are_refused_naming_their_slice(self) -> None:
        for model_id, slice_name in (
            ("cli-codex:gpt-6-astra", "slice 2"),
            ("cli-antigravity:gemini-3.8-flash-high", "slice 3"),
        ):
            with self.assertRaises(SystemExit) as ctx:
                build_chat_fn(model_id, None, label=model_id)
            self.assertIn(slice_name, str(ctx.exception))
        self.assertEqual(self.calls(), [])


class ClaudeCallTests(FakeClientMixin, unittest.TestCase):
    def test_command_line_and_prompt_routing(self) -> None:
        chat = build_chat_fn("cli-claude:claude-fable-5-1", None, label="cli-claude-fable-5-1")
        reply = chat([("system", "You are the ANSWERER."), ("user", "Question: why?")])
        self.assertEqual(reply, "answer from claude-fable-5-1")
        call = self.calls()[-1]
        argv = call["argv"]
        self.assertEqual(argv[0], "-p")
        self.assertEqual(argv[argv.index("--model") + 1], "claude-fable-5-1")
        self.assertEqual(argv[argv.index("--system-prompt") + 1], "You are the ANSWERER.")
        self.assertEqual(argv[argv.index("--output-format") + 1], "json")
        self.assertEqual(argv[argv.index("--tools") + 1], "")
        self.assertEqual(argv[argv.index("--setting-sources") + 1], "")
        self.assertIn("--no-session-persistence", argv)
        self.assertEqual(call["stdin"], "Question: why?")

    def test_usage_is_recorded_as_reported_with_cost(self) -> None:
        sink: dict = {}
        chat = build_chat_fn("cli-claude:claude-fable-5-1", None, usage_sink=sink,
                             label="cli-claude-fable-5-1")
        chat([("system", "s"), ("user", "u")])
        chat([("system", "s"), ("user", "u")])
        entry = sink["cli-claude-fable-5-1"]
        self.assertEqual(entry["calls"], 2)
        self.assertEqual(entry["input_tokens"], 806)
        self.assertEqual(entry["output_tokens"], 8)
        self.assertEqual(entry["num_turns"], 2)
        self.assertAlmostEqual(entry["total_cost_usd"], 0.01)
        self.assertEqual(entry["web_search_requests"], 0)
        self.assertNotIn("service_tier", entry)

    def test_client_failure_is_an_error_naming_the_engine(self) -> None:
        chat = build_chat_fn("cli-claude:claude-fable-5-1", None, label="cli-claude-fable-5-1")
        os.environ["FAKE_CLAUDE_FAIL"] = "1"
        with self.assertRaises(RuntimeError) as ctx:
            chat([("system", "s"), ("user", "u")])
        self.assertIn("cli-claude-fable-5-1", str(ctx.exception))
        self.assertIn("exited 3", str(ctx.exception))

    def test_timeout_is_an_error_naming_the_limit(self) -> None:
        def slow(command, **kwargs):
            raise subprocess.TimeoutExpired(command, kwargs["timeout"])

        os.environ[clients.TIMEOUT_ENV] = "7"
        chat = clients.build_client_chat_fn(
            "cli-claude:claude-fable-5-1", None, "cli-claude-fable-5-1", run=slow
        )
        with self.assertRaises(RuntimeError) as ctx:
            chat([("system", "s"), ("user", "u")])
        self.assertIn("7s", str(ctx.exception))

    def test_multi_turn_messages_are_rejected(self) -> None:
        chat = build_chat_fn("cli-claude:claude-fable-5-1", None, label="x")
        with self.assertRaises(ValueError):
            chat([("system", "s"), ("user", "u"), ("assistant", "a")])

    def test_error_report_is_surfaced(self) -> None:
        def run(command, **kwargs):
            return subprocess.CompletedProcess(
                command, 0, stdout=json.dumps({"is_error": True, "subtype": "error",
                                               "result": "quota"}), stderr="")

        chat = clients.build_client_chat_fn("cli-claude:claude-fable-5-1", None, "x", run=run)
        with self.assertRaises(RuntimeError) as ctx:
            chat([("system", "s"), ("user", "u")])
        self.assertIn("quota", str(ctx.exception))


class UsageSinkTests(unittest.TestCase):
    def test_float_fields_accumulate(self) -> None:
        sink: dict = {}
        record_usage(sink, "e", {"total_cost_usd": 0.25, "input_tokens": 1, "ok": True})
        record_usage(sink, "e", {"total_cost_usd": 0.5})
        self.assertAlmostEqual(sink["e"]["total_cost_usd"], 0.75)
        self.assertEqual(sink["e"]["input_tokens"], 1)
        self.assertNotIn("ok", sink["e"])


class EndToEndTests(FakeClientMixin, unittest.TestCase):
    def test_full_debate_through_the_fake_client(self) -> None:
        os.environ["FAKE_CLAUDE_REPLY"] = ENGINE_REPLY
        out = Path(self._tmp.name) / "debate.md"
        code = main([
            "ask", "Is water wet?",
            "--engines", "cli-claude-fable-5-1,cli-claude-sonnet-5,cli-claude-opus-5",
            "--out", str(out),
        ])
        self.assertEqual(code, 0)
        text = out.read_text(encoding="utf-8")
        self.assertIn('"cli-claude-fable-5-1": "cli-claude:claude-fable-5-1"', text)
        self.assertIn('"cli-claude-sonnet-5": "cli-claude:claude-sonnet-5"', text)
        self.assertIn("total_cost_usd", text)
        argvs = [c["argv"] for c in self.calls()]
        self.assertEqual(argvs.count(["auth", "status"]), 3)
        self.assertTrue(all(a[0] == "-p" for a in argvs if a[:2] != ["auth", "status"]))


if __name__ == "__main__":
    unittest.main()
