"""M6_cycle_flex: cycle and cost-flex model (method `cycle-flex`), margin build 13-14 Sep 2026.

Part A. Cyclicality measured: (i) seasonal profile split into mechanical (revenue timing vs flat costs) and discretionary
        timing, 2022-25 stability, 2026 Q3/Q4 profile; (ii) response of each cash line's y/y growth to revenue y/y growth
        (lags 0-2, episode dummies, asymmetry, peers BKNG/EXPE), recency weighted, HAC standard errors.
Part B. Scenario engine flex(cost_path_base, revenue_path_scenario, variant) with variants held / flex / hold_disc / cut,
        bear/base/bull from WS06 v2b, FY26 floor break-even, 1Q27 trough.
The lag-0 regression is also the registered forecaster (objects flex_margin, flex_lines; specs l0_rw (main), l0_eq, dl_rw,
revknown_rw; both replays), through the margin harness. Pre-registration: docs/margin-build/notes/M6_cycle_flex.md section 0.

Run:  py -3.13 analysis/src/margin_build/M6_cycle_flex/run.py     (from the worktree root; ~1 min; exit 0)
"""
from __future__ import annotations

import datetime as _dt
import json
import subprocess
import sys
import warnings
from pathlib import Path

import numpy as np
import pandas as pd
import statsmodels.api as sm

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[3]
HARNESS = REPO / "analysis" / "src" / "margin_build" / "10_harness_margin"
sys.path.insert(0, str(HARNESS))

from harness_margin import (  # noqa: E402
    load_targets, history_as_of, GUIDE_DATES_ALL, GUIDE_DATE_LIVE, TODAY,
    windows_for, register, revenue_forecast_pit, Q,
)

warnings.filterwarnings("ignore")

METHOD = "cycle-flex"
SLUG = "M6_cycle_flex"
OUT = REPO / "data" / "processed" / "margin_build" / SLUG
FIG = REPO / "analysis" / "figures" / "margin_build"
OUT.mkdir(parents=True, exist_ok=True)
FIG.mkdir(parents=True, exist_ok=True)
MB = REPO / "data" / "processed" / "margin_build"
WS06_DIR = MB / "06_fy27_path_v2"
WS06_LONG_V2B = WS06_DIR / "06_revenue_path_3q26_4q27_v2b.csv"
WS06_ANNUAL_V2B = WS06_DIR / "06_annual_fy26_fy28_v2b.csv"
WS06_CONS27 = WS06_DIR / "06_consensus_quarterly_2027.csv"
WS03_CURRENT = MB / "03_consensus_pit" / "03_current_consensus.csv"
M1_LIVE = MB / "M1_driver_lines" / "M1_driver_lines_live_quarterly.csv"
M1_SPEC = "b_elastic_rw"
PEER_OPEX = REPO / "data" / "raw" / "margin_build" / "04_alt_signals" / "misc" / "lseg_peer_opex_quarterly.csv"
PEER_SM = REPO / "data" / "raw" / "margin_build" / "04_alt_signals" / "misc" / "lseg_peer_sm_quarterly.csv"
REG_BASELINE = MB / "registry" / "baselines-margin__seasonal_naive_drift.csv"

LINES = ["cor", "ops", "pd", "sm", "ga"]
LINE_TARGET = {"cor": "cor_cash_musd", "ops": "ops_cash_musd", "pd": "pd_cash_musd", "sm": "sm_cash_musd",
               "ga": "ga_cash_ex_reserves_musd"}
MARGIN_TARGETS = ["adj_ebitda_margin_pct", "adj_ebitda_musd", "total_cash_costs_musd"]
RELATIVE_TARGETS = set(LINE_TARGET.values()) | {"adj_ebitda_musd", "total_cash_costs_musd"}

HALF_LIFE = 4.0
MIN_OBS = 4
FIRST_YOY_MAIN = "2022Q1"
FIRST_YOY_2021 = "2021Q1"
H_BACK, H_LIVE, H_ANNUAL = 2, 5, 9
RESID_MAX_N, MIN_RESID = 12, 3
FALLBACK_REL, FALLBACK_PP = 0.10, 3.0
QCOLS = ["q05", "q10", "q25", "q50", "q75", "q90", "q95"]
ZQ = dict(zip(QCOLS, [-1.6448536269514722, -1.2815515655446004, -0.6744897501960817, 0.0,
                      0.6744897501960817, 1.2815515655446004, 1.6448536269514722]))
HAC_LAGS = 2

# spec_id -> (family, weighting, revenue source)
SPECS = {"l0_rw": ("l0", "rw", "pit"), "l0_eq": ("l0", "eq", "pit"), "dl_rw": ("dl", "rw", "pit"),
         "revknown_rw": ("l0", "rw", "actual")}
MAIN_SPEC = "l0_rw"
N_PARAMS = {"l0": 12, "dl": 22}

EPISODES = {"E2": ("2022Q2", "2023Q1"), "E3": ("2023Q2", "2023Q4"), "E4": ("2025Q1", "2025Q4"), "E5": ("2026Q1", "2026Q2")}
SHOCK_2H22 = ["2022Q3", "2022Q4", "2023Q1"]
SHOCK_2025 = ["2025Q1", "2025Q2", "2025Q3", "2025Q4"]

# scenario engine constants (pre-registered)
CUT_CAPS = {"sm": 0.20, "pd": 0.10, "ga": 0.05}
FY26_FLOOR = 35.5
FY27_TARGET = 35.0
CUT_FIRST_Q = "2026Q4"


# ============================================================================ panel
def build_panel() -> pd.DataFrame:
    t = load_targets().copy()
    t["quarter"] = t["quarter"].map(Q.canon)
    p = t[["quarter", "print_date", "has_actual", "revenue_musd", "adj_ebitda_musd", "adj_ebitda_margin_pct"]
          + list(LINE_TARGET.values())].copy().rename(columns={"revenue_musd": "revenue"})
    for ln, col in LINE_TARGET.items():
        p[ln] = pd.to_numeric(p[col], errors="coerce")
    p["sum_lines"] = p[LINES].sum(axis=1, min_count=5)
    p["other_net"] = p["adj_ebitda_musd"] - p["revenue"] + p["sum_lines"]
    p["total_cash_costs_musd"] = p["revenue"] - p["adj_ebitda_musd"]
    return p.sort_values("quarter").set_index("quarter")


PANEL = build_panel()
ACT = PANEL[PANEL["has_actual"].astype(bool)]
PRINT_DATE = {q: r.print_date for q, r in PANEL.iterrows() if pd.notna(r.print_date)}


def hist_as_of(vd) -> pd.DataFrame:
    h = history_as_of(vd)
    qs = set(h["quarter"].map(Q.canon))
    return ACT[ACT.index.isin(qs)]


def qi(q: str) -> int:
    return Q.to_index(q)


def qrange(a: str, b: str) -> list:
    return [Q.from_index(i) for i in range(qi(a), qi(b) + 1)]


# ============================================================================ regressions
def yoy_frame(h: pd.DataFrame, first_yoy: str) -> pd.DataFrame:
    """Four-quarter log growth of every line, revenue and total cash costs, quarters >= first_yoy."""
    rows = []
    for q in h.index:
        if qi(q) < qi(first_yoy):
            continue
        lag = Q.shift(q, -4)
        if lag not in h.index:
            continue
        rec = {"quarter": q}
        ok = True
        for c in LINES + ["revenue", "total_cash_costs_musd"]:
            a, b = h.loc[q, c], h.loc[lag, c]
            if pd.isna(a) or pd.isna(b) or a <= 0 or b <= 0:
                ok = False
                break
            rec["g_" + c] = float(np.log(a / b))
        if ok:
            rows.append(rec)
    d = pd.DataFrame(rows)
    if len(d) == 0:
        return d
    d = d.set_index("quarter")
    d["r"] = d["g_revenue"]
    d["r_l1"] = d["r"].shift(1)
    d["r_l2"] = d["r"].shift(2)
    for e, (a, b) in EPISODES.items():
        d["d_" + e] = [(qi(a) <= qi(q) <= qi(b)) * 1.0 for q in d.index]
    d["d_E1"] = [(qi(q) <= qi("2021Q4")) * 1.0 for q in d.index]
    rbar = d["r"].rolling(4, min_periods=2).mean().shift(1)
    dev = d["r"] - rbar
    d["r_up"] = dev.clip(lower=0)
    d["r_dn"] = dev.clip(upper=0)
    return d


def weights_for(index, weighting: str, anchor: str) -> np.ndarray:
    if weighting == "eq":
        return np.ones(len(index))
    return np.array([0.5 ** ((qi(anchor) - qi(q)) / HALF_LIFE) for q in index])


def wls(y: pd.Series, X: pd.DataFrame, w: np.ndarray):
    """WLS with HAC(2) covariance. Returns (params, tvalues, pvalues, resid, model result)."""
    Xc = sm.add_constant(X, has_constant="add")
    res = sm.WLS(y.to_numpy(float), Xc.to_numpy(float), weights=w).fit(cov_type="HAC", cov_kwds={"maxlags": HAC_LAGS})
    names = list(Xc.columns)
    return (dict(zip(names, res.params)), dict(zip(names, res.tvalues)), dict(zip(names, res.pvalues)),
            pd.Series(res.resid, index=y.index), res)


def fit_line(d: pd.DataFrame, line: str, family: str, weighting: str, anchor: str, extra: list | None = None,
             xcols: list | None = None) -> dict:
    """Fit one line. family l0: r; dl: r, r_l1, r_l2; custom xcols override."""
    y = d["g_" + line]
    if xcols is None:
        xcols = ["r"] if family == "l0" else ["r", "r_l1", "r_l2"]
    xcols = list(xcols) + (extra or [])
    sub = d[["g_" + line] + xcols].dropna()
    if len(sub) < MIN_OBS:
        return None
    w = weights_for(sub.index, weighting, anchor)
    params, tv, pv, resid, res = wls(sub["g_" + line], sub[xcols], w)
    out = {"line": line, "family": family, "weighting": weighting, "n_obs": int(len(sub)),
           "first_obs": sub.index[0], "last_obs": sub.index[-1], "c": params["const"], "t_c": tv["const"]}
    for x in xcols:
        out["k_" + x if x.startswith("r") else x] = params[x]
        out["t_" + x if x.startswith("r") else "t_" + x] = tv[x]
        out["p_" + x if x.startswith("r") else "p_" + x] = pv[x]
    out["resid_sd"] = float(np.sqrt(np.average(resid ** 2, weights=w)))
    out["r2"] = float(res.rsquared) if np.isfinite(res.rsquared) else np.nan
    out["_res"] = res
    return out


def fit_all(h: pd.DataFrame, spec: str, anchor: str | None = None) -> dict:
    """Fit the five lines at a vintage for a spec; fall back to the 2021 observations if fewer than MIN_OBS."""
    family, weighting, _ = SPECS[spec]
    anchor = anchor or h.index.max()
    d = yoy_frame(h, FIRST_YOY_MAIN)
    flag = ""
    need = MIN_OBS + (2 if family == "dl" else 0)
    if len(d) == 0 or len(d.dropna(subset=["r_l2"] if family == "dl" else ["r"])) < need:
        d = yoy_frame(h, FIRST_YOY_2021)
        flag = "fit_incl_2021_obs"
    out = {}
    for ln in LINES:
        f = fit_line(d, ln, family, weighting, anchor)
        if f is None:
            # degenerate: no fit -> zero growth, k = 0 (flagged)
            f = {"line": ln, "family": family, "weighting": weighting, "n_obs": 0, "c": 0.0, "k_r": 0.0,
                 "k_r_l1": 0.0, "k_r_l2": 0.0, "resid_sd": np.nan}
            flag = "no_fit_zero_growth"
        f["flags"] = flag
        f.pop("_res", None)
        out[ln] = f
    # other_net rule: trailing-4 share of revenue
    tail = h.iloc[-4:]
    out["other_net_share"] = float((tail["other_net"] / tail["revenue"]).mean())
    out["n_train"] = int(len(d))
    return out


# ============================================================================ forecasting
def forecast_path(params: dict, spec: str, h: pd.DataFrame, vd, h_max: int, rev_source: str,
                  live_rev: dict | None = None) -> list:
    """Forecast quarters q0..q0+h_max at a vintage. rev_source: 'pit' (harness leg), 'actual', 'live' (dict q->rev)."""
    family, weighting, _ = SPECS[spec]
    q0 = Q.quarter_of_date(pd.to_datetime(vd).date())
    rev_known = h["revenue"].to_dict()
    rev_hat, lines_hat, rows = {}, {}, []
    last_print = h["print_date"].max()

    def rev_at(q):
        if q in rev_known:
            return float(rev_known[q]), "actual"
        if q in rev_hat:
            return rev_hat[q]
        if rev_source == "live":
            v = live_rev.get(q)
            return (float(v), "ws06_v2b") if v is not None and np.isfinite(v) else (np.nan, "none")
        if rev_source == "actual" and q in ACT.index:
            return float(ACT.loc[q, "revenue"]), "actual_oracle"
        v, leg = revenue_forecast_pit(vd, q, "PIT")
        return float(v), leg

    def line_at(ln, q):
        if q in h.index:
            return float(h.loc[q, ln])
        return lines_hat.get((ln, q), np.nan)

    for hz in range(0, h_max + 1):
        q = Q.shift(q0, hz)
        rev, leg = rev_at(q)
        if not np.isfinite(rev):
            continue
        rev_hat[q] = (rev, leg)
        lag4 = Q.shift(q, -4)
        r4, _ = rev_at(lag4)
        if not np.isfinite(r4):
            continue
        r_q = float(np.log(rev / r4))
        lagr = {}
        for l in (1, 2):
            ql = Q.shift(q, -l)
            a, _ = rev_at(ql)
            b, _ = rev_at(Q.shift(ql, -4))
            lagr[l] = float(np.log(a / b)) if np.isfinite(a) and np.isfinite(b) else 0.0
        rec = {"quarter": q, "horizon_q": hz, "revenue": rev, "rev_leg": leg}
        for ln in LINES:
            base = line_at(ln, lag4)
            p = params[ln]
            g = p["c"] + p.get("k_r", 0.0) * r_q
            if family == "dl":
                g += p.get("k_r_l1", 0.0) * lagr[1] + p.get("k_r_l2", 0.0) * lagr[2]
            val = base * float(np.exp(g)) if np.isfinite(base) else np.nan
            lines_hat[(ln, q)] = val
            rec[ln] = val
            rec["g_" + ln] = g
        rec["other_net"] = params["other_net_share"] * rev
        rec["sum_lines"] = sum(rec[ln] for ln in LINES)
        rec["adj_ebitda_musd"] = rev - rec["sum_lines"] + rec["other_net"]
        rec["adj_ebitda_margin_pct"] = 100.0 * rec["adj_ebitda_musd"] / rev
        rec["total_cash_costs_musd"] = rev - rec["adj_ebitda_musd"]
        rec["knowable_from"] = last_print
        rows.append(rec)
    return rows


def load_ws06() -> tuple[dict, pd.DataFrame]:
    """{scenario: {quarter: revenue}} from the WS06 v2b long file (base to 4Q28; bear/bull to 4Q27)."""
    d = pd.read_csv(WS06_LONG_V2B)
    d = d[d["line"] == "revenue_musd"].copy()
    d["quarter"] = d["quarter"].map(Q.canon)
    out = {s: g.set_index("quarter")["value"].astype(float).to_dict() for s, g in d.groupby("scenario")}
    return out, d


# ============================================================================ quantiles (harness convention)
def attach_quantiles(long: pd.DataFrame) -> pd.DataFrame:
    long = long.copy()
    for c in QCOLS + ["sd", "sigma_n"]:
        long[c] = np.nan
    long["sigma_kind"] = ""
    real = long[long["actual"].notna()]
    pools = {}
    for (sp, tg, hz, pb), g in real.groupby(["spec_id", "target", "horizon_q", "prior_basis"]):
        rel = tg in RELATIVE_TARGETS
        g = g[(g["point"] > 0) & (g["actual"] > 0)] if rel else g
        errs = ((g["point"] / g["actual"] - 1.0) if rel else (g["point"] - g["actual"])).to_numpy(float)
        pools[(sp, tg, int(hz), pb)] = (errs, g["target_print_date"].to_numpy())
    for i, r in long.iterrows():
        rel = r["target"] in RELATIVE_TARGETS
        hz = int(r["horizon_q"])
        errs, pdates = pools.get((r["spec_id"], r["target"], hz, r["prior_basis"]), (np.array([]), np.array([])))
        borrowed = ""
        if len(errs) < MIN_RESID:
            for hb in range(hz - 1, -1, -1):
                e2, p2 = pools.get((r["spec_id"], r["target"], hb, r["prior_basis"]), (np.array([]), np.array([])))
                if len(e2) >= MIN_RESID:
                    errs, pdates, borrowed = e2, p2, f"_borrowed_h{hb}"
                    break
        if r["prior_basis"] == "full_sample":
            e = errs
        else:
            m = np.array([pd.notna(d) and d <= r["vintage_date"] for d in pdates], dtype=bool)
            e = errs[m][-RESID_MAX_N:]
        sd = float(np.std(e, ddof=1)) if len(e) >= MIN_RESID else np.nan
        kind = ("relative" if rel else "additive") + borrowed
        if not np.isfinite(sd) or sd <= 0:
            sd = FALLBACK_REL if rel else FALLBACK_PP
            kind += "_fallback"
        pt = float(r["point"])
        for c in QCOLS:
            long.at[i, c] = pt * (1.0 + ZQ[c] * sd) if rel else pt + ZQ[c] * sd
        long.at[i, "sd"] = abs(pt) * sd if rel else sd
        long.at[i, "sigma_n"] = int(len(e))
        long.at[i, "sigma_kind"] = kind
    qm = long[QCOLS].to_numpy(float)
    qm.sort(axis=1)
    long[QCOLS] = qm
    return long


# ============================================================================ part A(i): seasonality
def seasonal_table(base_paths: dict) -> pd.DataFrame:
    """Quarter shares of FY adj EBITDA and lines, mechanical vs discretionary margin, 2022-25 + 2026 under the base paths."""
    rows = []
    for y in (2022, 2023, 2024, 2025):
        qs = [f"{y}Q{n}" for n in (1, 2, 3, 4)]
        sub = ACT.loc[qs]
        fy_cost = float(sub["total_cash_costs_musd"].sum())
        for q in qs:
            rec = {"year": y, "quarter": q, "qn": int(q[-1]), "source": "actual", "revenue": sub.loc[q, "revenue"],
                   "share_revenue_pct": 100 * sub.loc[q, "revenue"] / sub["revenue"].sum(),
                   "share_adj_ebitda_pct": 100 * sub.loc[q, "adj_ebitda_musd"] / sub["adj_ebitda_musd"].sum(),
                   "share_total_cash_costs_pct": 100 * sub.loc[q, "total_cash_costs_musd"] / fy_cost,
                   "margin_actual_pct": sub.loc[q, "adj_ebitda_margin_pct"],
                   "margin_if_costs_flat_pct": 100 * (1 - (fy_cost / 4) / sub.loc[q, "revenue"])}
            rec["margin_discretionary_timing_pp"] = rec["margin_actual_pct"] - rec["margin_if_costs_flat_pct"]
            for ln in LINES:
                rec[f"share_{ln}_pct"] = 100 * sub.loc[q, ln] / sub[ln].sum()
                rec[f"{ln}_pct_rev"] = 100 * sub.loc[q, ln] / sub.loc[q, "revenue"]
            rows.append(rec)
    # 2026: 1H actual + base path
    for label, bp in base_paths.items():
        qs = ["2026Q1", "2026Q2", "2026Q3", "2026Q4"]
        rev = {q: float(ACT.loc[q, "revenue"]) for q in qs[:2]}
        eb = {q: float(ACT.loc[q, "adj_ebitda_musd"]) for q in qs[:2]}
        ln_v = {q: {ln: float(ACT.loc[q, ln]) for ln in LINES} for q in qs[:2]}
        for q in qs[2:]:
            rev[q] = float(bp.loc[q, "revenue"]); eb[q] = float(bp.loc[q, "adj_ebitda_musd"])
            ln_v[q] = {ln: float(bp.loc[q, ln]) for ln in LINES}
        fy_rev = sum(rev.values()); fy_eb = sum(eb.values()); fy_cost = fy_rev - fy_eb
        for q in qs:
            rec = {"year": 2026, "quarter": q, "qn": int(q[-1]), "source": "actual" if q in qs[:2] else label,
                   "revenue": rev[q], "share_revenue_pct": 100 * rev[q] / fy_rev,
                   "share_adj_ebitda_pct": 100 * eb[q] / fy_eb,
                   "share_total_cash_costs_pct": 100 * (rev[q] - eb[q]) / fy_cost,
                   "margin_actual_pct": 100 * eb[q] / rev[q],
                   "margin_if_costs_flat_pct": 100 * (1 - (fy_cost / 4) / rev[q])}
            rec["margin_discretionary_timing_pp"] = rec["margin_actual_pct"] - rec["margin_if_costs_flat_pct"]
            for ln in LINES:
                rec[f"share_{ln}_pct"] = 100 * ln_v[q][ln] / sum(ln_v[x][ln] for x in qs)
                rec[f"{ln}_pct_rev"] = 100 * ln_v[q][ln] / rev[q]
            rows.append(rec)
    return pd.DataFrame(rows)


# ============================================================================ part A(ii): the k table at TODAY
def k_table(h_full: pd.DataFrame) -> pd.DataFrame:
    """Single-lag k at lags 0/1/2, distributed lag, episode dummies, incl-2021, asymmetry; rw and eq; ABNB lines + total."""
    rows = []
    anchor = h_full.index.max()
    for first, samp in ((FIRST_YOY_MAIN, "1Q22+"), (FIRST_YOY_2021, "1Q21+")):
        d = yoy_frame(h_full, first)
        for weighting in ("rw", "eq"):
            for ln in LINES + ["total_cash_costs_musd"]:
                # single lags
                for lag, x in ((0, "r"), (1, "r_l1"), (2, "r_l2")):
                    extra = ["d_E1"] if samp == "1Q21+" else None
                    f = fit_line(d, ln, "l0", weighting, anchor, extra=extra, xcols=[x])
                    if f:
                        rows.append({"sample": samp, "weighting": weighting, "line": ln, "spec": f"lag{lag}",
                                     "n_obs": f["n_obs"], "c": f["c"], "k": f["k_" + x], "t_k": f["t_" + x],
                                     "p_k": f["p_" + x], "resid_sd": f["resid_sd"], "r2": f["r2"]})
                # distributed lag
                f = fit_line(d, ln, "dl", weighting, anchor, extra=(["d_E1"] if samp == "1Q21+" else None))
                if f:
                    rows.append({"sample": samp, "weighting": weighting, "line": ln, "spec": "dl_0_1_2",
                                 "n_obs": f["n_obs"], "c": f["c"], "k": f["k_r"], "t_k": f["t_r"], "p_k": f["p_r"],
                                 "k_l1": f["k_r_l1"], "t_k_l1": f["t_r_l1"], "k_l2": f["k_r_l2"], "t_k_l2": f["t_r_l2"],
                                 "k_sum": f["k_r"] + f["k_r_l1"] + f["k_r_l2"], "resid_sd": f["resid_sd"], "r2": f["r2"]})
                # episode dummies (main sample only)
                if samp == "1Q22+":
                    dums = [c for c in ("d_E2", "d_E3", "d_E4", "d_E5")]
                    f = fit_line(d, ln, "l0", weighting, anchor, extra=dums, xcols=["r"])
                    if f:
                        rec = {"sample": samp, "weighting": weighting, "line": ln, "spec": "lag0_episode_dummies",
                               "n_obs": f["n_obs"], "c": f["c"], "k": f["k_r"], "t_k": f["t_r"], "p_k": f["p_r"],
                               "resid_sd": f["resid_sd"], "r2": f["r2"]}
                        for e in dums:
                            rec[e] = f[e]; rec["t_" + e] = f["t_" + e]
                        rows.append(rec)
                    # asymmetry
                    f = fit_line(d, ln, "l0", weighting, anchor, xcols=["r_up", "r_dn"])
                    if f:
                        res = f["_res"]
                        try:
                            wt = res.wald_test("x1 = x2", use_f=False) if False else res.wald_test(np.array([[0, 1, -1]]), use_f=False)
                            p_eq = float(np.squeeze(wt.pvalue))
                        except Exception:
                            p_eq = np.nan
                        rows.append({"sample": samp, "weighting": weighting, "line": ln, "spec": "asym_up_dn",
                                     "n_obs": f["n_obs"], "c": f["c"], "k": f["k_r_up"], "t_k": f["t_r_up"], "p_k": f["p_r_up"],
                                     "k_dn": f["k_r_dn"], "t_k_dn": f["t_r_dn"], "p_k_dn": f["p_r_dn"],
                                     "k_dn_minus_up": f["k_r_dn"] - f["k_r_up"], "p_equal": p_eq,
                                     "resid_sd": f["resid_sd"], "r2": f["r2"]})
    return pd.DataFrame(rows)


def peer_k_table() -> pd.DataFrame:
    """Lag-0 k for BKNG / EXPE / TRIP (and ABNB from LSEG GAAP lines as a cross-check) on the WS04 raw LSEG pull."""
    if not PEER_OPEX.exists():
        return pd.DataFrame()
    a = pd.read_csv(PEER_OPEX)
    b = pd.read_csv(PEER_SM) if PEER_SM.exists() else pd.DataFrame(columns=["Instrument", "Period End Date"])
    d = a.merge(b, on=["Instrument", "Period End Date"], how="left", suffixes=("", "_sm"))
    d["quarter"] = pd.to_datetime(d["Period End Date"]).dt.to_period("Q").astype(str)
    d["quarter"] = d["quarter"].map(Q.canon)
    d = d.rename(columns={"Revenue": "revenue", "Total Operating Expense": "opex_total", "Cost of Revenue, Total": "cor",
                          "Selling/General/Administrative Expense, Total": "sga", "Advertising Expense": "advertising"})
    d["opex_ex_cor"] = d["opex_total"] - d["cor"].fillna(0.0)
    rows = []
    anchor = "2026Q2"
    for tic, g in d.groupby("Instrument"):
        g = g.drop_duplicates("quarter").set_index("quarter").sort_index()
        for measure in ("opex_total", "opex_ex_cor", "sga", "advertising"):
            if measure not in g or g[measure].notna().sum() < 12:
                continue
            recs = []
            for q in g.index:
                lag = Q.shift(q, -4)
                if qi(q) < qi(FIRST_YOY_MAIN) or lag not in g.index:
                    continue
                y1, y0, r1, r0 = g.loc[q, measure], g.loc[lag, measure], g.loc[q, "revenue"], g.loc[lag, "revenue"]
                if any(pd.isna(v) or v <= 0 for v in (y1, y0, r1, r0)):
                    continue
                recs.append({"quarter": q, "g": np.log(y1 / y0), "r": np.log(r1 / r0)})
            dd = pd.DataFrame(recs)
            if len(dd) < 6:
                continue
            dd = dd.set_index("quarter")
            for weighting in ("rw", "eq"):
                w = weights_for(dd.index, weighting, anchor)
                params, tv, pv, resid, res = wls(dd["g"], dd[["r"]], w)
                rows.append({"ticker": tic.replace(".O", ""), "measure": measure, "weighting": weighting,
                             "n_obs": int(len(dd)), "first_obs": dd.index[0], "last_obs": dd.index[-1],
                             "c": params["const"], "k": params["r"], "t_k": tv["r"], "p_k": pv["r"],
                             "r2": float(res.rsquared)})
    return pd.DataFrame(rows)


# ============================================================================ part B: the engine
def flex(base: pd.DataFrame, rev_scen: dict, k: dict, variant: str, k_lags: dict | None = None,
         actual_1h26: dict | None = None, fy_targets: dict | None = None) -> tuple[pd.DataFrame, dict]:
    """Map a base cost path to a revenue scenario.
    base: index quarter, columns revenue, cor, ops, pd, sm, ga, other_net. rev_scen: {quarter: revenue}.
    k: {line: k_lag0}; k_lags: {line: (k0, k1, k2)} for variant flex_dl.
    variants: held | flex | flex_dl | hold_disc | cut. Returns (path, info)."""
    qs = [q for q in base.index if q in rev_scen and np.isfinite(rev_scen[q])]
    out = base.loc[qs].copy()
    out["revenue_base"] = base.loc[qs, "revenue"]
    out["revenue"] = [rev_scen[q] for q in qs]
    dev = {q: float(np.log(out.loc[q, "revenue"] / out.loc[q, "revenue_base"])) for q in qs}
    for ln in LINES:
        base_v = base.loc[qs, ln].to_numpy(float)
        if variant == "held" or (variant == "hold_disc" and ln in ("pd", "sm", "ga")):
            mult = np.ones(len(qs))
        elif variant == "flex_dl":
            k0, k1, k2 = k_lags[ln]
            mult = np.array([np.exp(k0 * dev[q] + k1 * dev.get(Q.shift(q, -1), 0.0) + k2 * dev.get(Q.shift(q, -2), 0.0))
                             for q in qs])
        else:
            mult = np.array([np.exp(k[ln] * dev[q]) for q in qs])
        out[ln] = base_v * mult
    out["other_net"] = base.loc[qs, "other_net"] * (out["revenue"] / out["revenue_base"])
    info = {"variant": variant}
    if variant == "cut":
        out, info = apply_cut(out, base, actual_1h26, fy_targets or {})
    out["sum_lines"] = out[LINES].sum(axis=1)
    out["adj_ebitda_musd"] = out["revenue"] - out["sum_lines"] + out["other_net"]
    out["adj_ebitda_margin_pct"] = 100 * out["adj_ebitda_musd"] / out["revenue"]
    out["total_cash_costs_musd"] = out["revenue"] - out["adj_ebitda_musd"]
    return out, info


def fy_margin(path: pd.DataFrame, fy: int, actual_1h26: dict | None) -> float:
    qs = [q for q in path.index if q.startswith(str(fy))]
    rev = float(path.loc[qs, "revenue"].sum()); eb = float((path.loc[qs, "revenue"] - path.loc[qs, LINES].sum(axis=1)
                                                          + path.loc[qs, "other_net"]).sum())
    if fy == 2026 and actual_1h26:
        rev += actual_1h26["revenue"]; eb += actual_1h26["adj_ebitda_musd"]
    return 100 * eb / rev if rev > 0 else np.nan


def apply_cut(out: pd.DataFrame, base: pd.DataFrame, actual_1h26: dict, fy_targets: dict) -> tuple[pd.DataFrame, dict]:
    """Cut pd/sm/ga from CUT_FIRST_Q by the smallest uniform fraction phi of the caps that restores each FY target."""
    info = {"variant": "cut"}
    for fy, target in fy_targets.items():
        qs = [q for q in out.index if q.startswith(str(fy)) and qi(q) >= qi(CUT_FIRST_Q)]
        if not qs:
            continue
        m0 = fy_margin(out, fy, actual_1h26)
        info[f"fy{fy}_margin_before_cut"] = m0
        if m0 >= target:
            info[f"fy{fy}_phi"] = 0.0; info[f"fy{fy}_cut_musd"] = 0.0; info[f"fy{fy}_margin_after_cut"] = m0
            info[f"fy{fy}_floor_reachable"] = True
            continue
        # linear in phi -> solve directly with the full cap
        full = out.copy()
        for q in qs:
            for ln, cap in CUT_CAPS.items():
                full.loc[q, ln] = out.loc[q, ln] - cap * base.loc[q, ln]
        m1 = fy_margin(full, fy, actual_1h26)
        phi = (target - m0) / (m1 - m0) if m1 > m0 else np.inf
        info[f"fy{fy}_phi"] = float(phi)
        info[f"fy{fy}_floor_reachable"] = bool(phi <= 1.0)
        phi_a = min(phi, 1.0)
        cut_total = 0.0
        for q in qs:
            for ln, cap in CUT_CAPS.items():
                c = phi_a * cap * base.loc[q, ln]
                out.loc[q, ln] = out.loc[q, ln] - c
                cut_total += c
        info[f"fy{fy}_cut_musd"] = float(cut_total)
        info[f"fy{fy}_margin_after_cut"] = fy_margin(out, fy, actual_1h26)
    return out, info


def break_even(base: pd.DataFrame, rev_base: dict, k: dict, variant: str, actual_1h26: dict, which: str,
               k_lags=None) -> dict:
    """Smallest uniform revenue shortfall s (fraction below base on 3Q26+4Q26, or 4Q26 only) at which FY26 margin = floor."""
    def margin_at(s):
        rs = dict(rev_base)
        for q in (["2026Q3", "2026Q4"] if which == "2H26" else ["2026Q4"]):
            rs[q] = rev_base[q] * (1 - s)
        p, info = flex(base, rs, k, variant, k_lags=k_lags, actual_1h26=actual_1h26,
                       fy_targets={2026: FY26_FLOOR} if variant == "cut" else None)
        return fy_margin(p, 2026, actual_1h26), info
    m0, _ = margin_at(0.0)
    rec = {"variant": variant, "shortfall_on": which, "fy26_margin_at_base_pct": m0}
    if m0 < FY26_FLOOR:
        rec.update({"break_even_shortfall_pct": 0.0, "note": "below the floor already at the base path"})
        return rec
    lo, hi = 0.0, 0.8
    mhi, _ = margin_at(hi)
    if mhi >= FY26_FLOOR:
        rec.update({"break_even_shortfall_pct": 100 * hi, "note": ">= 80 % shortfall survives (cap)"})
        return rec
    for _ in range(50):
        mid = 0.5 * (lo + hi)
        m, _ = margin_at(mid)
        if m >= FY26_FLOOR:
            lo = mid
        else:
            hi = mid
    s = 0.5 * (lo + hi)
    rec["break_even_shortfall_pct"] = 100 * s
    qs = ["2026Q3", "2026Q4"] if which == "2H26" else ["2026Q4"]
    rec["break_even_revenue_musd"] = sum(rev_base[q] for q in qs) * s
    rec["margin_sensitivity_pp_per_1pct_shortfall"] = (m0 - margin_at(0.01)[0]) / 1.0
    return rec


# ============================================================================ main
def main() -> int:
    t0 = _dt.datetime.now()
    print(f"M6 cycle flex: start {t0:%Y-%m-%d %H:%M:%S}")
    h_full = hist_as_of(TODAY)
    vintages = [d for d in GUIDE_DATES_ALL if d >= _dt.date(2022, 2, 15)]
    live_vintages = [GUIDE_DATE_LIVE, TODAY]
    ws06, ws06_long = load_ws06()

    # ---- fits at every vintage, forecasts ----------------------------------------------------
    full_params = {spec: fit_all(h_full, spec, anchor="2026Q2") for spec in SPECS}
    wide_rows, param_rows = [], []
    for spec in SPECS:
        for ln in LINES:
            param_rows.append({"vintage_date": "full_sample", "spec_id": spec, **full_params[spec][ln],
                               "other_net_share": full_params[spec]["other_net_share"], "n_train": full_params[spec]["n_train"]})
        for vd in vintages:
            h = hist_as_of(vd)
            pit = fit_all(h, spec)
            for ln in LINES:
                param_rows.append({"vintage_date": vd, "spec_id": spec, **pit[ln], "other_net_share": pit["other_net_share"],
                                   "n_train": pit["n_train"]})
            for replay, params in (("PIT", pit), ("full_sample", full_params[spec])):
                rev_source = SPECS[spec][2]
                rows = forecast_path(params, spec, h, vd, H_BACK, rev_source)
                for r in rows:
                    r.update({"vintage_date": vd, "spec_id": spec, "prior_basis": replay, "scenario": "backtest",
                              "n_train": params["n_train"], "flags": ";".join(sorted({params[ln]["flags"] for ln in LINES if params[ln]["flags"]}))})
                wide_rows += rows
        for vd in live_vintages:
            h = hist_as_of(vd)
            pit = fit_all(h, spec)
            for replay, params in (("PIT", pit), ("full_sample", full_params[spec])):
                for scen in ("base", "bear", "bull"):
                    rows = forecast_path(params, spec, h, vd, H_ANNUAL if scen == "base" else H_LIVE, "live",
                                         live_rev=ws06[scen])
                    for r in rows:
                        r.update({"vintage_date": vd, "spec_id": spec, "prior_basis": replay, "scenario": scen,
                                  "n_train": params["n_train"], "flags": ""})
                    wide_rows += rows
    wide = pd.DataFrame(wide_rows)
    wide["vintage_date"] = pd.to_datetime(wide["vintage_date"]).dt.date
    wide.to_csv(OUT / f"{SLUG}_forecasts_wide.csv", index=False)
    pr = pd.DataFrame(param_rows)
    pr.to_csv(OUT / f"{SLUG}_params_by_vintage.csv", index=False)
    print(f"  forecasts: {len(wide)} quarter-rows; params: {len(pr)} rows")

    # ---- registry -----------------------------------------------------------------------------
    target_cols = {**{v: k for k, v in LINE_TARGET.items()}, **{t: t for t in MARGIN_TARGETS}}
    long_rows, pool_rows = [], []
    for r in wide.itertuples():
        for tg, col in target_cols.items():
            actual = float(ACT.loc[r.quarter, tg]) if r.quarter in ACT.index else np.nan
            base_rec = dict(spec_id=r.spec_id, target=tg, horizon_q=int(r.horizon_q), prior_basis=r.prior_basis,
                            quarter=r.quarter, vintage_date=r.vintage_date, point=float(getattr(r, col)), actual=actual,
                            target_print_date=PRINT_DATE.get(r.quarter))
            if r.scenario == "backtest":
                pool_rows.append(base_rec)
            wins = windows_for(r.vintage_date, r.quarter)
            for w in wins:
                if (w == "LIVE") != (r.scenario != "backtest"):
                    continue
                if w == "LIVE" and r.scenario != "base":
                    continue
                if w == "LIVE" and int(r.horizon_q) > H_LIVE:
                    continue
                long_rows.append(dict(method=METHOD, object="lines" if tg in LINE_TARGET.values() else "margin",
                                      window=w, n_params=N_PARAMS[SPECS[r.spec_id][0]], n_train=int(r.n_train),
                                      knowable_from=r.knowable_from,
                                      notes=f"rev_leg={r.rev_leg};scenario={r.scenario};{r.flags}", **base_rec))
    long = pd.DataFrame(long_rows)
    long["object"] = long["object"].map({"lines": "flex_lines", "margin": "flex_margin"})
    pool = pd.DataFrame(pool_rows)
    long["_reg"] = True; pool["_reg"] = False
    both = attach_quantiles(pd.concat([long, pool], ignore_index=True, sort=False))
    long = both[both["_reg"] == True].drop(columns=["_reg"]).copy()  # noqa: E712
    long["q50"] = long["point"]
    long.to_csv(OUT / f"{SLUG}_registry_long.csv", index=False)
    reg_cols = ["method", "object", "target", "quarter", "vintage_date", "horizon_q", "point", "q50", "window",
                "prior_basis", "n_params", "n_train", "q05", "q10", "q25", "q75", "q90", "q95", "sd", "knowable_from",
                "spec_id", "notes"]
    for obj in ("flex_margin", "flex_lines"):
        d = long[long["object"] == obj][reg_cols].reset_index(drop=True)
        register(d, quiet=False)

    # ---- in-script backtest grid: full windows and shock quarters ------------------------------
    sn = {q: float(ACT.loc[Q.shift(q, -4), "adj_ebitda_margin_pct"]) for q in ACT.index if Q.shift(q, -4) in ACT.index}
    grid = []
    bt = wide[wide["scenario"] == "backtest"]
    for (spec, replay, hz), g in bt.groupby(["spec_id", "prior_basis", "horizon_q"]):
        g = g[g["quarter"].isin(ACT.index)].copy()
        g["actual"] = g["quarter"].map(ACT["adj_ebitda_margin_pct"])
        g["err"] = g["adj_ebitda_margin_pct"] - g["actual"]
        g["err_sn"] = g["quarter"].map(sn) - g["actual"]
        g["err_cost_rel"] = g["total_cash_costs_musd"] / g["quarter"].map(ACT["total_cash_costs_musd"]) - 1
        g["err_rev_rel"] = g["revenue"] / g["quarter"].map(ACT["revenue"]) - 1
        for label, qs in (("all_from_2022Q2", list(g["quarter"])), ("W1", qrange("2023Q1", "2026Q2")),
                          ("W2", qrange("2024Q1", "2026Q2")), ("shock_2H22", SHOCK_2H22), ("shock_2025", SHOCK_2025),
                          ("calm_W1_ex_2025", [q for q in qrange("2023Q1", "2026Q2") if q not in SHOCK_2025])):
            s = g[g["quarter"].isin(qs)]
            if len(s) == 0:
                continue
            w = np.array([0.5 ** ((qi("2026Q2") - qi(q)) / HALF_LIFE) for q in s["quarter"]]); w = w / w.sum()
            grid.append(dict(spec_id=spec, prior_basis=replay, horizon_q=int(hz), quarters=label, n=len(s),
                             mae_margin=s["err"].abs().mean(), rw_mae_margin=float((s["err"].abs() * w).sum()),
                             bias_margin=s["err"].mean(), mae_seasonal_naive=s["err_sn"].abs().mean(),
                             rw_mae_seasonal_naive=float((s["err_sn"].abs() * w).sum()),
                             ratio_vs_seasonal_naive=s["err"].abs().mean() / s["err_sn"].abs().mean(),
                             mape_total_cash_costs=100 * s["err_cost_rel"].abs().mean(),
                             mape_revenue_leg=100 * s["err_rev_rel"].abs().mean()))
    grid = pd.DataFrame(grid)
    grid.to_csv(OUT / f"{SLUG}_backtest_grid.csv", index=False)

    # ---- T2: 2H22 reproduction ------------------------------------------------------------------
    t2_rows = []
    vd22 = _dt.date(2022, 8, 2)
    h22 = hist_as_of(vd22)
    for kind, params in (("full_sample_k", full_params[MAIN_SPEC]), ("PIT_k", fit_all(h22, MAIN_SPEC))):
        base_rows = forecast_path(params, MAIN_SPEC, h22, vd22, 2, "pit")
        base = pd.DataFrame(base_rows).set_index("quarter")
        k = {ln: params[ln]["k_r"] for ln in LINES}
        rev_actual = {q: float(ACT.loc[q, "revenue"]) for q in SHOCK_2H22}
        p, _ = flex(base[["revenue"] + LINES + ["other_net"]], rev_actual, k, "flex")
        for q in SHOCK_2H22:
            t2_rows.append({"k_source": kind, "quarter": q, "vintage_date": vd22, "revenue_base_leg": base.loc[q, "revenue"],
                            "revenue_actual": rev_actual[q], "margin_base_path_pct": base.loc[q, "adj_ebitda_margin_pct"],
                            "margin_flexed_pct": p.loc[q, "adj_ebitda_margin_pct"],
                            "margin_actual_pct": float(ACT.loc[q, "adj_ebitda_margin_pct"]),
                            "error_flexed_pp": p.loc[q, "adj_ebitda_margin_pct"] - float(ACT.loc[q, "adj_ebitda_margin_pct"]),
                            "error_held_pp": (100 * (rev_actual[q] - base.loc[q, "sum_lines"] + base.loc[q, "other_net"] * rev_actual[q] / base.loc[q, "revenue"]) / rev_actual[q]
                                              - float(ACT.loc[q, "adj_ebitda_margin_pct"])),
                            "n_train": params["n_train"], "flags": ";".join(sorted({params[ln]["flags"] for ln in LINES if params[ln]["flags"]}))})
    t2 = pd.DataFrame(t2_rows)
    t2["within_1p5"] = t2["error_flexed_pp"].abs() <= 1.5
    t2.to_csv(OUT / f"{SLUG}_test_2H22_reproduction.csv", index=False)

    # ---- k tables ---------------------------------------------------------------------------------
    kt = k_table(h_full)
    kt.to_csv(OUT / f"{SLUG}_k_table.csv", index=False)
    pk = peer_k_table()
    pk.to_csv(OUT / f"{SLUG}_peer_k.csv", index=False)

    # ---- LIVE base paths and the engine ---------------------------------------------------------------
    k_main = {ln: full_params[MAIN_SPEC][ln]["k_r"] for ln in LINES}
    k_lags = {ln: (full_params["dl_rw"][ln]["k_r"], full_params["dl_rw"][ln]["k_r_l1"], full_params["dl_rw"][ln]["k_r_l2"]) for ln in LINES}
    actual_1h26 = {"revenue": float(ACT.loc[["2026Q1", "2026Q2"], "revenue"].sum()),
                   "adj_ebitda_musd": float(ACT.loc[["2026Q1", "2026Q2"], "adj_ebitda_musd"].sum())}
    own = wide[(wide["spec_id"] == MAIN_SPEC) & (wide["prior_basis"] == "PIT") & (wide["scenario"] == "base")
               & (wide["vintage_date"] == TODAY)].set_index("quarter")[["revenue"] + LINES + ["other_net", "adj_ebitda_musd", "adj_ebitda_margin_pct"]]
    bases = {"M6_l0_rw": own}
    base_label = "M6_l0_rw"
    if M1_LIVE.exists():
        m1 = pd.read_csv(M1_LIVE)
        m1 = m1[(m1["spec_id"] == M1_SPEC) & (m1["prior_basis"] == "PIT") & (m1["scenario"] == "base")].copy()
        m1["quarter"] = m1["quarter"].map(Q.canon)
        m1 = m1.set_index("quarter")[["revenue"] + LINES + ["other_net", "adj_ebitda_musd", "adj_ebitda_margin_pct"]]
        bases["M1_b_elastic_rw"] = m1
        base_label = "M1_b_elastic_rw"
    else:
        # harness seasonal_naive_drift fallback for the lines
        sb = pd.read_csv(REG_BASELINE)
        sb = sb[(sb["window"] == "LIVE") & (sb["prior_basis"] == "PIT") & (sb["vintage_date"].astype(str) == str(TODAY))]
        fb = sb.pivot_table(index="quarter", columns="target", values="point")
        fb = fb.rename(columns={v: k for k, v in LINE_TARGET.items()})
        fb["revenue"] = fb.index.map(ws06["base"])
        fb["other_net"] = full_params[MAIN_SPEC]["other_net_share"] * fb["revenue"]
        fb["adj_ebitda_musd"] = fb["revenue"] - fb[LINES].sum(axis=1) + fb["other_net"]
        fb["adj_ebitda_margin_pct"] = 100 * fb["adj_ebitda_musd"] / fb["revenue"]
        bases["harness_seasonal_naive_drift"] = fb[["revenue"] + LINES + ["other_net", "adj_ebitda_musd", "adj_ebitda_margin_pct"]]
        base_label = "harness_seasonal_naive_drift"
    print(f"  engine base cost path: {base_label} (bases available: {list(bases)})")

    variants = ["held", "flex", "flex_dl", "hold_disc", "cut"]
    scen_rows, info_rows = [], []
    for blabel, bpath in bases.items():
        for scen in ("bear", "base", "bull"):
            rev_scen = ws06[scen]
            for var in variants:
                p, info = flex(bpath, rev_scen, k_main, var, k_lags=k_lags, actual_1h26=actual_1h26,
                               fy_targets={2026: FY26_FLOOR, 2027: FY27_TARGET})
                info.update({"base": blabel, "scenario": scen})
                info_rows.append(info)
                for q, r in p.iterrows():
                    scen_rows.append({"base": blabel, "scenario": scen, "variant": var, "quarter": q, "horizon_q": qi(q) - qi("2026Q3"),
                                      **{c: r[c] for c in ["revenue", "revenue_base"] + LINES + ["other_net", "adj_ebitda_musd", "adj_ebitda_margin_pct", "total_cash_costs_musd"]}})
    scen = pd.DataFrame(scen_rows)
    # comparison columns
    cons = pd.read_csv(WS06_CONS27)
    cons["quarter"] = cons["quarter"].map(lambda x: Q.canon(x) if not str(x).startswith("FY") else x)
    cq = cons.set_index("quarter")
    scen["cons_revenue_musd"] = scen["quarter"].map(cq["revenue_mean_musd"])
    scen["cons_ebitda_musd"] = scen["quarter"].map(cq["ebitda_mean_musd"])
    scen["cons_margin_pct"] = 100 * scen["cons_ebitda_musd"] / scen["cons_revenue_musd"]
    scen["m1_base_margin_pct"] = scen["quarter"].map(bases["M1_b_elastic_rw"]["adj_ebitda_margin_pct"]) if "M1_b_elastic_rw" in bases else np.nan
    scen["mgmt_3q26_ceiling_margin_pct"] = np.where(scen["quarter"] == "2026Q3", float(ACT.loc["2025Q3", "adj_ebitda_margin_pct"]), np.nan)
    scen.to_csv(OUT / f"{SLUG}_scenarios_quarterly.csv", index=False)
    pd.DataFrame(info_rows).to_csv(OUT / f"{SLUG}_cut_solutions.csv", index=False)

    # annual
    ann_rows = []
    cur = pd.read_csv(WS03_CURRENT)
    cons_fy = {r.period: (r.revenue_mean, r.ebitda_mean) for r in cur[cur["vendor"] == "LSEG"].itertuples()}
    for (blabel, sc, var), g in scen.groupby(["base", "scenario", "variant"]):
        g = g.set_index("quarter")
        for fy in (2026, 2027, 2028):
            qs = [q for q in g.index if q.startswith(str(fy))]
            if len(qs) < (2 if fy == 2026 else 4):
                continue
            rev = float(g.loc[qs, "revenue"].sum()); eb = float(g.loc[qs, "adj_ebitda_musd"].sum())
            lines_fy = {ln: float(g.loc[qs, ln].sum()) for ln in LINES}
            if fy == 2026:
                rev += actual_1h26["revenue"]; eb += actual_1h26["adj_ebitda_musd"]
                for ln in LINES:
                    lines_fy[ln] += float(ACT.loc[["2026Q1", "2026Q2"], ln].sum())
            rec = {"fy": f"FY{str(fy)[2:]}", "base": blabel, "scenario": sc, "variant": var, "revenue": rev,
                   "adj_ebitda_musd": eb, "adj_ebitda_margin_pct": 100 * eb / rev, **lines_fy,
                   **{f"{ln}_pct_rev": 100 * lines_fy[ln] / rev for ln in LINES}}
            cr = cons_fy.get(f"FY{str(fy)[2:]}")
            rec["cons_revenue_musd"] = cr[0] if cr else np.nan
            rec["cons_ebitda_musd"] = cr[1] if cr else np.nan
            rec["cons_margin_pct"] = 100 * cr[1] / cr[0] if cr else np.nan
            rec["mgmt_fy26_floor_pct"] = FY26_FLOOR if fy == 2026 else np.nan
            rec["fy25_actual_margin_pct"] = 100 * ACT.loc[[f"2025Q{n}" for n in (1, 2, 3, 4)], "adj_ebitda_musd"].sum() / ACT.loc[[f"2025Q{n}" for n in (1, 2, 3, 4)], "revenue"].sum()
            ann_rows.append(rec)
    ann = pd.DataFrame(ann_rows)
    ann.to_csv(OUT / f"{SLUG}_annual_forecasts.csv", index=False)

    # break-even
    be_rows = []
    for blabel, bpath in bases.items():
        for var in variants:
            for which in ("2H26", "4Q26_only"):
                rec = break_even(bpath, ws06["base"], k_main, var, actual_1h26, which, k_lags=k_lags)
                rec["base"] = blabel
                be_rows.append(rec)
    be = pd.DataFrame(be_rows)
    be.to_csv(OUT / f"{SLUG}_fy26_floor_breakeven.csv", index=False)

    # seasonal (part A i)
    seas = seasonal_table({k: v for k, v in bases.items()})
    seas.to_csv(OUT / f"{SLUG}_seasonal.csv", index=False)
    stab = seas[seas["year"] <= 2025].groupby("qn")[["share_revenue_pct", "share_adj_ebitda_pct", "share_total_cash_costs_pct",
                                                       "margin_actual_pct", "margin_if_costs_flat_pct", "margin_discretionary_timing_pp"]
                                                      + [f"share_{ln}_pct" for ln in LINES]].agg(["mean", "std", "min", "max"])
    stab.columns = ["_".join(c) for c in stab.columns]
    stab.to_csv(OUT / f"{SLUG}_seasonal_stability_2022_25.csv")

    # ---- figures -------------------------------------------------------------------------------------
    try:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
        # F1: k by line
        fig, ax = plt.subplots(figsize=(9, 4.5))
        sub = kt[(kt["sample"] == "1Q22+") & (kt["spec"] == "lag0")]
        x = np.arange(len(LINES) + 1); labels = LINES + ["total"]
        for j, (wt, col) in enumerate((("rw", "#1f77b4"), ("eq", "#7f7f7f"))):
            s = sub[sub["weighting"] == wt].set_index("line")
            ks = [s.loc[l if l != "total" else "total_cash_costs_musd", "k"] for l in labels]
            ts = [s.loc[l if l != "total" else "total_cash_costs_musd", "t_k"] for l in labels]
            se = [abs(k_ / t_) if t_ != 0 else np.nan for k_, t_ in zip(ks, ts)]
            ax.bar(x + (j - 0.5) * 0.35, ks, 0.35, yerr=[2 * v for v in se], color=col, label=f"ABNB k, {wt} (±2 HAC se)", capsize=3)
        if len(pk):
            for tic, mk, col in (("BKNG", "o", "#d62728"), ("EXPE", "s", "#2ca02c")):
                s = pk[(pk["ticker"] == tic) & (pk["weighting"] == "rw")].set_index("measure")
                if "opex_ex_cor" in s.index:
                    ax.scatter([x[-1] + 0.05], [s.loc["opex_ex_cor", "k"]], marker=mk, color=col, zorder=5, label=f"{tic} opex ex CoR k")
                if "advertising" in s.index:
                    ax.scatter([x[3] + 0.05], [s.loc["advertising", "k"]], marker=mk, color=col, zorder=5, label=f"{tic} advertising k")
        ax.axhline(0, color="k", lw=.8); ax.axhline(1, color="k", lw=.5, ls=":")
        ax.set_xticks(x); ax.set_xticklabels(labels); ax.set_ylabel("k: line y/y growth per 1.0 of revenue y/y growth")
        ax.set_title("M6: cost-line response to revenue growth, lag 0, y/y log growth 1Q22-2Q26 (n=18)")
        ax.legend(fontsize=8); ax.grid(alpha=.3); fig.tight_layout()
        fig.savefig(FIG / f"{SLUG}_k_by_line.png", dpi=130); plt.close(fig)
        # F2: backtest h=0
        fig, ax = plt.subplots(figsize=(10, 4.5))
        s = bt[(bt["spec_id"] == MAIN_SPEC) & (bt["prior_basis"] == "PIT") & (bt["horizon_q"] == 0)].sort_values("quarter")
        s = s[s["quarter"].isin(ACT.index)]
        ax.plot(s["quarter"], s["quarter"].map(ACT["adj_ebitda_margin_pct"]), "k-o", label="actual")
        ax.plot(s["quarter"], s["adj_ebitda_margin_pct"], "-s", color="#1f77b4", label=f"M6 {MAIN_SPEC} PIT h=0")
        s2 = bt[(bt["spec_id"] == "revknown_rw") & (bt["prior_basis"] == "PIT") & (bt["horizon_q"] == 0)].sort_values("quarter")
        s2 = s2[s2["quarter"].isin(ACT.index)]
        ax.plot(s2["quarter"], s2["adj_ebitda_margin_pct"], "-^", color="#ff7f0e", label="M6 revknown_rw (actual revenue)")
        ax.plot(s["quarter"], s["quarter"].map(sn), "--", color="#7f7f7f", label="seasonal naive y[q-4]")
        for q in SHOCK_2H22 + SHOCK_2025:
            if q in list(s["quarter"]):
                ax.axvspan(list(s["quarter"]).index(q) - 0.5, list(s["quarter"]).index(q) + 0.5, color="#ffcccc", alpha=.4)
        ax.set_ylabel("adj EBITDA margin, %"); ax.set_title("M6 cycle flex: h=0 backtest at guide dates 2022-05..2026-05 (PIT); shock quarters shaded")
        ax.legend(fontsize=8); ax.grid(alpha=.3); plt.xticks(rotation=45); fig.tight_layout()
        fig.savefig(FIG / f"{SLUG}_backtest_margin.png", dpi=130); plt.close(fig)
        # F3: scenarios
        fig, ax = plt.subplots(figsize=(10, 4.8))
        sq = scen[(scen["base"] == base_label) & (scen["quarter"] <= "2027Q4")]
        for sc, col in (("bear", "#d62728"), ("base", "#1f77b4"), ("bull", "#2ca02c")):
            for var, ls in (("held", ":"), ("flex", "-"), ("cut", "--")):
                s = sq[(sq["scenario"] == sc) & (sq["variant"] == var)].sort_values("quarter")
                ax.plot(s["quarter"], s["adj_ebitda_margin_pct"], ls, color=col, marker="o" if var == "flex" else None, ms=4,
                        label=f"{sc} / {var}")
        s = sq[(sq["scenario"] == "base") & (sq["variant"] == "flex")].sort_values("quarter")
        ax.plot(s["quarter"], s["cons_margin_pct"], "k-.", label="LSEG consensus (Sep 2026)")
        ax.set_ylabel("adj EBITDA margin, %"); ax.set_title(f"M6 scenario engine: 3Q26-4Q27 margin, base cost path = {base_label}")
        ax.legend(fontsize=7, ncol=3); ax.grid(alpha=.3); fig.tight_layout()
        fig.savefig(FIG / f"{SLUG}_scenarios.png", dpi=130); plt.close(fig)
    except Exception as e:  # pragma: no cover
        print(f"  figure skipped: {e}")

    # ---- scoreboard -------------------------------------------------------------------------------------
    print("  running score.py ...")
    rc = subprocess.run([sys.executable, str(HARNESS / "score.py")], cwd=str(REPO), capture_output=True, text=True)
    print(rc.stdout[-1500:])
    if rc.returncode != 0:
        print(rc.stderr[-3000:])
        return rc.returncode
    sb = pd.read_csv(MB / "10_harness_margin" / "scoreboard_margin.csv")
    sb[sb["method"] == METHOD].to_csv(OUT / f"{SLUG}_scoreboard_rows.csv", index=False)
    # T3 from the by-quarter file
    bq = pd.read_csv(MB / "10_harness_margin" / "scoreboard_by_quarter.csv")
    t3 = bq[(bq["method"] == METHOD) & (bq["target"] == "adj_ebitda_margin_pct") & (bq["horizon_q"] == 0)
            & (bq["prior_basis"] == "PIT") & (bq["quarter"].isin(SHOCK_2025))]
    t3.to_csv(OUT / f"{SLUG}_test_T3_rows.csv", index=False)
    json.dump({"built": f"{t0:%Y-%m-%d %H:%M:%S}", "n_forecast_rows": int(len(wide)), "n_registry_rows": int(len(long)),
               "specs": list(SPECS), "main_spec": MAIN_SPEC, "engine_base": base_label, "k_main": k_main,
               "k_lags_dl": {k: list(v) for k, v in k_lags.items()}, "cut_caps": CUT_CAPS, "fy26_floor": FY26_FLOOR,
               "fy27_target": FY27_TARGET, "cut_first_q": CUT_FIRST_Q},
              open(OUT / f"{SLUG}_build.json", "w"), indent=2)
    print(f"done in {(_dt.datetime.now() - t0).total_seconds():.0f}s")
    return 0


if __name__ == "__main__":
    sys.exit(main())
