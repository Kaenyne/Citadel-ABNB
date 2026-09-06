"""WS22 step 1: frozen reproduction of the PRE-FIX regulatory Monte Carlo (audit finding A06).

This file deliberately embeds a frozen copy of the probability mechanics of
`analysis/src/abnb_regulatory_forecast.py` AS IT STOOD ON 2026-09-05 (git blame: commit that
introduced the regulatory forecast; audit `docs/2026-09-06_audit_findings_ai_handoff.md` section 8).
It exists so the audit's diagnostic percentages remain reproducible after the fix lands in the
live script. Do not "improve" it; it is a regression baseline.

Reads: nothing (probabilities are inlined).
Writes: data/processed/overnight/22_regulatory_before.csv
Run: py -3.13 analysis/src/overnight/22_regulatory_before.py
"""
from pathlib import Path
import numpy as np, pandas as pd
from scipy.stats import norm

ROOT = Path(__file__).resolve().parents[3]
OUT = ROOT / "data/processed/overnight"
N = 200_000
RNG = np.random.default_rng(20260905)

# id, p27, p30, loss(low,mode,high), scale30, group, cash  -- frozen 2026-09-05 values
OLD = [
    ("EU-AHA", 0.12, 0.45, (0.4, 1.2, 3.0), 1.0, "EU", 0),
    ("EU-TAIL", 0.02, 0.08, (2.0, 3.5, 6.0), 1.0, "EU", 0),
    ("ES-FINE", 0.55, 0.70, (0.0, 0.0, 0.0), 1.0, "EU", 76),
    ("ES-REMOVE", 0.35, 0.55, (0.10, 0.20, 0.45), 1.2, "EU", 0),
    ("ES-REGIONS", 0.45, 0.65, (0.05, 0.15, 0.35), 1.3, "EU", 0),
    ("BCN-2028", 0.0, 0.45, (0.15, 0.22, 0.35), 1.0, "EU", 0),
    ("BCN-PARTIAL", 0.0, 0.55, (0.05, 0.10, 0.18), 1.0, "EU", 0),
    ("MAUI", 0.0, 0.40, (0.04, 0.07, 0.12), 1.0, "US", 0),
    ("PARIS-PRO", 0.30, 0.55, (0.10, 0.20, 0.35), 1.2, "EU", 0),
    ("PARIS-COPRO", 0.90, 0.95, (0.01, 0.03, 0.06), 1.5, "EU", 0),
    ("GR-FREEZE", 0.70, 0.80, (0.02, 0.05, 0.12), 1.8, "EU", 0),
    ("IE-REG", 0.35, 0.55, (0.04, 0.07, 0.15), 1.0, "EU", 0),
    ("UK-ENG", 0.20, 0.45, (0.03, 0.08, 0.20), 1.3, "EU", 0),
    ("IT-NAT", 0.30, 0.60, (0.05, 0.12, 0.30), 1.4, "EU", 0),
    ("PT-RETIGHT", 0.20, 0.35, (0.04, 0.08, 0.18), 1.2, "EU", 0),
    ("NL-AMS", 0.30, 0.50, (0.01, 0.03, 0.06), 1.2, "EU", 0),
    ("US-CITY", 0.30, 0.55, (0.08, 0.18, 0.40), 1.3, "US", 0),
    ("NYC-LOOSEN", 0.20, 0.35, (-0.25, -0.12, -0.05), 1.0, "US", 0),
    ("CHI-SUIT", 0.40, 0.60, (0.01, 0.03, 0.08), 1.0, "US", 20),
    ("COMPLIANCE", 0.90, 0.95, (0.05, 0.12, 0.25), 1.2, "EU", 0),
]
GROUP_RHO = {"EU": 0.45, "US": 0.25}


def draw_old():
    z_eu, z_us = RNG.standard_normal(N), RNG.standard_normal(N)
    out = {}
    for hi_, (h, pi) in enumerate((("2027", 1), ("2030", 2))):
        loss = np.zeros(N); per = {}
        for (eid, p27, p30, loss_t, s30, grp, cash) in OLD:
            p = p27 if h == "2027" else p30
            rho = GROUP_RHO[grp]; zc = z_eu if grp == "EU" else z_us
            u = norm.cdf(np.sqrt(rho) * zc + np.sqrt(1 - rho) * RNG.standard_normal(N))
            occurs = u < p
            lo, mo, hh = loss_t
            size = (RNG.triangular(lo, mo, hh, N) if hh > lo else np.zeros(N)) * (s30 if h == "2030" else 1.0)
            if eid == "BCN-PARTIAL":
                occurs = occurs & ~per["BCN-2028"][0]
            per[eid] = (occurs, np.where(occurs, size, 0.0))
            loss += per[eid][1]
        out[h] = dict(loss=loss, per=per)
    return out


def main():
    o = draw_old()
    r = []
    for h in ("2027", "2030"):
        per = o[h]["per"]
        tail, parent = per["EU-TAIL"][0], per["EU-AHA"][0]
        orphan = tail & ~parent
        r.append(dict(horizon=h, metric="EU-TAIL without EU-AHA parent, % of all draws", value=100 * orphan.mean(),
                      audit_target=1.0845 if h == "2027" else 1.731))
        r.append(dict(horizon=h, metric="EU-TAIL without parent, % of tail occurrences", value=100 * orphan.sum() / max(tail.sum(), 1),
                      audit_target=54.02 if h == "2027" else 21.72))
        r.append(dict(horizon=h, metric="P(EU-TAIL) realised (marginal)", value=100 * tail.mean(), audit_target=2.0 if h == "2027" else 8.0))
        r.append(dict(horizon=h, metric="P(EU-AHA) realised (marginal)", value=100 * parent.mean(), audit_target=12.0 if h == "2027" else 45.0))
        r.append(dict(horizon=h, metric="P(EU-TAIL | EU-AHA) realised", value=100 * (tail & parent).sum() / max(parent.sum(), 1), audit_target=np.nan))
        full, part = per["BCN-2028"][0], per["BCN-PARTIAL"][0]
        r.append(dict(horizon=h, metric="BCN-PARTIAL effective probability, %", value=100 * part.mean(),
                      audit_target=np.nan if h == "2027" else 23.05))
        r.append(dict(horizon=h, metric="BCN full/partial overlap, % of draws", value=100 * (full & part).mean(), audit_target=0.0))
    p27, p30 = o["2027"]["per"], o["2030"]["per"]
    for eid in [e[0] for e in OLD]:
        rev = (p27[eid][0] & ~p30[eid][0]).mean() * 100
        if rev > 0:
            r.append(dict(horizon="2027->2030", metric=f"non-monotone path: {eid} in force by 2027 but not by 2030, % of draws",
                          value=rev, audit_target=3.01 if eid == "EU-AHA" else np.nan))
    any_rev = np.zeros(N, bool)
    for eid in [e[0] for e in OLD]:
        any_rev |= (p27[eid][0] & ~p30[eid][0])
    r.append(dict(horizon="2027->2030", metric="ANY event reverses between 2027 and 2030, % of draws", value=100 * any_rev.mean(), audit_target=np.nan))
    for h in ("2027", "2030"):
        comp = o[h]["per"]["COMPLIANCE"][1]
        rl = o[h]["loss"] - comp
        for lbl, v in (("median", np.median(rl)), ("mean", rl.mean()), ("p95", np.percentile(rl, 95))):
            r.append(dict(horizon=h, metric=f"revenue loss {lbl}, % of revenue", value=v, audit_target=np.nan))
    df = pd.DataFrame(r)
    OUT.mkdir(parents=True, exist_ok=True)
    df.round(4).to_csv(OUT / "22_regulatory_before.csv", index=False)
    print(df.round(4).to_string(index=False))


if __name__ == "__main__":
    main()
