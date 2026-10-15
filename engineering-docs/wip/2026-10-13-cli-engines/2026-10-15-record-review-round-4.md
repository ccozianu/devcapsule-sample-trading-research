# Record: review round 4, browsing by default on the client engines

Same pairs as [round 1](2026-10-14-record-review-round-1.md). The reviewer
worked on `ws-cli-engines/v0-clients-review-2` from a brief confined to
seven checks on commit `8e7f374`; its report, `REVIEW-4.md`, stayed
uncommitted in its worktree. Merged as `d52cddb`; the open finding
resolved in `adf6c31`. The implementor read the diff before deciding.

## Assessment

| # | Reviewer's finding | Decision | What was done |
|---|---|---|---|
| F1 | The guide still said client `--browse` refuses, and understated the evidence limits | Accepted, reviewer's fix merged | Guide and module overview corrected: client web access described per client; `num_turns` does not establish a fetch; `grounding_links` is a floor and counts marker occurrences. |
| F2 | A client last synthesizer kept its web access although the role never browses; the reviewer corrected the guide and proposed leaving the runtime to the later browsing-off slice | Accepted, resolved now in the runtime rather than documented | `build_client_chat_fn` takes `browse`; the last-synthesizer path passes it off: `claude` gets no web tools, `codex` runs with `web_search="disabled"` and a search item fails the call, `antigravity` is refused in that role because its grounding is an account-level setting. The main lineup browses whatever `--browse` says. Five tests, one end to end through the CLI. The guide's "never browses" wording is restored with the per-client mechanics. |
| F3 | The private home is a configuration redirect, not a filesystem boundary: the token link is writable and a refresh reaches the real file | Accepted as a stated limit, reviewer's fix merged | Docstring and guide say so. The link is the design: the sign-in must hold, and copying a credential into a temporary directory was rejected. |

Verified without change: the claude flag syntax against the vendor's own
examples, the usage sum, the codex counter and guard, the empty-response
error, the gate at 103 tests. The reviewer's supplementary probes (a
search item after `turn.completed`, a dangling token link, HOME override
not touching the parent process) are noted as evidence it ran, not as
tests added.

## Gate after the round

108 tests, compile and lint clean, offline. The live validation of the
browsing change is the three real calls recorded in the status file and
the NEM debate rerun with browsing, retained when it completes.

## Rounds

Two rounds on this pull request (round 3 on the clients, round 4 on
browsing), of three allowed.
