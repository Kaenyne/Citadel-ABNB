# ADR line v2, upgrade 3 — reconciling the mix terms to the company's own numbers

**22 September 2026.** Two checks on the sub-regional (country) mix term registered in
[`adr_v2_geomix_prereg.md`](adr_v2_geomix_prereg.md) and carried in [`adr_v1_design.md`](adr_v1_design.md) §3.3b.
The question this file answers is narrow and adversarial: **when our country-mix term is put inside Airbnb's own
accounting — the annual 10-K decomposition and the disclosed quarterly EMEA ex-FX ADR — does it survive, and what
does it leave for the "core" line to explain?** Nothing here is fitted; no window, weight or country was chosen
after seeing a result. Web fetches: zero.

Engine: `analysis/src/pitch_model_v2/adr_engine/reconcile.py`.
Outputs: `data/processed/pitch_model_v2/adr_engine/reconcile_annual.csv`,
`reconcile_emea_quarterly.csv`.

```
cd ~/Citadel-ABNB && PYTHONPATH=analysis/src python3 -W ignore -m pitch_model_v2.adr_engine.reconcile
# exit 0; prints both tables and writes the two CSVs
```

---

## 0. Verdict in five lines

1. **The sub-regional term survives the company's own accounting, and it survives with the wrong sign for the
   bull case.** It is negative, so it makes the implied like-for-like price *larger*, not smaller: 3.34 / 3.15 /
   3.93pp for FY2023-25 against a plug of 2.48 / 2.80 / 3.62.
2. **Inside the 10-K plug it is small and shrinking** — 35% of the plug's size in 2023, 13% in 2024, **8% in
   2025**. On the company's own annual numbers there is no growing country-mix drag.
3. **The four-region geo term is independently corroborated**: our quarterly build annualises to −1.10 / −1.33 /
   −1.67pp against the 10-K's −1.08 / −1.24 / −1.58 — agreement to 0.02-0.09pp in all three years.
4. **The EMEA quarterly identity closes.** Disclosed EMEA ex-FX less our EMEA country mix leaves an implied
   within-country price of 3.5-6.6% (mean 4.4, n 7) against a panel-weighted EMEA accommodation CPI of 2.6-4.9%:
   residual **+0.65pp mean, sd 0.72pp (n 7)**; **+0.30 / 0.83 (n 10)**. Regressing the disclosed-minus-CPI gap on
   our mix gives a slope of **+1.09 (n 7) / +1.16 (n 10)** — the identity implies exactly 1.0 — with r +0.48 /
   +0.44 (p 0.27 / 0.20, not significant at this n).
5. **What it costs the core line:** the implied like-for-like price is flat-to-up (3.34 → 3.15 → 3.93) while
   government accommodation inflation collapsed (GBV-weighted blend 7.10 → 2.37 → 1.51). **No external price
   index supports the core's level, and none supports its reversion either.** The 2026 step remains unexplained,
   exactly as §3.1 says.

---

## A. Annual: our sub-regional mix inside the 10-K plug (FY2023-25)

### A.1 The company-side decomposition, verbatim

From `data/processed/adr/07_full_decomposition.csv`, built by `analysis/src/adr/07_assemble.py`. All in pp of
reported ADR y/y.

| year | ADR y/y | geo mix (4-region) | FX | interaction | **within-region ex-FX** | size mix | LOS | **plug: pricing + sub-regional mix** |
|---|---|---|---|---|---|---|---|---|
| 2023 | 2.147 | −1.083 | 0.183 | −0.049 | **3.097** | 0.000 | 0.617 | **2.479** |
| 2024 | 1.644 | −1.244 | −0.449 | −0.107 | **3.443** | 0.441 | 0.205 | **2.797** |
| 2025 | 3.018 | −1.584 | 1.304 | −0.108 | **3.405** | −0.251 | 0.036 | **3.621** |

### A.2 The 07 file's identity — and what it is worth

Asked for: *do the columns add up (geo + fx + interaction + within = total)?* **They do, to machine precision
(−0.0 / 0.0 / −0.0pp), and so does plug + size + LOS = within (0.0 in all three years).** That is the honest
answer and it is also a **non-result**: `07_assemble.py` line 99 *defines*
`within_region_exfx_pp = adr_yoy − geo_mix − interaction − fx` and defines
`pricing_and_subregional_mix_pp = within_region_exfx − size_mix − LOS` (line 103). Both identities are closures by
construction. Reporting them as validation would be a category error; they are typo checks.

**The one non-trivial check in that file** is `reconciliation_gap_pp` — the same within-region ex-FX built
independently in `03_regional_annual_fx.csv` as the nights-weighted average of the four disclosed regional ex-FX
rates. It reconciles: **+0.031 (2023), +0.298 (2024), −0.131 (2025)**, i.e. the plug's parent quantity is right
to within a third of a point, and 2024 is the loosest year. No discrepancy beyond that was found.

**One discrepancy found that the file does not flag.** 07's `size_mix_pp` and `of_which_los_pp` come from
different objects than the ones this line uses, and they disagree materially:

| year | 07 size mix | our unit size (H) | 07 LOS | our LOS (H) | ours − 07's, size+LOS |
|---|---|---|---|---|---|
| 2023 | 0.000 (not measured) | 0.387 | 0.617 | 0.312 | +0.082 |
| 2024 | 0.441 (n 3 pairs, 1 market) | 0.841 | 0.205 | 0.274 | +0.469 |
| 2025 | −0.251 (n 11 pairs, 4 markets) | 0.739 | 0.036 | 0.291 | **+1.245** |

In 2025 the two size-mix objects differ by **0.99pp and in sign**. Because the plug is *defined* net of 07's size
and LOS, that 1.25pp lands in the plug. Everything below therefore carries both a headline number (the plug as
filed, as briefed) and a rebased number (within-region ex-FX net of *our* size/LOS terms instead).

### A.3 Our terms, GBV-weighted annual averages of the quarterly terms

| year | **sub-geo total** | NAM part | EMEA part | LatAm part | APAC part | NAM own mix | EMEA own mix | LatAm own mix | APAC own mix |
|---|---|---|---|---|---|---|---|---|---|
| 2023 | **−0.860** | −0.341 | +0.004 | −0.028 | −0.495 | −0.669 | +0.013 | −0.370 | −6.744 |
| 2024 | **−0.357** | −0.202 | −0.102 | +0.040 | −0.093 | −0.424 | −0.284 | +0.486 | −1.135 |
| 2025 | **−0.304** | −0.095 | −0.057 | −0.137 | −0.015 | −0.206 | −0.156 | −1.583 | −0.170 |

("Part" = the region's own mix times its 10-K GBV share; "own mix" = the within-region row before the weight.
2023's APAC −6.74 is the Thailand/Taiwan/Japan reopening against an Australia-heavy panel, as registered.)

Our four-region geo term, annualised the same way, is **−1.102 / −1.325 / −1.672** against the 10-K's −1.083 /
−1.244 / −1.584: **0.02 / 0.08 / 0.09pp apart**. The four-region layer is therefore corroborated against the
company's own annual arithmetic; that is worth more than it sounds, because the 07 geo term comes from the 10-K
Geographic Mix table and ours from the letters' regional buckets and the nights line.

### A.4 The reconciliation

| year | plug | our sub-geo | **implied like-for-like price** (plug − sub-geo) | implied price, rebased on our size/LOS | core (exfx_history, annualised) | sub-geo as % of plug |
|---|---|---|---|---|---|---|
| 2023 | 2.479 | −0.860 | **3.339** | 3.258 | 2.039 | −34.7% |
| 2024 | 2.797 | −0.357 | **3.154** | 2.685 | 2.576 | −12.8% |
| 2025 | 3.621 | −0.304 | **3.925** | 2.679 | 2.272 | −8.4% |

**Does the sub-regional mix sit inside the plug?** Yes — arithmetically it is a component of it, and its
magnitude (0.30-0.86pp) is comfortably smaller than the plug (2.5-3.6pp), so no year requires an implausible
price remainder to accommodate it. But **the sign matters for the thesis**: because the mix term is *negative*,
the price remainder is *bigger* than the plug in every year. The plug is not hiding a large country-mix drag on
top of a modest price; it is hiding a price that is larger than the plug, offset by a modest and **fading** mix
drag. The percentages above are the whole finding: 35% → 13% → **8%**.

### A.5 Is the price remainder plausible?

Against government accommodation price indices (quarter-mean y/y, annualised; `P_feature_quarterly_panel.csv`):

| year | implied price | euro-area HICP CP112 | EU27 HICP CP112 | US CPI lodging away from home | UK ONS accommodation | **GBV-weighted four-region blend** | price − blend |
|---|---|---|---|---|---|---|---|
| 2023 | 3.34 | 8.42 | 9.28 | 4.53 | 10.87 | **7.10** | **−3.76** |
| 2024 | 3.15 | 5.20 | 5.31 | −0.57 | 5.29 | **2.37** | **+0.78** |
| 2025 | 3.93 | 3.67 | 4.11 | −2.38 | 0.44 | **1.51** | **+2.42** |

(Blend = 10-K GBV shares × {NA: BLS lodging away from home, EMEA: euro-area HICP CP112, LatAm: IBGE IPCA
hospedagem, APAC: ABS CPI 30033}.)

**Plausible in level, implausible in trend.** In 2023 the implied price is *below* every accommodation index —
Airbnb under-priced the post-COVID hotel inflation, which is consistent with the letters. By 2025 it is
**2.4pp above** the blend and the gap widens monotonically. Two readings, and this file does not choose between
them: either Airbnb is genuinely taking price the industry is not (the bundle, the RNPL mix, the fee migration —
§3.2 sizes ~1pp of it), or the plug still contains mix and quality effects that neither the four-region term nor
our country term can see. On the rebased column (our size/LOS) the 2025 step disappears entirely — **2.685 →
2.679** — which is the sharper statement: *on our own size and LOS terms, like-for-like price did not accelerate
in 2025 at all; the 07 plug's 2025 step is almost entirely the size-mix sign flip in A.2.*

---

## B. Quarterly, EMEA: disclosed ex-FX = country mix + within-country price + size/LOS

Disclosed EMEA ex-FX ADR y/y, whole points, from `04_regional_quarterly_wide.csv` (`adr_yoy_exfx_emea_pct`,
basis `disclosed-chained`): 4Q24 +6, 1Q25 +4, 2Q25 +3, 3Q25 +4, 4Q25 +4, 1Q26 +4, 2Q26 +5 — **n 7**. Extended
back to 1Q24-3Q24 (5.02 / 4.61 / 4.61), where the ex-FX figure is *constructed* (reported less modelled FX) and
so flagged, **n 10**.

| quarter | disclosed ex-FX | our EMEA mix | **implied within-country price** | size (global) | LOS (global) | implied net of size/LOS |
|---|---|---|---|---|---|---|
| 1Q24* | 5.017 | −0.553 | 5.570 | 0.963 | 0.213 | 4.394 |
| 2Q24* | 4.610 | −0.185 | 4.795 | 0.772 | 0.232 | 3.791 |
| 3Q24* | 4.614 | +0.211 | 4.403 | 0.890 | 0.253 | 3.260 |
| 4Q24 | 6.000 | −0.617 | **6.617** | 0.707 | 0.432 | 5.478 |
| 1Q25 | 4.000 | −0.201 | **4.201** | 0.669 | 0.279 | 3.253 |
| 2Q25 | 3.000 | −0.509 | **3.509** | 0.732 | 0.348 | 2.428 |
| 3Q25 | 4.000 | +0.172 | **3.828** | 0.748 | 0.308 | 2.772 |
| 4Q25 | 4.000 | −0.063 | **4.063** | 0.822 | 0.221 | 3.019 |
| 1Q26 | 4.000 | −0.284 | **4.284** | 0.945 | 0.300 | 3.039 |
| 2Q26 | 5.000 | +0.431 | **4.569** | 0.700 | 0.300 | 3.568 |

\* constructed ex-FX, not a disclosed whole point. **No regional size/LOS is disclosed anywhere**; the global H
terms are used as a proxy and that is an assumption, not a measurement.

### B.1 The price series available for EMEA, and which one works

**(i) M2 quarterly medians (Rome, Paris, Barcelona, London), local currency — FAILS, and the failure is
structural.** Only same-basis pairs are usable (`listed_nightly` against `listed_nightly`, entire homes,
`median_old`, latest dump in each quarter); the 2026 files are `quote_per_night`, which has no 2025 comparator.
That leaves **Rome 4Q23-3Q25 (8 pairs) and Paris 4Q24-2Q25 (3 pairs); Barcelona and London have one quarter each
(3Q25) and contribute nothing.** The resulting y/y is violent — Rome +20.0 (1Q24) → −10.1 (1Q25); Paris +21.1
(4Q24) → −4.0 (1Q25) — because it is an asking-price median from a single dump date, not booked ADR. Residual
against it: **mean +6.07pp, sd 7.07pp (n 4)** in the disclosed window; **+0.03 / 9.69 (n 7)** extended. The M2
route cannot carry a quarterly EMEA price series and is not used for anything below.

**(ii) Euro-area HICP accommodation (CP112)** — the survivor proxy, as registered. **(iii) A panel-share-weighted
EMEA accommodation CPI**, new here: each panel country's own HICP CP112 (ONS CPI 11.2 for the UK) weighted by its
base-quarter share of the panel's EMEA stays, renormalised over covered countries (**91.9-95.7% coverage** in every
quarter). **Turkey is excluded from the primary blend** and shown separately: its accommodation CPI runs 27.9-58.0%
y/y on hyperinflation, and at a ~1.9% panel share it adds +0.47 to +1.07pp of spurious "price" to a series whose
ex-FX basket is EUR 70 / GBP 25 / USD 5 (`config.KAPPA`).

### B.2 Residuals

| quarter | implied price | EA HICP | **panel-weighted EMEA CPI** | coverage | resid vs EA | **resid vs panel** | resid net of size/LOS |
|---|---|---|---|---|---|---|---|
| 1Q24* | 5.57 | 5.30 | 5.97 | 92.9% | +0.27 | −0.40 | −1.58 |
| 2Q24* | 4.79 | 5.47 | 5.67 | 95.6% | −0.67 | −0.87 | −1.88 |
| 3Q24* | 4.40 | 4.97 | 4.69 | 95.7% | −0.56 | −0.29 | −1.43 |
| 4Q24 | 6.62 | 5.07 | 4.91 | 93.9% | +1.55 | +1.71 | +0.57 |
| 1Q25 | 4.20 | 4.53 | 4.17 | 92.1% | −0.33 | +0.03 | −0.92 |
| 2Q25 | 3.51 | 3.97 | 3.60 | 95.4% | −0.46 | −0.09 | −1.17 |
| 3Q25 | 3.83 | 2.83 | 2.61 | 95.4% | +0.99 | +1.22 | +0.16 |
| 4Q25 | 4.06 | 3.33 | 2.88 | 93.6% | +0.73 | +1.18 | +0.14 |
| 1Q26 | 4.28 | 3.93 | 4.33 | 91.9% | +0.35 | −0.04 | −1.29 |
| 2Q26 | 4.57 | 4.27 | 4.02 | 95.0% | +0.30 | +0.55 | −0.45 |

| residual | n 7 (disclosed) | n 10 (extended) |
|---|---|---|
| vs euro-area HICP | mean **+0.45**, sd **0.71**, MAE 0.67 | +0.22 / 0.73 / 0.62 |
| vs panel-weighted EMEA CPI | mean **+0.65**, sd **0.72**, MAE 0.69 | +0.30 / 0.83 / 0.64 |
| …**with our mix set to zero** | mean +0.50, sd 0.83, MAE **0.81** | +0.14 / 0.92 / 0.78 |
| vs panel CPI, net of size/LOS proxy | mean −0.42, sd 0.73, MAE 0.67 | −0.78 / 0.84 / 0.96 |
| …with our mix set to zero | mean −0.58, sd 0.85, MAE 0.69 | −0.94 / 0.95 / 1.03 |
| vs M2 medians | mean +6.07, sd 7.07 (n 4) | +0.03 / 9.69 (n 7) |

### B.3 Does the EMEA mix have the right sign and size?

Three answers, in increasing order of strength.

1. **Sign and size: yes.** Our EMEA mix is negative in 7 of 10 quarters, range −0.62 to +0.43pp. Subtracting it
   leaves an implied within-country price of 3.5-6.6% against a panel CPI of 2.6-4.9% — plausible on the face of
   it, and consistent with the 3.3-4.6% HICP band the brief names.
2. **It reduces the residual rather than enlarging it.** Setting the mix to zero raises the sd from 0.72 to 0.83
   and the MAE from 0.69 to 0.81 (n 7); on n 10, sd 0.83 → 0.92, MAE 0.64 → 0.78. A ~15% MAE improvement from a
   term built with no reference to the EMEA disclosure at all.
3. **The strongest piece: the scale is right.** Regress the CPI gap (disclosed EMEA ex-FX less panel CPI) on our
   mix term. The identity implies a slope of exactly 1.0 — a point of country mix must pass one-for-one into the
   disclosed number. Measured: **b = +1.09 (n 7)** and **+1.16 (n 10)**, r +0.48 / +0.44. **p 0.27 and 0.20:
   not significant, and it cannot be at this n.** But a slope within 0.1-0.2 of its theoretical value, from a
   term built out of an entirely different dataset (Inside Airbnb stays and June-2026 listed prices), is the
   check this term could most easily have failed and did not.

**Caveats, stated.** n is 7 on the disclosed window and 10 with the constructed quarters — far too small for
inference, and every number in B.2 should be read as a description, not a test. The size/LOS proxy is global, not
EMEA. The panel's EMEA country shares are Inside Airbnb's, not Airbnb's: Italy at 24% of panel EMEA stays is
almost certainly overweight. Turkey is excluded by judgement (stated above, and the inclusive column is in the
CSV). And the mean residual of +0.65pp is not nothing: on the disclosed window our reconstruction of EMEA runs
about two-thirds of a point hot against the accommodation CPI, which is either the bundle (§3.2 sizes ~1pp
globally, and the fee/cancellation leg went global in October 2025) or an unmeasured EMEA size/LOS effect.

---

## C. What this does to the line

**The sub-regional term survives the company's own accounting.** It is arithmetically inside the 10-K plug with
room to spare, it leaves a price remainder that is plausible in level against government indices, and in EMEA it
is correctly scaled against the only quarterly disclosure that can test it. **Nothing here changes DEC-0016's
disposition**: H2 failed, the term stays an attribution row and a forward scenario, and this file gives no reason
to promote it into the base.

**But it survives as a smaller thing than the thesis wanted.** Three numbers carry that:

- The term is **8% of the FY2025 plug** and falling (35% in 2023). Airbnb's own annual accounting leaves no room
  for a large, growing country-mix drag.
- The implied like-for-like price is **3.34 / 3.15 / 3.93** while the GBV-weighted accommodation CPI blend goes
  **7.10 / 2.37 / 1.51**. The core line is not an inflation pass-through and cannot be argued as one; its 2025-26
  level is 2.4pp above what the price environment supports, and the file names that as the exposure.
- On **our own** size/LOS terms rather than 07's, like-for-like price is flat at **2.69 / 2.68** in 2024-25. The
  2025 acceleration visible in the 10-K plug is mostly a 0.99pp sign disagreement between two size-mix objects,
  not a price event. **That is the single most fragile number in the annual chain** and it should be said out
  loud in the memo rather than left in a CSV.

For §3.1's core: this exercise removes none of the 1.45pp gap. It sharpens what the gap is *not* — it is not the
four-region mix (corroborated to 0.09pp), not the country mix (0.30pp and fading), and not accommodation
inflation (which fell as the core rose). It remains the bundle (~1pp, dated, lapping) plus an unexplained
residual, carried and labelled.

---

## RESUME

`reconcile.py` runs both checks end to end and exits 0; `reconcile_annual.csv` and `reconcile_emea_quarterly.csv`
hold every number above. Nothing in the base case changed and no decision was taken here. Three things are open.
**(1)** The 2025 size-mix disagreement — 07's `size_mix_pp` −0.251 (05_size_mix_summary, quote basis, 11 pairs /
4 markets) against the H decomposition's +0.739 — is 0.99pp and flips sign; it drives the entire apparent 2025
step in like-for-like price and should be adjudicated before the memo quotes either. **(2)** The EMEA
reconciliation runs +0.65pp hot against the panel accommodation CPI on n 7; the candidate explanations are the
bundle's global October-2025 leg and an unmeasured EMEA size/LOS, and neither is separated here. **(3)** The M2
quarterly price route is dead for EMEA (2026 files are `quote_per_night` with no 2025 comparator; only Rome has a
usable run) — if a within-country price series is wanted for the memo, it has to come from the government indices
or from a re-capture on the old basis, not from M2. Do not treat the 07 file's `identity_check_pp` or the
plug-plus-size-plus-LOS closure as validation: both are definitional. The only real check in that file is
`reconciliation_gap_pp` (+0.03 / +0.30 / −0.13), and it passes.
