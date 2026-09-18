"""A09 revision 2 (R01, R02, R03), after audit A09 (Astra, 2026-09-17).

One distribution for the 3Q26 Nights and Seats Booked print, derived ONLY from the team's nowcast and the reviews
index's measured walk-forward error (question fine print; brief rule 6). The management-delivery construction, the
sequential-change reference class and the Kalshi ladder are computed and reported as LABELLED ALTERNATIVES with zero
weight in the headline. R03 is rebuilt on C06 revision 2. Impact tables come from the same distribution as the
probabilities, with the held-cost identity applied to margins and EPS and the stock line read from S01 revision 2's
cells re-weighted to this distribution.

Run from anywhere:  py -3.13 a09_v2_print_distribution.py      (numpy + pandas; seed 20260917; ~20 s)
Reads (repo, read-only):
  data/processed/q3nowcast/E_aug/q3_2026_nowcast.csv, backtest_wf_paths.csv      (seven rows, W1 and W2 errors)
  data/processed/q3nowcast_v2/E/t1_fail_e5_rerun.csv                             (re-vintaged RMSE ratios)
  data/processed/overnight/02_guidance_ledger.csv                                (management record, diagnostics)
  data/processed/margin_build/23_final_model/23_forecast_annual.csv              (FY26/FY27 base revenue, EBITDA)
  docs/pitch-forecasts/questions/day1-move-5nov/datasets/s01_v2_cells.csv        (S01 rev 2 twelve joint cells)
  docs/pitch-forecasts/questions/risk-q3-nights-meets-guide/sources/kalshi_markets_KXABNB_open_20260917T032158Z.json
Writes, into the datasets/ folder of each of the three A09 questions (revision-1 files untouched):
  a09_v2_distribution_grid.csv, a09_v2_constructions.csv, a09_v2_windows.csv, a09_v2_alternatives.csv,
  a09_v2_r03_joint.csv, a09_v2_impact.csv, a09_v2_final.json
and, in risk-q3-nights-meets-guide/datasets only: adopted_print_states_v2.json (the object X01 and any re-basing read).
"""
from __future__ import annotations
import json, math, pathlib
import numpy as np
import pandas as pd

HERE = pathlib.Path(__file__).resolve()
QDIR = HERE.parents[2]                       # docs/pitch-forecasts/questions
ROOT = HERE.parents[5]                       # repo root
SLUGS = ("risk-q3-nights-meets-guide", "risk-q3-nights-accelerates", "risk-july-rnpl-expansion-offsets-lap")
OUTS = [QDIR / s / "datasets" for s in SLUGS]
rng = np.random.default_rng(20260917)
N = 400_000

# ----------------------------------------------------------------------------- conventions
BASE_3Q25 = 133.6                            # fixed denominator (registry; A09-02)
def growth_of(printed_m: float) -> float:    # printed millions -> exact growth %
    return (printed_m / BASE_3Q25 - 1) * 100
# Rounding convention (A09-18): the latent quantity is continuous nights; the press release prints millions to one
# decimal (rounded); "printed >= 147.0m" <=> latent >= 146.95m. Thresholds in growth space:
T_R01 = growth_of(146.95)                    # 9.9925 %
T_R02 = growth_of(147.75)                    # 10.5913 %
T_R01_EXACT, T_R02_EXACT = growth_of(147.0), growth_of(147.8)   # 10.0299 / 10.6287 (printed-exact, Astra's convention)
# S01 revision 2 print states (dead band 0.25pt on 2Q26's 10.34): decelerating < 10.09, flat 10.09-10.59, accelerating >= 10.59
S01_DECEL, S01_ACCEL = 10.09, 10.59

CENTRE = 9.5                                 # the team's nowcast centre (brief rule 6; memo "3Q26 nights read +9.5%")
SD = 1.70                                    # adopted predictive sd: midpoint of the fresh-vintage W2 RMSE range 1.63-1.82
MEMO_BASE_3Q26 = 9.5                         # memo base case for 3Q26 nights (146.3m); deltas are versus this

def phi(x):  return 0.5 * (1 + math.erf(x / math.sqrt(2)))
def pdf(x):  return math.exp(-x * x / 2) / math.sqrt(2 * math.pi)
def p_ge(c, s, t): return 1 - phi((t - c) / s)
def cond_mean_ge(c, s, t):
    z = (t - c) / s
    return c + s * pdf(z) / (1 - phi(z))
def cond_mean_lt(c, s, t):
    z = (t - c) / s
    return c - s * pdf(z) / phi(z)
def cond_mean_between(c, s, a, b):
    za, zb = (a - c) / s, (b - c) / s
    return c + s * (pdf(za) - pdf(zb)) / (phi(zb) - phi(za))

def save(name, obj):
    for o in OUTS:
        p = o / name
        if isinstance(obj, dict):
            p.write_text(json.dumps(obj, indent=1), encoding="utf-8")
        else:
            obj.to_csv(p, index=False)

# ----------------------------------------------------------------------------- 1. rows and errors, both windows
FEAT = {("yoy_all", "w_reviews", "GLOBAL"): "GLOBAL|yoy_all|w_reviews", ("yoy_all", "w_equal", "GLOBAL"): "GLOBAL|yoy_all|w_equal",
        ("yoy_all", "w_median", "GLOBAL"): "GLOBAL|yoy_all|w_median", ("yoy_all", "w_equal", "GLOBAL_NW"): "GLOBAL_NW|yoy_all|w_equal",
        ("yoy_vmatch", "w_reviews", "GLOBAL"): "GLOBAL|yoy_vmatch|w_reviews", ("yoy_vmatch", "w_equal", "GLOBAL"): "GLOBAL|yoy_vmatch|w_equal",
        ("yoy_vmatch", "w_equal", "GLOBAL_NW"): "GLOBAL_NW|yoy_vmatch|w_equal"}
nc = pd.read_csv(ROOT / "data/processed/q3nowcast/E_aug/q3_2026_nowcast.csv")
wf = pd.read_csv(ROOT / "data/processed/q3nowcast/E_aug/backtest_wf_paths.csv")
wf = wf[(wf.target == "nights_yoy") & (wf.lag == 0)]
rev = pd.read_csv(ROOT / "data/processed/q3nowcast_v2/E/t1_fail_e5_rerun.csv")
r_v1 = float(rev.loc[rev.variant.str.startswith("v1"), "wf_ratio_vs_naive"].iloc[0])
r_b = float(rev.loc[rev.variant.str.startswith("b:"), "wf_ratio_vs_naive"].iloc[0])
r_a = float(rev.loc[rev.variant.str.startswith("a:"), "wf_ratio_vs_naive"].iloc[0])
RMSE_PUB = float(rev.loc[rev.variant.str.startswith("v1"), "wf_rmse"].iloc[0])        # 1.475
RMSE_HON = float(rev.loc[rev.variant.str.startswith("b:"), "wf_rmse"].iloc[0])        # 1.634
RMSE_LIT = float(rev.loc[rev.variant.str.startswith("a:"), "wf_rmse"].iloc[0])        # 1.816
RMSE_NAIVE = float(rev.loc[rev.variant.str.startswith("v1"), "wf_rmse_naive"].iloc[0])  # 2.159

errs = {}   # (window, feature) -> np.array of pred-actual errors, chronological
win_rows = []
for _, r in nc.iterrows():
    key = FEAT[(r["measure"], r["weighting"], r["region"])]
    for window in ("2023Q1+", "2022Q1+"):
        e = wf[(wf.feature == key) & (wf.window == window)].sort_values("qi")
        if e.empty:
            continue
        v = e.err_feature.to_numpy(); errs[(window, key)] = v
        quarters = [f"{q // 4}Q{q % 4 + 1}" for q in e.qi.astype(int)]
        win_rows.append(dict(window="W2" if window == "2023Q1+" else "W1", feature=key, implied=r["implied_nights_yoy"], n=len(v),
                             mean=v.mean(), sd=v.std(ddof=1), rmse=math.sqrt((v ** 2).mean()),
                             rmse_naive=math.sqrt((e.err_naive.to_numpy() ** 2).mean()), n_over=int((v > 0).sum()),
                             quarters=" ".join(quarters), errors=" ".join(f"{x:+.2f}" for x in v)))
windows = pd.DataFrame(win_rows)
# common under-prediction quarters (A09-06)
for window, tag in (("2023Q1+", "W2"), ("2022Q1+", "W1")):
    panel = wf[wf.feature.isin(FEAT.values()) & (wf.window == window)].pivot(index="qi", columns="feature", values="err_feature")
    common = [f"{int(q) // 4}Q{int(q) % 4 + 1}" for q in panel.index[(panel < 0).all(axis=1)]]
    windows.loc[windows.window == tag, "all_rows_underpredicted"] = ", ".join(common)
save("a09_v2_windows.csv", windows)
HEAD = "GLOBAL|yoy_all|w_reviews"
e_w2 = errs[("2023Q1+", HEAD)]; e_w1 = errs[("2022Q1+", HEAD)]

# ----------------------------------------------------------------------------- 2. the adopted distribution and its sd grid
grid = []
for c in (9.0, 9.2, 9.49, 9.5, 9.9, 10.0, 10.3):
    for s in (1.0, 1.25, RMSE_PUB, RMSE_HON, SD, RMSE_LIT, 1.9, RMSE_NAIVE, 2.41, 2.5):
        grid.append(dict(centre=c, sd=round(s, 3), p_r01=p_ge(c, s, T_R01), p_r02=p_ge(c, s, T_R02),
                         p_r01_exact_threshold=p_ge(c, s, T_R01_EXACT), p_r02_exact_threshold=p_ge(c, s, T_R02_EXACT),
                         p_s01_accel=p_ge(c, s, S01_ACCEL), p_s01_flat=p_ge(c, s, S01_DECEL) - p_ge(c, s, S01_ACCEL),
                         p_s01_decel=1 - p_ge(c, s, S01_DECEL)))
grid = pd.DataFrame(grid)
save("a09_v2_distribution_grid.csv", grid)
P_R01 = p_ge(CENTRE, SD, T_R01); P_R02 = p_ge(CENTRE, SD, T_R02)

# ----------------------------------------------------------------------------- 3. alt-data-only constructions (all at centre 9.5)
cons = []
def add(name, p1, p2, note, form):
    cons.append(dict(construction=name, p_r01=p1, p_r02=p2, form=form, note=note))
add("ADOPTED: normal, centre 9.5, sd 1.70", P_R01, P_R02, "fine-print object: nowcast centre + index error sd; thresholds 146.95m/147.75m", "parametric")
add("normal, centre 9.5, sd 1.475 (published W2 RMSE, stale 1Q23 vintage)", p_ge(CENTRE, RMSE_PUB, T_R01), p_ge(CENTRE, RMSE_PUB, T_R02), "brief's quoted 1.48", "parametric")
add("normal, centre 9.5, sd 1.634 (honest re-vintage)", p_ge(CENTRE, RMSE_HON, T_R01), p_ge(CENTRE, RMSE_HON, T_R02), "WPK variant b", "parametric")
add("normal, centre 9.5, sd 1.816 (literal re-vintage)", p_ge(CENTRE, RMSE_LIT, T_R01), p_ge(CENTRE, RMSE_LIT, T_R02), "WPK variant a", "parametric")
add("normal, centre 9.5, sd 2.159 (index no better than naive)", p_ge(CENTRE, RMSE_NAIVE, T_R01), p_ge(CENTRE, RMSE_NAIVE, T_R02), "naive last-quarter RMSE", "parametric")
add("normal, centre 9.5, sd 1.712 (1.70 + partial-to-full gap sd 0.2 in quadrature)", p_ge(CENTRE, math.sqrt(SD ** 2 + 0.2 ** 2), T_R01), p_ge(CENTRE, math.sqrt(SD ** 2 + 0.2 ** 2), T_R02), "E_aug gap sd", "parametric")
def kern(errvec, scale=1.0, bw=0.5, centre=CENTRE, demean=True):
    v = errvec - errvec.mean() if demean else errvec
    return centre - (rng.choice(v, N) * scale + rng.normal(0, bw, N))
for label, vec, tag in (("W2 headline row, 10 errors", e_w2, "W2"), ("W1 headline row, 14 errors", e_w1, "W1")):
    plug = centre_actual = CENTRE - (vec - vec.mean())
    add(f"empirical plug-in, {label}, demeaned, centre 9.5", float((plug >= T_R01).mean()), float((plug >= T_R02).mean()), "actual = 9.5 - (err - mean err); 0.1 granularity", "empirical")
    k = kern(vec)
    add(f"empirical kernel bw 0.5, {label}, demeaned, centre 9.5", float((k >= T_R01).mean()), float((k >= T_R02).mean()), "resampled demeaned errors + N(0,0.5)", "empirical")
    k = kern(vec, scale=r_b / r_v1)
    add(f"empirical kernel, {label}, demeaned, errors x{r_b / r_v1:.3f} (STRESS: uniform re-vintage scaling, not refitted residuals)", float((k >= T_R01).mean()), float((k >= T_R02).mean()), "A09-05: labelled stress test", "empirical-stress")
    if tag == "W1":
        k = kern(vec, demean=False)
        add("empirical kernel, W1 headline row, NOT demeaned (carries the 2023 normalisation over-prediction bias +1.64)", float((k >= T_R01).mean()), float((k >= T_R02).mean()), "reported, not used: the bias is the 2023 normalisation", "empirical-stress")
# seven-row mixture (own centres, W2): implied level minus its own raw errors, which is by construction the
# bias-corrected centre (implied - mean error) with demeaned errors; the raw-level mean 9.16 is not a separate case
draws = []
for _, r in nc.iterrows():
    key = FEAT[(r["measure"], r["weighting"], r["region"])]; v = errs[("2023Q1+", key)]
    draws.append(r["implied_nights_yoy"] - v[rng.integers(0, len(v), N // 7)] - rng.normal(0, 0.5, N // 7))
d = np.concatenate(draws)
add("seven-row kernel mixture, W2, each row at its own implied level minus its own errors (= bias-corrected centres, mean 9.43)", float((d >= T_R01).mean()), float((d >= T_R02).mean()), f"mixture mean {d.mean():.2f}, sd {d.std():.2f}; reported, not adopted: the rows are the ingredients of the 9.5 call", "empirical")
# the six W1-available rows
draws = []
for _, r in nc.iterrows():
    key = FEAT[(r["measure"], r["weighting"], r["region"])]
    if ("2022Q1+", key) not in errs: continue
    v = errs[("2022Q1+", key)]; c = r["implied_nights_yoy"] - v.mean()
    draws.append(c - (v - v.mean())[rng.integers(0, len(v), N // 6)] - rng.normal(0, 0.5, N // 6))
d = np.concatenate(draws)
add("six-row kernel mixture, W1, each row minus its own W1 errors (W1 bias +0.7 to +1.6 is the 2023 normalisation; centres fall to ~8.0)", float((d >= T_R01).mean()), float((d >= T_R02).mean()), f"mixture mean {d.mean():.2f}, sd {d.std():.2f}; reported, not used (A09-05 both-window sensitivity)", "empirical-stress")
# rev-1 alt-data leg, for the audit trail
add("revision-1 alt-data leg (mean of seven-row kernel x1.107 at raw centres and N(9.55,1.70)), thresholds 10.0/10.6", 0.3321, 0.2179, "from a09_final.json (rev 1); Astra's 'alt-only 33.2%'", "rev-1")
cons_df = pd.DataFrame(cons)
save("a09_v2_constructions.csv", cons_df)

# ----------------------------------------------------------------------------- 4. labelled alternatives (zero headline weight)
alts = []
g = pd.read_csv(ROOT / "data/processed/overnight/02_guidance_ledger.csv")
g = g[g.metric.eq("nights_yoy_pct")].sort_values("print_date")
resolved = g[g.actual.notna()]
outcomes = resolved.outcome.value_counts().to_dict()
levels = dict(zip(resolved.target_period, resolved.actual)); levels["2Q22"] = float(g.loc[g.print_quarter.eq("2Q22"), "comparator_value"].iloc[0])
qi = lambda q: (2000 + int(q[-2:])) * 4 + int(q[0]) - 1
keys = sorted(levels, key=qi)
chg = [(q, levels[q] - levels[keys[i - 1]]) for i, q in enumerate(keys) if i]
need1, need2 = T_R01 - 10.342, T_R02 - 10.342
for label, rows in (("all sequential changes 3Q22-2Q26", chg), ("W1 targets 1Q23+", [x for x in chg if qi(x[0]) >= qi("1Q23")]),
                    ("W2 targets 1Q24+", [x for x in chg if qi(x[0]) >= qi("1Q24")]), ("Q2->Q3 transitions", [x for x in chg if x[0].startswith("3Q")])):
    n = len(rows); k1 = sum(d >= need1 for _, d in rows); k2 = sum(d >= need2 for _, d in rows)
    alts.append(dict(view=f"outside view: sequential change >= needed ({label})", n=n, p_r01=k1 / n, p_r02=k2 / n,
                     note=f"k1 {k1}, k2 {k2}; members " + " ".join(f"{q}:{d:+.2f}" for q, d in rows), weight_in_headline=0))
alts.append(dict(view="outside view: management nights guides met or exceeded (coded)", n=len(resolved),
                 p_r01=resolved.outcome.isin(["met", "above_range"]).mean(), p_r02=float("nan"),
                 note=f"ledger outcomes {outcomes}; heterogeneous guides (directional/approx/bucket); not a probability of this event", weight_in_headline=0))
for cm in (0.3, 0.6, 1.0):
    for es in (1.0, 1.3, 1.6):
        s = math.sqrt(0.5 ** 2 + es ** 2)
        alts.append(dict(view=f"outside view: management-delivery construction, floor 10.0 + cushion N({cm},0.5) + err N(0,{es}) [ASSUMPTION, no comparable sample]",
                         n=0, p_r01=p_ge(10.0 + cm, s, T_R01), p_r02=p_ge(10.0 + cm, s, T_R02), note="rev-1 grid, relabelled", weight_in_headline=0))
mk = json.loads((QDIR / SLUGS[0] / "sources/kalshi_markets_KXABNB_open_20260917T032158Z.json").read_text(encoding="utf-8"))
mids, lasts, vols = {}, {}, {}
for m in mk["markets"]:
    k = m["floor_strike"] / 1e6
    mids[k] = (float(m["yes_bid_dollars"]) + float(m["yes_ask_dollars"])) / 2; lasts[k] = float(m["last_price_dollars"]); vols[k] = float(m["volume_fp"])
def interp(x, d):
    ks = sorted(d)
    for lo, hi in zip(ks, ks[1:]):
        if lo <= x <= hi: return d[lo] + (d[hi] - d[lo]) * (x - lo) / (hi - lo)
    return float("nan")
alts.append(dict(view="market: Kalshi KXABNB mid quotes interpolated at 147.0m / 147.8m (2026-09-17T03:21:58Z)", n=0,
                 p_r01=interp(147.0, mids), p_r02=interp(147.8, mids),
                 note=f"mids {mids}; last trades {lasts}; cumulative volume_fp {vols} identical to the 29 Jul Octagon snapshot (999/428/591 at 146/148/150m) -> no trade since 29 Jul; 24h volume 0; zero weight (fine print + stale-source rule)", weight_in_headline=0))
alts.append(dict(view="market: Kalshi last-trade prices interpolated at 147.0m / 147.8m", n=0, p_r01=interp(147.0, lasts), p_r02=interp(147.8, lasts),
                 note="last trades 0.60/0.53/0.30 at 146/148/150m = Octagon's 29 Jul 60/53/30%", weight_in_headline=0))
alts.append(dict(view="revision-1 blend 0.60 alt / 0.30 outside / 0.10 market (WITHDRAWN as headline)", n=0, p_r01=0.4237, p_r02=0.3159, note="a09_final.json rev 1", weight_in_headline=0))
alts.append(dict(view="Astra A09 benchmark: N(9.5, 1.70) at printed-exact thresholds 10.0299 / 10.6287", n=0, p_r01=p_ge(9.5, 1.7, T_R01_EXACT), p_r02=p_ge(9.5, 1.7, T_R02_EXACT), note="audit §Independent forecasts", weight_in_headline=0))
alts_df = pd.DataFrame(alts)
save("a09_v2_alternatives.csv", alts_df)

# ----------------------------------------------------------------------------- 5. R03 joint on C06 revision 2
def c06_v2_share(n, s1=(19, 21), d12=(0.5, 3.5), s2_ok=(20.5, 23.5), ramp_frac=(0, 0.5), exp_mix=((0.75, 1.4), (0.25, 3.5)), cap=8, mix=(-1, 1)):
    """Exact structure of share_ramp_model_v2_2026-09-17.py (C06 rev 2), vectorised. Returns (share, expansion X)."""
    out_s, out_x = [], []
    while sum(len(a) for a in out_s) < n:
        m = n
        a = rng.uniform(*s1, m); d = rng.uniform(*d12, m); s2 = a + d
        ok = (s2 >= s2_ok[0]) & (s2 <= s2_ok[1])
        s2, d = s2[ok], d[ok]; m = len(s2)
        ramp = rng.uniform(*ramp_frac, m) * d
        u = rng.uniform(0, 1, m); x = np.zeros(m); acc = 0.0; done = np.zeros(m, bool)
        for w, mean in exp_mix:
            acc += w; sel = (~done) & (u <= acc)
            x[sel] = np.minimum(cap, rng.exponential(mean, sel.sum())); done |= sel
        s = s2 + ramp + x + rng.uniform(*mix, m)
        out_s.append(s); out_x.append(x)
    return np.concatenate(out_s)[:n], np.concatenate(out_x)[:n]
LEVEL_GATE = (0.75, 0.68, 0.55)   # C06 rev 2 level-dependent disclosure gate (>=25 / 21-24 / <=20)
LANG_A = 0.85                     # C06 rev 2 language map: true >= 24.5 -> (a) 0.85

def r03(k=0.10, lift_accel=0.10, lift_meet=0.05, gate=LEVEL_GATE, lang_a=LANG_A, centre=CENTRE, sd=SD, exp_mix=((0.75, 1.4), (0.25, 3.5)), label=""):
    share, X = c06_v2_share(N, exp_mix=exp_mix)
    sd_eps = math.sqrt(max(sd ** 2 - (k * X.std()) ** 2, 0.25))
    nights = centre + k * (X - X.mean()) + rng.normal(0, sd_eps, N)
    accel = nights >= S01_ACCEL; meet = (nights >= T_R01) & ~accel
    lift = lift_accel * accel + lift_meet * meet
    lift = lift - lift.mean()                     # centre the lift so C06's unconditional gate (and P(a)) is preserved
    lvl = np.where(share >= 24.5, gate[0], np.where(share >= 20.5, gate[1], gate[2]))
    disclosed = rng.uniform(0, 1, N) < np.clip(lvl + lift, 0, 1)
    A = (share >= 24.5) & disclosed & (rng.uniform(0, 1, N) < lang_a)
    R1 = nights >= T_R01; R2 = nights >= T_R02
    both = A & R1
    return dict(variant=label, k=k, lift_accel=lift_accel, lift_meet=lift_meet, p_true_ge25=float((share >= 24.5).mean()), p_a=float(A.mean()),
                p_r01=float(R1.mean()), p_r02=float(R2.mean()), p_r01_given_a=float(both.sum() / A.sum()), p_a_given_r01=float(both.sum() / R1.sum()),
                joint=float(both.mean()), product=float(A.mean() * R1.mean()), corr=float(np.corrcoef(A, R1)[0, 1]),
                e_nights_given_both=float(nights[both].mean()), p_accel_given_both=float(accel[both].mean()),
                p_flat_given_both=float(((nights >= S01_DECEL) & ~accel)[both].mean()),
                p_sliver_given_both=float(((nights >= T_R01) & (nights < S01_DECEL))[both].mean()),
                e_x_given_both=float(X[both].mean()), e_x=float(X.mean()), sd_x=float(X.std()))
J = [r03(label="ADOPTED: k 0.10 (B. Riley Q2 ratio), disclosure lift +0.10 accel / +0.05 meet, C06 v2 share + level gate")]
J.append(r03(k=0.0, lift_accel=0.0, lift_meet=0.0, label="independence"))
J.append(r03(k=0.0, label="disclosure dependence only (k 0)"))
J.append(r03(k=0.10, lift_accel=0.0, lift_meet=0.0, label="mechanical link only (k 0.10)"))
J.append(r03(k=0.2 / 1.4, label="k 0.143 (RNPL module base +0.20 / C06 rev-1 mean 1.4)"))
J.append(r03(k=0.3 / 1.4, label="k 0.214 (module bull)"))
J.append(r03(k=0.075, label="k 0.075 (bundle 'approximately 3 points' at ~20% share, RNPL half of it)"))
J.append(r03(lift_accel=0.20, lift_meet=0.10, label="disclosure lift doubled"))
J.append(r03(gate=(0.90, 0.90, 0.90), label="share treated as a standing KPI (gate 0.90 flat; C06 sensitivity a 0.30)"))
J.append(r03(gate=(0.50, 0.50, 0.50), label="reframing removes RNPL numbers (gate 0.50; C06 a 0.16)"))
J.append(r03(exp_mix=((1.0, 3.5),), label="July expansion large only (C06: true>=25 0.593, a 0.38)"))
J.append(r03(exp_mix=((1.0, 1.4),), label="July expansion small only (C06: a 0.21)"))
J.append(r03(lang_a=0.70, label="language (a) 0.70 ('nearly a quarter' habit)"))
J.append(r03(centre=9.9, label="nights centre 9.9 (model path)"))
J.append(r03(centre=9.2, label="nights centre 9.2 (external stack)"))
J.append(r03(sd=RMSE_PUB, label="nights sd 1.475"))
J.append(r03(sd=RMSE_NAIVE, label="nights sd 2.159"))
joint_df = pd.DataFrame(J)
save("a09_v2_r03_joint.csv", joint_df)
R03 = J[0]
P_R03 = R03["joint"]

# ----------------------------------------------------------------------------- 6. impact tables from the same distribution
annual = pd.read_csv(ROOT / "data/processed/margin_build/23_final_model/23_forecast_annual.csv")
annual = annual[annual.scenario.eq("base")].set_index("period")
R26, E26 = float(annual.loc["FY26", "revenue_musd"]), float(annual.loc["FY26", "adj_ebitda_musd"])
R27, E27 = float(annual.loc["FY27", "revenue_musd"]), float(annual.loc["FY27", "adj_ebitda_musd"])
cells = pd.read_csv(QDIR / "day1-move-5nov/datasets/s01_v2_cells.csv")
state_mean = {s: float((cells[cells.state == s]["mean"] * cells[cells.state == s]["prob"]).sum() / cells[cells.state == s]["prob"].sum()) for s in ("decel", "flat", "accel")}
# S01 rev-2 cell means: E[r | accel], E[r | flat], E[r | decel]; re-weighted to the adopted distribution
p_accel = p_ge(CENTRE, SD, S01_ACCEL); p_flat = p_ge(CENTRE, SD, S01_DECEL) - p_accel; p_sliver = p_ge(CENTRE, SD, T_R01) - p_ge(CENTRE, SD, S01_DECEL); p_decel = 1 - p_accel - p_flat
E_r_uncond = p_accel * state_mean["accel"] + p_flat * state_mean["flat"] + p_decel * state_mean["decel"]
E_r_r01 = (p_accel * state_mean["accel"] + p_flat * state_mean["flat"] + p_sliver * state_mean["decel"]) / P_R01
E_r_not_r01 = state_mean["decel"]                                  # every R01-No draw is decelerating
E_r_r02 = state_mean["accel"]
E_r_not_r02 = (p_flat * state_mean["flat"] + p_decel * state_mean["decel"]) / (1 - p_accel)
E_r_r03 = R03["p_accel_given_both"] * state_mean["accel"] + R03["p_flat_given_both"] * state_mean["flat"] + R03["p_sliver_given_both"] * state_mean["decel"]
E_r_not_r03 = (E_r_uncond - P_R03 * E_r_r03) / (1 - P_R03)
base_cell = cells[(cells.state == "decel") & cells.c01_below & cells.c02_cd].iloc[0]
E_r_basecase = float(base_cell["mean"])
PX = 167.51
PERSIST_4Q, PERSIST_FY27 = 0.6, 0.4                                # judgement (A09-15): labelled, sensitivity below
FLEX = 0.77                                                        # flow-through under the brief's 'flex' sensitivity (0.42/0.66 FY27; 0.38/0.59 2H26)

def impact(label, p, d3, e_r_event, e_r_not, note, persist4=PERSIST_4Q, persist27=PERSIST_FY27):
    d4 = persist4 * d3; d27 = persist27 * d3
    rev3 = d3 * 48.0; gbv3 = d3 * 1.34 * 176.8
    rev4 = (2 / 3) * gbv3 * 0.1203 + d4 * 30.0
    rev27 = d27 * 158.0
    dR26 = rev3 + rev4
    m26_held = 100 * ((E26 + dR26) / (R26 + dR26) - E26 / R26); m26_flex = 100 * ((E26 + FLEX * dR26) / (R26 + dR26) - E26 / R26)
    m27_held = 100 * ((E27 + rev27) / (R27 + rev27) - E27 / R27); m27_flex = 100 * ((E27 + FLEX * rev27) / (R27 + rev27) - E27 / R27)
    eps27_held = 0.0014 * rev27; eps27_flex = 0.0014 * FLEX * rev27
    d_event_vs_not = (e_r_event - e_r_not) / 100 * PX; d_event_vs_uncond = (e_r_event - E_r_uncond) / 100 * PX; d_event_vs_base = (e_r_event - E_r_basecase) / 100 * PX
    mult_line = d27 * 0.44 * 9.5
    return dict(question=label, p=p, nights_3q26_pts=d3, nights_4q26_pts=d4, nights_fy27_pts=d27, adr_pts=0.0,
                rev_3q26_musd=rev3, gbv_3q26_musd=gbv3, rev_4q26_musd=rev4, rev_fy27_musd=rev27,
                margin_fy26_pp_held=m26_held, margin_fy26_pp_flex=m26_flex, margin_fy27_pp_held=m27_held, margin_fy27_pp_flex=m27_flex,
                eps_fy27_usd_held=eps27_held, eps_fy27_usd_flex=eps27_flex,
                day1_pct_given_event=e_r_event, day1_pct_given_not_event=e_r_not, day1_pct_unconditional=E_r_uncond, day1_pct_memo_base_case_cell=E_r_basecase,
                stock_usd_vs_not_event=d_event_vs_not, stock_usd_vs_unconditional=d_event_vs_uncond, stock_usd_vs_base_case_cell=d_event_vs_base,
                multiple_line_usd_separate_horizon_not_added=mult_line,
                ev_stock_usd_vs_not_event=p * d_event_vs_not, ev_stock_usd_vs_base_case_cell=p * d_event_vs_base,
                material=bool(p * d_event_vs_not >= 1.0), note=note)
m_r01 = cond_mean_ge(CENTRE, SD, T_R01); m_r02 = cond_mean_ge(CENTRE, SD, T_R02); m_r03 = R03["e_nights_given_both"]
imp = [impact("R01", P_R01, m_r01 - MEMO_BASE_3Q26, E_r_r01, E_r_not_r01, f"E[nights | >=147.0m] {m_r01:.2f} vs memo base 9.5; S01 rev-2 state means accel {state_mean['accel']:.2f} / flat {state_mean['flat']:.2f} / decel {state_mean['decel']:.2f} re-weighted to N(9.5,1.70)"),
       impact("R02", P_R02, m_r02 - MEMO_BASE_3Q26, E_r_r02, E_r_not_r02, f"E[nights | >=147.8m] {m_r02:.2f}; subset of R01, do not add EVs"),
       impact("R03", P_R03, m_r03 - MEMO_BASE_3Q26, E_r_r03, E_r_not_r03, f"E[nights | R01 and C06(a)] {m_r03:.2f} from the joint draw (k 0.10); ADR mix effect unquantified, set 0 (A09-17); the FY27 lap-offset scenario (module bull-vs-base +0.47pt) is a separate labelled line, not in EV (A09-16)")]
imp_df = pd.DataFrame(imp)
# persistence sensitivity for R01
pers = [dict(question="R01", persist_4q=a, persist_fy27=b, **{k: v for k, v in impact("R01", P_R01, m_r01 - MEMO_BASE_3Q26, E_r_r01, E_r_not_r01, "", a, b).items() if k in ("nights_4q26_pts", "nights_fy27_pts", "rev_4q26_musd", "rev_fy27_musd", "margin_fy27_pp_held", "eps_fy27_usd_held", "eps_fy27_usd_flex")})
        for a, b in ((0.3, 0.2), (0.6, 0.4), (0.9, 0.6), (1.0, 1.0))]
save("a09_v2_impact.csv", imp_df)
save("a09_v2_impact_persistence_sensitivity.csv", pd.DataFrame(pers))

# ----------------------------------------------------------------------------- 7. monitoring rule and final objects
monitor = [dict(centre=c, p_r01=p_ge(c, SD, T_R01), p_r02=p_ge(c, SD, T_R02), p_r03_approx=P_R03 / P_R01 * p_ge(c, SD, T_R01)) for c in (8.5, 9.0, 9.2, 9.5, 9.7, 9.9, 10.0, 10.3, 10.6)]
final = dict(revision=2, seed=20260917, n_draws=N, run_date="2026-09-17",
             distribution=dict(form="normal", centre=CENTRE, sd=SD, sd_source="midpoint of the fresh-vintage W2 RMSE range (honest 1.634, literal 1.816); published 1.475 and naive 2.159 in the grid",
                               denominator_m=BASE_3Q25, rounding="printed millions rounded to one decimal; Yes iff latent >= threshold - 0.05m",
                               thresholds_pct=dict(r01=T_R01, r02=T_R02, r01_printed_exact=T_R01_EXACT, r02_printed_exact=T_R02_EXACT, s01_decel=S01_DECEL, s01_accel=S01_ACCEL)),
             final=dict(r01=P_R01, r02=P_R02, r03=P_R03),
             conditional_means=dict(e_nights_given_r01=m_r01, e_nights_given_r02=m_r02, e_nights_given_not_r01=cond_mean_lt(CENTRE, SD, T_R01),
                                    e_nights_given_flat_147_0_to_147_7=cond_mean_between(CENTRE, SD, T_R01, T_R02), e_nights_given_r03=m_r03),
             print_states=dict(r01_r02=dict(p_lt_147_0m=1 - P_R01, p_147_0_to_147_7m=P_R01 - P_R02, p_ge_147_8m=P_R02),
                               s01=dict(decel_lt_10_09=p_decel, flat_10_09_to_10_59=p_flat, accel_ge_10_59=p_accel, sliver_9_9925_to_10_09=p_sliver)),
             s01_state_means_used=state_mean, day1=dict(unconditional=E_r_uncond, given_r01=E_r_r01, given_not_r01=E_r_not_r01, given_r02=E_r_r02, given_not_r02=E_r_not_r02, given_r03=E_r_r03, memo_base_case_cell=E_r_basecase),
             r03=R03, monitoring_rule=monitor,
             alternatives_zero_weight=dict(sequential_all16=dict(r01=float(alts_df.iloc[0].p_r01), r02=float(alts_df.iloc[0].p_r02)),
                                           management_delivery_N06_13=dict(r01=float(alts_df[alts_df.view.str.contains("N\\(0.6,0.5\\) \\+ err N\\(0,1.3\\)")].p_r01.iloc[0]), r02=float(alts_df[alts_df.view.str.contains("N\\(0.6,0.5\\) \\+ err N\\(0,1.3\\)")].p_r02.iloc[0])),
                                           kalshi_mid=dict(r01=float(alts_df[alts_df.view.str.startswith("market: Kalshi KXABNB mid")].p_r01.iloc[0]), r02=float(alts_df[alts_df.view.str.startswith("market: Kalshi KXABNB mid")].p_r02.iloc[0])),
                                           rev1_blend=dict(r01=0.4237, r02=0.3159)),
             revintage_factors=dict(honest=r_b / r_v1, literal=r_a / r_v1, rmse=dict(published=RMSE_PUB, honest=RMSE_HON, literal=RMSE_LIT, naive=RMSE_NAIVE)))
save("a09_v2_final.json", final)

adopted = dict(
    object="Adopted 3Q26 Nights and Seats Booked print-state distribution (A09 revision 2, 2026-09-17). Read this, not the rev-1 N(9.67,1.70).",
    provenance="questions/risk-q3-nights-meets-guide/datasets/a09_v2_print_distribution.py (seed 20260917); audit A09 and response audits/A09-audit-response.md",
    parametric=dict(form="normal on latent 3Q26 nights y/y growth (%) over the fixed 133.6m base", centre=CENTRE, sd=SD,
                    centre_source="team nowcast +9.5% (brief rule 6; reviews index 9.5-10.0 bias-corrected 9.52; external stack 9.2; module 9.49)",
                    sd_source="reviews-index walk-forward RMSE, fresh-vintage W2 range 1.634-1.816 (published 1.475; naive 2.159); partial-to-full gap sd 0.2 adds 0.01",
                    rounding="printed millions = round(latent, 1); an event 'printed >= X.Ym' is latent >= X.Ym - 0.05m"),
    events=dict(R01_printed_ge_147_0m=dict(threshold_pct=T_R01, p=P_R01), R02_printed_ge_147_8m=dict(threshold_pct=T_R02, p=P_R02),
                R03_R01_and_C06a=dict(p=P_R03, p_r01_given_a=R03["p_r01_given_a"], c06_p_a=R03["p_a"])),
    print_states_r01_r02=dict(p_lt_10_0=1 - P_R01, p_10_0_to_10_6=P_R01 - P_R02, p_ge_10_6=P_R02, note="R01/R02 thresholds 146.95m / 147.75m"),
    print_states_s01=dict(decelerating_lt_10_09=p_decel, flat_10_09_to_10_59=p_flat, accelerating_ge_10_59=p_accel,
                          note="S01 revision 2 dead band on 2Q26's 10.34; the 9.9925-10.09 sliver (R01 Yes but S01 decelerating) has mass %.4f" % p_sliver),
    conditional_means_pct=dict(given_r01=m_r01, given_r02=m_r02, given_not_r01=cond_mean_lt(CENTRE, SD, T_R01), given_flat=cond_mean_between(CENTRE, SD, T_R01, T_R02)),
    sd_sensitivity=[dict(sd=round(s, 3), p_r01=p_ge(CENTRE, s, T_R01), p_r02=p_ge(CENTRE, s, T_R02), s01_accel=p_ge(CENTRE, s, S01_ACCEL), s01_decel=1 - p_ge(CENTRE, s, S01_DECEL)) for s in (1.0, 1.25, RMSE_PUB, RMSE_HON, SD, RMSE_LIT, 1.9, RMSE_NAIVE, 2.5)],
    centre_sensitivity=[dict(centre=c, p_r01=p_ge(c, SD, T_R01), p_r02=p_ge(c, SD, T_R02), s01_accel=p_ge(c, SD, S01_ACCEL), s01_decel=1 - p_ge(c, SD, S01_DECEL)) for c in (9.0, 9.2, 9.5, 9.9, 10.0, 10.3)],
    rebasing=dict(S01="YES: print states 0.595/0.085/0.32 -> %.3f/%.3f/%.3f and within-band N(9.67,1.70) -> N(9.5,1.70); a one-parameter re-run of s01_joint_v2.py (its rev-1-states sensitivity row already shows the direction: median about -0.3, base-case cell +0.02, breaker cell -0.02)" % (p_decel, p_flat, p_accel),
                  S02="YES for coherence, immaterial: accel 0.32 -> %.2f, flat 0.10 -> %.2f; decomposition median moves about -$0.7, P(<=150) +0.01 (inside its noise floor)" % (p_accel, P_R01 - P_R02),
                  C02="NO re-run needed: P(>=10.0) 0.423 -> %.3f moves (a) by about -0.01 and (d) by +0.01, below its 2-3 point noise floor; note the input change at X01 time" % P_R01,
                  C04="NO: R01 is recorded there as an input the log calls immaterial to its 3Q26 revenue draw ($8M on an $80M sd)",
                  X01="reads this file; must not use the rev-1 0.42/0.32 or N(9.67,1.70)"),
    superseded=dict(rev1_r01=0.4237, rev1_r02=0.3159, rev1_r03=0.0741, rev1_distribution="N(9.67,1.70) calibrated to a 0.60/0.30/0.10 blend of alt data, outside view and Kalshi (withdrawn: A09-01)"))
(QDIR / SLUGS[0] / "datasets/adopted_print_states_v2.json").write_text(json.dumps(adopted, indent=1), encoding="utf-8")

print(json.dumps(final, indent=1))
print(cons_df.to_string()); print(alts_df.drop(columns=["note"]).to_string()); print(joint_df.to_string()); print(imp_df.T.to_string())
print(windows.drop(columns=["errors"]).to_string())
