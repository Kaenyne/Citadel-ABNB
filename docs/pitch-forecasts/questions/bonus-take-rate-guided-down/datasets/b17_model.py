"""B17 bonus-take-rate-guided-down: routes at the 5 Nov print, correlated via a Gaussian copula. numpy/pandas/scipy, seed 20260917.
  py -3.13 docs/pitch-forecasts/questions/bonus-take-rate-guided-down/datasets/b17_model.py
"""
import pathlib
from math import erf, sqrt
import numpy as np
import pandas as pd

_erf = np.vectorize(erf)


class norm:  # minimal stand-in for scipy.stats.norm.cdf (numpy/math only)
    @staticmethod
    def cdf(x):
        return 0.5 * (1 + _erf(np.asarray(x) / sqrt(2)))


rng = np.random.default_rng(20260917)
N = 400_000
here = pathlib.Path(__file__).resolve().parent
rows = []

# 4Q26 take-rate arithmetic (4Q25 printed 13.62% = 2,778 / 20,400)
for lab, rev, gbv in [("team_bridge_v3", 3178.1, 22987), ("street_lseg_modl", 3161.8, 23003),
                      ("team_rev_street_gbv_high", 3178.1, 23565), ("short_case_rev_2966_gbv_scaled", 2966, 22987 * 2966 / 3178.1),
                      ("rnpl_pullforward_gbv_+2pct", 3178.1, 22987 * 1.02), ("rnpl_pullforward_gbv_+4pct", 3178.1, 22987 * 1.04)]:
    tr = rev / gbv * 100
    rows.append((f"tr_4q26_{lab}_pct", tr))
    rows.append((f"tr_4q26_{lab}_yoy_bp", (tr - 13.62) * 100))


def sim(p_letter_lower=0.12, p_topic=0.80, p_qual_given_topic=0.50, p_fy27=0.06, rho=0.5, strict=False):
    z = rng.normal(size=(N, 3))
    z[:, 1] = rho * z[:, 0] + np.sqrt(1 - rho ** 2) * z[:, 1]
    z[:, 2] = rho * z[:, 0] + np.sqrt(1 - rho ** 2) * z[:, 2]
    u = norm.cdf(z)
    a = u[:, 0] < p_letter_lower                                    # letter Q4 sentence: lower / down y/y
    b = (u[:, 1] < p_topic) & (rng.random(N) < p_qual_given_topic)  # incentives / new businesses / pilot named as reducing the forward take rate
    c = u[:, 2] < p_fy27                                            # explicit FY27 lower statement
    if strict:
        b = b & (rng.random(N) < 0.55)                              # only statements naming 4Q26 or FY27 count (FY26 wording excluded)
    return (a | b | c).mean(), a.mean(), b.mean(), c.mean()


p, a, b, c = sim()
rows += [("p_base", p), ("route_letter_lower", a), ("route_incentives_named", b), ("route_fy27", c)]
p_s, _, _, _ = sim(strict=True)
rows.append(("p_strict_convention", p_s))
for name, kw in [("letter_lower_0.20", dict(p_letter_lower=0.20)), ("letter_lower_0.06", dict(p_letter_lower=0.06)),
                 ("topic_0.60", dict(p_topic=0.60)), ("qual_given_topic_0.35", dict(p_qual_given_topic=0.35)),
                 ("qual_given_topic_0.65", dict(p_qual_given_topic=0.65)), ("rho_0", dict(rho=0.0)), ("rho_0.8", dict(rho=0.8)),
                 ("fy27_0.15", dict(p_fy27=0.15))]:
    pp, _, _, _ = sim(**kw)
    rows.append(("p_" + name, pp))
rows += [("base_rate_all_letters_2of13_laplace", (2 + 1) / (13 + 2)),
         ("base_rate_new_business_regime_1of5_laplace", (1 + 1) / (5 + 2)),
         ("base_rate_q3_letters_1of3_laplace", (1 + 1) / (3 + 2))]
out = pd.DataFrame(rows, columns=["item", "value"])
out.to_csv(here / "b17_results.csv", index=False)
print(out.to_string())
