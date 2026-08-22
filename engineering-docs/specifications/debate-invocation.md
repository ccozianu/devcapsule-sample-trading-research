# Specification — Debate Invocation Surfaces (v0)

Status: accepted 2026-08-22 (owner-settled outline,
`engineering-docs/design-notes/ux-outline.md`). This is the binding contract
for the first implementation. Deliberately unspecified points are marked;
they are gaps to fill by decision, not license to improvise.

## 1. `rotated_debate` — the stateless, domain-agnostic surface

```
python -m rotated_debate ask "<question>" [--context FILE ...]
    [--engines claude,gemini,chatgpt] [--rotations 3|6] [--rounds 1]
    [--browse | --no-browse] [--out FILE]
```

Contract:

- Reads nothing except the given `--context` files; writes nothing except
  `--out`. No knowledge of this repository, portfolios, or routing tables.
- Defaults: three engines, 3 rotations, 1 round, no browsing.
- Every rotation assigns distinct ANSWERER / CRITIC / SYNTHESIZER roles;
  across the run, role assignments must be recorded per rotation.
- Output is one self-contained Markdown transcript: YAML frontmatter
  (question, engines, rotations, rounds, browse flag, role-assignment table,
  outcome state fields, concession log distinguishing reasoned concessions
  from capitulations), then the syntheses, then the full exchange.
- Stdout: a one-line reported state. Exit code signals success/failure of
  the run only — the epistemic state is data, never an exit code.
- Outcome state: pending OQ-1, the frontmatter reserves fields for **both**
  the deterministic tally over structured engine positions and the
  synthesizer meta-verdict; when both exist they are recorded side by side.
  Their divergence is a finding, not an error.

## 2. `portfolio` — the stateful, repo-aware surface

Global rules: commands write only under `portfolio/` and `data/`; **never**
under `portfolio/decisions/`; every LLM-involving command writes its full
transcript(s) to `portfolio/debates/` and prints a one-screen digest to the
terminal. No alert channel exists (owner decision, 2026-08-22).

| Command | LLM calls | Contract |
|---|---|---|
| `ingest <raw.csv>` | no | Assist sanitization into `data/snapshots/portfolio-YYYY-MM-DD.csv` per `data/snapshots/FORMAT.md`; verify invariants; remind that the raw file must be deleted, never committed. |
| `context` | no | Regenerate `portfolio/CONTEXT.md` (INFORMATION_MODEL §5) deterministically within its token budget; refuse rather than truncate silently. |
| `calendar [--days N]` | no | Print upcoming events and what each can fire (default 30 days). |
| `sweep [--since DATE]` | yes | Knowledge catch-up; see §3. |
| `debate <POS-nnn\|TH-nnn\|"question">` | yes | See §4. |
| `resolve` | no (v0) | List evals-ledger entries whose resolution dates have arrived; record human-entered resolutions and scores. |
| `accept` | yes | The S8 acceptance debate. MUST refuse, stating why, unless repo records show ≥2 months of live usage crossing ≥1 earnings season (R-ACCEPT-001). |

## 3. `sweep` — watermark semantics

The contract is: **update the knowledge with what is new since the latest
recorded knowledge update.** Cadence is owned by the caller (the owner's
external daily trigger, or a human on demand), never by the tool.

- Each sweep transcript records the interval it covered (`covers_from`,
  `covers_until`). The next sweep's default `covers_from` is the latest
  recorded `covers_until`; the first sweep ever starts from the latest
  snapshot date. `--since` overrides explicitly.
- Stage 1: browsing-enabled debate — *which intervening news in the covered
  interval are relevant to held positions and registered theses?* If none:
  digest says so, watermark advances, done.
- Stage 2 (only if stage 1 surfaced items): debate on *what the news mean* —
  proposed thesis confirmations/infirmations, proposed calendar entries
  (with sources; dates enter `calendar/events.yaml` only after human
  verification), new scoreable claims to the evals ledger, disagreements to
  `DISPUTES.md`, and, when warranted, a digest line advising the user to
  reconsider positions. The digest is the entire notification contract.

## 4. `debate` — the four repo-aware behaviors

Exactly the generic protocol of §1 plus, in order:

1. **Packet assembly**: context is `portfolio/CONTEXT.md` plus the target's
   position, thesis, factor, and open-dispute files. Engines cite element
   IDs (`POS-005.KC-1`, `TH-001.C1`), not paraphrase.
2. **COI pruning**: rotations violating `portfolio/ROUTING.md` are removed
   before any call; the pruning is recorded in transcript frontmatter.
3. **Structured write-back**: transcript → `debates/`; new scoreable claims
   → `evals/ledger.yaml` (with `origin` adoption tracking); unresolved
   disagreements → `DISPUTES.md`.
4. **Human boundary**: the final digest line names what a `decisions/`
   entry would have to address. The tool never writes one.

## 5. Deliberately unspecified in v0

- The state-declaration mechanism (OQ-1) — both candidate fields recorded.
- Prompt templates for the roles, and browsing-evidence tier labeling.
- Provider access route (direct SDKs vs. router) — constrained by the
  requirement that every engine gets its vendor's browse tooling.
- `resolve` automation beyond listing due entries.
