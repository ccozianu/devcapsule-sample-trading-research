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
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

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

FIXTURES = Path(__file__).parent / "fixtures" / "claude-client"
PRINT_RESULT = json.loads((FIXTURES / "print-result.json").read_text(encoding="utf-8"))
AUTH_STATUS = json.loads((FIXTURES / "auth-status.json").read_text(encoding="utf-8"))

FAKE_CLAUDE = r'''#!/usr/bin/env python3
"""Fake `claude`: records its call, answers from the recorded fixtures."""
import json, os, sys
sys.stdin.reconfigure(encoding="utf-8")
sys.stdout.reconfigure(encoding="utf-8")
fixtures = os.environ["FAKE_CLAUDE_FIXTURES"]
log = os.environ.get("FAKE_CLAUDE_LOG")
if log:
    with open(log, "a", encoding="utf-8") as fh:
        fh.write(json.dumps({
            "argv": sys.argv[1:], "stdin": sys.stdin.read(), "cwd": os.getcwd(),
            "key_vars": sorted(k for k in os.environ
                               if k in ("ANTHROPIC_API_KEY", "ANTHROPIC_AUTH_TOKEN",
                                        "ANTHROPIC_CUSTOM_HEADERS")),
        }) + "\n")
if sys.argv[1:3] == ["auth", "status"]:
    with open(os.path.join(fixtures, "auth-status.json"), encoding="utf-8") as fh:
        status = json.load(fh)
    if os.environ.get("FAKE_CLAUDE_LOGGED_IN", "1") != "1":
        status["loggedIn"] = False
        print(json.dumps(status))
        sys.exit(1)
    print(json.dumps(status))
    sys.exit(0)
if os.environ.get("FAKE_CLAUDE_FAIL"):
    print("boom", file=sys.stderr)
    sys.exit(3)
model = sys.argv[sys.argv.index("--model") + 1]
with open(os.path.join(fixtures, "print-result.json"), encoding="utf-8") as fh:
    report = json.load(fh)
report["result"] = os.environ.get("FAKE_CLAUDE_REPLY", "answer from " + model)
print(json.dumps(report, ensure_ascii=False))
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
        os.environ["FAKE_CLAUDE_FIXTURES"] = str(FIXTURES)
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

    def test_handle_override_still_wins_over_a_cli_binding(self) -> None:
        spec = EngineSpec(alias="mine", provider_model="cli-claude-fable-5-1")
        with patch.dict(os.environ, {"ROTATED_DEBATE_MODEL_MINE": "openai:gpt-6-astra"}):
            self.assertEqual(resolve_model_id(spec), "openai:gpt-6-astra")
        with patch.dict(os.environ, {"ROTATED_DEBATE_MODEL_MINE": "cli-claude-opus-5"}):
            self.assertEqual(resolve_model_id(spec), "cli-claude:claude-opus-5")


class RefusalTests(FakeClientMixin, unittest.TestCase):
    def test_explicit_temperature_is_refused_before_any_call(self) -> None:
        for temperature in (0.0, 0.5):
            with self.subTest(temperature=temperature):
                with self.assertRaisesRegex(SystemExit, "--temperature.*cli-claude"):
                    build_chat_fn("cli-claude:claude-fable-5-1", temperature)
        self.assertEqual(self.calls(), [])

    def test_last_synthesizer_temperature_refuses_before_debate(self) -> None:
        with (
            patch("rotated_debate.engines.build_engines", return_value={}),
            patch("rotated_debate.protocol.run_debate") as debate,
            self.assertRaisesRegex(SystemExit, "--temperature"),
        ):
            main(["ask", "q", "--temperature", "0",
                  "--add-last-synthesizer", "cli-claude-fable-5-1"])
        debate.assert_not_called()
        self.assertEqual(self.calls(), [])

    def test_auth_process_failures_are_actionable_refusals(self) -> None:
        for error, expected in (
            (subprocess.TimeoutExpired(["claude", "auth", "status"], 60), "60s"),
            (OSError("cannot execute"), "installation"),
        ):
            with self.subTest(error=error):
                def fail(command, error=error, **kwargs):
                    raise error

                with self.assertRaises(SystemExit) as ctx:
                    clients.check_available("cli-claude:claude-fable-5-1", run=fail)
                self.assertIn("claude", str(ctx.exception))
                self.assertIn(expected, str(ctx.exception))
        self.assertEqual(self.calls(), [])

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

    def test_other_sign_in_methods_are_refused(self) -> None:
        for method in ({"authMethod": "api_key"}, {"apiProvider": "bedrock"}):
            status = {**AUTH_STATUS, **method}

            def run(command, status=status, **kwargs):
                return subprocess.CompletedProcess(
                    command, 0, stdout=json.dumps(status), stderr=""
                )

            with self.assertRaises(SystemExit) as ctx:
                clients.check_available("cli-claude:claude-fable-5-1", run=run)
            self.assertIn("claude.ai", str(ctx.exception))

    def test_temporary_root_under_a_project_is_refused(self) -> None:
        project = Path(self._tmp.name) / "project"
        (project / "tmp").mkdir(parents=True)
        (project / "CLAUDE.md").write_text("instructions", encoding="utf-8")
        with patch.dict(os.environ, {"TMPDIR": str(project / "tmp")}):
            with patch.object(tempfile, "tempdir", None):
                with self.assertRaises(SystemExit) as ctx:
                    build_chat_fn("cli-claude:claude-fable-5-1", None, label="x")
        self.assertIn("CLAUDE.md", str(ctx.exception))
        self.assertEqual(list((project / "tmp").iterdir()), [])

    def test_signed_out_status_exit_code_alone_is_a_refusal(self) -> None:
        def run(command, **kwargs):
            return subprocess.CompletedProcess(command, 1, stdout="", stderr="not logged in")

        with self.assertRaises(SystemExit):
            clients.check_available("cli-claude:claude-fable-5-1", run=run)

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
    def test_unicode_round_trip_in_an_ascii_locale(self) -> None:
        os.environ["FAKE_CLAUDE_REPLY"] = "Réponse: 水"
        code = r'''
import os
from rotated_debate.engines import build_chat_fn
# The fake, like the real Node client, uses UTF-8 independent of our locale.
os.environ["PYTHONUTF8"] = "1"
chat = build_chat_fn("cli-claude:claude-fable-5-1", None, label="x")
assert chat([("system", "s"), ("user", "caf\u00e9 \u6c34")]) == "R\u00e9ponse: \u6c34"
'''
        completed = subprocess.run(
            [sys.executable, "-c", code],
            env={**os.environ, "LC_ALL": "C", "PYTHONUTF8": "0",
                 "PYTHONCOERCECLOCALE": "0"},
            capture_output=True, encoding="utf-8", check=False,
        )
        self.assertEqual(completed.returncode, 0, completed.stderr)
        self.assertEqual(self.calls()[-1]["stdin"], "café 水")

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
        self.assertIn("--strict-mcp-config", argv)
        self.assertEqual(call["stdin"], "Question: why?")

    def test_client_runs_in_an_empty_directory_of_its_own(self) -> None:
        chat = build_chat_fn("cli-claude:claude-fable-5-1", None, label="x")
        chat([("system", "s"), ("user", "u")])
        cwd = Path(self.calls()[-1]["cwd"])
        self.assertNotEqual(cwd.resolve(), Path.cwd().resolve())
        self.assertTrue(cwd.name.startswith("rotated-debate-client-"))
        self.assertEqual(list(cwd.iterdir()), [])
        self.assertIs(chat.workdir.name, chat.workdir.name)

    def test_api_key_variables_never_reach_the_client(self) -> None:
        credentials = {
            "ANTHROPIC_API_KEY": "sk-test",
            "ANTHROPIC_AUTH_TOKEN": "t",
            "ANTHROPIC_CUSTOM_HEADERS": "X-Api-Key: sk-test\nAuthorization: Bearer test",
        }
        with patch.dict(os.environ, credentials):
            chat = build_chat_fn("cli-claude:claude-fable-5-1", None, label="x")
            chat([("system", "s"), ("user", "u")])
        calls = self.calls()
        self.assertEqual([c["argv"][:2] for c in calls][0], ["auth", "status"])
        self.assertTrue(all(c["key_vars"] == [] for c in calls), calls)

    def test_cloud_route_selectors_never_reach_the_client(self) -> None:
        selectors = {"CLAUDE_CODE_USE_BEDROCK": "1", "AWS_BEARER_TOKEN_BEDROCK": "t"}
        with patch.dict(os.environ, selectors):
            env = clients.client_env()
        self.assertNotIn("CLAUDE_CODE_USE_BEDROCK", env)
        self.assertNotIn("AWS_BEARER_TOKEN_BEDROCK", env)

    def test_fake_answers_from_the_recorded_fixture(self) -> None:
        chat = build_chat_fn("cli-claude:claude-fable-5-1", None, label="x")
        self.assertEqual(chat([("system", "s"), ("user", "u")]), "answer from claude-fable-5-1")
        usage = clients.claude_usage(PRINT_RESULT)
        self.assertEqual(usage["input_tokens"], 403)
        self.assertEqual(usage["total_cost_usd"], PRINT_RESULT["total_cost_usd"])
        self.assertTrue(AUTH_STATUS["loggedIn"])

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
        self.assertAlmostEqual(entry["total_cost_usd"], 2 * PRINT_RESULT["total_cost_usd"])
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
