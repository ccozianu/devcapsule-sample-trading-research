"""Command-line client engines, driven by fake `claude`, `codex` and
`antigravity` scripts on PATH.

No sign-in, no network, no real client: each fake answers its sign-in
command and its print command from the recorded fixtures under
tests/fixtures/<client>-client/. Re-record when a client version changes
the flags or the shape.
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
CODEX_FIXTURES = Path(__file__).parent / "fixtures" / "codex-client"
ANTIGRAVITY_FIXTURES = Path(__file__).parent / "fixtures" / "antigravity-client"
PRINT_RESULT = json.loads((FIXTURES / "print-result.json").read_text(encoding="utf-8"))
AUTH_STATUS = json.loads((FIXTURES / "auth-status.json").read_text(encoding="utf-8"))
ANTIGRAVITY_RESULT = json.loads(
    (ANTIGRAVITY_FIXTURES / "print-result.json").read_text(encoding="utf-8")
)

FAKE_CODEX = r'''#!/usr/bin/env python3
"""Fake `codex`: records its call, answers from the recorded fixtures."""
import json, os, sys
sys.stdin.reconfigure(encoding="utf-8")
sys.stdout.reconfigure(encoding="utf-8")
fixtures = os.environ["FAKE_CODEX_FIXTURES"]
log = os.environ.get("FAKE_CLAUDE_LOG")
stdin = "" if sys.argv[1:3] == ["login", "status"] else sys.stdin.read()
if log:
    with open(log, "a", encoding="utf-8") as fh:
        fh.write(json.dumps({"client": "codex", "argv": sys.argv[1:], "stdin": stdin,
                             "cwd": os.getcwd(), "codex_home": os.environ.get("CODEX_HOME"),
                             "key_vars": sorted(k for k in os.environ
                                                if k.endswith("_API_KEY"))}) + "\n")
if sys.argv[1:3] == ["login", "status"]:
    if os.environ.get("FAKE_CODEX_LOGGED_IN", "1") != "1":
        print("Not logged in"); sys.exit(1)
    with open(os.path.join(fixtures, "login-status.txt"), encoding="utf-8") as fh:
        sys.stdout.write(fh.read())
    sys.exit(0)
model = sys.argv[sys.argv.index("-m") + 1]
events = "exec-events-browse.jsonl" if os.environ.get("FAKE_CODEX_BROWSE") else "exec-events.jsonl"
with open(os.path.join(fixtures, events), encoding="utf-8") as fh:
    for line in fh:
        event = json.loads(line)
        if event.get("type") == "item.completed":
            event["item"]["text"] = os.environ.get("FAKE_CLAUDE_REPLY", "answer from " + model)
        print(json.dumps(event, ensure_ascii=False))
'''

FAKE_ANTIGRAVITY = r'''#!/usr/bin/env python3
"""Fake `antigravity`: records its call, answers from the recorded fixtures."""
import json, os, sys
sys.stdin.reconfigure(encoding="utf-8")
sys.stdout.reconfigure(encoding="utf-8")
fixtures = os.environ["FAKE_ANTIGRAVITY_FIXTURES"]
log = os.environ.get("FAKE_CLAUDE_LOG")
stdin = "" if sys.argv[1:2] == ["models"] else sys.stdin.read()
if log:
    with open(log, "a", encoding="utf-8") as fh:
        fh.write(json.dumps({"client": "antigravity", "argv": sys.argv[1:], "stdin": stdin,
                             "cwd": os.getcwd(), "home": os.environ.get("HOME"),
                             "key_vars": sorted(k for k in os.environ
                                                if k.endswith("_API_KEY"))}) + "\n")
if sys.argv[1:2] == ["models"]:
    if os.environ.get("FAKE_ANTIGRAVITY_LOGGED_IN", "1") != "1":
        print("Fetching available models...\nError: not signed in", file=sys.stderr); sys.exit(1)
    with open(os.path.join(fixtures, "models.txt"), encoding="utf-8") as fh:
        sys.stdout.write(fh.read())
    sys.exit(0)
model = sys.argv[sys.argv.index("--model") + 1]
suffixed = model.endswith(("-low", "-medium", "-high"))
name = "print-result.json" if "--effort" in sys.argv or suffixed else "print-error.json"
with open(os.path.join(fixtures, name), encoding="utf-8") as fh:
    report = json.load(fh)
if report["status"] != "SUCCESS":
    print(json.dumps(report)); sys.exit(1)
report["response"] = os.environ.get("FAKE_CLAUDE_REPLY", "answer from " + model)
print(json.dumps(report, ensure_ascii=False))
'''

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
        for name, source in (
            ("claude", FAKE_CLAUDE), ("codex", FAKE_CODEX), ("antigravity", FAKE_ANTIGRAVITY)
        ):
            fake = self.bin / name
            fake.write_text(source, encoding="utf-8")
            fake.chmod(fake.stat().st_mode | stat.S_IEXEC)
        self.log = Path(self._tmp.name) / "calls.jsonl"
        self._env = dict(os.environ)
        os.environ["PATH"] = f"{self.bin}{os.pathsep}{self._env.get('PATH', '')}"
        os.environ["FAKE_CLAUDE_LOG"] = str(self.log)
        os.environ["FAKE_CLAUDE_FIXTURES"] = str(FIXTURES)
        os.environ["FAKE_CODEX_FIXTURES"] = str(CODEX_FIXTURES)
        os.environ["FAKE_ANTIGRAVITY_FIXTURES"] = str(ANTIGRAVITY_FIXTURES)
        for key in ("FAKE_CLAUDE_LOGGED_IN", "FAKE_CLAUDE_FAIL", "FAKE_CLAUDE_REPLY",
                    "FAKE_CODEX_LOGGED_IN", "FAKE_ANTIGRAVITY_LOGGED_IN", "FAKE_CODEX_BROWSE"):
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

    def test_browse_flag_is_accepted_for_client_engines(self) -> None:
        specs = parse_engine_args("cli-claude-fable-5-1,cli-gpt-6-astra,cli-gemini-3.8-flash")
        engines = build_engines(specs, None, {}, browse=True)
        self.assertEqual(len(engines), 3)
        self.assertEqual(sorted(c["argv"][0] for c in self.calls()), ["auth", "login", "models"])

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

    def test_codex_not_signed_in_through_chatgpt_is_refused(self) -> None:
        os.environ["FAKE_CODEX_LOGGED_IN"] = "0"
        with self.assertRaises(SystemExit) as ctx:
            build_chat_fn("cli-codex:gpt-6-astra", None, label="x")
        self.assertIn("ChatGPT", str(ctx.exception))
        self.assertEqual([c["argv"] for c in self.calls()], [["login", "status"]])

    def test_codex_api_key_sign_in_is_refused(self) -> None:
        def run(command, **kwargs):
            return subprocess.CompletedProcess(
                command, 0, stdout="Logged in using API key\n", stderr=""
            )

        with self.assertRaises(SystemExit) as ctx:
            clients.check_available("cli-codex:gpt-6-astra", run=run)
        self.assertIn("ChatGPT", str(ctx.exception))

    def test_antigravity_not_signed_in_is_refused(self) -> None:
        os.environ["FAKE_ANTIGRAVITY_LOGGED_IN"] = "0"
        with self.assertRaises(SystemExit) as ctx:
            build_chat_fn("cli-antigravity:gemini-3.8-flash-high", None, label="x")
        self.assertIn("not signed in", str(ctx.exception))
        self.assertEqual([c["argv"] for c in self.calls()], [["models"]])

    def test_antigravity_unlisted_model_is_refused_with_the_list(self) -> None:
        with self.assertRaises(SystemExit) as ctx:
            build_chat_fn("cli-antigravity:gemini-9-ultra", None, label="x")
        self.assertIn("gemini-3.8-flash-high", str(ctx.exception))
        self.assertEqual(len(self.calls()), 1)

    def test_antigravity_base_id_is_accepted_when_a_suffixed_id_is_listed(self) -> None:
        build_chat_fn("cli-antigravity:gemini-3.8-flash", None, label="x")
        self.assertEqual([c["argv"] for c in self.calls()], [["models"]])

    def test_antigravity_preflight_matches_the_requested_effort_or_exact_id(self) -> None:
        cases = (
            ("gemini-3.8-flash", "gemini-3.8-flash", True),
            ("gemini-3.8-flash", "gemini-3.8-flash-high", True),
            ("gemini-3.8-flash", "gemini-3.8-flash-low", False),
            ("gemini-3.8-flash", "gemini-3.8-flash-medium", False),
            ("gemini-3.8-flash-low", "gemini-3.8-flash-low", True),
            ("gemini-3.8-flash-high", "gemini-3.8-flash-low", False),
        )
        for model, listed, accepted in cases:
            with self.subTest(model=model, listed=listed):
                def run(command, listed=listed, **kwargs):
                    return subprocess.CompletedProcess(
                        command, 0, stdout=f"{listed}\tDisplay name\n", stderr=""
                    )

                if accepted:
                    clients.check_available(f"cli-antigravity:{model}", run=run)
                else:
                    with self.assertRaisesRegex(SystemExit, "does not list"):
                        clients.check_available(f"cli-antigravity:{model}", run=run)
        self.assertEqual(self.calls(), [])

    def test_antigravity_empty_and_error_listings_are_refused(self) -> None:
        listing = (ANTIGRAVITY_FIXTURES / "models.txt").read_text(encoding="utf-8")
        for code, stdout in ((0, ""), (0, "Fetching available models...\n"),
                             (0, "Error: not signed in\n"), (1, listing)):
            with self.subTest(code=code, stdout=stdout):
                def run(command, code=code, stdout=stdout, **kwargs):
                    return subprocess.CompletedProcess(command, code, stdout=stdout, stderr="")

                with self.assertRaisesRegex(SystemExit, "antigravity.*not signed in"):
                    clients.check_available("cli-antigravity:gemini-3.8-flash", run=run)
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
        self.assertEqual(argv[argv.index("--tools") + 1], "WebSearch,WebFetch")
        self.assertEqual(argv[argv.index("--allowedTools") + 1], "WebSearch,WebFetch")
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
        self.assertNotIn("web_fetch_requests", entry)

    def test_web_searches_are_summed_from_model_usage(self) -> None:
        report = json.loads(json.dumps(PRINT_RESULT))
        for entry in report["modelUsage"].values():
            entry["webSearchRequests"] = 3
        self.assertEqual(clients.claude_usage(report)["web_search_requests"], 6)

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


class CodexCallTests(FakeClientMixin, unittest.TestCase):
    def test_command_line_instructions_file_and_prompt_routing(self) -> None:
        chat = build_chat_fn("cli-codex:gpt-6-astra", None, label="cli-gpt-6-astra")
        reply = chat([("system", "You are the CRITIC."), ("user", "Critique this.")])
        self.assertEqual(reply, "answer from gpt-6-astra")
        call = [c for c in self.calls() if c["argv"][:1] == ["exec"]][-1]
        argv = call["argv"]
        self.assertEqual(argv[argv.index("-m") + 1], "gpt-6-astra")
        self.assertEqual(argv[argv.index("-s") + 1], "read-only")
        self.assertIn("--ephemeral", argv)
        self.assertIn("--json", argv)
        self.assertEqual(argv[-1], "-")
        self.assertIn("--ignore-rules", argv)
        self.assertIn('web_search="live"', argv)
        self.assertNotIn('web_search="disabled"', argv)
        self.assertIn("features.shell_tool=false", argv)
        self.assertIn("features.apps=false", argv)
        self.assertNotIn("tools.web_search=false", argv)
        self.assertEqual(call["stdin"], "Critique this.")
        workdir = Path(argv[argv.index("-C") + 1])
        self.assertEqual(Path(call["cwd"]).resolve(), workdir.resolve())
        instructions = argv[argv.index("-c") + 1].removeprefix("model_instructions_file=")
        self.assertEqual(Path(instructions).read_text(encoding="utf-8"), "You are the CRITIC.")
        self.assertEqual(Path(instructions).parent, workdir)

    def test_codex_runs_with_a_private_home_linking_only_the_sign_in_file(self) -> None:
        real_home = Path(self._tmp.name) / "real-codex-home"
        real_home.mkdir()
        (real_home / "auth.json").write_text("{}", encoding="utf-8")
        (real_home / "AGENTS.md").write_text("planted", encoding="utf-8")
        with patch.dict(os.environ, {"CODEX_HOME": str(real_home)}):
            chat = build_chat_fn("cli-codex:gpt-6-astra", None, label="x")
            chat([("system", "s"), ("user", "u")])
        call = [c for c in self.calls() if c["argv"][:1] == ["exec"]][-1]
        home = Path(call["codex_home"])
        self.assertEqual(home.parent.resolve(), Path(call["cwd"]).resolve())
        self.assertEqual([p.name for p in home.iterdir()], ["auth.json"])
        self.assertEqual((home / "auth.json").resolve(), (real_home / "auth.json").resolve())
        self.assertFalse((home / "AGENTS.md").exists())

    def test_web_search_items_are_counted_not_refused(self) -> None:
        os.environ["FAKE_CODEX_BROWSE"] = "1"
        sink: dict = {}
        chat = build_chat_fn("cli-codex:gpt-6-astra", None, usage_sink=sink, label="g")
        text = chat([("system", "s"), ("user", "u")])
        self.assertEqual(text, "answer from gpt-6-astra")
        self.assertEqual(sink["g"]["web_search_requests"], 2)
        self.assertEqual(sink["g"]["input_tokens"], 33508)

    def test_a_tool_item_in_the_stream_fails_the_call(self) -> None:
        events = (CODEX_FIXTURES / "exec-events.jsonl").read_text(encoding="utf-8")
        tool = json.dumps({"type": "item.completed", "item": {"type": "command_execution",
                                                                "command": "ls"}})
        with self.assertRaisesRegex(RuntimeError, "used a tool.*command_execution"):
            clients._parse_codex_events("x", tool + "\n" + events)
        reasoning = json.dumps({"type": "item.completed", "item": {"type": "reasoning",
                                                                     "text": "hmm"}})
        text, _ = clients._parse_codex_events("x", reasoning + "\n" + events)
        self.assertEqual(text, "pong")

    def test_usage_comes_from_the_turn_completed_event(self) -> None:
        sink: dict = {}
        chat = build_chat_fn(
            "cli-codex:gpt-6-astra", None, usage_sink=sink, label="cli-gpt-6-astra"
        )
        chat([("system", "s"), ("user", "u")])
        entry = sink["cli-gpt-6-astra"]
        self.assertEqual(entry["calls"], 1)
        self.assertEqual(entry["input_tokens"], 9345)
        self.assertEqual(entry["cached_input_tokens"], 7424)
        self.assertEqual(entry["reasoning_output_tokens"], 0)
        self.assertEqual(entry["web_search_requests"], 0)

    def test_instructions_are_replaced_before_each_call(self) -> None:
        observed = []

        def run(command, **kwargs):
            instructions = Path(kwargs["cwd"]) / "instructions.md"
            observed.append(instructions.read_text(encoding="utf-8"))
            self.assertEqual(
                sorted(p.name for p in instructions.parent.iterdir()),
                ["codex-home", "instructions.md"],
            )
            return subprocess.CompletedProcess(
                command, 0,
                stdout=(CODEX_FIXTURES / "exec-events.jsonl").read_text(encoding="utf-8"),
                stderr="",
            )

        chat = clients.build_client_chat_fn("cli-codex:gpt-6-astra", None, "x", run=run)
        for system in ("Long original instructions: 水", "Short", ""):
            chat([("system", system), ("user", "u")])
        self.assertEqual(observed, ["Long original instructions: 水", "Short", ""])

    def test_message_without_completed_turn_is_refused_without_recording_usage(self) -> None:
        events = (CODEX_FIXTURES / "exec-events.jsonl").read_text(encoding="utf-8")
        incomplete = "\n".join(events.splitlines()[:-1])

        def run(command, **kwargs):
            return subprocess.CompletedProcess(command, 0, stdout=incomplete, stderr="")

        sink: dict = {}
        chat = clients.build_client_chat_fn("cli-codex:gpt-6-astra", sink, "x", run=run)
        with self.assertRaisesRegex(RuntimeError, "x:.*turn.completed"):
            chat([("system", "s"), ("user", "u")])
        self.assertEqual(sink, {})

    def test_malformed_stream_is_refused_even_with_a_message_and_completion(self) -> None:
        events = (CODEX_FIXTURES / "exec-events.jsonl").read_text(encoding="utf-8")
        for malformed in ("not JSON", '{"type":"error",', "[]"):
            with self.subTest(malformed=malformed):
                with self.assertRaisesRegex(RuntimeError, "x:.*codex.*event"):
                    clients._parse_codex_events("x", events + malformed + "\n")

    def test_failure_after_a_message_overrides_success(self) -> None:
        events = (CODEX_FIXTURES / "exec-events.jsonl").read_text(encoding="utf-8")
        failures = (
            {"type": "error", "message": "quota"},
            {"type": "turn.failed", "error": {"message": "quota"}},
        )
        for failure in failures:
            for prefix in (events, "\n".join(events.splitlines()[:-1]) + "\n"):
                with self.subTest(failure=failure, prefix=prefix):
                    with self.assertRaisesRegex(RuntimeError, "x:.*quota"):
                        clients._parse_codex_events("x", prefix + json.dumps(failure))

    def test_last_message_wins_and_unknown_events_and_blank_lines_are_ignored(self) -> None:
        events = (CODEX_FIXTURES / "exec-events.jsonl").read_text(encoding="utf-8")
        commentary = json.dumps({"type": "item.completed", "item": {
            "type": "agent_message", "text": "Checking the question."
        }})
        text, usage = clients._parse_codex_events(
            "x", '\n' + commentary + '\n{"type":"future.event"}\n' + events + '\n'
        )
        self.assertEqual(text, "pong")
        self.assertEqual(usage["input_tokens"], 9345)

    def test_error_event_and_missing_message_are_errors(self) -> None:
        with self.assertRaises(RuntimeError) as ctx:
            clients._parse_codex_events("x", '{"type":"error","message":"quota"}\n')
        self.assertIn("quota", str(ctx.exception))
        with self.assertRaises(RuntimeError) as ctx:
            clients._parse_codex_events("x", '{"type":"turn.completed","usage":{}}\n')
        self.assertIn("no agent message", str(ctx.exception))

    def test_api_keys_never_reach_codex(self) -> None:
        with patch.dict(os.environ, {"OPENAI_API_KEY": "sk-test", "CODEX_API_KEY": "k"}):
            chat = build_chat_fn("cli-codex:gpt-6-astra", None, label="x")
            chat([("system", "s"), ("user", "u")])
        self.assertTrue(all(c["key_vars"] == [] for c in self.calls()), self.calls())


class AntigravityCallTests(FakeClientMixin, unittest.TestCase):
    def test_command_line_and_prepended_system_prompt(self) -> None:
        chat = build_chat_fn("cli-antigravity:gemini-3.8-flash-high", None, label="x")
        reply = chat([("system", "You are the SYNTHESIZER."), ("user", "Synthesize.")])
        self.assertEqual(reply, "answer from gemini-3.8-flash-high")
        call = self.calls()[-1]
        argv = call["argv"]
        self.assertEqual(argv[argv.index("--model") + 1], "gemini-3.8-flash-high")
        self.assertEqual(argv[argv.index("--output-format") + 1], "json")
        self.assertIn("--sandbox", argv)
        self.assertNotIn("--print", argv)
        self.assertNotIn("--effort", argv)
        self.assertEqual(call["stdin"], "You are the SYNTHESIZER.\n\nSynthesize.")

    def test_antigravity_runs_with_a_private_home_and_its_own_settings(self) -> None:
        real_config = Path(self._tmp.name) / "real-home" / ".gemini" / "antigravity-cli"
        real_config.mkdir(parents=True)
        (real_config / "antigravity-oauth-token").write_text("token", encoding="utf-8")
        (real_config / "settings.json").write_text(
            '{"toolPermission": "always-proceed", "permissions": {"allow": ["command(*)"]}}',
            encoding="utf-8",
        )
        with patch.dict(os.environ, {"HOME": str(Path(self._tmp.name) / "real-home")}):
            chat = build_chat_fn("cli-antigravity:gemini-3.8-flash-high", None, label="x")
            chat([("system", "s"), ("user", "u")])
        call = self.calls()[-1]
        home = Path(call["home"])
        self.assertEqual(home.parent.resolve(), Path(call["cwd"]).resolve())
        config = home / ".gemini" / "antigravity-cli"
        self.assertEqual(sorted(p.name for p in config.iterdir()),
                         ["antigravity-oauth-token", "settings.json"])
        self.assertEqual((config / "antigravity-oauth-token").resolve(),
                         (real_config / "antigravity-oauth-token").resolve())
        settings = json.loads((config / "settings.json").read_text(encoding="utf-8"))
        self.assertEqual(settings["toolPermission"], "always-proceed")
        self.assertEqual(settings["permissions"]["allow"], ["read_url(*)"])
        self.assertIn("command(*)", settings["permissions"]["deny"])

    def test_empty_response_is_an_error_carrying_stderr(self) -> None:
        empty = json.dumps({**ANTIGRAVITY_RESULT, "response": ""})

        def run(command, **kwargs):
            return subprocess.CompletedProcess(
                command, 0, stdout=empty, stderr="jetski: no output produced — auto-denied"
            )

        sink: dict = {}
        chat = clients.build_client_chat_fn(
            "cli-antigravity:gemini-3.8-flash-high", sink, "g", run=run
        )
        with self.assertRaises(RuntimeError) as ctx:
            chat([("system", "s"), ("user", "u")])
        self.assertIn("auto-denied", str(ctx.exception))
        self.assertEqual(sink, {})

    def test_grounding_links_are_counted_as_browsing_evidence(self) -> None:
        marker = clients.ANTIGRAVITY_GROUNDING_MARKER
        os.environ["FAKE_CLAUDE_REPLY"] = (
            f"Price $1. [a](https://{marker}/x) [b](https://{marker}/y)"
        )
        sink: dict = {}
        chat = build_chat_fn(
            "cli-antigravity:gemini-3.8-flash-high", None, usage_sink=sink, label="g"
        )
        chat([("system", "s"), ("user", "u")])
        self.assertEqual(sink["g"]["grounding_links"], 2)

    def test_base_id_gets_the_default_effort(self) -> None:
        chat = build_chat_fn("cli-antigravity:gemini-3.8-flash", None, label="x")
        chat([("system", "s"), ("user", "u")])
        argv = self.calls()[-1]["argv"]
        self.assertEqual(argv[argv.index("--effort") + 1], "high")

    def test_usage_and_turns_are_recorded_as_reported(self) -> None:
        sink: dict = {}
        chat = build_chat_fn(
            "cli-antigravity:gemini-3.8-flash-high", None, usage_sink=sink, label="g"
        )
        chat([("system", "s"), ("user", "u")])
        entry = sink["g"]
        self.assertEqual(entry["input_tokens"], ANTIGRAVITY_RESULT["usage"]["input_tokens"])
        self.assertEqual(entry["thinking_tokens"], ANTIGRAVITY_RESULT["usage"]["thinking_tokens"])
        self.assertEqual(entry["num_turns"], 1)
        self.assertEqual(entry["grounding_links"], 0)

    def test_error_status_is_an_error_naming_the_client(self) -> None:
        error = (ANTIGRAVITY_FIXTURES / "print-error.json").read_text(encoding="utf-8")

        def run(command, **kwargs):
            return subprocess.CompletedProcess(command, 0, stdout=error, stderr="")

        sink: dict = {}
        chat = clients.build_client_chat_fn(
            "cli-antigravity:gemini-3.8-flash", sink, "x", run=run
        )
        with self.assertRaises(RuntimeError) as ctx:
            chat([("system", "s"), ("user", "u")])
        self.assertIn("requires --effort", str(ctx.exception))
        self.assertIn("antigravity", str(ctx.exception))
        self.assertEqual(sink, {})

    def test_model_ids_parse_from_the_listing(self) -> None:
        listing = (ANTIGRAVITY_FIXTURES / "models.txt").read_text(encoding="utf-8")
        ids = clients.antigravity_model_ids(listing)
        self.assertIn("gemini-3.8-flash-high", ids)
        self.assertIn("gpt-oss-120b-medium", ids)
        self.assertNotIn("Fetching", " ".join(ids))

    def test_api_keys_never_reach_antigravity(self) -> None:
        with patch.dict(os.environ, {"GEMINI_API_KEY": "g", "GOOGLE_API_KEY": "g"}):
            chat = build_chat_fn("cli-antigravity:gemini-3.8-flash-high", None, label="x")
            chat([("system", "s"), ("user", "u")])
        self.assertTrue(all(c["key_vars"] == [] for c in self.calls()), self.calls())


class NoBrowseRoleTests(FakeClientMixin, unittest.TestCase):
    """The last synthesizer passes browse=False; clients that can honor it do."""

    def test_claude_without_browsing_gets_no_web_tools(self) -> None:
        chat = build_chat_fn("cli-claude:claude-fable-5-1", None, browse=False, label="j")
        chat([("system", "s"), ("user", "u")])
        argv = self.calls()[-1]["argv"]
        self.assertEqual(argv[argv.index("--tools") + 1], "")
        self.assertEqual(argv[argv.index("--allowedTools") + 1], "")

    def test_codex_without_browsing_disables_search_and_rejects_a_search_item(self) -> None:
        chat = build_chat_fn("cli-codex:gpt-6-astra", None, browse=False, label="j")
        chat([("system", "s"), ("user", "u")])
        argv = [c for c in self.calls() if c["argv"][:1] == ["exec"]][-1]["argv"]
        self.assertIn('web_search="disabled"', argv)
        self.assertNotIn('web_search="live"', argv)
        events = (CODEX_FIXTURES / "exec-events-browse.jsonl").read_text(encoding="utf-8")
        with self.assertRaisesRegex(RuntimeError, "used a tool.*web_search"):
            clients._parse_codex_events("j", events, browse=False)

    def test_antigravity_is_refused_in_a_no_browse_role(self) -> None:
        with self.assertRaises(SystemExit) as ctx:
            build_chat_fn("cli-antigravity:gemini-3.8-flash-high", None, browse=False, label="j")
        self.assertIn("browsing off", str(ctx.exception))
        self.assertEqual(self.calls()[-1]["argv"], ["models"])

    def test_main_lineup_browses_whatever_the_flag_says(self) -> None:
        specs = parse_engine_args("cli-claude-fable-5-1,cli-gpt-6-astra,cli-gemini-3.8-flash")
        engines = build_engines(specs, None, {}, browse=False)
        engines["cli-claude-fable-5-1"]([("system", "s"), ("user", "u")])
        argv = self.calls()[-1]["argv"]
        self.assertEqual(argv[argv.index("--tools") + 1], "WebSearch,WebFetch")

    def test_client_last_synthesizer_runs_without_browsing_end_to_end(self) -> None:
        os.environ["FAKE_CLAUDE_REPLY"] = ENGINE_REPLY
        out = Path(self._tmp.name) / "debate.md"
        code = main([
            "ask", "q?",
            "--engines", "cli-claude-fable-5-1,cli-claude-sonnet-5,cli-claude-opus-5",
            "--add-last-synthesizer", "cli-gpt-6-astra", "--out", str(out),
        ])
        self.assertEqual(code, 0)
        judge = [c for c in self.calls() if c["argv"][:1] == ["exec"]]
        self.assertEqual(len(judge), 1)
        self.assertIn('web_search="disabled"', judge[0]["argv"])


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

    def test_full_debate_across_the_three_clients(self) -> None:
        os.environ["FAKE_CLAUDE_REPLY"] = ENGINE_REPLY
        out = Path(self._tmp.name) / "debate.md"
        code = main([
            "ask", "Is water wet?",
            "--engines", "cli-claude-fable-5-1,cli-gpt-6-astra,cli-gemini-3.8-flash",
            "--out", str(out),
        ])
        self.assertEqual(code, 0)
        text = out.read_text(encoding="utf-8")
        self.assertIn('"cli-gpt-6-astra": "cli-codex:gpt-6-astra"', text)
        self.assertIn('"cli-gemini-3.8-flash": "cli-antigravity:gemini-3.8-flash"', text)
        self.assertIn('"cli-claude-fable-5-1": "cli-claude:claude-fable-5-1"', text)
        self.assertIn("state=", "state=")  # the CLI printed; transcript has the state below
        self.assertIn("synthesizer_meta:", text)
        clients_used = {c.get("client", "claude") for c in self.calls()}
        self.assertEqual(clients_used, {"claude", "codex", "antigravity"})


if __name__ == "__main__":
    unittest.main()
