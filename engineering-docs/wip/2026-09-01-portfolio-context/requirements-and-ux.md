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

## Accepted Privacy Posture (owner, 2026-09-01)

- This public demo repository operates on test or sanitized data only. Its
  committed snapshots are not represented as the owner's exact live holdings.
- The general product may operate on exact broker data. A public Git remote is
  a privacy risk worth surfacing, but it is not a prohibition: an informed
  user may accept the risk and suppress repeat warnings.
- Public/private detection is best-effort. The product must not claim a remote
  is private merely because public status could not be established.
- Acceptance is local to the checkout and bound to the normalized `origin`
  identity. It must not be committed and must become invalid if `origin`
  changes. This prevents one user's acceptance, or acceptance for one remote,
  from silently applying elsewhere.

### Proposed public-remote warning UX

The read-only preview remains available without repeated privacy warnings. At
`--apply`, if `origin` is detected as public and the checkout has no matching
local acceptance, the command refuses before writing and prints:

```text
PRIVACY WARNING: Git remote 'origin' appears to be public.
Applying this import may write holdings, quantities, cost basis, and marks
into files that can be pushed to that remote.

Review the proposed files above. To accept and remember this risk for this
exact origin, rerun with --acknowledge-public-origin.
```

The explicit flag records a local acknowledgement associated with a
fingerprint of the normalized origin URL. Future applies suppress the warning
only while that fingerprint still matches. A committed project declaration
that the repository contains test/sanitized data may suppress the warning for
this demo, but it must not silently classify an arbitrary user's imported data
as safe.

Unknown status, no `origin`, unsupported forges, offline detection, and
multiple-remotes policy remain design questions. The accepted requirement is
best-effort warning on detected public `origin`, not perfect hosting-provider
classification.

## Questions Still To Settle

- Should preview/apply be two explicit invocations as proposed, or one
  interactive invocation with a confirmation prompt?
- Is the proposed `--acknowledge-public-origin` refusal-and-persist flow the
  desired warning UX, including warning only at apply rather than preview?
- When an export lacks a trustworthy timestamp, should `--as-of` be required
  or may the command default to the current time after confirmation?
- Which reconciliation gaps block apply, and which may remain pending after
  observable broker state is accepted?
- Does v0 support Fidelity only behind a broker-adapter boundary, or must it
  accept a small broker-neutral normalized schema as well?
