# ADR line v2 — mitigation B: does utilisation price? A market-level panel test of the core

Date 2026-09-22. Author: build agent, branch `theo/pitch-model-v2`.
Reproduce: `cd ~/Citadel-ABNB && PYTHONPATH=analysis/src python3 -W ignore -m pitch_model_v2.adr_engine.market_panel`

**Why this note exists.** `adr_v2_thesis.md` names the ADR line's weakest term first: *"the core like-for-like price
(3.85pp, 1.45pp above its 2023–25 mean) is carried, not explained; the supply-utilisation test failed its line."*
`adr_v1b_utilisation_prereg.md` ran the lodging analyst's mechanism — occupancy leads rate — on 13 quarterly points
and got a strong in-sample North American reading (β 0.32 per point of utilisation y/y, r 0.77 lagged, p 0.002)
that failed its walk-forward line (RMSE ratio 1.01 / 0.87). Thirteen quarters cannot settle a mechanism. The same
raw store that produced the quarterly series also has, for ~100 markets, two listing dumps about nine months apart —
which turns the one time series into a **cross-section of ~100 market growth pairs**. This note registers, builds
and scores that panel.

**Standing constraint (DEC-0016): no input is chosen to reach a number.** The registration in §1–§3 was written and
saved before any y, any x, or any regression was computed. The only thing inspected beforehand was the *inventory of
dump dates* (file listing; no listing contents read), because the pair window cannot be registered without knowing
whether pairs exist — and, as §2 records, they do not exist at the span the task assumed. That inventory is
reproduced in §2 so the amendment can be audited.

---

## 1. Registration — object, unit, variables

**Unit of observation.** market × dump-pair: one row per (market, dump A, dump B) with dump A earlier than dump B.

**Listing selection, identical in both dumps and identical to `refresh_prices.py` §(b).** `room_type ==
"Entire home/apt"` and `number_of_reviews_ltm > 0` ("established / active" listings). Prices are parsed from the
`price` string (`"$1,234.00"` → `1234.00`, any non-digit stripped, zero → missing). A market-dump whose median
entire-home price is below the local-currency equivalent of **USD 5** is dropped as a broken price field, not a
cheap market — this is the `MIN_USD_LEVEL = 5.0` rule that already drops the Swiss dumps, whose `price` column
carries 0.16–0.18 CHF a night. Conversion for the floor test only uses the frozen `COUNTRY_CCY` map and the 2026
calendar-year-average FX of `refresh_prices.py`; **every regression variable is a growth rate in local currency, so
FX drops out of the estimate entirely.**

**Dependent variables (price).**

| id | definition |
|---|---|
| `y_med` | growth of the market's **median** listed nightly price, local currency — **primary** |
| `y_rw` | growth of the **review-weighted mean** listed nightly price (weights `number_of_reviews_ltm`), local currency |
| `y_lfl` | growth of the **same-listing** median price: listings present in *both* dumps by `id`, median of the per-listing price ratio — the closest observable object to "like-for-like host pricing" |
| `y_quote` | growth of median `price_quote_price_per_night` — **registered and declared not executable**, see §2 |

**Independent variables (utilisation, supply, demand).**

| id | definition |
|---|---|
| `x_util` | growth of **stays per active listing** = Σ`number_of_reviews_ltm` ÷ (count of active listings), same selection — **primary x** |
| `x_supply` | growth of the **active listing count** (supply) |
| `x_rev` | growth of Σ`number_of_reviews_ltm` (demand) |
| `x_util_lfl` | secondary: within-dump-B like-for-like demand, Σ`number_of_reviews_ltm` ÷ Σ`number_of_reviews_ly` over listings present in dump B with a review history covering both windows |

By construction `x_util = x_rev − x_supply` in logs, so the split spec is an exact decomposition of the primary spec.

**Growth convention (registered here, before any estimate).** All growth is **annualised log growth in percent**:
`g = 100 · ln(v_B / v_A) · 365 / days(A,B)`. Annualising is forced by §2: the available pairs span 8 to 12.5 months,
not 12, and without annualisation a longer pair mechanically shows more growth on both sides and manufactures a
positive slope. Annualising removes that; it does not remove the seasonal-window problem, which §3 handles with
gap-bucket fixed effects and with §3's robustness arm (v), a same-span subsample.

## 2. Registration — the panel that actually exists, and the amendment

The task specified pairs **300–430 days** apart. That window is not executable. The inventory of the capture store
and the two sibling stores that hold the older vintages (the E-package backfill stores; read-only, nothing written
to them) gives, across 120 markets and 275 dump directories:

| store | files | markets | dump dates |
|---|---|---|---|
| `~/abnb_ia_capture` | 120 | 120 | 2026-06-14 … 2026-08-10 (119 of 120 in June 2026) |
| `~/abnb_scratch/raw_expansion/v3_2026-09-06/inside_airbnb_yoy_2025` | 115 | 115 | 2025-06-23 … 2025-12-31 (91 in September 2025) |
| `~/abnb_scratch/raw_expansion/v3_2026-09-06/inside_airbnb_listings_backfill` | 40 | 40 | 2026-06-15 … 2026-07-26 |

129 candidate within-market pairs. Their spans:

| span (days) | 0–60 | 60–250 | 250–300 | **300–330** | **330–365** | **365–400** | 400–430 |
|---|---|---|---|---|---|---|---|
| pairs | 7 | 27 | 94 | **0** | **0** | **1** | **0** |

**There is exactly one pair in 300–430 days** (`australia_wa_western-australia`, 2025-06-23 → 2026-06-28, 370 days).
The store's shape is a September-2025 wave against a June-2026 wave: the modal span is ~266–280 days, about nine
months, not twelve.

**Amendment, registered before any estimate:**

- **A1.** The primary window becomes **240–430 days**; the 300–430 arm is reported as *not executable (n = 1)* and is
  never scored. Pairs below 240 days (the 2025-11/12 → 2026-06/07 pairs and the near-duplicate 2026-06 → 2026-07
  pairs) are excluded from the primary and reported separately as a span-sensitivity arm.
- **A2.** Because spans differ, every growth variable is annualised (§1) and the primary spec carries **gap-bucket
  fixed effects** (30-day buckets of the span), so a span common to many markets — and the seasonal window it
  implies — is absorbed rather than fitted.
- **A3.** `y_quote` is **not executable on any pair**: `price_quote_price_per_night` exists only in the 2026 dumps;
  the 2025 dumps predate the column. Registered, declared dead, not scored. (Verified on the two headers: the 2026 files carry price_quote_checkin_date / _checkout_date / _total_price /
  _price_per_night / _raw; the 2025 files carry none of them.)
- **A4.** `number_of_reviews_ltm` is a trailing-twelve-month count at the dump date. On a 270-day pair the two LTM
  windows **overlap by about three months**, so `x_util`, `x_supply` and `x_rev` are attenuated toward zero relative
  to a true annual change. Attenuation in x biases |b| **up**, not down, in a univariate regression — so a *pass*
  here must be read as an upper bound on the elasticity, and a *fail* is the stronger result of the two.
- **A5.** With a September-2025 dump against a June-2026 dump, `y` compares an autumn asking price to a summer
  asking price. The common part of that is the intercept and the gap-bucket FE; the part that varies across markets
  (how seasonal a market is) is an unremoved confound and is stated as such in the verdict whichever way it lands.

## 3. Registration — models, pass line, and what each outcome means

**Specifications** (statsmodels OLS, `cov_type='cluster'`, clusters = market; a market contributes at most a
handful of pairs, so the cluster correction is small and the SE is effectively heteroskedasticity-robust — stated,
not hidden):

- **M1** `y_med = a + b·x_util`
- **M2** `y_med = a + b·x_util + region FE + gap-bucket FE` — **primary**
- **M3** `y_med = a + b1·x_rev + b2·x_supply + region FE + gap-bucket FE` — the supply/demand split
- **M2-exUS**, **M3-exUS**: M2 and M3 on the ex-United-States subsample
- Reported alongside, not as the line: M2 on `y_rw` and on `y_lfl`; M2 with `x_util_lfl`.

**Pass line, fixed now.** M2 gives **b > 0 with clustered p ≤ 0.05 on the full panel AND on the ex-US subsample.**
Both. The elasticity and its 95% CI are reported whatever happens. No lag, window, region or basis is chosen after
a result; the primary is `y_med` on `x_util` under M2 and nothing else can be promoted into its place.

**Robustness, listed now and run whatever the primary does:** (i) drop markets with fewer than 300 active listings
in either dump; (ii) winsorise y and x at 1/99; (iii) `y_rw` basis; (iv) `y_lfl` basis; (v) the modal-span
subsample (260–290 days only, where the seasonal window is common to every market); (vi) drop Switzerland; (vii) the
`y_quote` basis — dead, see A3; (viii) region-by-region M1.

**What a pass means.** The panel hands the ADR line a *measured* elasticity of like-for-like listed price to
utilisation. The NA/EMEA/APAC/LatAm 1H26 utilisation readings of `utilisation_vmatch_quarterly.csv` can then be
carried through it to a like-for-like price growth per region, and the carried core of 3.85pp gets a measured
comparator with a CI instead of a carry. It does **not** make the core a forecast: the panel is cross-sectional and
the mapping from a cross-market elasticity to a time-series one is an assumption, labelled as such.

**What a fail means.** The core stays carried exactly as `adr_v1_design.md` §3 leaves it. The NA quarterly β 0.32
stands alone as one in-sample reading on 13 points, with a market panel of ~100 pairs declining to confirm it, and
the ADR thesis's stated weakness is confirmed rather than repaired — which is the honest thing to put in front of
a lodging analyst who will ask this exact question.

<!-- SECTIONS 4+ ARE FILED AFTER THE RUN. NOTHING ABOVE THIS LINE CHANGES. -->

---

## 4. What ran

```
cd ~/Citadel-ABNB
PYTHONPATH=analysis/src python3 -W ignore -m pitch_model_v2.adr_engine.market_panel --rebuild   # raw pass, ~26 s
PYTHONPATH=analysis/src python3 -W ignore -m pitch_model_v2.adr_engine.market_panel             # from cache, seconds
```

Exit 0 both times. `analysis/src/pitch_model_v2/adr_engine/market_panel.py` reproduces every number below; it imports
`refresh_prices.py`'s `_clean_price`, `ROOM_TYPE_EH`, `MIN_USD_LEVEL`, `COUNTRY_CCY` and `fx_year_average` rather
than re-implementing them, so the listing selection is the engine's, not a second opinion on it. Outputs, all in
`data/processed/pitch_model_v2/adr_engine/`:

| file | what it holds |
|---|---|
| `market_panel_dump_aggregates.csv` | cache: 242 market-dumps, the raw-store pass |
| `market_panel_lfl_pairs.csv` | cache: id-matched price change per candidate pair |
| `market_panel_pairs.csv` | the panel: 129 pairs, every registered y_* and x_* |
| `market_panel_scores.csv` | M1, M2, M3, their ex-US twins and the alternative bases |
| `market_panel_by_region.csv` | region-by-region M1 |
| `market_panel_robustness.csv` | the registration's robustness list, §3 |
| `market_panel_descriptives.csv` | the facts §9 rests on |
| `market_panel_exclusions.csv` | every in-window pair that does not reach the primary, with its reason |
| `market_panel_implied_core.csv` | the elasticity carried through the 1H26 regional utilisation readings |

## 5. The panel that was built

242 market-dumps in 120 markets across the three stores (a market-dump held by two stores is one observation), 129
within-market pairs, **100 in the amended 240–430 day window, 94 reaching the primary**: 92 markets, 29 countries,
spans 243–370 days with a median of 275. On the A-side 88 of 94 dumps are September 2025; on the B-side 88 are June
2026. Region split EMEA 45 / NAM 31 / APAC 15 / **LatAm 3**. The primary panel covers 555,919 established
entire-home listings at A and 579,759 at B.

**Six in-window pairs and sixteen whole dumps are lost to data quality, and the losses are not random.**

- **Sixteen 2025 dumps carry a 100% empty `price` column** — an Inside Airbnb publication gap, verified on the raw
  files (Paris 2025-09-12: 81,853 rows, 72,297 entire homes, 42,978 with reviews in the last twelve months, `price`
  null on every one). The casualties include **Paris, New York City, Los Angeles, San Francisco, Barcelona, Lisbon,
  Porto, Boston, Sydney, Melbourne, Montreal, Rotterdam, Girona, Santa Clara County, Portland and Salem** — i.e. a
  large share of the panel's biggest markets. Three of them had an otherwise usable pair; the rest had no second
  dump anyway. The panel that survives is tilted toward mid-sized markets, and that is a limitation of the reading,
  not a choice.
- **Three Swiss pairs fail the $5 floor**, and the run locates the break more precisely than `refresh_prices.py`
  does: the 2025 Swiss dumps are clean (Geneva 126, Vaud 135, Zurich 140 CHF) and it is the **2026** wave that
  carries 0.16–0.18 CHF a night. Robustness (vi) "drop Switzerland" is therefore numerically identical to M2 —
  the floor had already removed them.

Descriptive facts the verdict rests on (`market_panel_descriptives.csv`):

| | value |
|---|---|
| mean / median `y_med`, annualised | **+52.0% / +51.3%** |
| median `y_lfl` (same-listing, id-matched) | **+50.6%** |
| sd of `y_med` across markets | 26.7pp |
| mean `x_util` / `x_supply` / `x_rev`, annualised | **+0.76% / +5.12% / +5.88%** |
| sd of `x_util` across markets | 7.7pp |
| raw corr(`y_med`, `x_util`) | **−0.097** |
| R² of the fixed effects alone | 0.446 |
| R² of M2 (FE + `x_util`) | 0.4462 |
| **R² added by `x_util`** | **0.001** |

The first three rows are the whole problem with this panel and must be read before any coefficient. A September-2025
asking price against a June-2026 asking price grows **52% at an annual rate**, and the same-listing measure grows
just as much (+50.6%), so it is **not** composition — it is the calendar. These are asking prices for the northern
summer set against asking prices for the autumn shoulder. The gap-bucket fixed effect removes the part of that wedge
common to the 85 markets sharing the 270–299 day span; what it cannot remove is that markets differ in *how*
seasonal they are, and that cross-market variation in seasonal amplitude is far larger than the cross-market
variation in utilisation (26.7pp of y against 7.7pp of x). This was registered as A5 before the estimate; the data
made it worse than feared.

## 6. The registered score — FAIL

| spec | n | markets | b | se | p | 95% CI | R² |
|---|---|---|---|---|---|---|---|
| M1 `y_med ~ x_util` (no FE) | 94 | 92 | −0.336 | 0.448 | 0.452 | [−1.214, +0.541] | 0.009 |
| **M2 `y_med ~ x_util` + region & gap FE — PRIMARY** | **94** | **92** | **+0.083** | **0.318** | **0.794** | **[−0.539, +0.705]** | **0.446** |
| M3 `y_med ~ x_rev + x_supply` + FE | 94 | 92 | +0.100 (`x_rev`) | 0.302 | 0.741 | [−0.493, +0.693] | 0.446 |
| — its supply leg | | | −0.068 (`x_supply`) | | 0.858 | | |
| **M2-exUS — the second half of the pass line** | **70** | **68** | **+0.041** | **0.741** | **0.956** | **[−1.412, +1.494]** | 0.269 |
| M3-exUS | 70 | 68 | −0.045 (`x_rev`) | 0.713 | 0.950 | [−1.442, +1.352] | 0.271 |
| M2 on `y_rw` | 94 | 92 | −0.165 | 0.462 | 0.720 | [−1.070, +0.740] | 0.355 |
| M2 on `y_lfl` (same-listing) | 94 | 92 | −0.070 | 0.274 | 0.798 | [−0.607, +0.467] | 0.401 |
| M2 with `x_util_lfl` | 94 | 92 | +0.000 | 0.439 | 1.000 | [−0.861, +0.861] | 0.446 |
| `y_lfl ~ x_util_lfl` (both like-for-like) | 94 | 92 | −0.131 | 0.445 | 0.769 | [−1.003, +0.742] | 0.401 |

**Registered pass line: b > 0 with clustered p ≤ 0.05 on M2 full AND M2-exUS. Result: FAIL, and not narrowly.**
Full-panel b +0.083 at p 0.79; ex-US b +0.041 at p 0.96. Every alternative basis is equally null and the signs do
not even agree with each other across bases. No specification in the file reaches p ≤ 0.05 on anything.

Region by region (M1 with gap FE, `market_panel_by_region.csv`):

| region | n | b | se | p |
|---|---|---|---|---|
| NAM | 31 | **+0.288** | 0.250 | 0.250 |
| EMEA | 45 | −0.684 | 0.794 | 0.389 |
| APAC | 15 | +1.857 | 2.164 | 0.391 |
| LatAm | 3 | — | — | fewer than 10 pairs, not estimable |

**Robustness (`market_panel_robustness.csv`) — all null, as registered, run whatever the primary did:**

| arm | n | b | p |
|---|---|---|---|
| (i) ≥ 300 active listings in both dumps | 92 | +0.091 | 0.780 |
| (ii) winsorised 1/99 on y and x | 94 | +0.079 | 0.839 |
| (iii) `y_rw` basis | 94 | −0.165 | 0.720 |
| (iv) `y_lfl` basis | 94 | −0.070 | 0.798 |
| (v) modal span 260–290d only (one common season) | 85 | −0.058 | 0.864 |
| (vi) ex-Switzerland | 94 | +0.083 | 0.794 (identical to M2 — the $5 floor had already removed it) |
| (vii) `y_quote` basis | 0 | — | NOT EXECUTABLE (A3) |
| span sensitivity 150–239d (excluded arm) | — | see file | reported, never part of the line |
| the task's 300–430d window | 1 | — | NOT EXECUTABLE (A1) |

## 7. What the panel does and does not rule out

Three things are worth saying precisely, because a lodging analyst will ask all three.

1. **The signs of the supply/demand split are the mechanism's signs.** In M3 demand carries +0.100 and supply
   −0.068: more reviews raise the price, more listings lower it. That is the right shape. Both are so far inside
   their standard errors (p 0.74 and 0.86) that the shape is a coincidence at this sample size, and it is reported
   as one.
2. **The panel cannot reject the v1b North American reading.** The primary 95% CI is [−0.54, +0.71] and the
   quarterly NA β was **0.32** — inside it. The regional cut is the same story: NAM is the only region whose point
   estimate (+0.288) sits where v1b put it, and it is the only one that does, but at p 0.25. So the panel does not
   contradict v1b; it fails to confirm it with 94 market pairs when 13 quarters could not either.
3. **What it does rule out is a large elasticity.** The upper bound of the CI is +0.71, so an elasticity above
   about 0.7 — one point of utilisation buying more than 0.7pp of like-for-like price — is outside the panel's
   95% interval on the primary basis and outside every robustness arm. And note A4: the overlapping trailing-twelve-
   month windows attenuate x, which biases |b| **upward**, so +0.71 is a generous ceiling.

Against that, the honest counterweight: with 26.7pp of cross-market dispersion in y, 7.7pp in x, and a seasonal
wedge of 52pp sitting on top of y, this panel would struggle to detect an elasticity of 0.3 even if it were there.
The test is not powerful. **A null here is weak evidence of absence, not evidence of absence** — which is exactly
why it is filed as a fail and not as a refutation.

## 8. What it means for the core, and for 4Q26

The carried core is 3.849pp (2Q26, `exfx_history.csv`); its 2023–25 mean is **2.272pp**, so the carry sits
**+1.58pp** above that mean on the 2Q26 point and +1.34pp on the 1H26 average — the thesis's "1.45pp above its
2023–25 mean" sits between the two. Carrying the panel's elasticity through the 1H26 regional utilisation readings
of `utilisation_vmatch_quarterly.csv` (`market_panel_implied_core.csv`):

| region | 1H26 util y/y | 4Q26 nights share | implied like-for-like price, panel b = 0.083 | same at v1b NA β = 0.32 | vs carried 3.85pp |
|---|---|---|---|---|---|
| NAM | +1.56% | 0.301 | **+0.13pp** | +0.50pp | −3.72pp |
| EMEA | +1.84% | 0.403 | **+0.15pp** | +0.59pp | −3.70pp |
| APAC | +2.41% | 0.123 | **+0.20pp** | +0.77pp | −3.65pp |
| LatAm | +46.81% | 0.174 | (+3.88pp) | (+14.98pp) | *vintage artefact, v1b §4.3 — excluded* |
| **BLEND ex-LatAm** | **+1.82%** | 0.826 | **+0.15pp, 95% CI [−0.98, +1.29]** | **+0.58pp** | **−3.70pp** |

**The reading.** Whichever of the two estimates you take, the measured utilisation channel accounts for **at most
about 0.6pp of the 3.85pp core, and on the panel's own number about 0.15pp.** The other ~3.2–3.7pp is still
unexplained. That is the ADR thesis's stated weakness, quantified rather than repaired: mitigation B does not
convert the carry into a measured term.

**For 4Q26 direction, the sign matters more than the size.** Utilisation is *positive* in all three clean regions in
1H26 (+1.6 / +1.8 / +2.4). So the one supply-demand mechanism an analyst would reach for first contributes, at every
estimate in this note, a **small tailwind** to like-for-like price into 4Q26 — not the give-back that a below-Street
4Q26 ADR needs. This is the same direction v1b found on the quarterly series (its reading 2), now on 92 markets in
29 countries rather than 13 North American quarters, and it is the opposite of convenient. **It does not move the
4Q26 base**, which stays the construction of `adr_v2_thesis.md` sentence 9; it removes one of the arguments for
cutting the core, and it removes it in both directions at once, because the panel is too weak to license a raise
either.

**Two limits that are not negotiable and belong on any slide that shows this.** (a) `price` in an Inside Airbnb dump
is the **host's asking price** for the listing, not a transacted ADR: it carries no discounts, no length-of-stay
pricing, no fees, and no occupancy weighting beyond the review weights of `y_rw`. (b) This is a **cross-section of
market pairs**, not a time series. Even a significant b would have answered "do markets where utilisation rose more
also price more?", not "does utilisation lead rate through time?" — and the core needs the second. The mapping from
one to the other is an assumption, and no result in this note licenses it.

## 9. Verdict

**FAIL on the pre-registered line, on every basis and in every robustness arm.** The core of the ADR line stays
carried exactly as `adr_v1_design.md` §3 leaves it and `adr_v2_thesis.md` describes it. Mitigation B does not
repair the line's weakest term; it establishes three smaller things that are worth having in front of an analyst:
the supply/demand signs are right and insignificant, a like-for-like elasticity above ~0.7 is outside the data, and
the mechanism's 1H26 direction is a small tailwind rather than the reversion a short needs. It also establishes,
against the task's own premise, that **the raw store has no twelve-month dump pairs at all** — the September-2025
to June-2026 wave structure is what exists, and the 52pp seasonal wedge it puts into y is the binding reason this
test cannot settle the question, not the sample size.

The one thing that would settle it is a third wave: a dump taken in **September 2026** against the September-2025
wave would give ~95 true twelve-month, same-season pairs and would kill the seasonal confound outright. That is a
capture job, not an analysis job, and it is the single highest-value addition to the store for this line.

## 10. RESUME

- **Registered §1–§3 before any estimate**, including the amendment A1 forced by the store: the task's 300–430 day
  window holds **one** pair, so the primary window became 240–430 days with annualised log growth and gap-bucket
  fixed effects.
- **Panel built**: 242 market-dumps → 129 pairs → **94 primary pairs, 92 markets, 29 countries**, median span 275
  days, 556k/580k established entire-home listings.
- **Primary M2: b = +0.083, se 0.318, p 0.794, 95% CI [−0.539, +0.705], R² added by x = 0.001. Ex-US: b = +0.041,
  p 0.956. FAIL on both halves of the pass line.** Every robustness arm null; no spec anywhere reaches p ≤ 0.05.
- **Implied**: the utilisation channel buys **+0.15pp** of like-for-like price (CI −0.98 to +1.29), or +0.58pp at
  the v1b NA β — against a carried core of **3.85pp**. The core stays carried; ~3.3–3.7pp remains unexplained.
- **4Q26 direction**: small *tailwind*, not reversion — the same uncomfortable direction v1b found, now on 92
  markets.
- **Data-quality findings for the store**: sixteen 2025 dumps (Paris, NYC, LA, SF, Barcelona, Lisbon, Boston,
  Sydney, Melbourne, Montreal …) publish an entirely empty `price` column; the broken Swiss CHF prices are in the
  **2026** wave, not the 2025 one; `price_quote_price_per_night` exists only from 2026, so the quote basis is dead
  for every pair.
- **Next**: a September-2026 capture wave is the one change that would make this test decisive (same-season,
  twelve-month pairs, ~95 markets). Nothing in this note moves the 4Q26 ADR base.
