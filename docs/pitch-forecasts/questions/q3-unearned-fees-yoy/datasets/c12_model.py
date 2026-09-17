"""C12 q3-unearned-fees-yoy: P(unearned fees at 30 Sep 2026 <= -3% y/y vs $1,820M at 30 Sep 2025).

Run from the repo root:  py -3.13 docs/pitch-forecasts/questions/q3-unearned-fees-yoy/datasets/c12_model.py
numpy/pandas only, seeded. Writes c12_history.csv, c12_routes.csv, c12_sensitivity.csv, c12_deferral_table.csv.

Three routes, each a decomposition into deferral (RNPL unpaid share u), migration (single fee raises the fee per
booking held in unearned fees), and FX (translation, small; the balance reconciles to the cash-flow line within $3-8M):

  Route A (y/y gap):     UF_yoy = GBV_yoy - k x (u_3Q26 - u_3Q25) + mig_incr + fx
  Route B (sequential):  UF_3Q26 = UF_2Q26 x (1 + seq_3Q), seq_3Q = 2023-25 mean Q3 change + 2026 deepening term
  Route C (norm level):  UF_3Q26 = norm_3Q x Rev_4Q26 x (1 - u_3Q26) x (1 + mig) x (1 + fx)
"""
from pathlib import Path
import numpy as np, pandas as pd

HERE = Path(__file__).resolve().parent
N = 400_000
UF_3Q25, UF_2Q26 = 1_820.0, 2_831.0
THRESH = -0.03

hist = pd.DataFrame([
    dict(q="1Q23", uf=2172, gbv=20400, rev_next=2484), dict(q="2Q23", uf=2347, gbv=19100, rev_next=3397),
    dict(q="3Q23", uf=1467, gbv=18300, rev_next=2218), dict(q="4Q23", uf=1427, gbv=15500, rev_next=2142),
    dict(q="1Q24", uf=2434, gbv=22900, rev_next=2748), dict(q="2Q24", uf=2621, gbv=21200, rev_next=3732),
    dict(q="3Q24", uf=1657, gbv=20100, rev_next=2480), dict(q="4Q24", uf=1616, gbv=17600, rev_next=2272),
    dict(q="1Q25", uf=2723, gbv=24500, rev_next=3096), dict(q="2Q25", uf=2857, gbv=23500, rev_next=4095),
    dict(q="3Q25", uf=1820, gbv=22900, rev_next=2778), dict(q="4Q25", uf=1743, gbv=20400, rev_next=2678),
    dict(q="1Q26", uf=2733, gbv=29200, rev_next=3608), dict(q="2Q26", uf=2831, gbv=27200, rev_next=np.nan),
])
hist["uf_yoy"] = hist.uf.pct_change(4) * 100
hist["gbv_yoy"] = hist.gbv.pct_change(4) * 100
hist["gap_pts"] = hist.uf_yoy - hist.gbv_yoy
hist["seq_pct"] = hist.uf.pct_change() * 100
hist["uf_to_next_rev"] = hist.uf / hist.rev_next
hist.to_csv(HERE / "c12_history.csv", index=False)
pd.set_option("display.width", 250); print(hist.round(3).to_string())

def route_a(gbv_mu=13.2, gbv_sd=1.9, u26_mu=18.0, u26_sd=3.0, u25_mu=3.5, u25_sd=1.0, k_mu=1.16, k_sd=0.15,
            mig_mu=1.0, mig_sd=0.7, fx_sd=0.5, seed=1, n=N):
    r = np.random.default_rng(seed)
    gbv = r.normal(gbv_mu, gbv_sd, n); u26 = r.normal(u26_mu, u26_sd, n); u25 = r.normal(u25_mu, u25_sd, n)
    k = r.normal(k_mu, k_sd, n); mig = r.normal(mig_mu, mig_sd, n); fx = r.normal(0, fx_sd, n)
    yoy = gbv - k * (u26 - u25) + mig + fx
    return yoy / 100

def route_b(seq_mu=-36.9, seq_sd=0.6, deepen_mu=-1.5, deepen_sd=1.5, seed=2, n=N):
    r = np.random.default_rng(seed)
    seq = r.normal(seq_mu, seq_sd, n) + r.normal(deepen_mu, deepen_sd, n)
    uf = UF_2Q26 * (1 + seq / 100)
    return uf / UF_3Q25 - 1

def route_c(norm_mu=0.661, norm_sd=0.004, rev4_mu=3_178.0, rev4_sd=60.0, u_mu=18.0, u_sd=3.0, mig_mu=1.5, mig_sd=1.0,
            fx_sd=0.5, base_u25_adj=True, seed=3, n=N):
    r = np.random.default_rng(seed)
    norm = r.normal(norm_mu, norm_sd, n); rev4 = r.normal(rev4_mu, rev4_sd, n); u = r.normal(u_mu, u_sd, n) / 100
    mig = r.normal(mig_mu, mig_sd, n) / 100; fx = r.normal(0, fx_sd, n) / 100
    uf = norm * rev4 * (1 - u) * (1 + mig) * (1 + fx)
    return uf / UF_3Q25 - 1

def summarise(label, yoy):
    return dict(route=label, p_yes=round((yoy <= THRESH).mean(), 3), median_yoy_pct=round(np.median(yoy) * 100, 2),
                q10_pct=round(np.percentile(yoy, 10) * 100, 2), q90_pct=round(np.percentile(yoy, 90) * 100, 2),
                median_uf_musd=round(UF_3Q25 * (1 + np.median(yoy))), p_ge_plus6=round((yoy >= 0.06).mean(), 3))

if __name__ == "__main__":
    A, B, C = route_a(), route_b(), route_c()
    rows = [summarise("A y/y gap (team GBV 13.2)", A), summarise("B sequential (2023-25 Q3 mean -36.9%, deepening -1.5)", B),
            summarise("C norm level (0.661 x 4Q26 revenue 3,178)", C)]
    mixw = [0.45, 0.30, 0.25]
    M = np.concatenate([A[: int(mixw[0] * N)], B[: int(mixw[1] * N)], C[: int(mixw[2] * N)]])
    rows.append(summarise("MIXTURE 0.45 A / 0.30 B / 0.25 C", M))
    rt = pd.DataFrame(rows); rt.to_csv(HERE / "c12_routes.csv", index=False); print(rt.to_string())

    sens = []
    def add(label, yoy): sens.append(summarise(label, yoy))
    add("A: GBV Street 15.2 +-1.9", route_a(gbv_mu=15.2))
    add("A: GBV 11.0", route_a(gbv_mu=11.0))
    add("A: u_3Q26 15 (flat vs 2Q26)", route_a(u26_mu=15.0))
    add("A: u_3Q26 20 (July expansion + international ramp)", route_a(u26_mu=20.0))
    add("A: u_3Q26 22", route_a(u26_mu=22.0))
    add("A: u_3Q25 base 5 (US launch quarter carried more)", route_a(u25_mu=5.0))
    add("A: migration 0 (audit's migration-neutral reading)", route_a(mig_mu=0.0, mig_sd=0.3))
    add("A: migration +2", route_a(mig_mu=2.0))
    add("A: k 1.0", route_a(k_mu=1.0))
    add("B: no deepening (Q3 decline equals 2023-25 mean)", route_b(deepen_mu=0.0, deepen_sd=1.0))
    add("B: deepening -3 (1Q26-style)", route_b(deepen_mu=-3.0))
    add("B: seq = 3Q25 only (-36.3)", route_b(seq_mu=-36.3))
    add("C: 4Q26 revenue 3,130 (bridge v2)", route_c(rev4_mu=3_130.0))
    add("C: 4Q26 revenue 3,240 (kernel at stacked GBV)", route_c(rev4_mu=3_240.0))
    add("C: u 15", route_c(u_mu=15.0))
    add("C: u 20", route_c(u_mu=20.0))
    add("C: norm 0.655 (3Q25 ratio, RNPL-contaminated)", route_c(norm_mu=0.655))
    add("C: migration 0", route_c(mig_mu=0.0, mig_sd=0.3))
    add("joint bear for YES: GBV 11, u 20, migration 0", route_a(gbv_mu=11.0, u26_mu=20.0, mig_mu=0.0))
    add("joint bull for NO: GBV 15.2, u 15, migration 2", route_a(gbv_mu=15.2, u26_mu=15.0, mig_mu=2.0))
    s = pd.DataFrame(sens); s.to_csv(HERE / "c12_sensitivity.csv", index=False); print(s.to_string())

    # deferral-only table at fixed inputs (for the log's decomposition section)
    tab = []
    for u in [12, 15, 17, 18, 20, 22, 25]:
        for g in [11.0, 13.2, 15.2]:
            yoy = g - 1.16 * (u - 3.5) + 1.0
            tab.append(dict(u_3Q26_pct=u, gbv_yoy_pct=g, uf_yoy_pct=round(yoy, 1), uf_musd=round(UF_3Q25 * (1 + yoy / 100)), yes=yoy <= -3))
    t = pd.DataFrame(tab); t.to_csv(HERE / "c12_deferral_table.csv", index=False); print(t.to_string())
