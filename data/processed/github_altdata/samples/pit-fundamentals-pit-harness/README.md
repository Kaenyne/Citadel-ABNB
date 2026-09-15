# pit-fundamentals sample (christianpichichero-max/pit-fundamentals)

Point-in-time annual XBRL fundamentals for 40 US large caps (16 concepts, FY2006-2026), each row stamped with
`first_filed`, `lag_days`, `original_value` vs `latest_value` and a `restated` flag. No ABNB or travel peers.
Pulled 2026-09-14 with keyless `curl` from raw.githubusercontent.com (HEAD): the full 868 KB CSV, `query_asof.py`,
`check_your_data.py`, `METHODOLOGY.md`, plus the upstream README/LICENSE (renamed UPSTREAM_*). Total ~0.9 MB,
well under the 25 MB cap; nothing truncated. Data is CC0, code MIT.
Value for us is the method: the as-of join in `query_asof.py` and the lookahead-bias audit in `check_your_data.py`
(run `python check_your_data.py <csv>` on our L0 vintage register or harness output). Filing-lag column is a prior
for EDGAR staleness at guide dates (median ~45 days, mean 54).
Full dataset = this repo (`git clone --depth 1 https://github.com/christianpichichero-max/pit-fundamentals`).
