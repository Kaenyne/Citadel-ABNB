"""R13 revision 2 (audit A13 response). Revision 1 is r13_model.py (untouched, with its outputs).
Changes, each tied to a finding:
  - A13-08: when the jump term (q = 2/99 per step, size U(0.9, 1.5), calibrated on the two Sep-2023 index-inclusion steps)
    is on, those two shocks are removed from the AR(1) bootstrap pool (|residual| >= 0.75 -> pool n 97, sd 0.249), so the
    episode is priced once, not twice
  - A13-09: down-print overlay at the MEAN of the six post-down-print three-settlement rises (+0.35pt), with +0.70 (max)
    and +1.5 (twice the max) as sensitivities
  - (missed by the audit) overlay probability = S01 REVISION 2 P(day-1 <= -5%) = 0.38, not revision 1's 0.41
  - A13-19: denominator reported on both the repo file's basic weighted-average count (592.0m) and the implied
    outstanding count (598.786m); the threshold moves by 0.34m shares
Seed 20260917, 300,000 paths per simulation. Run from the repo root:
  py -3.13 docs/pitch-forecasts/questions/risk-short-interest-crowding/datasets/r13_model_v2.py
"""
import json, pathlib, numpy as np, pandas as pd
HERE = pathlib.Path(__file__).resolve().parent
rng = np.random.default_rng(20260917)
h = pd.read_csv(HERE / "si_history_2022_2026.csv"); h["date"] = pd.to_datetime(h["date"]); h = h.sort_values("date")
SHARES_OUT_M = 592.0; SHARES_OUT_ALT_M = 598.785682
latest_shares = 14_228_547
latest_pct = latest_shares / (SHARES_OUT_M * 1e6) * 100
x = np.append(h["si_pct_used"].values, latest_pct); dates = list(h["date"].dt.date.astype(str)) + ["2026-08-31"]
n = len(x)
P_DOWN5_S01_REV2 = 0.38   # S01 revision 2 p_le_minus5 (../day1-move-5nov/forecasts/2026-09-17-forecast.json)
P_DOWN5_S01_REV1 = 0.41
out = {"n_settlements": n, "latest_pct_592m": float(latest_pct), "latest_pct_598_8m": latest_shares / (SHARES_OUT_ALT_M * 1e6) * 100,
       "threshold_shares_m_592m": 0.05 * SHARES_OUT_M, "threshold_shares_m_598_8m": 0.05 * SHARES_OUT_ALT_M,
       "rise_needed_pts_592m": 5 - latest_pct, "overlay_p_s01_rev2": P_DOWN5_S01_REV2}
# post-print rises (from revision 1's si_after_prints.csv): mean / median / max of the six down<=-5% prints
pp = pd.read_csv(HERE / "si_after_prints.csv"); d5 = pp[pp.day1 <= -5]
out["down5_rises"] = {"n": int(len(d5)), "values": d5.rise_max3.tolist(), "mean": float(d5.rise_max3.mean()), "median": float(d5.rise_max3.median()), "max": float(d5.rise_max3.max())}
# AR(1) fit on the full series
a, b = np.polyfit(x[:-1], x[1:], 1); resid = x[1:] - (a * x[:-1] + b)
clean = resid[np.abs(resid) < 0.75]
out["ar1"] = {"slope": float(a), "intercept": float(b), "long_run_mean": float(b / (1 - a)), "resid_sd_full": float(resid.std(ddof=1)),
              "resid_sd_clean": float(clean.std(ddof=1)), "n_full": int(len(resid)), "n_clean": int(len(clean)),
              "removed_residuals": [round(float(r), 3) for r in resid[np.abs(resid) >= 0.75]]}
q_jump = 2 / 99
def ar_sim(pool, start=latest_pct, n_unobs=1, n_win=8, nsim=300_000, jump_q=0.0, jump_lo=0.9, jump_hi=1.5, overlay_p=0.0, overlay_pts=0.35, overlay_steps=(3, 4)):
    v = np.full(nsim, start); m = np.full(nsim, -np.inf)
    ov = rng.random(nsim) < overlay_p
    for k in range(n_unobs + n_win):
        v = a * v + b + rng.choice(pool, nsim)
        if jump_q > 0:
            j = rng.random(nsim) < jump_q; v = v + j * rng.uniform(jump_lo, jump_hi, nsim)
        if overlay_p > 0 and (k - n_unobs) in overlay_steps: v = v + ov * overlay_pts / len(overlay_steps)
        if k >= n_unobs: m = np.maximum(m, v)
    return {"P(max>=5)": float((m >= 5).mean()), "P(max>=4.5)": float((m >= 4.5).mean()), "P(max>=4)": float((m >= 4).mean()), "P(max>=3.5)": float((m >= 3.5).mean()),
            "P(max>=3.43_float_basis_equiv)": float((m >= 3.43).mean()), "p50_max": float(np.median(m)), "p90_max": float(np.quantile(m, 0.9)), "p99_max": float(np.quantile(m, 0.99))}
runs = [
    ("rev1_ar1_full_pool", dict(pool=resid)),
    ("rev1_ar1_full_pool_jump", dict(pool=resid, jump_q=q_jump)),
    ("rev1_ar1_full_pool_jump_overlay_0.70_p0.41", dict(pool=resid, jump_q=q_jump, overlay_p=P_DOWN5_S01_REV1, overlay_pts=0.70)),
    ("clean_pool_no_jump", dict(pool=clean)),
    ("clean_pool_jump", dict(pool=clean, jump_q=q_jump)),
    ("BASE_clean_pool_jump_overlay_0.35_p0.38", dict(pool=clean, jump_q=q_jump, overlay_p=P_DOWN5_S01_REV2, overlay_pts=0.35)),
    ("clean_pool_jump_overlay_0.35_p0.41", dict(pool=clean, jump_q=q_jump, overlay_p=P_DOWN5_S01_REV1, overlay_pts=0.35)),
    ("clean_pool_jump_overlay_0.70_p0.38", dict(pool=clean, jump_q=q_jump, overlay_p=P_DOWN5_S01_REV2, overlay_pts=0.70)),
    ("clean_pool_jump_overlay_1.5_p0.38", dict(pool=clean, jump_q=q_jump, overlay_p=P_DOWN5_S01_REV2, overlay_pts=1.5)),
    ("clean_pool_jump_x2_overlay_0.35", dict(pool=clean, jump_q=2 * q_jump, overlay_p=P_DOWN5_S01_REV2, overlay_pts=0.35)),
    ("clean_pool_jump_bigger_U(1.5,2.5)_overlay_0.35", dict(pool=clean, jump_q=q_jump, jump_lo=1.5, jump_hi=2.5, overlay_p=P_DOWN5_S01_REV2, overlay_pts=0.35)),
    ("clean_pool_jump_overlay_0.35_start_3.0", dict(pool=clean, start=3.0, jump_q=q_jump, overlay_p=P_DOWN5_S01_REV2, overlay_pts=0.35)),
    ("clean_pool_jump_overlay_0.35_start_2.0", dict(pool=clean, start=2.0, jump_q=q_jump, overlay_p=P_DOWN5_S01_REV2, overlay_pts=0.35)),
    ("clean_pool_jump_overlay_0.35_conditional_down_print", dict(pool=clean, jump_q=q_jump, overlay_p=1.0, overlay_pts=0.35)),
    ("clean_pool_jump_no_overlay_conditional_up_print", dict(pool=clean, jump_q=q_jump)),
]
out["sims"] = {}
for name, kw in runs:
    out["sims"][name] = ar_sim(**kw)
    print("%-58s P(>=5) %.4f  P(>=4) %.4f  P(>=3.5) %.4f  p50 %.2f  p90 %.2f  p99 %.2f" % (name, out["sims"][name]["P(max>=5)"], out["sims"][name]["P(max>=4)"], out["sims"][name]["P(max>=3.5)"], out["sims"][name]["p50_max"], out["sims"][name]["p90_max"], out["sims"][name]["p99_max"]))
json.dump(out, open(HERE / "r13_v2_summary.json", "w"), indent=1, default=str)
print(json.dumps({k: v for k, v in out.items() if k != "sims"}, indent=1, default=str))
