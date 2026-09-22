# ADR line v1b — pre-registration: does supply-demand balance (utilisation) explain the like-for-like line?

Date 2026-09-22, written before any score is computed (the utilisation series itself was built first, without
being placed against the core). Context: Theo asks for an ADR engine that uses our alt-data with a more complex
model and lands at or below the Street's 4Q26 ADR ($171.33). **DEC-0016 stands**: no input is chosen to reach a
number. This registration tests the one supply-demand object a lodging analyst would ask for first — occupancy
leads rate — on the only supply data the repo has (Inside Airbnb listing counts), and reports the result
whichever way it lands. If it fails, the ADR line's core stays the carry of `adr_v1_design.md` §3.

## 1. Object

`util_yoy(t)` = year-on-year change of **stays per active listing** in quarter `t`, vintage-matched (reviews and
listing counts from the latest Inside Airbnb dump for `t`, from the dump ~12 months older for `t−4`, posting lag
2 months trimmed; the E4 rule). Global and by region (NAM / EMEA / LatAm / APAC on the reviews_index_v2 country
map). Written to `data/processed/pitch_model_v2/adr_engine/utilisation_vmatch_quarterly.csv` before this file.

Hypothesis (the lodging analyst's): like-for-like price growth follows utilisation with a lag — hosts raise rates
when their calendars fill and cut when they empty; supply growing faster than stays lowers utilisation and
compresses like-for-like ADR.

## 2. Target and models

Target: `core(t)` from `exfx_history.csv` (the residual net of the bundle), 1Q23–2Q26, n 14. Also reported on the
raw residual.

- **U1**: `core(t) = a + φ·core(t−1) + β·util_yoy(t−1)`, OLS refit walk-forward (features known one quarter before
  the print: the dump for `t−1` lands inside quarter `t`; **PIT caveat stated**: today's vintage is used for all
  history, as the reviews index does, so this is a description not a PIT backtest).
- **U2**: `Δcore(t) = β·Δutil_yoy(t−1)` (no intercept, first differences).
- Comparators: carry (naive: `core(t−1)`), AR(1) on core (K4 ρ 0.75 form, refit).
- Windows: W1 targets 1Q24–2Q26 (n 10; fits use ≥ 4 prior points), W2 targets 1Q25–2Q26 (n 6).
- **Pass line**: RMSE ratio to the carry ≤ 0.75 on **both** windows, and β < 0… no: β **> 0** (higher utilisation →
  higher price) with p ≤ 0.10 on the full sample. Both conditions. If it passes, U1 becomes a labelled
  **support row** for the core (not the base; DEC-0020/0028 mechanics-first), and its 3Q26/4Q26 read is shown
  beside the carry. If it fails, it is reported as a fail and the constellation gains a fourth panel.
- Also reported, descriptive: contemporaneous correlation of `util_yoy` with `core` and with disclosed ex-FX ADR
  by region; the 3Q26 quarter-to-date utilisation read.

## 3. What will not be done

No lag or window chosen after results; no regional pick after results; no scenario chosen by its 4Q26 output.
The 4Q26 ADR that comes out of the base construction is not moved by this note.

## 4. Results (filed after the run; nothing above changes)

Filed 2026-09-22 after the run (`utilisation_vmatch_quarterly.csv`, `utilisation_test_scores.csv`,
`utilisation_test_correlations.csv`). 123 markets, 119 with a matched prior vintage.

**Verdict: FAIL on the pre-registered line, every region.** No series reaches a ratio ≤ 0.75 vs the carry on both
windows.

| region | β (full, n 13) | p | r(util t−1, core t) | U1 ratio W1 / W2 | U2 ratio W1 / W2 | AR(1) ratio |
|---|---|---|---|---|---|---|
| GLOBAL | 0.07 | 0.62 | 0.31 | 1.73 / 1.52 | 1.07 / 0.87 | 1.24 / 1.53 |
| **NAM** | **0.32** | **0.002** | **0.77** | 1.01 / 0.87 | 0.79 / 0.74 | |
| EMEA | −0.10 | 0.36 | −0.13 | 4.73 / 1.62 | 1.52 / 1.02 | |
| APAC | −0.02 | 0.79 | 0.11 | 1.54 / 1.54 | 1.02 / 1.15 | |
| LatAm | −0.02 | 0.84 | −0.14 | 1.43 / 1.59 | 1.09 / 1.17 | |
| ex-LatAm composite (descriptive) | 0.06 | 0.72 | 0.28 | 1.91 / 1.55 | 1.16 / 0.61 | |

Reading, honest: (1) The lodging analyst's mechanism shows up **only in North America**, and only in sample:
lagged NA utilisation explains the core (β 0.32 per point of utilisation y/y, t ≈ 3.9) and its first differences
(r 0.60), but the walk-forward does not clear the line (1.01 / 0.87; first-difference form 0.79 / 0.74) — a
description with n 13, not a forecasting edge. (2) Its **direction argues for persistence, not reversion**: NA
stays per listing fell every year 2022–2025 (−1.4 to −5.7% y/y) and turned **positive in 1H26 (+1.3, +1.8%)** while
global listings growth slowed from 16% to 7%; that is the supply-demand picture behind NA ADR ex-FX moving to
+5–7%, and it is the opposite of what a below-Street ADR needs. (3) The LatAm series (+45–65% y/y every quarter)
is a vintage artefact of the listing counts, not utilisation; it is reported and not used. (4) The core stays the
carry of `adr_v1_design.md` §3; this test joins the constellation (§7) as a fourth, labelled panel.
