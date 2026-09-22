# ADR line, version 1 — design (the full logic)

**21–22 September 2026, overnight session (autonomous; Theo asleep).** Governing construction for line 2 of the
official model. Proposed decisions **DEC-0034** (FX-on-ADR = translation identity, pre-registered and promoted),
**DEC-0035** (ex-FX ADR = mechanism with the product bundle lapping on filed dates) and **DEC-0036** (line 2 in the
workbook), all **pending Theo's confirmation**. Rationale file: [`final_adr.md`](final_adr.md). Pre-registration
(fixed before any fit, blob `0495e5f3`): [`adr_fx_prereg.md`](adr_fx_prereg.md). Engine:
`analysis/src/pitch_model_v2/adr_engine/` (README there; `run.py` rebuilds everything, exit 0, 10 tests).
Research inputs, archived verbatim: `dossiers/ADR_A_disclosure_ledger.md` (what management said, dated),
`ADR_B_fx_translation_inventory.md` (every FX object in the repo), `ADR_C_exfx_mechanism_inventory.md` (every
ex-FX series). Branch `theo/pitch-model-v2`, base HEAD `2a77a36`. Web fetches: **zero** (FRED H.10 CSV only).

The composite figure of the whole logic is [`figures/adr_full_logic.png`](figures/adr_full_logic.png); the six
individual figures are listed in §11.

---

## 1. The claim, in one paragraph

Reported ADR growth is two things added together, and Airbnb discloses both halves every quarter: an ex-FX
(constant-currency) growth rate and an FX effect (`adr_history_components.csv` `identity_check_pp` ≤ 0.042pp in
all 14 quarters). **The FX half is a translation identity, not a forecast problem**: GBV is booked in USD at the
booking-date rate, so the FX effect on ADR is the year-on-year change of the booking-quarter average exchange
rate, weighted by the currency mix of GBV. Built from the 10-K regional GBV shares and the repo's frozen
destination-currency baskets, **with zero fitted parameters**, that identity beats the naive carry by a factor
of three at day 60 and pre-print on both scoring windows, point in time, against the 17 quarters Airbnb has
disclosed (RMSE ratio 0.34 / 0.30 on W1, 0.38 / 0.32 on W2; bootstrap upper bounds 0.44–0.51; pass line 0.75).
It puts 3Q26 ADR-FX at **+0.42pp with 88% of the quarter already printed**, against the committed card's
−0.43pp, a 0.85pp difference that is worth $1.45 of ADR and about $215M of 3Q26 GBV. **The ex-FX half is a
disclosed-mechanism construction, not a regression**: the like-for-like residual the card carries flat (4.85pp)
is split into the product bundle's ADR contribution as management sized it (~1pp, 4Q25 and 1Q26 calls) and a
core host-pricing rate (3.85pp); the bundle's two legs lap on the nights line's own filed anniversaries (US RNPL
in 3Q26, cancellation redesign and single fee in 4Q26), geographic mix is computed from the nights line's own
regional path and the 10-K regional ADR levels (it reproduces the H term within 0.13pp on 2Q24–2Q26), and the
measured mix terms are carried as the card carries them. Base: **3Q26 $177.68 (+3.7%), 4Q26 $173.03 (+3.3%),
FY27 $185.21 (+2.5%)**; Street (Bloomberg MODL, 12 Sep) $177.06 and $171.33; P(print ≥ Street) 65% and 70%.
The ADR line is therefore **on the Street in 3Q26 and 1.0% above it in 4Q26**, for two reasons the pitch can name:
FX is positive not negative, and the bundle lap takes 0.5pp out in 3Q26 and 1.0pp out from 4Q26 — a
deceleration in ex-FX ADR (3.3 → 2.8 → 2.4) that the Street's 4Q26 ADR (+2.3%) already more than prices.
The one unobserved line — the core at 3.85pp, 1.5pp above its 2023–25 mean — is labelled as such, carried with
its own historical error in the band, and its mean-reversion case (−$2.5 of ADR, −$0.35bn of GBV a quarter) is
the named downside.

---

## 2. The identity, and the FX engine (the half that is tested)

### 2.0 What Airbnb discloses and how it is computed

- 10-K: *"The entire amount of a booking is reflected in GBV during the quarter in which booking occurs"*; ADR =
  GBV ÷ Nights and Seats Booked. Both booking-dated. **No lag.** Revenue FX lags (check-in recognition, kernel
  Φ); ADR FX does not — `fx-lag.md` §4 and X1 §3 established this on 18 Sep, and this engine never applies Φ to
  an ADR quantity.
- Letters, Constant Currency section: *"current period foreign currency amounts are translated using the exchange
  rates of the comparative period."* → prior-year rates. The constant-currency ADR/GBV disclosure exists **only in
  the letters**; the 10-K/10-Q constant-currency sections cover revenue only (ledger A §3).
- **Hedges are designated against revenue only** (10-K: cash-flow hedging program "to minimize the effects of
  foreign currency fluctuations on future revenue", initiated 1Q23, typically up to 18 months). The ADR-FX
  disclosure is gross of hedging. The cleanest proof the objects differ: 2Q25 call, same speaker, 3Q25 guide —
  revenue FX "minimal… after factoring in our hedges", ADR "primarily driven by FX".
- The target series: 17 quarters, 2Q22–2Q26, `fx_pts_adr` = unrounded reported ADR y/y − the letter's whole-point
  ex-FX figure: −5.6, −7.1, −5.5, −2.8, −0.6, +2.7, +2.1, +0.6, −0.9, −0.6, −1.1, −1.9, +1.9, +2.7, +2.9, +5.0, +1.3.
  Two quarters (3Q23, 4Q23) say "less than 1%" and are carried as 0.5 ± 0.25; the rest ± 0.5 (rounding). Every
  score below is therefore read against a **resolution floor of ~0.3pp**.

### 2.1 The identity

```
FX_pp(t)  =  100 · Σ_c ω_c · [ ē_c(t) / ē_c(t−4) − 1 ]          ω_c = Σ_r g_r · β_r · κ_{r,c}
```

`ē_c` = business-day mean of the FRED H.10 rate (USD per unit) over the quarter; `g_r` = 10-K regional GBV share
(FY2025: NA 44.1 / EMEA 37.4 / LatAm 9.4 / APAC 9.1%; earlier years point in time); `κ` = the repo's frozen
destination-currency baskets (NA USD .90 CAD .08 MXN .02; EMEA EUR .70 GBP .25 USD .05; LatAm BRL .55 MXN .38 USD
.07; APAC AUD .55 JPY .20 KRW .10 INR .07 USD .08); `β_r` = 1 in the promoted variant. The resulting currency
weights on GBV: EUR 26.2%, GBP 9.4%, BRL 5.1%, AUD 5.0%, MXN 4.4%, CAD 3.5%, JPY 1.8%, KRW 0.9%, INR 0.6%; USD
43.0%. **Non-USD 57%** — close to the 10-K's 56% non-USD *revenue* share (a revenue figure; the non-USD GBV share
is not disclosed, ledger B §4).

### 2.2 Point-in-time protocol and the pre-registered pass line

Three origins per target quarter — **O1** the day before the quarter starts (none of the quarter's rates seen),
**O2** day 60 (~59% of business days printed after the H.10 one-week lag), **O3** the day before the print (all
printed). Information set: FRED prints dated ≤ origin − 7 days; disclosed points printed ≤ origin; the latest
10-K shares knowable ≤ origin. Unobserved days held at the last print (spot held). Windows W1 (targets 1Q23–2Q26,
n 14) and W2 (1Q24–2Q26, n 10). Naive = the latest disclosed FX pp at the origin. **Pass line, fixed before the
run: point-RMSE ratio to naive ≤ 0.75 at O2 and O3 on both windows.** V1 (fitted pass-through, prior N(1, 0.25²),
interval likelihood) is promoted over V0 only if strictly lower on all four cells.

### 2.3 Results (`fx_scores.csv`, figure `adr_fx_walkforward`)

| variant (fitted parameters) | W1 O1 | W1 O2 | W1 O3 | W2 O1 | W2 O2 | W2 O3 | verdict |
|---|---|---|---|---|---|---|---|
| **V0 translation identity (0)** | 0.44 | **0.34** [0.27, 0.44] | **0.30** [0.25, 0.37] | 0.63 | **0.38** [0.29, 0.51] | **0.32** [0.23, 0.42] | **promoted** |
| V1 fitted pass-through (4) | 0.50 | 0.38 | 0.34 | 0.67 | 0.35 | 0.29 | passes, not lower on W1 |
| V2 euro-only OLS (2) — the card's left leg | 0.40 | 0.27 | 0.28 | 0.53 | 0.27 | 0.27 | comparator; bias −0.3 to −0.5 |
| V3 broad-dollar OLS (2) | 0.59 | 0.53 | 0.52 | 0.76 | 0.60 | 0.57 | comparator |
| zero | 0.74 | 1.08 | 1.08 | 0.97 | 1.16 | 1.16 | — |

RMSE in pp for V0: 1.31 / 0.72 / 0.64 (W1), 1.47 / 0.75 / 0.62 (W2); naive 3.00 / 2.11 and 2.36 / 1.97.
Rounding-fair interval RMSE at O3: 0.27 / 0.25pp — the floor. Bias at O3 +0.15 / −0.04. Brackets are moving-block
bootstrap 90% intervals of the ratio (block 4, 2,000 draws). Sensitivity: revenue shares instead of GBV shares
→ 0.35 / 0.31 and 0.39 / 0.33, unchanged. Three things to say out loud:

1. **Even at quarter start (O1)** — with none of the quarter's FX observed — the identity beats the naive carry
   (0.44 / 0.63), because the year-ago base quarter and last year's currency moves are already in the number.
   That is the honest basis for the 2 October pitch's 4Q26 FX figure.
2. The euro-only fit has the lowest point RMSE but is **biased low by 0.3–0.5pp** in every cell: it has no
   channel for the LatAm and APAC currencies that carry the 2024–26 divergence. Its half-weight in the committed
   midpoint is why the card's 3Q26 leg is −0.43 when the identity says +0.42.
3. The identity's 2022 residuals are all one-signed (it under-predicts the dollar surge by about a third) —
   evidence that the nine bilaterals under-cover EMEA/APAC exposure in a broad-dollar move. The posterior on
   the pass-through (§2.4) measures that; the walk-forward says fitting it does not pay out of sample.

### 2.4 What 17 quarters say about exposure beyond the baskets (`fx_weights_posterior.csv`, figure `adr_fx_passthrough_posterior`)

PyMC NUTS, 4 chains × 1,500, R̂ 1.00, interval likelihood, prior N(1, 0.25²) per region:

| region | posterior β | 90% interval | P(β > 1) | reading |
|---|---|---|---|---|
| North America | 0.99 | [0.59, 1.40] | 0.49 | the basket is 90% USD; unidentified, as the repo's WS10 found |
| EMEA | **1.20** | [1.09, 1.31] | **0.996** | exposure ~20% above EUR+GBP: CHF, SEK, NOK, PLN, TRY and the euro-linked periphery move with the euro and more |
| Latin America | **0.46** | [0.17, 0.78] | **0.006** | half pass-through: USD-indexed pricing in Mexico and Argentina, cross-border USD guests, hosts repricing in dollar terms |
| Asia Pacific | 1.27 | [0.88, 1.64] | 0.87 | mildly above one; wide |
| σ (model error) | 0.53pp | [0.31, 0.84] | | consistent with the rounding floor |

These are **descriptive** (all 17 quarters, in sample) and are not the leg: the pre-registered rule keeps V0
because V1 is not lower on both windows. They are the analyst-grade explanation of *where* the identity's small
misses come from, and they are what a 5 November print will test (§9).

### 2.5 The ex-ante forecast (`fx_forecast_asof.csv`, figure `adr_fx_currency_contributions`)

Spot held from the last FRED print (18 Sep 2026); band = moving-block bootstrap (block 20 business days, 4,000
paths, demeaned joint daily log returns 2015→) on the days still unobserved at each as-of date.

| as of | 3Q26 | 4Q26 | 1Q27 | 2Q27 | 3Q27 | 4Q27 |
|---|---|---|---|---|---|---|
| **21 Sep 2026** (this build) | **+0.42** [0.36, 0.48], 88% printed | **+0.51** [−1.06, +2.26] | −0.37 [−3.20, +2.78] | −0.43 [−3.90, +3.68] | −0.15 [−4.34, +4.86] | 0.00 [−4.34, +5.12] |
| 2 Oct (memo) | +0.42 [0.38, 0.45] | same | same | same | same | same |
| 5 Nov (3Q26 print) | printed | +0.51 [−0.78, +1.97], 32% printed | same | same | | |
| 11 Feb 2027 (4Q26 print) | | printed | −0.37 [−2.20, +1.72], 39% printed | same | | |
| ±5% USD device (D5) | +0.76 / +0.07 | +3.39 / −2.36 | +2.46 / −3.20 | +2.40 / −3.26 | | |

Where 3Q26's +0.42 comes from, at FY2025 GBV weights (currency y/y of the quarterly average, contribution):
EUR −1.5% → −0.38pp; GBP −0.2% → −0.02; **MXN +8.2% → +0.37; BRL +6.1% → +0.31; AUD +8.1% → +0.40**; CAD −1.5%
→ −0.05; JPY −7.3% → −0.13; KRW −2.3% → −0.02; INR −8.7% → −0.05. The euro is a drag; the peso, real and
Australian dollar are the tailwind. An estimator with no LatAm/APAC channel cannot see this quarter. 4Q26
(+0.51): EUR −0.40, MXN +0.27, BRL +0.24, AUD +0.41, GBP +0.05, KRW +0.04, CAD −0.02, JPY −0.03, INR −0.04.
**4Q27 is 0.00 by construction** (its base quarter 4Q26 is also entirely spot-held); the band is the honest
content of that cell.

**The 3Q26 tell (filed, qualitative):** the 2Q26 letter's 3Q26 ADR outlook names "mix shift and price
appreciation" and, for the first time since 1Q25, **does not name FX**, while the revenue outlook in the same
letter carries "an approximate three percentage point FX tailwind after factoring in our hedging program". Both
the identity (+0.42) and the card (−0.43) are "near zero" against that sentence; the print will separate them.

---

## 3. The ex-FX mechanism (the half that is constructed)

### 3.0 The identity and the honest state of its terms

```
exFX_yoy(t) = core(t) + bundle(t) + geo_mix(t) + unit_size(t) + los_mix(t) + seats(t) + interaction(t)  [+ fee_K(t) = 0 in base]
```

The five mix/dilution terms are the H decomposition's (`adr_history_components.csv`, 1Q23–2Q26) and the card's
measured 3Q26 terms (`I_mix_terms_3q26.csv`), carried forward exactly as the card carries them (J3 convention).
The repo's record on them is negative and must be stated: **the H component build loses to the naive carry
(RMSE ratio 1.58, `adr_exfx_backtest.csv`, biased −1.4 to −2.3pp in every acceleration)**; unit size loses at
4.2–5.5× (r −0.17 vs ex-FX ADR); geo mix 1.1–1.3×; only LOS (0.88, r −0.13, p 0.69) and the letter-bucket geo
term (0.22, n 7) do not lose (ledger C §3). That is why card v3 abandoned the build for a residual *rule*. This
design keeps the identity for what it is good for — **attribution and mechanics** — and puts the forecasting
content where the record says it lives: the residual's carry, the bundle's dated laps, and the FX identity.

### 3.1 History: the residual split into bundle and core

| quarter | ex-FX (letter) | geo | unit | LOS | seats | inter. | **residual** | bundle live | **core** |
|---|---|---|---|---|---|---|---|---|---|
| 1Q23 | 3.0 | −1.35 | 0.46 | 0.46 | 0 | −0.05 | 3.48 | 0 | 3.48 |
| 2Q23 | 2.0 | −0.90 | 0.36 | 0.12 | 0 | −0.05 | 2.47 | 0 | 2.47 |
| 3Q23 | 0.5 | −1.17 | 0.41 | 0.30 | 0 | −0.05 | 1.01 | 0 | 1.01 |
| 4Q23 | 0.5 | −0.94 | 0.29 | 0.36 | 0 | −0.05 | 0.83 | 0 | 0.83 |
| 1Q24 | 2.0 | −1.33 | 0.96 | 0.21 | 0 | −0.11 | 2.26 | 0 | 2.26 |
| 2Q24 | 3.0 | −1.13 | 0.77 | 0.23 | 0 | −0.11 | 3.23 | 0 | 3.23 |
| 3Q24 | 2.0 | −1.12 | 0.89 | 0.25 | 0 | −0.11 | 2.08 | 0 | 2.08 |
| 4Q24 | 2.0 | −1.79 | 0.71 | 0.43 | 0 | −0.11 | 2.76 | 0 | 2.76 |
| 1Q25 | 1.0 | −1.89 | 0.67 | 0.28 | −0.18 | −0.11 | 2.23 | 0 | 2.23 |
| 2Q25 | 1.0 | −1.70 | 0.73 | 0.35 | −0.18 | −0.11 | 1.91 | 0 | 1.91 |
| 3Q25 | 2.0 | −1.59 | 0.75 | 0.31 | −0.18 | −0.11 | 2.82 | **0.51** (RNPL US) | 2.31 |
| 4Q25 | 3.0 | −1.46 | 0.82 | 0.22 | −0.18 | −0.11 | 3.70 | **1.00** | 2.70 |
| 1Q26 | 4.0 | −1.04 | 0.95 | 0.30 | −0.48 | −0.10 | 4.38 | 1.00 | 3.38 |
| 2Q26 | 4.0 | −1.27 | 0.70 | 0.30 | −0.48 | −0.10 | **4.85** | 1.00 | **3.85** |

The residual is the one unobserved line (D4 §2). Its 2023–25 mean is 2.40; it stepped to 4.4–4.9 in 1H26. The
split assigns **~1pp** of that level to the product bundle (§3.2) and leaves the rest — the core — at **3.85**,
still 1.45pp above its 2023–25 mean. **That gap is the unexplained half of the 2026 step, and it stays
unexplained here**: the design carries it, labels it, bands it with its own history, and names its reversion
as the downside. It does not dress it as a mechanism.

### 3.2 The bundle: what management sized, and the lap calendar

Management's only arithmetic on the bundle's ADR effect is on the calls (ledger A §2.1, **transcript-only**,
neither figure in any 8-K exhibit, 10-Q or the 10-K — X3): 4Q25 call, *"over 200 basis points of growth in nights
booked and roughly 300 basis points of growth in GBV"* (D014) and 1Q26 call, *"approximately three points of
nights booked growth and approximately four points of GBV growth"* (D032) — a GBV-minus-nights gap of **≈ 1pp of
ADR in each quarter**. The three features (D015): Reserve Now Pay Later, the cancellation-policy redesign, the
single fee. No per-feature split has ever been given. Filed substitutes that sit beside the mirror numbers: the
1Q26 letter's *"roughly 20% of global GBV came from Reserve Now, Pay Later bookings"* (a share, not a
contribution) and the 2Q26 10-Q MD&A: *"The increase in ADR was driven in part by the continued adoption of
RNPL"* — the only SEC-filed sentence naming RNPL as an ADR driver.

Sizing rule (assumed, stated): total **1.0pp** (the two quarters agree; band 0.8–1.2). Split by the residual's own
dated steps — K4's "residual steps" of +0.92 at 3Q25 (US RNPL live alone) and +0.88 at 4Q25 (cancellation
redesign + fee tranche 1) — so the **RNPL-NA leg is 0.51pp** (mix into larger entire homes: the NA paragraph says
so every quarter from 4Q25, "particularly listings with 4 or more bedrooms") and the **fee/cancellation leg is
0.49pp** (the host reprice: K2's payout-neutral arithmetic gives 0.5–0.8% on the migrated cohort). The ex-NA RNPL
leg (live 17 Feb 2026) is **0 in base**, because the 1Q26 "~1" did not rise above 4Q25's "~1" when it went live;
its high alternative is the 1H26 residual steps, 1.15pp, lapping in 1H27 ("full lap" row, §3.6).

| leg | live from | laps | 3Q26 | 4Q26 | 1Q27+ | source of the date |
|---|---|---|---|---|---|---|
| RNPL, North America (larger-home mix) | Aug 2025 (3Q25 letter, D008 filed) | **3Q26** | 0 | 0 | 0 | same calendar as the nights line |
| cancellation redesign + single fee tranche 1 | Oct 2025 global (D060, D013/D024 filed; two tranches inside 4Q25) | **4Q26** | 0.49 | 0 | 0 | same |
| RNPL ex-NA | 17 Feb 2026 (D025 filed) | 1Q27 (0.40 phase) / 2Q27 | 0 (base) | 0 | 0 (base) | same |
| single fee tranche 2 (K line) | Jul 2026 → 13 Oct 2026 | peaks 4Q26, laps 4Q27 | 0 (DEC-0008) | 0 | 0 | sensitivity: +0.17 / +0.38 |
| **bundle live, base** | | | **0.49** | **0.00** | **0.00** | |

So the residual goes **4.85 (2Q26) → 4.34 (3Q26) → 3.85 (4Q26 onward)**: the card's carry minus the laps. K4's own
"lap only, disclosed bundle ADR contribution" row lands at the same 3.85 for 4Q26 by a different route.

### 3.3 Geographic mix, from the nights line

The mix term is share-shift arithmetic at constant regional prices: `geo = [Σ s_r (1+g_r) ADR_r] / [(1+g_tot)
Σ s_r ADR_r] − 1`, base-quarter shares and anchored regional ADR levels from `04_regional_quarterly_wide.csv`
(disclosed-chained; FY2025 10-K levels NA $255 / EMEA $159 / LatAm $95 / APAC $118), regional growth from the
nights line: NA from `nights_v2_design.md` §2.1 (5.60 / 3.31 / 2.31 …) and ex-NA (11.62 / 10.06 / 10.63 / 7.42 /
7.81 / 7.51, the line's total less NA at the line's own share) split across EMEA / LatAm / APAC by the 2Q26
letter's bucket pattern (8 / 20 / 18) scaled each quarter. **Method check** (`geo_mix_method_check.csv`): the
same arithmetic on the disclosed bucket midpoints reproduces the H term to a mean absolute 0.13pp (max 0.22) on
2Q24–2Q26; it diverges in 2023 (the panel's 2023 buckets are wide), which is the method's stated limit.

| quarter | NA | EMEA | LatAm | APAC | ex-NA | **geo mix, pp** | card (E stays split) |
|---|---|---|---|---|---|---|---|
| 3Q26 | 5.60 | 7.08 | 17.70 | 15.93 | 11.62 | **−1.29** | −1.43 |
| 4Q26 | 3.31 | 6.32 | 15.79 | 14.21 | 10.06 | **−1.34** | −1.43 |
| 1Q27 | 2.31 | 6.53 | 16.33 | 14.70 | 10.63 | **−1.62** | −1.43 |
| 2Q27 | 2.31 | 4.67 | 11.68 | 10.51 | 7.42 | **−1.08** | −1.43 |
| 3Q27 | 2.31 | 4.67 | 11.68 | 10.51 | 7.81 | **−1.17** | −1.43 |
| 4Q27 | 2.31 | 4.64 | 11.59 | 10.43 | 7.51 | **−1.11** | −1.43 |

This is the link an analyst will look for: **the nights line's ex-NA growth is the ADR line's mix drag.** Every
point of LatAm/APAC outgrowth at a third of North America's ADR costs the blended ADR; 1Q27's −1.62 is the
Middle East lap (+1.0pt of ex-NA nights) showing up as mix.

### 3.3b The sub-regional layer and the composition lever (added 22 Sep, `adr_v2_geomix_prereg.md`)

Theo's thesis is that growth is shifting toward lower-ADR countries. Two objects now measure it. **(a) The
four-region term already carries the disclosed part**: at 3Q25 regional ADRs, one point of nights share moving from
North America to Latin America is **−0.89pp** of blended ADR, to Asia Pacific −0.78, to EMEA −0.51; the base pattern
(EMEA 8 / LatAm 20 / APAC 18) gives −1.34pp in 4Q26, a tilt to LatAm 30 / APAC 25 / EMEA 5 (the shape the
India +60% and Brazil +31% origin statements imply, same ex-NA total) gives **−1.70**, a Europe-led tilt −1.08
(`geo_mix_tilt_sensitivity.csv`). **(b) The sub-regional layer** — country mix inside each region, from the
123-market stays panel and June-2026 listed prices in USD for 30 countries — averaged **−0.45pp** over 1Q23–2Q26
but has faded to −0.15 over the last four quarters (APAC −9 → −1 as reopening ended; NAM −0.5 with Canada at
0.70× US prices; EMEA **+0.4** in 2Q26 with the UK, Ireland and the Netherlands outgrowing France and Portugal);
its forward rule gives −0.13 to −0.18pp, worth −$0.24 on 4Q26 ADR. Net of it, the 2026 step in like-for-like
price is 1.1pp, not 1.45. **What the panel cannot see** is the destination side of the Indian and Brazilian
origin growth (no Indian, Emirati or Indonesian market; one each in Thailand and Singapore) and origin mix inside
a destination; those channels live in the four-region buckets, i.e. in (a). The two scenarios are carried beside
the base in §3.6 and in the workbook: sub-regional adds −$0.24 to 4Q26; sub-regional plus tilt B adds −$0.84
($172.19) — still above the Street's $171.33. Composition alone does not get below the Street; the core has to.
**Origin evidence, descriptive:** reviewer language across the 123 markets (figure `adr_origin_language_shares`) —
English 71% of reviews in 2022 → 58% in 2026; Spanish 11 → 16%, Portuguese 1.8 → 3.5%, East-Asian 1.1 → 2.8%;
2025 growth Portuguese +45%, Spanish +37% vs English +17%. It is the composition change on Airbnb's own guests and
supports tilt B's direction; it carries no price and does not enter the term (`adr_v2_geomix_prereg.md` §4).

### 3.3c The four upgrades, 22 Sep (results; notes `adr_v2_upgrade1/2/3/6_*.md`, thesis `adr_v2_thesis.md`)

1. **Eurostat weights (upgrade 1).** Re-weighting the within-EMEA mix with Eurostat platform nights by country moves
   the weights a lot (France 10 → 21% of EMEA, Ireland 6 → 1%, Italy 24 → 16%) and the term almost not at all: EMEA
   mix mean −0.11 → −0.05pp, the sub-regional term −0.45 → −0.43 over 1Q23–2Q26, 4Q26 effect −$0.25 → −$0.27. The
   countries that gain weight sit near the EMEA mean price. The module reproduces the original build to 1e-14 as its
   control. **The term does not rest on the scrape footprint.** The price basis (median vs review-weighted) matters
   more than the weights (up to −$0.19).
2. **Origin → destination (upgrade 2).** The tourism-board files (NTTO, JNTO, ABS, StatCan; Eurostat carries no
   residence split) show the named origins' growth entirely ex-NA (India into the US −8% vs Airbnb +60%; Brazil −3%
   vs +31%), Canada's and Australia's US shares falling — and an implied ex-NA split of **EMEA 10.5 / LatAm 16.4 /
   APAC 14.9**, flatter than the letters' 8 / 20 / 18. Priced, the four-region term is −1.03 / −1.10 / −1.34 / −0.90
   (3Q26–2Q27) vs the base −1.29 / −1.34 / −1.62 / −1.08, i.e. +0.24pp on 4Q26. **Tilt B is retired**: reproducing
   8 / 20 / 18 from origin growth alone needs the named origins at 22% of global nights against a ceiling of 16.5%.
   Validation is cross-sectional only: ordering test 4 of 7 quarters (p 0.018; 4 of 5 identified, p 0.003); no
   time-series content (r 0.2 to −0.25, n 7). The India → EMEA vs APAC split is unidentified (bound 0–40% EMEA)
   and moves the priced term 0.03pp; the binding unknown is the undisclosed origin size weights (8.5–16.5%).
3. **Reconciliation (upgrade 3).** Annual: our four-region term −1.10 / −1.33 / −1.67 vs the 10-K's −1.08 / −1.24 /
   −1.58 (2023–25), 0.02–0.09pp apart from independent sources; our sub-regional term (−0.86 / −0.36 / −0.30) sits
   inside the 10-K's "pricing + sub-regional mix" plug (2.48 / 2.80 / 3.62), 8% of it in 2025, and being negative it
   *raises* the implied like-for-like price (3.34 / 3.15 / 3.93). Quarterly EMEA: disclosed ex-FX minus
   panel-weighted accommodation CPI regressed on our mix gives slope 1.09 (identity 1.0), r 0.48, n 7, p 0.27 —
   right sign and scale, not significant; residual mean +0.65pp, sd 0.72; zeroing the mix worsens the fit (sd 0.72
   → 0.83). Found: the 10-K route's 2025 size-mix term is −0.25 vs the H route's +0.74 — a 1pp sign disagreement to
   adjudicate; rebased on our size/LOS the implied price is flat 2024–25 (2.69 / 2.68).
4. **Sustainability (upgrade 6).** `refresh_prices.py` rebuilds the term's inputs from the raw stores in 14 s
   (reproduces `country_price_levels_usd.csv` to 1e-14); `run.py` has a `geomix` stage that verifies every table
   against disk before overwriting; 27 tests; eight pre-registered pass/fail lines for 5 Nov and 11 Feb
   (`adr_v2_upgrade6_sustainability_and_score.md`).

**Net effect on the line.** The base keeps the letter buckets (disclosed) with the measured origin-destination
split as its floor; the composition case for 4Q26 runs **$172.79 (sub-regional) to $173.19 (sub-regional + measured
tilt)** around the base $173.03; tilt B ($172.18) is retired. Composition, measured as far as the git allows, does
not put 4Q26 below the Street's $171.33.

### 3.4 The other terms, carried as the card carries them

Unit size / party size **+0.797pp** (booked capacity per reviewed stay +1.35% y/y on 2.05m vintage-matched
reviews, 119 markets, × 0.592 hedonic; band 0.53–1.00; the 7 Sep 29-market measurement gives +0.63); length of
stay **+0.056** (band −0.08 to +0.29); seats / new business **−0.483** in 2026 and **−0.565** in 2027 (assumed
volumes, `15_seats_dilution`); interaction **−0.10**. The filed size read is the 2Q26 letter's new metric —
**Bedroom Nights Booked +12% vs nights +10%** — which at the measured bedroom elasticity of 0.23 is +0.5 to
+0.8pp of ADR, not the "half of ADR growth" on the kill list.

### 3.5 The base path

| quarter | core | bundle | residual | geo | unit | LOS | seats | inter. | **ex-FX** | FX (§2.5) | **reported** |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 3Q26 | 3.85 | 0.49 | 4.34 | −1.29 | 0.80 | 0.06 | −0.48 | −0.10 | **3.32** | +0.42 | **+3.73%** |
| 4Q26 | 3.85 | 0 | 3.85 | −1.34 | 0.80 | 0.06 | −0.48 | −0.10 | **2.78** | +0.51 | **+3.30%** |
| 1Q27 | 3.85 | 0 | 3.85 | −1.62 | 0.80 | 0.06 | −0.57 | −0.10 | **2.42** | −0.37 | **+2.05%** |
| 2Q27 | 3.85 | 0 | 3.85 | −1.08 | 0.80 | 0.06 | −0.57 | −0.10 | **2.96** | −0.43 | **+2.53%** |
| 3Q27 | 3.85 | 0 | 3.85 | −1.17 | 0.80 | 0.06 | −0.57 | −0.10 | **2.86** | −0.15 | **+2.72%** |
| 4Q27 | 3.85 | 0 | 3.85 | −1.11 | 0.80 | 0.06 | −0.57 | −0.10 | **2.93** | 0.00 | **+2.93%** |

### 3.6 Alternatives, carried beside the base and never blended (`adr_scenarios.csv`)

| rule | 3Q26 ex-FX / ADR $ | 4Q26 ex-FX / ADR $ | 1Q27 ex-FX | 2Q27 ex-FX | what it assumes |
|---|---|---|---|---|---|
| **base: core carry + bundle laps** | **3.32 / 177.68** | **2.78 / 173.03** | 2.42 | 2.96 | management's ~1pp laps on its dates; core stays at 3.85 |
| card v3: residual carry, no lap (DEC-0008/9) | 3.69 / 178.32 | 3.69 / 174.55 | 3.61 | 3.61 | nothing laps; at the identity's FX the card would print $178.32, not $176.88 |
| K4 lap-only residual steps | 2.91 / 176.97 | 1.99 / **171.71** | 1.30 | 1.36 | every residual change since 2Q25 is a dated product step that laps (3Q25 +0.92, 4Q25 +0.88, 1H26 +1.15) — **lands on the Street** |
| full lap: ex-NA RNPL sized at the 1H26 steps | 3.32 / 177.68 | 2.78 / 173.03 | 1.96 | 1.81 | the 1H26 residual steps were RNPL-ex-NA and lap in 1H27 |
| core mean reversion to 2.40 (K4 floor) | 1.86 / 175.20 | 1.33 / 170.60 | 0.97 | 1.51 | the 2026 step in core reverses entirely — **the named downside**: −$2.5 of ADR, −$0.35bn of GBV a quarter |
| AR(1) on core (K4 ρ 0.75) | 3.09 / 177.30 | 2.39 / 172.38 | 1.90 | 2.35 | partial reversion |
| base + fee-migration K line (DEC-0008 sensitivity) | 3.49 / 177.97 | 3.16 / 173.66 | 2.76 | 3.27 | tranche 2 reprice at the central mechanics 0.007 × Δshare |

**Addendum, 22 Sep (Theo's question: can the line sit at the Street, then below?).** Two of the rows above do,
by stated assumption and not by fit: K4's lap-only steps ($171.71, on the Street) and core mean reversion
($170.60, below). Their argument is the same one: the 2026 step in like-for-like price coincides with three dated
product changes, the fee reprice is payout-neutral by construction (K2) and the RNPL effect is a mix effect, so
neither should persist in like-for-like price once lapped. Against them stands the one alt-data test run for this
question (`adr_v1b_utilisation_prereg.md`): North-American stays per listing, which fell every year 2022–2025,
turned positive in 1H26 as listings growth slowed to 7% — the supply-demand picture behind NA's +5–7% ex-FX ADR
argues for persistence, not reversion, though it fails its pre-registered walk-forward line (1.01 / 0.87). The base
therefore stays the carry (DEC-0016); adopting the lap-only or reversion row as the short's base is a labelled
decision for Theo, not an engine output. The card's carry and the base differ by exactly the bundle's lap: 0.37pp in 3Q26 (the 0.49 leg plus the geo
difference), 0.91pp from 4Q26. A judge who believes nothing laps has the card's row; one who believes the
2026 step was all product has the "full lap" row; the base is management's own sizing on management's own dates.

### 3.7 What is and is not tested here

The only lapped quarter in history (3Q26) has not printed, so the lap mechanism has no walk-forward and none is
claimed. What is scorable is small: carrying core with the known bundle schedule vs carrying the residual, on
3Q25–2Q26 (n 4): errors −0.39 / −0.68 / −0.47 vs −0.88 / −0.68 / −0.47 — identical when no leg changes, better in
the one quarter a leg went live (4Q25). Descriptive.

---

## 4. The band

Two layers, both mechanical (`exfx_envelope.csv`), added in quadrature (J3's RSS convention):

1. **Ex-FX parameter envelope**: bundle total 0.8–1.2 (±0.20 in 4Q26+); ex-NA RNPL leg 0–1.15 (±0.23 from 1Q27,
   ±0.58 from 2Q27); geo mix nights-linked vs card (±0.05–0.17); unit ±0.23; LOS ±0.19; seats ±0.26;
   interaction ±0.05; **and the core carry's own h-step error from its 14-quarter history** (sd of the h-quarter
   change: 0.88 / 1.35 / 1.38 / 1.15 / 0.98 / 0.97pp for h = 1…6 — the pre-registration's "core carry ± its own
   quarterly change sd"). Ex-FX half-band: 0.98 / 1.42 / 1.47 / 1.37 / 1.23 / 1.23pp.
2. **FX predictive sd** from the bootstrap: 0.05 / 1.31 / 2.31 / 2.94 / 3.55 / 3.70pp.

Reported half-band: **0.98 / 1.93 / 2.74 / 3.25 / 3.76 / 3.90pp** → ADR 3Q26 $176.01–179.36, 4Q26 $169.80–176.27,
1Q27 $185.52–195.77, 2Q27 $182.41–194.35. The mean-reversion case (§3.6) sits **outside** the 3Q26 band
(175.20 < 176.01) and is shown as a scenario, not inside the band — the risk is one-sided, as SYNTHESIS §4.2 said.

---

## 5. The view: our ADR vs the Street, and GBV on the nights line (`adr_path.csv`, figure `adr_path_vs_street`)

| quarter | ours | y/y | band | Street (MODL 12 Sep) | Street y/y | z | **P(print ≥ Street)** | card v3 | nights (m) | **GBV $bn** | Street GBV |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 3Q26 | **$177.68** | +3.73% | 176.01–179.36 | $177.06 (n 26; 173.71–179.12) | +3.37% | +0.37 | **65%** | 176.88 | 146.8 | **26.08** | 26.38 |
| 4Q26 | **$173.03** | +3.30% | 169.80–176.27 | $171.33 (n 25) | +2.28% | +0.53 | **70%** | 173.94 | 131.8 | **22.81** | 22.96 |
| 1Q27 | $190.65 | +2.05% | 185.52–195.77 | — | | | | (path 192.11) | 169.02 | 32.22 | |
| 2Q27 | $188.38 | +2.53% | 182.41–194.35 | — | | | | (188.48) | 157.10 | 29.59 | |
| 3Q27 | $182.51 | +2.72% | 175.83–189.18 | — | | | | (181.38) | 155.96 | 28.46 | |
| 4Q27 | $178.10 | +2.93% | 171.35–184.85 | — | | | | (177.47) | 139.77 | 24.89 | |
| FY26 | $180.62 | | | | | | | | 583.1 | 105.29 | |
| FY27 | **$185.21** | **+2.54%** | | no FY consensus exists anywhere | | | | (185.21) | 621.85 | **115.17** | |

Reading. On ADR the line sits **on the Street in 3Q26** (+$0.62, a third of a band) and **1.0% above it in 4Q26**
(+$1.70) — the Street's 4Q26 ADR implies +2.3% y/y, i.e. it already has FX rolling off (4Q25 carried +2.9pp)
and ex-FX decelerating; the base has FX at +0.5 and ex-FX at 2.8. **The ADR line is not where the variant view
is** — the nights line is (Street 149.0 / 134.0 vs 146.8 / 131.8); on GBV the two lines together put 3Q26 at
$26.1bn vs the Street's $26.4bn (−1.1%) and 4Q26 at $22.8bn vs $23.0bn (−0.7%). What the ADR line contributes to
the pitch is **shape and attribution**: FX turns from a 2.9–5.0pp tailwind (4Q25–1Q26) to ~0.4–0.5 now and
slightly negative in 1H27 at held spot; the bundle laps take ex-FX from 4.0 to ~2.8; geographic mix stays a
1.1–1.6pp drag as long as LatAm/APAC outgrow North America. A 4Q26 ADR that decelerates to +3.3% reported with
+2.8% ex-FX is the arithmetic consequence of disclosed dates, not a call on pricing power.

---

## 6. What management disclosed, and when (ledger A, all dated)

- **The driver vocabulary is a clean sequence**: 1Q23–2Q23 "willingness to pay" and "mix shift into urban" (ADR
  down); 2Q23 "our new Host pricing tools have had a moderating effect on ADR" (the only named downward product
  driver); "price appreciation" as the global ex-FX driver every quarter from 1Q24; "mix shift" as North America's
  primary driver in 1Q25, 3Q25, 4Q25; "price appreciation and mix" jointly in 4Q24, 1Q26, 2Q26.
- **"4 or more bedrooms"** enters the filed NA ADR sentence in 4Q25 and is global by 2Q26 ("entire homes,
  especially listings with four or more bedrooms continue to grow the fastest… extending a mix-shift trend we
  have now seen for over a year").
- **Regional ex-FX ADR** (filed, whole points): EMEA +4 / +4 / +4 / +5 (3Q25–2Q26), LatAm +3 / +3 / +3 / +2, APAC +3 /
  +2 / +2 / n.a.; **North America's ex-FX is not disclosed from 2Q25 onward** (reported +5 / +5 / +7 / +7). The
  repo's NA ex-FX series (5.05 / 4.78 / 6.30 / 6.75) is constructed, not disclosed, and this design does not use
  it as a coefficient.
- **FX on ADR vs revenue**: §2.0. The 3Q26 ADR outlook omits FX (§2.5).
- **Filed size facts**: Bedroom Nights Booked +12% vs nights +10% (2Q26); FY25 average nights per booking 3.7
  (NA 4.1 / EMEA 3.8 / LatAm 3.6 / APAC 3.3).
- **Contradictions found and carried**: the fee-tranche start is a Sep–Oct 2025 range across three sources;
  `06_fee_timeline.csv` misattributes two call-only coverage figures to letters; 2Q26 APAC ex-FX is blank in the
  letter but −1.35 in the wide file. None changes a number here.

---

## 7. The constellation of cross-checks, honest (figure `adr_constellation`)

Against the like-for-like line: **EMEA ex-FX ADR vs euro-area HICP accommodation** r 0.74 (n 14; L's walk-forward
0.914, jackknife max 1.17 — the one proxy that survives); **global ex-FX vs US lodging CPI** r 0.00; **reported
ADR vs Marriott / Hilton RevPAR** r −0.39 (the L3 hotel lane: every US comparator fails, best 1.03×). The
supply channel that M's lead points at (new-listing share moving opposite the residual, coefficient near −10)
cannot be run on disclosed supply: active-listings y/y exists for 7 of 24 quarters and stops at 1Q24; there is
no Airbnb occupancy series. So the core is cross-checked by one European price index and by nothing in the
US — and the design says so instead of borrowing a hotel line that does not fit.

---

## 8. The analyst's attacks, and where each component stands ("is this too shallow?")

Theo's standing question is asked of every component, against a hedge-fund travel-and-lodging analyst:

| component | the attack | the answer | verdict |
|---|---|---|---|
| FX identity | "Your FX number is a regression on the euro." | It is not: zero parameters, the company's own accounting basis (booking-date GBV, prior-year rates, unhedged), point-in-time tested on 17 disclosed quarters at three origins; ratio 0.30–0.38 vs naive, at the rounding floor. The euro-only fit is biased −0.3 to −0.5 because it has no peso/real/Aussie channel, and 3Q26 is a peso/real/Aussie quarter. | **clears** |
| currency weights | "Where do your baskets come from?" | 10-K GBV geographic mix (filed) × the repo's frozen destination baskets (judgement). The posterior says EMEA 1.2, LatAm 0.46 — legible economics (periphery currencies; USD-indexed LatAm pricing) — and fitting it does not beat the identity out of sample. Uncovered currencies are the stated limit. | clears, with the label |
| bundle ~1pp | "That's a transcript number." | Yes: D014/D032 are call-only, X3 confirmed no filing carries them; the filed substitutes (20% of GBV from RNPL; the 10-Q's RNPL→ADR sentence) sit beside them; the sizing band 0.8–1.2 is in the envelope. | clears, labelled |
| lap calendar | "Why would the ADR effect lap on the nights dates?" | Same features, same filed launch dates (Aug 2025 US RNPL; Oct 2025 global redesign and fee; 17 Feb 2026 global RNPL). The one asymmetry — the fee reprice peaks in 4Q26 rather than lapping — is carried as the K sensitivity. | clears |
| core 3.85 carried | "You carry an unobserved 3.85% like-for-like price growth when hotels run +1–2% and supply grows 10%." | Correct, and it is the same carry the committed card applies to 4.85. The design labels it, bands it with its own 0.9–1.4pp h-step error, cross-checks it with the one proxy that works (EMEA vs HICP), and names its full reversion as the downside (−$2.5 of ADR). It does not claim a mechanism it does not have. | **does not clear on its own**; carried honestly. What would clear it: an RNPL GBV-share / nights-share pair for one quarter (pins the RNPL ADR premium), a same-listing realised-rate series, a pre-registered supply term |
| geo mix | "Mix is a fudge." | Share-shift arithmetic on 10-K regional ADR levels and the nights line's own regional path; reproduces the disclosed-share term within 0.13pp; the drag is 1.1–1.6pp and it *comes from the nights line*. | **clears** |
| unit size +0.8 | "Bedroom nights +12% vs +10% — isn't half your ADR bigger homes?" | Elasticity 0.23 (1.65 bedrooms average; +1 bedroom = +15% price), measured +0.63–0.80pp, a fifth of ex-FX. | clears |
| LOS / seats / interaction | "Assumed." | Yes, small, banded, labelled; seats volumes are never disclosed. | clears, labelled |
| the Street | "You're on consensus." | On it in 3Q26, +1.0% in 4Q26; the variant view is nights, and on GBV the two lines are 0.7–1.1% below the Street. The ADR line's job is attribution and shape. | clears |
| supply-demand (utilisation) | "Occupancy leads rate — where is it?" | Built (stays per active listing, vintage-matched, 119 markets) and tested against the core, pre-registered: fails the line everywhere; NA alone explains the core in sample (r 0.77 lagged, β 0.32, p 0.002) and says pricing power is improving, not fading. Reported as a fourth constellation panel. | clears as a cross-check; does not move the number |
| the band | "Your 3Q26 band is ±1pp on a number you carry flat." | It includes the core carry's own one-quarter error (0.88pp) and the FX bootstrap; the mean-reversion case is outside it and shown as a scenario, because the risk is one-sided. | clears |

Net: the FX half is analyst-grade and new; the ex-FX half is as deep as the disclosed record allows and says
where its floor is. The path to continue is not another regression on the residual; it is the three disclosures
listed under "core".

---

## 9. Falsifiers and tells, pre-registered (adr_fx_prereg §7)

- **5 Nov 2026, 3Q26 print.** (a) Printed ADR-FX pp (reported y/y − the letter's ex-FX figure) vs the 21 Sep band
  [0.36, 0.48]: inside keeps the identity as the leg; outside withdraws it. The four candidates named before
  the print: identity **+0.42**, card midpoint −0.43, euro fit −1.12, fx_lag_v2 basket +0.44. (b) Printed ex-FX
  ADR y/y vs the base 3.3 and the card's 3.7: at or below 3.3 says the bundle laps; at or above 3.7 says it does
  not; in between, both stay on the slide. (c) The letter's 4Q26 ADR outlook: if it names FX again, the tell of
  §2.5 reverses.
- **11 Feb 2027, 4Q26 print.** Printed FX vs the 5 Nov band [−0.78, +1.97]; printed ex-FX vs 2.8 (base) / 3.7
  (card) / 1.3 (mean reversion) — the full-lap quarter, and the first the harness has ever scored.
- **Any quarter**: an RNPL GBV share alongside an RNPL nights share (pins the premium and splits the bundle);
  Bedroom Nights Booked returning or not.

---

## 10. What changes in the model and the workbook

- `model/ABNB_official_model.xlsx`: new sheet **`ADR_Engine`** after `Nights_Engine` (blocks A–F: the disclosed
  identity; the FX identity with the currency averages, κ, 10-K shares, the SUMPRODUCT and its in-sheet RMSE
  ratio; the ex-FX mechanism with the bundle legs and the C1 geo-mix arithmetic; the reported path, band, Street
  z and tail probability, GBV on line 1; engine reference values; alternatives; two charts). **`Income_Statement`
  rows 8–11** now carry GBV = nights × ADR and ADR, linked. The nights sheets and charts are untouched (the
  frozen builder is run and its workbook captured). Formulas need one Excel recalculation; block E ties out.
- `docs/pitch-model-v2/DECISIONS.md`: DEC-0034/0035/0036 appended, marked proposed.
- Cross-line consequences: **R2 / D6** — GBV 3Q26 $26.08bn, 4Q26 $22.81bn on these two lines (the card's
  comparison column was $25.97bn / $22.93bn); the take-rate line is next. **D5 / X1** — the ADR-FX leg is no
  longer the in-sample midpoint; the 0.85pp gap is on record and scored on 5 Nov. **D3** — the FY27 path's ADR
  legs (with-K, N-midpoint FX) should be rebuilt on this line when D3 is reopened; until then its levels are
  quoted beside ours in §5.

### 2a. Model inputs (machine-readable)

| item | scenario | period | point | unit | note |
|---|---|---|---|---|---|
| adr_fx_pp | base | 3Q26 | 0.42 | pp | translation identity, spot held from 2026-09-18, 88 pct of business days printed; P10 0.36 P90 0.48 |
| adr_fx_pp | base | 4Q26 | 0.51 | pp | identity, 0 pct printed; P10 -1.06 P90 2.26 |
| adr_fx_pp | base | 1Q27 | -0.37 | pp | identity; P10 -3.20 P90 2.78 |
| adr_fx_pp | base | 2Q27 | -0.43 | pp | identity; P10 -3.90 P90 3.68 |
| adr_fx_pp | base | 3Q27 | -0.15 | pp | identity |
| adr_fx_pp | base | 4Q27 | 0.00 | pp | identity; base quarter also spot held, zero by construction |
| adr_fx_pp | usd_weak_5pct | 4Q26 | 3.39 | pp | D5 device, foreign units worth 5 pct more after 18 Sep |
| adr_fx_pp | usd_strong_5pct | 4Q26 | -2.36 | pp | D5 device |
| fx_ratio_vs_naive_w1_o2 | base | 1Q23-2Q26 | 0.344 | ratio | V0 identity, day 60; pass line 0.75 |
| fx_ratio_vs_naive_w1_o3 | base | 1Q23-2Q26 | 0.303 | ratio | V0 identity, pre-print |
| fx_ratio_vs_naive_w2_o2 | base | 1Q24-2Q26 | 0.383 | ratio | V0 identity |
| fx_ratio_vs_naive_w2_o3 | base | 1Q24-2Q26 | 0.317 | ratio | V0 identity |
| fx_ratio_vs_naive_w1_o1 | base | 1Q23-2Q26 | 0.437 | ratio | V0 identity at quarter start, reported not scored |
| passthrough_beta_emea | posterior | 2Q22-2Q26 | 1.20 | scale | 90 pct 1.09 to 1.31; descriptive, not the leg |
| passthrough_beta_latam | posterior | 2Q22-2Q26 | 0.46 | scale | 90 pct 0.17 to 0.78; descriptive |
| bundle_adr_pp_total | base | 4Q25-2Q26 | 1.00 | pp | ledger D014 and D032 GBV minus nights gap; transcript-only; band 0.8 to 1.2 |
| bundle_leg_rnpl_na_pp | base | 3Q25-2Q26 | 0.511 | pp | split by K4 residual steps 0.92 to 0.88; laps 3Q26 |
| bundle_leg_fee_cancel_pp | base | 4Q25-3Q26 | 0.489 | pp | laps 4Q26 |
| bundle_leg_rnpl_exna_pp | base | all | 0.00 | pp | unsized by management; high alternative 1.15 laps 1H27 |
| core_pp | base | 3Q26-4Q27 | 3.849 | pp | 2Q26 residual 4.849 less bundle 1.00, carried; 2023-25 mean 2.398 is the downside |
| core_carry_sd_h1 | base | all | 0.882 | pp | sd of the one-quarter change of core, 1Q23-2Q26; h2 1.351 h3 1.379 h4 1.149 |
| geo_mix_pp | base | 3Q26 | -1.293 | pp | nights-line regional path on 3Q25 shares and anchored regional ADR; card -1.428 |
| geo_mix_pp | base | 4Q26 | -1.336 | pp | same |
| geo_mix_pp | base | 1Q27 | -1.620 | pp | same; Middle East lap raises ex-NA growth |
| geo_mix_pp | base | 2Q27 | -1.081 | pp | same |
| geo_mix_pp | base | 3Q27 | -1.174 | pp | same |
| geo_mix_pp | base | 4Q27 | -1.109 | pp | same |
| unit_size_pp | base | 3Q26-4Q27 | 0.797 | pp | card measured term carried; band 0.53 to 1.00 |
| los_pp | base | 3Q26-4Q27 | 0.056 | pp | card; band -0.08 to 0.29 |
| seats_pp | base | 3Q26-4Q26 | -0.483 | pp | assumed; 2027 -0.565 |
| interaction_pp | base | 3Q26-4Q27 | -0.10 | pp | descriptive |
| adr_exfx_yoy_pct | base | 3Q26 | 3.316 | pct | core + bundle + mix terms |
| adr_exfx_yoy_pct | base | 4Q26 | 2.784 | pct | same |
| adr_exfx_yoy_pct | base | 1Q27 | 2.417 | pct | same |
| adr_exfx_yoy_pct | base | 2Q27 | 2.957 | pct | same |
| adr_exfx_yoy_pct | base | 3Q27 | 2.863 | pct | same |
| adr_exfx_yoy_pct | base | 4Q27 | 2.928 | pct | same |
| adr_total_usd | base | 3Q26 | 177.68 | USD | 171.29 times 1.03731; band 176.01 to 179.36 |
| adr_total_usd | base | 4Q26 | 173.03 | USD | 167.51 times 1.03298; band 169.80 to 176.27 |
| adr_total_usd | base | 1Q27 | 190.65 | USD | 186.82 times 1.02048; band 185.52 to 195.77 |
| adr_total_usd | base | 2Q27 | 188.38 | USD | 183.73 times 1.02530; band 182.41 to 194.35 |
| adr_total_usd | base | 3Q27 | 182.51 | USD | 177.68 times 1.02716 |
| adr_total_usd | base | 4Q27 | 178.10 | USD | 173.03 times 1.02928 |
| adr_total_usd | base | FY27 | 185.21 | USD | nights-weighted on the nights line; FY26 180.62; plus 2.54 pct |
| adr_total_usd | card_v3_carry | 3Q26 | 178.32 | USD | residual carried, no lap, at the identity FX |
| adr_total_usd | card_v3_carry | 4Q26 | 174.55 | USD | same |
| adr_total_usd | core_mean_reversion | 3Q26 | 175.20 | USD | the named downside |
| adr_total_usd | core_mean_reversion | 4Q26 | 170.60 | USD | same |
| adr_total_usd | street | 3Q26 | 177.06 | USD | Bloomberg MODL 12 Sep 2026, n 26, 173.71 to 179.12 |
| adr_total_usd | street | 4Q26 | 171.33 | USD | Bloomberg MODL 12 Sep 2026, n 25 |
| p_print_ge_street | base | 3Q26 | 0.645 | prob | z 0.37 on the band |
| p_print_ge_street | base | 4Q26 | 0.701 | prob | z 0.53 |
| gbv_busd | base | 3Q26 | 26.08 | USD bn | 146.8m nights times 177.68; Street 26.38 |
| gbv_busd | base | 4Q26 | 22.81 | USD bn | 131.8m times 173.03; Street 22.96 |
| gbv_busd | base | FY27 | 115.17 | USD bn | nights line 621.85m |

## 11. Provenance and figures

Engine outputs `data/processed/pitch_model_v2/adr_engine/`: `fx_pit_walkforward.csv`, `fx_scores.csv`,
`fx_design_full.csv`, `fx_sensitivity_revenue_shares.csv`, `fx_weights_posterior.csv`, `fx_beta_draws.npy`,
`fx_forecast_asof.csv`, `fx_currency_contributions.csv`, `exfx_history.csv`, `exfx_forward_base.csv`,
`exfx_alternatives.csv`, `geo_mix_method_check.csv`, `regional_growth_forward.csv`, `geo_mix_forward.csv`,
`bundle_schedule.csv`, `exfx_envelope.csv`, `adr_path.csv`, `adr_scenarios.csv`, `00_summary.json`,
`fx_daily_2026-09-21.csv` + manifest. Figures (`docs/pitch-model-v2/lines/figures/`, PNG + SVG):
`adr_full_logic` (the four-panel composite), `adr_fx_walkforward`, `adr_fx_currency_contributions`,
`adr_exfx_mechanism`, `adr_path_vs_street`, `adr_fx_passthrough_posterior`, `adr_constellation`. Palette: the
dataviz reference set, validated (`validate_palette.js`, all checks pass; three light slots carry direct labels).
Inputs read, never written: `02_kpi_panel_quarterly.csv`, `02_guidance_ledger.csv`, `01_regional_annual.csv`,
`04_regional_quarterly_wide.csv`, `10_regional_panel_quarterly.csv`, `adr_history_components.csv`,
`I_mix_terms_3q26.csv`, `K4_residual_nowcast.csv`, `K4_fee_lap_schedule.csv`, `adr_card_v3.csv`,
`J2_proxy_quarterly_panel.csv`, `01b_basket_weights_used.csv` (values transcribed to `config.py`).
