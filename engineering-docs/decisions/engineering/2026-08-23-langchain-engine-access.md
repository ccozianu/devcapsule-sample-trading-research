# Decision — LangChain as the Engine Access Layer

Date: 2026-08-23
Decided by: project owner
Status: accepted

## Decision

Engine access goes through LangChain's chat-model abstractions
(`init_chat_model` with `provider:model` bindings) rather than direct vendor
SDKs or a hosted gateway. This resolves the access-route half of OQ-4.

## Rationale

- Future flexibility in addressing various LLMs and API endpoints (owner's
  stated reason): swapping or adding an engine is a `provider:model` string,
  not an adapter.
- The generic protocol must stay fully general (R-PROTO-001); LangChain
  keeps provider specifics out of the protocol entirely.
- Browsing (required later by R-REFRESH-001) can ride LangChain's bindings
  for provider-native web-search tools, so the choice does not foreclose S9.

## Consequences

- `rotated_debate` core (model, parsing, protocol, transcript) stays
  dependency-free; LangChain is imported lazily in `engines.py` only, and
  installed via the `engines` extra (`pip install -e .[engines]`).
- Engine aliases map to defaults (claude → `anthropic:claude-sonnet-5`,
  chatgpt → `openai:gpt-5`, gemini → `google_genai:gemini-2.5-pro`),
  overridable per invocation (`alias=provider:model`) or environment
  (`ROTATED_DEBATE_MODEL_<ALIAS>`). Defaults are v0 choices; revisit when
  keys are injected and live runs begin.
- API keys are the standard vendor environment variables; never committed.
