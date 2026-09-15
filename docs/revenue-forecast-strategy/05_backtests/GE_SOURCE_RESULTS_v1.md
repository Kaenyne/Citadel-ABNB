# GE-SOURCE — earnings timestamps, prices and Street objects

15 September 2026. Agent source_auditor. Branch `codex/submission-readiness-v1`, merged evidence base `2dfe0c2a1852181a246f4b6b9072e05e844d52d5`. Protocol: `GE_PREREG_v1.md`. Source inventory only; no fit, return calculation, forecast registration, scorer, original-file change or commit.

**PARTIAL: daily event legs and dated revenue expectations are available; a release-versus-call intraday panel and directly observed guide expectations are not established.** Continue the daily gap/next-session analysis and label its information set. Do not manufacture call candles or equate a daily gap to the move during the call.

## Inventory and exact boundaries

Canonical receipt: `data/processed/forecast_methods/gbv_event_v1/sources_v1/run_v2/receipt.json`; source hashes: `input_manifest.csv`. All paths in this note are relative to this worktree.

| Object | Coverage / n | Permitted interpretation |
|---|---:|---|
| `returns_v1/ohlc_daily.csv` | 2,895 ticker-day rows: ABNB1,444; QQQ1,451; through2026-09-11 | Raw daily OHLC. Open/high/low/close have no within-day ordering. |
| `returns_v1/earnings_reactions_open_v1.csv` | 23 earnings events, 2020Q4 through2026Q2 | Pre-release close to next open; next-open to subsequent daily closes. |
| `overnight/20_prices_ohlc.csv` | 1,447 date rows, through2026-09-04 | Older daily ABNB/QQQ opens/closes, not intraday. |
| `abnb_earnings_reactions.csv` | 23 event rows | Rounded daily return derivatives, not quotes. |
| `peer_readthrough/05_t1_gap_vs_intraday.csv` | 32 peer-event rows | Daily gap/regular-session decomposition; its name does not certify subdaily bars. |
| True timestamped intraday ABNB+QQQ event panels held in reviewed sources | **0/23** | No release-only, call-only, wick-order, or stop/target-execution claim. |

The real event universe excludes the calendar's approximate 2020Q3 pre-IPO observation, whose `letter_date` and `reaction_date` are empty, and excludes the future scheduled row. The exact daily-price evidence is the committed returns_v1 file; its source manifest says Yahoo/yfinance raw unadjusted bars retrieved2026-09-13. The file's SHA256 is `5b03005c30b1793e2d146e6a76fc352ecee56b7fbaf0e9f737bd479652b7a253`.

Daily gap contains release, call, overnight, and premarket information. Daily high/low cannot reveal their order. Even a genuine timestamped call-window return would remain an association with overlapping news, rather than a causal estimate of the call's effect. Use exact compounding for legs; an arithmetic subtraction of close-to-close and gap excess returns is not the exact regular-session excess return.

## Intraday availability: bounded attempt, then stop

Repository filenames, documented price inputs and catalogue references were searched. The one relevant catalogue hit is `vgreg/earnings_news_jar`: methodology using licensed RavenPack/IBES/Refinitiv Tick History/ITCH inputs, with no held ABNB price panel. No enabled purpose-built historical-intraday connector was found.

[yfinance maintainer documentation](https://ranaroussi.github.io/yfinance/reference/yfinance.functions.html) lists intraday intervals and a60-day history limit, plus pre/post-market support. This could at most help with a recent event, not all23 events. A public ABNB five-minute request for2026-08-06 through2026-08-07 first hit the sandbox socket restriction. After scoped network approval, the same bounded request returned **HTTP429**; zero bars were obtained. QQQ was not requested after ABNB failed; there were no retries or rate-limit workarounds. Both attempt receipts are preserved.

[Alpha Vantage documentation](https://www.alphavantage.co/documentation/#intraday) describes historical month-specific, raw and adjusted OHLCV, with extended hours, but marks this endpoint Premium and requires an API key. No key was sought and no purchase or API request was made. This is a possible external data source, not an available panel.

The missing object is a consistently sourced ABNB and QQQ one- or five-minute raw OHLCV/trade panel spanning each event's pre-release, release-to-call, call, post-call and next regular session, with timezone/DST, bar-time semantics, adjustment policy, missing-bar flags and exact publication/call-start/call-end timestamps. A suitably entitled export could close that gap. Its availability elsewhere is not ruled out; acquisition is not required to complete the honest daily-leg deliverable.

## Primary disclosure and event-time checks

Web checks and limitations are retained in `sources_v1/primary_web_checks.json`. The [August6 SEC shareholder letter](https://www.sec.gov/Archives/edgar/data/1559720/000119312526337928/d70413dex991.htm) gives Q3 revenue guidance **$4,690-4,770m** and low-double-digit Nights and Seats Booked growth; its webcast was scheduled17:00 New York time. The [May7 letter](https://s26.q4cdn.com/656283129/files/doc_financials/2026/q1/Airbnb_Q1-2026-Shareholder-Letter.pdf) also schedules its call17:00 New York time. Neither supplies an independently established first-public minute or call-end clock in this audit.

One inherited timing discrepancy matters specifically to intraday work: L3 precision's2025Q3 letter manifest carries21:30Z as an inherited webcast/public-by proxy. The [official announcement](https://investors.airbnb.com/press-releases/news-details/2025/Airbnb-to-Announce-Third-Quarter-2025-Results/default.aspx) schedules November6 2025 at17:00 ET, or22:00Z. This does not change the daily event date; it means the inherited proxy cannot set call boundaries. No old file was changed.

November5 2026 remains the **project expected/planning date**, also present in held Zacks expected-report wording. A company announcement for that date was not found in the bounded primary search. This is an unverified schedule field, not a claim that no announcement exists. No future call time is assigned. Q3's issued guide is an observed comparison, not an unknown guide to forecast.

## Street family, precision and expectation object

L0 contains **1,330 data rows**, including1,159 DoltHub revenue observations. There are20 original `pre_guide` rows;16 have a value, PIT-usable flag and attributed vendor. The other four are two unavailable/quarantined rows and two CNBC-unattributed observations. The event analyst should report exclusions by actual event, not assume all20 are comparable. Every original historical row is preserved in `historical_primary_expectation_inventory.csv`.

Primary rule recommended before GE-EVENT calculations: explicitly select the original attributed, usable `pre_guide` rows; retain vendor and timestamp; exclude missing/quarantined/unattributed cells. Date-only morning-of-print sources are admissible under the project's documented convention, not independently proven capture clocks. Explicit times must carry a timezone and precede16:00 New York on release day. Use DoltHub uniformly in a separate sensitivity; do not fill individual rows opportunistically or call `vendor=None`.

| Retained family/source | Q3 revenue $m | Q4 revenue $m | Timestamp and precision |
|---|---:|---:|---|
| Yahoo / LSEG-family API | 4,744.88187 | 3,161.02149 | Captured2026-09-13 15:20:58Z; n36. Exact source-dollar conversion retained; display approximately4,745/3,161. |
| S&P via StockAnalysis | 4,740 | 3,160 | Existing quarterly observation dated2026-09-10, n35; no fresh quarterly confirmation onSep13. |
| Zacks | 4,740 | 3,200 | Existing capture2026-09-11, n7/10; public display4.74B/3.20B is coarser than an exact-dollar estimate. |
| DoltHub mirror | 4,740 | 3,200 | Snapshot2026-09-13, n7/10; same Zacks-family information, not another independent panel. |
| Q1/Q2 2027 quarterly expectation | unavailable | unavailable | No such admissible quarterly revenue values found in reviewed L0 current/history rows. Do not split FY consensus into invented quarterly Street forecasts. |

All are **expectations of realised quarterly revenue**, not observed expectations of management's issued guide midpoint. The structured register contains **zero direct-guide-expectation metric rows**. A cushion-adjusted Street benchmark is a conditional proxy and must show its pre-event convention. No verified current nights/ADR/GBV Street panel was supplied by the September re-stamp. Yahoo and Alpha Vantage count once as LSEG family; DoltHub and Zacks count once as Zacks family. S&P's vendor attribution alone does not guarantee wholly independent analyst membership.

Retain raw values and source lexemes; do not treat returned decimals as forecast accuracy. The older rounded3,160 versus new API3,161.02149 comparison does not by itself establish a revision. Original press-quote precision is not fully retained, and DoltHub's whole-dollar storage does not prove unrounded underlying estimates. Midpoint±$0.5m scoring is the GE project's convention, not an interval inferred from original company endpoint reporting. Raw guide errors must remain visible.

## Reproduction and retained attempts

Canonical local inventory, no network:

```text
python analysis/src/forecast_methods/gbv_event_v1/sources/run_v2.py --name review_new
```

Use a new simple directory name each time; the script refuses an existing destination. Canonical completed command was the same with `--name run_v2 --probe-yahoo`; exit0, local runtime0.61s. It records an unavailable-source result, not successful acquisition. No research tests were run. Two routine inventory corrections were made only in additive `run_v2.py`: choose the event-date column correctly and exclude the approximate pre-IPO calendar row. First code/run remain preserved as `run.py` and `run_v1/`; canonical counts are in `run_v2/`.

## RESUME

GE-EVENT should use real daily legs and explicit vendor rules, label the first-issued-guide surprise as post-release information, and leave call-only moves unavailable. Parent can build Excel and the two-page memo with dated expectations, conditional scenarios and missing2027 Street cells. Independently review the resulting four-quarter arithmetic and claims when handed off; no broad data hunt, new predictor search or margin/FY2028 extension is needed.
