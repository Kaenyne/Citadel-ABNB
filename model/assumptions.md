# Model assumptions

Keep in sync with the model. Reviewer checks this file in PRs, since the .xlsx itself can't be diffed.

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
