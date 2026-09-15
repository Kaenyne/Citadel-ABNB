# Lane 2 — the point-in-time convention every brief uses (read this before your brief)

This page exists because Lane 1's A and B′ came back **0/14, 0/10 — empty, not negative** — after their briefs said
"consensus strictly before the guide date" and "refuse anything printed on/after the guide date". That wording was
*tighter than the harness itself* and made the tests unrunnable. The harness's own rules (FORMAT 1.0,
`analysis/src/forecast_methods/harness/README.md`, authoritative) are the convention. Do not tighten them again.

## 1. A guide-date vintage is the close of the letter day

Airbnb releases the shareholder letter **after the market close**. The letter dated *d* prints quarter *q*'s GBV,
nights, ADR and revenue **and** issues the revenue guide for *q+1*. FORMAT 1.0 §PIT allows `knowable_from <= vintage_date`:
everything in the letter dated *d* is knowable at `vintage_date = d`. So a kernel forecast at vintage *d* **may use
GBV_q and GBV_{q−1}** — the ⅔ / ⅓ lags are both printed by then. (Lane 1's `kernel_engine_v2` refuses same-day inputs
by design; call it with `as_of = d + 1 day` and say so in the note, or use its post-letter path — never re-derive λ.)

## 2. Morning-of-print consensus is pre-letter

FORMAT 1.0 §baseline_street: `16_consensus_at_print_merged.next_q_cons_revenue_musd`, "whose `as_of` is the morning of the
print date — ABNB reports after the close, so that number precedes the letter and the guide." The same rows live in the L0
register with `role = pre_guide` (IDs `PG-<quarter>-revenue`; the quarter is the one being *guided*) and `role = at_print`
(IDs `AP-…`; the quarter being *printed*), `as_of_timestamp = d`, `pit_usable = True`, vendor named. Those rows are
admissible at vintage *d*. Inadmissible: any row stamped after *d*; `pit_usable = False`; `vendor_attributed = False`
unless the brief allows it with a flag; every `role = current` row (September-2026 vintages) at a historical date.
The hard rule stands: the 6 Aug 2026 pre-guide 3Q26 Street is **LSEG $4,610M** and nothing else.

## 3. Executable returns start at the next open

`data/processed/forecast_methods/returns_v1/earnings_reactions_open_v1.csv` (public OHLC, manifest with timestamp):
entry = first trading day after *d*, at the **open**; `excess_open_{1,5,20,60}d_pct` = ABNB − QQQ, close *h* bars later
÷ entry open − 1. `gap_pct` (overnight) is not executable and enters no return statistic. The legacy close-to-close file
ties out to this one within 0.05pp (`cc_1d_pct`) and is not to be used for return legs.

## 4. Registration dates

Historical W1 / W2 rows: vintage = the guide date, through `harness_v1_1.registry.register` (its W1/W2 validator is the
frozen 1.0 code). LIVE rows (targets 2026Q3, 2026Q4, 1Q27): vintage = **the real run date** (`RUN_DATE`), FORMAT 1.1.
Never backdate a September forecast to 2026-09-11; never date it 5 Nov. Subagents register; only the parent scores.

## 5. Worked example — the 6 Aug 2026 letter

vintage *d* = 2026-08-06 · printed: 2Q26 GBV, nights, ADR, revenue · guide issued: 3Q26 $4,690–4,770M (mid $4,730M) ·
pre-guide Street for 3Q26: LSEG $4,610M, stamped 2026-08-06 (morning) → admissible · kernel at *d* uses GBV_2Q26 (⅔) and
GBV_1Q26 (⅓) with the λ_Q3 and cushion fitted on data through 1Q26 prints → S = kernel_guide / 4,610 − 1 ·
executable entry: 2026-08-07 open · `excess_open_20d_pct` for that event is in the returns file (+12.8pp).
