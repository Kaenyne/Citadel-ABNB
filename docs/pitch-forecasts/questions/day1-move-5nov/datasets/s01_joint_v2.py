"""S01 day1-move-5nov, revision 2: ONE joint distribution over (print state, C01, C02, latent signal flag, day-1 return).
Every unconditional and conditional number in the revision-2 log derives from the same draws (A06-01, A06-02).
Deterministic (seed 20260917, n 600,000). Inputs: repo panel files only. Run from the repo root:
  py -3.13 docs/pitch-forecasts/questions/day1-move-5nov/datasets/s01_joint_v2.py
Outputs (this folder, all prefixed s01_v2_): windows.csv, cells.csv, estimates.csv, percentiles.csv, thresholds.csv,
  conditionals.csv, sensitivity.csv, slider.csv, components.json. Revision-1 files (s01_mixture.py, s01_*.csv) are untouched.

Structure (one joint draw per row)
  1. print state S in {decel (<10.09), flat (10.09-10.59), accel (>=10.59)} with the run's adopted masses
     (R01: P(>=10.0) = 0.42, R02: P(>=10.59) = 0.32 -> decel 0.595 / flat 0.085 / accel 0.32); nights | S from
     N(9.67, 1.70) (R01's calibrated normal) truncated to the state's band.
  2. C01: gap = guide midpoint / Street - 1 (%) ~ N(g0 + 0.32 (nights - 9.67), 3.1); g0 solved so P(gap < 0) = 0.72 (C01 rev 2).
  3. C02: P(c or d | S) = decel 0.76 / flat 0.45 / accel 0.37 (from C02 rev 2's branch table; unconditional 0.61), with a
     within-state odds ratio OR_C02 (default 2) between guide-below and guide-at/above draws.
  4. model return r_model = mu(S, gap, cd) + coef_err + resid + qqq, where
     mu = w1 * S1[S] + (1 - w1) * (c + b_sign * sign + b_gvs * gap) + pos * 1[decel] + c02_effect * 1[c or d]
     (S1/S2 = mean of the n16 and W1 fits, excess-return scale; C02 has no measured day-1 coefficient so c02_effect = 0),
     coef_err ~ N(0, 2.4), resid ~ 0.93 N(0, 6.9) + 0.07 N(0, 14), qqq ~ N(0, 1.4).
  5. latent Z ~ Bernoulli(kappa), independent of (S, C01, C02): the panel's directional signal holds. r = r_model if Z,
     else a directionless draw: with prob 0.5 the 23-print history (post-2022 x2, Gaussian kernel bw 3) and with prob 0.5
     N(0, 9.0) (the options-implied event sd, symmetric). kappa = 0.6. Because Z is independent of the cell, every
     conditional table is kappa x (model | cell) + (1 - kappa) x directionless, from the same draws.
  6. explicit bound mass 0.001 each side (draw replaced by U(-60,-40) / U(40,60)); every summary is of the final draws.
"""
import json, pathlib
import numpy as np, pandas as pd
from scipy.stats import truncnorm, norm

HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE.parents[4]
SEED = 20260917
N = 600_000
PCT = [5, 10, 25, 50, 75, 90, 95]

panel = pd.read_csv(ROOT / "data/processed/reverse_dcf/C/C_print_panel.csv")
rx = pd.read_csv(ROOT / "data/processed/abnb_earnings_reactions.csv")
ex = panel[panel.sample_ex_reopening].copy()

# ---------- 0. the reaction-function windows (A06-06): n16 ex-reopening, W1 (1Q23+, n14), W2 (1Q24+, n10) ----------
def ols(df, cols):
    X = np.column_stack([np.ones(len(df))] + [df[c].values for c in cols])
    y = df.ret_1d_cc_excess_pct.values
    beta = np.linalg.lstsq(X, y, rcond=None)[0]
    res = y - X @ beta
    sd = np.sqrt((res ** 2).sum() / (len(y) - len(beta)))
    loo = 0.0; base = 0.0
    for i in range(len(y)):
        m = np.arange(len(y)) != i
        b = np.linalg.lstsq(X[m], y[m], rcond=None)[0]
        loo += (y[i] - X[i] @ b) ** 2
        base += (y[i] - y[m].mean()) ** 2
    return beta, sd, 1 - loo / base

wins = {"n16 ex-reopening": ex, "W1 (2023Q1+)": ex[ex.print_quarter >= "2023Q1"], "W2 (2024Q1+)": ex[ex.print_quarter >= "2024Q1"]}
wrows = []
for wn, d in wins.items():
    b1, s1, l1 = ols(d, ["nights_accel_sign"])
    b2, s2, l2 = ols(d, ["nights_accel_sign", "guide_vs_street_pct"])
    wrows.append(dict(window=wn, n=len(d), S1_c=round(b1[0], 2), S1_b_sign=round(b1[1], 2), S1_resid_sd=round(s1, 2), S1_loo_r2=round(l1, 3),
                      S1_decel=round(b1[0] - b1[1], 2), S1_flat=round(b1[0], 2), S1_accel=round(b1[0] + b1[1], 2),
                      S2_c=round(b2[0], 2), S2_b_sign=round(b2[1], 2), S2_b_gvs=round(b2[2], 2), S2_resid_sd=round(s2, 2), S2_loo_r2=round(l2, 3),
                      decel_n=int((d.nights_accel_sign == -1).sum()), decel_mean_raw=round(d[d.nights_accel_sign == -1].ret_1d_cc_raw_pct.mean(), 2),
                      decel_pos_excess=int((d[d.nights_accel_sign == -1].ret_1d_cc_excess_pct > 0).sum()),
                      accel_n=int((d.nights_accel_sign == 1).sum()), accel_mean_raw=round(d[d.nights_accel_sign == 1].ret_1d_cc_raw_pct.mean(), 2)))
windows = pd.DataFrame(wrows)
windows.to_csv(HERE / "s01_v2_windows.csv", index=False)
print(windows.to_string(index=False))

# ---------- 1. parameters ----------
P = dict(
    # print state (R01 0.42 at >= 10.0, R02 0.32 at >= 10.59; flat band 10.09-10.59 interpolated)
    p_state={"decel": 0.595, "flat": 0.085, "accel": 0.32}, nights_centre=9.67, nights_sd=1.70, decel_thr=10.09, accel_thr=10.59,
    # C01 rev 2: median 3,100 vs Street 3,161, sd $97M (3.07%) + 0.6% drift; +$5M per +0.5pt nights = 0.32%/pt (A06-13)
    gap_sd=3.1, gap_tilt_per_pt=0.32, p_c01=0.72,
    # C02 rev 2: (c)+(d) 0.61; branch conditionals mapped to the dead band; within-state odds ratio vs C01
    p_cd={"decel": 0.76, "flat": 0.45, "accel": 0.37}, or_c02=2.0,
    # reaction function: mean of n16 and W1 fits (excess scale); W2 in s01_v2_windows.csv as the check
    S1={"accel": 3.95, "flat": -0.56, "decel": -5.06}, S2={"c": -1.41, "b_sign": 4.66, "b_gvs": 1.69},
    w_S1=0.75,                    # was 0.6: the guide term fails W2 (A06-06)
    positioning_decel=-1.0,       # JUDGEMENT: accelerating Street bar meets a decelerating print (unobserved cell)
    c02_effect=0.0,               # no measured day-1 coefficient on the bucket direction (claim 6)
    coef_sd=2.4, resid_sd_core=6.9, resid_sd_wide=14.0, resid_p_wide=0.07, qqq_sd=1.4,
    kappa=0.6,                    # P(the panel's directional signal holds); 1 - kappa = directionless
    dirless_hist_share=0.5,       # directionless branch: share from the 23-print history, remainder options N(0, options_sd)
    kde_bw=3.0, post2022_weight=2.0, options_sd=9.0,
    bound=40.0, bound_mass=0.001,
)


def solve_g0(p):
    """g0 such that the unconditional P(gap < 0) = p_c01 under the state mixture (numerical, on the nights distribution)."""
    lo, hi = -6.0, 3.0
    for _ in range(60):
        mid = (lo + hi) / 2
        pb = 0.0
        for s, ps in p["p_state"].items():
            a, b = {"decel": (-np.inf, p["decel_thr"]), "flat": (p["decel_thr"], p["accel_thr"]), "accel": (p["accel_thr"], np.inf)}[s]
            xs = np.linspace(max(a, 3.0), min(b, 17.0), 400)
            w = norm.pdf(xs, p["nights_centre"], p["nights_sd"]); w /= w.sum()
            pb += ps * (w * norm.cdf(-(mid + p["gap_tilt_per_pt"] * (xs - p["nights_centre"])) / p["gap_sd"])).sum()
        if pb > p["p_c01"]:
            lo = mid            # too much mass below zero: raise the gap mean
        else:
            hi = mid
    return (lo + hi) / 2


def c02_split(marg, p_below, orr):
    """p_b, p_a with p_below*p_b + (1-p_below)*p_a = marg and odds(p_b) = orr*odds(p_a)."""
    lo, hi = 1e-6, 1 - 1e-6
    for _ in range(60):
        pa = (lo + hi) / 2
        pb = orr * pa / (1 - pa + orr * pa)
        if p_below * pb + (1 - p_below) * pa > marg:
            hi = pa
        else:
            lo = pa
    pa = (lo + hi) / 2
    return orr * pa / (1 - pa + orr * pa), pa


def simulate(p, n=N, seed=SEED, kappa=None, S1=None):
    rng = np.random.default_rng(seed)
    kappa = p["kappa"] if kappa is None else kappa
    S1 = p["S1"] if S1 is None else S1
    states = np.array(["decel", "flat", "accel"])
    ps = np.array([p["p_state"][s] for s in states])
    st = rng.choice(3, n, p=ps / ps.sum())
    nights = np.empty(n)
    bands = {0: (-np.inf, p["decel_thr"]), 1: (p["decel_thr"], p["accel_thr"]), 2: (p["accel_thr"], np.inf)}
    for i, (a, b) in bands.items():
        m = st == i
        nights[m] = truncnorm.rvs((a - p["nights_centre"]) / p["nights_sd"], (b - p["nights_centre"]) / p["nights_sd"],
                                  loc=p["nights_centre"], scale=p["nights_sd"], size=m.sum(), random_state=rng)
    sign = np.where(st == 2, 1, np.where(st == 0, -1, 0))
    g0 = solve_g0(p)
    gap = rng.normal(g0 + p["gap_tilt_per_pt"] * (nights - p["nights_centre"]), p["gap_sd"], n)
    below = gap < 0
    # C02 given state and C01
    cd = np.zeros(n, bool)
    splits = {}
    for i, s in enumerate(states):
        m = st == i
        pbelow = below[m].mean()
        pb, pa = c02_split(p["p_cd"][s], pbelow, p["or_c02"])
        splits[s] = dict(p_below_given_state=round(float(pbelow), 3), p_cd_given_below=round(pb, 3), p_cd_given_above=round(pa, 3))
        u = rng.random(m.sum())
        cd[m] = np.where(below[m], u < pb, u < pa)
    # model branch
    s1 = np.select([sign == 1, sign == 0], [S1["accel"], S1["flat"]], S1["decel"])
    s2 = p["S2"]["c"] + p["S2"]["b_sign"] * sign + p["S2"]["b_gvs"] * gap
    mu = p["w_S1"] * s1 + (1 - p["w_S1"]) * s2 + np.where(sign == -1, p["positioning_decel"], 0.0) + p["c02_effect"] * cd
    wide = rng.random(n) < p["resid_p_wide"]
    resid = np.where(wide, rng.normal(0, p["resid_sd_wide"], n), rng.normal(0, p["resid_sd_core"], n))
    r_model = mu + rng.normal(0, p["coef_sd"], n) + resid + rng.normal(0, p["qqq_sd"], n)
    # directionless branch: history KDE and symmetric options normal
    x = rx.abnb_1d_pct.values
    w = np.where(rx.quarter >= "2023Q1", p["post2022_weight"], 1.0); w = w / w.sum()
    r_hist = x[rng.choice(len(x), n, p=w)] + rng.normal(0, p["kde_bw"], n)
    r_opt = rng.normal(0, p["options_sd"], n)
    r_dirless = np.where(rng.random(n) < p["dirless_hist_share"], r_hist, r_opt)
    z = rng.random(n) < kappa
    r = np.where(z, r_model, r_dirless)
    # explicit bound mass, one distribution (A06-15)
    u = rng.random(n)
    r = np.where(u < p["bound_mass"], rng.uniform(-60, -40, n), np.where(u > 1 - p["bound_mass"], rng.uniform(40, 60, n), r))
    return dict(r=r, r_model=r_model, r_hist=r_hist, r_opt=r_opt, st=st, sign=sign, nights=nights, gap=gap, below=below, cd=cd, mu=mu, z=z,
                g0=g0, splits=splits)


def summ(r):
    d = {f"p{p}": round(float(np.percentile(r, p)), 2) for p in PCT}
    d.update(mean=round(float(r.mean()), 2), sd=round(float(r.std()), 2), rms=round(float(np.sqrt((r ** 2).mean())), 2),
             p_le_m8=round(float((r <= -8).mean()), 3), p_le_m5=round(float((r <= -5).mean()), 3), p_lt_0=round(float((r < 0).mean()), 3),
             p_ge_5=round(float((r >= 5).mean()), 3), p_ge_10=round(float((r >= 10).mean()), 3), p_abs_ge_7=round(float((np.abs(r) >= 7).mean()), 3),
             p_abs_ge_10=round(float((np.abs(r) >= 10).mean()), 3), p_abs_ge_15=round(float((np.abs(r) >= 15).mean()), 4),
             p_lt_m15=round(float((r < -15).mean()), 4), p_lt_m25=round(float((r < -25).mean()), 4), p_ge_17=round(float((r >= 17).mean()), 4),
             below_m40=round(float((r < -40).mean()), 4), above_p40=round(float((r > 40).mean()), 4), n=int(len(r)))
    return d


# ---------- 2. the three estimates and the final, from one draw ----------
J = simulate(P)
rng0 = np.random.default_rng(SEED + 7)
sdd, sdu = P["options_sd"] * 1.10, P["options_sd"] * 0.90        # rev-1 two-piece, kept as a labelled judgement
zz = np.abs(rng0.normal(0, 1, N)); side = rng0.random(N) < sdd / (sdd + sdu)
r_anchor_skew = -0.3 + np.where(side, -zz * sdd, zz * sdu)
est = {"base_rate_history_kde": summ(J["r_hist"]), "decomposition_model_branch": summ(J["r_model"]), "anchor_options_symmetric": summ(J["r_opt"]),
       "anchor_two_piece_rev1_judgement": summ(r_anchor_skew), "FINAL_joint": summ(J["r"])}
est_df = pd.DataFrame(est).T
est_df.to_csv(HERE / "s01_v2_estimates.csv")
print(est_df.to_string())
fin = est["FINAL_joint"]
print("g0 (gap mean at nights centre):", round(J["g0"], 3), "C02 splits:", J["splits"])

# ---------- 3. cells and conditionals, all from the FINAL draws ----------
r, st, below, cd, sign, z = J["r"], J["st"], J["below"], J["cd"], J["sign"], J["z"]
names = {0: "decel", 1: "flat", 2: "accel"}
cells = []
for i in range(3):
    for b in (True, False):
        for c in (True, False):
            m = (st == i) & (below == b) & (cd == c)
            cells.append(dict(state=names[i], c01_below=b, c02_cd=c, prob=round(float(m.mean()), 4), model_mean=round(float(J["r_model"][m].mean()), 2), **summ(r[m])))
cells_df = pd.DataFrame(cells)
cells_df.to_csv(HERE / "s01_v2_cells.csv", index=False)
print(cells_df[["state", "c01_below", "c02_cd", "prob", "model_mean", "mean", "p50", "p_lt_0", "p_le_m8", "p_ge_5"]].to_string(index=False))
cond = {}
masks = {
    "base case: decel & C01 below & C02 c/d (three gates)": (st == 0) & below & cd,
    "base case, model branch only (Z = 1)": (st == 0) & below & cd & z,
    "two gates: decel & C01 below": (st == 0) & below,
    "decel (any)": st == 0,
    "flat (any)": st == 1,
    "accel (any)": st == 2,
    "thesis breaker: accel & C01 at/above": (st == 2) & ~below,
    "thesis breaker, model branch only (Z = 1)": (st == 2) & ~below & z,
    "accel & C01 below": (st == 2) & below,
    "decel & C01 at/above": (st == 0) & ~below,
    "C01 below (any print)": below,
    "C01 at/above (any print)": ~below,
    "C02 c/d (any print)": cd,
    "C02 a/b/e (any print)": ~cd,
    "nights >= 10.0 (R01 Yes)": J["nights"] >= 10.0,
    "nights < 10.0 (R01 No)": J["nights"] < 10.0,
}
for k, m in masks.items():
    cond[k] = dict(prob=round(float(m.mean()), 4), **summ(r[m]))
cond_df = pd.DataFrame(cond).T
cond_df.to_csv(HERE / "s01_v2_conditionals.csv")
print(cond_df[["prob", "p5", "p25", "p50", "p75", "p95", "mean", "sd", "p_lt_0", "p_le_m8", "p_le_m5", "p_ge_5", "p_ge_10"]].to_string())
states = dict(p_decel=round(float((st == 0).mean()), 3), p_flat=round(float((st == 1).mean()), 3), p_accel=round(float((st == 2).mean()), 3),
              p_ge_10_0=round(float((J["nights"] >= 10.0).mean()), 3), p_c01_below=round(float(below.mean()), 3),
              p_below_given_decel=round(float(below[st == 0].mean()), 3), p_below_given_accel=round(float(below[st == 2].mean()), 3),
              p_c02_cd=round(float(cd.mean()), 3), p_cd_given_decel=round(float(cd[st == 0].mean()), 3),
              p_cd_given_decel_below=round(float(cd[(st == 0) & below].mean()), 3),
              p_base_case=round(float(((st == 0) & below & cd).mean()), 3), p_two_gate=round(float(((st == 0) & below).mean()), 3),
              p_breaker=round(float(((st == 2) & ~below).mean()), 3), p_z=round(float(z.mean()), 3))
print(states)

# ---------- 4. sensitivities: single-assumption reruns of the FINAL joint model ----------
sens = []


def variant(name, **kw):
    q = json.loads(json.dumps(P))
    kappa = kw.pop("kappa", None); S1 = kw.pop("S1", None)
    for k, v in kw.items():
        if isinstance(v, dict) and isinstance(q.get(k), dict):
            q[k].update(v)
        else:
            q[k] = v
    Jv = simulate(q, kappa=kappa, S1=S1)
    d = summ(Jv["r"]); d["variant"] = name
    mb = (Jv["st"] == 0) & Jv["below"] & Jv["cd"]
    d["base_case_prob"] = round(float(mb.mean()), 3); d["base_case_p50"] = round(float(np.median(Jv["r"][mb])), 2)
    d["base_case_p_le_m8"] = round(float((Jv["r"][mb] <= -8).mean()), 3); d["base_case_p_lt_0"] = round(float((Jv["r"][mb] < 0).mean()), 3)
    mk = (Jv["st"] == 2) & ~Jv["below"]
    d["breaker_prob"] = round(float(mk.mean()), 3); d["breaker_p50"] = round(float(np.median(Jv["r"][mk])), 2); d["breaker_p_ge_5"] = round(float((Jv["r"][mk] >= 5).mean()), 3)
    sens.append(d)
    return d


variant("base (revision 2)")
variant("print states rev-1 N(9.55,1.48): decel .642 / flat .116 / accel .241", p_state={"decel": 0.642, "flat": 0.116, "accel": 0.241}, nights_centre=9.55, nights_sd=1.48)
variant("print states Street/Kalshi N(11.0,1.7): decel .30 / flat .10 / accel .60", p_state={"decel": 0.30, "flat": 0.10, "accel": 0.60}, nights_centre=11.0)
variant("print states R01 normal N(9.67,1.70) untouched: decel .598 / flat .108 / accel .294", p_state={"decel": 0.598, "flat": 0.108, "accel": 0.294})
variant("print states team-low centre 9.0 sd 1.70: decel .74 / flat .09 / accel .17", p_state={"decel": 0.74, "flat": 0.09, "accel": 0.17}, nights_centre=9.0)
variant("kappa 0.4", kappa=0.4)
variant("kappa 0.5 (rev-1 mixture weight)", kappa=0.5)
variant("kappa 0.8", kappa=0.8)
variant("kappa 1.0 (model branch only, no shrinkage)", kappa=1.0)
variant("kappa 0 (directionless only: history + options)", kappa=0.0)
variant("directionless branch = options N(0,9) only", dirless_hist_share=0.0)
variant("directionless branch = history KDE only", dirless_hist_share=1.0)
variant("history KDE bandwidth 2 (thinner smoothed tail)", kde_bw=2.0)
variant("history KDE unweighted (no post-2022 x2)", post2022_weight=1.0)
variant("S1 from W2 alone (decel -6.89 / flat +0.40 / accel +7.69)", S1={"accel": 7.69, "flat": 0.40, "decel": -6.89})
variant("S1 from n16 alone (decel -4.02 / flat -0.67 / accel +2.69)", S1={"accel": 2.69, "flat": -0.67, "decel": -4.02})
variant("guide term weight 0 (S1 only)", w_S1=1.0)
variant("guide term weight 0.4 (rev 1)", w_S1=0.6)
variant("no positioning term", positioning_decel=0.0)
variant("positioning term -2.5", positioning_decel=-2.5)
variant("C02 return effect -1.0 on c/d", c02_effect=-1.0)
variant("C02 return effect -2.0 on c/d", c02_effect=-2.0)
variant("C02 independent of C01 within state (OR 1)", or_c02=1.0)
variant("C02 odds ratio 4 within state", or_c02=4.0)
variant("C02 (c+d) 0.50 overall (decel .65 / flat .35 / accel .28)", p_cd={"decel": 0.65, "flat": 0.35, "accel": 0.28})
variant("C01 P(below) 0.62 (Astra / C01 low)", p_c01=0.62)
variant("C01 P(below) 0.82 (C01 high)", p_c01=0.82)
variant("C01 gap sd 2.8 (rev 1)", gap_sd=2.8)
variant("residual core sd 6.5", resid_sd_core=6.5)
variant("residual core sd 7.5 (rev 1)", resid_sd_core=7.5)
variant("wide component 0 (pure normal core 7.4)", resid_p_wide=0.0, resid_sd_core=7.4)
variant("wide component 0.12", resid_p_wide=0.12)
variant("options sd 8.0 (thin 30 Oct leg)", options_sd=8.0)
variant("options sd 9.5 (B note)", options_sd=9.5)
variant("QQQ sd 2.0 (macro day)", qqq_sd=2.0)
variant("coefficient sampling sd 3.5", coef_sd=3.5)
sens_df = pd.DataFrame(sens).set_index("variant")
sens_df.to_csv(HERE / "s01_v2_sensitivity.csv")
print(sens_df[["p5", "p25", "p50", "p75", "p95", "sd", "p_le_m8", "p_le_m5", "p_lt_0", "p_ge_5", "p_ge_10", "p_abs_ge_10", "p_abs_ge_15",
               "base_case_prob", "base_case_p50", "base_case_p_le_m8", "base_case_p_lt_0", "breaker_prob", "breaker_p50", "breaker_p_ge_5"]].to_string())

# ---------- 5. Astra's independent construction, replayed for the comparison table ----------
Phi = norm.cdf
st_a = {-1: Phi((10.09 - 9.55) / 1.48), 1: 1 - Phi((10.59 - 9.55) / 1.48)}; st_a[0] = 1 - sum(st_a.values())
bel = {-1: .77, 0: .72}; bel[1] = (.72 - sum(st_a[s] * bel[s] for s in (-1, 0))) / st_a[1]
prior = float(ex.ret_1d_cc_raw_pct.mean())
acells = []
for sg in (-1, 0, 1):
    for isb in (True, False):
        smp = ex[(ex.nights_accel_sign == sg) & ((ex.guide_vs_street_pct < 0) == isb)]
        acells.append((st_a[sg] * (bel[sg] if isb else 1 - bel[sg]), (smp.ret_1d_cc_raw_pct.sum() + 4 * prior) / (len(smp) + 4)))
def acdf(xv, comps=acells):
    return sum(wt * (.95 * Phi((xv - mu) / 8) + .05 * Phi((xv - mu) / 18)) for wt, mu in comps)
def aq(cdf, pr):
    lo, hi = -200.0, 200.0
    for _ in range(80):
        mid = (lo + hi) / 2
        lo, hi = (mid, hi) if cdf(mid) < pr else (lo, mid)
    return (lo + hi) / 2
astra = {f"p{p}": round(aq(acdf, p / 100), 2) for p in PCT}
astra.update(p_le_m8=round(float(acdf(-8)), 3), p_le_m5=round(float(acdf(-5)), 3), p_lt_0=round(float(acdf(0)), 3), p_ge_5=round(float(1 - acdf(5)), 3),
             p_ge_10=round(float(1 - acdf(10)), 3), p_abs_ge_7=round(float(acdf(-7) + 1 - acdf(7)), 3), p_abs_ge_10=round(float(acdf(-10) + 1 - acdf(10)), 3),
             p_abs_ge_15=round(float(acdf(-15) + 1 - acdf(15)), 4), p_lt_m25=round(float(acdf(-25)), 4),
             base_prob=round(st_a[-1] * .77 * .80, 3), base_p50=round(aq(lambda v: acdf(v, [(1.0, acells[0][1])]), .5), 2),
             base_p_le_m8=round(float(acdf(-8, [(1.0, acells[0][1])])), 3), base_p_lt_0=round(float(acdf(0, [(1.0, acells[0][1])])), 3),
             cell_means_shrunk={f"sign{sg}_below{isb}": round(mu, 2) for (sg, isb), (wt, mu) in zip([(s, b) for s in (-1, 0, 1) for b in (True, False)], acells)})
print("Astra replay:", astra)

# ---------- 6. slider approximation (3 Gaussians fitted to the FINAL draws; max CDF error reported) ----------
from sklearn.mixture import GaussianMixture
sub = r[(r > -40) & (r < 40)][:150_000].reshape(-1, 1)
gm = GaussianMixture(3, random_state=SEED).fit(sub)
grid = np.linspace(-40, 40, 801)
emp = np.searchsorted(np.sort(r), grid) / len(r)
gcdf = sum(wt * Phi((grid - mu) / np.sqrt(v)) for wt, mu, v in zip(gm.weights_, gm.means_.ravel(), gm.covariances_.ravel()))
gcdf = P["bound_mass"] + (1 - 2 * P["bound_mass"]) * gcdf
slider = pd.DataFrame(dict(component=list("ABC"), centre=np.round(gm.means_.ravel(), 2), sd=np.round(np.sqrt(gm.covariances_.ravel()), 2), weight=np.round(gm.weights_, 3)))
slider["max_abs_cdf_error"] = round(float(np.abs(emp - gcdf).max()), 4)
slider.to_csv(HERE / "s01_v2_slider.csv", index=False)
print(slider.to_string(index=False))

# ---------- 7. history coverage of the final 5-95 interval ----------
xall = rx.abnb_1d_pct.values
cov_all = int(((xall >= fin["p5"]) & (xall <= fin["p95"])).sum())
xex = ex.ret_1d_cc_raw_pct.values
cov_ex = int(((xex >= fin["p5"]) & (xex <= fin["p95"])).sum())
print(f"5-95 interval [{fin['p5']}, {fin['p95']}] covers {cov_all}/23 all prints, {cov_ex}/16 ex-reopening; outside:",
      sorted([float(v) for v in xall if v < fin["p5"] or v > fin["p95"]]))

# ---------- 8. outputs ----------
pd.DataFrame([{"percentile": p, "return_pct": fin[f"p{p}"]} for p in PCT]).to_csv(HERE / "s01_v2_percentiles.csv", index=False)
pd.DataFrame([dict(threshold=k, p=v) for k, v in [("P(<= -8%)", fin["p_le_m8"]), ("P(<= -5%)", fin["p_le_m5"]), ("P(< 0)", fin["p_lt_0"]),
              ("P(>= +5%)", fin["p_ge_5"]), ("P(>= +10%)", fin["p_ge_10"]), ("P(|r| >= 7%)", fin["p_abs_ge_7"]), ("P(|r| >= 10%)", fin["p_abs_ge_10"]),
              ("P(|r| >= 15%)", fin["p_abs_ge_15"]), ("P(< -15%)", fin["p_lt_m15"]), ("P(< -25%)", fin["p_lt_m25"]), ("P(>= +17%)", fin["p_ge_17"]),
              ("P(< -40)", fin["below_m40"]), ("P(> +40)", fin["above_p40"])]]).to_csv(HERE / "s01_v2_thresholds.csv", index=False)
json.dump(dict(params=P, g0=J["g0"], c02_splits=J["splits"], states=states, estimates=est, conditionals=cond, cells=cells, astra_replay=astra,
               slider=slider.to_dict("records"), windows=wrows, coverage={"all23": cov_all, "ex16": cov_ex}, seed=SEED, n=N),
          open(HERE / "s01_v2_components.json", "w"), indent=2, default=float)
print("done")
