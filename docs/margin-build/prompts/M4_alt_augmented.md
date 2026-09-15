# M4: Alt-data-augmented line model: does any external signal add to the driver model?

Read `docs/margin-build/prompts/M_common.md` first. Slug: `M4_alt_augmented`. Method name: `alt-augmented`.
Inputs: WS04 (`04_signal_panel_quarterly.csv`, `04_signal_tests.csv`, `04_signal_catalogue.csv`), WS01 census, and M1's registered objects and
residuals (`data/processed/margin_build/M1_driver_lines/`; if M1 is not finished, build your own thin per-unit baseline per line and say so).

## Method

For each cash line, start from the M1 per-unit model (or the pct_rev_seasonal baseline) and add ONE external signal at a time, lagged so it is
knowable at the vintage date (WS04's `knowable_from`): job-posting / headcount proxies for pd and ga; Google Trends and ad-transparency series
for sm; support/complaint proxies and the AI-support step for ops; payment-rate, cross-border share and hosting-price series for cor; T-bill yield x
funds held for interest income (hand the interest-income result to M7 via your note). Use ridge / small OLS with recency weights; a LightGBM
variant only if n allows (it does not, so probably skip and say so). Register the best one-signal spec per line as `spec_id`, plus an
"all candidates, L2-penalised" spec, plus a "none" spec identical to M1 so the delta is visible.

## Tests (pre-register)

Incremental value = MAE(M1 + signal) / MAE(M1), PIT, W1 and W2, h=0 and h=1, equal and recency weighted. A signal counts only if the ratio is
below 0.9 in both windows and the coefficient sign matches the mechanism. Expect zero to two survivors; report the full grid and the count of tests.
Include a placebo: the same test with the signal shifted by +4 quarters (future values) to show what leakage would look like, and a random-series
placebo to show the false-positive rate on n 10-14.

## LIVE

Only for surviving signals: the adjusted line and margin forecasts 3Q26-4Q27 with and without the signal. If none survive, the LIVE table
equals M1 and the note says why the alt-data route does not move margins (or which signal is closest and what data would settle it).
