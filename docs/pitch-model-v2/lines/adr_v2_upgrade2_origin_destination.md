# ADR line, upgrade 2: turning the origin story into a measured destination tilt

Date: 22 September 2026. Branch `theo/pitch-model-v2`. Code `analysis/src/pitch_model_v2/adr_engine/od_layer.py`.
Outputs `data/processed/pitch_model_v2/adr_engine/od_*.csv`.

```
cd ~/Citadel-ABNB && PYTHONPATH=analysis/src python3 -W ignore -m pitch_model_v2.adr_engine.od_layer     # exit 0
```

## 0. What this is, in one paragraph

The ADR line prices geography with `exfx.geo_mix_pp`: hold the four regional ADRs at their base-quarter
levels ($255 NA / $159 EMEA / $95 LatAm / $118 APAC, 10-K), shift the nights shares by regional growth, read
the change in the blended ADR. One point of nights share moving NA to LatAm is -0.89pp, to APAC -0.78, to
EMEA -0.51. Forward, `exfx.regional_growth_forward()` takes the nights line's ex-NA rate and splits it
`EXNA_PATTERN = 8 / 20 / 18`, the 2Q26 letter bucket midpoints, and a "tilt B" of 5 / 30 / 25 was carried as a
scenario in `geo_mix_tilt_sensitivity.csv`, justified in its own row label by "India +60, Brazil +31 origin".
**That justification is a non-sequitur and this layer is the test of it.** India +60% and Brazil +31% are
ORIGIN statements; the ADR lever is a DESTINATION lever; the two are the same number only if you know where
those nights land. This layer measures the origin-to-destination allocation as far as the cached tourism-board
payloads allow, states every cell they cannot identify, and re-prices the mix.

**The answer goes the other way from tilt B.** At any origin size weight I can defend, the measured allocation
makes the ex-NA split FLATTER than 8 / 20 / 18, not steeper: EMEA 10.5 / LatAm 16.4 / APAC 14.9, and the
geo-mix drag shrinks from -1.29pp to **-1.03pp in 3Q26 (+0.26pp of ADR)**, band -1.16 to -0.93. Tilt B
(-1.67pp) needs the four named origins to be about 22% of global nights against a defensible ceiling of 16.5%.

## 1. What the files actually contain (checked, not assumed)

Every cell below was read from `data/processed/govdata/V/raw/` with `MANIFEST.csv` provenance. Four of the
survey's seven "origin" files do not resolve origin at all:

| File | What it actually holds | Origin-resolving? |
|---|---|---|
| `ntto_arrivals_by_country_monthly.csv` | arrivals **to the US** by origin country, 11 origins + totals, 2015-01 to 2026-07 | **yes**, for the NA column (US only) |
| `jnto_arrivals_monthly.csv` | arrivals **to Japan** by origin market (china, korea, usa, australia, hong_kong, taiwan), 2003-01 to 2026-07 | **yes**, for the APAC column (Japan only). **No India row.** |
| `abs_340101_arrivals_monthly.csv` | 3 series only: `st_residents_returning`, `st_visitors_arriving`, `total_arrivals` | **no** origin split. It is a **denominator** (all Australian outbound). |
| `eurostat_tour_occ_ninat_annual.csv` | `c_resid` takes only DOM / FOR / TOTAL, EU27 + 15 geos, annual to 2024 | **no.** It is domestic-vs-foreign, not by residence country. MANIFEST: "no monthly split by residence in this table". |
| `eurostat_tour_occ_nim_monthly.csv` | nights by NACE (I551 / I552 / I553), `c_resid=TOTAL` in the pulled query | **no** residence dimension at all |
| `ine_eoap_1998_monthly.csv` | 10 national series: Spain holiday-apartment travellers/nights split "Residents in Spain" vs "Residents abroad" | **no** origin country |
| `colombia_foreign_entries_monthly.csv` | 2 columns: period, total foreign entries | **no** |
| `statcan_24100053_monthly.csv` | Canadians returning **from the US** vs **from other countries**, plus US residents entering | **partly**: a clean NA / ex-NA split of Canadian outbound, no split inside "other" |
| `anac_brazil_passengers_monthly.csv` | Brazilian air pax, DOMESTICA vs INTERNACIONAL | **partly**: a domestic / international split, no destination |
| `jta_accommodation_nights_monthly.csv` | Japan nights, total and foreign | destination-side domestic share only |

So the task's premise that "Eurostat by residence gives EMEA" and "Australia inbound by origin gives part of
APAC" does not hold in these payloads. **There is no origin resolution for the EMEA or LatAm destination
columns anywhere in this tree.** The one file that would have closed it, StatCan 24-10-0045 "travel by
Canadian residents by destination", is in the MANIFEST as "no coverage: cube ends 2025Q4".

## 2. The measured cells (`od_measured_cells.csv`, 2Q26)

| Origin | Dest cell | Proxy | Level 2Q26 | y/y | As % of the origin's own total travel |
|---|---|---|---|---|---|
| Canada | NA | US, share of **all** Canadian outbound | 7,217,677 | +5.6% | **67.7%** (76.1% in 2Q24, 67.0% in 2Q25) |
| Australia | NA | US | 249,259 | -6.5% | **8.50%** (10.43% 2Q24, 9.10% 2Q25) |
| Australia | APAC | Japan | 248,653 | -1.9% | **8.48%** (7.93% 2Q24, 8.66% 2Q25) |
| Brazil | LatAm | Brazil domestic air | 12.23m trips | +0.6% | **85.7%** floor (road travel uncounted) |
| Brazil | NA | US | 460,830 | **-2.7%** | 3.2% |
| India | NA | US | 601,740 | **-8.0%** (1Q26 -16.1%) | not identified |
| Mexico | NA | US | 4,866,826 | **+15.8%** (1Q26 +13.4%) | not identified |
| Japan | NA | US | 422,551 | +4.5% | not identified |
| Japan | APAC | Japan domestic nights | 107.1m | **-4.1%** | not identified |
| China | NA | US | 348,751 | -0.2% | not identified |
| China | APAC | Japan | 984,599 | **-58.2%** (1Q26 -54.6%) | not identified |
| Korea | APAC | Japan | 2,617,007 | +14.9% | not identified |
| US | NA | Canada (overnight) | 3,807,419 | +6.3% | not identified |
| US | APAC | Japan | 1,018,248 | +3.4% (2Q25 +27.5%) | not identified |
| UK | NA | US | 1,028,895 | -2.2% | not identified |
| Germany | NA | US | 368,401 | -22.8% | not identified |

Three facts come straight off this table and need no model:

1. **The origins management names are not sending their growth to NA.** India-origin Airbnb nights +60% while
   India-to-US arrivals are -8.0%; Brazil +31% against -2.7%; China's two measured destination cells are
   -0.2% and -58.2%. Whatever those nights are, they are ex-NA nights.
2. **Two origins have a fully measured NA share and both have shifted out of NA.** Canada's US share of
   outbound fell 76.1% to 67.7% over two years; Australia's fell 10.43% to 8.50% while its Japan share rose
   7.93% to 8.48%. This is the geo-mix mechanism observed directly in third-party data.
3. **Mexico is the counter-example and it matters.** Mexico-to-US arrivals are +15.8%, the only named origin
   accelerating into NA. Mexican origin growth is partly an NA event, which pushes the mix the other way.

## 3. The allocation matrix (`od_origin_allocation.csv`)

37 cells, one row each, with a `tier` and a `source` string. Tier counts: **MEASURED 2, PARTIAL 4, ASSUMED 13,
UNIDENTIFIED 16.** That ratio is the honest headline of this layer.

The four origins that carry a disclosed Airbnb growth rate, and are therefore used in the tilt:

| Origin | NA | EMEA | LatAm | APAC | What is measured, what is not |
|---|---|---|---|---|---|
| India | 0.060 [0.03, 0.10] | **0.20 [0.00, 0.40]** | 0.005 | **0.735 [0.535, 0.965]** | ASSUMED level, MEASURED direction on NA (NTTO -8.0%). **The EMEA/APAC split is UNIDENTIFIED.** Nothing here observes Indian travel to the Gulf, Thailand, Singapore or the UK; JNTO has no India row; `india_mot_fta` is "no access (PDF only)". Airbnb's EMEA includes the Middle East, where most Indian outbound lands, and Indian *domestic* travel is an APAC destination. Bound, not point. |
| Brazil | 0.032 [0.02, 0.05] | 0.030 | **0.933 [0.86, 0.96]** | 0.005 | PARTIAL: ANAC domestic share 78.3% of air trips is a **floor** (road travel uncounted); NTTO Brazil-to-US over ANAC trips gives the NA cell at 3.2%. EMEA is a residual, no file. |
| Mexico | **0.300 [0.20, 0.45]** | 0.020 | 0.675 | 0.005 | ASSUMED level (Mexican domestic travel is in no file: datatur, banxico, upm all "no access"), MEASURED direction +15.8%. |
| Japan | 0.050 | 0.030 | 0.005 | **0.915 [0.84, 0.955]** | JTA measures Japanese *domestic* nights, not Japanese *outbound*, so the domestic/outbound split is judgement. |

Reference rows also in the file: Canada (MEASURED NA 0.677, ex-NA split UNIDENTIFIED), Australia (MEASURED NA
0.085, PARTIAL APAC 0.085, EMEA/LatAm UNIDENTIFIED), US, China, Korea, UK, Germany (levels only).

**Cross-source warning, quantified.** Dividing one agency's numerator by another's denominator is not clean:
the same flow, Canadians to the US in 2Q26, is 3,822,640 in NTTO and 7,217,677 in StatCan, **a 1.89x ratio**.
Any share built across sources here (Australia, Brazil) inherits an error of that order. It is in
`od_validation_scores.csv` as its own row.

## 4. The implied tilt (`od_implied_tilt.csv`)

Mechanism. For each ex-NA destination `d`, with `W_o` the origin's share of global nights and `a_od` its
allocation, `g_d = [ sum_o W_o a_od g_o + R_d g_rest ] / S_d` with `R_d = S_d - sum_o W_o a_od`, and `g_rest`
solved so the ex-NA aggregate lands exactly on the target. On 2Q26 shares the disclosed buckets imply ex-NA
+12.71%, and every pattern below sums to that same 12.71% (`exna_check` column), so they are directly
comparable to 8 / 20 / 18.

Origin growth used, 2Q26: India **+60** (panel `india_origin_growth_pct`), Brazil **+31** (panel), Japan
**+18** (2Q26 letter, "high-teens"), Mexico **+12** (1Q26 letter "continued double-digit", carried as a floor;
2Q26 gives no number). Panel in `od_origin_growth_panel.csv` with a source string per cell.

Size weights `W` (share of global nights booked on an origin basis) are **not disclosed anywhere**. Central
India 1.0%, Brazil 5.5%, Mexico 3.0%, Japan 3.0% = 12.5% of nights; band 8.5% to 16.5%. **This is the binding
unknown of the layer, larger in effect than any allocation cell.**

| Scenario | EMEA | LatAm | APAC | implied unnamed-origin growth |
|---|---|---|---|---|
| **2Q26 letter buckets (the line's base)** | **8.0** | **20.0** | **18.0** | -- |
| **measured OD tilt, central** | **10.48** | **16.36** | **14.91** | 10.14 |
| India all-APAC corner (EMEA 0.00) | 10.24 | 16.36 | 15.72 | 10.14 |
| India all-EMEA corner (EMEA 0.40) | 10.72 | 16.36 | 14.10 | 10.14 |
| W lo, India EMEA 0.40 (flattest) | 11.42 | 15.35 | 13.23 | 11.11 |
| W hi, India EMEA 0.00 (steepest) | 9.18 | 17.55 | 17.56 | 9.04 |
| tilt B (the v1 scenario) | 5.0 | 30.0 | 25.0 | -- |

**Band: EMEA 9.2 to 11.4, LatAm 15.4 to 17.6, APAC 13.2 to 17.6.** Tilt B is outside it in every dimension.

Note where the India ambiguity does and does not bite: moving India's EMEA share across its **full** [0, 0.40]
bound moves EMEA by 0.48pp and APAC by 1.62pp and LatAm by nothing. It is a second-order uncertainty. The
first-order one is `W`.

**The inverse question (`od_letter_bucket_decomposition.csv`).** Hold the letter buckets and ask what the
un-named origins must be doing:

| | letter bucket | named-origin mass, % of the region | named-origin contribution, pp | unnamed origins must grow |
|---|---|---|---|---|
| EMEA | 8.0 | 1.2% | +0.47 | 7.6% |
| LatAm | 20.0 | 40.2% | +10.30 | 16.2% |
| APAC | 18.0 | 28.6% | +7.67 | 14.5% |

So the named origins explain **82% of the LatAm-minus-EMEA gap and 72% of the APAC-minus-EMEA gap** at the
central weights -- but only because they are 40% and 29% of those regions' bases. The residual still has to
carry 16.2% into LatAm against 7.6% into EMEA, i.e. **the letter buckets embed a dispersion in the *unnamed*
base that the origin statements say nothing about.**

**How big would the named origins have to be to generate 8 / 20 / 18 on their own?** Bisection on the
LatAm-minus-EMEA gap (`od_letter_bucket_lambda.csv`): **lambda = 1.74, i.e. the four origins at 21.7% of
global nights** against a central 12.5% and a defensible ceiling of 16.5%. At lambda = 2.0 the pattern is
7.18 / 21.85 / 18.08, essentially the letter buckets. **The letter buckets are internally consistent with the
origin statements only if Brazil alone is ~11% of global origin nights when all of LatAm is 17.9% of
destination nights. That is the test tilt B fails.**

## 5. Pricing it (`od_geo_mix_measured_tilt.csv`)

Each pattern is scaled to each quarter's ex-NA rate from `regional_growth_forward.csv` on that quarter's base
shares -- exactly the `EXNA_PATTERN` convention -- then priced with `exfx.geo_mix_pp` on the base-quarter
shares and the `adr_*_usd_anchored` levels from `04_regional_quarterly_wide.csv`, carrying the ADR levels for
3Q27 / 4Q27 as `geo_mix_forward()` does. **Self-check asserted in code:** the base pattern re-priced here
reproduces `geo_mix_forward.csv` to `max |diff| < 1e-9`.

Geo-mix term, pp of blended ADR:

| Pattern | 3Q26 | 4Q26 | 1Q27 | 2Q27 | 3Q27 | 4Q27 |
|---|---|---|---|---|---|---|
| base 8 / 20 / 18 (the line today) | -1.293 | -1.336 | -1.620 | -1.081 | -1.174 | -1.109 |
| **measured OD tilt, central** | **-1.029** | **-1.095** | **-1.335** | **-0.895** | **-0.998** | **-0.926** |
| measured, flattest corner | -0.932 | -1.009 | -1.231 | -0.829 | -0.932 | -0.859 |
| measured, steepest corner | -1.159 | -1.210 | -1.473 | -0.985 | -1.085 | -1.014 |
| stress, named origins at 2x | -1.387 | -1.425 | -1.725 | -1.149 | -1.237 | -1.176 |
| tilt B 5 / 30 / 25 | -1.674 | -1.700 | -2.040 | -1.362 | -1.424 | -1.380 |

Delta vs base, central: **+0.263 / +0.241 / +0.285 / +0.186 / +0.176 / +0.184 pp**. Band +0.09 to +0.39pp.
Tilt B is -0.38pp at 3Q26 against base and **-0.65pp against the measured central**. The measured evidence
moves ex-FX ADR **up** by about a quarter of a point a quarter, and it removes tilt B from the scenario set.

## 6. Validation (`od_validation.csv`, `od_validation_scores.csv`)

The allocation is a fixed matrix, so it can only be tested on the **cross-section**: does a region's exposure
to the named high-growth origins predict how far its disclosed bucket sits above or below that quarter's
disclosed ex-NA rate? 7 quarters (4Q24 to 2Q26), 3 regions.

- **Ordering test (the honest one): the implied ranking of the three regions matches the disclosed ranking in
  4 of 7 quarters, binomial tail against a random ranking p = 0.018.** Two of the three misses (4Q24, 1Q26)
  are quarters where two disclosed buckets are **tied** (21.5 / 21.5 and 18 / 18), so the ordering is not
  identified there; dropping them gives **4 of 5, p = 0.003**. The one real miss is 4Q25, where the model puts
  APAC above LatAm (India +50 and Japan +27 into APAC) and the letter puts LatAm 18 above APAC 15.
- Pooled region-quarter correlation of exposure against bucket deviation: r = 0.889, rho = 0.809, sign
  agreement 95.2%, n = 21 -- **but the effective n is 7**, because it is the same cross-section repeated. It
  is recorded with that caveat in the CSV and should never be quoted on its own.
- **Time-series: nothing.** Within EMEA / LatAm / APAC, the quarter-to-quarter move in named-origin exposure
  against the quarter-to-quarter move in the bucket gives r = +0.18 / -0.15 / -0.25 (n = 7 each). Direct pairs
  are no better: Brazil origin growth vs the LatAm mid r = 0.38 (n = 7), India vs APAC r = 0.50 (n = 3),
  Japan vs APAC r = -0.19 (n = 6), Mexico vs LatAm r = -0.50 (n = 3). The V survey's point 6 applies: the
  LatAm mid takes four distinct values in ten quarters and the APAC mid three, so these are correlations on a
  step function and I am not leaning on any of them.
- **Level context, not validation.** Japan's domestic accommodation nights were **-4.1%** y/y in 2Q26 (JTA)
  while Airbnb's Japan-origin nights grew high-teens; Japan total inbound was -5.3%; Spain's holiday-apartment
  nights -0.03% in July. These files measure **markets**; Airbnb's growth is **share**. That is exactly why
  this layer uses them for the **allocation** and never for the **level**, and it is the same structural point
  the V survey made when it recommended no full workstream.

**Verdict: the cross-sectional shape is corroborated (4 of 5 identified quarters, p = 0.003); the
time-series is not, at all. This layer is entitled to set the SHAPE of the ex-NA split. It is not entitled to
forecast a quarter's bucket.**

## 7. Measured vs inferred, stated plainly

**Measured (a ratio of two cached agency series):** Canada's NA share of outbound (67.7%, and its two-year
fall from 76.1%); Australia's US share of outbound (8.50%) and Japan share (8.48%).

**Partial (numerator observed, denominator a proxy or one country only):** Brazil to NA (3.2% on an ANAC trips
denominator with a 0.60 resident-share assumption); Brazil's LatAm floor (85.7%, air only); Australia to APAC
(Japan only); US to APAC (Japan only, no denominator).

**Direction measured, level assumed:** India, Mexico, Japan, China, Korea, UK, Germany to NA, and China to
APAC. The growth rates are real agency numbers; the shares are my judgement with a stated band.

**Unidentified, bound only:**
- **India to EMEA vs India to APAC. These files cannot identify it.** No payload here observes Indian outbound
  to anywhere except the United States. The bound is EMEA in [0.00, 0.40] with APAC taking the residual
  [0.535, 0.965]. Effect on the priced term: 0.03pp at 3Q26. It is not the thing that matters.
- Canada's, Australia's, the US's and China's ex-NA destination splits.
- **The entire EMEA and LatAm destination columns by origin.** Eurostat gives DOM/FOR only, Spain gives
  residents-in/abroad only, Colombia gives a single total. There is no origin composition of EMEA or LatAm
  nights anywhere in this tree, at any tier.
- Origin size weights `W`. Nothing is disclosed. The band 8.5% to 16.5% drives the whole result range and
  the honest statement is that the tilt is identified in sign and shape, not in magnitude.

## 8. What I would change in the line

1. **Retire tilt B.** Its row label in `geo_mix_tilt_sensitivity.csv` claims India +60 / Brazil +31 as its
   justification. Those origin numbers, allocated with everything these files can measure, produce the
   OPPOSITE tilt. If a steep scenario is wanted, the defensible steep case is the W-hi corner (9.2 / 17.6 /
   17.6, -1.16pp at 3Q26), not 5 / 30 / 25.
2. **Carry the measured tilt as the composition scenario, not as the base.** The base 8 / 20 / 18 is a filed
   disclosure and outranks a judgement-weighted origin model. But the layer says the base is on the
   **conservative** side of the origin evidence by about +0.26pp of ADR, and that asymmetry belongs in the
   band: the geo-mix drag is more likely to be smaller than -1.29 than larger.
3. **Watch Mexico.** It is the single measured cell that runs against the cheap-region story (+15.8% into the
   US) and it is the one whose size weight I am least sure of.

## RESUME

`od_layer.py` builds an origin-to-destination-region allocation for the origins management names, from the
cached tourism-board payloads in `data/processed/govdata/V/raw/`, and re-prices the ADR line's four-region
geo-mix term under it. First finding: **four of the files the brief expected to resolve origin do not** --
Eurostat `ninat` is DOM/FOR only, `nim` has no residence dimension, ABS has three national series and no
origin split, Spain INE is residents-in/abroad, Colombia is a single total -- so **there is no origin
composition of the EMEA or LatAm destination columns anywhere in this tree**, and the matrix comes out
MEASURED 2 / PARTIAL 4 / ASSUMED 13 / UNIDENTIFIED 16. What IS measured is decisive anyway: India-origin
Airbnb nights +60% against India-to-US arrivals **-8.0%**, Brazil +31% against **-2.7%**, China's two
observable destination cells **-0.2%** and **-58.2%** -- the named origins' growth is entirely ex-NA -- while
Canada's US share of all its outbound fell **76.1% to 67.7%** in two years and Australia's **10.43% to 8.50%**,
the geo-mix mechanism visible directly in third-party counts. Mexico is the counter-example, **+15.8%** into
the US. Combining those allocations with the disclosed origin growth (India 60, Brazil 31, Japan 18, Mexico 12)
and origin size weights of 12.5% of global nights [8.5%, 16.5%] gives an implied ex-NA split of **EMEA 10.5 /
LatAm 16.4 / APAC 14.9** against the letter buckets 8 / 20 / 18, band EMEA 9.2-11.4 / LatAm 15.4-17.6 / APAC
13.2-17.6, all summing to the same ex-NA rate. Priced with `exfx.geo_mix_pp` on the same base-quarter shares
and anchored ADRs (base pattern reproduced to 1e-9), the geo-mix term goes from -1.29 / -1.34 / -1.62 / -1.08 /
-1.17 / -1.11 to **-1.03 / -1.10 / -1.34 / -0.90 / -1.00 / -0.93**, i.e. **+0.26pp of ADR in 3Q26** [+0.13,
+0.36]; **tilt B (-1.67 in 3Q26) needs the four named origins at 21.7% of global nights against a ceiling of
16.5% and should be retired.** Validation is cross-sectional only and comes back **4 of 5 identified quarters
on the ordering test, p = 0.003** (two of the seven quarters have tied disclosed buckets; the one real miss is
4Q25, where the model ranks APAC above LatAm), with **no time-series content at all** (within-region r = +0.18
/ -0.15 / -0.25, n = 7) -- so the layer sets the SHAPE of the ex-NA split and must not be used to forecast a
bucket. The **India EMEA-vs-APAC split is not identifiable in these files** (no payload observes Indian
outbound to anywhere but the US; JNTO has no India row; `india_mot_fta` is PDF-only); its full bound moves the
priced term by only 0.03pp, and the binding unknown is instead the undisclosed origin size weights. Next: if
the line wants this promoted past a scenario, the only thing that would do it is an origin-composition source
for EMEA or LatAm nights -- StatCan 24-10-0045 (Canadian trips by destination) is the closest and its cube
ends 2025Q4.
