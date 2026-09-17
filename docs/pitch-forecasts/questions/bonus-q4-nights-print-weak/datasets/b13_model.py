"""B13: P(4Q26 Nights and Seats Booked <= 131.0m, i.e. <= +7.46% y/y on 121.9m) -- the lower tail of R16's 4Q26 distribution.
Same three views, same parameters and seed as ../../risk-q4-nights-print-meets-street/datasets/r16_model.py, so that X01 has one
4Q26 object: V1 decomposition (R01 Q3 N(9.67,1.70) -> Q4 = 8.1 + 0.5 (Q3 - 9.67) + N(0,1.4), 12% short tail 5.5 +/- 1.5);
V2 management-guide route (C02 bucket vector x cushion N(1.2,1.3)); V3 the Street's own dispersion around the 134.0m bar.
Blend 0.5 / 0.3 / 0.2 as in R16. numpy only, seed 20260917, 400,000 draws. Writes b13_summary.csv, b13_views.csv, b13_conditional.csv, b13_sensitivity.csv.
Run: py -3.13 docs/pitch-forecasts/questions/bonus-q4-nights-print-weak/datasets/b13_model.py
"""
import numpy as np, csv, os
os.chdir(os.path.dirname(os.path.abspath(__file__)))
rng = np.random.default_rng(20260917); N = 400_000
BASE = 121.9; THR = 131.0; thr_g = (THR/BASE - 1)*100   # 7.465
Q3REF = 9.67
def v1(q3_mu=9.67, q3_sd=1.70, q4_mu=8.1, beta=0.5, res_sd=1.4, tail_w=0.12, tail_mu=5.5, tail_sd=1.5, q3_band=None):
    q3 = rng.normal(q3_mu, q3_sd, N)
    if q3_band is not None:
        lo, hi = q3_band; q3 = q3[(q3 >= lo) & (q3 < hi)]
    n = len(q3); tail = rng.random(n) < tail_w
    q4 = np.where(tail, tail_mu + beta*(q3 - Q3REF) + rng.normal(0, tail_sd, n), q4_mu + beta*(q3 - Q3REF) + rng.normal(0, res_sd, n))
    nights = np.round(BASE*(1 + q4/100), 1)
    yes = nights <= THR
    return yes.mean(), q4.mean(), q4.std(), (q4[yes].mean() if yes.any() else np.nan), (q4[~yes].mean() if (~yes).any() else np.nan), n, float((nights >= 134.0).mean())
def v2(vec=(0.21, 0.19, 0.39, 0.17, 0.04), mids=(10.75, 9.75, 8.0, 6.0, None), cushion_mu=1.2, cushion_sd=1.3):
    p = 0.0; parts = []
    for w, m in zip(vec, mids):
        if m is None: pm = v1()[0]
        else:
            draws = m + rng.normal(cushion_mu, cushion_sd, N); pm = (np.round(BASE*(1 + draws/100), 1) <= THR).mean()
        parts.append((w, m, pm)); p += w*pm
    return p, parts
def v3(mean=134.0, sd=1.5):
    # Street dispersion: 28 estimates, low 130.0 / high 136.0 (range 6m ~ 4 sd for n 28 -> sd ~1.5m); the at-print bar record
    # (actual - bar, 2023+: mean +0.9%, sd 1.5%) gives the same width. P(print <= 131.0) under N(134.0, 1.5).
    draws = rng.normal(mean, sd, N); return float((np.round(draws, 1) <= THR).mean())
base = v1(); p2, parts = v2(); p3 = v3()
sens = [("q4 centre = RNPL module 7.61", dict(q4_mu=7.61)), ("q4 centre = case A NA-only lap 8.9", dict(q4_mu=8.9)),
        ("q4 centre = Street bar 9.93, no short tail", dict(q4_mu=9.93, tail_w=0.0)), ("q4 centre = bridge no-lap 10.6, no tail", dict(q4_mu=10.6, tail_w=0.0)),
        ("q4 centre = short case 5.0 as the centre", dict(q4_mu=5.0, tail_w=0.0)),
        ("no short tail", dict(tail_w=0.0)), ("short tail 25%", dict(tail_w=0.25)), ("beta 0.3", dict(beta=0.3)), ("beta 0.8", dict(beta=0.8)),
        ("residual sd 1.0", dict(res_sd=1.0)), ("residual sd 2.0", dict(res_sd=2.0)), ("Q3 centre 9.2 (external stack)", dict(q3_mu=9.2)),
        ("Q3 centre 9.9 (team baseline)", dict(q3_mu=9.9)), ("Q3 sd 2.16 (naive)", dict(q3_sd=2.16)),
        ("joint weak: q4 7.61, tail 25%, Q3 9.2", dict(q4_mu=7.61, tail_w=0.25, q3_mu=9.2)),
        ("joint strong: q4 8.9, beta 0.8, no tail, Q3 9.9", dict(q4_mu=8.9, beta=0.8, tail_w=0.0, q3_mu=9.9))]
with open("b13_sensitivity.csv", "w", newline="") as f:
    w = csv.writer(f); w.writerow(["case", "p_yes_le_131", "q4_mean", "q4_sd", "e_q4_given_yes", "e_q4_given_no", "n", "p_ge_134_check"])
    w.writerow(["V1_base"] + [round(x, 4) for x in base])
    for name, kw in sens: w.writerow([name] + [round(x, 4) for x in v1(**kw)])
    for cm, cs in [(0.6, 1.3), (1.2, 1.3), (2.0, 1.5), (1.2, 0.8)]:
        w.writerow([f"V2 cushion N({cm},{cs})", round(v2(cushion_mu=cm, cushion_sd=cs)[0], 4)])
    w.writerow(["V2 with C02 vector shifted up (a .30 b .22 c .32 d .12 e .04)", round(v2(vec=(0.30, 0.22, 0.32, 0.12, 0.04))[0], 4)])
    w.writerow(["V2 with C02 vector shifted down (a .12 b .15 c .45 d .24 e .04)", round(v2(vec=(0.12, 0.15, 0.45, 0.24, 0.04))[0], 4)])
    for sd in (1.0, 1.5, 2.5): w.writerow([f"V3 Street N(134.0,{sd})", round(v3(sd=sd), 4)])
with open("b13_conditional.csv", "w", newline="") as f:
    w = csv.writer(f); w.writerow(["q3_band", "p_yes_V1", "q4_mean", "e_q4_given_yes", "n"])
    for lo, hi in [(-99, 9.0), (9.0, 10.0), (10.0, 10.6), (10.6, 99)]:
        r = v1(q3_band=(lo, hi)); w.writerow([f"[{lo},{hi})", round(r[0], 4), round(r[1], 3), round(r[3], 3), r[5]])
with open("b13_views.csv", "w", newline="") as f:
    w = csv.writer(f); w.writerow(["view", "p", "detail"])
    w.writerow(["V1_decomposition", round(base[0], 4), "Q3 N(9.67,1.70) -> Q4 8.1+0.5*(Q3-9.67)+N(0,1.4); 12% tail 5.5+/-1.5"])
    w.writerow(["V2_guide_route", round(p2, 4), "; ".join(f"{m}:w{wt}:p{pm:.3f}" for wt, m, pm in parts)])
    w.writerow(["V3_street_dispersion", round(p3, 4), "N(134.0, 1.5) on the 12 Sep Bloomberg bar (28 estimates, 130-136m)"])
    for wts in [(0.5, 0.3, 0.2), (0.6, 0.3, 0.1), (0.4, 0.4, 0.2), (0.7, 0.2, 0.1), (0.5, 0.5, 0.0), (0.34, 0.33, 0.33), (1.0, 0.0, 0.0)]:
        w.writerow([f"blend {wts}", round(wts[0]*base[0] + wts[1]*p2 + wts[2]*p3, 4), ""])
with open("b13_summary.csv", "w", newline="") as f:
    w = csv.writer(f); w.writerow(["item", "value"])
    for k, v in [("threshold_growth_pct", thr_g), ("p_V1", base[0]), ("q4_mean_V1", base[1]), ("q4_sd_V1", base[2]), ("e_q4_given_yes_V1", base[3]), ("e_q4_given_no_V1", base[4]), ("p_ge_134_V1_check", base[6]), ("p_V2", p2), ("p_V3", p3)]:
        w.writerow([k, round(float(v), 4)])
print(open("b13_summary.csv").read()); print(open("b13_views.csv").read()); print(open("b13_conditional.csv").read()); print(open("b13_sensitivity.csv").read())
