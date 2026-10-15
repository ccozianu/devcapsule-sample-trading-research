# Recorded `antigravity` client output

Raw output of the real client, recorded on 2026-10-15 against
`antigravity` 1.1.24 signed in, identifiers redacted. The fake client in
`tests/test_client_engines.py` builds its answers from these files.

- `print-result.json` — `printf '<prompt>' | antigravity --output-format
  json --model gemini-3.8-flash-high --sandbox`, from an empty directory.
  Redacted: `conversation_id`. The prompt on stdin selects print mode; the
  `--print` flag takes the prompt as its argument instead.
- `print-error.json` — the same with `--model gemini-3.8-flash` and no
  `--effort`: exit 1, the error inside the JSON. With `--effort high` the
  base id works, and so does a suffixed id with the flag beside it.
- `models.txt` — `antigravity models`, exit 0. The client is a
  multi-vendor router; the first field of each line is the id a user
  types after `cli-`.

Re-record when a client version changes the flags or the shape.
