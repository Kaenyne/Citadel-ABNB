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
