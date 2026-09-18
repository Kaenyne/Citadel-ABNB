# B11 — bonus-sellside-downgrades

Between 17 Sep and 15 Dec 2026, will ABNB receive ≥3 rating downgrades (to Hold/Sell-equivalent) from firms in the tracked yfinance/Benzinga feed (`data/processed/reverse_dcf/D/` convention)? Binary; resolves 15 Dec 2026.

Revision 1 (17 Sep 2026, Fable, batch A17): **P = 0.14, CI 0.07–0.25**. Twenty downgrades in the feed since 2021, none in 474 days; 90-day P(≥3) 0.11 all-history / 0.006 since 2024; only 2 of 23 print-shaped windows reached three (Feb 2022, Nov 2023). Downgrades follow price falls with a 2–5 week lag rather than prints, so the number is 0.23 on the team's base-case branch (decelerating print, guide below Street) and 0.04 on an accelerating print. Impact: no operating content; direct stock effect ≈ −$1.5/share, EV ≈ −$0.2/share, **immaterial** as a standalone line (a marker of the base-case branch: E[15 Dec close | Yes] $148 vs $161).

- `research-log.md` — the log (schema per the forecast skill), with the `## 9. Impact` table.
- `forecasts/2026-09-17-forecast.json` — the forecast in the brief's schema.
- `datasets/downgrade_base_rates.py` → `downgrade_base_rates.json`, `feed_downgrades_all.csv` (pandas; run from the repo root with `py -3.13`).
- `datasets/b11_model.py` → `b11_summary.json`, `b11_sensitivity.csv` (numpy, seed 20260917, ~1 min).
- `sources/` — fresh yfinance feed pull (2026-09-17T08:21:55Z), analyst-target snapshot, Kalshi/Polymarket snapshots (08:27:05Z), web-search log.
