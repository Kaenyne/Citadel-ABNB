"""C11 q3-take-rate-above-1810, revision 2 (audit response to A05). ONE joint model: the headline, the GBV-band
conditionals and the point-GBV conditionals are all read off the same draws, so the band table integrates to the
headline (A05-01) and the point rows are true conditionals (A05-11).

Structure (every input sourced in research-log.md, revision 2):
  nights y/y  ~ N(9.67, 1.70)%                    R01/R02 print-state distribution (batch A09), replaces the rev-1 N(9.5, 1.6)
  ADR y/y     ~ B02 structural mixture             mix N(-1.15,0.35) + residual mix + FX mix (bonus-adr-residual-reverts/datasets/b02_model.py)
  GBV         = 22,884.3 x (1+n)(1+a); the RELEASE prints GBV to $0.1bn, so the ratio uses round(GBV, -2) (A05-14)
  component S (0.25): Street/market GBV route, GBV ~ N(26,300, 850) (MODL 26,375 n 28 / Kalshi-ladder-implied 26,190; sd = B1's 853)
  revenue     = 4,730 x (1 + c); c ~ N(1.04%, 0.5%) with rho 0.5 to the GBV z-score inside each component (2023-25 Q3 cushion mean 1.0433%)
                revenue-light branch p 0.15: c ~ N(0.3%, 0.4%) (cushion trend -0.12pp/print; 0.86% in the last two Q3s; incentives)
                first-ever guide miss p 0.03: revenue = 4,690 x (1 + N(-0.3%, 0.4%))
  take        = 100 x revenue / GBV_print ; YES <=> take >= 18.10
Run from the repo root:  py -3.13 docs/pitch-forecasts/questions/q3-take-rate-above-1810/datasets/c11_model_v2.py
Writes c11_v2_summary.csv, c11_v2_by_gbv_band.csv, c11_v2_point_gbv.csv, c11_v2_sensitivity.csv, c11_v2_language_record.csv.
"""
from pathlib import Path
import numpy as np, pandas as pd

HERE = Path(__file__).resolve().parent
N = 600_000
GBV_3Q25 = 133.6 * 171.29
GUIDE_MID, GUIDE_LOW, THRESH = 4_730.0, 4_690.0, 18.10

def adr_draws(r, n, res_w=(0.45, 0.15, 0.25, 0.15), fx_w=(0.5, 0.25, 0.25), mix_mu=-1.15):
    """B02 structural ADR model: mix + residual mixture + FX mixture (reported y/y, %)."""
    mix = r.normal(mix_mu, 0.35, n)
    u = r.random(n); c = np.cumsum(res_w)
    res = np.select([u < c[0], u < c[1], u < c[2]], [r.normal(4.85, 0.55, n), r.normal(5.35, 0.55, n), r.normal(4.37, 0.94, n)], r.normal(3.6, 0.7, n))
    v = r.random(n); d = np.cumsum(fx_w)
    fx = np.select([v < d[0], v < d[1]], [r.normal(-0.43, 0.33, n), r.normal(0.26, 0.42, n)], r.normal(-1.12, 0.46, n))
    return mix + res + fx

def component(seed, n, nights_mu=9.67, nights_sd=1.70, adr_fixed=None, rho_na=0.0, gbv_override=None, gbv_sd=None,
              cushion_mu=0.0104, cushion_sd=0.005, rho=0.5, p_light=0.15, light_mu=0.003, light_sd=0.004, p_miss=0.03, round_gbv=True):
    r = np.random.default_rng(seed)
    if gbv_override is None:
        zn = r.normal(0, 1, n)
        gn = (nights_mu + nights_sd * zn) / 100
        if adr_fixed is not None:
            ga = (adr_fixed[0] + adr_fixed[1] * (rho_na * zn + np.sqrt(1 - rho_na ** 2) * r.normal(0, 1, n))) / 100
        else:
            ga = adr_draws(r, n) / 100
            if rho_na: ga = ga + rho_na * 0.010 * zn      # small common factor: a strong quarter lifts both
        gbv = GBV_3Q25 * (1 + gn) * (1 + ga)
    else:
        gbv = r.normal(gbv_override, gbv_sd, n); gn = np.full(n, np.nan)
    gbv_print = np.round(gbv / 100) * 100 if round_gbv else gbv
    z = (gbv - gbv.mean()) / gbv.std()
    e = r.normal(0, 1, n)
    c = cushion_mu + cushion_sd * (rho * z + np.sqrt(1 - rho ** 2) * e)
    light = r.random(n) < p_light
    c = np.where(light, light_mu + light_sd * e, c)
    rev = GUIDE_MID * (1 + c)
    miss = r.random(n) < p_miss
    rev = np.where(miss, GUIDE_LOW * (1 + r.normal(-0.003, 0.004, n)), rev)
    take = 100 * rev / gbv_print
    return dict(gbv=gbv, gbv_print=gbv_print, rev=rev, take=take, nights=gn * 100)

def summarise(o):
    t = o["take"]
    return dict(p_yes=(t >= THRESH).mean(), take_q50=np.median(t), take_sd=t.std(), p_le_1788=(t <= 17.88).mean(),
                gbv_mean=o["gbv"].mean(), gbv_sd=o["gbv"].std(), rev_mean=o["rev"].mean(), rev_sd=o["rev"].std(),
                p_gbv_ge_26410=(o["gbv"] >= 26_410).mean(), p_rev_below_guide_low=(o["rev"] < GUIDE_LOW).mean())

W_PRINT, W_STREET = 0.75, 0.25
def joint(seed_a=1, seed_b=2, w_street=W_STREET, **kw):
    a = component(seed_a, int(N * (1 - w_street)), **{k: v for k, v in kw.items() if k not in ("gbv_override", "gbv_sd")})
    b = component(seed_b, N - int(N * (1 - w_street)), gbv_override=kw.get("gbv_override", 26_300.0), gbv_sd=kw.get("gbv_sd", 850.0),
                  **{k: v for k, v in kw.items() if k in ("cushion_mu", "cushion_sd", "rho", "p_light", "light_mu", "light_sd", "p_miss", "round_gbv")})
    out = {k: np.concatenate([a[k], b[k]]) for k in a}
    out["comp"] = np.concatenate([np.zeros(len(a["take"])), np.ones(len(b["take"]))])
    return out, a, b

if __name__ == "__main__":
    pd.set_option("display.width", 250)
    J, A, B = joint()
    sA, sB, sJ = summarise(A), summarise(B), summarise(J)
    rows = [dict(object="print-state component (R01 nights x B02 ADR)", weight=W_PRINT, **sA),
            dict(object="Street/market GBV route N(26,300, 850)", weight=W_STREET, **sB),
            dict(object="JOINT (headline)", weight=1.0, **sJ)]
    summ = pd.DataFrame(rows); summ.to_csv(HERE / "c11_v2_summary.csv", index=False); print(summ.round(4).to_string())
    # nights distribution implied by the joint GBV marginal (coherence check against R01's P(>=10) = 0.42)
    print("implied P(nights >= 10.0) in the print-state component:", round((A["nights"] >= 10).mean(), 3),
          "| joint marginal, nights-equivalent (Street route at ADR 3.05):",
          round((np.concatenate([A["nights"], (B["gbv"] / GBV_3Q25 / 1.0305 - 1) * 100]) >= 10).mean(), 3))

    # ---- band table from the joint draws (fine print): masses x conditionals integrate to the headline ----
    cuts = [25_600, 25_900, 26_200, 26_500, 26_800]
    labels = ["< 25,600", "25,600-25,900", "25,900-26,200", "26,200-26,500", "26,500-26,800", ">= 26,800"]
    band = np.digitize(J["gbv_print"], cuts)
    brows = []
    for i, lab in enumerate(labels):
        m = band == i
        brows.append(dict(gbv_band_musd=lab, gbv_yoy_pct=(f"{(cuts[i-1] if i else 0)/GBV_3Q25*100-100:.1f} to {cuts[i]/GBV_3Q25*100-100:.1f}" if i < 5 else f">= {cuts[4]/GBV_3Q25*100-100:.1f}") if i else f"< {cuts[0]/GBV_3Q25*100-100:.1f}",
                          mass=m.mean(), p_yes_given_band=(J["take"][m] >= THRESH).mean(), take_median=np.median(J["take"][m]),
                          share_print_state=(J["comp"][m] == 0).mean()))
    bt = pd.DataFrame(brows); bt.to_csv(HERE / "c11_v2_by_gbv_band.csv", index=False); print(bt.round(4).to_string())
    print("band integral:", round((bt.mass * bt.p_yes_given_band).sum(), 4), "headline:", round(sJ["p_yes"], 4))

    # ---- point-GBV conditionals: the release prints GBV to $0.1bn, so {GBV_print = g} has mass; condition on it ----
    prow = []
    for g in [25_600, 25_900, 26_000, 26_185 // 100 * 100, 26_300, 26_400, 26_500, 26_600, 26_800, 27_000]:
        m = J["gbv_print"] == g
        prow.append(dict(gbv_print_musd=g, gbv_yoy_pct=round((g / GBV_3Q25 - 1) * 100, 1), n_draws=int(m.sum()), mass=m.mean(),
                         p_yes_given_gbv=(J["take"][m] >= THRESH).mean() if m.any() else None,
                         take_median=np.median(J["take"][m]) if m.any() else None, rev_median=np.median(J["rev"][m]) if m.any() else None))
    pt = pd.DataFrame(prow); pt.to_csv(HERE / "c11_v2_point_gbv.csv", index=False); print(pt.round(4).to_string())
    # break-even GBV at the median cushion
    print("break-even GBV at revenue 4,730 x 1.0104:", round(GUIDE_MID * 1.0104 / 0.1810), "; at the guide low:", round(GUIDE_LOW / 0.1810))

    # ---- sensitivities, all at the joint level ----
    sens = []
    def add(label, **kw):
        w = kw.pop("w_street", W_STREET)
        j, a, b = joint(w_street=w, **kw); s = summarise(j)
        sens.append(dict(assumption=label, p_yes=round(s["p_yes"], 3), take_q50=round(s["take_q50"], 3), take_sd=round(s["take_sd"], 3),
                         gbv_mean=round(s["gbv_mean"]), p_gbv_ge_26410=round(s["p_gbv_ge_26410"], 3), p_rev_below_guide=round(s["p_rev_below_guide_low"], 3)))
    add("BASE rev 2 (0.75 print-state / 0.25 Street GBV route)")
    add("print-state only (R01 x B02; Street weight 0)", w_street=0.0)
    add("Street GBV route weight 0.40", w_street=0.40)
    add("Street route only (GBV N(26,300, 850))", w_street=1.0)
    add("Street route = MODL N(26,375, 600)", w_street=1.0, gbv_override=26_375.0, gbv_sd=600.0)
    add("Street route = B1 stacked N(26,550, 853)", w_street=1.0, gbv_override=26_549.8, gbv_sd=853.2)
    add("nights centre 9.5 (rev 1), sd 1.6", nights_mu=9.5, nights_sd=1.6)
    add("nights centre 9.9 (team baseline path)", nights_mu=9.9)
    add("nights centre 10.5", nights_mu=10.5)
    add("nights centre 11.45 (Street mean), sd 1.7", nights_mu=11.45)
    add("nights sd 2.16 (index no better than naive)", nights_sd=2.16)
    add("nights sd 1.48 (published index RMSE)", nights_sd=1.48)
    add("ADR fixed N(3.3, 1.3) (rev-1 card)", adr_fixed=(3.3, 1.3))
    add("ADR fixed N(4.4, 1.0) (R07 case)", adr_fixed=(4.4, 1.0))
    add("ADR fixed N(2.0, 1.0) (B02 case)", adr_fixed=(2.0, 1.0))
    add("rho(nights, ADR) +0.3 common factor", rho_na=0.3)
    add("cushion 0.86% (last two Q3s)", cushion_mu=0.0086)
    add("cushion 1.40% (3Q23)", cushion_mu=0.014)
    add("cushion 1.86% (trailing-8 all quarters)", cushion_mu=0.0186)
    add("cushion 0 (print at the guide midpoint), sd 0.3%", cushion_mu=0.0, cushion_sd=0.003)
    add("revenue-light branch 0", p_light=0.0)
    add("revenue-light branch 0.30", p_light=0.30)
    add("P(guide miss) 0", p_miss=0.0)
    add("P(guide miss) 0.10", p_miss=0.10)
    add("rho(cushion, GBV) 0", rho=0.0)
    add("rho(cushion, GBV) 0.8", rho=0.8)
    add("no GBV rounding in the ratio", round_gbv=False)
    add("joint bull GBV: nights 11.0, ADR N(4.4,1.0), cushion 0.86, Street 0.40", nights_mu=11.0, adr_fixed=(4.4, 1.0), cushion_mu=0.0086, w_street=0.40)
    add("joint bear GBV: nights 8.5, ADR N(2.0,1.0), cushion 1.4, Street 0", nights_mu=8.5, adr_fixed=(2.0, 1.0), cushion_mu=0.014, w_street=0.0)
    s = pd.DataFrame(sens); s.to_csv(HERE / "c11_v2_sensitivity.csv", index=False); print(s.to_string())

    # ---- Astra's construction, reproduced, and what its language regime implies for the revenue guide ----
    r = np.random.default_rng(20260917); n = N
    gn = r.normal(9.5, 1.6, n) / 100; ga = r.normal(3.3, 1.3, n) / 100; gbv = GBV_3Q25 * (1 + gn) * (1 + ga)
    z = (gbv - gbv.mean()) / gbv.std(); cushion = 0.010433 + 0.005 * (0.5 * z + np.sqrt(0.75) * r.normal(0, 1, n))
    rev = 4_730 * (1 + cushion); miss = r.random(n) < 0.05; rev = np.where(miss, 4_690 * (1 + r.normal(-0.003, 0.004, n)), rev)
    direct = rev / gbv >= 0.181
    lang_take = r.normal(17.9, 0.35, n); language = lang_take >= 18.1
    lang_rev = lang_take / 100 * gbv
    use_lang = r.random(n) >= 0.70
    final = np.where(use_lang, language, direct)
    print("\nAstra reproduction: direct", round(direct.mean(), 4), "language", round(language.mean(), 4), "final", round(final.mean(), 4))
    print("Astra language regime: P(revenue implied by take N(17.9,0.35) x GBV < guide low 4,690) =", round((lang_rev < GUIDE_LOW).mean(), 3),
          "| < guide mid 4,730:", round((lang_rev < GUIDE_MID).mean(), 3), "| unconditional guide-miss probability implied:", round(0.30 * (lang_rev < GUIDE_LOW).mean() + 0.70 * 0.05, 3))

    # ---- management take-rate language record, corrected (A05-03), from the guidance ledger and the driver history ----
    lang = pd.DataFrame([
        ("4Q22", "1Q23", "similar to Q1 2022", "flat", 0.14), ("1Q23", "2Q23", "above Q2 2022", "higher", 0.63), ("2Q23", "3Q23", "higher than Q3 2022", "higher", 0.07),
        ("3Q23", "4Q23", "slightly higher than Q4 2022", "higher", 0.22), ("4Q23", "1Q24", "notably higher than Q1 2023", "higher", 0.44),
        ("2Q24", "3Q24", "higher on a year-over-year basis", "higher", 0.0043), ("3Q24", "4Q24", "slightly lower", "lower", -0.22),
        ("1Q25", "2Q25", "higher than in Q2 2024", "higher", 0.2122), ("2Q25", "3Q25", "flat year-over-year", "flat", -0.6851), ("3Q25", "4Q25", "relatively flat", "flat", -0.4733),
        ("4Q25", "1Q26", "up slightly", "higher", -0.1022), ("1Q26", "2Q26", "up slightly", "higher", 0.0902), ("2Q26", "3Q26", "relatively in-line", "flat", np.nan),
    ], columns=["guide_letter", "target", "language", "direction", "realised_yoy_pp"])
    lang["realised_bp"] = (lang.realised_yoy_pp * 100).round(1)
    lang["direction_met"] = np.where(lang.direction.eq("higher"), lang.realised_bp > 0, np.where(lang.direction.eq("lower"), lang.realised_bp < 0, lang.realised_bp.abs() <= 25))
    lang.loc[lang.realised_bp.isna(), "direction_met"] = None
    lang["ge_plus22bp"] = lang.realised_bp >= 22
    lang.to_csv(HERE / "c11_v2_language_record.csv", index=False)
    done = lang[lang.realised_bp.notna()]
    print(lang.to_string())
    print("language record n", len(done), "| direction met", int(done.direction_met.sum()), "| realised >= +22bp", int(done.ge_plus22bp.sum()),
          "| flat-class realised:", done[done.direction.eq("flat")].realised_bp.tolist(), "| last six mean bp", round(done.tail(6).realised_bp.mean(), 1),
          "sd", round(done.tail(6).realised_bp.std(ddof=1), 1))
