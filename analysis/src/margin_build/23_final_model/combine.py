"""WS23 step 1: the final margin combination.

Leave-future-out inverse-MAE weights with shrinkage toward equal weights, over a
pre-registered member pool (prereg.json), plus a zero-parameter management-sentence
clip. Registered as final-margin__combined with conformal quantiles built from the
combination's OWN point-in-time errors.

Outputs (data/processed/margin_build/23_final_model/)
  23_combination_by_quarter.csv    per window/horizon/quarter: members, weights, point, error
  23_combination_weights.csv       the weight table at every vintage (and LIVE)
  23_combination_scores.csv        MAE/RMSE/bias, equal and recency, vs every baseline, with p-values
  23_combination_live.csv          LIVE 3Q26-4Q27 points, margin and dollars, both revenue legs
  23_conformal.csv                 the conformal band at each vintage and LIVE
  registry/final-margin__combined.csv (via the harness)

Interpreter: py -3.13
"""
from __future__ import annotations

import json
import math
import sys
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[4]
HARNESS = ROOT / "analysis" / "src" / "margin_build" / "10_harness_margin"
sys.path.insert(0, str(HARNESS))

from harness_margin import register  # noqa: E402

PROC = ROOT / "data" / "processed" / "margin_build"
HDIR = PROC / "10_harness_margin"
OUT = PROC / "23_final_model"
OUT.mkdir(parents=True, exist_ok=True)
HERE = Path(__file__).resolve().parent
PREREG = json.loads((HERE / "prereg.json").read_text())

TODAY = "2026-09-11"
LAMBDA = 0.5
MIN_PRIOR = 4
HL = 4.0
TARGETS = ["adj_ebitda_margin_pct", "adj_ebitda_musd"]

FAMILY_A = [
    "driver-lines|margin_v2|b_elastic_rw",
    "cycle-flex|flex_margin|l0_rw",
    "margin-ts|sarima_margin|lines_aicc",
]

SPECS = {
    "stack_clip": dict(lam=0.5, clip=True),
    "stack": dict(lam=0.5, clip=False),
    "stack_lam25_clip": dict(lam=0.25, clip=True),
    "stack_ew_clip": dict(lam=1.0, clip=True),
}
PRIMARY = "stack_clip"


# --------------------------------------------------------------------------- utils
def rw_weights(n, hl=HL):
    age = np.arange(n - 1, -1, -1)
    return 0.5 ** (age / hl)


def nw1_t(d):
    """Newey-West(1) t on mean(d)."""
    d = np.asarray(d, float)
    d = d[~np.isnan(d)]
    n = len(d)
    if n < 3:
        return np.nan, np.nan
    dm = d - d.mean()
    g0 = (dm * dm).sum() / n
    g1 = (dm[1:] * dm[:-1]).sum() / n
    lrv = g0 + 2 * 0.5 * g1
    if lrv <= 0:
        lrv = g0
    se = math.sqrt(max(lrv, 1e-18) / n)
    t = d.mean() / se if se > 0 else np.nan
    from scipy.stats import norm
    p = 2 * (1 - norm.cdf(abs(t))) if np.isfinite(t) else np.nan
    return t, p


def sign_test(d):
    """One-sided exact binomial: how often is d < 0 (method better)? Ties dropped."""
    from scipy.stats import binom
    d = np.asarray(d, float)
    d = d[~np.isnan(d)]
    d = d[d != 0]
    n = len(d)
    k = int((d < 0).sum())
    if n == 0:
        return k, n, np.nan
    p = 1 - binom.cdf(k - 1, n, 0.5)
    return k, n, p


def conformal_qhat(errs, alpha):
    e = np.sort(np.abs(np.asarray(errs, float)))
    e = e[~np.isnan(e)]
    n = len(e)
    if n == 0:
        return np.nan, 0, "empty"
    k = math.ceil((n + 1) * (1 - alpha))
    if k > n:
        return float(e[-1] * (n + 1) / n), n, "inflated_max"
    return float(e[k - 1]), n, "split_conformal"


# --------------------------------------------------------------------------- data
def load_member_points():
    """Long frame of member points from the harness by-quarter file (backtest)."""
    q = pd.read_csv(HDIR / "scoreboard_by_quarter.csv")
    q = q[q.target.isin(TARGETS)].copy()
    q["spec_id"] = q["spec_id"].fillna("(none)")
    q["label"] = q.method + "|" + q["object"] + "|" + q.spec_id
    # baselines put target/horizon/replay inside spec_id: collapse them to method|object
    isb = q.method == "baselines-margin"
    q.loc[isb, "label"] = q.loc[isb, "method"] + "|" + q.loc[isb, "object"]
    return q


def load_live_points():
    import glob
    rows = []
    for f in glob.glob(str(PROC / "registry" / "*.csv")):
        if f.endswith(".bak"):
            continue
        d = pd.read_csv(f)
        d = d[(d.window == "LIVE") & (d.vintage_date == TODAY) & d.target.isin(TARGETS)]
        if len(d):
            rows.append(d)
    lv = pd.concat(rows, ignore_index=True)
    lv["spec_id"] = lv["spec_id"].fillna("(none)")
    lv["label"] = lv.method + "|" + lv["object"] + "|" + lv.spec_id
    isb = lv.method == "baselines-margin"
    lv.loc[isb, "label"] = lv.loc[isb, "method"] + "|" + lv.loc[isb, "object"]
    return lv


def load_guides():
    g = pd.read_csv(HDIR / "guides_margin.csv")
    g = g[(~g.is_fy) & g.metric.isin(["adj_ebitda_margin_yoy_pts", "adj_ebitda_margin_pct"])]
    return g.copy()


def guide_in_force(guides, vintage, quarter):
    s = guides[(guides.target_period == quarter) & (guides.guide_date <= vintage)]
    if s.empty:
        return None
    r = s.sort_values("guide_date").iloc[-1]
    return dict(metric=r.metric, guide_type=r.guide_type, value=float(r.value),
                guide_date=r.guide_date, quote=r.quote)


def apply_clip(point, guide, naive_level):
    """Clip a margin point to the quarterly management sentence. Zero parameters."""
    if guide is None or not np.isfinite(point):
        return point, "no_sentence", np.nan
    if guide["metric"] == "adj_ebitda_margin_yoy_pts":
        if not np.isfinite(naive_level):
            return point, "no_naive", np.nan
        level = naive_level + guide["value"]
    else:
        level = guide["value"]
    if guide["guide_type"] == "ceiling" and point > level:
        return level, "clipped_ceiling", level
    if guide["guide_type"] == "floor" and point < level:
        return level, "clipped_floor", level
    return point, "sentence_not_binding", level


# --------------------------------------------------------------------------- core
def member_pool(target, horizon):
    key = "members_margin" if target == "adj_ebitda_margin_pct" else "members_dollars"
    pool = PREREG[key].get(f"h{min(horizon, 2)}")
    return list(pool)


def expand(pool):
    """Replace FAMILY_A with its three constituents; return (atomic labels, family flag)."""
    atoms, fam = [], []
    for m in pool:
        if m == "FAMILY_A":
            fam = list(FAMILY_A)
            atoms += fam
        else:
            atoms.append(m)
    return atoms, fam


def member_matrix(qf, target, window, horizon, basis, pool):
    """quarter x member point matrix, with FAMILY_A collapsed to its mean."""
    atoms, fam = expand(pool)
    s = qf[(qf.target == target) & (qf.window == window) & (qf.horizon_q == horizon)
           & (qf.prior_basis == basis) & (qf.label.isin(atoms))]
    if s.empty:
        return None, None, None
    pts = s.pivot_table(index="quarter", columns="label", values="point")
    act = s.groupby("quarter")["actual"].first()
    nai = s.groupby("quarter")["seasonal_naive_point"].first()
    vin = s.groupby("quarter")["vintage_date"].first()
    cols = {}
    for m in pool:
        if m == "FAMILY_A":
            have = [c for c in fam if c in pts.columns]
            if have:
                cols["FAMILY_A"] = pts[have].mean(axis=1)
        elif m in pts.columns:
            cols[m] = pts[m]
    if not cols:
        return None, None, None
    P = pd.DataFrame(cols)
    meta = pd.DataFrame(dict(actual=act, naive=nai, vintage_date=vin)).reindex(P.index)
    return P, meta, list(P.columns)


def weights_from_prior(prior_abs, lam):
    mae = prior_abs.mean()
    mae = mae.replace(0, np.nan)
    inv = 1.0 / mae
    if inv.isna().all():
        w = pd.Series(1.0 / len(mae), index=mae.index)
    else:
        inv = inv.fillna(inv.min())
        w = inv / inv.sum()
    K = len(mae)
    w = (1 - lam) * w + lam * (1.0 / K)
    return w / w.sum()


def run_backtest():
    qf = load_member_points()
    guides = load_guides()
    rows, wrows, conf_rows = [], [], []

    for target in TARGETS:
        for window in ["W1", "W2"]:
            for horizon in [0, 1, 2]:
                pool = member_pool(target, horizon)
                for basis in ["PIT", "full_sample"]:
                    P, meta, members = member_matrix(qf, target, window, horizon, basis, pool)
                    if P is None:
                        continue
                    P = P.dropna(axis=1, how="all")
                    members = list(P.columns)
                    qs = sorted(P.index)
                    # per-spec state: running list of the combination's own abs errors
                    for spec, cfg in SPECS.items():
                        lam, clip = cfg["lam"], cfg["clip"]
                        own_err = {}          # quarter -> signed error
                        for i, tq in enumerate(qs):
                            p = P.loc[tq].dropna()
                            if p.empty:
                                continue
                            lab = list(p.index)
                            if basis == "PIT":
                                prior_q = qs[:i]
                            else:
                                prior_q = [x for x in qs if x != tq] or qs
                            prior = (P.loc[prior_q, lab] - meta.loc[prior_q, "actual"].values[:, None]).abs() \
                                if prior_q else pd.DataFrame(columns=lab)
                            prior = prior.dropna(axis=0, how="any")
                            if len(prior) >= MIN_PRIOR:
                                w = weights_from_prior(prior, lam)
                                wsrc = f"invmae_shrunk_lam{lam}"
                            else:
                                w = pd.Series(1.0 / len(lab), index=lab)
                                wsrc = "equal_insufficient_prior"
                            w = w.reindex(lab).fillna(0.0)
                            w = w / w.sum()
                            raw = float((p * w).sum())
                            g = guide_in_force(guides, meta.loc[tq, "vintage_date"], tq)
                            if clip and target == "adj_ebitda_margin_pct":
                                point, clipnote, level = apply_clip(raw, g, meta.loc[tq, "naive"])
                            else:
                                point, clipnote, level = raw, "clip_off", np.nan
                            a = float(meta.loc[tq, "actual"])
                            err = point - a
                            # conformal band from own PIT errors before this quarter
                            hist = [own_err[x] for x in qs[:i] if x in own_err]
                            if target == "adj_ebitda_margin_pct":
                                fb80, fb90, rel = 3.0, 4.0, False
                            else:
                                fb80, fb90, rel = 0.10 * abs(point), 0.13 * abs(point), True
                            if len(hist) >= MIN_PRIOR:
                                q80, n80, k80 = conformal_qhat(hist, 0.20)
                                q90, n90, k90 = conformal_qhat(hist, 0.10)
                            else:
                                q80, n80, k80 = fb80, len(hist), "fallback"
                                q90, n90, k90 = fb90, len(hist), "fallback"
                            own_err[tq] = err
                            rows.append(dict(
                                target=target, window=window, horizon_q=horizon,
                                prior_basis=basis, spec_id=spec, quarter=tq,
                                vintage_date=meta.loc[tq, "vintage_date"],
                                point=point, raw_point=raw, actual=a, err=err, abs_err=abs(err),
                                seasonal_naive_point=meta.loc[tq, "naive"],
                                clip=clipnote, sentence_level=level,
                                n_members=len(lab), weight_source=wsrc,
                                q10=point - q80, q90=point + q80,
                                q05=point - q90, q95=point + q90,
                                conformal_n=n80, conformal_kind=k80, qhat80=q80, qhat90=q90))
                            if spec == PRIMARY and basis == "PIT":
                                for m in lab:
                                    wrows.append(dict(target=target, window=window,
                                                      horizon_q=horizon, quarter=tq,
                                                      vintage_date=meta.loc[tq, "vintage_date"],
                                                      member=m, weight=float(w[m]),
                                                      member_point=float(p[m]),
                                                      prior_n=len(prior)))
                                conf_rows.append(dict(target=target, window=window,
                                                      horizon_q=horizon, quarter=tq,
                                                      qhat80=q80, qhat90=q90, n=n80, kind=k80))
    bt = pd.DataFrame(rows)
    bt.to_csv(OUT / "23_combination_by_quarter.csv", index=False)
    pd.DataFrame(wrows).to_csv(OUT / "23_combination_weights.csv", index=False)
    pd.DataFrame(conf_rows).to_csv(OUT / "23_conformal.csv", index=False)
    return bt


# --------------------------------------------------------------------------- LIVE
def run_live(bt):
    lv = load_live_points()
    guides = load_guides()
    qf = load_member_points()
    rev = pd.read_csv(PROC / "06_fy27_path_v2" / "06_revenue_path_3q26_4q27_v2b.csv")
    revb = rev[(rev.line == "revenue_musd")].pivot(index="quarter", columns="scenario", values="value")
    naive_lvl = {"2026Q3": 50.085470, "2026Q4": 28.286745}   # y[q-4] from targets.csv, filled below
    tg = pd.read_csv(HDIR / "targets.csv").set_index("quarter")
    for q, q4 in [("2026Q3", "2025Q3"), ("2026Q4", "2025Q4"), ("2027Q1", "2026Q1"),
                  ("2027Q2", "2026Q2")]:
        naive_lvl[q] = float(tg.loc[q4, "adj_ebitda_margin_pct"])

    qorder = ["2026Q3", "2026Q4", "2027Q1", "2027Q2", "2027Q3", "2027Q4"]
    out = []
    for target in TARGETS:
        for hz, qq in enumerate(qorder):
            pool = member_pool(target, hz)
            atoms, fam = expand(pool)
            sub = lv[(lv.target == target) & (lv.quarter == qq) & (lv.prior_basis == "PIT")
                     & (lv.label.isin(atoms))]
            if sub.empty:
                continue
            p = sub.groupby("label")["point"].first()
            vals = {}
            for m in pool:
                if m == "FAMILY_A":
                    have = [c for c in fam if c in p.index]
                    if have:
                        vals["FAMILY_A"] = float(p[have].mean())
                elif m in p.index:
                    vals[m] = float(p[m])
            if not vals:
                continue
            v = pd.Series(vals)
            # weights from the FULL PIT backtest history of the same target/horizon (W1)
            P, meta, members = member_matrix(qf, target, "W1", min(hz, 2), "PIT", pool)
            for spec, cfg in SPECS.items():
                lam, clip = cfg["lam"], cfg["clip"]
                lab = [m for m in v.index]
                if P is not None:
                    prior = (P[[c for c in lab if c in P.columns]]
                             .sub(meta["actual"], axis=0)).abs().dropna(axis=0, how="any")
                else:
                    prior = pd.DataFrame()
                if len(prior) >= MIN_PRIOR and set(prior.columns) == set(lab):
                    w = weights_from_prior(prior, lam)
                    wsrc = f"invmae_shrunk_lam{lam}_full_W1_history"
                else:
                    w = pd.Series(1.0 / len(lab), index=lab)
                    wsrc = "equal"
                w = w.reindex(lab).fillna(0.0)
                w = w / w.sum()
                raw = float((v[lab] * w).sum())
                g = guide_in_force(guides, TODAY, qq)
                if clip and target == "adj_ebitda_margin_pct":
                    point, clipnote, level = apply_clip(raw, g, naive_lvl.get(qq, np.nan))
                else:
                    point, clipnote, level = raw, "clip_off", np.nan
                # conformal from the PIT W1 h=min(hz,2) history of THIS spec
                hist = bt[(bt.target == target) & (bt.window == "W1")
                          & (bt.horizon_q == min(hz, 2)) & (bt.prior_basis == "PIT")
                          & (bt.spec_id == spec)]["err"].tolist()
                q80, n80, k80 = conformal_qhat(hist, 0.20) if len(hist) >= MIN_PRIOR else (np.nan, 0, "none")
                q90, n90, k90 = conformal_qhat(hist, 0.10) if len(hist) >= MIN_PRIOR else (np.nan, 0, "none")
                bias = float(np.mean(hist)) if len(hist) >= MIN_PRIOR else np.nan
                row = dict(target=target, quarter=qq, horizon_q=hz, spec_id=spec,
                           point=point, raw_point=raw, clip=clipnote, sentence_level=level,
                           weight_source=wsrc, n_members=len(lab),
                           qhat80=q80, qhat90=q90, conformal_n=n80, conformal_kind=k80,
                           pit_bias=bias)
                for m in lab:
                    row[f"w__{m}"] = float(w[m])
                    row[f"p__{m}"] = float(v[m])
                if target == "adj_ebitda_margin_pct":
                    for sc in ["base", "bear", "bull"]:
                        if qq in revb.index and sc in revb.columns and np.isfinite(revb.loc[qq, sc]):
                            row[f"ebitda_musd_{sc}"] = point / 100.0 * float(revb.loc[qq, sc])
                out.append(row)
    live = pd.DataFrame(out)
    live.to_csv(OUT / "23_combination_live.csv", index=False)
    return live


# --------------------------------------------------------------------------- scores
def score(bt):
    qf = load_member_points()
    base_labels = {"seasonal_naive": "baselines-margin|seasonal_naive",
                   "seasonal_naive_drift": "baselines-margin|seasonal_naive_drift",
                   "street": "baselines-margin|street",
                   "q_guide_implied": "baselines-margin|q_guide_implied",
                   "guide_implied": "baselines-margin|guide_implied",
                   "trailing4": "baselines-margin|trailing4"}
    rows = []
    for (target, window, hz, basis, spec), g in bt.groupby(
            ["target", "window", "horizon_q", "prior_basis", "spec_id"]):
        g = g.sort_values("quarter")
        w = rw_weights(len(g))
        rec = dict(target=target, window=window, horizon_q=hz, prior_basis=basis, spec_id=spec,
                   n=len(g), first_quarter=g.quarter.iloc[0], last_quarter=g.quarter.iloc[-1],
                   mae=g.abs_err.mean(), rw_mae=float((g.abs_err * w).sum() / w.sum()),
                   rmse=float(np.sqrt((g.err ** 2).mean())), bias=g.err.mean(),
                   cov80=float(((g.actual >= g.q10) & (g.actual <= g.q90)).mean()),
                   cov90=float(((g.actual >= g.q05) & (g.actual <= g.q95)).mean()),
                   n_clipped=int((g["clip"].astype(str).str.startswith("clipped")).sum()))
        for bname, blab in base_labels.items():
            b = qf[(qf.target == target) & (qf.window == window) & (qf.horizon_q == hz)
                   & (qf.prior_basis == basis) & (qf.label == blab)]
            if b.empty:
                b = qf[(qf.target == target) & (qf.window == window) & (qf.horizon_q == hz)
                       & (qf.prior_basis == "PIT") & (qf.label == blab)]
            if b.empty:
                continue
            bq = b.set_index("quarter")["abs_err"]
            m = g.set_index("quarter")["abs_err"]
            common = m.index.intersection(bq.index)
            if len(common) == 0:
                continue
            d = (m[common] - bq[common]).values
            wc = rw_weights(len(common))
            t, p = nw1_t(d)
            k, ncmp, ps = sign_test(d)
            rec[f"mae_ratio_{bname}"] = float(m[common].mean() / bq[common].mean())
            rec[f"rw_mae_ratio_{bname}"] = float((m[common] * wc).sum() / (bq[common] * wc).sum())
            rec[f"n_match_{bname}"] = len(common)
            rec[f"d_mean_{bname}"] = float(np.mean(d))
            rec[f"t_nw1_{bname}"] = t
            rec[f"p_nw1_{bname}"] = p
            rec[f"k_better_{bname}"] = k
            rec[f"n_cmp_{bname}"] = ncmp
            rec[f"p_sign_{bname}"] = ps
        rows.append(rec)
    sc = pd.DataFrame(rows)
    sc.to_csv(OUT / "23_combination_scores.csv", index=False)
    return sc


# --------------------------------------------------------------------------- registry
def build_registry(bt, live):
    rows = []
    for _, r in bt.iterrows():
        rows.append(dict(method="final-margin", object="combined", target=r.target,
                         quarter=r.quarter, vintage_date=r.vintage_date,
                         horizon_q=int(r.horizon_q), point=r.point, q50=r.point,
                         q05=r.q05, q10=r.q10, q90=r.q90, q95=r.q95,
                         window=r.window, prior_basis=r.prior_basis,
                         n_params=PREREG["n_params_declared"], n_train=int(r.n_members),
                         spec_id=r.spec_id,
                         notes=f"WS23 combination; {r.weight_source}; {r.clip}; "
                               f"conformal {r.conformal_kind} n={r.conformal_n}"))
    for _, r in live.iterrows():
        if not np.isfinite(r.qhat80):
            q10 = q90 = q05 = q95 = np.nan
        else:
            q10, q90 = r.point - r.qhat80, r.point + r.qhat80
            q05, q95 = r.point - r.qhat90, r.point + r.qhat90
        for basis in ["PIT", "full_sample"]:
            rows.append(dict(method="final-margin", object="combined", target=r.target,
                             quarter=r.quarter, vintage_date=TODAY, horizon_q=int(r.horizon_q),
                             point=r.point, q50=r.point, q05=q05, q10=q10, q90=q90, q95=q95,
                             window="LIVE", prior_basis=basis,
                             n_params=PREREG["n_params_declared"], n_train=int(r.n_members),
                             spec_id=r.spec_id,
                             notes=f"WS23 LIVE; {r.weight_source}; {r.clip}; "
                                   f"revenue leg = bridge v3 / WS06 v2b for dollars"))
    df = pd.DataFrame(rows)
    df = df.dropna(subset=["point"])
    register(df)
    return df


def main():
    print("WS23 combine: backtest replay ...")
    bt = run_backtest()
    print(f"  {len(bt)} backtest rows")
    print("WS23 combine: LIVE ...")
    live = run_live(bt)
    print(f"  {len(live)} live rows")
    print("WS23 combine: scoring ...")
    sc = score(bt)
    cols = ["target", "window", "horizon_q", "prior_basis", "spec_id", "n", "mae", "rw_mae",
            "mae_ratio_seasonal_naive", "rw_mae_ratio_seasonal_naive", "mae_ratio_street",
            "k_better_seasonal_naive", "p_sign_seasonal_naive", "cov80"]
    show = sc[(sc.target == "adj_ebitda_margin_pct") & (sc.prior_basis == "PIT")]
    print(show[cols].sort_values(["horizon_q", "window", "spec_id"]).to_string(index=False))
    print("WS23 combine: registering final-margin__combined ...")
    df = build_registry(bt, live)
    print(f"  registered {len(df)} rows")
    print(live[live.spec_id == PRIMARY][["target", "quarter", "point", "raw_point", "clip",
                                         "qhat80", "pit_bias"]].to_string(index=False))


if __name__ == "__main__":
    main()
