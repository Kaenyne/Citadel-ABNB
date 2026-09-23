"""adr_engine_v3 / fx_falsifier.py — audit fix (b): the 3Q26 / 4Q26 FX falsifier, re-specified before the print.

The registered falsifier (adr_fx_prereg.md section 7a) required the printed ADR-FX pp to fall inside the 21 Sep 80%
band [0.36, 0.48]. The printed figure is reported y/y minus a WHOLE-POINT ex-FX, so it carries +/-0.5pp of rounding;
a perfectly correct identity lands inside a 0.125pp band only ~12% of the time (audit F11). The amendment filed on
23 Sep 2026 (adr_fx_prereg.md section 11) replaces it with a comparative interval score:

  L_c = P( mu_c + e in [y - h, y + h] ),  e ~ N(0, SIGMA^2)

for each named candidate c, where y is the printed ADR-FX pp, h the rounding half-width (0.5, or 0.25 for a half-point
ex-FX disclosure) and SIGMA the registration's own V1 model error (MAP sigma on all 17 quarters, 0.44pp).
Rules: the identity (V0) is withdrawn as the leg only if it has the LOWEST likelihood of the named candidates; V1
replaces it only if V1 has the HIGHEST likelihood and at least 3x V0's."""
from __future__ import annotations
import numpy as np
import pandas as pd
from scipy import stats

SIGMA = 0.44
CANDIDATES_3Q26 = {"V0_identity": 0.415, "V1_fitted": 0.030, "card_midpoint": -0.43, "euro_fit": -1.12}   # named 21-23 Sep 2026
# audit fix (j), named 23 Sep: the card-method midpoint refreshed on the engine's data ((V0 + V2) / 2), the proposed leg
CANDIDATES_3Q26_J = CANDIDATES_3Q26 | {"midpoint_refreshed": -0.406}


def interval_likelihood(mu: float, y: float, h: float = 0.5, sigma: float = SIGMA) -> float:
    return float(stats.norm.cdf((y + h - mu) / sigma) - stats.norm.cdf((y - h - mu) / sigma))


def score_print(y: float, candidates: dict[str, float] | None = None, h: float = 0.5, sigma: float = SIGMA,
                leg: str = "V0_identity") -> dict:
    """Score a printed ADR-FX pp against the named candidates and apply the amended rules. `leg` is the candidate that
    is the adopted FX leg (V0 under DEC-0034/0044; midpoint_refreshed under DEC-0048): it is withdrawn only if it
    scores worst."""
    cands = candidates or CANDIDATES_3Q26
    t = pd.DataFrame({"candidate": list(cands), "point_pp": list(cands.values())})
    t["likelihood"] = [interval_likelihood(m, y, h, sigma) for m in t.point_pp]
    t = t.sort_values("likelihood", ascending=False).reset_index(drop=True)
    L = t.set_index("candidate").likelihood
    withdraw_v0 = bool(t.candidate.iloc[-1] == "V0_identity")
    withdraw_leg = bool(t.candidate.iloc[-1] == leg)
    # adr_fx_prereg.md section 12 (fix j): a leg in the middle of the candidate range can never rank last, so for the
    # midpoint leg the rule is a likelihood ratio: withdraw if the best candidate explains the print >= 3x better.
    withdraw_leg_ratio3 = bool(L.iloc[0] >= 3 * L[leg]) if leg in L.index else False
    promote_v1 = bool(t.candidate.iloc[0] == "V1_fitted" and L["V1_fitted"] >= 3 * L["V0_identity"])
    return {"table": t, "withdraw_v0": withdraw_v0, "withdraw_leg": withdraw_leg, "withdraw_leg_ratio3": withdraw_leg_ratio3,
            "promote_v1": promote_v1}


def false_withdrawal_rate(true_fx: float, n: int = 20000, seed: int = 11, candidates: dict[str, float] | None = None,
                          leg: str = "V0_identity", rule: str = "withdraw_leg") -> float:
    """Share of simulated prints that withdraw the leg when true FX = true_fx (ex-FX uniform, rounded to a whole point)."""
    rng = np.random.default_rng(seed)
    ex = rng.uniform(2.0, 5.0, n)
    printed = (ex + true_fx) - np.round(ex)
    return float(np.mean([score_print(float(y), candidates, leg=leg)[rule] for y in printed]))
