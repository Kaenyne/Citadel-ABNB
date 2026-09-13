# Margin harness scoreboard

Registry FORMAT v1.0; margin harness `10_harness_margin`. Built 2026-09-11 (validator TODAY). LIVE rows enter no metric. `mae_ratio_seasonal_naive` < 1 beats y[q-4] on the same target, window, horizon and replay; a claim must have `survives_both_windows` (equal-weighted) AND `rw_survives_both_windows` (recency-weighted, half-life 4 quarters) to be quoted.

> EXCHANGEABILITY VIOLATED: residuals are a time-ordered non-exchangeable sequence (expanding-window refits, a trending target, and a regime change at the 2022 reopening); conformal coverage here is descriptive, not a guarantee.

## target: `adj_ebitda_margin_pct`

| method | object | window | h | replay | n | mae | rw_mae | rmse | bias | rw_bias | r_sn | rw_r_sn | r_street | crps | cov80 | n_params | both | rw_both |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| baselines-margin | street | W1 | 0 | PIT | 14 | 1.59 | 1.25 | 2.00 | -1.22 | -1.10 | 0.712 | 0.654 | 1.000 | 1.28 | 1.00 | 1 | True | True |
| baselines-margin | q_guide_implied | W1 | 0 | PIT | 14 | 2.24 | 1.91 | 2.85 | -0.47 | -0.02 | 1.000 | 1.000 | 1.405 | 1.59 | 0.86 | 1 | False | False |
| baselines-margin | seasonal_naive | W1 | 0 | PIT | 14 | 2.24 | 1.91 | 2.85 | -0.47 | -0.02 | 1.000 | 1.000 | 1.405 | 2.17 | 1.00 | 1 | False | False |
| baselines-margin | seasonal_naive_drift | W1 | 0 | PIT | 14 | 2.38 | 1.98 | 3.06 | 0.26 | -0.17 | 1.066 | 1.036 | 1.498 | 2.06 | 1.00 | 1 | False | False |
| baselines-margin | guide_implied | W1 | 0 | PIT | 14 | 4.38 | 3.27 | 5.51 | -4.38 | -3.27 | 1.958 | 1.711 | 2.751 | 3.15 | 0.79 | 4 | False | False |
| baselines-margin | trailing4 | W1 | 0 | PIT | 14 | 9.48 | 8.49 | 12.10 | 0.64 | 1.21 | 4.236 | 4.440 | 5.953 | 6.93 | 0.79 | 2 | False | False |
| baselines-margin | street | W1 | 0 | full_sample | 14 | 1.59 | 1.25 | 2.00 | -1.22 | -1.10 | 0.712 | 0.654 | 1.000 | 1.32 | 1.00 | 1 | True | True |
| baselines-margin | q_guide_implied | W1 | 0 | full_sample | 14 | 2.24 | 1.91 | 2.85 | -0.47 | -0.02 | 1.000 | 1.000 | 1.405 | 1.59 | 0.86 | 1 | False | False |
| baselines-margin | seasonal_naive | W1 | 0 | full_sample | 14 | 2.24 | 1.91 | 2.85 | -0.47 | -0.02 | 1.000 | 1.000 | 1.405 | 2.31 | 1.00 | 1 | False | False |
| baselines-margin | seasonal_naive_drift | W1 | 0 | full_sample | 14 | 2.38 | 1.98 | 3.06 | 0.26 | -0.17 | 1.066 | 1.036 | 1.498 | 1.91 | 1.00 | 1 | False | False |
| baselines-margin | guide_implied | W1 | 0 | full_sample | 14 | 2.54 | 2.55 | 2.91 | -2.00 | -2.40 | 1.136 | 1.333 | 1.596 | 1.66 | 0.93 | 4 | False | False |
| baselines-margin | trailing4 | W1 | 0 | full_sample | 14 | 9.48 | 8.49 | 12.10 | 0.64 | 1.21 | 4.236 | 4.440 | 5.953 | 6.82 | 0.64 | 2 | False | False |
| baselines-margin | street | W1 | 1 | PIT | 13 | 1.64 | 1.25 | 2.17 | -0.66 | -0.34 | 0.698 | 0.647 | 1.000 | 1.46 | 1.00 | 1 | True | True |
| baselines-margin | seasonal_naive | W1 | 1 | PIT | 13 | 2.35 | 1.93 | 2.95 | -0.57 | -0.03 | 1.000 | 1.000 | 1.432 | 2.12 | 1.00 | 1 | False | False |
| baselines-margin | q_guide_implied | W1 | 1 | PIT | 1 | 2.55 | 2.55 | 2.55 | 2.55 | 2.55 |  |  |  | 1.48 | 1.00 | 1 | False | False |
| baselines-margin | guide_implied | W1 | 1 | PIT | 10 | 3.15 | 2.38 | 3.92 | -2.45 | -1.95 | 1.388 | 1.195 | 2.029 | 2.31 | 0.80 | 4 | False | False |
| baselines-margin | seasonal_naive_drift | W1 | 1 | PIT | 13 | 3.91 | 3.43 | 4.52 | 0.14 | -0.43 | 1.665 | 1.773 | 2.384 | 2.94 | 1.00 | 1 | False | False |
| baselines-margin | trailing4 | W1 | 1 | PIT | 13 | 8.91 | 8.54 | 11.62 | -0.73 | 0.97 | 3.789 | 4.418 | 5.426 | 6.44 | 0.92 | 2 | False | False |
| baselines-margin | street | W1 | 1 | full_sample | 13 | 1.64 | 1.25 | 2.17 | -0.66 | -0.34 | 0.698 | 0.647 | 1.000 | 1.53 | 1.00 | 1 | True | True |
| baselines-margin | guide_implied | W1 | 1 | full_sample | 10 | 2.02 | 1.74 | 2.52 | -1.98 | -1.68 | 0.892 | 0.872 | 1.303 | 1.43 | 0.90 | 4 | True | True |
| baselines-margin | seasonal_naive | W1 | 1 | full_sample | 13 | 2.35 | 1.93 | 2.95 | -0.57 | -0.03 | 1.000 | 1.000 | 1.432 | 2.10 | 1.00 | 1 | False | False |
| baselines-margin | q_guide_implied | W1 | 1 | full_sample | 1 | 2.55 | 2.55 | 2.55 | 2.55 | 2.55 |  |  |  | 1.47 | 1.00 | 1 | False | False |
| baselines-margin | seasonal_naive_drift | W1 | 1 | full_sample | 13 | 3.91 | 3.43 | 4.52 | 0.14 | -0.43 | 1.665 | 1.773 | 2.384 | 2.76 | 1.00 | 1 | False | False |
| baselines-margin | trailing4 | W1 | 1 | full_sample | 13 | 8.91 | 8.54 | 11.62 | -0.73 | 0.97 | 3.789 | 4.418 | 5.426 | 6.51 | 0.77 | 2 | False | False |
| baselines-margin | seasonal_naive | W1 | 2 | PIT | 12 | 2.48 | 1.96 | 3.06 | -0.68 | -0.05 | 1.000 | 1.000 |  | 1.94 | 1.00 | 1 | False | False |
| baselines-margin | guide_implied | W1 | 2 | PIT | 6 | 3.48 | 2.29 | 4.16 | 0.60 | 0.51 | 1.097 | 0.837 |  | 2.71 | 0.50 | 4 | False | True |
| baselines-margin | seasonal_naive_drift | W1 | 2 | PIT | 12 | 3.63 | 2.79 | 4.67 | 0.30 | 0.01 | 1.465 | 1.422 |  | 3.30 | 1.00 | 1 | False | False |
| baselines-margin | trailing4 | W1 | 2 | PIT | 12 | 9.52 | 8.70 | 12.19 | -0.76 | 1.16 | 3.841 | 4.438 |  | 7.03 | 0.92 | 2 | False | False |
| baselines-margin | seasonal_naive | W1 | 2 | full_sample | 12 | 2.48 | 1.96 | 3.06 | -0.68 | -0.05 | 1.000 | 1.000 |  | 1.85 | 0.92 | 1 | False | False |
| baselines-margin | guide_implied | W1 | 2 | full_sample | 6 | 2.50 | 1.77 | 2.95 | -2.04 | -0.90 | 0.789 | 0.648 |  | 1.76 | 1.00 | 4 | True | True |
| baselines-margin | seasonal_naive_drift | W1 | 2 | full_sample | 12 | 3.63 | 2.79 | 4.67 | 0.30 | 0.01 | 1.465 | 1.422 |  | 2.96 | 1.00 | 1 | False | False |
| baselines-margin | trailing4 | W1 | 2 | full_sample | 12 | 9.52 | 8.70 | 12.19 | -0.76 | 1.16 | 3.841 | 4.438 |  | 6.86 | 0.83 | 2 | False | False |
| baselines-margin | street | W2 | 0 | PIT | 10 | 1.31 | 1.12 | 1.74 | -1.13 | -1.03 | 0.669 | 0.636 | 1.000 | 1.11 | 1.00 | 1 | True | True |
| baselines-margin | q_guide_implied | W2 | 0 | PIT | 10 | 1.96 | 1.75 | 2.36 | 0.19 | 0.27 | 1.000 | 1.000 | 1.494 | 1.36 | 0.90 | 1 | False | False |
| baselines-margin | seasonal_naive | W2 | 0 | PIT | 10 | 1.96 | 1.75 | 2.36 | 0.19 | 0.27 | 1.000 | 1.000 | 1.494 | 1.85 | 1.00 | 1 | False | False |
| baselines-margin | seasonal_naive_drift | W2 | 0 | PIT | 10 | 2.02 | 1.85 | 2.66 | 0.54 | -0.07 | 1.031 | 1.052 | 1.541 | 1.78 | 1.00 | 1 | False | False |
| baselines-margin | guide_implied | W2 | 0 | PIT | 10 | 3.80 | 3.06 | 4.95 | -3.80 | -3.06 | 1.938 | 1.741 | 2.895 | 2.64 | 0.90 | 4 | False | False |
| baselines-margin | trailing4 | W2 | 0 | PIT | 10 | 8.98 | 8.32 | 11.09 | 1.77 | 1.73 | 4.583 | 4.739 | 6.848 | 6.33 | 0.90 | 2 | False | False |
| baselines-margin | street | W2 | 0 | full_sample | 10 | 1.31 | 1.12 | 1.74 | -1.13 | -1.03 | 0.669 | 0.636 | 1.000 | 1.24 | 1.00 | 1 | True | True |
| baselines-margin | q_guide_implied | W2 | 0 | full_sample | 10 | 1.96 | 1.75 | 2.36 | 0.19 | 0.27 | 1.000 | 1.000 | 1.494 | 1.36 | 0.90 | 1 | False | False |
| baselines-margin | seasonal_naive | W2 | 0 | full_sample | 10 | 1.96 | 1.75 | 2.36 | 0.19 | 0.27 | 1.000 | 1.000 | 1.494 | 2.21 | 1.00 | 1 | False | False |
| baselines-margin | seasonal_naive_drift | W2 | 0 | full_sample | 10 | 2.02 | 1.85 | 2.66 | 0.54 | -0.07 | 1.031 | 1.052 | 1.541 | 1.78 | 1.00 | 1 | False | False |
| baselines-margin | guide_implied | W2 | 0 | full_sample | 10 | 2.41 | 2.50 | 2.72 | -2.35 | -2.48 | 1.230 | 1.427 | 1.838 | 1.57 | 1.00 | 4 | False | False |
| baselines-margin | trailing4 | W2 | 0 | full_sample | 10 | 8.98 | 8.32 | 11.09 | 1.77 | 1.73 | 4.583 | 4.739 | 6.848 | 6.28 | 0.70 | 2 | False | False |
| baselines-margin | street | W2 | 1 | PIT | 9 | 0.99 | 0.97 | 1.21 | 0.28 | 0.03 | 0.629 | 0.605 | 1.000 | 1.18 | 1.00 | 1 | True | True |
| baselines-margin | seasonal_naive | W2 | 1 | PIT | 9 | 1.58 | 1.60 | 1.72 | 0.81 | 0.51 | 1.000 | 1.000 | 1.590 | 1.69 | 1.00 | 1 | False | False |
| baselines-margin | guide_implied | W2 | 1 | PIT | 7 | 2.14 | 1.99 | 2.59 | -1.79 | -1.69 | 1.276 | 1.139 | 1.941 | 1.56 | 1.00 | 4 | False | False |
| baselines-margin | q_guide_implied | W2 | 1 | PIT | 1 | 2.55 | 2.55 | 2.55 | 2.55 | 2.55 |  |  |  | 1.48 | 1.00 | 1 | False | False |
| baselines-margin | seasonal_naive_drift | W2 | 1 | PIT | 9 | 3.50 | 3.27 | 4.16 | 1.09 | -0.16 | 2.220 | 2.040 | 3.529 | 2.63 | 1.00 | 1 | False | False |
| baselines-margin | trailing4 | W2 | 1 | PIT | 9 | 8.59 | 8.37 | 10.98 | 0.51 | 1.38 | 5.442 | 5.229 | 8.651 | 6.20 | 1.00 | 2 | False | False |
| baselines-margin | street | W2 | 1 | full_sample | 9 | 0.99 | 0.97 | 1.21 | 0.28 | 0.03 | 0.629 | 0.605 | 1.000 | 1.30 | 1.00 | 1 | True | True |
| baselines-margin | guide_implied | W2 | 1 | full_sample | 7 | 1.55 | 1.56 | 2.05 | -1.49 | -1.49 | 0.924 | 0.889 | 1.406 | 1.21 | 1.00 | 4 | True | True |
| baselines-margin | seasonal_naive | W2 | 1 | full_sample | 9 | 1.58 | 1.60 | 1.72 | 0.81 | 0.51 | 1.000 | 1.000 | 1.590 | 1.81 | 1.00 | 1 | False | False |
| baselines-margin | q_guide_implied | W2 | 1 | full_sample | 1 | 2.55 | 2.55 | 2.55 | 2.55 | 2.55 |  |  |  | 1.47 | 1.00 | 1 | False | False |
| baselines-margin | seasonal_naive_drift | W2 | 1 | full_sample | 9 | 3.50 | 3.27 | 4.16 | 1.09 | -0.16 | 2.220 | 2.040 | 3.529 | 2.61 | 1.00 | 1 | False | False |
| baselines-margin | trailing4 | W2 | 1 | full_sample | 9 | 8.59 | 8.37 | 10.98 | 0.51 | 1.38 | 5.442 | 5.229 | 8.651 | 6.18 | 0.78 | 2 | False | False |
| baselines-margin | seasonal_naive | W2 | 2 | PIT | 8 | 1.72 | 1.66 | 1.82 | 0.86 | 0.52 | 1.000 | 1.000 |  | 1.52 | 1.00 | 1 | False | False |
| baselines-margin | guide_implied | W2 | 2 | PIT | 4 | 2.29 | 1.69 | 2.97 | 0.89 | 0.68 | 1.030 | 0.730 |  | 1.97 | 0.75 | 4 | False | True |
| baselines-margin | seasonal_naive_drift | W2 | 2 | PIT | 8 | 3.08 | 2.44 | 4.34 | 1.48 | 0.32 | 1.788 | 1.470 |  | 3.00 | 1.00 | 1 | False | False |
| baselines-margin | trailing4 | W2 | 2 | PIT | 8 | 9.74 | 8.83 | 11.97 | 0.57 | 1.65 | 5.661 | 5.310 |  | 6.86 | 1.00 | 2 | False | False |
| baselines-margin | guide_implied | W2 | 2 | full_sample | 4 | 1.54 | 1.34 | 1.75 | -0.84 | -0.32 | 0.694 | 0.576 |  | 1.34 | 1.00 | 4 | True | True |
| baselines-margin | seasonal_naive | W2 | 2 | full_sample | 8 | 1.72 | 1.66 | 1.82 | 0.86 | 0.52 | 1.000 | 1.000 |  | 1.47 | 1.00 | 1 | False | False |
| baselines-margin | seasonal_naive_drift | W2 | 2 | full_sample | 8 | 3.08 | 2.44 | 4.34 | 1.48 | 0.32 | 1.788 | 1.470 |  | 2.83 | 1.00 | 1 | False | False |
| baselines-margin | trailing4 | W2 | 2 | full_sample | 8 | 9.74 | 8.83 | 11.97 | 0.57 | 1.65 | 5.661 | 5.310 |  | 6.83 | 0.88 | 2 | False | False |

## target: `adj_ebitda_musd`

| method | object | window | h | replay | n | mae | rw_mae | rmse | bias | rw_bias | r_sn | rw_r_sn | r_street | crps | cov80 | n_params | both | rw_both |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| baselines-margin | q_guide_implied | W1 | 0 | PIT | 14 | 63.17 | 58.04 | 75.91 | -2.91 | 7.29 | 0.512 | 0.500 | 0.968 | 55.01 | 0.86 | 1 | True | True |
| baselines-margin | street | W1 | 0 | PIT | 14 | 65.28 | 62.31 | 77.76 | -51.33 | -53.74 | 0.529 | 0.537 | 1.000 | 49.85 | 0.93 | 1 | True | True |
| baselines-margin | seasonal_naive_drift | W1 | 0 | PIT | 14 | 103.36 | 93.49 | 118.54 | -3.21 | -20.32 | 0.837 | 0.806 | 1.583 | 76.17 | 1.00 | 1 | True | True |
| baselines-margin | guide_implied | W1 | 0 | PIT | 14 | 104.34 | 87.30 | 125.38 | -104.34 | -87.30 | 0.845 | 0.753 | 1.598 | 186.40 | 0.79 | 4 | True | True |
| baselines-margin | seasonal_naive | W1 | 0 | PIT | 14 | 123.43 | 115.99 | 157.20 | -122.43 | -114.97 | 1.000 | 1.000 | 1.891 | 137.86 | 0.93 | 1 | False | False |
| baselines-margin | pct_rev_last4 | W1 | 0 | PIT | 14 | 271.62 | 252.70 | 365.51 | -41.75 | -15.55 | 2.201 | 2.179 | 4.161 | 195.07 | 0.86 | 3 | False | False |
| baselines-margin | q_guide_implied | W1 | 0 | full_sample | 14 | 64.24 | 58.27 | 78.43 | -2.00 | 10.65 | 0.520 | 0.502 | 0.984 | 52.42 | 0.86 | 1 | True | True |
| baselines-margin | street | W1 | 0 | full_sample | 14 | 65.28 | 62.31 | 77.76 | -51.33 | -53.74 | 0.529 | 0.537 | 1.000 | 50.41 | 0.93 | 1 | True | True |
| baselines-margin | guide_implied | W1 | 0 | full_sample | 14 | 68.71 | 71.95 | 78.98 | -56.78 | -67.97 | 0.557 | 0.620 | 1.053 | 162.24 | 1.00 | 4 | True | True |
| baselines-margin | seasonal_naive_drift | W1 | 0 | full_sample | 14 | 103.36 | 93.49 | 118.54 | -3.21 | -20.32 | 0.837 | 0.806 | 1.583 | 74.84 | 0.93 | 1 | True | True |
| baselines-margin | seasonal_naive | W1 | 0 | full_sample | 14 | 123.43 | 115.99 | 157.20 | -122.43 | -114.97 | 1.000 | 1.000 | 1.891 | 130.45 | 1.00 | 1 | False | False |
| baselines-margin | pct_rev_last4 | W1 | 0 | full_sample | 14 | 271.52 | 251.99 | 366.10 | -40.71 | -12.13 | 2.200 | 2.172 | 4.159 | 195.29 | 0.86 | 3 | False | False |
| baselines-margin | street | W1 | 1 | PIT | 13 | 65.50 | 57.93 | 79.45 | -33.41 | -30.46 | 0.502 | 0.493 | 1.000 | 68.99 | 1.00 | 1 | True | True |
| baselines-margin | q_guide_implied | W1 | 1 | PIT | 1 | 75.88 | 75.88 | 75.88 | 75.88 | 75.88 |  |  |  | 46.78 | 1.00 | 1 | False | False |
| baselines-margin | guide_implied | W1 | 1 | PIT | 10 | 103.36 | 93.07 | 113.91 | -46.11 | -60.82 | 0.726 | 0.718 | 1.547 | 75.43 | 0.80 | 4 | True | True |
| baselines-margin | seasonal_naive_drift | W1 | 1 | PIT | 13 | 129.08 | 118.15 | 154.39 | -8.77 | -23.41 | 0.990 | 1.005 | 1.971 | 102.89 | 1.00 | 1 | False | False |
| baselines-margin | seasonal_naive | W1 | 1 | PIT | 13 | 130.38 | 117.54 | 162.87 | -129.31 | -116.50 | 1.000 | 1.000 | 1.991 | 162.43 | 1.00 | 1 | False | False |
| baselines-margin | pct_rev_last4 | W1 | 1 | PIT | 13 | 269.07 | 265.14 | 368.74 | -68.72 | -34.94 | 2.064 | 2.256 | 4.108 | 190.76 | 0.85 | 3 | False | False |
| baselines-margin | guide_implied | W1 | 1 | full_sample | 10 | 54.87 | 65.65 | 70.48 | -47.30 | -61.22 | 0.385 | 0.506 | 0.822 | 44.45 | 1.00 | 4 | True | True |
| baselines-margin | street | W1 | 1 | full_sample | 13 | 65.50 | 57.93 | 79.45 | -33.41 | -30.46 | 0.502 | 0.493 | 1.000 | 65.95 | 0.92 | 1 | True | True |
| baselines-margin | q_guide_implied | W1 | 1 | full_sample | 1 | 75.88 | 75.88 | 75.88 | 75.88 | 75.88 |  |  |  | 44.00 | 1.00 | 1 | False | False |
| baselines-margin | seasonal_naive_drift | W1 | 1 | full_sample | 13 | 129.08 | 118.15 | 154.39 | -8.77 | -23.41 | 0.990 | 1.005 | 1.971 | 95.85 | 0.92 | 1 | False | False |
| baselines-margin | seasonal_naive | W1 | 1 | full_sample | 13 | 130.38 | 117.54 | 162.87 | -129.31 | -116.50 | 1.000 | 1.000 | 1.991 | 137.89 | 1.00 | 1 | False | False |
| baselines-margin | pct_rev_last4 | W1 | 1 | full_sample | 13 | 269.07 | 265.14 | 368.74 | -68.72 | -34.94 | 2.064 | 2.256 | 4.108 | 193.88 | 0.77 | 3 | False | False |
| baselines-margin | seasonal_naive_drift | W1 | 2 | PIT | 12 | 114.58 | 91.41 | 140.10 | -2.25 | -8.01 | 0.866 | 0.776 |  | 94.57 | 0.83 | 1 | True | True |
| baselines-margin | seasonal_naive | W1 | 2 | PIT | 12 | 132.25 | 117.76 | 166.63 | -131.08 | -116.69 | 1.000 | 1.000 |  | 172.80 | 1.00 | 1 | False | False |
| baselines-margin | guide_implied | W1 | 2 | PIT | 6 | 142.84 | 98.28 | 190.85 | 88.05 | 57.19 | 0.981 | 1.048 |  | 101.97 | 0.50 | 4 | False | False |
| baselines-margin | pct_rev_last4 | W1 | 2 | PIT | 12 | 284.02 | 263.98 | 375.45 | -69.09 | -28.56 | 2.148 | 2.242 |  | 214.66 | 1.00 | 3 | False | False |
| baselines-margin | guide_implied | W1 | 2 | full_sample | 6 | 31.89 | 20.40 | 43.76 | -19.28 | -4.28 | 0.219 | 0.218 |  | 42.74 | 1.00 | 4 | True | True |
| baselines-margin | seasonal_naive_drift | W1 | 2 | full_sample | 12 | 114.58 | 91.41 | 140.10 | -2.25 | -8.01 | 0.866 | 0.776 |  | 86.57 | 0.92 | 1 | True | True |
| baselines-margin | seasonal_naive | W1 | 2 | full_sample | 12 | 132.25 | 117.76 | 166.63 | -131.08 | -116.69 | 1.000 | 1.000 |  | 140.51 | 1.00 | 1 | False | False |
| baselines-margin | pct_rev_last4 | W1 | 2 | full_sample | 12 | 284.02 | 263.98 | 375.45 | -69.09 | -28.56 | 2.148 | 2.242 |  | 204.03 | 1.00 | 3 | False | False |
| baselines-margin | street | W2 | 0 | PIT | 10 | 58.12 | 59.32 | 63.67 | -42.48 | -50.77 | 0.594 | 0.557 | 1.000 | 47.73 | 0.90 | 1 | True | True |
| baselines-margin | q_guide_implied | W2 | 0 | PIT | 10 | 61.72 | 55.99 | 70.85 | 16.36 | 14.98 | 0.631 | 0.526 | 1.062 | 55.04 | 0.90 | 1 | True | True |
| baselines-margin | seasonal_naive_drift | W2 | 0 | PIT | 10 | 81.80 | 86.19 | 88.38 | 1.40 | -20.76 | 0.836 | 0.810 | 1.407 | 66.46 | 1.00 | 1 | True | True |
| baselines-margin | guide_implied | W2 | 0 | PIT | 10 | 96.69 | 84.50 | 118.50 | -96.69 | -84.50 | 0.989 | 0.794 | 1.664 | 201.81 | 0.90 | 4 | True | True |
| baselines-margin | seasonal_naive | W2 | 0 | PIT | 10 | 97.80 | 106.41 | 117.15 | -96.40 | -105.27 | 1.000 | 1.000 | 1.683 | 118.12 | 0.90 | 1 | False | False |
| baselines-margin | pct_rev_last4 | W2 | 0 | PIT | 10 | 264.77 | 249.38 | 345.41 | -6.87 | 0.25 | 2.707 | 2.344 | 4.556 | 187.80 | 1.00 | 3 | False | False |
| baselines-margin | street | W2 | 0 | full_sample | 10 | 58.12 | 59.32 | 63.67 | -42.48 | -50.77 | 0.594 | 0.557 | 1.000 | 49.31 | 0.90 | 1 | True | True |
| baselines-margin | q_guide_implied | W2 | 0 | full_sample | 10 | 62.04 | 55.88 | 72.72 | 19.47 | 19.21 | 0.634 | 0.525 | 1.068 | 51.32 | 0.90 | 1 | True | True |
| baselines-margin | guide_implied | W2 | 0 | full_sample | 10 | 67.34 | 71.53 | 76.63 | -63.72 | -69.78 | 0.689 | 0.672 | 1.159 | 165.21 | 1.00 | 4 | True | True |
| baselines-margin | seasonal_naive_drift | W2 | 0 | full_sample | 10 | 81.80 | 86.19 | 88.38 | 1.40 | -20.76 | 0.836 | 0.810 | 1.407 | 66.35 | 1.00 | 1 | True | True |
| baselines-margin | seasonal_naive | W2 | 0 | full_sample | 10 | 97.80 | 106.41 | 117.15 | -96.40 | -105.27 | 1.000 | 1.000 | 1.683 | 129.42 | 1.00 | 1 | False | False |
| baselines-margin | pct_rev_last4 | W2 | 0 | full_sample | 10 | 264.04 | 248.39 | 344.75 | -3.86 | 4.44 | 2.700 | 2.334 | 4.543 | 186.60 | 1.00 | 3 | False | False |
| baselines-margin | street | W2 | 1 | PIT | 9 | 46.74 | 50.82 | 54.54 | -0.39 | -19.69 | 0.515 | 0.488 | 1.000 | 61.99 | 1.00 | 1 | True | True |
| baselines-margin | q_guide_implied | W2 | 1 | PIT | 1 | 75.88 | 75.88 | 75.88 | 75.88 | 75.88 |  |  |  | 46.78 | 1.00 | 1 | False | False |
| baselines-margin | guide_implied | W2 | 1 | PIT | 7 | 88.43 | 87.38 | 101.22 | -41.52 | -61.01 | 0.876 | 0.756 | 1.792 | 65.87 | 1.00 | 4 | True | True |
| baselines-margin | seasonal_naive | W2 | 1 | PIT | 9 | 90.67 | 104.06 | 111.05 | -89.11 | -102.87 | 1.000 | 1.000 | 1.940 | 142.62 | 1.00 | 1 | False | False |
| baselines-margin | seasonal_naive_drift | W2 | 1 | PIT | 9 | 103.33 | 108.41 | 118.19 | 8.22 | -22.55 | 1.140 | 1.042 | 2.211 | 94.08 | 1.00 | 1 | False | False |
| baselines-margin | pct_rev_last4 | W2 | 1 | PIT | 9 | 272.00 | 265.55 | 356.25 | -41.59 | -27.04 | 3.000 | 2.552 | 5.820 | 190.82 | 0.89 | 3 | False | False |
| baselines-margin | street | W2 | 1 | full_sample | 9 | 46.74 | 50.82 | 54.54 | -0.39 | -19.69 | 0.515 | 0.488 | 1.000 | 61.06 | 1.00 | 1 | True | True |
| baselines-margin | guide_implied | W2 | 1 | full_sample | 7 | 51.90 | 65.68 | 68.07 | -42.30 | -61.00 | 0.514 | 0.568 | 1.052 | 44.93 | 1.00 | 4 | True | True |
| baselines-margin | q_guide_implied | W2 | 1 | full_sample | 1 | 75.88 | 75.88 | 75.88 | 75.88 | 75.88 |  |  |  | 44.00 | 1.00 | 1 | False | False |
| baselines-margin | seasonal_naive | W2 | 1 | full_sample | 9 | 90.67 | 104.06 | 111.05 | -89.11 | -102.87 | 1.000 | 1.000 | 1.940 | 133.00 | 1.00 | 1 | False | False |
| baselines-margin | seasonal_naive_drift | W2 | 1 | full_sample | 9 | 103.33 | 108.41 | 118.19 | 8.22 | -22.55 | 1.140 | 1.042 | 2.211 | 86.49 | 1.00 | 1 | False | False |
| baselines-margin | pct_rev_last4 | W2 | 1 | full_sample | 9 | 272.00 | 265.55 | 356.25 | -41.59 | -27.04 | 3.000 | 2.552 | 5.820 | 190.93 | 0.78 | 3 | False | False |
| baselines-margin | seasonal_naive_drift | W2 | 2 | PIT | 8 | 77.00 | 74.33 | 86.76 | 16.00 | -9.06 | 0.831 | 0.704 |  | 84.82 | 1.00 | 1 | True | True |
| baselines-margin | seasonal_naive | W2 | 2 | PIT | 8 | 92.62 | 105.60 | 114.77 | -90.88 | -104.35 | 1.000 | 1.000 |  | 154.67 | 1.00 | 1 | False | False |
| baselines-margin | guide_implied | W2 | 2 | PIT | 4 | 109.48 | 81.18 | 166.33 | 82.03 | 53.06 | 1.652 | 1.360 |  | 85.51 | 0.75 | 4 | False | False |
| baselines-margin | pct_rev_last4 | W2 | 2 | PIT | 8 | 299.58 | 271.86 | 376.21 | -48.71 | -23.43 | 3.234 | 2.574 |  | 213.49 | 1.00 | 3 | False | False |
| baselines-margin | guide_implied | W2 | 2 | full_sample | 4 | 11.66 | 11.88 | 14.18 | 7.26 | 6.91 | 0.176 | 0.199 |  | 38.83 | 1.00 | 4 | True | True |
| baselines-margin | seasonal_naive_drift | W2 | 2 | full_sample | 8 | 77.00 | 74.33 | 86.76 | 16.00 | -9.06 | 0.831 | 0.704 |  | 71.06 | 1.00 | 1 | True | True |
| baselines-margin | seasonal_naive | W2 | 2 | full_sample | 8 | 92.62 | 105.60 | 114.77 | -90.88 | -104.35 | 1.000 | 1.000 |  | 135.85 | 1.00 | 1 | False | False |
| baselines-margin | pct_rev_last4 | W2 | 2 | full_sample | 8 | 299.58 | 271.86 | 376.21 | -48.71 | -23.43 | 3.234 | 2.574 |  | 211.77 | 1.00 | 3 | False | False |

## target: `cor_cash_pct_rev`

| method | object | window | h | replay | n | mae | rw_mae | rmse | bias | rw_bias | r_sn | rw_r_sn | r_street | crps | cov80 | n_params | both | rw_both |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| baselines-margin | seasonal_naive | W1 | 0 | PIT | 14 | 0.64 | 0.53 | 0.75 | 0.32 | 0.16 | 1.000 | 1.000 |  | 0.51 | 0.93 | 1 | False | False |
| baselines-margin | seasonal_naive_drift | W1 | 0 | PIT | 14 | 0.90 | 0.89 | 1.09 | -0.08 | -0.05 | 1.399 | 1.684 |  | 0.65 | 0.86 | 1 | False | False |
| baselines-margin | trailing4 | W1 | 0 | PIT | 14 | 2.53 | 2.12 | 3.30 | -0.15 | -0.31 | 3.935 | 4.036 |  | 1.87 | 0.64 | 2 | False | False |
| baselines-margin | seasonal_naive | W1 | 0 | full_sample | 14 | 0.64 | 0.53 | 0.75 | 0.32 | 0.16 | 1.000 | 1.000 |  | 0.52 | 1.00 | 1 | False | False |
| baselines-margin | seasonal_naive_drift | W1 | 0 | full_sample | 14 | 0.90 | 0.89 | 1.09 | -0.08 | -0.05 | 1.399 | 1.684 |  | 0.62 | 0.86 | 1 | False | False |
| baselines-margin | trailing4 | W1 | 0 | full_sample | 14 | 2.53 | 2.12 | 3.30 | -0.15 | -0.31 | 3.935 | 4.036 |  | 1.85 | 0.64 | 2 | False | False |
| baselines-margin | seasonal_naive | W1 | 1 | PIT | 13 | 0.66 | 0.53 | 0.77 | 0.30 | 0.16 | 1.000 | 1.000 |  | 0.48 | 1.00 | 1 | False | False |
| baselines-margin | seasonal_naive_drift | W1 | 1 | PIT | 13 | 0.77 | 0.88 | 0.95 | -0.08 | 0.03 | 1.171 | 1.670 |  | 0.62 | 0.92 | 1 | False | False |
| baselines-margin | trailing4 | W1 | 1 | PIT | 13 | 2.39 | 2.14 | 3.15 | 0.30 | -0.17 | 3.650 | 4.056 |  | 1.74 | 0.85 | 2 | False | False |
| baselines-margin | seasonal_naive | W1 | 1 | full_sample | 13 | 0.66 | 0.53 | 0.77 | 0.30 | 0.16 | 1.000 | 1.000 |  | 0.48 | 1.00 | 1 | False | False |
| baselines-margin | seasonal_naive_drift | W1 | 1 | full_sample | 13 | 0.77 | 0.88 | 0.95 | -0.08 | 0.03 | 1.171 | 1.670 |  | 0.57 | 1.00 | 1 | False | False |
| baselines-margin | trailing4 | W1 | 1 | full_sample | 13 | 2.39 | 2.14 | 3.15 | 0.30 | -0.17 | 3.650 | 4.056 |  | 1.76 | 0.77 | 2 | False | False |
| baselines-margin | seasonal_naive | W1 | 2 | PIT | 12 | 0.61 | 0.51 | 0.73 | 0.23 | 0.13 | 1.000 | 1.000 |  | 0.44 | 1.00 | 1 | False | False |
| baselines-margin | seasonal_naive_drift | W1 | 2 | PIT | 12 | 0.66 | 0.67 | 0.79 | -0.21 | -0.09 | 1.070 | 1.309 |  | 0.63 | 1.00 | 1 | False | False |
| baselines-margin | trailing4 | W1 | 2 | PIT | 12 | 2.48 | 2.15 | 3.30 | 0.30 | -0.18 | 4.047 | 4.196 |  | 1.91 | 0.83 | 2 | False | False |
| baselines-margin | seasonal_naive | W1 | 2 | full_sample | 12 | 0.61 | 0.51 | 0.73 | 0.23 | 0.13 | 1.000 | 1.000 |  | 0.43 | 1.00 | 1 | False | False |
| baselines-margin | seasonal_naive_drift | W1 | 2 | full_sample | 12 | 0.66 | 0.67 | 0.79 | -0.21 | -0.09 | 1.070 | 1.309 |  | 0.54 | 1.00 | 1 | False | False |
| baselines-margin | trailing4 | W1 | 2 | full_sample | 12 | 2.48 | 2.15 | 3.30 | 0.30 | -0.18 | 4.047 | 4.196 |  | 1.84 | 0.83 | 2 | False | False |
| baselines-margin | seasonal_naive | W2 | 0 | PIT | 10 | 0.61 | 0.51 | 0.74 | 0.16 | 0.10 | 1.000 | 1.000 |  | 0.46 | 0.90 | 1 | False | False |
| baselines-margin | seasonal_naive_drift | W2 | 0 | PIT | 10 | 1.01 | 0.92 | 1.23 | -0.08 | -0.05 | 1.644 | 1.812 |  | 0.68 | 0.80 | 1 | False | False |
| baselines-margin | trailing4 | W2 | 0 | PIT | 10 | 2.38 | 2.06 | 3.22 | -0.39 | -0.43 | 3.880 | 4.077 |  | 1.80 | 0.70 | 2 | False | False |
| baselines-margin | seasonal_naive | W2 | 0 | full_sample | 10 | 0.61 | 0.51 | 0.74 | 0.16 | 0.10 | 1.000 | 1.000 |  | 0.51 | 1.00 | 1 | False | False |
| baselines-margin | seasonal_naive_drift | W2 | 0 | full_sample | 10 | 1.01 | 0.92 | 1.23 | -0.08 | -0.05 | 1.644 | 1.812 |  | 0.69 | 0.80 | 1 | False | False |
| baselines-margin | trailing4 | W2 | 0 | full_sample | 10 | 2.38 | 2.06 | 3.22 | -0.39 | -0.43 | 3.880 | 4.077 |  | 1.79 | 0.70 | 2 | False | False |
| baselines-margin | seasonal_naive | W2 | 1 | PIT | 9 | 0.56 | 0.48 | 0.68 | 0.05 | 0.06 | 1.000 | 1.000 |  | 0.42 | 1.00 | 1 | False | False |
| baselines-margin | seasonal_naive_drift | W2 | 1 | PIT | 9 | 0.98 | 0.95 | 1.11 | -0.15 | 0.01 | 1.758 | 1.987 |  | 0.65 | 0.89 | 1 | False | False |
| baselines-margin | trailing4 | W2 | 1 | PIT | 9 | 2.18 | 2.03 | 3.04 | 0.11 | -0.23 | 3.912 | 4.231 |  | 1.67 | 0.78 | 2 | False | False |
| baselines-margin | seasonal_naive | W2 | 1 | full_sample | 9 | 0.56 | 0.48 | 0.68 | 0.05 | 0.06 | 1.000 | 1.000 |  | 0.44 | 1.00 | 1 | False | False |
| baselines-margin | seasonal_naive_drift | W2 | 1 | full_sample | 9 | 0.98 | 0.95 | 1.11 | -0.15 | 0.01 | 1.758 | 1.987 |  | 0.64 | 1.00 | 1 | False | False |
| baselines-margin | trailing4 | W2 | 1 | full_sample | 9 | 2.18 | 2.03 | 3.04 | 0.11 | -0.23 | 3.912 | 4.231 |  | 1.68 | 0.78 | 2 | False | False |
| baselines-margin | seasonal_naive | W2 | 2 | PIT | 8 | 0.50 | 0.45 | 0.63 | 0.18 | 0.12 | 1.000 | 1.000 |  | 0.37 | 1.00 | 1 | False | False |
| baselines-margin | seasonal_naive_drift | W2 | 2 | PIT | 8 | 0.67 | 0.67 | 0.78 | -0.08 | -0.02 | 1.345 | 1.491 |  | 0.59 | 1.00 | 1 | False | False |
| baselines-margin | trailing4 | W2 | 2 | PIT | 8 | 2.38 | 2.10 | 3.27 | 0.21 | -0.22 | 4.768 | 4.672 |  | 1.83 | 0.88 | 2 | False | False |
| baselines-margin | seasonal_naive | W2 | 2 | full_sample | 8 | 0.50 | 0.45 | 0.63 | 0.18 | 0.12 | 1.000 | 1.000 |  | 0.38 | 1.00 | 1 | False | False |
| baselines-margin | seasonal_naive_drift | W2 | 2 | full_sample | 8 | 0.67 | 0.67 | 0.78 | -0.08 | -0.02 | 1.345 | 1.491 |  | 0.53 | 1.00 | 1 | False | False |
| baselines-margin | trailing4 | W2 | 2 | full_sample | 8 | 2.38 | 2.10 | 3.27 | 0.21 | -0.22 | 4.768 | 4.672 |  | 1.81 | 0.88 | 2 | False | False |

## target: `ops_cash_pct_rev`

| method | object | window | h | replay | n | mae | rw_mae | rmse | bias | rw_bias | r_sn | rw_r_sn | r_street | crps | cov80 | n_params | both | rw_both |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| baselines-margin | seasonal_naive | W1 | 0 | PIT | 14 | 0.81 | 0.85 | 1.00 | 0.63 | 0.72 | 1.000 | 1.000 |  | 0.71 | 0.86 | 1 | False | False |
| baselines-margin | seasonal_naive_drift | W1 | 0 | PIT | 14 | 0.99 | 0.93 | 1.07 | -0.01 | 0.06 | 1.224 | 1.097 |  | 0.74 | 1.00 | 1 | False | False |
| baselines-margin | trailing4 | W1 | 0 | PIT | 14 | 1.22 | 1.13 | 1.53 | 0.31 | 0.37 | 1.500 | 1.324 |  | 0.87 | 0.86 | 2 | False | False |
| baselines-margin | seasonal_naive | W1 | 0 | full_sample | 14 | 0.81 | 0.85 | 1.00 | 0.63 | 0.72 | 1.000 | 1.000 |  | 0.66 | 1.00 | 1 | False | False |
| baselines-margin | seasonal_naive_drift | W1 | 0 | full_sample | 14 | 0.99 | 0.93 | 1.07 | -0.01 | 0.06 | 1.224 | 1.097 |  | 0.67 | 1.00 | 1 | False | False |
| baselines-margin | trailing4 | W1 | 0 | full_sample | 14 | 1.22 | 1.13 | 1.53 | 0.31 | 0.37 | 1.500 | 1.324 |  | 0.85 | 0.79 | 2 | False | False |
| baselines-margin | seasonal_naive | W1 | 1 | PIT | 13 | 0.87 | 0.87 | 1.04 | 0.68 | 0.73 | 1.000 | 1.000 |  | 0.63 | 0.92 | 1 | False | False |
| baselines-margin | trailing4 | W1 | 1 | PIT | 13 | 1.11 | 1.14 | 1.45 | 0.68 | 0.59 | 1.276 | 1.322 |  | 0.81 | 0.85 | 2 | False | False |
| baselines-margin | seasonal_naive_drift | W1 | 1 | PIT | 13 | 1.14 | 1.03 | 1.35 | 0.08 | 0.18 | 1.305 | 1.190 |  | 0.85 | 1.00 | 1 | False | False |
| baselines-margin | seasonal_naive | W1 | 1 | full_sample | 13 | 0.87 | 0.87 | 1.04 | 0.68 | 0.73 | 1.000 | 1.000 |  | 0.59 | 0.92 | 1 | False | False |
| baselines-margin | trailing4 | W1 | 1 | full_sample | 13 | 1.11 | 1.14 | 1.45 | 0.68 | 0.59 | 1.276 | 1.322 |  | 0.81 | 0.85 | 2 | False | False |
| baselines-margin | seasonal_naive_drift | W1 | 1 | full_sample | 13 | 1.14 | 1.03 | 1.35 | 0.08 | 0.18 | 1.305 | 1.190 |  | 0.81 | 0.92 | 1 | False | False |
| baselines-margin | seasonal_naive | W1 | 2 | PIT | 12 | 0.90 | 0.87 | 1.07 | 0.78 | 0.76 | 1.000 | 1.000 |  | 0.60 | 0.83 | 1 | False | False |
| baselines-margin | seasonal_naive_drift | W1 | 2 | PIT | 12 | 0.94 | 0.69 | 1.28 | 0.11 | 0.04 | 1.046 | 0.788 |  | 0.90 | 1.00 | 1 | False | True |
| baselines-margin | trailing4 | W1 | 2 | PIT | 12 | 1.24 | 1.16 | 1.58 | 0.87 | 0.74 | 1.378 | 1.329 |  | 0.96 | 1.00 | 2 | False | False |
| baselines-margin | seasonal_naive | W1 | 2 | full_sample | 12 | 0.90 | 0.87 | 1.07 | 0.78 | 0.76 | 1.000 | 1.000 |  | 0.61 | 0.75 | 1 | False | False |
| baselines-margin | seasonal_naive_drift | W1 | 2 | full_sample | 12 | 0.94 | 0.69 | 1.28 | 0.11 | 0.04 | 1.046 | 0.788 |  | 0.80 | 1.00 | 1 | False | True |
| baselines-margin | trailing4 | W1 | 2 | full_sample | 12 | 1.24 | 1.16 | 1.58 | 0.87 | 0.74 | 1.378 | 1.329 |  | 0.89 | 0.83 | 2 | False | False |
| baselines-margin | seasonal_naive | W2 | 0 | PIT | 10 | 0.89 | 0.87 | 1.08 | 0.75 | 0.75 | 1.000 | 1.000 |  | 0.67 | 0.80 | 1 | False | False |
| baselines-margin | trailing4 | W2 | 0 | PIT | 10 | 1.03 | 1.07 | 1.19 | 0.28 | 0.34 | 1.160 | 1.239 |  | 0.71 | 1.00 | 2 | False | False |
| baselines-margin | seasonal_naive_drift | W2 | 0 | PIT | 10 | 1.04 | 0.94 | 1.13 | -0.03 | 0.04 | 1.166 | 1.085 |  | 0.69 | 1.00 | 1 | False | False |
| baselines-margin | seasonal_naive | W2 | 0 | full_sample | 10 | 0.89 | 0.87 | 1.08 | 0.75 | 0.75 | 1.000 | 1.000 |  | 0.69 | 1.00 | 1 | False | False |
| baselines-margin | trailing4 | W2 | 0 | full_sample | 10 | 1.03 | 1.07 | 1.19 | 0.28 | 0.34 | 1.160 | 1.239 |  | 0.69 | 0.90 | 2 | False | False |
| baselines-margin | seasonal_naive_drift | W2 | 0 | full_sample | 10 | 1.04 | 0.94 | 1.13 | -0.03 | 0.04 | 1.166 | 1.085 |  | 0.69 | 1.00 | 1 | False | False |
| baselines-margin | seasonal_naive | W2 | 1 | PIT | 9 | 0.74 | 0.81 | 0.86 | 0.58 | 0.68 | 1.000 | 1.000 |  | 0.54 | 0.89 | 1 | False | False |
| baselines-margin | seasonal_naive_drift | W2 | 1 | PIT | 9 | 1.00 | 0.97 | 1.26 | -0.15 | 0.09 | 1.355 | 1.202 |  | 0.79 | 1.00 | 1 | False | False |
| baselines-margin | trailing4 | W2 | 1 | PIT | 9 | 1.11 | 1.15 | 1.33 | 0.57 | 0.55 | 1.507 | 1.431 |  | 0.77 | 0.89 | 2 | False | False |
| baselines-margin | seasonal_naive | W2 | 1 | full_sample | 9 | 0.74 | 0.81 | 0.86 | 0.58 | 0.68 | 1.000 | 1.000 |  | 0.51 | 1.00 | 1 | False | False |
| baselines-margin | seasonal_naive_drift | W2 | 1 | full_sample | 9 | 1.00 | 0.97 | 1.26 | -0.15 | 0.09 | 1.355 | 1.202 |  | 0.76 | 0.89 | 1 | False | False |
| baselines-margin | trailing4 | W2 | 1 | full_sample | 9 | 1.11 | 1.15 | 1.33 | 0.57 | 0.55 | 1.507 | 1.431 |  | 0.76 | 0.89 | 2 | False | False |
| baselines-margin | seasonal_naive | W2 | 2 | PIT | 8 | 0.76 | 0.82 | 0.88 | 0.58 | 0.69 | 1.000 | 1.000 |  | 0.51 | 0.88 | 1 | False | False |
| baselines-margin | seasonal_naive_drift | W2 | 2 | PIT | 8 | 0.82 | 0.61 | 1.11 | -0.27 | -0.11 | 1.088 | 0.743 |  | 0.81 | 1.00 | 1 | False | True |
| baselines-margin | trailing4 | W2 | 2 | PIT | 8 | 1.27 | 1.18 | 1.52 | 0.76 | 0.71 | 1.677 | 1.446 |  | 0.90 | 1.00 | 2 | False | False |
| baselines-margin | seasonal_naive | W2 | 2 | full_sample | 8 | 0.76 | 0.82 | 0.88 | 0.58 | 0.69 | 1.000 | 1.000 |  | 0.50 | 0.88 | 1 | False | False |
| baselines-margin | seasonal_naive_drift | W2 | 2 | full_sample | 8 | 0.82 | 0.61 | 1.11 | -0.27 | -0.11 | 1.088 | 0.743 |  | 0.74 | 1.00 | 1 | False | True |
| baselines-margin | trailing4 | W2 | 2 | full_sample | 8 | 1.27 | 1.18 | 1.52 | 0.76 | 0.71 | 1.677 | 1.446 |  | 0.86 | 0.88 | 2 | False | False |

## target: `pd_cash_pct_rev`

| method | object | window | h | replay | n | mae | rw_mae | rmse | bias | rw_bias | r_sn | rw_r_sn | r_street | crps | cov80 | n_params | both | rw_both |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| baselines-margin | seasonal_naive_drift | W1 | 0 | PIT | 14 | 0.66 | 0.58 | 0.74 | -0.17 | -0.01 | 0.826 | 0.892 |  | 0.76 | 1.00 | 1 | True | True |
| baselines-margin | seasonal_naive | W1 | 0 | PIT | 14 | 0.80 | 0.65 | 0.92 | 0.26 | 0.13 | 1.000 | 1.000 |  | 0.86 | 1.00 | 1 | False | False |
| baselines-margin | trailing4 | W1 | 0 | PIT | 14 | 1.97 | 1.82 | 2.39 | -0.02 | -0.12 | 2.482 | 2.801 |  | 1.36 | 0.86 | 2 | False | False |
| baselines-margin | seasonal_naive_drift | W1 | 0 | full_sample | 14 | 0.66 | 0.58 | 0.74 | -0.17 | -0.01 | 0.826 | 0.892 |  | 0.71 | 1.00 | 1 | True | True |
| baselines-margin | seasonal_naive | W1 | 0 | full_sample | 14 | 0.80 | 0.65 | 0.92 | 0.26 | 0.13 | 1.000 | 1.000 |  | 0.94 | 1.00 | 1 | False | False |
| baselines-margin | trailing4 | W1 | 0 | full_sample | 14 | 1.97 | 1.82 | 2.39 | -0.02 | -0.12 | 2.482 | 2.801 |  | 1.35 | 0.86 | 2 | False | False |
| baselines-margin | seasonal_naive | W1 | 1 | PIT | 13 | 0.75 | 0.64 | 0.88 | 0.18 | 0.10 | 1.000 | 1.000 |  | 0.67 | 1.00 | 1 | False | False |
| baselines-margin | seasonal_naive_drift | W1 | 1 | PIT | 13 | 1.02 | 0.85 | 1.19 | -0.22 | 0.13 | 1.357 | 1.325 |  | 0.99 | 1.00 | 1 | False | False |
| baselines-margin | trailing4 | W1 | 1 | PIT | 13 | 1.97 | 1.85 | 2.39 | 0.26 | -0.05 | 2.612 | 2.892 |  | 1.34 | 0.92 | 2 | False | False |
| baselines-margin | seasonal_naive | W1 | 1 | full_sample | 13 | 0.75 | 0.64 | 0.88 | 0.18 | 0.10 | 1.000 | 1.000 |  | 0.68 | 1.00 | 1 | False | False |
| baselines-margin | seasonal_naive_drift | W1 | 1 | full_sample | 13 | 1.02 | 0.85 | 1.19 | -0.22 | 0.13 | 1.357 | 1.325 |  | 0.87 | 1.00 | 1 | False | False |
| baselines-margin | trailing4 | W1 | 1 | full_sample | 13 | 1.97 | 1.85 | 2.39 | 0.26 | -0.05 | 2.612 | 2.892 |  | 1.35 | 0.85 | 2 | False | False |
| baselines-margin | seasonal_naive | W1 | 2 | PIT | 12 | 0.78 | 0.64 | 0.91 | 0.16 | 0.10 | 1.000 | 1.000 |  | 0.54 | 1.00 | 1 | False | False |
| baselines-margin | seasonal_naive_drift | W1 | 2 | PIT | 12 | 1.20 | 1.13 | 1.40 | -0.25 | 0.19 | 1.541 | 1.766 |  | 1.13 | 1.00 | 1 | False | False |
| baselines-margin | trailing4 | W1 | 2 | PIT | 12 | 2.07 | 1.89 | 2.53 | 0.20 | -0.11 | 2.659 | 2.935 |  | 1.51 | 1.00 | 2 | False | False |
| baselines-margin | seasonal_naive | W1 | 2 | full_sample | 12 | 0.78 | 0.64 | 0.91 | 0.16 | 0.10 | 1.000 | 1.000 |  | 0.54 | 1.00 | 1 | False | False |
| baselines-margin | seasonal_naive_drift | W1 | 2 | full_sample | 12 | 1.20 | 1.13 | 1.40 | -0.25 | 0.19 | 1.541 | 1.766 |  | 0.99 | 1.00 | 1 | False | False |
| baselines-margin | trailing4 | W1 | 2 | full_sample | 12 | 2.07 | 1.89 | 2.53 | 0.20 | -0.11 | 2.659 | 2.935 |  | 1.46 | 0.92 | 2 | False | False |
| baselines-margin | seasonal_naive_drift | W2 | 0 | PIT | 10 | 0.58 | 0.56 | 0.64 | -0.14 | 0.00 | 0.845 | 0.922 |  | 0.59 | 1.00 | 1 | True | True |
| baselines-margin | seasonal_naive | W2 | 0 | PIT | 10 | 0.68 | 0.60 | 0.80 | -0.06 | 0.02 | 1.000 | 1.000 |  | 0.70 | 1.00 | 1 | False | False |
| baselines-margin | trailing4 | W2 | 0 | PIT | 10 | 1.91 | 1.80 | 2.25 | -0.32 | -0.24 | 2.790 | 2.996 |  | 1.30 | 0.90 | 2 | False | False |
| baselines-margin | seasonal_naive_drift | W2 | 0 | full_sample | 10 | 0.58 | 0.56 | 0.64 | -0.14 | 0.00 | 0.845 | 0.922 |  | 0.69 | 1.00 | 1 | True | True |
| baselines-margin | seasonal_naive | W2 | 0 | full_sample | 10 | 0.68 | 0.60 | 0.80 | -0.06 | 0.02 | 1.000 | 1.000 |  | 0.91 | 1.00 | 1 | False | False |
| baselines-margin | trailing4 | W2 | 0 | full_sample | 10 | 1.91 | 1.80 | 2.25 | -0.32 | -0.24 | 2.790 | 2.996 |  | 1.29 | 0.90 | 2 | False | False |
| baselines-margin | seasonal_naive | W2 | 1 | PIT | 9 | 0.61 | 0.57 | 0.71 | -0.22 | -0.03 | 1.000 | 1.000 |  | 0.57 | 1.00 | 1 | False | False |
| baselines-margin | seasonal_naive_drift | W2 | 1 | PIT | 9 | 0.98 | 0.82 | 1.12 | -0.21 | 0.15 | 1.605 | 1.439 |  | 0.86 | 1.00 | 1 | False | False |
| baselines-margin | trailing4 | W2 | 1 | PIT | 9 | 1.90 | 1.82 | 2.27 | -0.10 | -0.15 | 3.125 | 3.192 |  | 1.30 | 0.89 | 2 | False | False |
| baselines-margin | seasonal_naive | W2 | 1 | full_sample | 9 | 0.61 | 0.57 | 0.71 | -0.22 | -0.03 | 1.000 | 1.000 |  | 0.64 | 1.00 | 1 | False | False |
| baselines-margin | seasonal_naive_drift | W2 | 1 | full_sample | 9 | 0.98 | 0.82 | 1.12 | -0.21 | 0.15 | 1.605 | 1.439 |  | 0.86 | 1.00 | 1 | False | False |
| baselines-margin | trailing4 | W2 | 1 | full_sample | 9 | 1.90 | 1.82 | 2.27 | -0.10 | -0.15 | 3.125 | 3.192 |  | 1.31 | 0.89 | 2 | False | False |
| baselines-margin | seasonal_naive | W2 | 2 | PIT | 8 | 0.65 | 0.59 | 0.74 | -0.28 | -0.05 | 1.000 | 1.000 |  | 0.48 | 1.00 | 1 | False | False |
| baselines-margin | seasonal_naive_drift | W2 | 2 | PIT | 8 | 1.34 | 1.18 | 1.54 | -0.23 | 0.25 | 2.065 | 2.023 |  | 1.07 | 1.00 | 1 | False | False |
| baselines-margin | trailing4 | W2 | 2 | PIT | 8 | 2.06 | 1.88 | 2.44 | -0.26 | -0.27 | 3.165 | 3.217 |  | 1.43 | 1.00 | 2 | False | False |
| baselines-margin | seasonal_naive | W2 | 2 | full_sample | 8 | 0.65 | 0.59 | 0.74 | -0.28 | -0.05 | 1.000 | 1.000 |  | 0.48 | 1.00 | 1 | False | False |
| baselines-margin | seasonal_naive_drift | W2 | 2 | full_sample | 8 | 1.34 | 1.18 | 1.54 | -0.23 | 0.25 | 2.065 | 2.023 |  | 1.03 | 1.00 | 1 | False | False |
| baselines-margin | trailing4 | W2 | 2 | full_sample | 8 | 2.06 | 1.88 | 2.44 | -0.26 | -0.27 | 3.165 | 3.217 |  | 1.43 | 1.00 | 2 | False | False |

## target: `sm_cash_pct_rev`

| method | object | window | h | replay | n | mae | rw_mae | rmse | bias | rw_bias | r_sn | rw_r_sn | r_street | crps | cov80 | n_params | both | rw_both |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| baselines-margin | seasonal_naive_drift | W1 | 0 | PIT | 14 | 1.27 | 1.07 | 1.58 | -0.24 | -0.08 | 0.740 | 0.559 |  | 1.01 | 1.00 | 1 | True | True |
| baselines-margin | seasonal_naive | W1 | 0 | PIT | 14 | 1.71 | 1.91 | 1.84 | -1.11 | -1.65 | 1.000 | 1.000 |  | 1.09 | 0.86 | 1 | False | False |
| baselines-margin | trailing4 | W1 | 0 | PIT | 14 | 3.51 | 3.47 | 4.11 | -1.02 | -1.56 | 2.052 | 1.814 |  | 2.39 | 0.79 | 2 | False | False |
| baselines-margin | seasonal_naive_drift | W1 | 0 | full_sample | 14 | 1.27 | 1.07 | 1.58 | -0.24 | -0.08 | 0.740 | 0.559 |  | 0.97 | 1.00 | 1 | True | True |
| baselines-margin | seasonal_naive | W1 | 0 | full_sample | 14 | 1.71 | 1.91 | 1.84 | -1.11 | -1.65 | 1.000 | 1.000 |  | 1.05 | 0.93 | 1 | False | False |
| baselines-margin | trailing4 | W1 | 0 | full_sample | 14 | 3.51 | 3.47 | 4.11 | -1.02 | -1.56 | 2.052 | 1.814 |  | 2.34 | 0.79 | 2 | False | False |
| baselines-margin | seasonal_naive | W1 | 1 | PIT | 13 | 1.71 | 1.91 | 1.85 | -1.05 | -1.65 | 1.000 | 1.000 |  | 1.10 | 0.85 | 1 | False | False |
| baselines-margin | seasonal_naive_drift | W1 | 1 | PIT | 13 | 1.88 | 1.48 | 2.12 | -0.36 | -0.41 | 1.101 | 0.772 |  | 1.22 | 1.00 | 1 | False | True |
| baselines-margin | trailing4 | W1 | 1 | PIT | 13 | 3.51 | 3.73 | 4.02 | -0.93 | -1.89 | 2.056 | 1.950 |  | 2.28 | 0.85 | 2 | False | False |
| baselines-margin | seasonal_naive | W1 | 1 | full_sample | 13 | 1.71 | 1.91 | 1.85 | -1.05 | -1.65 | 1.000 | 1.000 |  | 1.05 | 0.92 | 1 | False | False |
| baselines-margin | seasonal_naive_drift | W1 | 1 | full_sample | 13 | 1.88 | 1.48 | 2.12 | -0.36 | -0.41 | 1.101 | 0.772 |  | 1.21 | 0.85 | 1 | False | True |
| baselines-margin | trailing4 | W1 | 1 | full_sample | 13 | 3.51 | 3.73 | 4.02 | -0.93 | -1.89 | 2.056 | 1.950 |  | 2.29 | 0.85 | 2 | False | False |
| baselines-margin | seasonal_naive | W1 | 2 | PIT | 12 | 1.73 | 1.92 | 1.87 | -1.02 | -1.66 | 1.000 | 1.000 |  | 1.12 | 0.92 | 1 | False | False |
| baselines-margin | seasonal_naive_drift | W1 | 2 | PIT | 12 | 1.79 | 1.46 | 2.22 | -0.49 | -0.71 | 1.035 | 0.757 |  | 1.46 | 1.00 | 1 | False | True |
| baselines-margin | trailing4 | W1 | 2 | PIT | 12 | 3.85 | 4.08 | 4.29 | -1.17 | -2.25 | 2.232 | 2.120 |  | 2.49 | 0.83 | 2 | False | False |
| baselines-margin | seasonal_naive | W1 | 2 | full_sample | 12 | 1.73 | 1.92 | 1.87 | -1.02 | -1.66 | 1.000 | 1.000 |  | 1.07 | 0.92 | 1 | False | False |
| baselines-margin | seasonal_naive_drift | W1 | 2 | full_sample | 12 | 1.79 | 1.46 | 2.22 | -0.49 | -0.71 | 1.035 | 0.757 |  | 1.31 | 1.00 | 1 | False | True |
| baselines-margin | trailing4 | W1 | 2 | full_sample | 12 | 3.85 | 4.08 | 4.29 | -1.17 | -2.25 | 2.232 | 2.120 |  | 2.44 | 0.83 | 2 | False | False |
| baselines-margin | seasonal_naive_drift | W2 | 0 | PIT | 10 | 1.07 | 1.01 | 1.20 | -0.37 | -0.13 | 0.615 | 0.520 |  | 0.86 | 1.00 | 1 | True | True |
| baselines-margin | seasonal_naive | W2 | 0 | PIT | 10 | 1.73 | 1.94 | 1.90 | -1.56 | -1.87 | 1.000 | 1.000 |  | 1.14 | 0.80 | 1 | False | False |
| baselines-margin | trailing4 | W2 | 0 | PIT | 10 | 3.56 | 3.49 | 3.86 | -1.62 | -1.83 | 2.055 | 1.805 |  | 2.22 | 0.90 | 2 | False | False |
| baselines-margin | seasonal_naive_drift | W2 | 0 | full_sample | 10 | 1.07 | 1.01 | 1.20 | -0.37 | -0.13 | 0.615 | 0.520 |  | 0.84 | 1.00 | 1 | True | True |
| baselines-margin | seasonal_naive | W2 | 0 | full_sample | 10 | 1.73 | 1.94 | 1.90 | -1.56 | -1.87 | 1.000 | 1.000 |  | 1.08 | 0.90 | 1 | False | False |
| baselines-margin | trailing4 | W2 | 0 | full_sample | 10 | 3.56 | 3.49 | 3.86 | -1.62 | -1.83 | 2.055 | 1.805 |  | 2.22 | 0.90 | 2 | False | False |
| baselines-margin | seasonal_naive_drift | W2 | 1 | PIT | 9 | 1.56 | 1.35 | 1.71 | -0.85 | -0.58 | 0.854 | 0.681 |  | 1.04 | 1.00 | 1 | False | True |
| baselines-margin | seasonal_naive | W2 | 1 | PIT | 9 | 1.83 | 1.98 | 1.99 | -1.83 | -1.98 | 1.000 | 1.000 |  | 1.19 | 0.78 | 1 | False | False |
| baselines-margin | trailing4 | W2 | 1 | PIT | 9 | 3.65 | 3.79 | 3.95 | -1.64 | -2.18 | 1.997 | 1.912 |  | 2.27 | 0.89 | 2 | False | False |
| baselines-margin | seasonal_naive_drift | W2 | 1 | full_sample | 9 | 1.56 | 1.35 | 1.71 | -0.85 | -0.58 | 0.854 | 0.681 |  | 1.02 | 1.00 | 1 | False | True |
| baselines-margin | seasonal_naive | W2 | 1 | full_sample | 9 | 1.83 | 1.98 | 1.99 | -1.83 | -1.98 | 1.000 | 1.000 |  | 1.13 | 0.89 | 1 | False | False |
| baselines-margin | trailing4 | W2 | 1 | full_sample | 9 | 3.65 | 3.79 | 3.95 | -1.64 | -2.18 | 1.997 | 1.912 |  | 2.27 | 0.89 | 2 | False | False |
| baselines-margin | seasonal_naive_drift | W2 | 2 | PIT | 8 | 1.59 | 1.32 | 2.05 | -1.15 | -0.93 | 0.826 | 0.648 |  | 1.29 | 1.00 | 1 | False | True |
| baselines-margin | seasonal_naive | W2 | 2 | PIT | 8 | 1.92 | 2.03 | 2.07 | -1.92 | -2.03 | 1.000 | 1.000 |  | 1.22 | 0.88 | 1 | False | False |
| baselines-margin | trailing4 | W2 | 2 | PIT | 8 | 4.25 | 4.29 | 4.46 | -1.96 | -2.59 | 2.209 | 2.112 |  | 2.56 | 0.88 | 2 | False | False |
| baselines-margin | seasonal_naive_drift | W2 | 2 | full_sample | 8 | 1.59 | 1.32 | 2.05 | -1.15 | -0.93 | 0.826 | 0.648 |  | 1.25 | 1.00 | 1 | False | True |
| baselines-margin | seasonal_naive | W2 | 2 | full_sample | 8 | 1.92 | 2.03 | 2.07 | -1.92 | -2.03 | 1.000 | 1.000 |  | 1.18 | 0.88 | 1 | False | False |
| baselines-margin | trailing4 | W2 | 2 | full_sample | 8 | 4.25 | 4.29 | 4.46 | -1.96 | -2.59 | 2.209 | 2.112 |  | 2.55 | 0.88 | 2 | False | False |

## target: `ga_cash_pct_rev`

| method | object | window | h | replay | n | mae | rw_mae | rmse | bias | rw_bias | r_sn | rw_r_sn | r_street | crps | cov80 | n_params | both | rw_both |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| baselines-margin | seasonal_naive | W1 | 0 | PIT | 14 | 6.90 | 5.33 | 16.12 | 0.27 | 1.56 | 1.000 | 1.000 |  | 8.08 | 0.86 | 1 | False | False |
| baselines-margin | trailing4 | W1 | 0 | PIT | 14 | 7.26 | 4.98 | 12.84 | 0.18 | 1.02 | 1.051 | 0.936 |  | 6.46 | 0.93 | 2 | False | True |
| baselines-margin | seasonal_naive_drift | W1 | 0 | PIT | 14 | 13.11 | 10.46 | 22.65 | 0.14 | 0.01 | 1.899 | 1.963 |  | 12.72 | 0.71 | 1 | False | False |
| baselines-margin | seasonal_naive | W1 | 0 | full_sample | 14 | 6.90 | 5.33 | 16.12 | 0.27 | 1.56 | 1.000 | 1.000 |  | 7.74 | 0.86 | 1 | False | False |
| baselines-margin | trailing4 | W1 | 0 | full_sample | 14 | 7.26 | 4.98 | 12.84 | 0.18 | 1.02 | 1.051 | 0.936 |  | 6.23 | 0.93 | 2 | False | True |
| baselines-margin | seasonal_naive_drift | W1 | 0 | full_sample | 14 | 13.11 | 10.46 | 22.65 | 0.14 | 0.01 | 1.899 | 1.963 |  | 12.10 | 0.71 | 1 | False | False |
| baselines-margin | seasonal_naive | W1 | 1 | PIT | 13 | 7.41 | 5.42 | 16.73 | 0.27 | 1.59 | 1.000 | 1.000 |  | 8.34 | 0.85 | 1 | False | False |
| baselines-margin | trailing4 | W1 | 1 | PIT | 13 | 7.82 | 5.47 | 13.39 | 0.34 | 1.46 | 1.055 | 1.009 |  | 6.71 | 0.92 | 2 | False | False |
| baselines-margin | seasonal_naive_drift | W1 | 1 | PIT | 13 | 14.24 | 11.82 | 23.55 | 0.25 | 0.04 | 1.921 | 2.180 |  | 13.03 | 0.69 | 1 | False | False |
| baselines-margin | seasonal_naive | W1 | 1 | full_sample | 13 | 7.41 | 5.42 | 16.73 | 0.27 | 1.59 | 1.000 | 1.000 |  | 8.10 | 0.85 | 1 | False | False |
| baselines-margin | trailing4 | W1 | 1 | full_sample | 13 | 7.82 | 5.47 | 13.39 | 0.34 | 1.46 | 1.055 | 1.009 |  | 6.58 | 0.92 | 2 | False | False |
| baselines-margin | seasonal_naive_drift | W1 | 1 | full_sample | 13 | 14.24 | 11.82 | 23.55 | 0.25 | 0.04 | 1.921 | 2.180 |  | 12.74 | 0.69 | 1 | False | False |
| baselines-margin | seasonal_naive | W1 | 2 | PIT | 12 | 8.01 | 5.54 | 17.41 | 0.27 | 1.62 | 1.000 | 1.000 |  | 8.67 | 0.83 | 1 | False | False |
| baselines-margin | trailing4 | W1 | 2 | PIT | 12 | 8.37 | 5.85 | 13.99 | 0.34 | 1.88 | 1.045 | 1.057 |  | 6.99 | 0.92 | 2 | False | False |
| baselines-margin | seasonal_naive_drift | W1 | 2 | PIT | 12 | 14.89 | 12.13 | 24.50 | -0.15 | -1.31 | 1.858 | 2.189 |  | 13.72 | 0.67 | 1 | False | False |
| baselines-margin | seasonal_naive | W1 | 2 | full_sample | 12 | 8.01 | 5.54 | 17.41 | 0.27 | 1.62 | 1.000 | 1.000 |  | 8.55 | 0.83 | 1 | False | False |
| baselines-margin | trailing4 | W1 | 2 | full_sample | 12 | 8.37 | 5.85 | 13.99 | 0.34 | 1.88 | 1.045 | 1.057 |  | 6.95 | 0.92 | 2 | False | False |
| baselines-margin | seasonal_naive_drift | W1 | 2 | full_sample | 12 | 14.89 | 12.13 | 24.50 | -0.15 | -1.31 | 1.858 | 2.189 |  | 13.30 | 0.67 | 1 | False | False |
| baselines-margin | seasonal_naive | W2 | 0 | PIT | 10 | 5.47 | 4.48 | 14.06 | 4.47 | 3.13 | 1.000 | 1.000 |  | 7.15 | 0.90 | 1 | False | False |
| baselines-margin | trailing4 | W2 | 0 | PIT | 10 | 5.55 | 3.98 | 7.24 | 4.35 | 2.53 | 1.014 | 0.889 |  | 4.68 | 1.00 | 2 | False | True |
| baselines-margin | seasonal_naive_drift | W2 | 0 | PIT | 10 | 14.16 | 10.16 | 23.60 | 4.22 | 1.39 | 2.587 | 2.270 |  | 13.66 | 0.70 | 1 | False | False |
| baselines-margin | seasonal_naive | W2 | 0 | full_sample | 10 | 5.47 | 4.48 | 14.06 | 4.47 | 3.13 | 1.000 | 1.000 |  | 6.62 | 0.90 | 1 | False | False |
| baselines-margin | trailing4 | W2 | 0 | full_sample | 10 | 5.55 | 3.98 | 7.24 | 4.35 | 2.53 | 1.014 | 0.889 |  | 4.32 | 1.00 | 2 | False | True |
| baselines-margin | seasonal_naive_drift | W2 | 0 | full_sample | 10 | 14.16 | 10.16 | 23.60 | 4.22 | 1.39 | 2.587 | 2.270 |  | 12.74 | 0.70 | 1 | False | False |
| baselines-margin | seasonal_naive | W2 | 1 | PIT | 9 | 6.08 | 4.66 | 14.82 | 4.97 | 3.27 | 1.000 | 1.000 |  | 7.47 | 0.89 | 1 | False | False |
| baselines-margin | trailing4 | W2 | 1 | PIT | 9 | 6.14 | 4.55 | 7.71 | 5.07 | 3.15 | 1.010 | 0.976 |  | 4.84 | 1.00 | 2 | False | False |
| baselines-margin | seasonal_naive_drift | W2 | 1 | PIT | 9 | 15.75 | 11.86 | 24.79 | 4.87 | 1.49 | 2.593 | 2.543 |  | 14.18 | 0.67 | 1 | False | False |
| baselines-margin | seasonal_naive | W2 | 1 | full_sample | 9 | 6.08 | 4.66 | 14.82 | 4.97 | 3.27 | 1.000 | 1.000 |  | 7.03 | 0.89 | 1 | False | False |
| baselines-margin | trailing4 | W2 | 1 | full_sample | 9 | 6.14 | 4.55 | 7.71 | 5.07 | 3.15 | 1.010 | 0.976 |  | 4.59 | 1.00 | 2 | False | False |
| baselines-margin | seasonal_naive_drift | W2 | 1 | full_sample | 9 | 15.75 | 11.86 | 24.79 | 4.87 | 1.49 | 2.593 | 2.543 |  | 13.62 | 0.67 | 1 | False | False |
| baselines-margin | trailing4 | W2 | 2 | PIT | 8 | 6.74 | 5.08 | 8.31 | 5.66 | 3.76 | 0.988 | 1.034 |  | 5.08 | 1.00 | 2 | False | False |
| baselines-margin | seasonal_naive | W2 | 2 | PIT | 8 | 6.83 | 4.91 | 15.72 | 5.60 | 3.45 | 1.000 | 1.000 |  | 7.87 | 0.88 | 1 | False | False |
| baselines-margin | seasonal_naive_drift | W2 | 2 | PIT | 8 | 17.08 | 12.56 | 26.26 | 4.88 | -0.00 | 2.502 | 2.560 |  | 15.36 | 0.62 | 1 | False | False |
| baselines-margin | trailing4 | W2 | 2 | full_sample | 8 | 6.74 | 5.08 | 8.31 | 5.66 | 3.76 | 0.988 | 1.034 |  | 4.91 | 1.00 | 2 | False | False |
| baselines-margin | seasonal_naive | W2 | 2 | full_sample | 8 | 6.83 | 4.91 | 15.72 | 5.60 | 3.45 | 1.000 | 1.000 |  | 7.57 | 0.88 | 1 | False | False |
| baselines-margin | seasonal_naive_drift | W2 | 2 | full_sample | 8 | 17.08 | 12.56 | 26.26 | 4.88 | -0.00 | 2.502 | 2.560 |  | 14.59 | 0.62 | 1 | False | False |

## target: `sbc_pct_rev`

| method | object | window | h | replay | n | mae | rw_mae | rmse | bias | rw_bias | r_sn | rw_r_sn | r_street | crps | cov80 | n_params | both | rw_both |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| baselines-margin | seasonal_naive_drift | W1 | 0 | PIT | 14 | 0.63 | 0.53 | 0.87 | -0.09 | 0.07 | 0.929 | 0.929 |  | 22.26 | 1.00 | 1 | True | True |
| baselines-margin | seasonal_naive | W1 | 0 | PIT | 14 | 0.68 | 0.57 | 0.95 | -0.52 | -0.31 | 1.000 | 1.000 |  | 13.89 | 1.00 | 1 | False | False |
| baselines-margin | trailing4 | W1 | 0 | PIT | 14 | 1.83 | 1.65 | 2.11 | -0.45 | -0.43 | 2.675 | 2.869 |  | 4.26 | 0.93 | 2 | False | False |
| baselines-margin | seasonal_naive_drift | W1 | 0 | full_sample | 14 | 0.63 | 0.53 | 0.87 | -0.09 | 0.07 | 0.929 | 0.929 |  | 22.59 | 1.00 | 1 | True | True |
| baselines-margin | seasonal_naive | W1 | 0 | full_sample | 14 | 0.68 | 0.57 | 0.95 | -0.52 | -0.31 | 1.000 | 1.000 |  | 15.71 | 1.00 | 1 | False | False |
| baselines-margin | trailing4 | W1 | 0 | full_sample | 14 | 1.83 | 1.65 | 2.11 | -0.45 | -0.43 | 2.675 | 2.869 |  | 4.48 | 1.00 | 2 | False | False |
| baselines-margin | seasonal_naive | W1 | 1 | PIT | 13 | 0.71 | 0.58 | 0.98 | -0.53 | -0.31 | 1.000 | 1.000 |  | 0.96 | 1.00 | 1 | False | False |
| baselines-margin | seasonal_naive_drift | W1 | 1 | PIT | 13 | 0.86 | 0.76 | 1.14 | -0.04 | 0.25 | 1.199 | 1.311 |  | 18.92 | 1.00 | 1 | False | False |
| baselines-margin | trailing4 | W1 | 1 | PIT | 13 | 1.91 | 1.71 | 2.18 | -0.50 | -0.51 | 2.669 | 2.953 |  | 5.20 | 1.00 | 2 | False | False |
| baselines-margin | seasonal_naive | W1 | 1 | full_sample | 13 | 0.71 | 0.58 | 0.98 | -0.53 | -0.31 | 1.000 | 1.000 |  | 0.91 | 1.00 | 1 | False | False |
| baselines-margin | seasonal_naive_drift | W1 | 1 | full_sample | 13 | 0.86 | 0.76 | 1.14 | -0.04 | 0.25 | 1.199 | 1.311 |  | 15.97 | 1.00 | 1 | False | False |
| baselines-margin | trailing4 | W1 | 1 | full_sample | 13 | 1.91 | 1.71 | 2.18 | -0.50 | -0.51 | 2.669 | 2.953 |  | 4.70 | 1.00 | 2 | False | False |
| baselines-margin | seasonal_naive | W1 | 2 | PIT | 12 | 0.73 | 0.58 | 1.01 | -0.54 | -0.31 | 1.000 | 1.000 |  | 0.65 | 1.00 | 1 | False | False |
| baselines-margin | seasonal_naive_drift | W1 | 2 | PIT | 12 | 1.04 | 0.98 | 1.24 | 0.01 | 0.38 | 1.420 | 1.677 |  | 23.89 | 1.00 | 1 | False | False |
| baselines-margin | trailing4 | W1 | 2 | PIT | 12 | 2.05 | 1.77 | 2.28 | -0.64 | -0.66 | 2.805 | 3.032 |  | 6.39 | 1.00 | 2 | False | False |
| baselines-margin | seasonal_naive | W1 | 2 | full_sample | 12 | 0.73 | 0.58 | 1.01 | -0.54 | -0.31 | 1.000 | 1.000 |  | 0.62 | 1.00 | 1 | False | False |
| baselines-margin | seasonal_naive_drift | W1 | 2 | full_sample | 12 | 1.04 | 0.98 | 1.24 | 0.01 | 0.38 | 1.420 | 1.677 |  | 16.66 | 1.00 | 1 | False | False |
| baselines-margin | trailing4 | W1 | 2 | full_sample | 12 | 2.05 | 1.77 | 2.28 | -0.64 | -0.66 | 2.805 | 3.032 |  | 4.93 | 1.00 | 2 | False | False |
| baselines-margin | seasonal_naive_drift | W2 | 0 | PIT | 10 | 0.62 | 0.53 | 0.86 | -0.01 | 0.10 | 0.757 | 0.876 |  | 14.61 | 1.00 | 1 | True | True |
| baselines-margin | seasonal_naive | W2 | 0 | PIT | 10 | 0.82 | 0.60 | 1.10 | -0.64 | -0.33 | 1.000 | 1.000 |  | 8.78 | 1.00 | 1 | False | False |
| baselines-margin | trailing4 | W2 | 0 | PIT | 10 | 1.87 | 1.64 | 2.15 | -0.60 | -0.48 | 2.280 | 2.729 |  | 3.07 | 0.90 | 2 | False | False |
| baselines-margin | seasonal_naive_drift | W2 | 0 | full_sample | 10 | 0.62 | 0.53 | 0.86 | -0.01 | 0.10 | 0.757 | 0.876 |  | 22.58 | 1.00 | 1 | True | True |
| baselines-margin | seasonal_naive | W2 | 0 | full_sample | 10 | 0.82 | 0.60 | 1.10 | -0.64 | -0.33 | 1.000 | 1.000 |  | 15.75 | 1.00 | 1 | False | False |
| baselines-margin | trailing4 | W2 | 0 | full_sample | 10 | 1.87 | 1.64 | 2.15 | -0.60 | -0.48 | 2.280 | 2.729 |  | 4.49 | 1.00 | 2 | False | False |
| baselines-margin | seasonal_naive | W2 | 1 | PIT | 9 | 0.85 | 0.60 | 1.14 | -0.65 | -0.32 | 1.000 | 1.000 |  | 0.84 | 1.00 | 1 | False | False |
| baselines-margin | seasonal_naive_drift | W2 | 1 | PIT | 9 | 0.91 | 0.78 | 1.19 | 0.10 | 0.31 | 1.071 | 1.288 |  | 14.34 | 1.00 | 1 | False | False |
| baselines-margin | trailing4 | W2 | 1 | PIT | 9 | 1.95 | 1.70 | 2.25 | -0.62 | -0.53 | 2.304 | 2.821 |  | 3.96 | 1.00 | 2 | False | False |
| baselines-margin | seasonal_naive | W2 | 1 | full_sample | 9 | 0.85 | 0.60 | 1.14 | -0.65 | -0.32 | 1.000 | 1.000 |  | 0.94 | 1.00 | 1 | False | False |
| baselines-margin | seasonal_naive_drift | W2 | 1 | full_sample | 9 | 0.91 | 0.78 | 1.19 | 0.10 | 0.31 | 1.071 | 1.288 |  | 15.99 | 1.00 | 1 | False | False |
| baselines-margin | trailing4 | W2 | 1 | full_sample | 9 | 1.95 | 1.70 | 2.25 | -0.62 | -0.53 | 2.304 | 2.821 |  | 4.71 | 1.00 | 2 | False | False |
| baselines-margin | seasonal_naive | W2 | 2 | PIT | 8 | 0.75 | 0.55 | 1.06 | -0.52 | -0.25 | 1.000 | 1.000 |  | 0.62 | 1.00 | 1 | False | False |
| baselines-margin | seasonal_naive_drift | W2 | 2 | PIT | 8 | 1.10 | 0.99 | 1.29 | 0.33 | 0.56 | 1.474 | 1.814 |  | 19.41 | 1.00 | 1 | False | False |
| baselines-margin | trailing4 | W2 | 2 | PIT | 8 | 1.99 | 1.70 | 2.29 | -0.65 | -0.61 | 2.668 | 3.123 |  | 5.08 | 1.00 | 2 | False | False |
| baselines-margin | seasonal_naive | W2 | 2 | full_sample | 8 | 0.75 | 0.55 | 1.06 | -0.52 | -0.25 | 1.000 | 1.000 |  | 0.63 | 1.00 | 1 | False | False |
| baselines-margin | seasonal_naive_drift | W2 | 2 | full_sample | 8 | 1.10 | 0.99 | 1.29 | 0.33 | 0.56 | 1.474 | 1.814 |  | 16.67 | 1.00 | 1 | False | False |
| baselines-margin | trailing4 | W2 | 2 | full_sample | 8 | 1.99 | 1.70 | 2.29 | -0.65 | -0.61 | 2.668 | 3.123 |  | 4.92 | 1.00 | 2 | False | False |

## target: `op_margin_pct`

| method | object | window | h | replay | n | mae | rw_mae | rmse | bias | rw_bias | r_sn | rw_r_sn | r_street | crps | cov80 | n_params | both | rw_both |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| baselines-margin | seasonal_naive | W1 | 0 | PIT | 14 | 7.70 | 6.02 | 14.44 | -0.17 | -0.70 | 1.000 | 1.000 |  | 18.74 | 1.00 | 1 | False | False |
| baselines-margin | trailing4 | W1 | 0 | PIT | 14 | 14.51 | 12.11 | 18.47 | 1.01 | 0.99 | 1.884 | 2.013 |  | 11.05 | 1.00 | 2 | False | False |
| baselines-margin | seasonal_naive_drift | W1 | 0 | PIT | 14 | 14.72 | 11.89 | 22.20 | 0.44 | 0.01 | 1.912 | 1.977 |  | 28.97 | 1.00 | 1 | False | False |
| baselines-margin | seasonal_naive | W1 | 0 | full_sample | 14 | 7.70 | 6.02 | 14.44 | -0.17 | -0.70 | 1.000 | 1.000 |  | 19.77 | 1.00 | 1 | False | False |
| baselines-margin | trailing4 | W1 | 0 | full_sample | 14 | 14.51 | 12.11 | 18.47 | 1.01 | 0.99 | 1.884 | 2.013 |  | 10.85 | 0.93 | 2 | False | False |
| baselines-margin | seasonal_naive_drift | W1 | 0 | full_sample | 14 | 14.72 | 11.89 | 22.20 | 0.44 | 0.01 | 1.912 | 1.977 |  | 27.84 | 1.00 | 1 | False | False |
| baselines-margin | seasonal_naive | W1 | 1 | PIT | 13 | 8.29 | 6.13 | 14.98 | -0.17 | -0.72 | 1.000 | 1.000 |  | 8.08 | 0.85 | 1 | False | False |
| baselines-margin | trailing4 | W1 | 1 | PIT | 13 | 14.39 | 12.01 | 18.40 | -0.32 | 0.52 | 1.736 | 1.960 |  | 11.30 | 1.00 | 2 | False | False |
| baselines-margin | seasonal_naive_drift | W1 | 1 | PIT | 13 | 14.66 | 12.72 | 21.50 | 0.36 | -0.17 | 1.770 | 2.076 |  | 25.29 | 1.00 | 1 | False | False |
| baselines-margin | seasonal_naive | W1 | 1 | full_sample | 13 | 8.29 | 6.13 | 14.98 | -0.17 | -0.72 | 1.000 | 1.000 |  | 8.03 | 0.85 | 1 | False | False |
| baselines-margin | trailing4 | W1 | 1 | full_sample | 13 | 14.39 | 12.01 | 18.40 | -0.32 | 0.52 | 1.736 | 1.960 |  | 10.91 | 0.92 | 2 | False | False |
| baselines-margin | seasonal_naive_drift | W1 | 1 | full_sample | 13 | 14.66 | 12.72 | 21.50 | 0.36 | -0.17 | 1.770 | 2.076 |  | 21.47 | 1.00 | 1 | False | False |
| baselines-margin | seasonal_naive | W1 | 2 | PIT | 12 | 8.68 | 6.19 | 15.56 | 0.11 | -0.65 | 1.000 | 1.000 |  | 8.08 | 0.83 | 1 | False | False |
| baselines-margin | seasonal_naive_drift | W1 | 2 | PIT | 12 | 13.83 | 11.41 | 20.79 | 1.33 | 1.66 | 1.592 | 1.845 |  | 30.14 | 1.00 | 1 | False | False |
| baselines-margin | trailing4 | W1 | 2 | PIT | 12 | 15.30 | 12.33 | 19.10 | -0.07 | 0.51 | 1.762 | 1.993 |  | 12.92 | 1.00 | 2 | False | False |
| baselines-margin | seasonal_naive | W1 | 2 | full_sample | 12 | 8.68 | 6.19 | 15.56 | 0.11 | -0.65 | 1.000 | 1.000 |  | 8.01 | 0.83 | 1 | False | False |
| baselines-margin | seasonal_naive_drift | W1 | 2 | full_sample | 12 | 13.83 | 11.41 | 20.79 | 1.33 | 1.66 | 1.592 | 1.845 |  | 22.31 | 1.00 | 1 | False | False |
| baselines-margin | trailing4 | W1 | 2 | full_sample | 12 | 15.30 | 12.33 | 19.10 | -0.07 | 0.51 | 1.762 | 1.993 |  | 11.83 | 1.00 | 2 | False | False |
| baselines-margin | seasonal_naive | W2 | 0 | PIT | 10 | 6.72 | 5.32 | 13.02 | -3.11 | -1.81 | 1.000 | 1.000 |  | 13.43 | 1.00 | 1 | False | False |
| baselines-margin | trailing4 | W2 | 0 | PIT | 10 | 11.49 | 10.81 | 14.36 | -1.71 | 0.11 | 1.710 | 2.032 |  | 9.22 | 1.00 | 2 | False | False |
| baselines-margin | seasonal_naive_drift | W2 | 0 | PIT | 10 | 15.70 | 11.64 | 23.37 | -3.60 | -1.35 | 2.338 | 2.186 |  | 21.82 | 1.00 | 1 | False | False |
| baselines-margin | seasonal_naive | W2 | 0 | full_sample | 10 | 6.72 | 5.32 | 13.02 | -3.11 | -1.81 | 1.000 | 1.000 |  | 19.53 | 1.00 | 1 | False | False |
| baselines-margin | trailing4 | W2 | 0 | full_sample | 10 | 11.49 | 10.81 | 14.36 | -1.71 | 0.11 | 1.710 | 2.032 |  | 9.33 | 1.00 | 2 | False | False |
| baselines-margin | seasonal_naive_drift | W2 | 0 | full_sample | 10 | 15.70 | 11.64 | 23.37 | -3.60 | -1.35 | 2.338 | 2.186 |  | 28.09 | 1.00 | 1 | False | False |
| baselines-margin | seasonal_naive | W2 | 1 | PIT | 9 | 6.91 | 5.34 | 13.63 | -2.90 | -1.68 | 1.000 | 1.000 |  | 7.32 | 0.89 | 1 | False | False |
| baselines-margin | trailing4 | W2 | 1 | PIT | 9 | 11.33 | 10.66 | 14.15 | -3.38 | -0.62 | 1.640 | 1.997 |  | 9.58 | 1.00 | 2 | False | False |
| baselines-margin | seasonal_naive_drift | W2 | 1 | PIT | 9 | 15.95 | 12.77 | 22.41 | -3.61 | -1.48 | 2.308 | 2.393 |  | 21.14 | 1.00 | 1 | False | False |
| baselines-margin | seasonal_naive | W2 | 1 | full_sample | 9 | 6.91 | 5.34 | 13.63 | -2.90 | -1.68 | 1.000 | 1.000 |  | 7.29 | 0.89 | 1 | False | False |
| baselines-margin | trailing4 | W2 | 1 | full_sample | 9 | 11.33 | 10.66 | 14.15 | -3.38 | -0.62 | 1.640 | 1.997 |  | 9.34 | 1.00 | 2 | False | False |
| baselines-margin | seasonal_naive_drift | W2 | 1 | full_sample | 9 | 15.95 | 12.77 | 22.41 | -3.61 | -1.48 | 2.308 | 2.393 |  | 21.79 | 1.00 | 1 | False | False |
| baselines-margin | seasonal_naive | W2 | 2 | PIT | 8 | 7.40 | 5.46 | 14.41 | -3.64 | -1.92 | 1.000 | 1.000 |  | 7.45 | 0.88 | 1 | False | False |
| baselines-margin | trailing4 | W2 | 2 | PIT | 8 | 12.74 | 11.36 | 15.32 | -3.76 | -0.77 | 1.722 | 2.079 |  | 11.25 | 1.00 | 2 | False | False |
| baselines-margin | seasonal_naive_drift | W2 | 2 | PIT | 8 | 14.91 | 11.50 | 22.14 | -3.48 | 0.26 | 2.014 | 2.106 |  | 25.83 | 1.00 | 1 | False | False |
| baselines-margin | seasonal_naive | W2 | 2 | full_sample | 8 | 7.40 | 5.46 | 14.41 | -3.64 | -1.92 | 1.000 | 1.000 |  | 7.23 | 0.88 | 1 | False | False |
| baselines-margin | trailing4 | W2 | 2 | full_sample | 8 | 12.74 | 11.36 | 15.32 | -3.76 | -0.77 | 1.722 | 2.079 |  | 10.61 | 1.00 | 2 | False | False |
| baselines-margin | seasonal_naive_drift | W2 | 2 | full_sample | 8 | 14.91 | 11.50 | 22.14 | -3.48 | 0.26 | 2.014 | 2.106 |  | 22.58 | 1.00 | 1 | False | False |

## target: `eps_diluted`

| method | object | window | h | replay | n | mae | rw_mae | rmse | bias | rw_bias | r_sn | rw_r_sn | r_street | crps | cov80 | n_params | both | rw_both |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| baselines-margin | street | W1 | 0 | PIT | 14 | 0.52 | 0.27 | 1.29 | -0.27 | -0.10 | 0.541 | 0.435 | 1.000 | 0.63 | 0.86 | 1 | True | True |
| baselines-margin | seasonal_naive | W1 | 0 | PIT | 14 | 0.97 | 0.62 | 1.83 | -0.11 | -0.01 | 1.000 | 1.000 | 1.850 | 1.03 | 0.93 | 1 | False | False |
| baselines-margin | seasonal_naive_drift | W1 | 0 | PIT | 14 | 1.79 | 1.21 | 2.81 | 0.00 | -0.06 | 1.848 | 1.965 | 3.419 | 1.61 | 1.00 | 1 | False | False |
| baselines-margin | street | W1 | 0 | full_sample | 14 | 0.52 | 0.27 | 1.29 | -0.27 | -0.10 | 0.541 | 0.435 | 1.000 | 0.56 | 0.93 | 1 | True | True |
| baselines-margin | seasonal_naive | W1 | 0 | full_sample | 14 | 0.97 | 0.62 | 1.83 | -0.11 | -0.01 | 1.000 | 1.000 | 1.850 | 1.05 | 0.86 | 1 | False | False |
| baselines-margin | seasonal_naive_drift | W1 | 0 | full_sample | 14 | 1.79 | 1.21 | 2.81 | 0.00 | -0.06 | 1.848 | 1.965 | 3.419 | 1.60 | 0.86 | 1 | False | False |
| baselines-margin | street | W1 | 1 | PIT | 13 | 0.59 | 0.30 | 1.36 | -0.26 | -0.07 | 0.573 | 0.480 | 1.000 | 0.73 | 0.77 | 1 | True | True |
| baselines-margin | seasonal_naive | W1 | 1 | PIT | 13 | 1.03 | 0.62 | 1.90 | -0.11 | -0.00 | 1.000 | 1.000 | 1.745 | 1.03 | 0.77 | 1 | False | False |
| baselines-margin | seasonal_naive_drift | W1 | 1 | PIT | 13 | 1.87 | 1.31 | 2.64 | 0.02 | -0.07 | 1.821 | 2.103 | 3.178 | 1.51 | 1.00 | 1 | False | False |
| baselines-margin | street | W1 | 1 | full_sample | 13 | 0.59 | 0.30 | 1.36 | -0.26 | -0.07 | 0.573 | 0.480 | 1.000 | 0.61 | 0.92 | 1 | True | True |
| baselines-margin | seasonal_naive | W1 | 1 | full_sample | 13 | 1.03 | 0.62 | 1.90 | -0.11 | -0.00 | 1.000 | 1.000 | 1.745 | 0.96 | 0.85 | 1 | False | False |
| baselines-margin | seasonal_naive_drift | W1 | 1 | full_sample | 13 | 1.87 | 1.31 | 2.64 | 0.02 | -0.07 | 1.821 | 2.103 | 3.178 | 1.48 | 0.77 | 1 | False | False |
| baselines-margin | seasonal_naive | W1 | 2 | PIT | 12 | 1.08 | 0.63 | 1.97 | -0.08 | 0.01 | 1.000 | 1.000 |  | 1.10 | 0.67 | 1 | False | False |
| baselines-margin | seasonal_naive_drift | W1 | 2 | PIT | 12 | 1.81 | 1.28 | 2.62 | 0.07 | -0.04 | 1.674 | 2.033 |  | 1.51 | 1.00 | 1 | False | False |
| baselines-margin | seasonal_naive | W1 | 2 | full_sample | 12 | 1.08 | 0.63 | 1.97 | -0.08 | 0.01 | 1.000 | 1.000 |  | 1.00 | 0.83 | 1 | False | False |
| baselines-margin | seasonal_naive_drift | W1 | 2 | full_sample | 12 | 1.81 | 1.28 | 2.62 | 0.07 | -0.04 | 1.674 | 2.033 |  | 1.47 | 0.75 | 1 | False | False |
| baselines-margin | street | W2 | 0 | PIT | 10 | 0.12 | 0.12 | 0.15 | 0.01 | -0.01 | 0.169 | 0.235 | 1.000 | 0.33 | 1.00 | 1 | True | True |
| baselines-margin | seasonal_naive | W2 | 0 | PIT | 10 | 0.71 | 0.49 | 1.49 | 0.28 | 0.11 | 1.000 | 1.000 | 5.903 | 0.84 | 0.90 | 1 | False | False |
| baselines-margin | seasonal_naive_drift | W2 | 0 | PIT | 10 | 1.44 | 1.00 | 2.38 | -0.14 | -0.14 | 2.035 | 2.035 | 12.014 | 1.36 | 1.00 | 1 | False | False |
| baselines-margin | street | W2 | 0 | full_sample | 10 | 0.12 | 0.12 | 0.15 | 0.01 | -0.01 | 0.169 | 0.235 | 1.000 | 0.26 | 1.00 | 1 | True | True |
| baselines-margin | seasonal_naive | W2 | 0 | full_sample | 10 | 0.71 | 0.49 | 1.49 | 0.28 | 0.11 | 1.000 | 1.000 | 5.903 | 0.93 | 0.90 | 1 | False | False |
| baselines-margin | seasonal_naive_drift | W2 | 0 | full_sample | 10 | 1.44 | 1.00 | 2.38 | -0.14 | -0.14 | 2.035 | 2.035 | 12.014 | 1.42 | 0.90 | 1 | False | False |
| baselines-margin | street | W2 | 1 | PIT | 9 | 0.14 | 0.14 | 0.16 | 0.07 | 0.03 | 0.187 | 0.279 | 1.000 | 0.35 | 1.00 | 1 | True | True |
| baselines-margin | seasonal_naive | W2 | 1 | PIT | 9 | 0.76 | 0.50 | 1.57 | 0.34 | 0.12 | 1.000 | 1.000 | 5.339 | 0.84 | 0.89 | 1 | False | False |
| baselines-margin | seasonal_naive_drift | W2 | 1 | PIT | 9 | 1.52 | 1.10 | 2.25 | -0.13 | -0.19 | 1.991 | 2.180 | 10.631 | 1.31 | 1.00 | 1 | False | False |
| baselines-margin | street | W2 | 1 | full_sample | 9 | 0.14 | 0.14 | 0.16 | 0.07 | 0.03 | 0.187 | 0.279 | 1.000 | 0.28 | 1.00 | 1 | True | True |
| baselines-margin | seasonal_naive | W2 | 1 | full_sample | 9 | 0.76 | 0.50 | 1.57 | 0.34 | 0.12 | 1.000 | 1.000 | 5.339 | 0.79 | 0.89 | 1 | False | False |
| baselines-margin | seasonal_naive_drift | W2 | 1 | full_sample | 9 | 1.52 | 1.10 | 2.25 | -0.13 | -0.19 | 1.991 | 2.180 | 10.631 | 1.30 | 0.89 | 1 | False | False |
| baselines-margin | seasonal_naive | W2 | 2 | PIT | 8 | 0.84 | 0.52 | 1.66 | 0.37 | 0.12 | 1.000 | 1.000 |  | 0.88 | 0.88 | 1 | False | False |
| baselines-margin | seasonal_naive_drift | W2 | 2 | PIT | 8 | 1.36 | 1.03 | 2.14 | -0.14 | -0.23 | 1.612 | 1.966 |  | 1.28 | 1.00 | 1 | False | False |
| baselines-margin | seasonal_naive | W2 | 2 | full_sample | 8 | 0.84 | 0.52 | 1.66 | 0.37 | 0.12 | 1.000 | 1.000 |  | 0.83 | 0.88 | 1 | False | False |
| baselines-margin | seasonal_naive_drift | W2 | 2 | full_sample | 8 | 1.36 | 1.03 | 2.14 | -0.14 | -0.23 | 1.612 | 1.966 |  | 1.25 | 0.88 | 1 | False | False |

## target: `fcf_margin_pct`

| method | object | window | h | replay | n | mae | rw_mae | rmse | bias | rw_bias | r_sn | rw_r_sn | r_street | crps | cov80 | n_params | both | rw_both |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| baselines-margin | seasonal_naive | W1 | 0 | PIT | 14 | 7.65 | 7.32 | 9.82 | 1.73 | 2.22 | 1.000 | 1.000 |  | 6.26 | 0.93 | 1 | False | False |
| baselines-margin | seasonal_naive_drift | W1 | 0 | PIT | 14 | 13.81 | 13.86 | 16.46 | -0.31 | -1.19 | 1.807 | 1.893 |  | 10.29 | 1.00 | 1 | False | False |
| baselines-margin | trailing4 | W1 | 0 | PIT | 14 | 20.50 | 16.90 | 25.75 | -0.89 | -0.19 | 2.681 | 2.307 |  | 14.83 | 0.79 | 2 | False | False |
| baselines-margin | seasonal_naive | W1 | 0 | full_sample | 14 | 7.65 | 7.32 | 9.82 | 1.73 | 2.22 | 1.000 | 1.000 |  | 6.00 | 0.93 | 1 | False | False |
| baselines-margin | seasonal_naive_drift | W1 | 0 | full_sample | 14 | 13.81 | 13.86 | 16.46 | -0.31 | -1.19 | 1.807 | 1.893 |  | 9.80 | 1.00 | 1 | False | False |
| baselines-margin | trailing4 | W1 | 0 | full_sample | 14 | 20.50 | 16.90 | 25.75 | -0.89 | -0.19 | 2.681 | 2.307 |  | 14.53 | 0.71 | 2 | False | False |
| baselines-margin | seasonal_naive | W1 | 1 | PIT | 13 | 7.64 | 7.32 | 9.97 | 2.45 | 2.40 | 1.000 | 1.000 |  | 5.66 | 0.77 | 1 | False | False |
| baselines-margin | seasonal_naive_drift | W1 | 1 | PIT | 13 | 11.19 | 11.48 | 13.94 | 1.39 | 1.39 | 1.464 | 1.570 |  | 9.14 | 1.00 | 1 | False | False |
| baselines-margin | trailing4 | W1 | 1 | PIT | 13 | 19.07 | 17.49 | 23.58 | 2.91 | 1.48 | 2.495 | 2.391 |  | 13.51 | 0.77 | 2 | False | False |
| baselines-margin | seasonal_naive | W1 | 1 | full_sample | 13 | 7.64 | 7.32 | 9.97 | 2.45 | 2.40 | 1.000 | 1.000 |  | 5.55 | 0.77 | 1 | False | False |
| baselines-margin | seasonal_naive_drift | W1 | 1 | full_sample | 13 | 11.19 | 11.48 | 13.94 | 1.39 | 1.39 | 1.464 | 1.570 |  | 8.34 | 1.00 | 1 | False | False |
| baselines-margin | trailing4 | W1 | 1 | full_sample | 13 | 19.07 | 17.49 | 23.58 | 2.91 | 1.48 | 2.495 | 2.391 |  | 13.31 | 0.77 | 2 | False | False |
| baselines-margin | seasonal_naive | W1 | 2 | PIT | 12 | 8.15 | 7.45 | 10.37 | 2.52 | 2.42 | 1.000 | 1.000 |  | 5.76 | 0.75 | 1 | False | False |
| baselines-margin | seasonal_naive_drift | W1 | 2 | PIT | 12 | 9.69 | 8.24 | 12.19 | 1.35 | 1.13 | 1.190 | 1.107 |  | 7.43 | 1.00 | 1 | False | False |
| baselines-margin | trailing4 | W1 | 2 | PIT | 12 | 20.31 | 18.02 | 24.55 | 2.82 | 1.60 | 2.493 | 2.421 |  | 13.58 | 0.83 | 2 | False | False |
| baselines-margin | seasonal_naive | W1 | 2 | full_sample | 12 | 8.15 | 7.45 | 10.37 | 2.52 | 2.42 | 1.000 | 1.000 |  | 5.79 | 0.75 | 1 | False | False |
| baselines-margin | seasonal_naive_drift | W1 | 2 | full_sample | 12 | 9.69 | 8.24 | 12.19 | 1.35 | 1.13 | 1.190 | 1.107 |  | 6.97 | 0.92 | 1 | False | False |
| baselines-margin | trailing4 | W1 | 2 | full_sample | 12 | 20.31 | 18.02 | 24.55 | 2.82 | 1.60 | 2.493 | 2.421 |  | 13.95 | 0.75 | 2 | False | False |
| baselines-margin | seasonal_naive | W2 | 0 | PIT | 10 | 7.05 | 7.01 | 8.85 | 1.38 | 1.98 | 1.000 | 1.000 |  | 5.48 | 0.90 | 1 | False | False |
| baselines-margin | seasonal_naive_drift | W2 | 0 | PIT | 10 | 14.15 | 13.83 | 16.87 | -2.55 | -2.10 | 2.006 | 1.971 |  | 9.78 | 1.00 | 1 | False | False |
| baselines-margin | trailing4 | W2 | 0 | PIT | 10 | 18.34 | 15.90 | 23.03 | -2.92 | -1.26 | 2.600 | 2.267 |  | 13.02 | 0.90 | 2 | False | False |
| baselines-margin | seasonal_naive | W2 | 0 | full_sample | 10 | 7.05 | 7.01 | 8.85 | 1.38 | 1.98 | 1.000 | 1.000 |  | 5.64 | 1.00 | 1 | False | False |
| baselines-margin | seasonal_naive_drift | W2 | 0 | full_sample | 10 | 14.15 | 13.83 | 16.87 | -2.55 | -2.10 | 2.006 | 1.971 |  | 9.91 | 1.00 | 1 | False | False |
| baselines-margin | trailing4 | W2 | 0 | full_sample | 10 | 18.34 | 15.90 | 23.03 | -2.92 | -1.26 | 2.600 | 2.267 |  | 12.92 | 0.80 | 2 | False | False |
| baselines-margin | seasonal_naive | W2 | 1 | PIT | 9 | 7.60 | 7.22 | 9.30 | 1.77 | 2.16 | 1.000 | 1.000 |  | 5.32 | 0.78 | 1 | False | False |
| baselines-margin | seasonal_naive_drift | W2 | 1 | PIT | 9 | 13.20 | 12.06 | 15.27 | -0.95 | 0.63 | 1.737 | 1.671 |  | 8.97 | 1.00 | 1 | False | False |
| baselines-margin | trailing4 | W2 | 1 | PIT | 9 | 16.44 | 16.09 | 19.58 | 2.59 | 1.56 | 2.163 | 2.228 |  | 11.57 | 0.89 | 2 | False | False |
| baselines-margin | seasonal_naive | W2 | 1 | full_sample | 9 | 7.60 | 7.22 | 9.30 | 1.77 | 2.16 | 1.000 | 1.000 |  | 5.25 | 0.78 | 1 | False | False |
| baselines-margin | seasonal_naive_drift | W2 | 1 | full_sample | 9 | 13.20 | 12.06 | 15.27 | -0.95 | 0.63 | 1.737 | 1.671 |  | 8.96 | 1.00 | 1 | False | False |
| baselines-margin | trailing4 | W2 | 1 | full_sample | 9 | 16.44 | 16.09 | 19.58 | 2.59 | 1.56 | 2.163 | 2.228 |  | 11.36 | 0.89 | 2 | False | False |
| baselines-margin | seasonal_naive | W2 | 2 | PIT | 8 | 8.33 | 7.51 | 9.85 | 2.21 | 2.36 | 1.000 | 1.000 |  | 5.56 | 0.75 | 1 | False | False |
| baselines-margin | seasonal_naive_drift | W2 | 2 | PIT | 8 | 9.16 | 7.96 | 10.28 | -0.89 | 0.38 | 1.099 | 1.059 |  | 6.72 | 1.00 | 1 | False | False |
| baselines-margin | trailing4 | W2 | 2 | PIT | 8 | 17.85 | 16.83 | 20.34 | 2.62 | 1.60 | 2.142 | 2.241 |  | 11.82 | 1.00 | 2 | False | False |
| baselines-margin | seasonal_naive | W2 | 2 | full_sample | 8 | 8.33 | 7.51 | 9.85 | 2.21 | 2.36 | 1.000 | 1.000 |  | 5.57 | 0.75 | 1 | False | False |
| baselines-margin | seasonal_naive_drift | W2 | 2 | full_sample | 8 | 9.16 | 7.96 | 10.28 | -0.89 | 0.38 | 1.099 | 1.059 |  | 6.19 | 1.00 | 1 | False | False |
| baselines-margin | trailing4 | W2 | 2 | full_sample | 8 | 17.85 | 16.83 | 20.34 | 2.62 | 1.60 | 2.142 | 2.241 |  | 11.78 | 0.88 | 2 | False | False |

## target: `adj_ebitda_margin_yoy_pp`

| method | object | window | h | replay | n | mae | rw_mae | rmse | bias | rw_bias | r_sn | rw_r_sn | r_street | crps | cov80 | n_params | both | rw_both |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| baselines-margin | trailing4 | W1 | 0 | PIT | 14 | 3.91 | 2.79 | 4.80 | 1.42 | 0.30 | 0.707 | 0.896 |  | 3.18 | 0.93 | 2 | True | False |
| baselines-margin | seasonal_naive_drift | W1 | 0 | PIT | 14 | 4.77 | 3.68 | 6.76 | -1.38 | -0.63 | 0.863 | 1.182 |  | 11.90 | 1.00 | 1 | False | False |
| baselines-margin | seasonal_naive | W1 | 0 | PIT | 14 | 5.53 | 3.11 | 8.67 | 3.43 | 1.36 | 1.000 | 1.000 |  | 7.82 | 1.00 | 1 | False | False |
| baselines-margin | trailing4 | W1 | 0 | full_sample | 14 | 3.91 | 2.79 | 4.80 | 1.42 | 0.30 | 0.707 | 0.896 |  | 3.35 | 1.00 | 2 | True | False |
| baselines-margin | seasonal_naive_drift | W1 | 0 | full_sample | 14 | 4.77 | 3.68 | 6.76 | -1.38 | -0.63 | 0.863 | 1.182 |  | 9.26 | 1.00 | 1 | False | False |
| baselines-margin | seasonal_naive | W1 | 0 | full_sample | 14 | 5.53 | 3.11 | 8.67 | 3.43 | 1.36 | 1.000 | 1.000 |  | 7.34 | 1.00 | 1 | False | False |
| baselines-margin | trailing4 | W1 | 1 | PIT | 13 | 3.83 | 2.88 | 4.81 | 1.52 | 0.50 | 0.907 | 1.049 |  | 4.10 | 1.00 | 2 | True | False |
| baselines-margin | seasonal_naive | W1 | 1 | PIT | 13 | 4.22 | 2.75 | 6.47 | 1.96 | 0.97 | 1.000 | 1.000 |  | 7.87 | 1.00 | 1 | False | False |
| baselines-margin | seasonal_naive_drift | W1 | 1 | PIT | 13 | 7.35 | 5.17 | 10.43 | -3.41 | -1.97 | 1.742 | 1.882 |  | 8.98 | 1.00 | 1 | False | False |
| baselines-margin | trailing4 | W1 | 1 | full_sample | 13 | 3.83 | 2.88 | 4.81 | 1.52 | 0.50 | 0.907 | 1.049 |  | 3.98 | 1.00 | 2 | True | False |
| baselines-margin | seasonal_naive | W1 | 1 | full_sample | 13 | 4.22 | 2.75 | 6.47 | 1.96 | 0.97 | 1.000 | 1.000 |  | 6.91 | 1.00 | 1 | False | False |
| baselines-margin | seasonal_naive_drift | W1 | 1 | full_sample | 13 | 7.35 | 5.17 | 10.43 | -3.41 | -1.97 | 1.742 | 1.882 |  | 7.62 | 1.00 | 1 | False | False |
| baselines-margin | seasonal_naive | W1 | 2 | PIT | 12 | 3.05 | 2.40 | 4.18 | 0.60 | 0.58 | 1.000 | 1.000 |  | 8.51 | 1.00 | 1 | False | False |
| baselines-margin | trailing4 | W1 | 2 | PIT | 12 | 3.32 | 2.82 | 3.92 | 1.69 | 0.88 | 1.091 | 1.177 |  | 4.65 | 0.92 | 2 | False | False |
| baselines-margin | seasonal_naive_drift | W1 | 2 | PIT | 12 | 10.38 | 6.93 | 13.35 | -5.21 | -2.98 | 3.407 | 2.895 |  | 11.95 | 0.83 | 1 | False | False |
| baselines-margin | seasonal_naive | W1 | 2 | full_sample | 12 | 3.05 | 2.40 | 4.18 | 0.60 | 0.58 | 1.000 | 1.000 |  | 6.80 | 1.00 | 1 | False | False |
| baselines-margin | trailing4 | W1 | 2 | full_sample | 12 | 3.32 | 2.82 | 3.92 | 1.69 | 0.88 | 1.091 | 1.177 |  | 4.19 | 1.00 | 2 | False | False |
| baselines-margin | seasonal_naive_drift | W1 | 2 | full_sample | 12 | 10.38 | 6.93 | 13.35 | -5.21 | -2.98 | 3.407 | 2.895 |  | 8.76 | 1.00 | 1 | False | False |
| baselines-margin | trailing4 | W2 | 0 | PIT | 10 | 2.88 | 2.45 | 3.20 | 0.85 | 0.17 | 0.883 | 1.009 |  | 2.71 | 1.00 | 2 | True | False |
| baselines-margin | seasonal_naive | W2 | 0 | PIT | 10 | 3.26 | 2.42 | 4.49 | 1.12 | 0.74 | 1.000 | 1.000 |  | 6.04 | 1.00 | 1 | False | False |
| baselines-margin | seasonal_naive_drift | W2 | 0 | PIT | 10 | 3.84 | 3.30 | 4.39 | 0.17 | -0.09 | 1.179 | 1.363 |  | 8.83 | 1.00 | 1 | False | False |
| baselines-margin | trailing4 | W2 | 0 | full_sample | 10 | 2.88 | 2.45 | 3.20 | 0.85 | 0.17 | 0.883 | 1.009 |  | 2.95 | 1.00 | 2 | True | False |
| baselines-margin | seasonal_naive | W2 | 0 | full_sample | 10 | 3.26 | 2.42 | 4.49 | 1.12 | 0.74 | 1.000 | 1.000 |  | 6.67 | 1.00 | 1 | False | False |
| baselines-margin | seasonal_naive_drift | W2 | 0 | full_sample | 10 | 3.84 | 3.30 | 4.39 | 0.17 | -0.09 | 1.179 | 1.363 |  | 9.03 | 1.00 | 1 | False | False |
| baselines-margin | trailing4 | W2 | 1 | PIT | 9 | 2.90 | 2.54 | 3.39 | 1.62 | 0.54 | 0.988 | 1.121 |  | 3.73 | 1.00 | 2 | True | False |
| baselines-margin | seasonal_naive | W2 | 1 | PIT | 9 | 2.94 | 2.26 | 4.27 | 1.93 | 1.03 | 1.000 | 1.000 |  | 6.38 | 1.00 | 1 | False | False |
| baselines-margin | seasonal_naive_drift | W2 | 1 | PIT | 9 | 5.09 | 4.21 | 6.53 | 0.60 | -0.59 | 1.731 | 1.861 |  | 7.86 | 1.00 | 1 | False | False |
| baselines-margin | trailing4 | W2 | 1 | full_sample | 9 | 2.90 | 2.54 | 3.39 | 1.62 | 0.54 | 0.988 | 1.121 |  | 3.66 | 1.00 | 2 | True | False |
| baselines-margin | seasonal_naive | W2 | 1 | full_sample | 9 | 2.94 | 2.26 | 4.27 | 1.93 | 1.03 | 1.000 | 1.000 |  | 6.59 | 1.00 | 1 | False | False |
| baselines-margin | seasonal_naive_drift | W2 | 1 | full_sample | 9 | 5.09 | 4.21 | 6.53 | 0.60 | -0.59 | 1.731 | 1.861 |  | 6.75 | 1.00 | 1 | False | False |
| baselines-margin | trailing4 | W2 | 2 | PIT | 8 | 3.09 | 2.70 | 3.51 | 1.93 | 0.89 | 0.947 | 1.144 |  | 4.64 | 1.00 | 2 | False | False |
| baselines-margin | seasonal_naive | W2 | 2 | PIT | 8 | 3.26 | 2.36 | 4.52 | 2.22 | 1.10 | 1.000 | 1.000 |  | 7.21 | 1.00 | 1 | False | False |
| baselines-margin | seasonal_naive_drift | W2 | 2 | PIT | 8 | 6.58 | 5.32 | 7.81 | 0.73 | -0.89 | 2.018 | 2.249 |  | 8.97 | 1.00 | 1 | False | False |
| baselines-margin | trailing4 | W2 | 2 | full_sample | 8 | 3.09 | 2.70 | 3.51 | 1.93 | 0.89 | 0.947 | 1.144 |  | 4.13 | 1.00 | 2 | False | False |
| baselines-margin | seasonal_naive | W2 | 2 | full_sample | 8 | 3.26 | 2.36 | 4.52 | 2.22 | 1.10 | 1.000 | 1.000 |  | 6.85 | 1.00 | 1 | False | False |
| baselines-margin | seasonal_naive_drift | W2 | 2 | full_sample | 8 | 6.58 | 5.32 | 7.81 | 0.73 | -0.89 | 2.018 | 2.249 |  | 7.26 | 1.00 | 1 | False | False |

## target: `adj_ebitda_per_night`

| method | object | window | h | replay | n | mae | rw_mae | rmse | bias | rw_bias | r_sn | rw_r_sn | r_street | crps | cov80 | n_params | both | rw_both |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| baselines-margin | seasonal_naive | W1 | 0 | PIT | 14 | 0.62 | 0.57 | 0.79 | -0.30 | -0.20 | 1.000 | 1.000 |  | 0.49 | 1.00 | 1 | False | False |
| baselines-margin | seasonal_naive_drift | W1 | 0 | PIT | 14 | 0.65 | 0.60 | 0.78 | 0.03 | -0.10 | 1.057 | 1.054 |  | 0.47 | 1.00 | 1 | False | False |
| baselines-margin | trailing4 | W1 | 0 | PIT | 14 | 3.54 | 3.20 | 4.58 | 0.19 | 0.42 | 5.739 | 5.605 |  | 2.61 | 0.71 | 2 | False | False |
| baselines-margin | seasonal_naive | W1 | 0 | full_sample | 14 | 0.62 | 0.57 | 0.79 | -0.30 | -0.20 | 1.000 | 1.000 |  | 0.52 | 1.00 | 1 | False | False |
| baselines-margin | seasonal_naive_drift | W1 | 0 | full_sample | 14 | 0.65 | 0.60 | 0.78 | 0.03 | -0.10 | 1.057 | 1.054 |  | 0.46 | 1.00 | 1 | False | False |
| baselines-margin | trailing4 | W1 | 0 | full_sample | 14 | 3.54 | 3.20 | 4.58 | 0.19 | 0.42 | 5.739 | 5.605 |  | 2.57 | 0.79 | 2 | False | False |
| baselines-margin | seasonal_naive | W1 | 1 | PIT | 13 | 0.66 | 0.58 | 0.82 | -0.33 | -0.20 | 1.000 | 1.000 |  | 0.48 | 1.00 | 1 | False | False |
| baselines-margin | seasonal_naive_drift | W1 | 1 | PIT | 13 | 1.00 | 0.95 | 1.11 | -0.00 | -0.17 | 1.519 | 1.637 |  | 0.66 | 0.85 | 1 | False | False |
| baselines-margin | trailing4 | W1 | 1 | PIT | 13 | 3.41 | 3.22 | 4.55 | -0.26 | 0.31 | 5.177 | 5.550 |  | 2.51 | 0.77 | 2 | False | False |
| baselines-margin | seasonal_naive | W1 | 1 | full_sample | 13 | 0.66 | 0.58 | 0.82 | -0.33 | -0.20 | 1.000 | 1.000 |  | 0.49 | 0.92 | 1 | False | False |
| baselines-margin | seasonal_naive_drift | W1 | 1 | full_sample | 13 | 1.00 | 0.95 | 1.11 | -0.00 | -0.17 | 1.519 | 1.637 |  | 0.64 | 1.00 | 1 | False | False |
| baselines-margin | trailing4 | W1 | 1 | full_sample | 13 | 3.41 | 3.22 | 4.55 | -0.26 | 0.31 | 5.177 | 5.550 |  | 2.54 | 0.77 | 2 | False | False |
| baselines-margin | seasonal_naive | W1 | 2 | PIT | 12 | 0.69 | 0.59 | 0.85 | -0.33 | -0.20 | 1.000 | 1.000 |  | 0.50 | 1.00 | 1 | False | False |
| baselines-margin | seasonal_naive_drift | W1 | 2 | PIT | 12 | 0.92 | 0.78 | 1.14 | 0.06 | -0.06 | 1.329 | 1.329 |  | 0.69 | 1.00 | 1 | False | False |
| baselines-margin | trailing4 | W1 | 2 | PIT | 12 | 3.63 | 3.26 | 4.73 | -0.37 | 0.31 | 5.247 | 5.550 |  | 2.68 | 0.75 | 2 | False | False |
| baselines-margin | seasonal_naive | W1 | 2 | full_sample | 12 | 0.69 | 0.59 | 0.85 | -0.33 | -0.20 | 1.000 | 1.000 |  | 0.49 | 0.83 | 1 | False | False |
| baselines-margin | seasonal_naive_drift | W1 | 2 | full_sample | 12 | 0.92 | 0.78 | 1.14 | 0.06 | -0.06 | 1.329 | 1.329 |  | 0.68 | 1.00 | 1 | False | False |
| baselines-margin | trailing4 | W1 | 2 | full_sample | 12 | 3.63 | 3.26 | 4.73 | -0.37 | 0.31 | 5.247 | 5.550 |  | 2.65 | 0.75 | 2 | False | False |
| baselines-margin | seasonal_naive | W2 | 0 | PIT | 10 | 0.50 | 0.52 | 0.57 | -0.07 | -0.11 | 1.000 | 1.000 |  | 0.41 | 1.00 | 1 | False | False |
| baselines-margin | seasonal_naive_drift | W2 | 0 | PIT | 10 | 0.60 | 0.59 | 0.70 | 0.10 | -0.08 | 1.213 | 1.134 |  | 0.43 | 1.00 | 1 | False | False |
| baselines-margin | trailing4 | W2 | 0 | PIT | 10 | 3.51 | 3.16 | 4.35 | 0.57 | 0.60 | 7.032 | 6.099 |  | 2.48 | 0.80 | 2 | False | False |
| baselines-margin | seasonal_naive | W2 | 0 | full_sample | 10 | 0.50 | 0.52 | 0.57 | -0.07 | -0.11 | 1.000 | 1.000 |  | 0.46 | 1.00 | 1 | False | False |
| baselines-margin | seasonal_naive_drift | W2 | 0 | full_sample | 10 | 0.60 | 0.59 | 0.70 | 0.10 | -0.08 | 1.213 | 1.134 |  | 0.43 | 1.00 | 1 | False | False |
| baselines-margin | trailing4 | W2 | 0 | full_sample | 10 | 3.51 | 3.16 | 4.35 | 0.57 | 0.60 | 7.032 | 6.099 |  | 2.46 | 0.80 | 2 | False | False |
| baselines-margin | seasonal_naive | W2 | 1 | PIT | 9 | 0.44 | 0.50 | 0.49 | 0.04 | -0.07 | 1.000 | 1.000 |  | 0.37 | 1.00 | 1 | False | False |
| baselines-margin | seasonal_naive_drift | W2 | 1 | PIT | 9 | 0.93 | 0.93 | 1.05 | 0.18 | -0.13 | 2.120 | 1.861 |  | 0.61 | 1.00 | 1 | False | False |
| baselines-margin | trailing4 | W2 | 1 | PIT | 9 | 3.40 | 3.18 | 4.33 | 0.07 | 0.42 | 7.735 | 6.388 |  | 2.44 | 0.78 | 2 | False | False |
| baselines-margin | seasonal_naive | W2 | 1 | full_sample | 9 | 0.44 | 0.50 | 0.49 | 0.04 | -0.07 | 1.000 | 1.000 |  | 0.38 | 1.00 | 1 | False | False |
| baselines-margin | seasonal_naive_drift | W2 | 1 | full_sample | 9 | 0.93 | 0.93 | 1.05 | 0.18 | -0.13 | 2.120 | 1.861 |  | 0.61 | 1.00 | 1 | False | False |
| baselines-margin | trailing4 | W2 | 1 | full_sample | 9 | 3.40 | 3.18 | 4.33 | 0.07 | 0.42 | 7.735 | 6.388 |  | 2.44 | 0.78 | 2 | False | False |
| baselines-margin | seasonal_naive | W2 | 2 | PIT | 8 | 0.49 | 0.52 | 0.52 | 0.05 | -0.07 | 1.000 | 1.000 |  | 0.39 | 1.00 | 1 | False | False |
| baselines-margin | seasonal_naive_drift | W2 | 2 | PIT | 8 | 0.81 | 0.71 | 1.08 | 0.26 | -0.04 | 1.659 | 1.366 |  | 0.66 | 1.00 | 1 | False | False |
| baselines-margin | trailing4 | W2 | 2 | PIT | 8 | 3.72 | 3.29 | 4.64 | -0.04 | 0.42 | 7.587 | 6.312 |  | 2.63 | 0.75 | 2 | False | False |
| baselines-margin | seasonal_naive | W2 | 2 | full_sample | 8 | 0.49 | 0.52 | 0.52 | 0.05 | -0.07 | 1.000 | 1.000 |  | 0.37 | 1.00 | 1 | False | False |
| baselines-margin | seasonal_naive_drift | W2 | 2 | full_sample | 8 | 0.81 | 0.71 | 1.08 | 0.26 | -0.04 | 1.659 | 1.366 |  | 0.64 | 1.00 | 1 | False | False |
| baselines-margin | trailing4 | W2 | 2 | full_sample | 8 | 3.72 | 3.29 | 4.64 | -0.04 | 0.42 | 7.587 | 6.312 |  | 2.63 | 0.75 | 2 | False | False |

## target: `capex_musd`

| method | object | window | h | replay | n | mae | rw_mae | rmse | bias | rw_bias | r_sn | rw_r_sn | r_street | crps | cov80 | n_params | both | rw_both |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| baselines-margin | seasonal_naive_drift | W1 | 0 | PIT | 14 | 4.71 | 5.03 | 5.84 | -0.00 | -0.80 | 0.868 | 1.026 |  | 3.43 | 0.57 | 1 | True | False |
| baselines-margin | seasonal_naive | W1 | 0 | PIT | 14 | 5.43 | 4.91 | 6.30 | -0.57 | 0.23 | 1.000 | 1.000 |  | 3.83 | 0.57 | 1 | False | False |
| baselines-margin | seasonal_naive_drift | W1 | 0 | full_sample | 14 | 4.71 | 5.03 | 5.84 | -0.00 | -0.80 | 0.868 | 1.026 |  | 3.30 | 0.71 | 1 | True | False |
| baselines-margin | seasonal_naive | W1 | 0 | full_sample | 14 | 5.43 | 4.91 | 6.30 | -0.57 | 0.23 | 1.000 | 1.000 |  | 3.58 | 0.64 | 1 | False | False |
| baselines-margin | seasonal_naive | W1 | 1 | PIT | 13 | 5.85 | 5.00 | 6.54 | -0.62 | 0.23 | 1.000 | 1.000 |  | 4.25 | 0.54 | 1 | False | False |
| baselines-margin | seasonal_naive_drift | W1 | 1 | PIT | 13 | 7.85 | 8.25 | 9.18 | 0.31 | -0.17 | 1.342 | 1.651 |  | 5.65 | 0.54 | 1 | False | False |
| baselines-margin | seasonal_naive | W1 | 1 | full_sample | 13 | 5.85 | 5.00 | 6.54 | -0.62 | 0.23 | 1.000 | 1.000 |  | 3.75 | 0.62 | 1 | False | False |
| baselines-margin | seasonal_naive_drift | W1 | 1 | full_sample | 13 | 7.85 | 8.25 | 9.18 | 0.31 | -0.17 | 1.342 | 1.651 |  | 5.21 | 0.85 | 1 | False | False |
| baselines-margin | seasonal_naive | W1 | 2 | PIT | 12 | 6.00 | 5.02 | 6.71 | -0.33 | 0.33 | 1.000 | 1.000 |  | 4.41 | 0.50 | 1 | False | False |
| baselines-margin | seasonal_naive_drift | W1 | 2 | PIT | 12 | 9.25 | 8.28 | 10.90 | 0.92 | 0.49 | 1.542 | 1.650 |  | 7.35 | 0.42 | 1 | False | False |
| baselines-margin | seasonal_naive | W1 | 2 | full_sample | 12 | 6.00 | 5.02 | 6.71 | -0.33 | 0.33 | 1.000 | 1.000 |  | 3.86 | 0.58 | 1 | False | False |
| baselines-margin | seasonal_naive_drift | W1 | 2 | full_sample | 12 | 9.25 | 8.28 | 10.90 | 0.92 | 0.49 | 1.542 | 1.650 |  | 6.26 | 0.75 | 1 | False | False |
| baselines-margin | seasonal_naive_drift | W2 | 0 | PIT | 10 | 5.30 | 5.25 | 6.49 | 0.50 | -0.73 | 0.981 | 1.101 |  | 3.91 | 0.60 | 1 | True | False |
| baselines-margin | seasonal_naive | W2 | 0 | PIT | 10 | 5.40 | 4.77 | 6.15 | 1.40 | 0.92 | 1.000 | 1.000 |  | 3.64 | 0.70 | 1 | False | False |
| baselines-margin | seasonal_naive_drift | W2 | 0 | full_sample | 10 | 5.30 | 5.25 | 6.49 | 0.50 | -0.73 | 0.981 | 1.101 |  | 3.76 | 0.60 | 1 | True | False |
| baselines-margin | seasonal_naive | W2 | 0 | full_sample | 10 | 5.40 | 4.77 | 6.15 | 1.40 | 0.92 | 1.000 | 1.000 |  | 3.50 | 0.70 | 1 | False | False |
| baselines-margin | seasonal_naive | W2 | 1 | PIT | 9 | 5.11 | 4.63 | 5.91 | 2.44 | 1.29 | 1.000 | 1.000 |  | 3.54 | 0.78 | 1 | False | False |
| baselines-margin | seasonal_naive_drift | W2 | 1 | PIT | 9 | 9.67 | 8.86 | 10.48 | 1.89 | 0.21 | 1.891 | 1.912 |  | 6.76 | 0.56 | 1 | False | False |
| baselines-margin | seasonal_naive | W2 | 1 | full_sample | 9 | 5.11 | 4.63 | 5.91 | 2.44 | 1.29 | 1.000 | 1.000 |  | 3.33 | 0.78 | 1 | False | False |
| baselines-margin | seasonal_naive_drift | W2 | 1 | full_sample | 9 | 9.67 | 8.86 | 10.48 | 1.89 | 0.21 | 1.891 | 1.912 |  | 6.19 | 0.78 | 1 | False | False |
| baselines-margin | seasonal_naive | W2 | 2 | PIT | 8 | 5.62 | 4.82 | 6.25 | 2.62 | 1.31 | 1.000 | 1.000 |  | 3.85 | 0.62 | 1 | False | False |
| baselines-margin | seasonal_naive_drift | W2 | 2 | PIT | 8 | 10.38 | 8.46 | 12.27 | 2.38 | 0.71 | 1.844 | 1.754 |  | 8.21 | 0.62 | 1 | False | False |
| baselines-margin | seasonal_naive | W2 | 2 | full_sample | 8 | 5.62 | 4.82 | 6.25 | 2.62 | 1.31 | 1.000 | 1.000 |  | 3.55 | 0.75 | 1 | False | False |
| baselines-margin | seasonal_naive_drift | W2 | 2 | full_sample | 8 | 10.38 | 8.46 | 12.27 | 2.38 | 0.71 | 1.844 | 1.754 |  | 7.20 | 0.62 | 1 | False | False |

## target: `cfo_musd`

| method | object | window | h | replay | n | mae | rw_mae | rmse | bias | rw_bias | r_sn | rw_r_sn | r_street | crps | cov80 | n_params | both | rw_both |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| baselines-margin | seasonal_naive | W1 | 0 | PIT | 14 | 236.14 | 203.43 | 267.91 | -102.14 | -96.41 | 1.000 | 1.000 |  | 154.15 | 0.79 | 1 | False | False |
| baselines-margin | seasonal_naive_drift | W1 | 0 | PIT | 14 | 374.86 | 331.85 | 430.22 | -15.29 | -41.50 | 1.587 | 1.631 |  | 245.84 | 0.79 | 1 | False | False |
| baselines-margin | seasonal_naive | W1 | 0 | full_sample | 14 | 236.14 | 203.43 | 267.91 | -102.14 | -96.41 | 1.000 | 1.000 |  | 153.79 | 0.71 | 1 | False | False |
| baselines-margin | seasonal_naive_drift | W1 | 0 | full_sample | 14 | 374.86 | 331.85 | 430.22 | -15.29 | -41.50 | 1.587 | 1.631 |  | 243.15 | 0.79 | 1 | False | False |
| baselines-margin | seasonal_naive | W1 | 1 | PIT | 13 | 224.69 | 200.03 | 256.70 | -80.38 | -91.01 | 1.000 | 1.000 |  | 151.39 | 0.69 | 1 | False | False |
| baselines-margin | seasonal_naive_drift | W1 | 1 | PIT | 13 | 284.92 | 296.58 | 348.22 | 19.38 | -7.37 | 1.268 | 1.483 |  | 199.22 | 0.69 | 1 | False | False |
| baselines-margin | seasonal_naive | W1 | 1 | full_sample | 13 | 224.69 | 200.03 | 256.70 | -80.38 | -91.01 | 1.000 | 1.000 |  | 147.16 | 0.77 | 1 | False | False |
| baselines-margin | seasonal_naive_drift | W1 | 1 | full_sample | 13 | 284.92 | 296.58 | 348.22 | 19.38 | -7.37 | 1.268 | 1.483 |  | 195.73 | 0.69 | 1 | False | False |
| baselines-margin | seasonal_naive_drift | W1 | 2 | PIT | 12 | 210.00 | 143.01 | 285.99 | 25.00 | -1.88 | 0.896 | 0.708 |  | 158.67 | 0.83 | 1 | True | True |
| baselines-margin | seasonal_naive | W1 | 2 | PIT | 12 | 234.42 | 202.13 | 265.36 | -78.08 | -90.63 | 1.000 | 1.000 |  | 157.09 | 0.67 | 1 | False | False |
| baselines-margin | seasonal_naive_drift | W1 | 2 | full_sample | 12 | 210.00 | 143.01 | 285.99 | 25.00 | -1.88 | 0.896 | 0.708 |  | 152.23 | 0.92 | 1 | True | True |
| baselines-margin | seasonal_naive | W1 | 2 | full_sample | 12 | 234.42 | 202.13 | 265.36 | -78.08 | -90.63 | 1.000 | 1.000 |  | 153.06 | 0.67 | 1 | False | False |
| baselines-margin | seasonal_naive | W2 | 0 | PIT | 10 | 205.20 | 190.80 | 235.52 | -97.60 | -99.62 | 1.000 | 1.000 |  | 134.78 | 1.00 | 1 | False | False |
| baselines-margin | seasonal_naive_drift | W2 | 0 | PIT | 10 | 365.30 | 321.34 | 421.78 | -69.50 | -65.20 | 1.780 | 1.684 |  | 241.84 | 0.80 | 1 | False | False |
| baselines-margin | seasonal_naive | W2 | 0 | full_sample | 10 | 205.20 | 190.80 | 235.52 | -97.60 | -99.62 | 1.000 | 1.000 |  | 135.88 | 0.90 | 1 | False | False |
| baselines-margin | seasonal_naive_drift | W2 | 0 | full_sample | 10 | 365.30 | 321.34 | 421.78 | -69.50 | -65.20 | 1.780 | 1.684 |  | 239.99 | 0.80 | 1 | False | False |
| baselines-margin | seasonal_naive | W2 | 1 | PIT | 9 | 190.67 | 184.65 | 221.56 | -71.11 | -89.61 | 1.000 | 1.000 |  | 129.68 | 0.89 | 1 | False | False |
| baselines-margin | seasonal_naive_drift | W2 | 1 | PIT | 9 | 346.67 | 315.51 | 382.44 | -30.89 | -27.54 | 1.818 | 1.709 |  | 223.35 | 0.67 | 1 | False | False |
| baselines-margin | seasonal_naive | W2 | 1 | full_sample | 9 | 190.67 | 184.65 | 221.56 | -71.11 | -89.61 | 1.000 | 1.000 |  | 127.50 | 0.89 | 1 | False | False |
| baselines-margin | seasonal_naive_drift | W2 | 1 | full_sample | 9 | 346.67 | 315.51 | 382.44 | -30.89 | -27.54 | 1.818 | 1.709 |  | 220.12 | 0.67 | 1 | False | False |
| baselines-margin | seasonal_naive_drift | W2 | 2 | PIT | 8 | 126.00 | 106.80 | 152.84 | -24.50 | -24.24 | 0.640 | 0.571 |  | 111.24 | 1.00 | 1 | True | True |
| baselines-margin | seasonal_naive | W2 | 2 | PIT | 8 | 196.75 | 186.91 | 229.57 | -62.25 | -86.83 | 1.000 | 1.000 |  | 132.10 | 0.88 | 1 | False | False |
| baselines-margin | seasonal_naive_drift | W2 | 2 | full_sample | 8 | 126.00 | 106.80 | 152.84 | -24.50 | -24.24 | 0.640 | 0.571 |  | 99.34 | 1.00 | 1 | True | True |
| baselines-margin | seasonal_naive | W2 | 2 | full_sample | 8 | 196.75 | 186.91 | 229.57 | -62.25 | -86.83 | 1.000 | 1.000 |  | 131.23 | 0.88 | 1 | False | False |

## target: `cor_cash_musd`

| method | object | window | h | replay | n | mae | rw_mae | rmse | bias | rw_bias | r_sn | rw_r_sn | r_street | crps | cov80 | n_params | both | rw_both |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| baselines-margin | seasonal_naive_drift | W1 | 0 | PIT | 14 | 24.44 | 23.72 | 28.79 | -2.82 | -6.06 | 0.456 | 0.390 |  | 16.37 | 0.79 | 1 | True | True |
| baselines-margin | seasonal_naive | W1 | 0 | PIT | 14 | 53.65 | 60.80 | 58.12 | -53.65 | -60.80 | 1.000 | 1.000 |  | 37.77 | 0.57 | 1 | False | False |
| baselines-margin | pct_rev_last4 | W1 | 0 | PIT | 14 | 73.77 | 66.13 | 102.13 | 14.01 | 5.82 | 1.375 | 1.088 |  | 55.23 | 0.64 | 3 | False | False |
| baselines-margin | seasonal_naive_drift | W1 | 0 | full_sample | 14 | 24.44 | 23.72 | 28.79 | -2.82 | -6.06 | 0.456 | 0.390 |  | 16.09 | 0.79 | 1 | True | True |
| baselines-margin | seasonal_naive | W1 | 0 | full_sample | 14 | 53.65 | 60.80 | 58.12 | -53.65 | -60.80 | 1.000 | 1.000 |  | 33.96 | 0.57 | 1 | False | False |
| baselines-margin | pct_rev_last4 | W1 | 0 | full_sample | 14 | 73.53 | 66.15 | 101.87 | 14.49 | 7.61 | 1.371 | 1.088 |  | 54.00 | 0.57 | 3 | False | False |
| baselines-margin | seasonal_naive_drift | W1 | 1 | PIT | 13 | 21.45 | 23.95 | 27.25 | -3.78 | -10.26 | 0.407 | 0.394 |  | 15.82 | 0.77 | 1 | True | True |
| baselines-margin | seasonal_naive | W1 | 1 | PIT | 13 | 52.75 | 60.72 | 57.52 | -52.75 | -60.72 | 1.000 | 1.000 |  | 36.67 | 0.54 | 1 | False | False |
| baselines-margin | pct_rev_last4 | W1 | 1 | PIT | 13 | 79.09 | 71.89 | 109.35 | 25.69 | 1.43 | 1.499 | 1.184 |  | 57.20 | 0.85 | 3 | False | False |
| baselines-margin | seasonal_naive_drift | W1 | 1 | full_sample | 13 | 21.45 | 23.95 | 27.25 | -3.78 | -10.26 | 0.407 | 0.394 |  | 15.20 | 0.85 | 1 | True | True |
| baselines-margin | seasonal_naive | W1 | 1 | full_sample | 13 | 52.75 | 60.72 | 57.52 | -52.75 | -60.72 | 1.000 | 1.000 |  | 34.20 | 0.54 | 1 | False | False |
| baselines-margin | pct_rev_last4 | W1 | 1 | full_sample | 13 | 79.09 | 71.89 | 109.35 | 25.69 | 1.43 | 1.499 | 1.184 |  | 57.54 | 0.77 | 3 | False | False |
| baselines-margin | seasonal_naive_drift | W1 | 2 | PIT | 12 | 25.00 | 26.51 | 28.66 | -5.60 | -12.75 | 0.466 | 0.433 |  | 16.84 | 0.83 | 1 | True | True |
| baselines-margin | seasonal_naive | W1 | 2 | PIT | 12 | 53.65 | 61.15 | 58.63 | -53.65 | -61.15 | 1.000 | 1.000 |  | 37.57 | 0.25 | 1 | False | False |
| baselines-margin | pct_rev_last4 | W1 | 2 | PIT | 12 | 93.09 | 84.59 | 121.49 | 30.41 | 2.89 | 1.735 | 1.383 |  | 66.55 | 0.75 | 3 | False | False |
| baselines-margin | seasonal_naive_drift | W1 | 2 | full_sample | 12 | 25.00 | 26.51 | 28.66 | -5.60 | -12.75 | 0.466 | 0.433 |  | 16.43 | 1.00 | 1 | True | True |
| baselines-margin | seasonal_naive | W1 | 2 | full_sample | 12 | 53.65 | 61.15 | 58.63 | -53.65 | -61.15 | 1.000 | 1.000 |  | 37.87 | 0.25 | 1 | False | False |
| baselines-margin | pct_rev_last4 | W1 | 2 | full_sample | 12 | 93.09 | 84.59 | 121.49 | 30.41 | 2.89 | 1.735 | 1.383 |  | 64.10 | 0.75 | 3 | False | False |
| baselines-margin | seasonal_naive_drift | W2 | 0 | PIT | 10 | 26.80 | 24.28 | 31.92 | -5.00 | -7.14 | 0.490 | 0.392 |  | 18.59 | 0.70 | 1 | True | True |
| baselines-margin | seasonal_naive | W2 | 0 | PIT | 10 | 54.70 | 62.00 | 60.32 | -54.70 | -62.00 | 1.000 | 1.000 |  | 40.23 | 0.50 | 1 | False | False |
| baselines-margin | pct_rev_last4 | W2 | 0 | PIT | 10 | 73.53 | 65.41 | 104.05 | 6.62 | 2.03 | 1.344 | 1.055 |  | 55.97 | 0.70 | 3 | False | False |
| baselines-margin | seasonal_naive_drift | W2 | 0 | full_sample | 10 | 26.80 | 24.28 | 31.92 | -5.00 | -7.14 | 0.490 | 0.392 |  | 18.20 | 0.70 | 1 | True | True |
| baselines-margin | seasonal_naive | W2 | 0 | full_sample | 10 | 54.70 | 62.00 | 60.32 | -54.70 | -62.00 | 1.000 | 1.000 |  | 34.96 | 0.60 | 1 | False | False |
| baselines-margin | pct_rev_last4 | W2 | 0 | full_sample | 10 | 73.53 | 65.56 | 104.34 | 8.20 | 4.25 | 1.344 | 1.057 |  | 55.26 | 0.60 | 3 | False | False |
| baselines-margin | seasonal_naive_drift | W2 | 1 | PIT | 9 | 28.33 | 26.37 | 32.48 | -8.11 | -12.39 | 0.515 | 0.422 |  | 19.26 | 0.67 | 1 | True | True |
| baselines-margin | seasonal_naive | W2 | 1 | PIT | 9 | 55.00 | 62.42 | 61.18 | -55.00 | -62.42 | 1.000 | 1.000 |  | 40.27 | 0.44 | 1 | False | False |
| baselines-margin | pct_rev_last4 | W2 | 1 | PIT | 9 | 74.54 | 69.75 | 110.14 | 17.72 | -2.35 | 1.355 | 1.117 |  | 57.16 | 0.78 | 3 | False | False |
| baselines-margin | seasonal_naive_drift | W2 | 1 | full_sample | 9 | 28.33 | 26.37 | 32.48 | -8.11 | -12.39 | 0.515 | 0.422 |  | 18.74 | 0.78 | 1 | True | True |
| baselines-margin | seasonal_naive | W2 | 1 | full_sample | 9 | 55.00 | 62.42 | 61.18 | -55.00 | -62.42 | 1.000 | 1.000 |  | 36.47 | 0.44 | 1 | False | False |
| baselines-margin | pct_rev_last4 | W2 | 1 | full_sample | 9 | 74.54 | 69.75 | 110.14 | 17.72 | -2.35 | 1.355 | 1.117 |  | 57.68 | 0.78 | 3 | False | False |
| baselines-margin | seasonal_naive_drift | W2 | 2 | PIT | 8 | 29.88 | 28.36 | 33.03 | -7.38 | -14.29 | 0.568 | 0.459 |  | 19.29 | 0.75 | 1 | True | True |
| baselines-margin | seasonal_naive | W2 | 2 | PIT | 8 | 52.62 | 61.81 | 59.38 | -52.62 | -61.81 | 1.000 | 1.000 |  | 37.69 | 0.38 | 1 | False | False |
| baselines-margin | pct_rev_last4 | W2 | 2 | PIT | 8 | 94.28 | 85.31 | 124.19 | 22.36 | -2.12 | 1.791 | 1.380 |  | 67.79 | 0.75 | 3 | False | False |
| baselines-margin | seasonal_naive_drift | W2 | 2 | full_sample | 8 | 29.88 | 28.36 | 33.03 | -7.38 | -14.29 | 0.568 | 0.459 |  | 19.09 | 1.00 | 1 | True | True |
| baselines-margin | seasonal_naive | W2 | 2 | full_sample | 8 | 52.62 | 61.81 | 59.38 | -52.62 | -61.81 | 1.000 | 1.000 |  | 37.37 | 0.38 | 1 | False | False |
| baselines-margin | pct_rev_last4 | W2 | 2 | full_sample | 8 | 94.28 | 85.31 | 124.19 | 22.36 | -2.12 | 1.791 | 1.380 |  | 65.62 | 0.75 | 3 | False | False |

## target: `cor_cash_per_night`

| method | object | window | h | replay | n | mae | rw_mae | rmse | bias | rw_bias | r_sn | rw_r_sn | r_street | crps | cov80 | n_params | both | rw_both |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| baselines-margin | seasonal_naive | W1 | 0 | PIT | 14 | 0.12 | 0.16 | 0.17 | -0.06 | -0.11 | 1.000 | 1.000 |  | 0.10 | 0.79 | 1 | False | False |
| baselines-margin | seasonal_naive_drift | W1 | 0 | PIT | 14 | 0.14 | 0.14 | 0.20 | -0.02 | -0.03 | 1.159 | 0.874 |  | 0.12 | 0.86 | 1 | False | True |
| baselines-margin | trailing4 | W1 | 0 | PIT | 14 | 0.19 | 0.21 | 0.21 | -0.03 | -0.07 | 1.524 | 1.316 |  | 0.12 | 0.57 | 2 | False | False |
| baselines-margin | seasonal_naive | W1 | 0 | full_sample | 14 | 0.12 | 0.16 | 0.17 | -0.06 | -0.11 | 1.000 | 1.000 |  | 0.09 | 0.86 | 1 | False | False |
| baselines-margin | seasonal_naive_drift | W1 | 0 | full_sample | 14 | 0.14 | 0.14 | 0.20 | -0.02 | -0.03 | 1.159 | 0.874 |  | 0.12 | 0.93 | 1 | False | True |
| baselines-margin | trailing4 | W1 | 0 | full_sample | 14 | 0.19 | 0.21 | 0.21 | -0.03 | -0.07 | 1.524 | 1.316 |  | 0.12 | 0.71 | 2 | False | False |
| baselines-margin | seasonal_naive | W1 | 1 | PIT | 13 | 0.13 | 0.16 | 0.17 | -0.07 | -0.11 | 1.000 | 1.000 |  | 0.10 | 0.69 | 1 | False | False |
| baselines-margin | seasonal_naive_drift | W1 | 1 | PIT | 13 | 0.17 | 0.17 | 0.21 | -0.04 | -0.05 | 1.295 | 1.073 |  | 0.14 | 1.00 | 1 | False | False |
| baselines-margin | trailing4 | W1 | 1 | PIT | 13 | 0.19 | 0.22 | 0.21 | -0.06 | -0.10 | 1.428 | 1.361 |  | 0.12 | 0.77 | 2 | False | False |
| baselines-margin | seasonal_naive | W1 | 1 | full_sample | 13 | 0.13 | 0.16 | 0.17 | -0.07 | -0.11 | 1.000 | 1.000 |  | 0.10 | 0.77 | 1 | False | False |
| baselines-margin | seasonal_naive_drift | W1 | 1 | full_sample | 13 | 0.17 | 0.17 | 0.21 | -0.04 | -0.05 | 1.295 | 1.073 |  | 0.13 | 1.00 | 1 | False | False |
| baselines-margin | trailing4 | W1 | 1 | full_sample | 13 | 0.19 | 0.22 | 0.21 | -0.06 | -0.10 | 1.428 | 1.361 |  | 0.12 | 0.85 | 2 | False | False |
| baselines-margin | seasonal_naive | W1 | 2 | PIT | 12 | 0.14 | 0.16 | 0.18 | -0.07 | -0.12 | 1.000 | 1.000 |  | 0.10 | 0.58 | 1 | False | False |
| baselines-margin | trailing4 | W1 | 2 | PIT | 12 | 0.19 | 0.21 | 0.22 | -0.08 | -0.12 | 1.351 | 1.307 |  | 0.13 | 0.75 | 2 | False | False |
| baselines-margin | seasonal_naive_drift | W1 | 2 | PIT | 12 | 0.20 | 0.21 | 0.23 | -0.06 | -0.07 | 1.409 | 1.276 |  | 0.13 | 0.83 | 1 | False | False |
| baselines-margin | seasonal_naive | W1 | 2 | full_sample | 12 | 0.14 | 0.16 | 0.18 | -0.07 | -0.12 | 1.000 | 1.000 |  | 0.10 | 0.67 | 1 | False | False |
| baselines-margin | trailing4 | W1 | 2 | full_sample | 12 | 0.19 | 0.21 | 0.22 | -0.08 | -0.12 | 1.351 | 1.307 |  | 0.13 | 0.75 | 2 | False | False |
| baselines-margin | seasonal_naive_drift | W1 | 2 | full_sample | 12 | 0.20 | 0.21 | 0.23 | -0.06 | -0.07 | 1.409 | 1.276 |  | 0.13 | 0.83 | 1 | False | False |
| baselines-margin | seasonal_naive | W2 | 0 | PIT | 10 | 0.16 | 0.17 | 0.20 | -0.09 | -0.12 | 1.000 | 1.000 |  | 0.11 | 0.70 | 1 | False | False |
| baselines-margin | seasonal_naive_drift | W2 | 0 | PIT | 10 | 0.18 | 0.15 | 0.24 | -0.02 | -0.03 | 1.094 | 0.856 |  | 0.13 | 0.80 | 1 | False | True |
| baselines-margin | trailing4 | W2 | 0 | PIT | 10 | 0.20 | 0.21 | 0.22 | -0.04 | -0.07 | 1.203 | 1.237 |  | 0.13 | 0.60 | 2 | False | False |
| baselines-margin | seasonal_naive | W2 | 0 | full_sample | 10 | 0.16 | 0.17 | 0.20 | -0.09 | -0.12 | 1.000 | 1.000 |  | 0.11 | 0.80 | 1 | False | False |
| baselines-margin | seasonal_naive_drift | W2 | 0 | full_sample | 10 | 0.18 | 0.15 | 0.24 | -0.02 | -0.03 | 1.094 | 0.856 |  | 0.13 | 0.90 | 1 | False | True |
| baselines-margin | trailing4 | W2 | 0 | full_sample | 10 | 0.20 | 0.21 | 0.22 | -0.04 | -0.07 | 1.203 | 1.237 |  | 0.13 | 0.70 | 2 | False | False |
| baselines-margin | seasonal_naive | W2 | 1 | PIT | 9 | 0.17 | 0.18 | 0.20 | -0.09 | -0.12 | 1.000 | 1.000 |  | 0.12 | 0.56 | 1 | False | False |
| baselines-margin | trailing4 | W2 | 1 | PIT | 9 | 0.21 | 0.23 | 0.23 | -0.08 | -0.11 | 1.194 | 1.292 |  | 0.13 | 0.67 | 2 | False | False |
| baselines-margin | seasonal_naive_drift | W2 | 1 | PIT | 9 | 0.22 | 0.19 | 0.25 | -0.04 | -0.05 | 1.276 | 1.067 |  | 0.14 | 1.00 | 1 | False | False |
| baselines-margin | seasonal_naive | W2 | 1 | full_sample | 9 | 0.17 | 0.18 | 0.20 | -0.09 | -0.12 | 1.000 | 1.000 |  | 0.12 | 0.67 | 1 | False | False |
| baselines-margin | trailing4 | W2 | 1 | full_sample | 9 | 0.21 | 0.23 | 0.23 | -0.08 | -0.11 | 1.194 | 1.292 |  | 0.13 | 0.78 | 2 | False | False |
| baselines-margin | seasonal_naive_drift | W2 | 1 | full_sample | 9 | 0.22 | 0.19 | 0.25 | -0.04 | -0.05 | 1.276 | 1.067 |  | 0.15 | 1.00 | 1 | False | False |
| baselines-margin | seasonal_naive | W2 | 2 | PIT | 8 | 0.16 | 0.17 | 0.19 | -0.06 | -0.12 | 1.000 | 1.000 |  | 0.11 | 0.50 | 1 | False | False |
| baselines-margin | trailing4 | W2 | 2 | PIT | 8 | 0.20 | 0.22 | 0.24 | -0.08 | -0.12 | 1.230 | 1.287 |  | 0.14 | 0.62 | 2 | False | False |
| baselines-margin | seasonal_naive_drift | W2 | 2 | PIT | 8 | 0.24 | 0.22 | 0.25 | -0.03 | -0.06 | 1.490 | 1.301 |  | 0.15 | 0.75 | 1 | False | False |
| baselines-margin | seasonal_naive | W2 | 2 | full_sample | 8 | 0.16 | 0.17 | 0.19 | -0.06 | -0.12 | 1.000 | 1.000 |  | 0.11 | 0.62 | 1 | False | False |
| baselines-margin | trailing4 | W2 | 2 | full_sample | 8 | 0.20 | 0.22 | 0.24 | -0.08 | -0.12 | 1.230 | 1.287 |  | 0.14 | 0.62 | 2 | False | False |
| baselines-margin | seasonal_naive_drift | W2 | 2 | full_sample | 8 | 0.24 | 0.22 | 0.25 | -0.03 | -0.06 | 1.490 | 1.301 |  | 0.15 | 0.75 | 1 | False | False |

## target: `da_musd`

| method | object | window | h | replay | n | mae | rw_mae | rmse | bias | rw_bias | r_sn | rw_r_sn | r_street | crps | cov80 | n_params | both | rw_both |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| baselines-margin | seasonal_naive_drift | W1 | 0 | PIT | 14 | 3.36 | 3.07 | 4.73 | -0.93 | 0.79 | 0.485 | 0.569 |  | 2.99 | 0.86 | 1 | True | True |
| baselines-margin | pct_rev_last4 | W1 | 0 | PIT | 14 | 6.02 | 5.50 | 7.08 | 1.64 | 1.71 | 0.868 | 1.021 |  | 4.68 | 0.57 | 3 | True | False |
| baselines-margin | seasonal_naive | W1 | 0 | PIT | 14 | 6.93 | 5.39 | 8.50 | -0.21 | -1.45 | 1.000 | 1.000 |  | 5.07 | 0.57 | 1 | False | False |
| baselines-margin | seasonal_naive_drift | W1 | 0 | full_sample | 14 | 3.36 | 3.07 | 4.73 | -0.93 | 0.79 | 0.485 | 0.569 |  | 2.84 | 0.86 | 1 | True | True |
| baselines-margin | pct_rev_last4 | W1 | 0 | full_sample | 14 | 6.00 | 5.52 | 7.08 | 1.66 | 1.78 | 0.866 | 1.023 |  | 4.06 | 0.79 | 3 | True | False |
| baselines-margin | seasonal_naive | W1 | 0 | full_sample | 14 | 6.93 | 5.39 | 8.50 | -0.21 | -1.45 | 1.000 | 1.000 |  | 4.56 | 0.79 | 1 | False | False |
| baselines-margin | seasonal_naive_drift | W1 | 1 | PIT | 13 | 6.00 | 5.58 | 8.08 | -2.15 | 1.54 | 0.987 | 1.083 |  | 5.25 | 0.77 | 1 | True | False |
| baselines-margin | seasonal_naive | W1 | 1 | PIT | 13 | 6.08 | 5.16 | 7.27 | -1.62 | -1.82 | 1.000 | 1.000 |  | 4.54 | 0.54 | 1 | False | False |
| baselines-margin | pct_rev_last4 | W1 | 1 | PIT | 13 | 7.16 | 6.08 | 9.25 | 1.85 | 1.27 | 1.178 | 1.179 |  | 5.81 | 0.54 | 3 | False | False |
| baselines-margin | seasonal_naive_drift | W1 | 1 | full_sample | 13 | 6.00 | 5.58 | 8.08 | -2.15 | 1.54 | 0.987 | 1.083 |  | 5.06 | 0.77 | 1 | True | False |
| baselines-margin | seasonal_naive | W1 | 1 | full_sample | 13 | 6.08 | 5.16 | 7.27 | -1.62 | -1.82 | 1.000 | 1.000 |  | 4.07 | 0.77 | 1 | False | False |
| baselines-margin | pct_rev_last4 | W1 | 1 | full_sample | 13 | 7.16 | 6.08 | 9.25 | 1.85 | 1.27 | 1.178 | 1.179 |  | 4.92 | 0.69 | 3 | False | False |
| baselines-margin | seasonal_naive | W1 | 2 | PIT | 12 | 5.17 | 4.89 | 5.76 | -3.17 | -2.24 | 1.000 | 1.000 |  | 3.89 | 0.50 | 1 | False | False |
| baselines-margin | pct_rev_last4 | W1 | 2 | PIT | 12 | 6.99 | 6.18 | 10.57 | 1.23 | 0.46 | 1.352 | 1.264 |  | 5.62 | 0.67 | 3 | False | False |
| baselines-margin | seasonal_naive_drift | W1 | 2 | PIT | 12 | 9.00 | 8.01 | 11.06 | -3.83 | 1.62 | 1.742 | 1.639 |  | 8.84 | 0.67 | 1 | False | False |
| baselines-margin | seasonal_naive | W1 | 2 | full_sample | 12 | 5.17 | 4.89 | 5.76 | -3.17 | -2.24 | 1.000 | 1.000 |  | 3.56 | 0.83 | 1 | False | False |
| baselines-margin | pct_rev_last4 | W1 | 2 | full_sample | 12 | 6.99 | 6.18 | 10.57 | 1.23 | 0.46 | 1.352 | 1.264 |  | 5.08 | 0.75 | 3 | False | False |
| baselines-margin | seasonal_naive_drift | W1 | 2 | full_sample | 12 | 9.00 | 8.01 | 11.06 | -3.83 | 1.62 | 1.742 | 1.639 |  | 8.04 | 0.67 | 1 | False | False |
| baselines-margin | seasonal_naive_drift | W2 | 0 | PIT | 10 | 2.50 | 2.74 | 3.21 | 0.70 | 1.50 | 0.463 | 0.553 |  | 2.20 | 1.00 | 1 | True | True |
| baselines-margin | pct_rev_last4 | W2 | 0 | PIT | 10 | 5.03 | 5.21 | 6.35 | 0.02 | 1.38 | 0.932 | 1.053 |  | 3.75 | 0.80 | 3 | True | False |
| baselines-margin | seasonal_naive | W2 | 0 | PIT | 10 | 5.40 | 4.95 | 6.03 | -4.00 | -2.43 | 1.000 | 1.000 |  | 3.80 | 0.70 | 1 | False | False |
| baselines-margin | seasonal_naive_drift | W2 | 0 | full_sample | 10 | 2.50 | 2.74 | 3.21 | 0.70 | 1.50 | 0.463 | 0.553 |  | 2.00 | 1.00 | 1 | True | True |
| baselines-margin | pct_rev_last4 | W2 | 0 | full_sample | 10 | 5.05 | 5.23 | 6.39 | 0.09 | 1.48 | 0.934 | 1.056 |  | 3.66 | 0.80 | 3 | True | False |
| baselines-margin | seasonal_naive | W2 | 0 | full_sample | 10 | 5.40 | 4.95 | 6.03 | -4.00 | -2.43 | 1.000 | 1.000 |  | 3.76 | 0.80 | 1 | False | False |
| baselines-margin | seasonal_naive_drift | W2 | 1 | PIT | 9 | 4.11 | 4.89 | 4.89 | 1.44 | 3.18 | 0.725 | 0.971 |  | 3.31 | 1.00 | 1 | True | False |
| baselines-margin | pct_rev_last4 | W2 | 1 | PIT | 9 | 5.34 | 5.56 | 6.65 | -0.52 | 0.74 | 0.943 | 1.105 |  | 4.21 | 0.78 | 3 | False | False |
| baselines-margin | seasonal_naive | W2 | 1 | PIT | 9 | 5.67 | 5.03 | 6.28 | -4.11 | -2.40 | 1.000 | 1.000 |  | 4.16 | 0.67 | 1 | False | False |
| baselines-margin | seasonal_naive_drift | W2 | 1 | full_sample | 9 | 4.11 | 4.89 | 4.89 | 1.44 | 3.18 | 0.725 | 0.971 |  | 3.06 | 1.00 | 1 | True | False |
| baselines-margin | pct_rev_last4 | W2 | 1 | full_sample | 9 | 5.34 | 5.56 | 6.65 | -0.52 | 0.74 | 0.943 | 1.105 |  | 4.05 | 0.78 | 3 | False | False |
| baselines-margin | seasonal_naive | W2 | 1 | full_sample | 9 | 5.67 | 5.03 | 6.28 | -4.11 | -2.40 | 1.000 | 1.000 |  | 3.97 | 0.78 | 1 | False | False |
| baselines-margin | seasonal_naive_drift | W2 | 2 | PIT | 8 | 5.62 | 6.76 | 6.92 | 2.12 | 4.48 | 0.978 | 1.343 |  | 5.86 | 1.00 | 1 | False | False |
| baselines-margin | seasonal_naive | W2 | 2 | PIT | 8 | 5.75 | 5.03 | 6.42 | -4.00 | -2.26 | 1.000 | 1.000 |  | 4.36 | 0.75 | 1 | False | False |
| baselines-margin | pct_rev_last4 | W2 | 2 | PIT | 8 | 6.18 | 6.08 | 7.13 | -1.72 | -0.33 | 1.075 | 1.207 |  | 4.59 | 0.75 | 3 | False | False |
| baselines-margin | seasonal_naive_drift | W2 | 2 | full_sample | 8 | 5.62 | 6.76 | 6.92 | 2.12 | 4.48 | 0.978 | 1.343 |  | 5.24 | 1.00 | 1 | False | False |
| baselines-margin | seasonal_naive | W2 | 2 | full_sample | 8 | 5.75 | 5.03 | 6.42 | -4.00 | -2.26 | 1.000 | 1.000 |  | 4.10 | 0.75 | 1 | False | False |
| baselines-margin | pct_rev_last4 | W2 | 2 | full_sample | 8 | 6.18 | 6.08 | 7.13 | -1.72 | -0.33 | 1.075 | 1.207 |  | 4.49 | 0.75 | 3 | False | False |

## target: `diluted_shares_m`

| method | object | window | h | replay | n | mae | rw_mae | rmse | bias | rw_bias | r_sn | rw_r_sn | r_street | crps | cov80 | n_params | both | rw_both |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| baselines-margin | seasonal_naive_drift | W1 | 0 | PIT | 14 | 12.23 | 6.83 | 20.16 | 1.44 | 1.91 | 0.570 | 0.309 |  | 15.42 | 1.00 | 1 | True | True |
| baselines-margin | seasonal_naive | W1 | 0 | PIT | 14 | 21.45 | 22.11 | 22.65 | 16.49 | 20.84 | 1.000 | 1.000 |  | 36.48 | 0.79 | 1 | False | False |
| baselines-margin | seasonal_naive_drift | W1 | 0 | full_sample | 14 | 12.23 | 6.83 | 20.16 | 1.44 | 1.91 | 0.570 | 0.309 |  | 14.78 | 1.00 | 1 | True | True |
| baselines-margin | seasonal_naive | W1 | 0 | full_sample | 14 | 21.45 | 22.11 | 22.65 | 16.49 | 20.84 | 1.000 | 1.000 |  | 36.87 | 1.00 | 1 | False | False |
| baselines-margin | seasonal_naive_drift | W1 | 1 | PIT | 13 | 11.30 | 7.72 | 17.82 | 6.06 | 4.02 | 0.553 | 0.353 |  | 18.53 | 1.00 | 1 | True | True |
| baselines-margin | seasonal_naive | W1 | 1 | PIT | 13 | 20.43 | 21.88 | 21.44 | 20.43 | 21.88 | 1.000 | 1.000 |  | 13.42 | 0.77 | 1 | False | False |
| baselines-margin | seasonal_naive_drift | W1 | 1 | full_sample | 13 | 11.30 | 7.72 | 17.82 | 6.06 | 4.02 | 0.553 | 0.353 |  | 17.18 | 1.00 | 1 | True | True |
| baselines-margin | seasonal_naive | W1 | 1 | full_sample | 13 | 20.43 | 21.88 | 21.44 | 20.43 | 21.88 | 1.000 | 1.000 |  | 12.37 | 1.00 | 1 | False | False |
| baselines-margin | seasonal_naive_drift | W1 | 2 | PIT | 12 | 12.29 | 8.61 | 21.11 | 6.85 | 4.99 | 0.597 | 0.392 |  | 20.17 | 1.00 | 1 | True | True |
| baselines-margin | seasonal_naive | W1 | 2 | PIT | 12 | 20.59 | 21.95 | 21.67 | 20.59 | 21.95 | 1.000 | 1.000 |  | 13.73 | 0.83 | 1 | False | False |
| baselines-margin | seasonal_naive_drift | W1 | 2 | full_sample | 12 | 12.29 | 8.61 | 21.11 | 6.85 | 4.99 | 0.597 | 0.392 |  | 17.82 | 1.00 | 1 | True | True |
| baselines-margin | seasonal_naive | W1 | 2 | full_sample | 12 | 20.59 | 21.95 | 21.67 | 20.59 | 21.95 | 1.000 | 1.000 |  | 12.44 | 1.00 | 1 | False | False |
| baselines-margin | seasonal_naive_drift | W2 | 0 | PIT | 10 | 6.10 | 4.94 | 9.03 | -0.30 | 1.27 | 0.313 | 0.228 |  | 11.24 | 1.00 | 1 | True | True |
| baselines-margin | seasonal_naive | W2 | 0 | PIT | 10 | 19.50 | 21.67 | 20.51 | 19.50 | 21.67 | 1.000 | 1.000 |  | 27.40 | 0.70 | 1 | False | False |
| baselines-margin | seasonal_naive_drift | W2 | 0 | full_sample | 10 | 6.10 | 4.94 | 9.03 | -0.30 | 1.27 | 0.313 | 0.228 |  | 12.43 | 1.00 | 1 | True | True |
| baselines-margin | seasonal_naive | W2 | 0 | full_sample | 10 | 19.50 | 21.67 | 20.51 | 19.50 | 21.67 | 1.000 | 1.000 |  | 36.10 | 1.00 | 1 | False | False |
| baselines-margin | seasonal_naive_drift | W2 | 1 | PIT | 9 | 7.22 | 6.21 | 9.67 | 0.56 | 2.37 | 0.363 | 0.284 |  | 14.75 | 1.00 | 1 | True | True |
| baselines-margin | seasonal_naive | W2 | 1 | PIT | 9 | 19.89 | 21.91 | 20.95 | 19.89 | 21.91 | 1.000 | 1.000 |  | 13.13 | 0.67 | 1 | False | False |
| baselines-margin | seasonal_naive_drift | W2 | 1 | full_sample | 9 | 7.22 | 6.21 | 9.67 | 0.56 | 2.37 | 0.363 | 0.284 |  | 15.71 | 1.00 | 1 | True | True |
| baselines-margin | seasonal_naive | W2 | 1 | full_sample | 9 | 19.89 | 21.91 | 20.95 | 19.89 | 21.91 | 1.000 | 1.000 |  | 12.15 | 1.00 | 1 | False | False |
| baselines-margin | seasonal_naive_drift | W2 | 2 | PIT | 8 | 7.88 | 6.87 | 9.71 | 1.38 | 3.30 | 0.387 | 0.309 |  | 16.97 | 1.00 | 1 | True | True |
| baselines-margin | seasonal_naive | W2 | 2 | PIT | 8 | 20.38 | 22.22 | 21.49 | 20.38 | 22.22 | 1.000 | 1.000 |  | 13.29 | 0.75 | 1 | False | False |
| baselines-margin | seasonal_naive_drift | W2 | 2 | full_sample | 8 | 7.88 | 6.87 | 9.71 | 1.38 | 3.30 | 0.387 | 0.309 |  | 15.83 | 1.00 | 1 | True | True |
| baselines-margin | seasonal_naive | W2 | 2 | full_sample | 8 | 20.38 | 22.22 | 21.49 | 20.38 | 22.22 | 1.000 | 1.000 |  | 12.39 | 1.00 | 1 | False | False |

## target: `fcf_musd`

| method | object | window | h | replay | n | mae | rw_mae | rmse | bias | rw_bias | r_sn | rw_r_sn | r_street | crps | cov80 | n_params | both | rw_both |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| baselines-margin | seasonal_naive | W1 | 0 | PIT | 14 | 234.57 | 201.89 | 266.84 | -101.57 | -96.64 | 1.000 | 1.000 | 0.594 | 153.34 | 0.71 | 1 | False | False |
| baselines-margin | seasonal_naive_drift | W1 | 0 | PIT | 14 | 372.14 | 328.07 | 428.94 | -15.29 | -40.70 | 1.586 | 1.625 | 0.942 | 244.75 | 0.79 | 1 | False | False |
| baselines-margin | street | W1 | 0 | PIT | 14 | 395.05 | 431.37 | 507.03 | -131.65 | -183.39 | 1.684 | 2.137 | 1.000 | 281.95 | 0.86 | 1 | False | False |
| baselines-margin | seasonal_naive | W1 | 0 | full_sample | 14 | 234.57 | 201.89 | 266.84 | -101.57 | -96.64 | 1.000 | 1.000 | 0.594 | 153.16 | 0.79 | 1 | False | False |
| baselines-margin | seasonal_naive_drift | W1 | 0 | full_sample | 14 | 372.14 | 328.07 | 428.94 | -15.29 | -40.70 | 1.586 | 1.625 | 0.942 | 242.21 | 0.79 | 1 | False | False |
| baselines-margin | street | W1 | 0 | full_sample | 14 | 395.05 | 431.37 | 507.03 | -131.65 | -183.39 | 1.684 | 2.137 | 1.000 | 280.03 | 0.86 | 1 | False | False |
| baselines-margin | seasonal_naive | W1 | 1 | PIT | 13 | 223.00 | 198.47 | 255.50 | -79.77 | -91.25 | 1.000 | 1.000 | 0.457 | 150.49 | 0.69 | 1 | False | False |
| baselines-margin | seasonal_naive_drift | W1 | 1 | PIT | 13 | 285.38 | 295.52 | 348.01 | 19.08 | -7.21 | 1.280 | 1.489 | 0.585 | 199.43 | 0.69 | 1 | False | False |
| baselines-margin | street | W1 | 1 | PIT | 13 | 487.95 | 554.83 | 664.44 | -144.40 | -198.50 | 2.188 | 2.796 | 1.000 | 361.18 | 0.85 | 1 | False | False |
| baselines-margin | seasonal_naive | W1 | 1 | full_sample | 13 | 223.00 | 198.47 | 255.50 | -79.77 | -91.25 | 1.000 | 1.000 | 0.457 | 146.35 | 0.77 | 1 | False | False |
| baselines-margin | seasonal_naive_drift | W1 | 1 | full_sample | 13 | 285.38 | 295.52 | 348.01 | 19.08 | -7.21 | 1.280 | 1.489 | 0.585 | 196.07 | 0.69 | 1 | False | False |
| baselines-margin | street | W1 | 1 | full_sample | 13 | 487.95 | 554.83 | 664.44 | -144.40 | -198.50 | 2.188 | 2.796 | 1.000 | 360.20 | 0.85 | 1 | False | False |
| baselines-margin | seasonal_naive_drift | W1 | 2 | PIT | 12 | 211.08 | 143.47 | 287.21 | 24.08 | -2.37 | 0.906 | 0.715 |  | 159.13 | 0.83 | 1 | True | True |
| baselines-margin | seasonal_naive | W1 | 2 | PIT | 12 | 232.92 | 200.61 | 264.23 | -77.75 | -90.96 | 1.000 | 1.000 |  | 156.15 | 0.67 | 1 | False | False |
| baselines-margin | seasonal_naive_drift | W1 | 2 | full_sample | 12 | 211.08 | 143.47 | 287.21 | 24.08 | -2.37 | 0.906 | 0.715 |  | 152.35 | 0.92 | 1 | True | True |
| baselines-margin | seasonal_naive | W1 | 2 | full_sample | 12 | 232.92 | 200.61 | 264.23 | -77.75 | -90.96 | 1.000 | 1.000 |  | 152.32 | 0.67 | 1 | False | False |
| baselines-margin | seasonal_naive | W2 | 0 | PIT | 10 | 203.40 | 189.14 | 233.80 | -99.00 | -100.54 | 1.000 | 1.000 | 0.530 | 133.76 | 0.90 | 1 | False | False |
| baselines-margin | seasonal_naive_drift | W2 | 0 | PIT | 10 | 361.20 | 317.12 | 419.70 | -70.00 | -64.48 | 1.776 | 1.677 | 0.941 | 240.24 | 0.80 | 1 | False | False |
| baselines-margin | street | W2 | 0 | PIT | 10 | 383.92 | 433.03 | 507.11 | -118.80 | -193.84 | 1.888 | 2.289 | 1.000 | 280.74 | 0.90 | 1 | False | False |
| baselines-margin | seasonal_naive | W2 | 0 | full_sample | 10 | 203.40 | 189.14 | 233.80 | -99.00 | -100.54 | 1.000 | 1.000 | 0.530 | 134.93 | 0.90 | 1 | False | False |
| baselines-margin | seasonal_naive_drift | W2 | 0 | full_sample | 10 | 361.20 | 317.12 | 419.70 | -70.00 | -64.48 | 1.776 | 1.677 | 0.941 | 238.43 | 0.80 | 1 | False | False |
| baselines-margin | street | W2 | 0 | full_sample | 10 | 383.92 | 433.03 | 507.11 | -118.80 | -193.84 | 1.888 | 2.289 | 1.000 | 278.43 | 0.90 | 1 | False | False |
| baselines-margin | seasonal_naive | W2 | 1 | PIT | 9 | 189.56 | 183.26 | 220.87 | -73.56 | -90.91 | 1.000 | 1.000 | 0.438 | 129.17 | 0.89 | 1 | False | False |
| baselines-margin | seasonal_naive_drift | W2 | 1 | PIT | 9 | 345.89 | 313.89 | 381.36 | -32.78 | -27.76 | 1.825 | 1.713 | 0.800 | 222.97 | 0.67 | 1 | False | False |
| baselines-margin | street | W2 | 1 | PIT | 9 | 432.44 | 535.61 | 601.85 | -108.83 | -181.81 | 2.281 | 2.923 | 1.000 | 324.47 | 0.89 | 1 | False | False |
| baselines-margin | seasonal_naive | W2 | 1 | full_sample | 9 | 189.56 | 183.26 | 220.87 | -73.56 | -90.91 | 1.000 | 1.000 | 0.438 | 126.99 | 0.89 | 1 | False | False |
| baselines-margin | seasonal_naive_drift | W2 | 1 | full_sample | 9 | 345.89 | 313.89 | 381.36 | -32.78 | -27.76 | 1.825 | 1.713 | 0.800 | 219.91 | 0.67 | 1 | False | False |
| baselines-margin | street | W2 | 1 | full_sample | 9 | 432.44 | 535.61 | 601.85 | -108.83 | -181.81 | 2.281 | 2.923 | 1.000 | 323.46 | 0.89 | 1 | False | False |
| baselines-margin | seasonal_naive_drift | W2 | 2 | PIT | 8 | 128.88 | 107.86 | 154.10 | -26.88 | -24.96 | 0.660 | 0.582 |  | 112.11 | 1.00 | 1 | True | True |
| baselines-margin | seasonal_naive | W2 | 2 | PIT | 8 | 195.38 | 185.40 | 228.74 | -64.88 | -88.14 | 1.000 | 1.000 |  | 131.45 | 0.88 | 1 | False | False |
| baselines-margin | seasonal_naive_drift | W2 | 2 | full_sample | 8 | 128.88 | 107.86 | 154.10 | -26.88 | -24.96 | 0.660 | 0.582 |  | 100.08 | 1.00 | 1 | True | True |
| baselines-margin | seasonal_naive | W2 | 2 | full_sample | 8 | 195.38 | 185.40 | 228.74 | -64.88 | -88.14 | 1.000 | 1.000 |  | 130.77 | 0.88 | 1 | False | False |

## target: `ga_cash_ex_reserves_musd`

| method | object | window | h | replay | n | mae | rw_mae | rmse | bias | rw_bias | r_sn | rw_r_sn | r_street | crps | cov80 | n_params | both | rw_both |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| baselines-margin | seasonal_naive_drift | W1 | 0 | PIT | 14 | 15.75 | 18.46 | 19.88 | 4.23 | 6.45 | 0.765 | 0.928 |  | 16.50 | 0.86 | 1 | True | True |
| baselines-margin | seasonal_naive | W1 | 0 | PIT | 14 | 20.60 | 19.90 | 23.76 | -16.88 | -11.33 | 1.000 | 1.000 |  | 13.62 | 0.86 | 1 | False | False |
| baselines-margin | pct_rev_last4 | W1 | 0 | PIT | 14 | 39.74 | 40.14 | 55.08 | 16.88 | 20.62 | 1.930 | 2.017 |  | 28.23 | 0.86 | 3 | False | False |
| baselines-margin | seasonal_naive_drift | W1 | 0 | full_sample | 14 | 15.75 | 18.46 | 19.88 | 4.23 | 6.45 | 0.765 | 0.928 |  | 14.26 | 1.00 | 1 | True | True |
| baselines-margin | seasonal_naive | W1 | 0 | full_sample | 14 | 20.60 | 19.90 | 23.76 | -16.88 | -11.33 | 1.000 | 1.000 |  | 13.68 | 0.71 | 1 | False | False |
| baselines-margin | pct_rev_last4 | W1 | 0 | full_sample | 14 | 39.81 | 40.38 | 55.05 | 17.10 | 21.46 | 1.933 | 2.029 |  | 28.04 | 0.79 | 3 | False | False |
| baselines-margin | seasonal_naive | W1 | 1 | PIT | 13 | 20.37 | 19.84 | 23.78 | -16.37 | -11.10 | 1.000 | 1.000 |  | 14.68 | 0.54 | 1 | False | False |
| baselines-margin | seasonal_naive_drift | W1 | 1 | PIT | 13 | 21.12 | 29.87 | 26.85 | 7.06 | 12.34 | 1.037 | 1.506 |  | 18.24 | 0.77 | 1 | False | False |
| baselines-margin | pct_rev_last4 | W1 | 1 | PIT | 13 | 43.99 | 43.48 | 59.42 | 23.65 | 21.79 | 2.160 | 2.192 |  | 29.70 | 0.85 | 3 | False | False |
| baselines-margin | seasonal_naive | W1 | 1 | full_sample | 13 | 20.37 | 19.84 | 23.78 | -16.37 | -11.10 | 1.000 | 1.000 |  | 13.97 | 0.62 | 1 | False | False |
| baselines-margin | seasonal_naive_drift | W1 | 1 | full_sample | 13 | 21.12 | 29.87 | 26.85 | 7.06 | 12.34 | 1.037 | 1.506 |  | 15.45 | 1.00 | 1 | False | False |
| baselines-margin | pct_rev_last4 | W1 | 1 | full_sample | 13 | 43.99 | 43.48 | 59.42 | 23.65 | 21.79 | 2.160 | 2.192 |  | 30.26 | 0.85 | 3 | False | False |
| baselines-margin | seasonal_naive_drift | W1 | 2 | PIT | 12 | 16.89 | 23.30 | 23.70 | 7.66 | 10.77 | 0.875 | 1.193 |  | 16.12 | 0.92 | 1 | False | False |
| baselines-margin | seasonal_naive | W1 | 2 | PIT | 12 | 19.30 | 19.53 | 22.83 | -14.97 | -10.60 | 1.000 | 1.000 |  | 13.70 | 0.67 | 1 | False | False |
| baselines-margin | pct_rev_last4 | W1 | 2 | PIT | 12 | 47.17 | 44.60 | 65.00 | 27.99 | 23.62 | 2.443 | 2.284 |  | 33.59 | 0.83 | 3 | False | False |
| baselines-margin | seasonal_naive_drift | W1 | 2 | full_sample | 12 | 16.89 | 23.30 | 23.70 | 7.66 | 10.77 | 0.875 | 1.193 |  | 13.58 | 0.92 | 1 | False | False |
| baselines-margin | seasonal_naive | W1 | 2 | full_sample | 12 | 19.30 | 19.53 | 22.83 | -14.97 | -10.60 | 1.000 | 1.000 |  | 13.14 | 0.67 | 1 | False | False |
| baselines-margin | pct_rev_last4 | W1 | 2 | full_sample | 12 | 47.17 | 44.60 | 65.00 | 27.99 | 23.62 | 2.443 | 2.284 |  | 32.59 | 0.83 | 3 | False | False |
| baselines-margin | seasonal_naive_drift | W2 | 0 | PIT | 10 | 17.20 | 19.21 | 22.08 | 3.00 | 6.37 | 0.869 | 0.974 |  | 16.05 | 0.80 | 1 | True | True |
| baselines-margin | seasonal_naive | W2 | 0 | PIT | 10 | 19.80 | 19.72 | 23.79 | -14.60 | -10.23 | 1.000 | 1.000 |  | 13.65 | 0.80 | 1 | False | False |
| baselines-margin | pct_rev_last4 | W2 | 0 | PIT | 10 | 40.74 | 40.30 | 54.52 | 15.98 | 20.54 | 2.058 | 2.043 |  | 28.42 | 0.90 | 3 | False | False |
| baselines-margin | seasonal_naive_drift | W2 | 0 | full_sample | 10 | 17.20 | 19.21 | 22.08 | 3.00 | 6.37 | 0.869 | 0.974 |  | 15.17 | 1.00 | 1 | True | True |
| baselines-margin | seasonal_naive | W2 | 0 | full_sample | 10 | 19.80 | 19.72 | 23.79 | -14.60 | -10.23 | 1.000 | 1.000 |  | 13.56 | 0.70 | 1 | False | False |
| baselines-margin | pct_rev_last4 | W2 | 0 | full_sample | 10 | 40.96 | 40.60 | 54.92 | 16.73 | 21.58 | 2.069 | 2.059 |  | 28.44 | 0.80 | 3 | False | False |
| baselines-margin | seasonal_naive | W2 | 1 | PIT | 9 | 18.44 | 19.20 | 22.69 | -12.67 | -9.31 | 1.000 | 1.000 |  | 13.22 | 0.67 | 1 | False | False |
| baselines-margin | seasonal_naive_drift | W2 | 1 | PIT | 9 | 25.67 | 32.33 | 31.18 | 7.89 | 13.43 | 1.392 | 1.683 |  | 20.59 | 0.67 | 1 | False | False |
| baselines-margin | pct_rev_last4 | W2 | 1 | PIT | 9 | 44.43 | 43.76 | 59.68 | 24.11 | 22.52 | 2.409 | 2.279 |  | 30.08 | 0.89 | 3 | False | False |
| baselines-margin | seasonal_naive | W2 | 1 | full_sample | 9 | 18.44 | 19.20 | 22.69 | -12.67 | -9.31 | 1.000 | 1.000 |  | 12.80 | 0.78 | 1 | False | False |
| baselines-margin | seasonal_naive_drift | W2 | 1 | full_sample | 9 | 25.67 | 32.33 | 31.18 | 7.89 | 13.43 | 1.392 | 1.683 |  | 17.65 | 1.00 | 1 | False | False |
| baselines-margin | pct_rev_last4 | W2 | 1 | full_sample | 9 | 44.43 | 43.76 | 59.68 | 24.11 | 22.52 | 2.409 | 2.279 |  | 30.46 | 0.89 | 3 | False | False |
| baselines-margin | seasonal_naive | W2 | 2 | PIT | 8 | 17.88 | 19.00 | 22.65 | -11.38 | -8.58 | 1.000 | 1.000 |  | 13.08 | 0.75 | 1 | False | False |
| baselines-margin | seasonal_naive_drift | W2 | 2 | PIT | 8 | 20.88 | 25.93 | 27.73 | 7.62 | 11.56 | 1.168 | 1.365 |  | 17.89 | 0.88 | 1 | False | False |
| baselines-margin | pct_rev_last4 | W2 | 2 | PIT | 8 | 48.36 | 45.56 | 64.80 | 28.17 | 24.08 | 2.705 | 2.398 |  | 33.35 | 0.88 | 3 | False | False |
| baselines-margin | seasonal_naive | W2 | 2 | full_sample | 8 | 17.88 | 19.00 | 22.65 | -11.38 | -8.58 | 1.000 | 1.000 |  | 12.67 | 0.75 | 1 | False | False |
| baselines-margin | seasonal_naive_drift | W2 | 2 | full_sample | 8 | 20.88 | 25.93 | 27.73 | 7.62 | 11.56 | 1.168 | 1.365 |  | 15.48 | 0.88 | 1 | False | False |
| baselines-margin | pct_rev_last4 | W2 | 2 | full_sample | 8 | 48.36 | 45.56 | 64.80 | 28.17 | 24.08 | 2.705 | 2.398 |  | 32.75 | 0.88 | 3 | False | False |

## target: `ga_cash_musd`

| method | object | window | h | replay | n | mae | rw_mae | rmse | bias | rw_bias | r_sn | rw_r_sn | r_street | crps | cov80 | n_params | both | rw_both |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| baselines-margin | seasonal_naive | W1 | 0 | PIT | 14 | 162.81 | 117.35 | 361.71 | -22.10 | 8.10 | 1.000 | 1.000 |  | 157.16 | 0.86 | 1 | False | False |
| baselines-margin | pct_rev_last4 | W1 | 0 | PIT | 14 | 189.90 | 139.70 | 310.71 | 30.26 | 45.53 | 1.166 | 1.190 |  | 180.63 | 0.93 | 3 | False | False |
| baselines-margin | seasonal_naive_drift | W1 | 0 | PIT | 14 | 294.65 | 238.91 | 502.40 | 4.30 | 1.84 | 1.810 | 2.036 |  | 219.79 | 0.93 | 1 | False | False |
| baselines-margin | seasonal_naive | W1 | 0 | full_sample | 14 | 162.81 | 117.35 | 361.71 | -22.10 | 8.10 | 1.000 | 1.000 |  | 147.14 | 0.93 | 1 | False | False |
| baselines-margin | pct_rev_last4 | W1 | 0 | full_sample | 14 | 190.11 | 140.25 | 310.75 | 30.46 | 46.38 | 1.168 | 1.195 |  | 163.83 | 0.93 | 3 | False | False |
| baselines-margin | seasonal_naive_drift | W1 | 0 | full_sample | 14 | 294.65 | 238.91 | 502.40 | 4.30 | 1.84 | 1.810 | 2.036 |  | 218.18 | 0.86 | 1 | False | False |
| baselines-margin | seasonal_naive | W1 | 1 | PIT | 13 | 173.14 | 119.01 | 375.28 | -21.60 | 8.78 | 1.000 | 1.000 |  | 169.28 | 0.69 | 1 | False | False |
| baselines-margin | pct_rev_last4 | W1 | 1 | PIT | 13 | 212.87 | 155.59 | 330.68 | 41.62 | 56.18 | 1.230 | 1.307 |  | 197.92 | 0.92 | 3 | False | False |
| baselines-margin | seasonal_naive_drift | W1 | 1 | PIT | 13 | 323.43 | 272.03 | 525.87 | 6.98 | 1.63 | 1.868 | 2.286 |  | 240.50 | 0.92 | 1 | False | False |
| baselines-margin | seasonal_naive | W1 | 1 | full_sample | 13 | 173.14 | 119.01 | 375.28 | -21.60 | 8.78 | 1.000 | 1.000 |  | 155.48 | 0.92 | 1 | False | False |
| baselines-margin | pct_rev_last4 | W1 | 1 | full_sample | 13 | 212.87 | 155.59 | 330.68 | 41.62 | 56.18 | 1.230 | 1.307 |  | 179.50 | 0.92 | 3 | False | False |
| baselines-margin | seasonal_naive_drift | W1 | 1 | full_sample | 13 | 323.43 | 272.03 | 525.87 | 6.98 | 1.63 | 1.868 | 2.286 |  | 236.14 | 0.85 | 1 | False | False |
| baselines-margin | seasonal_naive | W1 | 2 | PIT | 12 | 185.14 | 121.06 | 390.52 | -20.97 | 9.65 | 1.000 | 1.000 |  | 181.21 | 0.67 | 1 | False | False |
| baselines-margin | pct_rev_last4 | W1 | 2 | PIT | 12 | 232.07 | 170.22 | 346.91 | 47.71 | 70.39 | 1.253 | 1.406 |  | 212.23 | 0.83 | 3 | False | False |
| baselines-margin | seasonal_naive_drift | W1 | 2 | PIT | 12 | 336.19 | 273.53 | 546.52 | -3.09 | -33.01 | 1.816 | 2.260 |  | 251.72 | 0.92 | 1 | False | False |
| baselines-margin | seasonal_naive | W1 | 2 | full_sample | 12 | 185.14 | 121.06 | 390.52 | -20.97 | 9.65 | 1.000 | 1.000 |  | 164.85 | 0.92 | 1 | False | False |
| baselines-margin | pct_rev_last4 | W1 | 2 | full_sample | 12 | 232.07 | 170.22 | 346.91 | 47.71 | 70.39 | 1.253 | 1.406 |  | 190.96 | 0.92 | 3 | False | False |
| baselines-margin | seasonal_naive_drift | W1 | 2 | full_sample | 12 | 336.19 | 273.53 | 546.52 | -3.09 | -33.01 | 1.816 | 2.260 |  | 245.18 | 0.83 | 1 | False | False |
| baselines-margin | seasonal_naive | W2 | 0 | PIT | 10 | 122.80 | 95.02 | 307.75 | 74.20 | 43.90 | 1.000 | 1.000 |  | 120.93 | 1.00 | 1 | False | False |
| baselines-margin | pct_rev_last4 | W2 | 0 | PIT | 10 | 161.45 | 119.85 | 216.62 | 129.84 | 80.48 | 1.315 | 1.261 |  | 154.35 | 1.00 | 3 | False | False |
| baselines-margin | seasonal_naive_drift | W2 | 0 | PIT | 10 | 319.60 | 233.24 | 524.78 | 95.00 | 32.56 | 2.603 | 2.455 |  | 217.90 | 1.00 | 1 | False | False |
| baselines-margin | seasonal_naive | W2 | 0 | full_sample | 10 | 122.80 | 95.02 | 307.75 | 74.20 | 43.90 | 1.000 | 1.000 |  | 109.41 | 1.00 | 1 | False | False |
| baselines-margin | pct_rev_last4 | W2 | 0 | full_sample | 10 | 161.86 | 120.52 | 216.66 | 130.59 | 81.55 | 1.318 | 1.268 |  | 129.20 | 1.00 | 3 | False | False |
| baselines-margin | seasonal_naive_drift | W2 | 0 | full_sample | 10 | 319.60 | 233.24 | 524.78 | 95.00 | 32.56 | 2.603 | 2.455 |  | 216.90 | 0.90 | 1 | False | False |
| baselines-margin | seasonal_naive | W2 | 1 | PIT | 9 | 132.44 | 97.52 | 324.17 | 86.44 | 47.28 | 1.000 | 1.000 |  | 130.59 | 1.00 | 1 | False | False |
| baselines-margin | pct_rev_last4 | W2 | 1 | PIT | 9 | 188.57 | 138.68 | 244.42 | 156.12 | 95.35 | 1.424 | 1.422 |  | 175.79 | 1.00 | 3 | False | False |
| baselines-margin | seasonal_naive_drift | W2 | 1 | PIT | 9 | 358.89 | 273.75 | 554.53 | 109.78 | 33.71 | 2.710 | 2.807 |  | 244.26 | 1.00 | 1 | False | False |
| baselines-margin | seasonal_naive | W2 | 1 | full_sample | 9 | 132.44 | 97.52 | 324.17 | 86.44 | 47.28 | 1.000 | 1.000 |  | 116.32 | 1.00 | 1 | False | False |
| baselines-margin | pct_rev_last4 | W2 | 1 | full_sample | 9 | 188.57 | 138.68 | 244.42 | 156.12 | 95.35 | 1.424 | 1.422 |  | 145.72 | 1.00 | 3 | False | False |
| baselines-margin | seasonal_naive_drift | W2 | 1 | full_sample | 9 | 358.89 | 273.75 | 554.53 | 109.78 | 33.71 | 2.710 | 2.807 |  | 236.32 | 0.89 | 1 | False | False |
| baselines-margin | seasonal_naive | W2 | 2 | PIT | 8 | 145.88 | 101.37 | 343.73 | 100.38 | 51.12 | 1.000 | 1.000 |  | 144.89 | 1.00 | 1 | False | False |
| baselines-margin | pct_rev_last4 | W2 | 2 | PIT | 8 | 212.37 | 157.68 | 266.38 | 177.05 | 114.07 | 1.456 | 1.555 |  | 193.06 | 1.00 | 3 | False | False |
| baselines-margin | seasonal_naive_drift | W2 | 2 | PIT | 8 | 385.00 | 282.85 | 586.95 | 107.00 | -5.49 | 2.639 | 2.790 |  | 262.04 | 1.00 | 1 | False | False |
| baselines-margin | seasonal_naive | W2 | 2 | full_sample | 8 | 145.88 | 101.37 | 343.73 | 100.38 | 51.12 | 1.000 | 1.000 |  | 124.71 | 1.00 | 1 | False | False |
| baselines-margin | pct_rev_last4 | W2 | 2 | full_sample | 8 | 212.37 | 157.68 | 266.38 | 177.05 | 114.07 | 1.456 | 1.555 |  | 157.84 | 1.00 | 3 | False | False |
| baselines-margin | seasonal_naive_drift | W2 | 2 | full_sample | 8 | 385.00 | 282.85 | 586.95 | 107.00 | -5.49 | 2.639 | 2.790 |  | 249.54 | 0.88 | 1 | False | False |

## target: `ga_cash_per_night`

| method | object | window | h | replay | n | mae | rw_mae | rmse | bias | rw_bias | r_sn | rw_r_sn | r_street | crps | cov80 | n_params | both | rw_both |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| baselines-margin | seasonal_naive | W1 | 0 | PIT | 14 | 1.56 | 1.17 | 3.64 | -0.01 | 0.28 | 1.000 | 1.000 |  | 1.82 | 0.86 | 1 | False | False |
| baselines-margin | trailing4 | W1 | 0 | PIT | 14 | 1.61 | 1.12 | 2.90 | 0.04 | 0.23 | 1.033 | 0.960 |  | 1.44 | 0.93 | 2 | False | True |
| baselines-margin | seasonal_naive_drift | W1 | 0 | PIT | 14 | 2.95 | 2.34 | 5.08 | 0.03 | 0.00 | 1.894 | 2.006 |  | 2.86 | 0.71 | 1 | False | False |
| baselines-margin | seasonal_naive | W1 | 0 | full_sample | 14 | 1.56 | 1.17 | 3.64 | -0.01 | 0.28 | 1.000 | 1.000 |  | 1.74 | 0.86 | 1 | False | False |
| baselines-margin | trailing4 | W1 | 0 | full_sample | 14 | 1.61 | 1.12 | 2.90 | 0.04 | 0.23 | 1.033 | 0.960 |  | 1.40 | 0.93 | 2 | False | True |
| baselines-margin | seasonal_naive_drift | W1 | 0 | full_sample | 14 | 2.95 | 2.34 | 5.08 | 0.03 | 0.00 | 1.894 | 2.006 |  | 2.72 | 0.71 | 1 | False | False |
| baselines-margin | seasonal_naive | W1 | 1 | PIT | 13 | 1.68 | 1.19 | 3.78 | -0.01 | 0.29 | 1.000 | 1.000 |  | 1.88 | 0.85 | 1 | False | False |
| baselines-margin | trailing4 | W1 | 1 | PIT | 13 | 1.70 | 1.19 | 3.03 | 0.01 | 0.30 | 1.015 | 1.001 |  | 1.50 | 0.92 | 2 | False | False |
| baselines-margin | seasonal_naive_drift | W1 | 1 | PIT | 13 | 3.21 | 2.66 | 5.31 | 0.04 | -0.02 | 1.917 | 2.232 |  | 2.94 | 0.69 | 1 | False | False |
| baselines-margin | seasonal_naive | W1 | 1 | full_sample | 13 | 1.68 | 1.19 | 3.78 | -0.01 | 0.29 | 1.000 | 1.000 |  | 1.83 | 0.85 | 1 | False | False |
| baselines-margin | trailing4 | W1 | 1 | full_sample | 13 | 1.70 | 1.19 | 3.03 | 0.01 | 0.30 | 1.015 | 1.001 |  | 1.47 | 0.92 | 2 | False | False |
| baselines-margin | seasonal_naive_drift | W1 | 1 | full_sample | 13 | 3.21 | 2.66 | 5.31 | 0.04 | -0.02 | 1.917 | 2.232 |  | 2.87 | 0.69 | 1 | False | False |
| baselines-margin | seasonal_naive | W1 | 2 | PIT | 12 | 1.81 | 1.21 | 3.93 | -0.00 | 0.29 | 1.000 | 1.000 |  | 1.96 | 0.83 | 1 | False | False |
| baselines-margin | trailing4 | W1 | 2 | PIT | 12 | 1.82 | 1.28 | 3.17 | 0.00 | 0.39 | 1.006 | 1.054 |  | 1.57 | 0.92 | 2 | False | False |
| baselines-margin | seasonal_naive_drift | W1 | 2 | PIT | 12 | 3.35 | 2.70 | 5.53 | -0.04 | -0.33 | 1.854 | 2.226 |  | 3.09 | 0.67 | 1 | False | False |
| baselines-margin | seasonal_naive | W1 | 2 | full_sample | 12 | 1.81 | 1.21 | 3.93 | -0.00 | 0.29 | 1.000 | 1.000 |  | 1.93 | 0.83 | 1 | False | False |
| baselines-margin | trailing4 | W1 | 2 | full_sample | 12 | 1.82 | 1.28 | 3.17 | 0.00 | 0.39 | 1.006 | 1.054 |  | 1.55 | 0.92 | 2 | False | False |
| baselines-margin | seasonal_naive_drift | W1 | 2 | full_sample | 12 | 3.35 | 2.70 | 5.53 | -0.04 | -0.33 | 1.854 | 2.226 |  | 3.00 | 0.67 | 1 | False | False |
| baselines-margin | seasonal_naive | W2 | 0 | PIT | 10 | 1.22 | 0.97 | 3.16 | 0.95 | 0.64 | 1.000 | 1.000 |  | 1.60 | 0.90 | 1 | False | False |
| baselines-margin | trailing4 | W2 | 0 | PIT | 10 | 1.24 | 0.90 | 1.61 | 1.00 | 0.58 | 1.018 | 0.932 |  | 1.04 | 1.00 | 2 | False | True |
| baselines-margin | seasonal_naive_drift | W2 | 0 | PIT | 10 | 3.18 | 2.28 | 5.30 | 0.95 | 0.31 | 2.608 | 2.352 |  | 3.07 | 0.70 | 1 | False | False |
| baselines-margin | seasonal_naive | W2 | 0 | full_sample | 10 | 1.22 | 0.97 | 3.16 | 0.95 | 0.64 | 1.000 | 1.000 |  | 1.48 | 0.90 | 1 | False | False |
| baselines-margin | trailing4 | W2 | 0 | full_sample | 10 | 1.24 | 0.90 | 1.61 | 1.00 | 0.58 | 1.018 | 0.932 |  | 0.97 | 1.00 | 2 | False | True |
| baselines-margin | seasonal_naive_drift | W2 | 0 | full_sample | 10 | 3.18 | 2.28 | 5.30 | 0.95 | 0.31 | 2.608 | 2.352 |  | 2.86 | 0.70 | 1 | False | False |
| baselines-margin | trailing4 | W2 | 1 | PIT | 9 | 1.33 | 0.99 | 1.71 | 1.08 | 0.68 | 0.991 | 0.985 |  | 1.07 | 1.00 | 2 | False | False |
| baselines-margin | seasonal_naive | W2 | 1 | PIT | 9 | 1.34 | 1.00 | 3.33 | 1.07 | 0.67 | 1.000 | 1.000 |  | 1.67 | 0.89 | 1 | False | False |
| baselines-margin | seasonal_naive_drift | W2 | 1 | PIT | 9 | 3.56 | 2.67 | 5.60 | 1.09 | 0.30 | 2.657 | 2.657 |  | 3.21 | 0.67 | 1 | False | False |
| baselines-margin | trailing4 | W2 | 1 | full_sample | 9 | 1.33 | 0.99 | 1.71 | 1.08 | 0.68 | 0.991 | 0.985 |  | 1.02 | 1.00 | 2 | False | False |
| baselines-margin | seasonal_naive | W2 | 1 | full_sample | 9 | 1.34 | 1.00 | 3.33 | 1.07 | 0.67 | 1.000 | 1.000 |  | 1.57 | 0.89 | 1 | False | False |
| baselines-margin | seasonal_naive_drift | W2 | 1 | full_sample | 9 | 3.56 | 2.67 | 5.60 | 1.09 | 0.30 | 2.657 | 2.657 |  | 3.08 | 0.67 | 1 | False | False |
| baselines-margin | trailing4 | W2 | 2 | PIT | 8 | 1.46 | 1.11 | 1.83 | 1.21 | 0.81 | 0.975 | 1.056 |  | 1.13 | 1.00 | 2 | False | False |
| baselines-margin | seasonal_naive | W2 | 2 | PIT | 8 | 1.50 | 1.05 | 3.53 | 1.21 | 0.71 | 1.000 | 1.000 |  | 1.76 | 0.88 | 1 | False | False |
| baselines-margin | seasonal_naive_drift | W2 | 2 | PIT | 8 | 3.83 | 2.79 | 5.93 | 1.09 | -0.04 | 2.550 | 2.649 |  | 3.46 | 0.62 | 1 | False | False |
| baselines-margin | trailing4 | W2 | 2 | full_sample | 8 | 1.46 | 1.11 | 1.83 | 1.21 | 0.81 | 0.975 | 1.056 |  | 1.08 | 1.00 | 2 | False | False |
| baselines-margin | seasonal_naive | W2 | 2 | full_sample | 8 | 1.50 | 1.05 | 3.53 | 1.21 | 0.71 | 1.000 | 1.000 |  | 1.69 | 0.88 | 1 | False | False |
| baselines-margin | seasonal_naive_drift | W2 | 2 | full_sample | 8 | 3.83 | 2.79 | 5.93 | 1.09 | -0.04 | 2.550 | 2.649 |  | 3.29 | 0.62 | 1 | False | False |

## target: `gbv_musd`

| method | object | window | h | replay | n | mae | rw_mae | rmse | bias | rw_bias | r_sn | rw_r_sn | r_street | crps | cov80 | n_params | both | rw_both |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| baselines-margin | seasonal_naive_drift | W1 | 0 | PIT | 14 | 678.57 | 752.42 | 812.84 | -107.14 | -172.75 | 0.261 | 0.257 |  | 579.12 | 0.93 | 1 | True | True |
| baselines-margin | seasonal_naive | W1 | 0 | PIT | 14 | 2,600.00 | 2,932.39 | 2,719.77 | -2,600.00 | -2,932.39 | 1.000 | 1.000 |  | 1,952.26 | 0.64 | 1 | False | False |
| baselines-margin | seasonal_naive_drift | W1 | 0 | full_sample | 14 | 678.57 | 752.42 | 812.84 | -107.14 | -172.75 | 0.261 | 0.257 |  | 510.60 | 1.00 | 1 | True | True |
| baselines-margin | seasonal_naive | W1 | 0 | full_sample | 14 | 2,600.00 | 2,932.39 | 2,719.77 | -2,600.00 | -2,932.39 | 1.000 | 1.000 |  | 1,587.68 | 1.00 | 1 | False | False |
| baselines-margin | seasonal_naive_drift | W1 | 1 | PIT | 13 | 507.69 | 734.02 | 733.80 | -230.77 | -578.01 | 0.199 | 0.251 |  | 622.34 | 0.85 | 1 | True | True |
| baselines-margin | seasonal_naive | W1 | 1 | PIT | 13 | 2,553.85 | 2,927.39 | 2,679.27 | -2,553.85 | -2,927.39 | 1.000 | 1.000 |  | 1,777.45 | 0.69 | 1 | False | False |
| baselines-margin | seasonal_naive_drift | W1 | 1 | full_sample | 13 | 507.69 | 734.02 | 733.80 | -230.77 | -578.01 | 0.199 | 0.251 |  | 498.26 | 1.00 | 1 | True | True |
| baselines-margin | seasonal_naive | W1 | 1 | full_sample | 13 | 2,553.85 | 2,927.39 | 2,679.27 | -2,553.85 | -2,927.39 | 1.000 | 1.000 |  | 1,530.84 | 0.85 | 1 | False | False |
| baselines-margin | seasonal_naive_drift | W1 | 2 | PIT | 12 | 791.67 | 975.45 | 975.11 | -308.33 | -694.25 | 0.305 | 0.331 |  | 650.89 | 1.00 | 1 | True | True |
| baselines-margin | seasonal_naive | W1 | 2 | PIT | 12 | 2,591.67 | 2,946.20 | 2,721.98 | -2,591.67 | -2,946.20 | 1.000 | 1.000 |  | 1,920.01 | 0.08 | 1 | False | False |
| baselines-margin | seasonal_naive_drift | W1 | 2 | full_sample | 12 | 791.67 | 975.45 | 975.11 | -308.33 | -694.25 | 0.305 | 0.331 |  | 605.61 | 1.00 | 1 | True | True |
| baselines-margin | seasonal_naive | W1 | 2 | full_sample | 12 | 2,591.67 | 2,946.20 | 2,721.98 | -2,591.67 | -2,946.20 | 1.000 | 1.000 |  | 1,945.18 | 0.08 | 1 | False | False |
| baselines-margin | seasonal_naive_drift | W2 | 0 | PIT | 10 | 610.00 | 745.17 | 786.77 | -170.00 | -204.24 | 0.231 | 0.250 |  | 542.96 | 0.90 | 1 | True | True |
| baselines-margin | seasonal_naive | W2 | 0 | PIT | 10 | 2,640.00 | 2,985.60 | 2,786.04 | -2,640.00 | -2,985.60 | 1.000 | 1.000 |  | 2,087.45 | 0.50 | 1 | False | False |
| baselines-margin | seasonal_naive_drift | W2 | 0 | full_sample | 10 | 610.00 | 745.17 | 786.77 | -170.00 | -204.24 | 0.231 | 0.250 |  | 512.25 | 1.00 | 1 | True | True |
| baselines-margin | seasonal_naive | W2 | 0 | full_sample | 10 | 2,640.00 | 2,985.60 | 2,786.04 | -2,640.00 | -2,985.60 | 1.000 | 1.000 |  | 1,638.71 | 1.00 | 1 | False | False |
| baselines-margin | seasonal_naive_drift | W2 | 1 | PIT | 9 | 633.33 | 802.19 | 862.17 | -433.33 | -684.46 | 0.238 | 0.267 |  | 618.01 | 0.78 | 1 | True | True |
| baselines-margin | seasonal_naive | W2 | 1 | PIT | 9 | 2,655.56 | 3,006.16 | 2,816.03 | -2,655.56 | -3,006.16 | 1.000 | 1.000 |  | 1,965.40 | 0.56 | 1 | False | False |
| baselines-margin | seasonal_naive_drift | W2 | 1 | full_sample | 9 | 633.33 | 802.19 | 862.17 | -433.33 | -684.46 | 0.238 | 0.267 |  | 553.63 | 1.00 | 1 | True | True |
| baselines-margin | seasonal_naive | W2 | 1 | full_sample | 9 | 2,655.56 | 3,006.16 | 2,816.03 | -2,655.56 | -3,006.16 | 1.000 | 1.000 |  | 1,597.49 | 0.89 | 1 | False | False |
| baselines-margin | seasonal_naive_drift | W2 | 2 | PIT | 8 | 850.00 | 1,027.60 | 1,072.38 | -575.00 | -853.18 | 0.312 | 0.336 |  | 667.34 | 1.00 | 1 | True | True |
| baselines-margin | seasonal_naive | W2 | 2 | PIT | 8 | 2,725.00 | 3,054.22 | 2,893.10 | -2,725.00 | -3,054.22 | 1.000 | 1.000 |  | 2,035.17 | 0.12 | 1 | False | False |
| baselines-margin | seasonal_naive_drift | W2 | 2 | full_sample | 8 | 850.00 | 1,027.60 | 1,072.38 | -575.00 | -853.18 | 0.312 | 0.336 |  | 645.07 | 1.00 | 1 | True | True |
| baselines-margin | seasonal_naive | W2 | 2 | full_sample | 8 | 2,725.00 | 3,054.22 | 2,893.10 | -2,725.00 | -3,054.22 | 1.000 | 1.000 |  | 2,046.95 | 0.12 | 1 | False | False |

## target: `interest_income_musd`

| method | object | window | h | replay | n | mae | rw_mae | rmse | bias | rw_bias | r_sn | rw_r_sn | r_street | crps | cov80 | n_params | both | rw_both |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| baselines-margin | seasonal_naive_drift | W1 | 0 | PIT | 14 | 22.04 | 14.54 | 25.77 | 7.50 | 3.60 | 0.391 | 0.454 |  | 42.95 | 1.00 | 1 | True | True |
| baselines-margin | seasonal_naive | W1 | 0 | PIT | 14 | 56.33 | 32.00 | 77.18 | -35.33 | -1.84 | 1.000 | 1.000 |  | 330.75 | 0.93 | 1 | False | False |
| baselines-margin | seasonal_naive_drift | W1 | 0 | full_sample | 14 | 22.04 | 14.54 | 25.77 | 7.50 | 3.60 | 0.391 | 0.454 |  | 41.60 | 1.00 | 1 | True | True |
| baselines-margin | seasonal_naive | W1 | 0 | full_sample | 14 | 56.33 | 32.00 | 77.18 | -35.33 | -1.84 | 1.000 | 1.000 |  | 307.71 | 0.93 | 1 | False | False |
| baselines-margin | seasonal_naive_drift | W1 | 1 | PIT | 13 | 37.68 | 26.26 | 46.17 | 20.32 | 11.16 | 0.757 | 0.876 |  | 160.18 | 1.00 | 1 | False | False |
| baselines-margin | seasonal_naive | W1 | 1 | PIT | 13 | 49.79 | 29.96 | 69.86 | -27.18 | 0.77 | 1.000 | 1.000 |  | 377.42 | 1.00 | 1 | False | False |
| baselines-margin | seasonal_naive_drift | W1 | 1 | full_sample | 13 | 37.68 | 26.26 | 46.17 | 20.32 | 11.16 | 0.757 | 0.876 |  | 137.76 | 1.00 | 1 | False | False |
| baselines-margin | seasonal_naive | W1 | 1 | full_sample | 13 | 49.79 | 29.96 | 69.86 | -27.18 | 0.77 | 1.000 | 1.000 |  | 328.92 | 1.00 | 1 | False | False |
| baselines-margin | seasonal_naive | W1 | 2 | PIT | 12 | 39.71 | 26.76 | 53.45 | -15.21 | 4.67 | 1.000 | 1.000 |  | 403.65 | 1.00 | 1 | False | False |
| baselines-margin | seasonal_naive_drift | W1 | 2 | PIT | 12 | 51.59 | 38.60 | 60.85 | 38.00 | 21.84 | 1.299 | 1.443 |  | 311.21 | 1.00 | 1 | False | False |
| baselines-margin | seasonal_naive | W1 | 2 | full_sample | 12 | 39.71 | 26.76 | 53.45 | -15.21 | 4.67 | 1.000 | 1.000 |  | 355.90 | 1.00 | 1 | False | False |
| baselines-margin | seasonal_naive_drift | W1 | 2 | full_sample | 12 | 51.59 | 38.60 | 60.85 | 38.00 | 21.84 | 1.299 | 1.443 |  | 286.34 | 1.00 | 1 | False | False |
| baselines-margin | seasonal_naive_drift | W2 | 0 | PIT | 10 | 15.50 | 11.95 | 18.08 | 9.70 | 3.02 | 0.613 | 0.555 |  | 38.33 | 1.00 | 1 | True | True |
| baselines-margin | seasonal_naive | W2 | 0 | PIT | 10 | 25.30 | 21.53 | 28.89 | 4.10 | 11.87 | 1.000 | 1.000 |  | 397.42 | 1.00 | 1 | False | False |
| baselines-margin | seasonal_naive_drift | W2 | 0 | full_sample | 10 | 15.50 | 11.95 | 18.08 | 9.70 | 3.02 | 0.613 | 0.555 |  | 40.69 | 1.00 | 1 | True | True |
| baselines-margin | seasonal_naive | W2 | 0 | full_sample | 10 | 25.30 | 21.53 | 28.89 | 4.10 | 11.87 | 1.000 | 1.000 |  | 372.60 | 1.00 | 1 | False | False |
| baselines-margin | seasonal_naive | W2 | 1 | PIT | 9 | 21.89 | 20.07 | 24.06 | 10.78 | 14.75 | 1.000 | 1.000 |  | 443.37 | 1.00 | 1 | False | False |
| baselines-margin | seasonal_naive_drift | W2 | 1 | PIT | 9 | 27.89 | 21.53 | 33.02 | 19.00 | 8.08 | 1.274 | 1.073 |  | 142.29 | 1.00 | 1 | False | False |
| baselines-margin | seasonal_naive | W2 | 1 | full_sample | 9 | 21.89 | 20.07 | 24.06 | 10.78 | 14.75 | 1.000 | 1.000 |  | 389.27 | 1.00 | 1 | False | False |
| baselines-margin | seasonal_naive_drift | W2 | 1 | full_sample | 9 | 27.89 | 21.53 | 33.02 | 19.00 | 8.08 | 1.274 | 1.073 |  | 132.61 | 1.00 | 1 | False | False |
| baselines-margin | seasonal_naive | W2 | 2 | PIT | 8 | 20.25 | 19.28 | 22.32 | 16.50 | 17.39 | 1.000 | 1.000 |  | 459.10 | 1.00 | 1 | False | False |
| baselines-margin | seasonal_naive_drift | W2 | 2 | PIT | 8 | 39.88 | 31.65 | 46.98 | 28.38 | 14.34 | 1.969 | 1.642 |  | 303.10 | 1.00 | 1 | False | False |
| baselines-margin | seasonal_naive | W2 | 2 | full_sample | 8 | 20.25 | 19.28 | 22.32 | 16.50 | 17.39 | 1.000 | 1.000 |  | 398.85 | 1.00 | 1 | False | False |
| baselines-margin | seasonal_naive_drift | W2 | 2 | full_sample | 8 | 39.88 | 31.65 | 46.98 | 28.38 | 14.34 | 1.969 | 1.642 |  | 262.05 | 1.00 | 1 | False | False |

## target: `net_income_musd`

| method | object | window | h | replay | n | mae | rw_mae | rmse | bias | rw_bias | r_sn | rw_r_sn | r_street | crps | cov80 | n_params | both | rw_both |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| baselines-margin | street | W1 | 0 | PIT | 14 | 341.87 | 170.54 | 841.18 | -165.24 | -55.58 | 0.544 | 0.439 | 1.000 | 409.45 | 0.86 | 1 | True | True |
| baselines-margin | seasonal_naive | W1 | 0 | PIT | 14 | 628.26 | 388.83 | 1,204.43 | -56.98 | 18.39 | 1.000 | 1.000 | 1.838 | 637.83 | 0.86 | 1 | False | False |
| baselines-margin | seasonal_naive_drift | W1 | 0 | PIT | 14 | 1,170.16 | 781.80 | 1,846.62 | 6.46 | -34.74 | 1.863 | 2.011 | 3.423 | 1,019.20 | 0.71 | 1 | False | False |
| baselines-margin | street | W1 | 0 | full_sample | 14 | 341.87 | 170.54 | 841.18 | -165.24 | -55.58 | 0.544 | 0.439 | 1.000 | 369.27 | 0.93 | 1 | True | True |
| baselines-margin | seasonal_naive | W1 | 0 | full_sample | 14 | 628.26 | 388.83 | 1,204.43 | -56.98 | 18.39 | 1.000 | 1.000 | 1.838 | 627.47 | 0.86 | 1 | False | False |
| baselines-margin | seasonal_naive_drift | W1 | 0 | full_sample | 14 | 1,170.16 | 781.80 | 1,846.62 | 6.46 | -34.74 | 1.863 | 2.011 | 3.423 | 999.37 | 0.71 | 1 | False | False |
| baselines-margin | street | W1 | 1 | PIT | 13 | 388.55 | 194.38 | 890.11 | -154.05 | -31.10 | 0.583 | 0.494 | 1.000 | 478.52 | 0.77 | 1 | True | True |
| baselines-margin | seasonal_naive | W1 | 1 | PIT | 13 | 666.14 | 393.56 | 1,249.33 | -50.91 | 21.27 | 1.000 | 1.000 | 1.714 | 678.32 | 0.77 | 1 | False | False |
| baselines-margin | seasonal_naive_drift | W1 | 1 | PIT | 13 | 1,219.19 | 842.52 | 1,737.45 | 16.94 | -44.36 | 1.830 | 2.141 | 3.138 | 958.34 | 0.69 | 1 | False | False |
| baselines-margin | street | W1 | 1 | full_sample | 13 | 388.55 | 194.38 | 890.11 | -154.05 | -31.10 | 0.583 | 0.494 | 1.000 | 399.73 | 0.92 | 1 | True | True |
| baselines-margin | seasonal_naive | W1 | 1 | full_sample | 13 | 666.14 | 393.56 | 1,249.33 | -50.91 | 21.27 | 1.000 | 1.000 | 1.714 | 627.30 | 0.85 | 1 | False | False |
| baselines-margin | seasonal_naive_drift | W1 | 1 | full_sample | 13 | 1,219.19 | 842.52 | 1,737.45 | 16.94 | -44.36 | 1.830 | 2.141 | 3.138 | 955.17 | 0.69 | 1 | False | False |
| baselines-margin | seasonal_naive | W1 | 2 | PIT | 12 | 699.06 | 396.34 | 1,297.99 | -32.56 | 27.92 | 1.000 | 1.000 |  | 722.90 | 0.75 | 1 | False | False |
| baselines-margin | seasonal_naive_drift | W1 | 2 | PIT | 12 | 1,187.49 | 839.30 | 1,727.02 | 50.95 | -25.96 | 1.699 | 2.118 |  | 926.66 | 0.75 | 1 | False | False |
| baselines-margin | seasonal_naive | W1 | 2 | full_sample | 12 | 699.06 | 396.34 | 1,297.99 | -32.56 | 27.92 | 1.000 | 1.000 |  | 654.54 | 0.83 | 1 | False | False |
| baselines-margin | seasonal_naive_drift | W1 | 2 | full_sample | 12 | 1,187.49 | 839.30 | 1,727.02 | 50.95 | -25.96 | 1.699 | 2.118 |  | 946.27 | 0.67 | 1 | False | False |
| baselines-margin | street | W2 | 0 | PIT | 10 | 77.04 | 70.74 | 100.08 | 16.12 | 3.90 | 0.169 | 0.230 | 1.000 | 218.10 | 1.00 | 1 | True | True |
| baselines-margin | seasonal_naive | W2 | 0 | PIT | 10 | 456.10 | 307.67 | 989.30 | 210.10 | 97.63 | 1.000 | 1.000 | 5.921 | 531.97 | 0.90 | 1 | False | False |
| baselines-margin | seasonal_naive_drift | W2 | 0 | PIT | 10 | 940.20 | 646.09 | 1,571.95 | -84.20 | -85.60 | 2.061 | 2.100 | 12.205 | 871.06 | 0.80 | 1 | False | False |
| baselines-margin | street | W2 | 0 | full_sample | 10 | 77.04 | 70.74 | 100.08 | 16.12 | 3.90 | 0.169 | 0.230 | 1.000 | 172.94 | 1.00 | 1 | True | True |
| baselines-margin | seasonal_naive | W2 | 0 | full_sample | 10 | 456.10 | 307.67 | 989.30 | 210.10 | 97.63 | 1.000 | 1.000 | 5.921 | 525.78 | 0.90 | 1 | False | False |
| baselines-margin | seasonal_naive_drift | W2 | 0 | full_sample | 10 | 940.20 | 646.09 | 1,571.95 | -84.20 | -85.60 | 2.061 | 2.100 | 12.205 | 852.18 | 0.80 | 1 | False | False |
| baselines-margin | street | W2 | 1 | PIT | 9 | 99.52 | 90.72 | 114.27 | 66.88 | 39.05 | 0.203 | 0.288 | 1.000 | 232.66 | 1.00 | 1 | True | True |
| baselines-margin | seasonal_naive | W2 | 1 | PIT | 9 | 490.44 | 314.48 | 1,041.66 | 249.78 | 107.99 | 1.000 | 1.000 | 4.928 | 555.70 | 0.89 | 1 | False | False |
| baselines-margin | seasonal_naive_drift | W2 | 1 | PIT | 9 | 985.22 | 702.89 | 1,495.96 | -77.89 | -120.58 | 2.009 | 2.235 | 9.900 | 827.31 | 0.78 | 1 | False | False |
| baselines-margin | street | W2 | 1 | full_sample | 9 | 99.52 | 90.72 | 114.27 | 66.88 | 39.05 | 0.203 | 0.288 | 1.000 | 187.18 | 1.00 | 1 | True | True |
| baselines-margin | seasonal_naive | W2 | 1 | full_sample | 9 | 490.44 | 314.48 | 1,041.66 | 249.78 | 107.99 | 1.000 | 1.000 | 4.928 | 516.03 | 0.89 | 1 | False | False |
| baselines-margin | seasonal_naive_drift | W2 | 1 | full_sample | 9 | 985.22 | 702.89 | 1,495.96 | -77.89 | -120.58 | 2.009 | 2.235 | 9.900 | 818.35 | 0.78 | 1 | False | False |
| baselines-margin | seasonal_naive | W2 | 2 | PIT | 8 | 539.88 | 326.12 | 1,104.34 | 269.12 | 108.68 | 1.000 | 1.000 |  | 577.05 | 0.88 | 1 | False | False |
| baselines-margin | seasonal_naive_drift | W2 | 2 | PIT | 8 | 896.50 | 679.59 | 1,421.00 | -84.50 | -147.28 | 1.661 | 2.084 |  | 779.00 | 0.88 | 1 | False | False |
| baselines-margin | seasonal_naive | W2 | 2 | full_sample | 8 | 539.88 | 326.12 | 1,104.34 | 269.12 | 108.68 | 1.000 | 1.000 |  | 548.44 | 0.88 | 1 | False | False |
| baselines-margin | seasonal_naive_drift | W2 | 2 | full_sample | 8 | 896.50 | 679.59 | 1,421.00 | -84.50 | -147.28 | 1.661 | 2.084 |  | 772.97 | 0.75 | 1 | False | False |

## target: `nights_m`

| method | object | window | h | replay | n | mae | rw_mae | rmse | bias | rw_bias | r_sn | rw_r_sn | r_street | crps | cov80 | n_params | both | rw_both |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| baselines-margin | seasonal_naive_drift | W1 | 0 | PIT | 14 | 2.12 | 1.53 | 2.81 | 0.06 | -0.38 | 0.179 | 0.130 |  | 2.32 | 1.00 | 1 | True | True |
| baselines-margin | seasonal_naive | W1 | 0 | PIT | 14 | 11.88 | 11.78 | 12.12 | -11.88 | -11.78 | 1.000 | 1.000 |  | 7.91 | 0.71 | 1 | False | False |
| baselines-margin | seasonal_naive_drift | W1 | 0 | full_sample | 14 | 2.12 | 1.53 | 2.81 | 0.06 | -0.38 | 0.179 | 0.130 |  | 2.21 | 1.00 | 1 | True | True |
| baselines-margin | seasonal_naive | W1 | 0 | full_sample | 14 | 11.88 | 11.78 | 12.12 | -11.88 | -11.78 | 1.000 | 1.000 |  | 7.15 | 1.00 | 1 | False | False |
| baselines-margin | seasonal_naive_drift | W1 | 1 | PIT | 13 | 2.11 | 2.02 | 2.50 | 0.52 | -0.61 | 0.186 | 0.174 |  | 2.98 | 1.00 | 1 | True | True |
| baselines-margin | seasonal_naive | W1 | 1 | PIT | 13 | 11.33 | 11.65 | 11.42 | -11.33 | -11.65 | 1.000 | 1.000 |  | 7.30 | 0.69 | 1 | False | False |
| baselines-margin | seasonal_naive_drift | W1 | 1 | full_sample | 13 | 2.11 | 2.02 | 2.50 | 0.52 | -0.61 | 0.186 | 0.174 |  | 2.52 | 1.00 | 1 | True | True |
| baselines-margin | seasonal_naive | W1 | 1 | full_sample | 13 | 11.33 | 11.65 | 11.42 | -11.33 | -11.65 | 1.000 | 1.000 |  | 6.57 | 1.00 | 1 | False | False |
| baselines-margin | seasonal_naive_drift | W1 | 2 | PIT | 12 | 2.04 | 1.98 | 3.06 | 0.61 | -0.59 | 0.180 | 0.170 |  | 2.60 | 1.00 | 1 | True | True |
| baselines-margin | seasonal_naive | W1 | 2 | PIT | 12 | 11.32 | 11.65 | 11.42 | -11.32 | -11.65 | 1.000 | 1.000 |  | 7.91 | 0.17 | 1 | False | False |
| baselines-margin | seasonal_naive_drift | W1 | 2 | full_sample | 12 | 2.04 | 1.98 | 3.06 | 0.61 | -0.59 | 0.180 | 0.170 |  | 2.20 | 0.92 | 1 | True | True |
| baselines-margin | seasonal_naive | W1 | 2 | full_sample | 12 | 11.32 | 11.65 | 11.42 | -11.32 | -11.65 | 1.000 | 1.000 |  | 7.63 | 0.00 | 1 | False | False |
| baselines-margin | seasonal_naive_drift | W2 | 0 | PIT | 10 | 1.29 | 1.26 | 1.48 | -0.33 | -0.56 | 0.115 | 0.108 |  | 1.82 | 1.00 | 1 | True | True |
| baselines-margin | seasonal_naive | W2 | 0 | PIT | 10 | 11.18 | 11.63 | 11.27 | -11.18 | -11.63 | 1.000 | 1.000 |  | 7.87 | 0.60 | 1 | False | False |
| baselines-margin | seasonal_naive_drift | W2 | 0 | full_sample | 10 | 1.29 | 1.26 | 1.48 | -0.33 | -0.56 | 0.115 | 0.108 |  | 2.00 | 1.00 | 1 | True | True |
| baselines-margin | seasonal_naive | W2 | 0 | full_sample | 10 | 11.18 | 11.63 | 11.27 | -11.18 | -11.63 | 1.000 | 1.000 |  | 6.83 | 1.00 | 1 | False | False |
| baselines-margin | seasonal_naive_drift | W2 | 1 | PIT | 9 | 1.74 | 1.93 | 1.97 | -0.54 | -1.05 | 0.157 | 0.166 |  | 2.40 | 1.00 | 1 | True | True |
| baselines-margin | seasonal_naive | W2 | 1 | PIT | 9 | 11.14 | 11.64 | 11.24 | -11.14 | -11.64 | 1.000 | 1.000 |  | 7.49 | 0.56 | 1 | False | False |
| baselines-margin | seasonal_naive_drift | W2 | 1 | full_sample | 9 | 1.74 | 1.93 | 1.97 | -0.54 | -1.05 | 0.157 | 0.166 |  | 2.50 | 1.00 | 1 | True | True |
| baselines-margin | seasonal_naive | W2 | 1 | full_sample | 9 | 11.14 | 11.64 | 11.24 | -11.14 | -11.64 | 1.000 | 1.000 |  | 6.43 | 1.00 | 1 | False | False |
| baselines-margin | seasonal_naive_drift | W2 | 2 | PIT | 8 | 1.40 | 1.76 | 1.87 | -0.73 | -1.22 | 0.124 | 0.150 |  | 2.21 | 1.00 | 1 | True | True |
| baselines-margin | seasonal_naive | W2 | 2 | PIT | 8 | 11.29 | 11.73 | 11.39 | -11.29 | -11.73 | 1.000 | 1.000 |  | 7.50 | 0.25 | 1 | False | False |
| baselines-margin | seasonal_naive_drift | W2 | 2 | full_sample | 8 | 1.40 | 1.76 | 1.87 | -0.73 | -1.22 | 0.124 | 0.150 |  | 1.94 | 1.00 | 1 | True | True |
| baselines-margin | seasonal_naive | W2 | 2 | full_sample | 8 | 11.29 | 11.73 | 11.39 | -11.29 | -11.73 | 1.000 | 1.000 |  | 7.45 | 0.00 | 1 | False | False |

## target: `op_income_musd`

| method | object | window | h | replay | n | mae | rw_mae | rmse | bias | rw_bias | r_sn | rw_r_sn | r_street | crps | cov80 | n_params | both | rw_both |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| baselines-margin | street | W1 | 0 | PIT | 14 | 111.65 | 73.71 | 234.35 | 50.74 | 14.62 | 0.539 | 0.422 | 1.000 | 116.36 | 0.93 | 1 | True | True |
| baselines-margin | seasonal_naive | W1 | 0 | PIT | 14 | 206.99 | 174.61 | 337.07 | -66.84 | -78.25 | 1.000 | 1.000 | 1.854 | 224.92 | 1.00 | 1 | False | False |
| baselines-margin | seasonal_naive_drift | W1 | 0 | PIT | 14 | 367.61 | 305.78 | 519.13 | 0.98 | -12.57 | 1.776 | 1.751 | 3.293 | 343.89 | 1.00 | 1 | False | False |
| baselines-margin | street | W1 | 0 | full_sample | 14 | 111.65 | 73.71 | 234.35 | 50.74 | 14.62 | 0.539 | 0.422 | 1.000 | 107.60 | 0.93 | 1 | True | True |
| baselines-margin | seasonal_naive | W1 | 0 | full_sample | 14 | 206.99 | 174.61 | 337.07 | -66.84 | -78.25 | 1.000 | 1.000 | 1.854 | 231.38 | 1.00 | 1 | False | False |
| baselines-margin | seasonal_naive_drift | W1 | 0 | full_sample | 14 | 367.61 | 305.78 | 519.13 | 0.98 | -12.57 | 1.776 | 1.751 | 3.293 | 335.64 | 1.00 | 1 | False | False |
| baselines-margin | street | W1 | 1 | PIT | 13 | 132.04 | 96.56 | 248.50 | 79.94 | 41.33 | 0.592 | 0.543 | 1.000 | 126.50 | 0.92 | 1 | True | True |
| baselines-margin | seasonal_naive | W1 | 1 | PIT | 13 | 222.90 | 177.87 | 349.80 | -71.98 | -79.71 | 1.000 | 1.000 | 1.688 | 192.46 | 0.77 | 1 | False | False |
| baselines-margin | seasonal_naive_drift | W1 | 1 | PIT | 13 | 369.59 | 331.15 | 494.51 | -2.62 | -10.29 | 1.658 | 1.862 | 2.799 | 305.46 | 1.00 | 1 | False | False |
| baselines-margin | street | W1 | 1 | full_sample | 13 | 132.04 | 96.56 | 248.50 | 79.94 | 41.33 | 0.592 | 0.543 | 1.000 | 118.49 | 0.92 | 1 | True | True |
| baselines-margin | seasonal_naive | W1 | 1 | full_sample | 13 | 222.90 | 177.87 | 349.80 | -71.98 | -79.71 | 1.000 | 1.000 | 1.688 | 183.58 | 0.85 | 1 | False | False |
| baselines-margin | seasonal_naive_drift | W1 | 1 | full_sample | 13 | 369.59 | 331.15 | 494.51 | -2.62 | -10.29 | 1.658 | 1.862 | 2.799 | 295.17 | 1.00 | 1 | False | False |
| baselines-margin | seasonal_naive | W1 | 2 | PIT | 12 | 228.63 | 178.41 | 361.35 | -65.13 | -78.01 | 1.000 | 1.000 |  | 197.72 | 0.75 | 1 | False | False |
| baselines-margin | seasonal_naive_drift | W1 | 2 | PIT | 12 | 330.88 | 268.37 | 466.66 | 23.42 | 41.23 | 1.447 | 1.504 |  | 312.28 | 1.00 | 1 | False | False |
| baselines-margin | seasonal_naive | W1 | 2 | full_sample | 12 | 228.63 | 178.41 | 361.35 | -65.13 | -78.01 | 1.000 | 1.000 |  | 189.94 | 0.83 | 1 | False | False |
| baselines-margin | seasonal_naive_drift | W1 | 2 | full_sample | 12 | 330.88 | 268.37 | 466.66 | 23.42 | 41.23 | 1.447 | 1.504 |  | 282.55 | 1.00 | 1 | False | False |
| baselines-margin | street | W2 | 0 | PIT | 10 | 58.68 | 49.15 | 69.15 | -5.68 | -10.31 | 0.341 | 0.315 | 1.000 | 73.50 | 1.00 | 1 | True | True |
| baselines-margin | seasonal_naive | W2 | 0 | PIT | 10 | 172.00 | 156.25 | 307.73 | -122.00 | -99.49 | 1.000 | 1.000 | 2.931 | 186.79 | 1.00 | 1 | False | False |
| baselines-margin | seasonal_naive_drift | W2 | 0 | PIT | 10 | 367.10 | 292.70 | 515.47 | -87.70 | -44.43 | 2.134 | 1.873 | 6.256 | 301.46 | 1.00 | 1 | False | False |
| baselines-margin | street | W2 | 0 | full_sample | 10 | 58.68 | 49.15 | 69.15 | -5.68 | -10.31 | 0.341 | 0.315 | 1.000 | 61.48 | 1.00 | 1 | True | True |
| baselines-margin | seasonal_naive | W2 | 0 | full_sample | 10 | 172.00 | 156.25 | 307.73 | -122.00 | -99.49 | 1.000 | 1.000 | 2.931 | 221.20 | 1.00 | 1 | False | False |
| baselines-margin | seasonal_naive_drift | W2 | 0 | full_sample | 10 | 367.10 | 292.70 | 515.47 | -87.70 | -44.43 | 2.134 | 1.873 | 6.256 | 333.45 | 1.00 | 1 | False | False |
| baselines-margin | street | W2 | 1 | PIT | 9 | 74.23 | 72.39 | 88.85 | 41.48 | 23.08 | 0.414 | 0.457 | 1.000 | 81.80 | 1.00 | 1 | True | True |
| baselines-margin | seasonal_naive | W2 | 1 | PIT | 9 | 179.33 | 158.38 | 322.44 | -123.78 | -99.22 | 1.000 | 1.000 | 2.416 | 169.77 | 0.89 | 1 | False | False |
| baselines-margin | seasonal_naive_drift | W2 | 1 | PIT | 9 | 381.67 | 326.90 | 502.79 | -91.00 | -42.46 | 2.128 | 2.064 | 5.142 | 288.31 | 1.00 | 1 | False | False |
| baselines-margin | street | W2 | 1 | full_sample | 9 | 74.23 | 72.39 | 88.85 | 41.48 | 23.08 | 0.414 | 0.457 | 1.000 | 69.80 | 1.00 | 1 | True | True |
| baselines-margin | seasonal_naive | W2 | 1 | full_sample | 9 | 179.33 | 158.38 | 322.44 | -123.78 | -99.22 | 1.000 | 1.000 | 2.416 | 162.83 | 0.89 | 1 | False | False |
| baselines-margin | seasonal_naive_drift | W2 | 1 | full_sample | 9 | 381.67 | 326.90 | 502.79 | -91.00 | -42.46 | 2.128 | 2.064 | 5.142 | 299.32 | 1.00 | 1 | False | False |
| baselines-margin | seasonal_naive | W2 | 2 | PIT | 8 | 198.50 | 165.40 | 341.88 | -142.50 | -105.86 | 1.000 | 1.000 |  | 178.87 | 0.88 | 1 | False | False |
| baselines-margin | seasonal_naive_drift | W2 | 2 | PIT | 8 | 342.50 | 262.46 | 494.63 | -85.50 | 5.83 | 1.725 | 1.587 |  | 294.73 | 1.00 | 1 | False | False |
| baselines-margin | seasonal_naive | W2 | 2 | full_sample | 8 | 198.50 | 165.40 | 341.88 | -142.50 | -105.86 | 1.000 | 1.000 |  | 173.79 | 0.88 | 1 | False | False |
| baselines-margin | seasonal_naive_drift | W2 | 2 | full_sample | 8 | 342.50 | 262.46 | 494.63 | -85.50 | 5.83 | 1.725 | 1.587 |  | 292.33 | 1.00 | 1 | False | False |

## target: `ops_cash_musd`

| method | object | window | h | replay | n | mae | rw_mae | rmse | bias | rw_bias | r_sn | rw_r_sn | r_street | crps | cov80 | n_params | both | rw_both |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| baselines-margin | seasonal_naive_drift | W1 | 0 | PIT | 14 | 18.84 | 18.07 | 22.26 | 1.10 | 0.89 | 0.842 | 0.952 |  | 12.72 | 0.79 | 1 | False | False |
| baselines-margin | seasonal_naive | W1 | 0 | PIT | 14 | 22.36 | 18.98 | 28.23 | -20.93 | -17.21 | 1.000 | 1.000 |  | 16.77 | 0.64 | 1 | False | False |
| baselines-margin | pct_rev_last4 | W1 | 0 | PIT | 14 | 37.72 | 38.02 | 51.33 | 17.74 | 18.66 | 1.687 | 2.003 |  | 26.27 | 0.79 | 3 | False | False |
| baselines-margin | seasonal_naive_drift | W1 | 0 | full_sample | 14 | 18.84 | 18.07 | 22.26 | 1.10 | 0.89 | 0.842 | 0.952 |  | 12.58 | 0.86 | 1 | False | False |
| baselines-margin | seasonal_naive | W1 | 0 | full_sample | 14 | 22.36 | 18.98 | 28.23 | -20.93 | -17.21 | 1.000 | 1.000 |  | 16.21 | 0.71 | 1 | False | False |
| baselines-margin | pct_rev_last4 | W1 | 0 | full_sample | 14 | 37.77 | 38.24 | 51.25 | 17.99 | 19.71 | 1.689 | 2.014 |  | 26.09 | 0.79 | 3 | False | False |
| baselines-margin | seasonal_naive | W1 | 1 | PIT | 13 | 20.57 | 18.49 | 26.42 | -19.03 | -16.68 | 1.000 | 1.000 |  | 15.10 | 0.69 | 1 | False | False |
| baselines-margin | seasonal_naive_drift | W1 | 1 | PIT | 13 | 25.88 | 25.75 | 29.15 | 3.23 | 1.23 | 1.258 | 1.393 |  | 17.29 | 0.62 | 1 | False | False |
| baselines-margin | pct_rev_last4 | W1 | 1 | PIT | 13 | 40.28 | 38.87 | 54.63 | 28.45 | 20.86 | 1.959 | 2.103 |  | 27.36 | 0.85 | 3 | False | False |
| baselines-margin | seasonal_naive | W1 | 1 | full_sample | 13 | 20.57 | 18.49 | 26.42 | -19.03 | -16.68 | 1.000 | 1.000 |  | 14.84 | 0.77 | 1 | False | False |
| baselines-margin | seasonal_naive_drift | W1 | 1 | full_sample | 13 | 25.88 | 25.75 | 29.15 | 3.23 | 1.23 | 1.258 | 1.393 |  | 16.87 | 0.77 | 1 | False | False |
| baselines-margin | pct_rev_last4 | W1 | 1 | full_sample | 13 | 40.28 | 38.87 | 54.63 | 28.45 | 20.86 | 1.959 | 2.103 |  | 27.69 | 0.77 | 3 | False | False |
| baselines-margin | seasonal_naive | W1 | 2 | PIT | 12 | 17.57 | 17.62 | 22.13 | -15.90 | -15.77 | 1.000 | 1.000 |  | 12.36 | 0.75 | 1 | False | False |
| baselines-margin | seasonal_naive_drift | W1 | 2 | PIT | 12 | 23.88 | 22.88 | 29.70 | 5.05 | -2.21 | 1.359 | 1.298 |  | 16.68 | 0.67 | 1 | False | False |
| baselines-margin | pct_rev_last4 | W1 | 2 | PIT | 12 | 48.35 | 42.55 | 64.99 | 36.81 | 26.16 | 2.752 | 2.415 |  | 33.38 | 0.75 | 3 | False | False |
| baselines-margin | seasonal_naive | W1 | 2 | full_sample | 12 | 17.57 | 17.62 | 22.13 | -15.90 | -15.77 | 1.000 | 1.000 |  | 12.36 | 0.83 | 1 | False | False |
| baselines-margin | seasonal_naive_drift | W1 | 2 | full_sample | 12 | 23.88 | 22.88 | 29.70 | 5.05 | -2.21 | 1.359 | 1.298 |  | 16.37 | 0.67 | 1 | False | False |
| baselines-margin | pct_rev_last4 | W1 | 2 | full_sample | 12 | 48.35 | 42.55 | 64.99 | 36.81 | 26.16 | 2.752 | 2.415 |  | 32.51 | 0.75 | 3 | False | False |
| baselines-margin | seasonal_naive | W2 | 0 | PIT | 10 | 17.20 | 17.55 | 22.32 | -15.20 | -15.59 | 1.000 | 1.000 |  | 12.32 | 0.80 | 1 | False | False |
| baselines-margin | seasonal_naive_drift | W2 | 0 | PIT | 10 | 19.10 | 18.02 | 23.33 | -0.30 | 0.18 | 1.110 | 1.027 |  | 13.41 | 0.70 | 1 | False | False |
| baselines-margin | pct_rev_last4 | W2 | 0 | PIT | 10 | 34.74 | 37.21 | 44.07 | 15.66 | 17.59 | 2.020 | 2.120 |  | 22.83 | 0.90 | 3 | False | False |
| baselines-margin | seasonal_naive | W2 | 0 | full_sample | 10 | 17.20 | 17.55 | 22.32 | -15.20 | -15.59 | 1.000 | 1.000 |  | 12.48 | 0.80 | 1 | False | False |
| baselines-margin | seasonal_naive_drift | W2 | 0 | full_sample | 10 | 19.10 | 18.02 | 23.33 | -0.30 | 0.18 | 1.110 | 1.027 |  | 13.24 | 0.80 | 1 | False | False |
| baselines-margin | pct_rev_last4 | W2 | 0 | full_sample | 10 | 34.97 | 37.52 | 44.71 | 16.61 | 18.90 | 2.033 | 2.138 |  | 22.78 | 0.90 | 3 | False | False |
| baselines-margin | seasonal_naive | W2 | 1 | PIT | 9 | 19.00 | 18.25 | 23.52 | -17.00 | -16.29 | 1.000 | 1.000 |  | 13.10 | 0.78 | 1 | False | False |
| baselines-margin | seasonal_naive_drift | W2 | 1 | PIT | 9 | 24.11 | 25.12 | 28.06 | -2.56 | -1.30 | 1.269 | 1.376 |  | 16.23 | 0.78 | 1 | False | False |
| baselines-margin | pct_rev_last4 | W2 | 1 | PIT | 9 | 39.70 | 38.94 | 50.99 | 24.31 | 19.17 | 2.090 | 2.133 |  | 26.41 | 0.89 | 3 | False | False |
| baselines-margin | seasonal_naive | W2 | 1 | full_sample | 9 | 19.00 | 18.25 | 23.52 | -17.00 | -16.29 | 1.000 | 1.000 |  | 13.29 | 0.78 | 1 | False | False |
| baselines-margin | seasonal_naive_drift | W2 | 1 | full_sample | 9 | 24.11 | 25.12 | 28.06 | -2.56 | -1.30 | 1.269 | 1.376 |  | 16.16 | 0.78 | 1 | False | False |
| baselines-margin | pct_rev_last4 | W2 | 1 | full_sample | 9 | 39.70 | 38.94 | 50.99 | 24.31 | 19.17 | 2.090 | 2.133 |  | 26.30 | 0.78 | 3 | False | False |
| baselines-margin | seasonal_naive | W2 | 2 | PIT | 8 | 19.38 | 18.37 | 24.30 | -17.12 | -16.30 | 1.000 | 1.000 |  | 13.94 | 0.75 | 1 | False | False |
| baselines-margin | seasonal_naive_drift | W2 | 2 | PIT | 8 | 22.62 | 22.15 | 27.23 | -5.62 | -7.12 | 1.168 | 1.205 |  | 14.90 | 0.75 | 1 | False | False |
| baselines-margin | pct_rev_last4 | W2 | 2 | PIT | 8 | 47.62 | 42.34 | 62.05 | 31.27 | 23.55 | 2.458 | 2.304 |  | 31.06 | 0.75 | 3 | False | False |
| baselines-margin | seasonal_naive | W2 | 2 | full_sample | 8 | 19.38 | 18.37 | 24.30 | -17.12 | -16.30 | 1.000 | 1.000 |  | 13.66 | 0.75 | 1 | False | False |
| baselines-margin | seasonal_naive_drift | W2 | 2 | full_sample | 8 | 22.62 | 22.15 | 27.23 | -5.62 | -7.12 | 1.168 | 1.205 |  | 14.81 | 0.75 | 1 | False | False |
| baselines-margin | pct_rev_last4 | W2 | 2 | full_sample | 8 | 47.62 | 42.34 | 62.05 | 31.27 | 23.55 | 2.458 | 2.304 |  | 31.19 | 0.75 | 3 | False | False |

## target: `ops_cash_per_night`

| method | object | window | h | replay | n | mae | rw_mae | rmse | bias | rw_bias | r_sn | rw_r_sn | r_street | crps | cov80 | n_params | both | rw_both |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| baselines-margin | seasonal_naive | W1 | 0 | PIT | 14 | 0.14 | 0.13 | 0.16 | 0.06 | 0.08 | 1.000 | 1.000 |  | 0.11 | 0.86 | 1 | False | False |
| baselines-margin | seasonal_naive_drift | W1 | 0 | PIT | 14 | 0.18 | 0.17 | 0.21 | -0.00 | 0.01 | 1.304 | 1.292 |  | 0.15 | 0.93 | 1 | False | False |
| baselines-margin | trailing4 | W1 | 0 | PIT | 14 | 0.22 | 0.23 | 0.27 | 0.07 | 0.09 | 1.529 | 1.711 |  | 0.15 | 0.71 | 2 | False | False |
| baselines-margin | seasonal_naive | W1 | 0 | full_sample | 14 | 0.14 | 0.13 | 0.16 | 0.06 | 0.08 | 1.000 | 1.000 |  | 0.10 | 1.00 | 1 | False | False |
| baselines-margin | seasonal_naive_drift | W1 | 0 | full_sample | 14 | 0.18 | 0.17 | 0.21 | -0.00 | 0.01 | 1.304 | 1.292 |  | 0.14 | 1.00 | 1 | False | False |
| baselines-margin | trailing4 | W1 | 0 | full_sample | 14 | 0.22 | 0.23 | 0.27 | 0.07 | 0.09 | 1.529 | 1.711 |  | 0.15 | 0.71 | 2 | False | False |
| baselines-margin | seasonal_naive | W1 | 1 | PIT | 13 | 0.15 | 0.13 | 0.17 | 0.07 | 0.08 | 1.000 | 1.000 |  | 0.10 | 0.92 | 1 | False | False |
| baselines-margin | trailing4 | W1 | 1 | PIT | 13 | 0.20 | 0.21 | 0.27 | 0.07 | 0.10 | 1.363 | 1.573 |  | 0.15 | 0.77 | 2 | False | False |
| baselines-margin | seasonal_naive_drift | W1 | 1 | PIT | 13 | 0.22 | 0.21 | 0.26 | 0.00 | 0.00 | 1.499 | 1.590 |  | 0.17 | 1.00 | 1 | False | False |
| baselines-margin | seasonal_naive | W1 | 1 | full_sample | 13 | 0.15 | 0.13 | 0.17 | 0.07 | 0.08 | 1.000 | 1.000 |  | 0.10 | 0.85 | 1 | False | False |
| baselines-margin | trailing4 | W1 | 1 | full_sample | 13 | 0.20 | 0.21 | 0.27 | 0.07 | 0.10 | 1.363 | 1.573 |  | 0.15 | 0.85 | 2 | False | False |
| baselines-margin | seasonal_naive_drift | W1 | 1 | full_sample | 13 | 0.22 | 0.21 | 0.26 | 0.00 | 0.00 | 1.499 | 1.590 |  | 0.16 | 1.00 | 1 | False | False |
| baselines-margin | seasonal_naive | W1 | 2 | PIT | 12 | 0.14 | 0.13 | 0.16 | 0.09 | 0.09 | 1.000 | 1.000 |  | 0.09 | 0.67 | 1 | False | False |
| baselines-margin | seasonal_naive_drift | W1 | 2 | PIT | 12 | 0.17 | 0.16 | 0.23 | 0.02 | -0.03 | 1.250 | 1.232 |  | 0.15 | 1.00 | 1 | False | False |
| baselines-margin | trailing4 | W1 | 2 | PIT | 12 | 0.22 | 0.22 | 0.28 | 0.09 | 0.12 | 1.560 | 1.637 |  | 0.16 | 0.75 | 2 | False | False |
| baselines-margin | seasonal_naive | W1 | 2 | full_sample | 12 | 0.14 | 0.13 | 0.16 | 0.09 | 0.09 | 1.000 | 1.000 |  | 0.09 | 0.58 | 1 | False | False |
| baselines-margin | seasonal_naive_drift | W1 | 2 | full_sample | 12 | 0.17 | 0.16 | 0.23 | 0.02 | -0.03 | 1.250 | 1.232 |  | 0.14 | 0.92 | 1 | False | False |
| baselines-margin | trailing4 | W1 | 2 | full_sample | 12 | 0.22 | 0.22 | 0.28 | 0.09 | 0.12 | 1.560 | 1.637 |  | 0.16 | 0.75 | 2 | False | False |
| baselines-margin | seasonal_naive | W2 | 0 | PIT | 10 | 0.14 | 0.13 | 0.16 | 0.08 | 0.08 | 1.000 | 1.000 |  | 0.10 | 0.80 | 1 | False | False |
| baselines-margin | seasonal_naive_drift | W2 | 0 | PIT | 10 | 0.17 | 0.17 | 0.21 | -0.01 | 0.00 | 1.212 | 1.273 |  | 0.13 | 0.90 | 1 | False | False |
| baselines-margin | trailing4 | W2 | 0 | PIT | 10 | 0.25 | 0.24 | 0.30 | 0.09 | 0.10 | 1.801 | 1.830 |  | 0.17 | 0.60 | 2 | False | False |
| baselines-margin | seasonal_naive | W2 | 0 | full_sample | 10 | 0.14 | 0.13 | 0.16 | 0.08 | 0.08 | 1.000 | 1.000 |  | 0.10 | 1.00 | 1 | False | False |
| baselines-margin | seasonal_naive_drift | W2 | 0 | full_sample | 10 | 0.17 | 0.17 | 0.21 | -0.01 | 0.00 | 1.212 | 1.273 |  | 0.13 | 1.00 | 1 | False | False |
| baselines-margin | trailing4 | W2 | 0 | full_sample | 10 | 0.25 | 0.24 | 0.30 | 0.09 | 0.10 | 1.801 | 1.830 |  | 0.17 | 0.60 | 2 | False | False |
| baselines-margin | seasonal_naive | W2 | 1 | PIT | 9 | 0.13 | 0.13 | 0.15 | 0.07 | 0.08 | 1.000 | 1.000 |  | 0.09 | 0.89 | 1 | False | False |
| baselines-margin | seasonal_naive_drift | W2 | 1 | PIT | 9 | 0.20 | 0.21 | 0.23 | -0.02 | -0.01 | 1.487 | 1.614 |  | 0.15 | 1.00 | 1 | False | False |
| baselines-margin | trailing4 | W2 | 1 | PIT | 9 | 0.21 | 0.21 | 0.26 | 0.06 | 0.10 | 1.530 | 1.635 |  | 0.15 | 0.78 | 2 | False | False |
| baselines-margin | seasonal_naive | W2 | 1 | full_sample | 9 | 0.13 | 0.13 | 0.15 | 0.07 | 0.08 | 1.000 | 1.000 |  | 0.09 | 0.89 | 1 | False | False |
| baselines-margin | seasonal_naive_drift | W2 | 1 | full_sample | 9 | 0.20 | 0.21 | 0.23 | -0.02 | -0.01 | 1.487 | 1.614 |  | 0.14 | 1.00 | 1 | False | False |
| baselines-margin | trailing4 | W2 | 1 | full_sample | 9 | 0.21 | 0.21 | 0.26 | 0.06 | 0.10 | 1.530 | 1.635 |  | 0.15 | 0.89 | 2 | False | False |
| baselines-margin | seasonal_naive | W2 | 2 | PIT | 8 | 0.14 | 0.13 | 0.16 | 0.07 | 0.08 | 1.000 | 1.000 |  | 0.09 | 0.75 | 1 | False | False |
| baselines-margin | seasonal_naive_drift | W2 | 2 | PIT | 8 | 0.17 | 0.16 | 0.21 | -0.05 | -0.06 | 1.177 | 1.205 |  | 0.14 | 1.00 | 1 | False | False |
| baselines-margin | trailing4 | W2 | 2 | PIT | 8 | 0.22 | 0.22 | 0.27 | 0.09 | 0.12 | 1.584 | 1.656 |  | 0.16 | 0.75 | 2 | False | False |
| baselines-margin | seasonal_naive | W2 | 2 | full_sample | 8 | 0.14 | 0.13 | 0.16 | 0.07 | 0.08 | 1.000 | 1.000 |  | 0.09 | 0.62 | 1 | False | False |
| baselines-margin | seasonal_naive_drift | W2 | 2 | full_sample | 8 | 0.17 | 0.16 | 0.21 | -0.05 | -0.06 | 1.177 | 1.205 |  | 0.13 | 1.00 | 1 | False | False |
| baselines-margin | trailing4 | W2 | 2 | full_sample | 8 | 0.22 | 0.22 | 0.27 | 0.09 | 0.12 | 1.584 | 1.656 |  | 0.15 | 0.75 | 2 | False | False |

## target: `pd_cash_musd`

| method | object | window | h | replay | n | mae | rw_mae | rmse | bias | rw_bias | r_sn | rw_r_sn | r_street | crps | cov80 | n_params | both | rw_both |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| baselines-margin | seasonal_naive_drift | W1 | 0 | PIT | 14 | 10.09 | 8.81 | 12.60 | -2.53 | -1.68 | 0.305 | 0.234 |  | 7.50 | 0.93 | 1 | True | True |
| baselines-margin | seasonal_naive | W1 | 0 | PIT | 14 | 33.04 | 37.58 | 36.18 | -33.04 | -37.58 | 1.000 | 1.000 |  | 24.79 | 0.14 | 1 | False | False |
| baselines-margin | pct_rev_last4 | W1 | 0 | PIT | 14 | 59.07 | 57.72 | 75.11 | 12.86 | 8.65 | 1.788 | 1.536 |  | 40.53 | 0.86 | 3 | False | False |
| baselines-margin | seasonal_naive_drift | W1 | 0 | full_sample | 14 | 10.09 | 8.81 | 12.60 | -2.53 | -1.68 | 0.305 | 0.234 |  | 7.57 | 0.93 | 1 | True | True |
| baselines-margin | seasonal_naive | W1 | 0 | full_sample | 14 | 33.04 | 37.58 | 36.18 | -33.04 | -37.58 | 1.000 | 1.000 |  | 24.64 | 0.29 | 1 | False | False |
| baselines-margin | pct_rev_last4 | W1 | 0 | full_sample | 14 | 59.12 | 57.96 | 74.95 | 13.18 | 9.80 | 1.789 | 1.543 |  | 40.02 | 0.79 | 3 | False | False |
| baselines-margin | seasonal_naive_drift | W1 | 1 | PIT | 13 | 15.13 | 13.09 | 18.45 | -3.58 | -2.13 | 0.451 | 0.346 |  | 10.83 | 0.85 | 1 | True | True |
| baselines-margin | seasonal_naive | W1 | 1 | PIT | 13 | 33.59 | 37.79 | 36.85 | -33.59 | -37.79 | 1.000 | 1.000 |  | 26.15 | 0.08 | 1 | False | False |
| baselines-margin | pct_rev_last4 | W1 | 1 | PIT | 13 | 63.20 | 57.33 | 79.44 | 20.09 | 5.23 | 1.882 | 1.517 |  | 42.38 | 0.77 | 3 | False | False |
| baselines-margin | seasonal_naive_drift | W1 | 1 | full_sample | 13 | 15.13 | 13.09 | 18.45 | -3.58 | -2.13 | 0.451 | 0.346 |  | 10.79 | 0.69 | 1 | True | True |
| baselines-margin | seasonal_naive | W1 | 1 | full_sample | 13 | 33.59 | 37.79 | 36.85 | -33.59 | -37.79 | 1.000 | 1.000 |  | 25.99 | 0.15 | 1 | False | False |
| baselines-margin | pct_rev_last4 | W1 | 1 | full_sample | 13 | 63.20 | 57.33 | 79.44 | 20.09 | 5.23 | 1.882 | 1.517 |  | 42.49 | 0.85 | 3 | False | False |
| baselines-margin | seasonal_naive_drift | W1 | 2 | PIT | 12 | 17.11 | 15.30 | 21.42 | -3.80 | -0.87 | 0.505 | 0.403 |  | 12.77 | 0.75 | 1 | True | True |
| baselines-margin | seasonal_naive | W1 | 2 | PIT | 12 | 33.89 | 37.97 | 37.37 | -33.89 | -37.97 | 1.000 | 1.000 |  | 26.41 | 0.08 | 1 | False | False |
| baselines-margin | pct_rev_last4 | W1 | 2 | PIT | 12 | 68.56 | 60.25 | 87.88 | 21.67 | 4.42 | 2.023 | 1.587 |  | 48.44 | 0.75 | 3 | False | False |
| baselines-margin | seasonal_naive_drift | W1 | 2 | full_sample | 12 | 17.11 | 15.30 | 21.42 | -3.80 | -0.87 | 0.505 | 0.403 |  | 12.35 | 0.83 | 1 | True | True |
| baselines-margin | seasonal_naive | W1 | 2 | full_sample | 12 | 33.89 | 37.97 | 37.37 | -33.89 | -37.97 | 1.000 | 1.000 |  | 26.06 | 0.25 | 1 | False | False |
| baselines-margin | pct_rev_last4 | W1 | 2 | full_sample | 12 | 68.56 | 60.25 | 87.88 | 21.67 | 4.42 | 2.023 | 1.587 |  | 46.40 | 0.92 | 3 | False | False |
| baselines-margin | seasonal_naive_drift | W2 | 0 | PIT | 10 | 9.30 | 8.49 | 12.30 | -3.90 | -2.18 | 0.239 | 0.213 |  | 7.25 | 0.90 | 1 | True | True |
| baselines-margin | seasonal_naive | W2 | 0 | PIT | 10 | 38.90 | 39.83 | 40.69 | -38.90 | -39.83 | 1.000 | 1.000 |  | 29.50 | 0.00 | 1 | False | False |
| baselines-margin | pct_rev_last4 | W2 | 0 | PIT | 10 | 59.03 | 57.66 | 71.27 | 4.25 | 5.36 | 1.517 | 1.448 |  | 39.37 | 0.90 | 3 | False | False |
| baselines-margin | seasonal_naive_drift | W2 | 0 | full_sample | 10 | 9.30 | 8.49 | 12.30 | -3.90 | -2.18 | 0.239 | 0.213 |  | 7.54 | 0.90 | 1 | True | True |
| baselines-margin | seasonal_naive | W2 | 0 | full_sample | 10 | 38.90 | 39.83 | 40.69 | -38.90 | -39.83 | 1.000 | 1.000 |  | 29.32 | 0.20 | 1 | False | False |
| baselines-margin | pct_rev_last4 | W2 | 0 | full_sample | 10 | 59.26 | 57.98 | 71.65 | 5.28 | 6.79 | 1.523 | 1.456 |  | 39.24 | 0.80 | 3 | False | False |
| baselines-margin | seasonal_naive_drift | W2 | 1 | PIT | 9 | 14.56 | 12.75 | 18.50 | -6.33 | -2.91 | 0.354 | 0.313 |  | 10.94 | 0.78 | 1 | True | True |
| baselines-margin | seasonal_naive | W2 | 1 | PIT | 9 | 41.11 | 40.71 | 42.42 | -41.11 | -40.71 | 1.000 | 1.000 |  | 32.21 | 0.00 | 1 | False | False |
| baselines-margin | pct_rev_last4 | W2 | 1 | PIT | 9 | 61.07 | 56.46 | 74.63 | 8.93 | 1.30 | 1.485 | 1.387 |  | 41.26 | 0.78 | 3 | False | False |
| baselines-margin | seasonal_naive_drift | W2 | 1 | full_sample | 9 | 14.56 | 12.75 | 18.50 | -6.33 | -2.91 | 0.354 | 0.313 |  | 10.91 | 0.78 | 1 | True | True |
| baselines-margin | seasonal_naive | W2 | 1 | full_sample | 9 | 41.11 | 40.71 | 42.42 | -41.11 | -40.71 | 1.000 | 1.000 |  | 32.39 | 0.00 | 1 | False | False |
| baselines-margin | pct_rev_last4 | W2 | 1 | full_sample | 9 | 61.07 | 56.46 | 74.63 | 8.93 | 1.30 | 1.485 | 1.387 |  | 41.44 | 0.89 | 3 | False | False |
| baselines-margin | seasonal_naive_drift | W2 | 2 | PIT | 8 | 20.00 | 16.02 | 24.56 | -8.25 | -1.79 | 0.457 | 0.383 |  | 15.28 | 0.62 | 1 | True | True |
| baselines-margin | seasonal_naive | W2 | 2 | PIT | 8 | 43.75 | 41.81 | 44.43 | -43.75 | -41.81 | 1.000 | 1.000 |  | 34.73 | 0.00 | 1 | False | False |
| baselines-margin | pct_rev_last4 | W2 | 2 | PIT | 8 | 65.55 | 59.10 | 81.05 | 5.40 | -2.41 | 1.498 | 1.413 |  | 45.08 | 0.75 | 3 | False | False |
| baselines-margin | seasonal_naive_drift | W2 | 2 | full_sample | 8 | 20.00 | 16.02 | 24.56 | -8.25 | -1.79 | 0.457 | 0.383 |  | 14.59 | 0.75 | 1 | True | True |
| baselines-margin | seasonal_naive | W2 | 2 | full_sample | 8 | 43.75 | 41.81 | 44.43 | -43.75 | -41.81 | 1.000 | 1.000 |  | 34.59 | 0.00 | 1 | False | False |
| baselines-margin | pct_rev_last4 | W2 | 2 | full_sample | 8 | 65.55 | 59.10 | 81.05 | 5.40 | -2.41 | 1.498 | 1.413 |  | 44.68 | 1.00 | 3 | False | False |

## target: `pd_cash_per_night`

| method | object | window | h | replay | n | mae | rw_mae | rmse | bias | rw_bias | r_sn | rw_r_sn | r_street | crps | cov80 | n_params | both | rw_both |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| baselines-margin | seasonal_naive_drift | W1 | 0 | PIT | 14 | 0.12 | 0.09 | 0.15 | -0.04 | -0.01 | 0.997 | 0.838 |  | 0.15 | 1.00 | 1 | True | True |
| baselines-margin | seasonal_naive | W1 | 0 | PIT | 14 | 0.12 | 0.10 | 0.15 | -0.03 | -0.07 | 1.000 | 1.000 |  | 0.13 | 1.00 | 1 | False | False |
| baselines-margin | trailing4 | W1 | 0 | PIT | 14 | 0.13 | 0.11 | 0.17 | -0.00 | -0.03 | 1.087 | 1.044 |  | 0.10 | 0.93 | 2 | False | False |
| baselines-margin | seasonal_naive_drift | W1 | 0 | full_sample | 14 | 0.12 | 0.09 | 0.15 | -0.04 | -0.01 | 0.997 | 0.838 |  | 0.14 | 1.00 | 1 | True | True |
| baselines-margin | seasonal_naive | W1 | 0 | full_sample | 14 | 0.12 | 0.10 | 0.15 | -0.03 | -0.07 | 1.000 | 1.000 |  | 0.14 | 1.00 | 1 | False | False |
| baselines-margin | trailing4 | W1 | 0 | full_sample | 14 | 0.13 | 0.11 | 0.17 | -0.00 | -0.03 | 1.087 | 1.044 |  | 0.10 | 0.93 | 2 | False | False |
| baselines-margin | seasonal_naive | W1 | 1 | PIT | 13 | 0.12 | 0.10 | 0.15 | -0.04 | -0.07 | 1.000 | 1.000 |  | 0.09 | 1.00 | 1 | False | False |
| baselines-margin | trailing4 | W1 | 1 | PIT | 13 | 0.15 | 0.12 | 0.19 | -0.03 | -0.05 | 1.222 | 1.215 |  | 0.12 | 1.00 | 2 | False | False |
| baselines-margin | seasonal_naive_drift | W1 | 1 | PIT | 13 | 0.17 | 0.13 | 0.22 | -0.06 | -0.01 | 1.402 | 1.279 |  | 0.18 | 1.00 | 1 | False | False |
| baselines-margin | seasonal_naive | W1 | 1 | full_sample | 13 | 0.12 | 0.10 | 0.15 | -0.04 | -0.07 | 1.000 | 1.000 |  | 0.10 | 1.00 | 1 | False | False |
| baselines-margin | trailing4 | W1 | 1 | full_sample | 13 | 0.15 | 0.12 | 0.19 | -0.03 | -0.05 | 1.222 | 1.215 |  | 0.12 | 0.92 | 2 | False | False |
| baselines-margin | seasonal_naive_drift | W1 | 1 | full_sample | 13 | 0.17 | 0.13 | 0.22 | -0.06 | -0.01 | 1.402 | 1.279 |  | 0.15 | 1.00 | 1 | False | False |
| baselines-margin | seasonal_naive | W1 | 2 | PIT | 12 | 0.13 | 0.10 | 0.15 | -0.04 | -0.07 | 1.000 | 1.000 |  | 0.09 | 0.75 | 1 | False | False |
| baselines-margin | trailing4 | W1 | 2 | PIT | 12 | 0.17 | 0.14 | 0.21 | -0.05 | -0.07 | 1.345 | 1.396 |  | 0.14 | 1.00 | 2 | False | False |
| baselines-margin | seasonal_naive_drift | W1 | 2 | PIT | 12 | 0.18 | 0.15 | 0.22 | -0.06 | 0.01 | 1.376 | 1.454 |  | 0.16 | 1.00 | 1 | False | False |
| baselines-margin | seasonal_naive | W1 | 2 | full_sample | 12 | 0.13 | 0.10 | 0.15 | -0.04 | -0.07 | 1.000 | 1.000 |  | 0.09 | 1.00 | 1 | False | False |
| baselines-margin | trailing4 | W1 | 2 | full_sample | 12 | 0.17 | 0.14 | 0.21 | -0.05 | -0.07 | 1.345 | 1.396 |  | 0.14 | 1.00 | 2 | False | False |
| baselines-margin | seasonal_naive_drift | W1 | 2 | full_sample | 12 | 0.18 | 0.15 | 0.22 | -0.06 | 0.01 | 1.376 | 1.454 |  | 0.14 | 1.00 | 1 | False | False |
| baselines-margin | seasonal_naive_drift | W2 | 0 | PIT | 10 | 0.09 | 0.08 | 0.12 | -0.03 | -0.01 | 0.824 | 0.780 |  | 0.11 | 1.00 | 1 | True | True |
| baselines-margin | trailing4 | W2 | 0 | PIT | 10 | 0.11 | 0.10 | 0.16 | -0.05 | -0.04 | 0.988 | 1.015 |  | 0.09 | 0.90 | 2 | False | False |
| baselines-margin | seasonal_naive | W2 | 0 | PIT | 10 | 0.11 | 0.10 | 0.14 | -0.10 | -0.09 | 1.000 | 1.000 |  | 0.11 | 1.00 | 1 | False | False |
| baselines-margin | seasonal_naive_drift | W2 | 0 | full_sample | 10 | 0.09 | 0.08 | 0.12 | -0.03 | -0.01 | 0.824 | 0.780 |  | 0.13 | 1.00 | 1 | True | True |
| baselines-margin | trailing4 | W2 | 0 | full_sample | 10 | 0.11 | 0.10 | 0.16 | -0.05 | -0.04 | 0.988 | 1.015 |  | 0.09 | 0.90 | 2 | False | False |
| baselines-margin | seasonal_naive | W2 | 0 | full_sample | 10 | 0.11 | 0.10 | 0.14 | -0.10 | -0.09 | 1.000 | 1.000 |  | 0.14 | 1.00 | 1 | False | False |
| baselines-margin | seasonal_naive | W2 | 1 | PIT | 9 | 0.12 | 0.10 | 0.15 | -0.11 | -0.09 | 1.000 | 1.000 |  | 0.09 | 1.00 | 1 | False | False |
| baselines-margin | trailing4 | W2 | 1 | PIT | 9 | 0.13 | 0.12 | 0.19 | -0.09 | -0.07 | 1.093 | 1.173 |  | 0.12 | 1.00 | 2 | False | False |
| baselines-margin | seasonal_naive_drift | W2 | 1 | PIT | 9 | 0.14 | 0.12 | 0.17 | -0.05 | -0.00 | 1.205 | 1.215 |  | 0.14 | 1.00 | 1 | False | False |
| baselines-margin | seasonal_naive | W2 | 1 | full_sample | 9 | 0.12 | 0.10 | 0.15 | -0.11 | -0.09 | 1.000 | 1.000 |  | 0.10 | 1.00 | 1 | False | False |
| baselines-margin | trailing4 | W2 | 1 | full_sample | 9 | 0.13 | 0.12 | 0.19 | -0.09 | -0.07 | 1.093 | 1.173 |  | 0.12 | 0.89 | 2 | False | False |
| baselines-margin | seasonal_naive_drift | W2 | 1 | full_sample | 9 | 0.14 | 0.12 | 0.17 | -0.05 | -0.00 | 1.205 | 1.215 |  | 0.14 | 1.00 | 1 | False | False |
| baselines-margin | seasonal_naive | W2 | 2 | PIT | 8 | 0.13 | 0.10 | 0.15 | -0.13 | -0.10 | 1.000 | 1.000 |  | 0.09 | 0.88 | 1 | False | False |
| baselines-margin | trailing4 | W2 | 2 | PIT | 8 | 0.16 | 0.14 | 0.21 | -0.13 | -0.10 | 1.210 | 1.332 |  | 0.13 | 1.00 | 2 | False | False |
| baselines-margin | seasonal_naive_drift | W2 | 2 | PIT | 8 | 0.18 | 0.15 | 0.23 | -0.05 | 0.02 | 1.409 | 1.469 |  | 0.15 | 1.00 | 1 | False | False |
| baselines-margin | seasonal_naive | W2 | 2 | full_sample | 8 | 0.13 | 0.10 | 0.15 | -0.13 | -0.10 | 1.000 | 1.000 |  | 0.09 | 1.00 | 1 | False | False |
| baselines-margin | trailing4 | W2 | 2 | full_sample | 8 | 0.16 | 0.14 | 0.21 | -0.13 | -0.10 | 1.210 | 1.332 |  | 0.14 | 1.00 | 2 | False | False |
| baselines-margin | seasonal_naive_drift | W2 | 2 | full_sample | 8 | 0.18 | 0.15 | 0.23 | -0.05 | 0.02 | 1.409 | 1.469 |  | 0.15 | 1.00 | 1 | False | False |

## target: `pretax_income_musd`

| method | object | window | h | replay | n | mae | rw_mae | rmse | bias | rw_bias | r_sn | rw_r_sn | r_street | crps | cov80 | n_params | both | rw_both |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| baselines-margin | seasonal_naive | W1 | 0 | PIT | 14 | 251.86 | 201.06 | 372.81 | -98.15 | -82.07 | 1.000 | 1.000 |  | 270.01 | 1.00 | 1 | False | False |
| baselines-margin | seasonal_naive_drift | W1 | 0 | PIT | 14 | 400.40 | 336.98 | 571.75 | 10.97 | -3.98 | 1.590 | 1.676 |  | 391.68 | 1.00 | 1 | False | False |
| baselines-margin | seasonal_naive | W1 | 0 | full_sample | 14 | 251.86 | 201.06 | 372.81 | -98.15 | -82.07 | 1.000 | 1.000 |  | 280.43 | 1.00 | 1 | False | False |
| baselines-margin | seasonal_naive_drift | W1 | 0 | full_sample | 14 | 400.40 | 336.98 | 571.75 | 10.97 | -3.98 | 1.590 | 1.676 |  | 377.86 | 1.00 | 1 | False | False |
| baselines-margin | seasonal_naive | W1 | 1 | PIT | 13 | 260.61 | 202.24 | 384.98 | -95.08 | -81.02 | 1.000 | 1.000 |  | 210.03 | 0.85 | 1 | False | False |
| baselines-margin | seasonal_naive_drift | W1 | 1 | PIT | 13 | 414.02 | 372.86 | 543.27 | 14.13 | -9.26 | 1.589 | 1.844 |  | 363.46 | 1.00 | 1 | False | False |
| baselines-margin | seasonal_naive | W1 | 1 | full_sample | 13 | 260.61 | 202.24 | 384.98 | -95.08 | -81.02 | 1.000 | 1.000 |  | 207.80 | 0.85 | 1 | False | False |
| baselines-margin | seasonal_naive_drift | W1 | 1 | full_sample | 13 | 414.02 | 372.86 | 543.27 | 14.13 | -9.26 | 1.589 | 1.844 |  | 343.68 | 1.00 | 1 | False | False |
| baselines-margin | seasonal_naive | W1 | 2 | PIT | 12 | 257.93 | 200.18 | 391.68 | -78.59 | -76.21 | 1.000 | 1.000 |  | 224.58 | 0.67 | 1 | False | False |
| baselines-margin | seasonal_naive_drift | W1 | 2 | PIT | 12 | 371.38 | 293.82 | 516.50 | 58.80 | 60.59 | 1.440 | 1.468 |  | 368.37 | 1.00 | 1 | False | False |
| baselines-margin | seasonal_naive | W1 | 2 | full_sample | 12 | 257.93 | 200.18 | 391.68 | -78.59 | -76.21 | 1.000 | 1.000 |  | 207.52 | 0.83 | 1 | False | False |
| baselines-margin | seasonal_naive_drift | W1 | 2 | full_sample | 12 | 371.38 | 293.82 | 516.50 | 58.80 | 60.59 | 1.440 | 1.468 |  | 326.20 | 1.00 | 1 | False | False |
| baselines-margin | seasonal_naive | W2 | 0 | PIT | 10 | 195.90 | 176.18 | 338.38 | -126.10 | -94.09 | 1.000 | 1.000 |  | 216.08 | 1.00 | 1 | False | False |
| baselines-margin | seasonal_naive_drift | W2 | 0 | PIT | 10 | 406.50 | 324.55 | 568.38 | -84.50 | -38.86 | 2.075 | 1.842 |  | 340.76 | 1.00 | 1 | False | False |
| baselines-margin | seasonal_naive | W2 | 0 | full_sample | 10 | 195.90 | 176.18 | 338.38 | -126.10 | -94.09 | 1.000 | 1.000 |  | 268.43 | 1.00 | 1 | False | False |
| baselines-margin | seasonal_naive_drift | W2 | 0 | full_sample | 10 | 406.50 | 324.55 | 568.38 | -84.50 | -38.86 | 2.075 | 1.842 |  | 376.17 | 1.00 | 1 | False | False |
| baselines-margin | seasonal_naive | W2 | 1 | PIT | 9 | 199.56 | 176.74 | 352.53 | -122.00 | -91.17 | 1.000 | 1.000 |  | 187.42 | 0.89 | 1 | False | False |
| baselines-margin | seasonal_naive_drift | W2 | 1 | PIT | 9 | 424.89 | 367.09 | 543.87 | -87.78 | -48.58 | 2.129 | 2.077 |  | 331.48 | 1.00 | 1 | False | False |
| baselines-margin | seasonal_naive | W2 | 1 | full_sample | 9 | 199.56 | 176.74 | 352.53 | -122.00 | -91.17 | 1.000 | 1.000 |  | 186.00 | 0.89 | 1 | False | False |
| baselines-margin | seasonal_naive_drift | W2 | 1 | full_sample | 9 | 424.89 | 367.09 | 543.87 | -87.78 | -48.58 | 2.129 | 2.077 |  | 344.20 | 1.00 | 1 | False | False |
| baselines-margin | seasonal_naive | W2 | 2 | PIT | 8 | 223.88 | 185.85 | 373.91 | -136.62 | -95.74 | 1.000 | 1.000 |  | 195.52 | 0.88 | 1 | False | False |
| baselines-margin | seasonal_naive_drift | W2 | 2 | PIT | 8 | 365.00 | 278.79 | 530.78 | -69.50 | 15.36 | 1.630 | 1.500 |  | 334.98 | 1.00 | 1 | False | False |
| baselines-margin | seasonal_naive | W2 | 2 | full_sample | 8 | 223.88 | 185.85 | 373.91 | -136.62 | -95.74 | 1.000 | 1.000 |  | 190.77 | 0.88 | 1 | False | False |
| baselines-margin | seasonal_naive_drift | W2 | 2 | full_sample | 8 | 365.00 | 278.79 | 530.78 | -69.50 | 15.36 | 1.630 | 1.500 |  | 327.61 | 1.00 | 1 | False | False |

## target: `revenue_musd`

| method | object | window | h | replay | n | mae | rw_mae | rmse | bias | rw_bias | r_sn | rw_r_sn | r_street | crps | cov80 | n_params | both | rw_both |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| baselines-margin | street | W1 | 0 | PIT | 14 | 86.40 | 94.12 | 99.95 | -68.74 | -80.48 | 0.254 | 0.263 | 1.000 | 61.23 | 0.79 | 1 | True | True |
| baselines-margin | seasonal_naive_drift | W1 | 0 | PIT | 14 | 94.04 | 95.90 | 110.60 | -10.17 | -31.89 | 0.277 | 0.268 | 1.089 | 68.10 | 0.93 | 1 | True | True |
| baselines-margin | seasonal_naive | W1 | 0 | PIT | 14 | 339.97 | 357.26 | 352.90 | -339.97 | -357.26 | 1.000 | 1.000 | 3.935 | 231.67 | 0.71 | 1 | False | False |
| baselines-margin | street | W1 | 0 | full_sample | 14 | 86.40 | 94.12 | 99.95 | -68.74 | -80.48 | 0.254 | 0.263 | 1.000 | 59.43 | 0.93 | 1 | True | True |
| baselines-margin | seasonal_naive_drift | W1 | 0 | full_sample | 14 | 94.04 | 95.90 | 110.60 | -10.17 | -31.89 | 0.277 | 0.268 | 1.089 | 65.67 | 0.86 | 1 | True | True |
| baselines-margin | seasonal_naive | W1 | 0 | full_sample | 14 | 339.97 | 357.26 | 352.90 | -339.97 | -357.26 | 1.000 | 1.000 | 3.935 | 210.46 | 1.00 | 1 | False | False |
| baselines-margin | street | W1 | 1 | PIT | 13 | 85.70 | 97.37 | 104.91 | -56.97 | -74.78 | 0.250 | 0.272 | 1.000 | 67.88 | 0.85 | 1 | True | True |
| baselines-margin | seasonal_naive_drift | W1 | 1 | PIT | 13 | 104.80 | 116.05 | 135.27 | -18.41 | -49.84 | 0.306 | 0.324 | 1.223 | 85.49 | 1.00 | 1 | True | True |
| baselines-margin | seasonal_naive | W1 | 1 | PIT | 13 | 342.34 | 358.16 | 356.05 | -342.34 | -358.16 | 1.000 | 1.000 | 3.995 | 226.54 | 0.77 | 1 | False | False |
| baselines-margin | street | W1 | 1 | full_sample | 13 | 85.70 | 97.37 | 104.91 | -56.97 | -74.78 | 0.250 | 0.272 | 1.000 | 64.32 | 1.00 | 1 | True | True |
| baselines-margin | seasonal_naive_drift | W1 | 1 | full_sample | 13 | 104.80 | 116.05 | 135.27 | -18.41 | -49.84 | 0.306 | 0.324 | 1.223 | 80.50 | 1.00 | 1 | True | True |
| baselines-margin | seasonal_naive | W1 | 1 | full_sample | 13 | 342.34 | 358.16 | 356.05 | -342.34 | -358.16 | 1.000 | 1.000 | 3.995 | 204.42 | 1.00 | 1 | False | False |
| baselines-margin | seasonal_naive_drift | W1 | 2 | PIT | 12 | 96.54 | 102.45 | 119.63 | -13.12 | -47.11 | 0.285 | 0.286 |  | 74.66 | 1.00 | 1 | True | True |
| baselines-margin | seasonal_naive | W1 | 2 | PIT | 12 | 339.22 | 357.67 | 353.99 | -339.22 | -357.67 | 1.000 | 1.000 |  | 216.30 | 0.83 | 1 | False | False |
| baselines-margin | seasonal_naive_drift | W1 | 2 | full_sample | 12 | 96.54 | 102.45 | 119.63 | -13.12 | -47.11 | 0.285 | 0.286 |  | 72.39 | 1.00 | 1 | True | True |
| baselines-margin | seasonal_naive | W1 | 2 | full_sample | 12 | 339.22 | 357.67 | 353.99 | -339.22 | -357.67 | 1.000 | 1.000 |  | 208.68 | 0.58 | 1 | False | False |
| baselines-margin | street | W2 | 0 | PIT | 10 | 80.05 | 93.65 | 92.91 | -55.33 | -78.55 | 0.247 | 0.264 | 1.000 | 58.89 | 0.70 | 1 | True | True |
| baselines-margin | seasonal_naive_drift | W2 | 0 | PIT | 10 | 85.60 | 92.73 | 103.12 | -19.60 | -37.74 | 0.264 | 0.261 | 1.069 | 64.77 | 0.90 | 1 | True | True |
| baselines-margin | seasonal_naive | W2 | 0 | PIT | 10 | 324.20 | 354.64 | 337.80 | -324.20 | -354.64 | 1.000 | 1.000 | 4.050 | 237.88 | 0.60 | 1 | False | False |
| baselines-margin | street | W2 | 0 | full_sample | 10 | 80.05 | 93.65 | 92.91 | -55.33 | -78.55 | 0.247 | 0.264 | 1.000 | 56.87 | 1.00 | 1 | True | True |
| baselines-margin | seasonal_naive_drift | W2 | 0 | full_sample | 10 | 85.60 | 92.73 | 103.12 | -19.60 | -37.74 | 0.264 | 0.261 | 1.069 | 63.60 | 0.90 | 1 | True | True |
| baselines-margin | seasonal_naive | W2 | 0 | full_sample | 10 | 324.20 | 354.64 | 337.80 | -324.20 | -354.64 | 1.000 | 1.000 | 4.050 | 206.33 | 1.00 | 1 | False | False |
| baselines-margin | street | W2 | 1 | PIT | 9 | 73.61 | 96.02 | 99.32 | -32.11 | -70.42 | 0.227 | 0.270 | 1.000 | 67.01 | 0.78 | 1 | True | True |
| baselines-margin | seasonal_naive_drift | W2 | 1 | PIT | 9 | 99.56 | 114.87 | 131.94 | -30.89 | -60.38 | 0.307 | 0.323 | 1.352 | 84.03 | 1.00 | 1 | True | True |
| baselines-margin | seasonal_naive | W2 | 1 | PIT | 9 | 324.22 | 355.94 | 339.30 | -324.22 | -355.94 | 1.000 | 1.000 | 4.405 | 229.05 | 0.67 | 1 | False | False |
| baselines-margin | street | W2 | 1 | full_sample | 9 | 73.61 | 96.02 | 99.32 | -32.11 | -70.42 | 0.227 | 0.270 | 1.000 | 63.01 | 1.00 | 1 | True | True |
| baselines-margin | seasonal_naive_drift | W2 | 1 | full_sample | 9 | 99.56 | 114.87 | 131.94 | -30.89 | -60.38 | 0.307 | 0.323 | 1.352 | 80.17 | 1.00 | 1 | True | True |
| baselines-margin | seasonal_naive | W2 | 1 | full_sample | 9 | 324.22 | 355.94 | 339.30 | -324.22 | -355.94 | 1.000 | 1.000 | 4.405 | 194.11 | 1.00 | 1 | False | False |
| baselines-margin | seasonal_naive_drift | W2 | 2 | PIT | 8 | 88.00 | 99.07 | 103.87 | -39.00 | -65.87 | 0.265 | 0.275 |  | 72.39 | 1.00 | 1 | True | True |
| baselines-margin | seasonal_naive | W2 | 2 | PIT | 8 | 331.75 | 360.81 | 347.57 | -331.75 | -360.81 | 1.000 | 1.000 |  | 220.50 | 0.75 | 1 | False | False |
| baselines-margin | seasonal_naive_drift | W2 | 2 | full_sample | 8 | 88.00 | 99.07 | 103.87 | -39.00 | -65.87 | 0.265 | 0.275 |  | 69.62 | 1.00 | 1 | True | True |
| baselines-margin | seasonal_naive | W2 | 2 | full_sample | 8 | 331.75 | 360.81 | 347.57 | -331.75 | -360.81 | 1.000 | 1.000 |  | 201.53 | 0.75 | 1 | False | False |

## target: `revenue_per_night`

| method | object | window | h | replay | n | mae | rw_mae | rmse | bias | rw_bias | r_sn | rw_r_sn | r_street | crps | cov80 | n_params | both | rw_both |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| baselines-margin | seasonal_naive_drift | W1 | 0 | PIT | 14 | 0.48 | 0.48 | 0.63 | -0.04 | -0.12 | 0.670 | 0.612 |  | 0.51 | 1.00 | 1 | True | True |
| baselines-margin | seasonal_naive | W1 | 0 | PIT | 14 | 0.72 | 0.78 | 0.85 | -0.67 | -0.73 | 1.000 | 1.000 |  | 0.51 | 0.86 | 1 | False | False |
| baselines-margin | trailing4 | W1 | 0 | PIT | 14 | 3.72 | 3.42 | 5.00 | 0.06 | 0.16 | 5.141 | 4.380 |  | 2.82 | 0.64 | 2 | False | False |
| baselines-margin | seasonal_naive_drift | W1 | 0 | full_sample | 14 | 0.48 | 0.48 | 0.63 | -0.04 | -0.12 | 0.670 | 0.612 |  | 0.46 | 1.00 | 1 | True | True |
| baselines-margin | seasonal_naive | W1 | 0 | full_sample | 14 | 0.72 | 0.78 | 0.85 | -0.67 | -0.73 | 1.000 | 1.000 |  | 0.49 | 0.79 | 1 | False | False |
| baselines-margin | trailing4 | W1 | 0 | full_sample | 14 | 3.72 | 3.42 | 5.00 | 0.06 | 0.16 | 5.141 | 4.380 |  | 2.78 | 0.64 | 2 | False | False |
| baselines-margin | seasonal_naive_drift | W1 | 1 | PIT | 13 | 0.66 | 0.73 | 0.71 | -0.13 | -0.27 | 0.862 | 0.929 |  | 0.61 | 1.00 | 1 | False | False |
| baselines-margin | seasonal_naive | W1 | 1 | PIT | 13 | 0.76 | 0.79 | 0.88 | -0.70 | -0.74 | 1.000 | 1.000 |  | 0.54 | 0.85 | 1 | False | False |
| baselines-margin | trailing4 | W1 | 1 | PIT | 13 | 3.55 | 3.41 | 4.94 | -0.58 | -0.11 | 4.669 | 4.319 |  | 2.71 | 0.77 | 2 | False | False |
| baselines-margin | seasonal_naive_drift | W1 | 1 | full_sample | 13 | 0.66 | 0.73 | 0.71 | -0.13 | -0.27 | 0.862 | 0.929 |  | 0.52 | 1.00 | 1 | False | False |
| baselines-margin | seasonal_naive | W1 | 1 | full_sample | 13 | 0.76 | 0.79 | 0.88 | -0.70 | -0.74 | 1.000 | 1.000 |  | 0.50 | 0.77 | 1 | False | False |
| baselines-margin | trailing4 | W1 | 1 | full_sample | 13 | 3.55 | 3.41 | 4.94 | -0.58 | -0.11 | 4.669 | 4.319 |  | 2.73 | 0.69 | 2 | False | False |
| baselines-margin | seasonal_naive_drift | W1 | 2 | PIT | 12 | 0.61 | 0.64 | 0.68 | -0.07 | -0.25 | 0.850 | 0.822 |  | 0.47 | 1.00 | 1 | False | True |
| baselines-margin | seasonal_naive | W1 | 2 | PIT | 12 | 0.72 | 0.78 | 0.83 | -0.65 | -0.72 | 1.000 | 1.000 |  | 0.55 | 0.83 | 1 | False | False |
| baselines-margin | trailing4 | W1 | 2 | PIT | 12 | 3.83 | 3.48 | 5.14 | -0.75 | -0.22 | 5.343 | 4.472 |  | 2.93 | 0.67 | 2 | False | False |
| baselines-margin | seasonal_naive_drift | W1 | 2 | full_sample | 12 | 0.61 | 0.64 | 0.68 | -0.07 | -0.25 | 0.850 | 0.822 |  | 0.44 | 1.00 | 1 | False | True |
| baselines-margin | seasonal_naive | W1 | 2 | full_sample | 12 | 0.72 | 0.78 | 0.83 | -0.65 | -0.72 | 1.000 | 1.000 |  | 0.48 | 0.83 | 1 | False | False |
| baselines-margin | trailing4 | W1 | 2 | full_sample | 12 | 3.83 | 3.48 | 5.14 | -0.75 | -0.22 | 5.343 | 4.472 |  | 2.86 | 0.67 | 2 | False | False |
| baselines-margin | seasonal_naive_drift | W2 | 0 | PIT | 10 | 0.49 | 0.48 | 0.64 | -0.04 | -0.13 | 0.733 | 0.627 |  | 0.45 | 1.00 | 1 | True | True |
| baselines-margin | seasonal_naive | W2 | 0 | PIT | 10 | 0.66 | 0.77 | 0.80 | -0.59 | -0.71 | 1.000 | 1.000 |  | 0.49 | 0.80 | 1 | False | False |
| baselines-margin | trailing4 | W2 | 0 | PIT | 10 | 3.69 | 3.40 | 4.91 | 0.33 | 0.30 | 5.559 | 4.435 |  | 2.75 | 0.70 | 2 | False | False |
| baselines-margin | seasonal_naive_drift | W2 | 0 | full_sample | 10 | 0.49 | 0.48 | 0.64 | -0.04 | -0.13 | 0.733 | 0.627 |  | 0.46 | 1.00 | 1 | True | True |
| baselines-margin | seasonal_naive | W2 | 0 | full_sample | 10 | 0.66 | 0.77 | 0.80 | -0.59 | -0.71 | 1.000 | 1.000 |  | 0.46 | 0.80 | 1 | False | False |
| baselines-margin | trailing4 | W2 | 0 | full_sample | 10 | 3.69 | 3.40 | 4.91 | 0.33 | 0.30 | 5.559 | 4.435 |  | 2.74 | 0.70 | 2 | False | False |
| baselines-margin | seasonal_naive | W2 | 1 | PIT | 9 | 0.61 | 0.75 | 0.75 | -0.52 | -0.69 | 1.000 | 1.000 |  | 0.49 | 0.78 | 1 | False | False |
| baselines-margin | seasonal_naive_drift | W2 | 1 | PIT | 9 | 0.73 | 0.77 | 0.77 | -0.06 | -0.27 | 1.202 | 1.031 |  | 0.56 | 1.00 | 1 | False | False |
| baselines-margin | trailing4 | W2 | 1 | PIT | 9 | 3.43 | 3.33 | 4.81 | -0.44 | -0.09 | 5.617 | 4.439 |  | 2.64 | 0.78 | 2 | False | False |
| baselines-margin | seasonal_naive | W2 | 1 | full_sample | 9 | 0.61 | 0.75 | 0.75 | -0.52 | -0.69 | 1.000 | 1.000 |  | 0.43 | 0.78 | 1 | False | False |
| baselines-margin | seasonal_naive_drift | W2 | 1 | full_sample | 9 | 0.73 | 0.77 | 0.77 | -0.06 | -0.27 | 1.202 | 1.031 |  | 0.54 | 1.00 | 1 | False | False |
| baselines-margin | trailing4 | W2 | 1 | full_sample | 9 | 3.43 | 3.33 | 4.81 | -0.44 | -0.09 | 5.617 | 4.439 |  | 2.66 | 0.67 | 2 | False | False |
| baselines-margin | seasonal_naive | W2 | 2 | PIT | 8 | 0.64 | 0.77 | 0.78 | -0.54 | -0.71 | 1.000 | 1.000 |  | 0.53 | 0.75 | 1 | False | False |
| baselines-margin | seasonal_naive_drift | W2 | 2 | PIT | 8 | 0.68 | 0.67 | 0.75 | -0.07 | -0.30 | 1.063 | 0.865 |  | 0.49 | 1.00 | 1 | False | True |
| baselines-margin | trailing4 | W2 | 2 | PIT | 8 | 3.82 | 3.50 | 5.12 | -0.64 | -0.21 | 5.996 | 4.544 |  | 2.88 | 0.62 | 2 | False | False |
| baselines-margin | seasonal_naive | W2 | 2 | full_sample | 8 | 0.64 | 0.77 | 0.78 | -0.54 | -0.71 | 1.000 | 1.000 |  | 0.45 | 0.75 | 1 | False | False |
| baselines-margin | seasonal_naive_drift | W2 | 2 | full_sample | 8 | 0.68 | 0.67 | 0.75 | -0.07 | -0.30 | 1.063 | 0.865 |  | 0.47 | 1.00 | 1 | False | True |
| baselines-margin | trailing4 | W2 | 2 | full_sample | 8 | 3.82 | 3.50 | 5.12 | -0.64 | -0.21 | 5.996 | 4.544 |  | 2.85 | 0.62 | 2 | False | False |

## target: `sbc_musd`

| method | object | window | h | replay | n | mae | rw_mae | rmse | bias | rw_bias | r_sn | rw_r_sn | r_street | crps | cov80 | n_params | both | rw_both |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| baselines-margin | seasonal_naive_drift | W1 | 0 | PIT | 14 | 11.64 | 10.56 | 13.47 | -2.50 | -2.20 | 0.210 | 0.193 |  | 20.33 | 1.00 | 1 | True | True |
| baselines-margin | pct_rev_last4 | W1 | 0 | PIT | 14 | 55.06 | 51.69 | 69.95 | -0.15 | -1.39 | 0.992 | 0.944 |  | 37.74 | 0.93 | 3 | True | True |
| baselines-margin | seasonal_naive | W1 | 0 | PIT | 14 | 55.50 | 54.77 | 57.24 | -55.50 | -54.77 | 1.000 | 1.000 |  | 36.16 | 0.57 | 1 | False | False |
| baselines-margin | seasonal_naive_drift | W1 | 0 | full_sample | 14 | 11.64 | 10.56 | 13.47 | -2.50 | -2.20 | 0.210 | 0.193 |  | 20.47 | 1.00 | 1 | True | True |
| baselines-margin | pct_rev_last4 | W1 | 0 | full_sample | 14 | 54.93 | 51.67 | 69.88 | 0.31 | 0.01 | 0.990 | 0.943 |  | 37.83 | 1.00 | 3 | True | True |
| baselines-margin | seasonal_naive | W1 | 0 | full_sample | 14 | 55.50 | 54.77 | 57.24 | -55.50 | -54.77 | 1.000 | 1.000 |  | 34.54 | 1.00 | 1 | False | False |
| baselines-margin | seasonal_naive_drift | W1 | 1 | PIT | 13 | 18.00 | 17.42 | 22.03 | -3.23 | -2.26 | 0.320 | 0.317 |  | 21.13 | 1.00 | 1 | True | True |
| baselines-margin | seasonal_naive | W1 | 1 | PIT | 13 | 56.31 | 54.95 | 58.07 | -56.31 | -54.95 | 1.000 | 1.000 |  | 39.24 | 0.15 | 1 | False | False |
| baselines-margin | pct_rev_last4 | W1 | 1 | PIT | 13 | 58.32 | 57.31 | 70.85 | -1.73 | -10.10 | 1.036 | 1.043 |  | 40.17 | 1.00 | 3 | False | False |
| baselines-margin | seasonal_naive_drift | W1 | 1 | full_sample | 13 | 18.00 | 17.42 | 22.03 | -3.23 | -2.26 | 0.320 | 0.317 |  | 17.42 | 1.00 | 1 | True | True |
| baselines-margin | seasonal_naive | W1 | 1 | full_sample | 13 | 56.31 | 54.95 | 58.07 | -56.31 | -54.95 | 1.000 | 1.000 |  | 39.99 | 0.23 | 1 | False | False |
| baselines-margin | pct_rev_last4 | W1 | 1 | full_sample | 13 | 58.32 | 57.31 | 70.85 | -1.73 | -10.10 | 1.036 | 1.043 |  | 40.52 | 1.00 | 3 | False | False |
| baselines-margin | seasonal_naive_drift | W1 | 2 | PIT | 12 | 22.50 | 23.34 | 25.34 | -2.33 | -0.12 | 0.400 | 0.425 |  | 22.40 | 1.00 | 1 | True | True |
| baselines-margin | seasonal_naive | W1 | 2 | PIT | 12 | 56.25 | 54.90 | 58.16 | -56.25 | -54.90 | 1.000 | 1.000 |  | 44.45 | 0.00 | 1 | False | False |
| baselines-margin | pct_rev_last4 | W1 | 2 | PIT | 12 | 66.19 | 63.56 | 75.98 | -3.63 | -14.09 | 1.177 | 1.158 |  | 43.44 | 1.00 | 3 | False | False |
| baselines-margin | seasonal_naive_drift | W1 | 2 | full_sample | 12 | 22.50 | 23.34 | 25.34 | -2.33 | -0.12 | 0.400 | 0.425 |  | 17.88 | 1.00 | 1 | True | True |
| baselines-margin | seasonal_naive | W1 | 2 | full_sample | 12 | 56.25 | 54.90 | 58.16 | -56.25 | -54.90 | 1.000 | 1.000 |  | 44.33 | 0.00 | 1 | False | False |
| baselines-margin | pct_rev_last4 | W1 | 2 | full_sample | 12 | 66.19 | 63.56 | 75.98 | -3.63 | -14.09 | 1.177 | 1.158 |  | 43.74 | 1.00 | 3 | False | False |
| baselines-margin | seasonal_naive_drift | W2 | 0 | PIT | 10 | 11.30 | 10.37 | 13.52 | -2.70 | -2.49 | 0.193 | 0.186 |  | 16.83 | 1.00 | 1 | True | True |
| baselines-margin | pct_rev_last4 | W2 | 0 | PIT | 10 | 57.59 | 51.79 | 72.21 | -4.72 | -2.99 | 0.981 | 0.931 |  | 38.50 | 0.90 | 3 | True | True |
| baselines-margin | seasonal_naive | W2 | 0 | PIT | 10 | 58.70 | 55.63 | 60.49 | -58.70 | -55.63 | 1.000 | 1.000 |  | 37.74 | 0.40 | 1 | False | False |
| baselines-margin | seasonal_naive_drift | W2 | 0 | full_sample | 10 | 11.30 | 10.37 | 13.52 | -2.70 | -2.49 | 0.193 | 0.186 |  | 21.92 | 1.00 | 1 | True | True |
| baselines-margin | pct_rev_last4 | W2 | 0 | full_sample | 10 | 57.49 | 51.81 | 72.57 | -3.50 | -1.29 | 0.979 | 0.931 |  | 39.78 | 1.00 | 3 | True | True |
| baselines-margin | seasonal_naive | W2 | 0 | full_sample | 10 | 58.70 | 55.63 | 60.49 | -58.70 | -55.63 | 1.000 | 1.000 |  | 37.08 | 1.00 | 1 | False | False |
| baselines-margin | seasonal_naive_drift | W2 | 1 | PIT | 9 | 19.33 | 17.93 | 23.50 | -2.67 | -2.24 | 0.327 | 0.322 |  | 19.40 | 1.00 | 1 | True | True |
| baselines-margin | seasonal_naive | W2 | 1 | PIT | 9 | 59.11 | 55.66 | 61.07 | -59.11 | -55.66 | 1.000 | 1.000 |  | 42.12 | 0.11 | 1 | False | False |
| baselines-margin | pct_rev_last4 | W2 | 1 | PIT | 9 | 63.26 | 58.62 | 73.81 | -7.55 | -12.14 | 1.070 | 1.053 |  | 42.27 | 1.00 | 3 | False | False |
| baselines-margin | seasonal_naive_drift | W2 | 1 | full_sample | 9 | 19.33 | 17.93 | 23.50 | -2.67 | -2.24 | 0.327 | 0.322 |  | 18.97 | 1.00 | 1 | True | True |
| baselines-margin | seasonal_naive | W2 | 1 | full_sample | 9 | 59.11 | 55.66 | 61.07 | -59.11 | -55.66 | 1.000 | 1.000 |  | 41.57 | 0.33 | 1 | False | False |
| baselines-margin | pct_rev_last4 | W2 | 1 | full_sample | 9 | 63.26 | 58.62 | 73.81 | -7.55 | -12.14 | 1.070 | 1.053 |  | 43.16 | 1.00 | 3 | False | False |
| baselines-margin | seasonal_naive_drift | W2 | 2 | PIT | 8 | 26.12 | 24.66 | 28.21 | 1.38 | 1.57 | 0.460 | 0.453 |  | 22.64 | 1.00 | 1 | True | True |
| baselines-margin | seasonal_naive | W2 | 2 | PIT | 8 | 56.75 | 54.48 | 58.61 | -56.75 | -54.48 | 1.000 | 1.000 |  | 43.77 | 0.00 | 1 | False | False |
| baselines-margin | pct_rev_last4 | W2 | 2 | PIT | 8 | 70.41 | 65.37 | 78.55 | -8.29 | -15.66 | 1.241 | 1.200 |  | 45.06 | 1.00 | 3 | False | False |
| baselines-margin | seasonal_naive_drift | W2 | 2 | full_sample | 8 | 26.12 | 24.66 | 28.21 | 1.38 | 1.57 | 0.460 | 0.453 |  | 19.98 | 1.00 | 1 | True | True |
| baselines-margin | seasonal_naive | W2 | 2 | full_sample | 8 | 56.75 | 54.48 | 58.61 | -56.75 | -54.48 | 1.000 | 1.000 |  | 43.75 | 0.00 | 1 | False | False |
| baselines-margin | pct_rev_last4 | W2 | 2 | full_sample | 8 | 70.41 | 65.37 | 78.55 | -8.29 | -15.66 | 1.241 | 1.200 |  | 45.80 | 1.00 | 3 | False | False |

## target: `sm_cash_musd`

| method | object | window | h | replay | n | mae | rw_mae | rmse | bias | rw_bias | r_sn | rw_r_sn | r_street | crps | cov80 | n_params | both | rw_both |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| baselines-margin | seasonal_naive_drift | W1 | 0 | PIT | 14 | 32.20 | 29.31 | 42.38 | -8.67 | -11.74 | 0.341 | 0.247 |  | 24.23 | 0.86 | 1 | True | True |
| baselines-margin | seasonal_naive | W1 | 0 | PIT | 14 | 94.30 | 118.71 | 105.63 | -94.30 | -118.71 | 1.000 | 1.000 |  | 68.28 | 0.36 | 1 | False | False |
| baselines-margin | pct_rev_last4 | W1 | 0 | PIT | 14 | 103.52 | 105.83 | 127.25 | -8.19 | -29.25 | 1.098 | 0.891 |  | 70.03 | 0.79 | 3 | False | True |
| baselines-margin | seasonal_naive_drift | W1 | 0 | full_sample | 14 | 32.20 | 29.31 | 42.38 | -8.67 | -11.74 | 0.341 | 0.247 |  | 24.02 | 0.79 | 1 | True | True |
| baselines-margin | seasonal_naive | W1 | 0 | full_sample | 14 | 94.30 | 118.71 | 105.63 | -94.30 | -118.71 | 1.000 | 1.000 |  | 65.26 | 0.36 | 1 | False | False |
| baselines-margin | pct_rev_last4 | W1 | 0 | full_sample | 14 | 102.67 | 104.36 | 126.46 | -7.56 | -27.20 | 1.089 | 0.879 |  | 68.71 | 0.64 | 3 | False | True |
| baselines-margin | seasonal_naive_drift | W1 | 1 | PIT | 13 | 50.33 | 45.64 | 55.34 | -15.37 | -26.93 | 0.536 | 0.383 |  | 34.81 | 0.77 | 1 | True | True |
| baselines-margin | seasonal_naive | W1 | 1 | PIT | 13 | 93.97 | 119.09 | 106.16 | -93.97 | -119.09 | 1.000 | 1.000 |  | 67.95 | 0.38 | 1 | False | False |
| baselines-margin | pct_rev_last4 | W1 | 1 | PIT | 13 | 109.76 | 121.21 | 133.47 | -8.89 | -50.13 | 1.168 | 1.018 |  | 71.87 | 0.85 | 3 | False | False |
| baselines-margin | seasonal_naive_drift | W1 | 1 | full_sample | 13 | 50.33 | 45.64 | 55.34 | -15.37 | -26.93 | 0.536 | 0.383 |  | 32.75 | 0.77 | 1 | True | True |
| baselines-margin | seasonal_naive | W1 | 1 | full_sample | 13 | 93.97 | 119.09 | 106.16 | -93.97 | -119.09 | 1.000 | 1.000 |  | 67.32 | 0.31 | 1 | False | False |
| baselines-margin | pct_rev_last4 | W1 | 1 | full_sample | 13 | 109.76 | 121.21 | 133.47 | -8.89 | -50.13 | 1.168 | 1.018 |  | 72.05 | 0.85 | 3 | False | False |
| baselines-margin | seasonal_naive_drift | W1 | 2 | PIT | 12 | 51.62 | 51.89 | 57.84 | -19.31 | -35.97 | 0.552 | 0.434 |  | 34.21 | 0.92 | 1 | True | True |
| baselines-margin | seasonal_naive | W1 | 2 | PIT | 12 | 93.45 | 119.52 | 106.64 | -93.45 | -119.52 | 1.000 | 1.000 |  | 70.54 | 0.25 | 1 | False | False |
| baselines-margin | pct_rev_last4 | W1 | 2 | PIT | 12 | 126.80 | 139.90 | 148.79 | -12.13 | -59.63 | 1.357 | 1.171 |  | 84.27 | 0.75 | 3 | False | False |
| baselines-margin | seasonal_naive_drift | W1 | 2 | full_sample | 12 | 51.62 | 51.89 | 57.84 | -19.31 | -35.97 | 0.552 | 0.434 |  | 33.70 | 0.75 | 1 | True | True |
| baselines-margin | seasonal_naive | W1 | 2 | full_sample | 12 | 93.45 | 119.52 | 106.64 | -93.45 | -119.52 | 1.000 | 1.000 |  | 72.22 | 0.25 | 1 | False | False |
| baselines-margin | pct_rev_last4 | W1 | 2 | full_sample | 12 | 126.80 | 139.90 | 148.79 | -12.13 | -59.63 | 1.357 | 1.171 |  | 81.15 | 0.83 | 3 | False | False |
| baselines-margin | seasonal_naive_drift | W2 | 0 | PIT | 10 | 30.60 | 28.70 | 38.73 | -15.00 | -14.23 | 0.281 | 0.228 |  | 22.60 | 1.00 | 1 | True | True |
| baselines-margin | pct_rev_last4 | W2 | 0 | PIT | 10 | 107.29 | 107.22 | 121.25 | -27.66 | -37.94 | 0.985 | 0.851 |  | 68.14 | 0.90 | 3 | False | True |
| baselines-margin | seasonal_naive | W2 | 0 | PIT | 10 | 108.90 | 126.00 | 116.59 | -108.90 | -126.00 | 1.000 | 1.000 |  | 79.23 | 0.30 | 1 | False | False |
| baselines-margin | seasonal_naive_drift | W2 | 0 | full_sample | 10 | 30.60 | 28.70 | 38.73 | -15.00 | -14.23 | 0.281 | 0.228 |  | 22.29 | 0.90 | 1 | True | True |
| baselines-margin | pct_rev_last4 | W2 | 0 | full_sample | 10 | 106.35 | 105.69 | 120.99 | -25.88 | -35.44 | 0.977 | 0.839 |  | 67.46 | 0.70 | 3 | False | True |
| baselines-margin | seasonal_naive | W2 | 0 | full_sample | 10 | 108.90 | 126.00 | 116.59 | -108.90 | -126.00 | 1.000 | 1.000 |  | 73.99 | 0.30 | 1 | False | False |
| baselines-margin | seasonal_naive_drift | W2 | 1 | PIT | 9 | 43.56 | 43.11 | 48.68 | -30.00 | -32.78 | 0.380 | 0.334 |  | 29.08 | 1.00 | 1 | True | True |
| baselines-margin | seasonal_naive | W2 | 1 | PIT | 9 | 114.67 | 128.92 | 121.42 | -114.67 | -128.92 | 1.000 | 1.000 |  | 83.81 | 0.22 | 1 | False | False |
| baselines-margin | pct_rev_last4 | W2 | 1 | PIT | 9 | 116.84 | 124.85 | 132.48 | -33.49 | -61.27 | 1.019 | 0.968 |  | 74.00 | 0.89 | 3 | False | False |
| baselines-margin | seasonal_naive_drift | W2 | 1 | full_sample | 9 | 43.56 | 43.11 | 48.68 | -30.00 | -32.78 | 0.380 | 0.334 |  | 28.79 | 0.89 | 1 | True | True |
| baselines-margin | seasonal_naive | W2 | 1 | full_sample | 9 | 114.67 | 128.92 | 121.42 | -114.67 | -128.92 | 1.000 | 1.000 |  | 82.06 | 0.11 | 1 | False | False |
| baselines-margin | pct_rev_last4 | W2 | 1 | full_sample | 9 | 116.84 | 124.85 | 132.48 | -33.49 | -61.27 | 1.019 | 0.968 |  | 73.57 | 0.89 | 3 | False | False |
| baselines-margin | seasonal_naive_drift | W2 | 2 | PIT | 8 | 49.88 | 51.18 | 57.83 | -40.62 | -44.58 | 0.418 | 0.389 |  | 34.86 | 0.88 | 1 | True | True |
| baselines-margin | seasonal_naive | W2 | 2 | PIT | 8 | 119.38 | 131.67 | 125.87 | -119.38 | -131.67 | 1.000 | 1.000 |  | 92.03 | 0.12 | 1 | False | False |
| baselines-margin | pct_rev_last4 | W2 | 2 | PIT | 8 | 144.65 | 150.43 | 154.96 | -41.77 | -74.47 | 1.212 | 1.142 |  | 89.86 | 0.75 | 3 | False | False |
| baselines-margin | seasonal_naive_drift | W2 | 2 | full_sample | 8 | 49.88 | 51.18 | 57.83 | -40.62 | -44.58 | 0.418 | 0.389 |  | 34.20 | 0.75 | 1 | True | True |
| baselines-margin | seasonal_naive | W2 | 2 | full_sample | 8 | 119.38 | 131.67 | 125.87 | -119.38 | -131.67 | 1.000 | 1.000 |  | 94.40 | 0.12 | 1 | False | False |
| baselines-margin | pct_rev_last4 | W2 | 2 | full_sample | 8 | 144.65 | 150.43 | 154.96 | -41.77 | -74.47 | 1.212 | 1.142 |  | 87.61 | 0.88 | 3 | False | False |

## target: `sm_cash_per_night`

| method | object | window | h | replay | n | mae | rw_mae | rmse | bias | rw_bias | r_sn | rw_r_sn | r_street | crps | cov80 | n_params | both | rw_both |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| baselines-margin | seasonal_naive_drift | W1 | 0 | PIT | 14 | 0.28 | 0.22 | 0.37 | -0.06 | -0.05 | 0.631 | 0.406 |  | 0.22 | 0.93 | 1 | True | True |
| baselines-margin | trailing4 | W1 | 0 | PIT | 14 | 0.38 | 0.45 | 0.47 | -0.22 | -0.35 | 0.851 | 0.825 |  | 0.27 | 0.71 | 2 | True | True |
| baselines-margin | seasonal_naive | W1 | 0 | PIT | 14 | 0.45 | 0.55 | 0.50 | -0.37 | -0.51 | 1.000 | 1.000 |  | 0.32 | 0.36 | 1 | False | False |
| baselines-margin | seasonal_naive_drift | W1 | 0 | full_sample | 14 | 0.28 | 0.22 | 0.37 | -0.06 | -0.05 | 0.631 | 0.406 |  | 0.21 | 0.93 | 1 | True | True |
| baselines-margin | trailing4 | W1 | 0 | full_sample | 14 | 0.38 | 0.45 | 0.47 | -0.22 | -0.35 | 0.851 | 0.825 |  | 0.27 | 0.71 | 2 | True | True |
| baselines-margin | seasonal_naive | W1 | 0 | full_sample | 14 | 0.45 | 0.55 | 0.50 | -0.37 | -0.51 | 1.000 | 1.000 |  | 0.30 | 0.43 | 1 | False | False |
| baselines-margin | seasonal_naive_drift | W1 | 1 | PIT | 13 | 0.41 | 0.30 | 0.48 | -0.11 | -0.13 | 0.903 | 0.544 |  | 0.27 | 1.00 | 1 | True | True |
| baselines-margin | trailing4 | W1 | 1 | PIT | 13 | 0.45 | 0.54 | 0.54 | -0.33 | -0.47 | 0.986 | 0.987 |  | 0.32 | 0.62 | 2 | False | True |
| baselines-margin | seasonal_naive | W1 | 1 | PIT | 13 | 0.46 | 0.55 | 0.51 | -0.37 | -0.52 | 1.000 | 1.000 |  | 0.33 | 0.31 | 1 | False | False |
| baselines-margin | seasonal_naive_drift | W1 | 1 | full_sample | 13 | 0.41 | 0.30 | 0.48 | -0.11 | -0.13 | 0.903 | 0.544 |  | 0.27 | 0.85 | 1 | True | True |
| baselines-margin | trailing4 | W1 | 1 | full_sample | 13 | 0.45 | 0.54 | 0.54 | -0.33 | -0.47 | 0.986 | 0.987 |  | 0.31 | 0.69 | 2 | False | True |
| baselines-margin | seasonal_naive | W1 | 1 | full_sample | 13 | 0.46 | 0.55 | 0.51 | -0.37 | -0.52 | 1.000 | 1.000 |  | 0.31 | 0.38 | 1 | False | False |
| baselines-margin | seasonal_naive_drift | W1 | 2 | PIT | 12 | 0.37 | 0.32 | 0.45 | -0.13 | -0.19 | 0.809 | 0.580 |  | 0.27 | 1.00 | 1 | True | True |
| baselines-margin | seasonal_naive | W1 | 2 | PIT | 12 | 0.45 | 0.55 | 0.51 | -0.36 | -0.52 | 1.000 | 1.000 |  | 0.32 | 0.33 | 1 | False | False |
| baselines-margin | trailing4 | W1 | 2 | PIT | 12 | 0.51 | 0.63 | 0.63 | -0.41 | -0.58 | 1.137 | 1.141 |  | 0.38 | 0.58 | 2 | False | False |
| baselines-margin | seasonal_naive_drift | W1 | 2 | full_sample | 12 | 0.37 | 0.32 | 0.45 | -0.13 | -0.19 | 0.809 | 0.580 |  | 0.25 | 0.92 | 1 | True | True |
| baselines-margin | seasonal_naive | W1 | 2 | full_sample | 12 | 0.45 | 0.55 | 0.51 | -0.36 | -0.52 | 1.000 | 1.000 |  | 0.31 | 0.42 | 1 | False | False |
| baselines-margin | trailing4 | W1 | 2 | full_sample | 12 | 0.51 | 0.63 | 0.63 | -0.41 | -0.58 | 1.137 | 1.141 |  | 0.36 | 0.67 | 2 | False | False |
| baselines-margin | seasonal_naive_drift | W2 | 0 | PIT | 10 | 0.23 | 0.20 | 0.30 | -0.10 | -0.06 | 0.480 | 0.360 |  | 0.19 | 0.90 | 1 | True | True |
| baselines-margin | trailing4 | W2 | 0 | PIT | 10 | 0.42 | 0.47 | 0.52 | -0.32 | -0.39 | 0.871 | 0.824 |  | 0.31 | 0.60 | 2 | True | True |
| baselines-margin | seasonal_naive | W2 | 0 | PIT | 10 | 0.49 | 0.57 | 0.54 | -0.49 | -0.57 | 1.000 | 1.000 |  | 0.35 | 0.30 | 1 | False | False |
| baselines-margin | seasonal_naive_drift | W2 | 0 | full_sample | 10 | 0.23 | 0.20 | 0.30 | -0.10 | -0.06 | 0.480 | 0.360 |  | 0.18 | 1.00 | 1 | True | True |
| baselines-margin | trailing4 | W2 | 0 | full_sample | 10 | 0.42 | 0.47 | 0.52 | -0.32 | -0.39 | 0.871 | 0.824 |  | 0.30 | 0.60 | 2 | True | True |
| baselines-margin | seasonal_naive | W2 | 0 | full_sample | 10 | 0.49 | 0.57 | 0.54 | -0.49 | -0.57 | 1.000 | 1.000 |  | 0.34 | 0.30 | 1 | False | False |
| baselines-margin | seasonal_naive_drift | W2 | 1 | PIT | 9 | 0.31 | 0.26 | 0.37 | -0.18 | -0.16 | 0.590 | 0.435 |  | 0.22 | 1.00 | 1 | True | True |
| baselines-margin | seasonal_naive | W2 | 1 | PIT | 9 | 0.53 | 0.59 | 0.57 | -0.53 | -0.59 | 1.000 | 1.000 |  | 0.38 | 0.22 | 1 | False | False |
| baselines-margin | trailing4 | W2 | 1 | PIT | 9 | 0.54 | 0.59 | 0.63 | -0.48 | -0.54 | 1.033 | 0.999 |  | 0.38 | 0.44 | 2 | False | True |
| baselines-margin | seasonal_naive_drift | W2 | 1 | full_sample | 9 | 0.31 | 0.26 | 0.37 | -0.18 | -0.16 | 0.590 | 0.435 |  | 0.22 | 1.00 | 1 | True | True |
| baselines-margin | seasonal_naive | W2 | 1 | full_sample | 9 | 0.53 | 0.59 | 0.57 | -0.53 | -0.59 | 1.000 | 1.000 |  | 0.36 | 0.22 | 1 | False | False |
| baselines-margin | trailing4 | W2 | 1 | full_sample | 9 | 0.54 | 0.59 | 0.63 | -0.48 | -0.54 | 1.033 | 0.999 |  | 0.37 | 0.56 | 2 | False | True |
| baselines-margin | seasonal_naive_drift | W2 | 2 | PIT | 8 | 0.34 | 0.30 | 0.43 | -0.25 | -0.24 | 0.607 | 0.494 |  | 0.25 | 1.00 | 1 | True | True |
| baselines-margin | seasonal_naive | W2 | 2 | PIT | 8 | 0.55 | 0.60 | 0.60 | -0.55 | -0.60 | 1.000 | 1.000 |  | 0.40 | 0.12 | 1 | False | False |
| baselines-margin | trailing4 | W2 | 2 | PIT | 8 | 0.61 | 0.68 | 0.73 | -0.58 | -0.65 | 1.102 | 1.127 |  | 0.47 | 0.50 | 2 | False | False |
| baselines-margin | seasonal_naive_drift | W2 | 2 | full_sample | 8 | 0.34 | 0.30 | 0.43 | -0.25 | -0.24 | 0.607 | 0.494 |  | 0.25 | 0.88 | 1 | True | True |
| baselines-margin | seasonal_naive | W2 | 2 | full_sample | 8 | 0.55 | 0.60 | 0.60 | -0.55 | -0.60 | 1.000 | 1.000 |  | 0.39 | 0.12 | 1 | False | False |
| baselines-margin | trailing4 | W2 | 2 | full_sample | 8 | 0.61 | 0.68 | 0.73 | -0.58 | -0.65 | 1.102 | 1.127 |  | 0.44 | 0.50 | 2 | False | False |

## target: `tax_provision_musd`

| method | object | window | h | replay | n | mae | rw_mae | rmse | bias | rw_bias | r_sn | rw_r_sn | r_street | crps | cov80 | n_params | both | rw_both |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| baselines-margin | seasonal_naive | W1 | 0 | PIT | 14 | 467.55 | 294.74 | 1,102.66 | -41.17 | -100.45 | 1.000 | 1.000 |  | 567.19 | 0.86 | 1 | False | False |
| baselines-margin | seasonal_naive_drift | W1 | 0 | PIT | 14 | 876.46 | 591.80 | 1,513.65 | 4.51 | 30.76 | 1.875 | 2.008 |  | 870.90 | 0.71 | 1 | False | False |
| baselines-margin | seasonal_naive | W1 | 0 | full_sample | 14 | 467.55 | 294.74 | 1,102.66 | -41.17 | -100.45 | 1.000 | 1.000 |  | 525.90 | 0.86 | 1 | False | False |
| baselines-margin | seasonal_naive_drift | W1 | 0 | full_sample | 14 | 876.46 | 591.80 | 1,513.65 | 4.51 | 30.76 | 1.875 | 2.008 |  | 810.76 | 0.71 | 1 | False | False |
| baselines-margin | seasonal_naive | W1 | 1 | PIT | 13 | 503.30 | 300.19 | 1,144.29 | -44.13 | -102.28 | 1.000 | 1.000 |  | 592.72 | 0.77 | 1 | False | False |
| baselines-margin | seasonal_naive_drift | W1 | 1 | PIT | 13 | 958.17 | 637.66 | 1,618.37 | -2.78 | 35.11 | 1.904 | 2.124 |  | 914.69 | 0.69 | 1 | False | False |
| baselines-margin | seasonal_naive | W1 | 1 | full_sample | 13 | 503.30 | 300.19 | 1,144.29 | -44.13 | -102.28 | 1.000 | 1.000 |  | 553.11 | 0.85 | 1 | False | False |
| baselines-margin | seasonal_naive_drift | W1 | 1 | full_sample | 13 | 958.17 | 637.66 | 1,618.37 | -2.78 | 35.11 | 1.904 | 2.124 |  | 872.79 | 0.69 | 1 | False | False |
| baselines-margin | seasonal_naive | W1 | 2 | PIT | 12 | 543.43 | 306.52 | 1,191.00 | -46.00 | -104.11 | 1.000 | 1.000 |  | 618.09 | 0.75 | 1 | False | False |
| baselines-margin | seasonal_naive_drift | W1 | 2 | PIT | 12 | 1,048.21 | 734.06 | 1,704.86 | 7.88 | 86.56 | 1.929 | 2.395 |  | 977.04 | 0.67 | 1 | False | False |
| baselines-margin | seasonal_naive | W1 | 2 | full_sample | 12 | 543.43 | 306.52 | 1,191.00 | -46.00 | -104.11 | 1.000 | 1.000 |  | 583.70 | 0.83 | 1 | False | False |
| baselines-margin | seasonal_naive_drift | W1 | 2 | full_sample | 12 | 1,048.21 | 734.06 | 1,704.86 | 7.88 | 86.56 | 1.929 | 2.395 |  | 929.25 | 0.67 | 1 | False | False |
| baselines-margin | seasonal_naive | W2 | 0 | PIT | 10 | 371.16 | 244.76 | 972.23 | -336.16 | -191.70 | 1.000 | 1.000 |  | 496.56 | 0.90 | 1 | False | False |
| baselines-margin | seasonal_naive_drift | W2 | 0 | PIT | 10 | 678.30 | 483.19 | 1,309.39 | -0.30 | 46.74 | 1.828 | 1.974 |  | 728.54 | 0.80 | 1 | False | False |
| baselines-margin | seasonal_naive | W2 | 0 | full_sample | 10 | 371.16 | 244.76 | 972.23 | -336.16 | -191.70 | 1.000 | 1.000 |  | 452.26 | 0.90 | 1 | False | False |
| baselines-margin | seasonal_naive_drift | W2 | 0 | full_sample | 10 | 678.30 | 483.19 | 1,309.39 | -0.30 | 46.74 | 1.828 | 1.974 |  | 681.92 | 0.80 | 1 | False | False |
| baselines-margin | seasonal_naive | W2 | 1 | PIT | 9 | 410.67 | 254.47 | 1,024.81 | -371.78 | -199.16 | 1.000 | 1.000 |  | 519.75 | 0.89 | 1 | False | False |
| baselines-margin | seasonal_naive_drift | W2 | 1 | PIT | 9 | 760.16 | 519.68 | 1,445.66 | -9.93 | 71.97 | 1.851 | 2.042 |  | 770.01 | 0.78 | 1 | False | False |
| baselines-margin | seasonal_naive | W2 | 1 | full_sample | 9 | 410.67 | 254.47 | 1,024.81 | -371.78 | -199.16 | 1.000 | 1.000 |  | 482.80 | 0.89 | 1 | False | False |
| baselines-margin | seasonal_naive_drift | W2 | 1 | full_sample | 9 | 760.16 | 519.68 | 1,445.66 | -9.93 | 71.97 | 1.851 | 2.042 |  | 755.25 | 0.78 | 1 | False | False |
| baselines-margin | seasonal_naive | W2 | 2 | PIT | 8 | 449.50 | 262.66 | 1,086.40 | -405.75 | -204.42 | 1.000 | 1.000 |  | 544.99 | 0.88 | 1 | False | False |
| baselines-margin | seasonal_naive_drift | W2 | 2 | PIT | 8 | 862.80 | 615.67 | 1,546.92 | 14.95 | 162.61 | 1.919 | 2.344 |  | 842.60 | 0.75 | 1 | False | False |
| baselines-margin | seasonal_naive | W2 | 2 | full_sample | 8 | 449.50 | 262.66 | 1,086.40 | -405.75 | -204.42 | 1.000 | 1.000 |  | 517.19 | 0.88 | 1 | False | False |
| baselines-margin | seasonal_naive_drift | W2 | 2 | full_sample | 8 | 862.80 | 615.67 | 1,546.92 | 14.95 | 162.61 | 1.919 | 2.344 |  | 820.35 | 0.75 | 1 | False | False |

## target: `tax_rate_pct`

| method | object | window | h | replay | n | mae | rw_mae | rmse | bias | rw_bias | r_sn | rw_r_sn | r_street | crps | cov80 | n_params | both | rw_both |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| baselines-margin | trailing4 | W1 | 0 | PIT | 14 | 33.95 | 22.32 | 53.50 | -5.41 | -5.28 | 0.815 | 0.849 |  | 28.61 | 0.93 | 2 | True | True |
| baselines-margin | seasonal_naive | W1 | 0 | PIT | 14 | 41.65 | 26.28 | 76.69 | -14.88 | -11.43 | 1.000 | 1.000 |  | 42.05 | 0.79 | 1 | False | False |
| baselines-margin | seasonal_naive_drift | W1 | 0 | PIT | 14 | 78.87 | 52.18 | 107.05 | -0.63 | 3.62 | 1.894 | 1.985 |  | 59.75 | 0.71 | 1 | False | False |
| baselines-margin | trailing4 | W1 | 0 | full_sample | 14 | 33.95 | 22.32 | 53.50 | -5.41 | -5.28 | 0.815 | 0.849 |  | 27.56 | 0.93 | 2 | True | True |
| baselines-margin | seasonal_naive | W1 | 0 | full_sample | 14 | 41.65 | 26.28 | 76.69 | -14.88 | -11.43 | 1.000 | 1.000 |  | 40.00 | 0.79 | 1 | False | False |
| baselines-margin | seasonal_naive_drift | W1 | 0 | full_sample | 14 | 78.87 | 52.18 | 107.05 | -0.63 | 3.62 | 1.894 | 1.985 |  | 59.53 | 0.57 | 1 | False | False |
| baselines-margin | seasonal_naive | W1 | 1 | PIT | 13 | 33.88 | 24.11 | 69.05 | -5.04 | -8.97 | 1.000 | 1.000 |  | 36.11 | 0.85 | 1 | False | False |
| baselines-margin | trailing4 | W1 | 1 | PIT | 13 | 35.23 | 22.10 | 55.86 | -6.90 | -8.54 | 1.040 | 0.917 |  | 29.49 | 0.92 | 2 | False | True |
| baselines-margin | seasonal_naive_drift | W1 | 1 | PIT | 13 | 72.01 | 46.99 | 120.70 | 7.83 | 2.47 | 2.126 | 1.949 |  | 64.36 | 0.92 | 1 | False | False |
| baselines-margin | seasonal_naive | W1 | 1 | full_sample | 13 | 33.88 | 24.11 | 69.05 | -5.04 | -8.97 | 1.000 | 1.000 |  | 35.52 | 0.85 | 1 | False | False |
| baselines-margin | trailing4 | W1 | 1 | full_sample | 13 | 35.23 | 22.10 | 55.86 | -6.90 | -8.54 | 1.040 | 0.917 |  | 28.94 | 0.92 | 2 | False | True |
| baselines-margin | seasonal_naive_drift | W1 | 1 | full_sample | 13 | 72.01 | 46.99 | 120.70 | 7.83 | 2.47 | 2.126 | 1.949 |  | 63.64 | 0.69 | 1 | False | False |
| baselines-margin | trailing4 | W1 | 2 | PIT | 12 | 33.00 | 23.36 | 49.28 | -8.52 | -11.00 | 0.905 | 0.950 |  | 26.58 | 0.92 | 2 | True | True |
| baselines-margin | seasonal_naive | W1 | 2 | PIT | 12 | 36.48 | 24.59 | 71.86 | -5.24 | -9.12 | 1.000 | 1.000 |  | 40.28 | 0.83 | 1 | False | False |
| baselines-margin | seasonal_naive_drift | W1 | 2 | PIT | 12 | 78.10 | 55.66 | 108.69 | 9.76 | 7.54 | 2.141 | 2.263 |  | 63.10 | 0.58 | 1 | False | False |
| baselines-margin | trailing4 | W1 | 2 | full_sample | 12 | 33.00 | 23.36 | 49.28 | -8.52 | -11.00 | 0.905 | 0.950 |  | 25.98 | 0.83 | 2 | True | True |
| baselines-margin | seasonal_naive | W1 | 2 | full_sample | 12 | 36.48 | 24.59 | 71.86 | -5.24 | -9.12 | 1.000 | 1.000 |  | 36.59 | 0.83 | 1 | False | False |
| baselines-margin | seasonal_naive_drift | W1 | 2 | full_sample | 12 | 78.10 | 55.66 | 108.69 | 9.76 | 7.54 | 2.141 | 2.263 |  | 60.59 | 0.58 | 1 | False | False |
| baselines-margin | trailing4 | W2 | 0 | PIT | 10 | 22.26 | 17.56 | 29.44 | -16.08 | -8.39 | 0.821 | 0.823 |  | 19.96 | 1.00 | 2 | True | True |
| baselines-margin | seasonal_naive | W2 | 0 | PIT | 10 | 27.12 | 21.35 | 58.97 | -22.61 | -14.37 | 1.000 | 1.000 |  | 32.24 | 0.90 | 1 | False | False |
| baselines-margin | seasonal_naive_drift | W2 | 0 | PIT | 10 | 47.00 | 40.65 | 77.05 | 1.02 | 4.75 | 1.733 | 1.904 |  | 44.85 | 0.80 | 1 | False | False |
| baselines-margin | trailing4 | W2 | 0 | full_sample | 10 | 22.26 | 17.56 | 29.44 | -16.08 | -8.39 | 0.821 | 0.823 |  | 19.14 | 1.00 | 2 | True | True |
| baselines-margin | seasonal_naive | W2 | 0 | full_sample | 10 | 27.12 | 21.35 | 58.97 | -22.61 | -14.37 | 1.000 | 1.000 |  | 30.38 | 0.90 | 1 | False | False |
| baselines-margin | seasonal_naive_drift | W2 | 0 | full_sample | 10 | 47.00 | 40.65 | 77.05 | 1.02 | 4.75 | 1.733 | 1.904 |  | 43.07 | 0.80 | 1 | False | False |
| baselines-margin | trailing4 | W2 | 1 | PIT | 9 | 23.42 | 17.24 | 32.96 | -19.46 | -11.83 | 0.779 | 0.775 |  | 20.92 | 1.00 | 2 | False | True |
| baselines-margin | seasonal_naive | W2 | 1 | PIT | 9 | 30.09 | 22.23 | 62.16 | -25.17 | -15.00 | 1.000 | 1.000 |  | 33.77 | 0.89 | 1 | False | False |
| baselines-margin | seasonal_naive_drift | W2 | 1 | PIT | 9 | 49.20 | 36.52 | 86.48 | -2.48 | 1.02 | 1.635 | 1.643 |  | 49.46 | 1.00 | 1 | False | False |
| baselines-margin | trailing4 | W2 | 1 | full_sample | 9 | 23.42 | 17.24 | 32.96 | -19.46 | -11.83 | 0.779 | 0.775 |  | 20.41 | 1.00 | 2 | False | True |
| baselines-margin | seasonal_naive | W2 | 1 | full_sample | 9 | 30.09 | 22.23 | 62.16 | -25.17 | -15.00 | 1.000 | 1.000 |  | 32.25 | 0.89 | 1 | False | False |
| baselines-margin | seasonal_naive_drift | W2 | 1 | full_sample | 9 | 49.20 | 36.52 | 86.48 | -2.48 | 1.02 | 1.635 | 1.643 |  | 47.63 | 0.78 | 1 | False | False |
| baselines-margin | trailing4 | W2 | 2 | PIT | 8 | 25.70 | 20.04 | 33.96 | -21.62 | -13.85 | 0.803 | 0.885 |  | 19.93 | 1.00 | 2 | True | True |
| baselines-margin | seasonal_naive | W2 | 2 | PIT | 8 | 32.02 | 22.64 | 65.73 | -26.49 | -15.02 | 1.000 | 1.000 |  | 34.44 | 0.88 | 1 | False | False |
| baselines-margin | seasonal_naive_drift | W2 | 2 | PIT | 8 | 58.24 | 45.33 | 92.10 | 0.62 | 8.24 | 1.819 | 2.003 |  | 50.73 | 0.75 | 1 | False | False |
| baselines-margin | trailing4 | W2 | 2 | full_sample | 8 | 25.70 | 20.04 | 33.96 | -21.62 | -13.85 | 0.803 | 0.885 |  | 19.19 | 0.88 | 2 | True | True |
| baselines-margin | seasonal_naive | W2 | 2 | full_sample | 8 | 32.02 | 22.64 | 65.73 | -26.49 | -15.02 | 1.000 | 1.000 |  | 33.13 | 0.88 | 1 | False | False |
| baselines-margin | seasonal_naive_drift | W2 | 2 | full_sample | 8 | 58.24 | 45.33 | 92.10 | 0.62 | 8.24 | 1.819 | 2.003 |  | 50.38 | 0.75 | 1 | False | False |

## target: `total_cash_costs_musd`

| method | object | window | h | replay | n | mae | rw_mae | rmse | bias | rw_bias | r_sn | rw_r_sn | r_street | crps | cov80 | n_params | both | rw_both |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| baselines-margin | seasonal_naive_drift | W1 | 0 | PIT | 14 | 49.83 | 39.88 | 62.57 | -6.96 | -11.57 | 0.229 | 0.165 |  | 36.40 | 0.86 | 1 | True | True |
| baselines-margin | seasonal_naive | W1 | 0 | PIT | 14 | 217.54 | 242.30 | 227.43 | -217.54 | -242.30 | 1.000 | 1.000 |  | 157.52 | 0.36 | 1 | False | False |
| baselines-margin | pct_rev_last4 | W1 | 0 | PIT | 14 | 284.34 | 271.28 | 389.68 | 52.35 | 24.02 | 1.307 | 1.120 |  | 207.48 | 0.79 | 3 | False | False |
| baselines-margin | seasonal_naive_drift | W1 | 0 | full_sample | 14 | 49.83 | 39.88 | 62.57 | -6.96 | -11.57 | 0.229 | 0.165 |  | 35.85 | 0.71 | 1 | True | True |
| baselines-margin | seasonal_naive | W1 | 0 | full_sample | 14 | 217.54 | 242.30 | 227.43 | -217.54 | -242.30 | 1.000 | 1.000 |  | 147.47 | 0.36 | 1 | False | False |
| baselines-margin | pct_rev_last4 | W1 | 0 | full_sample | 14 | 283.69 | 271.72 | 388.28 | 54.24 | 30.83 | 1.304 | 1.121 |  | 204.05 | 0.71 | 3 | False | False |
| baselines-margin | seasonal_naive_drift | W1 | 1 | PIT | 13 | 77.09 | 63.13 | 91.54 | -9.64 | -26.43 | 0.362 | 0.261 |  | 55.54 | 0.69 | 1 | True | True |
| baselines-margin | seasonal_naive | W1 | 1 | PIT | 13 | 213.04 | 241.66 | 223.25 | -213.04 | -241.66 | 1.000 | 1.000 |  | 151.55 | 0.23 | 1 | False | False |
| baselines-margin | pct_rev_last4 | W1 | 1 | PIT | 13 | 296.79 | 271.69 | 409.21 | 87.01 | -1.04 | 1.393 | 1.124 |  | 211.60 | 0.77 | 3 | False | False |
| baselines-margin | seasonal_naive_drift | W1 | 1 | full_sample | 13 | 77.09 | 63.13 | 91.54 | -9.64 | -26.43 | 0.362 | 0.261 |  | 52.80 | 0.77 | 1 | True | True |
| baselines-margin | seasonal_naive | W1 | 1 | full_sample | 13 | 213.04 | 241.66 | 223.25 | -213.04 | -241.66 | 1.000 | 1.000 |  | 149.93 | 0.15 | 1 | False | False |
| baselines-margin | pct_rev_last4 | W1 | 1 | full_sample | 13 | 296.79 | 271.69 | 409.21 | 87.01 | -1.04 | 1.393 | 1.124 |  | 214.31 | 0.77 | 3 | False | False |
| baselines-margin | seasonal_naive_drift | W1 | 2 | PIT | 12 | 82.03 | 73.28 | 96.72 | -10.87 | -39.10 | 0.394 | 0.304 |  | 58.12 | 0.67 | 1 | True | True |
| baselines-margin | seasonal_naive | W1 | 2 | PIT | 12 | 208.13 | 240.98 | 218.71 | -208.13 | -240.98 | 1.000 | 1.000 |  | 153.58 | 0.08 | 1 | False | False |
| baselines-margin | pct_rev_last4 | W1 | 2 | PIT | 12 | 343.27 | 314.51 | 456.40 | 104.40 | -1.41 | 1.649 | 1.305 |  | 243.87 | 0.75 | 3 | False | False |
| baselines-margin | seasonal_naive_drift | W1 | 2 | full_sample | 12 | 82.03 | 73.28 | 96.72 | -10.87 | -39.10 | 0.394 | 0.304 |  | 56.01 | 0.75 | 1 | True | True |
| baselines-margin | seasonal_naive | W1 | 2 | full_sample | 12 | 208.13 | 240.98 | 218.71 | -208.13 | -240.98 | 1.000 | 1.000 |  | 157.10 | 0.08 | 1 | False | False |
| baselines-margin | pct_rev_last4 | W1 | 2 | full_sample | 12 | 343.27 | 314.51 | 456.40 | 104.40 | -1.41 | 1.649 | 1.305 |  | 236.91 | 0.83 | 3 | False | False |
| baselines-margin | seasonal_naive_drift | W2 | 0 | PIT | 10 | 42.60 | 36.77 | 52.19 | -21.00 | -16.98 | 0.187 | 0.147 |  | 31.49 | 1.00 | 1 | True | True |
| baselines-margin | seasonal_naive | W2 | 0 | PIT | 10 | 227.80 | 249.37 | 234.21 | -227.80 | -249.37 | 1.000 | 1.000 |  | 164.87 | 0.30 | 1 | False | False |
| baselines-margin | pct_rev_last4 | W2 | 0 | PIT | 10 | 281.89 | 269.49 | 369.25 | 15.60 | 7.58 | 1.237 | 1.081 |  | 198.47 | 0.90 | 3 | False | False |
| baselines-margin | seasonal_naive_drift | W2 | 0 | full_sample | 10 | 42.60 | 36.77 | 52.19 | -21.00 | -16.98 | 0.187 | 0.147 |  | 30.63 | 0.80 | 1 | True | True |
| baselines-margin | seasonal_naive | W2 | 0 | full_sample | 10 | 227.80 | 249.37 | 234.21 | -227.80 | -249.37 | 1.000 | 1.000 |  | 151.39 | 0.30 | 1 | False | False |
| baselines-margin | pct_rev_last4 | W2 | 0 | full_sample | 10 | 282.29 | 270.45 | 370.69 | 21.63 | 16.00 | 1.239 | 1.085 |  | 197.79 | 0.80 | 3 | False | False |
| baselines-margin | seasonal_naive_drift | W2 | 1 | PIT | 9 | 63.56 | 57.62 | 72.67 | -39.11 | -37.83 | 0.270 | 0.228 |  | 43.59 | 0.89 | 1 | True | True |
| baselines-margin | seasonal_naive | W2 | 1 | PIT | 9 | 235.11 | 253.07 | 240.91 | -235.11 | -253.07 | 1.000 | 1.000 |  | 169.77 | 0.22 | 1 | False | False |
| baselines-margin | pct_rev_last4 | W2 | 1 | PIT | 9 | 287.02 | 266.63 | 395.99 | 42.17 | -20.22 | 1.221 | 1.054 |  | 209.65 | 0.78 | 3 | False | False |
| baselines-margin | seasonal_naive_drift | W2 | 1 | full_sample | 9 | 63.56 | 57.62 | 72.67 | -39.11 | -37.83 | 0.270 | 0.228 |  | 42.56 | 0.89 | 1 | True | True |
| baselines-margin | seasonal_naive | W2 | 1 | full_sample | 9 | 235.11 | 253.07 | 240.91 | -235.11 | -253.07 | 1.000 | 1.000 |  | 166.64 | 0.11 | 1 | False | False |
| baselines-margin | pct_rev_last4 | W2 | 1 | full_sample | 9 | 287.02 | 266.63 | 395.99 | 42.17 | -20.22 | 1.221 | 1.054 |  | 210.82 | 0.78 | 3 | False | False |
| baselines-margin | seasonal_naive_drift | W2 | 2 | PIT | 8 | 71.00 | 68.63 | 84.21 | -55.00 | -56.81 | 0.295 | 0.268 |  | 50.41 | 0.75 | 1 | True | True |
| baselines-margin | seasonal_naive | W2 | 2 | PIT | 8 | 240.88 | 256.47 | 246.63 | -240.88 | -256.47 | 1.000 | 1.000 |  | 179.12 | 0.12 | 1 | False | False |
| baselines-margin | pct_rev_last4 | W2 | 2 | PIT | 8 | 345.17 | 317.50 | 450.67 | 46.78 | -29.70 | 1.433 | 1.238 |  | 240.19 | 0.75 | 3 | False | False |
| baselines-margin | seasonal_naive_drift | W2 | 2 | full_sample | 8 | 71.00 | 68.63 | 84.21 | -55.00 | -56.81 | 0.295 | 0.268 |  | 49.52 | 0.75 | 1 | True | True |
| baselines-margin | seasonal_naive | W2 | 2 | full_sample | 8 | 240.88 | 256.47 | 246.63 | -240.88 | -256.47 | 1.000 | 1.000 |  | 186.68 | 0.00 | 1 | False | False |
| baselines-margin | pct_rev_last4 | W2 | 2 | full_sample | 8 | 345.17 | 317.50 | 450.67 | 46.78 | -29.70 | 1.433 | 1.238 |  | 237.35 | 0.88 | 3 | False | False |

## target: `total_cash_costs_pct_rev`

| method | object | window | h | replay | n | mae | rw_mae | rmse | bias | rw_bias | r_sn | rw_r_sn | r_street | crps | cov80 | n_params | both | rw_both |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| baselines-margin | seasonal_naive | W1 | 0 | PIT | 14 | 2.24 | 1.91 | 2.85 | 0.47 | 0.02 | 1.000 | 1.000 |  | 2.17 | 1.00 | 1 | False | False |
| baselines-margin | seasonal_naive_drift | W1 | 0 | PIT | 14 | 2.38 | 1.98 | 3.06 | -0.26 | 0.17 | 1.066 | 1.036 |  | 2.06 | 1.00 | 1 | False | False |
| baselines-margin | trailing4 | W1 | 0 | PIT | 14 | 9.48 | 8.49 | 12.10 | -0.64 | -1.21 | 4.236 | 4.440 |  | 6.93 | 0.79 | 2 | False | False |
| baselines-margin | seasonal_naive | W1 | 0 | full_sample | 14 | 2.24 | 1.91 | 2.85 | 0.47 | 0.02 | 1.000 | 1.000 |  | 2.31 | 1.00 | 1 | False | False |
| baselines-margin | seasonal_naive_drift | W1 | 0 | full_sample | 14 | 2.38 | 1.98 | 3.06 | -0.26 | 0.17 | 1.066 | 1.036 |  | 1.91 | 1.00 | 1 | False | False |
| baselines-margin | trailing4 | W1 | 0 | full_sample | 14 | 9.48 | 8.49 | 12.10 | -0.64 | -1.21 | 4.236 | 4.440 |  | 6.82 | 0.64 | 2 | False | False |
| baselines-margin | seasonal_naive | W1 | 1 | PIT | 13 | 2.35 | 1.93 | 2.95 | 0.57 | 0.03 | 1.000 | 1.000 |  | 2.12 | 1.00 | 1 | False | False |
| baselines-margin | seasonal_naive_drift | W1 | 1 | PIT | 13 | 3.91 | 3.43 | 4.52 | -0.14 | 0.43 | 1.665 | 1.773 |  | 2.94 | 1.00 | 1 | False | False |
| baselines-margin | trailing4 | W1 | 1 | PIT | 13 | 8.91 | 8.54 | 11.62 | 0.73 | -0.97 | 3.789 | 4.418 |  | 6.44 | 0.92 | 2 | False | False |
| baselines-margin | seasonal_naive | W1 | 1 | full_sample | 13 | 2.35 | 1.93 | 2.95 | 0.57 | 0.03 | 1.000 | 1.000 |  | 2.10 | 1.00 | 1 | False | False |
| baselines-margin | seasonal_naive_drift | W1 | 1 | full_sample | 13 | 3.91 | 3.43 | 4.52 | -0.14 | 0.43 | 1.665 | 1.773 |  | 2.76 | 1.00 | 1 | False | False |
| baselines-margin | trailing4 | W1 | 1 | full_sample | 13 | 8.91 | 8.54 | 11.62 | 0.73 | -0.97 | 3.789 | 4.418 |  | 6.51 | 0.77 | 2 | False | False |
| baselines-margin | seasonal_naive | W1 | 2 | PIT | 12 | 2.48 | 1.96 | 3.06 | 0.68 | 0.05 | 1.000 | 1.000 |  | 1.94 | 1.00 | 1 | False | False |
| baselines-margin | seasonal_naive_drift | W1 | 2 | PIT | 12 | 3.63 | 2.79 | 4.67 | -0.30 | -0.01 | 1.465 | 1.422 |  | 3.30 | 1.00 | 1 | False | False |
| baselines-margin | trailing4 | W1 | 2 | PIT | 12 | 9.52 | 8.70 | 12.19 | 0.76 | -1.16 | 3.841 | 4.438 |  | 7.03 | 0.92 | 2 | False | False |
| baselines-margin | seasonal_naive | W1 | 2 | full_sample | 12 | 2.48 | 1.96 | 3.06 | 0.68 | 0.05 | 1.000 | 1.000 |  | 1.85 | 0.92 | 1 | False | False |
| baselines-margin | seasonal_naive_drift | W1 | 2 | full_sample | 12 | 3.63 | 2.79 | 4.67 | -0.30 | -0.01 | 1.465 | 1.422 |  | 2.96 | 1.00 | 1 | False | False |
| baselines-margin | trailing4 | W1 | 2 | full_sample | 12 | 9.52 | 8.70 | 12.19 | 0.76 | -1.16 | 3.841 | 4.438 |  | 6.86 | 0.83 | 2 | False | False |
| baselines-margin | seasonal_naive | W2 | 0 | PIT | 10 | 1.96 | 1.75 | 2.36 | -0.19 | -0.27 | 1.000 | 1.000 |  | 1.85 | 1.00 | 1 | False | False |
| baselines-margin | seasonal_naive_drift | W2 | 0 | PIT | 10 | 2.02 | 1.85 | 2.66 | -0.54 | 0.07 | 1.031 | 1.052 |  | 1.78 | 1.00 | 1 | False | False |
| baselines-margin | trailing4 | W2 | 0 | PIT | 10 | 8.98 | 8.32 | 11.09 | -1.77 | -1.73 | 4.583 | 4.739 |  | 6.33 | 0.90 | 2 | False | False |
| baselines-margin | seasonal_naive | W2 | 0 | full_sample | 10 | 1.96 | 1.75 | 2.36 | -0.19 | -0.27 | 1.000 | 1.000 |  | 2.21 | 1.00 | 1 | False | False |
| baselines-margin | seasonal_naive_drift | W2 | 0 | full_sample | 10 | 2.02 | 1.85 | 2.66 | -0.54 | 0.07 | 1.031 | 1.052 |  | 1.78 | 1.00 | 1 | False | False |
| baselines-margin | trailing4 | W2 | 0 | full_sample | 10 | 8.98 | 8.32 | 11.09 | -1.77 | -1.73 | 4.583 | 4.739 |  | 6.28 | 0.70 | 2 | False | False |
| baselines-margin | seasonal_naive | W2 | 1 | PIT | 9 | 1.58 | 1.60 | 1.72 | -0.81 | -0.51 | 1.000 | 1.000 |  | 1.69 | 1.00 | 1 | False | False |
| baselines-margin | seasonal_naive_drift | W2 | 1 | PIT | 9 | 3.50 | 3.27 | 4.16 | -1.09 | 0.16 | 2.220 | 2.040 |  | 2.63 | 1.00 | 1 | False | False |
| baselines-margin | trailing4 | W2 | 1 | PIT | 9 | 8.59 | 8.37 | 10.98 | -0.51 | -1.38 | 5.442 | 5.229 |  | 6.20 | 1.00 | 2 | False | False |
| baselines-margin | seasonal_naive | W2 | 1 | full_sample | 9 | 1.58 | 1.60 | 1.72 | -0.81 | -0.51 | 1.000 | 1.000 |  | 1.81 | 1.00 | 1 | False | False |
| baselines-margin | seasonal_naive_drift | W2 | 1 | full_sample | 9 | 3.50 | 3.27 | 4.16 | -1.09 | 0.16 | 2.220 | 2.040 |  | 2.61 | 1.00 | 1 | False | False |
| baselines-margin | trailing4 | W2 | 1 | full_sample | 9 | 8.59 | 8.37 | 10.98 | -0.51 | -1.38 | 5.442 | 5.229 |  | 6.18 | 0.78 | 2 | False | False |
| baselines-margin | seasonal_naive | W2 | 2 | PIT | 8 | 1.72 | 1.66 | 1.82 | -0.86 | -0.52 | 1.000 | 1.000 |  | 1.52 | 1.00 | 1 | False | False |
| baselines-margin | seasonal_naive_drift | W2 | 2 | PIT | 8 | 3.08 | 2.44 | 4.34 | -1.48 | -0.32 | 1.788 | 1.470 |  | 3.00 | 1.00 | 1 | False | False |
| baselines-margin | trailing4 | W2 | 2 | PIT | 8 | 9.74 | 8.83 | 11.97 | -0.57 | -1.65 | 5.661 | 5.310 |  | 6.86 | 1.00 | 2 | False | False |
| baselines-margin | seasonal_naive | W2 | 2 | full_sample | 8 | 1.72 | 1.66 | 1.82 | -0.86 | -0.52 | 1.000 | 1.000 |  | 1.47 | 1.00 | 1 | False | False |
| baselines-margin | seasonal_naive_drift | W2 | 2 | full_sample | 8 | 3.08 | 2.44 | 4.34 | -1.48 | -0.32 | 1.788 | 1.470 |  | 2.83 | 1.00 | 1 | False | False |
| baselines-margin | trailing4 | W2 | 2 | full_sample | 8 | 9.74 | 8.83 | 11.97 | -0.57 | -1.65 | 5.661 | 5.310 |  | 6.83 | 0.88 | 2 | False | False |
