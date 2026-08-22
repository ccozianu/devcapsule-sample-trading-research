# UX Outline — How Debates Are Invoked (DRAFT for discussion)

Status: **proposal, not settled.** Drafted 2026-08-22 by Claude in response
to the owner's request to outline the user experience for (a) a generic
rotated debate and (b) a portfolio-applied debate. Awaiting owner reactions.

The UX doctrine is fixed by S3: the interface is an IDE. Markdown in, Markdown
out, terminal commands in between. Commands mutate knowledge state; tests
verify. Everything below is an application of that doctrine.

## 1. Generic debate — stateless, one-shot

```
python -m rotated_debate ask "Is intermittent fasting contraindicated with metformin?" \
    [--context notes.md ...]        # optional files the engines must read first
    [--engines claude,gemini,chatgpt]
    [--rotations 3|6]               # how many role permutations (token budget)
    [--rounds 1]                    # debate depth cap, default 1
    [--browse | --no-browse]
    [--out debate.md]
```

Properties:
- Knows nothing about portfolios, positions, or this repo. This is the
  standalone deliverable (R-PROTO-001) and the medical-question use case.
- Output is **one self-contained transcript file**: frontmatter (question,
  engines, role assignments per rotation, rounds, reported outcome state,
  concessions log), then the syntheses, then the full exchange. Reading the
  file top-down is the product.
- Exit is silent about truth: the outcome is the observed state
  (converged/diverged), printed as one line and recorded in frontmatter.
- No write-back anywhere. If the caller wants persistence, the caller says
  where (`--out`).

## 2. Portfolio-applied debate — stateful, repo-aware

One command namespace, subcommands mirroring the loop in README:

```
python -m portfolio ingest <raw.csv>       # sanitize-assist -> data/snapshots/, then delete raw
python -m portfolio context                # regenerate portfolio/CONTEXT.md
python -m portfolio calendar [--days 30]   # what fires in the next N days
python -m portfolio sweep                  # the daily S9 refresh (see below)
python -m portfolio debate <target> [...]  # convene a debate on POS-nnn | TH-nnn | "question"
python -m portfolio resolve                # score evals-ledger entries whose dates arrived
python -m portfolio accept                 # the S8 acceptance debate; refuses before eligibility
```

`portfolio debate` differs from the generic tool in exactly four ways:
1. **Packet assembly is automatic**: CONTEXT.md plus the target's position,
   thesis, factor, and dispute files are the debate context; the engines cite
   element IDs (POS-003.KC-1, TH-001.C1), not prose paraphrase.
2. **COI routing is enforced**: rotation is pruned per ROUTING.md before the
   first call; the pruning is recorded in the transcript frontmatter.
3. **Write-back is structured**: transcript to `portfolio/debates/`, new
   scoreable claims to `evals/ledger.yaml`, unresolved disagreements to
   `DISPUTES.md`. Never to `decisions/`.
4. **The command ends where the human begins**: its last output line names
   what a decision entry would have to address, but writing one is manual.

`portfolio sweep` (the S9 daily refresh) is the two-stage shape the owner
sketched: stage one, a browsing-enabled debate on *which intervening news
are relevant to the held positions and registered theses*; stage two, only
if stage one surfaces anything, a debate on *what the news mean* — whether
theses need confirmation/infirmation updates, whether calendar entries must
be added, and whether the user should be alerted (up to "consider getting
out"). Alerts are files plus a loud final line in the terminal; the demo has
no push channel, by design (S1).

## 3. A day in the life (the demo narrative)

Morning: `portfolio sweep` over coffee; read the one-screen digest; usually
nothing fires. An earnings day: `calendar` warned yesterday; after the
release, `debate POS-005` (NVDA); read the synthesis and the state; a kill
criterion fired or it didn't; write the decision entry by hand either way;
`resolve` scores whatever predictions came due. Monthly: skim the ledger
scores per engine — the calibration record accumulating toward the S8
acceptance debate.

## 4. Open UX questions for the owner

1. **Digest vs. transcript.** Sweep output: full transcripts always, or a
   one-screen digest with transcripts on disk? (Proposal: digest; transcripts
   are always written anyway.)
2. **Naming.** `rotated_debate` and `portfolio` as the two command names —
   good, or rename before they calcify?
3. **Sweep cadence ownership.** Cron-like automation of the daily sweep, or
   is the human running it manually part of the demo's honesty for now?
   (Proposal: manual first; automation is a later convenience, not a design
   question.)
4. **Alert semantics.** Does "tell the user to run for the hills" ever page
   the user (email etc.), or is reading the sweep output the contract?
   (Proposal: reading the output is the contract for the demo.)
