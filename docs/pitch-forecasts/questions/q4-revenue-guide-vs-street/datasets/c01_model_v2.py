"""C01 q4-revenue-guide-vs-street, REVISION 2 model (audit response to A01).

Run from the repo root:  py -3.13 docs/pitch-forecasts/questions/q4-revenue-guide-vs-street/datasets/c01_model_v2.py
numpy/pandas only, seeded. Writes c01_v2_*.csv next to this file. Revision-1 script c01_model.py is left untouched.

Changes from revision 1 (finding ids in docs/pitch-forecasts/audits/A01-audit-response.md):
  A01-01  three-way guidance gate: dollar range (0.985, $5M midpoint grid) / growth-only range (0.010, integer
          endpoints converted on 4Q25 revenue $2,778M, midpoint on a 0.5pt grid) / no revenue guidance (0.005 -> No).
  A01-03  residual eps = N(-0.19%, 2.05%) [kernel last3_ex_covid PIT bias and RMSE, kernel-lambda.md] plus a
          Bernoulli(0.40) RNPL-leakage branch of -0.84% [K1 grid central cell, 21% share, +4pt]; mean -0.53%.
  A01-04/05  market route: 3Q26 nights drawn from the Kalshi KXABNB ladder shape (bucket masses from mid prices,
          exponential tails), convolved with ADR ~ N(3.3, 1.3)%; weight cut 0.25 -> 0.20 (3,237 contracts, 24h vol 0).
  A01-08  nights sd 1.6 -> 1.8 (re-vintaged reviews-index RMSE 1.63pp, WPK note variant b).
  A01-07  every sensitivity is run through all three mixture components (mixture-level numbers), plus component-level.
  Weights 0.55 team band / 0.20 market-Street GBV route / 0.25 registered-conventions component.

Structure:
  print_4Q26 = lambda_Q4 * (1 + eps - leak) * [2/3 GBV_3Q26 + 1/3 GBV_2Q26] * (1 + fee_step)
  guide_mid  = grid( print_4Q26 / (1 + cushion) )           # $5M grid (dollar) or 0.5pt-of-2,778 grid (growth-only)
  YES        <=> guidance given (dollar or growth-only) AND guide_mid < street_4Nov
"""
from pathlib import Path
import numpy as np, pandas as pd

HERE = Path(__file__).resolve().parent
N = 400_000

# ---- printed / registered inputs -------------------------------------------------------------
GBV_2Q26 = 27_200.0            # 2Q26 letter, printed
NIGHTS_3Q25 = 133.6            # m, 3Q25 letter
ADR_3Q25 = 171.29              # $, 3Q25 letter (GBV 22,884)
REV_4Q25 = 2_778.0             # conversion base for a growth-only guide (resolution rule)
LAMBDA_Q4 = 0.120298           # kernel-lambda.md: mean of 4Q23 11.946 / 4Q24 12.117 / 4Q25 12.026
STREET_NOW = 3_161.02          # yfinance revenue_estimate +1q avg, LSEG family, captured 2026-09-17T02:52Z (n 36)
CUSHION_T8 = 0.018567          # guidance-policy.md trailing-8 mean, sd 1.0048pp (validated)
CUSHION_Q4 = 0.030419          # Q4 guides 2023-25: 3.16 / 2.69 / 3.27, sd 0.31pp (02_guidance_ledger.csv)
EPS_BIAS = -0.0019             # kernel last3_ex_covid PIT bias +0.187% (forecast above actual) -> actual = kernel x (1 - 0.0019)
EPS_SD = 0.0205                # kernel last3_ex_covid PIT RMSE 2.050% (W1 n 14; KS p 0.63)
LEAK = 0.0084                  # K1 leakage grid central cell (21% RNPL share, +4pt cancellation propensity)
P_LEAK = 0.40                  # judgment: 1H26 lambda cells show no leakage (K1 3.3), mechanism is in the 10-Q
P_DOLLAR, P_GROWTH_ONLY, P_NONE = 0.985, 0.010, 0.005   # 20/20 dollar ranges since 4Q21; 2 qualitative guides in 2021

# Kalshi KXABNB-26NOVNEB ladder, mid prices at 2026-09-17T02:53:04Z (yes-bid/ask): P(nights > strike)
KALSHI = {138: 0.955, 140: 0.925, 142: 0.880, 144: 0.795, 146: 0.645, 148: 0.525, 150: 0.340}


def ladder_nights(r, n, tail_scale_lo=2.0, tail_scale_hi=3.7):
    """Nights (m) drawn from the ladder: piecewise-uniform inside strikes, exponential tails outside.
    Upper tail scale 3.7m makes the density continuous at 150m (0.34 / (0.185 per 2m))."""
    ks = sorted(KALSHI)
    surv = [KALSHI[k] for k in ks]
    masses = [1 - surv[0]] + [surv[i] - surv[i + 1] for i in range(len(ks) - 1)] + [surv[-1]]
    comp = r.choice(len(masses), size=n, p=np.array(masses) / sum(masses))
    out = np.empty(n)
    lo = comp == 0
    out[lo] = ks[0] - r.exponential(tail_scale_lo, lo.sum())
    hi = comp == len(masses) - 1
    out[hi] = ks[-1] + r.exponential(tail_scale_hi, hi.sum())
    for i in range(1, len(masses) - 1):
        m = comp == i
        out[m] = r.uniform(ks[i - 1], ks[i], m.sum())
    return out


def run(nights_mu=9.5, nights_sd=1.8, adr_mu=3.3, adr_sd=1.3,
        eps_mu=EPS_BIAS, eps_sd=EPS_SD, p_leak=P_LEAK, leak=LEAK,
        fee_w=(0.45, 0.40, 0.15), fee_steps=(0.0, 0.005543, 0.011086),
        cushion_mu=0.024, cushion_sd=0.010,
        drift_mu=0.0, drift_sd=0.006, street_now=STREET_NOW, seed=20260917, n=N,
        gbv_override=None, gbv_override_sd=None, nights_source="team",
        p_dollar=P_DOLLAR, p_growth=P_GROWTH_ONLY):
    r = np.random.default_rng(seed)
    if gbv_override is not None:
        gbv3 = r.normal(gbv_override, gbv_override_sd, n)
    else:
        if nights_source == "kalshi":
            nights = ladder_nights(r, n)
        else:
            nights = NIGHTS_3Q25 * (1 + r.normal(nights_mu, nights_sd, n) / 100)
        g_a = r.normal(adr_mu, adr_sd, n) / 100
        gbv3 = nights * ADR_3Q25 * (1 + g_a)
    base = (2 / 3) * gbv3 + (1 / 3) * GBV_2Q26
    eps = r.normal(eps_mu, eps_sd, n) - leak * (r.random(n) < p_leak)
    fee = r.choice(np.array(fee_steps), size=n, p=np.array(fee_w))
    print_ = LAMBDA_Q4 * (1 + eps) * base * (1 + fee)
    c = r.normal(cushion_mu, cushion_sd, n)
    raw = print_ / (1 + c)
    u = r.random(n)
    dollar = u < p_dollar
    growth = (u >= p_dollar) & (u < p_dollar + p_growth)
    given = dollar | growth
    guide = np.where(dollar, np.round(raw / 5) * 5,                                        # $X.XX bn endpoints -> $5M midpoint grid
                     REV_4Q25 * (1 + np.round((raw / REV_4Q25 - 1) / 0.005) * 0.005))     # integer-% endpoints -> 0.5pt midpoint grid
    street = street_now * (1 + r.normal(drift_mu, drift_sd, n))
    yes = given & (guide < street)
    surprise = given & (guide < street * (1 - CUSHION_T8))
    gg = guide[given]                                                                       # continuous object: conditional on resolvable guidance
    q = np.percentile(gg, [5, 10, 25, 50, 75, 90, 95])
    return dict(p_yes=yes.mean(), p_below_given=(guide[given] < street[given]).mean(), p_surprise=surprise.mean(),
                p_none=(~given).mean(), p_growth_only=growth.mean(),
                p_below_3200=(gg < 3200).mean(), p_below_3100=(gg < 3100).mean(), p_below_3050=(gg < 3050).mean(),
                guide_mean=gg.mean(), guide_sd=gg.std(), print_mean=print_.mean(), print_sd=print_.std(),
                gbv3_mean=gbv3.mean(), gbv3_sd=gbv3.std(), nights_mean=(gbv3 / (ADR_3Q25 * (1 + adr_mu / 100))).mean() if gbv_override is None else np.nan,
                street_mean=street.mean(), street_sd=street.std(), eps_mean=eps.mean(), eps_sd_real=eps.std(),
                q05=q[0], q10=q[1], q25=q[2], q50=q[3], q75=q[4], q90=q[5], q95=q[6],
                p_guide_below_2900=(gg < 2900).mean(), p_guide_above_3400=(gg > 3400).mean(),
                guide=gg)


# ---- the three mixture components ----------------------------------------------------------------
W_A, W_B, W_C = 0.55, 0.20, 0.25
KW_A = dict()
KW_B = dict(nights_source="kalshi")
KW_C = dict(eps_mu=0.0, eps_sd=0.0286, p_leak=0.0, cushion_mu=CUSHION_T8, nights_sd=2.2, adr_sd=1.8, drift_sd=0.01)


def mixture(**shared):
    """Apply a shared change to every component (A01-07 update rule) and return the mixture summary."""
    comps = []
    for w, kw, seed in [(W_A, KW_A, 1), (W_B, KW_B, 2), (W_C, KW_C, 3)]:
        k = dict(kw); k.update(shared)
        comps.append((w, run(seed=seed, **k)))
    gmix = np.concatenate([o["guide"][: int(w * len(o["guide"]))] for w, o in comps])
    qm = np.percentile(gmix, [5, 10, 25, 50, 75, 90, 95])
    out = dict(p_yes=sum(w * o["p_yes"] for w, o in comps), p_surprise=sum(w * o["p_surprise"] for w, o in comps),
               p_none=sum(w * o["p_none"] for w, o in comps),
               comp_A=comps[0][1]["p_yes"], comp_B=comps[1][1]["p_yes"], comp_C=comps[2][1]["p_yes"],
               q05=qm[0], q10=qm[1], q25=qm[2], q50=qm[3], q75=qm[4], q90=qm[5], q95=qm[6],
               mean=gmix.mean(), sd=gmix.std(), p_below_2900=(gmix < 2900).mean(), p_above_3400=(gmix > 3400).mean(),
               p_below_2950=(gmix < 2950).mean(), p_above_3275=(gmix > 3275).mean(),
               p_below_3050=(gmix < 3050).mean(), p_below_3100=(gmix < 3100).mean(), p_below_3161=(gmix < 3161).mean(), p_below_3200=(gmix < 3200).mean())
    return out, gmix, comps


if __name__ == "__main__":
    pd.set_option("display.width", 250); pd.set_option("display.max_colwidth", 95)
    base = run()
    keep = {k: v for k, v in base.items() if k != "guide"}
    pd.DataFrame([keep]).T.rename(columns={0: "value"}).to_csv(HERE / "c01_v2_component_A_summary.csv")
    print("COMPONENT A (team band)"); [print(f"  {k:>22}: {v:,.4f}") for k, v in keep.items()]

    for lab, kw, seed in [("B", KW_B, 2), ("C", KW_C, 3)]:
        o = run(seed=seed, **kw); keep = {k: v for k, v in o.items() if k != "guide"}
        pd.DataFrame([keep]).T.rename(columns={0: "value"}).to_csv(HERE / f"c01_v2_component_{lab}_summary.csv")
        print(f"COMPONENT {lab}"); [print(f"  {k:>22}: {v:,.4f}") for k, v in keep.items()]

    mix, gmix, comps = mixture()
    pd.DataFrame([mix]).T.rename(columns={0: "value"}).to_csv(HERE / "c01_v2_final_mixture.csv")
    print("FINAL MIXTURE (0.55 A / 0.20 B / 0.25 C)"); [print(f"  {k:>14}: {v:,.4f}") for k, v in mix.items()]
    bins = np.arange(2850, 3451, 25)
    h, _ = np.histogram(gmix, bins=bins)
    pd.DataFrame({"bin_lo": bins[:-1], "bin_hi": bins[1:], "mass": h / len(gmix)}).to_csv(HERE / "c01_v2_final_mixture_hist.csv", index=False)
    pd.DataFrame({"percentile": [5, 10, 25, 50, 75, 90, 95],
                  "guide_mid_musd": [round(mix[k]) for k in ["q05", "q10", "q25", "q50", "q75", "q90", "q95"]]}
                 ).to_csv(HERE / "c01_v2_percentiles.csv", index=False)

    # ---- bridge from B2 (A01-03): sequential, at the same Street threshold, revision-2 conventions ---------------
    bridge = []
    steps = [
        ("B2 replication no fee: GBV N(26,550, 853), cushion 1.86, eps N(0, 2.86), no leak, 1% no-guide", dict(gbv_override=26_549.8, gbv_override_sd=853.2, cushion_mu=CUSHION_T8, eps_mu=0.0, eps_sd=0.0286, p_leak=0.0, fee_w=(1.0, 0, 0), p_dollar=0.99, p_growth=0.0)),
        ("+ team GBV: nights N(9.5, 1.8), ADR N(3.3, 1.3)", dict(cushion_mu=CUSHION_T8, eps_mu=0.0, eps_sd=0.0286, p_leak=0.0, fee_w=(1.0, 0, 0), p_dollar=0.99, p_growth=0.0)),
        ("+ fee mixture 45/40/15 over 0 / +0.55 / +1.11%", dict(cushion_mu=CUSHION_T8, eps_mu=0.0, eps_sd=0.0286, p_leak=0.0, p_dollar=0.99, p_growth=0.0)),
        ("+ three-way gate 0.985 / 0.010 / 0.005", dict(cushion_mu=CUSHION_T8, eps_mu=0.0, eps_sd=0.0286, p_leak=0.0)),
        ("+ eps sd 2.86 -> 2.05 (ex-COVID PIT RMSE, validated)", dict(cushion_mu=CUSHION_T8, eps_mu=0.0, p_leak=0.0)),
        ("+ eps mean 0 -> -0.19% (ex-COVID PIT bias, validated)", dict(cushion_mu=CUSHION_T8, p_leak=0.0)),
        ("+ RNPL leakage branch Bernoulli(0.40) x -0.84% (judgment)", dict(cushion_mu=CUSHION_T8)),
        ("+ cushion 1.86 -> 2.4 (Q4-season blend, judgment) = component A", dict()),
    ]
    for lab, kw in steps:
        o = run(**kw)
        bridge.append(dict(step=lab, p_yes=round(o["p_yes"], 4), p_surprise=round(o["p_surprise"], 4), guide_mean=round(o["guide_mean"], 1),
                           guide_sd=round(o["guide_sd"], 1), print_mean=round(o["print_mean"], 1), q50=round(o["q50"])))
    o = run(gbv_override=26_549.8, gbv_override_sd=853.2, cushion_mu=CUSHION_T8, eps_mu=0.0, eps_sd=0.0286, p_leak=0.0, fee_w=(0.0, 1.0, 0.0), p_dollar=0.99, p_growth=0.0)
    bridge.append(dict(step="B2 replication half fee certain (B2 published 0.433)", p_yes=round(o["p_yes"], 4), p_surprise=round(o["p_surprise"], 4),
                       guide_mean=round(o["guide_mean"], 1), guide_sd=round(o["guide_sd"], 1), print_mean=round(o["print_mean"], 1), q50=round(o["q50"])))
    o = run(cushion_mu=CUSHION_T8, eps_mu=0.0, eps_sd=0.0286, p_leak=0.0, fee_w=(0.0, 1.0, 0.0), nights_sd=1.6, p_dollar=0.99, p_growth=0.0)
    bridge.append(dict(step="Astra conventions in this model: team GBV (nights sd 1.6), cushion 1.86, eps N(0, 2.86), half fee certain, 1% no-guide (Astra analytic 0.624)",
                       p_yes=round(o["p_yes"], 4), p_surprise=round(o["p_surprise"], 4), guide_mean=round(o["guide_mean"], 1), guide_sd=round(o["guide_sd"], 1),
                       print_mean=round(o["print_mean"], 1), q50=round(o["q50"])))
    b = pd.DataFrame(bridge); b.to_csv(HERE / "c01_v2_bridge.csv", index=False); print("BRIDGE"); print(b.to_string())

    # ---- sensitivities: mixture-level (shared change through all three components) and component-A-level ---------
    sens = []
    def add(label, **kw):
        m, _, cs = mixture(**kw); a = run(**kw)
        sens.append(dict(assumption=label, mix_p_yes=round(m["p_yes"], 3), mix_p_surprise=round(m["p_surprise"], 3), mix_q50=round(m["q50"]),
                         mix_q05=round(m["q05"]), mix_q95=round(m["q95"]), comp_A=round(m["comp_A"], 3), comp_B=round(m["comp_B"], 3), comp_C=round(m["comp_C"], 3),
                         A_alone_p_yes=round(a["p_yes"], 3), A_alone_q50=round(a["q50"])))
    add("BASE (revision 2)")
    add("cushion = trailing-8 all-quarter 1.86% in every component", cushion_mu=CUSHION_T8)
    add("cushion = Q4-only 2023-25 mean 3.04% in every component", cushion_mu=CUSHION_Q4)
    add("cushion = all-Q4 2021-25 mean 3.85% (bridge v3 convention)", cushion_mu=0.0385)
    add("nights nowcast at top of band 10.0 (team components)", nights_mu=10.0)
    add("nights nowcast at bottom of band 8.5 (team components)", nights_mu=8.5)
    add("nights model path 9.9 (bridge v3 baseline)", nights_mu=9.9)
    add("nights 11.5 = Bloomberg MODL 149.0m (team components re-centred on the Street)", nights_mu=11.5)
    add("nights sd 1.6 (revision-1 width)", nights_sd=1.6)
    add("no RNPL leakage branch (p_leak 0)", p_leak=0.0)
    add("RNPL leakage certain at the K1 central cell -0.84%", p_leak=1.0)
    add("RNPL leakage certain at the K1 top cell -1.39%", p_leak=1.0, leak=0.0139)
    add("kernel residual unbiased, sd 2.86% (registered last3 W1 PIT RMSE), no leak", eps_mu=0.0, eps_sd=0.0286, p_leak=0.0)
    add("kernel residual unbiased, sd 0.7% (Q4 within-season dispersion only), no leak", eps_mu=0.0, eps_sd=0.007, p_leak=0.0)
    add("no fee step at all", fee_w=(1.0, 0.0, 0.0))
    add("half primitives fee step certain (+0.55%, B2 convention)", fee_w=(0.0, 1.0, 0.0))
    add("full primitives fee step certain (+1.11%)", fee_w=(0.0, 0.0, 1.0))
    add("architect full fee step +2.5% certain", fee_w=(0.0, 0.0, 1.0), fee_steps=(0.0, 0.0125, 0.025))
    add("Street drifts up 1% by 4 Nov", drift_mu=0.01)
    add("Street drifts down 1% by 4 Nov", drift_mu=-0.01)
    add("Street = Zacks 3,200 (thin panel; NOT the resolution source)", street_now=3200.0)
    add("Street = Bloomberg MODL 3,157", street_now=3157.0)
    add("Street = 3,130 (previews trim Q4 by 1%)", street_now=3130.0)
    add("no revenue guidance 5% (gate stress)", p_dollar=0.94, p_growth=0.01)
    add("growth-only guidance 10% (gate stress; converts on 2,778)", p_dollar=0.895, p_growth=0.10)
    add("all tight: eps sd 0.7, nights sd 1.0, ADR sd 0.9, cushion sd 0.5", eps_sd=0.007, nights_sd=1.0, adr_sd=0.9, cushion_sd=0.005)
    add("all wide: eps sd 2.86, nights sd 2.2, ADR sd 1.8, cushion sd 1.5, drift sd 1.0", eps_sd=0.0286, nights_sd=2.2, adr_sd=1.8, cushion_sd=0.015, drift_sd=0.01)
    add("bull print: nights 10.6, ADR 4.0, fee full, cushion 1.86, no leak", nights_mu=10.6, adr_mu=4.0, fee_w=(0.0, 0.0, 1.0), cushion_mu=CUSHION_T8, p_leak=0.0)
    add("bear print: nights 8.5, ADR 2.5, no fee, cushion 3.04, leak certain", nights_mu=8.5, adr_mu=2.5, fee_w=(1.0, 0.0, 0.0), cushion_mu=CUSHION_Q4, p_leak=1.0)
    s = pd.DataFrame(sens); s.to_csv(HERE / "c01_v2_sensitivity.csv", index=False); print("SENSITIVITY"); print(s.to_string())

    # ---- mixture-weight sensitivity ----------------------------------------------------------------------------
    rows = []
    for wa, wb, wc in [(0.55, 0.20, 0.25), (0.60, 0.25, 0.15), (0.50, 0.20, 0.30), (0.40, 0.20, 0.40), (0.34, 0.33, 0.33), (1, 0, 0), (0, 1, 0), (0, 0, 1)]:
        p = wa * mix["comp_A"] + wb * mix["comp_B"] + wc * mix["comp_C"]
        rows.append(dict(w_A=wa, w_B=wb, w_C=wc, p_yes=round(p, 4)))
    w = pd.DataFrame(rows); w.to_csv(HERE / "c01_v2_weight_sensitivity.csv", index=False); print("WEIGHTS"); print(w.to_string())

    # ---- Kalshi ladder-implied nights distribution (A01-05) ----------------------------------------------------
    r = np.random.default_rng(5); ln = ladder_nights(r, N)
    lad = dict(mean=ln.mean(), sd=ln.std(), median=np.median(ln), p_le_138=(ln <= 138).mean(), p_gt_150=(ln > 150).mean(),
               p_gt_147=(ln > 147).mean(), q05=np.percentile(ln, 5), q95=np.percentile(ln, 95),
               yoy_mean_pct=100 * (ln.mean() / NIGHTS_3Q25 - 1), yoy_median_pct=100 * (np.median(ln) / NIGHTS_3Q25 - 1))
    g_a = r.normal(3.3, 1.3, N) / 100; gbv = ln * ADR_3Q25 * (1 + g_a)
    lad.update(gbv_mean=gbv.mean(), gbv_sd=gbv.std(), gbv_p_below_25000=(gbv < 25000).mean(), gbv_p_above_27000=(gbv > 27000).mean(),
               normal_26260_600_p_le_138_equiv=float(np.mean(r.normal(26260, 600, N) < 138 * ADR_3Q25 * 1.034)))
    pd.DataFrame([lad]).T.rename(columns={0: "value"}).to_csv(HERE / "c01_v2_kalshi_ladder_distribution.csv")
    print("KALSHI LADDER"); [print(f"  {k:>34}: {v:,.4f}") for k, v in lad.items()]

    # ---- base rates, register-gated (A01-02) -------------------------------------------------------------------
    root = HERE.parents[4]
    panel = pd.read_csv(root / "data/processed/abnb_guidance_reaction_panel.csv")
    panel["period"] = pd.PeriodIndex(panel.print_quarter, freq="Q").shift(1).astype(str)
    reg = pd.read_csv(root / "data/processed/forecast_methods/L0/L0_vintage_register.csv", comment="#")
    pg = reg[(reg.role == "pre_guide") & (reg.metric == "revenue")]
    p = panel.merge(pg, on="period", validate="one_to_one")
    p["gap"] = 100 * (p.nq_rev_guide_mid / p.value - 1)
    ok = p[p.pit_usable.astype(str).str.lower().eq("true")].copy()
    rows = []
    def br(label, d):
        s = d.gap.dropna(); k = int((s < 0).sum()); n = len(s)
        rows.append(dict(reference_class=label, n=n, below=k, raw=round(k / n, 3) if n else None, laplace=round((k + 1) / (n + 2), 3),
                         mean_gap_pct=round(s.mean(), 2), sd_gap_pp=round(s.std(), 2)))
    br("PIT-usable, all vendors, 1Q22-3Q26 targets", ok)
    br("PIT-usable, LSEG era (guides given Nov 2023 on)", ok[ok.print_date >= "2023-11-01"])
    br("PIT-usable, LSEG/Refinitiv vendor only", ok[ok.vendor.isin(["LSEG", "Refinitiv"])])
    br("PIT-usable, November (Q4) guides", ok[ok.print_date.str[5:7] == "11"])
    br("PIT-usable, next-quarter nights guided lower / decelerating", ok[(ok.nq_nights_dir == -1) | (ok.nq_nights_guide_pts < -1)])
    br("PIT-usable, next-quarter nights guided higher", ok[(ok.nq_nights_dir == 1) | (ok.nq_nights_guide_pts > 0.5)])
    br("PIT-usable, last four guides (Nov 2025 - Aug 2026)", ok.sort_values("print_date").tail(4))
    br("PIT-usable, May 2024 - Aug 2025 run", ok[(ok.print_date >= "2024-05-01") & (ok.print_date <= "2025-08-01")])
    br("PIT-usable, W1 targets 2023Q1-2026Q2", ok[(ok.period >= "2023Q1") & (ok.period <= "2026Q2")])
    br("PIT-usable, W2 targets 2024Q1-2026Q2", ok[(ok.period >= "2024Q1") & (ok.period <= "2026Q2")])
    b = pd.DataFrame(rows); b.to_csv(HERE / "c01_v2_base_rates.csv", index=False); print("BASE RATES (register-gated)"); print(b.to_string())
    print("excluded:", p[~p.pit_usable.astype(str).str.lower().eq("true")][["register_id", "period", "value"]].to_string(index=False))
