# Final line — ADR (average daily rate, GBV ÷ Nights and Seats Booked)

**Version 2 — 22 September 2026.** The complete rationale for line 2 of the pitch model, per **DEC-0026**: why
every base number stands, the data and model behind each one, every alternative carried beside it, every test
that was run and what it returned, and how the thesis catalysts enter. This file supersedes version 1, which
covered the FX identity and the ex-FX mechanism only; it now also carries the v2 geographic-mix layer and the
four mitigations of 22 September.

Scope: **base scenario** (DEC-0020). Alternatives sit beside it and are never blended. **DEC-0016 governs
throughout**: every scenario is the mechanical consequence of a stated assumption, and no input was chosen to
reach a price. Decisions DEC-0034, DEC-0035, DEC-0036, DEC-0037, DEC-0038, DEC-0039, DEC-0040 and DEC-0041 are
all *proposed* and await Theo.

Everything reproduces from raw stores in about twenty seconds:
`PYTHONPATH=analysis/src python3 -m pitch_model_v2.adr_engine.run` (27 tests).

Companion documents, all still live: `adr_fx_prereg.md` (the pre-registration, blob 0495e5f3),
`adr_v1_design.md` (the full construction and the analyst's attacks), `adr_v2_geomix_prereg.md`, the four
upgrade notes, the four mitigation notes `adr_v2_mitigation_A/B/C/D_*.md`, and `adr_v2_thesis.md` (the ten
sentences).

---

## 1. The one identity the whole line rests on

Airbnb discloses reported ADR growth and constant-currency ADR growth every quarter. The difference is the FX
translation effect. So:

```
reported ADR y/y  =  constant-currency ("ex-FX") ADR y/y  +  FX translation effect
```

This closes to **≤ 0.042pp on all 14 disclosed quarters**. It is an accounting identity, not a fitted
relationship, and it is why the line is built as two halves rather than as one regression on ADR.

The two halves are epistemically different, and the document keeps them apart on purpose:

| half | what it is | tested? |
|---|---|---|
| **FX** | an identity with **zero fitted parameters** | **yes** — point in time, three origins, two windows, 17 disclosed quarters, pre-registered pass line |
| **ex-FX** | a **construction** on disclosed mechanics | **no** — and it is not given a pass line it cannot earn (the only lapped quarter has not printed) |

Claiming the second is tested would be the easiest way to lose credibility with a lodging analyst. It is
labelled as a construction everywhere it appears.

---

## 2. Part A — the FX leg

### 2.1 Why FX on ADR is a pure translation quantity

Airbnb records Gross Booking Value in USD at the exchange rate on the **booking date**, and ADR is GBV ÷ nights,
both booking-dated. Constant currency restates the current period at the **prior-year** period's rates.
Therefore the disclosed FX effect on ADR is, to first order:

```
FX_pp(t) = 100 · Σ_c  ω_c · [ ē_c(t) / ē_c(t−4) − 1 ]
```

where `ē_c(t)` is the booking-quarter average rate of currency c and `ω_c = Σ_r g_r · β_r · κ_{r,c}` is its
weight in GBV: the 10-K regional GBV share `g_r` times a frozen destination-currency basket `κ`. In the promoted
leg every `β_r = 1`, so **nothing is fitted**.

Two consequences that matter and are easy to get wrong:

- **It is contemporaneous and unhedged.** Never apply a lag operator or a hedge ratio to it. The revenue line's
  Φ-lagged FX construction is a different object and must never be added to an ADR growth rate.
- **It is booking-dated, not stay-dated.** The quarter's average rate is the right average because GBV is struck
  at booking.

### 2.2 The inputs, and where each is frozen

| input | value | source | frozen? |
|---|---|---|---|
| Regional GBV shares | NA 44.1 / EMEA 37.4 / LatAm 9.4 / APAC 9.1% | 10-K Geographic Mix, `01_regional_annual.csv`, with a `knowable_from` date so history uses only what was public | point-in-time |
| Destination baskets κ | NA: USD .90 / CAD .08 / MXN .02 · EMEA: EUR .70 / GBP .25 / USD .05 · LatAm: BRL .55 / MXN .38 / USD .07 · APAC: AUD .55 / JPY .20 / KRW .10 / INR .07 / USD .08 | judgement, inherited from `fx_lag_v2/01b_basket_weights_used.csv` | frozen before any fit |
| Daily rates | 9 FRED H.10 bilaterals + the broad dollar index | `fetch_fx.py`, keyless | dated file per pull |

Resulting currency weights: **USD 43%, EUR 26%, GBP 9%, BRL 5%, AUD 5%, MXN 4%, CAD 3.5%, JPY 2%, KRW 1%,
INR 0.6%.** The dollar block is inert by construction, so roughly 57% of GBV carries the effect.

### 2.3 The point-in-time protocol

A forecast is only honest if it could have been made on the day. Three origins are defined and used for every
historical target:

- **O1** — the first day of the quarter. Almost nothing is realised; this is the number the pitch quotes on
  2 October for 4Q26, and it is labelled as an O1-type number.
- **O2** — day 60 of the quarter.
- **O3** — the day before the print.

At each origin, rates are taken with the **FRED H.10 one-week publication lag**, and every unobserved day of the
quarter is held at the last observed spot. No future information leaks in.

Scoring uses an **interval likelihood**, because Airbnb discloses ex-FX growth rounded to whole points and twice
said only "less than 1%" (3Q23, 4Q23, scored as 0.5 ± 0.25). Treating a rounded disclosure as a point would
overstate our own error and the naive's differently.

### 2.4 What the pre-registration fixed, before any number was computed

`adr_fx_prereg.md`, blob `0495e5f3`, written and committed before the first fit. It fixed:

1. The identity and the baskets.
2. The windows: **W1** targets 1Q23–2Q26 (n 14), **W2** targets 1Q24–2Q26 (n 10).
3. The pass line: a variant is promoted only if its RMSE ratio to the naive carry is **≤ 0.75 at both O2 and O3
   on both windows**. O1 is reported but not scored for promotion.
4. The tie-break: if both the zero-parameter identity (V0) and the fitted pass-through (V1) pass, **V1 takes the
   leg only if it is strictly lower at O2 and O3 on both windows**; otherwise V0, on parsimony.
5. **"V2/V3/zero are comparators; they cannot be promoted by this registration."**

Point 5 turns out to matter enormously. Read §2.6.

### 2.5 The walk-forward result

Every cell is an out-of-sample, point-in-time forecast against a disclosed print.

| window | origin | n | RMSE (pp) | naive RMSE | **ratio** | bootstrap 90% upper | interval ratio |
|---|---|---:|---:|---:|---:|---:|---:|
| W1 | O1 | 13 | 1.313 | 3.002 | 0.437 | 0.728 | 0.366 |
| W1 | O2 | 14 | 0.724 | 2.106 | **0.344** | 0.438 | 0.211 |
| W1 | O3 | 14 | 0.637 | 2.106 | **0.303** | 0.369 | 0.151 |
| W2 | O1 | 10 | 1.473 | 2.358 | 0.625 | 0.881 | 0.560 |
| W2 | O2 | 10 | 0.754 | 1.967 | **0.383** | 0.509 | 0.240 |
| W2 | O3 | 10 | 0.624 | 1.967 | **0.317** | 0.418 | 0.153 |

The four promotion cells are 0.303 to 0.383 against a pre-registered line of 0.75, with moving-block bootstrap
90% upper bounds of **0.37 to 0.51** — still comfortably inside the line at the top of the interval. On the
interval metric the identity sits at **0.15 to 0.24**, essentially the rounding floor: it is about as close to
the disclosure as a whole-point disclosure permits.

Even at quarter start, with almost nothing realised, the identity beats the carry (0.437 and 0.625).

**V0 was promoted.** V1, the fitted regional pass-through, passes but is not strictly lower on both windows
(it wins W2 at 0.347/0.290 and loses W1 at 0.375/0.337), so the pre-registered tie-break keeps the
zero-parameter leg.

### 2.6 The variant that scored best, and why it is not the leg

Full comparison at the promotion origins:

| variant | W1 O2 | W1 O3 | W2 O2 | W2 O3 | bias (pp) |
|---|---:|---:|---:|---:|---|
| V0 translation identity (**promoted**) | 0.344 | 0.303 | 0.383 | 0.317 | +0.11 / +0.15 / −0.07 / −0.04 |
| V1 fitted pass-through | 0.375 | 0.337 | 0.347 | 0.290 | +0.29 / +0.34 / +0.12 / +0.17 |
| **V2 euro-only OLS** | **0.270** | **0.281** | **0.268** | **0.272** | **−0.33 / −0.27 / −0.34 / −0.27** |
| V3 broad-dollar OLS | 0.532 | 0.517 | 0.599 | 0.568 | −0.52 / −0.50 / −0.47 / −0.46 |
| naive carry | 1.000 | 1.000 | 1.000 | 1.000 | −0.49 / −0.49 / +0.08 / +0.08 |

**The euro-only OLS has the lowest RMSE ratio in all four cells.** This must be said plainly rather than
buried, because an analyst will find it.

It is not the leg for three reasons, and the first is the one that counts:

1. **It was excluded before the scores existed.** The pre-registration states that V2 and V3 are comparators and
   cannot be promoted. That sentence was written before any variant was run. Picking it up now because it won
   would be exactly the selection the registration exists to prevent.
2. **It is biased by −0.27 to −0.34pp in every single cell**, while the identity's bias is +0.15 to −0.07.
   A single-currency proxy fits the average quarter well and is systematically wrong about level.
3. **It is structurally blind to the currencies that drive the forecast quarters.** It cannot see the peso, the
   real or the Australian dollar; those three contribute **+1.08pp of the +0.42pp** 3Q26 effect and +0.92pp of
   the +0.51pp in 4Q26. 3Q26 is their quarter, not the euro's.

This is not a footnote for the thesis, it is a live disagreement with the committed card: the card's FX leg of
−0.43pp is the midpoint of a euro-only fit and a basket, so **it inherits the −0.3pp euro bias**. The 5 November
print adjudicates between four numbers named in advance (§7.1).

### 2.7 The pass-through posterior — descriptive, not used

A PyMC NUTS posterior on the regional pass-through β, priors N(1, 0.25²), interval likelihood, n 17:

| region | posterior mean | 90% HDI | P(β > 1) |
|---|---:|---|---:|
| North America | 0.994 | 0.587 – 1.399 | 0.49 |
| EMEA | **1.199** | 1.087 – 1.314 | 0.996 |
| Latin America | **0.460** | 0.173 – 0.784 | 0.006 |
| APAC | 1.266 | 0.882 – 1.641 | 0.869 |

Two regions are genuinely away from 1: EMEA above and Latin America below. That is informative about *why* the
identity's small misses happen — plausibly a heavier euro basket than assumed and a lighter effective LatAm
exposure, perhaps because LatAm GBV is more dollar-denominated than the frozen basket allows. It is reported
because it is interesting and because it is evidence about the baskets. **It is not used**, because the variant
that embeds it (V1) does not beat the identity out of sample on both windows.

### 2.8 The forecast, currency by currency

As of the 18 September FRED file, spot held for unobserved days.

**3Q26: +0.415pp**, with 87.9% of the quarter's business days already printed.

| currency | y/y rate change | GBV weight | contribution (pp) |
|---|---:|---:|---:|
| AUD | +8.07% | 5.0% | **+0.402** |
| MXN | +8.23% | 4.4% | **+0.365** |
| BRL | +6.08% | 5.1% | **+0.313** |
| GBP | −0.22% | 9.4% | −0.021 |
| KRW | −2.28% | 0.9% | −0.021 |
| CAD | −1.51% | 3.5% | −0.053 |
| INR | −8.67% | 0.6% | −0.055 |
| JPY | −7.31% | 1.8% | −0.132 |
| EUR | −1.46% | 26.2% | **−0.384** |
| | | | **+0.415** |

The whole quarter is a tug-of-war between a slightly weaker euro and three strong commodity and emerging
currencies. Band for the remaining days: **0.355 to 0.481**.

**4Q26: +0.514pp** at held spot, nothing printed, P10 −1.06 / P90 +2.26. Same structure: AUD +0.413, MXN +0.270,
BRL +0.237 against EUR −0.398. By the 5 November guide date about 32% will be printed.

**2027** turns slightly negative: 1Q27 −0.369, 2Q27 −0.427, 3Q27 −0.147, 4Q27 0.000, because the 2026 base
quarters were strong. **4Q27's 0.000 is an artefact**: both it and its base quarter are unobserved and held at
the same spot, so the identity returns exactly zero by construction. The honest content of that cell is its
±5pp band, not its point.

---

## 3. Part B — the ex-FX leg

### 3.1 Why it is a construction and not a regression

The repo has already run roughly 3,500 predictive tests on this company. The binding lesson is that fitting the
ex-FX residual produces objects that do not survive out of sample. So the ex-FX half is built as a sum of terms
that Airbnb has either disclosed or that we can measure, with the unexplained part isolated, named and carried:

```
exFX = core + bundle + geo_mix + unit_size + los_mix + seats + interaction + fee_K
```

The point of the decomposition is not accuracy. It is that **every term has an evidence label**, so the reader
can see exactly how much of the forecast is measured and how much is an assumption. The answer is that one term,
the core, is unobserved and carries the whole weight.

### 3.2 The terms, one by one

Forward values, all in pp of ADR:

| term | 3Q26 | 4Q26 | 1Q27 | 2Q27 | 3Q27 | 4Q27 | evidence label |
|---|---:|---:|---:|---:|---:|---:|---|
| core (like-for-like price) | 3.849 | 3.849 | 3.849 | 3.849 | 3.849 | 3.849 | **unobserved**, carried |
| bundle | 0.489 | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 | transcript-only, lapped on filed dates |
| geographic mix | −1.293 | −1.336 | −1.620 | −1.081 | −1.174 | −1.109 | measured, from the nights line |
| unit size | 0.797 | 0.797 | 0.797 | 0.797 | 0.797 | 0.797 | measured (alt data) + filed cross-check |
| length of stay | 0.056 | 0.056 | 0.056 | 0.056 | 0.056 | 0.056 | card term, carried |
| seats / new business | −0.483 | −0.483 | −0.565 | −0.565 | −0.565 | −0.565 | **assumed** (no volumes disclosed) |
| interaction | −0.100 | −0.100 | −0.100 | −0.100 | −0.100 | −0.100 | card term, carried |
| **ex-FX y/y** | **3.316** | **2.784** | **2.417** | **2.957** | **2.863** | **2.928** | |

### 3.3 The core — the one line that carries the thesis

`core = residual − bundle`, where the residual is disclosed ex-FX growth minus the five measured and assumed
terms. Its history:

| | 3Q25 | 4Q25 | 1Q26 | 2Q26 |
|---|---:|---:|---:|---:|
| residual | 2.822 | 3.699 | 4.381 | 4.849 |
| bundle | 0.511 | 1.000 | 1.000 | 1.000 |
| **core** | **2.311** | **2.699** | **3.381** | **3.849** |

The 2Q26 core of **3.849** is carried flat across all six forecast quarters. Two facts about it:

- Its 2023–25 mean is **2.272**. The 2Q26 reading is **1.58pp above** that.
- Its own one-quarter-ahead error, the standard deviation of its quarterly changes since 1Q23, is **0.88pp**,
  and that sits inside the band.

There is **no filed mechanism** for the step up. That is the honest position, and it is the single biggest
exposure in the line. Everything else in the ex-FX half is small by comparison.

**A labelling inconsistency found on 22 Sep and left for Theo.** The mean-reversion scenario reverts the core to
`CORE_MEAN_2023_25 = 2.398`, which is the 2023–25 mean of the **residual**, not of the core (2.272). The
residual mean is higher because it includes the bundle in 3Q25 and 4Q25. A like-for-like core reversion would
give 4Q26 ADR of about **$170.39** rather than the filed **$170.60**. The difference is $0.21 and it runs
*against* the short, so nothing here leans. It is flagged rather than silently corrected because the $170.60 is
already inside proposed DEC-0035.

### 3.4 The bundle and its lap calendar

Management sized a three-feature bundle — US Reserve Now Pay Later, the cancellation redesign, and the single
fee — at "over 200bp of nights / roughly 300bp of GBV" on the 4Q25 call and "approximately three points of
nights / approximately four points of GBV" on the 1Q26 call. Both imply **about 1pp of ADR**.

**This is transcript-only, and the label survives a wider search** (corrected 23 Sep). Mitigation A read the FY25
10-K and the 1Q26 and 2Q26 10-Qs, and X3 checked the 4Q25 and 1Q26 letters through a keyword extraction; the audit's
C5 search added the 2Q25, 3Q25 and 2Q26 letters, the 3Q25 10-Q, the 2026 DEF 14A and the 8-K list. Across those ten
filed documents no filing carries a magnitude. RNPL itself is named in filings from the 3Q25 letter (8-K Ex 99.1,
filed 6 Nov 2025: "In August, we launched our Reserve Now, Pay Later payment option within the U.S."); only the
10-K/10-Q series waits for the 2Q26 10-Q. The filed substitutes are "roughly 20% of global GBV came from Reserve
Now, Pay Later" and the 2Q26 10-Q's "the increase in ADR was driven in part by the continued adoption of RNPL".
DEC-0041 proposes that this closes the search.

The 1pp is split by the residual's own dated steps: +0.92 in 3Q25 when US RNPL went live alone, +0.88 in 4Q25
when the cancellation redesign and single fee went live. That gives **RNPL-NA 0.51, fee/cancellation 0.49**.

The lap calendar, on filed anniversaries rather than on judgement:

| quarter | US RNPL (live Aug 2025) | fee + cancellation (live Oct 2025) | bundle total |
|---|---|---|---:|
| 3Q26 | lapped | still in the y/y | **0.489** |
| 4Q26 onward | lapped | lapped | **0.000** |

The ex-NA RNPL leg (live 17 Feb 2026) is **0 in the base** because it has never been sized. The "full lap"
alternative sizes it at the 1H26 residual steps and takes 1Q27–2Q27 ex-FX down to 1.96 / 1.81.

### 3.5 Geographic mix — the arithmetic

Share-shift at constant regional prices. Anchored regional ADRs: **NA $255, EMEA $159, LatAm $95, APAC $118**.
Regional nights growth comes from the nights line (3Q26: NA +5.6%, EMEA +7.1%, LatAm +17.7%, APAC +15.9%).

The lever is easy to check on a napkin, which is exactly why it is credible: **one point of nights share moving
from North America to Latin America costs 0.89pp of blended ADR**, because $255 against $95 is a 2.7× ratio.

Method validation: this bucket arithmetic reproduces the repo's independent H-decomposition term to a mean of
**0.13pp (maximum 0.22pp) on 2Q24–2Q26**, one-signed from 4Q24: the bucket method runs 0.08–0.18pp less negative
than H in every quarter, which the corrected engine accounts for (`adr_v3_corrections.md`, fix c). The card's alternative (−1.428 flat, from the E stays split) is carried beside it.

### 3.6 Unit size, and why the filed metric matters

Booked capacity per reviewed stay is +1.35% y/y on 2.05m vintage-matched reviews across 119 markets, times a
0.592 hedonic coefficient, giving **+0.80pp**. The filed cross-check — Bedroom Nights Booked +12% against nights
+10%, at a measured bedroom elasticity of 0.23 — gives +0.42 to +0.8pp. Both routes agree in sign and rough
size. Note that the kill list forbids quoting this as "half of ADR growth"; it is not, and we do not.

---

## 4. Part C — the v2 geographic-mix layer

### 4.1 Theo's steer, and why it is the right one

Theo's direction: the pivotal change in Airbnb's composition is growth rotating toward lower-ADR countries and
lower-ADR travellers, which the four disclosed regional buckets cannot see *inside* each region. The repo's own
annual decomposition already leaves a jointly unidentified "pricing plus sub-regional mix" term, so the question
is well posed rather than invented.

Four upgrades were built and pre-registered under `adr_v2_geomix_prereg.md`, with **DEC-0016 restated**: the
term is measured and reported whichever way it lands, and no weight or window is chosen after seeing 4Q26 ADR.

### 4.2 The sub-regional (within-region country) term

`mix_r(t) = [Σ_c s_c(t−4)(1+g_c)P_c] / [(1+g_r) Σ_c s_c(t−4)P_c] − 1`, with country stay growth from 123 Inside
Airbnb markets vintage-matched, and USD price levels for 30 countries. The sub-regional term is the GBV-weighted
sum across regions.

Three pre-registered hypotheses, and what they returned:

- **H1, attribution: passes, but the term is fading.** Mean **−0.45pp** over 1Q23–2Q26, against a pre-registered
  line of 0.25pp. But the last four quarters to 2Q26 average only **−0.15**, and 2Q26 is −0.10.
- **H2, forecast content: FAILS.** RMSE ratios 0.909 on W1 and 0.719 on W2 against the residual carry; the
  pre-registered line was 0.75 on **both**. The term is knowable only one quarter late for history, which makes
  the v2 prediction arithmetically identical to v1. **Not promoted.** It enters as a labelled attribution and
  forward row (DEC-0038), not the base.
- **H3, forward:** with each country's growth differential to its region carried at its 2H25–1H26 average,
  the term runs **−0.137 (3Q26) to −0.147pp (4Q26)**, worth **−$0.24** on 4Q26 ADR.

The honest consequence, and it cuts against us: net of a fading mix drag, the *core* accelerates less than it
appeared to. The sub-regional data explain part of the 2026 step as a mix headwind that went away. **They do not
support a larger forward drag.**

### 4.3 Upgrade 1 — the Eurostat robustness check

The Inside Airbnb panel's footprint is not Airbnb's footprint; Europe is over-weighted toward a few scraped
cities. Re-weighting EMEA with Eurostat platform-nights instead of panel shares moves **France from 10% to 21%
of EMEA** and changes the sub-regional term by **0.02pp**. The conclusion does not rest on the scrape's
footprint. A caveat kept on record: the Eurostat-weighted and panel-weighted EMEA mix series correlate −0.30
quarter by quarter even though the aggregate barely moves.

### 4.4 Upgrade 2 — origin to destination

The letters' ex-NA nights growth split is EMEA 8 / LatAm 20 / APAC 18. Using tourism-board origin flows (NTTO,
JNTO, ABS, StatCan) to map named origin growth onto destinations gives a measurably **flatter** split:
**EMEA 10.5 / LatAm 16.4 / APAC 14.9**.

- The layer passes an ordering test against the disclosed regional buckets in **4 of 7 quarters (binomial
  p 0.018)**, and 4 of 5 on the quarters where the ordering is identified (p 0.003).
- Reproducing the letters' 8/20/18 would require the named origins to be **22% of nights against a 16.5%
  ceiling**, which is not possible.

So the steeper "tilt B" scenario is **retired** (DEC-0037), and the measured split becomes the floor rather than
the base. Tilt B would have made 4Q26 ADR lower, so retiring it is a decision taken *against* the short.

### 4.5 Upgrade 3 — reconciliation to the company's own accounting

Two independent checks.

**Annual.** Our between-region term, annualised, is **−1.10 / −1.33 / −1.67pp** for 2023–25 against the 10-K's
own mix line at **−1.08 / −1.24 / −1.58** — within 0.02 to 0.09pp in each of three years, from independent
sources.

**Pooled quarterly.** Across the 23 disclosed constant-currency regional prints, regressing the disclosed rate
minus regional accommodation inflation on our within-region mix, with region fixed effects:

| | slope | cluster-by-region p | 90% interval | n |
|---|---:|---:|---|---:|
| pooled, primary | **1.127** | 0.042 | 0.349 – 1.905 | 23 |

The identity implies a slope of 1.0 and the point estimate sits near it, but **the regression cannot test it**
(corrected 23 Sep after the audit, receipt `data/processed/pitch_model_v2/receipts/ADR_AUDIT/C4_pooled_reconciliation.md`).
With four regions as clusters the cluster-robust p-values in the table are not valid: a fully enumerated
wild-cluster bootstrap (Webb weights, 1,296 draws) gives p 0.89 against a slope of 0 and p 0.90 against 1. Of Latin
America's slope of 1.375, 1.04 (76%) comes from the Brazil hotel-CPI comparator moving inversely with the mix term
during a Brazilian stays boom (1Q25–2Q25), and only 0.36 from Airbnb's own disclosed ex-FX; with a neutral
Latin-American comparator the pooled slope is 0.24. **The quarterly reconciliation is not established.** The annual
reconciliation to the 10-K above stands, and it is the evidence for the between-region term.

The bad news is equally real and is stated in the thesis: **one region carries it.**

| leave-one-out | slope |
|---|---:|
| drop North America | 1.127 |
| drop EMEA | 1.235 |
| drop APAC | 1.247 |
| **drop Latin America** | **−0.302** |

Latin America's own comparator is Brazil alone at 24–33% coverage. And the earlier EMEA-only reading is
window-dependent: **1.085 on n 7, −0.381 on n 9** once two further disclosed quarters are admitted. So the scale
is *compatible* with the identity and *not pinned down* by anything Airbnb has published.

### 4.6 Origin composition, measured on Airbnb's own guests

Reviewer language on 53 million reviews across 123 markets is the only Airbnb-side origin object in the repo.
English fell from **71% of reviews in 2022 to 58% in 2026** on the annual series. On day-matched
last-twelve-month windows, non-English-origin guests grew **+81.0%** against **+40.0%** for English from 2024 to
2026, with English share going 62.9% → 56.8%.

On the quarterly series the y/y drop in English share has been **flat at about 2.9pp for four straight
quarters** (−2.79, −3.21, −2.73, −2.91) after running faster earlier. EMEA's English share first fell below 50% in
4Q25 (49.5%), then 46.2% in 1Q26 and 49.7% in 2Q26.

Against the filings: cross-border Portuguese runs **11.9pp above its own scope** where the filed Brazil-origin
statement runs 14pp above company nights — two independent measurements of the same excess agreeing within
about 2pp.

**What it cannot see:** Indian guests write in English, so the single largest origin story in the letters
(+50/+50/+60% y/y) is invisible to this object. That is stated rather than worked around.

---

## 5. Part D — the four mitigations of 22 September

Each was run to close a named weakness. Two closed, one narrowed, one failed. All four are reported the way they
landed.

### A — the size-mix sign, and the 10-Q search

The annual decomposition disagreed with itself on the 2025 unit-size term by a full point. The filed route gave
a **negative** 2025 size term, which would mean listings got smaller while the company reported Bedroom Nights
growing faster than nights.

**Resolved: the negative sign was a Paris-weighting artefact** of pooled aggregation. The hedonic route gives
**+0.739pp** for 2025, and it sits inside the filed bedroom-nights bracket of **[+0.42, +1.29]**. DEC-0040
proposes adopting it.

**The consequence runs against us and is stated first.** With the size term corrected, 2025 implied
like-for-like price is **2.68–2.93**, flat against 2024's 2.69–2.75, rather than the 3.93 previously carried.
So the 2026 step in like-for-like price is measured off a **flat** base and is therefore **larger**, not
smaller. The 3.93 is withdrawn.

Part 2 of the same mitigation closed the bundle search in the negative (§3.4, DEC-0041).

### B — the market-level utilisation panel: **FAILS its own pass line**

The registered test was whether a market-level price-to-utilisation elasticity could explain part of the core.
On 94 market pairs across 92 markets, with region and gap-bucket fixed effects:

| spec | b | p | 95% interval |
|---|---:|---:|---|
| primary | **+0.083** | 0.794 | −0.539 to 0.705 |
| ex-US | +0.041 | 0.956 | −1.41 to 1.49 |

The registered pass line required b > 0 and p ≤ 0.05 on both. It **fails**. The interval cannot reject 0.32 but
rules out anything above 0.7, which buys at most 0.6pp of the core, and in the *wrong* direction for a
give-back. The fix is not more analysis: it is a **September-2026 capture wave** against the September-2025 one,
which would give true same-season market pairs.

### C — pooled reconciliation

Widened the reconciliation from EMEA n 7 to 23 disclosed regional prints. Result in §4.5: compatible with the
identity, dependent on one region.

### D — origin language, priced

The geo-mix pre-registration had recorded that reviewer language gives direction but **no price**. That caveat is
now closed. Within the same market, a listing reviewed in a non-English language is **13.4% cheaper** on a
review-weighted median basis (16.7% on the weighted basis). Applying the measured rotation to that price gap,
the origin rotation alone costs about **−0.35% a year** of the price of the listing booked.

---

## 6. The numbers

### 6.1 The line

| period | base ADR | y/y | ex-FX | FX pp | band | Street | z | P(≥ Street) |
|---|---:|---:|---:|---:|---|---:|---:|---:|
| **3Q26** | **$177.68** | +3.73% | 3.316 | +0.415 | 176.01 – 179.36 | $177.06 (n 26) | +0.37 | **65%** |
| **4Q26** | **$173.03** | +3.30% | 2.784 | +0.514 | 169.80 – 176.27 | $171.33 (n 25) | +0.53 | **70%** |
| 1Q27 | $190.65 | +2.05% | 2.417 | −0.369 | 185.52 – 195.77 | none | | |
| 2Q27 | $188.38 | +2.53% | 2.957 | −0.427 | 182.41 – 194.35 | none | | |
| 3Q27 | $182.51 | +2.72% | 2.863 | −0.147 | 175.83 – 189.18 | none | | |
| 4Q27 | $178.10 | +2.93% | 2.928 | 0.000 | 171.35 – 184.85 | none | | |
| **FY26** | **$180.62** | | | | | | | |
| **FY27** | **$185.21** | +2.54% | | | | none exists | | |

GBV on the nights line: $26.08bn (3Q26), $22.81bn (4Q26), FY26 $105.29bn, FY27 $115.17bn.

Three mechanical warnings, all real:

1. **4Q27's FX of 0.000 is an artefact** of both quarters being spot-held (§2.8).
2. **3Q27 and 4Q27 chain on our own 3Q26 and 4Q26**, so any 5 November revision propagates forward.
3. **The band widens fast** — ±0.98pp in 3Q26 to ±3.90pp in 4Q27, almost all of it FX. A 2027 ADR is a
   statement about ex-FX shape plus a currency view, and the pitch must present it that way.

### 6.2 Every alternative, 4Q26, on one ladder

| construction | ex-FX | 4Q26 ADR | vs base | what you must believe |
|---|---:|---:|---:|---|
| card v3: residual carry, no lap | 3.69 | $174.55 | +1.52 | nothing lapped |
| base + fee-migration K line | 3.16 | $173.66 | +0.63 | tranche-2 reprice peaks in 4Q26 |
| base + sub-regional + measured OD tilt | 2.88 | $173.19 | +0.16 | tourism flows set the split |
| **base (mechanism)** | **2.78** | **$173.03** | — | bundle laps, core holds at 3.85 |
| base + sub-regional mix | 2.64 | $172.79 | −0.25 | country differentials persist |
| base + sub-regional + tilt B (**retired**) | 2.27 | $172.18 | −0.86 | the letters' 5/30/25 split |
| AR(1) on core | 2.39 | $172.38 | −0.66 | core decays at ρ 0.747 |
| lap-only residual steps | 1.99 | **$171.71** | −1.33 | every 2025–26 step was a product effect |
| core mean reversion | 1.33 | **$170.60** | −2.43 | the core gives back its 2026 step |
| | | **Street $171.33** | | |

**The binding negative, and it must be stated in the memo.** Composition, measured as far as the alt data allow,
runs from $172.18 to $173.19. **None of it crosses the Street.** Only assumptions about the unobserved core get
there: lap-only lands on it ($171.71, $0.38 above) and mean reversion crosses ($170.60). With the audit's corrections
(`adr_v3_corrections.md`) an AR(1) fitted on the core also crosses ($171.05) and lap-only moves to $171.61. A short that needs a below-Street 4Q26 ADR is leaning on a core
call, not a mix call, and a lodging analyst will say so within a minute of seeing the ladder.

---

## 7. What would change this line, pre-registered

### 7.1 5 November 2026 (the 3Q26 print)

- **Printed FX effect** against four numbers named in advance: **identity +0.42**, card midpoint −0.43, euro
  fit −1.12, fx_lag_v2 basket +0.44. Scored by the comparative interval rule filed 23 Sep 2026 (adr_fx_prereg.md §11). One whole-point-rounded print separates the identity from the euro fit, but not reliably from V1 (+0.03) or the basket (+0.44), so it settles §2.6 only partly.
- **Printed ex-FX** against 3.3 (base) versus 3.7 (card): at or below 3.3 the bundle lapped; at or above 3.7 it
  did not.
- **The 4Q26 ADR outlook sentence**: whether FX is named at all.
- **The eight score lines** of `adr_v2_upgrade6_sustainability_and_score.md` (DEC-0039), covering the four-region
  point, the tilt envelope, the sub-regional term, the fading claim, the within-region signs, global ex-FX, the
  ADR level, and the India-origin blindness check.

### 7.2 11 February 2027 (the 4Q26 print)

Printed FX against [−0.78, +1.97], scored by the comparative interval rule (adr_fx_prereg.md §11); ex-FX against 2.8 / 3.7 / 1.3 (base / card / mean reversion) — the first
fully lapped quarter. Also 4Q26 cost of revenue against $575M, which resolves DEC-0023 on the hosting step.

### 7.3 Any disclosure

An RNPL nights share for the same quarter as the GBV share; a per-feature bundle split; Bedroom Nights Booked
disclosed again.

---

## 8. Verification log

- FX identity closes against the disclosed effect to **≤ 0.042pp on 14 quarters**.
- Walk-forward: **0.303–0.383** at the four promotion cells, pass line 0.75, bootstrap 90% upper 0.37–0.51.
- Geo-mix method reproduces the independent H term to a mean of **0.13pp** (maximum 0.22pp) on 2Q24–2Q26,
  one-signed from 4Q24.
- Annual mix reconciles to the 10-K within **0.02–0.09pp** in each of three years.
- Price-level reproduction from raw stores: max |diff| **2.8e-14 USD** on 30 countries.
- **27 tests** pass. The workbook's `ADR_Engine` block E ties to the Python engine at **1e-12**.

---

## 9. What a lodging analyst attacks, and the honest answer

**"Your best-scoring FX variant isn't the one you use."** True. It was excluded in the pre-registration before
any score existed, it is biased −0.3pp in every window, and it is blind to the three currencies that drive the
forecast quarters. §2.6 gives the full table rather than hiding it.

**"The core is bigger than your whole ex-FX number and you can't explain it."** Correct: 3.85 against an ex-FX of
3.32 in 3Q26 and 2.78 in 4Q26 (the other terms net negative), and 1.58 of it is an unexplained 2026 step. It is
labelled that way everywhere. It is carried flat at 3.85 with its own 0.88pp one-quarter error in the band, and its full reversion
is the named downside. The mitigations made this exposure **larger**, not smaller: with 2025's size term
corrected, the 2026 step sits on a flat base. We say so rather than banking the difference.

**"Your reconciliation rests on Brazil."** Also correct. The pooled slope of 1.13 collapses to −0.30 without
Latin America, whose comparator is Brazil alone at 24–33% coverage, and the EMEA-only reading flips sign on two
more quarters. The right claim is "not established": with four clusters the regression has no valid p-value
(wild-cluster bootstrap p 0.89), and three-quarters of the Latin-American slope is Brazil's hotel CPI rather than
Airbnb's numbers. The annual 10-K reconciliation is the evidence that stands.

**"The bundle is a transcript number."** Yes. The search for a filed magnitude covers ten filed documents (FY25
10-K, three 10-Qs, five letters, the 2026 proxy, the 8-K list) and finds none. The letters name RNPL from 3Q25; the
10-Q series from 2Q26.

**"Your composition work doesn't actually get you below the Street."** It does not, and §6.2 says so on the
page. That is the most important honest statement in this line.

**"The sub-regional panel can't see India."** It cannot — no Indian, Emirati, Malaysian, Indonesian or
Vietnamese market, and one each in Thailand and Singapore. Australia is 57% of the panel's APAC stays but a far
smaller share of Airbnb's APAC nights, so the APAC within-region term is really Australia against the rest.

---

## 10. What is unbacktested, and what is open

**Unbacktested:** the lap mechanism (3Q26 is the only lapped quarter and has not printed); the core carry beyond
what its own history says; the seats term (no volumes disclosed); the 2027 FX (a currency view). The component
build loses to the naive by 1.58×, so **no component-based forecast skill is claimed** — the forecasting content
is the carry, the laps and the FX identity.

**Open items:**

1. Theo to confirm or amend DEC-0034 through DEC-0041.
2. The core-versus-residual mean in the mean-reversion scenario (§3.3), worth $0.21 on 4Q26.
3. A **September-2026 capture wave** — the only real fix for the core, and the window closes as the season turns.
4. The Bright Data Booking.com licence and any extension of the airbnb.com capture: **human decisions**, not
   ours (WP-O).
5. INEGI (Mexico) and INE Chile accommodation series, to test whether Latin America still carries the pooled
   slope once its comparator is broader than Brazil.
6. Deepening the core, in order of power: an RNPL GBV-share and nights-share pair; a same-listing realised-rate
   series; a pre-registered supply-growth term with sign and size stated first. **Not another regression on the
   residual.**

---

## 11. Decisions proposed on this line

| id | what |
|---|---|
| DEC-0034 | FX on ADR is the translation identity, promoted by the pre-registered walk-forward, replacing the card's −0.43 midpoint |
| DEC-0035 | ex-FX is the mechanism with the bundle lapping on filed dates and the core carried, labelled unobserved |
| DEC-0036 | the `ADR_Engine` sheet is line 2 of the official workbook, with `Income_Statement` rows 8–11 wired to it |
| DEC-0037 | the four-region term stays on the letter buckets, the measured origin-destination split is its floor, tilt B is retired |
| DEC-0038 | the sub-regional term is a labelled attribution and forward row, not the base (H2 failed) |
| DEC-0039 | the eight score lines of upgrade 6 are this line's falsifiers for 5 Nov and 11 Feb |
| DEC-0040 | the annual decomposition carries the hedonic size route; 2025 like-for-like price is flat and the 2026 core step is larger |
| DEC-0041 | "transcript-only" on the bundle is exhaustive and stays |

---

## 12. Provenance

| object | file | note |
|---|---|---|
| printed ADR, ex-FX, FX pp | `data/processed/overnight/02_kpi_panel_quarterly.csv` | letters; identity ≤ 0.042pp |
| daily FX | `adr_engine/fx_daily_2026-09-21.csv` | FRED H.10 through 18 Sep 2026 |
| currency baskets κ | `config.py` ← `fx_lag_v2/01b_basket_weights_used.csv` | judgement, frozen pre-fit |
| regional GBV shares | `data/processed/adr/01_regional_annual.csv` | 10-K, point-in-time via `knowable_from` |
| walk-forward, scores, posterior, forecast | `fx_pit_walkforward.csv`, `fx_scores.csv`, `fx_weights_posterior.csv`, `fx_forecast_asof.csv` | engine |
| ex-FX history | `data/processed/q3nowcast/H/adr_history_components.csv` | H decomposition |
| measured 3Q26 terms | `data/processed/adrq3/I/I_mix_terms_3q26.csv` | card v3 |
| bundle sizing | ledger D014, D032 | transcript-only, labelled |
| residual steps, K4 | `data/processed/adrv3/K/K4_residual_nowcast.csv` | |
| regional shares and ADR levels | `data/processed/adr/04_regional_quarterly_wide.csv` | disclosed-chained |
| nights line regional path | `lines/nights_v2_design.md` §2.1 | DEC-0028/0029 |
| sub-regional inputs | `refresh_prices.py` ← Inside Airbnb capture store | 123 markets, 30 priced countries |
| origin-destination flows | `od_layer.py` ← NTTO, JNTO, ABS, StatCan | |
| mitigation outputs | `sizemix_rebased_plug.csv`, `market_panel_scores.csv`, `reconcile_pooled_regressions.csv`, `origin_lang_*.csv` | |
| Street | Bloomberg MODL 12 Sep 2026, V1 dossier | 3Q26 n 26, 4Q26 n 25 |
| workbook | `model/ABNB_official_model.xlsx` sheet `ADR_Engine`, blocks A–G | `workbook.py` |
| figures | `figures/adr_full_logic.png`, `adr_geomix_logic.png` (six panels), + 7 singles | PNG + SVG |

---

## 13. Model inputs (machine-readable)

| item | scenario | period | point | unit | note |
|---|---|---|---|---|---|
| adr_total_usd | base | 3Q26 | 177.68 | USD | 171.29 × 1.03731 |
| adr_yoy_reported_pct | base | 3Q26 | 3.731 | pct | ex-FX 3.316 + FX 0.415 |
| adr_exfx_yoy_pct | base | 3Q26 | 3.316 | pct | |
| adr_fx_pp | base | 3Q26 | 0.415 | pp | spot held, 87.9% printed |
| adr_total_usd_lo | base | 3Q26 | 176.01 | USD | band half 0.978pp |
| adr_total_usd_hi | base | 3Q26 | 179.36 | USD | |
| adr_total_usd | base | 4Q26 | 173.03 | USD | 167.51 × 1.03298 |
| adr_yoy_reported_pct | base | 4Q26 | 3.298 | pct | ex-FX 2.784 + FX 0.514 |
| adr_exfx_yoy_pct | base | 4Q26 | 2.784 | pct | |
| adr_fx_pp | base | 4Q26 | 0.514 | pp | P10 −1.06, P90 +2.26 |
| adr_total_usd_lo | base | 4Q26 | 169.80 | USD | band half 1.932pp |
| adr_total_usd_hi | base | 4Q26 | 176.27 | USD | |
| adr_total_usd | base | 1Q27 | 190.65 | USD | ex-FX 2.417, FX −0.369 |
| adr_total_usd | base | 2Q27 | 188.38 | USD | ex-FX 2.957, FX −0.427 |
| adr_total_usd | base | 3Q27 | 182.51 | USD | ex-FX 2.863, FX −0.147 |
| adr_total_usd | base | 4Q27 | 178.10 | USD | ex-FX 2.928, FX 0.000 (artefact) |
| adr_total_usd | base | FY26 | 180.62 | USD | nights-weighted |
| adr_total_usd | base | FY27 | 185.21 | USD | nights-weighted, 621.85m nights |
| adr_yoy_reported_pct | base | FY27 | 2.544 | pct | |
| adr_total_usd | street | 3Q26 | 177.06 | USD | MODL 12 Sep 2026, n 26 |
| adr_total_usd | street | 4Q26 | 171.33 | USD | MODL 12 Sep 2026, n 25 |
| p_print_ge_street | base | 3Q26 | 0.645 | prob | |
| p_print_ge_street | base | 4Q26 | 0.701 | prob | |
| subgeo_pp | attribution | 3Q26 | −0.137 | pp | DEC-0038, not in base |
| subgeo_pp | attribution | 4Q26 | −0.147 | pp | worth −$0.24 on ADR |
| adr_total_usd | sub_regional | 4Q26 | 172.79 | USD | composition alternative |
| adr_total_usd | measured_od_tilt | 4Q26 | 173.19 | USD | composition alternative |
| adr_total_usd | lap_only | 4Q26 | 171.71 | USD | core assumption, below Street |
| adr_total_usd | core_mean_reversion | 4Q26 | 170.60 | USD | named downside (see §3.3) |
| adr_total_usd | core_mean_reversion | 3Q26 | 175.20 | USD | |
| gbv_busd | base | 3Q26 | 26.08 | USD bn | nights line 146.8m |
| gbv_busd | base | 4Q26 | 22.81 | USD bn | nights line 131.8m |
| gbv_busd | base | FY26 | 105.29 | USD bn | |
| gbv_busd | base | FY27 | 115.17 | USD bn | |
