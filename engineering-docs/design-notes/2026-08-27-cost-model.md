# Cost model — rotated debates (2026-08-27)

Status: scenario figures are **estimates** from list prices x the `usage:`
frontmatter of the 2026-08-27 live runs
(`tests/resources/test-debates/`). The five-run daily totals were reconciled
against the provider consoles from owner-reported actuals on 2026-09-01; see
Verification below. Known metering blind spots still make individual-run
figures floors, not totals.

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
| browse, 2 rounds, + last synthesizer gemini-3.7-flash (18:04) | $8.04 (28 searches, 574k in) | $0.43+ | $1.45+ | **~$9.9+** (flash leg ~$0.01) |

Note the 14:30 vs 18:04 comparison: same configuration apart from the
last synthesizer, yet the claude leg cost $11.4 vs $8.0 (903k vs 574k
input tokens) — run-to-run variance in search/context volume is large,
so single-run costs are indicative, not repeatable.

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

## Predicted console totals for 2026-08-27 (all FIVE runs)

- **OpenAI:** ~$4.38 in tokens (0.16 + 0.16 + 0.98 + 1.63 + 1.45)
  **plus** unmetered per-search charges — the delta vs the console is
  the per-search bill we cannot see.
- **Google:** ~$1.41 in tokens (0.15 + 0.15 + 0.28 + 0.39 + 0.43 +
  ~$0.01 flash) **plus** any grounding charges beyond the free tier —
  likely ~$0 at this volume.

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

## Verification (completed 2026-09-01)

The owner reported the provider-console totals for 2026-08-27. There was no
other API usage that day, so these actuals cover exactly the five runs above,
including the 10:08 run and the 18:04 last-synthesizer run. Amounts are USD.

| Provider | Predicted | Console actual | Delta / notes |
|---|---:|---:|---|
| Anthropic | ~$26.46 | $26.39 | -$0.07. Prediction reconstructs the five scenario rows ($0.19 + $0.64 + $6.17 + $11.42 + $8.04). The console attributed the reported spend to Fable 5, while the 10:08 transcript identifies `claude-sonnet-5`; preserve this provenance discrepancy. |
| OpenAI | ~$4.38 | $4.88 | +$0.50. The positive delta is consistent with the web-search charges absent from transcript metering, though the console total does not allocate the delta by request. |
| Google | ~$1.41 | $1.69 | +$0.28. The `gemini-3.7-flash` final-judge use did not appear as a separate billed line; the owner described it as below visible billing precision. The remaining delta may include grounding or other metering omitted from transcript usage. |
| **Total** | **~$32.25** | **$32.96** | **+$0.71** |

These daily actuals validate the aggregate cost model to about $0.71 (2.2%)
while confirming that provider-reported transcript metadata is insufficient
for exact per-run allocation. Do not use the aggregate deltas to invent search
counts or charges for an individual transcript.

## Cost/quality review of the GOOG run set (2026-09-01)

This is a traceable qualitative review of the five 2026-08-27 transcripts,
not a model benchmark. The runs repeatedly ask one question, have no resolved
ground-truth valuation, and use the same role order. Model identity, role, and
question are therefore confounded. The console figures are daily aggregates,
not exact per-call allocations; Google/OpenAI search metering is incomplete;
and the 10:08 Claude transcript/console model attribution differs as recorded
above.

Actual daily cost ratios were approximately **5.4x Anthropic/OpenAI**,
**15.6x Anthropic/Google**, and **2.9x OpenAI/Google**. Those ratios measure
provider spend, not output quality.

| Model/provider | Observed strengths | Material failures or limits | Cost/quality reading |
|---|---|---|---|
| Claude Fable 5 / Anthropic ($26.39 daily total, with the attribution caveat above) | Strongest exhaustive source audit and most nuanced detection of over-concession. In critic and synthesizer roles it caught unsupported valuation ranges, stale or ephemeral price evidence, critic overstatement, and the distinction between completed financing and authorized capacity. | Its own answer in the final run relied on the distorted headline P/E and omitted the financing side, then had to withdraw the undervaluation conclusion. Its browsing produced very large, highly variable contexts and long outputs; some secondary-source claims also required later qualification. | The premium bought real verification depth, but the transcripts do not support a 5.4x quality advantage over GPT or a 15.6x advantage over Google. Poor routine value; plausible selective value for a high-assurance audit. |
| GPT-5.6-sol / OpenAI ($4.88) | Best all-round performance in this sample. Its browsed initial answer already surfaced non-operating gains, capex, negative quarterly FCF, financing, dilution, and regulatory risk. Its syntheses most consistently separated “undervaluation not demonstrated” from “overvalued” and corrected excess bearish rhetoric. | It introduced underived bear/base/bull price ranges, leaned on ephemeral aggregator metrics, and briefly conceded an adjusted-EPS “miss” that was definition-sensitive. The second round was needed to remove those claims. | Best observed full-spectrum cost/quality balance. It was not error-free, but it contributed the most decision-relevant analysis per dollar among the three participant models. |
| Gemini 3.1 Pro / Google ($1.69 total including a Flash judge below visible billing precision) | As critic, it found the decisive flaw in the Claude answer: the 17x P/E was distorted by enormous unrealized investment gains. It also challenged the temporary-capex framing. Gemini 3.7 Flash compressed the three syntheses faithfully and separated factual from reasoning agreement at negligible visible marginal cost. | Gemini Pro's own answer was the weakest initial answer: categorical “excellent entry point,” 8/10 confidence, undefined “operating P/E,” and unsupported claims that regulation explained the discount and capex already proved adequate returns. For a GOOG topic, both Pro and Flash also carry the maker conflict recorded in `portfolio/ROUTING.md`; the domain-agnostic `ask` surface does not prune that conflict. Flash summarized existing evidence but added no independent verification. | Excellent low-cost adversarial and summarization value, but weak standalone recommendation quality in this sample. A Gemini synthesis or final verdict on GOOG should be discounted under the portfolio routing rule. |

### Findings

1. **Price did not scale proportionally with quality.** Anthropic produced the
   deepest audit, but also made the central error in its own answer. Its cost
   premium mainly reflects expensive output and repeatedly re-billed search
   context, not a five- to sixteen-fold improvement in reasoning.
2. **GPT was the strongest cost-adjusted generalist in this run set.** It had
   the best initial factual coverage and the most calibrated syntheses, while
   still benefiting materially from criticism.
3. **Gemini supplied unusually cheap marginal value.** Its critique changed
   the debate by finding the headline-P/E failure, even though its own answer
   was overconfident. This is evidence for debate diversity, not for trusting
   Gemini's standalone GOOG verdict.
4. **The Flash judge was useful compression, not new evidence.** Its near-zero
   visible cost makes the feature attractive, but a non-conflicted judge is
   required for a portfolio GOOG debate.
5. **The current evidence supports a budgeting hypothesis, not a lineup
   decision:** use Fable selectively where exhaustive audit may justify the
   premium, test Sonnet as the routine Claude binding, and retain GPT/Gemini
   diversity. The protocol's role rotation means permanent role specialization
   would require a separate design decision.

### What an objective comparison still requires

Across multiple questions with resolvable answers, annotate atomic claims
against primary sources and score: material errors caught and introduced,
source quality, concession correctness, synthesis fidelity, unique changes to
the final answer, latency, and dollars per useful correction. Rotate or
randomize role order and compare Fable with Sonnet on identical prompts. Until
that dataset exists, the conclusions above should guide experiments and token
budgets, not be treated as a stable model ranking.
