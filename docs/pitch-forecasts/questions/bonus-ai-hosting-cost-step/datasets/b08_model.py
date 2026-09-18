"""B08 bonus-ai-hosting-cost-step: 4Q26 cost of revenue >= $575M (leg 2) and/or a quantified FY27 AI/hosting step >= $50M (leg 1).
numpy/pandas only, seed 20260917. Run from the repo root:
  py -3.13 docs/pitch-forecasts/questions/bonus-ai-hosting-cost-step/datasets/b08_model.py
"""
import pathlib
from math import erf, sqrt
import numpy as np
import pandas as pd

rng = np.random.default_rng(20260917)
N = 400_000
here = pathlib.Path(__file__).resolve().parent
rows = []

# --- history: reported cost of revenue and GBV (data/processed/margin_build/02_financial_panel/02_panel_quarterly.csv)
hist = pd.DataFrame({
    "quarter": ["1Q23", "2Q23", "3Q23", "4Q23", "1Q24", "2Q24", "3Q24", "4Q24", "1Q25", "2Q25", "3Q25", "4Q25", "1Q26", "2Q26"],
    "cor": [428, 432, 459, 384, 480, 506, 465, 427, 506, 544, 549, 487, 581, 633],
    "gbv": [20400, 19100, 18300, 15500, 22900, 21200, 20100, 17600, 24500, 23500, 22900, 20400, 29200, 27200]})
hist["cor_yoy"] = hist["cor"].pct_change(4) * 100
hist["gbv_yoy"] = hist["gbv"].pct_change(4) * 100
hist["ratio"] = hist["cor"] / hist["gbv"] * 100
hist["ratio_yoy"] = hist["ratio"].pct_change(4) * 100
hist.to_csv(here / "b08_history.csv", index=False)
r = hist["ratio_yoy"].dropna()
rows.append(("ratio_yoy_mean_pct", r.mean()))
rows.append(("ratio_yoy_sd_pct", r.std(ddof=1)))


def leg2(gbv_mu=22990, gbv_sd=650, rate_mu=1.756, rate_sd=0.04, host_mix=(0.45, 0.35, 0.20), host_mu=(15, 30, 45), resid_sd=12, thr=575):
    """CoR = merchant fees (rate x GBV) + chargebacks + hosting + other, the 40_line_build formula."""
    gbv = rng.normal(gbv_mu, gbv_sd, N)
    rate = rng.normal(rate_mu, rate_sd, N)
    fees = gbv * rate / 100
    bookings = 132.7 / 3.65
    cb = rng.normal(0.72 * bookings, 4, N)
    other = rng.normal(0.36 * 132.7, 3, N)
    comp = rng.choice(3, N, p=host_mix)
    step = np.where(comp == 0, rng.normal(host_mu[0], 5, N),
                    np.where(comp == 1, rng.normal(host_mu[1], 8, N), rng.normal(host_mu[2], 10, N)))
    hosting = 56 + np.clip(step, 0, None)
    cor = fees + cb + hosting + other + rng.normal(0, resid_sd, N)
    return cor, (cor >= thr).mean()


cor, p2 = leg2()
rows += [("leg2_p_base", p2), ("leg2_cor_median", np.median(cor)), ("leg2_cor_p10", np.quantile(cor, .1)),
         ("leg2_cor_p90", np.quantile(cor, .9)), ("leg2_p_yoy_ge_18", ((cor / 487 - 1) >= 0.18).mean())]
for name, kw in [("gbv_street_high_23565", dict(gbv_mu=23565)), ("gbv_low_22400", dict(gbv_mu=22400)),
                 ("rate_1.735_rebates_persist", dict(rate_mu=1.735)), ("rate_1.818_fy25_rate", dict(rate_mu=1.818)),
                 ("hosting_evidence_only", dict(host_mix=(1.0, 0.0, 0.0))), ("hosting_line_build_recon", dict(host_mix=(0.0, 0.0, 1.0))),
                 ("hosting_mix_40_40_20", dict(host_mix=(0.40, 0.40, 0.20))), ("resid_sd_20", dict(resid_sd=20)), ("resid_sd_6", dict(resid_sd=6))]:
    _, p = leg2(**kw)
    rows.append(("leg2_p_" + name, p))

# base-rate route on the CoR/GBV ratio: needed y/y ratio change at GBV +12.7%
need = 1.18 / 1.127 - 1
rows.append(("leg2_needed_ratio_change_pct", need * 100))
Phi = lambda z: 0.5 * (1 + erf(z / sqrt(2)))
rows.append(("leg2_base_rate_unshifted", 1 - Phi((need * 100 - r.mean()) / r.std(ddof=1))))
rows.append(("leg2_base_rate_hosting_shift_+2.5", 1 - Phi((need * 100 - (r.mean() + 2.5)) / r.std(ddof=1))))
rows.append(("leg2_base_rate_gbv_15pct", 1 - Phi(((1.18 / 1.15 - 1) * 100 - r.mean()) / r.std(ddof=1))))

# --- leg 1: a quantified FY27 AI/hosting/infrastructure step >= $50M by the Feb print
p1_given_yes, p1_given_no = 0.40, 0.18
p_total = p2 + (1 - p2) * p1_given_no
rows += [("leg1_p_given_leg2", p1_given_yes), ("leg1_p_given_not_leg2", p1_given_no),
         ("leg1_unconditional", p2 * p1_given_yes + (1 - p2) * p1_given_no), ("p_total_base", p_total)]
for a, b in [(0.30, 0.12), (0.50, 0.25), (0.40, 0.10), (0.40, 0.30)]:
    rows.append((f"p_total_leg1_given_no_{b}", p2 + (1 - p2) * b))
out = pd.DataFrame(rows, columns=["item", "value"])
out.to_csv(here / "b08_results.csv", index=False)
print(out.to_string())
