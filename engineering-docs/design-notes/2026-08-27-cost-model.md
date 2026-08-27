# Cost model — rotated debates (2026-08-27)

Status: **estimates** from list prices x the `usage:` frontmatter of the
2026-08-27 live runs (`tests/resources/test-debates/`). Pending owner
verification against provider consoles — see Verification below. Known
blind spots make several figures floors, not totals.

## List prices (per 1M tokens, standard tier, 2026-08-27)

| Model | Input | Output | Search |
|---|---|---|---|
| claude-fable-5 | $10.00 | $50.00 | ~$10 / 1k searches |
| gpt-5.6-sol | $4.00 (promo thru >= 2026-11-21) | $20.00 | billed per search; count not visible to us |
| gemini-3.1-pro-preview | $2.00 (<=200k ctx) | $12.00 | grounding: free daily tier, then ~$35 / 1k |

## Measured scenarios (same GOOG question, 3 rotations)

| Scenario (run) | claude leg | gemini leg | chatgpt leg | Total |
|---|---|---|---|---|
| no browse, 1 round, Sonnet lineup (10:08) | ~$0.19 (est.*) | ~$0.15 | ~$0.16 | **~$0.50** |
| no browse, 1 round, Fable (10:26) | $0.64 | $0.15 | $0.16 | **~$0.96** |
| browse, 1 round (11:10) | $6.17 (19 searches, 471k in) | $0.28+ | $0.98+ | **~$7.4+** |
| browse, 2 rounds (14:30) | $11.42 (22 searches, 903k in) | $0.39+ | $1.63+ | **~$13.4+** |

\* the 10:08 run predates usage capture; claude leg estimated from the
10:26 token counts at Sonnet 5 prices ($3/$15).

Reading the shape:

- **Browse is the multiplier (~8x), rounds are ~1.8x on top.** Search
  results are injected into context and re-billed as input on subsequent
  calls; that, plus Fable's $50/M output (always-on thinking included),
  makes the claude leg ~85% of every browsing debate.
- **`+` marks the metering gap:** OpenAI and Gemini report no search
  counts through LangChain's `usage_metadata`, and Gemini's grounding
  tokens are invisible (25k reported input for an engine that
  demonstrably browsed). Those legs are floors.

## Predicted console totals for 2026-08-27 (all four runs)

- **OpenAI:** ~$2.93 in tokens (0.16 + 0.16 + 0.98 + 1.63) **plus**
  unmetered per-search charges — the delta vs the console is the
  per-search bill we cannot see.
- **Google:** ~$0.97 in tokens (0.15 + 0.15 + 0.28 + 0.39) **plus** any
  grounding charges beyond the free tier — likely ~$0 at this volume.

## Rough scenario costs (extrapolated)

| Scenario | Estimate |
|---|---|
| Bare `ask` (no browse, 1 round) | ~$1 |
| Knowledge-refresh debate (browse, 1 round) | ~$7.5 |
| Decision debate (browse, 2 rounds) | ~$13.5 |
| Position debate (browse, 2 rounds, ~5k-token context packet per call) | ~$14 |
| Full 17-position pass, browse 1 round | ~$130 |
| Same, with claude leg on Sonnet 5 | ~$55 |
| Daily sweep, steady state | far below a full pass — watermark semantics debate only what changed |

## Levers, in order of impact

1. **Claude binding**: `ROTATED_DEBATE_MODEL_CLAUDE=anthropic:claude-sonnet-5`
   roughly halves any browsing debate (open question: how much of the
   round-2 audit quality — EDGAR re-verification, the anchoring catch —
   was Fable-specific).
2. **Rounds**: 1 for sweeps/refresh, 2 for decision debates (see the
   2-rounds transcript analysis in the workstream handoff).
3. **`max_uses`** (Anthropic search cap, currently 5/call): binds at 2
   rounds (22 searches, "unverified within search limits" caveats) —
   raising it for decision debates trades dollars for verification depth.
4. **Prompt caching** (future): repeated context/search blocks are
   re-billed at full input price every call today; provider-side caching
   could cut the browse multiplier substantially. Not yet wired through
   the LangChain layer.

## Verification (OPEN TASK — owner)

**Task:** check the 2026-08-27 usage/billing dashboards for the OpenAI
and Google API keys. There was no other usage that day, so the daily
totals cover exactly the four runs above (note: *four*, including the
10:08 Sonnet-lineup run — not just the three later scenarios). Record
actuals here; the delta vs the predictions above quantifies the
unmetered items (OpenAI per-search billing, Gemini grounding).

| Provider | Predicted (tokens only) | Console actual | Delta / notes |
|---|---|---|---|
| OpenAI | ~$2.93 | *(pending)* | |
| Google | ~$0.97 | *(pending)* | |

Agents: if this table still says *(pending)* in a later session, remind
the owner.
