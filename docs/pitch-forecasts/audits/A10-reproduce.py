"""A10 audit reproduction - R04, R05, R07. stdlib + pandas only; writes nothing."""
from pathlib import Path
from statistics import NormalDist, mean, pstdev
import random
import pandas as pd

ROOT = Path.cwd()
N = 400_000


def read(p):
    return pd.read_csv(ROOT / p)


def hdr(s):
    print("\n" + "=" * 8 + " " + s + " " + "=" * 8)


# ---------------------------------------------------------------- R05
hdr("R05  ceiling base rate")
led = read("docs/pitch-forecasts/questions/fy26-margin-sentence/"
           "datasets/quarterly_margin_sentence_ledger.csv")
led = led[led.guide_type.isin(["ceiling", "point", "floor"]) & led.actual.notna()].copy()
led = led[~led.target_period.isin(["3Q21", "4Q21", "2Q22", "4Q22"])]
led.loc[led.target_period == "3Q22", "actual"] = 50.52 - 49.22
led.loc[led.target_period == "3Q22", "value_high"] = 49.0 - 49.22
ceil = led[led.guide_type == "ceiling"].drop_duplicates("target_period").copy()
ceil["excess"] = ceil.actual - ceil.value_high
n_c = len(ceil)
k14 = int((ceil.excess >= 1.4).sum())
k0 = int((ceil.excess > 0).sum())
print("ceilings n:", n_c, " exceeded by >=1.4pp:", k14, " exceeded at all:", k0,
      " Laplace:", (k14 + 1) / (n_c + 2))
print("rows in the source with target 4Q25 (2Q25 and 3Q25 prints):",
      int((led.target_period == "4Q25").sum()),
      "- drop_duplicates keeps the h=2 sentence, not the h=1 analogue")
print(ceil[["print_quarter", "target_period", "value_high", "actual", "excess"]]
      .to_string(index=False))

hdr("R05  line build: is D&A inside total_cash_costs?")
lb = read("data/processed/margin_build/40_line_build/40_lines_quarterly.csv")
b = lb[(lb.quarter == "3Q26") & (lb.scenario == "base")].iloc[0]
lines = ["cor_cash", "ops_cash", "pd_cash", "sm_cash", "ga_cash"]
print("sum of cash lines:", round(sum(b[c] for c in lines), 3),
      " total_cash_costs:", round(b.total_cash_costs, 3))
print("revenue - cash costs       :", round(b.revenue - b.total_cash_costs, 3))
print("revenue - cash costs + D&A :", round(b.revenue - b.total_cash_costs + b.da, 3),
      " == 40_lines adj_ebitda", round(b.adj_ebitda, 3))
print("op_income check rev-cash-SBC:", round(b.revenue - b.total_cash_costs - b.sbc, 3),
      " == op_income", round(b.op_income, 3))
print("line-build 3Q26 margin:", round(b.adj_ebitda_margin_pct, 4),
      " vs R05 MC centre (rev-cost, no add-back):",
      round(100 * (b.revenue - b.total_cash_costs) / b.revenue, 4),
      " -> D&A is worth", round(100 * b.da / b.revenue, 4), "pp")
cl = read("data/processed/abnb_quarterly_costlines.csv")
r25 = cl[cl.quarter == "3Q25"].iloc[0]
cash25 = (r25.cost_of_revenue_musd + r25.operations_and_support_musd
          + r25.product_development_musd + r25.sales_and_marketing_musd
          + r25.general_and_administrative_musd - r25.stock_based_comp_total_musd)
print("3Q25 identity: cash costs ex-SBC", cash25,
      " revenue-cash", r25.revenue_musd - cash25,
      " printed adj EBITDA", r25.adjusted_ebitda_musd,
      " implied D&A", round(r25.adjusted_ebitda_musd - (r25.revenue_musd - cash25), 1))
print("3Q25 printed S&M:", r25.sales_and_marketing_musd,
      " line-build S&M base implied by 40_lines:",
      round(b.sm_cash / (1 + b.sm_cash_yoy_pct / 100), 1))

hdr("R05  cost-stack Monte Carlo, as published and with the D&A add-back")
rng = random.Random(20260917)
draws = [(rng.gauss(4804, 50), rng.random(), rng.gauss(0, 60), rng.uniform(30, 97))
         for _ in range(N)]
for da, lab in [(0.0, "as published"), (20.634, "with line-build D&A add-back")]:
    hits = hits_ceiling = tot = 0
    ms = []
    for rev, u, e, slp in draws:
        cost = 2405.0 + e - (slp if u < 0.25 else 0.0) + 0.20 * (rev - 4804)
        m = 100 * (rev - cost + da) / rev
        ms.append(m)
        hits += m >= 51.5
        hits_ceiling += m >= 50.085
        tot += 1
    ms.sort()
    print(f"{lab:32s} P(>=51.5)={hits/tot:.4f}  median={ms[tot//2]:.3f}  "
          f"sd={pstdev(ms):.3f}  P(>=50.085)={hits_ceiling/tot:.4f}")

hdr("R05  Gaussian routes on the card, and what the card's own band says")
bands = read("data/processed/margin_build/23_final_model/23_bands.csv")
bm = bands[(bands.target == "adj_ebitda_margin_pct") & (bands.horizon_q == 0)]
print(bm[["calibration", "n", "qhat80", "gaussian_from_mae_80",
          "gaussian_sd_from_qhat80", "mae", "bias", "bias_last5"]].to_string(index=False))
card = read("data/processed/margin_build/23_final_model/23_card_5nov.csv")
mu = float(card.loc[card["item"] == "3Q26 adj EBITDA margin", "value"].iloc[0])
sd_w1 = float(bm[bm.calibration == "W1_all_n14"].gaussian_sd_from_qhat80.iloc[0])
sd_w2 = float(bm[bm.calibration == "recent_2024Q1plus"].gaussian_sd_from_qhat80.iloc[0])
b5 = float(bm.bias_last5.iloc[0])
for lab, m, s in [("card raw, W1 sd", mu, sd_w1), ("card raw, W2 sd", mu, sd_w2),
                  ("bias-corrected (last5), W2 sd", mu - b5, sd_w2)]:
    d = NormalDist(m, s)
    print(f"{lab:30s} mu={m:.3f} sd={s:.3f} P(>=51.5)={1-d.cdf(51.5):.4f} "
          f"P(>=50.085)={1-d.cdf(50.085):.4f} P(>Street 49.776)={1-d.cdf(49.7757):.4f}")
print("gaussian_from_mae_80 (1.297) is an 80% HALF-WIDTH; r05_model uses 1.30 as an sd."
      f"  as sd: {1-NormalDist(mu,1.2971).cdf(51.5):.4f}"
      f"  as half-width: {1-NormalDist(mu,1.2971/1.2816).cdf(51.5):.4f}")
print("C04 rev-2 draws 3Q26 margin ~ N(49.95, 1.0) -> P(>=51.5) =",
      round(1 - NormalDist(49.95, 1.0).cdf(51.5), 4), "(R05 publishes 0.17)")

hdr("R05  revenue leg: cash costs and S&M implied by a 51.5% print")
for rv in [4744.32, 4770, 4804.04, 4850]:
    c_pub = rv * (1 - 0.515)
    c_da = c_pub + 20.634
    sm_pub = 778.3 - (2405.0 - c_pub)
    sm_da = 778.3 - (2405.0 - c_da)
    print(f"rev {rv:8.1f} published: costs<={c_pub:7.1f} S&M<={sm_pub:6.0f} "
          f"({100*(sm_pub/585-1):+5.1f}% y/y) | with D&A: costs<={c_da:7.1f} "
          f"S&M<={sm_da:6.0f} ({100*(sm_da/585-1):+5.1f}% y/y)")
print("1H26 printed S&M growth: 1Q26", round(100 * (751 / 563 - 1), 1),
      "%  2Q26", round(100 * (875 / 691 - 1), 1), "%")

hdr("R05  Street and the M5 anchor")
vc = read("data/processed/margin_build/23_final_model/23_vs_consensus.csv")
q3 = vc[vc.period == "2026Q3"].iloc[0]
print("LSEG 3Q26 EBITDA", round(q3.lseg_ebitda_musd, 2), "margin",
      round(q3.lseg_margin_pct, 4), "n", q3.lseg_n, "EBITDA sd", q3.lseg_ebitda_sd_musd)
sd_m5 = (50.19 - q3.lseg_margin_pct) / NormalDist().inv_cdf(0.62)
print("sd implied by M5 composite 50.19 and P(margin beat) 0.62:", round(sd_m5, 3),
      "-> P(>=51.5) =", round(1 - NormalDist(50.19, sd_m5).cdf(51.5), 4))
print("raw Street at its own EBITDA sd: P(EBITDA >= 0.515 x 4804) =",
      round(1 - NormalDist(q3.lseg_ebitda_musd, q3.lseg_ebitda_sd_musd)
            .cdf(0.515 * 4804.0355), 6))

# ---------------------------------------------------------------- R07
hdr("R07  ADR history and base rates")
h = read("data/processed/q3nowcast/H/adr_history_components.csv")
hh = h[["quarter", "adr_yoy_reported_pp", "fx_effect_pp", "adr_exfx_yoy_pp",
        "residual_pricing_pp"]]
print(hh.to_string(index=False))
print("n:", len(hh), " reported >= 4.4:", int((hh.adr_yoy_reported_pp >= 4.4).sum()),
      " quarters with FX <= 0:", int((hh.fx_effect_pp <= 0).sum()), "(the log says 7)",
      " reported>=4.4 with FX<=0:",
      int(((hh.adr_yoy_reported_pp >= 4.4) & (hh.fx_effect_pp <= 0)).sum()),
      " ex-FX-0.43 >= 4.4:", int(((hh.adr_exfx_yoy_pp - 0.43) >= 4.4).sum()))
res = hh.residual_pricing_pp.tolist()
dif = [y - x for x, y in zip(res, res[1:])]
print("residual quarterly changes:", [round(x, 2) for x in dif])
print("  mean", round(mean(dif), 3), " sd", round(pstdev(dif), 3),
      " |change| >= 1.26 in", sum(abs(x) >= 1.26 for x in dif), "of", len(dif))

hdr("R07  card v3: what the mix term actually is")
c3 = read("data/processed/adrv3/P/adr_card_v3.csv")
for _, r in c3[c3.quarter == "3Q26"].iterrows():
    print(f"{r.variant:14s} {r.fx_estimator:9s} fx={r.fx_effect_pp:+.2f} "
          f"resid={r.residual_pp:.2f} exfx={r.adr_exfx_yoy_pp:.2f} "
          f"reported={r.adr_reported_yoy_pp:.2f} usd={r.adr_usd_point:.2f} "
          f"mix(exfx-resid)={r.adr_exfx_yoy_pp - r.residual_pp:+.3f}")
print("=> the card's mix term is -1.16, so r07_model's -1.15 IS the card's mix and its")
print("   'mix -0.98 (H fills)' row is the same thing with the K line moved out of the")
print("   residual. The MC's persistence branch reproduces the WITHOUT-K card (+3.26).")

hdr("R07  walk-forward errors and Gaussian routes")
p = read("data/processed/adrv3/P/P1_card_v3_backtest_paths.csv")
p2 = p[p.target == "t2_reported_usd_yoy"]
for fx, pt in [("midpoint", 3.43), ("eur", 2.74), ("baskets", 4.12)]:
    qf = p2[p2.fx_estimator == fx]
    e = (qf.v3_point_last_q_plus_K_line_measured_mix - qf.actual).tolist()
    rmse = (sum(x * x for x in e) / len(e)) ** 0.5
    bi = mean(e)
    print(f"{fx:9s} n={len(e)} RMSE={rmse:.3f} bias={bi:+.3f} "
          f"P(>=4.4) raw={1-NormalDist(pt, rmse).cdf(4.4):.4f} "
          f"bias-corrected={1-NormalDist(pt-bi, rmse).cdf(4.4):.4f}")

hdr("R07 / B02  one distribution or two?")
rng = random.Random(20260917)
lo = hi = tot = 0
vals = []
for _ in range(N):
    mix = rng.gauss(-1.15, 0.35)
    u = rng.random()
    r = (rng.gauss(4.85, 0.55) if u < 0.55 else
         rng.gauss(5.35, 0.55) if u < 0.75 else rng.gauss(3.6, 0.7))
    v = rng.random()
    fx = (rng.gauss(-0.43, 0.33) if v < 0.5 else
          rng.gauss(0.26, 0.42) if v < 0.75 else rng.gauss(-1.12, 0.46))
    x = mix + r + fx
    vals.append(x)
    hi += x >= 4.4
    lo += x <= 2.0
    tot += 1
vals.sort()
print(f"r07_model mixture: P(>=4.4)={hi/tot:.4f} P(<=2.0)={lo/tot:.4f} "
      f"median={vals[tot//2]:.3f} sd={pstdev(vals):.3f}")
print("published pair: R07 0.17 (model 0.11, lifted ~1.5x); B02 0.18 (model 0.176, no lift)")
z1, z2 = NormalDist().inv_cdf(1 - 0.17), NormalDist().inv_cdf(0.18)
sg = (4.4 - 2.0) / (z1 - z2)
mu_j = 4.4 - z1 * sg
print(f"the Normal that would carry BOTH published tails: N({mu_j:.2f}, {sg:.2f})")
print("  its centre is below the card without K (3.26) and with K (3.43); its sd is 38%")
print("  above the card's own walk-forward RMSE (0.93)")
for m, s in [(3.43, 0.93), (3.50, 1.05), (3.74, 0.93)]:
    d = NormalDist(m, s)
    print(f"  coherent alternative N({m}, {s}): R07 {1-d.cdf(4.4):.3f}  B02 {d.cdf(2.0):.3f}")

hdr("R07  MODL anchor")
e = read("data/processed/reverse_dcf/E/E_street_distribution_vs_team.csv")
a = e[(e.quarter == "3Q26") & (e.metric == "adr_usd")].iloc[0]
sd_modl = (a.street_high_growth - a.street_low_growth) / 4
print("MODL n", a.n_estimates, "low/mean/high growth",
      round(a.street_low_growth, 3), round(a.street_mean_growth, 3),
      round(a.street_high_growth, 3), " range/4 =", round(sd_modl, 3),
      " P(>=4.4) =", round(1 - NormalDist(a.street_mean_growth, sd_modl).cdf(4.4), 4))
print("threshold 178.83 sits at",
      round(100 * (178.83 - a.street_low) / (a.street_high - a.street_low), 1),
      "% of the analyst range (the log says the 96th percentile)")

# ---------------------------------------------------------------- R04
hdr("R04  driver-attribution table and route arithmetic")
d4 = read("docs/pitch-forecasts/questions/risk-single-fee-take-rate-accretion-stated/"
          "datasets/r04_driver_attribution_history.csv")
print("letters/calls n:", len(d4),
      " driver named:", int((~d4.driver_named.str.startswith("none")).sum()),
      " positive monetization driver:",
      int(d4.positive_monetization_driver_named.str.startswith("yes").sum()),
      " conditional:",
      int((d4.positive_monetization_driver_named == "conditional").sum()))
dec = read("docs/pitch-forecasts/questions/risk-single-fee-take-rate-accretion-stated/"
           "datasets/r04_decomposition.csv").set_index("item").value
a_, b_ = dec.letter_route_5nov, dec.call_route_5nov
ind = a_ * b_
inter = ind + dec.overlap_rho * (min(a_, b_) - ind)
union = a_ + b_ - inter
print(f"letter {a_} call {b_}  independence-intersection {ind:.6f}  "
      f"rho-blended intersection {inter:.6f}  union {union:.6f} "
      f"(file: {dec.p_yes_5nov})")
tot4 = union + (1 - union) * dec.p_yes_feb_given_no_nov
print("total with the Feb conditional:", round(tot4, 6), "(file:", dec.p_yes_total, ")")
for per in [0.375, 0.25, 0.5]:
    print(f"  per-print base {per} -> two prints, independent: {1-(1-per)**2:.4f}")
print("the two-print base rate assumes the prints are independent; management's framing")
print("is persistent, so 0.61 is an upper bound on that class.")
try:
    read("docs/pitch-forecasts/questions/risk-single-fee-take-rate-accretion-stated/"
         "datasets/r04_statement_record.csv")
    print("r04_statement_record.csv parses")
except Exception as exc:
    print("r04_statement_record.csv DOES NOT PARSE:", type(exc).__name__, exc)

hdr("R04  impact arithmetic")
fy27 = vc[vc.period == "FY27"].iloc[0]
fy27_rev, fy27_eb = float(fy27.model_revenue_musd), float(fy27.model_ebitda_musd)
d_rev, flow = 230.0, 0.90
old_m = 100 * fy27_eb / fy27_rev
new_m = 100 * (fy27_eb + d_rev * flow) / (fy27_rev + d_rev)
print(f"FY27 model revenue {fy27_rev:.1f} EBITDA {fy27_eb:.1f} margin {old_m:.3f}%")
print(f"  log's arithmetic  d_EBITDA / OLD revenue = {100*d_rev*flow/fy27_rev:.3f} pp "
      f"(the published +1.3pp)")
print(f"  correct           new margin {new_m:.3f}% -> {new_m-old_m:+.3f} pp")
print(f"  brief's rule      {100*d_rev/fy27_rev:.3f}% of revenue x 0.66 = "
      f"{0.66*100*d_rev/fy27_rev:+.3f} pp")
print("share count: the card uses 591.7m; the R04/R05/R07 impact tables use 620m "
      f"(205M of EBITDA at 16x: ${205*16/591.7:.2f} vs ${205*16/620:.2f} per share)")
