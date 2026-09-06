"""WS22 acceptance checks for the repaired regulatory Monte Carlo (audit finding A06).

Imports the live simulator `analysis/src/abnb_regulatory_forecast.py`, re-runs it with the same seed and
200,000 draws, and asserts the four properties the audit asked for:

  1. zero child-without-parent occurrences (EU-TAIL requires EU-AHA);
  2. zero mutually exclusive Barcelona full/partial overlaps;
  3. simulated marginal AND conditional probabilities inside a 4-sigma binomial Monte Carlo band around the
     declared targets (target sigma = sqrt(p(1-p)/N); at N=200k, 4 sigma is about 0.18pp at p=0.5);
  4. monotone by-date event sets: {in force by end-2027} is a subset of {in force by end-2030} on every path.

It also reports the sensitivity of the aggregate profile to the choice of nesting construction for EU-TAIL
(comonotone severity ladder on the parent's uniform, as shipped, versus an independent inner Bernoulli gate
inside the parent), because both preserve the 2%/8% marginal but imply different joint tails.

Reads:  analysis/src/abnb_regulatory_forecast.py (EVENTS, draw, GROUP_RHO, N, RNG)
Writes: data/processed/overnight/22_regulatory_checks.csv
Exit status: 0 if every check passes, 1 otherwise.
Run: py -3.13 analysis/src/overnight/22_regulatory_checks.py
"""
from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[3]
OUT = ROOT / "data/processed/overnight"
SRC = ROOT / "analysis/src/abnb_regulatory_forecast.py"

spec = importlib.util.spec_from_file_location("abnb_regulatory_forecast", SRC)
M = importlib.util.module_from_spec(spec)
spec.loader.exec_module(M)

N = M.N
SIG = 4.0  # sigma band on the binomial Monte Carlo error


def band(p, n=N):
    return SIG * np.sqrt(max(p * (1 - p), 1e-12) / n)


def main():
    ev, out = M.draw(N)
    rows = []

    def add(check, horizon, subject, value, target, tol, kind="probability"):
        ok = bool(target is None or abs(value - target) <= tol)
        rows.append(dict(check=check, horizon=horizon, subject=subject, kind=kind, value=round(float(value), 6),
                         target=None if target is None else round(float(target), 6),
                         tolerance=None if target is None else round(float(tol), 6), passed=ok))
        return ok

    pmap = {r.id: {"2027": r.p27, "2030": r.p30} for r in ev.itertuples()}
    parent_of = {r.id: r.parent for r in ev.itertuples()}
    excl_of = {r.id: r.excl for r in ev.itertuples()}
    kind_of = {r.id: (r.p_kind or "marginal") for r in ev.itertuples()}

    for h in ("2027", "2030"):
        per = out[h]["per_event"]

        # 1. child implies parent
        for cid, pid in parent_of.items():
            if not pid:
                continue
            orphan = (per[cid][0] & ~per[pid][0]).mean()
            add("1_child_without_parent", h, f"{cid} without {pid}, share of draws", orphan, 0.0, 0.0)
            pa = per[pid][0]
            cond = (per[cid][0] & pa).sum() / max(pa.sum(), 1)
            tgt = pmap[cid][h] / pmap[pid][h] if pmap[pid][h] else 0.0
            # conditional target sigma is driven by the number of parent draws
            add("3_conditional_probability", h, f"P({cid} | {pid})", cond, tgt,
                SIG * np.sqrt(max(tgt * (1 - tgt), 1e-12) / max(pa.sum(), 1)))

        # 2. mutually exclusive ladder rungs do not overlap
        for cid, sid in excl_of.items():
            if not sid:
                continue
            add("2_exclusive_overlap", h, f"{cid} and {sid} both occur, share of draws",
                (per[cid][0] & per[sid][0]).mean(), 0.0, 0.0)
            not_strong = ~per[sid][0]
            cond = (per[cid][0] & not_strong).sum() / max(not_strong.sum(), 1)
            tgt = pmap[cid][h]
            add("3_conditional_probability", h, f"P({cid} | not {sid})", cond, tgt,
                SIG * np.sqrt(max(tgt * (1 - tgt), 1e-12) / max(not_strong.sum(), 1)))

        # 3. marginal probabilities against the declared targets
        for r in ev.itertuples():
            p = pmap[r.id][h]
            if kind_of[r.id] == "conditional":
                tgt = p * (1 - pmap[r.excl][h])          # effective unconditional probability
                label = f"P({r.id}) effective = p_cond x (1 - p_{r.excl})"
            else:
                tgt = p
                label = f"P({r.id}) marginal"
            add("3_marginal_probability", h, label, per[r.id][0].mean(), tgt, band(tgt))

    # 4. monotone by-date event sets on a common path
    p27, p30 = out["2027"]["per_event"], out["2030"]["per_event"]
    for r in ev.itertuples():
        rev = (p27[r.id][0] & ~p30[r.id][0]).mean()
        add("4_monotone_path", "2027->2030", f"{r.id} in force by 2027 but not by 2030, share of draws", rev, 0.0, 0.0)
    any_rev = np.zeros(N, bool)
    for r in ev.itertuples():
        any_rev |= p27[r.id][0] & ~p30[r.id][0]
    add("4_monotone_path", "2027->2030", "ANY event reverses, share of draws", any_rev.mean(), 0.0, 0.0)

    # path-level loss monotonicity, excluding the one named upside event (NYC-LOOSEN is a revenue GAIN, so a
    # path can carry a smaller 2030 net loss than 2027 without any regulatory reversal)
    l27 = out["2027"]["loss"] - out["2027"]["per_event"]["NYC-LOOSEN"][1]
    l30 = out["2030"]["loss"] - out["2030"]["per_event"]["NYC-LOOSEN"][1]
    add("4_monotone_path", "2027->2030", "net loss ex NYC-LOOSEN falls from 2027 to 2030, share of draws",
        (l30 < l27 - 1e-9).mean(), 0.0, 0.0, kind="share")
    add("4_monotone_path", "2027->2030", "DIAGNOSTIC total net loss incl NYC-LOOSEN falls, share of draws",
        ((out["2030"]["loss"] - out["2027"]["loss"]) < -1e-9).mean(), None, None, kind="share")

    # 5. sensitivity: alternative admissible nesting for EU-TAIL that also preserves the 2%/8% marginal
    rng = np.random.default_rng(20260906)
    inner = rng.random(N)
    trow = ev[ev.id == "EU-TAIL"].iloc[0]
    lo, mo, hi = trow.loss
    alt_size = rng.triangular(lo, mo, hi, N)   # independent size realisation, same triangular law
    for h in ("2027", "2030"):
        per = out[h]["per_event"]
        parent = per["EU-AHA"][0]
        c = pmap["EU-TAIL"][h] / pmap["EU-AHA"][h]
        alt_occ = parent & (inner < c)         # independent inner Bernoulli inside the parent
        base_loss = out[h]["loss"] - per["EU-TAIL"][1]
        s = alt_size * (trow.scale30 if h == "2030" else 1.0)
        alt_loss = base_loss + np.where(alt_occ, s, 0.0)
        comp = per["COMPLIANCE"][1]
        for lbl, f in (("median", np.median), ("mean", np.mean), ("p95", lambda x: np.percentile(x, 95))):
            rows.append(dict(check="5_sensitivity_alt_nesting", horizon=h,
                             subject=f"revenue loss {lbl} %, independent inner gate instead of severity ladder",
                             kind="pct_of_revenue", value=round(float(f(alt_loss - comp)), 4),
                             target=round(float(f(out[h]["loss"] - comp)), 4), tolerance=None, passed=True))

    df = pd.DataFrame(rows)
    OUT.mkdir(parents=True, exist_ok=True)
    df.to_csv(OUT / "22_regulatory_checks.csv", index=False)
    failed = df[~df.passed]
    pd.set_option("display.width", 220); pd.set_option("display.max_rows", 400); pd.set_option("display.max_colwidth", 70)
    print(df.to_string(index=False))
    print(f"\n{len(df)} checks, {len(failed)} failed")
    if len(failed):
        print(failed.to_string(index=False))
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
