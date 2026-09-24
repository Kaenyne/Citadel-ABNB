"""adr_engine_v3 / core_horizon.py — fix (m): the core's point-in-time record by horizon, carry vs expanding mean
(docs/pitch-model-v2/lines/core_2027_prereg.md). Same construction as the audit's C1 walk-forward
(receipts/ADR_AUDIT/audit_core.py), extended from h = 1-4 to h = 1-6; h = 1-4 must reproduce the audit's scores.
The engine reads the h = 5 and h = 6 pass flags from core_horizon_scores.csv."""
from __future__ import annotations
import numpy as np
import pandas as pd
from . import config as C
from . import exfx as M

HORIZONS = range(1, 7)
WINDOWS = (("targets 1Q24+", "1Q24"), ("targets 1Q25+", "1Q25"))


def _ar1(x):
    b, a = np.polyfit(x[:-1], x[1:], 1)
    return a, b


def walkforward() -> pd.DataFrame:
    core = M.history().core; qs = list(core.index); c = core.values; recs = []
    for i in range(4, len(qs)):                     # origin qs[i-1]; at least 4 observations (the audit's rule)
        hist = c[:i]
        for k in HORIZONS:
            j = i - 1 + k
            if j >= len(qs):
                continue
            a, b = _ar1(hist); f = hist[-1]
            for _ in range(k):
                f = a + b * f
            recs.append({"origin": qs[i - 1], "target": qs[j], "h": k, "actual": c[j], "carry": hist[-1], "mean": hist.mean(), "ar1": f})
    return pd.DataFrame(recs)


def scores(wf: pd.DataFrame) -> pd.DataFrame:
    out = []
    for k, g in wf.groupby("h"):
        for w, start in WINDOWS:
            g2 = g[g.target.map(C.qlabel_to_period) >= C.qlabel_to_period(start)]
            e = {m: float(np.sqrt(np.mean((g2[m] - g2.actual) ** 2))) for m in ("carry", "mean", "ar1")}
            out.append({"h": int(k), "window": w, "n": len(g2), **{f"rmse_{m}": v for m, v in e.items()},
                        "mean_vs_carry": e["mean"] / e["carry"], "ar1_vs_carry": e["ar1"] / e["carry"],
                        "targets": f"{g2.target.iloc[0]}..{g2.target.iloc[-1]}" if len(g2) else ""})
    s = pd.DataFrame(out)
    s["registered"] = s.h.isin([5, 6])
    s["mean_wins"] = s.mean_vs_carry < 1
    return s


def rule_by_quarter(s: pd.DataFrame) -> pd.DataFrame:
    """Prereg section 2: carry at h 1-2; mean at h 3-4 (post-hoc, audit); mean at h 5 / 6 only if it wins there."""
    rows = []
    for h, q in enumerate(C.FORWARD_QUARTERS, start=1):
        g = s[s.h == h]
        if h <= 2:
            rule, basis = "carry", "h <= 2: carry (the windows split at h = 2)"
        elif h <= 4:
            rule, basis = "mean", "h = 3-4: mean wins both windows in the audit (post-hoc)"
        else:
            win = bool(g.mean_wins.all())
            rule, basis = ("mean" if win else "carry"), f"h = {h}: registered test {'PASS' if win else 'FAIL'} (mean/carry {g.mean_vs_carry.max():.3f}, n {int(g.n.max())})"
        rows.append({"quarter": q, "h": h, "core_rule": rule, "basis": basis,
                     "mean_rmse_max": float(g.rmse_mean.max()) if len(g) else np.nan})
    return pd.DataFrame(rows).set_index("quarter")


def main() -> pd.DataFrame:
    wf = walkforward(); s = scores(wf)
    wf.to_csv(C.OUT / "core_horizon_walkforward.csv", index=False); s.to_csv(C.OUT / "core_horizon_scores.csv", index=False)
    r = rule_by_quarter(s); r.to_csv(C.OUT / "core_horizon_rule.csv")
    return r


if __name__ == "__main__":
    print(main())
