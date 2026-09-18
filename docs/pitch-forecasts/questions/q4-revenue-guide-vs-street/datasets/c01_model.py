"""C01 q4-revenue-guide-vs-street: Monte Carlo for the 5 Nov 2026 4Q26 revenue guide midpoint
versus the LSEG-family 4Q26 revenue consensus mean on 4 Nov 2026.

Run from the repo root:  py -3.13 docs/pitch-forecasts/questions/q4-revenue-guide-vs-street/datasets/c01_model.py
Dependency-free apart from numpy/pandas. Seed fixed. Writes c01_mc_summary.csv, c01_percentiles.csv,
c01_sensitivity.csv, c01_base_rates.csv next to this file.

Structure (every input sourced in research-log.md claims ledger):
  print_4Q26   = lambda_Q4 * (1 + eps) * [2/3 GBV_3Q26 + 1/3 GBV_2Q26] * (1 + fee_step)
  guide_mid    = round5(print_4Q26 / (1 + cushion))
  GBV_3Q26     = nights_3Q25 * (1 + g_n) * ADR_3Q25 * (1 + g_a)
  street_4Nov  = street_now * (1 + drift)
  YES          <=> guide given AND guide_mid < street_4Nov
"""
from pathlib import Path
import numpy as np, pandas as pd

HERE = Path(__file__).resolve().parent
rng = np.random.default_rng(20260917)
N = 400_000

# ---- printed / registered inputs -------------------------------------------------------------
GBV_2Q26 = 27_200.0            # 2Q26 letter, printed
NIGHTS_3Q25 = 133.6            # m, 3Q25 letter
ADR_3Q25 = 171.29              # $, 3Q25 letter (GBV 22,884)
LAMBDA_Q4 = 0.120298           # kernel-lambda.md: mean of 4Q23 11.946 / 4Q24 12.117 / 4Q25 12.026
STREET_NOW = 3_161.02          # yfinance revenue_estimate +1q avg, LSEG family, captured 2026-09-17T02:52Z (n 36 on 13 Sep)
CUSHION_T8 = 0.018567          # guidance-policy.md trailing-8 mean, sd 1.0048pp
CUSHION_Q4 = 0.030419          # Q4 guides 2023-25: 3.16 / 2.69 / 3.27, sd 0.31pp (computed from 02_guidance_ledger.csv)
P_GUIDE_GIVEN = 0.99           # 20 of 20 letters since 3Q21 carried a next-quarter revenue dollar range

def run(nights_mu=9.5, nights_sd=1.6, adr_mu=3.3, adr_sd=1.3,
        eps_mu=-0.005, eps_sd=0.020,
        fee_w=(0.45, 0.40, 0.15), fee_steps=(0.0, 0.005543, 0.011086),
        cushion_mu=0.024, cushion_sd=0.010,
        drift_mu=0.0, drift_sd=0.006, street_now=STREET_NOW, seed=20260917, n=N,
        gbv_override=None, gbv_override_sd=None):
    r = np.random.default_rng(seed)
    if gbv_override is None:
        g_n = r.normal(nights_mu, nights_sd, n) / 100
        g_a = r.normal(adr_mu, adr_sd, n) / 100
        gbv3 = NIGHTS_3Q25 * (1 + g_n) * ADR_3Q25 * (1 + g_a)
    else:
        gbv3 = r.normal(gbv_override, gbv_override_sd, n)
    base = (2/3) * gbv3 + (1/3) * GBV_2Q26
    eps = r.normal(eps_mu, eps_sd, n)
    fee = r.choice(np.array(fee_steps), size=n, p=np.array(fee_w))
    print_ = LAMBDA_Q4 * (1 + eps) * base * (1 + fee)
    c = r.normal(cushion_mu, cushion_sd, n)
    guide = np.round(print_ / (1 + c) / 5) * 5          # letters give $X.XX bn endpoints -> $5m midpoint grid
    street = street_now * (1 + r.normal(drift_mu, drift_sd, n))
    given = r.random(n) < P_GUIDE_GIVEN
    yes = given & (guide < street)
    surprise = given & (guide < street * (1 - CUSHION_T8))
    q = np.percentile(guide, [5, 10, 25, 50, 75, 90, 95])
    return dict(p_yes=yes.mean(), p_below_given=(guide < street).mean(), p_surprise=surprise.mean(),
                p_below_3200=(guide < 3200).mean(), p_below_3100=(guide < 3100).mean(), p_below_3050=(guide < 3050).mean(),
                guide_mean=guide.mean(), guide_sd=guide.std(), print_mean=print_.mean(), print_sd=print_.std(),
                gbv3_mean=gbv3.mean(), gbv3_sd=gbv3.std(), street_mean=street.mean(), street_sd=street.std(),
                q05=q[0], q10=q[1], q25=q[2], q50=q[3], q75=q[4], q90=q[5], q95=q[6],
                p_guide_below_2900=(guide < 2900).mean(), p_guide_above_3400=(guide > 3400).mean(),
                guide=guide)

if __name__ == "__main__":
    base = run()
    keep = {k: v for k, v in base.items() if k != "guide"}
    pd.DataFrame([keep]).T.rename(columns={0: "value"}).to_csv(HERE / "c01_mc_summary.csv")
    print("BASE CASE"); [print(f"  {k:>22}: {v:,.4f}") for k, v in keep.items()]

    # histogram of the guide midpoint for the log
    g = base["guide"]
    bins = np.arange(2850, 3451, 25)
    h, _ = np.histogram(g, bins=bins)
    pd.DataFrame({"bin_lo": bins[:-1], "bin_hi": bins[1:], "mass": h / len(g)}).to_csv(HERE / "c01_guide_hist.csv", index=False)

    pd.DataFrame({"percentile": [5, 10, 25, 50, 75, 90, 95],
                  "guide_mid_musd": [round(base[k]) for k in ["q05", "q10", "q25", "q50", "q75", "q90", "q95"]]}
                 ).to_csv(HERE / "c01_percentiles.csv", index=False)

    # ---- sensitivities --------------------------------------------------------------------------
    sens = []
    def add(label, **kw):
        o = run(**kw); sens.append(dict(assumption=label, p_yes=round(o["p_yes"], 3), p_surprise=round(o["p_surprise"], 3),
                                        q50=round(o["q50"]), q05=round(o["q05"]), q95=round(o["q95"]),
                                        gbv3=round(o["gbv3_mean"]), print_mean=round(o["print_mean"])))
    add("BASE: nights 9.5±1.6, ADR 3.3±1.3, eps -0.5%±2.0%, fee 45/40/15, cushion 2.4±1.0, drift 0±0.6%")
    add("cushion = trailing-8 all-quarter 1.86% (B2 convention)", cushion_mu=CUSHION_T8)
    add("cushion = Q4-only 2023-25 mean 3.04%", cushion_mu=CUSHION_Q4)
    add("cushion = all-Q4 2021-25 mean 3.85% (bridge v3 convention)", cushion_mu=0.0385)
    add("GBV_3Q26 = programme stacked object N(26,550, 853) (B2 input)", gbv_override=26_549.8, gbv_override_sd=853.2)
    add("GBV_3Q26 = management 'mid teens' midpoint N(26,317, 550) (+15%)", gbv_override=26_317.0, gbv_override_sd=550.0)
    add("GBV_3Q26 = Kalshi-implied nights median 148.3m x ADR +3.4% ($177.1) => N(26,260, 600)", gbv_override=26_260.0, gbv_override_sd=600.0)
    add("B2 REPLICATION: GBV N(26,550,853), cushion 1.86, eps 0/2.86, fee half certain", gbv_override=26_549.8, gbv_override_sd=853.2, cushion_mu=CUSHION_T8, eps_mu=0.0, eps_sd=0.0286, fee_w=(0.0,1.0,0.0))
    add("B2 REPLICATION no fee: GBV N(26,550,853), cushion 1.86, eps 0/2.86", gbv_override=26_549.8, gbv_override_sd=853.2, cushion_mu=CUSHION_T8, eps_mu=0.0, eps_sd=0.0286, fee_w=(1.0,0.0,0.0))
    add("GBV_3Q26 = Bloomberg MODL mean N(26,375, 600)", gbv_override=26_375.0, gbv_override_sd=600.0)
    add("nights nowcast at top of band 10.0", nights_mu=10.0)
    add("nights nowcast at bottom of band 8.5", nights_mu=8.5)
    add("nights model path 9.9 (bridge v3 baseline)", nights_mu=9.9)
    add("kernel residual unbiased, sd 2.86% (registered W1 PIT RMSE)", eps_mu=0.0, eps_sd=0.0286)
    add("kernel residual unbiased, sd 0.7% (Q4 within-season dispersion only)", eps_mu=0.0, eps_sd=0.007)
    add("kernel residual -1.4% (top of K1 RNPL leakage range), sd 2.0%", eps_mu=-0.014)
    add("no fee step at all", fee_w=(1.0, 0.0, 0.0))
    add("full primitives fee step certain (+1.11%)", fee_w=(0.0, 0.0, 1.0))
    add("architect full fee step +2.5% certain", fee_w=(0.0, 0.0, 1.0), fee_steps=(0.0, 0.0125, 0.025))
    add("Street drifts up 1% by 4 Nov (sell-side previews raise Q4)", drift_mu=0.01)
    add("Street drifts down 1% by 4 Nov", drift_mu=-0.01)
    add("Street = Zacks 3,200 (thin panel; NOT the resolution source)", street_now=3200.0)
    add("Street = MODL 3,157", street_now=3157.0)
    add("all tight: eps sd 0.7, nights sd 1.0, ADR sd 0.9, cushion sd 0.5", eps_sd=0.007, nights_sd=1.0, adr_sd=0.9, cushion_sd=0.005)
    add("all wide: eps sd 2.86, nights sd 2.2, ADR sd 1.8, cushion sd 1.5, drift sd 1.0", eps_sd=0.0286, nights_sd=2.2, adr_sd=1.8, cushion_sd=0.015, drift_sd=0.01)
    add("bull print: nights 10.6, ADR 4.0, fee full, cushion 1.86", nights_mu=10.6, adr_mu=4.0, fee_w=(0.0, 0.0, 1.0), cushion_mu=CUSHION_T8)
    add("bear print: nights 8.5, ADR 2.5, no fee, cushion 3.04", nights_mu=8.5, adr_mu=2.5, fee_w=(1.0, 0.0, 0.0), cushion_mu=CUSHION_Q4)
    s = pd.DataFrame(sens); s.to_csv(HERE / "c01_sensitivity.csv", index=False)

    # ---- FINAL MIXTURE: 0.60 team-band decomposition, 0.25 market-implied GBV route, 0.15 structural-doubt component
    comps = [(0.60, run(seed=1)), (0.25, run(seed=2, gbv_override=26_260.0, gbv_override_sd=600.0)),
             (0.15, run(seed=3, eps_mu=0.0, eps_sd=0.0286, cushion_mu=CUSHION_T8, nights_sd=2.2, adr_sd=1.8, drift_sd=0.01))]
    gmix = np.concatenate([o["guide"][: int(w * N)] for w, o in comps])
    p_yes_mix = sum(w * o["p_yes"] for w, o in comps); p_sur_mix = sum(w * o["p_surprise"] for w, o in comps)
    qm = np.percentile(gmix, [5, 10, 25, 50, 75, 90, 95])
    mix = dict(p_yes=p_yes_mix, p_surprise=p_sur_mix, q05=qm[0], q10=qm[1], q25=qm[2], q50=qm[3], q75=qm[4], q90=qm[5], q95=qm[6],
               mean=gmix.mean(), sd=gmix.std(), p_below_2900=(gmix < 2900).mean(), p_above_3400=(gmix > 3400).mean(),
               p_below_3050=(gmix < 3050).mean(), p_below_3100=(gmix < 3100).mean(), p_below_3161=(gmix < 3161).mean(), p_below_3200=(gmix < 3200).mean())
    pd.DataFrame([mix]).T.rename(columns={0: "value"}).to_csv(HERE / "c01_final_mixture.csv")
    print("FINAL MIXTURE"); [print(f"  {k:>14}: {v:,.4f}") for k, v in mix.items()]
    h, _ = np.histogram(gmix, bins=bins)
    pd.DataFrame({"bin_lo": bins[:-1], "bin_hi": bins[1:], "mass": h / len(gmix)}).to_csv(HERE / "c01_final_mixture_hist.csv", index=False)
    pd.set_option("display.width", 250); pd.set_option("display.max_colwidth", 90)
    print(s.to_string())

    # ---- base rates from the reaction panel and register (recomputed here, not copied) -------------
    rows = []
    root = HERE.parents[4]
    p = pd.read_csv(root / "data/processed/abnb_guidance_reaction_panel.csv")
    p = p[p.guide_vs_street_pct.notna()].copy(); p["below"] = p.guide_vs_street_pct < 0
    def br(label, d):
        k = int(d.below.sum()); n = len(d)
        rows.append(dict(reference_class=label, n=n, below=k, raw=round(k / n, 3), laplace=round((k + 1) / (n + 2), 3),
                         mean_gap_pct=round(d.guide_vs_street_pct.mean(), 2), sd_gap_pp=round(d.guide_vs_street_pct.std(), 2)))
    br("all next-quarter revenue guides with a pre-guide Street, 4Q21-3Q26", p)
    br("LSEG-era (guides given Nov 2023 onward)", p[p.print_date >= "2023-11-01"])
    br("November (Q4) guides only", p[p.print_date.str[5:7] == "11"])
    br("guides where next-quarter nights were guided lower / decelerating", p[(p.nq_nights_dir == -1) | (p.nq_nights_guide_pts < -1)])
    br("guides where next-quarter nights were guided higher", p[(p.nq_nights_dir == 1) | (p.nq_nights_guide_pts > 0.5)])
    br("last four guides (Nov 2025 - Aug 2026, RNPL/FX regime)", p.tail(4))
    br("guides 2024Q1-2025Q2 (the below-Street run)", p[(p.print_date >= "2024-05-01") & (p.print_date <= "2025-08-01")])
    b = pd.DataFrame(rows); b.to_csv(HERE / "c01_base_rates.csv", index=False); print(b.to_string())
