# Record: review round 2 of slice 1, the `claude` client engine

Same pairs as [round 1](2026-10-14-record-review-round-1.md). The reviewer
worked on `ws-cli-engines/v0-review-2` from a brief confined to the six
round-1 resolutions; its report, `REVIEW-2.md`, stayed uncommitted in its
worktree. Merged as `8fc86e2`; the remaining items resolved in `d072244`.
The implementor read the diff before deciding.

## Assessment, item by item

| Item | Reviewer's verdict | Decision | What was done |
|---|---|---|---|
| F1, key scrub | Partial: `ANTHROPIC_CUSTOM_HEADERS` can carry a key (fixed by the reviewer, `ba920a0`); the Bedrock, Vertex and Foundry route selectors survive; stored and managed credentials are out of reach; the status check accepted any `authMethod` | Reviewer's fix merged; two proposals taken; one recorded as a limit | The scrub now also removes the three cloud route selectors and the Bedrock bearer token. The sign-in check now requires what the client itself reports for the claude.ai sign-in, `authMethod: claude.ai` and `apiProvider: firstParty`, and refuses anything else naming what it found. Verified against the real client. Credentials injected by managed organization settings remain outside reach and the guide says so. The reviewer's "matched configuration" point (the status command runs with ordinary settings) is accepted as a limit: the status command takes no setting-sources flag. |
| F2, isolation | Lifetime verified; `TMPDIR` under a project would put the empty directory beneath a `CLAUDE.md` | Proposal taken | The engine's directory is refused, with the path named, if any ancestor carries `CLAUDE.md` or `.claude`; tested with `TMPDIR` under a project. The docstring now calls the token counts a measurement on this version, not a guarantee. |
| F4 addition, stdin | Verified | None | |
| F7, override rule | Verified | None | |
| F8, fixtures | Verified, limits stated: signed-out status is a synthetic variation, not a recorded one | Accepted as a limit | Re-recording a signed-out status would require signing the owner's client out; not done. The README says what is recorded. |
| Gate | Verified, 71 tests | | 74 after this round's additions, compile and lint clean. |

## Rounds

Two rounds were run; the cap is three. The implementor stopped here because
every remaining proposal is either taken above or a documented limit that
no further offline round can establish: live billing determination,
configured MCP behavior and managed-settings credentials are matters for
the owner's acceptance run and for the owner's own client configuration.

## Evidence this round

- Gate after the round: 74 tests, compile and lint clean, offline.
- The real client's sign-in report passes the stricter check; a real engine
  builds with its working directory under the system temporary root.
- No paid model call was made this round; the command line is unchanged
  since the paid call recorded in round 1.
