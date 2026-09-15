"""WS22 discussion round, group C: the checks M7 was asked to answer (R10, R16, and the FCF result).

Additive only: reads the scoreboard `10_harness_margin/score.py` already wrote and writes NEW files.
Nothing `run.py` produces changes, so M7 does not need a re-run.

  py -3.13 analysis/src/margin_build/M7_below_ebitda/discussion_checks.py

Writes (data/processed/margin_build/M7_below_ebitda/):
  M7_discussion_coverage_band.csv - realised cov80/cov90 per cell against the EXACT binomial 5-95
                                    band attainable at that n, so an "under-covers" claim can be tested
  M7_discussion_eps_decomp.csv    - R16: EPS error with the actual EBITDA in (`ebitda_known`) vs with
                                    the harness baseline in (`ebitda_pit`), and the share of the
                                    ebitda_pit error the EBITDA input carries
  M7_discussion_summary.json      - the headline numbers quoted in docs/margin-build/discussion/group_C.md
"""
from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pandas as pd
from scipy import stats

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[3]
PROC = REPO / "data/processed/margin_build"
OUT = PROC / "M7_below_ebitda"
BQ = PROC / "10_harness_margin/scoreboard_by_quarter.csv"


def binom_band(n: int, p: float = 0.8, lo_q: float = 0.05, hi_q: float = 0.95):
    """Exact 5-95 band for the realised coverage share of n independent draws at nominal p."""
    if n <= 0:
        return (np.nan, np.nan)
    lo = stats.binom.ppf(lo_q, n, p) / n
    hi = stats.binom.ppf(hi_q, n, p) / n
    return float(lo), float(hi)


def main() -> int:
    bq = pd.read_csv(BQ)
    m7 = bq[(bq["method"] == "below-ebitda") & (bq["prior_basis"] == "PIT")]

    rows = []
    for (obj, tgt, win, h, spec), g in m7.groupby(["object", "target", "window", "horizon_q", "spec_id"]):
        for lvl, col in ((0.80, "in80"), (0.90, "in90")):
            v = pd.to_numeric(g[col], errors="coerce").dropna()
            if len(v) < 5:
                continue
            lo, hi = binom_band(len(v), lvl)
            cov = float(v.mean())
            rows.append(dict(object=obj, target=tgt, window=win, horizon_q=int(h), spec_id=spec,
                             nominal=lvl, n=int(len(v)), coverage=cov, band_lo=lo, band_hi=hi,
                             below_band=bool(cov < lo - 1e-9), above_band=bool(cov > hi + 1e-9)))
    cov = pd.DataFrame(rows).sort_values(["nominal", "coverage"])
    cov.to_csv(OUT / "M7_discussion_coverage_band.csv", index=False)

    c80 = cov[cov["nominal"] == 0.80]
    tax = c80[c80["target"].isin(["tax_rate_pct", "tax_provision_musd"])]

    # ---- R16: how much of the ebitda_pit EPS error is the EBITDA input?
    eps = m7[(m7["object"] == "eps")].copy()
    eps["ebitda_basis"] = np.where(eps["spec_id"].str.startswith("ebitda_known"), "known", "pit")
    eps["weighting"] = np.where(eps["spec_id"].str.endswith("|rw"), "rw", "eq")
    dec = []
    for (tgt, win, h, wgt), g in eps.groupby(["target", "window", "horizon_q", "weighting"]):
        k = g[g["ebitda_basis"] == "known"].set_index("quarter")["err"]
        p = g[g["ebitda_basis"] == "pit"].set_index("quarter")["err"]
        q = sorted(set(k.index) & set(p.index))
        if len(q) < 5:
            continue
        ek, ep = k.loc[q].to_numpy(float), p.loc[q].to_numpy(float)
        contrib = ep - ek                      # what the PIT EBITDA input added to the error
        dec.append(dict(target=tgt, window=win, horizon_q=int(h), weighting=wgt, n=len(q),
                        mae_ebitda_known=float(np.abs(ek).mean()),
                        mae_ebitda_pit=float(np.abs(ep).mean()),
                        mae_ebitda_input_contrib=float(np.abs(contrib).mean()),
                        share_of_pit_mae_from_ebitda_input=float(np.abs(contrib).mean() / np.abs(ep).mean())
                        if np.abs(ep).mean() else np.nan,
                        corr_err_pit_vs_contrib=float(np.corrcoef(ep, contrib)[0, 1]) if len(q) > 2 else np.nan))
    dc = pd.DataFrame(dec).sort_values(["target", "window", "horizon_q", "weighting"])
    dc.to_csv(OUT / "M7_discussion_eps_decomp.csv", index=False)

    # ---- WS20 question 11: what happens to 3Q26 EPS if the recommended margin blend replaces M1
    # as the EBITDA input, and does the interval widen? The waterfall is linear in EBITDA, so the
    # slope is exact: d(EPS)/d(EBITDA) = (1 - ETR) / diluted shares.
    wf = pd.read_csv(OUT / "M7_live_waterfall_quarterly.csv")
    q3 = wf[(wf["quarter"] == "2026Q3") & (wf["scenario"] == "base")].set_index("ebitda_source")
    rev = float(q3.loc["driver-lines", "revenue_musd"])
    e_m1, eps_m1 = float(q3.loc["driver-lines", "adj_ebitda_musd"]), float(q3.loc["driver-lines", "eps_diluted"])
    e_st, eps_st = float(q3.loc["street", "adj_ebitda_musd"]), float(q3.loc["street", "eps_diluted"])
    slope = (eps_m1 - eps_st) / (e_m1 - e_st)                       # $ of EPS per $M of EBITDA
    blend_margin = 50.39                                           # WS20 note section 9, recommended_ws23_60_20_20
    e_blend = blend_margin / 100.0 * rev
    eps_blend = eps_st + slope * (e_blend - e_st)
    # interval: bridge-only (M7's own h=0 EPS error with the EBITDA known) vs propagated
    sd_bridge = 0.0661 * 1.2533                                     # W2 h=0 MAE with ebitda_known -> sd
    sd_margin_pp = 0.743 * 1.2533                                   # M5 W2 h=0 margin MAE -> sd, in pp
    sd_eps_ebitda = sd_margin_pp / 100.0 * rev * slope
    sd_total = float(np.sqrt(sd_bridge ** 2 + sd_eps_ebitda ** 2))
    z80 = float(stats.norm.ppf(0.9))
    eps_block = {
        "revenue_musd": rev, "slope_eps_per_musd_ebitda": slope,
        "eps_on_M1_ebitda": eps_m1, "ebitda_M1": e_m1,
        "eps_on_street_ebitda": eps_st, "ebitda_street": e_st,
        "blend_margin_pct": blend_margin, "ebitda_blend_musd": e_blend, "eps_on_blend": eps_blend,
        "delta_eps_vs_M1": eps_blend - eps_m1, "delta_eps_vs_street": eps_blend - eps_st,
        "sd_bridge_only": sd_bridge, "sd_from_ebitda_uncertainty": sd_eps_ebitda, "sd_total": sd_total,
        "band80_propagated": [eps_blend - z80 * sd_total, eps_blend + z80 * sd_total],
        "band80_registered_M7": [2.73, 3.09],
        "eps_per_1pp_of_margin": rev / 100.0 * slope,
    }
    pd.DataFrame([eps_block]).to_csv(OUT / "M7_discussion_blend_eps.csv", index=False)

    summary = {
        "WS20_q11_blend_eps": eps_block,
        "R10_cells_tested_cov80": int(len(c80)),
        "R10_cells_below_band_cov80": int(c80["below_band"].sum()),
        "R10_cells_above_band_cov80": int(c80["above_band"].sum()),
        "R10_mean_cov80": float(c80["coverage"].mean()),
        "R10_tax_cells": tax[["target", "window", "spec_id", "horizon_q", "n", "coverage",
                              "band_lo", "band_hi", "below_band"]].to_dict("records"),
        "R10_lowest_cells": c80.nsmallest(6, "coverage")[["object", "target", "window", "horizon_q",
                                                          "spec_id", "n", "coverage", "band_lo",
                                                          "below_band"]].to_dict("records"),
        "R16_eps_h0": dc[(dc.target == "eps_diluted") & (dc.horizon_q == 0) & (dc.weighting == "rw")]
                        .to_dict("records"),
    }
    (OUT / "M7_discussion_summary.json").write_text(json.dumps(summary, indent=2, default=float), encoding="utf-8")
    print(json.dumps(summary, indent=2, default=float))
    print("\ncov80 cells below their exact binomial 5-95 band:")
    print(c80[c80["below_band"]][["object", "target", "window", "horizon_q", "spec_id", "n",
                                 "coverage", "band_lo"]].round(3).to_string(index=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
