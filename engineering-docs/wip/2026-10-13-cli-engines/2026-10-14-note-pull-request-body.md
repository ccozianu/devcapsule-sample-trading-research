# Note: pull-request body for slice 1

The GitHub CLI is not installed in the capsule and no token is present, so
the owner opens the pull request from the pushed branch. This is the body
to paste, kept here so the record survives the pull request's lifetime.
Counts were filled in after review round 2.

---

**Title:** cli-engines slice 1: the `claude` command-line client as an engine route

**Branch:** `ws-cli-engines/v0` → `main`, merge commit. Review branches
`ws-cli-engines/v0-review` (round 1, merged) and `ws-cli-engines/v0-review-2`
(round 2) are stacked on it.

## What changed

```text
--engines item            resolves to                  built by
cli-claude-fable-5-1  ->  cli-claude:claude-fable-5-1  clients.py: claude -p, JSON out,
                                                        prompt on stdin, system prompt
                                                        replaced, no tools, no MCP, no
                                                        session, empty cwd, key vars
                                                        scrubbed
cli-gpt-6-astra       ->  cli-codex:gpt-6-astra        refused: slice 2
cli-gemini-3.8-...    ->  cli-antigravity:gemini-...   refused: slice 3
claude / gemini / ... ->  anthropic:... (unchanged)    engines.py: LangChain, as before
```

An `--engines` item `cli-<full model name>` reaches the model through its
vendor's signed-in command-line client, with no API key. The vendor is
inferred from the name as for bare names; the client per vendor is a
one-line table. Only `claude` is implemented in this slice. Refusals come
before any model call: `--browse`, `--temperature`, a client not yet
implemented, not on PATH, or not signed in. Usage is recorded as the
client reports it, dollar estimate included; the engine is labeled as
typed, so the same model by API and by client stay distinct in one debate.

Files: `src/rotated_debate/clients.py` (new), `engines.py` (dispatch,
numeric usage sink), `transcript.py` (type only), `docs/rotated-debate.md`,
`tests/test_client_engines.py` (new), `tests/fixtures/claude-client/`
(recorded client output), one retained live transcript under
`tests/resources/test-debates/`.

Work order: `engineering-docs/work-orders/2026-10-14-cli-engines-slice-1-claude-client.md`.
Decisions: `engineering-docs/wip/2026-10-13-cli-engines/CURRENT-STATUS.md`,
*Decisions, 2026-10-14*.

## Judgments taken, for the owner's review

1. The route lives in a sibling module, `clients.py`; `engines.py` stays
   the single entry point and dispatches on the `cli-` prefix.
2. A client engine's transcript entry reads `cli-claude:<model>`; the
   client's version is not recorded.
3. The usage sink's value type widened from `int` to `int | float` so the
   client's dollar estimate is recorded as reported.
4. The client runs in an empty temporary directory with
   `--strict-mcp-config`, and with `ANTHROPIC_API_KEY` and
   `ANTHROPIC_AUTH_TOKEN`, `ANTHROPIC_CUSTOM_HEADERS` and the cloud route
   selectors removed from its environment, and the client's own sign-in
   report must say claude.ai, first party. Measured: the same
   prompt costs 805 input tokens from this repository and 417 from an
   empty directory. Managed organization settings are outside reach and
   the guide says so.
5. A handle's `ROTATED_DEBATE_MODEL_<NAME>` override keeps its documented
   precedence over a `cli-` binding; an override in the `cli-` form
   resolves like any `cli-` item.
6. One client call is bounded by 600 s, overridable by
   `ROTATED_DEBATE_CLIENT_TIMEOUT`.

## Review

Round 1 by the Codex pair (`gpt-6-astra`), own worktree, written brief:
nine findings, four fixes merged (UTF-8 pipes, actionable sign-in process
failures, temperature refusal, cost wording), four resolved by the
implementor (key scrub, working-directory isolation, override rule,
recorded fixtures), one noted. Assessment:
`engineering-docs/wip/2026-10-13-cli-engines/2026-10-14-record-review-round-1.md`.
Round 2, confined to those resolutions: four verified, one further scrub
merged from the reviewer (`ANTHROPIC_CUSTOM_HEADERS`), two proposals taken
(sign-in method check, `TMPDIR` guard), the rest documented limits:
`engineering-docs/wip/2026-10-13-cli-engines/2026-10-14-record-review-round-2.md`.
Two rounds of the three allowed.

## Validation

- Gate `.venv/bin/nox`: 74 tests (43 before this slice), compile
  and lint clean, offline, no keys, no sign-in.
- Smoke: `python -m rotated_debate --help` lists `ask`.
- Refusals against the real environment, no model call: `--browse`, the
  `codex` placeholder, an unrecognized name, a missing client.
- Live: one real debate, three engines all through the signed-in `claude`
  client, `state=converged`, zero parse errors, 12 calls, 3m47s, $0.69 at
  list price as the client reports it; retained as
  `tests/resources/test-debates/20261014-214924-cli-claude-91-prime-debate.md`.
  One real call through the final code path with a bogus
  `ANTHROPIC_API_KEY` exported: answered, 419 input tokens.
- Not run: the owner's mixed-route acceptance run
  (`cli-claude-fable-5-1,gemini,chatgpt`), which needs the API keys only
  the owner holds; it is the acceptance evidence named in the work order.
