# SCOREBOARD v2 — re-scored narrative after the v2 objects were registered

This is a **new** document. It does not modify or replace `SCOREBOARD.md`, `scoreboard.csv`, or any
registry file — it is a fresh read of the harness output taken this evening. `harness/score.py` was **not**
run to produce it; every number below is read directly out of the CSV that was already on disk.

**CSV vintage.** `data/processed/forecast_methods/harness/scoreboard.csv` — **276 rows**, file mtime
**2026-09-11 18:18:02** (11 Sep 2026, ~18:18 ET). Registry directory
`data/processed/forecast_methods/registry/` holds **69 files**; the latest mtime in that
directory is **2026-09-11 18:51:49** (`l1-reconciliation-v2__fy27_growth_v2.csv`), which is **after** the CSV
was written — i.e. the `l1-reconciliation-v2` files landed on disk after this scoreboard run and their
objects are not, and cannot be, in the 276 rows below. `guidance-policy-v2` (16:56) and `live-block-v2`
(17:00) also postdate the run at the file-timestamp level but register only LIVE rows with no realised
outcome, so their absence from the scored rows is expected regardless of timing (see §2). `fx-lag-v2`
carries a registry mtime of 18:22, four minutes after the CSV — its two files nonetheless appear scored
below; the CSV is the source of truth used throughout, not the file timestamps.

**Every number in every table below is read from `scoreboard.csv` — nothing is recomputed, re-run, or
carried over from the old `SCOREBOARD.md`, whose numbers predate this re-score.** Where this note's
prose disagrees with `SCOREBOARD.md`, the CSV wins.

Registry accounting: **69** `(method, object)` file-groups on disk, of which **48**
appear in `scoreboard.csv` (scored) and **21** do not (LIVE-only — no realised outcome exists yet,
so the scorer correctly drops them; this is expected, not a gap).

**Reading rule.** `RMSE ratio` is the harness's own `rmse_ratio_to_naive` column: the object's RMSE divided
by `baselines__naive`'s RMSE on the identical `(target, window, prior_basis, quarter)` set. The harness
registers a naive baseline for **four** targets only — `revenue_musd`, `revenue_yoy`, `gbv_musd`,
`nights_m`. For the other six targets (`take_rate_pct`, `guide_mid`, `fx_pts_revenue`, `adr_yoy`,
`gbv_yoy`, `nights_yoy`) the ratio column is genuinely empty for every row, and the status column below
says **"no baseline exists"** — never "failed" — per RED_TEAM.md's must-fix. `coverage` is the empirical
coverage of the harness's `[q10, q90]` interval (nominal 0.80, column `cov_empirical`). A status of
**"vacuous (same 10 quarters both windows)"** marks an object whose W1 and W2 windows cover the identical
`first_quarter`/`last_quarter` (both 2024Q1–2026Q2, n=10) — its `survives_both_windows` flag, where True,
carries no information, per RED_TEAM.md §6.4 / §10.3.

Tables below restrict to `prior_basis == PIT` unless headed "full-sample prior"; the CSV's column name for
this is `prior_basis`, values `PIT` and `full_sample`.

---

## 1. Per target, per window (PIT prior)


### Revenue level (revenue_musd) — PIT prior


**W1**

| method | object | n | MAE | RMSE ratio | bias | coverage | status |
|---|---|---:|---:|---:|---:|---:|---|
| calibration-rail | gbm_surprise_guide | 10 | 32.293 | 0.339 | 12.646 | 0.300 | vacuous (same 10 quarters both windows) |
| optimal-mix | mix_revenue_musd_parsimonious | 14 | 28.326 | 0.360 | 12.311 | 0.929 | survives both windows |
| baselines | guide_cushion | 14 | 30.994 | 0.377 | 10.598 | 0.643 | survives both windows |
| guidance-policy | print_from_guide | 14 | 29.167 | 0.379 | 14.689 | 0.857 | survives both windows |
| optimal-mix | mix_revenue_musd_all | 14 | 33.764 | 0.432 | 22.261 | 1.000 | survives both windows |
| kernel-lambda | revenue_level_next_q_last3_ex_covid | 14 | 38.507 | 0.555 | 0.256 | 0.643 | survives both windows |
| kernel-lambda | revenue_level_next_q_ex_covid | 14 | 39.531 | 0.565 | 2.271 | 0.643 | survives both windows |
| optimal-mix | mix_revenue_musd_noguide | 14 | 50.035 | 0.710 | 28.695 | 0.929 | survives both windows |
| guidance-policy | print_kernel_policy | 14 | 52.704 | 0.766 | 37.287 | 1.000 | survives both windows |
| kernel-lambda | revenue_level_next_q_last3 | 14 | 52.704 | 0.766 | 37.287 | 0.786 | survives both windows |
| kernel-lambda | revenue_level_next_q | 14 | 61.096 | 0.831 | 59.023 | 0.786 | survives both windows |
| calibration-rail | gbm_revenue | 10 | 73.590 | 0.927 | 37.001 | 0.600 | vacuous (same 10 quarters both windows) |
| baselines | naive | 14 | 75.093 | 1.000 | 12.777 | 0.929 |  |
| baselines | street | 14 | 87.714 | 1.073 | -68.286 | 0.786 |  |
| baselines | ar1 | 14 | 90.117 | 1.101 | -48.778 | 0.286 |  |
| kernel-lambda | revenue_level_h1 | 14 | 88.260 | 1.169 | 70.214 | 0.857 |  |
| kernel-lambda | revenue_level_next_q_w038 | 14 | 109.548 | 1.433 | 98.669 | 0.929 |  |
| kernel-lambda | revenue_level_next_q_w033 | 14 | 120.146 | 1.584 | 106.900 | 0.929 |  |
| baselines | trailing4 | 14 | 134.788 | 1.806 | 75.334 | 0.857 |  |
| baselines | naive_seasonal | 14 | 340.000 | 3.754 | -340.000 | 0.714 |  |
| l1-reconciliation | revenue_contemporaneous | 10 | 1147.249 | 11.338 | 126.924 | 0.700 | vacuous (same 10 quarters both windows) |


**W2**

| method | object | n | MAE | RMSE ratio | bias | coverage | status |
|---|---|---:|---:|---:|---:|---:|---|
| optimal-mix | mix_revenue_musd_all | 10 | 29.500 | 0.313 | 13.686 | 1.000 | survives both windows |
| baselines | guide_cushion | 10 | 30.895 | 0.319 | 8.728 | 0.600 | survives both windows |
| guidance-policy | print_from_guide | 10 | 30.689 | 0.331 | 12.145 | 0.800 | survives both windows |
| optimal-mix | mix_revenue_musd_parsimonious | 10 | 31.613 | 0.332 | 9.824 | 0.900 | survives both windows |
| calibration-rail | gbm_surprise_guide | 10 | 32.293 | 0.339 | 12.646 | 0.300 | vacuous (same 10 quarters both windows) |
| kernel-lambda | revenue_level_next_q_last3_ex_covid | 10 | 36.165 | 0.472 | 5.857 | 0.700 | survives both windows |
| kernel-lambda | revenue_level_next_q_ex_covid | 10 | 37.598 | 0.484 | 8.679 | 0.700 | survives both windows |
| optimal-mix | mix_revenue_musd_noguide | 10 | 45.424 | 0.587 | 15.548 | 0.900 | survives both windows |
| guidance-policy | print_kernel_policy | 10 | 49.053 | 0.647 | 27.470 | 1.000 | survives both windows |
| kernel-lambda | revenue_level_next_q_last3 | 10 | 49.053 | 0.647 | 27.470 | 0.800 | survives both windows |
| kernel-lambda | revenue_level_next_q | 10 | 60.801 | 0.727 | 57.900 | 0.800 | survives both windows |
| baselines | street | 10 | 82.100 | 0.871 | -54.900 | 0.700 |  |
| kernel-lambda | revenue_level_h1 | 10 | 72.737 | 0.886 | 54.356 | 0.900 |  |
| calibration-rail | gbm_revenue | 10 | 73.590 | 0.927 | 37.001 | 0.600 | vacuous (same 10 quarters both windows) |
| baselines | naive | 10 | 91.482 | 1.000 | 4.239 | 0.900 |  |
| baselines | ar1 | 10 | 93.441 | 1.009 | -35.567 | 0.400 |  |
| baselines | trailing4 | 10 | 98.990 | 1.101 | 15.754 | 1.000 |  |
| kernel-lambda | revenue_level_next_q_w038 | 10 | 106.749 | 1.196 | 93.593 | 0.900 |  |
| kernel-lambda | revenue_level_next_q_w033 | 10 | 116.284 | 1.311 | 101.101 | 0.900 |  |
| baselines | naive_seasonal | 10 | 324.200 | 3.115 | -324.200 | 0.600 |  |
| l1-reconciliation | revenue_contemporaneous | 10 | 1147.249 | 11.338 | 126.924 | 0.700 | vacuous (same 10 quarters both windows) |


### Revenue y/y (revenue_yoy) — PIT prior


**W1**

| method | object | n | MAE | RMSE ratio | bias | coverage | status |
|---|---|---:|---:|---:|---:|---:|---|
| kernel-lambda | revenue_yoy_next_q | 14 | 2.626 | 0.903 | 2.533 | 0.786 | survives both windows |
| optimal-mix | mix_revenue_yoy_all | 14 | 2.519 | 0.909 | 1.540 | 1.000 | survives both windows |
| optimal-mix | mix_revenue_yoy_parsimonious | 14 | 2.574 | 0.937 | 1.450 | 1.000 | survives both windows |
| baselines | naive | 14 | 3.100 | 1.000 | 0.544 | 0.571 |  |
| baselines | ar1 | 14 | 3.839 | 1.138 | -2.221 | 0.286 |  |
| tracker-backlog | revenue_yoy_next_q | 112 | 4.405 | 1.630 | 1.723 | 0.768 |  |
| baselines | trailing4 | 14 | 6.162 | 2.297 | 3.843 | 0.786 |  |
| baselines | naive_seasonal | 14 | 14.139 | 3.849 | -14.139 | 0.000 |  |


**W2**

| method | object | n | MAE | RMSE ratio | bias | coverage | status |
|---|---|---:|---:|---:|---:|---:|---|
| optimal-mix | mix_revenue_yoy_all | 10 | 1.624 | 0.505 | 0.254 | 1.000 | survives both windows |
| optimal-mix | mix_revenue_yoy_parsimonious | 10 | 1.644 | 0.520 | 0.072 | 1.000 | survives both windows |
| kernel-lambda | revenue_yoy_next_q | 10 | 2.389 | 0.756 | 2.258 | 0.800 | survives both windows |
| baselines | naive | 10 | 3.587 | 1.000 | 0.008 | 0.600 |  |
| baselines | ar1 | 10 | 3.799 | 1.034 | -1.535 | 0.400 |  |
| baselines | trailing4 | 10 | 3.820 | 1.077 | 0.573 | 1.000 |  |
| tracker-backlog | revenue_yoy_next_q | 80 | 3.824 | 1.331 | 0.218 | 0.775 |  |
| baselines | naive_seasonal | 10 | 12.501 | 3.036 | -12.501 | 0.000 |  |


### Guide midpoint (guide_mid) — PIT prior


**W1**

| method | object | n | MAE | RMSE ratio | bias | coverage | status |
|---|---|---:|---:|---:|---:|---:|---|
| guidance-policy | guide_mid_next_q | 14 | 51.241 |  | 21.933 | 1.000 | no baseline exists |


**W2**

| method | object | n | MAE | RMSE ratio | bias | coverage | status |
|---|---|---:|---:|---:|---:|---:|---|
| guidance-policy | guide_mid_next_q | 10 | 47.647 |  | 14.909 | 1.000 | no baseline exists |


### Nights y/y (nights_yoy) — PIT prior


**W1**

| method | object | n | MAE | RMSE ratio | bias | coverage | status |
|---|---|---:|---:|---:|---:|---:|---|
| calibration-rail | ref_naive | 14 | 2.128 |  | 0.702 | 0.714 | no baseline exists |
| optimal-mix | mix_nights_yoy_all | 14 | 2.430 |  | 1.825 | 1.000 | no baseline exists |
| optimal-mix | mix_nights_yoy_parsimonious | 14 | 2.430 |  | 1.825 | 1.000 | no baseline exists |
| tracker-backlog | nights_yoy_next_q | 112 | 3.676 |  | 1.627 | 0.964 | no baseline exists |
| calibration-rail | ref_trailing4 | 14 | 3.775 |  | 2.978 | 0.786 | no baseline exists |
| calibration-rail | ref_ar1 | 14 | 4.943 |  | 4.783 | 0.500 | no baseline exists |


**W2**

| method | object | n | MAE | RMSE ratio | bias | coverage | status |
|---|---|---:|---:|---:|---:|---:|---|
| optimal-mix | mix_nights_yoy_all | 10 | 1.472 |  | 0.625 | 1.000 | no baseline exists |
| optimal-mix | mix_nights_yoy_parsimonious | 10 | 1.472 |  | 0.625 | 1.000 | no baseline exists |
| calibration-rail | ref_naive | 10 | 1.656 |  | 0.168 | 0.900 | no baseline exists |
| calibration-rail | ref_trailing4 | 10 | 1.916 |  | 0.801 | 1.000 | no baseline exists |
| calibration-rail | ref_ar1 | 10 | 2.878 |  | 2.654 | 0.700 | no baseline exists |
| tracker-backlog | nights_yoy_next_q | 80 | 3.385 |  | 0.652 | 0.950 | no baseline exists |


### ADR y/y (adr_yoy) — PIT prior


**W1**

| method | object | n | MAE | RMSE ratio | bias | coverage | status |
|---|---|---:|---:|---:|---:|---:|---|
| calibration-rail | ref_ar1 | 14 | 1.475 |  | -0.345 | 0.500 | no baseline exists |
| optimal-mix | mix_adr_yoy_all | 14 | 1.542 |  | -0.426 | 0.643 | no baseline exists |
| optimal-mix | mix_adr_yoy_parsimonious | 14 | 1.542 |  | -0.426 | 0.643 | no baseline exists |
| calibration-rail | ref_naive | 14 | 1.539 |  | -0.416 | 0.643 | no baseline exists |
| calibration-rail | ref_trailing4 | 14 | 1.999 |  | -0.791 | 0.571 | no baseline exists |


**W2**

| method | object | n | MAE | RMSE ratio | bias | coverage | status |
|---|---|---:|---:|---:|---:|---:|---|
| calibration-rail | ref_ar1 | 10 | 1.773 |  | -0.518 | 0.300 | no baseline exists |
| calibration-rail | ref_naive | 10 | 1.727 |  | -0.274 | 0.600 | no baseline exists |
| optimal-mix | mix_adr_yoy_all | 10 | 1.856 |  | -0.487 | 0.600 | no baseline exists |
| optimal-mix | mix_adr_yoy_parsimonious | 10 | 1.856 |  | -0.487 | 0.600 | no baseline exists |
| calibration-rail | ref_trailing4 | 10 | 2.217 |  | -1.053 | 0.600 | no baseline exists |


### GBV y/y (gbv_yoy) — PIT prior


**W1**

| method | object | n | MAE | RMSE ratio | bias | coverage | status |
|---|---|---:|---:|---:|---:|---:|---|
| calibration-rail | ref_naive | 14 | 3.247 |  | 0.266 | 0.786 | no baseline exists |
| optimal-mix | mix_gbv_yoy_all | 14 | 4.119 |  | 1.995 | 0.786 | no baseline exists |
| optimal-mix | mix_gbv_yoy_parsimonious | 14 | 4.119 |  | 1.995 | 0.786 | no baseline exists |
| calibration-rail | ref_ar1 | 14 | 4.949 |  | 4.074 | 0.429 | no baseline exists |
| calibration-rail | ref_trailing4 | 14 | 4.861 |  | 2.243 | 0.786 | no baseline exists |


**W2**

| method | object | n | MAE | RMSE ratio | bias | coverage | status |
|---|---|---:|---:|---:|---:|---:|---|
| calibration-rail | ref_naive | 10 | 3.089 |  | -0.093 | 0.900 | no baseline exists |
| optimal-mix | mix_gbv_yoy_all | 10 | 3.244 |  | 0.306 | 0.900 | no baseline exists |
| optimal-mix | mix_gbv_yoy_parsimonious | 10 | 3.244 |  | 0.306 | 0.900 | no baseline exists |
| calibration-rail | ref_trailing4 | 10 | 3.371 |  | -0.295 | 1.000 | no baseline exists |
| calibration-rail | ref_ar1 | 10 | 3.366 |  | 2.140 | 0.600 | no baseline exists |


### Take rate (take_rate_pct) — PIT prior


**W1**

| method | object | n | MAE | RMSE ratio | bias | coverage | status |
|---|---|---:|---:|---:|---:|---:|---|
| fee-takerate | take_rate_lastyear | 14 | 0.279 |  | 0.139 | 0.714 | no baseline exists |
| optimal-mix | mix_take_rate_pct_repaired | 14 | 0.253 |  | 0.188 | 0.786 | no baseline exists |
| fee-takerate | take_rate_kernel | 14 | 0.343 |  | 0.282 | 0.643 | no baseline exists |
| optimal-mix | mix_take_rate_pct_all | 14 | 0.873 |  | 0.293 | 1.000 | no baseline exists |
| optimal-mix | mix_take_rate_pct_parsimonious | 14 | 1.074 |  | 0.305 | 1.000 | no baseline exists |
| calibration-rail | ref_trailing4 | 14 | 2.465 |  | 0.352 | 0.786 | no baseline exists |
| calibration-rail | ref_ar1 | 14 | 2.521 |  | -0.061 | 0.786 | no baseline exists |
| calibration-rail | ref_naive | 14 | 4.569 |  | 0.059 | 1.000 | no baseline exists |


**W2**

| method | object | n | MAE | RMSE ratio | bias | coverage | status |
|---|---|---:|---:|---:|---:|---:|---|
| optimal-mix | mix_take_rate_pct_repaired | 10 | 0.256 |  | 0.165 | 0.700 | no baseline exists |
| fee-takerate | take_rate_lastyear | 10 | 0.297 |  | 0.102 | 0.600 | no baseline exists |
| fee-takerate | take_rate_kernel | 10 | 0.345 |  | 0.291 | 0.600 | no baseline exists |
| optimal-mix | mix_take_rate_pct_all | 10 | 0.501 |  | 0.440 | 1.000 | no baseline exists |
| optimal-mix | mix_take_rate_pct_parsimonious | 10 | 0.575 |  | 0.424 | 1.000 | no baseline exists |
| calibration-rail | ref_trailing4 | 10 | 2.392 |  | 0.554 | 0.800 | no baseline exists |
| calibration-rail | ref_ar1 | 10 | 2.398 |  | 0.180 | 0.800 | no baseline exists |
| calibration-rail | ref_naive | 10 | 4.489 |  | 0.105 | 1.000 | no baseline exists |


### FX points on revenue (fx_pts_revenue) — PIT prior


**W1**

| method | object | n | MAE | RMSE ratio | bias | coverage | status |
|---|---|---:|---:|---:|---:|---:|---|
| fx-lag | fx_rev_next_q_h2 | 10 | 0.898 |  | 0.097 | 1.000 | no baseline exists; vacuous (same 10 quarters both windows) |
| fx-lag-v2 | fx_rev_next_q_h2_v2 | 10 | 0.898 |  | 0.097 | 1.000 | no baseline exists; vacuous (same 10 quarters both windows) |
| fx-lag | fx_rev_next_q_h3 | 14 | 1.186 |  | 0.432 | 0.500 | no baseline exists |


**W2**

| method | object | n | MAE | RMSE ratio | bias | coverage | status |
|---|---|---:|---:|---:|---:|---:|---|
| fx-lag | fx_rev_next_q_h2 | 10 | 0.898 |  | 0.097 | 1.000 | no baseline exists; vacuous (same 10 quarters both windows) |
| fx-lag-v2 | fx_rev_next_q_h2_v2 | 10 | 0.898 |  | 0.097 | 1.000 | no baseline exists; vacuous (same 10 quarters both windows) |
| fx-lag | fx_rev_next_q_h3 | 10 | 1.398 |  | 0.453 | 0.400 | no baseline exists |


---

## 1b. Full-sample-prior rows (leaky by construction — shown separately, never mixed with PIT above)


The `full_sample` replay refits on the whole sample including the test quarter and is included here only
because it is on the CSV; RED_TEAM.md documents PIT-vs-full-sample gaps up to 51% on these same objects.
Label every number below **full-sample prior** if it is ever quoted.


### Revenue level (revenue_musd) — full-sample prior


**W1**

| method | object | n | MAE | RMSE ratio | bias | coverage | status |
|---|---|---:|---:|---:|---:|---:|---|
| guidance-policy | print_kernel_policy | 14 | 26.175 | 0.357 | -1.206 | 1.000 | survives both windows |
| kernel-lambda | revenue_level_next_q_last3 | 14 | 26.175 | 0.357 | -1.206 | 1.000 | survives both windows |
| kernel-lambda | revenue_level_next_q_last3_ex_covid | 14 | 26.175 | 0.357 | -1.206 | 0.857 | survives both windows |
| optimal-mix | mix_revenue_musd_all | 14 | 29.069 | 0.367 | 17.470 | 1.000 | survives both windows |
| baselines | guide_cushion | 14 | 28.495 | 0.375 | 13.530 | 0.786 | survives both windows |
| guidance-policy | print_from_guide | 14 | 28.672 | 0.379 | 14.206 | 1.000 | survives both windows |
| optimal-mix | mix_revenue_musd_noguide | 14 | 29.558 | 0.383 | 13.944 | 1.000 | survives both windows |
| calibration-rail | gbm_surprise_guide | 14 | 31.356 | 0.387 | 4.605 | 0.214 | vacuous (same 10 quarters both windows) |
| kernel-lambda | revenue_level_next_q_ex_covid | 14 | 26.534 | 0.389 | 0.258 | 0.929 | survives both windows |
| optimal-mix | mix_revenue_musd_parsimonious | 14 | 30.642 | 0.411 | 20.972 | 1.000 | survives both windows |
| kernel-lambda | revenue_level_next_q | 14 | 38.497 | 0.533 | 31.818 | 0.929 | survives both windows |
| calibration-rail | gbm_revenue | 14 | 52.978 | 0.777 | -9.395 | 0.429 | vacuous (same 10 quarters both windows) |
| kernel-lambda | revenue_level_next_q_w038 | 14 | 62.714 | 0.827 | 53.842 | 1.000 | survives both windows |
| kernel-lambda | revenue_level_h1 | 14 | 64.935 | 0.859 | 42.618 | 0.857 | survives both windows |
| baselines | ar1 | 14 | 64.055 | 0.900 | -5.079 | 0.714 | survives both windows |
| kernel-lambda | revenue_level_next_q_w033 | 14 | 68.024 | 0.909 | 58.407 | 1.000 | survives both windows |
| baselines | naive | 14 | 75.093 | 1.000 | 12.777 | 0.714 |  |
| baselines | street | 14 | 87.714 | 1.073 | -68.286 | 0.929 |  |
| baselines | trailing4 | 14 | 134.788 | 1.806 | 75.334 | 0.643 |  |
| baselines | naive_seasonal | 14 | 340.000 | 3.754 | -340.000 | 0.000 |  |
| l1-reconciliation | revenue_contemporaneous | 14 | 1003.685 | 10.927 | -12.292 | 0.643 | vacuous (same 10 quarters both windows) |


**W2**

| method | object | n | MAE | RMSE ratio | bias | coverage | status |
|---|---|---:|---:|---:|---:|---:|---|
| optimal-mix | mix_revenue_musd_noguide | 10 | 27.957 | 0.326 | 6.098 | 1.000 | survives both windows |
| guidance-policy | print_kernel_policy | 10 | 29.825 | 0.348 | 2.026 | 1.000 | survives both windows |
| kernel-lambda | revenue_level_next_q_last3 | 10 | 29.825 | 0.348 | 2.026 | 1.000 | survives both windows |
| kernel-lambda | revenue_level_next_q_last3_ex_covid | 10 | 29.825 | 0.348 | 2.026 | 0.800 | survives both windows |
| optimal-mix | mix_revenue_musd_all | 10 | 32.872 | 0.352 | 16.634 | 1.000 | survives both windows |
| baselines | guide_cushion | 10 | 31.221 | 0.359 | 17.769 | 0.700 | survives both windows |
| guidance-policy | print_from_guide | 10 | 31.454 | 0.363 | 18.479 | 1.000 | survives both windows |
| optimal-mix | mix_revenue_musd_parsimonious | 10 | 31.938 | 0.365 | 18.401 | 1.000 | survives both windows |
| kernel-lambda | revenue_level_next_q_ex_covid | 10 | 31.356 | 0.375 | 4.481 | 0.900 | survives both windows |
| calibration-rail | gbm_surprise_guide | 10 | 37.269 | 0.376 | 9.044 | 0.100 | vacuous (same 10 quarters both windows) |
| calibration-rail | gbm_revenue | 10 | 44.254 | 0.484 | -1.725 | 0.400 | vacuous (same 10 quarters both windows) |
| kernel-lambda | revenue_level_next_q | 10 | 45.388 | 0.527 | 37.979 | 0.900 | survives both windows |
| kernel-lambda | revenue_level_h1 | 10 | 57.274 | 0.703 | 34.359 | 0.900 | survives both windows |
| kernel-lambda | revenue_level_next_q_w038 | 10 | 74.853 | 0.812 | 62.433 | 1.000 | survives both windows |
| baselines | street | 10 | 82.100 | 0.871 | -54.900 | 1.000 |  |
| kernel-lambda | revenue_level_next_q_w033 | 10 | 81.008 | 0.887 | 67.544 | 1.000 | survives both windows |
| baselines | ar1 | 10 | 82.801 | 0.916 | -7.628 | 0.600 | survives both windows |
| baselines | naive | 10 | 91.482 | 1.000 | 4.239 | 0.600 |  |
| baselines | trailing4 | 10 | 98.990 | 1.101 | 15.754 | 0.700 |  |
| baselines | naive_seasonal | 10 | 324.200 | 3.115 | -324.200 | 0.000 |  |
| l1-reconciliation | revenue_contemporaneous | 10 | 1077.295 | 10.093 | 22.522 | 0.700 | vacuous (same 10 quarters both windows) |


### Revenue y/y (revenue_yoy) — full-sample prior


**W1**

| method | object | n | MAE | RMSE ratio | bias | coverage | status |
|---|---|---:|---:|---:|---:|---:|---|
| kernel-lambda | revenue_yoy_next_q | 14 | 1.597 | 0.551 | 1.275 | 0.929 | survives both windows |
| optimal-mix | mix_revenue_yoy_all | 14 | 2.069 | 0.691 | 1.329 | 1.000 | survives both windows |
| optimal-mix | mix_revenue_yoy_parsimonious | 14 | 2.182 | 0.725 | 1.334 | 1.000 | survives both windows |
| baselines | ar1 | 14 | 2.616 | 0.896 | -0.249 | 0.714 | survives both windows |
| baselines | naive | 14 | 3.100 | 1.000 | 0.544 | 0.714 |  |
| tracker-backlog | revenue_yoy_next_q | 112 | 3.377 | 1.231 | 1.318 | 0.857 |  |
| baselines | trailing4 | 14 | 6.162 | 2.297 | 3.843 | 0.643 |  |
| baselines | naive_seasonal | 14 | 14.139 | 3.849 | -14.139 | 0.000 |  |


**W2**

| method | object | n | MAE | RMSE ratio | bias | coverage | status |
|---|---|---:|---:|---:|---:|---:|---|
| optimal-mix | mix_revenue_yoy_all | 10 | 1.623 | 0.495 | 0.588 | 1.000 | survives both windows |
| optimal-mix | mix_revenue_yoy_parsimonious | 10 | 1.698 | 0.510 | 0.511 | 1.000 | survives both windows |
| kernel-lambda | revenue_yoy_next_q | 10 | 1.812 | 0.552 | 1.429 | 0.900 | survives both windows |
| baselines | ar1 | 10 | 3.333 | 0.935 | -0.451 | 0.600 | survives both windows |
| baselines | naive | 10 | 3.587 | 1.000 | 0.008 | 0.600 |  |
| baselines | trailing4 | 10 | 3.820 | 1.077 | 0.573 | 0.700 |  |
| tracker-backlog | revenue_yoy_next_q | 80 | 3.311 | 1.127 | 0.687 | 0.850 |  |
| baselines | naive_seasonal | 10 | 12.501 | 3.036 | -12.501 | 0.000 |  |


### Guide midpoint (guide_mid) — full-sample prior


**W1**

| method | object | n | MAE | RMSE ratio | bias | coverage | status |
|---|---|---:|---:|---:|---:|---:|---|
| guidance-policy | guide_mid_next_q | 14 | 33.122 |  | -15.030 | 1.000 | no baseline exists |


**W2**

| method | object | n | MAE | RMSE ratio | bias | coverage | status |
|---|---|---:|---:|---:|---:|---:|---|
| guidance-policy | guide_mid_next_q | 10 | 31.727 |  | -16.045 | 1.000 | no baseline exists |


### Nights y/y (nights_yoy) — full-sample prior


**W1**

| method | object | n | MAE | RMSE ratio | bias | coverage | status |
|---|---|---:|---:|---:|---:|---:|---|
| optimal-mix | mix_nights_yoy_all | 14 | 1.664 |  | 1.067 | 1.000 | no baseline exists |
| optimal-mix | mix_nights_yoy_parsimonious | 14 | 1.664 |  | 1.067 | 1.000 | no baseline exists |
| calibration-rail | ref_ar1 | 14 | 2.138 |  | 1.583 | 0.786 | no baseline exists |
| calibration-rail | ref_naive | 14 | 2.128 |  | 0.702 | 0.786 | no baseline exists |
| tracker-backlog | nights_yoy_next_q | 112 | 2.845 |  | 1.023 | 0.955 | no baseline exists |
| calibration-rail | ref_trailing4 | 14 | 3.775 |  | 2.978 | 0.643 | no baseline exists |


**W2**

| method | object | n | MAE | RMSE ratio | bias | coverage | status |
|---|---|---:|---:|---:|---:|---:|---|
| optimal-mix | mix_nights_yoy_all | 10 | 1.430 |  | 0.594 | 1.000 | no baseline exists |
| optimal-mix | mix_nights_yoy_parsimonious | 10 | 1.430 |  | 0.594 | 1.000 | no baseline exists |
| calibration-rail | ref_naive | 10 | 1.656 |  | 0.168 | 0.800 | no baseline exists |
| calibration-rail | ref_trailing4 | 10 | 1.916 |  | 0.801 | 0.900 | no baseline exists |
| calibration-rail | ref_ar1 | 10 | 1.970 |  | 1.513 | 0.800 | no baseline exists |
| tracker-backlog | nights_yoy_next_q | 80 | 2.899 |  | 0.806 | 0.950 | no baseline exists |


### ADR y/y (adr_yoy) — full-sample prior


**W1**

| method | object | n | MAE | RMSE ratio | bias | coverage | status |
|---|---|---:|---:|---:|---:|---:|---|
| calibration-rail | ref_ar1 | 14 | 1.441 |  | -0.078 | 0.857 | no baseline exists |
| optimal-mix | mix_adr_yoy_all | 14 | 1.511 |  | -0.324 | 0.929 | no baseline exists |
| optimal-mix | mix_adr_yoy_parsimonious | 14 | 1.511 |  | -0.324 | 0.929 | no baseline exists |
| calibration-rail | ref_naive | 14 | 1.539 |  | -0.416 | 0.786 | no baseline exists |
| calibration-rail | ref_trailing4 | 14 | 1.999 |  | -0.791 | 0.786 | no baseline exists |


**W2**

| method | object | n | MAE | RMSE ratio | bias | coverage | status |
|---|---|---:|---:|---:|---:|---:|---|
| calibration-rail | ref_ar1 | 10 | 1.735 |  | -0.213 | 0.800 | no baseline exists |
| optimal-mix | mix_adr_yoy_all | 10 | 1.841 |  | -0.367 | 0.900 | no baseline exists |
| optimal-mix | mix_adr_yoy_parsimonious | 10 | 1.841 |  | -0.367 | 0.900 | no baseline exists |
| calibration-rail | ref_naive | 10 | 1.727 |  | -0.274 | 0.700 | no baseline exists |
| calibration-rail | ref_trailing4 | 10 | 2.217 |  | -1.053 | 0.700 | no baseline exists |


### GBV y/y (gbv_yoy) — full-sample prior


**W1**

| method | object | n | MAE | RMSE ratio | bias | coverage | status |
|---|---|---:|---:|---:|---:|---:|---|
| calibration-rail | ref_ar1 | 14 | 2.843 |  | 1.474 | 0.857 | no baseline exists |
| calibration-rail | ref_naive | 14 | 3.247 |  | 0.266 | 0.786 | no baseline exists |
| optimal-mix | mix_gbv_yoy_all | 14 | 3.494 |  | 1.487 | 0.857 | no baseline exists |
| optimal-mix | mix_gbv_yoy_parsimonious | 14 | 3.494 |  | 1.487 | 0.857 | no baseline exists |
| calibration-rail | ref_trailing4 | 14 | 4.861 |  | 2.243 | 0.786 | no baseline exists |


**W2**

| method | object | n | MAE | RMSE ratio | bias | coverage | status |
|---|---|---:|---:|---:|---:|---:|---|
| optimal-mix | mix_gbv_yoy_all | 10 | 3.043 |  | 0.577 | 0.900 | no baseline exists |
| optimal-mix | mix_gbv_yoy_parsimonious | 10 | 3.043 |  | 0.577 | 0.900 | no baseline exists |
| calibration-rail | ref_ar1 | 10 | 2.710 |  | 1.449 | 0.900 | no baseline exists |
| calibration-rail | ref_naive | 10 | 3.089 |  | -0.093 | 0.900 | no baseline exists |
| calibration-rail | ref_trailing4 | 10 | 3.371 |  | -0.295 | 0.900 | no baseline exists |


### Take rate (take_rate_pct) — full-sample prior


**W1**

| method | object | n | MAE | RMSE ratio | bias | coverage | status |
|---|---|---:|---:|---:|---:|---:|---|
| optimal-mix | mix_take_rate_pct_repaired | 14 | 0.303 |  | 0.183 | 0.857 | no baseline exists |
| fee-takerate | take_rate_lastyear | 14 | 0.288 |  | 0.190 | 0.857 | no baseline exists |
| fee-takerate | take_rate_kernel | 14 | 0.336 |  | 0.154 | 0.786 | no baseline exists |
| optimal-mix | mix_take_rate_pct_all | 14 | 0.899 |  | 0.349 | 1.000 | no baseline exists |
| optimal-mix | mix_take_rate_pct_parsimonious | 14 | 1.102 |  | 0.414 | 0.929 | no baseline exists |
| calibration-rail | ref_trailing4 | 14 | 2.465 |  | 0.352 | 0.571 | no baseline exists |
| calibration-rail | ref_ar1 | 14 | 2.479 |  | -0.019 | 0.714 | no baseline exists |
| calibration-rail | ref_naive | 14 | 4.569 |  | 0.059 | 1.000 | no baseline exists |


**W2**

| method | object | n | MAE | RMSE ratio | bias | coverage | status |
|---|---|---:|---:|---:|---:|---:|---|
| fee-takerate | take_rate_kernel | 10 | 0.327 |  | 0.205 | 0.800 | no baseline exists |
| optimal-mix | mix_take_rate_pct_repaired | 10 | 0.321 |  | 0.263 | 0.800 | no baseline exists |
| fee-takerate | take_rate_lastyear | 10 | 0.339 |  | 0.291 | 0.800 | no baseline exists |
| optimal-mix | mix_take_rate_pct_all | 10 | 0.548 |  | 0.541 | 1.000 | no baseline exists |
| optimal-mix | mix_take_rate_pct_parsimonious | 10 | 0.618 |  | 0.615 | 0.900 | no baseline exists |
| calibration-rail | ref_trailing4 | 10 | 2.392 |  | 0.554 | 0.600 | no baseline exists |
| calibration-rail | ref_ar1 | 10 | 2.368 |  | 0.143 | 0.800 | no baseline exists |
| calibration-rail | ref_naive | 10 | 4.489 |  | 0.105 | 1.000 | no baseline exists |


### FX points on revenue (fx_pts_revenue) — full-sample prior


**W1**

| method | object | n | MAE | RMSE ratio | bias | coverage | status |
|---|---|---:|---:|---:|---:|---:|---|
| fx-lag | fx_rev_next_q_h2 | 10 | 0.866 |  | -0.019 | 1.000 | no baseline exists; vacuous (same 10 quarters both windows) |
| fx-lag-v2 | fx_rev_next_q_h2_v2 | 10 | 0.866 |  | -0.019 | 1.000 | no baseline exists; vacuous (same 10 quarters both windows) |
| fx-lag | fx_rev_next_q_h3 | 14 | 0.864 |  | 0.026 | 0.857 | no baseline exists |


**W2**

| method | object | n | MAE | RMSE ratio | bias | coverage | status |
|---|---|---:|---:|---:|---:|---:|---|
| fx-lag | fx_rev_next_q_h3 | 10 | 0.723 |  | 0.191 | 0.900 | no baseline exists |
| fx-lag | fx_rev_next_q_h2 | 10 | 0.866 |  | -0.019 | 1.000 | no baseline exists; vacuous (same 10 quarters both windows) |
| fx-lag-v2 | fx_rev_next_q_h2_v2 | 10 | 0.866 |  | -0.019 | 1.000 | no baseline exists; vacuous (same 10 quarters both windows) |
---

## 2. What changed with the v2 objects

Four new method names appear in the registry since the base build: `live-block-v2`,
`guidance-policy-v2`, `l1-reconciliation-v2`, `fx-lag-v2` (B1–B4 respectively; see
`05_backtests/B1_TAKE_RATE_RECONCILIATION.md` … `B4_FX_EXHIBIT.md`). Checked against
`scoreboard.csv` directly:

**LIVE-only — no realised outcome yet, absence from the scored rows is expected, not a gap:**

| method | registry objects | why they cannot be scored |
|---|---|---|
| `live-block-v2` | `revenue`, `gbv`, `nights`, `adr`, `take_rate` (all 5 files) | All 2026Q3, window `LIVE` — the quarter has not printed; the harness scorer drops any row with no actual by design, exactly as it does for the 8 v1 LIVE objects (`kernel-lambda__live_3q26_print`, `guidance-policy__q4_2026_print`, etc.) |
| `guidance-policy-v2` | `gbv_musd_live`, `q4_2026_guide_mid_v2`, `q4_2026_print_v2` (all 3 files) | Same reason — 2026Q3/2026Q4 LIVE rows, no actual exists |
| `l1-reconciliation-v2` | `fy27_revenue_v2`, `fy27_growth_v2` (both files) | FY27 has not printed, **and** these files were written at 18:51 ET, after this scoreboard CSV (18:18 ET) was produced — they could not appear even if they were scorable today |

**Scored — the only v2 method with a realised-outcome row in the CSV:**

`fx-lag-v2 / fx_rev_next_q_h2_v2`, target `fx_pts_revenue`, appears on **4 rows**: W1/W2 × PIT/full-sample
(identical values across W1 and W2 because this object is vacuous — see §3). Read from the CSV:

| prior_basis | n | MAE | RMSE | bias | coverage |
|---|---:|---:|---:|---:|---:|
| PIT | 10 | 0.898 | 0.994 | 0.097 | 1.000 |
| full_sample | 10 | 0.866 | 0.990 | -0.019 | 1.000 |

MAE is **0.87–0.90 pp**, matching the range quoted in the task brief. `fx_pts_revenue` has no naive
baseline registered (§4), so `rmse_ratio_to_naive` is empty for these rows too — "no baseline exists,"
not "failed" — and the RMSE/MAE values above are pp-level errors, not ratios.

**A data-quality note that belongs here, not just in §4:** `fx-lag-v2 / fx_rev_next_q_h2_v2`'s four scored
rows are numerically **identical** to `fx-lag / fx_rev_next_q_h2`'s four rows (n=10, MAE 0.89771/0.86628,
RMSE 0.993590/0.989844, bias 0.09747/-0.01904, coverage 1.000, in both PIT and full-sample). Diffing the
two registry CSVs confirms the underlying per-quarter rows are the same forecast, re-registered under a
new method/object name with `spec_id` suffixed `_FXrefresh_2026-09-11` and a notes field saying "FX
refreshed to 2026-09-04" — but the FX refresh moves only 3Q26 QTD data (per B4_FX_EXHIBIT.md), which is
outside the 2024Q1–2026Q2 backtest window scored here. So the v2 refresh changed nothing that reaches
this scoreboard; the historical PIT/backtest numbers for `fx_rev_next_q_h2` and `fx_rev_next_q_h2_v2` are,
correctly, the same object measured twice.

**Revenue-level winner on PIT rows — is it still `guide_cushion` on both windows?**

**Not exactly, and the CSV now shows why.** Quoting `rmse_ratio_to_naive` exactly, PIT, `revenue_musd`:

| object | method | W1 ratio | W2 ratio |
|---|---|---:|---:|
| `guide_cushion` | baselines | **0.377073** | **0.319073** |
| `print_from_guide` | guidance-policy | 0.378782 | 0.330772 |
| `mix_revenue_musd_parsimonious` | optimal-mix | **0.360353** | 0.332362 |
| `mix_revenue_musd_all` | optimal-mix | 0.431772 | **0.312855** |

With the optimal-mix objects now scored, `mix_revenue_musd_parsimonious` has a **lower** ratio than
`guide_cushion` on W1 (0.360 vs 0.377) and `mix_revenue_musd_all` has a **lower** ratio than
`guide_cushion` on W2 (0.313 vs 0.319). Neither mix variant beats `guide_cushion` on **both** windows at
once — they split the windows exactly the way RED_TEAM.md §2 anticipated before the mix objects were even
scored ("both split the windows, so the 'no combination survives both windows' conclusion is unchanged —
but it should be shown, not asserted"). So: **`guide_cushion` is no longer the single lowest-ratio row on
either window**, but it is still the best-performing object that is not itself a stacked combination of
other objects on the board, and it still beats `print_from_guide` — the guidance-policy package's own
headline object — on both windows (0.377 < 0.379 on W1, 0.319 < 0.331 on W2). No object of any kind beats
naive on both windows by more than the `mix_revenue_musd_parsimonious` / `guide_cushion` pair does, and
no single object is the ratio-minimiser on both windows simultaneously.

---

## 3. Survivors on both windows

Restricting to `prior_basis == PIT` and pairing each object's W1 and W2 `rmse_ratio_to_naive` (both
present and both below 1.0 — i.e. `survives_both_windows == True` with a real ratio):

**Non-vacuous survivors (13 objects):**

| method | object | target | W1 ratio | W2 ratio |
|---|---|---|---:|---:|
| optimal-mix | mix_revenue_musd_parsimonious | revenue_musd | 0.360 | 0.332 |
| baselines | guide_cushion | revenue_musd | 0.377 | 0.319 |
| guidance-policy | print_from_guide | revenue_musd | 0.379 | 0.331 |
| optimal-mix | mix_revenue_musd_all | revenue_musd | 0.432 | 0.313 |
| kernel-lambda | revenue_level_next_q_last3_ex_covid | revenue_musd | 0.555 | 0.472 |
| kernel-lambda | revenue_level_next_q_ex_covid | revenue_musd | 0.565 | 0.484 |
| optimal-mix | mix_revenue_musd_noguide | revenue_musd | 0.710 | 0.587 |
| guidance-policy | print_kernel_policy | revenue_musd | 0.766 | 0.647 |
| kernel-lambda | revenue_level_next_q_last3 | revenue_musd | 0.766 | 0.647 |
| kernel-lambda | revenue_level_next_q | revenue_musd | 0.831 | 0.727 |
| kernel-lambda | revenue_yoy_next_q | revenue_yoy | 0.903 | 0.756 |
| optimal-mix | mix_revenue_yoy_all | revenue_yoy | 0.909 | 0.505 |
| optimal-mix | mix_revenue_yoy_parsimonious | revenue_yoy | 0.937 | 0.520 |

All 13 are `revenue_musd` or `revenue_yoy` objects — the only two targets in the CSV with a naive
baseline **and** at least one object beating it on both windows. No `gbv_musd` or `nights_m` object
(the other two targets with a naive baseline) survives both windows in this CSV.

**Flagged vacuous (survives both windows only because W1 and W2 are the identical 10 quarters — 2
objects, both `revenue_musd`):**

| method | object | target | W1 ratio | W2 ratio |
|---|---|---|---:|---:|
| calibration-rail | gbm_surprise_guide | revenue_musd | 0.339 | 0.339 |
| calibration-rail | gbm_revenue | revenue_musd | 0.927 | 0.927 |

Two further objects are vacuous by the same same-quarters test but do **not** count as survivors because
their ratio is empty or above 1: `fx-lag / fx_rev_next_q_h2` and `fx-lag-v2 / fx_rev_next_q_h2_v2` (no
naive baseline exists for `fx_pts_revenue`, so `survives_both_windows` is `False` by construction, not by
failing) and `l1-reconciliation / revenue_contemporaneous` (ratio 11.338, a declared negative control that
loses badly on both windows). All five same-quarters objects are listed here for completeness; only the
first two are counted as "survivors."

---

## 4. Data quality

**4.1 Missing baselines, per target.** `baselines__naive` exists for four targets only:
`revenue_musd`, `revenue_yoy`, `gbv_musd`, `nights_m`. The other six targets have **zero** rows with a
populated `rmse_ratio_to_naive`:

| target | total rows (PIT + full-sample) | rows with empty ratio |
|---|---:|---:|
| adr_yoy | 20 | 20 |
| fx_pts_revenue | 12 | 12 |
| gbv_yoy | 20 | 20 |
| guide_mid | 4 | 4 |
| nights_yoy | 24 | 24 |
| take_rate_pct | 32 | 32 |

That is **112 of 276 rows (41%)** with a structurally empty denominator. Every one of them has
`survives_both_windows == False`, and per RED_TEAM.md's must-fix, that `False` means **"not testable
here,"** not "lost to naive." `gbv_musd`, `nights_m`, `revenue_musd` and `revenue_yoy` have a naive row
and no missing-ratio problem.

**4.2 The calibration-rail take-rate reference-row bug.** `calibration-rail__ref_naive`,
`__ref_ar1` and `__ref_trailing4` register rows against `take_rate_pct` (among other targets) with MAE
**2.4–4.6** on a 13–18% level series — 10–15× the MAE of `fee-takerate__take_rate_lastyear` (0.28–0.30) or
`take_rate_kernel` (0.34) on the identical quarters. Confirmed directly in the CSV (PIT, W1):
`ref_naive` MAE 4.569, `ref_ar1` MAE 2.521, `ref_trailing4` MAE 2.465, against `take_rate_lastyear` MAE
0.279 and `take_rate_kernel` MAE 0.343. This is the classification bug RED_TEAM.md documents: the harness
treats `take_rate_pct` as growth-like by its `_pct` suffix and compounds a y/y growth rate onto a level,
rather than comparing levels to levels. These three `ref_*` rows are not a meaningful comparator for a
level series and should be read as a symptom of the bug, not as a baseline any take-rate object should be
expected to beat.

**4.3 Objects registered by more than one package under different names.** `fx-lag / fx_rev_next_q_h2`
and `fx-lag-v2 / fx_rev_next_q_h2_v2` score **identically** on every metric in the CSV across PIT and
full-sample, both windows (§2) — the same forecast, registered twice under two method names. No other
confirmed duplicate exists among the 48 `(method, object)` pairs that are actually scored in this CSV.
Three LIVE-only v2 packages (`guidance-policy-v2`, `l1-reconciliation-v2`, `live-block-v2`) register
object names that read as v2 counterparts of existing v1 LIVE objects (e.g. `q4_2026_guide_mid_v2` next
to v1's `q4_2026_guide_mid`; `fy27_revenue_v2` next to v1's `fy27_revenue`) — worth the same duplication
check once they have a realised outcome and appear in a future scoreboard CSV, but this cannot be
confirmed or refuted from `scoreboard.csv` today because none of them has a scored row.

**4.4 Vacuous same-quarters objects (from §3), restated as a data-quality item.** Five `(method,
object)` groups have `first_quarter`/`last_quarter` identical between W1 and W2 (both 2024Q1–2026Q2,
n=10 in both): `calibration-rail / gbm_revenue`, `calibration-rail / gbm_surprise_guide`, `fx-lag /
fx_rev_next_q_h2`, `fx-lag-v2 / fx_rev_next_q_h2_v2`, `l1-reconciliation / revenue_contemporaneous`. For
these five, "W1" and "W2" are the same backtest re-labelled twice; `survives_both_windows == True` on
`gbm_revenue` and `gbm_surprise_guide` is real arithmetic but carries no both-windows information.

**4.5 Row-count reconciliation.** 276 rows in the CSV; 48 of the 69 registry `(method, object)` file
groups are represented (scored); 21 are LIVE-only and correctly absent (§2). This CSV is larger than any
prior scoreboard version because it is the first run after the `optimal-mix` objects and `fx-lag-v2` were
registered; it predates `l1-reconciliation-v2` by about half an hour (§ header) and postdates
`guidance-policy-v2` / `live-block-v2`, whose objects do not appear because they have no realised outcome,
not because of timing.

---

*This narrative was written 11 Sep 2026 by reading `data/processed/forecast_methods/harness/scoreboard.csv`
(276 rows), the registry directory (69 files), `RED_TEAM.md`, `SCOREBOARD.md` (structure reference only —
its numbers predate this re-score), `B1_TAKE_RATE_RECONCILIATION.md` through `B4_FX_EXHIBIT.md`, and
`PREREG_ABNB-INT-v1.md`. `harness/score.py` was not run. No registry file, `scoreboard.csv`, or
`SCOREBOARD.md` was modified. Nothing was committed to git.*
