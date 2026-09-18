"""C11 q3-take-rate-above-1810: joint Monte Carlo of the printed 3Q26 take rate = revenue / same-quarter GBV.

Run from the repo root:  py -3.13 docs/pitch-forecasts/questions/q3-take-rate-above-1810/datasets/c11_model.py
numpy/pandas only, seeded. Writes c11_mc_summary.csv, c11_by_gbv_band.csv, c11_sensitivity.csv, c11_history.csv.

Structure (every input sourced in research-log.md):
  GBV_3Q26 = 22,884 x (1 + g_n) x (1 + g_a)                      3Q25 base: 133.6m nights x $171.29
  revenue  = 4,730 x (1 + cushion)                               2Q26 letter guide midpoint x beat; 19/19 beats
  cushion  = mu_c + rho x sd_c x z_gbv + sqrt(1-rho^2) x sd_c x e   part of the revenue beat is the same in-quarter demand
  take     = 100 x revenue / GBV_3Q26 ; YES <=> take >= 18.10
"""
from pathlib import Path
import numpy as np, pandas as pd

HERE = Path(__file__).resolve().parent
N = 400_000
GBV_3Q25 = 133.6 * 171.29          # 22,884.3 musd
GUIDE_MID = 4_730.0
GUIDE_LOW = 4_690.0
THRESH = 18.10

def run(nights_mu=9.5, nights_sd=1.6, adr_mu=3.3, adr_sd=1.3, cushion_mu=0.011, cushion_sd=0.005, rho=0.5,
        p_miss=0.03, gbv_override=None, gbv_override_sd=None, seed=20260917, n=N, rev_override=None, rev_override_sd=None):
    r = np.random.default_rng(seed)
    if gbv_override is None:
        gn = r.normal(nights_mu, nights_sd, n) / 100
        ga = r.normal(adr_mu, adr_sd, n) / 100
        gbv = GBV_3Q25 * (1 + gn) * (1 + ga)
    else:
        gbv = r.normal(gbv_override, gbv_override_sd, n)
    z = (gbv - gbv.mean()) / gbv.std()
    e = r.normal(0, 1, n)
    if rev_override is None:
        c = cushion_mu + cushion_sd * (rho * z + np.sqrt(1 - rho**2) * e)
        rev = GUIDE_MID * (1 + c)
        miss = r.random(n) < p_miss                       # a first-ever guide miss: revenue lands at the low end
        rev = np.where(miss, GUIDE_LOW * (1 + r.normal(-0.003, 0.004, n)), rev)
    else:
        rev = rev_override + rev_override_sd * (rho * z + np.sqrt(1 - rho**2) * e)
    take = 100 * rev / gbv
    yes = take >= THRESH
    return dict(p_yes=yes.mean(), take_mean=take.mean(), take_sd=take.std(), take_q10=np.percentile(take, 10),
                take_q50=np.percentile(take, 50), take_q90=np.percentile(take, 90), gbv_mean=gbv.mean(), gbv_sd=gbv.std(),
                rev_mean=rev.mean(), rev_sd=rev.std(), p_le_1788=(take <= 17.88).mean(), gbv=gbv, take=take)

if __name__ == "__main__":
    base = run()
    keep = {k: v for k, v in base.items() if k not in ("gbv", "take")}
    pd.DataFrame([keep]).T.rename(columns={0: "value"}).to_csv(HERE / "c11_mc_summary.csv")
    print("BASE (team band)"); [print(f"  {k:>12}: {v:,.4f}") for k, v in keep.items()]

    # ---- final mixture: 0.50 team band, 0.30 market-implied GBV (Kalshi nights median 148.3m x ADR +3.4%), 0.20 wide
    comps = [(0.50, run(seed=1)),
             (0.30, run(seed=2, gbv_override=26_260.0, gbv_override_sd=600.0)),
             (0.20, run(seed=3, nights_mu=10.0, nights_sd=2.2, adr_mu=3.3, adr_sd=1.8, cushion_sd=0.008))]
    gmix = np.concatenate([o["gbv"][: int(w * N)] for w, o in comps]); tmix = np.concatenate([o["take"][: int(w * N)] for w, o in comps])
    p_mix = (tmix >= THRESH).mean()
    print("FINAL MIXTURE P(>=18.10) =", round(p_mix, 3), "take median", round(np.median(tmix), 3), "sd", round(tmix.std(), 3),
          "P(<=17.88)", round((tmix <= 17.88).mean(), 3))

    # ---- conditional on GBV band (fine print) ----
    bands = [(0, 25_600), (25_600, 25_900), (25_900, 26_200), (26_200, 26_500), (26_500, 26_800), (26_800, 1e9)]
    rows = []
    for lo, hi in bands:
        m = (gmix >= lo) & (gmix < hi)
        rows.append(dict(gbv_band_musd=f"{lo:,.0f}-{hi:,.0f}" if hi < 1e8 else f">= {lo:,.0f}", mass=round(m.mean(), 3),
                         p_yes_given_band=round((tmix[m] >= THRESH).mean(), 3) if m.any() else None,
                         take_median_given_band=round(np.median(tmix[m]), 3) if m.any() else None,
                         gbv_yoy_pct=f"{(lo/GBV_3Q25-1)*100:.1f} to {(hi/GBV_3Q25-1)*100:.1f}" if hi < 1e8 else f">= {(lo/GBV_3Q25-1)*100:.1f}"))
    # point-GBV rows like B1's 04_gbv_sensitivity, at the guide-cushion revenue
    for g in [25_600, 25_900, 26_185, 26_300, 26_410, 26_550, 26_800, 27_000]:
        o = run(seed=7, gbv_override=float(g), gbv_override_sd=1.0)
        rows.append(dict(gbv_band_musd=f"point {g:,}", mass=None, p_yes_given_band=round(o["p_yes"], 3),
                         take_median_given_band=round(o["take_q50"], 3), gbv_yoy_pct=f"{(g/GBV_3Q25-1)*100:.1f}"))
    bt = pd.DataFrame(rows); bt.to_csv(HERE / "c11_by_gbv_band.csv", index=False); print(bt.to_string())

    # ---- sensitivities ----
    sens = []
    def add(label, **kw):
        o = run(**kw); sens.append(dict(assumption=label, p_yes=round(o["p_yes"], 3), take_q50=round(o["take_q50"], 3),
                                        take_sd=round(o["take_sd"], 3), gbv_mean=round(o["gbv_mean"]), rev_mean=round(o["rev_mean"])))
    add("BASE: nights 9.5+-1.6, ADR 3.3+-1.3, cushion 1.1%+-0.5% rho 0.5, P(miss) 3%")
    add("GBV = Kalshi-implied N(26,260, 600)", gbv_override=26_260.0, gbv_override_sd=600.0)
    add("GBV = Bloomberg MODL N(26,375, 600)", gbv_override=26_375.0, gbv_override_sd=600.0)
    add("GBV = management 'mid teens' midpoint N(26,317, 550)", gbv_override=26_317.0, gbv_override_sd=550.0)
    add("GBV = programme stacked N(26,550, 853) (B1 input)", gbv_override=26_549.8, gbv_override_sd=853.2)
    add("B1 REPLICATION: GBV N(26,550,853), revenue N(4,816,48), rho 0.76", gbv_override=26_549.8, gbv_override_sd=853.2, rev_override=4_816.1, rev_override_sd=48.0, rho=0.7595)
    add("nights at top of band 10.0", nights_mu=10.0)
    add("nights at bottom of band 8.5", nights_mu=8.5)
    add("nights 11.0 (Kalshi median), ADR 3.4", nights_mu=11.0, adr_mu=3.4)
    add("ADR +2.0 (B02 case)", adr_mu=2.0)
    add("ADR +4.4 (R07 case)", adr_mu=4.4)
    add("cushion = Q3 2024-25 mean 0.86%", cushion_mu=0.0086)
    add("cushion = 3Q23 1.40%", cushion_mu=0.014)
    add("cushion = trailing-8 all-quarter 1.86%", cushion_mu=0.0186)
    add("cushion = 0 (print at guide midpoint)", cushion_mu=0.0, cushion_sd=0.003)
    add("cushion sd 1.0%", cushion_sd=0.010)
    add("rho 0 (revenue beat independent of GBV)", rho=0.0)
    add("rho 0.8", rho=0.8)
    add("P(guide miss) 0", p_miss=0.0)
    add("P(guide miss) 10%", p_miss=0.10)
    add("bull GBV: nights 11.0, ADR 4.4, cushion 0.86", nights_mu=11.0, adr_mu=4.4, cushion_mu=0.0086)
    add("bear GBV: nights 8.5, ADR 2.0, cushion 1.4", nights_mu=8.5, adr_mu=2.0, cushion_mu=0.014)
    s = pd.DataFrame(sens); s.to_csv(HERE / "c11_sensitivity.csv", index=False)
    pd.set_option("display.width", 250); print(s.to_string())

    # ---- printed Q3 take-rate history and the y/y wedge decomposition (letters) ----
    hist = pd.DataFrame([
        dict(quarter="3Q21", revenue=2237, gbv=11900, rev_fx=3, gbv_fx=2),
        dict(quarter="3Q22", revenue=2884, gbv=15600, rev_fx=-7, gbv_fx=-9),
        dict(quarter="3Q23", revenue=3397, gbv=18300, rev_fx=4, gbv_fx=3),
        dict(quarter="3Q24", revenue=3732, gbv=20100, rev_fx=0, gbv_fx=0),
        dict(quarter="3Q25", revenue=4095, gbv=22900, rev_fx=0, gbv_fx=2),
    ])
    hist["take_rate_pct"] = 100 * hist.revenue / hist.gbv
    hist["take_rate_yoy_bp"] = (hist.take_rate_pct.diff() * 100).round(0)
    hist["fx_wedge_rev_minus_gbv_pp"] = hist.rev_fx - hist.gbv_fx
    hist.to_csv(HERE / "c11_history.csv", index=False); print(hist.round(3).to_string())
