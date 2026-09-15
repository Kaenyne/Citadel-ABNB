# M — Consensus re-stamp, 13 September 2026

Codex WP-M subagent · 13 September 2026 · codex/lane2-full · complete, partial vendor coverage; measured command times below

## Verdict

**PASS on the pre-registered append-integrity line; PARTIAL on multi-vendor capture coverage.** Added 10 documented current rows: eight Yahoo/LSEG-family observations covering revenue and EPS for Q3 2026, Q4 2026, FY2026 and FY2027, plus two S&P/StockAnalysis FY2026 observations. The register grew **161 → 171 rows**. Every original byte and the protected 6 August LSEG row are unchanged; the dated backup exists; all **20 frozen L0 tests pass**. Zacks could not be refreshed, and quarterly S&P data were unavailable through the permitted fetch route. No current nights, ADR, GBV or adjusted-EBITDA consensus was verified. This is a data-capture package, with **zero fitted parameters** and no W1/W2 model claim.

## Pre-registered pass line

Written 2026-09-13T15:18:40Z UTC, before capture and append:

Every new row has vendor + timestamp + n; the 6 Aug 2026 LSEG $4,610M row is byte-identical; the backup exists; row counts before / after are in
the note; the L0 tests pass after the append.

## Scope and controls

Public Yahoo/yfinance, Zacks and StockAnalysis panels; Alpha Vantage only when ALPHAVANTAGE_API_KEY is already available in the environment. Current capture timestamps are UTC to the minute, never historical guide-date timestamps. Yahoo and Alpha Vantage count as one LSEG-family panel. Missing analyst counts are not imputed; such observations stay in the capture evidence and are not admitted under this pass line. The existing 14-column register schema remains unchanged: capture_method and any high/low detail are preserved in a new sidecar and the note field.

Backup: data\processed\forecast_methods\L0\backups\L0_vintage_register_20260913T151840Z.csv

## What ran

Pre-registration and backup were written at 2026-09-13 15:18:40 UTC. Public Yahoo capture completed at 15:20:58 UTC; StockAnalysis web facts were recorded at 15:23 UTC. The append occurred at 17:07:22 UTC. Capture time, vendor publication date and append time are different fields and are not substituted for one another.

Exact repository-root commands on this Windows environment:

```powershell
.\.venv\Scripts\python.exe -X utf8 analysis/src/forecast_methods/consensus_stamp_v2/run.py --capture
.\.venv\Scripts\python.exe -X utf8 analysis/src/forecast_methods/consensus_stamp_v2/prepare.py
.\.venv\Scripts\python.exe -X utf8 analysis/src/forecast_methods/consensus_stamp_v2/run.py --append data/processed/forecast_methods/consensus_stamp_v2/candidates_20260913.json --backup data/processed/forecast_methods/L0/backups/L0_vintage_register_20260913T151840Z.csv
.\.venv\Scripts\python.exe -X utf8 -m pytest analysis/src/forecast_methods/L0 -q
.\.venv\Scripts\python.exe -X utf8 -m pytest analysis/src/forecast_methods/consensus_stamp_v2 -q
.\.venv\Scripts\python.exe -X utf8 analysis/src/forecast_methods/consensus_stamp_v2/run.py
.\.venv\Scripts\python.exe -X utf8 analysis/src/forecast_methods/consensus_stamp_v2/prepare.py
```

All seven commands exited 0. Measured shell wall times: capture 2.40s; candidate build 0.51s; append 0.75s; frozen L0 suite 3.53s (pytest 1.79s); final append-safety suite 1.45s (pytest 0.44s); verification plus candidate replay 0.54s. Initial invocation of the unactivated `python` alias failed because it is not on PATH; the existing `.venv` interpreter was then used. No frozen code or test was edited. No scorer was run by this subagent; the parent owns both CLOSE scorer runs.

The public `web.run` fetch of [StockAnalysis](https://stockanalysis.com/stocks/abnb/forecast/) supplied the annual financial forecast, its source attribution and publication date. The direct HTTP request returned 403, so its separate failure manifest is retained. The manual transcription contains only the observed financial facts, not raw HTML. The `?p=quarterly` fetch did not expose a quarterly table. Public Zacks fetches failed; searches returned historical Q2 reporting rather than an admissible current Q3 operating-KPI panel.

## Results

All appended rows are **current observations**, usable only at or after their own capture time. They are neither PIT historical backtest rows nor full-sample fitted estimates. Revenue units below are USD millions; exact source precision is retained in the sidecar.

| Vendor / panel | Period | Revenue, $M | Analyst n | Capture timestamp UTC | Rows added |
|---|---|---:|---:|---|---:|
| Yahoo Finance / LSEG family | 2026Q3 | 4,744.88187 | 36 | 2026-09-13 15:20 | 1 |
| Yahoo Finance / LSEG family | 2026Q4 | 3,161.02149 | 36 | 2026-09-13 15:20 | 1 |
| Yahoo Finance / LSEG family | FY2026 | 14,164.59484 | 43 | 2026-09-13 15:20 | 1 |
| Yahoo Finance / LSEG family | FY2027 | 15,798.22296 | 43 | 2026-09-13 15:20 | 1 |
| S&P Global via StockAnalysis | FY2026 | 14,160 | 43, fiscal-period panel | 2026-09-13 15:23; vendor updated 2026-09-10 | 1 |

| Vendor / panel | Period | EPS, USD | Metric stored | Analyst n | Capture timestamp UTC | Rows added |
|---|---|---:|---|---:|---|---:|
| Yahoo Finance / LSEG family | 2026Q3 | 2.86264 | eps_estimate | 33 | 2026-09-13 15:20 | 1 |
| Yahoo Finance / LSEG family | 2026Q4 | 0.83151 | eps_estimate | 32 | 2026-09-13 15:20 | 1 |
| Yahoo Finance / LSEG family | FY2026 | 5.31197 | eps_estimate | 39 | 2026-09-13 15:20 | 1 |
| Yahoo Finance / LSEG family | FY2027 | 6.22514 | eps_estimate | 40 | 2026-09-13 15:20 | 1 |
| S&P Global via StockAnalysis | FY2026 | 5.30 | eps_adj | 43, fiscal-period panel | 2026-09-13 15:23; vendor updated 2026-09-10 | 1 |

Yahoo's returned tables do not independently identify adjusted versus GAAP EPS. The new rows therefore use `eps_estimate`, rather than silently asserting the existing `eps_adj` convention. StockAnalysis explicitly identifies its EPS as adjusted. Its n=43 is the count displayed for the FY2026 financial forecast column, not a separately disclosed count for each metric. The source and count distinction remain in every relevant row's note and the candidate sidecar.

Q4 comparison card, with observation ages kept explicit:

| Panel | Q4 2026 revenue, $M | Analyst n | Timestamp attached to that value | Today’s status |
|---|---:|---:|---|---|
| Yahoo / LSEG family | 3,161.02149 | 36 | New capture 2026-09-13 15:20 UTC | Added |
| S&P via StockAnalysis | 3,160 | 35 | Existing register 2026-09-10; time not recorded | No new Q4 capture |
| Zacks | 3,200 | 10 | Existing register 2026-09-11; time not recorded | No new capture |

The last two values are shown only as dated existing register anchors. They have not been certified unchanged today. Yahoo and Alpha Vantage remain one LSEG-family panel; the unavailable Alpha Vantage capture adds zero independent information.

| Audit item | n | Result |
|---|---:|---|
| Original register rows | 161 | Every byte preserved as an exact prefix |
| New rows | 10 | Vendor, UTC minute, positive analyst n, URL and capture method present |
| Final register rows | 171 | 8 Yahoo + 2 S&P new observations |
| Protected pre-guide August row | 1 | Byte-identical; LSEG 4,610M, 2026-08-06 |
| Frozen L0 tests | 20 | PASS, no frozen test edits |
| New append-boundary tests | 8 | PASS, including stale backup, invalid count, historical timestamp, missing provenance, duplicate ID and Git line-ending normalization |
| Candidate deterministic replay | 10 | PASS; existing candidate file unchanged |

The raw backup SHA-256 is `c6402930b7e785a5c24829c6e124023525d3a4be64f33f41ad0ef394cb5af3de`; raw post-append SHA-256 is `199904b04ee4286644b7d2c36f5f9f53f401ff2e2c4ae908ab099125f2de727d`. The source backup has CRLF line endings; the appended lines use LF. No old bytes were normalized. `append_receipt.json` additionally records CRLF-to-LF logical hashes so a Git-normalized checkout can reproduce the audit. `run.py` still requires the local backup to be an exact byte prefix, and reports either `raw_capture_bytes` or explicitly `git_text_normalized`; the final local check is `raw_capture_bytes`. No input file is rewritten by verification.

Evidence is under `data/processed/forecast_methods/consensus_stamp_v2/`: timestamped public Yahoo tables and request manifest, `stockanalysis_web_capture.json`, the reproducible candidate sidecar, append receipt, frozen-test receipt, and both successful append-test receipts. The backup is under the sanctioned `L0/backups/` path. No full raw HTML, licensed terminal export or credentials are retained.

## What failed or could not be done, and why

- **Zacks current panel:** HTTP 403 through the public web fetch and direct request. Search did not yield the requested current panel with its analyst counts. Added n=0 Zacks rows; did not restamp existing values.
- **Quarterly S&P panel:** the allowed fetch returned only the annual page; the quarterly query did not return the required table. Added n=0 Q3/Q4 S&P rows. Browser automation was not used.
- **S&P FY2027:** the page showed revenue 15,770M and adjusted EPS 6.17, but analyst n was hidden with the detail columns. Captured these two observations with n unavailable in the sidecar, admitted n=0 such rows. FY2028 and Q1 2027 were not visible.
- **Alpha Vantage:** the environment variable was absent. No key was sought, typed or printed; added n=0 rows.
- **Operating KPIs and adjusted EBITDA:** no admissible current Q3/Q4 nights, ADR, GBV or adjusted-EBITDA panel was found; added n=0 rows. An August Zacks Q2 comparison article is historical, so its estimates were not presented as a September Q3 consensus.
- **Coverage is partial:** a valid 10-row append does not establish a fresh three-vendor comparison. No inference about dispersion changes, revisions, price impact or an expectations edge is justified by this run alone.

## Interpretation

The new large-panel Q4 revenue anchor is approximately **$3,161M**, captured from Yahoo/LSEG-family estimates at 2026-09-13 15:20 UTC with n=36. The older registered Yahoo page rounded its displayed value to $3,160M; the extra precision now returned by the API is not by itself evidence of a $1M upward consensus revision. A revision claim requires comparable precision and a controlled vendor vintage pair. The FY2026 S&P observation is a re-observation of a vendor-stated 10 September panel, not proof of a new 13 September forecast publication.

The UTC minute timestamps are intentionally more precise than older date-only register rows. Downstream readers must support both formats and must continue excluding current September observations from historical guide-date tests. No frozen L0 API or harness change was requested or made. The parent was notified that L0 was stable after the append and frozen tests, and owns shared workboard, integration, scoring and PR steps.

## RESUME

Run the offline verification and candidate replay commands above to audit this snapshot; do not rerun the append, which deliberately fails against an already changed register. On the next authorized consensus refresh, create a new package/output version and dated backup, capture comparable Yahoo revenue/EPS tables, and seek a public Zacks panel plus quarterly S&P figures with disclosed counts. Preserve both the actual capture time and any vendor publication date, count Yahoo/Alpha Vantage once, and keep unconfirmed EPS basis explicit. On 2–3 November, specifically look for current Zacks nights/ADR/GBV estimates. Parent should update WP-M as done with partial vendor coverage and run both integration scorers; neither the register nor the backup needs any further modification for this package.
