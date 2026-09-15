#!/usr/bin/env python
"""M3 (`guide-policy-margin`) -- WS22 discussion round: reproduce the red-team findings addressed to M3
(R05 spec provenance, R06 the pin's one-quarter win, R08 the n=3 flag, R12 the LIVE path) and re-quote
every claim with a paired-loss p-value and a quarters-better count (R01, R02).

  cd "<worktree root>"
  py -3.13 analysis/src/margin_build/M3_guide_policy_margin/discussion_checks.py    # ~10 s, exit 0

Writes (data/processed/margin_build/M3_guide_policy_margin/):
  M3_discussion_paired_tests.csv     every M3 claim vs seasonal naive, the harness guide_implied
                                     baseline and the within-method proration ablation
  M3_discussion_pin_decomposition.csv  R06: the quarter that carries each pin spec's win
  M3_discussion_live_coherence.csv   R12: every LIVE spec against the 2022-26 quarter-of-year range
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

from harness_margin import load_targets, TODAY  # noqa: E402

REG = REPO / "data" / "processed" / "margin_build" / "registry"
OUT = REPO / "data" / "processed" / "margin_build" / "M3_guide_policy_margin"
M3F = "guide-policy-margin__actual_given_guide.csv"
T = load_targets()
ACT = T[T["has_actual"]].set_index("quarter")


def nw_t(d, lag: int = 1):
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


def errors(file: str, spec: str, target: str = "adj_ebitda_margin_pct", hz: int = 0,
           basis: str = "PIT", window: str = "W1"):
    d = pd.read_csv(REG / file)
    d = d[(d["spec_id"] == spec) & (d["target"] == target) & (d["horizon_q"] == hz)
          & (d["prior_basis"] == basis) & (d["window"] == window)]
    a = ACT[target]
    qs = [q for q in d["quarter"] if q in a.index and pd.notna(a[q])]
    return d.set_index("quarter")["point"][qs] - a[qs]


def base_errors(obj: str, target: str = "adj_ebitda_margin_pct", hz: int = 0,
                basis: str = "PIT", window: str = "W1"):
    return errors(f"baselines-margin__{obj}.csv", f"{obj}|{target}|h{hz}|{basis}",
                  target, hz, basis, window)


def paired(m: pd.Series, b: pd.Series) -> dict:
    qs = sorted(set(m.index) & set(b.index))
    d = (m[qs].abs() - b[qs].abs()).to_numpy()
    mu, t, p = nw_t(d)
    better = int((d < 0).sum())
    best = int(np.argmin(d))
    return dict(n=len(d), mae_method=float(m[qs].abs().mean()), mae_base=float(b[qs].abs().mean()),
                mae_ratio=float(m[qs].abs().mean() / b[qs].abs().mean()), mean_d_pp=mu, nw_t=t,
                p_value=p, quarters_better=better,
                sign_test_p=stats.binomtest(better, len(d), 0.5).pvalue,
                biggest_gain_quarter=qs[best], biggest_gain=float(d[best]),
                mean_d_ex_biggest=float(np.delete(d, best).mean()))


PRE_REG = ["rw_hl4", "equal", "last", "nocushion", "rw_hl4_prorata"]
POST_HOC = ["rw_hl4_pin", "nocushion_pin", "last_pin", "nov_sentence_pin"]


def run_paired() -> pd.DataFrame:
    rows = []
    for spec in PRE_REG + POST_HOC:
        for w in ("W1", "W2"):
            m = errors(M3F, spec, window=w)
            if len(m) == 0:
                continue
            for base_lab, b in (("seasonal_naive", base_errors("seasonal_naive", window=w)),
                                ("harness guide_implied", base_errors("guide_implied", window=w)),
                                ("street", base_errors("street", window=w)),
                                ("within-method rw_hl4_prorata", errors(M3F, "rw_hl4_prorata", window=w))):
                if spec == "rw_hl4_prorata" and base_lab.startswith("within"):
                    continue
                r = paired(m, b)
                r.update(spec_id=spec, pre_registered=spec in PRE_REG, baseline=base_lab,
                         window=w, target="adj_ebitda_margin_pct", horizon_q=0)
                rows.append(r)
    cols = ["spec_id", "pre_registered", "baseline", "window", "target", "horizon_q", "n",
            "mae_method", "mae_base", "mae_ratio", "mean_d_pp", "nw_t", "p_value",
            "quarters_better", "sign_test_p", "biggest_gain_quarter", "biggest_gain",
            "mean_d_ex_biggest"]
    return pd.DataFrame(rows)[cols]


def pin_decomposition() -> pd.DataFrame:
    """R06: how much of each pin spec's win against seasonal naive is a single quarter."""
    rows = []
    for spec in ["rw_hl4_pin", "last_pin", "nocushion_pin", "nov_sentence_pin", "rw_hl4"]:
        for w in ("W1", "W2"):
            m = errors(M3F, spec, window=w)
            b = base_errors("seasonal_naive", window=w)
            qs = sorted(set(m.index) & set(b.index))
            d = (m[qs].abs() - b[qs].abs())
            if len(d) == 0:
                continue
            order = d.sort_values().index
            rows.append(dict(spec_id=spec, window=w, n=len(d), mean_d_pp=float(d.mean()),
                             quarters_better=int((d < 0).sum()),
                             best_quarter=order[0], best_gain=float(d[order[0]]),
                             mean_d_ex_best=float(d.drop(order[0]).mean()),
                             second_quarter=order[1], second_gain=float(d[order[1]]),
                             mean_d_ex_two_best=float(d.drop(list(order[:2])).mean())))
    return pd.DataFrame(rows)


def live_coherence() -> pd.DataFrame:
    """R12: each LIVE spec against the 2022-26 range for the same quarter of the year."""
    d = pd.read_csv(REG / M3F)
    d = d[(d["window"] == "LIVE") & (d["prior_basis"] == "PIT")
          & (d["target"] == "adj_ebitda_margin_pct")
          & (d["vintage_date"].astype(str) == str(TODAY))]
    hist = ACT[ACT.index >= "2022Q1"]["adj_ebitda_margin_pct"]
    rows = []
    for r in d.itertuples():
        qtr = int(r.quarter[-1])
        h = hist[[q for q in hist.index if q.endswith(f"Q{qtr}")]]
        rows.append(dict(spec_id=r.spec_id, quarter=r.quarter, point=float(r.point),
                         hist_min=float(h.min()), hist_max=float(h.max()), n_hist=len(h),
                         above_every_historical=bool(r.point > h.max()),
                         q10=float(r.q10), q90=float(r.q90), band_width_pp=float(r.q90 - r.q10)))
    return pd.DataFrame(rows).sort_values(["quarter", "spec_id"])


CROSS_OBJECTS = {
    "M1 margin_v2|b_elastic_rw": ("driver-lines__margin_v2.csv", "b_elastic_rw"),
    "M2 q_sentence_direction|k_fit_rw": ("margin-ts__q_sentence_direction.csv", "k_fit_rw"),
    "M2 sarima_margin|lines_aicc": ("margin-ts__sarima_margin.csv", "lines_aicc"),
    "M3 rw_hl4_pin": (M3F, "rw_hl4_pin"),
    "M3 nov_sentence_pin": (M3F, "nov_sentence_pin"),
    "M3 nocushion": (M3F, "nocushion"),
    "M4 margin_aug|none_rw": ("alt-augmented__margin_aug.csv", "none_rw"),
    "M6 flex_margin|l0_rw": ("cycle-flex__flex_margin.csv", "l0_rw"),
    "M5 dispersion_conditioned|rw_hl4": ("street-bias__dispersion_conditioned.csv", "rw_hl4"),
    "street": ("baselines-margin__street.csv", "street|adj_ebitda_margin_pct|h0|PIT"),
}


def cross_method() -> tuple[pd.DataFrame, pd.DataFrame]:
    """WS20 Q3: does the R12 spec swap keep M3's two useful properties -- low error correlation with
    the rest of the build, and the 1H23 regime-break accuracy?"""
    cols = {}
    for lab, (f, spec) in CROSS_OBJECTS.items():
        try:
            cols[lab] = errors(f, spec, window="W1")
        except (FileNotFoundError, KeyError, ValueError):
            continue
    df = pd.DataFrame(cols).dropna()
    corr = df.corr()
    rows = []
    for lab in corr.columns:
        others = [c for c in corr.columns if c != lab and not (c.startswith("M3") and lab.startswith("M3"))]
        stress = df.loc[[q for q in ("2023Q1", "2023Q2") if q in df.index], lab].abs()
        rows.append(dict(object=lab, n=len(df), mean_pairwise_r=float(corr.loc[lab, others].mean()),
                         mae_1h23_stress=float(stress.mean()), mae_w1=float(df[lab].abs().mean())))
    return corr, pd.DataFrame(rows)


def main() -> int:
    OUT.mkdir(parents=True, exist_ok=True)
    pt = run_paired()
    pt.to_csv(OUT / "M3_discussion_paired_tests.csv", index=False)
    pin = pin_decomposition()
    pin.to_csv(OUT / "M3_discussion_pin_decomposition.csv", index=False)
    lc = live_coherence()
    lc.to_csv(OUT / "M3_discussion_live_coherence.csv", index=False)
    corr, cross = cross_method()
    corr.to_csv(OUT / "M3_discussion_error_correlations.csv")
    cross.to_csv(OUT / "M3_discussion_cross_method.csv", index=False)
    with pd.option_context("display.width", 260, "display.max_rows", 200):
        print("== paired loss differentials, adj EBITDA margin, h=0, PIT ==")
        print(pt[["spec_id", "pre_registered", "baseline", "window", "n", "mae_ratio", "mean_d_pp",
                  "nw_t", "p_value", "quarters_better", "sign_test_p"]].round(3).to_string(index=False))
        print("\n== R06 pin decomposition (vs seasonal naive) ==")
        print(pin.round(3).to_string(index=False))
        print("\n== R12 LIVE coherence (TODAY vintage, base revenue path) ==")
        print(lc.round(2).to_string(index=False))
        print("\n== cross-method: orthogonality and the 1H23 regime break (W1 h=0 PIT errors) ==")
        print(cross.round(3).to_string(index=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
