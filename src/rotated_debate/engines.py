"""LangChain-backed engine construction. The only module that touches
providers; imported lazily so the core stays dependency-free.

Access-route decision (2026-08-23): LangChain chat-model abstractions give
provider flexibility; model bindings are `provider:model` strings accepted
by `langchain.chat_models.init_chat_model`.
"""

from __future__ import annotations

import os
import re
from collections.abc import Mapping

from rotated_debate.model import EngineSpec
from rotated_debate.protocol import ChatFn

# The vendor aliases are the project's *curated pick* of each vendor's most
# capable model, pinned here and changed only by a deliberate commit (owner
# decision 2026-08-27, "Reading A"): what ran must be auditable in git log,
# never silently upgraded, because the evals ledger scores predictions
# across months. Staleness surfaces as a provider 404 on first use.
DEFAULT_MODELS = {
    "claude": "anthropic:claude-fable-5",
    "chatgpt": "openai:gpt-5.6-sol",
    "gemini": "google_genai:gemini-3.1-pro-preview",
}
ENV_PREFIX = "ROTATED_DEBATE_MODEL_"  # e.g. ROTATED_DEBATE_MODEL_CLAUDE

# Bare model names accepted directly in --engines; the provider is inferred
# from the name's shape. Anything else needs the explicit provider:model form.
MODEL_NAME_PATTERNS = (
    (re.compile(r"^claude-"), "anthropic"),
    (re.compile(r"^gemini-"), "google_genai"),
    (re.compile(r"^(gpt-|o\d)"), "openai"),
)


def infer_provider(model_name: str) -> str | None:
    for pattern, provider in MODEL_NAME_PATTERNS:
        if pattern.match(model_name):
            return provider
    return None


# Vendor-native, server-executed web-search tools (spec section 1: every
# engine gets its vendor's browse tooling). Search runs on the provider's
# side, so invoke() still returns a final answer - no tool loop here.
# max_uses bounds Anthropic search spend per call; the other providers do
# not expose an equivalent cap in the tool payload.
BROWSE_TOOLS: dict[str, list[dict[str, object]]] = {
    "anthropic": [{"type": "web_search_20260209", "name": "web_search", "max_uses": 5}],
    "openai": [{"type": "web_search"}],
    "google_genai": [{"google_search": {}}],
}


def browse_tools_for(model_id: str) -> list[dict[str, object]]:
    provider = model_id.partition(":")[0]
    if provider not in BROWSE_TOOLS:
        raise ValueError(
            f"no browse (web-search) tool known for provider {provider!r}; "
            f"supported: {', '.join(sorted(BROWSE_TOOLS))}"
        )
    return BROWSE_TOOLS[provider]


def parse_engine_args(raw: str) -> list[EngineSpec]:
    """Parse "claude,gemini,chatgpt" or "myname=provider:model" items."""
    specs: list[EngineSpec] = []
    for item in [part.strip() for part in raw.split(",") if part.strip()]:
        alias, _, binding = item.partition("=")
        specs.append(EngineSpec(alias=alias, provider_model=binding or None))
    aliases = [spec.alias for spec in specs]
    if len(set(aliases)) != len(aliases):
        raise ValueError(f"duplicate engine aliases in {raw!r}")
    return specs


def resolve_model_id(spec: EngineSpec) -> str:
    """Priority: env override > explicit binding > curated alias > name pattern."""
    env_override = os.environ.get(ENV_PREFIX + spec.alias.upper())
    if env_override:
        return env_override
    if spec.provider_model:
        return spec.provider_model
    if spec.alias in DEFAULT_MODELS:
        return DEFAULT_MODELS[spec.alias]
    provider = infer_provider(spec.alias)
    if provider:
        return f"{provider}:{spec.alias}"
    raise ValueError(
        f"engine {spec.alias!r} has no model binding; use a vendor alias "
        f"({', '.join(sorted(DEFAULT_MODELS))}), a model name matching "
        f"claude-*/gemini-*/gpt-*/o<digit>*, the alias=provider:model form, "
        f"or set {ENV_PREFIX}{spec.alias.upper()}"
    )


# Per-engine consumption totals. Units are whatever the provider reports —
# tokens for all current bindings, but nothing here assumes tokens: every
# top-level integer field of the provider's usage report is summed as-is.
UsageSink = dict[str, dict[str, int]]


def record_usage(sink: UsageSink, alias: str, usage: Mapping[str, object] | None) -> None:
    """Fold one call's usage report into the per-engine sink.

    Always counts the call; sums top-level integer fields (LangChain's
    usage_metadata: input_tokens, output_tokens, total_tokens); skips
    nested detail dicts and non-numeric fields.
    """
    entry = sink.setdefault(alias, {"calls": 0})
    entry["calls"] += 1
    if not usage:
        return
    for key, value in usage.items():
        if isinstance(value, int) and not isinstance(value, bool):
            entry[key] = entry.get(key, 0) + value


def record_server_tool_use(
    sink: UsageSink, alias: str, response_metadata: Mapping[str, object] | None
) -> None:
    """Fold server-side tool counts (e.g. web searches) into the sink.

    Searches are billed per search, separately from tokens. Reads the
    Anthropic-documented shape usage.server_tool_use.{*_requests}; other
    providers' shapes are folded in as their transcripts reveal them.
    """
    if not response_metadata:
        return
    usage = response_metadata.get("usage")
    if not isinstance(usage, Mapping):
        return
    server_tool_use = usage.get("server_tool_use")
    if not isinstance(server_tool_use, Mapping):
        return
    entry = sink.setdefault(alias, {"calls": 0})
    for key, value in server_tool_use.items():
        if isinstance(value, int) and not isinstance(value, bool):
            entry[key] = entry.get(key, 0) + value


def engine_labels(specs: list[EngineSpec]) -> dict[str, str]:
    """Alias -> reporting name: the bare model name, no provider prefix.

    Aliases stay the invocation-side interface (CLI, env overrides); all
    reporting (progress, transcript, usage) uses these labels. If two
    aliases resolve to the same model, every label falls back to
    "alias=model" so keys stay unique.
    """
    labels = {spec.alias: resolve_model_id(spec).rpartition(":")[2] for spec in specs}
    if len(set(labels.values())) != len(labels):
        labels = {alias: f"{alias}={label}" for alias, label in labels.items()}
    return labels


def _normalize_content(content: object) -> str:
    """LangChain content may be a string or a list of content blocks."""
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        parts: list[str] = []
        for block in content:
            if isinstance(block, str):
                parts.append(block)
            elif isinstance(block, dict) and isinstance(block.get("text"), str):
                parts.append(block["text"])
        return "\n".join(parts)
    return str(content)


def build_chat_fn(
    model_id: str,
    temperature: float | None,
    browse: bool = False,
    usage_sink: UsageSink | None = None,
    label: str | None = None,
) -> ChatFn:
    try:
        from langchain.chat_models import init_chat_model
    except ImportError as exc:  # pragma: no cover - environment-dependent
        raise SystemExit(
            "LangChain is not installed. Install the provider extra first:\n"
            "  pip install -e .[engines]"
        ) from exc
    # Only forward temperature when the caller set one: current Anthropic and
    # OpenAI models return a 400 for any explicit sampling parameter.
    extra: dict[str, object] = {} if temperature is None else {"temperature": temperature}
    if browse and model_id.startswith("openai:"):
        # OpenAI's server-side web_search tool lives on the Responses API.
        extra["output_version"] = "responses/v1"
    model = init_chat_model(model_id, **extra)
    if browse:
        model = model.bind_tools(browse_tools_for(model_id))
    sink_label = label if label is not None else model_id

    def chat(messages: list[tuple[str, str]]) -> str:
        response = model.invoke(messages)
        if usage_sink is not None:
            record_usage(usage_sink, sink_label, getattr(response, "usage_metadata", None))
            record_server_tool_use(
                usage_sink, sink_label, getattr(response, "response_metadata", None)
            )
        return _normalize_content(response.content)

    return chat


def build_engines(
    specs: list[EngineSpec],
    temperature: float | None,
    usage_sink: UsageSink | None = None,
    browse: bool = False,
) -> dict[str, ChatFn]:
    """Engines keyed by reporting label (see engine_labels), not alias."""
    labels = engine_labels(specs)
    return {
        labels[spec.alias]: build_chat_fn(
            resolve_model_id(spec),
            temperature,
            browse=browse,
            usage_sink=usage_sink,
            label=labels[spec.alias],
        )
        for spec in specs
    }
