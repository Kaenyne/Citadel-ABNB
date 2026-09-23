**Audit of Citadel-ABNB PRs 39-44 — 11 September 2026**

The highest-priority error is PR40's inference that management's “over 200 basis points” disclosure pins a 40-50% product allocation and therefore a Q4 nights forecast of 8.0-8.2%. The disclosure is a lower bound and does not identify that range. Other confirmed errors affect historical comparisons, robustness statistics, coverage statements, the proposed September refresh, and ADR uncertainty presentation. Several headline estimates change little in the targeted corrections; their stated evidential strength needs more substantial revision.

The audit used local evidence copies and reproduction scripts. Production code, forecasts, branches and GitHub discussions were not modified during the audit. This publication preserves the findings and reproduction checks against the exact PR heads below. P1 means resolve before relying on the affected conclusion; P2 means a confirmed error requiring correction in the relevant analysis or refresh.

| PR | Scope | Audited head |
|---|---|---|
| [39](https://github.com/Kaenyne/Citadel-ABNB/pull/39) | RNPL handoff, materiality, original bridge and calendar pilot | `5fce83b337fd528801f6547480745308084c09b3` |
| [40](https://github.com/Kaenyne/Citadel-ABNB/pull/40) | Calendar expansion, FX/consumer regional models, RNPL ledger/cohort scenarios | `0324cace7172db757280988888f64f0d27c877f7` |
| [41](https://github.com/Kaenyne/Citadel-ABNB/pull/41) | Reviews, calendars, external indicators and first ADR card | `5a590cedb42928666c580e06974947c301e2bbab` |
| [42](https://github.com/Kaenyne/Citadel-ABNB/pull/42) | Team explainer | `316815dc275e9186421e46b00d327e6e571ee9fc` |
| [43](https://github.com/Kaenyne/Citadel-ABNB/pull/43) | Tokyo acquisition fix and reviews refresh | `ad29bba9e34a88ee7dddaa74fd442a57d6251732` |
| [44](https://github.com/Kaenyne/Citadel-ABNB/pull/44) | Measured mix proxies, residual tests and ADR card v2 | `573b3770e80ef4418bcc8c75a4cf0dcf906fc8f9` |

All six were merged and had no review/discussion comments when queried. Review covered analytical scripts, relevant committed inputs/outputs and handoff claims. The large raw calendar/review archives were not downloaded and rebuilt in full. Consequently this is not a certification of every raw observation or every external disclosure. It separates executed reproductions from code/provenance findings and already disclosed limitations.

**1. [P1] Do not turn a disclosed lower bound into an upper bound — PR40, propagated into PR42.**

[D1_rnpl_cohort_scenarios.py:614-623](https://github.com/Kaenyne/Citadel-ABNB/blob/0324cace7172db757280988888f64f0d27c877f7/analysis/src/overnight2/D1_rnpl_cohort_scenarios.py#L614) marks 70% and 100% ex-North-America fee/cancellation allocations inconsistent with “over 200 basis points,” because they imply contributions of 2.58 and 3.10 points. Both satisfy a greater-than-2.0 statement. Using the code's other fixed assumptions, the disclosure implies only an allocation above approximately 37.1%, not a cap at 50%.

The selected 40-50% scenarios yield Q4 growth of 8.20%/8.03%. The rejected scenarios yield 7.68%/7.15%, and the quoted lower bound does not reject them. These alternative numbers are conditional examples, not corrected forecasts. Remove the “pinned” designation, retain the full assumption sensitivity, and obtain independent allocation evidence before choosing the base case. Reproduced directly by the original `bundle_crosscheck()` and `exna_4q26_gap()` functions; see `root_reproduction_results.json`.

**2. [P2] Align NTTO growth by calendar quarter before fitting — PR41.**

[G2_external_backtests.py:119-124](https://github.com/Kaenyne/Citadel-ABNB/blob/5a590cedb42928666c580e06974947c301e2bbab/analysis/src/q3nowcast/G2_external_backtests.py#L119) uses a positional four-row lag after aggregating a sparse quarterly series. The raw NTTO table lacks January-September 2022. January 2023 Western Europe arrivals are consequently compared with April 2021, producing the published +1,561.9%, rather than a year-over-year comparison. Overseas Q4 2022 full-quarter growth is 84.6%, not 596.3%.

The original code reproduces committed feature columns to within 1e-10. Reindexing to complete calendar quarters changes the overseas first-month specification's RMSE ratio versus naive from 0.743 to 0.895; scored quarters fall from ten to seven because missing year-ago inputs are now correctly missing. On those identical seven evaluation quarters the comparison is 0.729 versus 0.895, so this is not merely an evaluation-sample effect. The total-arrivals version changes from 0.724 to 0.965. The current ensemble median changes only from 9.232% to 9.312%. Recover the missing source history and regenerate the training features, survivor selection and narrative. Evidence: `external/ntto_backtest_comparison.csv` and `external/reproduction_summary.json`.

**3. [P2] Qualify the reviews backtest as retrospective, not a demonstrated historical live nowcast — PR42.**

[Explainer:31](https://github.com/Kaenyne/Citadel-ABNB/blob/316815dc275e9186421e46b00d327e6e571ee9fc/docs/2026-09-11_q3-nowcast-explainer.md#L31) describes fitting with only prior-quarter data and presents the 0.68 ratio as the case for the pitch exhibit. The coefficient fit is chronological, but the predictors are reconstructed from later 2025/2026 listing snapshots and use completed historical quarters. The live Q3 input is a partial-quarter window. [E5:154](https://github.com/Kaenyne/Citadel-ABNB/blob/5a590cedb42928666c580e06974947c301e2bbab/analysis/src/q3nowcast/E5_backtest.py#L154) explicitly sets `point_in_time=False`.

The 0.68 result is not shown to be numerically wrong by this finding. It demonstrates a narrower retrospective relationship than a forecast using only data actually available at each past decision date. Carry that qualification into the explainer/deck, and separately evaluate historical as-of vintages with the same partial-quarter cutoff. This is a documentation/validation finding; the source code does disclose the limitation.

**4. [P2] Correct the share of Q3 actually observed — PR41/42, updated by PR43.**

[Explainer:33](https://github.com/Kaenyne/Citadel-ABNB/blob/316815dc275e9186421e46b00d327e6e571ee9fc/docs/2026-09-11_q3-nowcast-explainer.md#L33) states 60-65% of the quarter is covered. The committed vintage-matched Q3 windows span 19-47 of 92 days: median 40 days, or 43.5%, and 41.6% using prior-review weights. PR43 raises the market median to 44.6%. Even the longest within-vintage window ends August 17, only 52.2% of Q3.

Correct the temporal coverage and distinguish it from the 88-90% coverage of the panel's prior-year review base. The present wording understates the part of Q3 still unseen. These calculations describe the panel's window lengths, not a measured fraction of company-wide bookings. Evidence: `reviews/reproduction_results.json`.

**5. [P2] Cap August windows at month-end during the September refresh — PR41, inherited by PR43.**

[E6_nowcast.py:145](https://github.com/Kaenyne/Citadel-ABNB/blob/5a590cedb42928666c580e06974947c301e2bbab/analysis/src/q3nowcast/E6_nowcast.py#L145) and [line 199](https://github.com/Kaenyne/Citadel-ABNB/blob/5a590cedb42928666c580e06974947c301e2bbab/analysis/src/q3nowcast/E6_nowcast.py#L199) end the August row at snapshot date minus 14 days without capping it at August 31. A September 30 snapshot therefore labels August 1-September 16 as August.

Executing the unchanged function on synthetic counts with flat August activity and doubled September activity reports false August growth of +34.04% instead of 0%. This affects the explicitly recommended September rerun, not the current August-only result. Bound each monthly window independently and keep a separately labeled Q3-to-date window. Evidence: `reviews/reproduce_reviews_findings.py`.

**6. [P2] Include I3 and I5 in the ADR refresh dependency chain — PR44.**

[ADR synthesis:42](https://github.com/Kaenyne/Citadel-ABNB/blob/573b3770e80ef4418bcc8c75a4cf0dcf906fc8f9/docs/adrq3/SYNTHESIS.md#L42) recommends rerunning E/I1/I1b and then J3. J3 instead reads `I_mix_terms_3q26.csv`, which I5 creates. I3 must first translate the updated regional review split into the geographic-mix input. The documented sequence can therefore run successfully while retaining the old mix terms.

Provide one explicit orchestrator, rebuild I3 and I5 before J3, and verify input observation dates. Update LOS stages too when calendar inputs change. Dependency trace: [I5:82](https://github.com/Kaenyne/Citadel-ABNB/blob/573b3770e80ef4418bcc8c75a4cf0dcf906fc8f9/analysis/src/adrq3/I5_summary.py#L82), [J3:119](https://github.com/Kaenyne/Citadel-ABNB/blob/573b3770e80ef4418bcc8c75a4cf0dcf906fc8f9/analysis/src/adrq3/J3_residual_nowcast_card_v2.py#L119). This was established from the dependency graph, without acquiring future snapshots.

**7. [P2] Freeze the calendar captures used by the RNPL studies — PR39/40 after PR41.**

[PR40 A2:104-114](https://github.com/Kaenyne/Citadel-ABNB/blob/0324cace7172db757280988888f64f0d27c877f7/analysis/src/overnight2/A2_cross_market_analysis.py#L104) assigns fixed 2025/26 research-window labels to the first four consecutive capture pairs by position. A1 discovers every file in the shared raw store. PR41 adds 164 historical captures; Austin now has 20, with the first four pairs covering May-September 2024. Rebuilding A1 with overwrite makes A2 analyze those 2024 intervals under the 2025/26 labels. Of 32 previously complete markets, 29 now have more than five captures.

PR39's [pilot:124-126](https://github.com/Kaenyne/Citadel-ABNB/blob/5fce83b337fd528801f6547480745308084c09b3/analysis/src/rnpl_calendar_pilot.py#L124) fails explicitly because it requires exactly five globbed files; PR41 provenance records Austin 20, Rome 22 and Sydney 6. Select the original dated captures from a frozen manifest, validate intervals, and rebuild the stable cohort using that exact selection. The committed PR40 historical aggregates are not demonstrated wrong; their rebuild becomes unstable after the later acquisition. Provenance checks and a synthetic extra-file failure reproduce the trigger; the full raw corpus was not rerun.

**8. [P2] Preserve model identity in reviews robustness tests — PR41/43.**

[E5:162-164](https://github.com/Kaenyne/Citadel-ABNB/blob/5a590cedb42928666c580e06974947c301e2bbab/analysis/src/q3nowcast/E5_backtest.py#L162) omits the level/first-difference transform from saved forecast-error paths. [The robustness grouping:275](https://github.com/Kaenyne/Citadel-ABNB/blob/5a590cedb42928666c580e06974947c301e2bbab/analysis/src/q3nowcast/E5_backtest.py#L275) consequently pools different models and drops one row rather than one quarter per model.

There are 63 collided groups, including 31 for nights. For EMEA/all-reviews/equal-weight/lag-one, the pooled maximum jackknife ratio is 0.949, while separate models reach 1.117 and 1.019 and fail the robustness criterion. Recovering separate paths matches all 463 original source RMSE ratios to floating-point precision. Include the transform in every key and assert one error per model/quarter. The headline lag-zero all-reviews 0.68 result is unaffected by this particular bug.

**9. [P2] Refit the original ADR benchmark within each forecast window — PR41.**

[H1_adr_card.py:258-263](https://github.com/Kaenyne/Citadel-ABNB/blob/5a590cedb42928666c580e06974947c301e2bbab/analysis/src/q3nowcast/H1_adr_card.py#L258) fits AR(1) once using the full history, including future target outcomes. Fitting strictly before each target quarter raises its RMSE from 0.804 to 1.058 percentage points on the same nine observations. Recompute this benchmark and its comparison text. The component model still loses to the simple last-quarter benchmark. PR44's J3 already performs the AR(1) refit correctly; that does not update the original H outputs. Evidence: `adr/audit_evidence.json`.

**10. [P2] Preserve the asymmetric ADR downside when constructing the band — PR44.**

[J3:187-193](https://github.com/Kaenyne/Citadel-ABNB/blob/573b3770e80ef4418bcc8c75a4cf0dcf906fc8f9/analysis/src/adrq3/J3_residual_nowcast_card_v2.py#L187) uses half the low-to-high range symmetrically around a point near the top of that range. The main residual is 2.398/4.615/4.849 percentage points for low/point/high. Its downside distance is 2.217 points, versus only 0.234 points of upside.

The resulting headline Q3 ADR band of +1.70% to +4.35% excludes its own residual mean-reversion-only scenario: +0.81% reported ADR, $172.68 ADR, about $557 million less Q3 GBV with other assumptions fixed. That scenario is disclosed in the detailed note, but the headline band's centering hides the asymmetry. Publish the explicit scenario table or preserve separate downside/upside distances. These are assumed scenario bounds, not estimated confidence intervals; distinct sources do not establish independence.

**11. [P2] Correct the direction of the proposed cancellation diagnostic — PR40.**

[D1:641-646](https://github.com/Kaenyne/Citadel-ABNB/blob/0324cace7172db757280988888f64f0d27c877f7/analysis/src/overnight2/D1_rnpl_cohort_scenarios.py#L641) treats a widening GBV-growth-minus-nights-growth gap as support for cancellations of higher-ADR RNPL nights, claiming their removal reduces GBV proportionally less. Holding other components fixed, removing above-average-ADR nights reduces GBV proportionally more and lowers blended ADR.

Counterexample: 100 nights/$10,000 GBV, then cancel ten nights priced at $125. Nights fall 10%, GBV falls 12.5%, and the growth gap falls by 2.5 points. Other pricing/mix/FX changes could offset that effect, but the gap's sign is not the stated cancellation signature. Rewrite the scoring rule using an explicit nights-and-GBV bridge; do not interpret the existing sign as causal evidence. Reproduced in `root_reproduction_results.json`.

**12. [P2] Parse the full year in the FX historical quarter keys — PR40.**

[B3:44-45](https://github.com/Kaenyne/Citadel-ABNB/blob/0324cace7172db757280988888f64f0d27c877f7/analysis/src/overnight2/B3_mix_tests.py#L44) uses `q[3:]` for labels such as `1Q19`, reading only the final digit. It sorts 2019 after 2026. B2's sort key has the same defect. The cross-border share calculation then compares 1Q19 with 2Q23, 2Q19 with 3Q23, and so on when applying its four-row lag.

Use a validated quarter parser and calendar-key joins/reindexing for lags. The affected cross-border-share history includes future-period comparisons. The 2024-26 BEA gap correlation and pooled regional elasticity are not overturned by this specific defect because those target samples do not include 2019. Evidence: `pr40_crossborder_wrong_years.csv`.

**13. [P2] Do not infer zero repricing from a zero median — PR44.**

[ADR synthesis:29](https://github.com/Kaenyne/Citadel-ABNB/blob/573b3770e80ef4418bcc8c75a4cf0dcf906fc8f9/docs/adrq3/SYNTHESIS.md#L29) says hosts do not reprice existing dates and ADR growth comes from composition/new listings. The matched-panel mean prices change +2.62% in EMEA and -1.19% in North America even though median changes are zero; the revision diagnostic finds changes exceeding 0.5% on 6.74% of matched observations.

Those fixed listing/date mean changes require within-panel price changes. A zero median cannot establish zero contribution to an average, and listed future prices do not by themselves attribute realized ADR growth. Retain the valid finding that current calendar prices are unavailable and this proxy has not validated a forecast; remove the unsupported mechanism claim.

**14. [P2] Replace author-specific input/output paths with explicit repository/data roots — PR40/41/43/44.**

Examples are [B1:30-31](https://github.com/Kaenyne/Citadel-ABNB/blob/0324cace7172db757280988888f64f0d27c877f7/analysis/src/overnight2/B1_fx_relative_strength.py#L30), [G2:36/52](https://github.com/Kaenyne/Citadel-ABNB/blob/5a590cedb42928666c580e06974947c301e2bbab/analysis/src/q3nowcast/G2_external_backtests.py#L36), and [J3:112](https://github.com/Kaenyne/Citadel-ABNB/blob/573b3770e80ef4418bcc8c75a4cf0dcf906fc8f9/analysis/src/adrq3/J3_residual_nowcast_card_v2.py#L112). They read `C:\Users\krish\citadel-abnb` or another personal worktree even for committed processed inputs. Calling the original G2 target loader on this checkout reproduces `FileNotFoundError`.

Resolve committed data relative to the repository and accept a separate configured raw-data root. Document or implement acquisition of required external-price raw inputs. Add a clean-checkout smoke test and freshness checks. Missing raw vendor archives should be a distinct acquisition status, not confused with missing committed files at a personal path.

Two additional, smaller corrections were reproduced:

- [E6:309](https://github.com/Kaenyne/Citadel-ABNB/blob/5a590cedb42928666c580e06974947c301e2bbab/analysis/src/q3nowcast/E6_nowcast.py#L309) uses the equal-weighted historical partial-quarter gap for the median variant while labeling it measured. Its own median gap changes the forecast from 9.203% to 9.653% and band from 1.519 to 1.605 points. The seven-row average changes only approximately 0.064 points; this does not overturn the headline.
- [G3:172-184](https://github.com/Kaenyne/Citadel-ABNB/blob/5a590cedb42928666c580e06974947c301e2bbab/analysis/src/q3nowcast/G3_rank_sources.py#L172) gives July-only data the July-and-August coverage score, and lexicographically interprets a Q2 observation released in September as September coverage. Parse observation dates separately from release dates before ranking sources.

Several checks passed and limit how broadly to interpret the findings:

- PR39's ten materiality thresholds and 48 exposure/rebooking scenarios regenerate. Its saved pilot report regenerates, and all 15 source URL/size comparisons pass. Pilot synthetic matching and run-boundary checks pass. No separate hidden materiality arithmetic error was established.
- PR40's no-excess-cancellation reference engine reproduces all supplied quarterly targets to within 2.9e-14 million nights. That verifies the arithmetic, not assumed exposures, causal attribution or lead-time identification.
- PR40 A1 and PR41 F1 synthetic tests pass. Their explicit distinction between calendar blocks and bookings was not treated as an undisclosed bug.
- PR43's Tokyo fix does not show a new material standalone numerical regression in the checks performed; it inherits E5/E6 issues. The stale missing-August-batch premise was corrected in its documentation.
- PR44's point ADR/GBV arithmetic reconciles. J3 explicitly discloses its realized target-quarter mix backtest as an upper bound; that is not an undisclosed live forecast test. The admitted failure to beat naive, unobserved residual, small samples and review/LOS proxy limitations were not themselves reported as new code defects.

The audit scripts run without downloading raw archives:

```text
python outputs/pr_39_44_audit/reproduce_root_findings.py
python outputs/pr_39_44_audit/reviews/reproduce_reviews_findings.py
python outputs/pr_39_44_audit/external/reproduce.py
python outputs/pr_39_44_audit/adr/reproduce_adr_findings.py
python outputs/pr_39_44_audit/39/check_pr39.py
```

They require the saved evidence files beside them and, where applicable, pandas, numpy and scipy. Detailed component reports and machine-readable results are in `reviews/`, `external/`, `adr/`, and `39/`. A complete fresh-vintage raw-data rebuild remains necessary after production fixes before replacing the team's estimates.
