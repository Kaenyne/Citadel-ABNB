# R11 — risk-q4-us-revpar-strong

**Question.** Will STR/CoStar's US hotel RevPAR growth for 4Q26 (Oct–Dec, reported Jan 2027) be ≥ +4% y/y? Binary. Resolution ~25 Jan 2027 (mean of the three monthly releases). Full text and conventions: `research-log.md` §0b.

**Forecast (revision 1, 2026-09-17, Fable, batch A12 with R10, R15, R16).** **P = 0.38**, credible interval 0.25–0.52.

**Why.** The summer ran +5–8% (July +8.2% with the World Cup final; August weeks +7.3 → +7.2 → +6.2 → +4.4 → +1.7 before a Labor Day mirror), and the 4Q25 base is soft (October 2025 −0.9%, FY2025 −0.3%, the first annual decline since 2020). Against that, CoStar/Tourism Economics' FY2026 forecast of +4.4% (10 Aug) arithmetically leaves 4Q26 near +3%, the operators' 3.0–3.5% FY guides imply an H2 near +2.5%, ADR growth had faded to +0.6% by late August, and November 2026 carries a midterm-election week against the easy 2025 election comp, with a CR expiry on 11 Dec. Centre +3.5%, sd 1.7 → 0.38; the mirror B15 (≤ +1%) is 0.07.

**Impact if it happens.** +1.7pp of US hotel RevPAR (a stay-date, US-only series that has decoupled from Airbnb's KPI since 2024): 4Q26 nights +0.4pt, ADR +0.3pt, 4Q26 revenue +$20M, FY27 +$30M, margins +0.03–0.05pp, EPS +$0.01; stock ~+$1.5 (mostly the loss of the memo's "hotels are decelerating" corroboration). EV 0.38 × $1.5 ≈ **$0.6/share: immaterial.** Drop the hotel line as a risk; keep the weekly STR series as a monitor.

**Files.**
- `research-log.md` — claims ledger, query log (5 WebSearch, several fetches; costar.com/str.com 403), three estimates, sensitivity, pre-mortem, monitoring, `## 9. Impact`.
- `forecasts/2026-09-17-forecast.json`.
- `datasets/r11_model.py` — deterministic (`py -3.13`); outputs `r11_path.csv` (FY-implied Q4 grid), `r11_views.csv`, `r11_sensitivity.csv`; `str_weekly_us_3q26_repo_copy.csv` (copy of the repo's weekly STR series with source URLs).

**Not submitted anywhere.** Next: Astra audit, then a revision-2 response.
