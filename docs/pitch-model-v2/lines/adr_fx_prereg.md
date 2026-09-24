# ADR line v1 — pre-registration of the ex-ante FX-on-ADR engine and the ex-FX mechanism construction

Date 2026-09-21 (overnight session, Theo asleep; autonomous). Status: registered BEFORE any fit, walk-forward or
forecast is run. Proposed decision id **DEC-0034** (pending Theo's confirmation in the morning). Package
`analysis/src/pitch_model_v2/adr_engine/`; outputs `data/processed/pitch_model_v2/adr_engine/`; governing design
`adr_v1_design.md`; rationale file `final_adr.md`. Nothing above §9 is changed after the results are filed.

## 0. Why this object, and why now

ADR is line 2 of the official model (`model/ABNB_official_model.xlsx`, `Income_Statement` rows 10–11, still
yellow). The committed ADR card (adrv3 card v3, DEC-0008/0009/0027) carries **two** legs nobody has built as a
mechanism: (a) the FX leg is the midpoint of two in-sample fits chosen by an in-sample ranking on the same 17
quarters it is scored on (X1 §6: "cannot be quoted as out-of-sample skill"); (b) the ex-FX leg is a persistence
rule on an unobserved residual ("next quarter's residual is this quarter's"), which a lodging analyst will call a
carry, not a model. The nights line was rebuilt on 18 Sep as a disclosed-mechanism decomposition (DEC-0028); the
ADR line is rebuilt the same way here. The FX leg is the part that can be tested point-in-time, so it gets a
pre-registered pass line. The ex-FX leg is a construction on disclosed mechanics and is **not** given a pass
line it cannot earn (the lap quarters have never been scored, §6).

## 1. The identity the FX engine runs on

Airbnb records Gross Booking Value in USD at the exchange rate on the **booking date**; ADR = GBV ÷ Nights and
Seats Booked, both booking-dated. Constant-currency ADR translates the current period at the **prior-year**
period's rates. Therefore, to first order, the disclosed FX effect on ADR is a pure translation quantity:

```
FX_pp(t)  =  100 · Σ_c  ω_c(t)  ·  [ ē_c(t) / ē_c(t−4)  −  1 ]
```

- `ē_c(t)` = mean of the daily USD-per-unit rate of currency `c` over the business days of quarter `t`
  (FRED H.10 noon buying rates; bookings assumed uniform over business days — a stated assumption, §8).
- `ω_c(t)` = share of quarter-`t` GBV settled in currency `c`; USD legs contribute zero.
- No lag. Revenue FX lags (recognition at check-in, kernel Φ); ADR FX does not (X1 §3, `fx-lag.md` §4: "ADR FX
  is contemporaneous-at-booking by construction"). This engine never applies Φ to an ADR quantity.
- The identity closes on the disclosed data to ≤ 0.042pp in every quarter (`adr_history_components.csv`
  `identity_check_pp`): reported y/y − ex-FX y/y = FX pp.

The **only** unknown in the identity is the currency mix `ω`. Everything else is observable at the origin date,
apart from the unobserved remainder of the current quarter's rates.

## 2. The currency mix: structure, priors, and what is fitted

```
ω_c(t)  =  Σ_r  g_r(t) · β_r · κ_{r,c}
```

- `g_r(t)` = regional GBV share, from the 10-K "Geographic Mix" table of the **latest fiscal year filed before the
  origin date** (`data/processed/adr/01_regional_annual.csv`, `gbv_share_pct`; FY2021…FY2025). Point-in-time:
  FY(y) shares become knowable 7 calendar days after the 4Q(y) print date in `02_guidance_ledger.csv`.
- `κ_{r,c}` = within-region destination-currency basket, **frozen** at the WS-B / adrv3-N judgement weights already
  in the repo (`data/processed/forecast_methods/fx_lag_v2/01b_basket_weights_used.csv`, collapsed to FRED
  bilaterals): NA USD .90 CAD .08 MXN .02; EMEA EUR .70 GBP .25 USD .05; LatAm BRL .55 MXN .38 USD .07;
  APAC AUD .55 JPY .20 KRW .10 INR .07 USD .08. Not fitted here.
- `β_r` = regional pass-through scale, one per region, which absorbs (i) USD settlement inside a region that the
  basket misses, (ii) currencies the nine FRED bilaterals do not cover, (iii) the difference between destination
  currency and settlement currency. Prior **β_r ~ Normal(1, 0.25²)**, i.e. pure translation is the prior mean and
  a one-sigma deviation is a quarter of the exposure.

Three model variants, all fixed now, all reported whatever they score:

| variant | fitted parameters | description |
|---|---|---|
| **V0 translation** | 0 | β_r ≡ 1. The identity with the repo's frozen baskets and the 10-K GBV shares. |
| **V1 fitted pass-through** | 4 (+σ) | β_r estimated on disclosed quarters printed before the origin, with the prior above and the rounding-aware likelihood of §3. MAP (scipy) inside the walk-forward for speed; full posterior (PyMC NUTS, 4 chains) for the final in-sample estimate and the predictive band. |
| **V2 euro-only OLS** | 2 | `y = a + b · EURUSD_yoy(t)`, refit point-in-time — the comparator the card's midpoint half-uses (`05_fx_fits.csv`). |
| V3 broad-dollar OLS | 2 | `y = a + b · DTWEXBGS_yoy(t)`, refit point-in-time — the other classic proxy. |
| naive | 0 | the latest **disclosed** ADR-FX pp at the origin (at O1 that is FX(t−2); at O2 and O3 it is FX(t−1), which prints about day 35–40 of quarter t). |
| zero | 0 | 0pp. |

## 3. Target, likelihood, and the rounding floor

Target: `y_t` = disclosed ADR-FX pp for the 17 quarters 2Q22–2Q26 (`02_kpi_panel_quarterly.csv` `fx_pts_adr`,
identical to X1 §2a): unrounded reported ADR y/y from disclosed levels minus the letter's ex-FX figure. The ex-FX
figure is disclosed to whole points except 3Q23 and 4Q23 ("approximately 0.5%"). The observation is therefore an
**interval**: `[y_t − h_t, y_t + h_t]` with `h_t = 0.5` (whole-point quarters) or `0.25` (half-point quarters).

Likelihood for V1: Gaussian model error `ε ~ N(0, σ²)`, `σ ~ HalfNormal(1pp)`, scored on the interval
(probability mass of the prediction inside the interval), exactly the interval likelihood `fx-lag.md` §2 used.
Consequence stated in advance: an RMSE near 0.3–0.4pp is at the resolution floor of the data; two estimators
inside that floor cannot be separated and will not be claimed to be.

Scoring metrics, all reported: point RMSE (prediction − y_t), **interval RMSE** (distance to the nearest interval
edge, zero when inside — the rounding-fair metric), mean error (bias), and the ratio of each to the naive's.

## 4. Point-in-time protocol

Three forecast origins per target quarter `t`:

| origin | date | what is observed |
|---|---|---|
| **O1** quarter start | the day before the first calendar day of `t` | none of `t`'s rates; all of `t−4`'s |
| **O2** day 60 | first day of `t` + 59 days | about two-thirds of `t`'s business days |
| **O3** pre-print | the day before Airbnb's print date for `t` (`02_guidance_ledger.csv`) | all of `t`'s business days |

Information set at an origin `d`: FRED prints with observation date ≤ `d − 7` calendar days (H.10 is published
weekly with about a one-week lag — the convention of `B4_FX_EXHIBIT.md` §2); disclosed ADR-FX points whose print
date ≤ `d`; 10-K shares knowable ≤ `d`. Unobserved business days of `t` are filled with the **last observed rate
held constant** (spot held; a business day with no print inside a completed quarter takes the last rate on or
before it, the `fx_lag_v2` fix). The base quarter `t−4` is always fully observed.

## 5. Windows and the pass line (fixed now)

- **W1**: targets 1Q23–2Q26, n = 14 (fits use ≥ 3 prior disclosed points; 2Q22–4Q22 exist by 1Q23).
- **W2**: targets 1Q24–2Q26, n = 10.
- A variant is **promoted to the ADR-FX leg of the model** only if its point-RMSE ratio to the naive is
  **≤ 0.75 at O2 and at O3 on both windows**. O1 is reported, not scored for promotion (at quarter start the
  quantity is mostly unrealised FX; the number the pitch quotes on 2 Oct for 4Q26 is an O1-type number and will
  be labelled so).
- If both V0 and V1 pass, V1 is the leg only if its point RMSE is **strictly lower than V0's at O2 and O3 on
  both windows**; otherwise V0 is the leg (fewer parameters). If neither passes, the leg stays the committed
  card's midpoint (DEC-0027) and this engine's numbers are carried as a labelled cross-check.
- V2/V3/zero are comparators; they cannot be promoted by this registration.
- Everything is reported with n, both metrics, the per-quarter errors, and the moving-block bootstrap 90%
  interval of the ratio (block 4 quarters, 2,000 resamples).

## 6. The ex-FX ADR mechanism — a construction, registered but not given a pass line

```
exFX_yoy(t) = core(t) + bundle(t) + geo_mix(t) + unit_size(t) + los_mix(t) + seats(t) + interaction(t) + fee_K(t)
```

Definitions fixed now, sources named, each carried in the design with its evidence label:

- `geo_mix`, `unit_size`, `los_mix`, `seats`, `interaction`: the H/I measured and assumed terms, quarterly history
  `adr_history_components.csv` (1Q23–2Q26) and the 3Q26 measured terms `I_mix_terms_3q26.csv`, carried forward
  exactly as the card does (J3 convention). `fee_K` = 0 in base (DEC-0008), the K line as a labelled sensitivity.
- `residual(t)` = disclosed ex-FX minus those terms (the H residual, 1Q23–2Q26: mean 2.40 in 2023–25, 4.38 and
  4.85 in 1H26).
- `bundle(t)` = the product bundle's ADR contribution **as management sized it**, on the nights line's own lap
  calendar: the 1Q26 call's "~4 points of GBV growth vs ~3 points of nights growth" (ledger D032, mirror) gives
  ≈ 1pp of ADR; 4Q25 ">200bp nights / ~300bp GBV" (D014, mirror) gives ≈ 1pp. The split of that ~1pp between the
  RNPL leg (live NA from 3Q25, global from 17 Feb 2026 — larger-home mix) and the fee/cancellation leg (global
  from Oct 2025 — host reprice) is **assumed** using the residual's own dated steps (K4 "lap only, residual
  steps": 3Q25 step 0.92, 4Q25 step 0.88) scaled to the disclosed ~1pp; each leg laps on its filed anniversary.
- `core(t)` = residual(t) − bundle(t): the like-for-like host-pricing rate with the product steps removed.
  Forward rule: **carried at its latest observed value** (2Q26), the same carry the card applies to the whole
  residual — so the base and the card differ only by whether the bundle laps.

Alternatives carried beside the base, never blended: (i) card v3 `last_q` (no lap), (ii) K4 lap-only residual
steps, (iii) mean reversion to the 2023–25 mean, (iv) AR(1) on the residual, (v) the regional carry (L, memo
only). A judge-facing band = the parameter envelope (bundle split, ~1pp sizing 0.8–1.2, core carry ± its own
2023–26 quarterly change sd) plus the FX predictive band.

No walk-forward claim is made for the lap mechanism: the only lapped quarter in history (3Q26) has not printed.
What **is** scorable is the carry rule for `core` vs the carry rule for `residual` on 3Q25–2Q26 (n 4, descriptive).

## 7. Ex-ante forecast and falsifiers

As-of dates: **2026-09-21** (this build; FRED through 18 Sep), **2026-10-02** (memo), **2026-11-05** (3Q26 print /
4Q26 guide), **2027-02-11** (4Q26 print / FY27 guide). Targets 3Q26–4Q27. Spot held after the last print. Predictive
band from a moving-block bootstrap of the joint daily log-return vector of the nine currencies (block 20 business
days, sample 2015-01-02 → last print, 4,000 paths) applied to the unobserved days; report P10/P50/P90. The ±5%
parallel USD shift (D5's one-sigma device) is reported for comparability, not as the band.

Falsifiers: (a) on 5 Nov the printed 3Q26 ADR-FX pp (reported y/y − ex-FX figure) must fall inside the 21 Sep
as-of 80% band, else the weights are wrong and the leg is withdrawn; (b) on 11 Feb 2027 the printed 4Q26 point
must fall inside the 5 Nov as-of 80% band; (c) the printed 3Q26 ex-FX ADR y/y is placed against the mechanism's
base and the card's carry — a print at or below the mechanism says the bundle laps; a print at or above the carry
says it does not; in between is unresolved and both stay on the slide.

## 8. Stated assumptions and what will not be done

Assumptions: uniform booking intensity over business days; destination currency ≈ settlement currency; the nine
FRED bilaterals span the non-USD exposure; hedges are designated against revenue, not GBV (the ADR-FX disclosure
is gross of hedging — X1 §3); the 10-K GBV shares are the right exposure weights (revenue shares are the
alternative, run as a sensitivity, not a variant).

Will not be done: no lag on ADR FX; no variant added or dropped after results; no window or origin chosen after
results; no quarter dropped; no scenario selected by its 3Q26 output; no scraping; nothing under
`analysis/src/forecast_methods/`, `data/processed/forecast_methods/`, `data/processed/overnight/` or `model/`
other than the official workbook's new ADR sheet and rows is written.

## 9. Outputs

`fx_pit_walkforward.csv` (every origin × target × variant), `fx_scores.csv` (both windows, both metrics, ratios,
bootstrap intervals), `fx_weights_posterior.csv`, `fx_forecast_asof.csv` (as-of × quarter × P10/P50/P90),
`exfx_mechanism.csv` (quarter × term, history and forward), `adr_path.csv` (reported ADR path, band, Street,
z-scores), figures under `docs/pitch-model-v2/lines/figures/adr_*.png|svg`, the `ADR_Engine` sheet and rows 8–11
of `Income_Statement` in `model/ABNB_official_model.xlsx`, `adr_v1_design.md`, `final_adr.md`.

---

## 10. Results (to be filed after the run; nothing above this line changes)

Filed 2026-09-22 02:10 EDT after the run (`python3 -m pitch_model_v2.adr_engine.run`, exit 0; FRED through 2026-09-18;
pre-registration blob at registration `0495e5f32a904274cd0cce0c5ffa73f41aa70918`, verified with `git hash-object` before this
section was appended).

**Walk-forward (§4–§5), point RMSE ratio to the naive (latest disclosed FX pp), bootstrap 90% interval in brackets:**

| variant | W1 O1 (n 13) | W1 O2 (n 14) | W1 O3 (n 14) | W2 O1 (n 10) | W2 O2 (n 10) | W2 O3 (n 10) |
|---|---|---|---|---|---|---|
| **V0 translation (0 parameters)** | 0.44 [0.19, 0.73] | **0.34** [0.27, 0.44] | **0.30** [0.25, 0.37] | 0.63 [0.36, 0.88] | **0.38** [0.29, 0.51] | **0.32** [0.23, 0.42] |
| V1 fitted pass-through | 0.50 | 0.38 | 0.34 | 0.67 | 0.35 | 0.29 |
| V2 euro-only OLS (comparator; bias −0.27 to −0.46) | 0.40 | 0.27 | 0.28 | 0.53 | 0.27 | 0.27 |
| V3 broad-dollar OLS | 0.59 | 0.53 | 0.52 | 0.76 | 0.60 | 0.57 |
| zero | 0.74 | 1.08 | 1.08 | 0.97 | 1.16 | 1.16 |

RMSE in pp, V0: W1 1.31 / 0.72 / 0.64 (naive 3.00 / 2.11); W2 1.47 / 0.75 / 0.62 (naive 2.36 / 1.97). Interval RMSE at O3
(rounding-fair): 0.27 (W1), 0.25 (W2) — at the resolution floor. Bias +0.15 / −0.04 at O3.

- **V0 passes** (≤ 0.75 at O2 and O3 on both windows, every bootstrap upper bound ≤ 0.51). **V1 passes** but is not lower
  than V0 on both windows (W1: 0.38 vs 0.34, 0.34 vs 0.30). **Promoted leg: V0, the translation identity.** V2 has the lowest
  point RMSE at O2/O3 but is a comparator by registration and is biased low by 0.3–0.5pp (no LatAm/APAC channel).
- Sensitivity (§8): revenue-share weights instead of GBV shares → V0 ratios 0.35 / 0.31 (W1), 0.39 / 0.33 (W2); unchanged.
- Posterior on the pass-through (descriptive, all 17 quarters; PyMC NUTS 4 × 1,500, R̂ 1.00): β NA 0.99 [0.59, 1.40],
  EMEA **1.20 [1.09, 1.31]** (P > 1 = 0.996), LatAm **0.46 [0.17, 0.78]** (P > 1 = 0.006), APAC 1.27 [0.88, 1.64], σ 0.53pp.
- **Ex-ante forecast (§7), as of 2026-09-21, spot held from 18 Sep, P10–P90:** 3Q26 **+0.42** [0.36, 0.48] (88% of business
  days printed); 4Q26 **+0.51** [−1.06, +2.26]; 1Q27 −0.37 [−3.20, +2.78]; 2Q27 −0.43 [−3.90, +3.68]; 3Q27 −0.15; 4Q27 0.00
  (base 4Q26 also spot-held). ±5% USD device: 4Q26 +3.39 / −2.36; 1Q27 +2.46 / −3.20. At the 5 Nov guide date 4Q26 will be
  32% printed and its band [−0.78, +1.97]; at 11 Feb 1Q27 39% printed, band [−2.20, +1.72].
- Ex-FX construction (§6): base 3.32 / 2.78 / 2.42 / 2.96 / 2.86 / 2.93 (3Q26–4Q27); core carried 3.85; bundle 0.49 in 3Q26,
  0 from 4Q26. Descriptive carry check on 3Q25–2Q26 (n 4): core-carry + known bundle errors −0.39 / −0.68 / −0.47 vs residual
  carry −0.88 / −0.68 / −0.47 (identical when no leg changes; better in the one quarter a leg went live).
- Files: as §9. Figures `adr_fx_walkforward`, `adr_fx_currency_contributions`, `adr_exfx_mechanism`, `adr_path_vs_street`,
  `adr_fx_passthrough_posterior`, `adr_constellation`, `adr_full_logic`. Nothing in §0–§9 was changed after the run.

---

## 11. Dated amendment — 23 September 2026, filed before the 3Q26 print (5 Nov 2026)

Appended; nothing above is changed. Source: the 22 Sep adversarial audit
(`docs/pitch-model-v2/dossiers/ADR_AUDIT_krish.md`, finding F11). Code: `analysis/src/pitch_model_v2/adr_engine_v3/fx_falsifier.py`.

**Why.** Falsifier §7(a) required the printed 3Q26 ADR-FX pp to fall inside the 21 Sep 80% band [0.36, 0.48]. The
printed figure is reported ADR y/y (unrounded, from disclosed levels) minus the letter's **whole-point** ex-FX, so it
carries ±0.5pp of rounding. A perfectly correct identity would land inside a 0.125pp band only about 12% of the time,
so the test would withdraw a correct leg about 88% of the time. §7(b) has the same defect on a wider band.

**Replacement (applies to both 7a and 7b).** For each named candidate c with point μ_c, with y the printed ADR-FX pp
and h the rounding half-width (0.5; 0.25 if the letter gives a half-point ex-FX), compute

L_c = P(μ_c + e ∈ [y − h, y + h]), where e ~ N(0, 0.44²) (0.44 = V1's MAP model error on all 17 quarters).

1. **The identity (V0) is withdrawn as the leg only if its L is the lowest** of the named candidates.
2. **V1 replaces it only if V1's L is the highest and at least 3× V0's.** Otherwise V0 stays and the ranking is
   reported.

**Named candidates for 3Q26, fixed now:**

| candidate | point (pp) |
|---|---:|
| V0 identity | +0.415 |
| V1 fitted pass-through | +0.030 |
| committed card midpoint | −0.43 |
| euro-only fit | −1.12 |

The V0 and V1 points are re-computed at O3 (FRED through the print date minus 7 days) before scoring, as the
walk-forward does; the card and euro-fit points are fixed as above.

**Candidates for 4Q26 (scored 11 Feb 2027)** are fixed on 5 Nov 2026 at that as-of date: V0 and V1 recomputed, the
card's +0.15, and the euro fit recomputed.

**Operating characteristics, simulated before the print.** Share of prints that would withdraw V0, by which candidate
is actually true:

| true FX | withdrawn |
|---|---:|
| the identity's +0.415 | 0% |
| V1's +0.03 | 11% |
| the card's −0.43 | 57% |
| the euro fit's −1.12 | 100% |

A single whole-point-rounded print can separate the identity from the euro fit, but not reliably from V1 or the
fx_lag_v2 basket (+0.44). That is stated now so it is not discovered on 5 Nov.

## 12. Dated addendum — 23 September 2026, before the 3Q26 print: if the owner adopts the midpoint as the leg

Appended; nothing above is changed, and the V0 promotion result in §10 stands.

**Context.** On 23 Sep the ADR owner proposed (DEC-0048) that the FX leg for 3Q26 and 4Q26 be the card's method:
the midpoint of V0 and V2, refreshed on this engine's data. Scored point in time on this registration's own
protocol, it has the lowest RMSE ratio in all four promotion cells (0.223 / 0.199 / 0.247 / 0.201, against V0's
0.344 / 0.303 / 0.383 / 0.317; `adr_engine_v3/fx_scores.csv`). That comparison was run after the registration and is
labelled as such. The registration's promotion rule governs whether the identity has skill; it does not oblige its
adoption.

**Falsifier for a midpoint leg.** A leg in the middle of the candidate range can never rank last, so §11's rule
(withdraw only if worst) has no teeth for it. For the midpoint leg, scored with §11's likelihood L_c:

- The named candidates are §11's four plus the refreshed midpoint (−0.406 at 21 Sep, recomputed at O3 before
  scoring).
- **The leg is withdrawn if the best candidate's L is at least 3× the leg's L.**

Simulated before the print, the share of prints that would withdraw the leg, by which candidate is actually true:

| true FX | withdrawn |
|---|---:|
| the midpoint's −0.41 | 0% |
| V1's +0.03 | 14% |
| the euro fit's −1.12 | 41% |
| the identity's +0.42 | 53% |

One rounded print gives this much power and no more; it is stated now so it is not discovered on 5 Nov.
