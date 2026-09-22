# Final line — ADR (average daily rate, GBV ÷ Nights and Seats Booked)

**Version 1 — 22 September 2026** (overnight, autonomous; every decision below is *proposed* and awaits Theo:
DEC-0034, DEC-0035, DEC-0036). Rationale file for the second settled line of the pitch model v2, per **DEC-0026**:
why each base number stands, the data and model behind it, every alternative beside it, and how the thesis
catalysts enter it. The governing construction is [`adr_v1_design.md`](adr_v1_design.md) (the full logic,
figures, the analyst's attacks); the pre-registration is [`adr_fx_prereg.md`](adr_fx_prereg.md). Scope: **base
scenario** (DEC-0020); alternatives are carried beside it, never blended (DEC-0016: no input chosen to reach a
price). Everything is in this repository; the Street row is a dated Bloomberg MODL aggregate.

## 1. The line at a glance

| period | base ADR ($) | y/y | ex-FX | FX pp | band ($) | how the number is constructed | decision |
|---|---:|---:|---:|---:|---|---|---|
| 1Q23–2Q26 | printed (168.43 … 183.73) | | letters | letters | — | 8-K Ex-99.1 KPI box; identity closes ≤ 0.04pp | DEC-0003 |
| 2Q26 | 183.73 | +5.30% | +4 | +1.3 | — | printed; the naive the FX leg is scored against | DEC-0003 |
| **3Q26** | **177.68** | **+3.73%** | **+3.32** | **+0.42** | 176.01–179.36 | 171.29 × (1 + (3.316 + 0.415)/100): core 3.85 + bundle 0.49 + geo −1.29 + unit 0.80 + LOS 0.06 + seats −0.48 + inter. −0.10; FX identity, 88% printed | DEC-0034/35 |
| **4Q26** | **173.03** | **+3.30%** | **+2.78** | **+0.51** | 169.80–176.27 | 167.51 × (1 + (2.784 + 0.514)/100): bundle fully lapped; geo −1.34 | same |
| **1Q27** | **190.65** | **+2.05%** | 2.42 | −0.37 | 185.52–195.77 | 186.82 × …; geo −1.62 (Middle East lap in ex-NA nights); seats −0.57 | same |
| **2Q27** | **188.38** | **+2.53%** | 2.96 | −0.43 | 182.41–194.35 | 183.73 × … | same |
| **3Q27** | **182.51** | **+2.72%** | 2.86 | −0.15 | 175.83–189.18 | chained on our 3Q26 | same |
| **4Q27** | **178.10** | **+2.93%** | 2.93 | 0.00 | 171.35–184.85 | chained on our 4Q26; FX zero by construction | same |
| **FY27** | **185.21** | **+2.54%** | | | | nights-weighted on the nights line (621.85m); FY26 $180.62 | same |

Alternatives carried beside each decided number (design §3.6):

| period | base | shown beside it |
|---|---|---|
| 3Q26 | **177.68 (+3.7%)** | card v3 carry at the identity FX 178.32 · card v3 as committed (DEC-0008, midpoint FX −0.43) 176.88 · core mean reversion 175.20 · AR(1) 177.30 · +K line 177.97 · **Street 177.06 (n 26)** |
| 4Q26 | **173.03 (+3.3%)** | card carry 174.55 · committed card 173.94 · mean reversion 170.60 · AR(1) 172.38 · +K 173.66 · **Street 171.33 (n 25)** |
| 1Q27–2Q27 | 190.65 / 188.38 | full lap (ex-NA RNPL sized at the 1H26 steps) ex-FX 1.96 / 1.81 · committed FY27 path 192.11 / 188.48 |

Mechanical warnings, all real:

1. **4Q27's FX is 0.00 because its base quarter is also unobserved** (both spot-held); the P10–P90 of ±5pp is the
   honest content of that cell, not the point.
2. **3Q27 and 4Q27 chain on the engine's own 3Q26 and 4Q26**, so any 5 Nov revision propagates.
3. **The band widens fast**: ±0.98pp in 3Q26, ±1.9 in 4Q26, ±2.7–3.9 in 2027, almost all of it FX. A 2027 ADR
   is a statement about ex-FX shape plus a currency view, and the pitch should present it that way.

## 2. Why 3Q26 is $177.68, word by word

**Base.** 3Q25 printed ADR $171.29 (10-Q). Everything below is a growth rate on that base.

**FX, +0.42pp.** Airbnb books GBV in USD at the booking-date rate and restates constant currency at the prior
year's rates, so the FX effect on ADR is the year-on-year change of the quarter's average exchange rates
weighted by the GBV currency mix. With the 10-K FY2025 regional GBV shares (NA 44.1 / EMEA 37.4 / LatAm 9.4 /
APAC 9.1%) and the repo's frozen destination baskets, the currency weights are EUR 26%, GBP 9%, BRL 5%, AUD 5%,
MXN 4%, CAD 3.5%, JPY 2%, KRW 1%, INR 0.6%, USD 43%. On FRED data through 18 Sep (88% of the quarter's business
days), the euro is −1.5% y/y (−0.38pp), sterling flat, the peso +8.2% (+0.37), the real +6.1% (+0.31), the
Australian dollar +8.1% (+0.40), yen −7.3% (−0.13), the rest small: **+0.42pp**, band 0.36–0.48 for the days left.
Nothing is fitted. Tested point in time against the 17 quarters Airbnb has disclosed the effect, the identity's
RMSE is a third of the naive carry's (ratios 0.34 / 0.30 on W1, 0.38 / 0.32 on W2; pre-registered pass line
0.75) and sits at the rounding floor (interval RMSE 0.25–0.27pp). The committed card's leg (−0.43) is the midpoint
of a euro-only fit and a basket; the euro fit is biased −0.3 to −0.5 in every window because it cannot see the
peso, the real or the Australian dollar, and 3Q26 is their quarter. The 2Q26 letter's 3Q26 ADR outlook names
"mix shift and price appreciation" and drops FX for the first time since 1Q25 — consistent with a number near
zero; the print decides between +0.4 and −0.4 (§7).

**Ex-FX, +3.32pp**, seven sourced pieces:

- **Core like-for-like pricing, +3.85.** The 2Q26 residual (ex-FX 4.0 less the five measured/assumed terms) is
  4.85; less the product bundle's ~1pp it is 3.85. It is carried flat — the same carry the committed card applies
  to the whole residual — and it is **the one unobserved line**: 1.45pp above its 2023–25 mean of 2.40, with no
  filed mechanism for the difference. Its own one-quarter-ahead error (0.88pp, the sd of its quarterly changes
  since 1Q23) is in the band; its full reversion (ADR $175.20) is the named downside.
- **Bundle, +0.49.** Management sized the three-feature bundle at "over 200bp of nights / roughly 300bp of GBV"
  (4Q25 call) and "approximately three points of nights / approximately four points of GBV" (1Q26 call) — about
  1pp of ADR each time, **transcript-only** (no filing carries the figures; the filed substitutes are "roughly
  20% of global GBV came from Reserve Now, Pay Later" and the 2Q26 10-Q's "the increase in ADR was driven in part
  by the continued adoption of RNPL"). Split by the residual's own dated steps (3Q25 +0.92 when US RNPL went
  live alone; 4Q25 +0.88 when the cancellation redesign and single fee went live): RNPL-NA 0.51, fee/cancel
  0.49. In 3Q26 the US RNPL leg has lapped (live Aug 2025); the fee/cancellation leg (live Oct 2025) is still in
  the year-on-year: **0.49**.
- **Geographic mix, −1.29.** Share-shift arithmetic at constant regional prices on 3Q25 shares and anchored
  regional ADR ($255 NA / $159 EMEA / $95 LatAm / $118 APAC), with regional nights growth from the nights line
  (NA +5.6%, ex-NA +11.6% split EMEA 7.1 / LatAm 17.7 / APAC 15.9). The method reproduces the disclosed-share
  term within 0.13pp on 2Q24–2Q26. The card's −1.43 (E stays split) is the alternative.
- **Unit size, +0.80.** Booked capacity per reviewed stay +1.35% y/y (2.05m vintage-matched reviews, 119
  markets) × 0.592 hedonic. The filed read — Bedroom Nights Booked +12% vs nights +10% — at the measured
  bedroom elasticity of 0.23 is +0.5–0.8pp; not "half of ADR growth" (kill list).
- **Length of stay, +0.06**; **seats / new business, −0.48** (assumed volumes; Experiences supply +80% y/y);
  **interaction, −0.10**. Card terms, carried.

Sum **3.32**; reported **3.73%**; **$177.68**, band $176.01–179.36 (±0.98pp: core carry error 0.88, bundle 0.8–1.2,
the mix bands, FX 0.05, in quadrature). Street $177.06 (+3.37%, n 26, range 173.71–179.12): z +0.37,
**P(print ≥ Street) 65%**. On the Street.

## 3. Why 4Q26 is $173.03

Base 4Q25 $167.51. FX **+0.51** (0% printed; P10 −1.06, P90 +2.26; at held spot the peso, real and Aussie still
outweigh the euro against the 4Q25 base; at the 5 Nov guide date 32% will be printed and the band [−0.78,
+1.97]). Ex-FX **2.78**: core 3.85, **bundle 0** (both 2025 legs lapped — the cancellation redesign and fee
tranche 1 went live in October 2025), geo −1.34, unit 0.80, LOS 0.06, seats −0.48, interaction −0.10. Reported
**3.30%**, band ±1.93pp ($169.80–176.27). Street $171.33 (+2.28%, n 25): z +0.53, **P(≥ Street) 70%**. The Street
already has 4Q26 ADR decelerating to +2.3% — FX rolling off (4Q25 carried +2.9pp) and ex-FX slowing — so the base
sits **$1.70 (1.0%) above it**, mostly because held-spot FX is +0.5 rather than zero. The K4 scenarios for the
4Q26 residual (3.06 lap-only, 3.85 disclosed-bundle lap, 4.85 carry, 5.22 K-chained) bracket the base's 3.85
exactly at the "disclosed bundle laps" row; the card's carry (no lap) is $174.55 at the same FX; the fee tranche 2
reprice, which peaks rather than laps in 4Q26, is the +K row ($173.66).

## 4. 2027: the shape

FX at held spot is slightly negative (1Q27 −0.37, 2Q27 −0.43; the euro base of 1Q26–2Q26 was strong) with
±3pp bands; ex-FX runs 2.4 / 3.0 / 2.9 / 2.9 — the core at 3.85, the bundle gone, geo mix −1.6 in 1Q27 (the
Middle East lap lifts ex-NA nights) then −1.1 to −1.2, seats −0.57. Levels $190.65 / 188.38 / 182.51 / 178.10;
FY27 $185.21, +2.54%. The committed FY27 path (D4 §2a: 192.11 / 188.48 / 181.38 / 177.47, on the with-K residual
glide and the N-midpoint FX) is within $1.5 of every quarter; the difference is composition, not level. **No FY
ADR consensus exists** (V1, exhaustive). The "full lap" alternative (the 1H26 residual steps were ex-NA RNPL and
lap in 1H27) takes 1Q27–2Q27 ex-FX to 1.96 / 1.81 and is the second-most-likely shape after the base.

## 5. What is unbacktested

The lap mechanism (the only lapped quarter, 3Q26, has not printed); the core carry beyond what its own history
says (the H component build loses to naive 1.58×, so no component-based forecast is claimed); the seats term
(no volumes disclosed); the 2027 FX (a currency view). What **is** tested: the FX identity, point in time,
three origins, both windows, 17 disclosed quarters, pre-registered.

## 6. How the thesis catalysts enter this line

- **RNPL.** Two channels, both carried. Mix into larger entire homes lifts ADR (the 0.51pp NA leg live 3Q25–2Q26,
  lapping 3Q26; ex-NA leg unsized, 0 in base, 1.15 in the alternative); lead-time lengthening ("longer booking
  lead times", D016/D045) is a non-price reason for the residual's rise and is inside the core, unattributed.
  The filed anchor is "roughly 20% of global GBV" from RNPL; the RNPL ADR premium is not identified (the repo's
  1.33 ratio is imposed, not measured — ledger C §8). What would identify it: an RNPL nights share for the same
  quarter as the GBV share.
- **The nights deceleration.** Enters ADR as geographic mix: the nights line's regional path (NA +5.6 → +2.3,
  ex-NA +11.6 → +7.5) is the −1.1 to −1.6pp mix drag, quarter by quarter. Lower ex-NA growth in 2027 *raises*
  ADR slightly (2Q27 geo −1.08 vs 1Q27 −1.62).
- **FX.** The identity (§2). Held spot: +0.4 (3Q26), +0.5 (4Q26), −0.4 (1H27). A 5% stronger dollar takes 4Q26 FX to
  −2.4pp and ADR to about $168; 5% weaker, +3.4pp and about $178. It is the largest single swing in the line.
- **The World Cup.** Not in the ADR base (its nights pull-forward is in the nights line; its price effect is
  unsized). Named as a 2Q26/2Q27 tell only.
- **Fee migration.** The single-fee reprice is the 0.49pp fee/cancellation leg (lapping 4Q26) plus the tranche-2
  K sensitivity (+0.17 / +0.38pp, coefficient imposed at the payout-neutral mechanics, DEC-0008 keeps it out of
  base). Cleaning-fee removals and total-price display (2023–24) are inside the history's core.

## 7. What would change this line (pre-registered)

- **5 Nov 2026.** Printed 3Q26 ADR-FX pp vs the band [0.36, 0.48] — four candidates named in advance: identity
  +0.42, card midpoint −0.43, euro fit −1.12, fx_lag_v2 basket +0.44. Printed ex-FX vs 3.3 (base) / 3.7 (card):
  at or below 3.3 the bundle laps; at or above 3.7 it does not. The 4Q26 ADR outlook sentence: FX named or not.
- **11 Feb 2027.** Printed 4Q26 FX vs [−0.78, +1.97]; ex-FX vs 2.8 / 3.7 / 1.3 (base / card / mean reversion) —
  the first fully lapped quarter.
- **Any disclosure** of an RNPL nights share, a per-feature bundle split, or Bedroom Nights Booked again.

## 8. Open items

1. Theo to confirm or amend DEC-0034/0035/0036 (the FX leg switch from the card's midpoint; the bundle lap in
   base; the workbook line).
2. Excel recalculation of `ADR_Engine` and tie-out of block E (no LibreOffice on this Mac; formulas were written
   from the same inputs the engine uses and checked cell by cell in openpyxl, not recalculated).
3. Cross-line: D6/R2 GBV now $26.08bn / $22.81bn on lines 1 and 2; D3's FY27 ADR legs to be rebuilt on this line
   when reopened; D5's `adr_fx_pp` rows to be renamed (X1) — unchanged here.
4. The 2Q25 shareholder letter text exists nowhere on this machine (verified by a full filesystem search; ledger A §0), so the 2Q25 global ADR driver sentence is a hole; one SEC fetch of `2Q25_d17531dex991.htm` closes it.
5. Deepening the core (in order of power): an RNPL GBV-share / nights-share pair; a same-listing realised-rate
   series; a pre-registered supply-growth term with sign and size stated first. Not another regression on the
   residual.

## 9. Provenance table

| object | file | note |
|---|---|---|
| printed ADR, ex-FX, FX pp | `data/processed/overnight/02_kpi_panel_quarterly.csv` | letters; identity ≤ 0.04pp |
| daily FX | `data/processed/pitch_model_v2/adr_engine/fx_daily_2026-09-21.csv` | FRED H.10 through 18 Sep 2026; `fetch_fx.py` |
| currency baskets κ | `config.py` ← `fx_lag_v2/01b_basket_weights_used.csv` | judgement, frozen |
| regional GBV shares | `data/processed/adr/01_regional_annual.csv` | 10-K Geographic Mix, point in time |
| walk-forward, scores, posterior, forecast | `fx_pit_walkforward.csv`, `fx_scores.csv`, `fx_weights_posterior.csv`, `fx_forecast_asof.csv` | engine |
| ex-FX history | `data/processed/q3nowcast/H/adr_history_components.csv` | H decomposition |
| measured 3Q26 terms | `data/processed/adrq3/I/I_mix_terms_3q26.csv` | card v3 |
| bundle sizing | ledger D014, D032 (calls; `dossiers/ADR_A_disclosure_ledger.md` §2.1) | transcript-only, labelled |
| residual steps, K4 scenarios | `data/processed/adrv3/K/K4_residual_nowcast.csv` | |
| regional shares and ADR levels | `data/processed/adr/04_regional_quarterly_wide.csv` | disclosed-chained |
| nights line regional path | `lines/nights_v2_design.md` §2.1 | DEC-0028/0029 |
| Street | Bloomberg MODL screenshot 12 Sep 2026 (Krish), V1 dossier | 3Q26 n 26, 4Q26 n 25 |
| mechanism tables, path, scenarios | `exfx_*.csv`, `bundle_schedule.csv`, `geo_mix_*.csv`, `adr_path.csv`, `adr_scenarios.csv` | engine |
| workbook | `model/ABNB_official_model.xlsx` sheet `ADR_Engine`; `Income_Statement` rows 8–11 | `workbook.py` |

## 10. Figures

`figures/adr_full_logic.png` (the four-panel logic: identity walk-forward; currency contributions with bands;
ex-FX decomposition history and forward with the alternatives; ADR path vs the Street), and singly
`adr_fx_walkforward`, `adr_fx_currency_contributions`, `adr_exfx_mechanism`, `adr_path_vs_street`,
`adr_fx_passthrough_posterior`, `adr_constellation` (PNG + SVG).

### 2a. Model inputs (machine-readable)

| item | scenario | period | point | unit | note |
|---|---|---|---|---|---|
| adr_total_usd | base | 3Q26 | 177.68 | USD | adr_path.csv; 171.29 times 1.03731 |
| adr_yoy_reported_pct | base | 3Q26 | 3.731 | pct | ex-FX 3.316 plus FX 0.415 |
| adr_exfx_yoy_pct | base | 3Q26 | 3.316 | pct | exfx_forward_base.csv |
| adr_fx_pp | base | 3Q26 | 0.415 | pp | fx_forecast_asof.csv, 2026-09-21, spot held |
| adr_total_usd_lo | base | 3Q26 | 176.01 | USD | band half 0.978pp |
| adr_total_usd_hi | base | 3Q26 | 179.36 | USD | same |
| adr_total_usd | base | 4Q26 | 173.03 | USD | 167.51 times 1.03298 |
| adr_yoy_reported_pct | base | 4Q26 | 3.298 | pct | ex-FX 2.784 plus FX 0.514 |
| adr_exfx_yoy_pct | base | 4Q26 | 2.784 | pct | |
| adr_fx_pp | base | 4Q26 | 0.514 | pp | |
| adr_total_usd_lo | base | 4Q26 | 169.80 | USD | band half 1.932pp |
| adr_total_usd_hi | base | 4Q26 | 176.27 | USD | |
| adr_total_usd | base | 1Q27 | 190.65 | USD | 186.82 times 1.02048 |
| adr_yoy_reported_pct | base | 1Q27 | 2.048 | pct | ex-FX 2.417 plus FX -0.369 |
| adr_total_usd | base | 2Q27 | 188.38 | USD | 183.73 times 1.02530 |
| adr_yoy_reported_pct | base | 2Q27 | 2.530 | pct | ex-FX 2.957 plus FX -0.427 |
| adr_total_usd | base | 3Q27 | 182.51 | USD | 177.68 times 1.02716 |
| adr_yoy_reported_pct | base | 3Q27 | 2.716 | pct | ex-FX 2.863 plus FX -0.147 |
| adr_total_usd | base | 4Q27 | 178.10 | USD | 173.03 times 1.02928 |
| adr_yoy_reported_pct | base | 4Q27 | 2.928 | pct | ex-FX 2.928 plus FX 0.000 |
| adr_total_usd | base | FY27 | 185.21 | USD | nights-weighted; FY26 180.62 |
| adr_yoy_reported_pct | base | FY27 | 2.544 | pct | |
| adr_total_usd | street | 3Q26 | 177.06 | USD | Bloomberg MODL 12 Sep 2026 n 26 |
| adr_total_usd | street | 4Q26 | 171.33 | USD | Bloomberg MODL 12 Sep 2026 n 25 |
| p_print_ge_street | base | 3Q26 | 0.645 | prob | |
| p_print_ge_street | base | 4Q26 | 0.701 | prob | |
| adr_total_usd | card_v3_carry_at_identity_fx | 3Q26 | 178.32 | USD | alternative |
| adr_total_usd | core_mean_reversion | 3Q26 | 175.20 | USD | downside |
| adr_total_usd | core_mean_reversion | 4Q26 | 170.60 | USD | downside |
| gbv_busd | base | 3Q26 | 26.08 | USD bn | nights line 146.8m |
| gbv_busd | base | 4Q26 | 22.81 | USD bn | nights line 131.8m |
| gbv_busd | base | FY26 | 105.29 | USD bn | 29.2 + 27.2 + 26.08 + 22.81 |
| gbv_busd | base | FY27 | 115.17 | USD bn | |
