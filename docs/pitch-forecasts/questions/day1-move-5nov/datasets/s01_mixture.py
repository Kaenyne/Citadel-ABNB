"""S01 day1-move-5nov: unconditional day-1 close-to-close return mixture, three estimates, conditional base case.
Deterministic (seed 20260917). Inputs: repo panel files only (paths relative to repo root). Run from the repo root:
  py -3.13 docs/pitch-forecasts/questions/day1-move-5nov/datasets/s01_mixture.py
Outputs (this folder): s01_cells.csv, s01_estimates.csv, s01_percentiles.csv, s01_thresholds.csv, s01_sensitivity.csv,
  s01_conditional_base_case.csv, s01_components.json
"""
import json, pathlib
import numpy as np, pandas as pd

HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE.parents[4]
SEED = 20260917
N = 400_000

panel = pd.read_csv(ROOT / "data/processed/reverse_dcf/C/C_print_panel.csv")
rx = pd.read_csv(ROOT / "data/processed/abnb_earnings_reactions.csv")

# ---------- 1. panel cells (ex-reopening sample 3Q22-2Q26, n 16; raw close-to-close, the question's object) ----------
ex = panel[panel.sample_ex_reopening].copy()
ex["gvs_sign"] = np.where(ex.guide_vs_street_pct < 0, "below", "at/above")
ex["sign"] = ex.nights_accel_sign.map({1.0: "accel", 0.0: "flat", -1.0: "decel"})
ex["bucket_down"] = ex.guide_dir_code < 0
cells = []


def cell(name, m, note=""):
    d = ex[m]
    cells.append(dict(cell=name, n=len(d), mean_raw=round(d.ret_1d_cc_raw_pct.mean(), 2) if len(d) else np.nan,
                      median_raw=round(d.ret_1d_cc_raw_pct.median(), 2) if len(d) else np.nan,
                      sd_raw=round(d.ret_1d_cc_raw_pct.std(ddof=1), 2) if len(d) > 1 else np.nan,
                      mean_excess=round(d.ret_1d_cc_excess_pct.mean(), 2) if len(d) else np.nan,
                      n_pos_raw=int((d.ret_1d_cc_raw_pct > 0).sum()), prints=" ".join(d.label), note=note))


cell("all ex-reopening", ex.index == ex.index)
cell("all post-2022", ex.sample_post2022)
for s in ["accel", "flat", "decel"]:
    cell(f"print {s}", ex.sign == s)
    cell(f"print {s} & guide below Street", (ex.sign == s) & (ex.gvs_sign == "below"))
    cell(f"print {s} & guide at/above Street", (ex.sign == s) & (ex.gvs_sign == "at/above"))
cell("decel & guide below & nights guide direction down (team base case cell)", (ex.sign == "decel") & (ex.gvs_sign == "below") & ex.bucket_down)
cell("decel & guide below & nights guide down-or-stable", (ex.sign == "decel") & (ex.gvs_sign == "below") & (ex.guide_dir_code <= 0))
cell("guide below Street (any print)", ex.gvs_sign == "below")
cell("guide at/above Street (any print)", ex.gvs_sign == "at/above")
cell("Q3 prints (November reaction), ex-reopening", ex.label.str.startswith("3Q"))
cells_df = pd.DataFrame(cells)
cells_df.to_csv(HERE / "s01_cells.csv", index=False)
print(cells_df.to_string(index=False))
print("UNOBSERVED: accelerating Street bar (3Q26E +11.45pct) meeting a decelerating print: 0 prints in the panel (E_street_sign_history).")

# QQQ day-1 dispersion on print days (raw = excess + QQQ)
qqq_sd = float(rx.qqq_1d_pct.std(ddof=1))
qqq_mean = float(rx.qqq_1d_pct.mean())
print(f"QQQ day-1 on the 23 reaction days: mean {qqq_mean:.2f}, sd {qqq_sd:.2f}")

# ---------- 2. parameters (documented in the research log) ----------
P = dict(
    nowcast_centre=9.55, nowcast_sd=1.48,           # team band +9.5 (band 8.5-10.0, model path 9.9); reviews-index walk-forward RMSE
    accel_thr=10.59, decel_thr=10.09,               # 2Q26 10.34 +/- 0.25 dead band (C note)
    gap_mean=-1.93, gap_sd=2.8, gap_tilt_per_pt=0.32,  # C01: guide median 3,100 vs Street 3,161 (sd 87 and drift 0.6pct); +$10M per +0.5pt nights
    S1={"accel": 3.95, "flat": -0.56, "decel": -5.06},  # mean of S1 n16 / n14 bucket expectations (C_coefficients_used)
    S2={"c": -1.41, "b_sign": 4.66, "b_gvs": 1.69},     # mean of S2 n16 / n14 (post-hoc, fragile)
    w_S1=0.6, w_S2=0.4,
    positioning_decel=-1.0,                          # JUDGEMENT: accelerating bar meets decelerating print (unobserved cell)
    coef_sd=2.4,                                     # sampling error of the fitted conditional mean (bootstrap p10/p90 +/-3)
    resid_sd=7.5, resid_df=5,                        # residual sd 6.9-8.8 (S1) / 7.3 (S2); t5 tails
    qqq_sd=1.3,
    options_sd_fresh=9.0, options_sd_B=9.5, options_skew_down=1.10, options_mode=-0.3,
    weights={"decomposition": 0.50, "base_rate": 0.25, "options": 0.25},
    bound=40.0,
)


def decomposition(rng, n=N, centre=None, sd=None, w_S1=None, pos=None, resid_sd=None, gap_mean=None, return_draws=False):
    centre = P["nowcast_centre"] if centre is None else centre
    sd = P["nowcast_sd"] if sd is None else sd
    w_S1 = P["w_S1"] if w_S1 is None else w_S1
    w_S2 = 1 - w_S1
    pos = P["positioning_decel"] if pos is None else pos
    resid_sd = P["resid_sd"] if resid_sd is None else resid_sd
    gap_mean = P["gap_mean"] if gap_mean is None else gap_mean
    nights = rng.normal(centre, sd, n)
    sign = np.where(nights >= P["accel_thr"], 1, np.where(nights < P["decel_thr"], -1, 0))
    gap = rng.normal(gap_mean + P["gap_tilt_per_pt"] * (nights - centre), P["gap_sd"], n)
    s1 = np.select([sign == 1, sign == 0], [P["S1"]["accel"], P["S1"]["flat"]], P["S1"]["decel"])
    s2 = P["S2"]["c"] + P["S2"]["b_sign"] * sign + P["S2"]["b_gvs"] * gap
    mean_x = w_S1 * s1 + w_S2 * s2 + np.where(sign == -1, pos, 0.0) + rng.normal(0, P["coef_sd"], n)
    resid = rng.standard_t(P["resid_df"], n) * resid_sd / np.sqrt(P["resid_df"] / (P["resid_df"] - 2))
    r = mean_x + resid + rng.normal(0, P["qqq_sd"], n)
    if return_draws:
        return r, nights, sign, gap
    return r


def base_rate(rng, n=N):
    """Regime-weighted empirical distribution of the 23 raw day-1 prints (post-2022 prints weighted 2x), Gaussian kernel bw 3."""
    x = rx.abnb_1d_pct.values
    w = np.where(rx.quarter >= "2023Q1", 2.0, 1.0)
    w = w / w.sum()
    idx = rng.choice(len(x), n, p=w)
    return x[idx] + rng.normal(0, 3.0, n)


def options_anchor(rng, n=N, sd=None):
    """Two-piece normal at the options-implied event sd (mode -0.3, downside sd x1.10, upside x0.90: the -3.5 vol pt risk reversal)."""
    sd = P["options_sd_fresh"] if sd is None else sd
    sdd, sdu = sd * P["options_skew_down"], sd * (2 - P["options_skew_down"])
    z = np.abs(rng.normal(0, 1, n))
    side = rng.random(n) < sdd / (sdd + sdu)
    return P["options_mode"] + np.where(side, -z * sdd, z * sdu)


PCT = [5, 10, 25, 50, 75, 90, 95]


def summ(r):
    r = np.clip(r, -60, 60)
    d = {f"p{p}": round(float(np.percentile(r, p)), 2) for p in PCT}
    d.update(mean=round(float(r.mean()), 2), sd=round(float(r.std()), 2), rms=round(float(np.sqrt((r ** 2).mean())), 2),
             p_le_m8=round(float((r <= -8).mean()), 3), p_le_m5=round(float((r <= -5).mean()), 3), p_lt_0=round(float((r < 0).mean()), 3),
             p_ge_5=round(float((r >= 5).mean()), 3), p_ge_10=round(float((r >= 10).mean()), 3), p_abs_ge_7=round(float((np.abs(r) >= 7).mean()), 3),
             p_abs_ge_10=round(float((np.abs(r) >= 10).mean()), 3), p_ge_17=round(float((r >= 17).mean()), 3),
             below_m40=round(float((r < -40).mean()), 4), above_p40=round(float((r > 40).mean()), 4))
    return d


rng = np.random.default_rng(SEED)
r_dec, nights, sign, gap = decomposition(rng, return_draws=True)
r_br = base_rate(rng)
r_op = options_anchor(rng)
w = P["weights"]
k = int(N * w["decomposition"])
k2 = int(N * w["base_rate"])
r_final = np.concatenate([r_dec[:k], r_br[:k2], r_op[:N - k - k2]])
est = {"decomposition": summ(r_dec), "base_rate": summ(r_br), "options_anchor": summ(r_op), "FINAL_mixture": summ(r_final)}
est_df = pd.DataFrame(est).T
est_df.to_csv(HERE / "s01_estimates.csv")
print(est_df.to_string())
p_states = dict(p_accel=round(float((sign == 1).mean()), 3), p_flat=round(float((sign == 0).mean()), 3), p_decel=round(float((sign == -1).mean()), 3),
                p_guide_below=round(float((gap < 0).mean()), 3),
                p_below_given_decel=round(float((gap[sign == -1] < 0).mean()), 3), p_below_given_accel=round(float((gap[sign == 1] < 0).mean()), 3))
print(p_states)
# cell expectations inside the decomposition
cellrows = []
for s, nm in [(1, "accel"), (0, "flat"), (-1, "decel")]:
    for b, bn in [(True, "guide below"), (False, "guide at/above")]:
        m = (sign == s) & ((gap < 0) == b)
        cellrows.append(dict(cell=f"{nm} & {bn}", prob=round(float(m.mean()), 3), mean=round(float(r_dec[m].mean()), 2),
                             p_lt_0=round(float((r_dec[m] < 0).mean()), 3), p_le_m8=round(float((r_dec[m] <= -8).mean()), 3)))
cell_model = pd.DataFrame(cellrows)
print(cell_model.to_string(index=False))

# ---------- 3. conditional base case: decelerating print, guide below Street, nights bucket downgraded ----------
m = (sign == -1) & (gap < 0)
r_cond_model = r_dec[m]
emp = ex[(ex.sign == "decel") & (ex.gvs_sign == "below") & (ex.guide_dir_code <= 0)].ret_1d_cc_raw_pct.values  # n 4 cell
rng2 = np.random.default_rng(SEED + 1)
r_cond_emp = emp[rng2.integers(0, len(emp), 200_000)] + rng2.normal(0, 4.0, 200_000)
n_emp = int(len(r_cond_model) * 0.3 / 0.7)
r_cond = np.concatenate([r_cond_model, r_cond_emp[:n_emp]])
cond = {"model_only": summ(r_cond_model), "empirical_cell_n4_smoothed": summ(r_cond_emp),
        "FINAL_conditional_base_case (0.7 model / 0.3 cell)": summ(r_cond)}
cond_df = pd.DataFrame(cond).T
cond_df.to_csv(HERE / "s01_conditional_base_case.csv")
print(cond_df.to_string())
mb = (sign == 1) & (gap >= 0)
breaker = summ(r_dec[mb])
print("thesis-breaker cell (accel & guide at/above):", breaker)

# ---------- 4. sensitivities (decomposition component swapped, final recomputed) ----------
sens = []


def run_variant(name, osd=None, **kw):
    rng = np.random.default_rng(SEED)
    rd = decomposition(rng, **kw)
    rb = base_rate(rng)
    ro = options_anchor(rng, sd=osd)
    rf = np.concatenate([rd[:k], rb[:k2], ro[:N - k - k2]])
    d = summ(rf)
    d["variant"] = name
    d["decomp_median"] = round(float(np.median(rd)), 2)
    d["decomp_mean"] = round(float(rd.mean()), 2)
    sens.append(d)


run_variant("base")
run_variant("nowcast centre 9.9 sd 0.85 (C-note band shape)", centre=9.9, sd=0.85)
run_variant("nowcast centre 9.75 sd 0.75", centre=9.75, sd=0.75)
run_variant("nowcast at the Street bar 11.1 sd 0.85", centre=11.1, sd=0.85)
run_variant("nowcast centre 9.0 sd 1.48 (team-low)", centre=9.0)
run_variant("nowcast centre 10.1 sd 1.48 (top of band / model path)", centre=10.1)
run_variant("S1 only (guide term dropped)", w_S1=1.0)
run_variant("S2 only (fragile guide slope fully trusted)", w_S1=0.0)
run_variant("no positioning term", pos=0.0)
run_variant("positioning term -2.5", pos=-2.5)
run_variant("residual sd 6.5", resid_sd=6.5)
run_variant("residual sd 8.8 (S1 n16)", resid_sd=8.8)
run_variant("guide gap mean 0 (guide at Street)", gap_mean=0.0)
run_variant("guide gap mean -3.5", gap_mean=-3.5)
run_variant("options anchor at B's 9.5 sd", osd=P["options_sd_B"])
run_variant("options anchor at 8.0 sd (thin 30 Oct leg)", osd=8.0)
for wd, wb, wo in [(1.0, 0, 0), (0.34, 0.33, 0.33), (0.6, 0.2, 0.2), (0.4, 0.2, 0.4), (0.0, 0.5, 0.5)]:
    rng = np.random.default_rng(SEED)
    rd = decomposition(rng)
    rb = base_rate(rng)
    ro = options_anchor(rng)
    a = int(N * wd)
    b = int(N * wb)
    rf = np.concatenate([rd[:a], rb[:b], ro[:N - a - b]])
    d = summ(rf)
    d["variant"] = f"weights decomposition {wd} / base rate {wb} / options {wo}"
    sens.append(d)
sens_df = pd.DataFrame(sens).set_index("variant")
sens_df.to_csv(HERE / "s01_sensitivity.csv")
print(sens_df.to_string())

# ---------- 5. outputs ----------
fin = est["FINAL_mixture"]
pd.DataFrame([{"percentile": p, "return_pct": fin[f"p{p}"]} for p in PCT]).to_csv(HERE / "s01_percentiles.csv", index=False)
pd.DataFrame([dict(threshold="P(<= -8%)", p=fin["p_le_m8"]), dict(threshold="P(<= -5%)", p=fin["p_le_m5"]), dict(threshold="P(< 0)", p=fin["p_lt_0"]),
              dict(threshold="P(>= +5%)", p=fin["p_ge_5"]), dict(threshold="P(>= +10%)", p=fin["p_ge_10"]), dict(threshold="P(|r| >= 7%)", p=fin["p_abs_ge_7"]),
              dict(threshold="P(|r| >= 10%)", p=fin["p_abs_ge_10"]), dict(threshold="P(>= +17%, squeeze repeat)", p=fin["p_ge_17"])]).to_csv(HERE / "s01_thresholds.csv", index=False)
json.dump(dict(params=P, states=p_states, estimates=est, conditional=cond, thesis_breaker_cell=breaker, cells_model=cellrows,
               qqq=dict(mean=qqq_mean, sd=qqq_sd), seed=SEED, n=N),
          open(HERE / "s01_components.json", "w"), indent=2, default=float)
print("done")
