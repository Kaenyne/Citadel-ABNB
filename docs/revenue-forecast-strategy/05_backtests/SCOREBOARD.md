# SCOREBOARD — overnight forecast-methods programme

Scorekeeper run, 2026-09-11. Every number below was either produced by the harness scorer
on this run or read directly out of a package CSV; nothing is quoted from a package's prose
without being checked against its own data file. Where a package's claim and its CSV
disagree, the CSV wins and the disagreement is stated.

## What was run

```bash
cd "/Users/theomachado/Library/CloudStorage/OneDrive-UniversityofFlorida/Young, Willem K.'s files - Citadel - ABNB/Citadel-ABNB"
/Users/theomachado/.venvs/citadel-abnb/bin/python analysis/src/forecast_methods/harness/score.py
```

Exit code 0. Console: `registry: 3170 rows across 37 objects` / `scoreboard: 200 rows`.

* Registry files read: **37** (6 baseline objects + 31 package objects), all 37 parsed and
  validated by the harness loader. **No file needed a format fix and no file was excluded.**
* Objects scored: **29**. The other **8** are LIVE-only (2026Q3 onward), have no actual, and
  the scorer drops LIVE by design. They are assembled by hand in section 5.
* Outputs: `data/processed/forecast_methods/harness/scoreboard.csv` (200 rows x 42 cols),
  `scoreboard.md`, and (scorekeeper supplement, not a harness product)
  `scoreboard_tracker_backlog_by_spec.csv`, plus
  `data/processed/forecast_methods/harness/live_objects.json`.

**Reading rule for every table.** `RMSE/naive` is the harness ratio against
`baselines__naive` on the same `(target, window, prior_basis, quarter)` set. The harness
registers naive only for `revenue_musd`, `revenue_yoy`, `gbv_musd` and `nights_m`; for the
other six targets the column is genuinely empty and any ratio shown is marked `*` and is a
locally built denominator, not the harness ratio. `cov80` is empirical coverage of the
[q10,q90] band, nominal 0.80. `survives both` is the harness flag: beats naive in **both**
W1 and W2; it is `no` wherever no naive denominator exists, so absence of the flag on
`take_rate_pct`, `fx_pts_revenue`, `nights_yoy`, `gbv_yoy`, `adr_yoy` and `guide_mid` means
"not testable here", not "failed". Conformal coverage carries the harness caveat verbatim:
EXCHANGEABILITY VIOLATED — residuals are a time-ordered non-exchangeable sequence, so
conformal coverage is descriptive, not a guarantee; at n_cal 6 / alpha 0.2 the attainable
band is [85.7%, 100%] and no 80% guarantee exists at this sample size.

---

## 1. Per target, per window

### revenue_musd — PIT prior

| window | method / object | n | MAE | RMSE | bias | RMSE/naive | CRPS | cov80 | survives both |
|---|---|---:|---:|---:|---:|---:|---:|---:|:--:|
| W1 | baselines / guide_cushion | 14 | 30.994 | 35.457 | 10.598 | 0.377 | 19.691 | 0.643 | YES |
| W1 | guidance-policy / print_from_guide | 14 | 29.167 | 35.617 | 14.689 | 0.379 | 19.827 | 0.857 | YES |
| W1 | calibration-rail / gbm_surprise_guide | 10 | 32.293 | 36.766 | 12.646 | 0.339 | 25.357 | 0.300 | YES |
| W1 | kernel-lambda / revenue_level_next_q_last3_ex_covid | 14 | 38.507 | 52.207 | 0.256 | 0.555 | 30.931 | 0.643 | YES |
| W1 | kernel-lambda / revenue_level_next_q_ex_covid | 14 | 39.531 | 53.139 | 2.271 | 0.565 | 31.549 | 0.643 | YES |
| W1 | guidance-policy / print_kernel_policy | 14 | 52.704 | 72.006 | 37.287 | 0.766 | 45.156 | 1.000 | YES |
| W1 | kernel-lambda / revenue_level_next_q_last3 | 14 | 52.704 | 72.006 | 37.287 | 0.766 | 41.981 | 0.786 | YES |
| W1 | kernel-lambda / revenue_level_next_q | 14 | 61.096 | 78.127 | 59.023 | 0.831 | 45.557 | 0.786 | YES |
| W1 | baselines / naive | 14 | 75.093 | 94.031 | 12.777 | 1.000 | 57.858 | 0.929 | no |
| W1 | calibration-rail / gbm_revenue | 10 | 73.6 | 100.5 | 37.0 | 0.927 | 60.1 | 0.600 | YES |
| W1 | baselines / street | 14 | 87.7 | 100.9 | -68.3 | 1.073 | 58.4 | 0.786 | no |
| W1 | baselines / ar1 | 14 | 90.1 | 103.5 | -48.8 | 1.101 | 68.8 | 0.286 | no |
| W1 | kernel-lambda / revenue_level_h1 | 14 | 88.3 | 109.9 | 70.2 | 1.169 | 63.0 | 0.857 | no |
| W1 | kernel-lambda / revenue_level_next_q_w038 | 14 | 109.5 | 134.8 | 98.7 | 1.433 | 73.1 | 0.929 | no |
| W1 | kernel-lambda / revenue_level_next_q_w033 | 14 | 120.1 | 148.9 | 106.9 | 1.584 | 80.1 | 0.929 | no |
| W1 | baselines / trailing4 | 14 | 134.8 | 169.8 | 75.3 | 1.806 | 108.4 | 0.857 | no |
| W1 | baselines / naive_seasonal | 14 | 340.0 | 352.9 | -340.0 | 3.754 | 227.7 | 0.714 | no |
| W1 | l1-reconciliation / revenue_contemporaneous | 10 | 1,147.2 | 1,229.4 | 126.9 | 11.338 | 835.8 | 0.700 | no |
| W2 | baselines / guide_cushion | 10 | 30.895 | 34.596 | 8.728 | 0.319 | 20.404 | 0.600 | YES |
| W2 | guidance-policy / print_from_guide | 10 | 30.689 | 35.865 | 12.145 | 0.331 | 20.164 | 0.800 | YES |
| W2 | calibration-rail / gbm_surprise_guide | 10 | 32.293 | 36.766 | 12.646 | 0.339 | 25.357 | 0.300 | YES |
| W2 | kernel-lambda / revenue_level_next_q_last3_ex_covid | 10 | 36.165 | 51.189 | 5.857 | 0.472 | 30.030 | 0.700 | YES |
| W2 | kernel-lambda / revenue_level_next_q_ex_covid | 10 | 37.598 | 52.513 | 8.679 | 0.484 | 30.896 | 0.700 | YES |
| W2 | guidance-policy / print_kernel_policy | 10 | 49.053 | 70.187 | 27.470 | 0.647 | 43.898 | 1.000 | YES |
| W2 | kernel-lambda / revenue_level_next_q_last3 | 10 | 49.053 | 70.187 | 27.470 | 0.647 | 40.881 | 0.800 | YES |
| W2 | kernel-lambda / revenue_level_next_q | 10 | 60.801 | 78.821 | 57.900 | 0.727 | 45.888 | 0.800 | YES |
| W2 | baselines / street | 10 | 82.100 | 94.493 | -54.900 | 0.871 | 54.700 | 0.700 | no |
| W2 | kernel-lambda / revenue_level_h1 | 10 | 72.737 | 96.040 | 54.356 | 0.886 | 55.346 | 0.900 | no |
| W2 | calibration-rail / gbm_revenue | 10 | 73.6 | 100.5 | 37.0 | 0.927 | 60.1 | 0.600 | YES |
| W2 | baselines / naive | 10 | 91.5 | 108.4 | 4.2 | 1.000 | 64.4 | 0.900 | no |
| W2 | baselines / ar1 | 10 | 93.4 | 109.4 | -35.6 | 1.009 | 71.1 | 0.400 | no |
| W2 | baselines / trailing4 | 10 | 99.0 | 119.4 | 15.8 | 1.101 | 77.2 | 1.000 | no |
| W2 | kernel-lambda / revenue_level_next_q_w038 | 10 | 106.7 | 129.7 | 93.6 | 1.196 | 70.9 | 0.900 | no |
| W2 | kernel-lambda / revenue_level_next_q_w033 | 10 | 116.3 | 142.2 | 101.1 | 1.311 | 77.1 | 0.900 | no |
| W2 | baselines / naive_seasonal | 10 | 324.2 | 337.8 | -324.2 | 3.115 | 230.9 | 0.600 | no |
| W2 | l1-reconciliation / revenue_contemporaneous | 10 | 1,147.2 | 1,229.4 | 126.9 | 11.338 | 835.8 | 0.700 | no |


### revenue_musd — full-sample prior

| window | method / object | n | MAE | RMSE | bias | RMSE/naive | CRPS | cov80 | survives both |
|---|---|---:|---:|---:|---:|---:|---:|---:|:--:|
| W1 | guidance-policy / print_kernel_policy | 14 | 26.175 | 33.586 | -1.206 | 0.357 | 33.561 | 1.000 | YES |
| W1 | kernel-lambda / revenue_level_next_q_last3 | 14 | 26.175 | 33.586 | -1.206 | 0.357 | 25.550 | 1.000 | YES |
| W1 | kernel-lambda / revenue_level_next_q_last3_ex_covid | 14 | 26.175 | 33.586 | -1.206 | 0.357 | 20.184 | 0.857 | YES |
| W1 | baselines / guide_cushion | 14 | 28.495 | 35.252 | 13.530 | 0.375 | 17.762 | 0.786 | YES |
| W1 | guidance-policy / print_from_guide | 14 | 28.672 | 35.627 | 14.206 | 0.379 | 19.147 | 1.000 | YES |
| W1 | calibration-rail / gbm_surprise_guide | 14 | 31.356 | 36.419 | 4.605 | 0.387 | 26.295 | 0.214 | YES |
| W1 | kernel-lambda / revenue_level_next_q_ex_covid | 14 | 26.534 | 36.589 | 0.258 | 0.389 | 20.935 | 0.929 | YES |
| W1 | kernel-lambda / revenue_level_next_q | 14 | 38.497 | 50.108 | 31.818 | 0.533 | 31.071 | 0.929 | YES |
| W1 | calibration-rail / gbm_revenue | 14 | 52.978 | 73.037 | -9.395 | 0.777 | 41.043 | 0.429 | YES |
| W1 | kernel-lambda / revenue_level_next_q_w038 | 14 | 62.714 | 77.793 | 53.842 | 0.827 | 46.318 | 1.000 | YES |
| W1 | kernel-lambda / revenue_level_h1 | 14 | 64.935 | 80.818 | 42.618 | 0.859 | 48.039 | 0.857 | YES |
| W1 | baselines / ar1 | 14 | 64.055 | 84.618 | -5.079 | 0.900 | 47.003 | 0.714 | YES |
| W1 | kernel-lambda / revenue_level_next_q_w033 | 14 | 68.024 | 85.462 | 58.407 | 0.909 | 50.065 | 1.000 | YES |
| W1 | baselines / naive | 14 | 75.093 | 94.031 | 12.777 | 1.000 | 52.753 | 0.714 | no |
| W1 | baselines / street | 14 | 87.7 | 100.9 | -68.3 | 1.073 | 60.1 | 0.929 | no |
| W1 | baselines / trailing4 | 14 | 134.8 | 169.8 | 75.3 | 1.806 | 97.5 | 0.643 | no |
| W1 | baselines / naive_seasonal | 14 | 340.0 | 352.9 | -340.0 | 3.754 | 285.0 | 0.000 | no |
| W1 | l1-reconciliation / revenue_contemporaneous | 14 | 1,003.7 | 1,027.4 | -12.3 | 10.927 | 616.2 | 0.643 | no |
| W2 | guidance-policy / print_kernel_policy | 10 | 29.825 | 37.741 | 2.026 | 0.348 | 33.929 | 1.000 | YES |
| W2 | kernel-lambda / revenue_level_next_q_last3 | 10 | 29.825 | 37.741 | 2.026 | 0.348 | 27.743 | 1.000 | YES |
| W2 | kernel-lambda / revenue_level_next_q_last3_ex_covid | 10 | 29.825 | 37.741 | 2.026 | 0.348 | 23.064 | 0.800 | YES |
| W2 | baselines / guide_cushion | 10 | 31.221 | 38.876 | 17.769 | 0.359 | 19.593 | 0.700 | YES |
| W2 | guidance-policy / print_from_guide | 10 | 31.454 | 39.314 | 18.479 | 0.363 | 21.298 | 1.000 | YES |
| W2 | kernel-lambda / revenue_level_next_q_ex_covid | 10 | 31.356 | 40.678 | 4.481 | 0.375 | 24.055 | 0.900 | YES |
| W2 | calibration-rail / gbm_surprise_guide | 10 | 37.269 | 40.727 | 9.044 | 0.376 | 31.048 | 0.100 | YES |
| W2 | calibration-rail / gbm_revenue | 10 | 44.254 | 52.442 | -1.725 | 0.484 | 31.641 | 0.400 | YES |
| W2 | kernel-lambda / revenue_level_next_q | 10 | 45.388 | 57.124 | 37.979 | 0.527 | 34.985 | 0.900 | YES |
| W2 | kernel-lambda / revenue_level_h1 | 10 | 57.274 | 76.258 | 34.359 | 0.703 | 45.969 | 0.900 | YES |
| W2 | kernel-lambda / revenue_level_next_q_w038 | 10 | 74.853 | 88.017 | 62.433 | 0.812 | 51.667 | 1.000 | YES |
| W2 | baselines / street | 10 | 82.100 | 94.493 | -54.900 | 0.871 | 57.976 | 1.000 | no |
| W2 | kernel-lambda / revenue_level_next_q_w033 | 10 | 81.008 | 96.191 | 67.544 | 0.887 | 55.719 | 1.000 | YES |
| W2 | baselines / ar1 | 10 | 82.801 | 99.318 | -7.628 | 0.916 | 56.952 | 0.600 | YES |
| W2 | baselines / naive | 10 | 91.5 | 108.4 | 4.2 | 1.000 | 62.3 | 0.600 | no |
| W2 | baselines / trailing4 | 10 | 99.0 | 119.4 | 15.8 | 1.101 | 67.1 | 0.700 | no |
| W2 | baselines / naive_seasonal | 10 | 324.2 | 337.8 | -324.2 | 3.115 | 265.8 | 0.000 | no |
| W2 | l1-reconciliation / revenue_contemporaneous | 10 | 1,077.3 | 1,094.4 | 22.5 | 10.093 | 721.1 | 0.700 | no |



### revenue_yoy — PIT prior

| window | method / object | n | MAE | RMSE | bias | RMSE/naive | CRPS | cov80 | survives both |
|---|---|---:|---:|---:|---:|---:|---:|---:|:--:|
| W1 | kernel-lambda / revenue_yoy_next_q | 14 | 2.626 | 3.454 | 2.533 | 0.903 | 1.934 | 0.786 | YES |
| W1 | baselines / naive | 14 | 3.100 | 3.825 | 0.544 | 1.000 | 2.263 | 0.571 | no |
| W1 | baselines / ar1 | 14 | 3.839 | 4.351 | -2.221 | 1.138 | 2.988 | 0.286 | no |
| W1 | tracker-backlog / revenue_yoy_next_q | 112 | 4.405 | 6.236 | 1.723 | 1.630 | 3.105 | 0.768 | no |
| W1 | baselines / trailing4 | 14 | 6.162 | 8.784 | 3.843 | 2.297 | 5.295 | 0.786 | no |
| W1 | baselines / naive_seasonal | 14 | 14.139 | 14.722 | -14.139 | 3.849 | 12.482 | 0.000 | no |
| W2 | kernel-lambda / revenue_yoy_next_q | 10 | 2.389 | 3.242 | 2.258 | 0.756 | 1.817 | 0.800 | YES |
| W2 | baselines / naive | 10 | 3.587 | 4.289 | 0.008 | 1.000 | 2.577 | 0.600 | no |
| W2 | baselines / ar1 | 10 | 3.799 | 4.435 | -1.535 | 1.034 | 2.854 | 0.400 | no |
| W2 | baselines / trailing4 | 10 | 3.820 | 4.621 | 0.573 | 1.077 | 2.831 | 1.000 | no |
| W2 | tracker-backlog / revenue_yoy_next_q | 80 | 3.824 | 5.708 | 0.218 | 1.331 | 2.760 | 0.775 | no |
| W2 | baselines / naive_seasonal | 10 | 12.501 | 13.024 | -12.501 | 3.036 | 10.432 | 0.000 | no |


### revenue_yoy — full-sample prior

| window | method / object | n | MAE | RMSE | bias | RMSE/naive | CRPS | cov80 | survives both |
|---|---|---:|---:|---:|---:|---:|---:|---:|:--:|
| W1 | kernel-lambda / revenue_yoy_next_q | 14 | 1.597 | 2.107 | 1.275 | 0.551 | 1.277 | 0.929 | YES |
| W1 | baselines / ar1 | 14 | 2.616 | 3.428 | -0.249 | 0.896 | 1.896 | 0.714 | YES |
| W1 | baselines / naive | 14 | 3.100 | 3.825 | 0.544 | 1.000 | 2.147 | 0.714 | no |
| W1 | tracker-backlog / revenue_yoy_next_q | 112 | 3.377 | 4.710 | 1.318 | 1.231 | 2.337 | 0.857 | no |
| W1 | baselines / trailing4 | 14 | 6.162 | 8.784 | 3.843 | 2.297 | 4.662 | 0.643 | no |
| W1 | baselines / naive_seasonal | 14 | 14.139 | 14.722 | -14.139 | 3.849 | 11.926 | 0.000 | no |
| W2 | kernel-lambda / revenue_yoy_next_q | 10 | 1.812 | 2.368 | 1.429 | 0.552 | 1.377 | 0.900 | YES |
| W2 | baselines / ar1 | 10 | 3.333 | 4.010 | -0.451 | 0.935 | 2.252 | 0.600 | YES |
| W2 | baselines / naive | 10 | 3.587 | 4.289 | 0.008 | 1.000 | 2.435 | 0.600 | no |
| W2 | baselines / trailing4 | 10 | 3.820 | 4.621 | 0.573 | 1.077 | 2.595 | 0.700 | no |
| W2 | tracker-backlog / revenue_yoy_next_q | 80 | 3.311 | 4.835 | 0.687 | 1.127 | 2.368 | 0.850 | no |
| W2 | baselines / naive_seasonal | 10 | 12.501 | 13.024 | -12.501 | 3.036 | 10.290 | 0.000 | no |



### guide_mid — PIT prior

| window | method / object | n | MAE | RMSE | bias | RMSE/naive | CRPS | cov80 | survives both |
|---|---|---:|---:|---:|---:|---:|---:|---:|:--:|
| W1 | guidance-policy / guide_mid_next_q | 14 | 51.241 | 63.604 | 21.933 | n/a | 43.268 | 1.000 | no |
| W2 | guidance-policy / guide_mid_next_q | 10 | 47.647 | 58.797 | 14.909 | n/a | 41.113 | 1.000 | no |


### guide_mid — full-sample prior

| window | method / object | n | MAE | RMSE | bias | RMSE/naive | CRPS | cov80 | survives both |
|---|---|---:|---:|---:|---:|---:|---:|---:|:--:|
| W1 | guidance-policy / guide_mid_next_q | 14 | 33.122 | 37.233 | -15.030 | n/a | 36.147 | 1.000 | no |
| W2 | guidance-policy / guide_mid_next_q | 10 | 31.727 | 35.800 | -16.045 | n/a | 35.434 | 1.000 | no |



### nights_yoy — PIT prior

| window | method / object | n | MAE | RMSE | bias | RMSE/naive | CRPS | cov80 | survives both |
|---|---|---:|---:|---:|---:|---:|---:|---:|:--:|
| W1 | calibration-rail / ref_naive | 14 | 2.128 | 2.877 | 0.702 | 1.000 \* | 1.736 | 0.714 | no |
| W1 | tracker-backlog / nights_yoy_next_q | 112 | 3.676 | 5.034 | 1.627 | 1.750 \* | 2.747 | 0.964 | no |
| W1 | calibration-rail / ref_trailing4 | 14 | 3.775 | 5.341 | 2.978 | 1.857 \* | 3.232 | 0.786 | no |
| W1 | calibration-rail / ref_ar1 | 14 | 4.943 | 6.673 | 4.783 | 2.320 \* | 4.058 | 0.500 | no |
| W2 | calibration-rail / ref_naive | 10 | 1.656 | 2.159 | 0.168 | 1.000 \* | 1.280 | 0.900 | no |
| W2 | calibration-rail / ref_trailing4 | 10 | 1.916 | 2.237 | 0.801 | 1.036 \* | 1.484 | 1.000 | no |
| W2 | calibration-rail / ref_ar1 | 10 | 2.878 | 3.624 | 2.654 | 1.678 \* | 2.030 | 0.700 | no |
| W2 | tracker-backlog / nights_yoy_next_q | 80 | 3.385 | 4.785 | 0.652 | 2.216 \* | 2.526 | 0.950 | no |

\* no `baselines__naive` row exists for `nights_yoy`; ratio shown is against the locally built denominator (calibration-rail ref_naive), RMSE W1 2.8767 / W2 2.1593. It is NOT the harness ratio.


### nights_yoy — full-sample prior

| window | method / object | n | MAE | RMSE | bias | RMSE/naive | CRPS | cov80 | survives both |
|---|---|---:|---:|---:|---:|---:|---:|---:|:--:|
| W1 | calibration-rail / ref_ar1 | 14 | 2.138 | 2.769 | 1.583 | 0.963 \* | 1.545 | 0.786 | no |
| W1 | calibration-rail / ref_naive | 14 | 2.128 | 2.877 | 0.702 | 1.000 \* | 1.546 | 0.786 | no |
| W1 | tracker-backlog / nights_yoy_next_q | 112 | 2.845 | 3.892 | 1.023 | 1.353 \* | 2.089 | 0.955 | no |
| W1 | calibration-rail / ref_trailing4 | 14 | 3.775 | 5.341 | 2.978 | 1.857 \* | 2.917 | 0.643 | no |
| W2 | calibration-rail / ref_naive | 10 | 1.656 | 2.159 | 0.168 | 1.000 \* | 1.203 | 0.800 | no |
| W2 | calibration-rail / ref_trailing4 | 10 | 1.916 | 2.237 | 0.801 | 1.036 \* | 1.266 | 0.900 | no |
| W2 | calibration-rail / ref_ar1 | 10 | 1.970 | 2.396 | 1.513 | 1.110 \* | 1.366 | 0.800 | no |
| W2 | tracker-backlog / nights_yoy_next_q | 80 | 2.899 | 4.063 | 0.806 | 1.882 \* | 2.129 | 0.950 | no |

\* no `baselines__naive` row exists for `nights_yoy`; ratio shown is against the locally built denominator (calibration-rail ref_naive), RMSE W1 2.8767 / W2 2.1593. It is NOT the harness ratio.



### nights_m — PIT prior

| window | method / object | n | MAE | RMSE | bias | RMSE/naive | CRPS | cov80 | survives both |
|---|---|---:|---:|---:|---:|---:|---:|---:|:--:|
| W1 | baselines / naive | 14 | 2.375 | 3.167 | 0.837 | 1.000 | 2.235 | 1.000 | no |
| W1 | baselines / trailing4 | 14 | 4.053 | 5.562 | 3.133 | 1.756 | 3.322 | 0.786 | no |
| W1 | baselines / ar1 | 14 | 5.416 | 7.123 | 5.258 | 2.249 | 4.267 | 0.429 | no |
| W1 | baselines / naive_seasonal | 14 | 11.879 | 12.118 | -11.879 | 3.827 | 7.716 | 0.714 | no |
| W2 | baselines / naive | 10 | 1.988 | 2.593 | 0.342 | 1.000 | 1.921 | 1.000 | no |
| W2 | baselines / trailing4 | 10 | 2.282 | 2.644 | 0.994 | 1.020 | 1.907 | 1.000 | no |
| W2 | baselines / ar1 | 10 | 3.532 | 4.487 | 3.311 | 1.730 | 2.564 | 0.600 | no |
| W2 | baselines / naive_seasonal | 10 | 11.180 | 11.271 | -11.180 | 4.346 | 7.642 | 0.600 | no |


### nights_m — full-sample prior

| window | method / object | n | MAE | RMSE | bias | RMSE/naive | CRPS | cov80 | survives both |
|---|---|---:|---:|---:|---:|---:|---:|---:|:--:|
| W1 | baselines / naive | 14 | 2.375 | 3.167 | 0.837 | 1.000 | 1.722 | 0.786 | no |
| W1 | baselines / ar1 | 14 | 2.459 | 3.195 | 1.908 | 1.009 | 1.774 | 0.786 | no |
| W1 | baselines / trailing4 | 14 | 4.053 | 5.562 | 3.133 | 1.756 | 3.081 | 0.643 | no |
| W1 | baselines / naive_seasonal | 14 | 11.879 | 12.118 | -11.879 | 3.827 | 10.656 | 0.000 | no |
| W2 | baselines / naive | 10 | 1.988 | 2.593 | 0.342 | 1.000 | 1.440 | 0.800 | no |
| W2 | baselines / trailing4 | 10 | 2.282 | 2.644 | 0.994 | 1.020 | 1.505 | 0.900 | no |
| W2 | baselines / ar1 | 10 | 2.416 | 3.007 | 1.964 | 1.159 | 1.681 | 0.800 | no |
| W2 | baselines / naive_seasonal | 10 | 11.180 | 11.271 | -11.180 | 4.346 | 9.887 | 0.000 | no |



### gbv_musd — PIT prior

| window | method / object | n | MAE | RMSE | bias | RMSE/naive | CRPS | cov80 | survives both |
|---|---|---:|---:|---:|---:|---:|---:|---:|:--:|
| W1 | baselines / naive | 14 | 626.5 | 722.0 | 64.0 | 1.000 | 506.4 | 1.000 | no |
| W1 | baselines / ar1 | 14 | 922.2 | 1,200.0 | 736.3 | 1.662 | 710.0 | 0.500 | no |
| W1 | baselines / trailing4 | 14 | 909.6 | 1,204.7 | 359.8 | 1.668 | 734.7 | 0.786 | no |
| W1 | baselines / naive_seasonal | 14 | 2,600.0 | 2,719.8 | -2,600.0 | 3.767 | 1,817.3 | 0.643 | no |
| W2 | baselines / naive | 10 | 645.0 | 737.3 | 12.2 | 1.000 | 487.3 | 1.000 | no |
| W2 | baselines / trailing4 | 10 | 697.8 | 837.9 | -72.0 | 1.136 | 546.1 | 0.900 | no |
| W2 | baselines / ar1 | 10 | 707.9 | 903.5 | 447.7 | 1.225 | 498.3 | 0.600 | no |
| W2 | baselines / naive_seasonal | 10 | 2,640.0 | 2,786.0 | -2,640.0 | 3.779 | 1,961.1 | 0.500 | no |


### gbv_musd — full-sample prior

| window | method / object | n | MAE | RMSE | bias | RMSE/naive | CRPS | cov80 | survives both |
|---|---|---:|---:|---:|---:|---:|---:|---:|:--:|
| W1 | baselines / ar1 | 14 | 554.3 | 709.3 | 294.0 | 0.982 | 382.9 | 0.857 | no |
| W1 | baselines / naive | 14 | 626.5 | 722.0 | 64.0 | 1.000 | 401.5 | 0.786 | no |
| W1 | baselines / trailing4 | 14 | 909.6 | 1,204.7 | 359.8 | 1.668 | 659.3 | 0.786 | no |
| W1 | baselines / naive_seasonal | 14 | 2,600.0 | 2,719.8 | -2,600.0 | 3.767 | 2,232.0 | 0.000 | no |
| W2 | baselines / naive | 10 | 645.0 | 737.3 | 12.2 | 1.000 | 407.6 | 0.900 | no |
| W2 | baselines / ar1 | 10 | 574.2 | 744.5 | 312.1 | 1.010 | 397.4 | 0.900 | no |
| W2 | baselines / trailing4 | 10 | 697.8 | 837.9 | -72.0 | 1.136 | 463.7 | 0.900 | no |
| W2 | baselines / naive_seasonal | 10 | 2,640.0 | 2,786.0 | -2,640.0 | 3.779 | 2,247.3 | 0.000 | no |



### gbv_yoy — PIT prior

| window | method / object | n | MAE | RMSE | bias | RMSE/naive | CRPS | cov80 | survives both |
|---|---|---:|---:|---:|---:|---:|---:|---:|:--:|
| W1 | calibration-rail / ref_naive | 14 | 3.247 | 3.662 | 0.266 | 1.000 \* | 2.307 | 0.786 | no |
| W1 | calibration-rail / ref_ar1 | 14 | 4.949 | 6.575 | 4.074 | 1.795 \* | 3.967 | 0.429 | no |
| W1 | calibration-rail / ref_trailing4 | 14 | 4.861 | 6.583 | 2.243 | 1.797 \* | 3.968 | 0.786 | no |
| W2 | calibration-rail / ref_naive | 10 | 3.089 | 3.423 | -0.093 | 1.000 \* | 1.991 | 0.900 | no |
| W2 | calibration-rail / ref_trailing4 | 10 | 3.371 | 3.881 | -0.295 | 1.134 \* | 2.295 | 1.000 | no |
| W2 | calibration-rail / ref_ar1 | 10 | 3.366 | 4.215 | 2.140 | 1.231 \* | 2.398 | 0.600 | no |

\* no `baselines__naive` row exists for `gbv_yoy`; ratio shown is against the locally built denominator (calibration-rail ref_naive), RMSE W1 3.6624 / W2 3.4234. It is NOT the harness ratio.


### gbv_yoy — full-sample prior

| window | method / object | n | MAE | RMSE | bias | RMSE/naive | CRPS | cov80 | survives both |
|---|---|---:|---:|---:|---:|---:|---:|---:|:--:|
| W1 | calibration-rail / ref_ar1 | 14 | 2.843 | 3.495 | 1.474 | 0.954 \* | 1.967 | 0.857 | no |
| W1 | calibration-rail / ref_naive | 14 | 3.247 | 3.662 | 0.266 | 1.000 \* | 2.088 | 0.786 | no |
| W1 | calibration-rail / ref_trailing4 | 14 | 4.861 | 6.583 | 2.243 | 1.797 \* | 3.582 | 0.786 | no |
| W2 | calibration-rail / ref_ar1 | 10 | 2.710 | 3.386 | 1.449 | 0.989 \* | 1.886 | 0.900 | no |
| W2 | calibration-rail / ref_naive | 10 | 3.089 | 3.423 | -0.093 | 1.000 \* | 1.958 | 0.900 | no |
| W2 | calibration-rail / ref_trailing4 | 10 | 3.371 | 3.881 | -0.295 | 1.134 \* | 2.222 | 0.900 | no |

\* no `baselines__naive` row exists for `gbv_yoy`; ratio shown is against the locally built denominator (calibration-rail ref_naive), RMSE W1 3.6624 / W2 3.4234. It is NOT the harness ratio.



### adr_yoy — PIT prior

| window | method / object | n | MAE | RMSE | bias | RMSE/naive | CRPS | cov80 | survives both |
|---|---|---:|---:|---:|---:|---:|---:|---:|:--:|
| W1 | calibration-rail / ref_ar1 | 14 | 1.475 | 1.880 | -0.345 | 0.972 \* | 1.076 | 0.500 | no |
| W1 | calibration-rail / ref_naive | 14 | 1.539 | 1.934 | -0.416 | 1.000 \* | 1.088 | 0.643 | no |
| W1 | calibration-rail / ref_trailing4 | 14 | 1.999 | 2.540 | -0.791 | 1.313 \* | 1.466 | 0.571 | no |
| W2 | calibration-rail / ref_ar1 | 10 | 1.773 | 2.156 | -0.518 | 0.995 \* | 1.311 | 0.300 | no |
| W2 | calibration-rail / ref_naive | 10 | 1.727 | 2.168 | -0.274 | 1.000 \* | 1.255 | 0.600 | no |
| W2 | calibration-rail / ref_trailing4 | 10 | 2.217 | 2.810 | -1.053 | 1.296 \* | 1.637 | 0.600 | no |

\* no `baselines__naive` row exists for `adr_yoy`; ratio shown is against the locally built denominator (calibration-rail ref_naive), RMSE W1 1.9344 / W2 2.1675. It is NOT the harness ratio.


### adr_yoy — full-sample prior

| window | method / object | n | MAE | RMSE | bias | RMSE/naive | CRPS | cov80 | survives both |
|---|---|---:|---:|---:|---:|---:|---:|---:|:--:|
| W1 | calibration-rail / ref_ar1 | 14 | 1.441 | 1.785 | -0.078 | 0.923 \* | 0.992 | 0.857 | no |
| W1 | calibration-rail / ref_naive | 14 | 1.539 | 1.934 | -0.416 | 1.000 \* | 1.084 | 0.786 | no |
| W1 | calibration-rail / ref_trailing4 | 14 | 1.999 | 2.540 | -0.791 | 1.313 \* | 1.404 | 0.786 | no |
| W2 | calibration-rail / ref_ar1 | 10 | 1.735 | 2.056 | -0.213 | 0.949 \* | 1.151 | 0.800 | no |
| W2 | calibration-rail / ref_naive | 10 | 1.727 | 2.168 | -0.274 | 1.000 \* | 1.219 | 0.700 | no |
| W2 | calibration-rail / ref_trailing4 | 10 | 2.217 | 2.810 | -1.053 | 1.296 \* | 1.576 | 0.700 | no |

\* no `baselines__naive` row exists for `adr_yoy`; ratio shown is against the locally built denominator (calibration-rail ref_naive), RMSE W1 1.9344 / W2 2.1675. It is NOT the harness ratio.



### take_rate_pct — PIT prior

| window | method / object | n | MAE | RMSE | bias | RMSE/naive | CRPS | cov80 | survives both |
|---|---|---:|---:|---:|---:|---:|---:|---:|:--:|
| W1 | fee-takerate / take_rate_lastyear | 14 | 0.279 | 0.326 | 0.139 | 1.003 \* | 0.191 | 0.714 | no |
| W1 | fee-takerate / take_rate_kernel | 14 | 0.343 | 0.436 | 0.282 | 1.342 \* | 0.247 | 0.643 | no |
| W1 | calibration-rail / ref_trailing4 | 14 | 2.465 | 3.205 | 0.352 | 9.857 \* | 1.804 | 0.786 | no |
| W1 | calibration-rail / ref_ar1 | 14 | 2.521 | 3.356 | -0.061 | 10.321 \* | 1.879 | 0.786 | no |
| W1 | calibration-rail / ref_naive | 14 | 4.569 | 4.606 | 0.059 | 14.166 \* | 2.670 | 1.000 | no |
| W2 | fee-takerate / take_rate_lastyear | 10 | 0.297 | 0.335 | 0.102 | 1.055 \* | 0.195 | 0.600 | no |
| W2 | fee-takerate / take_rate_kernel | 10 | 0.345 | 0.413 | 0.291 | 1.299 \* | 0.239 | 0.600 | no |
| W2 | calibration-rail / ref_trailing4 | 10 | 2.392 | 3.136 | 0.554 | 9.866 \* | 1.754 | 0.800 | no |
| W2 | calibration-rail / ref_ar1 | 10 | 2.398 | 3.236 | 0.180 | 10.181 \* | 1.799 | 0.800 | no |
| W2 | calibration-rail / ref_naive | 10 | 4.489 | 4.522 | 0.105 | 14.227 \* | 2.624 | 1.000 | no |

\* no `baselines__naive` row exists for `take_rate_pct`; ratio shown is against the locally built denominator (fee-takerate seasonal naive tau[q-4]), RMSE W1 0.3251 / W2 0.3178. It is NOT the harness ratio.


### take_rate_pct — full-sample prior

| window | method / object | n | MAE | RMSE | bias | RMSE/naive | CRPS | cov80 | survives both |
|---|---|---:|---:|---:|---:|---:|---:|---:|:--:|
| W1 | fee-takerate / take_rate_lastyear | 14 | 0.288 | 0.376 | 0.190 | 1.158 \* | 0.206 | 0.857 | no |
| W1 | fee-takerate / take_rate_kernel | 14 | 0.336 | 0.401 | 0.154 | 1.234 \* | 0.227 | 0.786 | no |
| W1 | calibration-rail / ref_trailing4 | 14 | 2.465 | 3.205 | 0.352 | 9.857 \* | 1.793 | 0.571 | no |
| W1 | calibration-rail / ref_ar1 | 14 | 2.479 | 3.235 | -0.019 | 9.951 \* | 1.809 | 0.714 | no |
| W1 | calibration-rail / ref_naive | 14 | 4.569 | 4.606 | 0.059 | 14.166 \* | 2.687 | 1.000 | no |
| W2 | fee-takerate / take_rate_kernel | 10 | 0.327 | 0.375 | 0.205 | 1.181 \* | 0.213 | 0.800 | no |
| W2 | fee-takerate / take_rate_lastyear | 10 | 0.339 | 0.422 | 0.291 | 1.327 \* | 0.236 | 0.800 | no |
| W2 | calibration-rail / ref_trailing4 | 10 | 2.392 | 3.136 | 0.554 | 9.866 \* | 1.748 | 0.600 | no |
| W2 | calibration-rail / ref_ar1 | 10 | 2.368 | 3.137 | 0.143 | 9.869 \* | 1.750 | 0.800 | no |
| W2 | calibration-rail / ref_naive | 10 | 4.489 | 4.522 | 0.105 | 14.227 \* | 2.635 | 1.000 | no |

\* no `baselines__naive` row exists for `take_rate_pct`; ratio shown is against the locally built denominator (fee-takerate seasonal naive tau[q-4]), RMSE W1 0.3251 / W2 0.3178. It is NOT the harness ratio.



### fx_pts_revenue — PIT prior

| window | method / object | n | MAE | RMSE | bias | RMSE/naive | CRPS | cov80 | survives both |
|---|---|---:|---:|---:|---:|---:|---:|---:|:--:|
| W1 | fx-lag / fx_rev_next_q_h2 | 10 | 0.898 | 0.994 | 0.097 | n/a | 0.672 | 1.000 | no |
| W1 | fx-lag / fx_rev_next_q_h3 | 14 | 1.186 | 1.485 | 0.432 | n/a | 0.869 | 0.500 | no |
| W2 | fx-lag / fx_rev_next_q_h2 | 10 | 0.898 | 0.994 | 0.097 | n/a | 0.672 | 1.000 | no |
| W2 | fx-lag / fx_rev_next_q_h3 | 10 | 1.398 | 1.697 | 0.453 | n/a | 1.054 | 0.400 | no |


### fx_pts_revenue — full-sample prior

| window | method / object | n | MAE | RMSE | bias | RMSE/naive | CRPS | cov80 | survives both |
|---|---|---:|---:|---:|---:|---:|---:|---:|:--:|
| W1 | fx-lag / fx_rev_next_q_h2 | 10 | 0.866 | 0.990 | -0.019 | n/a | 0.610 | 1.000 | no |
| W1 | fx-lag / fx_rev_next_q_h3 | 14 | 0.864 | 1.000 | 0.026 | n/a | 0.565 | 0.857 | no |
| W2 | fx-lag / fx_rev_next_q_h3 | 10 | 0.723 | 0.824 | 0.191 | n/a | 0.468 | 0.900 | no |
| W2 | fx-lag / fx_rev_next_q_h2 | 10 | 0.866 | 0.990 | -0.019 | n/a | 0.610 | 1.000 | no |



---

## 2. Supplement — tracker-backlog scored per spec_id

The harness groups on `(method, object, target, window, prior_basis)` and **not** on
`spec_id`. tracker-backlog registers 8 specs inside one object, so its two shared-scoreboard
rows pool 8 forecasts per quarter (n=112 on W1, n=80 on W2) and the pooled RMSE is
meaningless as a method score. This is the package's own open harness change request.
I re-ran the harness's own `score_registry()` on a copy of the frame with
`object := object + "::" + spec_id` — no harness file was edited — and wrote the result to
`data/processed/forecast_methods/harness/scoreboard_tracker_backlog_by_spec.csv`.

**revenue_yoy** (PIT prior)

| window | spec_id | n | MAE | RMSE | bias | RMSE/naive | CRPS | cov80 |
|---|---|---:|---:|---:|---:|---:|---:|---:|
| W1 | unearned_rnpl_scenario_k1.0 | 14 | 1.902 | 2.601 | 1.146 | 0.680 | 1.416 | 0.929 |
| W1 | unearned_rnpl_scenario_k1.5 | 14 | 2.303 | 2.975 | 1.872 | 0.778 | 1.638 | 0.857 |
| W1 | unearned_rnpl_scenario_k0.5 | 14 | 2.468 | 3.262 | 0.429 | 0.853 | 1.780 | 0.786 |
| W1 | unearned_raw | 14 | 3.170 | 4.479 | -0.273 | 1.171 | 2.399 | 0.786 |
| W1 | funds_raw | 14 | 4.949 | 6.467 | 0.867 | 1.691 | 3.457 | 0.786 |
| W1 | funds_rnpl_scenario_k0.5 | 14 | 5.633 | 6.891 | 2.066 | 1.802 | 3.736 | 0.714 |
| W1 | funds_rnpl_scenario_k1.0 | 14 | 6.828 | 8.336 | 3.261 | 2.180 | 4.697 | 0.643 |
| W1 | funds_rnpl_scenario_k1.5 | 14 | 7.986 | 10.293 | 4.419 | 2.691 | 5.718 | 0.643 |
| W2 | unearned_rnpl_scenario_k1.0 | 10 | 1.733 | 2.542 | 0.970 | 0.593 | 1.348 | 0.900 |
| W2 | unearned_rnpl_scenario_k1.5 | 10 | 2.294 | 3.062 | 1.987 | 0.714 | 1.659 | 0.800 |
| W2 | unearned_rnpl_scenario_k0.5 | 10 | 2.525 | 3.447 | -0.033 | 0.804 | 1.857 | 0.700 |
| W2 | funds_raw | 10 | 3.173 | 4.225 | -2.542 | 0.985 | 2.301 | 0.900 |
| W2 | unearned_raw | 10 | 3.507 | 5.008 | -1.016 | 1.167 | 2.725 | 0.700 |
| W2 | funds_rnpl_scenario_k0.5 | 10 | 4.130 | 5.078 | -0.863 | 1.184 | 2.691 | 0.800 |
| W2 | funds_rnpl_scenario_k1.0 | 10 | 5.804 | 7.522 | 0.810 | 1.754 | 4.037 | 0.700 |
| W2 | funds_rnpl_scenario_k1.5 | 10 | 7.426 | 10.375 | 2.432 | 2.419 | 5.465 | 0.700 |

**nights_yoy** (PIT prior)

| window | spec_id | n | MAE | RMSE | bias | RMSE/naive | CRPS | cov80 |
|---|---|---:|---:|---:|---:|---:|---:|---:|
| W1 | unearned_rnpl_scenario_k0.5 | 14 | 1.683 | 2.157 | 0.609 | 0.750 \* | 1.675 | 1.000 |
| W1 | unearned_rnpl_scenario_k1.0 | 14 | 1.837 | 2.293 | 1.102 | 0.797 \* | 1.737 | 1.000 |
| W1 | unearned_raw | 14 | 2.060 | 2.602 | 0.123 | 0.904 \* | 1.826 | 1.000 |
| W1 | unearned_rnpl_scenario_k1.5 | 14 | 2.335 | 2.950 | 1.600 | 1.025 \* | 1.938 | 1.000 |
| W1 | funds_raw | 14 | 4.341 | 5.269 | 1.220 | 1.832 \* | 3.042 | 1.000 |
| W1 | funds_rnpl_scenario_k0.5 | 14 | 4.945 | 5.861 | 2.013 | 2.038 \* | 3.286 | 1.000 |
| W1 | funds_rnpl_scenario_k1.0 | 14 | 5.728 | 6.922 | 2.797 | 2.406 \* | 3.903 | 0.857 |
| W1 | funds_rnpl_scenario_k1.5 | 14 | 6.481 | 8.204 | 3.549 | 2.852 \* | 4.568 | 0.857 |
| W2 | unearned_rnpl_scenario_k0.5 | 10 | 1.572 | 1.890 | 0.341 | 0.875 \* | 1.472 | 1.000 |
| W2 | unearned_rnpl_scenario_k1.0 | 10 | 1.787 | 2.101 | 1.032 | 0.973 \* | 1.558 | 1.000 |
| W2 | unearned_raw | 10 | 2.099 | 2.555 | -0.339 | 1.183 \* | 1.683 | 1.000 |
| W2 | unearned_rnpl_scenario_k1.5 | 10 | 2.484 | 3.039 | 1.728 | 1.407 \* | 1.840 | 1.000 |
| W2 | funds_raw | 10 | 3.339 | 4.080 | -1.031 | 1.890 \* | 2.493 | 1.000 |
| W2 | funds_rnpl_scenario_k0.5 | 10 | 4.183 | 5.087 | 0.080 | 2.356 \* | 2.834 | 1.000 |
| W2 | funds_rnpl_scenario_k1.0 | 10 | 5.280 | 6.698 | 1.177 | 3.102 \* | 3.698 | 0.800 |
| W2 | funds_rnpl_scenario_k1.5 | 10 | 6.334 | 8.486 | 2.230 | 3.930 \* | 4.629 | 0.800 |

---

## 3. What each package actually established

Verifier status is carried from the package outcomes: six packages `pass`, one
(`calibration-rail`) `partial`. Anything the verifier left open, or an acceptance test the
package itself records as FAILED, is marked below.

### harness (format v1.0, frozen 2026-09-11)

Established: a single frozen registry format, a point-in-time spine (`calendar.csv`,
`targets.csv`, `windows.csv`), 6 baseline objects, and a scorer that runs the whole registry
to exit 0. W1 = 14 guide dates, targets 2023Q1-2026Q2; W2 = 10, targets 2024Q1-2026Q2;
2026-08-06 is LIVE and scores in nothing. The validator rejects a forecast whose
`vintage_date` is on or after the target's print date and refuses a Street value whose
`as_of` postdates the vintage date, which is how the "no September vendor as the 6-Aug
pre-guide Street" rule is enforced mechanically rather than by good intentions.

Limits that shaped every table above: naive/AR(1)/trailing-4 exist for four targets only
(`revenue_musd`, `revenue_yoy`, `gbv_musd`, `nights_m`); `guide_cushion` and `street` for
revenue only; `spec_id` is not a grouping key; `LIVE` admits 2026Q3 only; there is no annual
target slot for FY27.

### kernel-lambda — verification pass

* The acceptance table reproduces: all 12 architect conversion cells to 2 dp, max abs diff
  0.0005pp, Q4 within-season range 0.171pp. Extra usable cells 1Q23 12.803, 2Q23 13.724.
* **Backtest, recomputed here.** Published w=2/3 spec (`revenue_level_next_q`): W1 PIT RMSE
  78.13 musd, ratio 0.831, bias +59.0 musd; W2 PIT RMSE 78.82, ratio 0.727. Survives both.
  The ex-COVID estimation window is materially better and is what the memo should use:
  `revenue_level_next_q_ex_covid` ratio 0.565 / 0.484, bias +2.3 / +8.7 musd.
* **Calibration is the real result.** The published spec's PIT is rejected on W1
  (KS p 0.0027) and marginal on W2 (0.0298); the ex-COVID variant is clean (0.631 / 0.742).
  A w=2/3 kernel fitted through the COVID lambda cells is biased high, not just noisy.
* **The low-weight variants fail under PIT replay.** w=0.38 ratio 1.433 / 1.196 and w=0.33
  1.584 / 1.311 — both fail W1 and W2. The package states plainly, and I agree, that this is
  an artefact of COVID quarters in the early expanding windows and is **not** independent
  evidence for 2/3. The honest statement remains: the weight is not identified better than
  about +/-0.2, and on 4Q26 the whole 0.20-0.80 range moves the print by 13 musd (0.42%).
* **Two acceptance tests FAILED and are reported as failures.** (i) The pre-registered
  phi_0 ~ 0 test: phi_0 is 0.225-0.405 across three windows with bootstrap CIs excluding
  0.02, and the free fit wins leave-one-quarter-out in all three, so the memo must say
  "most", not "all", of the quarter is already booked. (ii) The quoted walk-forward triple
  MAE 1.74 / RMSE 2.44 / bias +0.99 does not reproduce as a strict PIT replay (strict PIT is
  2.313 / 3.066 / +2.230); it reads as full-sample.
* `revenue_level_h1` (two quarters out) fails W1 at ratio 1.169 and does not survive.
  Published as a negative.
* Beats naive, AR(1), trailing-4 and the vintage-stamped pre-guide Street on both windows;
  **loses to guide+cushion** (0.565 vs 0.377 on W1 PIT). Said first: once management has
  guided, guide+cushion is the better forecast. The kernel earns its place only at the
  pitch date, when no 4Q26 guide exists and the cushion baseline is undefined.

### guidance-policy — verification pass

* `print_from_guide` is the best registered non-baseline object on revenue level:
  W1 PIT RMSE 35.62 musd, ratio 0.3788; W2 35.86, ratio 0.3308; survives both; **1 free
  parameter**. In percent terms MAE 1.01% / 1.03%. It is a one-parameter restatement of the
  cushion, and it is within 0.5 musd of the `guide_cushion` baseline itself (35.46 / 34.60) —
  which is the point, not a defect: the cushion is the edge, and it is nearly free.
* `print_kernel_policy` ratio 0.766 / 0.647, 5 params. Survives both, clearly worse than the
  guide route, and the two are the same object once a guide exists.
* `guide_mid_next_q`: no harness naive denominator exists for `guide_mid`. Against the
  package's own local comparators (`07_backtest_scores.csv`) it is 0.869 of local naive on
  W1 and 1.049 on W2 — **fails the survives-both rule and may not be quoted as beating
  naive**. Against the vintage-stamped pre-guide Street it loses on both windows:
  MAE 1.986% vs 1.966% (W1 PIT) and 1.762% vs 1.609% (W2 PIT).
* **Gate G4 FAILS on both windows**: 7 of 14 on W1 PIT (one-sided p 0.605) and 4 of 10 on
  W2 (p 0.828). There is no measured edge over the pre-guide Street on the level or the sign
  of the next guide midpoint. This is disclosed, not softened.
* The 9/9 guide-below-Street drift rule is dead as a signal: executable from the reaction
  close it is 8 of 9, spread -1.50pp, Fisher p 0.141, and 9 of 11 of all prints in
  2022Q3-2025Q1 were negative regardless of guide sign. Base rate only, with the returns.
* Predictive sd for 4Q26 is **3.03pp**, not the 2.6pp in the decisions document, because the
  measured walk-forward kernel PIT RMSE is 2.86pp not the assumed 2.44pp. Not forced back.

### fx-lag — verification pass, four verifier items still open

Scored objects carry no naive denominator (`fx_pts_revenue` has no baseline), so the
harness ratio column is empty by construction. On its own PIT window scores
(`09c_pit_window_scores.csv`): H2 RMSE 0.9936 on both windows; H3 1.485 (W1) / 1.697 (W2);
the zero baseline is 2.268 and the last-value baseline 2.111 on the same target. The full
hypothesis answer is section 4.

Open failures, unchanged and not papered over: the repo's `05_fx_fits.csv` rev_fx rows do
not reproduce (repo n 13 against 14 non-null points; slope -0.5348 against -0.5023); the
architect's Object-C slope does not reproduce on any of eight conventions (0.389 against
0.158, though n=12, se 0.277 against 0.275, and the |t|<2 conclusion all do); H2 covers only
10 of 14 W1 quarters because its ADR-FX driver starts 2Q22, so **its W1 and W2 rows are the
same ten quarters and its "survives both windows" is not a real two-window test**; and the
harness cannot register a LIVE object past 2026Q3.

The one programme-wide caveat worth repeating: the fitted basket scale is 0.95 against a
disclosed non-USD revenue share of 0.56, i.e. the judgemental currency weights understate
exposure by roughly 70%. Anyone using this basket for a LEVEL rather than a change must
rebuild the weights from booking-currency data first.

### fee-takerate — verification pass

* **Nothing in this package's backtest is a forecasting win, and that is the finding.**
  Recomputed from `06c`/`06d`: `take_rate_lastyear` W1 PIT RMSE 0.3262 against a locally
  built seasonal naive tau[q-4] of 0.3251 (ratio 1.003) and W2 0.3354 against 0.3178
  (ratio 1.055); `take_rate_kernel` 1.342 / 1.299. **0 of 8 scored rows beat the seasonal
  naive**; `survives_both_windows` is False on all eight. The printed take rate is an OUTPUT
  with no forecasting lever.
* The harness reports `rmse_ratio_to_naive` as **NaN on every fee-takerate row** because no
  `take_rate_pct` baseline is registered at all. NaN here means NO DENOMINATOR, not a win.
* theta is declared **unidentified** in Inside Airbnb, not measured: 0.833-1.407 across 402
  rows and 34 markets, with 0.833-0.845 only the Austin sub-sample. Migrated-cohort uplift is
  carried as +1.1% to +1.8% of revenue; +4.05% is the theta=1 upper bound and is labelled.
* Acceptance test A5 **FAILED, deliberately and on the record**: on the full 420-row file
  more listings RAISED than CUT by over 10% (mean 0.2149 vs 0.2025); the "more cut than
  raised" claim holds only on the 20-row Austin sub-sample.
* Two items remain above the package's authority and are still open before the memo: the
  fiat de-gross-up equation is dimensionally wrong for a GBV-basis reported ADR (both forms
  are implemented side by side, `gbv_consistent` is the default), and the 15-Sep / 13-Oct
  2026 migration deadlines are **absent from `06_fee_timeline.csv` and have no source
  anywhere in the repository** — they are an explicit dated assumption.
* FY27 delta against the assumed +0.9pp fee line, recomputed from `07c`: +0.27pp at full
  weight and **-0.31pp at half weight** (central theta). The +0.9pp line is, if anything,
  slightly generous at half weight.

### l1-reconciliation — verification pass

* Gate **G2 passes**: all 72 exact regional revenue cells reproduce (max abs 2.3e-13 musd),
  composition 56 filed + 16 exact Q4 back-outs; 16 of 16 in-window annual regional nights
  cells inside +/-0.5M. The remaining 8 annual cells are out of the fitted panel window
  (FY2020-21), not dirty.
* The registered `revenue_contemporaneous` object loses to naive by **11.3x** (ratio 11.338
  on both windows PIT, 10.93 / 10.09 full-sample) and survives neither window. It is a
  deliberate negative control and must never be quoted as a forecast.
* Acceptance test A8 **FAILS**: within-region ex-FX ADR reproduces at +2.60 / +2.01 / +3.13pp
  against the ADR note's +3.10 / +3.44 / +3.41, worst gap -1.43pp in 2024. The FX split is
  identified only to about +/-1.4pp and the disclosures on disk cannot close it.
* The regional ADR y/y disclosure class is **mutually inconsistent** with filed revenue,
  annual nights and nights growth under a constant or linearly drifting regional take rate.
  Reported as an inconsistency in the disclosures, not relaxed.
* FY27 (from `l1_fy27_revenue_grid.csv`): 15,720 musd at w=0.33, 15,779 at w=0.50,
  **15,838 at w=2/3**; kernel-weight sensitivity 117.3 musd = 0.74% of revenue = 2.34pp of
  growth. Growth +11.52% at w=2/3. Parameter count 60 free in the reconciliation
  (54 softmax logits + 3 take-rate tilts + 3 drifts), 68 on the registered objects.

### tracker-backlog — verification pass

* **Gate G1 fails on revenue, on both windows, on the raw series**, exactly as pre-registered.
  Per-spec (section 2): `unearned_raw` ratio 1.171 (W1) / 1.168 (W2); `funds_raw` 1.691 /
  0.985. Neither survives both windows.
* On nights the raw unearned series is 0.904 of the local naive on W1 but 1.183 on W2 —
  again not both windows.
* The RNPL-corrected specs DO clear on both windows: `unearned_rnpl_scenario_k1.0` on
  revenue_yoy is 0.680 (W1) / 0.593 (W2), and `unearned_rnpl_scenario_k0.5` on nights_yoy is
  0.750 / 0.875 against the local naive. **This must be cited with its caveats every time**:
  2 of the 14 (W1) and 10 (W2) dates use researcher-assumed RNPL shares, only the >20% floor
  is management-disclosed and the 22% point is the package's own pick, and k was swept over
  four values on two series, so there is real multiple-comparison exposure. It is a
  conditional result, never "Gate G1 cleared".
* The circularity test T1 was run first, as instructed, and the legacy W2 discrepancy is
  reconciled: the legacy 0.600 ratio reproduces to 4 dp (0.600200 vs 0.600143) only under an
  undisclosed truncated 2023Q1+ training window; this package's full-history convention gives
  0.985. The legacy number is the same cell under a shorter window, **not** independent
  corroboration.

### calibration-rail — verification PARTIAL

* Contributes the reference baselines on the four targets the harness does not cover
  (`adr_yoy`, `gbv_yoy`, `nights_yoy`, `take_rate_pct`) — that infrastructure is what makes
  four of the tables in section 1 readable at all.
* **Optimal mix, on revenue level: 100% guide+cushion.** No tested method improves on it;
  the recomputed claim file gives guide+cushion mean absolute error 1.068% PIT / 0.990%
  full-sample on n=14. On surprise-vs-Street nothing beats `bl_last_quarter` (RMSE 1.760pp);
  `bl_guide` 2.588 and `bl_guide_plus_cushion` 2.642 are the WORST of the bank, above even
  `bl_zero` 1.873. Guide is an excellent level forecast and a terrible surprise forecast.
* The must-fix from round 1 was real: PIT z-scores were being passed where quantile
  probabilities belonged; 128 of 284 scored PIT values were outside [0,1] before the fix and
  all 284 are inside after. Part (d) counts corrected to 12 BIASED / 21 calibrated /
  1 OVERCONFIDENT of 34 groups.
* **Both GBM objects are scored on 10 quarters in BOTH windows** (2024Q1-2026Q2 on W1 as
  well as W2 — confirmed in `first_quarter`/`last_quarter` on the scoreboard). Their
  `survives_both_windows = True` is therefore vacuous: it is the same ten quarters twice.
  `gbm_surprise_guide` ratio 0.339 and `gbm_revenue` 0.927 must be read as W2-only results.
* Verifier left four items open, all in the note rather than the outputs, and the
  full-registry conformal claim is now stale again. **Recomputed on this run**, over all 200
  scoreboard rows: 13 distinct `conformal_cov_empirical` values, 87 rows at 1.000, 46 at
  0.750, 41 at 0.875, 11 at 0.500, 5 at 0.250. The interesting number is that **70 of 200
  rows sit BELOW the attainable floor of 0.857** — the floor is derived for exchangeable
  residuals and 35% of the registry is under it, which is the exchangeability violation
  showing up in the data rather than in a caveat string. calibration-rail's own 56 rows:
  28 at 1.000, 12 at 0.750, 10 at 0.875, 3 at 0.500, 2 at 0.250, 1 at 0.625.


---

## 4. FX lag — the answer

All numbers here are read from `data/processed/forecast_methods/fx_lag/`
(`06_object_a_summary.csv`, `06b_object_a_hypothesis_tests.csv`, `09_hypothesis_horse_race_loo.csv`,
`09c_pit_window_scores.csv`, `10_determined_share.csv`, `13_four_way_reconciliation.csv`,
`11_forward_schedule.csv`, `11b_fy27_annualisation.csv`). Two regressands are carried
throughout: **gross ex-hedge** revenue FX (14 letter-rounded integers, scored on +/-0.5) and
**stated** (after-hedge) revenue FX.

### 4.1 The horse race, four hypotheses

Leave-one-out RMSE, n=14, gross ex-hedge target (`09_hypothesis_horse_race_loo.csv`);
lower is better. Baselines on the same target: zero 2.473, last-value 2.109.

| hypothesis | what it asserts | coefficients | LOO RMSE | PIT W1 / W2 RMSE | params |
|---|---|---|---:|---|---:|
| H0 contemporaneous | FX hits revenue in the quarter of the spot move (lag 0) | 0.8368 | 1.364 | 1.766 / 1.823 | 2 |
| H1 repo EUR mean(t-1,t-2) | the repo's existing reduced form | 0.4481, 0.2982 | 1.756 | 2.464 / 1.093 | 3 |
| H2 Phi-shape on ADR-FX | architect kernel (2/3, 1/3), one free scale | 0.6612 | 1.838 | 0.994 / 0.994 \* | 2 |
| H2b Phi-shape on the basket | same shape, basket driver | 0.7207 | 1.707 | 1.798 / 1.316 | 2 |
| **H3 free weights, lags 0/1/2** | **let the data pick** | **0.538, 0.4135, 0.000** | **1.155** | 1.485 / 1.697 | 4 |
| H3b free lags 1/2/3 | forces lag >= 1 | 0.7515, 0, 0 | 1.428 | 1.665 / 1.484 | 4 |

\* H2's "W1" is the same ten quarters as its W2 (2024Q1-2026Q2) because its ADR-FX driver
starts 2Q22 and five training rows do not accumulate until the Feb-2024 guide date. It is
**not** quotable as a W1 winner and its survives-both flag is not a two-window test.

**The estimation-hindsight premium dominates the race.** Knowing the weights in advance
improves W2 RMSE by +0.88, 0.83, 0.51, 0.31, 0.00 and -0.06pp across the six specs — larger
than every spec-versus-spec difference in the PIT table. Any backtest of this family without
a PIT replay is typically 0.3-0.9pp too good. H2 is the one spec whose two replays nearly
coincide (mean absolute point delta 0.22pp, max 0.50pp), which is a stronger argument for the
Phi shape than the horse race itself can make; H3 pays the whole estimation penalty (PIT W2
1.70 worse than its PIT W1 1.49, while its full-sample replay goes the other way).

### 4.2 Object A — the joint interval-likelihood fit and the H0 tests

Gross ex-hedge, n=14, 4 free parameters (a0, a1, a2, sigma), letter integers scored on
+/-0.5 boxes:

* Point weights **a0 = 0.538, a1 = 0.4135, a2 = 0.000**; total scale **0.9515**; normalised
  **w0 = 0.565, w1 = 0.435, w2 = 0.000**; **effective lag 0.435 quarters**, 95% confidence
  set **[0.029, 0.923]**; sigma 0.878; calibration slope 0.993; interval RMSE 0.560.
* The disclosed non-USD revenue share 0.56 is **outside** the scale confidence set
  [0.625, 1.325] on the gross series (it is inside on the stated series). The over-identifying
  restriction fails: the judgemental currency weights understate exposure by roughly 70%.

Every pre-registered restriction, gross ex-hedge series:

| H0 | weights | LR | df | p | verdict |
|---|---|---:|---:|---:|---|
| architect Phi (0, 2/3, 1/3) x 0.56 | 0, 0.373, 0.187 | 16.762 | 3 | 0.0008 | **REJECTED** |
| Theo pure lag-2 x 0.56 | 0, 0, 0.56 | 24.725 | 3 | 0.0000 | **REJECTED** |
| contemporaneous x 0.56 | 0.56, 0, 0 | 12.274 | 3 | 0.0065 | **REJECTED** |
| pure lag-1 x 0.56 | 0, 0.56, 0 | 12.937 | 3 | 0.0048 | **REJECTED** |
| Phi shape, free scale | 0, 0.480, 0.240 | 15.888 | 2 | 0.0004 | **REJECTED** |

On the **stated** (after-hedge) series the same tests give: architect Phi rejected
(p 0.0168), pure lag-2 rejected (p 0.0004), **contemporaneous NOT rejected (p 0.0575)** and
**pure lag-1 NOT rejected (p 0.0693)**.

**The answer, in one sentence.** Theo's two-quarter lead is **rejected on both series** — it
is the single worst-fitting restriction tested (LR 24.7, p < 0.0001 gross; 18.0, p 0.0004
stated) — and so is the architect's 2/3-1/3 Phi read as a 1.33-quarter mean lag times 0.56;
what survives is a **mean lag between 0 and about 1 quarter, point 0.44, 95% CS
[0.03, 0.92]**, with roughly 57% of the effect landing in the quarter of the move and 43% one
quarter later and **nothing at lag 2**. The M6 critic's lag-1 reading is the closest survivor
of the three that were in the repo; Theo's lag-2 is the furthest. At n=14 with 4 parameters
this is 3.5 observations per parameter and the confidence set is wide — that width IS the
finding, and no downstream package may treat the point weights as identified.

### 4.3 Object B (revenue-FX minus ADR-FX wedge) and Object C (the falsification)

* **Object B.** Wedge mean +0.002pp (gross) and -0.236pp (stated), sd 1.43 / 1.57pp.
  Univariate slopes on the wedge: lag-0 -0.028 (t -0.17), lag-1 +0.239 (t 1.82), lag-2 +0.208
  (t 1.57) on gross. Nothing reaches |t| = 2. There is no separately identified
  revenue-minus-ADR FX wedge.
* **Object C.** The architect's falsification survives as a conclusion but **not as a
  replication**. Headline convention, n=12, 3Q23-2Q26: slope 0.0297, se 0.0280, t 1.06,
  p 0.313 (architect: 0.158, se 0.275, t 0.57). n=12 and the |t| < 2 conclusion reproduce
  exactly; se reproduces to 0.277 vs 0.275; the slope does not reproduce on any of eight
  conventions and the wedge construction is not recoverable from the documents on disk.
  Extended to n=14 with the interval likelihood: slope 0.0273, se 0.0222, t 1.23, p 0.243 —
  **still not distinguishable from zero on all 20 rows** (|t| 0.09 to 1.40, never near 2).
  The booking-to-check-in remeasurement inside lambda stays indistinguishable from zero.

### 4.4 Already-determined shares, by date (publish all three numbers, never one)

From `10_determined_share.csv`. FX-determined share = (1 - w0) + w0 x (days elapsed / days in
quarter), published as a band across the Object-A confidence set; volume-determined share is
the fraction of the GBV driver already printed.

| as-of | target | FX determined: lo-CS (w0 0.147) | point (w0 0.565) | hi-CS (w0 0.972) | volume determined |
|---|---|---:|---:|---:|---:|
| 2026-08-06 (Q2 letter / Q3 guide) | 3Q26 | 0.911 | 0.656 | 0.408 | 1.000 |
| **2026-09-11 (today, pitch build)** | 3Q26 | 0.968 | **0.877** | 0.789 | **1.000** |
| **2026-10-02 (memo due)** | 4Q26 | 0.855 | **0.441** | 0.039 | **0.333** |
| **2026-10-23 (finals, NYC)** | 4Q26 | 0.888 | **0.570** | 0.260 | **0.333** |
| **2026-11-05 (Q3 print + Q4 guide)** | 4Q26 | 0.909 | **0.650** | 0.398 | **1.000** |
| 2027-02-11 (Q4 print + FY27 guide) | 1Q27 | 0.920 | 0.692 | 0.471 | 1.000 |

At the M6 lambda = 0.75 reading the 5-Nov 4Q26 FX share is 0.535; at the architect's w0 = 0
it is 1.000. **The pitch-date versus guide-date asymmetry is the sentence that matters**: on
2 October only one third of the 4Q26 GBV driver has printed, because 3Q26 GBV has not printed
yet; by 5 November all of it has. The 82% figure and the 85-90% "on the ledger" claim are
struck, as ruled.

### 4.5 No additive FX pp, and the four-way reconciliation

There is **no additive FX pp to revenue anywhere** in this package; the FX pp is an OUTPUT of
the kernel arithmetic. The 4Q26 readings that exist in the repo, with the adopted one last
(`13_four_way_reconciliation.csv`):

| construction | 4Q26 FX pp | status |
|---|---:|---|
| repo `05_fx_schedule` revenue_fx_fit | -0.4 | REJECTED as an input (reduced-form level fit; double-counts the lag inside the lagged GBV base) |
| repo `29_q4_fy27_bridge` FX step | -3.4 | REJECTED as an input (the double subtraction) |
| M6 memo forward schedule | +0.4 | REJECTED as an input (its own build says +0.73 against +1.04 in its schedule) |
| guide-anchored (hold the Q3 guided tailwind flat) | +2.6 | REJECTED as an input (management's basket rolls over) |
| **kernel-implied, Object-A weights on the rebuilt basket** | **+0.7** | **ADOPTED as the reported reading, as an OUTPUT** |

Spread across the four rejected readings: **6.0pp, or 167 musd on 4Q26** — larger than the
edge the pitch is claiming. Forward schedule, spot held from 2026-08-28: 3Q26 +1.2pp
(band 0.0 to +2.3), 4Q26 +0.7 (-0.4 to +1.8), 1Q27 +0.5, 2Q27 +0.1, 3Q27 +0.2, 4Q27 +0.1.

**FY27 FX is an average, not a sum.** Revenue-weighted average of the four 2027 quarterly
contributions = **+0.2pp** (simple mean also +0.2); the sum 0.9 is meaningless and the file
parks it in a column literally named `sum_of_four_quarters_pp_DO_NOT_QUOTE`. Weak-USD -1sd
path +2.3pp, strong-USD +1sd path -2.0pp.


---

## 5. The live objects, assembled, with vendor-stamped Street

Eight registry objects are LIVE-only and score in nothing. Vendor and as-of are carried on
every Street number; **the 4-Sep and 11-Sep vendor quotes are used only against LIVE 2026Q3+
objects and never as a historical pre-guide Street** — the harness raises `StreetVintageError`
if anyone tries. Machine-readable copy: `data/processed/forecast_methods/harness/live_objects.json`.

### 5.1 3Q26 print card vs the frozen card

| construction | 3Q26 revenue, musd | band | source |
|---|---:|---|---|
| kernel-lambda `live_3q26_print`, PIT prior | **4,804.0** | q10 4,707.3 / q90 4,902.8, sd 76.9 | base 2/3 x 27,200 + 1/3 x 29,200 = 27,867; lambda_Q3 17.239% |
| kernel-lambda `live_3q26_print`, full-sample prior | 4,832.4 | q10 4,648.1 / q90 5,024.0, sd 148.9 | same arithmetic, full-sample lambda |
| guide midpoint x mean trailing-8 cushion | 4,817.8 | guide range 4,690-4,770 | 4,730 x 1.01857 |
| frozen card (20_frozen_q3_2026.csv), designated | 4,805.1 | 1-sd band +0.46 to +2.29pp of surprise | +1.374% surprise on the Zacks 4,740 bar |

**These are not three views, they are one.** The kernel print and the frozen card's designated
print differ by **1.1 musd (0.02%)**, and guide+cushion sits 13.8 musd (0.29%) above the
kernel. 3Q26 needs no GBV forecast at all — both GBV lags have printed — which is why the
spread is this tight and why the object is worth almost nothing as a differentiated call.

Street anchors for 3Q26, stamped: **Zacks $4,740M, 7 estimates, as_of 2026-09-04**;
**LSEG $4,610M, as_of 2026-08-06** (this is the pre-guide number and the only one admissible
as the 6-Aug Street); guide range $4,690-4,770M issued 2026-08-06.

Take rate, same quarter (`fee_takerate/07a`), against the pre-registered 18.10% threshold:
at GBV 26,300 and central theta the printed take rate is **18.397%**, P(>= 18.10) = **0.775**,
P(<= 17.88, the guide-language mapping) = 0.095. At GBV 26,000 it is 18.609% and P = 0.899;
at GBV 26,800 it is 18.054% and P = 0.453. The test's power depends almost entirely on GBV,
not on the fee migration — which is the honest reading of a 4bp pre-registration.

### 5.2 4Q26 guide midpoint distribution vs Zacks and the 36-analyst panel

Grid from `guidance_policy/09_q4_2026_grid.csv`; central GBV_3Q26 = 26,300 musd,
lambda_Q4 = 12.0298%, cushion = +1.857% (mean), predictive sd = **3.03pp**
(95-98 musd), which is the measured number, not the 2.6pp the decisions document carries.

| GBV_3Q26 | fee step | print | guide midpoint | guide range |
|---:|---|---:|---:|---|
| 25,900 | none | 3,167.8 | 3,110.1 | 3,084.0-3,136.2 |
| **26,300 (central)** | **none** | **3,199.9** | **3,141.6** | 3,115.2-3,168.0 |
| **26,300 (central)** | **half weight (+1.25%)** | **3,239.9** | **3,180.9** | 3,154.1-3,207.6 |
| 26,300 (central) | full weight (+2.5%) | 3,279.9 | 3,220.1 | 3,193.1-3,247.2 |
| 27,000 | half weight | 3,296.8 | 3,236.7 | — |

Probability the **guide midpoint** lands below each vendor anchor
(`guidance_policy/10_q4_2026_probabilities.csv`):

| anchor | vendor, as_of, n est | no fee step | half weight | full weight | min-max over the whole grid |
|---|---|---:|---:|---:|---|
| $3,200M | **Zacks, 2026-09-04, 10 estimates** (median ~3,150, one 3,700 outlier) | **0.730** | **0.579** | 0.418 | 0.220 - 0.830 |
| $3,158M | **Alpha Vantage 36-analyst panel, 2026-09-11** | **0.568** | **0.406** | 0.262 | 0.116 - 0.694 |

**The trade flips on the vendor quoted.** Against Zacks it is a 58-73% call; against the
36-analyst panel it is a coin toss at best (41-57%) and the half-weight central case is
actually *below* even money. Name the vendor and the timestamp or do not state the trade.
The decisions document's 0.60 / 0.47 reproduce as **0.579 / 0.406** at half weight; the
Zacks figure is close, the 36-analyst figure is 6pp lower than assumed.

**Say this first.** The consensus disagrees with itself by **$126M**: Zacks' own quarterly
sum (2,678 + 3,608 + 4,740 + 3,200) is 14,226 against its FY26 line of 14,100 (8 estimates,
2026-09-04). Alpha Vantage FY26 is 14,155 (43 est, 2026-09-11) and S&P Global MI 14,160
(43 est, 2026-09-03). The gap between vendors is larger than the edge being claimed.

Fee step, recomputed from primitives (`fee_takerate/07b`): the 4Q26 half-weight step is
**+0.28pp at the modal-jump theta, +0.57pp at central theta 0.833, +1.48pp at theta = 1**,
against the **+2.5% full step the architect's arithmetic implies**. The quoted 4Q26 range
therefore runs from **no step (print 3,200.0, guide 3,141.4)** to the **central-theta half
step actually handed to guidance-policy (print 3,218.2, guide 3,159.4)**. The full-step
central case (3,236.4 / 3,177.3) is NOT part of the quoted range.

### 5.3 FY27 revenue and its named decomposition vs the Street

FY27 revenue, `l1_fy27_revenue_grid.csv`, driver_base scenario:

| kernel weight w | FY27 revenue, musd | FY27 growth |
|---:|---:|---:|
| 0.33 | 15,720.3 | +9.18% |
| 0.50 | 15,779.5 | +10.35% |
| **0.667 (published)** | **15,837.6** | **+11.52%** |

Kernel-weight sensitivity across 0.33-0.667: **117.3 musd = 0.74% of revenue = 2.34pp of
growth**. Street: **Zacks FY27 $15.73-15.76bn, as_of 2026-09-04**, midpoint 15,745. We are
**+0.59% above the Street midpoint** — inside the kernel's own walk-forward error. Say in the
first 200 words that our FY27 is within 1% of consensus; a judge finds it in ninety seconds
and it is better said by us.

The named, non-overlapping decomposition actually built
(`l1_fy27_growth_decomposition.csv`, each line with one owner, appearing once):

| line | pp | owner | basis |
|---|---:|---|---|
| volume: NA nights (+6.0% y/y) | +2.34 | l1-reconciliation | estimated |
| volume: EMEA nights (+7.0%) | +2.90 | l1-reconciliation | estimated |
| volume: LatAm nights (+16.0%) | +1.60 | l1-reconciliation | estimated |
| volume: APAC nights (+15.0%) | +1.41 | l1-reconciliation | estimated |
| within-region ADR ex-FX (like-for-like + sub-regional mix, **deliberately unsplit**) | +3.00 | l1-reconciliation | estimated |
| geographic mix | -1.09 | l1-reconciliation | OUTPUT of the share identity |
| unit size and LOS (bedroom elasticity 0.23) | +0.38 | l1-reconciliation | estimated; the +2pp Street mapping is NOT used |
| seats and hotel dilution | 0.00 | l1-reconciliation | OUTPUT; nets out of GBV (reported-ADR drag -3.52pp in 2026) |
| booking-date FX carried through Phi | 0.00 | l1-reconciliation | already inside the lagged USD GBV base; never subtracted again |
| fee / take-rate mechanism, half weight | +0.90 | fee-takerate | **assumed, not rebuilt tonight** |
| new lines | +0.20 | fee-takerate | **assumed** |
| regulation | -0.30 | fee-takerate | **assumed** |
| hedge (dollars, added once) | 0.00 | kernel-lambda | assumed |
| kernel timing (revenue is a convolution of lagged GBV) | +0.17 | kernel-lambda | identity, not a residual |
| **total** | **+11.52** | | |

Three things to say out loud about this table. (1) It totals **+11.52%**, not the +10.5%
placeholder in the decisions document; the volume block is +8.26 against the assumed +8.6 and
the price block +3.00 against +3.5, but mix is -1.09 not -1.5, seats 0.00 not -0.5 and FX
0.00 not -0.4, and those three identity outputs are where the extra point comes from.
(2) Four lines totalling +0.80pp are **assumed inputs, not built tonight**, exactly as
pre-authorised; nobody fabricated a build to fill the gap. (3) fee-takerate's own recompute
says the +0.90pp fee line is **-0.31pp too generous at half weight** (central theta) and
+0.27pp too stingy at full weight, so the FY27 total is soft by roughly a third of a point in
the direction of our own thesis. And the booking-date FX zero is a flat-spot carry assumption,
not a measurement — fx-lag's spot-held FY27 average is **+0.2pp**, which is the largest
unmodelled FY27 term and the one place these two packages do not agree.


---

## 6. Data quality — what is missing, what is mislabelled, what cannot be scored

### 6.1 Registration coverage

**Every package registered.** All seven build packages (kernel-lambda, fx-lag,
guidance-policy, fee-takerate, l1-reconciliation, tracker-backlog, calibration-rail) have
objects in the registry and all of them parse. L0-spine registers no forecast object, which
is correct — it is a data spine, not a method. No file required a format fix and no file was
excluded from the scorer.

**Unscorable by design (8 objects, all LIVE-only, no actual exists yet):**
`fee-takerate__take_rate_mechanism`, `fx-lag__live_fx_schedule`,
`guidance-policy__q4_2026_guide_mid`, `guidance-policy__q4_2026_print`,
`kernel-lambda__live_3q26_print`, `kernel-lambda__live_4q26_print`,
`l1-reconciliation__fy27_revenue`, `l1-reconciliation__fy27_growth`.

### 6.2 Missing baselines — the biggest hole in the scoreboard

`baselines__naive` exists for **four** target metrics only: `revenue_musd`, `revenue_yoy`,
`gbv_musd`, `nights_m`. `guide_cushion` and `street` exist for `revenue_musd` only.
Consequently `rmse_ratio_to_naive` is **structurally NaN** for every row on `take_rate_pct`
(8 fee-takerate + 12 calibration-rail rows), `fx_pts_revenue` (8), `guide_mid` (4),
`nights_yoy` (16), `gbv_yoy` (12) and `adr_yoy` (12) — **72 of 200 scoreboard rows have no
denominator**, and their `survives_both_windows = False` means "not testable", not "failed".
Three consequences worth stating plainly:

* No fee-takerate object can be judged on the shared scoreboard at all. The harness
  `baseline_naive_seasonal` returns 0.0 on `take_rate_pct` because the metric is classified
  growth-like by name, so even the obvious denominator is unavailable. fee-takerate built its
  own (`06d`) and I used it above, marked `*`.
* The same growth-like misclassification distorts calibration-rail's `ref_*` rows on
  `take_rate_pct`: they compound a y/y growth rate onto a take-rate LEVEL, which is why their
  RMSE is 3.1-4.6pp on a 13-18% series against 0.33pp for a plain seasonal naive. Those three
  rows are not a meaningful comparator for a level and should be read as a symptom of the
  classification bug, not as a baseline anyone should beat.
* fx-lag has no denominator of any kind for `fx_pts_revenue`; the only comparators are inside
  the package (`BASE_zero` 2.268, `BASE_naive_last_fx_pp` 2.109).
* `guide_mid` has no baseline, so guidance-policy's headline object is scored against its own
  local naive only.

### 6.3 The scorer pools spec_id (confirmed, quantified)

`GROUP_KEYS` omits `spec_id`, so an object holding a grid of variants is scored as one
pooled series. This bites exactly one package: tracker-backlog registers 8 specs per object,
giving n=112 (W1) and n=80 (W2) rows whose pooled RMSE is not a method score. Section 2
carries the per-spec re-score. Nobody else duplicates a `(target, quarter, window,
prior_basis)` cell, so no other row is affected — I checked all 37 files.

### 6.4 Objects whose W1 and W2 are the same quarters (vacuous survives-both)

Four rows carry `survives_both_windows = True` on a W1 that is really W2:
`calibration-rail__gbm_revenue` and `__gbm_surprise_guide` (first_quarter 2024Q1,
last_quarter 2026Q2 on **both** windows, n=10 each) and `fx-lag__fx_rev_next_q_h2`
(n=10 on both). Their ratios (0.927, 0.339) are correctly computed against a
quarter-matched naive, but they are **W2-only results** and the survives-both flag on them
carries no information.

### 6.5 Mislabelled registry content — read this before quoting FY27 off the registry

`l1-reconciliation__fy27_revenue.csv` contains **one row**: quarter 2026Q3, point
**4,804.0 musd**. `l1-reconciliation__fy27_growth.csv` contains one row: quarter 2026Q3,
point **+17.31%**. Neither is FY27. They are the first quarter of the FY27 build, parked
under an FY27 object name because the harness has no annual target slot; the other five
quarters sit in `l1_unregistered_fy27_revenue.csv` / `_growth.csv` and the annual totals
(15,838 musd, +11.52%) live only in `l1_fy27_revenue_grid.csv`. **Anyone reading FY27 off
the registry gets 4,804 musd and +17.3% growth, both wrong by a mile.** Highest-priority
labelling fix before anything downstream consumes the registry.

### 6.6 Two estimators sharing one name

The harness `baseline_guide_cushion` uses the **median** trailing-8 cushion; every live
object in guidance-policy, kernel-lambda and fee-takerate uses the **mean +1.857%**. They are
different estimators and the scoreboard's `guide_cushion` row is therefore not the same object
as the "guide + cushion" that produces the 4Q26 guide midpoints in section 5.

### 6.7 Stale or absent source data

* **FRED daily FX ends 2026-08-28.** Nothing in fx-lag is genuinely as-of 11 September; the
  forward schedule holds spot from 28 August. Recorded in the package's own caveats file.
* **The 15-Sep-2026 and 13-Oct-2026 fee-migration deadlines do not appear in
  `06_fee_timeline.csv` and have no source anywhere in the repository.** They are a dated
  assumption carried in code and in the README, not a disclosure.
* fx-lag's historical training features (`b_lag1/2/3`, `eur_lag1/2`, `adrfx_lag1/2`) come
  from a regional-weight construction with no `knowable_from` filter, unlike the target
  quarter's own lag-0 basket. Documented, not eliminated; the L0 spine carries **zero**
  restated rows, so a per-vintage rebuild would reproduce the same numbers today. If a
  restated row ever lands, that caveat count stops being 0 and the decision must be revisited.
* Two prior-art reproductions FAILED and are unresolved, in both cases because the
  construction is not written down anywhere on disk: the repo's `05_fx_fits.csv` rev_fx rows
  (n 13 vs 14) and the architect's Object-C slope (0.389 vs 0.158). Both are unused
  downstream.
* The `20_frozen_q3_2026.csv` card has three features still PENDING at the 2026-09-06 freeze
  (`pr_hotel_revpar_yoy_pit`, `eu_platform_yoy_lag1`, and the non-PIT revpar variant), so the
  designated forecast rests on the trailing-4 baseline, not on the alt-data features.

### 6.8 Conformal coverage, honestly

Split conformal at n_cal 6 / alpha 0.2 has attainable band [85.7%, 100%] and **no 80%
guarantee exists at this sample size**. Across all 200 scoreboard rows the empirical
conformal coverage takes 13 distinct values and **70 rows (35%) fall below the 85.7% floor**,
including 11 rows at 0.500 and 5 at 0.250. The harness prints the exchangeability caveat on
every row; the sub-floor mass is that caveat showing up in the numbers.

### 6.9 Open harness change requests carried by packages (none actioned; harness is frozen)

1. Add `spec_id` to `score.py` `GROUP_KEYS` (tracker-backlog; quantified in 6.3).
2. Register a `naive` / `naive_seasonal` baseline for `take_rate_pct`, `fx_pts_revenue`,
   `guide_mid`, `nights_yoy`, `gbv_yoy`, `adr_yoy`; and fix the name-based growth-like
   classification that makes `baseline_naive_seasonal` return 0.0 on `take_rate_pct`
   (fee-takerate, calibration-rail, fx-lag, guidance-policy).
3. Admit LIVE windows past 2026Q3 (fx-lag: 5 forward rows; l1-reconciliation: 5 FY27
   quarters; kernel-lambda and guidance-policy needed `strict_windows=False` for 4Q26).
4. Add an annual target slot so FY27 can be registered as FY27 (l1-reconciliation; see 6.5).
5. Add `nights_yoy` to `BASELINE_SPECS` (tracker-backlog).
6. `guide_date` dtype (l1-reconciliation, HCR-2), worked around locally.

### 6.10 Results that may NOT be quoted

* Anything from `l1-reconciliation__revenue_contemporaneous` (11.3x naive; deliberate
  negative control).
* Any fee-takerate backtest object as a forecasting win (0 of 8 beat the seasonal naive).
* `guidance-policy__guide_mid_next_q` as beating naive (0.869 W1 but 1.049 W2).
* `kernel-lambda__revenue_level_h1` (1.169 on W1).
* The w=0.38 / w=0.33 PIT ratios as evidence FOR w=2/3 (COVID-window artefact).
* tracker-backlog's RNPL result as "Gate G1 cleared" (conditional on researcher-assumed RNPL
  shares at 2 dates, with a 4-value k sweep behind it).
* H2's W1 row as a W1 result, or any GBM W1 row as a W1 result (same ten quarters as W2).
* The FY27 number off the registry (see 6.5) — use the grid file.
* The 9/9 guide-below-Street drift rule as a tradeable signal (8 of 9 executable,
  Fisher p 0.141).
* Any second subtraction of the FX step; any addition of the forward hedge file on top of
  letter-stated after-hedge FX; the September vendor quotes as the 6-Aug pre-guide Street.

---

*Scorekeeper: harness scorer run 2026-09-11, exit 0, 3,170 registry rows / 37 objects /
200 scoreboard rows / 29 objects scored / 8 LIVE-only.*
