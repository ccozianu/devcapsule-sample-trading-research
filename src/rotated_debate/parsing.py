"""Lenient extraction of the structured JSON block engines append. No deps."""

from __future__ import annotations

import json
import re

_FENCE = re.compile(r"```(?:json)?\s*\n(.*?)```", re.DOTALL)


def extract_json_block(text: str) -> tuple[dict | None, str | None]:
    """Return (parsed object, error). Never raises.

    Tries the last fenced code block first, then the last brace-delimited
    span. A debate must survive an engine that ignores formatting rules;
    the failure is recorded, not raised.
    """
    candidates: list[str] = [match.group(1) for match in _FENCE.finditer(text)]
    start = text.rfind("{")
    if start != -1:
        candidates.append(text[start : text.rfind("}") + 1])
    for candidate in reversed(candidates):
        try:
            parsed = json.loads(candidate)
        except (json.JSONDecodeError, ValueError):
            continue
        if isinstance(parsed, dict):
            return parsed, None
    return None, "no parseable JSON block found"


def string_list(value: object) -> tuple[str, ...]:
    """Coerce a decoded-JSON value into a tuple of strings, dropping junk."""
    if isinstance(value, list):
        return tuple(str(item) for item in value if isinstance(item, (str, int, float)))
    if isinstance(value, str) and value.strip():
        return (value,)
    return ()
