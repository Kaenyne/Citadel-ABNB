# ADR line v2, upgrade 1 — re-weighting the within-EMEA country mix with Eurostat platform nights

**22 September 2026.** The sub-regional geographic-mix term registered in
[`adr_v2_geomix_prereg.md`](adr_v2_geomix_prereg.md) measures, inside each Airbnb region, whether stays are growing
faster in cheaper or dearer countries. Its weakest joint inside EMEA is the weight vector: the country shares
`s_c(t−4)` are the **Inside Airbnb panel's** shares (10 Italian markets, 9 Spanish, 4 French, 4 UK, 4 Greek, 2 Irish),
which is a scrape footprint, not Airbnb's night distribution. This file replaces that weight vector with Eurostat's
**short-stay platform nights by country** and asks a single question: **does the EMEA mix term, and the GBV-weighted
sub-regional term that carries it into the 4Q26 ADR, move when the weights stop being an artefact of where Inside
Airbnb scrapes?** Nothing is fitted. No country, window or price basis was chosen after seeing a result. Web
fetches: zero — every input was already on disk.

Engine: `analysis/src/pitch_model_v2/adr_engine/geomix_eurostat.py`.
Outputs: `data/processed/pitch_model_v2/adr_engine/geomix_eurostat_{coverage,shares,emea_mix,emea_forward,
subregional_term,adr_effect}.csv`.

```
cd ~/Citadel-ABNB && PYTHONPATH=analysis/src python3 -W ignore -m pitch_model_v2.adr_engine.geomix_eurostat
# exit 0; writes the six CSVs above. Nothing else on disk is touched.
```

**Control first.** The module re-implements the frozen `geomix.build_term` arithmetic and the (previously one-off)
forward roll. Run with `share_src='panel', growth_src='panel', price_basis='median'` it reproduces
`geomix_within_region.csv` (EMEA, n 43), `geomix_within_region_forward.csv` (EMEA, n 6),
`geomix_subregional_term.csv` (n 43) and `geomix_subregional_term_forward.csv` (n 6) to **max |Δ| = 2.2e-14 pp**.
Every number below is therefore a weight effect, not a re-implementation effect.

---

## 0. Verdict in five lines

1. **The Eurostat weights are very different from the panel's** — France +10.6pp of EMEA weight, Germany +5.4,
   Spain +3.9 against Italy −8.4, Ireland −5.4, Hungary −1.5, Czechia −1.3 (base 2Q25) — **and the EMEA mix term
   barely moves**: 1Q23–2Q26 mean −0.11pp (panel) vs **−0.05pp** (Eurostat shares), mean |Δ| 0.15pp, r 0.84 (n 14).
2. **The GBV-weighted sub-regional term is nearly unchanged**: 1Q23–2Q26 mean **−0.453pp → −0.431pp**. H1's
   "≥ 0.25pp absolute mean" line still passes under every variant (−0.43 to −0.47).
3. **The 4Q26 ADR effect moves by $0.02.** Forward 4Q26 sub-regional term −0.147 → **−0.160pp**; ADR effect
   −$0.246 → **−$0.268** on a 4Q25 base of $167.51. That is inside the rounding of the pitch card.
4. **The only variant that moves anything is Eurostat's own growth** (variant B): term mean −0.47pp, forward 4Q26
   **−0.261pp**, ADR effect **−$0.437** (−$0.19 vs today). But that object is all platforms, all guests, stops at
   **1Q26**, and carries EMEA growth of +6 to +16% against the panel's −5 to +13% — it is not Airbnb's stays and
   should not enter the base.
5. **Coverage is good but not complete and the gaps are structural.** Eurostat covers 18 of the panel's 21 EMEA
   countries; the UK, Turkey and South Africa are outside the EU/EEA frame and keep their panel share
   (**12.3% of EMEA weight** at the 2Q25 base, 9.8–16.5% across 1Q23–2Q26). A further **~12.5%** of Eurostat's own
   EMEA platform nights sit in countries the panel has no market in (Poland, Croatia, Romania, Bulgaria, Cyprus,
   Finland, Estonia, Lithuania, Luxembourg, Slovenia, Slovakia, Iceland, Liechtenstein) and stay at zero weight —
   the reweighting redistributes among panel countries, it cannot add countries the panel cannot grow.

---

## 1. What was inspected, and what was used

| file | what it is | verdict |
|---|---|---|
| `data/processed/eurostat_platform_nights_monthly.csv` | Eurostat short-stay **platform** nights (collaborative-economy accommodation), monthly **2018-01 → 2026-03**, 31 geos (EU27 + CH, NO, IS, LI), **zero missing cells** in 99 months × 31 columns; EU27 columns sum to the `eu27_nights` aggregate to 1.0000 in every month | **used** — the weight source and variant-B growth source |
| `data/processed/govdata/V/raw/eurostat_tour_occ_nim_monthly.csv` | nights at **all** tourist accommodation establishments (`I551` hotels / `I552` holiday / `I553` campsites / `I551-I553`), 2015-01 → **2026-06**, but only **15 countries + EU27** | **not used as weights** — not platform-specific, and it drops Belgium, Latvia, Malta, Norway, Switzerland, Turkey. Noted only because it is the one Eurostat object that reaches **2Q26**, one quarter past the platform series |
| `data/processed/govdata/V/raw/eurostat_tour_occ_ninat_annual.csv` | same establishment universe, **annual**, by residency (DOM / FOR / TOTAL), 2015–2025, 15 countries + EU27 | **not used** — annual only, so it cannot form a base *quarter* |

**Point-in-time.** The platform series was pulled with the rest of the govdata tree on 18 Sep 2026 and ends
2026-03, i.e. a ~5.5-month publication lag. The mix term needs the share vector at **t−4**, which is 13.5 months
old at the print of t, so the lag never binds for history — there is no look-ahead in any history number here.
It does bind forward: Eurostat cannot supply a 2Q26 base quarter, which is why the forward keeps the registered
**roll** (below) rather than reading observed base quarters.

## 2. Construction

Unchanged in form:
`mix_r(t) = [Σ_c s_c(t−4)(1+g_c(t)) P_c] / [(1+g_r(t)) Σ_c s_c(t−4) P_c] − 1`, `subgeo(t) = Σ_r w_r mix_r(t)`,
`w_r` the 10-K GBV share knowable at the print (FY2025: EMEA **0.3743**). Only the EMEA row is rebuilt; NAM, LatAm
and APAC are taken from `geomix_within_region.csv` verbatim and re-weighted by `geomix.subregional_term`.

**Shares (the change).** Monthly Eurostat nights → quarterly sums (quarters with all three months only, n 33,
2018Q1–2026Q1). ISO → panel country: AT, BE, CH, CZ, DE, DK, **EL**→greece, ES, FR, HU, IE, IT, LV, MT, NL, NO, PT,
SE. **united-kingdom, turkey, south-africa are not in Eurostat**; they keep their Inside Airbnb panel share `s_panel`
and the 18 Eurostat countries are scaled to the remaining `1 − Σ s_panel(UK,TR,ZA)`, so the vector sums to 1 and the
three uncovered countries are neither dropped nor silently inflated. That kept block is **12.3%** of EMEA weight at
the 2Q25 base (range 9.8% in 3Q23 to 16.5% in 1Q26 — it is seasonal because UK/ZA are winter-weighted in the panel).

**Growth.** Variant **A** keeps the panel's vintage-matched `stays_yoy_pct`. Variant **B** substitutes Eurostat's own
country nights y/y where it exists (18 of 21 countries every quarter; UK/TR/ZA fall back to the panel), available
1Q19–**1Q26** only, so **2Q26 has no variant-B reading**.

**Prices.** `P_c` is rebuilt from `market_price_levels_capture_2026.csv` as the `n_listed`-weighted mean over each
country's priced markets — which reproduces `country_price_levels_usd.csv` to 5.7e-14 on the median basis. The
**rw_mean** sensitivity (upgrade 4, partial) is the same aggregation of `rw_mean_listed_usd`, the review-weighted
mean listed price. Malta has no row in the capture store and Switzerland's three markets carry a broken price field
(Geneva/Vaud/Zurich at **$0.20–$0.30**, dropped at a stated $5 floor, exactly as the build behind
`country_price_levels_usd.csv` did); both take the EMEA median ($179.52 median basis / $228.92 rw basis). That
imputed block is **1.9–2.2%** of EMEA weight.

**Forward (3Q26–4Q27), re-implemented and verified.** `g_c = g_EMEA(q)` from `regional_growth_forward.csv` **+** the
country's average differential to its region over 2H25–1H26 (3Q25, 4Q25, 1Q26, 2Q26); shares start at the last
complete base cross-section (2Q25, from `n_prior` at 2026Q2), are rolled once with the realised 2Q26 growth to reach
the 3Q26 base, and rolled one step per quarter thereafter. This reproduces the existing
`geomix_within_region_forward.csv` EMEA row to 2.2e-14. For the Eurostat variants only the starting share vector
changes; for variant B the differentials use 3Q25–1Q26 (**n 3**, not 4) and the initial roll uses Eurostat 1Q26
growth.

## 3. How different are the weights? (base quarter 2Q25, n 21 countries)

| country | panel share | Eurostat share | Δ | P (USD, median basis) |
|---|---:|---:|---:|---:|
| france | 0.1043 | **0.2105** | **+0.1062** | 216.70 |
| germany | 0.0218 | 0.0762 | +0.0543 | 210.63 |
| spain | 0.1528 | 0.1919 | +0.0391 | 249.01 |
| sweden | 0.0048 | 0.0082 | +0.0034 | 244.24 |
| austria | 0.0171 | 0.0196 | +0.0025 | 145.27 |
| switzerland | 0.0093 | 0.0105 | +0.0013 | *imputed* |
| the-netherlands | 0.0141 | 0.0149 | +0.0008 | 350.99 |
| united-kingdom | 0.0898 | 0.0898 | 0 (kept) | 305.80 |
| turkey | 0.0191 | 0.0191 | 0 (kept) | 100.25 |
| south-africa | 0.0143 | 0.0143 | 0 (kept) | 108.08 |
| norway | 0.0099 | 0.0085 | −0.0014 | 198.82 |
| latvia | 0.0045 | 0.0020 | −0.0025 | 97.62 |
| belgium | 0.0188 | 0.0152 | −0.0036 | 168.97 |
| malta | 0.0123 | 0.0086 | −0.0037 | *imputed* |
| denmark | 0.0138 | 0.0085 | −0.0053 | 272.46 |
| greece | 0.0648 | 0.0538 | −0.0110 | 177.13 |
| czech-republic | 0.0252 | 0.0124 | −0.0128 | 124.72 |
| portugal | 0.0689 | 0.0546 | −0.0144 | 165.17 |
| hungary | 0.0278 | 0.0129 | −0.0149 | 102.39 |
| ireland | 0.0634 | **0.0098** | **−0.0536** | 298.45 |
| italy | 0.2431 | **0.1587** | **−0.0843** | 179.52 |

The panel's distortions are exactly what you would guess from its market list: **Ireland is 6.3% of the panel's EMEA
stays and 1.0% of EMEA platform nights** (Dublin is one market and rural Ireland is not scraped); **Italy is 24.3%
against 15.9%** (ten Italian markets); **France is 10.4% against 21.1%** (four French markets miss the rural stock
that dominates French platform nights); Germany 2.2% against 7.6%. The same pattern holds at the 1Q22 base
(France +13.6pp, Italy −10.0, Ireland −5.0). **This is a large re-weighting.** What follows is the point of the file.

## 4. The within-EMEA mix term, 1Q23–2Q26 (pp)

`euro` = Eurostat shares, `med`/`rw` = median vs review-weighted-mean price basis.

| quarter | panel/panel/med *(current)* | euro/panel/med **(A)** | euro/euro/med **(B)** | euro/panel/rw | panel/panel/rw | euro/euro/rw |
|---|---:|---:|---:|---:|---:|---:|
| 1Q23 | 0.192 | 0.229 | −0.066 | −0.199 | −0.052 | −0.354 |
| 2Q23 | −0.216 | −0.197 | −0.419 | −0.165 | −0.210 | −0.319 |
| 3Q23 | 0.189 | −0.015 | −0.291 | −0.097 | 0.057 | −0.382 |
| 4Q23 | −0.149 | −0.020 | −0.138 | −0.045 | −0.133 | −0.151 |
| 1Q24 | −0.553 | −0.185 | −0.058 | −0.339 | −0.572 | −0.029 |
| 2Q24 | −0.185 | −0.116 | −0.246 | −0.226 | −0.201 | −0.205 |
| 3Q24 | 0.211 | 0.105 | 0.109 | −0.102 | 0.078 | 0.237 |
| 4Q24 | −0.617 | −0.302 | −0.466 | −0.177 | −0.464 | −0.298 |
| 1Q25 | −0.201 | 0.123 | −0.133 | 0.353 | −0.011 | −0.028 |
| 2Q25 | −0.509 | −0.338 | −0.374 | −0.150 | −0.386 | −0.304 |
| 3Q25 | 0.172 | 0.211 | −0.015 | 0.233 | 0.180 | 0.015 |
| 4Q25 | −0.063 | −0.162 | −0.349 | −0.330 | −0.188 | −0.402 |
| 1Q26 | −0.284 | −0.364 | −0.324 | −0.446 | −0.316 | −0.306 |
| 2Q26 | **0.431** | **0.320** | *n/a* | **0.209** | 0.362 | *n/a* |
| **mean, n 14** | **−0.113** | **−0.051** | *(n 13) −0.213* | −0.106 | −0.133 | *(n 13) −0.194* |
| mean 1Q23–1Q26, n 13 | −0.155 | −0.079 | −0.213 | −0.130 | −0.171 | −0.194 |
| mean 3Q25–2Q26, n 4 | +0.064 | +0.002 | *(n 3) −0.229* | −0.084 | +0.009 | *(n 3) −0.231* |
| sd | 0.319 | 0.222 | 0.176 | 0.226 | 0.245 | 0.198 |

Correlations with the current series (n 14, n 13 for B): **Eurostat shares r 0.84**, Eurostat growth r 0.54,
rw price basis r 0.94. Mean |Δ| from re-weighting alone is **0.148pp**, max **0.368pp** (1Q24).

**Why the big weight change buys so little.** The mix term is a covariance between growth differentials and *relative*
price, not a level. The three countries that gain most weight — France ($217), Germany ($211), Spain ($249) — sit
close to the EMEA weighted mean, so extra weight on them mostly cancels. The two that lose most weight pull in
opposite directions: Italy is **below** average ($180) and Ireland well **above** ($298), and in 2025–26 both were
growing near the regional rate in the panel. The reweighting is large in the share vector and small in the term
because it is nearly orthogonal to the price ordering.

**2Q26 survives.** The prereg's headline EMEA reading (+0.43pp, "UK +7.7% at 1.46× the regional price") is
**+0.32pp** on Eurostat shares and **+0.21pp** on the review-weighted price basis. The sign and the story hold; the
size is 25–50% smaller because the UK's 1.46× multiple is computed against a dearer regional average once France
and Germany replace Italy.

**3Q26 is unchanged by construction** (0.136pp): the partial-quarter panel has only Italy and Turkey, and Turkey is a
kept country, so Italy takes the complement under either weighting.

## 5. The GBV-weighted sub-regional term

| variant | mean 1Q23–2Q26 (n 14) | mean 1Q23–1Q26 (n 13) | 1Q26 | 2Q26 |
|---|---:|---:|---:|---:|
| panel shares / panel growth / median **(current)** | **−0.453** | −0.481 | −0.258 | −0.100 |
| Eurostat shares / panel growth / median **(A)** | **−0.431** | −0.453 | −0.288 | −0.142 |
| Eurostat shares / Eurostat growth / median **(B)** | −0.472 *(n 13)* | −0.500 | −0.273 | n/a |
| panel / panel / rw_mean | −0.460 | −0.486 | −0.270 | −0.126 |
| Eurostat / panel / rw_mean | −0.450 | −0.471 | −0.319 | −0.183 |
| Eurostat / Eurostat / rw_mean | −0.465 *(n 13)* | −0.493 | −0.267 | n/a |

**H1 (the registered ≥ 0.25pp absolute-mean line) passes under all six.** The spread across every weight, growth and
price choice is **0.04pp** on the 14-quarter mean. The prereg's other H1 finding — that the drag is *fading*
(1Q23–2Q26 −0.45 → 3Q25–2Q26 −0.15) — also survives, marginally deeper: the last four quarters average **−0.175pp**
on Eurostat shares against **−0.152pp** today (−0.207 on Eurostat shares with the review-weighted price basis).

## 6. Forward 3Q26–4Q27 and the 4Q26 ADR effect

Sub-regional term, forward (pp):

| quarter | current | A: euro/panel/med | B: euro/euro/med | euro/panel/rw | euro/euro/rw |
|---|---:|---:|---:|---:|---:|
| 3Q26 | −0.137 | −0.153 | −0.254 | −0.182 | −0.252 |
| **4Q26** | **−0.147** | **−0.160** | **−0.261** | **−0.189** | **−0.258** |
| 1Q27 | −0.155 | −0.166 | −0.265 | −0.194 | −0.262 |
| 2Q27 | −0.165 | −0.173 | −0.273 | −0.202 | −0.270 |
| 3Q27 | −0.173 | −0.180 | −0.278 | −0.208 | −0.275 |
| 4Q27 | −0.181 | −0.186 | −0.284 | −0.215 | −0.280 |

The EMEA *part* of that term goes from **+0.021pp** (current, 4Q26) to **+0.008** (A), **−0.021** (A, rw price) and
**−0.093** (B); the rest of the term is the unchanged Canada-vs-US NAM leg.

**4Q26 ADR effect** (on `adr_usd_base_year` = 4Q25 ADR **$167.51**; the scenario row in `exfx.alternatives` adds the
term to `geo_mix`):

| variant | 4Q26 subgeo (pp) | Δ vs current (pp) | ADR effect ($) | **Δ ADR ($)** |
|---|---:|---:|---:|---:|
| current (panel shares) | −0.1468 | — | −0.246 | — |
| **A: Eurostat shares, panel growth, median P** | −0.1598 | −0.0130 | −0.268 | **−0.022** |
| Eurostat shares, panel growth, rw price | −0.1890 | −0.0422 | −0.317 | −0.071 |
| panel shares, rw price (price effect alone) | −0.1659 | −0.0191 | −0.278 | −0.032 |
| **B: Eurostat shares, Eurostat growth, median P** | −0.2608 | −0.1140 | −0.437 | **−0.191** |
| Eurostat shares, Eurostat growth, rw price | −0.2585 | −0.1116 | −0.433 | −0.187 |

On the base 4Q26 ADR of $173.03, upgrade 1 as registered (variant A) moves the composition scenario from $172.79 to
**$172.77**. Even the aggressive variant B only reaches **$172.60**.

## 7. Honest reading of variant B

Variant B is the only thing here that changes a number anybody would notice, and it is the variant that should not
enter the base. Its mechanism is visible in the growth table (3Q25–1Q26 averages, y/y %):

| | Eurostat | panel | | | Eurostat | panel |
|---|---:|---:|---|---|---:|---:|
| malta ($imp) | **+32.2** | +6.3 | | netherlands ($351) | +6.1 | +3.2 |
| czech-republic ($125) | +16.1 | +14.0 | | austria ($145) | +6.3 | +3.6 |
| norway ($199) | +15.9 | +0.6 | | belgium ($169) | +6.6 | −1.4 |
| ireland ($298) | +15.1 | +6.4 | | portugal ($165) | +8.0 | −1.9 |
| germany ($211) | +14.1 | −1.3 | | france ($217) | +8.0 | −0.4 |
| greece ($177) | +13.5 | +1.1 | | spain ($249) | +8.5 | +2.5 |
| latvia ($98) | +13.3 | +8.4 | | italy ($180) | +10.7 | +7.7 |

Every Eurostat number is 5–16pp above the panel's, because Eurostat counts **all** platforms and has no delisting
attrition, while the panel's vintage-matched counts subtract it. Levels do not matter for a mix term — only
differentials do — but three things disqualify B from the base: (i) the differentials are a *category* signal
(Booking, Vrbo and local platforms growing in Czechia, Latvia, Greece and Malta) and not Airbnb's own country mix,
which is the object the term claims to measure; (ii) the series stops at 1Q26, so B cannot see 2Q26 and its forward
differential window is **n 3** rather than n 4; (iii) Malta, whose Eurostat growth is +32% and whose price is
*imputed* at the EMEA median, is the single largest contributor to B's extra drag — a country where both legs are
proxies. B is reported as a bound, not a candidate. **The registered answer is variant A.**

## 8. What this does and does not settle

It settles the weight objection. The panel's EMEA share vector is demonstrably wrong — Ireland 6× overweight, France
half-weight, Italy 1.5× — and correcting it against the one independent measure of European platform nights moves
the 14-quarter sub-regional term by **0.02pp** and the 4Q26 ADR by **2 cents**. That is the useful result: the term's
*conclusion* does not rest on the scrape footprint.

It does not settle coverage. Eurostat is an EU/EEA frame; Airbnb's EMEA includes the entire Middle East and Africa,
which Eurostat cannot see at all and which the panel sees through one market each in Turkey and South Africa. The
kept-from-panel block is 12.3% of weight and is exactly the part of EMEA where the two sources agree by
construction, because there is nothing to disagree with. And ~12.5% of Eurostat's own EMEA platform nights sit in
countries with no panel market, still at zero weight. **A weight correction cannot fix a country the panel cannot
grow**, and the prereg's "what the panel cannot see" paragraph is untouched by this file.

---

## RESUME

`geomix_eurostat.py` runs end to end and exits 0; it reproduces the frozen `geomix.py` term and the previously
one-off forward roll to 2.2e-14 before changing anything, then rebuilds the EMEA row on Eurostat short-stay platform
nights. **Result: the sub-regional term is robust to its weakest joint.** 1Q23–2Q26 mean −0.453 → **−0.431pp**,
forward 4Q26 −0.147 → **−0.160pp**, 4Q26 ADR effect −$0.246 → **−$0.268**, i.e. the composition scenario moves
$172.79 → **$172.77**. H1 passes under all six share/growth/price combinations (mean −0.43 to −0.47pp), the fading
pattern survives (last four quarters −0.175 vs −0.152), and 2Q26's positive EMEA reading survives at +0.32pp
(+0.21 on the review-weighted price basis). **No base-case number changes and no decision was taken here.** Three
things are open. **(1)** Variant B (Eurostat's own country growth) is the only variant that moves the 4Q26 ADR
materially, to −$0.437, and it is a bound rather than a candidate — all platforms, no delisting attrition, stops at
1Q26, n 3 forward differentials, and its largest single contributor (Malta, +32% y/y) has an *imputed* price. Do not
quote it as our number. **(2)** The review-weighted price basis moves the term more than the Eurostat weights do
(−$0.032 vs −$0.022 at 4Q26) and it is systematically 10–36% above the median basis with a country-specific spread
(France ×1.36, Greece ×1.36, Netherlands ×1.00) — upgrade 4 should adjudicate which basis the term uses, because it
is the larger of the two effects tested here. **(3)** Malta and Switzerland are still price-imputed at the EMEA
median (1.9–2.2% of weight) and Switzerland's capture-store prices are broken ($0.20–$0.30 per night in all three
markets); that is a data defect in `market_price_levels_capture_2026.csv`, not a modelling choice, and it should be
fixed at source rather than floored. Nothing in `run.py`, `reconcile.py`, `od_layer.py` or the frozen lanes was
touched.
