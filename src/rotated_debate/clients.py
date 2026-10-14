"""Engines reached through a vendor's signed-in command-line client.

Owner decision 2026-10-14 (cli-engines workstream, decisions 1 to 5): an
`--engines` item `cli-<model>` means the model `<model>`, by its vendor's
full id, reached through that vendor's default command-line client with
the sign-in already present in the environment. No key is read, written
or mentioned anywhere on this path. The client is called as a chat engine
on the prompt alone: the protocol's system message is the whole system
prompt, the user message is the prompt, no tools, no session, no
repository access. The protocol, parsing and transcript modules do not
know this module exists; `engines.py` dispatches here.

Only the `claude` client is implemented in this slice. `codex` and
`antigravity` resolve, so that the lineup grammar is final, but stop before
any call with a message naming the slice that adds them.
"""

from __future__ import annotations

import json
import os
import shutil
import subprocess
from collections.abc import Callable, Mapping

from rotated_debate import prompts

CLI_PREFIX = "cli-"

# Vendor (as engines.infer_provider names it) -> that vendor's default client.
CLIENT_FOR_PROVIDER = {
    "anthropic": "claude",
    "openai": "codex",
    "google_genai": "antigravity",
}
IMPLEMENTED_CLIENTS = {"claude"}
PLANNED_SLICE = {"codex": "slice 2", "antigravity": "slice 3"}

# Seconds a single client call may take before it is reported as a failure.
TIMEOUT_ENV = "ROTATED_DEBATE_CLIENT_TIMEOUT"
DEFAULT_TIMEOUT = 600.0

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
            f"gpt-* or o<digit>*"
        )
    return f"{CLI_PREFIX}{CLIENT_FOR_PROVIDER[provider]}:{model}"


def split_client_model_id(model_id: str) -> tuple[str, str]:
    """`cli-<client>:<model>` -> (client, model)."""
    provider, _, model = model_id.partition(":")
    return provider[len(CLI_PREFIX) :], model


def is_client_model_id(model_id: str) -> bool:
    return model_id.startswith(CLI_PREFIX) and ":" in model_id


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


def check_available(model_id: str, run: Runner = subprocess.run) -> None:
    """Refuse, before any model call, unless the client is implemented, present
    and signed in. The refusal names the client and what would fix it."""
    client, _ = split_client_model_id(model_id)
    if client not in IMPLEMENTED_CLIENTS:
        raise SystemExit(
            f"{model_id!r}: the {client!r} client is not available yet; it arrives in "
            f"{PLANNED_SLICE.get(client, 'a later slice')} of the cli-engines workstream"
        )
    executable = _executable(client)
    if client == "claude":
        _check_claude_signed_in(executable, run)


def _check_claude_signed_in(executable: str, run: Runner) -> None:
    try:
        completed = run(
            [executable, "auth", "status"],
            capture_output=True,
            text=True,
            encoding="utf-8",
            timeout=60,
            check=False,
        )
    except subprocess.TimeoutExpired as exc:
        raise SystemExit(
            "the 'claude' client sign-in check did not finish within 60s; "
            "check `claude auth status` and rerun"
        ) from exc
    except OSError as exc:
        raise SystemExit(
            f"could not run the 'claude' client sign-in check: {exc}; "
            "check the client installation and rerun"
        ) from exc
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


def claude_command(executable: str, model: str, system_prompt: str) -> list[str]:
    """The exact call, probed against claude 2.1.261 on 2026-10-14.

    The prompt travels on stdin so a large context packet never hits the
    argument-length limit. `--system-prompt` replaces the client's own agent
    prompt (about 20,000 tokens otherwise); `--tools ""` leaves it no tools;
    `--setting-sources ""` ignores every settings file, so the repository's
    own agent configuration never shapes an engine; `--no-session-persistence`
    writes nothing to disk.
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
        "",
        "--no-session-persistence",
        "--setting-sources",
        "",
    ]


def _parse_claude_result(label: str, stdout: str) -> tuple[str, Mapping[str, object]]:
    try:
        report = json.loads(stdout)
    except json.JSONDecodeError as exc:
        raise RuntimeError(
            f"{label}: the claude client did not return JSON: {stdout[:200]!r}"
        ) from exc
    if not isinstance(report, Mapping):
        raise RuntimeError(f"{label}: unexpected claude client output: {stdout[:200]!r}")
    if report.get("is_error") or report.get("subtype") != "success":
        raise RuntimeError(
            f"{label}: the claude client reported {report.get('subtype')!r}: "
            f"{str(report.get('result', ''))[:500]}"
        )
    text = report.get("result")
    if not isinstance(text, str):
        raise RuntimeError(f"{label}: the claude client returned no result text")
    return text, report


def claude_usage(report: Mapping[str, object]) -> dict[str, object]:
    """What the client reports, as it reports it: the token fields of `usage`,
    the call's dollar cost under the subscription, and the turn count. Nested
    details are left to `record_server_tool_use`; nothing is normalized."""
    usage: dict[str, object] = {}
    reported = report.get("usage")
    if isinstance(reported, Mapping):
        usage.update(reported)
    for key in ("total_cost_usd", "num_turns"):
        if key in report:
            usage[key] = report[key]
    return usage


def build_client_chat_fn(
    model_id: str,
    usage_sink: dict[str, dict[str, int | float]] | None,
    label: str,
    run: Runner = subprocess.run,
) -> Callable[[list[prompts.Message]], str]:
    """A ChatFn that runs the client once per call. `check_available` has
    already refused anything that cannot run."""
    from rotated_debate.engines import record_server_tool_use, record_usage

    client, model = split_client_model_id(model_id)
    executable = _executable(client)
    timeout = _timeout()

    def chat(messages: list[prompts.Message]) -> str:
        system_prompt, prompt = _split_messages(messages)
        command = claude_command(executable, model, system_prompt)
        try:
            completed = run(
                command,
                input=prompt,
                capture_output=True,
                text=True,
                encoding="utf-8",
                timeout=timeout,
                check=False,
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
        text, report = _parse_claude_result(label, completed.stdout)
        if usage_sink is not None:
            usage = claude_usage(report)
            record_usage(usage_sink, label, usage)
            record_server_tool_use(usage_sink, label, {"usage": usage})
        return text

    return chat
