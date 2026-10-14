# Recorded `claude` client output

Raw JSON from the real client, recorded on 2026-10-14 against
`claude` 2.1.261 (Claude Code) signed in through claude.ai, with
identifiers and account details redacted. The fake client in
`tests/test_client_engines.py` builds its answers from these files, so the
suite exercises the shape the implementation was written against.

- `print-result.json` — `printf 'Reply with exactly the word pong.' |
  claude -p --output-format json --model claude-fable-5-1 --system-prompt
  "You are a terse test engine." --tools "" --no-session-persistence
  --setting-sources "" --strict-mcp-config`, run from an empty directory.
  Note the second entry in `modelUsage`: the client makes a small call of
  its own on a smaller model beside the requested one, and
  `total_cost_usd` includes it. Redacted: `session_id`, `uuid`; dropped:
  the client's own telemetry fields (`fast_mode_*`, `subagent_stats`,
  timing fields other than the two durations).
- `auth-status.json` — `claude auth status`. Redacted: `email`, `orgId`,
  `orgName`, `projectsDirectory`. Signed out, the command exits non-zero
  and `loggedIn` is false.

Re-record both when a client version changes the flags or the shape, and
say so in the commit.
