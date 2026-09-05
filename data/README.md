# Data

| File | Source | Pulled by | Date | Notes |
|---|---|---|---|---|
| processed/abnb_daily_close.csv | Yahoo Finance daily closes (ABNB), via yfinance | Krish (Claude Code) | 2026-09-05 | Date, Close, 10 Dec 2020 to 4 Sep 2026 (1,440 sessions). Input to the major-moves screen. |
| processed/abnb_major_moves_events.csv | Derived from abnb_daily_close.csv plus same-day QQQ, BKNG, EXPE moves; triggers from shareholder letters, call transcripts and same-day press | Krish (Claude Code) | 2026-09-05 | 41 close-to-close moves of 7% or more, each attributed macro/industry vs company-specific with headline and KPI detail. Attribution is hand-checked, not scripted. See research/notes/2026-09-05_abnb-major-moves.md. |
| processed/abnb_earnings_reactions.csv | Theo's guidance dataset (`theos-past-research/research/guidance/data/normalized/market_returns.csv`, Nasdaq closes vs QQQ) | Krish (Claude Code) | 2026-09-05 | 1/5/20-session ABNB, QQQ and excess returns for all 23 prints Q4 2020 to Q2 2026. Rebuild with `python analysis/src/abnb_from_theo_guidance.py`. Q2 2026 20-session window incomplete at Theo's 3 Sep cutoff. |
| processed/abnb_revenue_guidance_vs_actual.csv | Theo's guidance dataset (`guidance_items.csv`, `quarterly_actuals.csv`, from SEC-filed shareholder letters) | Krish (Claude Code) | 2026-09-05 | Next-quarter revenue guide range, midpoint, actual, beat vs midpoint and vs top, Q4 2021 to Q3 2026 (20 numeric guides). Same rebuild script. |

`raw/` is gitignored except this log - put the actual files in the shared Drive if they're large or licensed, and record them here.
`processed/` files should be reproducible by running something in `analysis/src/`.
