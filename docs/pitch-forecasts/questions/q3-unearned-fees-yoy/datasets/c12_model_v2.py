"""C12 q3-unearned-fees-yoy, revision 2 (audit response to A05). P(unearned fees at 30 Sep 2026 <= -3% y/y vs $1,820M).

Changes from revision 1 (finding ids in research-log.md section 10):
  * u_3Q26 (effective unpaid-RNPL shortfall of the fee-bearing backlog at B = 1) is a THREE-BRANCH mixture that carries the
    alternative reading of management's D038 sentence (A05-07): catch-up (u falls vs 30 Jun), convergence (u tracks ~0.70 x
    the disclosed flow share), deepening (July expansion / longer-dated Q4-Q1 book / C06's P(flow >= 25%) = 0.39);
  * the quoted solved ranges are note 04's (A05-08): 1Q26 10.7-13.9% and 2Q26 14.0-16.8% at B = 1.00; u and B inseparable;
  * Route C uses the two-year pre-RNPL norm 0.6648 +- 0.008 (A05-09), 4Q26 revenue N(3,170, 70) (bridge v3 3,178; C01 rev 2 print mean 3,162);
  * Route B ties its sequential deepening to the same u mixture instead of a free N(-1.5, 1.5) (A05-07);
  * GBV growth in Route A is drawn from the run's print-state distribution (R01 nights N(9.67, 1.70) x B02 ADR mixture);
  * the historical frequency of the event is published (A05-13).
Run from the repo root:  py -3.13 docs/pitch-forecasts/questions/q3-unearned-fees-yoy/datasets/c12_model_v2.py
Writes c12_v2_routes.csv, c12_v2_sensitivity.csv, c12_v2_deferral_table.csv, c12_v2_base_rate.csv, c12_v2_u_mixture.csv.
"""
from pathlib import Path
import numpy as np, pandas as pd

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[4]
N = 600_000
UF_3Q25, UF_2Q26 = 1_820.0, 2_831.0
THRESH = -0.03
GBV_3Q25 = 133.6 * 171.29

# ---- u_3Q26 mixture (all three branches are judgments; weights labelled) ----
U_BRANCHES = [  # (label, weight, mean, sd)
    ("catch-up: D038 read as a flow statement (summer RNPL payments land in Q3; 30 Sep book is nearer-dated); u below 30 Jun's 15.1", 0.30, 14.5, 2.0),
    ("convergence: u tracks ~0.70 x the disclosed flow share (2Q26: 15.1 solved / 'over 20%' stated); Q3 flow ~24 (C06 v2 median)", 0.45, 17.0, 2.5),
    ("deepening: July eligibility expansion + longer-dated Q4/Q1 book at 30 Sep (B > 1 read as higher effective u); C06 P(flow >= 25) 0.39", 0.25, 19.5, 3.0),
]

def draw_u(r, n, branches=U_BRANCHES):
    w = np.array([b[1] for b in branches]); w = w / w.sum()
    idx = r.choice(len(branches), size=n, p=w)
    mu = np.array([b[2] for b in branches])[idx]; sd = np.array([b[3] for b in branches])[idx]
    return r.normal(mu, sd)

def adr_draws(r, n):
    mix = r.normal(-1.15, 0.35, n); u = r.random(n)
    res = np.select([u < 0.45, u < 0.60, u < 0.85], [r.normal(4.85, 0.55, n), r.normal(5.35, 0.55, n), r.normal(4.37, 0.94, n)], r.normal(3.6, 0.7, n))
    v = r.random(n); fx = np.select([v < 0.5, v < 0.75], [r.normal(-0.43, 0.33, n), r.normal(0.26, 0.42, n)], r.normal(-1.12, 0.46, n))
    return mix + res + fx

def gbv_yoy_draws(r, n, nights_mu=9.67, nights_sd=1.70):
    gn = r.normal(nights_mu, nights_sd, n) / 100; ga = adr_draws(r, n) / 100
    return ((1 + gn) * (1 + ga) - 1) * 100

def route_a(u_branches=U_BRANCHES, gbv_mu=None, gbv_sd=1.9, u25_mu=3.5, u25_sd=1.0, k_mu=1.16, k_sd=0.15, mig_mu=1.0, mig_sd=0.7, fx_sd=0.5, seed=1, n=N, u_fixed=None):
    r = np.random.default_rng(seed)
    gbv = r.normal(gbv_mu, gbv_sd, n) if gbv_mu is not None else gbv_yoy_draws(r, n)
    u26 = draw_u(r, n, u_branches) if u_fixed is None else r.normal(u_fixed[0], u_fixed[1], n)
    u25 = r.normal(u25_mu, u25_sd, n); k = r.normal(k_mu, k_sd, n); mig = r.normal(mig_mu, mig_sd, n); fx = r.normal(0, fx_sd, n)
    return (gbv - k * (u26 - u25) + mig + fx) / 100

def route_b(u_branches=U_BRANCHES, seq_mu=-36.9, seq_sd=1.0, u2q_mu=15.1, u2q_sd=1.0, mig_incr_mu=0.4, mig_incr_sd=0.3, seed=2, n=N, u_fixed=None):
    """Sequential: (1 + seq) = (1 + seq_norm) x (1 - u_3Q26)/(1 - u_2Q26) x (1 + within-quarter migration increment)."""
    r = np.random.default_rng(seed)
    seq_norm = r.normal(seq_mu, seq_sd, n) / 100
    u26 = (draw_u(r, n, u_branches) if u_fixed is None else r.normal(u_fixed[0], u_fixed[1], n)) / 100
    u2q = r.normal(u2q_mu, u2q_sd, n) / 100; mig = r.normal(mig_incr_mu, mig_incr_sd, n) / 100
    uf = UF_2Q26 * (1 + seq_norm) * (1 - u26) / (1 - u2q) * (1 + mig)
    return uf / UF_3Q25 - 1

def route_c(u_branches=U_BRANCHES, norm_mu=0.664776, norm_sd=0.008, rev4_mu=3_170.0, rev4_sd=70.0, mig_mu=1.5, mig_sd=1.0, fx_sd=0.5, seed=3, n=N, u_fixed=None):
    r = np.random.default_rng(seed)
    norm = r.normal(norm_mu, norm_sd, n); rev4 = r.normal(rev4_mu, rev4_sd, n)
    u = (draw_u(r, n, u_branches) if u_fixed is None else r.normal(u_fixed[0], u_fixed[1], n)) / 100
    mig = r.normal(mig_mu, mig_sd, n) / 100; fx = r.normal(0, fx_sd, n) / 100
    return norm * rev4 * (1 - u) * (1 + mig) * (1 + fx) / UF_3Q25 - 1

def summarise(label, yoy):
    return dict(route=label, p_yes=round((yoy <= THRESH).mean(), 3), median_yoy_pct=round(np.median(yoy) * 100, 2),
                q10_pct=round(np.percentile(yoy, 10) * 100, 2), q90_pct=round(np.percentile(yoy, 90) * 100, 2),
                median_uf_musd=round(UF_3Q25 * (1 + np.median(yoy))), p_ge_plus6=round((yoy >= 0.06).mean(), 3),
                p_inconclusive=round(((yoy > THRESH) & (yoy < 0.06)).mean(), 3))

W = dict(A=0.45, B=0.30, C=0.25)
def mixture(A, B, C, w=W):
    return np.concatenate([A[: int(w["A"] * N)], B[: int(w["B"] * N)], C[: int(w["C"] * N)]])

if __name__ == "__main__":
    pd.set_option("display.width", 250); pd.set_option("display.max_colwidth", 120)
    r0 = np.random.default_rng(0); u_s = draw_u(r0, N)
    um = pd.DataFrame([dict(branch=b[0], weight=b[1], mean=b[2], sd=b[3]) for b in U_BRANCHES] +
                      [dict(branch="MIXTURE", weight=1.0, mean=round(u_s.mean(), 2), sd=round(u_s.std(), 2))])
    um.to_csv(HERE / "c12_v2_u_mixture.csv", index=False); print(um.to_string())
    print("u mixture percentiles 10/50/90:", np.percentile(u_s, [10, 50, 90]).round(1), "P(u >= 17.7)", round((u_s >= 17.7).mean(), 3))

    A, B, C = route_a(), route_b(), route_c()
    M = mixture(A, B, C)
    rows = [summarise("A y/y gap (R01 x B02 GBV; u mixture)", A), summarise("B sequential (norm -36.9 +-1.0; deepening tied to u)", B),
            summarise("C norm level (0.6648 x 4Q26 revenue 3,170; u mixture)", C), summarise("MIXTURE 0.45 A / 0.30 B / 0.25 C", M),
            summarise("MIXTURE equal weights", mixture(A, B, C, dict(A=1 / 3, B=1 / 3, C=1 / 3)))]
    rt = pd.DataFrame(rows); rt.to_csv(HERE / "c12_v2_routes.csv", index=False); print(rt.to_string())

    sens = []
    def add(label, yoy): sens.append(summarise(label, yoy))
    add("all routes: u = catch-up branch only N(14.5, 2)", mixture(route_a(u_fixed=(14.5, 2)), route_b(u_fixed=(14.5, 2)), route_c(u_fixed=(14.5, 2))))
    add("all routes: u = convergence branch only N(17, 2.5)", mixture(route_a(u_fixed=(17, 2.5)), route_b(u_fixed=(17, 2.5)), route_c(u_fixed=(17, 2.5))))
    add("all routes: u = deepening branch only N(19.5, 3)", mixture(route_a(u_fixed=(19.5, 3)), route_b(u_fixed=(19.5, 3)), route_c(u_fixed=(19.5, 3))))
    add("all routes: u = rev-1 N(18, 3)", mixture(route_a(u_fixed=(18, 3)), route_b(u_fixed=(18, 3)), route_c(u_fixed=(18, 3))))
    add("all routes: u = Astra N(16.5, 4)", mixture(route_a(u_fixed=(16.5, 4)), route_b(u_fixed=(16.5, 4)), route_c(u_fixed=(16.5, 4))))
    add("all routes: u = flat at 2Q26 solved N(15.1, 1.5)", mixture(route_a(u_fixed=(15.1, 1.5)), route_b(u_fixed=(15.1, 1.5)), route_c(u_fixed=(15.1, 1.5))))
    add("all routes: u = 20 +- 3", mixture(route_a(u_fixed=(20, 3)), route_b(u_fixed=(20, 3)), route_c(u_fixed=(20, 3))))
    add("u weights 0.45 catch-up / 0.40 convergence / 0.15 deepening", mixture(*[f(u_branches=[(U_BRANCHES[0][0], 0.45) + U_BRANCHES[0][2:], (U_BRANCHES[1][0], 0.40) + U_BRANCHES[1][2:], (U_BRANCHES[2][0], 0.15) + U_BRANCHES[2][2:]]) for f in (route_a, route_b, route_c)]))
    add("u weights 0.15 catch-up / 0.45 convergence / 0.40 deepening", mixture(*[f(u_branches=[(U_BRANCHES[0][0], 0.15) + U_BRANCHES[0][2:], (U_BRANCHES[1][0], 0.45) + U_BRANCHES[1][2:], (U_BRANCHES[2][0], 0.40) + U_BRANCHES[2][2:]]) for f in (route_a, route_b, route_c)]))
    add("A: GBV Street +15.2 +-1.9", mixture(route_a(gbv_mu=15.2), B, C))
    add("A: GBV +11.0 +-1.9", mixture(route_a(gbv_mu=11.0), B, C))
    add("A: GBV rev-1 N(13.2, 1.9)", mixture(route_a(gbv_mu=13.2), B, C))
    add("A: u_3Q25 base 5", mixture(route_a(u25_mu=5.0), B, C))
    add("A: u_3Q25 base 2", mixture(route_a(u25_mu=2.0), B, C))
    add("A: migration 0 (migration-neutral)", mixture(route_a(mig_mu=0.0, mig_sd=0.3), B, C))
    add("A: migration +2", mixture(route_a(mig_mu=2.0), B, C))
    add("A: k 1.0", mixture(route_a(k_mu=1.0), B, C))
    add("B: seq norm sd 0.6 (2023-25 sample sd)", mixture(A, route_b(seq_sd=0.6), C))
    add("B: seq = 3Q25 only (-36.3)", mixture(A, route_b(seq_mu=-36.3), C))
    add("B: u_2Q26 13.0 (note 04 1Q26-2Q26 low end)", mixture(A, route_b(u2q_mu=13.0), C))
    add("C: norm 0.661 (three-year, RNPL launch quarter included)", mixture(A, B, route_c(norm_mu=0.661566)))
    add("C: norm 0.655 (3Q25 ratio only)", mixture(A, B, route_c(norm_mu=0.655148)))
    add("C: 4Q26 revenue 3,130 (bridge v2)", mixture(A, B, route_c(rev4_mu=3_130.0)))
    add("C: 4Q26 revenue 3,240 (kernel at stacked GBV)", mixture(A, B, route_c(rev4_mu=3_240.0)))
    add("C: migration 0", mixture(A, B, route_c(mig_mu=0.0, mig_sd=0.3)))
    add("weights all A", A); add("weights all B", B); add("weights all C", C)
    add("joint bear-for-YES: GBV 11, u deepening only, migration 0", mixture(route_a(gbv_mu=11.0, u_fixed=(19.5, 3), mig_mu=0.0), route_b(u_fixed=(19.5, 3)), route_c(u_fixed=(19.5, 3), mig_mu=0.0)))
    add("joint bull-for-NO: GBV 15.2, u catch-up only, migration 2", mixture(route_a(gbv_mu=15.2, u_fixed=(14.5, 2), mig_mu=2.0), route_b(u_fixed=(14.5, 2)), route_c(u_fixed=(14.5, 2), mig_mu=2.5)))
    s = pd.DataFrame(sens); s.to_csv(HERE / "c12_v2_sensitivity.csv", index=False); print(s.to_string())

    # ---- Astra's comparison model, reproduced with this seed ----
    r = np.random.default_rng(12)
    for um_ in (0.15, 0.165, 0.18):
        bal = r.normal(0.664776, 0.008, N) * r.normal(3_178.108, 60, N) * (1 - r.normal(um_, 0.04, N)) * (1 + r.normal(0.01, 0.01, N)) * (1 + r.normal(0, 0.005, N))
        print(f"Astra model u {um_}: P", round((bal <= 0.97 * UF_3Q25).mean(), 3), "median", round(np.median(bal)))

    # ---- deferral table v2 (central inputs; Route C level form) ----
    tab = []
    for u in [12, 14, 15, 16, 17, 17.7, 18, 20, 22, 25]:
        for rev4 in [3_130, 3_170, 3_240]:
            uf = 0.664776 * rev4 * (1 - u / 100) * 1.015
            tab.append(dict(u_3Q26_pct=u, rev_4q26_musd=rev4, uf_musd=round(uf), uf_yoy_pct=round((uf / UF_3Q25 - 1) * 100, 1), yes=uf <= 0.97 * UF_3Q25))
    t = pd.DataFrame(tab); t.to_csv(HERE / "c12_v2_deferral_table.csv", index=False)
    print(t[t.rev_4q26_musd.eq(3_170)].to_string())

    # ---- historical frequency of the event (A05-13) ----
    k = pd.read_csv(ROOT / "data/processed/overnight/02_kpi_panel_quarterly.csv", comment="#")
    k["ord"] = k.quarter.str[-2:].astype(int) * 4 + k.quarter.str[0].astype(int); k = k.sort_values("ord").reset_index(drop=True)
    k["uf_yoy"] = k.unearned_fees_musd.pct_change(4) * 100
    k["gbv_yoy"] = k.gbv_musd.pct_change(4) * 100
    k["gap"] = k.uf_yoy - k.gbv_yoy
    k["seq"] = k.unearned_fees_musd.pct_change() * 100
    k["norm_next"] = k.unearned_fees_musd / k.revenue_musd.shift(-1)
    kk = k[k.uf_yoy.notna()][["quarter", "unearned_fees_musd", "uf_yoy", "gbv_yoy", "gap", "seq", "norm_next"]]
    kk.to_csv(HERE / "c12_v2_base_rate.csv", index=False); print(kk.round(3).to_string())
    for lab, sub in [("W1 (1Q23+)", kk[kk.quarter.str[-2:].astype(int) >= 23]), ("W2 (1Q24+)", kk[kk.quarter.str[-2:].astype(int) >= 24]),
                     ("Q3 only", kk[kk.quarter.str.startswith("3Q")]), ("post-launch 3Q25-2Q26", kk[kk.quarter.isin(["3Q25", "4Q25", "1Q26", "2Q26"])])]:
        print(lab, "UF y/y <= -3%:", int((sub.uf_yoy <= -3).sum()), "/", len(sub), "| gap <= -12:", int((sub.gap <= -12).sum()), "/", len(sub),
              "| min gap", round(sub.gap.min(), 1))
