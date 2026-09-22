# ADR line v2, mitigation C — raising n on the mix-term reconciliation: pooled regions, monthly EMEA

**22 September 2026.** [`adr_v2_upgrade3_reconciliation.md`](adr_v2_upgrade3_reconciliation.md) §B.3 found the
strongest single check the sub-regional mix term could have failed and did not: regressing the disclosed EMEA
ex-FX ADR less a panel-weighted accommodation CPI on our within-EMEA mix term gives a slope of **+1.09** where
the identity implies exactly **1.0**, r +0.48 — but on **n 7**, p 0.27. The weakness is n and only n. This file
raises n two ways that do not require a single new judgement call about the term itself, and registers the pass
lines before scoring.

Engine: `analysis/src/pitch_model_v2/adr_engine/reconcile_pooled.py` (new; imports nothing from and modifies
nothing in `reconcile.py`).
Outputs: `data/processed/pitch_model_v2/adr_engine/reconcile_pooled_cells.csv`,
`reconcile_pooled_cpi_proxy.csv`, `reconcile_pooled_regressions.csv`,
`reconcile_pooled_emea_monthly.csv`, `reconcile_pooled_emea_monthly_check.csv`.

```
cd ~/Citadel-ABNB && PYTHONPATH=analysis/src python3 -W ignore -m pitch_model_v2.adr_engine.reconcile_pooled
# exit 0; prints every table below and writes the five CSVs
```

Web fetches: zero. Nothing here is fitted: every window, weight, country set and exclusion below was written into
this section before the engine was run for the first time.

---

## 1. Registration — written before scoring

### 1.1 Leg (a): pooled across the four regions

**Object.** The same identity as upgrade 3 §B, applied to all four disclosed regions instead of EMEA alone:

```
disclosed regional ex-FX ADR y/y  =  within-region country mix  +  within-country price  +  size/LOS
```

so that, moving the measurable pieces to the left,

```
y_{r,t}  =  disclosed ex-FX_{r,t}  −  CPI proxy_{r,t}  −  global size_t  −  global LOS_t   =   a_r + b · mix_{r,t} + e_{r,t}
```

**The identity implies b = 1.** A point of within-region country mix must pass one-for-one into the disclosed
regional number. b is the parameter of interest; `a_r` are region fixed effects (they absorb any constant
level error in that region's CPI proxy, which is exactly the error we cannot measure).

**Inputs, frozen.**
- `mix_{r,t}` — `data/processed/pitch_model_v2/adr_engine/geomix_within_region.csv`, column `mix_pp`, the frozen
  `geomix.build_term` output. Untouched.
- `disclosed ex-FX_{r,t}` — `data/processed/adr/04_regional_quarterly_wide.csv`,
  `adr_yoy_exfx_{na,emea,latam,apac}_pct`.
- `global size_t`, `global LOS_t` — `unit_size_pp`, `los_mix_pp` from
  `data/processed/q3nowcast/H/adr_history_components.csv`. **These are global, not regional. No regional size or
  LOS is disclosed anywhere.** Using the global terms for every region is the same assumption upgrade 3 §B made
  for EMEA, and it is an assumption, not a measurement.
- `CPI proxy_{r,t}` — see 1.2.

**Two samples, both reported; the verdict is taken on the first.**
1. **Disclosed-only cells.** A cell counts as disclosed iff `basis_adr_{r}` is `disclosed-chained` **and** the
   ex-FX figure in `04_regional_quarterly_wide.csv` is a whole point **and** it equals the letter-sourced
   `{r}_adr_yoy_exfx_pct` in `data/processed/overnight/10_regional_panel_quarterly.csv`. That triple test is
   mechanical and it is what separates a number Airbnb said from a number we constructed. **This sample carries
   the verdict**, because on the other cells the left-hand side contains our own modelled FX.
2. **All chained cells.** Every cell with `basis_adr_{r} == 'disclosed-chained'`. Larger n, weaker object.

Both samples are additionally bounded below by the govdata price panel, which starts 1Q22, and by the H
decomposition, which starts 1Q23.

**Inference.** OLS on the stacked region-quarter panel with region dummies. **Primary SE: cluster-by-region
(CRV1, G = 4 clusters, t reference distribution with G − 1 = 3 degrees of freedom).** With four clusters that is
a punishing choice and it is the right one. Also reported, all of them, pass or fail: iid, HC1,
Newey–West HAC with 3 lags, and a **wild cluster bootstrap under the restricted null with Rademacher weights,
enumerated over all 2⁴ = 16 sign vectors** (so the smallest attainable bootstrap p is 1/16 = 0.0625 — stated in
advance so that a 0.0625 cannot later be read as a 0.06).

**PASS LINE (a).** The pooled test passes iff, on the **disclosed-only** sample, primary specification:
> **b ∈ [0.5, 1.5]** and **p ≤ 0.10** (cluster-by-region CRV1, two-sided, H0: b = 0).

Additionally reported, not part of the pass line: the two-sided p on **H0: b = 1** (is the scale consistent with
the identity?), the 90% and 95% CIs, r² (overall and within), n, and the number of regions contributing
within-region variation.

**Required variants, all reported whatever they show.**
- **No fixed effects** — single pooled intercept.
- **No CPI adjustment** — `y = disclosed ex-FX − size − LOS`, with and without FE.
- **Neither** — `y = disclosed ex-FX` on mix alone.
- **CPI spec 2** (1.2 below).
- Both samples for each.

### 1.2 The regional accommodation-CPI proxy

**Spec P1 (primary).** For each region-quarter, a **panel-share-weighted accommodation CPI**: each panel country's
own government accommodation price index (y/y %), weighted by that country's base-quarter share of the region's
panel stays (`share_base` in `geomix_country_contributions.csv` — the same s_c(t−4) vector the mix term itself
uses), renormalised over the countries that have a series. Coverage is reported per region-quarter. Series map,
fixed here:

| region | panel countries with a series | series |
|---|---|---|
| NAM | united-states, canada | BLS CPI lodging away from home (`bls_CUUR0000SEHB02`); StatCan CPI traveller accommodation |
| EMEA | 18 HICP countries + the UK | Eurostat HICP CP112 by country; ONS CPI 11.2 accommodation for the UK |
| LatAm | brazil | IBGE IPCA hospedagem 12-month rate |
| APAC | australia, new-zealand | ABS CPI holiday travel and accommodation (30033); Stats NZ CPI accommodation services |

**Turkey is excluded from EMEA**, exactly as registered in upgrade 3 §B.1 (27.9–58.0% y/y on hyperinflation at a
~1.9% panel weight). **Mexico, Argentina and Chile (LatAm) and Thailand, Taiwan, China, Singapore (APAC) have no
accommodation price series in the govdata store and are dropped from the weight**, so LatAm's proxy is Brazil
alone at ~30% coverage and APAC's is Australia + New Zealand at ~87%. Both numbers are stated in every table.
**Japan is in the govdata store but is not a country in the APAC panel**, so it carries no share and does not
enter P1.

**Spec P2 (secondary).** The four frozen headline series already used for the annual blend in `reconcile.py`
(`REGION_CPI`): NA = BLS lodging away from home, EMEA = euro-area HICP CP112, LatAm = IBGE IPCA hospedagem,
APAC = ABS 30033. One series per region, no weighting, no coverage question.

### 1.3 Leg (b): a monthly within-EMEA mix

**Object.** The same share-shift arithmetic as `geomix.build_term`, at monthly frequency with a 12-month lag:

```
mix(m) = Σ_c s_c(m−12) (1 + g_c(m)) P_c / [ (1 + g(m)) Σ_c s_c(m−12) P_c ] − 1,
g_c(m) = nights_c(m)/nights_c(m−12) − 1,   g(m) = Σ_c s_c(m−12) g_c(m)
```

**Inputs.** Shares and growth from `data/processed/eurostat_platform_nights_monthly.csv` (Eurostat tour_ce_omn12,
nights in short-stay accommodation booked through collaborative-economy platforms, monthly 2018-01 → 2026-03).
Country set = the **18 Eurostat geos that map to panel EMEA countries** in `geomix_eurostat.ISO_TO_COUNTRY`.
The United Kingdom, Turkey and South Africa are outside the Eurostat frame and have no monthly nights, so they
are **absent from the monthly object entirely** — this is the one structural difference from the quarterly
Eurostat variant, which keeps them at their Inside Airbnb panel share. Prices `P_c` =
`country_price_levels_usd.csv` (June-2026 capture, USD), Switzerland and Malta imputed at the EMEA median exactly
as in `geomix.py` / `geomix_eurostat.py`.

**PASS LINE (b1) — the monthly object must reproduce the quarterly one.** The quarter mean of the monthly mix,
compared with `geomix_eurostat_emea_mix.csv` (variant `share_src = eurostat`, `growth_src = eurostat`,
`price_basis = median` — the only published variant built from Eurostat shares *and* Eurostat growth):
> **mean absolute difference ≤ 0.15pp** over the overlapping quarters.

Because the country sets differ (UK/TR/ZA), a **like-for-like control** is also built and reported: the same
quarterly arithmetic on the same 18 Eurostat countries only. If b1 fails, the two comparisons together say
whether the failure is the monthly aggregation or the country set.

**PASS LINE (b2) — the monthly series must move with the disclosure.** Quarter-average the monthly mix, take its
12-month change, and correlate it with the 4-quarter change in the EMEA CPI gap
(`adr_yoy_exfx_emea_pct − hicp_CP112_EA_RCH_A`):
> **correlation > 0** (the identity's sign) on the overlapping quarters, reported on the disclosed-cell subset
and on all chained EMEA quarters, with n stated for each.

**What n does and does not buy here, stated in advance.** The monthly mix will have ~85 monthly observations and
its own 12-month change ~75. **That n belongs to the mix object, not to the test of it.** The target — Airbnb's
disclosed EMEA ex-FX ADR — is published quarterly and only quarterly, so the number of independent confrontations
with the company's own number does not rise at all in leg (b). Leg (b) can establish that the monthly series is a
faithful, higher-frequency rendering of the quarterly term (b1) and that it is not sign-inverted against the
disclosure (b2). **It cannot produce a significant slope, and no p-value computed on monthly observations against
a quarterly target will be reported as if it could.** Only leg (a) raises the number of real confrontations.

---

## 0. Verdict in six lines *(written after the run; §1 above was on disk before the engine was first executed)*

1. **Leg (a) meets its registered pass line and should not be believed as written.** Pooled over 23 disclosed
   regional prints with region fixed effects: **b = +1.127, cluster-by-region SE 0.331, p 0.042, 90% CI
   [0.35, 1.91], r² 0.828 (within 0.249), n 23.** The identity's **b = 1 cannot be rejected (p 0.73)**. n rose
   from 7 to 23 and the slope is still within 13% of its theoretical value.
2. **But it is one region's correlation, not four.** Region by region, the slope is **LatAm +1.375 (r 0.92, n 7)**,
   **EMEA −0.169 (r −0.04, n 9)**, **APAC −0.447 (r −0.10, n 6)**, NAM not identified (n 1). Drop Latin America
   and the pooled slope goes to **−0.302 (p 0.15), which rejects b = 1 at p 0.010.** Pooling did not turn one
   seven-point correlation into four confirmations; it replaced EMEA's seven points with Latin America's seven.
3. **And Latin America is the region with the worst price comparator.** Its accommodation-CPI proxy is Brazil's
   IPCA hospedagem alone, covering **24–33% of the region's panel stays**; Mexico, Argentina and Chile have no
   series in the store. What the regression fits there is the co-movement of Brazilian accommodation inflation
   with the Argentina/Mexico/Chile share shift, at n 7.
4. **Upgrade 3's EMEA result replicates exactly and then breaks.** On upgrade 3's own object and window the engine
   returns **b = +1.085, r² 0.234 (r +0.48), n 7** — the +1.09 / r 0.48 of §B.3, reproduced from an independent
   code path. Adding the **two further EMEA quarters that the mechanical disclosure test admits (3Q23 and 4Q23,
   both whole disclosed points)** takes the same EMEA regression to **b = −0.381, n 9.** The EMEA slope was
   window-dependent and neither this file nor upgrade 3 knew it.
5. **Leg (b) splits.** The monthly EMEA mix is a **faithful** rendering of the quarterly arithmetic — the quarter
   mean reproduces the same-country-set quarterly build to **MAE 0.100pp (n 29), pass line 0.15pp** — but it is
   **not** the published Eurostat variant (MAE 1.181pp, driven entirely by 2020-22: 1.919pp before 2023Q1 against
   0.272pp from 2023Q1 on). Pass line **b2 fails outright and with the wrong sign**: the 12-month change in the
   monthly mix correlates **−0.47** with the 4-quarter change in the EMEA CPI gap (n 9), **−0.26** on disclosed
   quarters (n 6).
6. **The scale question, answered.** b is consistent with 1 in the registered specification and in every pooled
   fixed-effect variant (point estimates 1.12–1.30, H0: b = 1 never rejected, p 0.37–0.77). It is **not** consistent
   with 1 without fixed effects (2.35–3.11, p 0.008–0.089) or without Latin America (−0.30, p 0.010). Across
   defensible specifications b spans **−0.38 to +3.11**, which is wider than the distance from 1. **The sub-regional
   term's scale is compatible with the identity and is not pinned down by any data Airbnb has published.**

---

## 2. Leg (a): what ran

### 2.1 The cell inventory — which ex-FX prints are actually the company's?

`basis_adr_{r} == 'disclosed-chained'` **and** a whole point **and** equal to the letter-sourced
`{r}_adr_yoy_exfx_pct` in `10_regional_panel_quarterly.csv`. All three, mechanically:

| quarter | APAC | EMEA | LatAm | NAM |
|---|---|---|---|---|
| 1Q23 | modl | chain | modl | modl |
| 2Q23 | modl | chain | modl | chain |
| 3Q23 | modl | **DISC** | modl | chain |
| 4Q23 | modl | **DISC** | modl | chain |
| 1Q24 | modl | chain | modl | chain |
| 2Q24 | modl | chain | modl | chain |
| 3Q24 | modl | chain | modl | chain |
| 4Q24 | **DISC** | **DISC** | **DISC** | chain |
| 1Q25 | **DISC** | **DISC** | **DISC** | **DISC** |
| 2Q25 | **DISC** | **DISC** | **DISC** | chain |
| 3Q25 | **DISC** | **DISC** | **DISC** | chain |
| 4Q25 | **DISC** | **DISC** | **DISC** | chain |
| 1Q26 | **DISC** | **DISC** | **DISC** | chain |
| 2Q26 | chain | **DISC** | **DISC** | chain |

**Disclosed whole points: n 23** (EMEA 9, LatAm 7, APAC 6, **NAM 1**). **Chained cells: n 41** (EMEA 14, NAM 13,
APAC 7, LatAm 7). Two facts worth stating plainly:

- **North America has exactly one disclosed ex-FX print in the whole sample (1Q25, +3%).** The brief's warning
  that NA ex-FX is constructed from 2Q25 is if anything generous: the 1Q24–3Q24 letter figures are *"ex-FX **and
  mix**"* (`"ADR +3% (flat ex-FX and mix)"`), a different object from ex-FX alone, and `04_regional_quarterly_wide`
  correctly builds its own ex-FX-only series for those quarters (2.78 / 4.09 / 3.33 against the letters' 0 / 1 / 1).
  Under region fixed effects a single-cell region contributes **nothing** to b; NAM is a fixed effect and no more.
- **EMEA 3Q23 and 4Q23 are disclosed whole points (+6% each) and upgrade 3 did not use them.** Upgrade 3's window
  was 4Q24–2Q26 (n 7) extended back to 1Q24 (n 10). The mechanical test admits 3Q23 and 4Q23 and excludes
  1Q24–3Q24, which is the reverse of upgrade 3's choice. §3.3 below is what that costs.

### 2.2 The panel, disclosed cells

`y = disclosed ex-FX − CPI proxy P1 − global size − global LOS`, all pp.

| region | quarter | disclosed ex-FX | our mix | CPI P1 | coverage | size | LOS | **y** | implied price | resid vs CPI |
|---|---|---|---|---|---|---|---|---|---|---|
| APAC | 4Q24 | 2.0 | −0.688 | 3.704 | 88.9% | 0.707 | 0.432 | −2.842 | 2.688 | −1.016 |
| APAC | 1Q25 | 3.0 | −0.402 | 0.757 | 89.4% | 0.669 | 0.279 | +1.295 | 3.402 | +2.645 |
| APAC | 2Q25 | 1.0 | −0.082 | 2.525 | 86.8% | 0.732 | 0.348 | −2.606 | 1.082 | −1.444 |
| APAC | 3Q25 | 3.0 | −0.149 | 3.935 | 86.5% | 0.748 | 0.308 | −1.991 | 3.149 | −0.786 |
| APAC | 4Q25 | 2.0 | −0.016 | 5.134 | 87.4% | 0.822 | 0.221 | −4.178 | 2.016 | −3.118 |
| APAC | 1Q26 | 2.0 | −1.075 | 3.367 | 88.2% | 0.945 | 0.300 | −2.612 | 3.075 | −0.292 |
| EMEA | 3Q23 | 6.0 | +0.189 | 9.887 | 96.2% | 0.410 | 0.302 | −4.599 | 5.811 | −4.077 |
| EMEA | 4Q23 | 6.0 | −0.149 | 8.215 | 94.3% | 0.291 | 0.364 | −2.870 | 6.149 | −2.066 |
| EMEA | 4Q24 | 6.0 | −0.617 | 4.910 | 93.9% | 0.707 | 0.432 | −0.048 | 6.617 | +1.707 |
| EMEA | 1Q25 | 4.0 | −0.201 | 4.171 | 92.1% | 0.669 | 0.279 | −1.119 | 4.201 | +0.030 |
| EMEA | 2Q25 | 3.0 | −0.509 | 3.601 | 95.4% | 0.732 | 0.348 | −1.681 | 3.509 | −0.092 |
| EMEA | 3Q25 | 4.0 | +0.172 | 2.612 | 95.4% | 0.748 | 0.308 | +0.333 | 3.828 | +1.216 |
| EMEA | 4Q25 | 4.0 | −0.063 | 2.879 | 93.6% | 0.822 | 0.221 | +0.078 | 4.063 | +1.184 |
| EMEA | 1Q26 | 4.0 | −0.284 | 4.327 | 91.9% | 0.945 | 0.300 | −1.572 | 4.284 | −0.043 |
| EMEA | 2Q26 | 5.0 | +0.431 | 4.016 | 95.0% | 0.700 | 0.300 | −0.017 | 4.569 | +0.552 |
| LatAm | 4Q24 | 4.0 | +0.498 | 8.297 | 25.4% | 0.707 | 0.432 | −5.435 | 3.502 | −4.795 |
| LatAm | 1Q25 | 2.0 | −2.669 | 10.863 | 27.2% | 0.669 | 0.279 | −9.811 | 4.669 | −6.194 |
| LatAm | 2Q25 | 2.0 | −2.542 | 10.870 | 25.0% | 0.732 | 0.348 | −9.951 | 4.542 | −6.328 |
| LatAm | 3Q25 | 3.0 | −0.244 | 9.160 | 25.7% | 0.748 | 0.308 | −7.216 | 3.244 | −5.916 |
| LatAm | 4Q25 | 3.0 | −0.677 | 10.770 | 24.4% | 0.822 | 0.221 | −8.813 | 3.677 | −7.093 |
| LatAm | 1Q26 | 3.0 | −0.472 | 7.883 | 32.9% | 0.945 | 0.300 | −6.128 | 3.472 | −4.412 |
| LatAm | 2Q26 | 2.0 | +0.443 | 6.650 | 30.0% | 0.700 | 0.300 | −5.650 | 1.557 | −5.093 |
| NAM | 1Q25 | 3.0 | −0.074 | −0.389 | 100.0% | 0.669 | 0.279 | +2.442 | 3.074 | +3.464 |

**CPI proxy P1 coverage** (share of the region's panel stays with a government accommodation series):
NAM 100.0%, EMEA 91.9–96.2 (mean 94.2), APAC 86.5–97.4 (mean 90.3), **LatAm 22.1–32.9 (mean 26.6)**.

The EMEA rows reproduce upgrade 3 §B.2 to the third decimal (4Q24 panel CPI 4.910, implied price 6.617; 1Q25
4.171 / 4.201; …) from an independent code path, which is the cheapest available check that the two files are
computing the same object.

### 2.3 The regressions

`y = a_r + b·mix + e`. The identity implies b = 1. Pass line: b ∈ [0.5, 1.5] and p ≤ 0.10, cluster-by-region.

| sample | spec | n | **b** | SE (cl-region) | **p (b=0)** | p (b=1) | 90% CI | r² | within r² | **PASS** |
|---|---|---|---|---|---|---|---|---|---|---|
| **disclosed** | **primary: FE + CPI P1 + size/LOS** | **23** | **+1.127** | **0.331** | **0.042** | **0.727** | **[0.35, 1.91]** | **0.828** | **0.249** | **PASS** |
| chained | primary | 41 | +2.093 | 1.136 | 0.163 | 0.407 | [−0.58, 4.77] | 0.599 | 0.156 | fail |
| disclosed | no FE | 23 | +2.345 | 0.260 | 0.003 | 0.014 | [1.73, 2.96] | 0.288 | — | fail |
| chained | no FE | 41 | +2.891 | 0.761 | 0.032 | 0.089 | [1.10, 4.68] | 0.166 | — | fail |
| disclosed | no CPI adjustment, FE | 23 | +0.346 | 0.046 | 0.005 | 0.001 | [0.24, 0.46] | 0.642 | 0.078 | fail (band) |
| chained | no CPI adjustment, FE | 41 | +0.896 | 0.628 | 0.249 | 0.879 | [−0.58, 2.38] | 0.377 | 0.063 | fail (p) |
| disclosed | neither (raw ex-FX on mix) | 23 | +0.656 | 0.293 | 0.111 | 0.325 | [−0.04, 1.35] | 0.139 | — | fail (p) |
| chained | neither | 41 | +1.465 | 0.942 | 0.218 | 0.655 | [−0.75, 3.68] | 0.131 | — | fail (p) |
| disclosed | CPI P2 headline, FE | 23 | +1.297 | 0.120 | 0.002 | 0.089 | [1.02, 1.58] | 0.925 | 0.510 | PASS |
| chained | CPI P2 headline, FE | 41 | +2.203 | 1.126 | 0.145 | 0.364 | [−0.45, 4.85] | 0.647 | 0.198 | fail |
| disclosed | CPI P2, no FE | 23 | +2.525 | 0.240 | 0.002 | 0.008 | [1.96, 3.09] | 0.347 | — | fail |
| chained | CPI P2, no FE | 41 | +3.114 | 0.675 | 0.019 | 0.052 | [1.53, 4.70] | 0.204 | — | fail |
| disclosed | FE + CPI P1, size/LOS **not** removed | 23 | +1.120 | 0.374 | 0.058 | 0.769 | [0.24, 2.00] | 0.812 | 0.231 | PASS |
| chained | same | 41 | +2.120 | 1.170 | 0.168 | 0.409 | [−0.63, 4.87] | 0.574 | 0.148 | fail |

**Robustness on the primary spec, disclosed sample**

| variant | n | b | SE | p(b=0) | p(b=1) | PASS |
|---|---|---|---|---|---|---|
| drop NAM | 22 | +1.127 | 0.343 | 0.081 | 0.747 | PASS |
| drop EMEA | 14 | +1.235 | 0.255 | 0.040 | 0.455 | PASS |
| **drop LatAm** | **16** | **−0.302** | **0.134** | **0.153** | **0.010** | **fail** |
| drop APAC | 17 | +1.247 | 0.225 | 0.031 | 0.387 | PASS |
| 4Q24+ only (common window) | 21 | +1.233 | 0.221 | 0.011 | 0.369 | PASS |
| EMEA alone, primary y | 9 | −0.169 | n/a (G = 1) | — | — | — |
| EMEA alone, upgrade-3 y, all 9 disclosed | 9 | **−0.381** | n/a | — | — | — |
| **EMEA alone, upgrade-3 y and window (replication)** | **7** | **+1.085** | n/a | — | — | — |

**Where the slope comes from** (within-region OLS of the primary y on mix, disclosed cells):

| region | n | mix range | mix sd | y sd | **b (region)** | **r** | CPI coverage |
|---|---|---|---|---|---|---|---|
| NAM | 1 | — | — | — | — | — | 100.0% |
| EMEA | 9 | −0.617 … +0.431 | 0.339 | 1.634 | **−0.169** | −0.035 | 94.2% |
| **LatAm** | **7** | **−2.669 … +0.498** | **1.303** | 1.944 | **+1.375** | **+0.922** | **27.3%** |
| APAC | 6 | −1.075 … −0.016 | 0.412 | 1.839 | **−0.447** | −0.100 | 87.9% |

**Influence.** Leave-one-**cell**-out (23 refits of the primary spec): b ranges **+1.025 to +1.233**, median
+1.127; only 2 of 23 removals break the pass line, both on p (0.101, 0.112) and both LatAm cells. The slope is
therefore **robust to any single quarter and fragile to one region.** That is the whole finding: the four regions
do not agree, and the pooled number is an average that happens to sit near 1 because the one region with real
regressor variation happens to sit near 1.

**Every SE flavour** (p on H0: b = 0), primary spec, disclosed sample: iid 0.025, HC1 0.000, Newey–West(3) within
region 0.000, **cluster-by-region 0.042**, cluster-by-quarter 0.000. **The registered wild cluster bootstrap
returns p = 1.000** — all 16 Rademacher sign vectors produce a |t*| at least as large as the observed one. With
G = 4 clusters and four fixed effects the restricted residuals carry almost all the cluster-level variation, and
the bootstrap is uninformative rather than contradictory. It was registered, it is reported, and **no weight is
placed on it in either direction**; on the specifications without fixed effects it returns 0.125, the second
smallest attainable value.

---

## 3. Leg (b): the monthly EMEA mix

### 3.1 The object

87 monthly observations, **2019-01 to 2026-03**, 18 Eurostat countries, 12-month share shift, June-2026 USD price
levels, 2.55% of base share carrying an imputed (EMEA-median) price. mix mean −0.023pp, sd 1.560pp, range
−4.230 to +4.762pp. 75 twelve-month changes.

### 3.2 Pass line b1 — reproduction

| comparison | n | **MAE** | mean | max abs | line 0.15pp |
|---|---|---|---|---|---|
| vs the published quarterly Eurostat variant (`eurostat` shares / `eurostat` growth / median price) | 29 | **1.181pp** | −0.015 | 4.996 | **FAIL** |
| vs the like-for-like control (same 18 countries, quarterly 4-lag arithmetic) | 29 | **0.100pp** | +0.002 | 0.486 | **PASS** |
| *(diagnostic, not registered)* vs the published variant, 2023Q1 on | 13 | 0.272pp | +0.084 | 0.816 | — |
| *(diagnostic, not registered)* vs the published variant, before 2023Q1 | 16 | 1.919pp | −0.096 | 4.996 | — |

**Read it as the two comparisons together say it.** The monthly aggregation itself is clean: quarter-averaging
the monthly term reproduces the *same data on the same 18 countries* at quarterly frequency to **0.100pp MAE**,
inside the registered line. What fails is the comparison with the *published* Eurostat variant, and the failure is
**not the monthly frequency** — it is (i) the country set, since the published variant keeps the UK, Turkey and
South Africa at their Inside Airbnb panel shares and the monthly object cannot see them at all, and (ii) 2020–22,
where the two growth vectors diverge violently (max |diff| 4.996pp in 1Q22, 3.940pp in 1Q21). From 2023Q1 the
same comparison is 0.272pp MAE and every quarter from 3Q23 on is within 0.60pp. **Registered line b1: FAIL as
written; the object is nonetheless a faithful monthly rendering of its own quarterly arithmetic.**

One further diagnostic, and it matters for the whole file: the monthly-derived quarterly mix and the
**panel-derived EMEA mix that leg (a) actually uses** agree only in magnitude, not in sign —
**MAE 0.405pp, mean +0.026pp, r = −0.295 over the 13 overlapping quarters.** The Eurostat-weighted EMEA mix and
the Inside-Airbnb-weighted EMEA mix are, quarter by quarter, **different series**. Upgrade 1 showed the two move
the *sub-regional term* by only 0.02pp — true, and consistent with this, because the EMEA piece is a small
fraction of a GBV-weighted four-region sum. At the level at which upgrade 3 and this file test the term, they
are not interchangeable.

### 3.3 Pass line b2 — does the monthly series move with the disclosure?

| cut | object | n | **r** | slope | line: r > 0 |
|---|---|---|---|---|---|
| all chained EMEA quarters | Δ12 monthly mix vs Δ4 CPI gap | 9 | **−0.474** | −1.501 | **FAIL** |
| disclosed EMEA quarters | Δ12 monthly mix vs Δ4 CPI gap | 6 | **−0.263** | −0.810 | **FAIL** |
| all chained EMEA quarters | levels: mix vs CPI gap | 13 | −0.213 | −0.984 | **FAIL** |
| disclosed EMEA quarters | levels: mix vs CPI gap | 8 | −0.009 | −0.064 | **FAIL** |

**Four cuts, four wrong signs.** The levels row on disclosed quarters is the direct analogue of upgrade 3 §B.3's
+1.09: **built on the Eurostat-monthly mix instead of the panel mix, the same regression gives −0.06 with r
−0.009 — nothing at all.** Together with §3.2's r = −0.295 between the two mix series, that says the +1.09 is a
property of the **Inside Airbnb panel's** EMEA share vector, not of "within-EMEA country mix" as a concept. A
second, independent weighting of the same idea does not reproduce it.

### 3.4 What n bought, stated as registered

The monthly object has 87 observations and 75 twelve-month changes. **None of them is a new confrontation with
Airbnb's disclosure**, which is quarterly and which the monthly file can reach only 13 times (and only 8 of those
are disclosed whole points). The registration said this in advance and it held: **leg (b) raised the resolution
of the mix series and raised the number of real tests by zero.** Its value is diagnostic, and the diagnosis is
negative — see §3.3.

---

## 4. What this does to the line

**The pooled test's implication for the sub-regional term's scale.** b is **consistent with 1**: the registered
specification gives +1.127 with a 90% interval of [0.35, 1.91] and cannot reject b = 1 at p 0.73, and every pooled
fixed-effect variant (CPI P1, CPI P2, with and without the size/LOS proxy, dropping NAM, EMEA or APAC, and on the
common 4Q24+ window) lands between **+1.12 and +1.30** with b = 1 never rejected. That is the strongest form in
which the claim can honestly be made, and it is a real strengthening of upgrade 3: the same statement now rests on
**23 disclosed prints across three identifying regions rather than 7 in one**, and it clears a pre-registered
significance line at p 0.042 instead of failing one at p 0.27.

**And the same exercise names the price of that sentence.** Remove the fixed effects and b is 2.3–3.1; remove
Latin America and b is −0.30 and the identity's 1.0 is *rejected*; use the chained cells and b is 2.09 with p
0.163. Region by region the four slopes are +1.38, −0.17, −0.45 and undefined. **The term is compatible with
passing one-for-one into the disclosed number and Airbnb has not published enough to establish that it does.**
Anyone who quotes +1.13 without quoting −0.30 is quoting a specification, not a finding.

**One sentence on thesis sentence 6.** Yes, it changes: the EMEA clause — *"regresses on our within-region mix
with a slope of 1.09 where the identity implies 1.0 (r 0.48, n 7, p 0.27)"* — replicates exactly (+1.085) but is
**window-dependent** (adding the two further disclosed EMEA quarters, 3Q23 and 4Q23, takes it to −0.381) and
**weighting-dependent** (rebuilt on Eurostat monthly shares the same regression gives −0.06), so it should be
replaced by the pooled statement with its own caveat attached: *"pooled across the four regions on the 23
quarters Airbnb has actually disclosed a constant-currency regional ADR, the same regression gives a slope of
1.13 (cluster-by-region p 0.04) and cannot reject the identity's 1.0 — but the slope is carried by Latin America
alone, and without it the pooled slope is −0.30, so the scale is compatible with the identity and not established
by it."* That is longer and weaker than the sentence it replaces, and it is what the data support.

**Nothing in the base case changes.** DEC-0016's disposition is untouched: H2 failed, the sub-regional term stays
an attribution row and a forward scenario, and this file gives no reason to promote it. What it changes is the
**evidence sentence**, and it changes it in both directions at once — a pre-registered pass where upgrade 3 had a
p 0.27, and a named single point of failure where upgrade 3 had an unexamined window.

---

## RESUME

`reconcile_pooled.py` runs both legs end to end and **exits 0**; the five CSVs hold every number above. Registered
before scoring in §1; §0 and §§2–4 were written after. No existing file was modified and no decision was taken
here.

**Registered lines, scored.** (a) **PASS** on the disclosed sample, primary specification: b = +1.127, cluster-by-
region p 0.042, b ∈ [0.5, 1.5]. **FAIL** on the all-chained sample (b 2.093, p 0.163). (b1) **FAIL** against the
published quarterly Eurostat variant (MAE 1.181pp) and **PASS** against the like-for-like same-country control
(0.100pp). (b2) **FAIL**, wrong sign, on all four cuts.

**Five things are open, in the order they should be closed.**
**(1)** The pooled slope is Latin America's slope (+1.375, r 0.92, n 7) and Latin America's accommodation-CPI
proxy is Brazil alone at ~27% of the region's panel stays. **A Mexican (INEGI INPC hospedaje) and Chilean (INE)
accommodation series would either break that correlation or make it the strongest evidence in the line, and the
whole pooled result turns on which.** Nothing else in this file is worth more than that one data pull.
**(2)** EMEA 3Q23 and 4Q23 are disclosed whole points that upgrade 3's window excluded and this file's mechanical
test admits, and including them flips the EMEA slope from +1.09 to −0.38. **Someone has to adjudicate the window
before either number is quoted** — the two quarters are real disclosures and the reason to drop them cannot be
that they spoil the answer.
**(3)** The Eurostat-weighted and panel-weighted EMEA mix series correlate **r −0.295** quarter by quarter. Upgrade
1 established that this does not move the *sub-regional term*; it does move every test of the *EMEA* term, and
§B.3's +1.09 does not survive the reweighting. The term should not be described as "corroborated in EMEA" until
that is resolved.
**(4)** North America has **one** disclosed ex-FX print in the entire sample (1Q25). Under fixed effects it is a
constant and contributes nothing. Any future claim that this reconciliation is "four-region" is wrong: it is
three-region at best, and one-region in practice.
**(5)** The wild cluster bootstrap is uninformative at G = 4 with fixed effects (p 1.000 on the primary spec, the
second-smallest attainable value of 0.125 elsewhere). If inference on this panel is going to be pressed further,
it needs either more disclosed quarters or a different device (randomisation inference over the mix series, say),
not a smaller p from the same 16 draws.

**Do not read the cluster-by-quarter p-values (0.000–0.045) as the answer.** They cluster on the dimension the
common global size/LOS proxy varies over and leave the region dimension unclustered, which is exactly backwards
for a panel whose errors are regional; they are in the CSV for completeness and the registered primary is the
cluster-by-region column.
