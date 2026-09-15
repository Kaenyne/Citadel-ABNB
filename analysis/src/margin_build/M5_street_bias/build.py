"""M5 — street-bias: the Street's adjusted-EBITDA consensus at the vintage plus its systematic bias.

Three objects (see docs/margin-build/notes/M5_street_bias.md for the pre-registration):

  street_plus_bias        EBITDA_q = Street_q(vintage) + b(vintage, h)
                          b = shrunk, recency-weighted mean (or median) of PIT-knowable surprises
                          at the SAME horizon, pool starting 2022Q1.
  street_plus_flowthrough EBITDA_q = Street_q + a + m * (Rev_team_q - Rev_Street_q)
                          a, m from a PIT weighted OLS of the $ EBITDA surprise on the $ revenue
                          surprise; m shrunk to the prior m0 = 0.45, a shrunk to zero.
                          Margin = EBITDA / Rev_team.
  dispersion_conditioned  street_plus_bias with b and sigma scaled by
                          clip(disp(v,h) / disp_ref(v,h), 0.5, 2.0), disp = ebitda_sd / ebitda_mean.

Street exists at h = 0 (the quarter being guided) and h = 1 only (WS03 roles guided_q_pre_guide /
next_q_pre_guide), so the backtest is h = 0 and h = 1. LIVE 1Q27-4Q27 uses a Street quarterly path
allocated from the FY27 consensus with the harness PIT seasonal shares (spec suffix `_fyalloc`).

Interpreter: py -3.13.  Run: py -3.13 analysis/src/margin_build/M5_street_bias/build.py
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[3]
sys.path.insert(0, str(REPO / "analysis" / "src" / "margin_build" / "10_harness_margin"))

from harness_margin import (  # noqa: E402
    Q, W, TODAY, GUIDE_DATES_W1, GUIDE_DATE_LIVE, load_targets, history_as_of, load_street,
    register, windows_for, revenue_forecast_pit, fy_guide_in_force,
)

OUT = REPO / "data" / "processed" / "margin_build" / "M5_street_bias"
OUT.mkdir(parents=True, exist_ok=True)
WS03 = REPO / "data" / "processed" / "margin_build" / "03_consensus_pit"
WS06 = REPO / "data" / "processed" / "margin_build" / "06_fy27_path_v2" / "06_revenue_path_3q26_4q27_v2b.csv"

METHOD = "street-bias"
EBITDA, MARGIN, REVENUE = "adj_ebitda_musd", "adj_ebitda_margin_pct", "revenue_musd"

# ---- pre-registered constants (data/processed/margin_build/M5_street_bias/M5_prereg.json)
HALF_LIFE = 4.0
KAPPA_B = 2.0
M0 = 0.45
KAPPA_M = 4.0
DISP_CAP = (0.5, 2.0)
POOL_FIRST_Q = "2022Q1"
POOL_FIRST_Q_ALT = "2021Q1"
RESID_MAX_N, MIN_RESID = 12, 3
FALLBACK_REL, FALLBACK_PP = 0.10, 3.0

QCOLS = ["q05", "q10", "q25", "q50", "q75", "q90", "q95"]
Z = dict(zip(QCOLS, [-1.6448536269514722, -1.2815515655446004, -0.6744897501960817, 0.0,
                     0.6744897501960817, 1.2815515655446004, 1.6448536269514722]))

SPECS = {  # spec_id -> (weighting, estimator, dollar_bias_mode, pool_first_q)
    "rw_hl4":        ("rw", "mean",   "pct", POOL_FIRST_Q),
    "ew":            ("ew", "mean",   "pct", POOL_FIRST_Q),
    "rw_hl4_usd":    ("rw", "mean",   "usd", POOL_FIRST_Q),
    "ew_usd":        ("ew", "mean",   "usd", POOL_FIRST_Q),
    "rw_hl4_med":    ("rw", "median", "pct", POOL_FIRST_Q),
    "rw_hl4_from21": ("rw", "mean",   "pct", POOL_FIRST_Q_ALT),
}
N_PARAMS = {"street_plus_bias": 2, "street_plus_flowthrough": 5, "dispersion_conditioned": 4}


# ------------------------------------------------------------------ data
def load_panels():
    t = load_targets()
    act = {}
    for m in (EBITDA, MARGIN, REVENUE):
        act[m] = {r.quarter: getattr(r, m) for r in t.itertuples()
                  if r.has_actual and pd.notna(getattr(r, m))}
    pdm = {r.quarter: r.print_date for r in t.itertuples() if pd.notna(r.print_date)}
    s = load_street()
    s = s[s["target"].isin([EBITDA, MARGIN, REVENUE])].copy()
    wide = s.pivot_table(index=["vintage_date", "quarter", "horizon_q"], columns="target",
                         values="value").reset_index()
    meta = (s[s["target"] == EBITDA][["vintage_date", "quarter", "horizon_q", "as_of", "n_est", "role"]]
            .drop_duplicates())
    wide = wide.merge(meta, on=["vintage_date", "quarter", "horizon_q"], how="left")
    wide["print_date"] = wide["quarter"].map(pdm)
    for m in (EBITDA, MARGIN, REVENUE):
        wide["act_" + m] = wide["quarter"].map(act[m])
    return t, wide, pdm, act


def load_dispersion():
    """disp = ebitda_sd / ebitda_mean at each vintage, by horizon."""
    d = pd.read_csv(WS03 / "03_consensus_at_dates.csv")
    d = d[d["found"].astype(str).str.lower() == "true"]
    role_h = {"guided_q_pre_guide": 0, "next_q_pre_guide": 1, "current_q": 0, "current_next_q": 1}
    rows = []
    for r in d.itertuples():
        if r.target_role not in role_h:
            continue
        vd = TODAY if r.target_role.startswith("current") else pd.to_datetime(r.date).date()
        if not (pd.notna(r.ebitda_sd) and pd.notna(r.ebitda_mean)) or r.ebitda_mean <= 0:
            continue
        rows.append(dict(vintage_date=vd, horizon_q=role_h[r.target_role],
                         disp=float(r.ebitda_sd) / float(r.ebitda_mean), n_est=r.ebitda_n))
    return pd.DataFrame(rows).drop_duplicates(subset=["vintage_date", "horizon_q"])


# ------------------------------------------------------------------ weights / estimators
def _w(quarters, weighting):
    idx = np.array([Q.to_index(q) for q in quarters], dtype=float)
    if weighting == "ew":
        return np.ones_like(idx)
    return 0.5 ** ((idx.max() - idx) / HALF_LIFE)


def _wmean(x, w):
    return float(np.sum(w * x) / np.sum(w))


def _wmedian(x, w):
    o = np.argsort(x)
    x, w = np.asarray(x)[o], np.asarray(w)[o]
    c = np.cumsum(w) / np.sum(w)
    return float(x[np.searchsorted(c, 0.5)])


def shrunk(x, w, estimator):
    """Shrink toward zero with KAPPA_B effective observations of prior mass at 0."""
    n_eff = float(np.sum(w))
    raw = _wmean(x, w) if estimator == "mean" else _wmedian(x, w)
    return raw * n_eff / (n_eff + KAPPA_B), raw, n_eff, len(x)


def wls2(y, x, w):
    """Weighted OLS y = a + m x. Returns (a, m)."""
    X = np.column_stack([np.ones_like(x), x])
    sw = np.sqrt(w)
    beta, *_ = np.linalg.lstsq(X * sw[:, None], y * sw, rcond=None)
    return float(beta[0]), float(beta[1])


# ------------------------------------------------------------------ the model at one vintage
def surprise_pool(wide, vintage, h, first_q):
    """Surprises knowable at `vintage`: the target quarter must have printed on or before it."""
    p = wide[(wide["horizon_q"] == h) & wide["print_date"].notna() &
             wide["act_" + EBITDA].notna() & (wide["quarter"] >= first_q)].copy()
    p = p[p["print_date"] <= vintage]
    p = p[p["vintage_date"] < vintage]
    p["s_usd"] = p["act_" + EBITDA] - p[EBITDA]
    p["s_pt"] = p["act_" + MARGIN] - p[MARGIN]
    p["s_pct"] = np.where(p[EBITDA] > 0, p["act_" + EBITDA] / p[EBITDA] - 1.0, np.nan)
    p["rev_surp_usd"] = p["act_" + REVENUE] - p[REVENUE]
    return p.sort_values("quarter")


def bias_at(wide, vintage, h, spec):
    weighting, estimator, _dollar, first_q = SPECS[spec]
    p = surprise_pool(wide, vintage, h, first_q)
    out = dict(n_pool=len(p))
    if len(p) == 0:
        return dict(out, b_pt=0.0, b_pct=0.0, b_usd=0.0, n_eff=0.0)
    w = _w(p["quarter"].tolist(), weighting)
    b_pt, raw_pt, n_eff, _ = shrunk(p["s_pt"].to_numpy(float), w, estimator)
    b_usd, raw_usd, _, _ = shrunk(p["s_usd"].to_numpy(float), w, estimator)
    m = p["s_pct"].notna().to_numpy()
    if m.sum() >= 1:
        b_pct, raw_pct, _, _ = shrunk(p["s_pct"].to_numpy(float)[m], w[m], estimator)
    else:
        b_pct, raw_pct = 0.0, np.nan
    return dict(out, b_pt=b_pt, b_pct=b_pct, b_usd=b_usd, n_eff=n_eff,
                raw_pt=raw_pt, raw_usd=raw_usd, raw_pct=raw_pct)


def flowthrough_at(wide, vintage, h, spec):
    weighting, estimator, _dollar, first_q = SPECS[spec]
    p = surprise_pool(wide, vintage, h, first_q)
    p = p[p["rev_surp_usd"].notna()]
    if len(p) < 4:
        b = bias_at(wide, vintage, h, spec)
        return dict(m=M0, a=b["b_usd"], m_hat=np.nan, n_pool=len(p), n_eff=b.get("n_eff", 0.0))
    w = _w(p["quarter"].tolist(), weighting)
    a_hat, m_hat = wls2(p["s_usd"].to_numpy(float), p["rev_surp_usd"].to_numpy(float), w)
    n_eff = float(np.sum(w))
    m = (n_eff * m_hat + KAPPA_M * M0) / (n_eff + KAPPA_M)
    resid = p["s_usd"].to_numpy(float) - m * p["rev_surp_usd"].to_numpy(float)
    a, raw_a, _, _ = shrunk(resid, w, estimator)
    return dict(m=m, a=a, m_hat=m_hat, a_raw=raw_a, n_pool=len(p), n_eff=n_eff)


def disp_ratio_at(disp, vintage, h, weighting="rw"):
    cur = disp[(disp["vintage_date"] == vintage) & (disp["horizon_q"] == h)]
    past = disp[(disp["vintage_date"] <= vintage) & (disp["horizon_q"] == h)]
    if len(cur) == 0 or len(past) < 3:
        return 1.0, np.nan, np.nan
    d0 = float(cur["disp"].iloc[0])
    idx = np.arange(len(past), dtype=float)
    w = np.ones(len(past)) if weighting == "ew" else 0.5 ** ((idx.max() - idx) / HALF_LIFE)
    ref = _wmean(past["disp"].to_numpy(float), w)
    r = float(np.clip(d0 / ref, *DISP_CAP)) if ref > 0 else 1.0
    return r, d0, ref


# ------------------------------------------------------------------ LIVE street extension
def live_street_fyalloc(t):
    """Street 1Q27-4Q27 EBITDA / revenue / margin from the FY27 consensus and PIT seasonal shares."""
    cur = pd.read_csv(WS03 / "03_current_consensus.csv")
    row = cur[cur["period"].astype(str).str.upper() == "FY27"]
    if len(row) == 0:
        return pd.DataFrame()
    fy_e = float(row["ebitda_mean"].iloc[0])
    fy_r = float(row["revenue_mean"].iloc[0])
    h = t[t["has_actual"]].copy()
    fys = [2023, 2024, 2025]
    e_sh, r_sh = {}, {}
    for k, col, store in ((EBITDA, EBITDA, e_sh), (REVENUE, REVENUE, r_sh)):
        tot = {}
        for y in fys:
            qs = [f"{y}Q{i}" for i in (1, 2, 3, 4)]
            v = h[h["quarter"].isin(qs)][col]
            tot[y] = v.sum() if len(v) == 4 else np.nan
        for i in (1, 2, 3, 4):
            vals = [float(h[h["quarter"] == f"{y}Q{i}"][col].iloc[0]) / tot[y] for y in fys
                    if np.isfinite(tot[y])]
            store[i] = float(np.mean(vals))
    rows = []
    for i in (1, 2, 3, 4):
        e = fy_e * e_sh[i] / sum(e_sh.values())
        r = fy_r * r_sh[i] / sum(r_sh.values())
        rows.append(dict(quarter=f"2027Q{i}", **{EBITDA: e, REVENUE: r, MARGIN: 100.0 * e / r}))
    out = pd.DataFrame(rows)
    out["e_share"] = [e_sh[i] / sum(e_sh.values()) for i in (1, 2, 3, 4)]
    out["r_share"] = [r_sh[i] / sum(r_sh.values()) for i in (1, 2, 3, 4)]
    return out


_WS06_CACHE = {}


def _ws06():
    if "d" not in _WS06_CACHE:
        _WS06_CACHE["d"] = pd.read_csv(WS06)
    return _WS06_CACHE["d"]


_REV_CACHE = {}


def team_revenue(vintage, quarter, scenario="base"):
    """LIVE: WS06 v2b path (bridge v3 for 3Q26/4Q26). Backtest: the harness PIT revenue leg."""
    if vintage in (GUIDE_DATE_LIVE, TODAY) and WS06.exists():
        r = _ws06()
        lab = f"{quarter[-1]}Q{quarter[2:4]}"                    # 2026Q3 -> 3Q26
        sel = r[(r["quarter"].str.upper() == lab) & (r["line"] == "revenue_musd") &
                (r["scenario"] == scenario)]
        if len(sel):
            return float(sel["value"].iloc[0]), f"WS06_v2b_{scenario}"
    k = (vintage, quarter)
    if k not in _REV_CACHE:
        try:
            v, leg = revenue_forecast_pit(vintage, quarter)
        except Exception:
            v, leg = np.nan, "unavailable"
        _REV_CACHE[k] = ((float(v) if v is not None and np.isfinite(v) else np.nan), leg)
    return _REV_CACHE[k]


# ------------------------------------------------------------------ build the grid
def build_grid():
    t, wide, pdm, act = load_panels()
    disp = load_dispersion()
    vintages = sorted(set(wide["vintage_date"]))
    live_street = live_street_fyalloc(t)
    rows, diag = [], []
    for vd in vintages:
        is_live = vd in (GUIDE_DATE_LIVE, TODAY)
        n_train = len(history_as_of(vd, EBITDA, t))
        hist = history_as_of(vd, None, t)
        kf = hist["print_date"].max() if len(hist) else None
        base = wide[wide["vintage_date"] == vd]
        street_rows = [(r.quarter, int(r.horizon_q), getattr(r, EBITDA), getattr(r, MARGIN),
                        getattr(r, REVENUE), r.as_of, "street_pit") for r in base.itertuples()]
        if is_live and vd == TODAY and len(live_street):
            for r in live_street.itertuples():
                h = Q.to_index(r.quarter) - Q.to_index(Q.quarter_of_date(vd))
                street_rows.append((r.quarter, h, getattr(r, EBITDA), getattr(r, MARGIN),
                                    getattr(r, REVENUE), vd, "fyalloc"))
        for spec in SPECS:
            for h in (0, 1):
                b = bias_at(wide, vd, h, spec)
                f = flowthrough_at(wide, vd, h, spec)
                dr, d0, dref = disp_ratio_at(disp, vd, h, SPECS[spec][0])
                diag.append(dict(vintage_date=vd, horizon_q=h, spec_id=spec, **b,
                                 m=f["m"], m_hat=f["m_hat"], a=f["a"], ft_n=f["n_pool"],
                                 disp=d0, disp_ref=dref, disp_ratio=dr))
            for (q, h, se, sm, sr, as_of, src) in street_rows:
                if not (np.isfinite(se) and np.isfinite(sm) and np.isfinite(sr)):
                    continue
                hb = min(h, 1)                      # h>=2 (fyalloc) borrows the h=1 bias
                b = bias_at(wide, vd, hb, spec)
                f = flowthrough_at(wide, vd, hb, spec)
                dr, d0, dref = disp_ratio_at(disp, vd, hb, SPECS[spec][0])
                dollar_mode = SPECS[spec][2]
                # --- object 1
                e1 = se * (1.0 + b["b_pct"]) if dollar_mode == "pct" else se + b["b_usd"]
                m1 = sm + b["b_pt"]
                # --- object 3
                e3 = se * (1.0 + b["b_pct"] * dr) if dollar_mode == "pct" else se + b["b_usd"] * dr
                m3 = sm + b["b_pt"] * dr
                # --- object 2
                scen_list = ["base", "bear", "bull"] if is_live else ["base"]
                for scen in scen_list:
                    rev_team, leg = team_revenue(vd, q, scen)
                    if not np.isfinite(rev_team):
                        rev_team, leg = sr, "street_revenue"
                    e2 = se + f["a"] + f["m"] * (rev_team - sr)
                    m2 = 100.0 * e2 / rev_team if rev_team else np.nan
                    if scen != "base":
                        rows.append(dict(vintage_date=vd, quarter=q, horizon_q=h, spec_id=spec,
                                         object="street_plus_flowthrough", scenario=scen,
                                         target=EBITDA, point=e2, street=se, n_train=n_train,
                                         knowable_from=kf, street_as_of=as_of, src=src,
                                         note=f"scen={scen} rev={rev_team:.0f} leg={leg}"))
                        rows.append(dict(vintage_date=vd, quarter=q, horizon_q=h, spec_id=spec,
                                         object="street_plus_flowthrough", scenario=scen,
                                         target=MARGIN, point=m2, street=sm, n_train=n_train,
                                         knowable_from=kf, street_as_of=as_of, src=src,
                                         note=f"scen={scen} rev={rev_team:.0f} leg={leg}"))
                        continue
                    packs = [("street_plus_bias", e1, m1,
                              f"b_pct={b['b_pct']:+.4f} b_pt={b['b_pt']:+.3f} n_pool={b['n_pool']}"),
                             ("street_plus_flowthrough", e2, m2,
                              f"a={f['a']:+.1f} m={f['m']:.3f} rev={rev_team:.0f} leg={leg}"),
                             ("dispersion_conditioned", e3, m3,
                              f"disp={d0:.4f} ref={dref:.4f} ratio={dr:.3f} b_pt={b['b_pt']:+.3f}")]
                    for obj, ev, mv, nt in packs:
                        for tgt, pv, stv in ((EBITDA, ev, se), (MARGIN, mv, sm)):
                            rows.append(dict(vintage_date=vd, quarter=q, horizon_q=h, spec_id=spec,
                                             object=obj, scenario="base", target=tgt, point=pv,
                                             street=stv, n_train=n_train, knowable_from=kf,
                                             street_as_of=as_of, src=src, note=nt))
    g = pd.DataFrame(rows)
    g["actual"] = [act[tg].get(q, np.nan) for tg, q in zip(g["target"], g["quarter"])]
    g["print_date"] = g["quarter"].map(pdm)
    g["err"] = g["point"] - g["actual"]
    with np.errstate(divide="ignore", invalid="ignore"):
        g["rel_err"] = g["actual"] / g["point"] - 1.0
    return g, pd.DataFrame(diag), wide, t, disp, live_street


# ------------------------------------------------------------------ quantiles
RELATIVE = {EBITDA}


def attach_quantiles(g):
    g = g.copy()
    for c in ["sd_pit", "n_pit", "sd_full", "n_full"]:
        g[c] = np.nan
    g["sigma_kind"] = ""
    key = ["object", "target", "horizon_q", "spec_id", "scenario"]
    pools = {}
    for k, grp in g.groupby(key):
        rel = k[1] in RELATIVE
        p = grp[grp["actual"].notna() & grp["print_date"].notna()]
        if rel:
            p = p[(p["point"] > 0) & (p["actual"] > 0)]
        p = p.sort_values("quarter")
        pools[k] = ((p["rel_err"] if rel else p["err"]).to_numpy(float),
                    p["print_date"].to_numpy())
    for k, grp in g.groupby(key):
        rel = k[1] in RELATIVE
        errs, pdates = pools[k]
        borrowed = ""
        if len(errs) < MIN_RESID and k[2] >= 2:
            for hb in (1, 0):
                e2, p2 = pools.get((k[0], k[1], hb, k[3], k[4]), (np.array([]), np.array([])))
                if len(e2) >= MIN_RESID:
                    errs, pdates, borrowed = e2, p2, f"_borrowed_h{hb}"
                    break
        full_sd = float(np.std(errs, ddof=1)) if len(errs) >= MIN_RESID else np.nan
        for i in grp.index:
            vd = g.at[i, "vintage_date"]
            m = np.array([d <= vd for d in pdates], dtype=bool) if len(pdates) else np.array([], bool)
            e = errs[m][-RESID_MAX_N:]
            sd_pit = float(np.std(e, ddof=1)) if len(e) >= MIN_RESID else np.nan
            g.at[i, "sd_pit"] = sd_pit
            g.at[i, "n_pit"] = len(e)
            g.at[i, "sd_full"] = full_sd
            g.at[i, "n_full"] = len(errs)
            g.at[i, "sigma_kind"] = ("relative" if rel else "additive") + borrowed
    return g


def rows_for_replay(g, pb):
    out = []
    for r in g.itertuples():
        rel = r.target in RELATIVE
        sd = r.sd_pit if pb == "PIT" else r.sd_full
        kind = r.sigma_kind
        if not np.isfinite(sd) or sd <= 0:
            sd = FALLBACK_REL if rel else FALLBACK_PP
            kind += "_fallback"
        pt = r.point
        q = {c: (pt * (1.0 + Z[c] * sd) if rel else pt + Z[c] * sd) for c in QCOLS}
        vals = sorted(q.values())
        q = dict(zip(QCOLS, vals))
        out.append(dict(vintage_date=r.vintage_date, quarter=r.quarter, horizon_q=int(r.horizon_q),
                        spec_id=r.spec_id, object=r.object, scenario=r.scenario, target=r.target,
                        point=float(pt), prior_basis=pb, sd=abs(pt) * sd if rel else sd,
                        n_train=int(r.n_train), knowable_from=r.knowable_from,
                        street_as_of=r.street_as_of, src=r.src, note=r.note,
                        sigma_kind=kind, sigma_n=int(r.n_pit if pb == "PIT" else r.n_full), **q))
    return pd.DataFrame(out)


# ------------------------------------------------------------------ registry frames
def registry_frames(gq):
    both = pd.concat([rows_for_replay(gq, "PIT"), rows_for_replay(gq, "full_sample")],
                     ignore_index=True)
    both = both[both["scenario"] == "base"]           # bear/bull are LIVE-only side tables
    frames = {}
    for obj, grp in both.groupby("object"):
        rows = []
        for r in grp.itertuples():
            for win in windows_for(r.vintage_date, r.quarter):
                spec = r.spec_id + ("_fyalloc" if r.src == "fyalloc" else "")
                row = dict(method=METHOD, object=obj, target=r.target, quarter=r.quarter,
                           vintage_date=r.vintage_date, horizon_q=int(r.horizon_q),
                           point=float(r.point), q50=float(r.q50), window=win,
                           prior_basis=r.prior_basis,
                           n_params=N_PARAMS[obj] + (0 if r.sigma_kind.endswith("fallback") else 1),
                           n_train=int(r.n_train), sd=float(r.sd),
                           knowable_from=r.knowable_from, street_vendor="LSEG",
                           street_as_of=r.street_as_of, spec_id=spec,
                           notes=f"{r.note}; sigma {r.sigma_kind} n={r.sigma_n} ({r.prior_basis}); "
                                 f"street_src={r.src}")
                for c in QCOLS:
                    row[c] = float(getattr(r, c))
                rows.append(row)
        frames[obj] = pd.DataFrame(rows)
    return frames


# ------------------------------------------------------------------ secondary tests
def secondary_tests(wide, t):
    import scipy.stats as st
    from statsmodels.stats.diagnostic import acorr_ljungbox
    out = {}
    p0 = wide[(wide["horizon_q"] == 0) & wide["act_" + MARGIN].notna()].copy()
    p0["s_pt"] = p0["act_" + MARGIN] - p0[MARGIN]
    p0 = p0.sort_values("quarter")
    s = p0["s_pt"].to_numpy(float)
    lb = acorr_ljungbox(s, lags=[1, 4], return_df=True)
    out["ljungbox_all"] = {f"lag{int(i)}": dict(stat=float(r.lb_stat), p=float(r.lb_pvalue))
                           for i, r in lb.iterrows()}
    out["n_ljungbox_all"] = int(len(s))
    s2 = p0[p0["quarter"] >= "2022Q1"]["s_pt"].to_numpy(float)
    lb2 = acorr_ljungbox(s2, lags=[1, 4], return_df=True)
    out["ljungbox_from22"] = {f"lag{int(i)}": dict(stat=float(r.lb_stat), p=float(r.lb_pvalue))
                              for i, r in lb2.iterrows()}
    out["n_ljungbox_from22"] = int(len(s2))
    # quarter-of-year seasonality of the surprise (W2 era)
    for lab, sub in (("from22", p0[p0["quarter"] >= "2022Q1"]),
                     ("W2era", p0[p0["quarter"] >= "2024Q1"])):
        qy = sub["quarter"].str[-1].astype(int)
        groups = [sub["s_pt"][qy == i].to_numpy(float) for i in (1, 2, 3, 4)]
        groups = [x for x in groups if len(x) >= 2]
        if len(groups) >= 2:
            F, p = st.f_oneway(*groups)
            out[f"seasonality_{lab}"] = dict(F=float(F), p=float(p),
                                             n=int(len(sub)), k=len(groups),
                                             means={str(i): float(np.mean(sub["s_pt"][qy == i]))
                                                    for i in (1, 2, 3, 4)
                                                    if (qy == i).sum() > 0})
    # dispersion regressions
    d = load_dispersion()
    p0d = p0.merge(d, on=["vintage_date", "horizon_q"], how="inner")
    if len(p0d) >= 6:
        for lab, y in (("signed", p0d["s_pt"].to_numpy(float)),
                       ("abs", np.abs(p0d["s_pt"].to_numpy(float)))):
            x = p0d["disp"].to_numpy(float)
            sl, ic, r, p, se = st.linregress(x, y)
            out[f"dispersion_{lab}"] = dict(slope=float(sl), intercept=float(ic), r2=float(r ** 2),
                                            p=float(p), se=float(se), n=int(len(x)))
        p0d2 = p0d[p0d["quarter"] >= "2022Q1"]
        if len(p0d2) >= 6:
            sl, ic, r, p, se = st.linregress(p0d2["disp"].to_numpy(float),
                                             p0d2["s_pt"].to_numpy(float))
            out["dispersion_signed_from22"] = dict(slope=float(sl), intercept=float(ic),
                                                   r2=float(r ** 2), p=float(p), se=float(se),
                                                   n=int(len(p0d2)))
    # FY floor anchoring, replicated against the harness guide table
    fy_rows = []
    cons = pd.read_csv(WS03 / "03_consensus_at_dates.csv")
    cons = cons[(cons["target_role"] == "fy_current_post_guide_5td") &
                (cons["found"].astype(str).str.lower() == "true")]
    for r in cons.itertuples():
        vd = pd.to_datetime(r.date).date()
        per = str(r.target_period)
        if not per.startswith("FY") or not pd.notna(r.implied_margin_pct):
            continue
        g = fy_guide_in_force(vd, int(per[2:]), t)
        if g is None or not np.isfinite(float(g["level_pct"])):
            continue
        fl = float(g["level_pct"])
        fy_rows.append(dict(guide_date=str(vd), fy=per, floor=fl, guide_type=g["guide_type"],
                            form=g["form"], cons_margin=float(r.implied_margin_pct),
                            gap_pt=float(r.implied_margin_pct) - fl))
    out["fy_floor"] = fy_rows
    return out


# ------------------------------------------------------------------ main
def main():
    g, diag, wide, t, disp, live_street = build_grid()
    gq = attach_quantiles(g)
    gq.to_csv(OUT / "M5_grid_all_vintages.csv", index=False)
    diag.to_csv(OUT / "M5_parameters_by_vintage.csv", index=False)
    if len(live_street):
        live_street.to_csv(OUT / "M5_street_fy27_allocation.csv", index=False)

    # surprise panel actually used (PIT ground truth)
    sp = wide[wide["act_" + EBITDA].notna()].copy()
    sp["s_usd"] = sp["act_" + EBITDA] - sp[EBITDA]
    sp["s_pt"] = sp["act_" + MARGIN] - sp[MARGIN]
    sp["s_pct"] = np.where(sp[EBITDA] > 0, sp["act_" + EBITDA] / sp[EBITDA] - 1.0, np.nan)
    sp["rev_surp_usd"] = sp["act_" + REVENUE] - sp[REVENUE]
    sp.to_csv(OUT / "M5_surprise_panel.csv", index=False)

    frames = registry_frames(gq)
    for obj, f in frames.items():
        print(f"  {obj:26s} {len(f):5d} rows  windows {sorted(f['window'].unique())} "
              f"specs {f['spec_id'].nunique()}")
        register(f, quiet=False)

    tests = secondary_tests(wide, t)
    (OUT / "M5_secondary_tests.json").write_text(json.dumps(tests, indent=2, default=str))
    print(json.dumps({k: v for k, v in tests.items() if k != "fy_floor"}, indent=2, default=str))
    return gq, diag


if __name__ == "__main__":
    main()
