# Recorded `codex` client output

Raw output of the real client, recorded on 2026-10-15 against
`codex-cli` 0.153.4 signed in through ChatGPT, identifiers redacted. The
fake client in `tests/test_client_engines.py` builds its answers from these
files.

- `exec-events.jsonl` — `printf '<prompt>' | codex exec --json --ephemeral
  --skip-git-repo-check -s read-only -m gpt-6-astra -C <empty dir>
  -c model_instructions_file=<file holding the system prompt> -`.
  Redacted: `thread_id`. The usage line is the one with the instructions
  file; without it the same prompt cost 14,283 input tokens.
- `exec-events-browse.jsonl` — the same call with `web_search="live"` and a
  prompt demanding a search, recorded 2026-10-15: two `web_search` items,
  a query and a page open, before the answer. Redacted: `thread_id`.
- `login-status.txt` — `codex login status`, exit 0. Signed out, the
  command exits non-zero and does not print this line.

Re-record when a client version changes the flags or the shape.
