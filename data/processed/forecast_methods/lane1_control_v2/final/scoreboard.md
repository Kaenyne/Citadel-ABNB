# Harness scoreboard

Format v1.0. Built 2026-09-11. LIVE rows are excluded by construction: the 2026-08-06 guide enters no metric.

`rmse_ratio_to_naive` < 1 beats the naive rule (`y[q-4] * (1 + last observed y/y growth)`) on the same series, same window, same replay. A result must have `survives_both_windows` = True to be quoted.

> EXCHANGEABILITY VIOLATED: residuals are a time-ordered non-exchangeable sequence (expanding-window refits, a trending target, and a regime change at the 2022 reopening); conformal coverage here is descriptive, not a guarantee.

## target: `adr_yoy`

| method | object | window | prior_basis | n | mae | rmse | bias | rmse_ratio_to_naive | crps | cov_nominal | cov_empirical | conformal_cov_empirical | n_params | param_obs_ratio | survives_both_windows |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| calibration-rail | ref_ar1 | W1 | PIT | 14 | 1.5 | 1.9 | -0.3 |  | 1.1 | 0.800 | 0.500 | 0.625 | 3 | 0.214 | False |
| optimal-mix | mix_adr_yoy_all | W1 | PIT | 14 | 1.5 | 1.9 | -0.4 |  | 1.1 | 0.800 | 0.643 | 0.625 | 0 | 0.000 | False |
| optimal-mix | mix_adr_yoy_parsimonious | W1 | PIT | 14 | 1.5 | 1.9 | -0.4 |  | 1.1 | 0.800 | 0.643 | 0.625 | 0 | 0.000 | False |
| calibration-rail | ref_naive | W1 | PIT | 14 | 1.5 | 1.9 | -0.4 |  | 1.1 | 0.800 | 0.643 | 0.750 | 1 | 0.071 | False |
| calibration-rail | ref_trailing4 | W1 | PIT | 14 | 2.0 | 2.5 | -0.8 |  | 1.5 | 0.800 | 0.571 | 0.500 | 2 | 0.143 | False |
| calibration-rail | ref_ar1 | W1 | full_sample | 14 | 1.4 | 1.8 | -0.1 |  | 1.0 | 0.800 | 0.857 | 0.500 | 3 | 0.214 | False |
| optimal-mix | mix_adr_yoy_all | W1 | full_sample | 14 | 1.5 | 1.9 | -0.3 |  | 1.0 | 0.800 | 0.929 | 0.625 | 0 | 0.000 | False |
| optimal-mix | mix_adr_yoy_parsimonious | W1 | full_sample | 14 | 1.5 | 1.9 | -0.3 |  | 1.0 | 0.800 | 0.929 | 0.625 | 0 | 0.000 | False |
| calibration-rail | ref_naive | W1 | full_sample | 14 | 1.5 | 1.9 | -0.4 |  | 1.1 | 0.800 | 0.786 | 0.750 | 1 | 0.071 | False |
| calibration-rail | ref_trailing4 | W1 | full_sample | 14 | 2.0 | 2.5 | -0.8 |  | 1.4 | 0.800 | 0.786 | 0.500 | 2 | 0.143 | False |
| calibration-rail | ref_ar1 | W2 | PIT | 10 | 1.8 | 2.2 | -0.5 |  | 1.3 | 0.800 | 0.300 | 0.750 | 3 | 0.300 | False |
| calibration-rail | ref_naive | W2 | PIT | 10 | 1.7 | 2.2 | -0.3 |  | 1.3 | 0.800 | 0.600 | 1.000 | 1 | 0.100 | False |
| optimal-mix | mix_adr_yoy_all | W2 | PIT | 10 | 1.9 | 2.2 | -0.5 |  | 1.3 | 0.800 | 0.600 | 0.750 | 0 | 0.000 | False |
| optimal-mix | mix_adr_yoy_parsimonious | W2 | PIT | 10 | 1.9 | 2.2 | -0.5 |  | 1.3 | 0.800 | 0.600 | 0.750 | 0 | 0.000 | False |
| calibration-rail | ref_trailing4 | W2 | PIT | 10 | 2.2 | 2.8 | -1.1 |  | 1.6 | 0.800 | 0.600 | 0.250 | 2 | 0.200 | False |
| calibration-rail | ref_ar1 | W2 | full_sample | 10 | 1.7 | 2.1 | -0.2 |  | 1.2 | 0.800 | 0.800 | 0.750 | 3 | 0.300 | False |
| optimal-mix | mix_adr_yoy_all | W2 | full_sample | 10 | 1.8 | 2.1 | -0.4 |  | 1.2 | 0.800 | 0.900 | 0.750 | 0 | 0.000 | False |
| optimal-mix | mix_adr_yoy_parsimonious | W2 | full_sample | 10 | 1.8 | 2.1 | -0.4 |  | 1.2 | 0.800 | 0.900 | 0.750 | 0 | 0.000 | False |
| calibration-rail | ref_naive | W2 | full_sample | 10 | 1.7 | 2.2 | -0.3 |  | 1.2 | 0.800 | 0.700 | 1.000 | 1 | 0.100 | False |
| calibration-rail | ref_trailing4 | W2 | full_sample | 10 | 2.2 | 2.8 | -1.1 |  | 1.6 | 0.800 | 0.700 | 0.250 | 2 | 0.200 | False |

## target: `fx_pts_revenue`

| method | object | window | prior_basis | n | mae | rmse | bias | rmse_ratio_to_naive | crps | cov_nominal | cov_empirical | conformal_cov_empirical | n_params | param_obs_ratio | survives_both_windows |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| fx-lag | fx_rev_next_q_h2 | W1 | PIT | 10 | 0.9 | 1.0 | 0.1 |  | 0.7 | 0.800 | 1.000 | 1.000 | 2 | 0.200 | False |
| fx-lag-v2 | fx_rev_next_q_h2_v2 | W1 | PIT | 10 | 0.9 | 1.0 | 0.1 |  | 0.7 | 0.800 | 1.000 | 1.000 | 2 | 0.200 | False |
| fx-lag | fx_rev_next_q_h3 | W1 | PIT | 14 | 1.2 | 1.5 | 0.4 |  | 0.9 | 0.800 | 0.500 | 0.500 | 4 | 0.286 | False |
| fx-lag | fx_rev_next_q_h2 | W1 | full_sample | 10 | 0.9 | 1.0 | -0.0 |  | 0.6 | 0.800 | 1.000 | 0.750 | 2 | 0.200 | False |
| fx-lag-v2 | fx_rev_next_q_h2_v2 | W1 | full_sample | 10 | 0.9 | 1.0 | -0.0 |  | 0.6 | 0.800 | 1.000 | 0.750 | 2 | 0.200 | False |
| fx-lag | fx_rev_next_q_h3 | W1 | full_sample | 14 | 0.9 | 1.0 | 0.0 |  | 0.6 | 0.800 | 0.857 | 0.875 | 4 | 0.286 | False |
| fx-lag | fx_rev_next_q_h2 | W2 | PIT | 10 | 0.9 | 1.0 | 0.1 |  | 0.7 | 0.800 | 1.000 | 1.000 | 2 | 0.200 | False |
| fx-lag-v2 | fx_rev_next_q_h2_v2 | W2 | PIT | 10 | 0.9 | 1.0 | 0.1 |  | 0.7 | 0.800 | 1.000 | 1.000 | 2 | 0.200 | False |
| fx-lag | fx_rev_next_q_h3 | W2 | PIT | 10 | 1.4 | 1.7 | 0.5 |  | 1.1 | 0.800 | 0.400 | 0.250 | 4 | 0.400 | False |
| fx-lag | fx_rev_next_q_h3 | W2 | full_sample | 10 | 0.7 | 0.8 | 0.2 |  | 0.5 | 0.800 | 0.900 | 0.750 | 4 | 0.400 | False |
| fx-lag | fx_rev_next_q_h2 | W2 | full_sample | 10 | 0.9 | 1.0 | -0.0 |  | 0.6 | 0.800 | 1.000 | 0.750 | 2 | 0.200 | False |
| fx-lag-v2 | fx_rev_next_q_h2_v2 | W2 | full_sample | 10 | 0.9 | 1.0 | -0.0 |  | 0.6 | 0.800 | 1.000 | 0.750 | 2 | 0.200 | False |

## target: `gbv_musd`

| method | object | window | prior_basis | n | mae | rmse | bias | rmse_ratio_to_naive | crps | cov_nominal | cov_empirical | conformal_cov_empirical | n_params | param_obs_ratio | survives_both_windows |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| baselines | naive | W1 | PIT | 14 | 626.5 | 722.0 | 64.0 | 1.000 | 506.4 | 0.800 | 1.000 | 0.875 | 1 | 0.071 | False |
| optimal-mix | mix_gbv_musd_all | W1 | PIT | 14 | 781.4 | 947.0 | 352.2 | 1.312 | 533.3 | 0.800 | 1.000 | 0.875 | 0 | 0.000 | False |
| optimal-mix | mix_gbv_musd_parsimonious | W1 | PIT | 14 | 781.4 | 947.0 | 352.2 | 1.312 | 533.3 | 0.800 | 1.000 | 0.875 | 0 | 0.000 | False |
| baselines | ar1 | W1 | PIT | 14 | 922.2 | 1,200.0 | 736.3 | 1.662 | 710.0 | 0.800 | 0.500 | 0.875 | 3 | 0.214 | False |
| baselines | trailing4 | W1 | PIT | 14 | 909.6 | 1,204.7 | 359.8 | 1.668 | 734.7 | 0.800 | 0.786 | 0.750 | 2 | 0.143 | False |
| baselines | naive_seasonal | W1 | PIT | 14 | 2,600.0 | 2,719.8 | -2,600.0 | 3.767 | 1,817.3 | 0.800 | 0.643 | 0.750 | 1 | 0.071 | False |
| baselines | ar1 | W1 | full_sample | 14 | 554.3 | 709.3 | 294.0 | 0.982 | 382.9 | 0.800 | 0.857 | 0.875 | 3 | 0.214 | False |
| baselines | naive | W1 | full_sample | 14 | 626.5 | 722.0 | 64.0 | 1.000 | 401.5 | 0.800 | 0.786 | 0.875 | 1 | 0.071 | False |
| optimal-mix | mix_gbv_musd_all | W1 | full_sample | 14 | 687.4 | 778.8 | 255.0 | 1.079 | 429.8 | 0.800 | 0.857 | 0.875 | 0 | 0.000 | False |
| optimal-mix | mix_gbv_musd_parsimonious | W1 | full_sample | 14 | 687.4 | 778.8 | 255.0 | 1.079 | 429.8 | 0.800 | 0.857 | 0.875 | 0 | 0.000 | False |
| baselines | trailing4 | W1 | full_sample | 14 | 909.6 | 1,204.7 | 359.8 | 1.668 | 659.3 | 0.800 | 0.786 | 0.750 | 2 | 0.143 | False |
| baselines | naive_seasonal | W1 | full_sample | 14 | 2,600.0 | 2,719.8 | -2,600.0 | 3.767 | 2,232.0 | 0.800 | 0.000 | 0.750 | 1 | 0.071 | False |
| baselines | naive | W2 | PIT | 10 | 645.0 | 737.3 | 12.2 | 1.000 | 487.3 | 0.800 | 1.000 | 1.000 | 1 | 0.100 | False |
| optimal-mix | mix_gbv_musd_all | W2 | PIT | 10 | 676.5 | 753.0 | 81.0 | 1.021 | 488.9 | 0.800 | 1.000 | 1.000 | 0 | 0.000 | False |
| optimal-mix | mix_gbv_musd_parsimonious | W2 | PIT | 10 | 676.5 | 753.0 | 81.0 | 1.021 | 488.9 | 0.800 | 1.000 | 1.000 | 0 | 0.000 | False |
| baselines | trailing4 | W2 | PIT | 10 | 697.8 | 837.9 | -72.0 | 1.136 | 546.1 | 0.800 | 0.900 | 0.750 | 2 | 0.200 | False |
| baselines | ar1 | W2 | PIT | 10 | 707.9 | 903.5 | 447.7 | 1.225 | 498.3 | 0.800 | 0.600 | 1.000 | 3 | 0.300 | False |
| baselines | naive_seasonal | W2 | PIT | 10 | 2,640.0 | 2,786.0 | -2,640.0 | 3.779 | 1,961.1 | 0.800 | 0.500 | 0.500 | 1 | 0.100 | False |
| optimal-mix | mix_gbv_musd_all | W2 | full_sample | 10 | 657.8 | 726.6 | 106.0 | 0.985 | 403.0 | 0.800 | 0.900 | 1.000 | 0 | 0.000 | False |
| optimal-mix | mix_gbv_musd_parsimonious | W2 | full_sample | 10 | 657.8 | 726.6 | 106.0 | 0.985 | 403.0 | 0.800 | 0.900 | 1.000 | 0 | 0.000 | False |
| baselines | naive | W2 | full_sample | 10 | 645.0 | 737.3 | 12.2 | 1.000 | 407.6 | 0.800 | 0.900 | 1.000 | 1 | 0.100 | False |
| baselines | ar1 | W2 | full_sample | 10 | 574.2 | 744.5 | 312.1 | 1.010 | 397.4 | 0.800 | 0.900 | 1.000 | 3 | 0.300 | False |
| baselines | trailing4 | W2 | full_sample | 10 | 697.8 | 837.9 | -72.0 | 1.136 | 463.7 | 0.800 | 0.900 | 0.750 | 2 | 0.200 | False |
| baselines | naive_seasonal | W2 | full_sample | 10 | 2,640.0 | 2,786.0 | -2,640.0 | 3.779 | 2,247.3 | 0.800 | 0.000 | 0.500 | 1 | 0.100 | False |

## target: `gbv_yoy`

| method | object | window | prior_basis | n | mae | rmse | bias | rmse_ratio_to_naive | crps | cov_nominal | cov_empirical | conformal_cov_empirical | n_params | param_obs_ratio | survives_both_windows |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| calibration-rail | ref_naive | W1 | PIT | 14 | 3.2 | 3.7 | 0.3 |  | 2.3 | 0.800 | 0.786 | 0.875 | 1 | 0.071 | False |
| optimal-mix | mix_gbv_yoy_all | W1 | PIT | 14 | 4.1 | 5.1 | 2.0 |  | 2.8 | 0.800 | 0.786 | 0.875 | 0 | 0.000 | False |
| optimal-mix | mix_gbv_yoy_parsimonious | W1 | PIT | 14 | 4.1 | 5.1 | 2.0 |  | 2.8 | 0.800 | 0.786 | 0.875 | 0 | 0.000 | False |
| calibration-rail | ref_ar1 | W1 | PIT | 14 | 4.9 | 6.6 | 4.1 |  | 4.0 | 0.800 | 0.429 | 0.875 | 3 | 0.214 | False |
| calibration-rail | ref_trailing4 | W1 | PIT | 14 | 4.9 | 6.6 | 2.2 |  | 4.0 | 0.800 | 0.786 | 0.750 | 2 | 0.143 | False |
| calibration-rail | ref_ar1 | W1 | full_sample | 14 | 2.8 | 3.5 | 1.5 |  | 2.0 | 0.800 | 0.857 | 0.875 | 3 | 0.214 | False |
| calibration-rail | ref_naive | W1 | full_sample | 14 | 3.2 | 3.7 | 0.3 |  | 2.1 | 0.800 | 0.786 | 0.875 | 1 | 0.071 | False |
| optimal-mix | mix_gbv_yoy_all | W1 | full_sample | 14 | 3.5 | 4.0 | 1.5 |  | 2.2 | 0.800 | 0.857 | 0.875 | 0 | 0.000 | False |
| optimal-mix | mix_gbv_yoy_parsimonious | W1 | full_sample | 14 | 3.5 | 4.0 | 1.5 |  | 2.2 | 0.800 | 0.857 | 0.875 | 0 | 0.000 | False |
| calibration-rail | ref_trailing4 | W1 | full_sample | 14 | 4.9 | 6.6 | 2.2 |  | 3.6 | 0.800 | 0.786 | 0.750 | 2 | 0.143 | False |
| calibration-rail | ref_naive | W2 | PIT | 10 | 3.1 | 3.4 | -0.1 |  | 2.0 | 0.800 | 0.900 | 1.000 | 1 | 0.100 | False |
| optimal-mix | mix_gbv_yoy_all | W2 | PIT | 10 | 3.2 | 3.5 | 0.3 |  | 2.1 | 0.800 | 0.900 | 1.000 | 0 | 0.000 | False |
| optimal-mix | mix_gbv_yoy_parsimonious | W2 | PIT | 10 | 3.2 | 3.5 | 0.3 |  | 2.1 | 0.800 | 0.900 | 1.000 | 0 | 0.000 | False |
| calibration-rail | ref_trailing4 | W2 | PIT | 10 | 3.4 | 3.9 | -0.3 |  | 2.3 | 0.800 | 1.000 | 0.750 | 2 | 0.200 | False |
| calibration-rail | ref_ar1 | W2 | PIT | 10 | 3.4 | 4.2 | 2.1 |  | 2.4 | 0.800 | 0.600 | 1.000 | 3 | 0.300 | False |
| optimal-mix | mix_gbv_yoy_all | W2 | full_sample | 10 | 3.0 | 3.3 | 0.6 |  | 1.9 | 0.800 | 0.900 | 1.000 | 0 | 0.000 | False |
| optimal-mix | mix_gbv_yoy_parsimonious | W2 | full_sample | 10 | 3.0 | 3.3 | 0.6 |  | 1.9 | 0.800 | 0.900 | 1.000 | 0 | 0.000 | False |
| calibration-rail | ref_ar1 | W2 | full_sample | 10 | 2.7 | 3.4 | 1.4 |  | 1.9 | 0.800 | 0.900 | 1.000 | 3 | 0.300 | False |
| calibration-rail | ref_naive | W2 | full_sample | 10 | 3.1 | 3.4 | -0.1 |  | 2.0 | 0.800 | 0.900 | 1.000 | 1 | 0.100 | False |
| calibration-rail | ref_trailing4 | W2 | full_sample | 10 | 3.4 | 3.9 | -0.3 |  | 2.2 | 0.800 | 0.900 | 0.750 | 2 | 0.200 | False |

## target: `guide_mid`

| method | object | window | prior_basis | n | mae | rmse | bias | rmse_ratio_to_naive | crps | cov_nominal | cov_empirical | conformal_cov_empirical | n_params | param_obs_ratio | survives_both_windows |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| guidance-policy | guide_mid_next_q | W1 | PIT | 14 | 51.2 | 63.6 | 21.9 |  | 43.3 | 0.800 | 1.000 | 1.000 | 6 | 0.429 | False |
| guidance-policy | guide_mid_next_q | W1 | full_sample | 14 | 33.1 | 37.2 | -15.0 |  | 36.1 | 0.800 | 1.000 | 0.625 | 6 | 0.429 | False |
| guidance-policy | guide_mid_next_q | W2 | PIT | 10 | 47.6 | 58.8 | 14.9 |  | 41.1 | 0.800 | 1.000 | 1.000 | 6 | 0.600 | False |
| guidance-policy | guide_mid_next_q | W2 | full_sample | 10 | 31.7 | 35.8 | -16.0 |  | 35.4 | 0.800 | 1.000 | 0.500 | 6 | 0.600 | False |

## target: `nights_m`

| method | object | window | prior_basis | n | mae | rmse | bias | rmse_ratio_to_naive | crps | cov_nominal | cov_empirical | conformal_cov_empirical | n_params | param_obs_ratio | survives_both_windows |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| baselines | naive | W1 | PIT | 14 | 2.4 | 3.2 | 0.8 | 1.000 | 2.2 | 0.800 | 1.000 | 0.875 | 1 | 0.071 | False |
| optimal-mix | mix_nights_m_all | W1 | PIT | 14 | 3.6 | 4.9 | 2.6 | 1.549 | 2.5 | 0.800 | 0.929 | 0.875 | 0 | 0.000 | False |
| optimal-mix | mix_nights_m_parsimonious | W1 | PIT | 14 | 3.6 | 4.9 | 2.6 | 1.549 | 2.5 | 0.800 | 0.929 | 0.875 | 0 | 0.000 | False |
| baselines | trailing4 | W1 | PIT | 14 | 4.1 | 5.6 | 3.1 | 1.756 | 3.3 | 0.800 | 0.786 | 1.000 | 2 | 0.143 | False |
| baselines | ar1 | W1 | PIT | 14 | 5.4 | 7.1 | 5.3 | 2.249 | 4.3 | 0.800 | 0.429 | 0.875 | 3 | 0.214 | False |
| baselines | naive_seasonal | W1 | PIT | 14 | 11.9 | 12.1 | -11.9 | 3.827 | 7.7 | 0.800 | 0.714 | 0.750 | 1 | 0.071 | False |
| baselines | naive | W1 | full_sample | 14 | 2.4 | 3.2 | 0.8 | 1.000 | 1.7 | 0.800 | 0.786 | 0.875 | 1 | 0.071 | False |
| baselines | ar1 | W1 | full_sample | 14 | 2.5 | 3.2 | 1.9 | 1.009 | 1.8 | 0.800 | 0.786 | 0.875 | 3 | 0.214 | False |
| optimal-mix | mix_nights_m_all | W1 | full_sample | 14 | 2.7 | 3.6 | 2.0 | 1.136 | 1.9 | 0.800 | 0.714 | 0.875 | 0 | 0.000 | False |
| optimal-mix | mix_nights_m_parsimonious | W1 | full_sample | 14 | 2.7 | 3.6 | 2.0 | 1.136 | 1.9 | 0.800 | 0.714 | 0.875 | 0 | 0.000 | False |
| baselines | trailing4 | W1 | full_sample | 14 | 4.1 | 5.6 | 3.1 | 1.756 | 3.1 | 0.800 | 0.643 | 1.000 | 2 | 0.143 | False |
| baselines | naive_seasonal | W1 | full_sample | 14 | 11.9 | 12.1 | -11.9 | 3.827 | 10.7 | 0.800 | 0.000 | 0.750 | 1 | 0.071 | False |
| baselines | naive | W2 | PIT | 10 | 2.0 | 2.6 | 0.3 | 1.000 | 1.9 | 0.800 | 1.000 | 1.000 | 1 | 0.100 | False |
| baselines | trailing4 | W2 | PIT | 10 | 2.3 | 2.6 | 1.0 | 1.020 | 1.9 | 0.800 | 1.000 | 1.000 | 2 | 0.200 | False |
| optimal-mix | mix_nights_m_all | W2 | PIT | 10 | 2.2 | 2.9 | 0.9 | 1.105 | 1.9 | 0.800 | 1.000 | 1.000 | 0 | 0.000 | False |
| optimal-mix | mix_nights_m_parsimonious | W2 | PIT | 10 | 2.2 | 2.9 | 0.9 | 1.105 | 1.9 | 0.800 | 1.000 | 1.000 | 0 | 0.000 | False |
| baselines | ar1 | W2 | PIT | 10 | 3.5 | 4.5 | 3.3 | 1.730 | 2.6 | 0.800 | 0.600 | 1.000 | 3 | 0.300 | False |
| baselines | naive_seasonal | W2 | PIT | 10 | 11.2 | 11.3 | -11.2 | 4.346 | 7.6 | 0.800 | 0.600 | 0.500 | 1 | 0.100 | False |
| baselines | naive | W2 | full_sample | 10 | 2.0 | 2.6 | 0.3 | 1.000 | 1.4 | 0.800 | 0.800 | 1.000 | 1 | 0.100 | False |
| baselines | trailing4 | W2 | full_sample | 10 | 2.3 | 2.6 | 1.0 | 1.020 | 1.5 | 0.800 | 0.900 | 1.000 | 2 | 0.200 | False |
| optimal-mix | mix_nights_m_all | W2 | full_sample | 10 | 2.1 | 2.7 | 1.2 | 1.038 | 1.4 | 0.800 | 0.700 | 1.000 | 0 | 0.000 | False |
| optimal-mix | mix_nights_m_parsimonious | W2 | full_sample | 10 | 2.1 | 2.7 | 1.2 | 1.038 | 1.4 | 0.800 | 0.700 | 1.000 | 0 | 0.000 | False |
| baselines | ar1 | W2 | full_sample | 10 | 2.4 | 3.0 | 2.0 | 1.159 | 1.7 | 0.800 | 0.800 | 1.000 | 3 | 0.300 | False |
| baselines | naive_seasonal | W2 | full_sample | 10 | 11.2 | 11.3 | -11.2 | 4.346 | 9.9 | 0.800 | 0.000 | 0.500 | 1 | 0.100 | False |

## target: `nights_yoy`

| method | object | window | prior_basis | n | mae | rmse | bias | rmse_ratio_to_naive | crps | cov_nominal | cov_empirical | conformal_cov_empirical | n_params | param_obs_ratio | survives_both_windows |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| calibration-rail | ref_naive | W1 | PIT | 14 | 2.1 | 2.9 | 0.7 |  | 1.7 | 0.800 | 0.714 | 0.875 | 1 | 0.071 | False |
| optimal-mix | mix_nights_yoy_all | W1 | PIT | 14 | 2.4 | 3.5 | 1.8 |  | 2.0 | 0.800 | 1.000 | 1.000 | 0 | 0.000 | False |
| optimal-mix | mix_nights_yoy_parsimonious | W1 | PIT | 14 | 2.4 | 3.5 | 1.8 |  | 2.0 | 0.800 | 1.000 | 1.000 | 0 | 0.000 | False |
| tracker-backlog | nights_yoy_next_q | W1 | PIT | 112 | 3.7 | 5.0 | 1.6 |  | 2.7 | 0.800 | 0.964 | 0.868 | 2 | 0.018 | False |
| calibration-rail | ref_trailing4 | W1 | PIT | 14 | 3.8 | 5.3 | 3.0 |  | 3.2 | 0.800 | 0.786 | 1.000 | 2 | 0.143 | False |
| calibration-rail | ref_ar1 | W1 | PIT | 14 | 4.9 | 6.7 | 4.8 |  | 4.1 | 0.800 | 0.500 | 1.000 | 3 | 0.214 | False |
| optimal-mix | mix_nights_yoy_all | W1 | full_sample | 14 | 1.7 | 2.3 | 1.1 |  | 1.5 | 0.800 | 1.000 | 1.000 | 0 | 0.000 | False |
| optimal-mix | mix_nights_yoy_parsimonious | W1 | full_sample | 14 | 1.7 | 2.3 | 1.1 |  | 1.5 | 0.800 | 1.000 | 1.000 | 0 | 0.000 | False |
| calibration-rail | ref_ar1 | W1 | full_sample | 14 | 2.1 | 2.8 | 1.6 |  | 1.5 | 0.800 | 0.786 | 0.875 | 3 | 0.214 | False |
| calibration-rail | ref_naive | W1 | full_sample | 14 | 2.1 | 2.9 | 0.7 |  | 1.5 | 0.800 | 0.786 | 0.875 | 1 | 0.071 | False |
| tracker-backlog | nights_yoy_next_q | W1 | full_sample | 112 | 2.8 | 3.9 | 1.0 |  | 2.1 | 0.800 | 0.955 | 0.783 | 2 | 0.018 | False |
| calibration-rail | ref_trailing4 | W1 | full_sample | 14 | 3.8 | 5.3 | 3.0 |  | 2.9 | 0.800 | 0.643 | 1.000 | 2 | 0.143 | False |
| optimal-mix | mix_nights_yoy_all | W2 | PIT | 10 | 1.5 | 2.1 | 0.6 |  | 1.5 | 0.800 | 1.000 | 1.000 | 0 | 0.000 | False |
| optimal-mix | mix_nights_yoy_parsimonious | W2 | PIT | 10 | 1.5 | 2.1 | 0.6 |  | 1.5 | 0.800 | 1.000 | 1.000 | 0 | 0.000 | False |
| calibration-rail | ref_naive | W2 | PIT | 10 | 1.7 | 2.2 | 0.2 |  | 1.3 | 0.800 | 0.900 | 1.000 | 1 | 0.100 | False |
| calibration-rail | ref_trailing4 | W2 | PIT | 10 | 1.9 | 2.2 | 0.8 |  | 1.5 | 0.800 | 1.000 | 1.000 | 2 | 0.200 | False |
| calibration-rail | ref_ar1 | W2 | PIT | 10 | 2.9 | 3.6 | 2.7 |  | 2.0 | 0.800 | 0.700 | 1.000 | 3 | 0.300 | False |
| tracker-backlog | nights_yoy_next_q | W2 | PIT | 80 | 3.4 | 4.8 | 0.7 |  | 2.5 | 0.800 | 0.950 | 0.851 | 2 | 0.025 | False |
| optimal-mix | mix_nights_yoy_all | W2 | full_sample | 10 | 1.4 | 1.9 | 0.6 |  | 1.3 | 0.800 | 1.000 | 1.000 | 0 | 0.000 | False |
| optimal-mix | mix_nights_yoy_parsimonious | W2 | full_sample | 10 | 1.4 | 1.9 | 0.6 |  | 1.3 | 0.800 | 1.000 | 1.000 | 0 | 0.000 | False |
| calibration-rail | ref_naive | W2 | full_sample | 10 | 1.7 | 2.2 | 0.2 |  | 1.2 | 0.800 | 0.800 | 1.000 | 1 | 0.100 | False |
| calibration-rail | ref_trailing4 | W2 | full_sample | 10 | 1.9 | 2.2 | 0.8 |  | 1.3 | 0.800 | 0.900 | 1.000 | 2 | 0.200 | False |
| calibration-rail | ref_ar1 | W2 | full_sample | 10 | 2.0 | 2.4 | 1.5 |  | 1.4 | 0.800 | 0.800 | 1.000 | 3 | 0.300 | False |
| tracker-backlog | nights_yoy_next_q | W2 | full_sample | 80 | 2.9 | 4.1 | 0.8 |  | 2.1 | 0.800 | 0.950 | 0.743 | 2 | 0.025 | False |

## target: `revenue_musd`

| method | object | window | prior_basis | n | mae | rmse | bias | rmse_ratio_to_naive | crps | cov_nominal | cov_empirical | conformal_cov_empirical | n_params | param_obs_ratio | survives_both_windows |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| optimal-mix | mix_revenue_musd_parsimonious | W1 | PIT | 14 | 28.3 | 33.9 | 12.3 | 0.360 | 23.8 | 0.800 | 0.929 | 0.875 | 0 | 0.000 | True |
| baselines | guide_cushion | W1 | PIT | 14 | 31.0 | 35.5 | 10.6 | 0.377 | 19.7 | 0.800 | 0.643 | 1.000 | 1 | 0.071 | True |
| guidance-policy | print_from_guide | W1 | PIT | 14 | 29.2 | 35.6 | 14.7 | 0.379 | 19.8 | 0.800 | 0.857 | 0.875 | 1 | 0.071 | True |
| calibration-rail | gbm_surprise_guide | W1 | PIT | 10 | 32.3 | 36.8 | 12.6 | 0.339 | 25.4 | 0.800 | 0.300 | 0.750 | 4 | 0.400 | True |
| optimal-mix | mix_revenue_musd_all | W1 | PIT | 14 | 33.8 | 40.6 | 22.3 | 0.432 | 25.8 | 0.800 | 1.000 | 1.000 | 0 | 0.000 | True |
| kernel-lambda | revenue_level_next_q_last3_ex_covid | W1 | PIT | 14 | 38.5 | 52.2 | 0.3 | 0.555 | 30.9 | 0.800 | 0.643 | 0.875 | 5 | 0.357 | True |
| kernel-lambda | revenue_level_next_q_ex_covid | W1 | PIT | 14 | 39.5 | 53.1 | 2.3 | 0.565 | 31.5 | 0.800 | 0.643 | 0.875 | 5 | 0.357 | True |
| optimal-mix | mix_revenue_musd_noguide | W1 | PIT | 14 | 50.0 | 66.8 | 28.7 | 0.710 | 39.5 | 0.800 | 0.929 | 0.875 | 0 | 0.000 | True |
| guidance-policy | print_kernel_policy | W1 | PIT | 14 | 52.7 | 72.0 | 37.3 | 0.766 | 45.2 | 0.800 | 1.000 | 1.000 | 5 | 0.357 | True |
| kernel-lambda | revenue_level_next_q_last3 | W1 | PIT | 14 | 52.7 | 72.0 | 37.3 | 0.766 | 42.0 | 0.800 | 0.786 | 1.000 | 5 | 0.357 | True |
| kernel-lambda | revenue_level_next_q | W1 | PIT | 14 | 61.1 | 78.1 | 59.0 | 0.831 | 45.6 | 0.800 | 0.786 | 1.000 | 5 | 0.357 | True |
| baselines | naive | W1 | PIT | 14 | 75.1 | 94.0 | 12.8 | 1.000 | 57.9 | 0.800 | 0.929 | 0.875 | 1 | 0.071 | False |
| calibration-rail | gbm_revenue | W1 | PIT | 10 | 73.6 | 100.5 | 37.0 | 0.927 | 60.1 | 0.800 | 0.600 | 1.000 | 4 | 0.400 | True |
| baselines | street | W1 | PIT | 14 | 87.7 | 100.9 | -68.3 | 1.073 | 58.4 | 0.800 | 0.786 | 0.875 | 0 | 0.000 | False |
| baselines | ar1 | W1 | PIT | 14 | 90.1 | 103.5 | -48.8 | 1.101 | 68.8 | 0.800 | 0.286 | 0.875 | 3 | 0.214 | False |
| kernel-lambda | revenue_level_h1 | W1 | PIT | 14 | 88.3 | 109.9 | 70.2 | 1.169 | 63.0 | 0.800 | 0.857 | 1.000 | 5 | 0.357 | False |
| kernel-lambda | revenue_level_next_q_w038 | W1 | PIT | 14 | 109.5 | 134.8 | 98.7 | 1.433 | 73.1 | 0.800 | 0.929 | 0.750 | 5 | 0.357 | False |
| kernel-lambda | revenue_level_next_q_w033 | W1 | PIT | 14 | 120.1 | 148.9 | 106.9 | 1.584 | 80.1 | 0.800 | 0.929 | 0.875 | 5 | 0.357 | False |
| baselines | trailing4 | W1 | PIT | 14 | 134.8 | 169.8 | 75.3 | 1.806 | 108.4 | 0.800 | 0.857 | 1.000 | 2 | 0.143 | False |
| baselines | naive_seasonal | W1 | PIT | 14 | 340.0 | 352.9 | -340.0 | 3.754 | 227.7 | 0.800 | 0.714 | 0.500 | 1 | 0.071 | False |
| l1-reconciliation | revenue_contemporaneous | W1 | PIT | 10 | 1,147.2 | 1,229.4 | 126.9 | 11.338 | 835.8 | 0.800 | 0.700 | 1.000 | 68 | 6.800 | False |
| guidance-policy | print_kernel_policy | W1 | full_sample | 14 | 26.2 | 33.6 | -1.2 | 0.357 | 33.6 | 0.800 | 1.000 | 1.000 | 5 | 0.357 | True |
| kernel-lambda | revenue_level_next_q_last3 | W1 | full_sample | 14 | 26.2 | 33.6 | -1.2 | 0.357 | 25.6 | 0.800 | 1.000 | 1.000 | 5 | 0.357 | True |
| kernel-lambda | revenue_level_next_q_last3_ex_covid | W1 | full_sample | 14 | 26.2 | 33.6 | -1.2 | 0.357 | 20.2 | 0.800 | 0.857 | 1.000 | 5 | 0.357 | True |
| optimal-mix | mix_revenue_musd_all | W1 | full_sample | 14 | 29.1 | 34.5 | 17.5 | 0.367 | 23.2 | 0.800 | 1.000 | 0.750 | 0 | 0.000 | True |
| baselines | guide_cushion | W1 | full_sample | 14 | 28.5 | 35.3 | 13.5 | 0.375 | 17.8 | 0.800 | 0.786 | 0.750 | 1 | 0.071 | True |
| guidance-policy | print_from_guide | W1 | full_sample | 14 | 28.7 | 35.6 | 14.2 | 0.379 | 19.1 | 0.800 | 1.000 | 0.750 | 1 | 0.071 | True |
| optimal-mix | mix_revenue_musd_noguide | W1 | full_sample | 14 | 29.6 | 36.0 | 13.9 | 0.383 | 27.3 | 0.800 | 1.000 | 0.875 | 0 | 0.000 | True |
| calibration-rail | gbm_surprise_guide | W1 | full_sample | 14 | 31.4 | 36.4 | 4.6 | 0.387 | 26.3 | 0.800 | 0.214 | 0.750 | 4 | 0.286 | True |
| kernel-lambda | revenue_level_next_q_ex_covid | W1 | full_sample | 14 | 26.5 | 36.6 | 0.3 | 0.389 | 20.9 | 0.800 | 0.929 | 0.875 | 5 | 0.357 | True |
| optimal-mix | mix_revenue_musd_parsimonious | W1 | full_sample | 14 | 30.6 | 38.7 | 21.0 | 0.411 | 24.1 | 0.800 | 1.000 | 0.750 | 0 | 0.000 | True |
| kernel-lambda | revenue_level_next_q | W1 | full_sample | 14 | 38.5 | 50.1 | 31.8 | 0.533 | 31.1 | 0.800 | 0.929 | 1.000 | 5 | 0.357 | True |
| calibration-rail | gbm_revenue | W1 | full_sample | 14 | 53.0 | 73.0 | -9.4 | 0.777 | 41.0 | 0.800 | 0.429 | 1.000 | 4 | 0.286 | True |
| kernel-lambda | revenue_level_next_q_w038 | W1 | full_sample | 14 | 62.7 | 77.8 | 53.8 | 0.827 | 46.3 | 0.800 | 1.000 | 0.750 | 5 | 0.357 | True |
| kernel-lambda | revenue_level_h1 | W1 | full_sample | 14 | 64.9 | 80.8 | 42.6 | 0.859 | 48.0 | 0.800 | 0.857 | 1.000 | 5 | 0.357 | True |
| baselines | ar1 | W1 | full_sample | 14 | 64.1 | 84.6 | -5.1 | 0.900 | 47.0 | 0.800 | 0.714 | 0.875 | 3 | 0.214 | True |
| kernel-lambda | revenue_level_next_q_w033 | W1 | full_sample | 14 | 68.0 | 85.5 | 58.4 | 0.909 | 50.1 | 0.800 | 1.000 | 0.750 | 5 | 0.357 | True |
| baselines | naive | W1 | full_sample | 14 | 75.1 | 94.0 | 12.8 | 1.000 | 52.8 | 0.800 | 0.714 | 0.875 | 1 | 0.071 | False |
| baselines | street | W1 | full_sample | 14 | 87.7 | 100.9 | -68.3 | 1.073 | 60.1 | 0.800 | 0.929 | 0.875 | 0 | 0.000 | False |
| baselines | trailing4 | W1 | full_sample | 14 | 134.8 | 169.8 | 75.3 | 1.806 | 97.5 | 0.800 | 0.643 | 1.000 | 2 | 0.143 | False |
| baselines | naive_seasonal | W1 | full_sample | 14 | 340.0 | 352.9 | -340.0 | 3.754 | 285.0 | 0.800 | 0.000 | 0.500 | 1 | 0.071 | False |
| l1-reconciliation | revenue_contemporaneous | W1 | full_sample | 14 | 1,003.7 | 1,027.4 | -12.3 | 10.927 | 616.2 | 0.800 | 0.643 | 0.875 | 68 | 4.857 | False |
| optimal-mix | mix_revenue_musd_all | W2 | PIT | 10 | 29.5 | 33.9 | 13.7 | 0.313 | 19.4 | 0.800 | 1.000 | 1.000 | 0 | 0.000 | True |
| baselines | guide_cushion | W2 | PIT | 10 | 30.9 | 34.6 | 8.7 | 0.319 | 20.4 | 0.800 | 0.600 | 1.000 | 1 | 0.100 | True |
| guidance-policy | print_from_guide | W2 | PIT | 10 | 30.7 | 35.9 | 12.1 | 0.331 | 20.2 | 0.800 | 0.800 | 1.000 | 1 | 0.100 | True |
| optimal-mix | mix_revenue_musd_parsimonious | W2 | PIT | 10 | 31.6 | 36.0 | 9.8 | 0.332 | 20.0 | 0.800 | 0.900 | 1.000 | 0 | 0.000 | True |
| calibration-rail | gbm_surprise_guide | W2 | PIT | 10 | 32.3 | 36.8 | 12.6 | 0.339 | 25.4 | 0.800 | 0.300 | 0.750 | 4 | 0.400 | True |
| kernel-lambda | revenue_level_next_q_last3_ex_covid | W2 | PIT | 10 | 36.2 | 51.2 | 5.9 | 0.472 | 30.0 | 0.800 | 0.700 | 1.000 | 5 | 0.500 | True |
| kernel-lambda | revenue_level_next_q_ex_covid | W2 | PIT | 10 | 37.6 | 52.5 | 8.7 | 0.484 | 30.9 | 0.800 | 0.700 | 1.000 | 5 | 0.500 | True |
| optimal-mix | mix_revenue_musd_noguide | W2 | PIT | 10 | 45.4 | 63.6 | 15.5 | 0.587 | 35.8 | 0.800 | 0.900 | 1.000 | 0 | 0.000 | True |
| guidance-policy | print_kernel_policy | W2 | PIT | 10 | 49.1 | 70.2 | 27.5 | 0.647 | 43.9 | 0.800 | 1.000 | 1.000 | 5 | 0.500 | True |
| kernel-lambda | revenue_level_next_q_last3 | W2 | PIT | 10 | 49.1 | 70.2 | 27.5 | 0.647 | 40.9 | 0.800 | 0.800 | 1.000 | 5 | 0.500 | True |
| kernel-lambda | revenue_level_next_q | W2 | PIT | 10 | 60.8 | 78.8 | 57.9 | 0.727 | 45.9 | 0.800 | 0.800 | 1.000 | 5 | 0.500 | True |
| baselines | street | W2 | PIT | 10 | 82.1 | 94.5 | -54.9 | 0.871 | 54.7 | 0.800 | 0.700 | 0.750 | 0 | 0.000 | False |
| kernel-lambda | revenue_level_h1 | W2 | PIT | 10 | 72.7 | 96.0 | 54.4 | 0.886 | 55.3 | 0.800 | 0.900 | 1.000 | 5 | 0.500 | False |
| calibration-rail | gbm_revenue | W2 | PIT | 10 | 73.6 | 100.5 | 37.0 | 0.927 | 60.1 | 0.800 | 0.600 | 1.000 | 4 | 0.400 | True |
| baselines | naive | W2 | PIT | 10 | 91.5 | 108.4 | 4.2 | 1.000 | 64.4 | 0.800 | 0.900 | 1.000 | 1 | 0.100 | False |
| baselines | ar1 | W2 | PIT | 10 | 93.4 | 109.4 | -35.6 | 1.009 | 71.1 | 0.800 | 0.400 | 1.000 | 3 | 0.300 | False |
| baselines | trailing4 | W2 | PIT | 10 | 99.0 | 119.4 | 15.8 | 1.101 | 77.2 | 0.800 | 1.000 | 1.000 | 2 | 0.200 | False |
| kernel-lambda | revenue_level_next_q_w038 | W2 | PIT | 10 | 106.7 | 129.7 | 93.6 | 1.196 | 70.9 | 0.800 | 0.900 | 0.750 | 5 | 0.500 | False |
| kernel-lambda | revenue_level_next_q_w033 | W2 | PIT | 10 | 116.3 | 142.2 | 101.1 | 1.311 | 77.1 | 0.800 | 0.900 | 1.000 | 5 | 0.500 | False |
| baselines | naive_seasonal | W2 | PIT | 10 | 324.2 | 337.8 | -324.2 | 3.115 | 230.9 | 0.800 | 0.600 | 0.250 | 1 | 0.100 | False |
| l1-reconciliation | revenue_contemporaneous | W2 | PIT | 10 | 1,147.2 | 1,229.4 | 126.9 | 11.338 | 835.8 | 0.800 | 0.700 | 1.000 | 68 | 6.800 | False |
| optimal-mix | mix_revenue_musd_noguide | W2 | full_sample | 10 | 28.0 | 35.4 | 6.1 | 0.326 | 25.2 | 0.800 | 1.000 | 1.000 | 0 | 0.000 | True |
| guidance-policy | print_kernel_policy | W2 | full_sample | 10 | 29.8 | 37.7 | 2.0 | 0.348 | 33.9 | 0.800 | 1.000 | 1.000 | 5 | 0.500 | True |
| kernel-lambda | revenue_level_next_q_last3 | W2 | full_sample | 10 | 29.8 | 37.7 | 2.0 | 0.348 | 27.7 | 0.800 | 1.000 | 1.000 | 5 | 0.500 | True |
| kernel-lambda | revenue_level_next_q_last3_ex_covid | W2 | full_sample | 10 | 29.8 | 37.7 | 2.0 | 0.348 | 23.1 | 0.800 | 0.800 | 1.000 | 5 | 0.500 | True |
| optimal-mix | mix_revenue_musd_all | W2 | full_sample | 10 | 32.9 | 38.2 | 16.6 | 0.352 | 21.8 | 0.800 | 1.000 | 0.750 | 0 | 0.000 | True |
| baselines | guide_cushion | W2 | full_sample | 10 | 31.2 | 38.9 | 17.8 | 0.359 | 19.6 | 0.800 | 0.700 | 0.750 | 1 | 0.100 | True |
| guidance-policy | print_from_guide | W2 | full_sample | 10 | 31.5 | 39.3 | 18.5 | 0.363 | 21.3 | 0.800 | 1.000 | 0.750 | 1 | 0.100 | True |
| optimal-mix | mix_revenue_musd_parsimonious | W2 | full_sample | 10 | 31.9 | 39.5 | 18.4 | 0.365 | 20.9 | 0.800 | 1.000 | 0.750 | 0 | 0.000 | True |
| kernel-lambda | revenue_level_next_q_ex_covid | W2 | full_sample | 10 | 31.4 | 40.7 | 4.5 | 0.375 | 24.1 | 0.800 | 0.900 | 1.000 | 5 | 0.500 | True |
| calibration-rail | gbm_surprise_guide | W2 | full_sample | 10 | 37.3 | 40.7 | 9.0 | 0.376 | 31.0 | 0.800 | 0.100 | 0.750 | 4 | 0.400 | True |
| calibration-rail | gbm_revenue | W2 | full_sample | 10 | 44.3 | 52.4 | -1.7 | 0.484 | 31.6 | 0.800 | 0.400 | 1.000 | 4 | 0.400 | True |
| kernel-lambda | revenue_level_next_q | W2 | full_sample | 10 | 45.4 | 57.1 | 38.0 | 0.527 | 35.0 | 0.800 | 0.900 | 1.000 | 5 | 0.500 | True |
| kernel-lambda | revenue_level_h1 | W2 | full_sample | 10 | 57.3 | 76.3 | 34.4 | 0.703 | 46.0 | 0.800 | 0.900 | 1.000 | 5 | 0.500 | True |
| kernel-lambda | revenue_level_next_q_w038 | W2 | full_sample | 10 | 74.9 | 88.0 | 62.4 | 0.812 | 51.7 | 0.800 | 1.000 | 0.750 | 5 | 0.500 | True |
| baselines | street | W2 | full_sample | 10 | 82.1 | 94.5 | -54.9 | 0.871 | 58.0 | 0.800 | 1.000 | 0.750 | 0 | 0.000 | False |
| kernel-lambda | revenue_level_next_q_w033 | W2 | full_sample | 10 | 81.0 | 96.2 | 67.5 | 0.887 | 55.7 | 0.800 | 1.000 | 0.750 | 5 | 0.500 | True |
| baselines | ar1 | W2 | full_sample | 10 | 82.8 | 99.3 | -7.6 | 0.916 | 57.0 | 0.800 | 0.600 | 1.000 | 3 | 0.300 | True |
| baselines | naive | W2 | full_sample | 10 | 91.5 | 108.4 | 4.2 | 1.000 | 62.3 | 0.800 | 0.600 | 1.000 | 1 | 0.100 | False |
| baselines | trailing4 | W2 | full_sample | 10 | 99.0 | 119.4 | 15.8 | 1.101 | 67.1 | 0.800 | 0.700 | 1.000 | 2 | 0.200 | False |
| baselines | naive_seasonal | W2 | full_sample | 10 | 324.2 | 337.8 | -324.2 | 3.115 | 265.8 | 0.800 | 0.000 | 0.250 | 1 | 0.100 | False |
| l1-reconciliation | revenue_contemporaneous | W2 | full_sample | 10 | 1,077.3 | 1,094.4 | 22.5 | 10.093 | 721.1 | 0.800 | 0.700 | 1.000 | 68 | 6.800 | False |

## target: `revenue_yoy`

| method | object | window | prior_basis | n | mae | rmse | bias | rmse_ratio_to_naive | crps | cov_nominal | cov_empirical | conformal_cov_empirical | n_params | param_obs_ratio | survives_both_windows |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| kernel-lambda | revenue_yoy_next_q | W1 | PIT | 14 | 2.6 | 3.5 | 2.5 | 0.903 | 1.9 | 0.800 | 0.786 | 0.875 | 5 | 0.357 | True |
| optimal-mix | mix_revenue_yoy_all | W1 | PIT | 14 | 2.5 | 3.5 | 1.5 | 0.909 | 2.1 | 0.800 | 1.000 | 0.875 | 0 | 0.000 | True |
| optimal-mix | mix_revenue_yoy_parsimonious | W1 | PIT | 14 | 2.6 | 3.6 | 1.5 | 0.937 | 2.1 | 0.800 | 1.000 | 0.875 | 0 | 0.000 | True |
| baselines | naive | W1 | PIT | 14 | 3.1 | 3.8 | 0.5 | 1.000 | 2.3 | 0.800 | 0.571 | 1.000 | 1 | 0.071 | False |
| baselines | ar1 | W1 | PIT | 14 | 3.8 | 4.4 | -2.2 | 1.138 | 3.0 | 0.800 | 0.286 | 0.875 | 3 | 0.214 | False |
| tracker-backlog | revenue_yoy_next_q | W1 | PIT | 112 | 4.4 | 6.2 | 1.7 | 1.630 | 3.1 | 0.800 | 0.768 | 0.868 | 2 | 0.018 | False |
| baselines | trailing4 | W1 | PIT | 14 | 6.2 | 8.8 | 3.8 | 2.297 | 5.3 | 0.800 | 0.786 | 0.875 | 2 | 0.143 | False |
| baselines | naive_seasonal | W1 | PIT | 14 | 14.1 | 14.7 | -14.1 | 3.849 | 12.5 | 0.800 | 0.000 | 0.875 | 1 | 0.071 | False |
| kernel-lambda | revenue_yoy_next_q | W1 | full_sample | 14 | 1.6 | 2.1 | 1.3 | 0.551 | 1.3 | 0.800 | 0.929 | 0.875 | 5 | 0.357 | True |
| optimal-mix | mix_revenue_yoy_all | W1 | full_sample | 14 | 2.1 | 2.6 | 1.3 | 0.691 | 1.8 | 0.800 | 1.000 | 0.875 | 0 | 0.000 | True |
| optimal-mix | mix_revenue_yoy_parsimonious | W1 | full_sample | 14 | 2.2 | 2.8 | 1.3 | 0.725 | 1.9 | 0.800 | 1.000 | 0.875 | 0 | 0.000 | True |
| baselines | ar1 | W1 | full_sample | 14 | 2.6 | 3.4 | -0.2 | 0.896 | 1.9 | 0.800 | 0.714 | 0.750 | 3 | 0.214 | True |
| baselines | naive | W1 | full_sample | 14 | 3.1 | 3.8 | 0.5 | 1.000 | 2.1 | 0.800 | 0.714 | 1.000 | 1 | 0.071 | False |
| tracker-backlog | revenue_yoy_next_q | W1 | full_sample | 112 | 3.4 | 4.7 | 1.3 | 1.231 | 2.3 | 0.800 | 0.857 | 0.840 | 2 | 0.018 | False |
| baselines | trailing4 | W1 | full_sample | 14 | 6.2 | 8.8 | 3.8 | 2.297 | 4.7 | 0.800 | 0.643 | 0.875 | 2 | 0.143 | False |
| baselines | naive_seasonal | W1 | full_sample | 14 | 14.1 | 14.7 | -14.1 | 3.849 | 11.9 | 0.800 | 0.000 | 0.875 | 1 | 0.071 | False |
| optimal-mix | mix_revenue_yoy_all | W2 | PIT | 10 | 1.6 | 2.2 | 0.3 | 0.505 | 1.7 | 0.800 | 1.000 | 1.000 | 0 | 0.000 | True |
| optimal-mix | mix_revenue_yoy_parsimonious | W2 | PIT | 10 | 1.6 | 2.2 | 0.1 | 0.520 | 1.7 | 0.800 | 1.000 | 1.000 | 0 | 0.000 | True |
| kernel-lambda | revenue_yoy_next_q | W2 | PIT | 10 | 2.4 | 3.2 | 2.3 | 0.756 | 1.8 | 0.800 | 0.800 | 1.000 | 5 | 0.500 | True |
| baselines | naive | W2 | PIT | 10 | 3.6 | 4.3 | 0.0 | 1.000 | 2.6 | 0.800 | 0.600 | 1.000 | 1 | 0.100 | False |
| baselines | ar1 | W2 | PIT | 10 | 3.8 | 4.4 | -1.5 | 1.034 | 2.9 | 0.800 | 0.400 | 1.000 | 3 | 0.300 | False |
| baselines | trailing4 | W2 | PIT | 10 | 3.8 | 4.6 | 0.6 | 1.077 | 2.8 | 0.800 | 1.000 | 0.750 | 2 | 0.200 | False |
| tracker-backlog | revenue_yoy_next_q | W2 | PIT | 80 | 3.8 | 5.7 | 0.2 | 1.331 | 2.8 | 0.800 | 0.775 | 0.824 | 2 | 0.025 | False |
| baselines | naive_seasonal | W2 | PIT | 10 | 12.5 | 13.0 | -12.5 | 3.036 | 10.4 | 0.800 | 0.000 | 0.750 | 1 | 0.100 | False |
| optimal-mix | mix_revenue_yoy_all | W2 | full_sample | 10 | 1.6 | 2.1 | 0.6 | 0.495 | 1.6 | 0.800 | 1.000 | 1.000 | 0 | 0.000 | True |
| optimal-mix | mix_revenue_yoy_parsimonious | W2 | full_sample | 10 | 1.7 | 2.2 | 0.5 | 0.510 | 1.7 | 0.800 | 1.000 | 1.000 | 0 | 0.000 | True |
| kernel-lambda | revenue_yoy_next_q | W2 | full_sample | 10 | 1.8 | 2.4 | 1.4 | 0.552 | 1.4 | 0.800 | 0.900 | 1.000 | 5 | 0.500 | True |
| baselines | ar1 | W2 | full_sample | 10 | 3.3 | 4.0 | -0.5 | 0.935 | 2.3 | 0.800 | 0.600 | 0.750 | 3 | 0.300 | True |
| baselines | naive | W2 | full_sample | 10 | 3.6 | 4.3 | 0.0 | 1.000 | 2.4 | 0.800 | 0.600 | 1.000 | 1 | 0.100 | False |
| baselines | trailing4 | W2 | full_sample | 10 | 3.8 | 4.6 | 0.6 | 1.077 | 2.6 | 0.800 | 0.700 | 0.750 | 2 | 0.200 | False |
| tracker-backlog | revenue_yoy_next_q | W2 | full_sample | 80 | 3.3 | 4.8 | 0.7 | 1.127 | 2.4 | 0.800 | 0.850 | 0.797 | 2 | 0.025 | False |
| baselines | naive_seasonal | W2 | full_sample | 10 | 12.5 | 13.0 | -12.5 | 3.036 | 10.3 | 0.800 | 0.000 | 0.750 | 1 | 0.100 | False |

## target: `take_rate_pct`

| method | object | window | prior_basis | n | mae | rmse | bias | rmse_ratio_to_naive | crps | cov_nominal | cov_empirical | conformal_cov_empirical | n_params | param_obs_ratio | survives_both_windows |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| fee-takerate | take_rate_lastyear | W1 | PIT | 14 | 0.3 | 0.3 | 0.1 |  | 0.2 | 0.800 | 0.714 | 0.875 | 2 | 0.143 | False |
| optimal-mix | mix_take_rate_pct_repaired | W1 | PIT | 14 | 0.3 | 0.3 | 0.2 |  | 0.2 | 0.800 | 0.786 | 0.875 | 0 | 0.000 | False |
| fee-takerate | take_rate_kernel | W1 | PIT | 14 | 0.3 | 0.4 | 0.3 |  | 0.2 | 0.800 | 0.643 | 0.875 | 5 | 0.357 | False |
| optimal-mix | mix_take_rate_pct_all | W1 | PIT | 14 | 0.9 | 1.4 | 0.3 |  | 0.6 | 0.800 | 1.000 | 1.000 | 0 | 0.000 | False |
| optimal-mix | mix_take_rate_pct_parsimonious | W1 | PIT | 14 | 1.1 | 1.6 | 0.3 |  | 0.7 | 0.800 | 1.000 | 1.000 | 0 | 0.000 | False |
| calibration-rail | ref_trailing4 | W1 | PIT | 14 | 2.5 | 3.2 | 0.4 |  | 1.8 | 0.800 | 0.786 | 1.000 | 2 | 0.143 | False |
| calibration-rail | ref_ar1 | W1 | PIT | 14 | 2.5 | 3.4 | -0.1 |  | 1.9 | 0.800 | 0.786 | 1.000 | 3 | 0.214 | False |
| calibration-rail | ref_naive | W1 | PIT | 14 | 4.6 | 4.6 | 0.1 |  | 2.7 | 0.800 | 1.000 | 0.875 | 1 | 0.071 | False |
| optimal-mix | mix_take_rate_pct_repaired | W1 | full_sample | 14 | 0.3 | 0.4 | 0.2 |  | 0.2 | 0.800 | 0.857 | 0.875 | 0 | 0.000 | False |
| fee-takerate | take_rate_lastyear | W1 | full_sample | 14 | 0.3 | 0.4 | 0.2 |  | 0.2 | 0.800 | 0.857 | 0.875 | 2 | 0.143 | False |
| fee-takerate | take_rate_kernel | W1 | full_sample | 14 | 0.3 | 0.4 | 0.2 |  | 0.2 | 0.800 | 0.786 | 0.750 | 5 | 0.357 | False |
| optimal-mix | mix_take_rate_pct_all | W1 | full_sample | 14 | 0.9 | 1.4 | 0.3 |  | 0.6 | 0.800 | 1.000 | 1.000 | 0 | 0.000 | False |
| optimal-mix | mix_take_rate_pct_parsimonious | W1 | full_sample | 14 | 1.1 | 1.6 | 0.4 |  | 0.7 | 0.800 | 0.929 | 1.000 | 0 | 0.000 | False |
| calibration-rail | ref_trailing4 | W1 | full_sample | 14 | 2.5 | 3.2 | 0.4 |  | 1.8 | 0.800 | 0.571 | 1.000 | 2 | 0.143 | False |
| calibration-rail | ref_ar1 | W1 | full_sample | 14 | 2.5 | 3.2 | -0.0 |  | 1.8 | 0.800 | 0.714 | 0.875 | 3 | 0.214 | False |
| calibration-rail | ref_naive | W1 | full_sample | 14 | 4.6 | 4.6 | 0.1 |  | 2.7 | 0.800 | 1.000 | 0.875 | 1 | 0.071 | False |
| optimal-mix | mix_take_rate_pct_repaired | W2 | PIT | 10 | 0.3 | 0.3 | 0.2 |  | 0.2 | 0.800 | 0.700 | 0.750 | 0 | 0.000 | False |
| fee-takerate | take_rate_lastyear | W2 | PIT | 10 | 0.3 | 0.3 | 0.1 |  | 0.2 | 0.800 | 0.600 | 0.750 | 2 | 0.200 | False |
| fee-takerate | take_rate_kernel | W2 | PIT | 10 | 0.3 | 0.4 | 0.3 |  | 0.2 | 0.800 | 0.600 | 0.750 | 5 | 0.500 | False |
| optimal-mix | mix_take_rate_pct_all | W2 | PIT | 10 | 0.5 | 0.9 | 0.4 |  | 0.4 | 0.800 | 1.000 | 1.000 | 0 | 0.000 | False |
| optimal-mix | mix_take_rate_pct_parsimonious | W2 | PIT | 10 | 0.6 | 1.0 | 0.4 |  | 0.4 | 0.800 | 1.000 | 1.000 | 0 | 0.000 | False |
| calibration-rail | ref_trailing4 | W2 | PIT | 10 | 2.4 | 3.1 | 0.6 |  | 1.8 | 0.800 | 0.800 | 1.000 | 2 | 0.200 | False |
| calibration-rail | ref_ar1 | W2 | PIT | 10 | 2.4 | 3.2 | 0.2 |  | 1.8 | 0.800 | 0.800 | 1.000 | 3 | 0.300 | False |
| calibration-rail | ref_naive | W2 | PIT | 10 | 4.5 | 4.5 | 0.1 |  | 2.6 | 0.800 | 1.000 | 1.000 | 1 | 0.100 | False |
| fee-takerate | take_rate_kernel | W2 | full_sample | 10 | 0.3 | 0.4 | 0.2 |  | 0.2 | 0.800 | 0.800 | 0.750 | 5 | 0.500 | False |
| optimal-mix | mix_take_rate_pct_repaired | W2 | full_sample | 10 | 0.3 | 0.4 | 0.3 |  | 0.2 | 0.800 | 0.800 | 0.750 | 0 | 0.000 | False |
| fee-takerate | take_rate_lastyear | W2 | full_sample | 10 | 0.3 | 0.4 | 0.3 |  | 0.2 | 0.800 | 0.800 | 0.750 | 2 | 0.200 | False |
| optimal-mix | mix_take_rate_pct_all | W2 | full_sample | 10 | 0.5 | 0.9 | 0.5 |  | 0.4 | 0.800 | 1.000 | 1.000 | 0 | 0.000 | False |
| optimal-mix | mix_take_rate_pct_parsimonious | W2 | full_sample | 10 | 0.6 | 1.0 | 0.6 |  | 0.4 | 0.800 | 0.900 | 1.000 | 0 | 0.000 | False |
| calibration-rail | ref_trailing4 | W2 | full_sample | 10 | 2.4 | 3.1 | 0.6 |  | 1.7 | 0.800 | 0.600 | 1.000 | 2 | 0.200 | False |
| calibration-rail | ref_ar1 | W2 | full_sample | 10 | 2.4 | 3.1 | 0.1 |  | 1.7 | 0.800 | 0.800 | 1.000 | 3 | 0.300 | False |
| calibration-rail | ref_naive | W2 | full_sample | 10 | 4.5 | 4.5 | 0.1 |  | 2.6 | 0.800 | 1.000 | 1.000 | 1 | 0.100 | False |

## Attainable conformal coverage

At `n_cal=6`, `alpha=0.2`: `k = ceil(7 x 0.8) = 6`, so `qhat` is the **maximum** of six residuals and attainable coverage lies in [0.857, 1.000] = [85.7%, 100.0%]. There is no 80% guarantee at this sample size. Full grid: `conformal_attainable_grid.csv`.
