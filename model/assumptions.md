# Model assumptions

Keep in sync with the model. Reviewer checks this file in PRs, since the .xlsx itself can't be diffed.

**Live model (5 Sep 2026):** `analysis/src/abnb_driver_model.py` (Python; outputs in `data/processed/abnb_valuation_scenarios.csv`, `abnb_valuation_sensitivity.csv`, `abnb_reverse_dcf.csv`, `abnb_multiples_today.csv`). The Excel workbook `ABNB_model.xlsx` does not exist yet; when it is built, its Drivers and Scenarios tabs should carry these values. Operating cases FY2026E and FY2027E are inherited from the margin-drivers branch (`abnb_margin_scenarios.csv`, `analysis/src/abnb_margin_bridge.py`); FY2028E, cash conversion, SBC, buybacks and multiples are set here. Write-up: `research/notes/2026-09-05_driver-model.md`.

| Driver | Bear | Base | Bull | Source / rationale |
|---|---|---|---|---|
| Nights & experiences booked growth | FY26 +9.5%, FY27 +6% | FY26 +10%, FY27 +9% | FY26 +10.5%, FY27 +10% | 1H26 ran +9% and +10%; RNPL lap in H2. Margin note section 11 |
| ADR growth | FY26 +3% ex-FX +2% FX; FY27 +1% ex-FX, -1.5% FX | FY26 +3.5% ex-FX +2% FX; FY27 +3%, no FX | FY26 +4% ex-FX +2.5% FX; FY27 +3.5% +0.5% FX | 1H26 ADR ex-FX +4%; hotels caught up in Q2 26 (note 3.4) |
| Take rate | 13.36% FY26, 13.21% FY27 (incentives) | flat at 13.41% (FY25 revenue / GBV) | 13.46% FY26, 13.56% FY27 (single fee, insurance) | Mgmt: flat FY26 incl. new-business incentives; note section 7 |
| Adj. EBITDA margin | 35.3% FY26, 33.8% FY27 | 35.9% FY26, 36.5% FY27 | 37.7% FY26, 39.8% FY27 | Bottom-up cash stack, `analysis/src/abnb_margin_bridge.py`; guide is at least 35.5% FY26, floors beaten by 60 to 180 bps since 2023 |
| SBC % revenue | 14% | 13% (FY25 12.9%; growth guided below FY25's +13%) | 12% | 4Q25 letter; excluded from Adj. EBITDA so it sits between EBITDA and FCF |
| Capex % revenue | | | | |
| WACC | | | | |
| Terminal growth / exit multiple | | | | |
| Share count | | | | |
| Nights & experiences booked growth, FY26 / FY27 / FY28 | +9.5% / +6% / n.a. (FY28 revenue +6%) | +10% / +9% / n.a. (FY28 revenue +11%) | +10.5% / +10% / n.a. (FY28 revenue +14%) | FY26 and FY27 from the margin-drivers scenarios (management: FY26 nights "low double digits" in Q3, five quarters at 9% to 10%). Bear FY27 = RNPL and fee-migration tailwinds lap (management attributes 2 to 4 pts of 2025 to 2026 growth to them); bull = first-time bookers +11% and expansion markets at 2x core persist |
| ADR growth ex-FX / FX, FY26 / FY27 | +3% / +2% then +1% / -1.5% | +3.5% / +2% then +3% / 0% | +4% / +2.5% then +3.5% / +0.5% | Margin-drivers scenarios. Inside Airbnb same-listing prices fell 1% to 11% in 2025 (supply-panel note), so ADR growth is mix; bear takes it to +1% |
| Take rate (revenue / GBV), FY26 / FY27 | 13.36% / 13.21% | 13.41% / 13.41% | 13.46% / 13.56% | Margin-drivers scenarios around the 13.41% FY25 base. Management guided FY26 flat (Aug 2026, down from "modest upside" in May); single-fee migration to 15.5% and insurance versus RNPL timing, hotel credits and the 6% to 10% host-fee pilot |
| Adj. EBITDA margin, FY26 / FY27 / FY28 | 35.3% / 33.8% / 33.5% | 35.9% / 36.5% / 37.0% | 37.7% / 39.8% / 40.5% | FY26 and FY27 from the margin bridge (guide "at least 35.5%"; every floor since 2023 beaten by 60 to 180 bps). FY28 extends the FY27 trajectory by +0.5 pt (base), -0.3 (bear), +0.7 (bull) |
| SBC % revenue | 14.0% | 13.0% | 12.0% | FY25 13.1%, LTM 12.9%, 2Q26 13.5%; management's SBC guidance is "flat to slightly down as % of revenue" (margin note). Bear = 1Q26 run rate |
| FCF conversion (FCF / Adj. EBITDA) | 92% | 100% | 105% | FY23 105%, FY24 111%, FY25 107%, LTM 105%; conversion above 100% is guest-float growth and interest income. Base assumes float growth slows with GBV growth in the low teens |
| Capex % revenue | 0.3% | 0.3% | 0.3% | FY25 capex $33M on $12.2B revenue (capital-return panel); immaterial |
| D&A % revenue, tax rate, yield on cash and float, debt cost | 0.7%, 21%, 3.5%, 5.0% | same | same | Used only for the GAAP-ish earnings proxy (EPS lens). FY25 interest income about $0.8B on cash, investments and the $12B float; the 2026 senior notes are $2.5B |
| Buybacks per year (FY27, FY28; FY26 = H1 actual $2.14B plus half a year) | $3.0B | $4.0B | $4.5B | FY24 $3.4B, FY25 $3.8B, H1 26 $2.1B; $3.4B authorisation left (Aug 2026). Share count falls by buybacks / price less RSU issuance (SBC / price x 65% after tax withholding) |
| Net cash for EV (30 Jun 2026) | $9.6B = cash $6.8B + short-term investments $5.2B - notes $2.5B | same | same | SEC XBRL 10-Q. Funds held for clients ($12.2B) are excluded: guest prepayments matched by a liability |
| Diluted shares (start) | 597M | same | same | 2Q26 weighted diluted (XBRL) |
| WACC / terminal growth (reverse DCF only) | 9% to 11% / 2.5% to 4% grid | 10% / 3% | | The pitches use 9.5% to 10.5% and 2.5% to 5.5% (pitch landscape, section 3). The model reports what the price implies rather than picking a point |
| Exit multiples on FY2027E: EV/EBITDA, EV/FCF, P/SBC-adjusted FCF, P/E proxy | 18x, 15x, 20x, 20x | 22x, 19x, 26x, 26x | 25.5x, 23x, 32x, 32x | Base holds today's LTM multiples (EV/EBITDA 21.5x, EV/FCF 20.5x, P/SBC-adj FCF 34.7x is cut to 26x). Bear = Truist 20x cut to 18x, Barclays 20x P/E; bull = Bernstein 25.5x EV/EBITDA, Wells 28x to 33x P/E (landscape, section 3) |

**Not yet in the model:** consensus at each call (needed for the reaction function; Bloomberg session), a regional (NA / EMEA / LatAm / APAC) nights build, hotels and Experiences contribution (management: 3 to 5 years to materiality; the landscape's SOTP add-ons of $50 to $150 a share are not included), and a quarterly cadence for FY2026E beyond the Q3 guide midpoint.

---

## Overnight run 6-7 Sep 2026 (workstream 13)

**Live model from this date:** `model/ABNB_driver_model.xlsx` (openpyxl-built, live formulas on eight
sheets: Inputs / History / Revenue / Costs / Cash / Valuation / Street / Card_5Nov, plus a Recon sheet)
and its Python mirror `analysis/src/overnight/13_driver_model.py`. Outputs:
`data/processed/overnight/13_model_quarterly.csv`, `13_model_annual.csv`, `13_valuation_summary.csv`,
`13_scenario_grid.csv`, `13_reconciliation.csv`. Write-up: `research/notes/overnight/13_driver-model-build.md`.
The 5 Sep Python model (`analysis/src/abnb_driver_model.py`) stays as the reverse-DCF and reaction-function
reference; its FY26/FY27 operating cases are superseded by the rows below. **Nothing above this line was
deleted; every row below either changes or adds to it.**

Structure changes versus the 5 Sep model: (i) a regional (NA / EMEA / LatAm / APAC) nights build, which
was listed there as "not yet in the model"; (ii) a quarterly cadence 3Q26-4Q27, likewise; (iii) FX split
into an ADR effect (contemporaneous) and a revenue effect (lagged), with the gap carried as an explicit
"FX timing wedge" line; (iv) a new-business revenue line for the pieces that sit outside GBV x take rate;
(v) a regulatory nights drag by region; (vi) an AI referral cost line; (vii) net income, an effective tax
rate and an EPS line, so the model can be compared with Street adjusted EPS.

| Driver | Bear | Base | Bull | Source workstream / rationale | Changes what |
|---|---|---|---|---|---|
| Nights growth by region, 3Q26 / 4Q26 (NA, EMEA, LatAm, APAC) | 5/6/15/14, 4/5/14/13 | 7/8/18/17, 7/7/18/17 | 9/10/21/19, 9/9/21/19 | WS10 `10_regional_forecast.csv`, bottom-up from disclosed regional commentary and public benchmarks | NEW: there was no regional build |
| Nights growth by region, FY27 | 3/4/12/11 | 6/7/16/15 | 8/9/19/18 | WS10 | NEW |
| Total nights growth FY26 / FY27 / FY28 | +8.6 / +5.5 / +4.4% | **+9.9 / +8.9 / +7.4%** | +11.0 / +11.7 / +9.5% | Output of the regional build net of the regulatory drag; FY28 from WS07's total-nights lever (5.0 / 8.0 / 9.5%) | REPLACES 9.5/6, 10/9, 10.5/10 |
| ADR ex-FX, 3Q26 / 4Q26 | +2.0% | **+3.0%** | +4.0% | WS10; 1H26 actual was +4% (letters), so FY26 blends to about +3.5%, which is WS07's FY26 lever | REPLACES the annual-only FY26 +3.5% |
| ADR ex-FX, FY27 / FY28 | +1.0% | **+2.5%** | +3.5% | WS06 (bedroom mix +1.5-2.0pp decaying, price at CoStar's +1.6% 2027 hotel ADR forecast) and WS07's lever, which agree | REPLACES FY27 +3% |
| FX effect on **revenue**, by quarter 3Q26-4Q27 | strong-USD path +3.00 / -0.43 / -1.56 / -2.48 / -3.18 / -3.02 pp | **+3.00 / -0.43 / -1.03 / -0.80 / -0.61 / -0.07 pp** | weak-USD path +3.00 / -0.43 / -0.50 / +0.53 / +1.25 / +2.16 pp | WS05 `05_fx_schedule.csv`, lagged fit -0.640 + 0.413 x mean(EUR/USD y/y at t-1, t-2), n 17, r 0.80. 3Q26 set to the company's guided +3.0pp | REPLACES FY26 +2%, FY27 0% / -1.5% |
| FX effect on **ADR**, by quarter 3Q26-4Q27 | see the Inputs sheet | **+0.80 / -0.36 / -0.40 / +0.02 / +0.66 / +0.49 pp** | see the Inputs sheet | WS05 broad-USD fit, re-estimated independently by WS08 (r 0.96, walk-forward 0.44x naive) | NEW: ADR and revenue FX were one number before |
| FX timing wedge (revenue FX less ADR FX) | derived | derived | derived | Revenue is recognised at check-in and GBV at booking, so the two FX effects genuinely differ (2Q26: ADR +1.3pp, revenue +4.0pp). Carried as an explicit line rather than hidden inside the take rate | NEW |
| Take rate change vs prior year, FY26 / FY27 / FY28 | -5 / -15 / -10 bps | **0 / 0 / +5 bps** | +5 / +15 / +20 bps | WS07 lever; management guided FY26 flat (Aug 2026). WS11: the 15.5% single fee is the upside, the 6-10% direct-link pilot (29 Aug 2026) is the cap | level unchanged, extended to FY28 |
| Regulatory nights drag, incremental pp of growth (NA / EMEA), FY26 / FY27 / FY28 | 1.67x the WS11 median | **0.03/0.36, 0.05/0.71, 0.07/1.00 pp (1.67x the WS11 median)** | 0 | WS11 `11_regulatory_overlay.csv`; WS11 asks for the mean in the base and mean/median = 1.67. WS01 asks for it on EMEA nights, not on global revenue | NEW |
| New business outside GBV x take rate (sponsored listings + Services), FY26 / FY27 / FY28 | 24 / 38 / 114 $M | **42 / 212 / 516 $M** | 60 / 430 / 1,096 $M | WS11 `11_new_business_scenarios.csv`. Hotels and Experiences are excluded: their nights are already inside "nights and experiences booked" | NEW |
| Incremental EBITDA margin on that revenue | 70% | 70% | 70% | Sponsored listings are near-100% margin, Services materially lower | NEW |
| AI referral cost, % of revenue, FY27 / FY28 | 2.28 / 3.83% | **0.38 / 0.77%** | 0 / 0% | WS11 `11_ai_exposure_scenarios.csv`, high / low / zero at a 5% referral fee | NEW |
| Cost levers: cost of revenue per $ GBV, ops & support per night, product development, brand & performance marketing, field operations, G&A | see the Inputs sheet | see the Inputs sheet | see the Inputs sheet | WS07 `07_margin_levers_fy26_fy28.csv`: all 21 levers carried verbatim with their evidence strings | REPLACES the single "Adj. EBITDA margin" row |
| Adj. EBITDA margin FY26 / FY27 / FY28 (**output**, not an input) | 34.5 / 28.4 / 25.5% | **36.2 / 35.9 / 37.3%** | 37.8 / 38.0 / 38.0% | Output of the levers above. Base FY27 is 36.3% before the AI referral cost, against WS07's 36.6% and WS05's 36.4% | REPLACES 35.3/36.5/37.7 and 33.8/36.5/39.8 |
| Adj. EBITDA margin cap | 38% | 38% | 38% | WS07: the realistic ceiling, against BKNG's five-year EBITDA-proxy range of 30.0-37.4%. Binds in the bull from FY27 | NEW |
| SBC growth, FY26 / FY27 / FY28 | 16 / 14 / 12% | **13 / 10 / 8%** | 10 / 6 / 4% | WS07 lever; 1H26 +14.7%, guided below FY25's +13% | REPLACES the flat "SBC % of revenue" |
| Interest income / expense ($M), FY26 / FY27 / FY28 | 620/125, 540/128, 500/128 | **660/120, 620/125, 590/125** | 700/115, 690/122, 680/122 | WS07 lever | NEW below-the-line detail |
| Cash taxes, % of revenue | 3.5 / 4.5 / 5.2% | **2.6 / 3.4 / 4.0%** | 2.0 / 2.6 / 3.2% | WS07 lever; FY25 cash taxes were 1.9% of revenue against a 5.1% provision | REPLACES the flat 21% |
| Effective tax rate (net income and EPS) | 21% | **19% FY26, 20% FY27-28** | 18 / 19 / 19% | WS02: FY26 guide "high teens" (17-19%), tax guides run about 50bp hot, FY25 actual 20.0% | NEW |
| Buybacks, FY26 / FY27 / FY28 | $4.2 / 3.0 / 3.0bn | **$4.2 / 4.0 / 4.0bn** | $4.2 / 4.5 / 4.5bn | FY26 = 1H26 actual $2,139M plus H2 at the 1H run rate. $3.4bn of authorisation was left in Aug 2026, so FY27-28 needs a top-up | FY26 made explicit |
| Diluted shares, period end FY26 / FY27 / FY28 (**output**) | 589 / 580 / 573M | **589 / 575 / 562M** | 589 / 571 / 555M | Buybacks and RSU issuance at a price rising 5% a year, 35% of SBC withheld. **Corrected 7 Sep (WS17 finding 3 / WS18):** the roll starts from the 2Q26 diluted count (597M), so FY2026 consumes only the 2H26 buyback (FY26 less the $2,139M already spent in 1H26) and only 2H26 SBC (FY26 less $897M) — the same deltas the net-cash line uses. The first build applied the full-year flows to the 30 Jun count and so understated FY2026E shares by 8.55M, carried into FY27-28. Every per-share and price output is ~1.5% lower than the 6 Sep version | method unchanged, now a live formula; **1H26 no longer double-counted** |
| Net cash ex float, FY27E (**output**) | $8.6bn | **$10.1bn** | $11.3bn | Rolled forward from the $9,593M actual at 30 Jun 2026, less buybacks **and RSU tax withholding** (about $0.7bn a year). `abnb_valuation_scenarios.csv`'s $12.0-13.4bn omitted withholding | CORRECTS the earlier net-cash path |
| Cost of equity | 11.5% | **10.5%** | 10.3% | WS09 recommends 10.5-11.5% (Rf 4.78%, beta 1.2-1.3, ERP 4.5-5.5%); WS12's CAPM gives 10.3% | REPLACES the 9-11% grid with a point estimate |
| Terminal growth | 2.5% | **3.0%** | 3.0% | WS12 | unchanged |
| Exit multiple, FY27E EV / adj. EBITDA | **13.5x** | **16.5x** | **18.5x** | WS12 `12_exit_multiple_recommendation.csv`: blend of a time-series regression (+0.48 turns per point of NTM revenue growth), a peer cross-section and an intrinsic fade DCF | **REPLACES 18 / 22 / 25.5x** |
| Exit EV / FCF; P / SBC-adjusted FCF; P / earnings proxy | 11.3x; 15x; 15x | **14.3x; 19.5x; 19.5x** | 17.3x; 24x; 24x | The 5 Sep set (15/19/23x and 20/26/32x) rescaled by the same 0.75x haircut WS12 applies to the EBITDA multiple | REPLACES the 5 Sep set |
| DCF start growth (year-1 FCF growth, fading linearly to terminal over 10 years) | 0% | **9%** | 15% | A round number just under the model's own FY2026-FY2028 FCF CAGR of 9.9%; the input is clipped to 0-15%. Unclipped, a bear starting at -21% and a bull at +26% produce extrapolation artefacts rather than valuations | NEW |
| Reverse DCF convention | constant growth for 10 years then terminal | same | same | Kept identical to `analysis/src/abnb_driver_model.py`, so the two agree: at 10% / 3% both give **7.50%** implied growth on reported FCF and **13.32%** on SBC-adjusted FCF | unchanged |

**Still not in the model:** consensus at each historical call as a live regressor (WS04 built the series;
no reaction feature survived leave-one-out, so none is in the workbook); long-term stays, Airbnb for Work
and RNPL float as separate revenue lines (WS11 could not size them); a balance sheet below net cash;
anything past FY2028.
