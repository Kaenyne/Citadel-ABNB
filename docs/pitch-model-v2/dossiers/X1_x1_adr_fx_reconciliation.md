# X1 — the ADR FX object: D4 vs D5, reconciled

## 1. Header
- Line: X1 · Judge's question: "Your two FX numbers for the same quarter differ by more than three points. Which is the effect of currency on reported ADR, and what did Airbnb itself disclose?"
- Digger: opus · Date: 2026-09-18 · Commit: c82b968 (the working tree for this wave; D4 and D5 were written at `e39d9e4`, three commits earlier, and nothing under `adrv3/N` or `fx_lag_v2` moved in between — both packages reproduced byte-identical at `c82b968`, §5)
- One-line answer: **there is no 3.3pp disagreement about ADR FX, because only one of the two numbers is an ADR quantity.** D4's −0.43pp is an estimate of the effect Airbnb discloses (reported ADR growth minus ex-FX ADR growth), scored on the disclosed record at 0.33–0.42pp RMSE depending on the window (0.406 on all 17). D5's +2.89pp is `fx_lag_v2`'s `point_phi_adrfx_pp`, which by construction puts **zero weight on the quarter's own currency basket** and two-thirds on the prior quarter's — it is B4 §6 reading A, "booking-date FX carried through the Φ kernel", i.e. a **revenue**-FX construction that happens to consume ADR-FX points as its driver. Scored against disclosed ADR FX it has RMSE **2.20pp**, gets the sign wrong in 4 of 17 quarters and misses by as much as 4.06pp. The ADR line must carry **−0.43pp (3Q26) and +0.15pp (4Q26)**.

## 2. The number

Convention. `adr_fx_pp` is a **contribution in points of y/y ADR growth**, not a level: `reported ADR y/y = ex-FX ADR y/y + adr_fx_pp`, the same identity and sign Airbnb uses in the letters. Denominator is the prior-year quarter's ADR. It is **gross of hedging** — Airbnb's hedges are designated against *revenue*, never against GBV or ADR, so the letters' ADR ex-FX sentence is a pure translation restatement while the revenue-FX sentence is stated after hedging. Scenarios are the estimator envelope, not a dollar path: the point is the N midpoint, low is the euro fit, high is the widest contemporaneous estimator in the repo (`fx_lag_v2`'s own basket fit). Per DEC-0020 only `base` enters the spec; low/high are on record.

| scenario | period | point | low | high | unit | vintage |
|---|---|---|---|---|---|---|
| base | 3Q26 | -0.43 | -1.12 | 0.44 | pp | adrv3 N1 midpoint, FRED through 2026-09-04 (low = euro fit; high = fx_lag_v2 contemporaneous basket fit) |
| base | 4Q26 | 0.15 | -0.66 | 1.10 | pp | same |
| base | 1Q27 | -0.30 | n/a | n/a | pp | D4's committed FY27 path leg (`06_adr_build.csv`), same N-midpoint family |
| base | 2Q27 | -0.19 | n/a | n/a | pp | same |
| base | 3Q27 | 0.03 | n/a | n/a | pp | same |
| base | 4Q27 | -0.29 | n/a | n/a | pp | same |

**The two objects side by side, 3Q26 and 4Q26 (the whole of the dispute):**

| object | 3Q26 | 4Q26 | weights on basket lag 0 / 1 / 2 | what it is an estimate of |
|---|---|---|---|---|
| **D4 — adrv3 N midpoint** | **−0.43** | **+0.15** | **1 / 0 / 0** | the disclosed ADR-FX effect (reported ADR y/y − ex-FX ADR y/y) |
| D4 leg: euro fit | −1.12 | −0.66 | 1 / 0 / 0 | same |
| D4 leg: regional baskets | +0.26 | +0.97 | 1 / 0 / 0 | same |
| `fx_lag_v2` contemporaneous basket fit | +0.44 | +1.10 | 1 / 0 / 0 | same (the package's own ADR-FX estimator; published for 3Q26 as `adr_fx_3Q26_fitted_pp` = 0.44 in `27_kernel_carried_fx_v2.csv`; 4Q26 is my arithmetic on its published coefficients) |
| **D5 — `point_phi_adrfx_pp`** | **+2.89** | **+0.93** | **0 / ⅔ / ⅓** | **3Q26/4Q26 REVENUE FX** (B4 §6 reading A) |
| D5's own `revenue_fx_pp` (Φ×0.851) | +2.89 | +0.98 | 0 / ⅔ / ⅓ | 3Q26/4Q26 revenue FX |
| management, 6 Aug 2026 letter | ~+3.0 | — | n/a | 3Q26 **revenue** FX, after hedging |

The tell a judge will find in ten seconds: **D5's "ADR FX" for 3Q26 and D5's own revenue FX for 3Q26 are the same number to two decimals (+2.89 / +2.89), and both sit within 0.11pp of management's revenue guide of ~+3pp.** Two different quantities cannot coincide to two decimals in a quarter when the disclosed record says they differed by 2.7pp in 2Q26 (ADR +1.3, revenue +4.0). They coincide because they are the same object built two ways: Φ(0, ⅔, ⅓) applied to a basket at scale 0.851, and Φ(0, ⅔, ⅓) applied to that basket through an ADR-FX fit of slope 0.872. 0.872 ≈ 0.851 is the entire difference.

**What Airbnb disclosed, verbatim (2Q26 shareholder letter, 8-K exh. 99.1, 6 Aug 2026):**
- ADR: *"ADR was $184 in Q2 2026, increasing 5% compared to Q2 2025. On an ex-FX basis, ADR in Q2 2026 increased 4% year-over-year"* → **ADR FX = +1.3pp** on the panel convention (unrounded reported +5.301% minus the letter's whole-point ex-FX +4%).
- Revenue, 3Q26 guide: *"revenue of $4.69 billion to $4.77 billion, representing year-over-year growth of 15% to 17%, inclusive of an approximate three percentage point FX tailwind after factoring in our hedging program."* → **the ~+3pp is a revenue number, after hedging.**
- 3Q26 ADR, the same letter: *"a moderate increase in ADR due to mix shift and price appreciation."* **FX is not named in the ADR sentence at all** — the first guide since 1Q25 in which it is not. The 3Q25 letter said ADR would rise *"primarily due to price appreciation and FX"*; the 1Q26 letter said *"We expect the FX tailwind to ADR to be significantly lower in Q2 2026 than in Q1."* Management dropping FX from the 3Q26 ADR sentence is qualitative corroboration of an ADR-FX effect near zero — consistent with −0.43 to +0.44, flatly inconsistent with +2.89.

**Disclosed ADR FX, every quarter Airbnb has disclosed it, against both objects** (`X1_disclosed_vs_objects.csv`; D5's column for history is my reconstruction of `exhibit.py` L283-289 applied to the same panel, since D5's dossier publishes the object only forward):

| quarter | disclosed ADR FX | D5's object (Φ on lagged ADR-FX) | D4's term (N midpoint) | D5 error | D4 error |
|---|---|---|---|---|---|
| 2Q22 | −5.6 | −1.65 | −5.29 | +3.95 | +0.31 |
| 3Q22 | −7.1 | −3.15 | −6.75 | +3.95 | +0.35 |
| 4Q22 | −5.5 | −4.63 | −5.16 | +0.87 | +0.34 |
| 1Q23 | −2.8 | −4.27 | −2.54 | −1.47 | +0.26 |
| 2Q23 | −0.6 | −2.63 | +0.40 | −2.03 | +1.00 |
| 3Q23 | +2.7 | −0.49 | +3.25 | −3.19 | +0.55 |
| 4Q23 | +2.1 | +2.05 | +2.14 | −0.05 | +0.04 |
| 1Q24 | +0.6 | +2.41 | +0.39 | +1.81 | −0.21 |
| 2Q24 | −0.9 | +1.21 | −0.87 | +2.11 | +0.03 |
| 3Q24 | −0.6 | −0.22 | −0.18 | +0.38 | +0.42 |
| 4Q24 | −1.1 | −0.59 | −0.98 | +0.51 | +0.12 |
| 1Q25 | −1.9 | −1.04 | −2.18 | +0.86 | −0.28 |
| 2Q25 | +1.9 | −2.16 | +1.58 | −4.06 | −0.32 |
| 3Q25 | +2.7 | −0.36 | +2.16 | −3.06 | −0.54 |
| 4Q25 | +2.9 | +1.39 | +3.46 | −1.51 | +0.56 |
| 1Q26 | +5.0 | +2.64 | +4.75 | −2.36 | −0.25 |
| 2Q26 | **+1.3** | **+4.28** | **+1.14** | **+2.98** | **−0.16** |

D5's object is wrong-signed in **4 of 17** quarters (3Q23, 2Q24, 2Q25, 3Q25) and its worst miss is 4.06pp; D4's is wrong-signed in **1 of 17** (2Q23, where the disclosed value is −0.6) and its worst miss is 1.00pp. On the most recent quarter, the one a judge will pick, disclosed +1.3 against D4 +1.14 and D5 +4.28.

**Scores** (`X1_estimator_scores.csv`), all against the disclosed ADR-FX series:

| estimator | window | n | RMSE pp | bias pp |
|---|---|---|---|---|
| **D4 N midpoint** | full 2Q22–2Q26 | 17 | **0.406** | +0.13 |
| **D4 N midpoint** | 1Q23–2Q26 | 14 | **0.420** | +0.09 |
| **D4 N midpoint** | 1Q24–2Q26 | 10 | **0.332** | −0.06 |
| `fx_lag_v2` contemporaneous basket fit | 1Q23–2Q26 (its own fit window) | 14 | 0.582 | 0.000 |
| `fx_lag_v2` contemporaneous basket fit | 1Q24–2Q26 | 10 | 0.575 | −0.19 |
| **D5 `point_phi_adrfx`** | full 2Q22–2Q26 | 17 | **2.424** | −0.02 |
| **D5 `point_phi_adrfx`** | 1Q23–2Q26 | 14 | **2.203** | −0.65 |
| **D5 `point_phi_adrfx`** | 1Q24–2Q26 | 10 | **2.269** | −0.23 |

D5's object is 5–6× worse than D4's at the job of estimating ADR FX. Against **disclosed revenue FX** on the same 17 quarters it scores 2.13pp unscaled — and at the registered H2 spec's fitted scale it is the best point-in-time revenue-FX forecaster in the programme (B4: W1/W2 RMSE 0.99pp). It is a good object pointed at the wrong line.

**What each number does to the model** (`X1_model_impact.csv`; ex-FX +3.69pp per DEC-0008, nights 146.3m/131.8m per DEC-0024/DEC-0019):

| object used for ADR FX | 3Q26 reported ADR y/y | 3Q26 ADR $ | 3Q26 GBV $M | vs D4 |
|---|---|---|---|---|
| **D4 (committed)** | **+3.26%** | **$176.87** | **$25,877** | — |
| D5 | +6.58% | $182.56 | $26,709 | **+$5.69 of ADR, +$832M of GBV** |
| euro leg only | +2.57% | $175.69 | $25,704 | −$1.18, −$173M |
| baskets leg only | +3.95% | $178.06 | $26,050 | +$1.19, +$173M |

Adopting D5's leg would put our 3Q26 ADR at **$182.56 against a Street mean of $177.06** with no change to a single ex-FX term — a 3.1% variant view on ADR created entirely by a labelling error. The committed card ($176.88) already carries D4's leg, so the recommendation changes nothing downstream; it removes a hole.

### 2a. Model inputs (machine-readable)

`adr_fx_pp_disclosed` is `adr_yoy − adr_exfx_yoy` (`analysis/src/predictive/03_nowcast_tests.py` L66), reported ADR y/y computed from disclosed ADR levels minus the letter's whole-point ex-FX figure; the identity closes to within 0.042pp in every quarter (`compare_stdout.txt`). 2Q22–4Q22 are disclosed too and are included; 1Q23–2Q26 is the 14-quarter W1 span.

| item | scenario | period | point | unit | note |
|---|---|---|---|---|---|
| adr_fx_pp_disclosed | actual | 2Q22 | -5.6 | pp | letter: reported ADR y/y minus ex-FX ADR y/y |
| adr_fx_pp_disclosed | actual | 3Q22 | -7.1 | pp | same |
| adr_fx_pp_disclosed | actual | 4Q22 | -5.5 | pp | same |
| adr_fx_pp_disclosed | actual | 1Q23 | -2.8 | pp | same |
| adr_fx_pp_disclosed | actual | 2Q23 | -0.6 | pp | same |
| adr_fx_pp_disclosed | actual | 3Q23 | 2.7 | pp | same |
| adr_fx_pp_disclosed | actual | 4Q23 | 2.1 | pp | same |
| adr_fx_pp_disclosed | actual | 1Q24 | 0.6 | pp | same |
| adr_fx_pp_disclosed | actual | 2Q24 | -0.9 | pp | same |
| adr_fx_pp_disclosed | actual | 3Q24 | -0.6 | pp | same |
| adr_fx_pp_disclosed | actual | 4Q24 | -1.1 | pp | same |
| adr_fx_pp_disclosed | actual | 1Q25 | -1.9 | pp | same |
| adr_fx_pp_disclosed | actual | 2Q25 | 1.9 | pp | same |
| adr_fx_pp_disclosed | actual | 3Q25 | 2.7 | pp | same |
| adr_fx_pp_disclosed | actual | 4Q25 | 2.9 | pp | same |
| adr_fx_pp_disclosed | actual | 1Q26 | 5.0 | pp | same |
| adr_fx_pp_disclosed | actual | 2Q26 | 1.3 | pp | ADR $184, +5% reported, +4% ex-FX (6 Aug 2026 letter); unrounded reported +5.301% minus +4 |
| adr_fx_pp_d5 | base | 3Q26 | 2.89 | pp | D5 §2a as written; = 23_forecast_4q26_v2.csv point_phi_adrfx_pp, spot_held; NOT an ADR quantity (weights 0/2/3,1/3 on basket lags) |
| adr_fx_pp_d5 | base | 4Q26 | 0.93 | pp | same |
| adr_fx_pp_d4 | base | 3Q26 | -0.43 | pp | adrv3 N1 midpoint of euro fit -1.12 and regional baskets +0.26; contemporaneous |
| adr_fx_pp_d4 | base | 4Q26 | 0.15 | pp | same (euro -0.66, baskets +0.97) |
| adr_fx_pp_recommended | base | 3Q26 | -0.43 | pp | D4's object (adrv3 N1 midpoint) governs: it is the only one of the two estimating the disclosed effect, RMSE 0.42pp on 1Q23-2Q26 against D5's 2.20pp |
| adr_fx_pp_recommended | base | 4Q26 | 0.15 | pp | D4's object (adrv3 N1 midpoint) governs; same reason |
| adr_fx_pp_recommended_low | base | 3Q26 | -1.12 | pp | euro-fit leg of the midpoint |
| adr_fx_pp_recommended_low | base | 4Q26 | -0.66 | pp | euro-fit leg of the midpoint |
| adr_fx_pp_recommended_high | base | 3Q26 | 0.44 | pp | fx_lag_v2 contemporaneous basket fit (27_kernel_carried_fx_v2.csv adr_fx_3Q26_fitted_pp), above the N baskets leg of +0.26 |
| adr_fx_pp_recommended_high | base | 4Q26 | 1.10 | pp | same fit coefficients applied to the 4Q26 spot-held basket (+1.349%); my arithmetic, not a published cell |
| revenue_fx_pp_from_d5_adrfx_line | base | 3Q26 | 2.89 | pp | what D5's adr_fx_pp row actually measures: 3Q26 revenue FX, against management's stated ~3.0 after hedging |
| revenue_fx_pp_from_d5_adrfx_line | base | 4Q26 | 0.93 | pp | same, 4Q26 revenue FX; D5's adopted revenue line (Phi x 0.851) is 0.98 |

## 3. Derivation chain

**Object 1 — D4 / adrv3 N midpoint (contemporaneous, disclosed-calibrated).**
1. Letters → `data/processed/predictive/03_quarterly_panel.csv`: `adr_fx_effect = adr_yoy − adr_exfx_yoy` (`analysis/src/predictive/03_nowcast_tests.py` L66), 2Q22–2Q26.
2. FRED daily crosses → quarterly averages → `analysis/src/overnight2/B4_application_3q26_4q26.py`:
   - `est_from_eur = −0.5687 + 0.4512 × EURUSD_yoy%(q)` — two-parameter OLS of the disclosed series on the contemporaneous euro cross, window `ex21`, n 17 (`data/processed/overnight/05_fx_fits.csv`, reproduced to the fourth decimal in `fx-lag.md` §2).
   - `est_from_regional_baskets = Σ_r (GBV_share_2025_r / Σ shares) × passthrough_r × basket_yoy_r(q)` — **no parameter fitted to this target**. GBV shares FY2025 NA .4415 / EMEA .3743 / LatAm .0936 / APAC .0907; pass-throughs NA 1.00 / EMEA 1.04 / LatAm 0.62 / APAC 0.86 (WS10 fits); destination-currency baskets (NA USD .90 CAD .08 MXN .02; EMEA EUR .70 GBP .25 USD .05; LatAm BRL .55 MXN .38 USD .07; APAC AUD .55 JPY .20 KRW .10 INR .07 USD .08), geometric weighted.
   - → `data/processed/overnight2/B/B_adr_fx_estimator_backtest.csv` (17 rows, each estimate and its error against the disclosed point).
3. `analysis/src/adrv3/N1_fx_estimator.py` → `est_from_midpoint = (eur + baskets)/2`; per-quarter and per-window RMSE/bias → `data/processed/adrv3/N/N1_fx_estimator_by_quarter.csv`, `..._window_summary.csv`, `N1_fx_choice_card.csv` (row `quarter=3Q26, fx_estimator=midpoint`, column `fx_effect_pp` = **−0.43**; `4Q26` = **+0.15**).
4. → `analysis/src/adrv3/P1_card_v3.py` → `data/processed/adrv3/P/adr_card_v3.csv`, `fx_estimator=midpoint` → D4 §2a `fx_pp` −0.430.

**Object 2 — D5 / `fx_lag_v2 point_phi_adrfx_pp` (lagged; a revenue construction).**
1. FRED daily (cached `fx_daily_2026-09-11.csv`, through 2026-09-04) → `baskets.py` → `02_basket_quarterly.csv`, global revenue-weighted basket (3Q26 spot-held +0.595%, 2Q26 +2.266%, 1Q26 +5.673%).
2. `fits.py` stage (b): OLS of the **disclosed ADR-FX** series on the **contemporaneous** basket, 1Q23–2Q26, n 14 → **slope 0.872, intercept −0.076, r 0.962** (printed live by `run.py`, `stdout_fx_lag_v2.txt` line 21). *This* fit is a contemporaneous ADR-FX estimator, and the package publishes its 3Q26 value as `adr_fx_3Q26_fitted_pp` = **+0.44**.
3. `exhibit.py::forecast_4q26` L283-289 then **discards the contemporaneous term** and evaluates the fit at lags 1 and 2: `phi_adr = ⅔·f(basket_{q−1}) + ⅓·f(basket_{q−2})` → column `point_phi_adrfx_pp` in `23_forecast_4q26_v2.csv` (3Q26 spot-held **2.89**, 4Q26 **0.93**) → D5 §2b and §2a `adr_fx_pp`.
4. The same construction at one decimal, on *disclosed* rather than fitted lags, is `exhibit.py::kernel_carried` → `27_kernel_carried_fx_v2.csv` row **`A_disclosed_ADR_FX_through_Phi`**, +2.5 / +0.7. The function's own docstring: *"Booking-date FX carried through the Phi kernel"*. B4 §6 prints it as one of five readings of **3Q26/4Q26 revenue FX**, beside the adopted Φ×0.851 (+2.9 / +1.0).

**Why the lag is there, and why it does not belong on ADR.** `fx-lag.md` §4 (Object B, the wedge): *"ADR FX is contemporaneous-at-booking by construction, so if the revenue leg needs a lag and the ADR leg does not, the wedge should load on lags 1-2 and not on lag 0"* — and it does (r −0.05 at lag 0, positive at lags 1 and 2). GBV, nights and therefore ADR are **booking-quarter** metrics; revenue is recognised at check-in, roughly 0.43–0.50 quarters later. The Φ(0, ⅔, ⅓) kernel **is** that recognition lag. Applying it to an ADR-FX series converts ADR FX into revenue FX. That is precisely what `point_phi_adrfx_pp` does, and it is what the 2Q26 record shows: disclosed ADR FX +1.3 in 2Q26 against disclosed **revenue** FX +4.0, and ⅔(+5.0 in 1Q26) + ⅓(+2.9 in 4Q25) = +4.3 ≈ 4.
One more basis break: the ADR-FX disclosure is **gross** (hedges are designated against revenue, not GBV), while management's ~+3pp revenue figure is **after hedging**. The programme's own candidate list for the 3Q26 revenue integer (`docs/pitch-forecasts/questions/q3-revenue-fx-integer/datasets/c08_spec_points.csv`) carries the row *"Phi on disclosed ADR-FX at scale 1 (reading A), **less 0.21pp hedge**"* = 2.32 — it subtracts a hedge drag, which is only meaningful for a revenue quantity.

## 4. Governing sources

| date | note or package | claim | status (governs / superseded by …) |
|---|---|---|---|
| 2026-08-06 (web 1 of 5) | 2Q26 shareholder letter, 8-K exh. 99.1, `sec.gov/Archives/edgar/data/1559720/000119312526337928/d70413dex991.htm` | ADR $184, **+5% reported, +4% ex-FX**; 3Q26 revenue guide "inclusive of an approximate three percentage point FX tailwind **after factoring in our hedging program**"; 3Q26 ADR "a moderate increase … due to **mix shift and price appreciation**" — FX not named | **PRIMARY.** Fixes the disclosed definition, fixes ~+3pp as a *revenue* figure, and shows management naming no FX effect on 3Q26 ADR. |
| 2026-09-11 | `research/notes/adrv3/N_fx-estimator-and-q4-lap-decisions.md` + `analysis/src/adrv3/N1_fx_estimator.py` | midpoint of euro fit and regional baskets is the ADR-FX estimator: RMSE 0.406pp on 2Q22–2Q26 (euro 0.458, baskets 0.535) and 0.332 on 1Q24–2Q26 (0.455, 0.416); 3Q26 −0.43, 4Q26 +0.15. **Self-declared "not a test … decision memos, not pre-registered pass/fail workstreams."** | **GOVERNS the ADR-FX leg.** Adopted by `docs/adrv3/SYNTHESIS.md` §5 and §6.4 and carried into D4, DEC-0008 and the committed card. |
| 2026-09-11 | `docs/revenue-forecast-strategy/05_backtests/fx-lag.md` §2 and §4 | ADR-FX contemporaneous fits reproduce to the fourth decimal (eur ex21 slope 0.4512; basket_global post22 slope 0.8717, r 0.962, se 0.667); **"ADR FX is contemporaneous-at-booking by construction"**; the revenue−ADR wedge loads on lags 1–2, not lag 0 | **GOVERNS the definitional question.** This is the sentence that settles X1. |
| 2026-09-11 | `docs/revenue-forecast-strategy/05_backtests/B4_FX_EXHIBIT.md` §5–§6 (`fx_lag_v2`) | §6 "Booking-date FX through Φ": five readings of **3Q26/4Q26 revenue FX**, of which A = disclosed ADR-FX through Φ (+2.5/+0.7) and C = Φ×0.851 (+2.9/+1.0, ADOPTED). "The 3Q26 ADR-FX point is not yet disclosed and is fitted from the contemporaneous basket … at **+0.4**." | **GOVERNS the revenue-FX line.** It never claims +2.9 is an ADR number; the ADR number it publishes is +0.4. |
| 2026-09-12 | `docs/revenue-forecast-strategy/05_backtests/FXSWAP_h2_bridge_kernel_fx.md` §1 and §4 | swaps the bridge's ADR-FX line to **−0.43 / +0.15** ("ADR v3 midpoint … RMSE 0.33pp on 1Q24–2Q26 vs 0.46 EUR / 0.42 baskets"); names the open gap as **"basket-contemporaneous +0.4 vs midpoint −0.4, a 0.8pp disagreement"** | **GOVERNS the cross-line arithmetic.** It already resolved the ADR-FX line to D4's object in September; the live gap it records is 0.8pp, not 3.3pp. |
| 2026-09-12 | `docs/revenue-forecast-strategy/05_backtests/REBASE_h2_bridge_v3_nights_adr.md` §5 and §7.3 | bridge v3 reproduces the ADR v3 card exactly (3Q26 ADR $177.17, 4Q26 $174.58) on the same FX leg; "the v2 inconsistency stands: the dollar path implicitly carries about +0.15pp of 4Q26 FX (Φ on the ADR-FX midpoint) against the +1.0pp kernel line on the basket" | consistent with FXSWAP; confirms the ADR-FX midpoint is the leg every downstream object is built on. |
| 2026-09-17 | `docs/pitch-forecasts/questions/q3-revenue-fx-integer/datasets/c08_spec_points.csv` | the candidate list for the **3Q26 revenue-FX integer** contains "Φ on disclosed ADR-FX at scale 1 (reading A), less 0.21pp hedge" 2.32 and "H2 Φ on disclosed ADR-FX, PIT coefficient 0.7313 (the registered spec)" 1.85 | independent confirmation that the Φ-on-ADR-FX family is a **revenue**-FX family in the programme's own registry. |
| 2026-09-18 | `docs/pitch-model-v2/dossiers/D5_d5_fx.md` §2b, §2a, §8.3 | publishes `point_phi_adrfx_pp` under the heading "ADR-FX contribution (pp of y/y ADR growth)" and as `adr_fx_pp` in the machine block; §8.3 recommends **(b) "let D4's digger own the reconciliation"** | **SUPERSEDED on the label by this dossier.** The numbers are read correctly from the file; the heading and the `adr_fx_pp` item name are wrong. D5's own §4 already flagged the ADR-FX gap as "unresolved … this dossier does not resolve". |
| 2026-09-18 | `docs/pitch-model-v2/dossiers/D4_d4_adr.md` §8.7, DEC-0008 | "someone must establish whether D5's `adr_fx_pp` is the same object as the ADR-FX effect Airbnb discloses in the letter (2Q26: +1.3pp)"; the committed card carries −0.43 | **this dossier answers it: it is not.** |
| 2026-09-11 | `docs/revenue-forecast-strategy/AGENT_BRIEF.md` §2 (FX row), §6 | "4Q26 revenue FX +1.0pp (CS +0.3–2.2); the −3.4pp step double counts; pre-registered: stated 3Q26 FX ≈ +3 → kernel". Kill list: the −3.4pp Q4 step; "82% of Q4 FX already determined" | governs. Note the brief's §2 FX row is **entirely about revenue FX**; the programme has no pre-registered line for the ADR-FX estimator at all. |

Web fetch budget: **1 of 5 used** (the SEC exhibit above). No airbnb.com page fetched; no credential typed.

## 5. Reproduction receipt
- Receipt: `data/processed/pitch_model_v2/receipts/X1/receipt.json` (copy: `receipt_fx_lag_v2.json`)
- Command: `PYTHONPATH=analysis/src python3 analysis/src/pitch_model_v2/repro.py --id X1 --watch analysis/src/forecast_methods/fx_lag_v2 --watch data/processed/forecast_methods/fx_lag_v2 --cmd "python3 analysis/src/forecast_methods/fx_lag_v2/run.py" --timeout 600` · Exit: **0** · Wall: 7.4s · Interpreter: `/Library/Frameworks/Python.framework/Versions/3.13/bin/python3` (plain `python3`, pandas 3; `.venv-pd2` not needed) · `fetch_fx_v2.py` NOT run, per the brief · `"changed": []`, `"restored": true` (the eight `__pycache__` `.pyc` files listed under `new_files` were removed by the wrapper; `git status` on both watched trees is clean)
- Output: `data/processed/forecast_methods/fx_lag_v2/23_forecast_4q26_v2.csv`, row `path=spot_held, quarter=3Q26`, column `point_phi_adrfx_pp` = **2.89** · D5's committed value: **2.89** · Tolerance: exact · **Match: yes**. Second cell from the same run: `27_kernel_carried_fx_v2.csv`, `adr_fx_3Q26_fitted_pp` = **0.44** (the package's own contemporaneous ADR-FX estimate), and `stdout_fx_lag_v2.txt` line 21 prints the fit live: *"ADR-FX on the contemporaneous basket: slope 0.872, intercept -0.076, r 0.962"*.
- Second command: `PYTHONPATH=analysis/src python3 analysis/src/pitch_model_v2/repro.py --id X1 --watch data/processed/adrv3/N --cmd "python3 analysis/src/adrv3/N1_fx_estimator.py" --timeout 300` · Exit: **0** · Wall: 0.2s · same interpreter · receipt `receipt_N1_fx_estimator.json`, `"changed": []`, `"new_files": []`, `"restored": true` — **byte-identical**. Output: `data/processed/adrv3/N/N1_fx_choice_card.csv`, row `quarter=3Q26, fx_estimator=midpoint`, column `fx_effect_pp` = **−0.43** · D4's committed value: **−0.430** · Tolerance: exact · **Match: yes**. Same file, `4Q26 / midpoint` = **+0.15**.
- Derived arithmetic (not a package run, so not through the wrapper; reads committed CSVs, writes only inside this receipt folder): `python3 data/processed/pitch_model_v2/receipts/X1/compare.py` → `X1_disclosed_vs_objects.csv`, `X1_estimator_scores.csv`, `X1_forward_cells.csv`, `X1_cells.json`, `compare_stdout.txt`; `python3 data/processed/pitch_model_v2/receipts/X1/impact.py` → `X1_model_impact.csv`, `impact_stdout.txt`. Cross-checks that landed: the N-midpoint RMSEs recompute to N's published 0.406 / 0.332 exactly; the reconstruction of `point_phi_adrfx_pp` from `exhibit.py`'s formula reproduces the committed forward cells (3Q26 2.89, 4Q26 0.93) to 0.00; the disclosed identity `reported − ex-FX = fx_effect_pp` closes to ≤0.042pp in all 14 quarters of `adr_history_components.csv`.
- Tree state after both runs: `git status --porcelain` clean on `analysis/src/forecast_methods/fx_lag_v2`, `data/processed/forecast_methods/fx_lag_v2` and `data/processed/adrv3`. No `"restored": false` was seen, so no hand restoration was needed. Nothing outside `docs/pitch-model-v2/dossiers/X1_x1_adr_fx_reconciliation.md` and `data/processed/pitch_model_v2/receipts/X1/` was written. Nothing committed.

## 6. Test record

The metric is RMSE against the **disclosed** ADR-FX series (17 quarters, 2Q22–2Q26). There is no naive baseline registered for this object in the harness and no guide or Street value for it, so those columns are `n/a` rather than blank.

| window | n | metric | this line (D4 N midpoint) | D5 `point_phi_adrfx` | naive | guide+cushion | Street | pre-registered pass line | pass/fail |
|---|---|---|---|---|---|---|---|---|
| full 2Q22–2Q26 | 17 | RMSE pp vs disclosed ADR FX | **0.406** | 2.424 | n/a — none registered | n/a (ADR FX is not guided) | n/a | **none exists** (N is self-declared "not a test") | descriptive |
| 1Q23–2Q26 (the W1 span) | 14 | same | **0.420** | 2.203 | n/a | n/a | n/a | none | descriptive |
| 1Q24–2Q26 (the W2 span) | 10 | same | **0.332** | 2.269 | n/a | n/a | n/a | none | descriptive |
| 2Q26 alone (latest print) | 1 | abs error vs disclosed +1.3 | **0.16** | 2.98 | n/a | n/a | n/a | none | descriptive |
| full 2Q22–2Q26 | 17 | RMSE pp vs disclosed **REVENUE** FX | 1.450 | **2.127** unscaled | n/a | n/a | n/a | none | descriptive; at the registered H2 scale the Φ family scores **0.99pp** PIT (B4) |
| ADR-A 1Q24–2Q26 / ADR-B 2Q24–2Q26 (card walk-forward, eur and baskets legs) | 10 / 9 | RMSE ratio vs naive, reported $ ADR | 0.912 / 0.898 (eur), 0.873 / 0.868 (baskets) | not run on this target | 1.000 | n/a | n/a | ratio < 1 and jackknife max < 1, 4 of 4 | pass (4 of 4) — **but the midpoint itself is not one of the four required checks** (0.889 / 0.876, labelled descriptive in D4 §6) |

Strongest known failure: **the object I recommend has never been scored against a pre-registered line, and the estimator comparison that selects it is in-sample on the same data it is scored on** — N declares itself "not a test", its windows (2Q22–2Q26, 1Q24–2Q26) are not the programme's W1/W2, the euro leg is a two-parameter OLS fitted on 17 of the same 17 disclosed quarters and the basket leg's origin and pass-through weights are WS-B judgement calls, so the 0.33–0.42pp advantage over `fx_lag_v2`'s contemporaneous fit (0.58pp) is a within-sample ranking of two in-sample fits and cannot be quoted as out-of-sample skill.

Three further failures worth naming. (a) **The remaining live disagreement is 0.87pp, not zero**: on the same contemporaneous definition, D4's midpoint says −0.43 for 3Q26 and `fx_lag_v2`'s basket fit says +0.44, and nothing in the repo separates them — FXSWAP flagged this in September and 5 Nov is the first test. (b) **`fx_lag_v2`'s PIT machinery leaks on exactly these features**: `fx-lag.md` §5 records that `b_lag1/2/3` and `adrfx_lag1/2` are built once from the current vintage of `L0_exact_regional_revenue.csv` with no `knowable_from` filter, so a PIT fit at an early guide date weights a 2022 basket with today's regional revenue split — my historical reconstruction of D5's object inherits that and is a description, not a PIT backtest. (c) **The disclosed target is itself noisy by construction**: it is an unrounded reported ADR minus a whole-integer ex-FX figure, so every observation carries up to ±0.5pp of the letter's rounding — a 0.4pp RMSE is at the resolution floor of the data, which is the honest reason no estimator in this family can be separated from another by much less than a point.

## 7. Kill list and consistency
- Kill-list check: **clean.** Nothing from AGENT_BRIEF §6 is quoted as ours. The **−3.4pp Q4 FX step** appears nowhere in this dossier. **"82% of Q4 FX already determined"** appears nowhere, and I did not import D5's neighbouring dispute about memo v3's "84% observed for 4Q26" — for the record, `data/processed/overnight/05_fx_schedule.csv` carries `driver_realised_share = 0.84` on the `2026Q4` rows, which is a plausible origin for that figure and a different object again from the `20_observed_share_triple` readings D5 checked; that belongs to D5, not to X1. No **"+4.05% fee uplift"** and no **L-primary ex-FX (+0.6 / +1.1)** figure is used.
- **Conflict 1, with D5 (the reason this line exists), resolved.** D5 §2b's heading "ADR-FX contribution (pp of y/y ADR growth)" and its §2a item name `adr_fx_pp` are wrong; the cell values are read correctly from `23_forecast_4q26_v2.csv`. The object is `point_phi_adrfx_pp`, which is B4 §6 reading A — a revenue-FX construction. D5's own §8.3 declined to pick a winner and recommended D4's digger own it; D4's §8.7 asked exactly the right question ("is D5's `adr_fx_pp` the same object as the ADR-FX effect Airbnb discloses"). **The answer is no.** D5's §2a rows `adr_fx_pp` (base 2.89 / 0.93 / 0.88 / 0.56, short 2.89 / 0.45 / −1.11 / −2.05, breaker 2.89 / 1.40 / 2.87 / 3.16) should be renamed to something like `revenue_fx_pp_phi_adrfx_driver` and never added to an ADR growth rate. Nothing in DEC-0010 is disturbed: DEC-0010 adopts **revenue** FX +0.98pp, which is the `point_phi_basket_scale_0.851_pp` column, not this one.
- **Conflict 2, with D4, minor and in D4's favour.** D4 §8.7 states D5 "has no 3Q27 or 4Q27 value". `23_forecast_4q26_v2.csv` does carry them (`point_phi_adrfx_pp` 3Q27 +0.24, 4Q27 +0.31, spot held); D5's dossier simply stopped at 2Q27. It does not change D4's recommendation, since those cells are the wrong object anyway.
- **Conflict 3, unresolved and named**: the 0.87pp spread between the two *contemporaneous* estimators (D4 midpoint −0.43, `fx_lag_v2` basket fit +0.44) for 3Q26, and 0.95pp for 4Q26 (+0.15 vs +1.10). FXSWAP §4 already carries it as an open item worth $24M of 4Q26 revenue through the GBV lag. This dossier narrows the dispute from 3.3pp to 0.87pp; it does not close it.
- Consistency with the committed model: **adopting the recommendation changes nothing.** DEC-0008's base ADR ($176.88, ex-FX +3.69) already carries −0.43; REBASE's bridge v3 and FXSWAP's bridge v2 both already carry −0.43 / +0.15; D4's FY27 path legs (−0.301 / −0.193 / +0.034 / −0.285) are the same family. The only thing that changes is that D4 §8.7 and D5 §8.3 can be closed.
- Consistency with the revenue line: the ADR-FX leg must **not** be added on top of the kernel revenue. R1/R2's kernel base is lagged GBV, which already carries booking-date FX; B4 §5 and FXSWAP's RESUME both say so ("Do not add any FX pp on top of the GBV-lag dollar path"). The recommendation here is a leg of the ADR/GBV build only.

## 8. Open choices
1. **Which object is the ADR-FX line?** Options: (a) D4's adrv3 N midpoint, −0.43 (3Q26) / +0.15 (4Q26), contemporaneous, calibrated on the disclosed series; (b) D5's `point_phi_adrfx_pp`, +2.89 / +0.93; (c) carry both as a range. — **Recommendation: (a).** Why: (b) puts zero weight on the quarter's own currencies and scores RMSE 2.20pp against the thing Airbnb actually discloses, wrong-signed in 4 of 17 quarters with a worst miss of 4.06pp, while (a) scores 0.42pp; (c) is not a range, it is two different quantities, and printing them side by side would be the error a judge is looking for. Adopting (a) changes no committed cell.
2. **Does D5's dossier get corrected, and by whom?** Options: (a) D5's digger renames §2b's heading and the §2a `adr_fx_pp` item to a revenue-FX name and adds one sentence pointing at X1; (b) X1 stands as the correction and D5 is left as written; (c) a human edits D5 at freeze. — **Recommendation: (a).** Why: the machine-readable §2a block is what a builder reads; an item literally named `adr_fx_pp` carrying a revenue number is a trap that survives any amount of prose around it. I did not edit D5 — the brief allows me only my own dossier.
3. **What band goes on the 3Q26 ADR-FX point?** Options: (a) N's two legs, −1.12 to +0.26; (b) widen to −1.12 to +0.44 to include `fx_lag_v2`'s contemporaneous basket fit, as §2 does; (c) point only, no band. — **Recommendation: (b).** Why: the +0.44 fit is a third contemporaneous estimator built by a different team on a different (revenue-weighted, holiday-fill-corrected) basket, and excluding it would hide the only live disagreement that remains. The band is ±0.8pp, about ±$1.3 of ADR and ±$190M of 3Q26 GBV.
4. **Should the estimator become a three-way average?** Options: (a) keep the two-leg midpoint N named; (b) average all three contemporaneous estimators (eur −1.12, adrv3 baskets +0.26, fx_lag_v2 basket +0.44 → −0.14 for 3Q26, +0.54 for 4Q26); (c) drop the euro leg, which is the one with no channel for the LatAm/APAC divergence that dominates 2024–26. — **Recommendation: (a) for 2 October**, with (b) computed and on record. Why: N's midpoint is the only one of the three with a written selection memo, a committed card built on it and two bridges reproducing it; re-picking an estimator nine days before the memo, on an in-sample ranking, is exactly the post-hoc move the programme's rules exist to prevent. But (b) and (c) are both defensible and (b) moves 3Q26 ADR by +$0.50.
5. **What does the 4Q26 ADR-FX leg carry?** Options: (a) +0.15, the N midpoint; (b) the basket family's +0.97 to +1.10; (c) a widened band −0.66 to +1.10 with +0.15 as the point. — **Recommendation: (c).** Why: the 4Q26 estimator spread (1.76pp between the euro and `fx_lag_v2` legs) is *wider* than 3Q26's, because 4Q26 is a pure spot-held projection with nothing printed, and 4Q26 is the quarter the pitch actually trades. 1.76pp is $2.9 of ADR and $390M of 4Q26 GBV — larger than the D2 nights case A/B difference.
6. **Pre-register the 5 November scoring of this object now.** Options: (a) the printed 3Q26 ADR-FX point (reported ADR y/y minus the letter's ex-FX figure) scores all four contemporaneous estimators — euro −1.12, adrv3 baskets +0.26, N midpoint −0.43, `fx_lag_v2` basket +0.44 — and the winner is named before the print; (b) score only the midpoint against its own point; (c) nothing. — **Recommendation: (a).** Why: it is free, it is already half-built (`P2_score_sheet.py --fx` takes the printed point and scores the three adrv3 estimators), it settles the 0.87pp gap FXSWAP left open, and pre-registering the four candidates before 5 Nov is the only way this line ever earns better than a B. Add `fx_lag_v2`'s +0.44 as a fourth candidate to the score sheet's list.

## 9. Judge Q&A
1. Q: "Your two FX numbers for the same quarter differ by more than three points. Which is the effect of currency on reported ADR, and what did Airbnb itself disclose?"
   A: **−0.43 points, and the other number is not an ADR number at all.** Airbnb discloses this effect directly: it gives reported ADR growth and ex-FX ADR growth in every letter, and the gap is the FX effect — in 2Q26, ADR was $184, up 5% reported and **4% ex-FX**, so **+1.3 points** of FX on our unrounded arithmetic. That is a *contemporaneous* translation effect, because ADR is a booking-quarter metric: it is this quarter's bookings in this quarter's currencies. Our −0.43 is the midpoint of two estimators of that quantity — a euro regression and an unfitted bottom-up build on four destination-currency baskets — and across the seventeen quarters Airbnb has disclosed it, that midpoint has a root-mean-square error of **0.4 points**, and missed the most recent print by 0.16. The +2.89 is a different object that our FX package produces for the *revenue* line: it is the currency basket of the **previous two quarters**, weighted two-thirds and one-third, with **zero weight on this quarter**, because revenue is recognised at check-in about half a quarter after booking. Scored against disclosed ADR FX it has an error of 2.2 points, the wrong sign in four of seventeen quarters, and a worst miss of 4.1 points. You can see it is a revenue number without any of that: it equals our own revenue-FX figure to the penny, +2.89 versus +2.89, and it lands within a tenth of management's guidance of "approximately three percentage points of FX tailwind" — which is a **revenue** sentence, after hedging, in the same letter. We had it mislabelled in one working paper; the model has always carried −0.43, and this is the paper that says why.
2. Q: "How do you know the lag belongs on revenue and not on ADR? That sounds convenient."
   A: Three independent ways, none of them ours. First, the accounting: gross booking value and nights are booked-in-the-quarter; revenue is recognised at check-in. Second, our own data: in 2Q26 Airbnb disclosed ADR FX of **+1.3** and revenue FX of **+4.0** in the same letter. Two-thirds of 1Q26's ADR FX (+5.0) plus one-third of 4Q25's (+2.9) is **+4.3** — the lag reproduces the revenue number from the ADR numbers, which is exactly what it is for. Third, we tested it: we regressed the revenue-minus-ADR FX wedge on the basket at lags zero, one and two, and it loads on lags one and two with essentially nothing at lag zero. And if that is still not convincing, note that our own FX package publishes a **contemporaneous** ADR-FX estimate for 3Q26 — **+0.44** — sitting a few lines above the +2.89 in the same output file. Its ADR number and our ADR number are 0.87 points apart. That is the real disagreement, and it is worth about $1.3 of ADR, not $5.7.
3. Q: "So what is the honest uncertainty on your ADR FX, and what happens on 5 November?"
   A: About ±0.8 points on 3Q26 and ±0.9 on 4Q26 — a genuinely wide band on a small number, and we show it: −1.12 on a euro-only fit, +0.26 on our regional baskets, +0.44 on the FX package's revenue-weighted basket. The euro is flat year-on-year while the Latin American and Asia-Pacific baskets are up 6% and 2-5%, so the estimators that carry regional divergence say positive and the euro-only one says negative, and 2026 looks like the regional era, not the 2022 broad-dollar era. We named the midpoint in September, before we knew which way it would break, and we have never re-picked it. The limits we will state unprompted: this estimator has never been scored against a pre-registered line, both of its legs are calibrated on the same seventeen quarters we score them on, and the disclosed target itself is an unrounded reported figure minus a whole-number ex-FX figure, so every observation carries up to half a point of the company's own rounding — a 0.4-point error is at the resolution floor of the data. On 5 November Airbnb prints the 3Q26 ex-FX ADR sentence and we score all four candidates against it in one line. We have written down which four, and what each predicts, before the print.
4. Q: "Does anything in your model change if you have this wrong?"
   A: Not in the direction you would fear, because the model already carries the ADR number, not the revenue one. Our committed 3Q26 ADR is $176.88, which is ex-FX +3.69 plus FX −0.43, and both bridges and the FY27 path are built on the same leg. Had the other number gone in, 3Q26 ADR would have been **$182.56** — 3.1% above the Street's $177.06 — with not one ex-FX assumption changed, and **$832 million** more of 3Q26 gross booking value. That is the size of a labelling error in this business, which is why we reconciled it on paper before the ADR line was built rather than discovering it in front of you. The one thing that does move if we are wrong within the honest band is 4Q26: the estimator spread there is 1.76 points, about $390 million of booking value, wider than the gap between our two nights cases.

## 10. Grade
Grade: B — both packages reproduced through the wrapper at exit 0 with `"changed": []` and `"restored": true`, and both disputed cells came back byte-identical (`point_phi_adrfx_pp` 3Q26 = 2.89, `N1_fx_choice_card` midpoint 3Q26 = −0.43), so the reconciliation rests on re-run code rather than on quoted notes; the definitional verdict is anchored in the 6 August 2026 letter and in the governing `fx-lag.md` sentence that ADR FX is contemporaneous-at-booking. It is not an A because the object I recommend has no pre-registered pass line anywhere in the programme — WS-N declares itself "not a test", its selection windows are not the harness W1/W2, both of its legs are calibrated in-sample on the same seventeen disclosed quarters they are scored against, and a 0.87pp disagreement with the only other contemporaneous estimator in the repo remains open until the 5 November print.
