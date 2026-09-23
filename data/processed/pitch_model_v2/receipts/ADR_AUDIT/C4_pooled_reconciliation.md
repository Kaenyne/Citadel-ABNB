# C4 — "the reconciliation rests on one region": adversarial audit receipt

**22 September 2026.** Audit of `docs/pitch-model-v2/lines/adr_v2_mitigation_C_pooled_reconciliation.md` and the
pooled-reconciliation sentence in `final_adr.md` §4.5 / §9. Worktree `C:\Users\krish\citadel-abnb-adraudit`
(detached HEAD 84c430b7, branch theo/pitch-model-v2). Nothing under the worktree was modified; everything new is in
this folder. `pitch_model_v2.adr_engine.run` was NOT executed.

## 0. Pre-registration (written before any script was run)

**What counts as "the slope is carried by Latin America".** The pooled slope is *carried by Latin America* if,
on the primary specification (disclosed sample, region FE, CPI P1, size/LOS removed), **either** (i) replacing the
Latin-American comparator with a neutral one (zero inflation, or the quarter's median of the other regions'
comparators) moves the pooled slope outside the registered band [0.5, 1.5], **or** (ii) the fully-enumerated Webb
six-point wild cluster bootstrap p-value for H0: b = 0 exceeds 0.10 while the leave-LatAm-out slope stays below
0.5 — i.e. the only region with a positive within-region slope is also the one whose comparator is a single-country
proxy, and the pooled significance does not survive a bootstrap that is valid at G = 4. If neither (i) nor (ii)
holds, the "one region" objection is weaker than the note says and the claim should be *strengthened*, not
downgraded.

**Also pre-stated.** Leave-one-quarter-out inside Latin America is diagnostic only: with n 7 in the region, any
single quarter moving the LatAm slope by more than 0.5 will be reported as "one or two prints carry it", but is not
by itself a pass/fail line.

**Blend weights for the broadened LatAm comparator (if Mexico and/or Chile series are obtained).** Same rule as
spec P1: quarter-specific `share_base` from `geomix_country_contributions.csv` (the s_c(t−4) vector the mix term
uses), renormalised over the LatAm countries that have a series. On the seven disclosed LatAm quarters the raw
share_base averages are approximately brazil 0.27, mexico 0.33, chile 0.14, argentina 0.23, belize 0.02; so with all
three series the renormalised weights are approximately **brazil 0.37 / mexico 0.44 / chile 0.19** and coverage rises
from ~27% to ~74%; with Mexico only, brazil 0.45 / mexico 0.55 (~60% coverage); with Chile only, brazil 0.66 / chile
0.34 (~41%). Quarterly value = mean of the monthly 12-month rates in the quarter (the govdata `rate_M` rule used
for IBGE). The cross-check against `stays_yoy_by_country_vmatch.csv` (complete quarters only, ≤ 2Q26) is reported
but does not set the weights.

**Web-fetch budget.** At most three fetches (curl/WebFetch), logged below with URL, UTC time, HTTP status, bytes.
No credentials, no registration, nothing touching airbnb.com.

---

## 1. What ran (exact commands, from the worktree root)

```
py -3.13 data/processed/pitch_model_v2/receipts/ADR_AUDIT/C4_audit.py     # exit 0; writes C4_*.csv, C4_audit_output.txt
py -3.13 data/processed/pitch_model_v2/receipts/ADR_AUDIT/C4_bounds.py    # exit 0; writes C4_brazil_weight_curve.csv,
                                                                          #   C4_required_bX.csv, C4_brazil_mechanism.csv, C4_bounds_output.txt
```

Both scripts read the frozen engine output `data/processed/pitch_model_v2/adr_engine/reconcile_pooled_cells.csv`
(23 disclosed cells) and re-implement OLS / CRV1 / wild-cluster independently of `reconcile_pooled.py`; the engine
was not re-run. `C4_bounds.py` additionally reads the IBGE monthly raw file from the main tree
(`C:\Users\krish\citadel-abnb\data\processed\govdata\P\raw\ibge_ipca_hospedagem_monthly.csv`) and
`stays_yoy_by_country_vmatch.csv` (filtered to complete quarters at or before 2Q26; the file's only rows past 2Q26
are 3Q26 partials for italy and turkey, none in LatAm).

## 2. Reproduction (task 1)

Every number in the note reproduces to machine precision from an independent code path.

| stat | note | audit | diff |
|---|---:|---:|---:|
| b | 1.127000 | 1.127000 | 0 |
| SE cluster-by-region (CRV1) | 0.330774 | 0.330774 | 0 |
| p (b = 0), t(3) | 0.042238 | 0.042238 | 0 |
| p (b = 1), t(3) | 0.726613 | 0.726613 | 0 |
| 90% CI | 0.348570 – 1.905431 | same | 0 |
| n | 23 | 23 | |
| p iid | 0.025059 | 0.025059 | 0 |
| p HC1 | 0.000063 | 0.000063 | 0 |

| leave-one-region-out | n | b (audit) | b (note) | p(b=0) | p(b=1) |
|---|---:|---:|---:|---:|---:|
| drop NAM | 22 | 1.127 | 1.127 | 0.081 | 0.747 |
| drop EMEA | 14 | 1.235 | 1.235 | 0.040 | 0.455 |
| **drop LatAm** | 16 | **−0.302** | −0.302 | 0.153 | **0.010** |
| drop APAC | 17 | 1.247 | 1.247 | 0.031 | 0.387 |

Within-region slopes of the primary y on mix: EMEA −0.169 (r −0.04, n 9), **LatAm +1.375 (r +0.92, n 7)**, APAC
−0.447 (r −0.10, n 6), NAM n 1. All as stated.

## 3. Inference with four clusters (task 2a, 2b)

Fully enumerated wild cluster bootstrap-t, restricted null (WCR) and unrestricted (WCU), Rademacher (2^4 = 16) and
Webb six-point (6^4 = 1296). Primary spec, disclosed sample. File: `C4_wildboot.csv`.

| spec | H0 | weights | WCR p | WCU p | n draws | min attainable p |
|---|---|---|---:|---:|---:|---:|
| primary (FE, CPI P1) | b = 0 | Rademacher | **1.000** | 0.875 | 16 | 0.0625 |
| primary | b = 0 | **Webb-6** | **0.889** | 0.815 | 1296 | 0.0008 |
| primary | b = 1 | Rademacher | 1.000 | 0.875 | 16 | |
| primary | b = 1 | **Webb-6** | **0.898** | 0.759 | 1296 | |
| drop LatAm (G = 3) | b = 0 | Webb-6 | 0.333 | 0.778 | 216 | 0.0046 |
| drop LatAm (G = 3) | b = 1 | Webb-6 | 0.278 | 0.806 | 216 | |
| no FE | b = 0 | Webb-6 | 0.065 | 0.076 | 1296 | |
| no FE | b = 1 | Webb-6 | 0.096 | 0.096 | 1296 | |
| CPI P2, FE | b = 0 | Webb-6 | 0.130 | 0.685 | 1296 | |
| CPI P2, FE | b = 1 | Webb-6 | 0.639 | 0.602 | 1296 | |

**Claimed p 0.042 vs bootstrap: 0.889 (Webb WCR), 0.815 (Webb WCU).** Webb weights do not rescue the test: with
G = 4 and four region dummies the bootstrap is uninformative, and the reason is visible in the 16 Rademacher
draws printed in `C4_audit_output.txt`: the observed sign vector is the *least* extreme of the 16 (|t*| ranges
3.41–5.72, all at or above t_obs 3.41). Under the restricted null the LatAm cluster's residuals carry the whole
within-LatAm slope, and flipping the sign of EMEA's or APAC's residuals (whose within slopes are negative) *raises*
the pooled |t*|. So the cluster-robust p 0.042 is a t(3) on a CRV1 SE that is estimated from essentially one
cluster with regressor variation; the honest statement is that **with four clusters the pooled slope has no valid
cluster-level p-value at all.** Plain OLS p 0.025 and HC1 p 0.00006 assume independent cells, which the note itself
rejects (regional errors); they are reported, not believed.

**Randomisation inference (added, not in the note).** Permuting the mix series within each region (the regressor
is ours; the target and the comparator are not touched), 20,000 draws: p(|b*| at or above 1.127) = **0.035**,
one-sided 0.019. Holding LatAm's mix fixed and shuffling only EMEA/APAC, b* stays in [+0.57, +1.70] (mean +1.17):
the other two regions cannot move the pooled slope out of the band in either direction. LatAm alone, exact 7! =
5040 permutations: p(|b*| at or above 1.375) = **0.0014**. So there *is* a real within-LatAm association between
the mix term and y at n 7. The question §4 answers is what y is made of.

## 4. Which Latin-American prints carry it (task 2c)

Leave-one-quarter-out inside LatAm (pooled primary refit each time), file `C4_latam_loqo.csv`:

| dropped LatAm quarter | pooled b | p(b=0) | LatAm b (n 6) | LatAm r |
|---|---:|---:|---:|---:|
| 4Q24 | 1.025 | 0.070 | 1.312 | 0.90 |
| 1Q25 | 1.088 | 0.112 | 1.488 | 0.90 |
| 2Q25 | 1.025 | 0.101 | 1.376 | 0.89 |
| 3Q25 | 1.143 | 0.046 | 1.403 | 0.93 |
| 4Q25 | 1.145 | 0.043 | 1.397 | 0.97 |
| 1Q26 | 1.092 | 0.045 | 1.337 | 0.94 |
| 2Q26 | 1.053 | 0.066 | 1.340 | 0.90 |

No single quarter carries it. Leave-two-out (21 pairs, `C4_latam_l2o.csv`): pooled b ranges **0.642 (drop
1Q25+2Q25, p 0.53)** to 1.177; 0 of 21 leave the band. The pair that matters is **1Q25+2Q25**, the two quarters
where the LatAm mix term is −2.67 / −2.54pp against −0.7 to +0.5 elsewhere: they are the regressor's whole range,
and they are also the two quarters where Brazil's IPCA hospedagem peaked at 10.9%.

**Decomposition of the LatAm slope (the finding).** y = ex-FX − CPI − size − LOS, so the slope of y on mix is the
sum of the component slopes (`C4_latam_decomposition.csv`):

| component of y | slope on mix (n 7) | r | contribution to b_LatAm = 1.375 |
|---|---:|---:|---:|
| disclosed ex-FX ADR | +0.358 | +0.62 | **+0.358 (26%)** |
| Brazil IPCA hospedagem (entered with −) | −1.042 | **−0.81** | **+1.042 (76%)** |
| global size (−) | +0.013 | +0.19 | −0.013 |
| global LOS (−) | +0.012 | +0.24 | −0.012 |

**Three-quarters of the Latin-American slope, and therefore of the pooled 1.127, is the Brazil comparator
moving inversely with the mix term. Airbnb's own disclosed number contributes a slope of 0.36.**

## 5. The slope with a neutral Latin-American comparator (task 2d)

Pre-registered criterion (i). File `C4_neutral_comparator.csv`; LORO under each variant in
`C4_neutral_comparator_loro.csv`.

| LatAm comparator | pooled b | SE | p(b=0) | p(b=1) | 90% CI | Webb p(b=0) | LatAm b (r) | in band |
|---|---:|---:|---:|---:|---|---:|---|---|
| as published (Brazil, ~27% coverage) | 1.127 | 0.331 | 0.042 | 0.727 | 0.35 to 1.91 | 0.889 | 1.375 (0.92) | yes |
| **zero inflation** | **0.239** | 0.126 | 0.155 | **0.009** | −0.06 to 0.54 | 0.870 | 0.333 (0.62) | **no** |
| same-quarter median of other regions | **−0.353** | 0.022 | 0.001 | 0.000 | −0.41 to −0.30 | 0.074 | −0.362 (−0.46) | **no** |
| same-quarter mean of other regions | −0.287 | 0.019 | 0.001 | 0.000 | −0.33 to −0.24 | 0.102 | −0.284 (−0.32) | no |
| Brazil's own 7-quarter mean (constant) | 0.239 | 0.126 | 0.155 | 0.009 | −0.06 to 0.54 | 0.870 | 0.333 (0.62) | no |

With any neutral comparator the pooled slope leaves the band, and **b = 1 is rejected (p 0.009 with a zero
comparator, p < 0.001 with the other regions' median)**. Under the neutral comparators all four leave-one-region-out
slopes agree (0.24 to 0.29, or −0.28 to −0.37): the regions stop disagreeing once Brazil's inflation series is
taken out of Latin America's y. **Pre-registered criterion (i) is met: the slope is carried by Latin America, and
more precisely by the Brazil IPCA hospedagem series.**

## 6. Broadening the comparator: Mexico and Chile (task 3)

### 6.1 Fetch log (three fetches, the registered maximum; five WebSearch queries, which are not fetches, listed for completeness)

| # | tool | URL | UTC | status | bytes | result |
|---|---|---|---|---|---:|---|
| 1 | WebFetch | `https://www.ine.gob.cl/estadisticas/economia/indices-de-precio-e-inflacion/indice-de-precios-al-consumidor` | 2026-09-22 approx. 19:33 | page returned (tool does not expose the code) | n/r | Only PDF bulletins (Jun–Aug 2026) and the calculator; the "cuadros estadísticos" file list is behind an interactive category selector not present in the static HTML. No xlsx URL obtainable. |
| 2 | curl | `https://stat.ine.cl/restsdmx/sdmx.ashx/GetDataStructure/ALL` | 2026-09-22T19:35:38Z (returned 20:03:09Z) | **200** | **32,456** | Saved as `stat_ine_cl_datastructure_all.xml`. **INE.Stat serves no price-index dataset at all**: the ~80 KeyFamilies are labour (ENE/ESI), wages (IR), energy, environment, agriculture. IPC is not on the SDMX endpoint. |
| 3 | WebFetch | `https://www.inegi.org.mx/programas/inpc/2018a/` | 2026-09-22 approx. 20:06 | page returned | n/r | Page is JS-rendered; the static HTML carries only the title. No tabulado/open-data URL obtainable. |

WebSearch queries (no data fetched): (1) INE Chile IPC "servicios de alojamiento" serie histórica xlsx base 2023;
(2) INEGI INPC "hoteles" genérico serie histórica descarga; (3) site:ine.gob.cl "series históricas" xlsx "base
anual 2023"; (4) inegi.org.mx/contenidos/programas/inpc/2018/datosabiertos; (5) stat.ine.cl restsdmx IPC 2023.
Search (3) surfaced one concrete file, not fetched because it cannot serve: INE Chile
`.../serie-histórica-empalmada-divisiones-ipc-diciembre-2009-a-diciembre-2023-xls.xlsx`, division level only
(division 11 "restaurantes y hoteles", not class 11.2 accommodation) and ending December 2023, before every
disclosed LatAm quarter.

**No Mexico or Chile series was obtained.** Nothing was registered, no token was used, nothing touched airbnb.com.

### 6.2 What a human needs to do

- **Mexico.** Register (free) for an INEGI API token at `https://www.inegi.org.mx/app/desarrolladores/` (or a Banxico
  SIE token at `https://www.banxico.org.mx/SieAPIRest/service/v1/token`) and pull the INPC genérico *hoteles*
  (INEGI BIE indicator 628229 per `P_candidates.csv`, or Banxico series SP30578), monthly index 2023-10 to 2026-06,
  then compute the 12-month rate and quarter-average it. Alternatively, in a browser, open
  `https://inegi.org.mx/app/indicesdeprecios/Estructura.aspx?idEstructura=112001700030` (INPC Nacional mensual),
  expand *Restaurantes y hoteles* then *Hoteles*, and use the page's export (an interactive ASP.NET control; a
  fetcher cannot drive it).
- **Chile.** On the INE IPC page above, use the "Seleccione una categoría para mostrar archivos" selector, then
  *Cuadros estadísticos*, *Base anual 2023 = 100*, *series históricas*; the class-level file (división 11, grupo
  11.2 *servicios de alojamiento*) is an xlsx behind that selector. `stat.ine.cl` will not help (verified, fetch 2).
- Then run the blend in `C4_bounds.py` with the real series in place of X (the code path is `pooled_for_bx`, with
  a real vector instead of the synthetic one), weights **0.368 / 0.440 / 0.192** as pre-stated.

### 6.3 What the broadened comparator can and cannot do, bounded without the series

Pre-stated blend weights (§0) cross-checked: `share_base` means brazil 0.273 / mexico 0.326 / chile 0.143
(vmatch current-quarter shares 0.285 / 0.316 / 0.152, same picture). Renormalised: **BR 0.368 / MX 0.440 / CL
0.192, coverage 74.1%**; BR+MX only 0.455/0.545 (59.9%); BR+CL only 0.657/0.343 (41.5%).

Because y is linear in the comparator, the pooled slope under a blend is exactly determined by Brazil's weight and
by the unobserved slope b_X of the Mexico+Chile component on the LatAm mix term. `C4_brazil_weight_curve.csv`
traces the pooled slope with X neutral (no co-movement with the mix term):

| Brazil weight | blend | pooled b | p(b=0) | p(b=1) | 90% CI | LatAm b | in band |
|---:|---|---:|---:|---:|---|---:|---|
| 1.000 | as published | 1.127 | 0.042 | 0.727 | 0.35 to 1.91 | 1.375 | yes |
| 0.657 | BR+CL | 0.822 | 0.051 | 0.544 | 0.21 to 1.44 | 1.018 | yes |
| 0.455 | BR+MX | 0.643 | 0.061 | 0.202 | 0.13 to 1.16 | 0.807 | yes |
| **0.368** | **BR+MX+CL** | **0.566** | 0.067 | 0.120 | 0.09 to 1.04 | 0.716 | yes (barely) |
| 0.200 | | 0.416 | 0.088 | 0.040 | 0.02 to 0.81 | 0.541 | no |
| 0.000 | no Brazil | 0.239 | 0.155 | 0.009 | −0.06 to 0.54 | 0.333 | no |

Required co-movement (`C4_required_bX.csv`), three-country blend: for the pooled slope to stay at **1.0** the
Mexico+Chile accommodation-CPI y/y must move **−0.81pp per pp of the LatAm mix term**, nearly as strongly and
inversely as Brazil's own −1.04; to stay at the band floor 0.5 it needs −0.12; if it is uncorrelated with the mix
term the pooled slope is 0.57 and b = 1 is not rejected only because the interval is wide (p 0.12). **The open item
therefore cannot "make it the strongest evidence in the line": the best case for the pooled claim is that Mexican
and Chilean hotel inflation happened to surge in exactly 1H25 the way Brazil's did.**

### 6.4 The mechanism, tested on the data in hand

Why does Brazil's hotel CPI co-move inversely with the LatAm mix term? The mix term is negative when Brazil, the
region's cheapest country (rel_price 0.68), gains share: Brazil panel stays grew **+51% / +58% y/y in 1Q25 / 2Q25**,
the same two quarters IPCA hospedagem ran 10.9%. `C4_brazil_mechanism.csv`, 1Q22 on:

| window | n | r(Brazil stays y/y, IBGE hospedagem) | r(Brazil stays y/y, LatAm mix) | r(IBGE hospedagem, LatAm mix) |
|---|---:|---:|---:|---:|
| disclosed 4Q24–2Q26 | 7 | +0.81 | **−0.98** | **−0.81** |
| 1Q22 on | 18 | +0.69 | −0.12 | **+0.00** |

Over the 18 quarters the comparator is available, Brazil's hotel inflation has **zero** correlation with the LatAm
mix term. The −0.81 that produces the pooled slope is a property of seven quarters in which a Brazilian demand boom
moved both the panel's share vector and Brazilian hotel prices at once. That is a demand shock entering both sides
of the regression, not the identity's one-for-one pass-through.

## 7. Interpretation and verdict

1. **Reproduction: exact.** Nothing in the note's arithmetic is wrong.
2. **The p 0.042 is not a real p-value.** Webb-enumerated wild cluster bootstrap: 0.889 (b = 0), 0.898 (b = 1).
   The CRV1 t(3) is computed from four clusters of which one supplies all the identifying variation; the note
   already flagged the Rademacher 1.000 as uninformative and the Webb version confirms it rather than fixing it.
   Randomisation inference does give p 0.035 for *some* association in LatAm, but §4 shows what that association is.
3. **Which prints carry it:** no single quarter; the 1Q25+2Q25 pair (pooled b 0.64 without them); and, more
   important than any quarter, the Brazil comparator: **76% of the LatAm slope is the IBGE series moving against
   the mix term, 26% is Airbnb's disclosed number.**
4. **Neutral comparator:** pooled b 0.24 (zero) / −0.35 (other regions' median); b = 1 rejected at p 0.009 /
   < 0.001; the four leave-one-out slopes then agree with each other. **Pre-registered criterion (i) met.**
5. **Mexico/Chile:** not obtained (INE.Stat has no IPC; INEGI/Banxico token-gated; INE Chile's file list is
   interactive). Bounded: with the pre-stated blend the pooled slope is 0.57 if the new series are neutral and
   returns to about 1.0 only if they co-move with the mix term about as strongly as Brazil's did, which over 18
   quarters Brazil's own series does not (r 0.00).

**Verdict.** "Compatible with the identity" is no longer a fair summary and should be downgraded. The pooled
regression does not test whether within-region country mix passes one-for-one into Airbnb's disclosed regional
ADR; on the sample that identifies it, it measures the co-movement of Brazilian hotel inflation with a Brazilian
demand boom. The defensible sentence is: *"Across the 23 disclosed regional ex-FX prints the within-region mix term
has a slope of 0.36 on Airbnb's own numbers in the one region with regressor variation; the reported 1.13 is
obtained only after subtracting a single-country inflation series that supplies three-quarters of the slope, and
with a neutral comparator the identity's 1.0 is rejected (p at or below 0.01)."* The note's own caveats (one
region, Brazil alone, −0.30 without LatAm) were honest but under-stated: the problem is not that Latin America is
one region, it is that Latin America's y is mostly Brazil's CPI. `final_adr.md` §4.5's "cannot reject it ... that is
the good news, and it is real" and §9's "the right claim is compatible with the identity" should both become "not
established; the only region-level test that isolates Airbnb's number gives 0.36." DEC-0038 (attribution row, not
the base) is unaffected and if anything reinforced.

## 8. Parameter count and files

Regressions: 5 parameters (slope + 4 FE) on 23 cells; nothing fitted beyond that. Files in this folder:
`C4_audit.py`, `C4_bounds.py`, `C4_audit_output.txt`, `C4_bounds_output.txt`, `C4_reproduction.csv`, `C4_loro.csv`,
`C4_wildboot.csv`, `C4_latam_loqo.csv`, `C4_latam_l2o.csv`, `C4_latam_decomposition.csv`,
`C4_neutral_comparator.csv`, `C4_neutral_comparator_loro.csv`, `C4_permutation_summary.csv`,
`C4_brazil_weight_curve.csv`, `C4_required_bX.csv`, `C4_brazil_mechanism.csv`, `stat_ine_cl_datastructure_all.xml`.

## RESUME

The pooled reconciliation reproduces exactly and fails its own purpose: the 1.127 is 76% the Brazil IPCA
hospedagem series and its cluster p-value is not valid at G = 4 (Webb WCR 0.89). Next agent: (1) obtain the INEGI
hoteles and INE Chile 11.2 series by the human routes in §6.2 and drop them into the blend in `C4_bounds.py` with
the pre-stated weights 0.368/0.440/0.192; the pass line is already fixed by §6.3 (pooled b at or above 0.5 with the
real blend, and b_X reported); (2) rewrite `final_adr.md` §4.5 and §9 per §7 (a new file, per the copy rule, not an
edit in place); (3) consider replacing the pooled test with the one number that survives, the 0.36 slope of the
disclosed ex-FX on the mix term inside LatAm with its interval, as the honest evidence sentence.
