#!/usr/bin/env python
"""M2 (`margin-ts`) -- WS22 discussion round: reproduce the red-team findings addressed to M2 and
re-quote every claim with a paired-loss p-value and a quarters-better count (WS21 R01, R02).

  cd "<worktree root>"
  py -3.13 analysis/src/margin_build/M2_margin_ts/discussion_checks.py     # ~10 s, exit 0

Writes (data/processed/margin_build/M2_margin_ts/):
  M2_discussion_paired_tests.csv   every M2 claim vs its baseline: MAE ratio, NW(1) t, p, quarters better
  M2_discussion_sentence_info.csv  R07: the sentence sequence, its sign changes and its information
  M2_discussion_guide_ledger.csv   the q_guide_in_force leakage surface (orchestrator question)
  M2_discussion_bands.csv          R10: realised-error band vs the registered Gaussian band
Nothing here registers a forecast and nothing here runs score.py.
"""
from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pandas as pd
from scipy import stats

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[3]
sys.path.insert(0, str(REPO / "analysis" / "src" / "margin_build" / "10_harness_margin"))

from harness_margin import (  # noqa: E402
    Q, load_targets, load_guides, q_guide_in_force, GUIDE_DATES_W1, TODAY,
)

REG = REPO / "data" / "processed" / "margin_build" / "registry"
OUT = REPO / "data" / "processed" / "margin_build" / "M2_margin_ts"
T = load_targets()
ACT = T[T["has_actual"]].set_index("quarter")
W2_FIRST = "2024Q1"


# ------------------------------------------------------------------ paired-loss machinery
def nw_t(d, lag: int = 1):
    """Mean loss differential and a Newey-West(1) t on it."""
    d = np.asarray(d, float)
    n = len(d)
    mu = d.mean()
    e = d - mu
    s = (e @ e) / n
    for l in range(1, lag + 1):
        s += 2.0 * (1.0 - l / (lag + 1.0)) * ((e[l:] @ e[:-l]) / n)
    se = np.sqrt(max(s, 1e-12) / n)
    t = mu / se
    return mu, t, 2.0 * (1.0 - stats.norm.cdf(abs(t)))


def errors(file: str, spec: str, target: str, hz: int = 0, basis: str = "PIT", window: str = "W1"):
    d = pd.read_csv(REG / file)
    d = d[(d["spec_id"] == spec) & (d["target"] == target) & (d["horizon_q"] == hz)
          & (d["prior_basis"] == basis) & (d["window"] == window)]
    a = ACT[target]
    qs = [q for q in d["quarter"] if q in a.index and pd.notna(a[q])]
    return d.set_index("quarter")["point"][qs] - a[qs]


def base_errors(obj: str, target: str, hz: int = 0, basis: str = "PIT", window: str = "W1"):
    return errors(f"baselines-margin__{obj}.csv", f"{obj}|{target}|h{hz}|{basis}",
                  target, hz, basis, window)


def paired(m: pd.Series, b: pd.Series) -> dict:
    qs = sorted(set(m.index) & set(b.index))
    d = (m[qs].abs() - b[qs].abs()).to_numpy()
    mu, t, p = nw_t(d)
    better = int((d < 0).sum())
    best = int(np.argmin(d))
    return dict(n=len(d), mae_method=float(m[qs].abs().mean()), mae_base=float(b[qs].abs().mean()),
                mae_ratio=float(m[qs].abs().mean() / b[qs].abs().mean()), mean_d_pp=mu,
                nw_t=t, p_value=p, quarters_better=better,
                sign_test_p=stats.binomtest(better, len(d), 0.5).pvalue,
                biggest_gain_quarter=qs[best], biggest_gain=float(d[best]),
                mean_d_ex_biggest=float(np.delete(d, best).mean()))


CLAIMS = [
    # (label, registry file, spec, target, baseline object)
    ("sentence rule, margin", "margin-ts__q_sentence_direction.csv", "k_fit_rw", "adj_ebitda_margin_pct", "seasonal_naive"),
    ("sentence rule, margin", "margin-ts__q_sentence_direction.csv", "k_fit_rw", "adj_ebitda_margin_pct", "street"),
    ("sentence rule, EBITDA $", "margin-ts__q_sentence_direction.csv", "k_fit_rw", "adj_ebitda_musd", "seasonal_naive"),
    ("sentence rule, EBITDA $", "margin-ts__q_sentence_direction.csv", "k_fit_rw", "adj_ebitda_musd", "q_guide_implied"),
    ("sentence rule, EBITDA $", "margin-ts__q_sentence_direction.csv", "k_fit_rw", "adj_ebitda_musd", "street"),
    ("sentence rule median, margin", "margin-ts__q_sentence_direction.csv", "k_fit_median", "adj_ebitda_margin_pct", "seasonal_naive"),
    ("sentence rule median, EBITDA $", "margin-ts__q_sentence_direction.csv", "k_fit_median", "adj_ebitda_musd", "street"),
    ("sarima lines, margin", "margin-ts__sarima_margin.csv", "lines_aicc", "adj_ebitda_margin_pct", "seasonal_naive"),
    ("sarima lines, EBITDA $", "margin-ts__sarima_margin.csv", "lines_aicc", "adj_ebitda_musd", "street"),
    ("per-night (rw), margin", "margin-ts__per_night_seasonal.csv", "g_k4_rw", "adj_ebitda_margin_pct", "seasonal_naive"),
    ("incremental k8_median, margin", "margin-ts__incremental_margin.csv", "k8_median", "adj_ebitda_margin_pct", "seasonal_naive"),
]


def run_paired() -> pd.DataFrame:
    rows = []
    for label, f, spec, tgt, base in CLAIMS:
        for w in ("W1", "W2"):
            try:
                r = paired(errors(f, spec, tgt, window=w), base_errors(base, tgt, window=w))
            except (ValueError, KeyError):
                continue
            r.update(claim=label, spec_id=spec, target=tgt, baseline=base, window=w, horizon_q=0)
            rows.append(r)
    cols = ["claim", "spec_id", "target", "baseline", "window", "horizon_q", "n", "mae_method",
            "mae_base", "mae_ratio", "mean_d_pp", "nw_t", "p_value", "quarters_better",
            "sign_test_p", "biggest_gain_quarter", "biggest_gain", "mean_d_ex_biggest"]
    return pd.DataFrame(rows)[cols]


# ------------------------------------------------------------------ R07: sentence information
def sentence_info() -> tuple[pd.DataFrame, pd.DataFrame]:
    rows = []
    for vd in GUIDE_DATES_W1:
        q0 = Q.quarter_of_date(vd)
        g = q_guide_in_force(vd, q0, T)
        d = {"ceiling": -1, "floor": +1}.get((g or {}).get("guide_type", ""), 0)
        m = float(ACT.at[q0, "adj_ebitda_margin_pct"])
        m4 = float(ACT.at[Q.shift(q0, -4), "adj_ebitda_margin_pct"])
        rows.append(dict(vintage_date=str(vd), quarter=q0, guide_type=(g or {}).get("guide_type", "none"),
                         direction=d, realised_yoy_pp=m - m4,
                         quote=str((g or {}).get("quote", ""))[:120]))
    s = pd.DataFrame(rows)
    summ = []
    for lab, sub in (("W1", s), ("W2", s[s["quarter"] >= W2_FIRST])):
        nz = sub[sub["direction"] != 0]
        summ.append(dict(window=lab, n=len(sub), n_nonzero=len(nz),
                         n_minus1=int((nz["direction"] < 0).sum()), n_plus1=int((nz["direction"] > 0).sum()),
                         sign_changes_along_sequence=int((np.diff(nz["direction"].to_numpy()) != 0).sum()),
                         rule_agrees_with_realised_sign=int((np.sign(nz["realised_yoy_pp"]) == nz["direction"]).sum()),
                         always_negative_agrees=int((np.sign(nz["realised_yoy_pp"]) == -1).sum())))
    return s, pd.DataFrame(summ)


# ------------------------------------------------------------------ the q_guide_in_force leakage surface
def guide_ledger() -> pd.DataFrame:
    g = load_guides()
    q = g[~g["is_fy"]].copy()
    q["expected_target"] = [Q.shift(p, 1) for p in q["print_quarter"]]
    q["target_is_print_plus_1"] = q["target_period"] == q["expected_target"]
    pdt = T.set_index("quarter")["print_date"]
    q["print_date_of_print_quarter"] = [str(pdt.get(p)) for p in q["print_quarter"]]
    q["guide_date_equals_print_date"] = q["guide_date"].astype(str) == q["print_date_of_print_quarter"]
    return q[["guide_id", "guide_date", "print_quarter", "target_period", "expected_target",
              "target_is_print_plus_1", "guide_date_equals_print_date", "guide_type", "quote"]]


# ------------------------------------------------------------------ R10: bands
def bands() -> pd.DataFrame:
    rows = []
    for f, spec in (("margin-ts__q_sentence_direction.csv", "k_fit_rw"),
                    ("margin-ts__q_sentence_direction.csv", "k_fit_median"),
                    ("margin-ts__sarima_margin.csv", "lines_aicc")):
        for w in ("W1", "W2"):
            e = errors(f, spec, "adj_ebitda_margin_pct", window=w)
            d = pd.read_csv(REG / f)
            live = d[(d["spec_id"] == spec) & (d["target"] == "adj_ebitda_margin_pct")
                     & (d["window"] == "LIVE") & (d["prior_basis"] == "PIT")
                     & (d["quarter"] == "2026Q3")
                     & (d["vintage_date"].astype(str) == str(TODAY))]   # the TODAY vintage, not 6 Aug
            rows.append(dict(spec_id=spec, window=w, n=len(e), err_mean_pp=float(e.mean()),
                             err_sd_pp=float(e.std(ddof=1)),
                             emp_q10=float(np.percentile(e, 10)), emp_q90=float(np.percentile(e, 90)),
                             empirical_band_width_pp=float(np.percentile(e, 90) - np.percentile(e, 10)),
                             registered_live_q10=float(live["q10"].iloc[0]) if len(live) else np.nan,
                             registered_live_q90=float(live["q90"].iloc[0]) if len(live) else np.nan,
                             registered_band_width_pp=float(live["q90"].iloc[0] - live["q10"].iloc[0]) if len(live) else np.nan,
                             live_point=float(live["point"].iloc[0]) if len(live) else np.nan,
                             bias_corrected_live_point=float(live["point"].iloc[0] - e.mean()) if len(live) else np.nan))
    return pd.DataFrame(rows)


def main() -> int:
    OUT.mkdir(parents=True, exist_ok=True)
    pt = run_paired()
    pt.to_csv(OUT / "M2_discussion_paired_tests.csv", index=False)
    s, summ = sentence_info()
    s.to_csv(OUT / "M2_discussion_sentence_info.csv", index=False)
    summ.to_csv(OUT / "M2_discussion_sentence_summary.csv", index=False)
    gl = guide_ledger()
    gl.to_csv(OUT / "M2_discussion_guide_ledger.csv", index=False)
    bd = bands()
    bd.to_csv(OUT / "M2_discussion_bands.csv", index=False)
    with pd.option_context("display.width", 250, "display.max_rows", 100):
        print("== paired loss differentials (h=0, PIT) ==")
        print(pt[["claim", "baseline", "window", "n", "mae_ratio", "mean_d_pp", "nw_t", "p_value",
                  "quarters_better", "sign_test_p"]].round(3).to_string(index=False))
        print("\n== R07 sentence information ==")
        print(summ.to_string(index=False))
        print("\n== q_guide_in_force leakage surface ==")
        print(f"quarterly margin guides n={len(gl)}; target == print quarter + 1: "
              f"{int(gl['target_is_print_plus_1'].sum())}; guide_date == the print date of the print "
              f"quarter: {int(gl['guide_date_equals_print_date'].sum())}")
        print(gl[~gl["target_is_print_plus_1"]][["guide_id", "guide_date", "print_quarter",
                                                 "target_period"]].to_string(index=False))
        print("\n== R10 bands ==")
        print(bd.round(2).to_string(index=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
