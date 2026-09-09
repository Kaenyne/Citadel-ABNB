# ADR: history, reconstruction, and what actually drives it

Krish with Claude Code, 7 Sep 2026. Branch `krish/adr-decomposition`.
Scripts `analysis/src/adr/01`-`08`; outputs `data/processed/adr/`.

---

## 0. Bottom line

1. **Reported ADR growth is three things, and only one of them is measurable with confidence.**
   FX is mechanical and now reconstructed back to 1Q20 with validated error. Geographic mix is
   measurable from the 10-K and is a persistent, *accelerating* drag. Unit size and
   like-for-like price are, on public data, close to unidentified — and the decomposition
   now says so explicitly instead of hiding it in a residual.
2. **The decomposition reconciles, after an audit corrected two method errors.** The first
   version carried an "unexplained" line of 19-131% of the ADR move. That was mostly
   artefact: FX had been re-derived from regional baskets instead of taken from the letters
   (wrong by 1.33pp in 2022), and a hotel price benchmark with r~0 against ABNB ADR ex-FX had
   been subtracted as a component (it absorbed 6.73pp in 2022 purely because hotel prices
   were inflating post-COVID). Corrected, the within-region term reconciles to the
   independently built 10-K regional panel within **0.03, 0.30 and -0.13pp** in 2023-2025.
   Audit: `analysis/src/adr/10_audit_decomposition.py`, `10_audit.csv`.
3. **The consensus reading of the bedroom-nights disclosure -- including our own WS06 --
   maps a +2pp bedroom-night wedge onto +2pp of ADR. That mapping is wrong.** ADR responds to
   bedroom count with a local elasticity of **0.23**, stable across both panels (0.2289 on 12
   urban markets, 0.2312 on 29): the average booked listing has 1.65 bedrooms, so one more is
   +61% of bedroom count but only **+15.05%** of price on Airbnb's own quote data. Our direct
   measurement of both size channels on 29 markets gives **+0.63pp of ADR**. Against ex-FX ADR
   growth of +4%, unit-size mix is roughly **a sixth of the move, not a half**.
   **Do not scale by the ADR-per-wedge ratio** -- it is 0.629 on the 12-market panel and 0.913
   on the 29-market one, because capacity and bedroom growth are not proportional across
   samples. Use the structural elasticity or the direct measurement, never the sample ratio.
4. **The size-mix story is a North America and Europe phenomenon, and Airbnb's growth is not.**
   Now on 29 markets (was 12): NA +1.97pp, EMEA +1.56pp, **APAC +0.08pp (15 markets, was
   Sydney alone), LatAm −0.89pp (4 markets, was Mexico City alone)**. Nights growth is
   concentrated in LatAm and APAC, where the size wedge is nil or negative. Geographic mix and
   size mix pull against each other, which is why blended ADR moves so little. Enlarging the
   panel **cut the global wedge roughly in half** (+1.41pp → +0.69pp; ADR +0.89 → +0.63pp), so
   the panel now supports *less* of the disclosed ≥+2pp, not more.
5. **The obvious explanation for that gap has been tested and rejected.** The natural defence of
   the disclosure is that our dense-urban panel misses non-urban family stock where the size
   shift happens. It does not: non-urban markets show a **smaller** wedge (+0.30pp on 9 markets,
   capacity actually **−0.14% y/y**) than urban (+0.87pp on 20). The urban panel was biased
   **up**, not down.
6. **Geographic mix has been negative every year since 2021 and is getting worse**: −0.5,
   −2.8, −1.1, −1.2, **−1.6pp**. Every region's ADR grew faster than the blend. Anyone reading
   blended ADR ex-FX as a pricing signal is under-reading like-for-like pricing in all four regions.
7. **Two errors in existing merged work were found and are corrected here** (section 5).

---

## 1. What is now in hand

| Series | Was | Now | Where |
|---|---|---|---|
| ADR level, quarterly | 3Q20 | **1Q19** | `02b_adr_history_extended.csv` |
| ADR y/y, quarterly | 3Q21 | **1Q20** | same |
| ADR ex-FX, quarterly | 2Q22 (disclosed) | **1Q20** (9 reconstructed + 17 disclosed) | same |
| Regional ADR levels, annual | none | **2020-2025**, from 10-K | `01_regional_annual.csv` |
| Regional ADR, quarterly | none | **1Q21-2Q26**, basis-flagged | `04_regional_quarterly.csv` |
| Unit-size mix | one disclosed point | **298-dump panel, 29 paired markets** | `05_`, `08_size_mix_*` |
| Like-for-like price | residual plug | **externally measured + error line** | `06_measured_price_quarterly.csv` |

---

## 2. The FX reconstruction

The letters give ex-FX ADR only from 2Q22. A GBV-weighted regional currency basket with WS10's
regional pass-throughs reproduces the disclosed FX effect on the 17 known quarters at
**r 0.988, raw (unfitted) RMSE 0.68pp, calibration slope 1.10**, against 3.29pp for assuming
zero; leave-one-out 0.56pp. Slope near one means the construction is right in *level*, not
merely correlated — the calibration only improves RMSE to 0.50pp, so the result does not lean
on the fit.

| | 1Q20 | 2Q20 | 3Q20 | 4Q20 | 1Q21 | 2Q21 | 3Q21 | 4Q21 | 1Q22 |
|---|---|---|---|---|---|---|---|---|---|
| ADR reported y/y | −3.2 | −2.5 | +15.6 | +13.3 | +34.9 | +41.4 | +14.8 | +20.4 | +5.2 |
| FX contribution | −2.2 | −2.9 | +0.3 | +1.2 | +3.0 | +4.9 | +1.2 | −1.4 | −2.7 |
| **ADR ex-FX** | **−1.0** | **+0.3** | **+15.3** | **+12.0** | **+31.9** | **+36.5** | **+13.6** | **+21.8** | **+7.9** |

Independent check: the reconstructed 1Q22 (+7.9%) runs continuously into the disclosed 2Q22
(+7.0%). Nothing was fitted to make that happen.

**1Q20-2Q21 carry `usable_for_calibration = False`.** 2Q20 nights fell 67% and 2Q21 rose 197%;
an ex-FX ADR there is arithmetically fine and economically meaningless, because the move is a
collapse and rebound in geographic, urban/rural and stay-length mix, not pricing. Do not fit
anything on those quarters.

---

## 3. The decomposition

`07_full_decomposition.csv`. Terms sum to the ADR move by construction *except* the
unexplained line, which is the point.

| pp of ADR y/y | 2022 | 2023 | 2024 | 2025 |
|---|---|---|---|---|
| **ADR y/y** | **+2.68** | **+2.15** | **+1.64** | **+3.02** |
| Geographic mix (4-region) | −2.75 | −1.08 | −1.24 | **−1.58** |
| FX (disclosed, GBV-weighted) | −5.17 | +0.18 | −0.45 | +1.30 |
| Interaction | −0.39 | −0.05 | −0.11 | −0.11 |
| **= Within-region ADR ex-FX** | **+10.99** | **+3.10** | **+3.44** | **+3.41** |
| — of which length of stay | +0.26 | +0.62 | +0.21 | +0.04 |
| — of which unit-size mix | n/a | n/a | +0.44 | −0.25 |
| — of which **pricing + sub-regional mix** | +10.73 | +2.48 | +2.80 | **+3.62** |

**Reconciliation, the check the first version lacked.** The within-region term is compared
against the nights-weighted regional ADR ex-FX built independently from the 10-K in `03`:

| | 2022 | 2023 | 2024 | 2025 |
|---|---|---|---|---|
| within-region (identity) | +10.99 | +3.10 | +3.44 | +3.41 |
| independent regional build | +9.76 | +3.07 | +3.15 | +3.54 |
| **gap** | +1.23 | **+0.03** | **+0.30** | **−0.13** |

2023-2025 agree to within a third of a point from two constructions that share no
intermediate step. 2022 is flagged low — the FX reconstruction is weakest in the high-
dispersion COVID window.

**The last line is jointly unidentified, not unexplained.** Airbnb discloses no
country-level ADR, so within-region pricing cannot be separated from sub-regional (country)
mix. That term is not noise: expansion-market origin nights have grown ~2x core for ten
consecutive quarters and those markets are lower-ADR, so it carries a real negative mix
component that a four-region decomposition cannot see.

**The hotel price benchmark is a comparator, never a component.** Subtracting a series with
r~0 against the target injects variance rather than explaining it. It is retained in the CSV
as `hotel_price_comparator_pp` for context only.

---

## 4. The terms

### 4.1 Geographic mix — the solid one

From the 10-K "Geographic Mix" tables, 2020-2025, which give regional nights, GBV and revenue,
and *name* regional ADR outright through FY2022. Computed ADR matches company-stated ADR to
within 0.25% for 2020-21; the drift to 1.7% from 2022 is fully explained by the switch to
whole-million nights rounding (`01_adr_disclosure_check.csv`).

| Regional ADR | 2020 | 2021 | 2022 | 2023 | 2024 | 2025 |
|---|---|---|---|---|---|---|
| NA | $174 | $222 | $240 | $239 | $246 | $255 |
| EMEA | $98 | $124 | $128 | $140 | $148 | $159 |
| LatAm | $76 | $95 | $93 | $95 | $93 | $95 |
| APAC | $86 | $110 | $117 | $118 | $117 | $118 |
| **Global** | **$124** | **$156** | **$160** | **$164** | **$166** | **$171** |

NA nights share fell 39.1% → 29.6% while LatAm + APAC went 25.9% → 30.0%. Every region's ADR
rose more than the blend. That wedge is the mix drag, and it is compounding.

### 4.2 Unit-size mix — corroborated, and smaller than management implies

Built from 196 Inside Airbnb dumps: the repo's 13 cities for time depth plus 28 OneDrive
markets across 14 countries for breadth. Listings are weighted by `estimated_occupancy_l365d`
(**estimated nights booked in the last 365 days, a count — not an occupancy percentage**), which
converts a supply-side size distribution into an approximation of a booked one.

2Q26 disclosure window, 39 pairs across 12 markets, ~81m estimated nights:

| Measure | Result |
|---|---|
| Size wedge (bedroom-nights growth less nights growth) | **+1.41pp** vs Airbnb's disclosed ≥+2pp |
| capacity per booked night | +1.63pp |
| whole-home complete cases, zero imputation | +1.24pp |
| **ADR contribution** | **+0.89pp** (+0.32 bedrooms, +0.56 capacity) |
| 3Q26 (22 pairs) | +1.46pp — the wedge persists past the reported quarter |

Three independent size measures agree. The panel is dense-urban, and Airbnb's size growth is
concentrated in non-urban family stock the panel does not cover, so a somewhat smaller wedge in
cities is the expected direction of bias. **Call the disclosure corroborated.**

**But the conversion to ADR is where management's framing breaks.** Priced through the same
hedonics, Airbnb's own +2pp wedge is worth ~+1.26pp of ADR. Against +4% ex-FX ADR growth,
unit-size mix is ~a fifth to a quarter of the move — not "about half".

**Within vs between:** +1.33pp of the +1.47pp total comes from listings present in both dumps —
about 91% is booking volume reallocating onto bigger *existing* homes. That is demand behaviour,
which is management's stated mechanism, not the listing base drifting bigger.

**Regional — extended to 29 markets (section 4.2a).** The one-city-per-growth-region caveat
is gone.

**The artifact that nearly wrecked it, and is a warning for any future Inside Airbnb work:**
the `bedrooms` field's population is not stable and shifts twice inside the test window, almost
entirely on private rooms (London 99.9% populated Jan 2026 → 15% Aug 2026). The hedonic's native
`bedrooms_f` falls back to `round(accommodates/2)` on missing values, so it reads the metadata
change as a size trend and returns **+1.44pp of ADR contribution against +0.89pp** on a
coverage-robust measure. Rejected and recorded. The gate (drop dumps below 80% whole-home
coverage, drop pairs with >10pp coverage drift) excluded Barcelona, which had been producing a
spurious −6.9pp wedge.

### 4.2a Extending the panel into LatAm and APAC

`08_size_mix_latam_apac.py` (imports 05's functions directly, so the two builds cannot
diverge), `08_size_mix_extended_*.csv`, `08_acquisition_log.csv`.

2,553 ranged-GET probes against the Inside Airbnb CDN found 130 live dumps and 1,697 gone;
118 downloaded, 12 taken from the OneDrive pull. **17 of 21 new markets paired.** Retention is
patchy rather than a clean cutoff, and the get-the-data page *lags* the CDN — every target
market has July and August 2026 dumps the page does not list, found by daily date probing, and
those rescued Melbourne.

Not obtainable: **são-paulo, bogotá** (Inside Airbnb only added them in 2026; no 2025 dump
exists), **hong-kong** (whole-home `bedrooms` coverage 78.7-78.8%, below the 80% floor),
**buenos-aires** (coverage drift 99.9% → 85.7%, over the 10pp limit).

| 2Q26 window | 05 baseline | extended |
|---|---|---|
| NA | +1.97pp wedge / +1.36pp ADR, 7 cities | unchanged |
| EMEA | +1.56pp / +0.90pp, 3 cities | unchanged |
| **APAC** | +0.29pp / +0.40pp, **Sydney alone** | **+0.08pp / +0.32pp, 15 markets, 41 pairs** |
| **LatAm** | −0.06pp / +0.25pp, **Mexico City alone** | **−0.89pp / +0.23pp, 4 markets, 13 pairs** |
| **Panel** | +1.41pp / +0.89pp, 12 markets | **+0.69pp / +0.63pp, 29 markets, 87 pairs** |

**The finding holds and strengthens.** Size mix is a NA/EMEA phenomenon; in the regions
carrying 52% of Airbnb's nights growth the wedge is nil (APAC) or negative (LatAm). And the
enlarged panel *halves* the global wedge, so Inside Airbnb now supports **less** of the
disclosed ≥+2pp than the urban-only panel did.

**Urban vs non-urban: the suspicion is refuted with the sign reversed.**

| | markets | wedge | capacity y/y | ADR |
|---|---|---|---|---|
| urban | 20 | +0.87pp | +1.43% | +0.73pp |
| non-urban | 9 | +0.30pp | **−0.14%** | +0.08pp |

The natural defence of the disclosure — that a dense-urban panel misses non-urban family stock —
is wrong. Eight Australian regional/coastal markets give +0.21pp against APAC urban +0.75pp,
with capacity per booked night actually falling. **The urban panel was biased up, not down.**

Robustness: market-unweighted LatAm +0.19pp / APAC +0.29pp; capacity-only with the bedrooms
gate relaxed (so Hong Kong and Buenos Aires re-enter) gives the same ranking — NA +0.83pp,
EMEA +0.68pp, APAC +0.56pp, LatAm +0.22pp. Scope flags move nothing (APAC +0.08 → −0.05pp
ignoring them), and no 2Q26 pair is scope-unverified. The recomputed `partial_scope` flag
reproduces WS21's on 168/168 repo dumps.

**The `bedrooms` metadata artefact fires harder outside the West.** Private-room population
falls from 0.86-0.99 (2025) to 0.22-0.51 (2026) in *every* new market (Tokyo 0.956 → 0.452,
Buenos Aires 0.994 → 0.277, Singapore 0.885 → 0.432). The rejected `bedrooms_f` variant would
have printed APAC +0.67pp and LatAm +0.72pp instead of +0.32 / +0.23 — two to three times too
high. Pinning private rooms at one bedroom is what neutralises it.

One outlier to know: **Singapore −5.84pp** on nights −18% (3,659 → 3,097 listings), scope ratio
0.98 — a real contraction consistent with Singapore's STR rules, not a scrape artefact. The
APAC median market wedge is +0.43pp, so it does not drive the regional conclusion.

### 4.3 Like-for-like price — measured, and the measurement fails

Definition: constant-currency change in the nightly price of a fixed bundle. Two legs — a US
matched-item leg (CPI lodging + BEA hotels price) and a worldwide same-store constant-currency
leg (MAR + HLT comparable RevPAR) — **weighted by GBV share, not nights share**, because a
region's price change reaches group ADR through GBV share (NA is 30% of nights but 44% of GBV).

The informativeness test is the result:

| vs ABNB ADR ex-FX | full sample (n=20) | 2023Q1+ (n=14) |
|---|---|---|
| CPI lodging | +0.755 *** | +0.05 (p=1.00) |
| BEA hotels price | +0.749 *** | +0.01 (p=1.00) |
| MAR + HLT RevPAR | +0.87 | +0.13 (p=1.00) |

**No external benchmark tracks Airbnb's own pricing post-reopening.** The full-sample
correlations are 2021-22 reopening co-movement — the same trap the predictive study found for
nights. CPI and BEA correlate at r = +0.999, so they are one vote, not two.

MAR+HLT worldwide comparable constant-currency RevPAR is the best-matched benchmark *on
construction* (only series matching ABNB on both geography and currency, and it prints 1-8 days
before ABNB), but it has no demonstrated power. **AirDNA US STR ADR is the one worth
backfilling** — the only same-asset-class series — but only four months exist.

Rejected: Inside Airbnb like-for-like prices (r +0.32, p 0.60, n=5; one city in 4Q25; basis
break; discontinued after Sep 2025); Airbnb's own 1BR-vs-hotel comparison (3 points,
discontinued, no methodology); quote discount penetration (no year-ago comparison, and the rise
is contaminated by a taxes-line schema change, 0.2% → 6.5%).

### 4.4 Length of stay — bounded, not fitted

A LOS elasticity fitted on the regional panel is **NOT IDENTIFIED**: t = 1.82, and the sign
flips from +0.64 to −0.40 depending on whether APAC is dropped (APAC's ALOS jumping 2.7 → 3.2 in
2022 carries the whole fit). Recorded in `03_los_elasticity.csv` and rejected. An externally
bounded value from Airbnb's host discount structure (−0.15, band −0.25 to −0.05) is used
instead. The term is small in every year (+0.04 to +0.62pp), so this choice does not drive
anything — but nobody should quote a LOS number as measured.

---

## 5. Corrections to existing work

1. **WS10's regional ADR index has LatAm and APAC swapped.** It uses LatAm 0.68 / APAC 0.59;
   the 10-K gives 0.554 / 0.690 (2025) and 0.561 / 0.703 (2024). LatAm's ADR is *below* APAC's.
   WS10's estimated quarterly nights shares were calibrated on that index and inherit it:

   | 2025 nights share | WS10 estimate | 10-K disclosed | error |
   |---|---|---|---|
   | LatAm | 13.6% | **16.9%** | −3.3pp (−20% relative) |
   | APAC | 15.8% | **13.1%** | +2.7pp (+21% relative) |
   | NA | 31.1% | 29.6% | +1.5pp |
   | EMEA | 39.5% | 40.3% | −0.8pp |

   These shares are **disclosed annually in the 10-K and did not need estimating.** The error
   propagates to the regional nights build, the FY27 bridge (WS29) and the driver model, and it
   understates the weight of the fastest-growing region by a fifth. Shares are rebuilt here by
   RAS against 10-K annual nights and disclosed quarterly totals, touching no ADR.

2. **The KPI panel's regional ADR disclosure map is incomplete.** From the 23 raw letters: EMEA
   reported ADR y/y starts **1Q23** (not 2Q23); LatAm and APAC start **4Q24** (not 1Q25). Also,
   the 4Q23-3Q24 NA/EMEA constant-currency figures are stated "excluding FX **and mix shift**" —
   they are *not* ex-FX and must not be used as such. Carried as a separate metric.

3. **The October 2025 CPI gap is live in `06_price_gap_series.csv`.** It averages the monthly
   *index*, printing 4Q25 CPI lodging at −1.59%; rebuilt as a mean of month-matched y/y over
   available months it is **−2.54%**. This affects the hotel price monitor, not just this build.

4. WS10's FX pass-throughs **survive** an independent test on the 21 quarters giving both
   reported and ex-FX regional ADR: EMEA 1.07 (assumed 1.04), LatAm 0.63 (0.62), APAC 0.82
   (0.86). NA remains not identified and is carried at 1.0, which moves nothing.

---

## 6. For the model and the 5 Nov card

| Parameter | Value | Confidence |
|---|---|---|
| Geographic mix drag, FY27 | −1.5 to −1.8pp, worsening with LatAm/APAC share | **High** — 10-K disclosed |
| Unit-size mix contribution to ADR | **+0.63pp** measured (2Q26, 29 markets) | Medium |
| Size mix in LatAm/APAC | ~0 to negative | **Medium** — 19 markets |
| Like-for-like price | **not measurable** from external data post-2023 | — |
| LOS contribution | −0.1 to +0.2pp | Low, bounded not fitted |
| FX contribution | mechanical, `0.52 − 0.72 × broad USD y/y` | **High** |

**What to watch on 5 November.** Does Airbnb repeat the Bedroom Nights Booked disclosure? It is
the single input that makes the size half of ADR checkable, it has exactly one data point, and
the company has form for dropping metrics that stop flattering the story — it discontinued the
1BR-vs-hotel comparison after 4Q23 and the long-term-stay share after 1Q24. If bedroom-night
growth converges toward nights growth, the durable half of the ADR story is gone. If the metric
disappears, treat that the way we treat the other two.

---

## 7. What to build next

1. **Monthly Inside Airbnb capture, starting now.** The CDN keeps about a year, so every missed
   month is unrecoverable, and the size panel only has a credible annual series for 2026 (51
   pairs, 12 cities) against 2025 (11 pairs, 4 cities) and 2024 (3 pairs, 1 city).
2. **Pair são-paulo and bogotá from 2027.** Inside Airbnb only added them in 2026, so the first
   y/y becomes possible next year; Hong Kong and Buenos Aires need a `bedrooms`-independent
   measure (capacity-only already works for them).
3. **Backfill AirDNA US STR ADR.** The only same-asset-class price benchmark; four months exist.
4. **Model the single-fee repricing artifact.** Migration completed 15 Sep / 13 Oct 2026, inside
   the quarters being forecast; if hosts reprice to hold payout, listed prices rise ~14.8% for
   the migrating cohort and flow into ADR. Not represented in the model.

## Files

| File | Contents |
|---|---|
| `01_regional_annual.csv` | Regional nights/GBV/revenue/ADR/ALOS, 2020-2025, from 10-K |
| `02_fx_backcast.csv`, `02b_adr_history_extended.csv` | FX reconstruction and the 1Q19+ ADR history |
| `03_annual_decomposition.csv`, `03_los_elasticity.csv` | Annual decomposition; the rejected LOS fit |
| `04_regional_quarterly.csv`, `04_reconciliation.csv` | Quarterly regional panel, basis-flagged, and its reconciliation |
| `05_size_mix_panel.csv`, `05_size_mix_summary.csv`, `05_size_evidence.csv` | Size-mix panel, 196 dumps, 41 markets |
| `06_measured_price_quarterly.csv`, `06_price_benchmark_informativeness.csv` | Measured price and the benchmark tests |
| `07_full_decomposition.csv` | The assembled decomposition with the unexplained line |
