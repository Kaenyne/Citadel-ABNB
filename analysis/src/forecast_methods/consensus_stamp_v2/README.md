# Consensus re-stamp v2

Public ABNB consensus captured 13 September 2026. No model parameters or forecasts are fitted. The L0 register schema is unchanged; extended provenance, high/low and count definitions live in `candidates_20260913.json`.

Run from the repository root in the activated virtual environment:

```powershell
python -X utf8 analysis/src/forecast_methods/consensus_stamp_v2/run.py
python -X utf8 analysis/src/forecast_methods/consensus_stamp_v2/prepare.py
python -X utf8 -m pytest analysis/src/forecast_methods/L0 -q
```

On Windows without an activated environment, replace `python` with `.\.venv\Scripts\python.exe`. The first command verifies the backup is still an exact byte prefix of the register, the row count and receipt hashes. Capture hashes record the original Windows CRLF backup and the mixed-ending append. Git can normalize text to LF on commit/checkout; the receipt therefore also records hashes after CRLF-to-LF normalization. Verification reports `raw_capture_bytes` when raw hashes match, or explicitly `git_text_normalized` when only these canonical hashes match. The raw backup-prefix check remains mandatory in either mode. This check never changes register or backup bytes. The second command reproduces the reviewed candidates without rewriting them. These are offline and exit 0 on success.

Capture uses:

```powershell
python -X utf8 analysis/src/forecast_methods/consensus_stamp_v2/run.py --capture
```

Every capture writes a new UTC folder. Requests use the named public Yahoo/yfinance, Zacks and StockAnalysis interfaces, with no login. Alpha Vantage is attempted only if its environment variable is already set. No credential is printed or retained. `manifest.json` preserves unsuccessful public requests; full raw HTML is not saved. StockAnalysis's public page facts retrieved with `web.run` are transcribed separately in `stockanalysis_web_capture.json`; they are not fabricated from the unsuccessful direct request.

The one authorized append command for this run is recorded in the WP-M note. It requires the register to equal the dated backup immediately before writing, valid provenance and analyst counts, current UTC timestamps, and unique IDs. It appends bytes and writes a receipt. Repeating the append fails safely because the register already differs from the backup. A future run must use a new package/output version, reviewed fresh candidates and a fresh backup; do not change this run's timestamps or receipt.

Yahoo and Alpha Vantage are one LSEG-family panel. Raw Yahoo EPS estimates are stored under `eps_estimate`: the returned table does not independently establish adjusted/GAAP basis. StockAnalysis explicitly labels its EPS as non-GAAP adjusted, so those observations use `eps_adj`. StockAnalysis's displayed analyst count is the fiscal-period forecast panel count; it is not imputed as a metric-specific disclosure. All entries are `role=current`; no September capture belongs in a historical guide-date backtest.
