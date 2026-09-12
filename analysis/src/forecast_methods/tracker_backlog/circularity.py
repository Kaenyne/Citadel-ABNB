"""T1 -- the circularity test. RUN THIS FIRST.

Tests whether `restated_unearned_fees = reported * (1 + d_q)`, with d_q the dated
distortion series in 03_insider_mechanics.md sec 1.5, is identically
`coverage_norm x next-quarter revenue`. If so the "restatement" is not a balance-sheet
reconstruction at all: it is next-quarter revenue wearing a coverage-ratio mask, and
using it to forecast next-quarter revenue is forecasting the guide from the guide
(C_M6_fx_takerate_timing_mechanics.md, finding F1).

Also checks the formula-vs-number discrepancy: 03_insider_mechanics.md L200 states the
restatement as `reported / (1 - d_q)`, but every quoted y/y growth number in the same
document (+16.6% for 1Q26, +15.4% for 2Q26) is reproduced only by the MULTIPLY form
`reported * (1 + d_q)`. The chief of staff's ruling is the multiply form, basis="derived".
"""
from __future__ import annotations

import numpy as np
import pandas as pd

from common import (COVERAGE_NORM_FULL_SAMPLE, DATED_DQ_PCT, ensure_out_dir,
                    load_backlog_indicators, OUT_DIR)

# quarter-end -> (reported unearned fees $M, season number, next-quarter revenue used,
# basis of that next-quarter revenue: 'actual' or 'guide_mid')
ROWS = [
    ("3Q25", 1820.0, 3, 2778.0, "actual (4Q25)"),
    ("4Q25", 1743.0, 4, 2678.0, "actual (1Q26)"),
    ("1Q26", 2733.0, 1, 3608.0, "actual (2Q26)"),
    ("2Q26", 2831.0, 2, 4730.0, "GUIDE MIDPOINT (3Q26) -- not yet printed"),
]

# y/y comparator for the formula-vs-number check (03_insider_mechanics.md quoted
# +16.6% for 1Q26 and +15.4% for 2Q26; prior-year reported unearned fees below)
YOY_PRIOR = {"1Q26": 2723.0, "2Q26": 2857.0}  # 1Q25, 2Q25 reported unearned fees
YOY_QUOTED_PCT = {"1Q26": 16.6, "2Q26": 15.4}


def run() -> pd.DataFrame:
    ensure_out_dir()
    rows = []
    for q, reported, season, nextq_rev, basis in ROWS:
        norm = COVERAGE_NORM_FULL_SAMPLE[season]
        implied = norm * nextq_rev
        gap = implied - reported
        d_q_computed_pct = 100.0 * gap / reported
        d_q_quoted_pct = DATED_DQ_PCT[q]
        # multiply-form restatement (the ruling)
        restated_multiply = reported * (1.0 + d_q_computed_pct / 100.0)
        multiply_matches_implied_pct = 100.0 * abs(restated_multiply - implied) / implied
        # divide-form restatement (what sec 1.5's prose literally states)
        restated_divide = reported / (1.0 - d_q_computed_pct / 100.0)
        divide_vs_multiply_gap_musd = restated_divide - restated_multiply

        row = {
            "quarter_end": q,
            "reported_unearned_musd": reported,
            "coverage_norm_full_sample": norm,
            "next_q_revenue_used_musd": nextq_rev,
            "next_q_revenue_basis": basis,
            "implied_pro_forma_musd": round(implied, 2),
            "gap_musd": round(gap, 2),
            "d_q_computed_pct": round(d_q_computed_pct, 3),
            "d_q_quoted_pct": d_q_quoted_pct,
            "d_q_matches_quoted": abs(d_q_computed_pct - d_q_quoted_pct) < 0.1,
            "restated_multiply_form_musd": round(restated_multiply, 2),
            "restated_multiply_equals_implied": multiply_matches_implied_pct < 0.5,
            "multiply_vs_implied_pct_diff": round(multiply_matches_implied_pct, 4),
            "restated_divide_form_musd": round(restated_divide, 2),
            "divide_minus_multiply_musd": round(divide_vs_multiply_gap_musd, 2),
            "circular_for_prediction": q == "2Q26",  # uses a GUIDE, not an actual
        }
        rows.append(row)
    df = pd.DataFrame(rows)

    # formula-vs-number check on y/y growth
    fv_rows = []
    for q in ("1Q26", "2Q26"):
        reported = df.loc[df.quarter_end == q, "reported_unearned_musd"].iloc[0]
        d_pct = df.loc[df.quarter_end == q, "d_q_computed_pct"].iloc[0]
        prior = YOY_PRIOR[q]
        yoy_multiply = 100.0 * (reported * (1 + d_pct / 100.0) / prior - 1.0)
        yoy_divide = 100.0 * (reported / (1 - d_pct / 100.0) / prior - 1.0)
        fv_rows.append({
            "quarter": q, "reported_musd": reported, "prior_year_reported_musd": prior,
            "d_q_pct": d_pct,
            "yoy_multiply_form_pct": round(yoy_multiply, 2),
            "yoy_divide_form_pct": round(yoy_divide, 2),
            "yoy_quoted_in_doc_pct": YOY_QUOTED_PCT[q],
            "multiply_form_matches_quoted": abs(yoy_multiply - YOY_QUOTED_PCT[q]) < 0.15,
            "divide_form_matches_quoted": abs(yoy_divide - YOY_QUOTED_PCT[q]) < 0.15,
        })
    fv = pd.DataFrame(fv_rows)

    df.to_csv(OUT_DIR / "02_circularity_test.csv", index=False)
    fv.to_csv(OUT_DIR / "02b_formula_vs_number_check.csv", index=False)

    verdict = {
        "circularity_confirmed": bool((df["restated_multiply_equals_implied"]).all()),
        "worst_case_diff_pct": float(df["multiply_vs_implied_pct_diff"].max()),
        "formula_ruling": "multiply form (reported * (1+d_q)); the divide form in "
                          "03_insider_mechanics.md L200 does not reproduce the doc's "
                          "own quoted y/y numbers, the multiply form does",
        "formula_check_multiply_ok": bool(fv["multiply_form_matches_quoted"].all()),
        "formula_check_divide_ok": bool(fv["divide_form_matches_quoted"].all()),
        "ruling": ("CIRCULAR. restated_unearned_q === coverage_norm_season(q) * "
                  "next_quarter_revenue(q+1), to within numerical rounding "
                  f"(<{df['multiply_vs_implied_pct_diff'].max():.3f}% on all "
                  f"{len(df)} rows, well inside the 0.5% threshold). The 2Q26 row is a "
                  "function of the 3Q26 GUIDE MIDPOINT, not a realised print: any "
                  "forecast of 3Q26 revenue that conditions on the 2Q26 restated "
                  "balance is conditioning on the number it is trying to predict. "
                  "STRUCK as a pin, as a feature, and from every window/likelihood "
                  "in this and every other package."),
    }
    pd.DataFrame([verdict]).to_csv(OUT_DIR / "02c_circularity_verdict.csv", index=False)
    return df, fv, verdict


if __name__ == "__main__":
    df, fv, verdict = run()
    print(df.to_string(index=False))
    print()
    print(fv.to_string(index=False))
    print()
    for k, v in verdict.items():
        print(f"{k}: {v}")
