# WS21: Inside Airbnb pair eligibility — fixing partial-snapshot contamination of year-over-year pairs

**Workstream 21, 7 Sep 2026. Audit finding A04 (P2).** Author: Claude Code for Krishang.
**Fixes:** `analysis/src/inside_airbnb_supply_panel.py`. **Adds:** `analysis/src/overnight/21_test_pair_eligibility.py`, `analysis/src/overnight/21_pair_eligibility_delta.py`.
**Regenerated:** `data/processed/inside_airbnb_like_for_like.csv`, `inside_airbnb_city_snapshots.csv`, `inside_airbnb_host_concentration.csv`, `analysis/figures/inside_airbnb_retention_yoy.png`, `inside_airbnb_reviews_ltm_yoy.png`, `inside_airbnb_lfl_price_yoy.png` (plus the five snapshot-level figures, unchanged in content).
**New outputs:** `data/processed/overnight/21_pair_eligibility_delta.csv` (per pair), `21_retention_by_city_delta.csv` (per city).
**Note updated:** `research/notes/2026-09-05_inside-airbnb-supply-panel.md`, new section 7 "Correction 7 Sep 2026".
Full rebuild from the 168 raw parquet dumps, `py -3.13 analysis/src/inside_airbnb_supply_panel.py build` then `figures`, ran in under 3 minutes. Nothing was restricted or short-cut.

---

## 1. Bottom line

`partial_scope` existed on the snapshot table and was applied to the snapshot-level charts, but it was **never joined onto the two endpoints of a pair**. All 103 year-ago pairs went onto the retention and matched-review figures and into `inside_airbnb_like_for_like.csv` with no coverage flag. **25 of the 103 have a partial-scrape endpoint**, and they average **48.9% retention against 72.6% for the 78 clean pairs**. The worst is **Paris 3 Mar 2025 (86,064 listings) vs 21 Mar 2026 (38,075, a partial scrape): 33.15% retention** — it reads as two thirds of Paris leaving Airbnb in a year. Paris was back at 77,679 listings in Jun 2026 and the clean Sep 2025 → Aug 2026 pair retains 77.5%. Nothing left.

That pair is now `pair_eligible=False`, `exclusion_reason=partial_scope_b`, `retention_clean=NaN`, and `pair_eligible_pit=False` as well. Confirmed in `21_pair_eligibility_delta.csv` and asserted in the fixture test.

Panel effect: mean year-ago retention **66.9% → 72.6%**, minimum **33.1% → 48.9%**. Matched-review y/y barely moves (**+7.2% → +6.9%**): a partial scrape drops listings but does not change the surviving listings' review counts, so the review series was far less damaged than retention. Sequential pairs: 101 of 155 eligible (the Dec 2025 – May 2026 monthlies).

## 2. What changed in `inside_airbnb_supply_panel.py`

1. **`add_scope_flags(s)`** — coverage classified twice per dump, both stored:
   - `partial_scope` / `scope_vs_peer` — **retrospective**, listing count vs the largest dump of that city within ±200 days. Unchanged rule, unchanged results (41 of 168 dumps partial, byte-identical to the pre-fix flags). Revisable by a later scrape.
   - `partial_scope_pit` / `scope_vs_peer_pit` — **point-in-time**, same ±200-day half-width but trailing only, so no later scrape can revise it. 32 of 168 partial.
   - `partial_scope_pit_long` / `scope_vs_peer_pit_long` — point-in-time with a 400-day trailing lookback. Needed because a *run* of consecutive partial dumps hides itself from a 200-day window: Nashville has six partial dumps in a row (2025-12-27 through 2026-05-26, 5,997 to 8,101 listings against 9,443 in Sep 2025), so each looks normal beside the others and the short trailing rule clears 2026-04-25 at ratio 0.90 while the 400-day rule catches it at 0.62.
   - `scope_unverified*` — fewer than two dumps in the reference window, so coverage cannot be judged either way.
2. **`add_pair_eligibility(p, s)`** — joins **both** endpoints' flags onto every pair *before* any selection or plotting, and adds `listings_a/_b`, `scope_vs_peer_a/_b`, `partial_scope_a/_b`, the three point-in-time equivalents per side, `pair_eligible` + `exclusion_reason`, `pair_eligible_pit` + `exclusion_reason_pit`, `scope_drift`, `span_min_vs_max_listings` + `span_step_warning`. Reasons are explicit strings: `partial_scope_a`, `partial_scope_b`, `partial_scope_b_long_lookback`, `coverage_unverifiable_b_at_cutoff`, `scope_missing_a/b`.
3. **Same policy on reviews and prices, not just retention.** `retention_clean`, `matched_reviews_ltm_chg_clean` and `lfl_price_chg_median_clean` are null on ineligible pairs; the figures plot the `_clean` columns. `price_pair_eligible` = `pair_eligible` **and** the pre-existing `price_comparable` same-price-basis check (kept exactly as it was — it is what stops the 2026 fee-inclusive quote basis being read as +25% price inflation) **and** ≥500 matched priced entire homes.
4. **Nothing is deleted.** Ineligible pairs keep every raw column and appear on the retention and reviews figures as grey crosses, with the eligible pairs joined by lines. Pairs that are eligible but straddle a listing-count step are ringed.
5. `build()` now computes scope flags first, then joins, then writes; it logs how many year-ago pairs are ineligible on each rule.

## 3. Point-in-time vs retrospective — this is the part that matters for replay

The retrospective flag uses **future** scrapes. Nine dumps in this panel are labelled partial *only* because a later, larger scrape exists: Mexico City 2025-12-29, 2026-01-25, 2026-02-26, 2026-03-30, 2026-04-29; Nashville 2026-04-25 and 2026-05-26; Paris 2023-12-12; Sydney 2026-02-17. On 25 Apr 2026 the Nashville dump (5,997 listings) looked like 90% of everything then visible; only the Jun 2026 rebound to 10,242 revealed it as partial. **A frozen forecast made on 25 Apr 2026 that used `partial_scope` would have been silently rewritten by a scrape that had not happened yet.**

- 25 pairs ineligible retrospectively, 27 point-in-time, 22 in both.
- **Three** pairs the retrospective rule rejects were **not** rejectable at the time: Mexico City 2025-06-25 → 2026-03-30 and → 2026-04-29, Nashville 2025-06-19 → 2026-05-26.
- **Five** pairs the point-in-time rule rejects are retrospectively fine: Austin 2024-12-14→2026-01-18, 2025-03-06→2026-02-19, 2025-06-13→2026-06-22, 2025-06-13→2026-07-18, and Barcelona 2025-09-14→2026-06-24. The 400-day lookback fires on Austin's permanent scope reduction and Barcelona's contraction. That is the conservative answer for a frozen call, not evidence the market shrank.

**Rule for WS08 and anything else replaying a decision as of a past date: use `pair_eligible_pit`, and store the flag alongside the prediction.** `pair_eligible` is quality control for the write-up, not point-in-time information.

## 4. What the fix cannot do

An Inside Airbnb scope reduction and a genuine market contraction are **not separable from listing counts alone**. I checked whether partial dumps are geographic truncations — they are not: all 20 Paris arrondissements appear in the 38,075-listing dump, so neighbourhood coverage does not discriminate; the partial scrapes are uniform subsamples. So `span_step_warning` marks the ambiguous pairs rather than deciding: **Austin 2024-12-14→2026-01-18, 2025-03-06→2026-02-19, 2025-06-13→2026-06-22, 2025-06-13→2026-07-18** (Austin stepped from 15,187 listings in Jun 2025 to ~11,000 from Sep 2025 and stayed there) and **Barcelona 2025-09-14→2026-06-24**. Austin's 49–53% "retention" on those pairs is the step, not churn. Barcelona's contraction is regulatory and is discussed in the supply-panel note.

**Austin has no usable year-ago retention or review y/y at all** and should be dropped from every churn and demand cut until two post-Sep-2025 Septembers exist (Sep 2026).

## 5. Before / after retention by city (year-ago pairs)

Retention arithmetic is unchanged; what changed is which pairs may carry a market interpretation. "All pairs" is what the pre-fix charts and CSV showed.

| City | Pairs | Now excluded | Mean retention, all | Mean, eligible | Δ pts | Min, all | Min, eligible | Matched reviews y/y, all | eligible |
|---|---|---|---|---|---|---|---|---|---|
| Austin | 11 | 6 | 51.0% | 55.6% | +4.6 | 36.8% | 48.9% | +0.2% | −0.7% |
| Barcelona | 3 | 0 | 63.0% | 63.0% | 0.0 | 62.7% | 62.7% | +10.5% | +10.5% |
| Chicago | 9 | 2 | 66.6% | 74.2% | +7.6 | 39.6% | 64.9% | +11.1% | +12.1% |
| London | 3 | 0 | 71.0% | 71.0% | 0.0 | 69.6% | 69.6% | +9.7% | +9.7% |
| Los Angeles | 9 | 0 | 70.0% | 70.0% | 0.0 | 64.9% | 64.9% | +6.1% | +6.1% |
| Mexico City | 6 | 2 | 70.5% | 73.7% | +3.2 | 64.0% | 67.7% | +10.6% | +10.6% |
| Nashville | 11 | 6 | 61.2% | 75.2% | +14.0 | 44.1% | 72.2% | +6.7% | +5.1% |
| New Orleans | 6 | 1 | 67.9% | 73.3% | +5.3 | 41.2% | 68.9% | +7.2% | +6.1% |
| New York | 2 | 0 | 69.9% | 69.9% | 0.0 | 69.5% | 69.5% | +4.2% | +4.2% |
| Paris | 13 | 6 | 59.8% | 73.2% | +13.4 | 33.1% | 69.3% | +9.9% | +6.5% |
| Rome | 17 | 2 | 77.3% | 79.1% | +1.8 | 63.4% | 72.8% | +7.6% | +7.5% |
| San Diego | 10 | 0 | 73.2% | 73.2% | 0.0 | 65.9% | 65.9% | +6.2% | +6.2% |
| Sydney | 3 | 0 | 75.3% | 75.3% | 0.0 | 74.1% | 74.1% | +5.4% | +5.4% |
| **Panel** | **103** | **25** | **66.9%** | **72.6%** | **+5.8** | **33.1%** | **48.9%** | **+7.2%** | **+6.9%** |

Six cities are unaffected (Barcelona, London, LA, NYC, San Diego, Sydney): their pairs were already clean. Paris and Nashville were the worst hit.

**Latest comparable year-ago pair per city** (the number the pitch should quote): Rome 82.3%, Chicago 77.6%, New Orleans 78.0%, Paris 77.5%, San Diego 76.9%, Nashville 76.4%, Mexico City 76.4%, Sydney 74.1%, London 69.6%, NYC 69.5%, LA 67.0%, Barcelona 62.7%. Austin: none.

## 6. Fixture test

`analysis/src/overnight/21_test_pair_eligibility.py`, 17 checks, all passing, exit 0. Run: `py -3.13 analysis/src/overnight/21_test_pair_eligibility.py`. It calls the real `pair_row`, `add_scope_flags`, `scope_as_of` and `add_pair_eligibility` on synthetic dumps. The claims it pins:

- A partial dump holding a strict subset of the same 86,000-listing city produces **44.2% raw retention** and must be flagged on both rules, given a reason, and nulled out of the clean series. Minimum clean retention 96.5% vs 44.2% raw — **no apparent market exit survives**.
- The raw pair row is preserved (`ids_b` still 38,000, `retention` still populated).
- A **genuine** 50% exit at unchanged scope stays eligible and still reads 50.0% — the filter does not launder real bad news.
- The point-in-time flag is identical whether or not later dumps exist.
- A run of consecutive partial dumps escapes the short trailing window (documenting why the long one exists) and is caught by the 400-day one.

## 7. Downstream: who consumed the contaminated pairs, and what they should now carry

I did not edit any other workstream's files. This is what each owner must change.

### WS08 — `analysis/src/overnight/08_altdata_backtests.py`, `08_inside_airbnb_demand.py`

`08_altdata_backtests.py:196` already filters the review/blocked/listings features on `~partial_scope` from `08_ia_city_yoy.csv`, so **the review-side features and the "0 of 36 flagged, n = 0 usable fixed-13-city quarters" conclusion are unaffected.** Two changes are required:

1. **`ia_lfl_price_yoy` (line 221-224) is filtered on `price_comparable` only, not on scope.** It should read `l = l[l.price_pair_eligible]`. Effect on the quarterly feature: **2025Q3 goes from −5.71% (3 cities) to −8.35% (2 cities)** — the Austin 2024-09-13 → 2025-09-16 pair (−4.8%) is dropped because the Sep 2025 Austin dump is a partial scrape (`scope_vs_peer` 0.68). **2024Q4 stays 0.00% but on 1 city, not 2** (Paris 2023-12-12 → 2024-12-06 drops; the Dec 2023 Paris dump is 74,329 listings vs 95,885 in Jun 2024, `scope_vs_peer` 0.78). 2023Q4 +9.09%, 2024Q1 +12.31%, 2024Q2 +4.70%, 2024Q3 +1.95%, 2025Q1 −5.90%, 2025Q2 −4.32% are unchanged. Since this feature already fails every test (r +0.13 with ADR y/y, n = 8) the conclusion does not move, but the reported series and the n-per-quarter must be corrected, and the n = 8 becomes **n = 8 with 1-4 cities per quarter, 2 of the 8 quarters resting on one city**.
2. **The scope filter is retrospective, so it is not point-in-time.** Both `08_ia_city_yoy.csv`'s `partial_scope` column and the pair table's `pair_eligible` use future scrapes. For any walk-forward or frozen-replay test, switch to `pair_eligible_pit` / `partial_scope_pit`. Concretely, three year-ago pairs (Mexico City ending 2026-03-30 and 2026-04-29, Nashville ending 2026-05-26) are currently dropped from the backtest using information that did not exist at the dump date, and five others (four Austin, one Barcelona) should be dropped and are not; nine of the 168 dumps carry a retrospective-only partial label. This is the same class of defect as A01 and must be recorded in the feature registry with the availability date of the coverage decision.

### WS11 — `analysis/src/overnight/11_competition_supply_overlays.py`, note `11_competition-supply-and-overlays.md`

WS11 **already** joins the snapshot scope flag onto both endpoints (lines 234-247) and drops partial pairs, so `data/processed/overnight/11_supply_economics.csv` is **arithmetically correct as it stands** and its year-ago retention rows match `pair_eligible` exactly. Two changes:

1. Replace the hand-rolled join with the published `pair_eligible` column so the policy lives in one place (`lfl = lfl[lfl.pair_eligible]`), and cite `exclusion_reason` in the source string.
2. **The note's headline needs the span-step caveat.** `11_competition-supply-and-overlays.md` line 161 says "On the seven cities with a clean read in both years, mean retention fell **75.4% → 71.1%**, with the new-listing share steady at 25.4% → 25.8%." That 7-city figure is dominated by Austin, whose 2026 rows (0.509 mean over 4 pairs, in `11_supply_economics.csv`) straddle its permanent scope step rather than measuring churn. **Excluding Austin, the six-city figure is 75.5% → 73.4% (−2.1 pts, n = 14 pairs in 2025 and 34 in 2026), and the new-listing share is 25.4% → 25.4%, flat.** The "retention is falling" claim survives but is half the size, and the new-listing share is exactly flat rather than drifting up. The Austin row `inside_airbnb_year_ago_retention_austin` 2026 = 0.509 should be relabelled a scope artefact or removed.

### WS06 — `analysis/src/overnight/06_wtp_hedonics.py`, `06_quote_panel.py`, note `06_consumer-choice-and-willingness-to-pay.md`

WS06 reads the raw parquet dumps directly and pools them with **city × dump fixed effects**, demeaning log price inside each city-dump. A partial dump is a uniform subsample of the same city (checked: all 20 Paris arrondissements present in the 38k dump), so the hedonic premia are **not biased** by A04 and no premium needs restating. One change:

- `06_price_per_unit_panel.csv` and `06_quote_discount_panel.csv` are **per-city-dump level series**. Rows built on partial dumps describe a subsample, not the city, and should carry `partial_scope` / `scope_vs_peer` joined from `inside_airbnb_city_snapshots.csv`. Any cut that compares a 2026 monthly to an earlier dump as a level (quote discount over time, price per unit over time) needs the pair-eligibility rule, not just the price-basis rule. The WTP premia themselves stand.

### WS14 — `research/notes/overnight/14_master-synthesis.md`

Line 977 already records the defect and quotes the right numbers ("25 of 103 pairs, averaging 0.489 against 0.726 for the clean pairs"). It should now say the fix is **applied**, not pending, and point at `pair_eligible` / `21_pair_eligibility_delta.csv`. Line 67's "Inside Airbnb like-for-like price (r +0.13 with ADR, n 8)" keeps its verdict but the underlying series changed in 2025Q3 (see WS08 above) and the n = 8 rests on 1-4 cities per quarter.

### Other consumers

- `analysis/src/predictive/03_nowcast_tests.py:312` reads a **copy** of the old pair table at `data/external/inside_airbnb_like_for_like.csv`. That copy is now stale and has no eligibility columns; refresh it from `data/processed/` before the file is used again.
- `analysis/src/overnight/01_data_census.py` rows D122-D124 describe the pair table; the column list should mention `pair_eligible` / `exclusion_reason` and the two coverage vintages.
- `data/README.md` line 46 describes `partial_scope` only; add the pair-level flags.
- `research/regulatory/` uses snapshot-level exposed nights from full-scope dumps and is unaffected.

## 8. For the model

| Parameter | Value | Unit | Source |
|---|---|---|---|
| Year-ago listing retention, panel mean, comparable pairs | 0.726 | share | `inside_airbnb_like_for_like.csv`, `pair_eligible=True`, 78 pairs |
| Year-ago listing retention, latest comparable pair, 12 cities | 0.627 – 0.823 | share | same, latest eligible pair per city |
| Six-city retention 2025 → 2026 (ex-Austin) | 0.755 → 0.734 | share | `21_pair_eligibility_delta.csv` |
| New-listing share of ending base, six cities, 2025 and 2026 | 0.254 → 0.254 | share | same |
| Matched-listing reviews LTM y/y, panel mean, comparable pairs | +6.9% | % | same, `matched_reviews_ltm_chg_clean` |
| Quoted like-for-like nightly price y/y, 2025 pairs | −0.9% to −11.0% | % | `price_pair_eligible=True`, 13 pairs, 4 cities |

## 9. For the 5 Nov card

Nothing here forecasts the Q3 print. Two negatives worth carrying: the supply-exit story that the contaminated pairs implied (Paris 33%, Nashville 44%, Chicago 40%) **is not real** and must not appear on a slide; and Austin, which several cuts treat as a US demand read, has no comparable year-ago pair until the Sep 2026 dump lands. When Sep and Oct 2026 dumps are pulled before the print, re-run `build` and check `pair_eligible` before quoting any new retention number — Inside Airbnb's monthly scrapes have been partial more often than not since Dec 2025 (41 of 168 dumps overall, and most of the Dec 2025 – May 2026 monthlies).
