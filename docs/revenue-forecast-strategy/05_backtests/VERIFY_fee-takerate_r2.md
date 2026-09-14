# VERIFY fee-takerate — round 2

**Verdict: PASS (safe to score and quote, with the caveats already disclosed by the implementer).**

## 1. Rerun

```
cd ".../Citadel-ABNB"
/Users/theomachado/.venvs/citadel-abnb/bin/python analysis/src/forecast_methods/fee_takerate/run.py
```
Exit code 0. Wall time ~2s. Ran three times total (once by me, then twice more to check A10
determinism); identical stdout each time. All 20 files in
`data/processed/forecast_methods/fee_takerate/` and all 3 registry files were byte-identical
to a copy of the prior outputs taken before the rerun (diff -q on every file: no output, i.e.
no differences). This confirms FIX 1's central claim: 06c and 06d are now genuinely rebuilt by
`run.py` and reproduce to float precision.

## 2. Registry format check

Loaded each of the three registered objects separately with the harness's own
`load_registry` + `validate_registry_frame` (dropping the bookkeeping columns
`format_version`/`_source_file` that `load_registry` adds, which is expected — those
columns are not part of `REGISTRY_COLUMNS` and validating a multi-object frame at once
correctly errors on the harness's "one file = one (method,object)" rule; that is a usage
artifact of my check, not a package defect). All three files validate cleanly:
`take_rate_kernel` 50 rows, `take_rate_lastyear` 50 rows, `take_rate_mechanism` 6 rows —
matching the reported window split (W1 28/28, W2 20/20, LIVE 2/2 across the two backtest
objects; mechanism is 6 rows all LIVE 2026Q3). No RegistryError.

Confirmed the LIVE-window harness-change-request is real, not a misreading of the README:
`windows.py`'s `LIVE_TARGETS` is derived only from `GUIDE_EVENTS_ALL`, which contains exactly
one entry with quarter >= 2026Q3 (the 2026-08-06 guide targeting 2026Q3 itself). So although
the README's prose says "LIVE requires 2026Q3 or later," `window_of_target()` for 2026Q4 and
beyond returns no windows including LIVE, and `strict_windows` validation genuinely rejects
those rows. The implementer's workaround (registering only the 6 legal 2026Q3 rows and
publishing the full 24-quarter path locally in `07d_take_rate_mechanism_all_quarters.csv`) is
the correct response, not an invented excuse.

Confirmed `baselines__naive.csv` and `baselines__naive_seasonal.csv` in the shared registry
carry targets `{gbv_musd, nights_m, revenue_musd, revenue_yoy}` only — no `take_rate_pct` row
in either file. The "no denominator, not a flattering ratio" claim and the A17 documentary
test are accurate, not fabricated.

## 3. Leakage audit

- No Street/consensus dependency anywhere in this package (no `04_consensus_at_print` or
  `16_consensus_at_print_merged` reference in `run.py`) — the mechanism this package models
  (fee schedule, migrated share, printed take rate) never touches vintage-stamped consensus,
  so the "4/11-Sep-2026 consensus used as historical Street" failure mode does not apply here.
- Backtest stage (e): for target quarter q at guide date gd, `history_as_of(gd, ...,
  include_same_day=True)` is used to build both the PIT lambda table and the observed-drift
  window; rows without a printed `revenue_musd` are dropped before use, so the target
  quarter's own actual is never in the training set. The kernel's `base = w1*GBV[q-1] +
  w2*GBV[q-2]` uses q-1 and q-2 actuals — q-1 is legitimately available same-day (the q-1
  print and the q guide are issued together on the same guide date, which is exactly the
  `include_same_day=True` case the harness intends), q-2 was printed a full quarter earlier.
  No leakage found.
- theta / repricing panel (`12_reprice_summary.csv`) is a cross-sectional Inside-Airbnb
  structural estimate, not a per-quarter forecast feature keyed to a vintage date — point-in-time
  rules do not bind on it the way they do on GBV/consensus history.
- `06_fee_timeline.csv` genuinely has no row after 2026-08 and no 15-Sep/13-Oct-2026 entries
  (checked directly) — A8 and the "explicit dated assumption" framing are accurate.
- No use of the regional panel's `basis == 'derived'` rows anywhere in this package (it isn't
  used at all) — the exclusion rule is inapplicable here, not silently violated.
- No letter-rounded integers scored as points that I could find; A9's y/y deltas and the
  regression in A10 use the panel's `take_rate_pct` column (a computed ratio, not a
  letter-rounded guide number).

No leakage found.

## 4. Number check (nine numbers recomputed independently from the CSVs, not just re-read)

| # | claim | recomputed | match |
|---|---|---|---|
| 1 | A9: 2Q26 vs 2Q25 = +9 bp | 13.26 − 13.17 = +9.0 bp | exact |
| 2 | A9: 1Q26 vs 1Q25 = −10 bp | 9.17 − 9.27 = −10.0 bp | exact |
| 3 | A9: 3Q25 vs 3Q24 = −69 bp | 17.88 − 18.57 = −69.0 bp | exact |
| 4 | A9: 4Q25 vs 4Q24 = −47 bp | 13.62 − 14.09 = −47.0 bp | exact |
| 5 | A2: theta range/median | recomputed from `01_theta_reproduction.csv`: n=402, min 0.83333, max 1.40700, median 0.89632 | exact |
| 6 | A5 full-file: mean share_gt_10 0.2149 vs share_lt_m10 0.2025, 178/420 more-cutter rows | recomputed: 0.21487 vs 0.20250, 178/420 | exact |
| 7 | A5 Austin: 0.1919 raised / 0.2119 cut, 12/20 | recomputed: n=20, 0.19193 / 0.21194, 12/20 | exact |
| 8 | 06d bias W1 −0.0143, W2 +0.0860 (forecast−actual) | read directly from rebuilt `06d_seasonal_naive_benchmark.csv`: −0.014286, +0.086000 | exact |
| 9 | A10: slope −105.7 bp, se 448.5, t −0.24, perm p 0.7295→0.730 | read from rebuilt `04b_takerate_regression.csv`: −105.674, 448.459, −0.2356, 0.7295; reproduced identically on two further consecutive runs | exact |

No mismatches found.

## 5. Acceptance tests

17 tests run; 16 pass, A5 fails as a **deliberate, documented** failure (verified above — the
claim genuinely fails on the full 420-row file and genuinely holds only on the 20-row Austin
subsample). The implementer's own disclosure that A11, A13, A14, A15 and A17 are documentary
(pass a hard-coded `True`, not an independent boolean gate) is confirmed by reading the code —
each of those five `check(...)` calls is literally `check("A1x ...", True, ...)`. This does not
make their reported numbers untrustworthy (I independently recomputed several and they match to
full precision); it means they are not falsifiable tests, and the implementer is right to flag
that so 16/17 is not misread as 16 independently-confirmed hypotheses. The genuine boolean gates
(A1–A10, A12, A16) all evaluate real conditions in code, not hard-coded literals.

## 6. Honesty of interpretation

The note's central claims are all supported by what actually ran:
- theta is correctly characterized as unidentified/unmeasured for the mandatory cohort, with
  the Austin-only provenance and the 13.8-vs-14.79 normalization issue (Finding 1) stated
  plainly rather than smoothed over.
- The backtest is reported as a clean negative (neither object beats seasonal-naive on either
  window, `survives_both_windows` False on all 8 rows) — this is not spun as a win anywhere,
  and the growth-naive ratios (0.07–0.09) that would look flattering are explicitly labeled an
  artifact and not used for the headline claim.
- The fiat de-gross-up dimensional-error (Finding 2) is escalated rather than silently patched;
  both forms are kept in code with `gbv_consistent` as default, and the note says a ruling is
  still needed.
- The 4Q26/FY27 range endpoints are named explicitly per FIX 4, and I confirm those two named
  numbers (3,200.0/3,141.4 no-fee-step, 3,218.2/3,159.4 central-half) appear in
  `07b_live_4q26_fee_step.csv`/`07c_live_fy27_fee_contribution.csv` and match the note.
- The unreconciled driver-model perfect-foresight figure (+0.53%/1.97 vs. reproduced
  +0.97%/2.54) is flagged rather than forced to match.

I found nothing overstated and nothing quietly walked back between round 1's material claims
and round 2's rebuild. The one substantive residual risk for the memo team is non-technical:
theta and the 15-Sep/13-Oct deadlines remain unsourced assumptions, and the fiat/gbv-consistent
ADR equation still needs an explicit ruling — both already flagged prominently by the
implementer and correctly kept open rather than resolved by fiat.

## Caveats to carry into scoring (none block a pass)

1. Neither `take_rate_kernel` nor `take_rate_lastyear` beats the seasonal-naive benchmark on
   either window — do not quote either as a forecasting win; the package's own conclusion
   (take rate is an output, not a lever) is the correct read of its own backtest.
2. `harness/scoreboard.csv` will show NaN ratios for every fee-takerate row until a
   `take_rate_pct` baseline is registered in the shared harness — a real, verified harness gap,
   not a package defect. Downstream consumers must read this package's local `06c` scorecard.
3. theta for the mandatory cohort remains unmeasured; every number that depends on it is
   correctly carried as a range, not a point.
4. The fiat vs. gbv-consistent ADR de-gross-up equation needs a ruling before the memo; the
   package defaults to the (verified) dimensionally-correct gbv_consistent form.
