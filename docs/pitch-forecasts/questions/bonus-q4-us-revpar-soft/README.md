# B15 - bonus-q4-us-revpar-soft

**Question.** Will STR/CoStar's US hotel RevPAR growth for 4Q26 (Oct-Dec, reported Jan 2027) be <= +1% y/y? Binary, the lower-tail mirror of R11 (`../risk-q4-us-revpar-strong/`). Resolution ~25 Jan 2027 (mean of the three monthly releases). Full text and conventions: `research-log.md` section 0b.

**Forecast (revision 1, 2026-09-17, Fable, batch A18 with B14 and B16).** **P = 0.10**, credible interval 0.05-0.18. One distribution with R11: P(>= 4) 0.38, P(1 < x < 4) 0.52, P(<= 1) 0.10.

**Why.** R11's centre +3.5 / sd 1.7 gives 0.07 on its own. A <= +1% quarter needs a demand contraction of the 2024-25 kind (occupancy -1 to -2 against an October 2025 base that was already -0.9%), not just the summer premium fading (the weakest clean August week was +1.7 with occupancy +1.1). Those quarters were the norm two quarters ago (6 of 8 in 2024-25 were <= +1), and the dated downside mechanisms are real: a CR expiry on 11 Dec, the 16 Sep Fed hike with three more priced, TSA -3.7% as airfares ration travel. A 10% shock branch centred at +0.8 lifts the tail to 0.10 while leaving R11's P(>= 4) at 0.38.

**Impact if it happens.** -3.6pp of US hotel RevPAR: 4Q26 nights -0.7pt, ADR -0.5pt, 4Q26 revenue -$36M, FY27 -$60M, margins -0.05/-0.10pp, EPS -$0.04; stock about -$2.5 (mostly corroboration of the memo's deceleration narrative). EV 0.10 x -$2.5 = **-$0.25/share: immaterial.** Keep the STR tape as a monitor; if October prints <= +2 it becomes a one-line corroboration.

**Files.**
- `research-log.md`: claims ledger, query log (1 WebSearch), three estimates, sensitivity, pre-mortem, monitoring, `## 9. Impact`.
- `forecasts/2026-09-17-forecast.json`.
- `datasets/b15_model.py` (`py -3.13`) writes `b15_views.csv`, `b15_sensitivity.csv`; `str_weekly_us_3q26_repo_copy.csv`.
- `sources/`: trade-press listing fetches and the web log.

**Not submitted anywhere.** Next: Astra audit, then a revision-2 response.
