# R13 — risk-short-interest-crowding

**Question.** Will ABNB short interest be ≥5.0% of shares outstanding at any Nasdaq settlement date between 30 Sep 2026 and 15 Jan 2027 (eight settlements; Nasdaq/MarketBeat series as in `data/processed/overnight/09_short_interest.csv`, basic total shares ~592m, threshold ~29.6m shares)? Binary. Resolution 15 Jan 2027 (data lag allowed). Full text and conventions: `research-log.md` §0b.

**Forecast (revision 1, 2026-09-17, Fable, batch A13 with R12 and R14).** **P = 0.03**, credible interval 0.01–0.08.

**Why.** The latest reading is 14.23m shares (31 Aug 2026 settlement, Nasdaq API pulled 17 Sep) = 2.40% of shares, the 34th percentile of a 100-settlement series (Sep 2021–Aug 2026, mean 2.76%, max 5.44%). The threshold needs the short to more than double (2.08×) inside four and a half months. In 92 overlapping eight-settlement windows the maximum reached 5% in 8, all of them one episode: the S&P 500 inclusion of September 2023 (announced 1 Sep, effective 18 Sep; 3.10% → 4.04% → 5.44% in a month, unwound to 3.0% by December). No window starting below 3.0% (n 61) reached 4.5%; the largest eight-settlement rise in five years is 2.3pt against the 2.6pt needed. An AR(1) with bootstrapped residuals from 2.40% puts the window maximum at 5% with P 0.005; adding a jump component calibrated to the two observed ≥0.9pt single-step rises and a +0.7pt overlay after a down 5 Nov print (P 0.41, the mean post-down-print rise is 0.35pt, max 0.70) gives 0.03. The structural short sources are gone: the $2bn 2026 convertible notes (the convertible-arbitrage hedge) were repaid in March 2026 with straight senior notes, and short interest has fallen from 17.9m (Dec 2025) to 12.9–14.2m since; the stock is already in the S&P 500 and Nasdaq-100, so no inclusion event is scheduled.

**Resolution basis matters.** On the "% of float" basis MarketBeat and Yahoo display (float ~406m Class A), 5.0% is 20.3m shares = 3.43% of total shares — a level the series exceeded as recently as September 2025 (21.7m). Under that reading P would be ~0.20–0.30. The question names the repo file's basis (basic shares outstanding), and the forecast is on that basis; the alternative is reported.

**Impact if it happens.** No operating delta. A 5% short base (six days to cover at current volume) widens the right tail on an up print; judgement +$3/share on the thesis-breaker branch. EV 0.03 × $3 ≈ **$0.1/share: immaterial**; the memo can drop it (the real consequence is trade-level — borrow cost and recall risk — not price).

**Files.**
- `research-log.md` — schema log with claims ledger, query log, three estimates, extreme-probability audit, sensitivity, monitoring, `## 9. Impact`.
- `forecasts/2026-09-17-forecast.json`.
- `datasets/marketbeat_history.py` → `si_history_2022_2026.csv` (99 settlements from MarketBeat's dollar series, calibrated to the repo file); `si_base_rates.py` → `si_base_rates.json` (earlier attempt, 84-settlement file, kept for comparison); `r13_model.py` → `r13_summary.json`, `si_window_max.csv`, `si_after_prints.csv` (this run: windows, AR(1), jump, down-print overlay, post-print rises).
- `sources/` — Nasdaq API pulls (03:52Z, 08:01Z), yfinance info subset, MarketBeat page, `web_search_log.md` (1 WebSearch, 1 WebFetch).

**Not submitted anywhere.** Next: Astra audit (`docs/pitch-forecasts/audits/A13-research-audit.md`), then a revision-2 response.
