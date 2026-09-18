"""Revision-2 final S02 / S03 distributions (A07-03): CDF mixture of the v2 decomposition Monte Carlo (weight W_DECOMP)
and the v2 options anchor (two-lognormal mixture RND, real-world shifted; anchor_cdf_v2.csv from implied_dist_v2.py).
The anchor CDF used in the blend is now the same object the logs describe (no lognormal substitution).
Run from the repo root after implied_dist_v2.py: py -3.13 docs/pitch-forecasts/questions/close-15dec-2026/datasets/final_blend_v2.py
"""
import json, pathlib, sys
import numpy as np, pandas as pd
HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from abnb_path_mixture_v2 import run, PARAMS, QS
W_DECOMP = 0.65
anchor = pd.read_csv(HERE / "anchor_cdf_v2.csv")
grid = anchor.price.to_numpy()
out, sims = run(verbose=False)
res = {}
for q, key, arr in (("S02", "cdf_dec15_rw", sims["P_dec"]), ("S03", "cdf_feb12_rw", sims["P_feb"])):
    cdf_d = np.searchsorted(np.sort(arr), grid) / len(arr)
    cdf_a = anchor[key].to_numpy()
    cdf = W_DECOMP * cdf_d + (1 - W_DECOMP) * cdf_a
    pct = {str(p): float(np.interp(p / 100, cdf, grid)) for p in QS}
    thr = {"P(<=143)": float(np.interp(143, grid, cdf)), "P(<=150)": float(np.interp(150, grid, cdf)),
           "P(>=180)": float(1 - np.interp(180, grid, cdf)), "P(<=125)": float(np.interp(125, grid, cdf)),
           "P(>=200)": float(1 - np.interp(200, grid, cdf)), "P(<100)": float(np.interp(100, grid, cdf)),
           "P(>260)": float(1 - np.interp(260, grid, cdf))}
    pdf5 = np.diff(np.interp(np.arange(60, 340, 5), grid, cdf))
    bins = np.arange(60, 335, 5)
    dens = np.gradient(cdf, grid); dens = np.clip(dens, 0, None); dens /= np.trapezoid(dens, grid)
    mean = float(np.trapezoid(grid * dens, grid)); mlog = float(np.trapezoid(np.log(grid) * dens, grid))
    res[q] = {"weights": {"decomposition": W_DECOMP, "anchor_mixture_rnd_shifted": 1 - W_DECOMP},
              "anchor_real_world_median": float(np.interp(0.5, cdf_a, grid)),
              "anchor_thresholds": {"P(<=143)": float(np.interp(143, grid, cdf_a)), "P(<=150)": float(np.interp(150, grid, cdf_a)),
                                    "P(>=180)": float(1 - np.interp(180, grid, cdf_a)), "P(<100)": float(np.interp(100, grid, cdf_a)),
                                    "P(>260)": float(1 - np.interp(260, grid, cdf_a))},
              "decomposition_median": float(np.median(arr)),
              "percentiles": pct, "thresholds": thr, "mean": mean,
              "log_sd_pct": float(np.sqrt(np.trapezoid((np.log(grid) - mlog) ** 2 * dens, grid)) * 100),
              "min_pdf_per_5usd_bin_120_to_230": float(pdf5[(bins >= 120) & (bins <= 230)].min()),
              "argmin_bin_120_to_230": int(bins[(bins >= 120) & (bins <= 230)][np.argmin(pdf5[(bins >= 120) & (bins <= 230)])]),
              "peak_5usd_bin": int(bins[np.argmax(pdf5)])}
    pd.DataFrame({"price": grid, "cdf_decomp": cdf_d, "cdf_anchor": cdf_a, "cdf_final": cdf}).to_csv(HERE / f"{q}_final_cdf_v2.csv", index=False)
# S02 monitoring references: 6 Nov close -> 15 Dec median and P(<=150) with the post block only (26 sessions, 30% vol, drift -1.0% avg)
from scipy.stats import norm
import math
v = PARAMS["bg_vol_ann"]; k = PARAMS["sessions_post_to_dec15"] / 252; mu = PARAMS["total_drift_ann"]
res["S02_after_6nov_reference"] = {}
for c in (150, 160, 175):
    m = math.log(c) + math.log1p(-0.010) + (mu - 0.5 * v * v) * k; s = v * math.sqrt(k)
    res["S02_after_6nov_reference"][str(c)] = {"median": float(math.exp(m)), "P(<=150)": float(norm.cdf((math.log(150) - m) / s)),
                                               "P(>=180)": float(1 - norm.cdf((math.log(180) - m) / s))}
print(json.dumps(res, indent=1))
json.dump(res, open(HERE / "final_blend_v2.json", "w"), indent=1)
