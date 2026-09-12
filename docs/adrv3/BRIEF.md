# ADR v3 run, 11 Sep 2026: shared brief

Branch `krish/adr-v3`, worktree `C:\Users\krish\citadel-abnb-adrv3`, based on main 5bd2d08 (PR #44 merged). Owner Krishang Surapaneni, compiled with Claude Code. Follow-up to the ADR Q3 nowcast (PR #44, `docs/adrq3/SYNTHESIS.md`), whose card v2 tied naive (walk-forward ratio 0.994 on 1Q24-2Q26, 1.042 on 2Q24-2Q26) with all of the error in the unobserved pricing residual.

## The question
Can the ADR card be made to beat naive honestly, by (a) scoring it on a target that is not integer-rounded, (b) decomposing the pricing residual into pieces that can be dated or measured, and (c) adding a composition term the current mix set lacks? The pitch is due 2 October; the model freezes the week of 21 September after the September Inside Airbnb dumps are folded in.

## Phases and workstreams

| Phase | WS | Task | Model | Depends on |
|---|---|---|---|---|
| 0 | **S** | Scoring harness and v3 pre-registration | Fable | nothing; runs first and alone |
| 1 | **K** | Residual decomposition: is the 1H26 step the fee-migration reprice, and does it lap in 4Q26 | Fable | S committed |
| 1 | **L** | Regional residual: rebuild by region, test regional proxies region by region, aggregate on nights shares | Fable | S committed |
| 1 | **M** | New-listing price premium as a fifth mix term | Fable | S committed |
| 1 | **N** | Two decision memos: the ADR-FX estimator pick, and the 4Q26 lap arithmetic | Sonnet or Opus | nothing |
| 2 | **P** | Card v3 on the S harness with K, L, M, N; SYNTHESIS.md; 5 November score-sheet script | Fable | K, L, M, N |
| trigger | **T** | September dumps: daily CDN probe; when files land, re-run E1-E7, F0b, I1b, then P | any | dumps landing (10-30 Sep) |

Never more than four agents at once. Phase 1 does not start until S has committed `S1_scoring.py` and its note.

## Pre-registered pass criteria (written before any Phase 1 result exists; do not edit after)

**S (harness).** Two scored targets replace the single integer target of J3:
1. *Ex-FX, integer-fair:* the model's ex-FX output is rounded to the nearest whole point before scoring against disclosed ex-FX (itself whole points). Naive = last disclosed ex-FX. Both sides now face the same rounding.
2. *Reported dollar ADR y/y, unrounded:* target = `adr_usd` y/y from `adr_history_components.csv` (two decimals). Model = ex-FX model + FX estimator; naive = last disclosed ex-FX + the same FX estimator for the scored quarter. FX for historical quarters comes from `data/processed/overnight2/B/B_adr_fx_estimator_backtest.csv` (est_from_eur and est_from_regional_baskets, both knowable at quarter end), never from the disclosed FX effect. Score under both estimators and their midpoint; report all three.

Windows: 1Q24-2Q26 (n 10) and 2Q24-2Q26 (n 9). Benchmarks as J3: naive, prior year, AR(1) expanding. Jackknife drop-one range on every ratio. Knowable-before-print flag on every model.

**v3 residual rule, pre-registered here: last-quarter residual (`last_q`).** This is a post-hoc choice: it was the best rule in J3's sensitivity table (0.89, below 1 in all ten jackknife samples) and was not the pre-registered v2 rule. It is promoted here, before the new harness runs, and the note must say so in the first paragraph.

**v3 pass criterion (stricter than v2's "ratio below 1"):** ratio vs naive below 1.0 on both windows AND jackknife maximum below 1.0, on target 2 under both FX estimators. Target 1 is reported alongside; passing target 1 alone is not a pass.

**K.** Pass = a residual model that uses the migrated-cohort share (WS-D dating: single fee and cancellation redesign global from October 2025, NA earlier per the ledger) beats `last_q` on the S harness on both windows, with a fee coefficient whose sign and size are consistent with the fee mechanics (state the expected size before fitting). Otherwise report the null and the dated lap arithmetic for 4Q26 as a scenario, not a forecast.

**L.** Pass = the regional residual aggregate (regional rule or regional proxy, chosen region by region on data strictly before each scored quarter) beats `last_q` on the S harness on both windows. Euro-area HICP accommodation against EMEA (J2: 0.91, the one marginal survivor) is the starting point. n is 10; report jackknife and say if the result rests on one quarter.

**M.** Pass = a new-listing price premium series with at least eight quarters of history exists (listings under a year old vs older, on the 2025 listed-price basis and the 2026 quote basis separately, never mixed), times E's new-listing nights share, and adding it to the mix set lowers the S-harness RMSE on both windows. Otherwise report the null with the series.

**N.** Not a test. Each memo ends in one recommended choice and the delta it makes to 3Q26 and 4Q26 ADR (FX) or 4Q26 nights (lap).

**P.** Card v3 reports the pre-registered v3 result on the S harness first, then any K, L, M term that passed. A term that failed its criterion is a memo line, never in the point.

## What is already established (read first, do not redo)
- `docs/adrq3/SYNTHESIS.md`, `research/notes/adrq3/I_adr-mix-terms-3q26.md`, `research/notes/adrq3/J_adr-pricing-residual-and-card-v2.md`. Card v2: 3Q26 reported +3.0%, $176.5; ex-FX +3.46 = residual 4.61 + geo -1.43 + size +0.80 + LOS +0.06 + new business -0.48 + interaction -0.10. Error attribution in `data/processed/adrq3/J/J3_card_v2_error_attribution.csv`: residual rule late 0.8-1.7 pp in every acceleration quarter (1Q24, 2Q24, 4Q25, 1Q26).
- Residual history 1Q23-2Q26: `data/processed/q3nowcast/H/adr_history_components.csv` (columns residual_pricing_pp, adr_exfx_yoy_pp, fx_effect_pp, adr_usd, geo_mix_pp, unit_size_pp, los_mix_pp, new_business_pp, interaction_pp). The residual stepped from 2-3.5 pp (2023-25) to 4.4 and 4.9 in 1H26. It absorbs like-for-like pricing, sub-regional mix, the fee-migration reprice and measurement error in the other terms.
- Regional ADR history: `data/processed/adr/04_regional_quarterly_wide.csv` (NA, EMEA, LatAm, APAC: ADR, y/y, ex-FX y/y, FX pp, nights share, basis flag per quarter from 1Q21). Letter regional buckets are what 04's shares are built from.
- FX: `data/processed/overnight2/B/` (B_adr_fx_estimator_backtest.csv has disclosed FX and three estimators by quarter from 2Q22; the euro fit backtests at 0.46 pp error, baskets 0.54; the basket build says +1.7 pp more FX help in 4Q26). `research/notes/overnight2/B_fx-relative-strength-geographic-mix.md`.
- Fee and cancellation dating: `data/processed/overnight2/D/rnpl_statement_ledger.csv`, `D1_lap_anniversary.csv`, `D1_exna_4q26_gap.csv`, `D1_rnpl_cohort_scenarios.csv`; `research/notes/overnight2/D_rnpl-statement-ledger-and-cohort-scenarios.md`. Fee migration notes on main under `research/notes/` (grep fee). PR #32 laps the products in NA only; lapping ex-NA at the 40-50% split moves 4Q26 nights from 8.9% to 8.0-8.2%.
- Proxies: `data/processed/adrq3/J/proxy_tests.csv` (164 tests, none beat naive against the blended residual), `J2_proxy_quarterly_panel.csv`, `J2_proxy_monthly.csv`. Raw external prices `data/raw/external_prices/` (main tree, manifest) plus the G cache `data/processed/q3nowcast/G/raw/`.
- Reviews stays index: `data/processed/q3nowcast/E_aug/` (includes Tokyo; `stable_listing_index.csv` and `stable_listing_yoy_market.csv` carry the same-listing variant; all growth in mature markets comes from listings under a year old, E note section 1 point 5). Party-size term: `data/processed/adrq3/I/`. Seats dilution: `data/processed/adr/15_seats_dilution_quarterly.csv`.
- Price data: 13-city listings dumps `C:\Users\krish\citadel-abnb\data\raw\inside_airbnb\` (Dec 2022 to Aug 2026, parquet alongside csv). Through Sep 2025 `price` is the listed nightly rate; Dec 2025 to Feb 2026 no price; from Mar 2026 `price` is a fee-inclusive quote per night, 24-29% higher. The two bases are never comparable y/y. Calendars carry no price after May 2025. The quote index does not track disclosed regional ADR (8 Sep); same-listing calendar prices are unchanged y/y on 72-77% of dates (J1). Do not build another same-listing price panel and do not scrape.
- Scoring protocol: `analysis/src/adrq3/I0_protocol.py` (note-08 expanding walk-forward, permutation p, knowable flag) and the J3 walk-forward block in `analysis/src/adrq3/J3_residual_nowcast_card_v2.py`. J3 stays untouched as the record of v2.
- Raw (main tree, read-only, gitignored): reviews `C:\Users\krish\citadel-abnb\data\raw\inside_airbnb_reviews\`, calendars `data\raw\inside_airbnb_calendar\`, letters `data\raw\letters`, FRED cache `data\processed\overnight\05_fred_cache`.

## Rules
- Label every number sourced / descriptive / assumed / causal. Backtest with the note-08 protocol via S's harness once it exists. A term that does not meet its pre-registered criterion is reported as such.
- The team nights baseline, the H card and card v2 are comparison columns, not inputs. No valuation. Forecast 3Q26 and 4Q26 independently; consensus is a comparison column only.
- Write only inside this worktree: scripts `analysis/src/adrv3/<WS>_*.py`, outputs `data/processed/adrv3/<WS>/`, note `research/notes/adrv3/<WS>_<slug>.md`. Never modify the main tree. New raw downloads go to the main-tree raw dirs with a manifest.
- Python `py -3.13`. Bash calls time out at 10 minutes: checkpoint per file, run long jobs in the background with a log, poll with short calls.
- Note format: date 2026-09-11 (or the day written), author "Krishang Surapaneni (compiled with Claude Code)", sections Bottom line, Tables, Method, What this can and cannot identify, Next evidence, Files. Plain prose, no em-dashes.
- Commit only your own files at the end (`git add <your paths>`; on `index.lock` wait 30 s, retry up to five times). Never push.
