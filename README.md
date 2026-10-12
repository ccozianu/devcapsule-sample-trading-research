# Coordination Branch

This branch carries the workflow's live coordination state and is never
merged into the integration branch. Nobody resets or force-pushes it.

- `mail/<recipient>/`: intake items in flight. A sender adds one file; the
  recipient deletes only its own files after copying them into its intake
  directory.
- `state/<name>/`: the live copy of each open workstream's status file and
  decision log, pushed by that workstream from its working branch, and its
  claim: who is working on it, on what, until when. While a workstream is
  open this is the truth; the copies on the integration branch
  are the record as of its last integration.

Read and write it with `devcapsule workflow brief`, `status`, `claim`,
`publish`, and `mail check|send|take`, or with plain git: `git fetch origin coordination` and `git show origin/coordination:<path>`.
See *The Coordination Branch* in `WORKFLOW.md`.
