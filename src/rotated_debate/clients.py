"""Engines reached through a vendor's signed-in command-line client.

Owner decision 2026-10-14 (cli-engines workstream, decisions 1 to 5): an
`--engines` item `cli-<model>` means the model `<model>`, by its vendor's
full id, reached through that vendor's default command-line client with
the sign-in already present in the environment. No key is read, written
or mentioned anywhere on this path. The client is called as a chat engine
on the prompt alone: the protocol's system message is the engine's whole
instruction where the client can take one, the user message is the
prompt, no tools of ours, no session, no repository access. The protocol,
parsing and transcript modules do not know this module exists;
`engines.py` dispatches here.

Three clients, one per vendor, probed on 2026-10-14 and 2026-10-15:

- `claude` 2.1.261 (Anthropic): `-p`, JSON result, `--system-prompt`
  replaces its agent prompt, `--tools ""`, no MCP, no settings files.
- `codex` 0.153.4 (OpenAI): `exec --json`, a replacement instructions
  file carries the system prompt, read-only sandbox, ephemeral, a private
  `CODEX_HOME` holding only a link to the sign-in file so that no global
  instructions, user config, MCP servers or rules reach the engine.
- `antigravity` 1.1.24 (Google): prompt on stdin, JSON result; it has no
  instruction flag, so the system prompt is prepended to the prompt; its
  model ids carry an effort level and one is added when the id has none.

Each runs in an empty directory of its own, with the vendors' key
variables removed from its environment, after its own sign-in report has
been checked.

Browsing is on by default on this route (owner direction 2026-10-15; a
later slice adds the switch to turn it off): `claude` with its WebSearch
and WebFetch tools allowed, `codex` with `web_search="live"`, and
`antigravity` through the Google Search grounding its account setting
enables, plus URL reads. Each client's evidence of browsing is recorded as
usage: search counts where the client reports them, grounding links
counted in the answer where it does not.
"""

from __future__ import annotations

import json
import os
import shutil
import subprocess
import tempfile
from collections.abc import Callable, Mapping
from pathlib import Path

from rotated_debate import prompts

CLI_PREFIX = "cli-"

# Vendor (as engines.infer_provider names it) -> that vendor's default client.
CLIENT_FOR_PROVIDER = {
    "anthropic": "claude",
    "openai": "codex",
    "google_genai": "antigravity",
}
IMPLEMENTED_CLIENTS = {"claude", "codex", "antigravity"}

# Seconds a single client call may take before it is reported as a failure.
TIMEOUT_ENV = "ROTATED_DEBATE_CLIENT_TIMEOUT"
DEFAULT_TIMEOUT = 600.0

# Direct credentials, custom headers that can carry one, and the selectors
# of the cloud-provider routes that bill a cloud account instead of the
# sign-in, for every vendor. Removed from every client subprocess, sign-in
# check included. Credentials supplied by managed settings are outside this
# module's reach; the sign-in checks below read what each client itself
# reports and refuse any route other than the vendor's sign-in.
KEY_VARIABLES = (
    "ANTHROPIC_API_KEY",
    "ANTHROPIC_AUTH_TOKEN",
    "ANTHROPIC_CUSTOM_HEADERS",
    "CLAUDE_CODE_USE_BEDROCK",
    "CLAUDE_CODE_USE_VERTEX",
    "CLAUDE_CODE_USE_FOUNDRY",
    "AWS_BEARER_TOKEN_BEDROCK",
    "OPENAI_API_KEY",
    "CODEX_API_KEY",
    "GEMINI_API_KEY",
    "GOOGLE_API_KEY",
)
# What `claude auth status` reports for the claude.ai sign-in, recorded in
# tests/fixtures/claude-client/auth-status.json.
CLAUDE_SIGNED_IN = {"authMethod": "claude.ai", "apiProvider": "firstParty"}
# What `codex login status` prints for the ChatGPT sign-in.
CODEX_SIGNED_IN = "Logged in using ChatGPT"
# Antigravity model ids end in their effort level; one is added otherwise.
ANTIGRAVITY_EFFORTS = ("low", "medium", "high")
ANTIGRAVITY_DEFAULT_EFFORT = "high"
# Antigravity's settings and sign-in token live at a fixed path under the
# home directory; the call runs with a private home holding a link to the
# token and these settings, so the owner's own permissions (which may allow
# every tool unprompted) never reach the engine. Google Search grounding is
# a model-side feature governed by an account-level setting, not by these
# permissions: a deny-everything file still produced grounded answers. URL
# reads are allowed so the model can open what it finds. `always-proceed`
# with a deny list is the mode that works headless: under `strict` the
# client auto-denied the URL read despite the allow rule and returned an
# empty answer, while the deny list held under `always-proceed` (a shell
# command was refused with the model saying so).
ANTIGRAVITY_SETTINGS = {
    "toolPermission": "always-proceed",
    "permissions": {
        "allow": ["read_url(*)"],
        "deny": ["command(*)", "execute_url(*)", "mcp(*)", "write_file(*)"],
    },
    "trustedWorkspaces": [],
}
ANTIGRAVITY_CONFIG_DIR = (".gemini", "antigravity-cli")
ANTIGRAVITY_TOKEN_FILE = "antigravity-oauth-token"
# A grounded answer cites Google's grounding redirect service; counting the
# links is the only browsing evidence this client gives.
ANTIGRAVITY_GROUNDING_MARKER = "vertexaisearch.cloud.google.com/grounding-api-redirect"
# Files whose presence in an ancestor directory means a client would load
# instructions from there; the empty working directory must have none.
INSTRUCTION_MARKERS = ("CLAUDE.md", ".claude", "AGENTS.md", ".codex")
# Codex event items the engine accepts: the model talking, and the hosted
# web search it is allowed. Any other item is a tool the engine did not
# grant, and fails the call rather than letting a tool-assisted answer pass
# as a chat answer.
CODEX_TALK_ITEMS = {"agent_message", "reasoning", "web_search"}
CODEX_HOME_ENV = "CODEX_HOME"
# Codex configuration, probed on 2026-10-15 against 0.153.4: `web_search`
# takes `disabled`, `cached` (the default, an OpenAI-maintained index),
# `indexed` or `live`; `live` is unrestricted retrieval and is what browsing
# means here. `tools.web_search=false` does nothing. The feature switches
# remove every built-in tool, the shell and the built-in apps MCP server
# included (with the search off, the model reached for that server), so the
# only tool left is the search. The prompt shrinks from about 9,400 to
# about 4,600 input tokens without the tool descriptions.
CODEX_SETTINGS = (
    'web_search="live"',
    "features.apps=false",
    "features.browser_use=false",
    "features.browser_use_external=false",
    "features.computer_use=false",
    "features.shell_tool=false",
    "features.multi_agent=false",
    "features.image_generation=false",
    "features.plugins=false",
    "features.remote_plugin=false",
    "features.skill_search=false",
    "features.tool_suggest=false",
    "features.goals=false",
    "features.hooks=false",
)

Runner = Callable[..., "subprocess.CompletedProcess[str]"]


def is_client_item(item: str) -> bool:
    return item.startswith(CLI_PREFIX)


def client_model_id(item: str, infer_provider: Callable[[str], str | None]) -> str:
    """`cli-<model>` -> `cli-<client>:<model>`, the transcript's provider:model form.

    The vendor is inferred from the model name's shape by the same rule bare
    names use; the client per vendor is the table above.
    """
    model = item[len(CLI_PREFIX) :]
    provider = infer_provider(model) if model else None
    if provider is None or provider not in CLIENT_FOR_PROVIDER:
        raise ValueError(
            f"{item!r}: cannot tell which client serves {model!r}; the name after "
            f"{CLI_PREFIX!r} must be a full model id shaped like claude-*, gemini-*, "
            f"gpt-* or o<digit>* (vendor aliases such as 'chatgpt' are API-route names)"
        )
    return f"{CLI_PREFIX}{CLIENT_FOR_PROVIDER[provider]}:{model}"


def split_client_model_id(model_id: str) -> tuple[str, str]:
    """`cli-<client>:<model>` -> (client, model)."""
    provider, _, model = model_id.partition(":")
    return provider[len(CLI_PREFIX) :], model


def is_client_model_id(model_id: str) -> bool:
    return model_id.startswith(CLI_PREFIX) and ":" in model_id


def client_env() -> dict[str, str]:
    return {key: value for key, value in os.environ.items() if key not in KEY_VARIABLES}


def _timeout() -> float:
    raw = os.environ.get(TIMEOUT_ENV)
    return float(raw) if raw else DEFAULT_TIMEOUT


def _executable(client: str) -> str:
    path = shutil.which(client)
    if path is None:
        raise SystemExit(
            f"the {client!r} command-line client is not on PATH; install it and sign in, "
            f"or use the API route for this engine"
        )
    return path


def _run_status(client: str, command: list[str], run: Runner) -> subprocess.CompletedProcess[str]:
    try:
        return run(
            command,
            stdin=subprocess.DEVNULL,
            capture_output=True,
            text=True,
            encoding="utf-8",
            timeout=60,
            check=False,
            env=client_env(),
        )
    except subprocess.TimeoutExpired as exc:
        raise SystemExit(
            f"the {client!r} client sign-in check did not finish within 60s; "
            f"run `{' '.join(command[1:])}` yourself and rerun"
        ) from exc
    except OSError as exc:
        raise SystemExit(
            f"could not run the {client!r} client sign-in check: {exc}; "
            f"check the client installation and rerun"
        ) from exc


def check_available(model_id: str, run: Runner = subprocess.run) -> None:
    """Refuse, before any model call, unless the client is implemented, present
    and signed in through its vendor's sign-in, and (for antigravity) lists
    the model. The refusal names the client and what would fix it."""
    client, model = split_client_model_id(model_id)
    if client not in IMPLEMENTED_CLIENTS:
        raise SystemExit(f"{model_id!r}: no runner exists for the {client!r} client")
    executable = _executable(client)
    if client == "claude":
        _check_claude_signed_in(executable, run)
    elif client == "codex":
        _check_codex_signed_in(executable, run)
    else:
        _check_antigravity_signed_in(executable, model, run)


def _check_claude_signed_in(executable: str, run: Runner) -> None:
    completed = _run_status("claude", [executable, "auth", "status"], run)
    status: Mapping[str, object] = {}
    try:
        parsed = json.loads(completed.stdout or "{}")
        if isinstance(parsed, Mapping):
            status = parsed
    except json.JSONDecodeError:
        status = {}
    if completed.returncode != 0 or status.get("loggedIn") is not True:
        raise SystemExit(
            "the 'claude' client is not signed in; run `claude` once and sign in "
            "(no API key is read on this route), then rerun"
        )
    found = {key: status.get(key) for key in CLAUDE_SIGNED_IN}
    if found != CLAUDE_SIGNED_IN:
        raise SystemExit(
            f"the 'claude' client reports {found} where the claude.ai sign-in "
            f"reports {CLAUDE_SIGNED_IN}; this route uses only the sign-in, so sign in "
            f"through claude.ai or use the API route for this engine"
        )


def _check_codex_signed_in(executable: str, run: Runner) -> None:
    completed = _run_status("codex", [executable, "login", "status"], run)
    report = (completed.stdout + completed.stderr).strip()
    if completed.returncode != 0 or CODEX_SIGNED_IN not in report:
        raise SystemExit(
            f"the 'codex' client is not signed in through ChatGPT (it reports "
            f"{report[:120]!r}); run `codex login` and sign in with ChatGPT, then rerun"
        )


def antigravity_model_ids(listing: str) -> list[str]:
    """Ids from `antigravity models`: the first field of each listing line."""
    ids = []
    for line in listing.splitlines():
        fields = line.split("\t")
        first = fields[0].strip()
        if first and len(fields) > 1 and " " not in first:
            ids.append(first)
    return ids


def _antigravity_candidates(model: str) -> list[str]:
    if model.endswith(tuple(f"-{effort}" for effort in ANTIGRAVITY_EFFORTS)):
        return [model]
    # Match the exact id or the effort the command will actually request.
    return [model, f"{model}-{ANTIGRAVITY_DEFAULT_EFFORT}"]


def _check_antigravity_signed_in(executable: str, model: str, run: Runner) -> None:
    completed = _run_status("antigravity", [executable, "models"], run)
    ids = antigravity_model_ids(completed.stdout)
    if completed.returncode != 0 or not ids:
        raise SystemExit(
            "the 'antigravity' client is not signed in or lists no models; run "
            "`antigravity` once and sign in, then rerun"
        )
    if not any(candidate in ids for candidate in _antigravity_candidates(model)):
        raise SystemExit(
            f"the 'antigravity' client does not list {model!r}; it lists: "
            + ", ".join(ids)
        )


def _split_messages(messages: list[prompts.Message]) -> tuple[str, str]:
    """The protocol sends one system message and one user message per call."""
    system_parts: list[str] = []
    user_parts: list[str] = []
    for role, content in messages:
        if role == "system":
            system_parts.append(content)
        elif role == "user":
            user_parts.append(content)
        else:
            raise ValueError(
                f"client engines take single-turn messages; got a {role!r} message"
            )
    return "\n\n".join(system_parts), "\n\n".join(user_parts)


def _instruction_free_directory() -> tempfile.TemporaryDirectory[str]:
    """An empty directory of our own with no instruction file in any
    ancestor, so a client loads no instructions from the file system. The
    temporary root follows `TMPDIR`; one pointed inside a project would
    defeat the isolation, so that is refused rather than silently accepted."""
    workdir = tempfile.TemporaryDirectory(prefix="rotated-debate-client-")
    path = Path(workdir.name).resolve()
    for ancestor in path.parents:
        for marker in INSTRUCTION_MARKERS:
            if (ancestor / marker).exists():
                workdir.cleanup()
                raise SystemExit(
                    f"the temporary directory {path} sits under {ancestor}, which "
                    f"carries {marker}; the client would load instructions from "
                    f"there. Point TMPDIR at a directory outside any project"
                )
    return workdir


# ---- claude ---------------------------------------------------------------


def claude_command(executable: str, model: str, system_prompt: str) -> list[str]:
    """The exact call, probed against claude 2.1.261 on 2026-10-14 and 15.

    The prompt travels on stdin so a large context packet never hits the
    argument-length limit. `--system-prompt` replaces the client's own agent
    prompt (about 20,000 tokens otherwise); `--tools "WebSearch,WebFetch"`
    leaves it exactly its two web tools and `--allowedTools` the same two
    lets them run without a permission prompt, which print mode cannot
    answer (named in `--tools` alone, the model reported the permission as
    not granted); `--strict-mcp-config` with no `--mcp-config` leaves it
    no MCP servers; `--setting-sources ""` ignores the user, project and
    local settings files; `--no-session-persistence` saves no session. The
    call also runs in an empty working directory with no instruction files
    in any ancestor (see `_instruction_free_directory`) because the client
    discovers `CLAUDE.md` from its working directory and its ancestors
    regardless of setting sources: measured 805 input tokens from this
    repository against 417 from an empty directory for the same prompt, a
    measurement on this version, not a guarantee. Managed (organization)
    settings are outside these flags' reach.
    """
    return [
        executable,
        "-p",
        "--output-format",
        "json",
        "--model",
        model,
        "--system-prompt",
        system_prompt,
        "--tools",
        "WebSearch,WebFetch",
        "--allowedTools",
        "WebSearch,WebFetch",
        "--no-session-persistence",
        "--setting-sources",
        "",
        "--strict-mcp-config",
    ]


def _parse_claude_result(label: str, stdout: str) -> tuple[str, dict[str, object]]:
    report = _load_json_object(label, "claude", stdout)
    if report.get("is_error") or report.get("subtype") != "success":
        raise RuntimeError(
            f"{label}: the claude client reported {report.get('subtype')!r}: "
            f"{str(report.get('result', ''))[:500]}"
        )
    text = report.get("result")
    if not isinstance(text, str):
        raise RuntimeError(f"{label}: the claude client returned no result text")
    return text, claude_usage(report)


def claude_usage(report: Mapping[str, object]) -> dict[str, object]:
    """What the client reports, as it reports it: the token fields of `usage`,
    the client's reported dollar estimate, the turn count, and the web
    searches summed from `modelUsage` (the client's WebSearch tool is not
    the server-side search, so `usage.server_tool_use` stays at zero for
    it). Fetches have no counter; the turn count is their trace."""
    usage: dict[str, object] = {}
    reported = report.get("usage")
    if isinstance(reported, Mapping):
        usage.update(reported)
        usage.pop("server_tool_use", None)
    for key in ("total_cost_usd", "num_turns"):
        if key in report:
            usage[key] = report[key]
    per_model = report.get("modelUsage")
    if isinstance(per_model, Mapping):
        searches = 0
        for entry in per_model.values():
            if isinstance(entry, Mapping) and isinstance(entry.get("webSearchRequests"), int):
                searches += entry["webSearchRequests"]
        usage["web_search_requests"] = searches
    return usage


# ---- codex ----------------------------------------------------------------


def codex_command(executable: str, model: str, workdir: str, instructions: str) -> list[str]:
    """The exact call, probed against codex 0.153.4 on 2026-10-15.

    `exec` runs one turn and exits; `--json` streams events, the last of
    which carries token usage; `-` reads the prompt from stdin; `-C` sets
    the empty working directory and `--skip-git-repo-check` lets it run
    there; `-s read-only` is the tightest sandbox the client offers, and the
    directory is empty anyway; `--ephemeral` persists no session;
    `--ignore-rules` loads no execution-policy rules; `CODEX_SETTINGS`
    turns the hosted web search to live and removes every built-in tool,
    the shell included; `model_instructions_file` replaces the
    client's built-in instructions with the engine's system prompt (measured
    9,345 input tokens against 14,283 without, on this version). The client
    still reads `AGENTS.md` from its home directory whatever these say
    (measured: a planted marker was obeyed under `--ignore-user-config` and
    `project_doc_max_bytes=0` alike), so the call runs with a private
    `CODEX_HOME`; see `codex_home`. Should a tool item still appear in the
    event stream, the call fails rather than pass a tool-assisted answer.
    """
    command = [
        executable,
        "exec",
        "--json",
        "--ephemeral",
        "--skip-git-repo-check",
        "--ignore-rules",
        "-s",
        "read-only",
        "-C",
        workdir,
        "-m",
        model,
        "-c",
        f"model_instructions_file={instructions}",
    ]
    for setting in CODEX_SETTINGS:
        command += ["-c", setting]
    return command + ["-"]


def codex_home(workdir: str) -> Path:
    """A private home for the call: a directory under the engine's own with
    one entry, a link to the real home's sign-in file. The help says auth
    still uses `CODEX_HOME`, and a probe confirmed the sign-in holds through
    the link while the real home's `AGENTS.md`, `config.toml` (and so its
    MCP servers) and rules are not read. Nothing is copied; the client
    writes its caches here and they die with the directory."""
    real_home = Path(os.environ.get(CODEX_HOME_ENV) or Path.home() / ".codex")
    home = Path(workdir) / "codex-home"
    if not home.exists():
        home.mkdir()
        (home / "auth.json").symlink_to(real_home / "auth.json")
    return home


def _parse_codex_events(label: str, stdout: str) -> tuple[str, dict[str, object]]:
    """Use the last agent message only after a completed turn. Malformed
    events and explicit failures invalidate the response, even after text.
    Each `web_search` item is counted as the browsing evidence."""
    text: str | None = None
    usage: dict[str, object] = {}
    turn_completed = False
    searches = 0
    for line in stdout.splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            event = json.loads(line)
        except json.JSONDecodeError as exc:
            raise RuntimeError(f"{label}: the codex client returned an invalid JSON event") from exc
        if not isinstance(event, Mapping):
            raise RuntimeError(f"{label}: the codex client returned a non-object event")
        kind = event.get("type")
        if kind == "item.completed":
            item = event.get("item")
            item_type = item.get("type") if isinstance(item, Mapping) else None
            if item_type not in CODEX_TALK_ITEMS:
                raise RuntimeError(
                    f"{label}: the codex client used a tool ({item_type!r}); client "
                    f"engines are plain chat engines, so the call is not accepted"
                )
            if item_type == "agent_message" and isinstance(item.get("text"), str):
                text = item["text"]
            elif item_type == "web_search":
                searches += 1
        elif kind == "turn.completed":
            turn_completed = True
            reported = event.get("usage")
            if isinstance(reported, Mapping):
                usage.update(reported)
        elif kind in ("error", "turn.failed"):
            raise RuntimeError(
                f"{label}: the codex client reported an error: "
                f"{str(event.get('message', event.get('error', event)))[:500]}"
            )
    if text is None:
        raise RuntimeError(
            f"{label}: the codex client produced no agent message: {stdout[-300:]!r}"
        )
    if not turn_completed:
        raise RuntimeError(f"{label}: the codex client produced no turn.completed event")
    usage["web_search_requests"] = searches
    return text, usage


# ---- antigravity ----------------------------------------------------------


def antigravity_command(executable: str, model: str) -> list[str]:
    """The exact call, probed against antigravity 1.1.24 on 2026-10-15.

    The prompt travels on stdin, which selects print mode (the `--print`
    flag takes the prompt as its argument instead); `--output-format json`
    returns the response with usage; `--sandbox` restricts the terminal;
    an id without an effort suffix gets `--effort high`, since the client
    requires one. There is no instruction flag: the system prompt is
    prepended to the prompt, separated by a blank line, and the client's
    own agent prompt (about 14,600 tokens on this version) stays. The call
    runs with `HOME` set to a private home; see `antigravity_home`.
    """
    command = [executable, "--output-format", "json", "--model", model, "--sandbox"]
    if _antigravity_candidates(model) != [model]:
        command += ["--effort", ANTIGRAVITY_DEFAULT_EFFORT]
    return command


def antigravity_home(workdir: str) -> Path:
    """A private home for the call: the client's config directory holding a
    link to the real sign-in token and `ANTIGRAVITY_SETTINGS`. Probed: the
    sign-in held through the link and the settings were honored. The client
    writes its own state files here; they die with the directory."""
    real_config = Path.home().joinpath(*ANTIGRAVITY_CONFIG_DIR)
    home = Path(workdir) / "antigravity-home"
    config = home.joinpath(*ANTIGRAVITY_CONFIG_DIR)
    if not config.exists():
        config.mkdir(parents=True)
        (config / ANTIGRAVITY_TOKEN_FILE).symlink_to(real_config / ANTIGRAVITY_TOKEN_FILE)
        (config / "settings.json").write_text(
            json.dumps(ANTIGRAVITY_SETTINGS, indent=2) + "\n", encoding="utf-8"
        )
    return home


def _parse_antigravity_result(
    label: str, stdout: str, stderr: str = ""
) -> tuple[str, dict[str, object]]:
    report = _load_json_object(label, "antigravity", stdout)
    if report.get("status") != "SUCCESS":
        raise RuntimeError(
            f"{label}: the antigravity client reported {report.get('status')!r}: "
            f"{str(report.get('error', ''))[:500]}"
        )
    text = report.get("response")
    if not isinstance(text, str) or not text.strip():
        # The client reports SUCCESS with an empty response when a tool it
        # needed was auto-denied; the reason is on stderr.
        raise RuntimeError(
            f"{label}: the antigravity client returned no response text; "
            f"stderr: {stderr.strip()[-400:]!r}"
        )
    usage: dict[str, object] = {}
    reported = report.get("usage")
    if isinstance(reported, Mapping):
        usage.update(reported)
    if "num_turns" in report:
        usage["num_turns"] = report["num_turns"]
    usage["grounding_links"] = text.count(ANTIGRAVITY_GROUNDING_MARKER)
    return text, usage


# ---- shared ---------------------------------------------------------------


def _load_json_object(label: str, client: str, stdout: str) -> dict[str, object]:
    try:
        report = json.loads(stdout)
    except json.JSONDecodeError as exc:
        raise RuntimeError(
            f"{label}: the {client} client did not return JSON: {stdout[:200]!r}"
        ) from exc
    if not isinstance(report, Mapping):
        raise RuntimeError(f"{label}: unexpected {client} client output: {stdout[:200]!r}")
    return dict(report)


def build_client_chat_fn(
    model_id: str,
    usage_sink: dict[str, dict[str, int | float]] | None,
    label: str,
    run: Runner = subprocess.run,
) -> Callable[[list[prompts.Message]], str]:
    """A ChatFn that runs the client once per call. `check_available` has
    already refused anything that cannot run."""
    from rotated_debate.engines import record_usage

    client, model = split_client_model_id(model_id)
    executable = _executable(client)
    timeout = _timeout()
    # Removed when the engine is collected; see _instruction_free_directory.
    workdir = _instruction_free_directory()

    def chat(messages: list[prompts.Message]) -> str:
        system_prompt, prompt = _split_messages(messages)
        env = client_env()
        if client == "claude":
            command = claude_command(executable, model, system_prompt)
            stdin_text = prompt
        elif client == "codex":
            instructions = Path(workdir.name) / "instructions.md"
            instructions.write_text(system_prompt, encoding="utf-8")
            command = codex_command(executable, model, workdir.name, str(instructions))
            env[CODEX_HOME_ENV] = str(codex_home(workdir.name))
            stdin_text = prompt
        else:
            command = antigravity_command(executable, model)
            env["HOME"] = str(antigravity_home(workdir.name))
            stdin_text = f"{system_prompt}\n\n{prompt}" if system_prompt else prompt
        try:
            completed = run(
                command,
                input=stdin_text,
                capture_output=True,
                text=True,
                encoding="utf-8",
                timeout=timeout,
                check=False,
                env=env,
                cwd=workdir.name,
            )
        except subprocess.TimeoutExpired as exc:
            raise RuntimeError(
                f"{label}: the {client} client did not answer within {timeout:g}s "
                f"(set {TIMEOUT_ENV} to change the limit)"
            ) from exc
        if completed.returncode != 0:
            raise RuntimeError(
                f"{label}: the {client} client exited {completed.returncode}: "
                f"{(completed.stderr or completed.stdout).strip()[-500:]}"
            )
        if client == "claude":
            text, usage = _parse_claude_result(label, completed.stdout)
        elif client == "codex":
            text, usage = _parse_codex_events(label, completed.stdout)
        else:
            text, usage = _parse_antigravity_result(
                label, completed.stdout, completed.stderr or ""
            )
        if usage_sink is not None:
            record_usage(usage_sink, label, usage)
        return text

    chat.workdir = workdir  # type: ignore[attr-defined]  # keeps the directory alive
    return chat
