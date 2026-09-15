# WS06: FY27 quarterly revenue path v2 — PR #32 audited, re-based on the bridge v3 exit

Agent: Claude (Fable 5.1), margin build run, 13-14 Sep 2026. Branch `krish/margin-build`, worktree `citadel-abnb-margins`.
Package: `analysis/src/margin_build/06_fy27_path_v2/` (`run.py`, `fig.py`, `README.md`), data `data/processed/margin_build/06_fy27_path_v2/`,
figure `analysis/figures/margin_build/06_fy27_path_v2_quarterly.png`, manifest `data/manifests/margin_build/06_fy27_path_v2.csv`.
A first WS06 agent wrote most of `run.py` before a usage-limit kill (01:24); this session audited it, fixed the GBV convention, added the
INT-06 take-rate memo, the FY28 comparison, the figure, the README and this note. Nothing outside the WS06 folders was modified.

## Bottom line

**FY27 revenue, base $15,829M (+10.94% on the v2's own FY26 $14,268M); bear $14,948M (+5.2%); bull $16,571M (+15.7%).** The base sits inside
the pre-registered B3 band (+9.18 to +11.52%) and $10M from the LSEG FY27 mean ($15,819M, n 44, obs 8 Sep 2026, pulled 13 Sep 01:15) —
**but the composition is not the Street's.** v2 nights are **+6.6% for FY27** (B3 driver base +9.5%, WS29 +9.2%, reverse-DCF market path 8-9%),
offset by reported ADR +2.7% (B3 +1.9%) and a higher FY26 base (bridge v3 4Q26 $3,178M against B3's kernel $3,111M). The quarterly shape is
front-loaded: 1Q27 +14.0% (LSEG +12.4%), then 2Q27 +11.7%, 3Q27 +9.9%, 4Q27 +9.1% (LSEG +11.1% / +11.6%). The kernel carries 2H26's +13% GBV
growth into 1H27 revenue while nights decelerate to ~6% once the global product bundle laps; the Street runs ~11-12% every quarter.

**What changed against PR #32 and why.** PR #32 gave two FY27 nights rates (+8.2% NA-only lap, +6.4% bundle laps everywhere) and never chose or
summed either; 3Q27/4Q27 levels are blank in its CSV. Bridge v3 adopted the *global* lap for 4Q26 (case B, 8.12%), which makes the NA-only case
inconsistent with the exit and the "everywhere from 1Q27" case a double count of the fee/cancellation leg that already lapped in 4Q26. v2 laps
the ex-NA fee/cancellation leg from 4Q26 (inside the exit), the ex-NA RNPL leg 40% in 1Q27 and fully from 2Q27 (WS-D dates: live 17 Feb to
4 Mar 2026), phases WS10's ex-NA rate linearly from its 4Q26 value so 1Q27 does not jump, corrects the NA share weight, and adds two dated
events (Middle East base +1.0 in 1Q27, World Cup booking lap -0.5 in 2Q27). Result: FY27 nights +6.6%, between PR #32's two cases and closer
to the global-lap one, on real quarterly levels that sum.

## Pre-registered pass line (from the prompt) and result (`06_pass_line.csv`, 7 tests, 7 pass)

| test | value | pass |
|---|---|---|
| FY27 base revenue growth inside B3 band +9.18 to +11.52 | 10.94 | yes |
| quarterly revenue sums equal annual, all scenarios FY26-FY28 | asserted in code | yes |
| 1Q27 nights growth within 2 pts of the 4Q26 exit (8.12) unless a named lap explains it | +0.09 (8.21 vs 8.12) | yes |
| 1Q27 revenue growth within 2 pts of the 4Q26 exit | -0.39 (14.01 vs 14.40) | yes |
| every number traceable to an input file | 55 assumption rows, 10 judgement | yes |
| 4Q26 exit re-derived on the v2 decomposition vs bridge 8.12 | 8.157 | yes (<0.1) |
| 2027 seasonal shares within 1 pt of the 2023-25 mean | max dev 0.23 pt | yes |

## Exact commands

```
cd "C:\Users\krish\citadel-abnb-margins"
python analysis/src/margin_build/06_fy27_path_v2/run.py      # exit 0, ~3 s; shells to py -3.13 for fig.py
```

## The quarterly table, base (`06_revenue_path_wide.csv`; 3Q26 and 4Q26 are bridge v3 unchanged)

| | nights y/y | nights mm | ADR ex-FX | FX pts ADR | ADR $ | GBV $bn | GBV y/y | revenue $M | rev y/y | printed take rate | rev FX memo pp |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 3Q26 | 9.89 | 146.8 | 3.86 | -0.43 | 177.17 | 26.03 | 13.66 | 4,804.0 | 17.31 | 18.46 | 3.00 |
| 4Q26 | 8.12 | 131.8 | 4.07 | 0.15 | 174.58 | 22.99 | 12.68 | 3,178.1 | 14.40 | 13.83 | 0.98 |
| 1Q27 | 8.21 | 169.0 | 3.48 | -0.30 | 192.75 | 32.60 | 11.64 | 3,053.1 | 14.01 | 9.37 | 0.93 |
| 2Q27 | 5.93 | 157.1 | 3.09 | -0.19 | 189.05 | 29.65 | 9.00 | 4,029.0 | 11.67 | 13.59 | 0.62 |
| 3Q27 | 6.23 | 156.0 | 2.65 | 0.03 | 181.92 | 28.39 | 9.08 | 5,280.7 | 9.92 | 18.60 | 0.31 |
| 4Q27 | 6.04 | 139.8 | 2.16 | -0.28 | 177.85 | 24.83 | 8.03 | 3,465.8 | 9.05 | 13.96 | 0.38 |
| **FY26** | 9.40 | 583.1 | | | | 105.4 | 15.46 | **14,268.1** | 16.56 | 13.54 | |
| **FY27** | **6.64** | 621.8 | | | +2.72 rep. | 115.5 | 9.54 | **15,828.6** | **10.94** | 13.71 | ~0.5 |
| FY28 (flagged) | 6.04 | 659.4 | | | +2.03 | 124.9 | 8.20 | 17,137.4 | 8.27 | 13.72 | 0 |

Bear / bull, FY27: nights +3.6 / +9.2%; reported ADR -0.3 / +5.1%; GBV +3.3 / +14.7%; revenue $14,948M (+5.2%) / $16,571M (+15.7%).
Per quarter in `06_comparison_quarterly.csv`. Bear 2H26 uses the bridge's band lows jointly for nights and ex-FX ADR (bull the highs); 3Q26 revenue is
identical across scenarios because the kernel reads only 1Q26/2Q26 GBV, which are printed.

Revenue is `lambda_q x (2/3 GBV_{q-1} + 1/3 GBV_{q-2})` with lambda the 2023-25 mean by fiscal quarter (Q1 0.1272, Q2 0.1371, Q3 0.1724, Q4 0.1203;
Q3/Q4 equal bridge v3's `conversion_mean` exactly, Q1/Q2 are 0.03pt from B3's on GBV rounding). GBV is compounded y/y on the printed prior-year
GBV (bridge convention); the nights x ADR identity gap is a memo line (-0.07% to +0.17%). The printed take rate is revenue / same-quarter GBV.

## Audit of PR #32 (`06_pr32_rederivation.csv`), numbered, with severity

1. **HIGH — no FY27 object existed.** Every PR #32 NA and total rate re-derives to 0.00 from its stated features (n 18 rows), so the arithmetic is
   sound; but `nights_quarterly_total.csv` leaves 3Q27/4Q27 `nights_mm` blank and the note's "+8.2% / +6.4%" are uniform rates, not sums. Summing
   levels on PR #32's own FY26 (584.1mm) gives +8.17% / +6.42% — same numbers, but the margin model needs the levels, which v2 supplies.
2. **HIGH — the lap placement is inconsistent with the adopted exit.** Bridge v3's 4Q26 (8.12%) is the ADR v3 N memo case B: the ex-NA fee and
   cancellation legs (global, Oct-Dec 2025 per the 3Q25/4Q25 letters) lap in 4Q26, worth 0.45 x the ex-NA bundle. PR #32's NA-only case (8.9% in 4Q26,
   8.17% through 2027) never laps them; its "everywhere from 1Q27" case laps the whole bundle flat from 1Q27 and would count the fee/cancellation
   leg twice once the 4Q26 exit already carries it. v2: fee/cancel leg inside the 4Q26 exit; ex-NA RNPL leg (55% of the bundle, live 17 Feb-4 Mar 2026,
   `D1_lap_anniversary.csv`) lapped 40% in 1Q27 (judgement: last 5-6 of 13 weeks, ramping) and fully from 2Q27.
3. **MEDIUM — NA share weight.** PR #32 sizes the ex-NA bundle with the FY27 forecast-year share 0.266 (giving 1.75 pts of total nights) and uses 0.266 as
   the 2027 y/y weight. The y/y weight is the prior-year-quarter share (0.291 1H26 chained from FY25's 29.6%, 0.288 3Q26, 0.282 4Q26 per WS10), and the bundle
   was measured in 1Q26 at ~0.29 NA share: 3.0 - 0.288 x 4.69 = **1.65 pts**, not 1.75. Worth 0.1 pt of 2027 nights; the corrected figure re-derives the
   4Q26 exit at 8.16 vs the adopted 8.12 (which was built on 1.75). 4Q26 is carried unchanged from the bridge as instructed; the 0.04 is disclosed, not hidden.
4. **MEDIUM — year-boundary jump.** PR #32 holds WS10's FY27 total (9.15%) in every 2027 quarter after 9.94% in 4Q26 and drops the NA underlying by 1.0 pt at
   1Q27, so 4Q26 -> 1Q27 steps down ~0.8 pt with no named cause. v2 phases the WS10 ex-NA rate linearly from its 4Q26 value (11.1%) so that the four-quarter
   mean equals WS10's FY27 rate (10.3%); the NA step stays at 1Q27 (it is the choice model's annual rate) but is offset by the Middle East base effect.
5. **MEDIUM — dated events missing.** (a) Mertz, 1Q26 call: nights grew 9% after ~100bp Middle East headwind -> 1Q27 laps an easy base, +1.0 (bear 0 for
   recurrence). (b) World Cup nights were booked 4Q25-2Q26 (WS10, WS29), never sized by Airbnb -> 2Q27 lap -0.5 base, -0.75 bear, 0 bull (judgement).
   (c) The July 2026 RNPL eligibility expansion (D044) laps in **3Q27**, not 2Q27 as `29_fy27_quarterly_path.csv` labels it; unsized, carried at 0.
6. **LOW — scope.** PR #32 is nights only. The only prior quarterly FY27 revenue path is WS29's, whose FX line B4 rejected (double subtraction) and whose
   nights are WS10 with no lap at all (FY27 +9.2%). v2 supplies ADR ex-FX (ADR v3 card terms carried; residual by the K4 AR(1) rho 0.747, const 0.75, n 14,
   iterated from the adopted 4Q26 value 4.85; K fee-mechanics line 0.007 x change in y/y migrated share, turning negative in 4Q27 as migration completes;
   seats dilution -0.565 for 2027), ADR FX (midpoint of the reconstructed EUR fit and a baskets proxy, spot held at EUR/USD 1.1618; +/-1sd USD variants
   from `fx_lag_v2/23_forecast_4q26_v2.csv`; note the kernel file's 4Q27 lag-0 basket is 0 on all paths, so the variants converge there), and revenue FX memo
   (Phi x 0.851, spot held: 0.93 / 0.62 / 0.31 / 0.38 pp).
7. **LOW — seasonal shape holds**: 2027 shares 27.2 / 25.3 / 25.1 / 22.5 vs 2023-25 mean 26.95 / 25.45 / 25.10 / 22.50 (`06_seasonal_check.csv`).
8. **INFO — GBV convention.** The first draft built GBV as nights x ADR and missed bridge v3's 4Q26 revenue by $1.4M. Bridge v3 compounds y/y rates on the
   printed prior-year GBV (`h1_to_h2_bridge_v3.py` lines 423, 508); adopting that reproduces $4,804.04M / $3,178.11M to the dollar (asserted).

### Corrections to existing work (recorded, not edited)
- `research/notes/nights_quarterly.md` / `nights_quarterly.py`: ex-NA bundle 1.75 uses the forecast-year NA share (finding 3); FY27 rates never summed to levels (finding 1).
- `data/processed/overnight/29_fy27_quarterly_path.csv` `lap` column: RNPL eligibility expansion laps 3Q27, not 2Q27 (finding 5c).

## Comparison columns (never inputs), FY27 (`06_comparison_annual.csv`, `06_comparison_fy28.csv`)

| source | FY27 $M | growth | nights | ADR |
|---|---|---|---|---|
| **06 v2 base / bear / bull** | **15,829 / 14,948 / 16,571** | **10.94 / 5.17 / 15.73** | 6.64 / 3.64 / 9.18 | 2.72 / -0.33 / 5.09 |
| PR #32 base, NA-only lap / global lap | — | — | 8.17 / 6.42 (re-derived sums) | — |
| WS29 base (bear / bull) | 15,804 (14,318 / 16,910) | 11.55 (3.17 / 16.96) | 9.2 | — |
| B3 / l1-reconciliation-v2, w = 0.33 / 0.50 / 2/3 | 15,720 / 15,780 / 15,838 | 9.18 / 10.35 / 11.52 | 9.46 (w=2/3) | 1.88 |
| LSEG FY27 (n 44, obs 8 Sep, pull 13 Sep 01:15) | 15,819 | (+11.5% on LSEG's own FY26 14,190) | — | — |
| Bloomberg BEST FY27 (pull 5 Sep, pull-date anchored) | 15,760 | — | — | — |
| LSEG sum of 1Q27-4Q27 (n 19-21) | 15,846 | — | — | — |
| reverse DCF, market / Street path (midpoints) | ~15,800 | 10.4-11.5 | 8-9 | 3.0 |
| reverse DCF, management delivered | 16,025 | 12.6 | 10.0 | 3.0 |
| FY28: 06 v2 continuation (FLAGGED) / WS07 FY2028E lever / LSEG FY3 (n 27) | 17,137 / — / 17,535 | 8.27 / 10.7 (GBV proxy) / 10.85 | 6.04 / 8.0 / — | 2.03 / 2.5 / — |

Quarterly, base vs LSEG (n 19-21, obs 13 Aug-8 Sep): 1Q27 3,053 vs 3,010 (+1.4%); 2Q27 4,029 vs 4,037 (-0.2%); 3Q27 5,281 vs 5,270 (+0.2%);
4Q27 3,466 vs 3,529 (-1.8%). l1-v2 kernel (w=2/3) quarterly: 2,996 / 4,037 / 5,353 / 3,451 — v2 is above it in 1Q27 (higher FY26 exit GBV) and below in 3Q27 (lap).

## INT-06 take-rate asymmetry, carried into the path file (3Q26 rows)

The pre-registration card computes the printed take rate as revenue / same-quarter GBV, with revenue near-fixed by guide x cushion ($4,816.1M, sd 1.0%) and
GBV the uncertain leg (sd 3.2%), so the take rate prints **inversely** to GBV. At the v2 base GBV $26,028M the registered revenue gives 18.50% and P(>=18.10) =
0.80 (card grid: 25,900 -> 0.85, 26,185 -> 0.73); bear GBV $25,351M -> 19.00%, P 0.97; bull $26,649M -> 18.07%, P 0.48. Kernel revenue $4,804.0M at the base
GBV gives 18.46%. Flip GBV $26,608.3M. Lines `take_rate_int06_*` in `06_revenue_path_3q26_4q27.csv`; the registered 18.14% / sd 0.4628 are in `06_assumptions.csv`.

## Assumptions and parameter count (`06_assumptions.csv`, 55 rows, 10 judgement)

Sourced (45): kernel lambdas (4) and w; bridge v3 2H26 lines (8); PR #32 fitted NA product (2, fitted on 4 WS10 NA observations); choice-model underlying 2026/27 (2);
management's global ~3 pts; NA shares 3Q26/4Q26 (WS10); WS-D 45% split; WS10 ex-NA rates (6); ADR v3 card terms (5), residual 4Q26, AR(1) (2), K coefficient, K line;
EUR fit (2, exact reconstruction of `h2_bridge_fx.csv`); spot EUR; FX mapping; Middle East 1.0; GBV convention; INT-06 constants.
Judgement (10): 1H26 NA share chain 0.291; 1Q27 ex-NA RNPL lap fraction 0.40; ex-NA phasing rule; World Cup -0.5; RNPL-expansion lap 0; PR #32's bull lever +2.35 and bear
tranche-2 -1.0 (carried); AR(1) as the multi-quarter residual rule; baskets proxy ratio 0.699; FY28 continuation rule.
Free parameters that were *fitted* anywhere in the chain: 2 (NA product, PR #32) + 2 (AR(1), n 14) + 2 (EUR fit, n 4) + 4 lambdas (n 3 each) = 10; the rest are carried, pinned or imposed.

## What failed or is weak

- None of this is backtested: it is a forward build on the adopted exit and the repo's own rules. The residual AR(1) (n 14) and the K line are the ADR legs with the least
  evidence (ADR v3 K note: "a nudge"); the ex-NA RNPL split (45%) and the 1Q27 fraction (0.40) carry the nights swing. A 10-pt move in the split is ~0.16 pt of FY27 nights.
- The FY27 band is wide because bear/bull stack the bridge's 2H26 band lows/highs on nights and ADR jointly, then PR #32's levers and the +/-1sd USD paths. It is a
  scenario envelope, not a predictive interval.
- The venv's `python` has no scipy (the brief says it does); the INT-06 normal CDF uses `math.erf`.
- LSEG quarterly panels for 2027 are thin (n 19-21) and three of the four were last revised 13 Aug; treat the quarterly comparison loosely.

## For the model (exact series the margin model reads)

File `data/processed/margin_build/06_fy27_path_v2/06_revenue_path_3q26_4q27.csv` (quarter x scenario x line x value x source) and `06_revenue_path_wide.csv`;
annuals `06_annual_fy26_fy28.csv`. Lines per quarter and scenario (bear/base/bull): `nights_yoy_pct`, `nights_mm`, `adr_exfx_yoy_pct`, `fx_pts_adr`, `adr_reported_yoy_pct`,
`adr_usd`, `gbv_busd`, `gbv_yoy_pct`, `lagged_gbv_busd`, `revenue_musd`, `revenue_yoy_pct`, `revenue_conversion_lo/hi_musd` (kernel-lambda min/max), `take_rate_printed_pct`,
`take_rate_prior_year_pct`, `take_rate_change_pts`, `revenue_alt_same_q_take_rate_musd`, `fx_pts_revenue_memo`, `revenue_exfx_yoy_memo_pct`, `gbv_identity_gap_pct`;
3Q26 adds `take_rate_int06_*`. Quarters 3Q26-4Q27 all scenarios; 1Q28-4Q28 base only, source flagged. Units: %, mm nights, $, $bn GBV, $M revenue.
Regional split is not in the file (WS10's shares 28.8 / 28.2 / 26.6 NA are in `06_assumptions.csv` and `06_nights_build.csv`).

## For the 5 Nov card

The 4Q26 guide will not separate the cases (both inside D's inconclusive 7.6-9.4%); the read is any restated bundle contribution for 3Q26 (<=1.5 pts case B, >=2.5 case A)
and whether management gives FY27 nights colour. v2's implicit FY27 claim is that the Street's ~+11.5% every quarter turns into 1H27 ~+13% / 2H27 ~+9.5%; the 3Q27 and
4Q27 revenue rows ($5,281M / $3,466M) are where v2 sits below the Street (-0.2% / -1.8%), and the FY27 level does not.

## RESUME

WS06 is complete: `run.py` exits 0 and writes 15 CSVs, the figure and the manifest; all 7 pass-line tests pass. WS06v should re-derive (i) the 4Q26 exit on the v2
decomposition (8.157 vs 8.12: the 1.65-vs-1.75 bundle sizing, finding 3), (ii) the 1Q27 partial-lap fraction 0.40 against the WS-D go-live dates, (iii) the ex-NA phasing
(linear from WS10's 4Q26 rate, four-quarter mean = WS10 FY27) and whether WS10's FY27 regional rates already embed any product lap (if they do, the 2027 lap is double
counted and FY27 nights are ~+8.3%, `sens_no_exna_lap_case_A_pct` in `06_nights_build.csv`), and (iv) the kernel-lambda choice (2023-25 mean; the l1-v2 band on w is
the published uncertainty). If WS06v changes anything, write `_v2b` files in this folder; M6 should read the base/bear/bull revenue paths from `06_revenue_path_wide.csv`
and treat FY28 as flagged.
