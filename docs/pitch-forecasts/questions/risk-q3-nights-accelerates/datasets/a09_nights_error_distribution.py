"""A09 (R01, R02, R03): 3Q26 nights print distribution from the team's reviews-index nowcast and its
measured walk-forward error, the management-delivery view, the Kalshi ladder, and the R03 joint with the
RNPL GBV share. Standard library + numpy + pandas. Deterministic (seed 20260917).

Run from anywhere:  py -3.13 a09_nights_error_distribution.py
Reads (repo, read-only):
  data/processed/q3nowcast/E/q3_2026_nowcast.csv, E_aug/q3_2026_nowcast.csv   (seven implied-nights rows)
  data/processed/q3nowcast/E/backtest_wf_paths.csv, E_aug/backtest_wf_paths.csv (walk-forward errors, pred - actual)
  data/processed/q3nowcast_v2/E/t1_fail_e5_rerun.csv                           (revintaged RMSE ratios)
Writes, into the datasets/ folder of each of the three questions:
  a09_rows_and_errors.csv, a09_alt_data_estimates.csv, a09_sd_sensitivity.csv, a09_base_rates.csv,
  a09_three_views.csv, a09_final.json, a09_r03_joint.csv, a09_impact.csv
"""
from __future__ import annotations
import json, math, pathlib, csv
import numpy as np
import pandas as pd

HERE = pathlib.Path(__file__).resolve()
QDIR = HERE.parents[2]                      # docs/pitch-forecasts/questions
ROOT = HERE.parents[5]                      # repo root
OUTS = [QDIR / s / "datasets" for s in ("risk-q3-nights-meets-guide", "risk-q3-nights-accelerates",
                                        "risk-july-rnpl-expansion-offsets-lap")]
for o in OUTS:
    o.mkdir(parents=True, exist_ok=True)
rng = np.random.default_rng(20260917)
N = 400_000

T_R01, T_R02 = 10.0, 10.6                   # question thresholds, % y/y on 133.6m
BASE_3Q25 = 133.6

def save(name: str, df: pd.DataFrame | dict):
    for o in OUTS:
        p = o / name
        if isinstance(df, dict):
            p.write_text(json.dumps(df, indent=1), encoding="utf-8")
        else:
            df.to_csv(p, index=False)

def phi(x):  # standard normal cdf
    return 0.5 * (1 + math.erf(x / math.sqrt(2)))

# ------------------------------------------------------------------ 1. rows and their WF errors
FEAT = {  # (measure, weighting, region) -> feature key in backtest_wf_paths
    ("yoy_all", "w_reviews", "GLOBAL"): "GLOBAL|yoy_all|w_reviews",
    ("yoy_all", "w_equal", "GLOBAL"): "GLOBAL|yoy_all|w_equal",
    ("yoy_all", "w_median", "GLOBAL"): "GLOBAL|yoy_all|w_median",
    ("yoy_all", "w_equal", "GLOBAL_NW"): "GLOBAL_NW|yoy_all|w_equal",
    ("yoy_vmatch", "w_reviews", "GLOBAL"): "GLOBAL|yoy_vmatch|w_reviews",
    ("yoy_vmatch", "w_equal", "GLOBAL"): "GLOBAL|yoy_vmatch|w_equal",
    ("yoy_vmatch", "w_equal", "GLOBAL_NW"): "GLOBAL_NW|yoy_vmatch|w_equal",
}
rows = []
for run in ("E", "E_aug"):
    nc = pd.read_csv(ROOT / "data/processed/q3nowcast" / run / "q3_2026_nowcast.csv")
    wf = pd.read_csv(ROOT / "data/processed/q3nowcast" / run / "backtest_wf_paths.csv")
    wf = wf[(wf["target"] == "nights_yoy") & (wf["lag"] == 0)]
    for _, r in nc.iterrows():
        key = FEAT[(r["measure"], r["weighting"], r["region"])]
        for window in ("2023Q1+", "2022Q1+"):
            e = wf[(wf["feature"] == key) & (wf["window"] == window)].sort_values("qi")
            if e.empty:
                continue
            errs = e["err_feature"].to_numpy()           # pred - actual, pp
            naive = e["err_naive"].to_numpy()
            quarters = [f"{q // 4}Q{q % 4 + 1}" for q in e["qi"].astype(int)]
            rows.append(dict(run=run, feature=key, window=window, implied=r["implied_nights_yoy"],
                             implied_anchored_2q26=r["implied_nights_yoy_anchored_2q26"],
                             band_pp=r["band_pp"], n=len(errs), err_mean=errs.mean(),
                             err_sd=errs.std(ddof=1), rmse=math.sqrt((errs ** 2).mean()),
                             rmse_naive=math.sqrt((naive ** 2).mean()),
                             n_over=int((errs > 0).sum()), quarters=" ".join(quarters),
                             errors=" ".join(f"{x:+.2f}" for x in errs)))
rows_df = pd.DataFrame(rows)
save("a09_rows_and_errors.csv", rows_df)

# ------------------------------------------------------------------ 2. alt-data probability constructions
def p_ge(samples, t):
    return float((samples >= t).mean())

est = []
# 2a. the headline construction used by C02/S01: N(9.55, 1.48)
for c, s in ((9.55, 1.48), (9.55, 1.70), (9.9, 1.48), (9.5, 1.48), (9.2, 1.48)):
    est.append(dict(construction=f"normal centre {c} sd {s}", p_r01=1 - phi((T_R01 - c) / s),
                    p_r02=1 - phi((T_R02 - c) / s), centre=c, sd=s, note="parametric"))
# 2b. each row, empirical WF errors (2023Q1+ window, E_aug values), plug-in and kernel-smoothed (bw 0.5)
sub = rows_df[(rows_df.run == "E_aug") & (rows_df.window == "2023Q1+")]
mix_plug, mix_kern, mix_bc = [], [], []
for _, r in sub.iterrows():
    errs = np.array([float(x) for x in r["errors"].split()])
    actual_draws = r["implied"] - errs                              # actual = pred - err
    kern = r["implied"] - (rng.choice(errs, N) + rng.normal(0, 0.5, N))
    bc = rng.normal(r["implied"] - r["err_mean"], r["rmse"], N)     # bias-corrected normal
    est.append(dict(construction=f"{r['feature']} plug-in (10 WF errors)", p_r01=p_ge(actual_draws, T_R01),
                    p_r02=p_ge(actual_draws, T_R02), centre=r["implied"], sd=r["rmse"], note="pred-actual errors applied to the implied level"))
    est.append(dict(construction=f"{r['feature']} kernel bw 0.5", p_r01=p_ge(kern, T_R01), p_r02=p_ge(kern, T_R02),
                    centre=r["implied"], sd=r["rmse"], note="resampled errors + N(0,0.5)"))
    est.append(dict(construction=f"{r['feature']} bias-corrected normal", p_r01=p_ge(bc, T_R01), p_r02=p_ge(bc, T_R02),
                    centre=r["implied"] - r["err_mean"], sd=r["rmse"], note="centre = implied - mean WF error"))
    mix_plug.append(actual_draws); mix_kern.append(kern); mix_bc.append(bc)
mix_kern = np.concatenate(mix_kern); mix_bc = np.concatenate(mix_bc); mix_plug = np.concatenate(mix_plug)
est.append(dict(construction="SEVEN-ROW MIXTURE plug-in", p_r01=p_ge(mix_plug, T_R01), p_r02=p_ge(mix_plug, T_R02),
                centre=float(np.mean(mix_plug)), sd=float(np.std(mix_plug)), note="equal weight over the seven level rows"))
est.append(dict(construction="SEVEN-ROW MIXTURE kernel", p_r01=p_ge(mix_kern, T_R01), p_r02=p_ge(mix_kern, T_R02),
                centre=float(np.mean(mix_kern)), sd=float(np.std(mix_kern)), note="equal weight over the seven level rows"))
est.append(dict(construction="SEVEN-ROW MIXTURE bias-corrected normal", p_r01=p_ge(mix_bc, T_R01), p_r02=p_ge(mix_bc, T_R02),
                centre=float(np.mean(mix_bc)), sd=float(np.std(mix_bc)), note="equal weight over the seven level rows"))
# 2c. revintaged: widen every row's error by the WPK ratio (0.757/0.683 = 1.108 honest; 0.841/0.683 = 1.231 literal)
rev = pd.read_csv(ROOT / "data/processed/q3nowcast_v2/E/t1_fail_e5_rerun.csv")
r_v1 = float(rev.loc[rev.variant.str.startswith("v1"), "wf_ratio_vs_naive"].iloc[0])
r_b = float(rev.loc[rev.variant.str.startswith("b:"), "wf_ratio_vs_naive"].iloc[0])
r_a = float(rev.loc[rev.variant.str.startswith("a:"), "wf_ratio_vs_naive"].iloc[0])
for label, f in (("honest 0.757", r_b / r_v1), ("literal 0.841", r_a / r_v1)):
    draws = []
    for _, r in sub.iterrows():
        errs = np.array([float(x) for x in r["errors"].split()])
        draws.append(r["implied"] - (rng.choice(errs, N) * f + rng.normal(0, 0.5, N)))
    d = np.concatenate(draws)
    est.append(dict(construction=f"SEVEN-ROW MIXTURE kernel, errors x{f:.3f} (revintaged {label})",
                    p_r01=p_ge(d, T_R01), p_r02=p_ge(d, T_R02), centre=float(d.mean()), sd=float(d.std()),
                    note="WPK T1 fail branch scaling of the 2023Q1+ WF errors"))
# 2d. the anchored-on-2Q26 rows (a first-difference construction; E5 says first differences never beat naive)
anch = sub["implied_anchored_2q26"].to_numpy()
d = np.concatenate([rng.normal(a, 1.48 * 1.47, N // 7) for a in anch])   # naive-losing ratio 1.47 -> sd 2.18
est.append(dict(construction="anchored-on-2Q26 rows (first-difference family), sd 2.18", p_r01=p_ge(d, T_R01),
                p_r02=p_ge(d, T_R02), centre=float(anch.mean()), sd=2.18, note="reported, not used: first differences lose to naive (E note 2.6)"))
est_df = pd.DataFrame(est)
save("a09_alt_data_estimates.csv", est_df)

# ------------------------------------------------------------------ 3. sd sensitivity grid (fine print)
grid = []
for c in (9.2, 9.5, 9.55, 9.9, 10.0, 10.3):
    for s in (1.0, 1.25, 1.48, 1.63, 1.70, 1.82, 2.16, 2.5):
        grid.append(dict(centre=c, sd=s, p_r01=round(1 - phi((T_R01 - c) / s), 3), p_r02=round(1 - phi((T_R02 - c) / s), 3)))
save("a09_sd_sensitivity.csv", pd.DataFrame(grid))

# ------------------------------------------------------------------ 4. base rates
# disclosed nights y/y, 1Q22..2Q26 (letters; 02_guidance_ledger comparator/actual columns, driver history)
nights_yoy = {"1Q22": 58.5, "2Q22": 24.6, "3Q22": 25.1, "4Q22": 20.2, "1Q23": 18.6, "2Q23": 11.0, "3Q23": 13.5,
              "4Q23": 12.0, "1Q24": 9.5, "2Q24": 8.7, "3Q24": 8.5, "4Q24": 12.35, "1Q25": 7.9, "2Q25": 7.4,
              "3Q25": 8.8, "4Q25": 9.8, "1Q26": 9.15, "2Q26": 10.34}
keys = list(nights_yoy)
chg = [(keys[i], nights_yoy[keys[i]] - nights_yoy[keys[i - 1]]) for i in range(2, len(keys))]  # from 3Q22
need_r01 = T_R01 - 10.34      # -0.34: the print may decelerate by at most 0.34
need_r02 = T_R02 - 10.34      # +0.26
br = []
for label, sample in (("all sequential changes 3Q22-2Q26", chg), ("post-2023 (1Q24-2Q26)", [c for c in chg if c[0] >= "1Q24" and c[0][-2:] >= "24"]),
                      ("Q3 transitions only (3Q22, 3Q23, 3Q24, 3Q25)", [c for c in chg if c[0].startswith("3Q")])):
    n = len(sample)
    k1 = sum(1 for _, d in sample if d >= need_r01); k2 = sum(1 for _, d in sample if d >= need_r02)
    br.append(dict(reference_class=label, n=n, k_r01=k1, p_r01=k1 / n, p_r01_laplace=(k1 + 1) / (n + 2),
                   k_r02=k2, p_r02=k2 / n, p_r02_laplace=(k2 + 1) / (n + 2),
                   members=" ".join(f"{q}:{d:+.2f}" for q, d in sample)))
# management-delivery view: floor 10.0 + cushion + management forecast error
# cushion: bucket era beats above the midpoint +4.8 (4Q25) and +1.15 (1Q26) were on buckets set 1-4pts BELOW the printed
# rate; this bucket is set AT the printed rate, so the cushion is scaled down: c ~ N(0.6, 0.5) (sensitivity 0.3 / 1.0)
# management error around its own expectation: stable-guide outcomes (+0.49, -1.59, -0.81, -0.58, +1.39) and the 1Q26
# "slightly decelerate" miss (+1.2 vs ~-0.5 implied): sd ~1.3
mg = []
for cmean in (0.3, 0.6, 1.0):
    for esd in (1.0, 1.3, 1.6):
        s = math.sqrt(0.5 ** 2 + esd ** 2)
        mg.append(dict(cushion_mean=cmean, mgmt_err_sd=esd, p_r01=1 - phi((0 - cmean) / s), p_r02=1 - phi((0.6 - cmean) / s)))
mg_df = pd.DataFrame(mg)
raw_record = dict(reference_class="management nights guides met (directional + bucket, 2Q22-2Q26, ledger)", n=16, k_r01=15,
                  p_r01=15 / 16, p_r01_laplace=16 / 18, k_r02=None, p_r02=None, p_r02_laplace=None,
                  members="15 met, 1 not met in the company's favour (1Q26->2Q26 'slightly decelerate', printed +1.2); 1Q25 'stable' printed -0.58 is coded met (E note: soft miss)")
br.append(raw_record)
br_df = pd.DataFrame(br)
save("a09_base_rates.csv", br_df)
save("a09_mgmt_delivery_view.csv", mg_df)

# ------------------------------------------------------------------ 5. Kalshi ladder (mid prices, 2026-09-17T03:21:58Z)
kalshi = {150: (0.32, 0.36), 148: (0.50, 0.55), 146: (0.63, 0.66), 144: (0.76, 0.83), 142: (0.84, 0.92), 140: (0.89, 0.96), 138: (0.94, 0.97)}
mids = {k: (b + a) / 2 for k, (b, a) in kalshi.items()}
def interp(m):  # linear interpolation of P(> m) between strikes
    ks = sorted(mids)
    for lo, hi in zip(ks, ks[1:]):
        if lo <= m <= hi:
            return mids[lo] + (mids[hi] - mids[lo]) * (m - lo) / (hi - lo)
    return float("nan")
k_r01 = interp(BASE_3Q25 * (1 + T_R01 / 100))     # 146.96m
k_r02 = interp(BASE_3Q25 * (1 + T_R02 / 100))     # 147.76m

# ------------------------------------------------------------------ 6. three views and the blend
alt_r01 = float(est_df.loc[est_df.construction.str.startswith("SEVEN-ROW MIXTURE kernel, errors x1.1"), "p_r01"].iloc[0])
alt_r02 = float(est_df.loc[est_df.construction.str.startswith("SEVEN-ROW MIXTURE kernel, errors x1.1"), "p_r02"].iloc[0])
alt_par_r01 = 1 - phi((T_R01 - 9.55) / 1.70); alt_par_r02 = 1 - phi((T_R02 - 9.55) / 1.70)
alt_use_r01 = 0.5 * (alt_r01 + alt_par_r01); alt_use_r02 = 0.5 * (alt_r02 + alt_par_r02)
mg_r01 = float(mg_df[(mg_df.cushion_mean == 0.6) & (mg_df.mgmt_err_sd == 1.3)].p_r01.iloc[0])
mg_r02 = float(mg_df[(mg_df.cushion_mean == 0.6) & (mg_df.mgmt_err_sd == 1.3)].p_r02.iloc[0])
seq_r01 = float(br_df.loc[br_df.reference_class.str.startswith("all sequential"), "p_r01"].iloc[0])
seq_r02 = float(br_df.loc[br_df.reference_class.str.startswith("all sequential"), "p_r02"].iloc[0])
base_r01 = 0.5 * (seq_r01 + mg_r01); base_r02 = 0.5 * (seq_r02 + mg_r02)   # outside view = sequential base rate x mgmt delivery
W = dict(alt=0.60, base=0.30, market=0.10)
final_r01 = W["alt"] * alt_use_r01 + W["base"] * base_r01 + W["market"] * k_r01
final_r02 = W["alt"] * alt_use_r02 + W["base"] * base_r02 + W["market"] * k_r02
views = pd.DataFrame([
    dict(view="alt-data: seven-row kernel mixture, revintaged errors x1.108", p_r01=alt_r01, p_r02=alt_r02),
    dict(view="alt-data: parametric N(9.55, 1.70)", p_r01=alt_par_r01, p_r02=alt_par_r02),
    dict(view="alt-data used (mean of the two)", p_r01=alt_use_r01, p_r02=alt_use_r02),
    dict(view="base rate: sequential change >= needed (16 transitions)", p_r01=seq_r01, p_r02=seq_r02),
    dict(view="base rate: management delivery (floor + cushion N(0.6,0.5) + err N(0,1.3))", p_r01=mg_r01, p_r02=mg_r02),
    dict(view="base rate used (mean of the two)", p_r01=base_r01, p_r02=base_r02),
    dict(view="market: Kalshi KXABNB mid, interpolated at 147.0m / 147.8m", p_r01=k_r01, p_r02=k_r02),
    dict(view=f"FINAL blend {W}", p_r01=final_r01, p_r02=final_r02),
])
save("a09_three_views.csv", views)

# weight sensitivity
ws = []
for wa, wb, wm in ((1, 0, 0), (0.8, 0.2, 0), (0.7, 0.2, 0.1), (0.6, 0.3, 0.1), (0.5, 0.3, 0.2), (0.5, 0.5, 0), (0.4, 0.4, 0.2), (0, 1, 0), (0, 0, 1)):
    ws.append(dict(w_alt=wa, w_base=wb, w_market=wm, p_r01=wa * alt_use_r01 + wb * base_r01 + wm * k_r01,
                   p_r02=wa * alt_use_r02 + wb * base_r02 + wm * k_r02))
save("a09_weight_sensitivity.csv", pd.DataFrame(ws))

# ------------------------------------------------------------------ 7. R03 joint: share >= 25 disclosed AND nights >= 10
# nights distribution calibrated to the R01 final (shift a N(., 1.70) so that P(>=10) = final_r01), then the July
# expansion X (C06: Exp(mean 1.4) capped 6, in pts of GBV share) adds k*X pts of nights (RNPL module: base scenario
# +0.20 pts of nights for the expansion at the C06 mean of 1.4 pts of share -> k = 0.143; bull 0.30 -> 0.214).
def r03(exp_mean=1.4, k=0.2 / 1.4, p_disc=0.70, p_a_lang=0.90, disc_lift_accel=0.10, disc_lift_meet=0.05, target_r01=final_r01, cap_a=0.15):
    X = np.minimum(6, rng.exponential(exp_mean, N))
    share = rng.uniform(21, 23, N) + rng.uniform(0, 2, N) + X + rng.uniform(-2, 0, N)
    sd_eps = math.sqrt(max(1.70 ** 2 - (k * X.std()) ** 2, 0.5))
    # solve the centre so that the marginal P(nights >= 10) equals target_r01
    lo, hi = 7.0, 12.0
    for _ in range(40):
        c = (lo + hi) / 2
        nights = c + k * (X - X.mean()) + rng.normal(0, sd_eps, N)
        if (nights >= T_R01).mean() > target_r01: hi = c
        else: lo = c
    nights = c + k * (X - X.mean()) + rng.normal(0, sd_eps, N)
    pd_ = p_disc + disc_lift_accel * (nights >= T_R02) + disc_lift_meet * ((nights >= T_R01) & (nights < T_R02))
    disclosed = rng.uniform(0, 1, N) < pd_
    lang_a = rng.uniform(0, 1, N) < p_a_lang
    A = (share >= 24.5) & disclosed & lang_a            # C06 option (a)
    R1 = nights >= T_R01
    pa = A.mean(); pr1 = R1.mean(); joint = (A & R1).mean()
    # cap: C06's published P(a) = 0.15; if the model's marginal differs, rescale the joint proportionally
    joint_capped = joint * min(1.0, cap_a / pa) if pa > 0 else 0.0
    return dict(exp_mean=exp_mean, k_pts_nights_per_pt_share=k, nights_centre=c, p_a_model=pa, p_r01_model=pr1,
                p_r01_given_a=(A & R1).sum() / max(A.sum(), 1), joint_model=joint, product_of_marginals=pa * pr1,
                joint_capped_to_c06=joint_capped, corr_A_R1=float(np.corrcoef(A.astype(float), R1.astype(float))[0, 1]),
                p_true_share_ge25=float((share >= 24.5).mean()))
j = [r03()]
j.append(r03(exp_mean=4.0))                       # C06 sensitivity: large expansion
j.append(r03(k=0.3 / 1.4))                        # RNPL module bull nights-per-share
j.append(r03(k=0.0))                              # no mechanical link, only the disclosure dependence
j.append(r03(disc_lift_accel=0.0, disc_lift_meet=0.0, k=0.0))   # independence
j.append(r03(p_disc=0.90))                        # share treated as a standing KPI
j.append(r03(target_r01=0.38))                    # R01 at the C02/S01 conditioning value
j.append(r03(target_r01=0.55))                    # R01 at the market view
joint_df = pd.DataFrame(j)
save("a09_r03_joint.csv", joint_df)
final_r03 = float(joint_df.iloc[0]["joint_capped_to_c06"])

# ------------------------------------------------------------------ 8. impact tables (brief sensitivities)
# conditional means of nights given the event, from the final-calibrated normal
def cond_mean(c, s, t):
    z = (t - c) / s
    return c + s * math.exp(-z * z / 2) / math.sqrt(2 * math.pi) / (1 - phi(z))
c_fin = None
lo, hi = 7.0, 12.0
for _ in range(40):
    c = (lo + hi) / 2
    if 1 - phi((T_R01 - c) / 1.70) > final_r01: hi = c
    else: lo = c
c_fin = c
m_r01 = cond_mean(c_fin, 1.70, T_R01); m_r02 = cond_mean(c_fin, 1.70, T_R02)
TEAM_3Q26 = 9.9
def impact(label, d3, d4, dfy27, adr, stock_vs_base, stock_vs_uncond, p, note):
    rev3 = d3 * 48.0                                   # $M, 1pt 3Q26 nights = $48M 3Q26 revenue
    gbv3 = d3 * 1.34 * 176.8                           # $M GBV
    rev4 = (2 / 3) * gbv3 * 0.1203 + d4 * 30.0         # kernel carry + own-quarter 1pt = $30M
    rev27 = dfy27 * 158.0
    m26 = 0.59 * (rev3 + rev4) / 7980 * 100 * 0.5      # 2H26 held flex 0.59pp per 1pt of 2H26 revenue (~$7.98bn), FY weight ~0.5
    m27 = 0.66 * dfy27
    ebitda27 = rev27 * 0.66
    eps27 = 0.0014 * ebitda27
    return dict(question=label, p=p, nights_3q26_pts=round(d3, 2), nights_4q26_pts=round(d4, 2), nights_fy27_pts=round(dfy27, 2),
                adr_pts=adr, rev_3q26_musd=round(rev3), rev_4q26_musd=round(rev4), rev_fy27_musd=round(rev27),
                margin_fy26_pp=round(m26, 2), margin_fy27_pp=round(m27, 2), eps_fy27_usd=round(eps27, 3),
                stock_usd_per_share_vs_base_case=round(stock_vs_base, 1), stock_usd_per_share_vs_unconditional=round(stock_vs_uncond, 1),
                ev_stock_usd_per_share=round(p * stock_vs_base, 2), material=bool(p * stock_vs_base >= 1.0), note=note)
PX = 167.51
# stock: S01 cells (raw day-1): base-case conditional median -8.6; unconditional -2.9; given nights >= 10 the cell mix
# (accel&above +5.0 w.08, accel&below +1.8 w.17, flat&below -2.9 w.08, flat&above +0.2 w.04) -> +1.3%; given >= 10.6 -> +2.8%
d1_r01 = (0.08 * 5.0 + 0.17 * 1.8 + 0.08 * -2.9 + 0.04 * 0.2) / 0.37
d1_r02 = (0.08 * 5.0 + 0.17 * 1.8) / 0.25
mult = lambda dfy27: dfy27 * 0.44 * 9.5             # +0.40-0.48 turns per pt of forward growth, one turn ~$9-10
imp = [
    impact("R01", m_r01 - TEAM_3Q26, 0.6 * (m_r01 - TEAM_3Q26), 0.4 * (m_r01 - TEAM_3Q26), 0.0,
           (d1_r01 + 8.6) / 100 * PX + mult(0.4 * (m_r01 - TEAM_3Q26)), (d1_r01 + 2.9) / 100 * PX + mult(0.4 * (m_r01 - TEAM_3Q26)),
           final_r01, f"E[nights | >=10] = {m_r01:.2f} vs team 9.9; 4Q26 carries 60%, FY27 40%; day-1 {d1_r01:+.1f}% vs base-case -8.6 / unconditional -2.9; multiple line 0.44 turns x $9.5 per pt of FY27 growth"),
    impact("R02", m_r02 - TEAM_3Q26, 0.6 * (m_r02 - TEAM_3Q26), 0.5 * (m_r02 - TEAM_3Q26), 0.0,
           (d1_r02 + 8.6) / 100 * PX + mult(0.5 * (m_r02 - TEAM_3Q26)), (d1_r02 + 2.9) / 100 * PX + mult(0.5 * (m_r02 - TEAM_3Q26)),
           final_r02, f"E[nights | >=10.6] = {m_r02:.2f}; breaker cells day-1 {d1_r02:+.1f}%; FY27 carries 50%"),
    impact("R03", m_r01 - TEAM_3Q26, 0.6 * (m_r01 - TEAM_3Q26) + 0.4, 0.4 * (m_r01 - TEAM_3Q26) + 0.8, 0.3,
           (d1_r01 + 8.6) / 100 * PX + mult(0.4 * (m_r01 - TEAM_3Q26) + 0.8), (d1_r01 + 2.9) / 100 * PX + mult(0.4 * (m_r01 - TEAM_3Q26) + 0.8),
           final_r03, "R01 plus the RNPL-drag rebuttal: 4Q26 +0.4 and FY27 +0.8 pts more (module bull-vs-base 0.5 plus the ex-NA lap offset), ADR +0.3 (larger-home mix)"),
]
save("a09_impact.csv", pd.DataFrame(imp))

final = dict(seed=20260917, n_draws=N, thresholds=dict(r01=T_R01, r02=T_R02),
             revintage_factors=dict(honest=r_b / r_v1, literal=r_a / r_v1, ratios=dict(v1=r_v1, b=r_b, a=r_a)),
             alt_data=dict(kernel_revintaged=dict(r01=alt_r01, r02=alt_r02), parametric_9_55_1_70=dict(r01=alt_par_r01, r02=alt_par_r02),
                           used=dict(r01=alt_use_r01, r02=alt_use_r02)),
             base_rate=dict(sequential=dict(r01=seq_r01, r02=seq_r02), mgmt_delivery=dict(r01=mg_r01, r02=mg_r02), used=dict(r01=base_r01, r02=base_r02)),
             market=dict(kalshi_mid_interp=dict(r01=k_r01, r02=k_r02), timestamp="2026-09-17T03:21:58Z"),
             weights=W, final=dict(r01=final_r01, r02=final_r02, r03=final_r03),
             final_calibrated_normal=dict(centre=c_fin, sd=1.70, e_nights_given_r01=m_r01, e_nights_given_r02=m_r02),
             r03=j[0])
save("a09_final.json", final)
print(json.dumps(final, indent=1))
print(views.to_string())
print(joint_df.to_string())
print(pd.DataFrame(imp).to_string())
