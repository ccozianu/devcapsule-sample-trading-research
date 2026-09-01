# Portfolio Context — Requirements And UX Discovery

Status: discovery draft; no requirements or UX proposed below are accepted
until the owner confirms them.

## User Job 1: Reconcile Broker Reality

Owner framing (2026-09-01): the application does not actuate the brokerage
account. The user changes the real portfolio at the broker, later downloads a
fresh export, and needs one understandable workflow that makes the repository
reflect the new observable reality. Rich broker data should not be forced into
Markdown frontmatter merely because the surrounding knowledge repository uses
Markdown.

### Proposed capability requirements

- A raw broker export is transient input, never portfolio knowledge and never
  commit-safe evidence. It must be protected from accidental Git inclusion and
  deleted after a successful import.
- Broker observations are authoritative for holdings, quantity, cost basis,
  and marks at the export time. The repository remains authoritative for
  position IDs, theses, criteria, factors, disputes, and human decisions.
- Import is reconciliation against the most recent accepted snapshot, not a
  blind overwrite. It classifies unchanged rows, mark-only changes, quantity
  or basis changes, newly observed instruments, missing instruments, and
  ambiguous mappings.
- A delta does not prove intent. In particular, a missing instrument must not
  be silently labeled a discretionary close; a quantity change must not invent
  a buy/sell rationale; and a possible roll must not be linked without human
  confirmation.
- Accepting broker reality must not wait for every semantic explanation. The
  new snapshot can become current while unexplained deltas remain explicit
  reconciliation gaps for follow-up.
- Re-importing the same export is idempotent. The tool identifies source
  content and snapshot time so it cannot create duplicate snapshots or apply
  the same transition twice.
- A successful apply regenerates derived current-state views, including
  `portfolio/CONTEXT.md`, from the newly accepted snapshot. The standalone
  `portfolio context` command remains available for rebuilding derived views.
- No import or reconciliation command writes a human decision under
  `portfolio/decisions/`.

### Proposed user experience

Recommended repository-local landing place:

```text
data/inbox/fidelity-positions.csv
```

`data/inbox/` would be Git-ignored and documented as private, transient, and
delete-after-import. The command accepts any readable path so a user may leave
the download outside the repository instead.

Preview, with no repository mutation:

```bash
python -m portfolio ingest data/inbox/fidelity-positions.csv
```

The default is deliberately a preview. It prints one screen containing:

- detected broker/export time and latest snapshot compared;
- unchanged and mark-only row counts;
- each material position delta;
- proposed new position IDs and possible roll/replacement relationships;
- ambiguous or invalid rows requiring attention;
- privacy/sanitization mode and exact files that an apply would write; and
- a stable import fingerprint so the reviewed preview can be identified.

Apply the reviewed reconciliation:

```bash
python -m portfolio ingest data/inbox/fidelity-positions.csv --apply
```

Apply must recompute and verify the preview before writing. If the file,
latest snapshot, import options, or mappings changed since preview, it refuses
and asks for a new preview. On success it writes atomically:

1. an immutable normalized snapshot under `data/snapshots/`;
2. a generated reconciliation report under `portfolio/reconciliations/`;
3. new position skeletons or generated observation fields where mappings are
   unambiguous, without overwriting authored thesis/criteria prose; and
4. regenerated derived context.

The final terminal digest lists applied facts separately from unresolved
knowledge gaps, then reminds the user to delete the raw export. Source deletion
is not implicit; an explicit future `--delete-source` option may move it to the
operating system trash after a verified apply.

### Proposed reconciliation report

One generated Markdown report per accepted import should record:

- import fingerprint, broker, account alias, and observation time;
- previous and new snapshot references;
- normalized deltas and their mapping to stable portfolio IDs;
- user-confirmed mappings;
- unresolved semantic gaps (for example, “POS-007 no longer observed; reason
  unknown”); and
- generated files changed by the apply.

This report is the audit bridge between tabular broker facts and authored
portfolio knowledge. It does not duplicate all snapshot rows in frontmatter.

## Load-Bearing Open Decision: Privacy And Canonical Reality

The existing demo policy commits altered quantities and placeholder account
identifiers. That is safe for a public repository but cannot simultaneously be
the exact operational truth for position sizing and concentration. Choose one
product posture before accepting paths or write behavior:

1. **Private-repository posture:** normalized exact snapshots are canonical and
   commit-eligible because the user controls a private repository. Sanitized
   demo export is a separate publication operation.
2. **Public-demo posture:** exact normalized state remains local and ignored;
   only a stable sanitized projection is committed. Context and debate output
   must then have explicit private and publishable variants to avoid leaking
   exact holdings.
3. **Sanitized-only posture:** the repository intentionally reasons over an
   altered representative portfolio. This is simplest and safest but cannot
   claim exact sizing or concentration advice for the owner's real account.

Current recommendation: make exact-state operation a private-repository
capability and treat sanitization as an explicit publication boundary. For
this public demo checkout, use local-only exact input/state and commit only the
sanitized projection. This is more complex than one snapshot, but it does not
pretend altered data are exact reality.

## Questions Still To Settle

- Which privacy/canonical-reality posture is the product contract?
- Should preview/apply be two explicit invocations as proposed, or one
  interactive invocation with a confirmation prompt?
- When an export lacks a trustworthy timestamp, should `--as-of` be required
  or may the command default to the current time after confirmation?
- Which reconciliation gaps block apply, and which may remain pending after
  observable broker state is accepted?
- Does v0 support Fidelity only behind a broker-adapter boundary, or must it
  accept a small broker-neutral normalized schema as well?
