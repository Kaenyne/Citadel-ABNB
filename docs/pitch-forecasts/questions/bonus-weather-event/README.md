# B14 - bonus-weather-event

**Question.** Between 17 Sep and 31 Dec 2026, will a hurricane or other natural disaster be cited by Airbnb management as reducing nights or GBV, or will a Category 3+ hurricane make US landfall in Florida, Texas or the Carolinas? Binary. Resolution 31 Dec 2026 (citation counted through the Feb print). Full text and conventions: `research-log.md` section 0b.

**Forecast (revision 1, 2026-09-17, Fable, batch A18 with B15 and B16).** **P = 0.08**, credible interval 0.04-0.14 (landfall leg about 0.065, citation leg about 0.02).

**Why.** Climatology for the window is 13-17% of seasons (HURDAT2, 1966-2025 / 1991-2025), but 2026 is the most hostile Atlantic in the satellite era: as of 17 Sep the NHC counts 5 named storms, 0 hurricanes, ACE -94%, under a very strong El Nino with record Caribbean shear; the 11 El Nino analog seasons are 0 for 11 in the window; CSU's 5 Aug landfall probabilities were already 7-9% by coast with six empty weeks since; Kalshi prices a one-in-three chance of any major hurricane this season, which times the historical conditional landfall rate (about 0.23) gives 0.08. Management has never cited a hurricane or disaster as reducing nights or GBV in 23 letters and 23 calls (Ian 2022, Helene/Milton 2024 and the LA fires appear only as Airbnb.org relief), so the citation leg is small.

**Impact if it happens.** 4Q26 nights -0.1pt, revenue -$3M, margins and EPS nil, stock -$0.2; EV about **-$0.02/share: immaterial.** Drop from the memo; watch the NHC outlook only because a landfall would hand management an excuse.

**Files.**
- `research-log.md`: claims ledger, query log (1 WebSearch), three estimates, sensitivity, pre-mortem, monitoring, `## 9. Impact`.
- `forecasts/2026-09-17-forecast.json`.
- `datasets/b14_hurdat_base_rate.py` (stdlib, `py -3.13`) writes `b14_landfalls.csv`, `b14_base_rates.csv`.
- `sources/`: HURDAT2 file, NHC season summary and outlook (17 Sep), CSU August PDF and text, Kalshi/Polymarket JSON, web log.

**Not submitted anywhere.** Next: Astra audit, then a revision-2 response.
