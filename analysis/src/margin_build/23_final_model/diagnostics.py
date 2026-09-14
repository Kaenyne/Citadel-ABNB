"""WS23 diagnostics: how much of the combination's edge is which member, and is it
the weights or the pool?

  23_diag_leave_one_out.csv   drop each member in turn, re-run the PIT replay
  23_diag_member_scores.csv   each member's own PIT MAE on the same matched quarters
  23_diag_shock_vs_calm.csv   the combination in the 1H23 break, the 1H25 shock and the calm quarters

Interpreter: py -3.13
"""
from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[4]
HERE = Path(__file__).resolve().parent
import sys
sys.path.insert(0, str(HERE))
import combine as C  # noqa: E402

OUT = C.OUT


def replay(qf, guides, target, window, horizon, pool, lam=0.5, clip=True):
    P, meta, members = C.member_matrix(qf, target, window, horizon, "PIT", pool)
    if P is None:
        return None
    qs = sorted(P.index)
    rows = []
    for i, tq in enumerate(qs):
        p = P.loc[tq].dropna()
        if p.empty:
            continue
        lab = list(p.index)
        prior_q = qs[:i]
        prior = (P.loc[prior_q, lab] - meta.loc[prior_q, "actual"].values[:, None]).abs() \
            if prior_q else pd.DataFrame(columns=lab)
        prior = prior.dropna(axis=0, how="any")
        if len(prior) >= C.MIN_PRIOR:
            w = C.weights_from_prior(prior, lam)
        else:
            w = pd.Series(1.0 / len(lab), index=lab)
        w = w.reindex(lab).fillna(0.0)
        w = w / w.sum()
        raw = float((p * w).sum())
        g = C.guide_in_force(guides, meta.loc[tq, "vintage_date"], tq)
        point = C.apply_clip(raw, g, meta.loc[tq, "naive"])[0] if (clip and target.endswith("pct")) else raw
        a = float(meta.loc[tq, "actual"])
        rows.append(dict(quarter=tq, point=point, actual=a, err=point - a, abs_err=abs(point - a),
                         naive_abs_err=abs(float(meta.loc[tq, "naive"]) - a)))
    return pd.DataFrame(rows)


def main():
    qf = C.load_member_points()
    guides = C.load_guides()
    target = "adj_ebitda_margin_pct"
    full_pool = C.PREREG["members_margin"]["h0"]

    rows = []
    for window in ["W1", "W2"]:
        base = replay(qf, guides, target, window, 0, full_pool)
        b_mae = base.abs_err.mean()
        rows.append(dict(window=window, variant="ALL (stack_clip)", n=len(base), mae=b_mae,
                         ratio_to_naive=b_mae / base.naive_abs_err.mean(),
                         delta_vs_full_pp=0.0, dropped=""))
        for m in full_pool:
            pool = [x for x in full_pool if x != m]
            r = replay(qf, guides, target, window, 0, pool)
            rows.append(dict(window=window, variant=f"drop {m}", n=len(r), mae=r.abs_err.mean(),
                             ratio_to_naive=r.abs_err.mean() / r.naive_abs_err.mean(),
                             delta_vs_full_pp=r.abs_err.mean() - b_mae, dropped=m))
        # Street-independent: everything that does not read consensus
        ind = [m for m in full_pool if not m.startswith("street-bias")
               and m != "baselines-margin|street"]
        r = replay(qf, guides, target, window, 0, ind)
        rows.append(dict(window=window, variant="STREET-INDEPENDENT ONLY (M3 + M2sent + family)",
                         n=len(r), mae=r.abs_err.mean(),
                         ratio_to_naive=r.abs_err.mean() / r.naive_abs_err.mean(),
                         delta_vs_full_pp=r.abs_err.mean() - b_mae, dropped="all Street-anchored"))
        # no clip
        r = replay(qf, guides, target, window, 0, full_pool, clip=False)
        rows.append(dict(window=window, variant="NO SENTENCE CLIP", n=len(r), mae=r.abs_err.mean(),
                         ratio_to_naive=r.abs_err.mean() / r.naive_abs_err.mean(),
                         delta_vs_full_pp=r.abs_err.mean() - b_mae, dropped="the clip"))
    lo = pd.DataFrame(rows)
    lo.to_csv(OUT / "23_diag_leave_one_out.csv", index=False)

    # each member's own PIT MAE on the same quarters
    rows = []
    for window in ["W1", "W2"]:
        P, meta, members = C.member_matrix(qf, target, window, 0, "PIT", full_pool)
        for m in P.columns:
            e = P[m] - meta["actual"]
            rows.append(dict(window=window, member=m, n=int(e.notna().sum()),
                             mae=float(e.abs().mean()), bias=float(e.mean())))
        nai = meta["naive"] - meta["actual"]
        rows.append(dict(window=window, member="seasonal_naive (= the sentence level)",
                         n=int(nai.notna().sum()), mae=float(nai.abs().mean()), bias=float(nai.mean())))
    pd.DataFrame(rows).to_csv(OUT / "23_diag_member_scores.csv", index=False)

    # shock vs calm
    bt = pd.read_csv(OUT / "23_combination_by_quarter.csv")
    s = bt[(bt.target == target) & (bt.window == "W1") & (bt.horizon_q == 0)
           & (bt.prior_basis == "PIT") & (bt.spec_id == "stack_clip")]
    sets = {"all_14": s.quarter.tolist(),
            "stress_1H23": ["2023Q1", "2023Q2"],
            "hard_2H23": ["2023Q3", "2023Q4"],
            "shock_1H25": ["2025Q1", "2025Q2"],
            "calm_last4": ["2025Q3", "2025Q4", "2026Q1", "2026Q2"]}
    rows = []
    for name, qs in sets.items():
        sub = s[s.quarter.isin(qs)]
        nb = qf[(qf.target == target) & (qf.window == "W1") & (qf.horizon_q == 0)
                & (qf.prior_basis == "PIT") & (qf.label == "baselines-margin|street")]
        nb = nb[nb.quarter.isin(qs)]
        rows.append(dict(set=name, n=len(sub), combination_mae=sub.abs_err.mean(),
                         street_mae=nb.abs_err.mean() if len(nb) else np.nan,
                         naive_mae=sub.seasonal_naive_point.sub(sub.actual).abs().mean()))
    pd.DataFrame(rows).to_csv(OUT / "23_diag_shock_vs_calm.csv", index=False)

    # LIVE 3Q26 for the Street-independent variant (what the pitch may quote when it
    # explicitly does not want to lean on consensus)
    lvp = C.load_live_points()
    ind = [m for m in full_pool if not m.startswith("street-bias") and m != "baselines-margin|street"]
    atoms, fam = C.expand(ind)
    sub = lvp[(lvp.target == target) & (lvp.quarter == "2026Q3") & (lvp.prior_basis == "PIT")
              & (lvp.label.isin(atoms))]
    pt = sub.groupby("label")["point"].first()
    vals = {}
    for m in ind:
        if m == "FAMILY_A":
            have = [c for c in fam if c in pt.index]
            if have:
                vals["FAMILY_A"] = float(pt[have].mean())
        elif m in pt.index:
            vals[m] = float(pt[m])
    P, meta, _ = C.member_matrix(qf, target, "W1", 0, "PIT", ind)
    prior = (P[list(vals)] .sub(meta["actual"], axis=0)).abs().dropna(axis=0, how="any")
    w = C.weights_from_prior(prior, 0.5).reindex(list(vals)).fillna(0.0)
    w = w / w.sum()
    raw = float(sum(vals[m] * w[m] for m in vals))
    g = C.guide_in_force(guides, C.TODAY, "2026Q3")
    clipped = C.apply_clip(raw, g, 50.085470)[0]
    pd.DataFrame([dict(variant="street_independent_live_3Q26", raw_pct=raw, clipped_pct=clipped,
                       weights=json.dumps({k: round(float(w[k]), 4) for k in vals}),
                       points=json.dumps({k: round(v, 4) for k, v in vals.items()}))])         .to_csv(OUT / "23_diag_street_independent_live.csv", index=False)
    print("street-independent LIVE 3Q26: raw %.3f clipped %.3f" % (raw, clipped))

    pd.set_option("display.width", 220)
    print(lo.round(4).to_string(index=False))
    print()
    print(pd.read_csv(OUT / "23_diag_member_scores.csv").round(3).to_string(index=False))
    print()
    print(pd.read_csv(OUT / "23_diag_shock_vs_calm.csv").round(3).to_string(index=False))


if __name__ == "__main__":
    main()
