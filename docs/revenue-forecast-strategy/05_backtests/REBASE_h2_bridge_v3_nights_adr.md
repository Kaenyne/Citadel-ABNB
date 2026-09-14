# REBASE — the H1/H2 bridge's nights and ex-FX ADR lines re-based to the team baseline and the ADR v3 card (v3)

Package: `analysis/src/h1_to_h2_bridge_v3.py` (a COPY of `h1_to_h2_bridge_v2.py`, modified; v1 and v2 untouched)
Data: `data/processed/h2_bridge_v3/` (v1 and v2 output folders untouched)
Registry: nothing new; `harness/score.py` NOT run, nothing to score.
Run date 2026-09-12. FX inputs through **2026-09-04**. Follows `FXSWAP_h2_bridge_kernel_fx.md` (v2) on the same branch, `krish/fx-line-swap`.
Author: Krish (with Claude).

## Verdict first

**Done. The bridge now shares every input with the ADR v3 card and reproduces it: nights, reported ADR and GBV agree to $0.02bn in both quarters (`h2_bridge_v3_card_check.csv`).** The two stale lines were replaced, not adjusted: 3Q26 nights go from the pattern-plus-overlays 8.5% to the team baseline 9.9%, and ex-FX ADR goes from the pattern-plus-seats 3.0% / 3.3% to the card's 3.9% / 4.1%. 4Q26 nights were already at 8.1% by coincidence (v1's unfitted "half lap" overlay landed on the same number as the case B global lap), so that line's value does not move but its source does.

**Net effect on the number that matters: 4Q26 revenue on the GBV-lag path rises $43M to $3,178M, and the implied Q4 guide midpoint (if the historical cushion holds) rises to $3,059M.** Together with the v2 FX swap (−$31M) the two-step rebuild is +$12M against the 10 Sep v1. The 3Q26 GBV behind the Q4 lag is now $26.03bn, which sits $155M below the frozen card's $26,185M and $220M below B4's ex-FX-acceleration break-even of $26,250M, so on B4's reading C the ex-FX growth step into 4Q26 is a small deceleration, not the "flat" the frozen card gives. That is stated, not hidden.

## Exact commands

```bash
cd "<repo root>"
python analysis/src/h1_to_h2_bridge_v3.py data/raw/fred     # exit 0, ~5 s, 15 CSVs to data/processed/h2_bridge_v3/
```

## 1. What was re-based (`h2_bridge_v3_rebased_lines.csv`)

| line | quarter | v2 (pattern + overlays) | **v3 adopted** | band | source |
|---|---|---|---|---|---|
| nights y/y | 3Q26 | 8.49% (pattern 9.49 − 1.5 RNPL lap + 0.5 World Cup) | **9.89% (146.8mm)** | 8.5 to 11.0 | team baseline, PR #32 base = reviews stays index read (`nights_baseline_reconciliation.csv`; q3nowcast E) |
| nights y/y | 4Q26 | 8.12% (pattern 10.62 − 2.5 RNPL lap) | **8.12% (131.8mm)** | 8.0 to 8.86 | ADR v3 N memo case B (WS-D global lap, 45% ex-NA split); case A 8.86% (132.7mm) is the top of the band |
| ADR ex-FX y/y | 3Q26 | 3.01% (pattern 3.5 − 0.49 seats) | **3.86%** | 2.46 to 5.27 (central) | ADR v3 card, `v3_with_K`, midpoint FX; `v3_without_K` 3.69 carried as comparison |
| ADR ex-FX y/y | 4Q26 | 3.35% (pattern 3.83 − 0.49 seats) | **4.07%** | 2.62 to 5.51 (central) | same; `v3_without_K` 3.69 |

The seats-dilution overlay (−0.49) is retired rather than stacked, because the card's ex-FX already contains `new_business_seats` −0.48 (`P1_card_v3_terms.csv`). The three nights overlays are retired with a stated reason each: the baseline already carries the lap; WS10 says the World Cup gives no lift to 3Q26 booked nights. All retired rows stay in `h2_bridge_overlays.csv` with `pts = 0` so a reader can see what v1 applied.

The card variant carried is `v3_with_K` because it is the ADR v3 synthesis headline (3Q26 reported +3.4%, $177.2). The K line is worth 0.17pp in 3Q26 and 0.37pp in 4Q26 and met its criterion by 0.003 to 0.007, which K's own note calls a nudge; the without-K value is one column away.

## 2. Card consistency check (`h2_bridge_v3_card_check.csv`)

| quarter | object | bridge | card | diff |
|---|---|---|---|---|
| 3Q26 | ADR reported y/y | 3.43% | 3.43% | 0.00 |
| 3Q26 | ADR $ | 177.17 | 177.17 | 0.00 |
| 3Q26 | nights, mm | 146.81 | 146.80 | 0.01 |
| 3Q26 | GBV, $bn | 26.03 | 26.01 | 0.02 |
| 4Q26 | ADR reported y/y | 4.22% | 4.22% | 0.00 |
| 4Q26 | ADR $ | 174.58 | 174.57 | 0.01 |
| 4Q26 | nights, mm | 131.80 | 131.80 | 0.00 |
| 4Q26 | GBV, $bn | 22.99 | 23.01 | −0.02 |

The $0.02bn GBV differences are compounding y/y rates on the 2025 base (bridge) versus ADR $ × nights (card). The script asserts the card's FX effect equals the bridge's before running.

## 3. What moved (`h2_bridge_v3_vs_v2_delta.csv`, and against v1)

| object | v1 (10 Sep) | v2 (FX swap) | **v3** | v3 − v2 |
|---|---|---|---|---|
| nights y/y, 3Q26 | 8.49 | 8.49 | **9.89** | +1.40 |
| ADR ex-FX, 3Q26 / 4Q26 | 3.01 / 3.35 | 3.01 / 3.35 | **3.86 / 4.07** | +0.85 / +0.72 |
| ADR reported, 3Q26 / 4Q26 | 4.14 / 5.44 | 2.58 / 3.50 | **3.43 / 4.22** | +0.85 / +0.72 |
| GBV y/y, 3Q26 / 4Q26 | 12.98 / 14.00 | 11.29 / 11.90 | **13.66 / 12.68** | +2.36 / +0.78 |
| 3Q26 GBV assumed for the Q4 lag, $bn | 25.87 | 25.49 | **26.03** | +0.54 |
| 4Q26 lagged GBV base, $bn | 26.32 | 26.06 | **26.42** | +0.36 |
| **4Q26 revenue, GBV-lag path, $M** | 3,166 | 3,135 | **3,178** (3,156 to 3,201) | **+43** |
| 4Q26 revenue y/y, GBV-lag path | 13.95% | 12.84% | **14.40%** | +1.56 |
| 4Q26 implied guide midpoint if the Q4 cushion (3.9%) holds, $M | 3,047 | 3,018 | **3,059** | +42 |
| 3Q26 revenue, $M | 4,804 | 4,804 | 4,804 | 0 (base is printed GBV) |

FX lines and the pattern-route revenue y/y are unchanged from v2 by construction.

## 4. Two things the reader should not miss

**(a) The bridge's 4Q26 revenue ($3,178M) is now $44M above the ADR v3 card's own comparison revenue ($3,134M) on identical nights, ADR and GBV.** The difference is conversion, not inputs: the card multiplies 4Q26 GBV by the 4Q25 same-quarter take rate (13.62%), the bridge multiplies the ⅔/⅓ lagged GBV by the 2023–25 mean Q4 conversion (12.03%). The card labels its revenue a comparison column, not an input; the bridge's kernel route is the one the FX programme built its FX arithmetic on. Both sit above the anticipated guide arithmetic ($3,050 to $3,100M) and below Zacks consensus ($3,200M). The bridge's implied guide midpoint of $3,059M is the number to set against the $3,050 to $3,100M range, and it lands inside it.

**(b) The 3Q26 GBV of $26.03bn sits below B4's ex-FX-acceleration break-even ($26,250M under reading C; $26,288M under reading A).** On B4's arithmetic the kernel base steps down about 1.6pp into 4Q26 and the FX carried in it steps down 1.9pp, so ex-FX decelerates by about 0.3pp. The frozen card ($26,185M) gives −0.2pp; the architect's central ($26,300M) gives +0.1pp. The sign is worth a quarter of a percent of GBV, and the bridge is on the deceleration side of it. Do not write "ex-FX accelerates" off these numbers.

## 5. What failed or was not done

1. **Nothing was registered, so nothing was scored.** The bridge's 4Q26 revenue dollars remain unscored; that is WP-K0's object.
2. **The 3Q26 nights band (8.5 to 11.0) is hard-coded from the q3nowcast synthesis**, not read from a file, because the reviews index writes its band into prose and the card's source string. Stated so it is checked when the September re-run moves it.
3. **The v2 inconsistency stands**: the dollar path implicitly carries about +0.15pp of 4Q26 FX (Φ on the ADR-FX midpoint) against the +1.0pp kernel line on the basket. Re-basing nights and ADR does not touch it; 5 Nov settles it.
4. **The regional nights lines (NA / EMEA / LatAm / APAC) in the projection are still pattern values** and were not re-based to WS-C's regional split; they feed nothing downstream in the bridge.
5. **The 3Q26 revenue-dollar row does not change** because its base is printed 1Q26 and 2Q26 GBV; the re-based 3Q26 nights and ADR only enter through the 4Q26 lag.

## 6. Parameter count

Zero new free parameters. Point estimates and bands are imported from the nights baseline reconciliation and the ADR v3 card and applied by arithmetic.

## 7. Files written (all new)

`analysis/src/h1_to_h2_bridge_v3.py` · `data/processed/h2_bridge_v3/` (the v2-format CSVs rebuilt under v3, `h2_bridge_v3_fx_line.csv`, `h2_bridge_v3_rebased_lines.csv`, `h2_bridge_v3_card_check.csv`, `h2_bridge_v3_vs_v2_delta.csv`, `h2_bridge_v3_vs_v1_delta.csv`, `README.md`) · this note · one WORKBOARD row.

## RESUME

The next agent should treat `h1_to_h2_bridge_v3.py` as the bridge to quote and v1/v2 as history. When the September Inside Airbnb dumps land and the ADR v3 T trigger re-runs the card, re-run v3 so the card check stays at zero; if `adr_card_v3.csv` changes its variant or nights case names, the three `.iloc[0]` lookups near the top will raise, which is intended. On 5 Nov, feed the printed 3Q26 nights, ADR, FX and GBV into the panel, re-run, and read the 4Q26 revenue-dollar row against the printed Q4 guide; the two open sign questions are the ex-FX acceleration (§4b, break-even $26,250M of 3Q26 GBV) and the FX estimator (v2 §4). Do not stack any seats, lap or FX overlay on top of the re-based lines; each already contains the term.
