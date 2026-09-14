#!/usr/bin/env python
"""WS22: paired-loss significance for every scored cell, WITHOUT re-running the scorer.

`score.py` now writes these columns itself (harness_margin/significance.py), but three discussion
agents were running at once and only the orchestrator may re-score. This script recomputes exactly the
same columns from `scoreboard_by_quarter.csv`, joins them onto the existing `scoreboard_margin.csv`,
and writes a NEW file. It never touches the scoreboard files.

  py -3.13 analysis/src/margin_build/10_harness_margin/significance_check.py

Writes data/processed/margin_build/10_harness_margin/scoreboard_significance.csv:
  one row per (method, object, target, window, horizon_q, prior_basis, spec_id) with
  d_mean_/t_nw1_/p_nw1_/k_better_/p_sign_ against `seasonal_naive` and `street`, the existing MAE
  ratios and survivor flags, and the n-gated flags `survives_both_windows_n8` /
  `survives_both_windows_sig`.
"""
from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent))

from harness_margin import paths as P            # noqa: E402
from harness_margin import significance as SIG   # noqa: E402

GK = ["method", "object", "target", "window", "horizon_q", "prior_basis", "spec_id"]
KEEP = ["n", "mae", "rw_mae", "bias", "cov80", "n_params",
        "mae_ratio_seasonal_naive", "rw_mae_ratio_seasonal_naive", "mae_ratio_street",
        "rw_mae_ratio_street", "beats_seasonal_naive", "rw_beats_seasonal_naive",
        "survives_both_windows", "rw_survives_both_windows"]


def main() -> int:
    bq = pd.read_csv(P.OUT_BY_QUARTER)
    sb = pd.read_csv(P.OUT_SCOREBOARD)
    sig = SIG.from_by_quarter(bq).drop(columns=["n"])
    for d in (sb, sig):
        d["spec_id"] = d["spec_id"].fillna("").astype(str)
        d["horizon_q"] = d["horizon_q"].astype(int)
    out = sb[GK + [c for c in KEEP if c in sb.columns]].merge(sig, on=GK, how="left")
    out = SIG.add_window_flags(out)
    out = SIG.mark_oracle(out)
    dest = P.OUT_SCOREBOARD.parent / "scoreboard_significance.csv"
    out.to_csv(dest, index=False)
    print(f"{len(out)} cells -> {dest}")

    m = out[(out["target"] == "adj_ebitda_margin_pct") & (out["horizon_q"] == 0)
            & (out["prior_basis"] == "PIT") & (out["method"] != "baselines-margin")]
    show = ["method", "object", "spec_id", "window", "n", "mae_ratio_seasonal_naive",
            "k_better_seasonal_naive", "n_cmp_seasonal_naive", "p_sign_seasonal_naive",
            "t_nw1_seasonal_naive", "p_nw1_seasonal_naive"]
    with pd.option_context("display.width", 250, "display.max_columns", 30, "display.max_rows", 40):
        print("\nadj_ebitda_margin_pct, h=0, PIT, cells carrying both survivor flags:")
        print(m[m["survives_both_windows"] & m["rw_survives_both_windows"]][show]
              .sort_values(["window", "mae_ratio_seasonal_naive"]).round(4).to_string(index=False))
        print("\nsame cells after the n>=8 and W1 sign-test gates:")
        print(m[m["survives_both_windows_sig"]][show].round(4).to_string(index=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
