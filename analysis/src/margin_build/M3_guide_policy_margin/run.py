"""M3 -- guidance-policy model for the adjusted-EBITDA margin.

Three objects (see docs/margin-build/notes/M3_guide_policy_margin.md for the pre-registration):

  1. actual_given_guide : FY margin = (FY guide in force) + PIT cushion for the same guide bucket
                          (FEB / MAY / AUG / NOV); the remaining quarters are allocated by
                          m_q = m_{q-4} + delta, one delta solved so the remaining quarters plus the
                          YTD actual hit the FY EBITDA target (the harness baseline prorates the
                          remaining EBITDA by seasonal shares instead; that is the `*_prorata` spec).
  2. guide_forecast     : the NEXT margin sentence -- the November type/level rule and the February
                          floor rule -- backtested at every November / February since 2021.
  3. q4_implied         : the Q4 margin implied by the November FY sentence and 9M actuals.

Interpreter: py -3.13.  Run from the repo root:
    py -3.13 analysis/src/margin_build/M3_guide_policy_margin/run.py
"""
from __future__ import annotations

import datetime as dt
import sys
from pathlib import Path

import numpy as np
import pandas as pd

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[3]
sys.path.insert(0, str(REPO / "analysis" / "src" / "margin_build" / "10_harness_margin"))

from harness_margin import (  # noqa: E402
    Q, W, TODAY, GUIDE_DATES_ALL, GUIDE_DATES_W1, GUIDE_DATES_W2, GUIDE_DATE_LIVE,
    load_targets, history_as_of, series_as_of, load_guides, fy_guide_in_force, q_guide_in_force,
    fy_actual_margin_as_of, revenue_forecast_pit, seasonal_ebitda_shares, load_street,
    register, windows_for, QUANTILE_LEVELS, load_frozen_targets,
)

OUT = REPO / "data" / "processed" / "margin_build" / "M3_guide_policy_margin"
OUT.mkdir(parents=True, exist_ok=True)
FIG = REPO / "analysis" / "figures" / "margin_build"
FIG.mkdir(parents=True, exist_ok=True)

METHOD = "guide-policy-margin"
QCOLS = ["q05", "q10", "q25", "q50", "q75", "q90", "q95"]
_Z = dict(zip(QCOLS, [-1.6448536269514722, -1.2815515655446004, -0.6744897501960817, 0.0,
                      0.6744897501960817, 1.2815515655446004, 1.6448536269514722]))
HALF_LIFE_Q = 4.0
RESID_MAX_N, MIN_RESID = 12, 3
FALLBACK_PP, FALLBACK_REL = 3.0, 0.10
BUCKET = {2: "FEB", 5: "MAY", 8: "AUG", 11: "NOV"}
# Pre-registered cushion specs (the note's pre-registration paragraph): rw_hl4 (main), equal, last,
# nocushion, rw_hl4_prorata.  Everything else was added after the first backtest run and is POST-HOC:
# rw_hl4_pin / nocushion_pin / last_pin (WS21 R05) and nov_sentence_pin (WS22, the R12 reconciliation).
# `oracle_` prefix = the actual revenue is fed in; a diagnostic, never a forecast (WS21 R03).
PRE_REGISTERED_SPECS = ["rw_hl4", "equal", "last", "nocushion", "rw_hl4_prorata"]
POST_HOC_SPECS = {"rw_hl4_pin": "post-hoc: specified after the first backtest run (WS21 R05)",
                  "nocushion_pin": "post-hoc: specified after the first backtest run (WS21 R05)",
                  "last_pin": "post-hoc: specified after the first backtest run (WS21 R05)",
                  "nov_sentence_pin": "post-hoc: added in the WS22 discussion round as the R12 fix"}
SPECS = ["rw_hl4", "equal", "last", "nocushion", "rw_hl4_prorata", "rw_hl4_pin",
         "oracle_rw_hl4_revknown", "nocushion_pin", "last_pin", "nov_sentence_pin"]
MAIN_SPEC = "rw_hl4"
VINTAGES = list(GUIDE_DATES_ALL) + [TODAY]

T = load_targets()
FT = load_frozen_targets()
ACT = T[T["has_actual"]].set_index("quarter")

# WS06 v2b revenue path (base / bear / bull) for the LIVE rows (M_common rule 6)
_v2b = pd.read_csv(REPO / "data" / "processed" / "margin_build" / "06_fy27_path_v2" /
                   "06_revenue_path_3q26_4q27_v2b.csv")
_rev = _v2b[_v2b["line"] == "revenue_musd"]
LIVE_REV = {sc: {Q.canon(r.quarter): float(r.value) for r in g.itertuples()}
            for sc, g in _rev.groupby("scenario")}
LIVE_QUARTERS = ["2026Q3", "2026Q4", "2027Q1", "2027Q2", "2027Q3", "2027Q4"]


# ------------------------------------------------------------------ helpers
def _d(x) -> dt.date:
    return pd.to_datetime(x).date()


def qi(q) -> int:
    return Q.to_index(Q.canon(q))


def print_date(q):
    r = T[T["quarter"] == Q.canon(q)]
    return _d(r["print_date"].iloc[0]) if len(r) and pd.notna(r["print_date"].iloc[0]) else None


def actual(q, col):
    q = Q.canon(q)
    if q in ACT.index and pd.notna(ACT.at[q, col]):
        return float(ACT.at[q, col])
    return np.nan


def fy_actual_margin(fy: int):
    qs = [f"{fy}Q{n}" for n in (1, 2, 3, 4)]
    if not all(q in ACT.index and pd.notna(ACT.at[q, "adj_ebitda_musd"]) for q in qs):
        return np.nan
    return 100.0 * sum(actual(q, "adj_ebitda_musd") for q in qs) / sum(actual(q, "revenue_musd") for q in qs)


def guide_is_numeric(g) -> bool:
    """A guide the market can read as a number: a stated % level, or a non-zero y/y-pts guide."""
    if g is None:
        return False
    if g["form"] == "level":
        return True
    return ("yoy_pts(+0.0)" not in g["form"]) and ("yoy_pts(-0.0)" not in g["form"])


def rev_guide_mid(q):
    r = FT[FT["quarter"] == Q.canon(q)]
    if len(r) == 0 or pd.isna(r["guide_mid"].iloc[0]):
        return np.nan, None
    gd = r["guide_date"].iloc[0]
    return float(r["guide_mid"].iloc[0]), (_d(gd) if pd.notna(gd) else None)


# ------------------------------------------------------------------ 1. cushion history
def build_cushion_history() -> pd.DataFrame:
    """(FY, bucket) -> realised FY margin minus the level of the guide in force at that bucket."""
    rows, seen = [], set()
    for vd in VINTAGES:
        fy = int(Q.quarter_of_date(vd)[:4])
        g = fy_guide_in_force(vd, fy, T)
        if g is None:
            continue
        b = BUCKET.get(_d(g["guide_date"]).month)
        if b is None:
            continue
        key = (fy, b, _d(g["guide_date"]))
        if key in seen:
            continue
        seen.add(key)
        a = fy_actual_margin(fy)
        rows.append({"fy": fy, "bucket": b, "guide_date": _d(g["guide_date"]),
                     "guide_type": g["guide_type"], "guide_level_pct": g["level_pct"],
                     "numeric": guide_is_numeric(g), "form": g["form"],
                     "fy_actual_margin_pct": a,
                     "cushion_pp": (a - g["level_pct"]) if np.isfinite(a) else np.nan,
                     "knowable_from": print_date(f"{fy}Q4"), "quote": str(g.get("quote", ""))[:120]})
    return pd.DataFrame(rows).sort_values(["bucket", "fy"]).reset_index(drop=True)


CUSH = build_cushion_history()


def cushion(vd, bucket: str, spec: str, prior_basis: str):
    """(cushion pp, n, label). PIT: only cushions whose FY printed on or before the vintage."""
    if spec.startswith("nocushion"):
        return 0.0, 0, "zero"
    if spec.startswith("nov_sentence"):
        # the November-sentence spec carries no estimated cushion: its only adjustment to the guide in
        # force is object 2's floor+50bp rule, applied inside fy_forecast (WS22 R12 fix).
        return 0.0, 0, "zero (nov_sentence rule)"
    h = CUSH[(CUSH["bucket"] == bucket) & CUSH["cushion_pp"].notna()].copy()
    if prior_basis == "PIT":
        h = h[h["knowable_from"].map(lambda x: x is not None and x <= _d(vd))]
    if len(h) == 0:
        return 0.0, 0, "empty->0"
    h = h.sort_values("guide_date")
    if spec.startswith("last"):
        return float(h["cushion_pp"].iloc[-1]), len(h), f"last FY{int(h['fy'].iloc[-1])}"
    if spec.startswith("equal"):
        return float(h["cushion_pp"].mean()), len(h), "equal"
    age_q = np.array([(_d(vd) - gd).days / 91.3125 for gd in h["guide_date"]])
    w = 0.5 ** (np.maximum(age_q, 0.0) / HALF_LIFE_Q)
    return float(np.sum(w * h["cushion_pp"]) / np.sum(w)), len(h), "rw_hl4"


# ------------------------------------------------------------------ 2. the forecast engine
def revenue_at(vd, q, prior_basis, spec, scenario="base"):
    q = Q.canon(q)
    if spec.endswith("revknown"):
        a = actual(q, "revenue_musd")
        if np.isfinite(a):
            return a, "actual"
    if _d(vd) == TODAY and q in LIVE_REV.get(scenario, {}):
        return LIVE_REV[scenario][q], f"ws06_v2b_{scenario}"
    v, leg = revenue_forecast_pit(vd, q, prior_basis)
    return float(v), leg


def allocate(vd, fy, target_margin_pct, spec, prior_basis, scenario="base"):
    """Split the FY EBITDA target over the remaining quarters. Returns (dict q -> (m, e, rev, leg), note)."""
    h = history_as_of(vd, None, T)
    fyq = [f"{fy}Q{n}" for n in (1, 2, 3, 4)]
    ytd = h[h["quarter"].isin(fyq)]
    ytd_rev, ytd_eb = float(ytd["revenue_musd"].sum()), float(ytd["adj_ebitda_musd"].sum())
    remaining = [q for q in fyq if q not in set(ytd["quarter"])]
    if not remaining:
        return {}, "fy complete"
    rev = {}
    for r in remaining:
        v, leg = revenue_at(vd, r, prior_basis, spec, scenario)
        if not np.isfinite(v):
            return {}, f"no revenue for {r}"
        rev[r] = (v, leg)
    fy_rev = ytd_rev + sum(v for v, _ in rev.values())
    rem_eb = target_margin_pct / 100.0 * fy_rev - ytd_eb

    if spec.endswith("prorata"):
        shares, lab = seasonal_ebitda_shares(vd if prior_basis == "PIT" else None, prior_basis, T)
        if shares is None:
            return {}, lab
        ssum = sum(shares[int(r[5])] for r in remaining)
        out = {}
        for r in remaining:
            e = rem_eb * shares[int(r[5])] / ssum
            out[r] = (100.0 * e / rev[r][0], e, rev[r][0], rev[r][1])
        return out, f"prorata shares {lab}"

    base = {}
    for r in remaining:
        m4 = actual(Q.shift(r, -4), "adj_ebitda_margin_pct")
        if not np.isfinite(m4):
            return {}, f"no lagged margin for {r}"
        base[r] = m4
    free = list(remaining)
    fixed = {}
    note = "delta on m[q-4]"
    if spec.endswith("pin"):
        # the quarterly sentence is a direction constraint on the quarter it covers
        d0 = rem_eb - sum(base[r] / 100.0 * rev[r][0] for r in free)
        delta0 = 100.0 * d0 / sum(rev[r][0] for r in free)
        for r in list(free):
            g = q_guide_in_force(vd, r, T)
            if g is None or g.get("level_pct") is None:
                continue
            m_free, lvl, gt = base[r] + delta0, float(g["level_pct"]), g["guide_type"]
            m_new = (min(m_free, lvl) if gt == "ceiling" else
                     max(m_free, lvl) if gt == "floor" else lvl)
            if abs(m_new - m_free) > 1e-9:
                fixed[r] = m_new
                free.remove(r)
                note += f"; {r} pinned by {gt} sentence at {m_new:.2f}"
    rem_eb2 = rem_eb - sum(m / 100.0 * rev[r][0] for r, m in fixed.items())
    out = {r: (m, m / 100.0 * rev[r][0], rev[r][0], rev[r][1]) for r, m in fixed.items()}
    if free:
        num = rem_eb2 - sum(base[r] / 100.0 * rev[r][0] for r in free)
        delta = 100.0 * num / sum(rev[r][0] for r in free)
        for r in free:
            m = base[r] + delta
            out[r] = (m, m / 100.0 * rev[r][0], rev[r][0], rev[r][1])
        note += f"; delta {delta:+.2f}pp"
    return out, note


FEB_HAIRCUT_KIND = "pct_level"


def haircut_history() -> pd.DataFrame:
    """Realised February haircut: the February FY guide level minus the prior-FY actual margin."""
    rows = []
    for vd in VINTAGES:
        if _d(vd).month != 2:
            continue
        fy = int(Q.quarter_of_date(vd)[:4])
        g = fy_guide_in_force(vd, fy, T)
        if g is None or _d(g["guide_date"]) != _d(vd):
            continue
        prior = fy_actual_margin(fy - 1)
        rows.append({"fy": fy, "guide_date": _d(vd), "guide_level_pct": g["level_pct"],
                     "prior_fy_actual_pct": prior, "haircut_pp": g["level_pct"] - prior,
                     "kind": FEB_HAIRCUT_KIND if g["form"] == "level" else "qualitative_yoy",
                     "form": g["form"], "quote": str(g.get("quote", ""))[:120]})
    return pd.DataFrame(rows)


HC = haircut_history()


def feb_haircut_pit(vd):
    h = HC[(HC["guide_date"] < _d(vd)) & (HC["kind"] == FEB_HAIRCUT_KIND)]
    if len(h) == 0:
        return 0.0, 0
    return float(h["haircut_pp"].mean()), len(h)


def round50(x):
    return round(float(x) * 2.0) / 2.0


def fy_forecast(vd, fy, spec, prior_basis, scenario="base"):
    """FY margin forecast = guide in force + cushion. Returns dict or None."""
    g = fy_guide_in_force(vd, fy, T)
    if g is None:
        return None
    b = BUCKET.get(_d(g["guide_date"]).month)
    c, n_c, lab = cushion(vd, b, spec, prior_basis)
    if spec.startswith("nov_sentence"):
        # WS22 R12 fix. The quotable FY target is the sentence management is predicted to give, not the
        # floor plus a backward-looking cushion: object 2's November rule ("numeric floor in force ->
        # approximately floor + 50 bp", exact 2/2) when the guide in force is numeric, else the guide
        # taken literally. 0 estimated parameters; the +50 bp is a fixed rule, not a fitted cushion.
        if guide_is_numeric(g) and g["form"] == "level":
            lvl = round50(float(g["level_pct"]) + 0.5)
            c, lab = lvl - float(g["level_pct"]), "nov_sentence rule floor+50bp"
        else:
            c, lab = 0.0, "nov_sentence rule (no numeric floor -> literal guide)"
    return {"fy": fy, "guide_level_pct": g["level_pct"], "guide_type": g["guide_type"],
            "guide_date": _d(g["guide_date"]), "bucket": b, "cushion_pp": c, "cushion_n": n_c,
            "cushion_label": lab, "fy_margin_pct": g["level_pct"] + c, "numeric": guide_is_numeric(g),
            "form": g["form"]}


def policy_next_fy(vd, fy_hat_margin, spec, prior_basis):
    """No guide yet for FY+1: the policy chain -- February floor = FY_hat - haircut, then + FEB cushion."""
    hc, n_h = feb_haircut_pit(vd)
    c, n_c, lab = cushion(vd, "FEB", spec, prior_basis)
    return (fy_hat_margin + hc + c, hc, c,
            f"policy_chain(haircut {hc:+.2f} n{n_h}, cushion {c:+.2f} n{n_c} {lab})")


def forecast_quarters(vd, spec, prior_basis, hmax, scenario="base"):
    """({quarter: dict(margin, ebitda, revenue, note)}, fy_forecast_dict) for h = 0..hmax."""
    vd = _d(vd)
    q0 = Q.quarter_of_date(vd)
    fy0 = int(q0[:4])
    f0 = fy_forecast(vd, fy0, spec, prior_basis, scenario)
    if f0 is None:
        return {}, None
    alloc, note = allocate(vd, fy0, f0["fy_margin_pct"], spec, prior_basis, scenario)
    out = {}
    for q, (m, e, rev, leg) in alloc.items():
        out[q] = {"margin": m, "ebitda": e, "revenue": rev, "rev_leg": leg,
                  "note": (f"FY{fy0} {f0['guide_type']} {f0['guide_level_pct']:.2f}% + cushion "
                           f"{f0['cushion_pp']:+.2f}pp ({f0['cushion_label']}, n{f0['cushion_n']}, "
                           f"{f0['bucket']}) = {f0['fy_margin_pct']:.2f}%; {note}; rev[{leg}]")}
    want = [Q.shift(q0, h) for h in range(hmax + 1)]
    fy_hat = {fy0: f0["fy_margin_pct"]}
    later = sorted({int(q[:4]) for q in want if int(q[:4]) > fy0})
    for fy in later:
        for y in range(fy0 + 1, fy + 1):
            if y in fy_hat:
                continue
            g = fy_guide_in_force(vd, y, T)
            if g is not None:
                b = BUCKET.get(_d(g["guide_date"]).month)
                c, n_c, lab = cushion(vd, b, spec, prior_basis)
                fy_hat[y] = g["level_pct"] + c
            else:
                fy_hat[y] = policy_next_fy(vd, fy_hat[y - 1], spec, prior_basis)[0]
    for fy in later:
        qs = [f"{fy}Q{n}" for n in (1, 2, 3, 4)]
        revs, base, ok = {}, {}, True
        for r in qs:
            v, leg = revenue_at(vd, r, prior_basis, spec, scenario)
            lagq = Q.shift(r, -4)
            m4 = actual(lagq, "adj_ebitda_margin_pct")
            if not np.isfinite(m4) and lagq in out:
                m4 = out[lagq]["margin"]
            if not np.isfinite(v) or not np.isfinite(m4):
                ok = False
                break
            revs[r], base[r] = (v, leg), m4
        if not ok:
            continue
        fy_rev = sum(v for v, _ in revs.values())
        num = fy_hat[fy] / 100.0 * fy_rev - sum(base[r] / 100.0 * revs[r][0] for r in qs)
        delta = 100.0 * num / fy_rev
        for r in qs:
            m = base[r] + delta
            out[r] = {"margin": m, "ebitda": m / 100.0 * revs[r][0], "revenue": revs[r][0],
                      "rev_leg": revs[r][1],
                      "note": (f"FY{fy} policy chain {fy_hat[fy]:.2f}%; delta {delta:+.2f}pp on m[q-4]; "
                               f"rev[{revs[r][1]}]")}
    return {q: out[q] for q in want if q in out}, f0


# ------------------------------------------------------------------ 3. grid, quantiles, registry
def build_grid() -> pd.DataFrame:
    rows = []
    for vd in VINTAGES:
        vd = _d(vd)
        live = vd in (GUIDE_DATE_LIVE, TODAY)
        hmax = 5 if live else 2
        for spec in SPECS:
            for pb in ("PIT", "full_sample"):
                fc, f0 = forecast_quarters(vd, spec, pb, hmax)
                if f0 is None:
                    continue
                n_train = len(history_as_of(vd, "adj_ebitda_margin_pct", T))
                for q, d in fc.items():
                    h = qi(q) - qi(Q.quarter_of_date(vd))
                    for tgt, pt in (("adj_ebitda_margin_pct", d["margin"]),
                                    ("adj_ebitda_musd", d["ebitda"])):
                        rows.append({"object": "actual_given_guide", "spec_id": spec, "target": tgt,
                                     "quarter": q, "vintage_date": vd, "horizon_q": h,
                                     "prior_basis": pb, "point": float(pt), "n_train": n_train,
                                     "fy_margin_hat": f0["fy_margin_pct"],
                                     "cushion_pp": f0["cushion_pp"], "cushion_n": f0["cushion_n"],
                                     "notes": d["note"][:300]})
    g = pd.DataFrame(rows)
    g["actual"] = [actual(q, t) for q, t in zip(g["quarter"], g["target"])]
    g["target_print_date"] = g["quarter"].map(print_date)
    g["err"] = g["point"] - g["actual"]
    with np.errstate(divide="ignore", invalid="ignore"):
        g["rel_err"] = g["actual"] / g["point"] - 1.0
    return g


def attach_quantiles(g: pd.DataFrame) -> pd.DataFrame:
    g = g.copy()
    for c in QCOLS + ["sd", "sigma_n"]:
        g[c] = np.nan
    g["sigma_kind"] = ""
    key = ["object", "spec_id", "target", "horizon_q"]
    pools = {}
    for k, grp in g.groupby(key):
        rel = k[2] == "adj_ebitda_musd"
        p = grp[(grp["prior_basis"] == "PIT") & grp["actual"].notna() & grp["target_print_date"].notna()]
        if rel:
            p = p[(p["point"] > 0) & (p["actual"] > 0)]
        p = p.sort_values("quarter")
        pools[k] = ((p["rel_err"] if rel else p["err"]).to_numpy(dtype=float),
                    p["target_print_date"].to_numpy())
    for k, grp in g.groupby(key):
        rel = k[2] == "adj_ebitda_musd"
        errs, pdates = pools[k]
        borrowed = ""
        if len(errs) < MIN_RESID:
            for hb in range(int(k[3]) - 1, -1, -1):
                e2, p2 = pools.get((k[0], k[1], k[2], hb), (np.array([]), np.array([])))
                if len(e2) >= MIN_RESID:
                    errs, pdates, borrowed = e2, p2, f"_borrowed_h{hb}"
                    break
        full_sd = float(np.std(errs, ddof=1)) if len(errs) >= MIN_RESID else np.nan
        for i in grp.index:
            vd, pb, pt = g.at[i, "vintage_date"], g.at[i, "prior_basis"], float(g.at[i, "point"])
            if pb == "full_sample":
                sd, n = full_sd, len(errs)
            else:
                e = errs[np.array([d <= vd for d in pdates], dtype=bool)][-RESID_MAX_N:] \
                    if len(errs) else np.array([])
                sd, n = (float(np.std(e, ddof=1)) if len(e) >= MIN_RESID else np.nan), len(e)
            kind = ("relative" if rel else "additive") + borrowed
            if not np.isfinite(sd) or sd <= 0:
                sd, kind = (FALLBACK_REL if rel else FALLBACK_PP), kind + "_fallback"
            for c in QCOLS:
                g.at[i, c] = pt * (1.0 + _Z[c] * sd) if rel else pt + _Z[c] * sd
            g.at[i, "sd"] = abs(pt) * sd if rel else sd
            g.at[i, "sigma_n"] = n
            g.at[i, "sigma_kind"] = kind
    qm = g[QCOLS].to_numpy(dtype=float)
    qm.sort(axis=1)
    g[QCOLS] = qm
    return g


N_PARAMS = {"rw_hl4": 1, "equal": 1, "last": 0, "nocushion": 0, "rw_hl4_prorata": 4,
            "rw_hl4_pin": 1, "oracle_rw_hl4_revknown": 1, "nocushion_pin": 0, "last_pin": 0,
            "nov_sentence_pin": 0}

ORACLE_STAMP = ("ORACLE DIAGNOSTIC (actual revenue fed in at the vintage; NOT a point-in-time forecast; "
                "exclude from survivor and ranking tables -- WS21 R03). ")
# WS21 R12: the registered rw_hl4_pin LIVE path puts 4Q26 above every historical Q4 because the AUG-bucket
# cushion (+1.53pp) that M3's own FY backtest rejects (P2) is pushed into the residual quarter.
R12_STAMP = ("NOT QUOTABLE AS A LIVE FORECAST (WS21 R12): the AUG-bucket cushion in this spec is the one "
             "M3's own FY backtest rejects; use spec nov_sentence_pin for the LIVE path. ")


def _spec_stamp(spec_id: str, window: str) -> str:
    s = ORACLE_STAMP if str(spec_id).startswith("oracle_") else ""
    if str(spec_id) in POST_HOC_SPECS:
        s += POST_HOC_SPECS[str(spec_id)] + ". "
    if window == "LIVE" and str(spec_id) in ("rw_hl4_pin", "rw_hl4", "equal"):
        s += R12_STAMP
    return s


def registry_frame(g: pd.DataFrame, obj: str) -> pd.DataFrame:
    rows = []
    for r in g[g["object"] == obj].itertuples():
        for win in windows_for(r.vintage_date, r.quarter):
            row = {"method": METHOD, "object": obj, "target": r.target, "quarter": r.quarter,
                   "vintage_date": r.vintage_date, "horizon_q": int(r.horizon_q),
                   "point": float(r.point), "window": win, "prior_basis": r.prior_basis,
                   "n_params": (N_PARAMS.get(r.spec_id, 1)
                                + (0 if str(r.sigma_kind).endswith("fallback") else 1)
                                + (1 if r.target == "adj_ebitda_musd" else 0)),
                   "n_train": int(r.n_train), "sd": float(r.sd), "spec_id": r.spec_id,
                   "notes": (_spec_stamp(r.spec_id, win)
                             + f"{r.notes}; sigma {r.sigma_kind} n={int(r.sigma_n)}")[:700]}
            for c in QCOLS:
                row[c] = float(getattr(r, c))
            rows.append(row)
    return pd.DataFrame(rows)


# ------------------------------------------------------------------ 4. object 2: guide_forecast
def november_rule(vd):
    """Predict the FY margin sentence that the November letter of `vd` will carry."""
    vd = _d(vd)
    fy = int(Q.quarter_of_date(vd)[:4])
    prev = fy_guide_in_force(vd - dt.timedelta(days=1), fy, T)   # in force BEFORE the print
    fy_prev_hint = None
    if guide_is_numeric(prev) and prev["form"] == "level":
        lvl = round50(prev["level_pct"] + 0.5)
        return {"type": "point", "level_pct": lvl, "counterfactual_level_pct": lvl,
                "rule": "1 floor+50bp",
                "detail": f"floor {prev['level_pct']:.2f} in force since {prev['guide_date']}"}
    prev_nov = None
    for v in VINTAGES:
        if _d(v).month == 11 and _d(v) < vd:
            gg = fy_guide_in_force(_d(v), int(Q.quarter_of_date(v)[:4]), T)
            if gg is not None and _d(gg["guide_date"]) == _d(v) and guide_is_numeric(gg):
                prev_nov = _d(v)
    h = history_as_of(vd, None, T)
    fyq = [f"{fy}Q{n}" for n in (1, 2, 3, 4)]
    ytd = h[h["quarter"].isin(fyq)]
    q4 = f"{fy}Q4"
    rev4, gd4 = rev_guide_mid(q4)
    if gd4 is not None and gd4 > vd:
        rev4 = np.nan
    m4 = actual(Q.shift(q4, -4), "adj_ebitda_margin_pct")
    lvl2 = np.nan
    if len(ytd) == 3 and np.isfinite(rev4) and np.isfinite(m4):
        eb = float(ytd["adj_ebitda_musd"].sum()) + m4 / 100.0 * rev4
        lvl2 = round50(100.0 * eb / (float(ytd["revenue_musd"].sum()) + rev4))
    if prev_nov is not None:
        return {"type": "point", "level_pct": lvl2, "counterfactual_level_pct": lvl2,
                "rule": "2 implied FY, round 50bp", "detail": f"prior November {prev_nov} gave a number"}
    return {"type": "none", "level_pct": np.nan, "counterfactual_level_pct": lvl2,
            "rule": "3 no numeric anchor",
            "detail": "counterfactual level (rule 2) = " + (f"{lvl2:.2f}" if np.isfinite(lvl2) else "n/a")}


def november_actual(vd):
    """What the November letter actually said about the FY margin."""
    vd = _d(vd)
    fy = int(Q.quarter_of_date(vd)[:4])
    g = load_guides()
    rows = g[g["is_fy"] & (g["fy"].astype(int) == fy) & (g["guide_date"] == vd)]
    if len(rows) == 0:
        return {"type": "none", "level_pct": np.nan, "quote": ""}
    gg = fy_guide_in_force(vd, fy, T)
    return {"type": "point" if gg["guide_type"] == "point" else gg["guide_type"],
            "level_pct": gg["level_pct"], "quote": str(rows["quote"].iloc[0])[:140]}


def february_rule(vd):
    vd = _d(vd)
    fy = int(Q.quarter_of_date(vd)[:4])
    prior = fy_actual_margin_as_of(vd, fy - 1, T)
    if prior is None:
        return None
    prev_nov = fy_guide_in_force(vd - dt.timedelta(days=1), fy - 1, T)
    if guide_is_numeric(prev_nov):
        hc, n = feb_haircut_pit(vd)
        return {"level_pct": round50(prior + hc), "kind": "numeric floor", "haircut_pp": hc,
                "haircut_n": n, "prior_fy_actual_pct": prior}
    return {"level_pct": prior, "kind": "qualitative (prior-FY actual)", "haircut_pp": 0.0,
            "haircut_n": 0, "prior_fy_actual_pct": prior}


def build_guide_forecast():
    nov_rows, feb_rows = [], []
    for vd in VINTAGES:
        vd = _d(vd)
        if vd.month == 11:
            p, a = november_rule(vd), november_actual(vd)
            lvl = p["counterfactual_level_pct"]
            nov_rows.append({
                "vintage_date": vd, "fy": int(Q.quarter_of_date(vd)[:4]),
                "pred_type": p["type"], "pred_level_pct": p["level_pct"],
                "pred_level_incl_counterfactual": lvl, "rule": p["rule"], "detail": p["detail"],
                "actual_type": a["type"], "actual_level_pct": a["level_pct"],
                "type_hit": int(p["type"] == a["type"]),
                "level_err_pp": ((lvl - a["level_pct"]) if np.isfinite(lvl) and np.isfinite(a["level_pct"])
                                 else np.nan),
                "level_err_pp_rule_only": ((p["level_pct"] - a["level_pct"])
                                           if np.isfinite(p["level_pct"]) and np.isfinite(a["level_pct"])
                                           else np.nan),
                "actual_quote": a["quote"]})
        if vd.month == 2:
            p = february_rule(vd)
            fy = int(Q.quarter_of_date(vd)[:4])
            g = fy_guide_in_force(vd, fy, T)
            if p is None or g is None or _d(g["guide_date"]) != vd:
                continue
            feb_rows.append({"vintage_date": vd, "fy": fy, "pred_level_pct": p["level_pct"],
                             "kind": p["kind"], "haircut_pp": p["haircut_pp"],
                             "haircut_n": p["haircut_n"], "prior_fy_actual_pct": p["prior_fy_actual_pct"],
                             "actual_level_pct": g["level_pct"], "actual_form": g["form"],
                             "err_pp": p["level_pct"] - g["level_pct"],
                             "actual_quote": str(g.get("quote", ""))[:140]})
    return pd.DataFrame(nov_rows), pd.DataFrame(feb_rows)


# ------------------------------------------------------------------ 5. object 3: q4_implied
def q4_implied_row(vd, fy, level_pct, rev4_source="guide_mid", scenario="base", q3_margin_pct=None):
    """Q4 margin implied by an FY margin sentence, 9M actuals and the Q4 revenue.
    `q3_margin_pct`: at a vintage where Q3 has not printed (the LIVE case), the assumed Q3 margin;
    Q3 revenue then comes from the same source as Q4."""
    vd = _d(vd)
    h = history_as_of(vd, None, T)
    fyq = [f"{fy}Q{n}" for n in (1, 2, 3, 4)]
    ytd = h[h["quarter"].isin(fyq)]
    q4 = f"{fy}Q4"
    q3_add_rev = q3_add_eb = 0.0
    if len(ytd) == 2 and q3_margin_pct is not None:
        q3 = f"{fy}Q3"
        r3 = (LIVE_REV.get(scenario, {}).get(q3, np.nan) if rev4_source == "ws06_v2b"
              else rev_guide_mid(q3)[0])
        if not np.isfinite(r3):
            return None
        q3_add_rev, q3_add_eb = r3, q3_margin_pct / 100.0 * r3
    if rev4_source == "guide_mid":
        rev4, gd = rev_guide_mid(q4)
        if gd is not None and gd > vd:
            rev4 = np.nan
    elif rev4_source == "ws06_v2b":
        rev4 = LIVE_REV.get(scenario, {}).get(q4, np.nan)
    else:
        rev4, _ = revenue_forecast_pit(vd, q4, "PIT")
    if (len(ytd) + (1 if q3_add_rev else 0)) < 3 or not np.isfinite(rev4) or not np.isfinite(level_pct):
        return None
    ytd_rev = float(ytd["revenue_musd"].sum()) + q3_add_rev
    ytd_eb = float(ytd["adj_ebitda_musd"].sum()) + q3_add_eb
    eb4 = level_pct / 100.0 * (ytd_rev + rev4) - ytd_eb
    return {"quarter": q4, "ytd_rev": ytd_rev, "ytd_ebitda": ytd_eb,
            "q3_margin_assumed_pct": q3_margin_pct if q3_add_rev else np.nan,
            "ytd_margin_pct": 100 * ytd_eb / ytd_rev, "fy_sentence_level_pct": level_pct,
            "rev4": rev4, "rev4_source": rev4_source,
            "q4_margin_implied_pct": 100.0 * eb4 / rev4, "q4_ebitda_implied_musd": eb4}


def build_q4_implied():
    rows = []
    st = load_street()
    for vd in VINTAGES:
        vd = _d(vd)
        if vd.month != 11:
            continue
        fy = int(Q.quarter_of_date(vd)[:4])
        g = fy_guide_in_force(vd, fy, T)
        if g is None or _d(g["guide_date"]) != vd:
            continue                       # no FY sentence issued in that November
        for src in ("guide_mid", "cushion"):
            r = q4_implied_row(vd, fy, g["level_pct"], src)
            if r is None:
                continue
            q4 = r["quarter"]
            s = st[(st["vintage_date"] == vd) & (st["quarter"] == q4) &
                   (st["target"] == "adj_ebitda_margin_pct")] if len(st) else st
            sn = actual(Q.shift(q4, -4), "adj_ebitda_margin_pct")
            rows.append({"vintage_date": vd, "fy": fy, **r,
                         "q4_margin_actual_pct": actual(q4, "adj_ebitda_margin_pct"),
                         "q4_ebitda_actual_musd": actual(q4, "adj_ebitda_musd"),
                         "street_q4_margin_pct": float(s["value"].iloc[0]) if len(s) else np.nan,
                         "seasonal_naive_q4_margin_pct": sn,
                         "guide_quote": str(g.get("quote", ""))[:140]})
    return pd.DataFrame(rows)


# ------------------------------------------------------------------ 6. "slightly" test (for M2)
def slightly_test():
    g = load_guides()
    q = g[(~g["is_fy"]) & (g["metric"] == "adj_ebitda_margin_yoy_pts")].copy()
    rows = []
    for r in q.itertuples():
        tq = r.target_period
        a, b = actual(tq, "adj_ebitda_margin_pct"), actual(Q.shift(tq, -4), "adj_ebitda_margin_pct")
        ql = str(r.quote).lower()
        rows.append({"guide_date": r.guide_date, "quarter": tq, "guide_type": r.guide_type,
                     "adverb": "slightly" if "slight" in ql else ("modest" if "modest" in ql else "plain"),
                     "direction": {"ceiling": -1, "floor": 1, "point": 0}[r.guide_type],
                     "realised_yoy_pp": (a - b) if np.isfinite(a) and np.isfinite(b) else np.nan,
                     "quote": str(r.quote)[:120]})
    return pd.DataFrame(rows)


# ------------------------------------------------------------------ main
def main():
    print(f"M3 guidance-policy margin  |  {len(VINTAGES)} vintages, {len(SPECS)} specs")
    CUSH.to_csv(OUT / "M3_cushion_history.csv", index=False)
    HC.to_csv(OUT / "M3_february_haircut_history.csv", index=False)
    print("\ncushion history by bucket:")
    print(CUSH[CUSH["cushion_pp"].notna()].groupby("bucket")["cushion_pp"]
          .agg(["count", "mean", "min", "max"]).round(2).to_string())

    g = attach_quantiles(build_grid())
    g.to_csv(OUT / "M3_grid_all_vintages.csv", index=False)
    print(f"\ngrid: {len(g)} rows")

    frame = registry_frame(g, "actual_given_guide")
    register(frame)

    # ---- FY annual forecasts (not scored by the harness)
    ann = []
    for vd in VINTAGES:
        vd = _d(vd)
        fy0 = int(Q.quarter_of_date(vd)[:4])
        for spec in SPECS:
            for pb in ("PIT", "full_sample"):
                f0 = fy_forecast(vd, fy0, spec, pb)
                if f0 is None:
                    continue
                ann.append({"vintage_date": vd, "spec_id": spec, "prior_basis": pb, "fy": fy0,
                            **{k: f0[k] for k in ("guide_level_pct", "guide_type", "guide_date",
                                                  "bucket", "cushion_pp", "cushion_n",
                                                  "cushion_label", "fy_margin_pct")},
                            "fy_actual_margin_pct": fy_actual_margin(fy0),
                            "err_pp": f0["fy_margin_pct"] - fy_actual_margin(fy0)})
                if vd == TODAY:
                    m27, hc, c, note = policy_next_fy(vd, f0["fy_margin_pct"], spec, pb)
                    m28 = policy_next_fy(vd, m27, spec, pb)[0]
                    for fy, m in ((2027, m27), (2028, m28)):
                        ann.append({"vintage_date": vd, "spec_id": spec, "prior_basis": pb, "fy": fy,
                                    "guide_level_pct": np.nan, "guide_type": "none (policy chain)",
                                    "guide_date": None, "bucket": "FEB", "cushion_pp": c,
                                    "cushion_n": np.nan, "cushion_label": note, "fy_margin_pct": m,
                                    "fy_actual_margin_pct": np.nan, "err_pp": np.nan})
    annual = pd.DataFrame(ann)
    annual.to_csv(OUT / "M3_guide_policy_margin_annual_forecasts.csv", index=False)
    print("\nFY backtest (PIT), err_pp by spec:")
    bt = annual[(annual["prior_basis"] == "PIT") & annual["err_pp"].notna()]
    print(bt.pivot_table(index=["fy", "bucket"], columns="spec_id", values="err_pp").round(2).to_string())

    # ---- LIVE quarterly table, three revenue scenarios
    live = []
    for scen in ("base", "bear", "bull"):
        for spec in SPECS:
            fc, f0 = forecast_quarters(TODAY, spec, "PIT", 5, scen)
            for q, d in fc.items():
                live.append({"vintage_date": TODAY, "scenario": scen, "spec_id": spec, "quarter": q,
                             "revenue_musd": d["revenue"], "rev_source": d["rev_leg"],
                             "adj_ebitda_margin_pct": d["margin"], "adj_ebitda_musd": d["ebitda"],
                             "fy_margin_hat_pct": f0["fy_margin_pct"], "note": d["note"][:300]})
    livedf = pd.DataFrame(live)
    livedf.to_csv(OUT / "M3_live_forecasts.csv", index=False)
    print("\nLIVE margin % (base revenue path, PIT):")
    print(livedf[livedf.scenario == "base"].pivot_table(index="quarter", columns="spec_id",
          values="adj_ebitda_margin_pct").round(2).to_string())

    # ---- object 2
    nov, feb = build_guide_forecast()
    nov.to_csv(OUT / "M3_guide_forecast_november_backtest.csv", index=False)
    feb.to_csv(OUT / "M3_guide_forecast_february_backtest.csv", index=False)
    print("\nNovember rule:")
    print(nov[["vintage_date", "pred_type", "pred_level_incl_counterfactual", "actual_type",
               "actual_level_pct", "type_hit", "level_err_pp"]].to_string(index=False))
    print(f"type hit {nov['type_hit'].sum()}/{len(nov)}; level MAE (incl counterfactual) "
          f"{nov['level_err_pp'].abs().mean():.3f} pp (n {nov['level_err_pp'].notna().sum()}); "
          f"rule-only {nov['level_err_pp_rule_only'].abs().mean():.3f} pp "
          f"(n {nov['level_err_pp_rule_only'].notna().sum()})")
    print("\nFebruary rule:")
    print(feb[["vintage_date", "pred_level_pct", "actual_level_pct", "err_pp", "kind"]]
          .to_string(index=False))
    print(f"level MAE {feb['err_pp'].abs().mean():.3f} pp (n {len(feb)})")

    # ---- object 3
    q4 = build_q4_implied()
    q4.to_csv(OUT / "M3_q4_implied_backtest.csv", index=False)
    print("\nq4_implied:")
    if len(q4):
        print(q4[["vintage_date", "rev4_source", "fy_sentence_level_pct", "q4_margin_implied_pct",
                  "q4_margin_actual_pct", "street_q4_margin_pct", "seasonal_naive_q4_margin_pct"]]
              .round(2).to_string(index=False))

    rows = []
    for r in q4[q4["rev4_source"] == "guide_mid"].itertuples():
        for tgt, pt in (("adj_ebitda_margin_pct", r.q4_margin_implied_pct),
                        ("adj_ebitda_musd", r.q4_ebitda_implied_musd)):
            rows.append({"object": "q4_implied", "spec_id": "guide_mid", "target": tgt,
                         "quarter": r.quarter, "vintage_date": r.vintage_date, "horizon_q": 0,
                         "prior_basis": "PIT", "point": float(pt),
                         "n_train": len(history_as_of(r.vintage_date, "adj_ebitda_margin_pct", T)),
                         "notes": (f"FY sentence {r.fy_sentence_level_pct:.2f}% over 9M actual "
                                   f"({r.ytd_margin_pct:.2f}%) and Q4 revenue guide mid {r.rev4:.0f}")})
    q4g = pd.DataFrame(rows)
    if len(q4g):
        q4g["actual"] = [actual(q, t) for q, t in zip(q4g["quarter"], q4g["target"])]
        q4g["target_print_date"] = q4g["quarter"].map(print_date)
        q4g["err"] = q4g["point"] - q4g["actual"]
        q4g["rel_err"] = q4g["actual"] / q4g["point"] - 1.0
        q4g = pd.concat([q4g, q4g.assign(prior_basis="full_sample")], ignore_index=True)
        q4g = attach_quantiles(q4g)
        fr = registry_frame(q4g, "q4_implied")
        if len(fr):
            fr["n_params"] = (fr["n_params"] - 1).clip(lower=0)
            register(fr)

    nov26 = november_rule(dt.date(2026, 11, 5))
    live_q4 = []
    for lvl, lab in ((nov26["level_pct"], "predicted: approximately 36.0%"), (35.5, "floor held 35.5%"),
                     (36.5, "bull: approximately 36.5%")):
        for scen in ("base", "bear", "bull"):
            for q3m in (49.0, 49.5, 50.1):
                r = q4_implied_row(TODAY, 2026, lvl, "ws06_v2b", scen, q3_margin_pct=q3m)
                if r:
                    live_q4.append({"scenario": scen, "sentence": lab, "level_pct": lvl, **r})
    lq = pd.DataFrame(live_q4)
    lq.to_csv(OUT / "M3_q4_implied_live_5nov.csv", index=False)
    print("\n5 Nov 2026 sentence rule ->", nov26)
    if len(lq):
        print(lq[lq.scenario == "base"][["sentence", "q3_margin_assumed_pct", "ytd_margin_pct",
                                        "rev4", "q4_margin_implied_pct", "q4_ebitda_implied_musd"]]
              .round(2).to_string(index=False))

    sl = slightly_test()
    sl.to_csv(OUT / "M3_slightly_magnitude.csv", index=False)
    print("\n'slightly' test:")
    print(sl.groupby("adverb")["realised_yoy_pp"].agg(["count", "mean", "min", "max"]).round(2).to_string())

    try:                                    # figures need matplotlib and the current scoreboard
        import runpy
        runpy.run_path(str(HERE / "make_figures.py"), run_name="__main__")
    except Exception as e:                  # pragma: no cover
        print(f"figures skipped: {e}")
    print("\nDONE")


if __name__ == "__main__":
    main()
