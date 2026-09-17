"""Final S02 / S03 distributions: CDF mixture of the decomposition Monte Carlo (weight W_DECOMP) and the
options-implied smile risk-neutral density shifted by the real-world drift (weight 1 - W_DECOMP).
Also writes the percentile tables and threshold probabilities the forecast JSONs quote.
Run from the repo root after abnb_path_mixture.py and implied_dist.py:
  py -3.13 docs/pitch-forecasts/questions/close-15dec-2026/datasets/final_blend.py
"""
import glob, json, math, pathlib
import numpy as np, pandas as pd
from scipy.stats import norm
HERE = pathlib.Path(__file__).resolve().parent
import sys
sys.path.insert(0, str(HERE))
from abnb_path_mixture import run, PARAMS, QS
W_DECOMP = 0.65
EQUITY_DRIFT = PARAMS["equity_drift_ann"]
imp = json.load(open(sorted(HERE.glob("implied_dist_*.json"))[-1]))
out, sims = run(verbose=False)
grid = np.arange(60, 340, 0.25)


def smile_cdf(key):
    """Rebuild the smile RND CDF on the grid from the saved percentiles is lossy; instead re-derive from the
    lognormal at the saved sigma but centred on the smile median, then shift by the real-world drift.
    (The smile RND and lognormal quartiles differ by < $1.5 at these horizons; see implied_dist_*.json.)"""
    d = imp[key]
    T = d["T_years"]; sig = d["sigma_pct"] / 100
    med = d["smile_rnd"]["50"] * math.exp(EQUITY_DRIFT * T)   # real-world shift: forward carries r; add the equity premium
    mu = math.log(med)
    return norm.cdf((np.log(grid) - mu) / (sig * math.sqrt(T)))


res = {}
for q, key, arr in (("S02", "dec15", sims["P_dec"]), ("S03", "feb12", sims["P_feb"])):
    cdf_d = np.searchsorted(np.sort(arr), grid) / len(arr)
    cdf_a = smile_cdf(key)
    cdf = W_DECOMP * cdf_d + (1 - W_DECOMP) * cdf_a
    pct = {str(p): float(np.interp(p / 100, cdf, grid)) for p in QS}
    thr = {"P(<=143)": float(np.interp(143, grid, cdf)), "P(<=150)": float(np.interp(150, grid, cdf)),
           "P(>=180)": float(1 - np.interp(180, grid, cdf)), "P(<=125)": float(np.interp(125, grid, cdf)),
           "P(>=200)": float(1 - np.interp(200, grid, cdf)), "P(<100)": float(np.interp(100, grid, cdf)),
           "P(>260)": float(1 - np.interp(260, grid, cdf))}
    # density floor check: mixture pdf on $5 bins
    pdf5 = np.diff(np.interp(np.arange(60, 340, 5), grid, cdf))
    res[q] = {"weights": {"decomposition": W_DECOMP, "anchor_options_smile_shifted": 1 - W_DECOMP},
              "anchor_real_world_median": float(np.interp(0.5, cdf_a, grid)),
              "decomposition_median": float(np.median(arr)),
              "percentiles": pct, "thresholds": thr,
              "min_pdf_per_5usd_bin_120_to_230": float(pdf5[(np.arange(60, 335, 5) >= 120) & (np.arange(60, 335, 5) <= 230)].min())}
    pd.DataFrame({"price": grid, "cdf_decomp": cdf_d, "cdf_anchor": cdf_a, "cdf_final": cdf}).to_csv(HERE / f"{q}_final_cdf.csv", index=False)
print(json.dumps(res, indent=1))
json.dump(res, open(HERE / "final_blend.json", "w"), indent=1)
