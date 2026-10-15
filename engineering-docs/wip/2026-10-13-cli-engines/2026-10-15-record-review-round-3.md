# Record: review round 3, slices 2 and 3, the `codex` and `antigravity` clients

Same pairs as [round 1](2026-10-14-record-review-round-1.md). The reviewer
worked on `ws-cli-engines/v0-clients-review` from a written brief, no
push; its report, `REVIEW-3.md`, stayed uncommitted in its worktree. It
reviewed commit `b2d488b`. Merged as `ffb9fba`; the open findings
resolved in `8afa46f`. The implementor read the diff before deciding.

## Assessment

| # | Reviewer's finding | Decision | What was done |
|---|---|---|---|
| F1 | The codex event parser accepted a stream with no `turn.completed`, ignored `turn.failed`, and dropped non-JSON lines silently | Accepted, reviewer's fix merged | A completed turn is required, malformed events and `turn.failed` fail the call, usage is not recorded on a rejected response. Verified by a real call through the code path afterwards. |
| F2 | The antigravity preflight matched any effort suffix while the command asked for `high`, and rejected an exact unsuffixed id | Accepted, reviewer's fix merged | The preflight now matches the exact id or the `high` variant the command requests. |
| F3 | Antigravity's listing establishes sign-in, not the sign-in method; the guide's "a key-based sign-in refuses" was too broad | Accepted as a limit, guide corrected | The client reports no method and has no status command. The guide now says `claude` and `codex` report their method and refuse a key, and that antigravity's listing shows it is signed in, not how. |
| F4 | Codex's read-only sandbox still allows commands, hosted web search, MCP servers and instructions from the client's home directory | Accepted, resolved as far as the client allows, remainder detected | Measured with a planted `~/.codex/AGENTS.md`: the marker was obeyed under the instructions file, under `--ignore-user-config`, under `project_doc_max_bytes=0` and under `project_doc_fallback_filenames=[]`; it was not obeyed under a private `CODEX_HOME` holding only a symlink to `auth.json`, and the sign-in held through the link. Each call now runs with such a home under the engine's directory, plus `--ignore-rules` and `tools.web_search=false`. Commands cannot be switched off: any tool item in the event stream now fails the call, so a tool-assisted answer is never recorded as a chat answer. Antigravity has no tools-off switch; documented, with `num_turns` as the evidence. |

Other checks the reviewer made (instructions file replaced per call,
multiple messages, codex sign-in wording, listing parser, usage and
documentation, scope) were verified without change, except that the
directory now also holds the private home, which its test reflects.

## Gate after the round

98 tests (89 before the round, 96 after the reviewer's fixes), compile and
lint clean, offline. One real codex call through the final code path:
`pong`, 9,379 input tokens, caches written into the private home only.

## Rounds

One round for this pull request, out of three allowed. The reviewer's two
proposals were taken as far as the clients permit and the rest is stated
as a limit in the guide; a further offline round could not establish more.
