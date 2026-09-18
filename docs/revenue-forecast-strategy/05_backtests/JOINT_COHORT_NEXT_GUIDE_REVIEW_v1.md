# Joint versus fixed next-guide snapshot — independent review

15 September 2026. Reviewer: chart_auditor. Bounded continuation under `WORKBOARD_JOINT_COHORT_NEXT_GUIDE_v1.md`; no new optimization, feature search or predictive race by the reviewer.

**PASS for the directly comparable Q4 2026 research snapshot.** Both models use the 15 September cutoff, the same forecast Q3 GBV and the same trailing-eight mean cushion. The joint fit uses all 20 eligible prior quarters, not the W1-only retrospective subset. The prior forecast-promotion FAIL and physical-cohort measurement UNAVAILABLE verdicts remain unchanged.

| USD millions unless stated | Joint model | Fixed lag model |
|---|---:|---:|
| Q4 2026 revenue forecast | 3,244.389252 | 3,219.235470 |
| Q4 2026 guide midpoint forecast | **3,185.247392** | **3,160.552138** |
| Q4 seasonal conversion coefficient | 12.681513% | 12.040367% |
| Training count shown | 20 complete quarters | 5 Q4 observations |
| Shared arithmetic mean cushion | 1.856743% | 1.856743% |

The joint guide is $24.695254M, or 0.781359%, above the fixed forecast. This is a difference between two models, not a measured edge against Street guidance expectations.

The calculation date is 15 September 2026; the latest company data in both calculations were published on 6 August 2026, through Q2. Q2 GBV of $27,200M is reported. Q3 GBV of $26,505.531915M and Q4 GBV of $23,611.914894M are forecasts, carrying the latest reported GBV year-on-year growth of 15.744681%. The fixed model uses forecast Q3 and reported Q2; its weight on forecast Q4 is zero. The joint model uses both projected quarters.

Let G4, G3 and G2 denote those Q4, Q3 and Q2 GBV inputs. The independent calculation reproduces:

`fixed revenue = 0.1204036694 × [(2/3) G3 + (1/3) G2]`

`joint revenue = 0.1268151334 × [0.3589564470 G4 + 0.4729102396 G3 + 0.1681333135 G2]`

Both guide forecasts divide revenue by `1.0185674306`. The candidate's fitted lag3/4 group weight is zero at this particular fit. That is a fitted exposure coefficient, not evidence that older bookings contribute no physical fee revenue. Likewise, its weight coefficients are not observed backward booking-cohort shares.

## What was independently checked

The new adapter imports the accepted core only after checking its exact hash. Source inspection confirms it calls the unchanged `features(known, [3,4])` and `fit_shape(train)` without a W1/W2 date filter. Saved training rows match all eligible quarters from 2021Q3 through 2026Q2, five observations per season. The reviewer independently recomputed every historical exposure and all four seasonal scales using the supplied fitted shape; the optimizer was not rerun by the reviewer. The fixed Q4 scale uses the five Q4 observations from 2021 through 2025. The different displayed training counts describe those different fitted objects, not different current information cutoffs.

All source/output hashes, GBV status labels, shared projected inputs, historical cushion observations and availability dates, revenue/guide point arithmetic, dollar contributions, backward conditional shares and effective forward rates reconcile. No predictive interval was calculated; historical RMSE and earlier near-fit ranges were not presented as next-event probability bands.

**117 independent snapshot checks passed**, exit 0, with no candidate-function imports. Expected source inputs and the fixed forecast were independently recorded before inspecting the new joint output in `review_v1/next_guide_inputs_v1.json`. Exact command from the worktree root:

```powershell
& 'C:/Users/wille/Desktop/Citadel - ABNB/.venv/Scripts/python.exe' -B analysis/src/forecast_methods/gbv_joint_cohort_v1/review_v1/next_guide_check.py --source data/processed/forecast_methods/gbv_joint_cohort_v1/next_guide_v1/results_v1 --out data/processed/forecast_methods/gbv_joint_cohort_v1/review_v1/next_guide_v1
```

Use a new output directory for a repeat. The receipt is `review_v1/next_guide_v1/receipt.json`; it binds snapshot manifest SHA256 `3a6682753c2a14de6dde51c2f84386c4759a6fa3cfb5e8998f463d35235e8b18` and adapter SHA256 `213a65ab80e4297e0d9508a37793cacbd928ebac754592c2484f6d517ceb3efe`. The accepted underlying core remains `6f395b2956762f179701e78f4c6743ba523da55e45cb7c9f742a2151aa2495af`.

## Prepared research registration

**20 separate stage checks passed for two LIVE rows** in `control_v1/next_guide_prepare_v1/prepared_registry/`; receipt `review_v1/next_guide_registry_v1.json`. Points, September 15 vintage, August 6 underlying availability, Q4 target, one-quarter calendar horizon, PIT basis and parameter/training counts match. The joint guide records eight parameters and 20 complete training quarters. The fixed guide records five parameters for its model-wide four seasonal scales plus cushion, while its target scale uses five same-season observations; this basis is explicit in the source metadata. Both q50 values are point-only format placeholders, with no calibrated bands or Street edge asserted. The parent may register these reviewed research snapshots and owns both scorer runs; this review does not promote either model.

## RESUME

The bounded next-guide check is complete. Use the $3,185.25M versus $3,160.55M comparison to explain how the two frozen predictors differ under shared inputs. Keep the calculation cutoff distinct from the latest company publication, identify Q3/Q4 GBV as forecasts, and preserve the existing failed robustness verdict. The result establishes neither a physical booking-cohort split, an RNPL effect, a same-date Street advantage nor a stock-return forecast. No further model testing is required for this clarification.
