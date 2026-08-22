# Portfolio Snapshot Format

Snapshot files in this directory are the demo project's single source of truth
for position quantities, cost bases, and marks (see
`engineering-docs/sketch-of-a-project/INFORMATION_MODEL.md`, principle 4).

## Provenance and privacy

Snapshots are derived from real brokerage exports. Before a snapshot is
committed: account identifiers are replaced with placeholders, broker-specific
branding and footer text are removed, and some position sizes are altered so
the file does not represent the author's actual holdings. Market facts —
ticker symbols, security descriptions, option contract terms, last prices,
and daily price changes — are real as of the snapshot date (for this file:
2026-08-22, late morning US Eastern time). Derived columns are recomputed for
internal consistency after any alteration.

**Raw brokerage exports must never be committed.** Drop them under
`tests/resources/`, which is gitignored for this reason.

## File format

Plain CSV, UTF-8, one header row, one row per position, no footer rows.
Filename pattern: `portfolio-YYYY-MM-DD.csv` (the snapshot date).

| Column | Meaning |
|---|---|
| Account number | Placeholder identifier (`000000000` in demo data) |
| Account name | Account label; also placeholder in demo data |
| Symbol | Ticker for stocks/cash; option grammar below for options |
| Description | Human-readable security description |
| Quantity | Shares for stocks; contracts for options (1 contract = 100 shares); empty for cash |
| Last price | Per-share / per-contract-share mark, `$` prefixed |
| Last price change | Day's per-share price change, signed |
| Current value | Position market value (see invariants) |
| Today's gain/loss dollar | Day's change in position value, signed |
| Today's gain/loss percent | Day's change as percent of prior value |
| Total gain/loss dollar | Current value minus cost basis total, signed |
| Total gain/loss percent | Total gain/loss over cost basis total |
| Percent of account | Position value over total account value |
| Cost basis total | Total amount paid for the position |
| Average cost basis | Per-share cost (see invariants) |
| Type | Account funding type of the lot (`Cash` or `Margin`) |

Money fields carry a `$` prefix and signed fields a `+`/`-` sign; percent
fields end in `%`. The cash-sweep row (`Symbol` = `CASH`) leaves quantity,
price, and gain fields empty.

### Option symbol grammar

```
-ROOT YYMMDD [C|P] STRIKE     (written without spaces)
```

Examples: `-NEM280121C80` is the NEM January 21 2028 $80 call;
`-SBUX280121P95` is the SBUX January 21 2028 $95 put. A leading `-` marks the
row as an option position.

## Consistency invariants

Tools and tests may rely on these:

- `Current value = Quantity x Last price x M`, where `M` is 100 for options
  and 1 for stocks.
- `Today's gain/loss dollar = Quantity x Last price change x M`.
- `Total gain/loss dollar = Current value - Cost basis total`.
- `Average cost basis = Cost basis total / (Quantity x M)`.
- `Percent of account` sums to ~100% across all rows (rounding to two
  decimals may leave the sum a few hundredths off).
