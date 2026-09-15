"""targets.csv: the margin target panel, 1Q20-2Q26 actuals plus forward rows to 4Q27.

Primary source: WS02 `02_panel_quarterly.csv` (letter/XBRL panel), used only if it passes
`validate_ws02()`. Fallback: the pre-existing repo panels (cost stack ex-SBC 1Q21-2Q26, GAAP
cost lines 1Q20-2Q26, FCF bridge, capital-return panel, KPI panel). The chosen source and
the validation log are written to targets_source.json. Set env MARGIN_HARNESS_PANEL=fallback
to force the fallback (used by tests).

UNITS (also written to targets_units.csv):
  *_musd            USD millions, quarterly flow
  *_pct, *_pct_rev  percent (0-100), ratio to revenue of the same quarter
  *_per_night       USD per booked night (line / nights_m)
  eps_diluted       USD per diluted share, GAAP
  diluted_shares_m  weighted-average diluted shares, millions
  nights_m          millions; gbv_musd USD millions
Cash cost lines are GAAP line minus the SBC allocated to that line (the "ex-SBC" lines the
31-series notes use). ga_cash_musd INCLUDES the 4Q23 $931M lodging-tax reserve (it is in
GAAP G&A); ga_cash_ex_reserves_musd removes lodging-tax reserves (an adj-EBITDA add-back).
total_cash_costs_musd = revenue - adj EBITDA by identity (the exact cash cost total adj
EBITDA is measured against, restructuring and every add-back included).
"""
from __future__ import annotations

import datetime as _dt
import json
import os

import numpy as np
import pandas as pd

from . import paths as P
from .frozen import Q, load_frozen_calendar

FIRST_TARGET_Q = "2020Q1"
LAST_ACTUAL_Q = "2026Q2"
LAST_FORWARD_Q = "2027Q4"

LINES = ["cor", "ops", "pd", "sm", "ga"]
PROSPECTUS_DATE = _dt.date(2020, 12, 10)      # 424B4: first public disclosure of 1Q20/2Q20 quarterlies

META_COLS = ["quarter", "print_date", "knowable_from", "has_actual", "source"]

UNITS = {
    "revenue_musd": ("USD m", "revenue"),
    "nights_m": ("m", "nights and seats booked"),
    "gbv_musd": ("USD m", "gross booking value"),
    "adj_ebitda_musd": ("USD m", "adjusted EBITDA as reported in the letter"),
    "adj_ebitda_margin_pct": ("%", "100 * adj EBITDA / revenue"),
    "cor_cash_musd": ("USD m", "cost of revenue ex SBC"),
    "ops_cash_musd": ("USD m", "operations and support ex SBC"),
    "pd_cash_musd": ("USD m", "product development ex SBC"),
    "sm_cash_musd": ("USD m", "sales and marketing ex SBC"),
    "ga_cash_musd": ("USD m", "general and administrative ex SBC (includes 4Q23 lodging-tax reserve)"),
    "ga_cash_ex_reserves_musd": ("USD m", "G&A ex SBC ex lodging-tax reserves"),
    "total_cash_costs_musd": ("USD m", "revenue - adj EBITDA (identity)"),
    "sbc_musd": ("USD m", "stock-based compensation add-back"),
    "da_musd": ("USD m", "depreciation and amortisation"),
    "op_income_musd": ("USD m", "GAAP income from operations"),
    "op_margin_pct": ("%", "100 * op income / revenue"),
    "net_income_musd": ("USD m", "GAAP net income"),
    "eps_diluted": ("USD/share", "GAAP diluted EPS (fallback: net income / diluted shares where not reported)"),
    "fcf_musd": ("USD m", "free cash flow as reported (CFO - capex)"),
    "fcf_margin_pct": ("%", "100 * FCF / revenue"),
    "interest_income_musd": ("USD m", "interest income"),
    "tax_rate_pct": ("%", "100 * tax provision / pretax income (can be wild in small-pretax quarters)"),
    "tax_provision_musd": ("USD m", "income tax provision (benefit negative)"),
    "pretax_income_musd": ("USD m", "income before taxes"),
    "diluted_shares_m": ("m", "weighted-average diluted shares"),
    "cfo_musd": ("USD m", "cash from operations"),
    "capex_musd": ("USD m", "purchases of property and equipment"),
    "adj_ebitda_margin_yoy_pp": ("pp", "margin minus same quarter last year"),
}
for _ln in LINES:
    UNITS[f"{_ln}_cash_pct_rev"] = ("%", f"100 * {_ln}_cash_musd / revenue")
    UNITS[f"{_ln}_cash_per_night"] = ("USD/night", f"{_ln}_cash_musd / nights_m")
UNITS["total_cash_costs_pct_rev"] = ("%", "100 * total_cash_costs_musd / revenue")
UNITS["sbc_pct_rev"] = ("%", "100 * sbc / revenue")
UNITS["adj_ebitda_per_night"] = ("USD/night", "adj EBITDA / nights_m")
UNITS["revenue_per_night"] = ("USD/night", "revenue / nights_m")

TARGET_METRICS = list(UNITS)          # every scoreable column


# --------------------------------------------------------------------------- helpers
def q_range(a: str, b: str):
    return [Q.from_index(i) for i in range(Q.to_index(a), Q.to_index(b) + 1)]


def _print_dates() -> dict:
    cal = load_frozen_calendar()
    return {r.print_quarter: r.print_date for r in cal.itertuples()}


def _derive(t: pd.DataFrame) -> pd.DataFrame:
    """Ratios and per-night columns from the level columns."""
    rev = t["revenue_musd"]
    t["adj_ebitda_margin_pct"] = 100.0 * t["adj_ebitda_musd"] / rev
    t["op_margin_pct"] = 100.0 * t["op_income_musd"] / rev
    t["fcf_margin_pct"] = 100.0 * t["fcf_musd"] / rev
    t["total_cash_costs_musd"] = rev - t["adj_ebitda_musd"]
    t["total_cash_costs_pct_rev"] = 100.0 * t["total_cash_costs_musd"] / rev
    t["sbc_pct_rev"] = 100.0 * t["sbc_musd"] / rev
    for ln in LINES:
        t[f"{ln}_cash_pct_rev"] = 100.0 * t[f"{ln}_cash_musd"] / rev
        t[f"{ln}_cash_per_night"] = t[f"{ln}_cash_musd"] / t["nights_m"]
    t["adj_ebitda_per_night"] = t["adj_ebitda_musd"] / t["nights_m"]
    t["revenue_per_night"] = rev / t["nights_m"]
    with np.errstate(divide="ignore", invalid="ignore"):
        t["tax_rate_pct"] = 100.0 * t["tax_provision_musd"] / t["pretax_income_musd"]
    t = t.sort_values("quarter").reset_index(drop=True)
    t["adj_ebitda_margin_yoy_pp"] = t["adj_ebitda_margin_pct"] - t["adj_ebitda_margin_pct"].shift(4)
    return t


# --------------------------------------------------------------------------- WS02
def validate_ws02(p: pd.DataFrame) -> list:
    """Return a list of problems (empty == usable). Written to targets_source.json."""
    probs = []
    p = p.copy()
    p["q"] = p["quarter"].map(Q.canon)
    need_q = set(q_range(FIRST_TARGET_Q, LAST_ACTUAL_Q))
    missing = sorted(need_q - set(p["q"]))
    if missing:
        probs.append(f"missing quarters {missing}")
    win = p[p["q"].isin(q_range("2021Q1", LAST_ACTUAL_Q))]
    for c in ["revenue", "adj_ebitda_reported", "cor_cash", "ops_cash", "pd_cash", "sm_cash",
              "ga_cash", "sbc_recon", "da", "op_income", "net_income", "fcf_reported",
              "interest_income", "nights_m"]:
        if c not in p.columns:
            probs.append(f"column {c} absent")
            continue
        v = pd.to_numeric(win[c], errors="coerce")
        if v.isna().any():
            probs.append(f"{c} null in {win.loc[v.isna(), 'q'].tolist()}")
        if c in ("cor_cash", "ops_cash", "pd_cash", "sm_cash", "ga_cash", "da", "nights_m"):
            bad = win.loc[(v <= 0) | v.isna(), "q"].tolist()
            if bad:
                probs.append(f"{c} <= 0 in {bad}")
    if "rebuild_gap" in p.columns:
        g = pd.to_numeric(win["rebuild_gap"], errors="coerce").abs()
        bad = win.loc[g > 2.0, "q"].tolist()
        if bad:
            probs.append(f"|rebuild_gap| > 2 in {bad}")
    # cross-check adj EBITDA against the repo cost stack
    if P.SRC_FB_COST_STACK.exists():
        fb = pd.read_csv(P.SRC_FB_COST_STACK)
        fb["q"] = fb["quarter"].map(Q.canon)
        m = win.merge(fb[["q", "adj_ebitda"]], on="q", how="inner")
        d = (pd.to_numeric(m["adj_ebitda_reported"], errors="coerce") - m["adj_ebitda"]).abs()
        bad = m.loc[d > 1.5, "q"].tolist()
        if bad:
            probs.append(f"adj EBITDA differs from repo cost stack by > 1.5 in {bad}")
    return probs


def _from_ws02(p: pd.DataFrame) -> pd.DataFrame:
    p = p.copy()
    p["quarter"] = p["quarter"].map(Q.canon)
    t = pd.DataFrame({"quarter": p["quarter"]})

    def num(c):
        return pd.to_numeric(p[c], errors="coerce") if c in p.columns else pd.Series(np.nan, index=p.index)

    t["revenue_musd"] = num("revenue")
    t["nights_m"] = num("nights_m")
    t["gbv_musd"] = num("gbv_busd") * 1000.0
    t["adj_ebitda_musd"] = num("adj_ebitda_reported")
    for ln in LINES:
        t[f"{ln}_cash_musd"] = num(f"{ln}_cash")
    t["ga_cash_ex_reserves_musd"] = t["ga_cash_musd"] - num("lodging_tax_reserves").fillna(0.0)
    t["sbc_musd"] = num("sbc_recon").where(num("sbc_recon").notna(), num("sbc_total_is"))
    t["da_musd"] = num("da")
    t["op_income_musd"] = num("op_income")
    t["net_income_musd"] = num("net_income")
    t["eps_diluted"] = num("eps_diluted")
    t["fcf_musd"] = num("fcf_reported")
    t["interest_income_musd"] = num("interest_income")
    t["tax_provision_musd"] = num("tax_provision")
    t["pretax_income_musd"] = num("pretax_income")
    t["diluted_shares_m"] = num("shares_diluted_m")
    t["cfo_musd"] = num("cfo")
    t["capex_musd"] = num("capex")
    # WS02's Q4 share counts / EPS come from 10-K minus YTD and can be broken; patch from the
    # capital-return panel (letter values) where WS02 is null or implausible.
    t = _patch_shares_eps(t, "ws02")
    return t


# --------------------------------------------------------------------------- fallback
def _from_fallback() -> pd.DataFrame:
    cs = pd.read_csv(P.SRC_FB_COST_STACK)
    cs["quarter"] = cs["quarter"].map(Q.canon)
    cl = pd.read_csv(P.SRC_FB_COSTLINES)
    cl["quarter"] = cl["quarter"].map(Q.canon)
    fb = pd.read_csv(P.SRC_FB_FCF_BRIDGE)
    fb = fb[fb["period"].astype(str).str.match(r"^[1-4]Q[0-9][0-9]$")].copy()
    fb["quarter"] = fb["period"].map(Q.canon)
    kp = pd.read_csv(P.SRC_KPI_PANEL)
    kp["quarter"] = kp["quarter"].map(Q.canon)

    qs = q_range(FIRST_TARGET_Q, LAST_ACTUAL_Q)
    t = pd.DataFrame({"quarter": qs})
    cl_i = cl.set_index("quarter")
    cs_i = cs.set_index("quarter")
    fb_i = fb.set_index("quarter")
    kp_i = kp.set_index("quarter")

    def g(df, c):
        return t["quarter"].map(df[c]) if c in df.columns else pd.Series(np.nan, index=t.index)

    t["revenue_musd"] = g(cl_i, "revenue_musd")
    t["nights_m"] = g(kp_i, "nights_m")
    t["gbv_musd"] = g(kp_i, "gbv_musd")
    t["adj_ebitda_musd"] = g(cl_i, "adjusted_ebitda_musd")
    for ln in LINES:
        t[f"{ln}_cash_musd"] = g(cs_i, f"{ln}_cash")
    oa = g(cs_i, "other_addbacks").fillna(0.0)
    # lodging-tax reserves are not a column in the fallback stack; the only material case is
    # the 4Q23 $931M (other_addbacks 928). Approximate: strip other add-backs above $50M.
    t["ga_cash_ex_reserves_musd"] = t["ga_cash_musd"] - oa.where(oa > 50.0, 0.0)
    sbc_letter = g(cs_i, "sbc_total_letter")
    t["sbc_musd"] = sbc_letter.where(sbc_letter.notna(), g(cl_i, "stock_based_comp_total_musd"))
    t["da_musd"] = g(cs_i, "da")
    t["op_income_musd"] = g(cl_i, "operating_income_musd")
    ni = g(fb_i, "net_income")
    t["net_income_musd"] = ni.where(ni.notna(), g(kp_i, "net_income_musd"))
    fcf = g(fb_i, "fcf")
    t["fcf_musd"] = fcf.where(fcf.notna(), g(kp_i, "fcf_musd"))
    t["interest_income_musd"] = g(fb_i, "interest_income")
    # the FCF bridge signs the provision as a deduction (negative = expense); flip to provision
    tp = -g(fb_i, "tax_provision")
    t["tax_provision_musd"] = tp.where(tp.notna(), g(kp_i, "income_tax_musd"))
    t["pretax_income_musd"] = t["net_income_musd"] + t["tax_provision_musd"]
    t["diluted_shares_m"] = g(kp_i, "diluted_wa_shares_m")
    cfo = g(fb_i, "cfo")
    t["cfo_musd"] = cfo.where(cfo.notna(), g(kp_i, "cfo_musd"))
    cap = -g(fb_i, "capex")
    t["capex_musd"] = cap.where(cap.notna(), g(kp_i, "capex_musd"))
    t["eps_diluted"] = np.nan
    t = _patch_shares_eps(t, "fallback")
    return t


def _patch_shares_eps(t: pd.DataFrame, src: str) -> pd.DataFrame:
    """Diluted shares from the capital-return panel where missing/implausible; EPS computed
    as NI / diluted shares where not reported (GAAP diluted EPS uses basic shares in loss
    quarters, so the computed value is an approximation there; flagged in eps_source)."""
    if P.SRC_FB_CAPRET.exists():
        cr = pd.read_csv(P.SRC_FB_CAPRET)
        cr["quarter"] = cr["quarter"].map(Q.canon)
        cr_i = cr.set_index("quarter")
        sh = t["quarter"].map(cr_i["diluted_wa_shares_m"])
        bad = t["diluted_shares_m"].isna() | (t["diluted_shares_m"] < 100)
        t["diluted_shares_m"] = t["diluted_shares_m"].where(~bad, sh)
    comp = t["net_income_musd"] / t["diluted_shares_m"]
    t["eps_source"] = np.where(t["eps_diluted"].notna(), f"{src}:reported",
                               np.where(comp.notna(), "computed:ni_over_diluted_shares", "na"))
    t["eps_diluted"] = t["eps_diluted"].where(t["eps_diluted"].notna(), comp)
    return t


# --------------------------------------------------------------------------- build
def build_targets(write: bool = True):
    """Build targets.csv (+ units, source json). Returns (targets, source_info)."""
    P.ensure_dirs()
    force = os.environ.get("MARGIN_HARNESS_PANEL", "").strip().lower()
    info = {"built_at": _dt.datetime.now().isoformat(timespec="seconds"),
            "ws02_path": str(P.SRC_WS02_PANEL), "ws02_exists": P.SRC_WS02_PANEL.exists(),
            "forced": force or None}
    src = None
    t = None
    if force != "fallback" and P.SRC_WS02_PANEL.exists():
        p = pd.read_csv(P.SRC_WS02_PANEL)
        probs = validate_ws02(p)
        info["ws02_validation_problems"] = probs
        info["ws02_mtime"] = _dt.datetime.fromtimestamp(P.SRC_WS02_PANEL.stat().st_mtime).isoformat(timespec="seconds")
        if not probs:
            t = _from_ws02(p)
            src = "ws02"
    if src is None:
        t = _from_fallback()
        src = "fallback_repo_panels"
        info["fallback_files"] = [str(x) for x in (P.SRC_FB_COST_STACK, P.SRC_FB_COSTLINES,
                                                    P.SRC_FB_FCF_BRIDGE, P.SRC_FB_CAPRET,
                                                    P.SRC_KPI_PANEL)]
    info["source"] = src
    idx = t["quarter"].map(Q.to_index)
    t = t[(idx >= Q.to_index(FIRST_TARGET_Q)) & (idx <= Q.to_index(LAST_ACTUAL_Q))].copy()
    t = _derive(t)
    t["source"] = src
    # forward rows (no actuals) so LIVE registrations can find the quarter
    fwd = q_range(Q.shift(LAST_ACTUAL_Q, 1), LAST_FORWARD_Q)
    t = pd.concat([t, pd.DataFrame({"quarter": fwd})], ignore_index=True)
    pdm = _print_dates()
    t["print_date"] = t["quarter"].map(pdm)
    # 1Q20 and 2Q20 pre-date the frozen calendar; they became public in the IPO prospectus
    # (424B4, accession 0001193125-20-315318, filed 2020-12-10). Stamp them with that date.
    pre = t["print_date"].isna() & (t["quarter"].map(Q.to_index) < Q.to_index("2020Q3"))
    t.loc[pre, "print_date"] = PROSPECTUS_DATE
    t["knowable_from"] = t["print_date"]
    t["has_actual"] = t["adj_ebitda_musd"].notna() & t["print_date"].notna()
    metric_cols = [c for c in t.columns if c in UNITS]
    t.loc[~t["has_actual"], metric_cols] = np.nan
    t["source"] = t["source"].where(t["has_actual"], "forward_row")
    cols = META_COLS + [c for c in UNITS if c in t.columns] + ["eps_source"]
    t = t[cols].sort_values("quarter").reset_index(drop=True)
    if write:
        t.to_csv(P.OUT_TARGETS, index=False)
        pd.DataFrame([{"metric": k, "unit": v[0], "definition": v[1]} for k, v in UNITS.items()]
                     ).to_csv(P.OUT_TARGETS_UNITS, index=False)
        P.OUT_TARGETS_SOURCE.write_text(json.dumps(info, indent=2, default=str))
    return t, info


_CACHE = {}


def load_targets(refresh: bool = False) -> pd.DataFrame:
    if refresh:
        _CACHE.clear()
    if "t" in _CACHE:
        return _CACHE["t"]
    if not P.OUT_TARGETS.exists():
        build_targets()
    t = pd.read_csv(P.OUT_TARGETS)
    t["quarter"] = t["quarter"].map(Q.canon)
    for c in ("print_date", "knowable_from"):
        t[c] = pd.to_datetime(t[c], errors="coerce").dt.date
    _CACHE["t"] = t
    return t


def history_as_of(vintage_date, metric: str | None = None, targets: pd.DataFrame | None = None,
                  include_same_day: bool = True) -> pd.DataFrame:
    """PIT slice: quarters whose PRINT DATE is <= vintage_date (same-day letter included,
    the frozen harness convention; pass include_same_day=False for strict <)."""
    t = load_targets() if targets is None else targets
    vd = pd.to_datetime(vintage_date).date()
    ok = t["print_date"].map(lambda d: pd.notna(d) and ((d <= vd) if include_same_day else (d < vd)))
    h = t[ok & t["has_actual"]].sort_values("quarter").reset_index(drop=True)
    if metric is None:
        return h
    return h[["quarter", "print_date", metric]].dropna(subset=[metric]).reset_index(drop=True)


def series_as_of(vintage_date, metric: str, targets=None) -> pd.Series:
    h = history_as_of(vintage_date, metric, targets)
    return pd.Series(pd.to_numeric(h[metric]).to_numpy(dtype=float), index=h["quarter"].to_numpy())


def full_series(metric: str, targets=None) -> pd.Series:
    t = load_targets() if targets is None else targets
    t = t[t["has_actual"]].sort_values("quarter")
    return pd.Series(pd.to_numeric(t[metric], errors="coerce").to_numpy(dtype=float),
                     index=t["quarter"].to_numpy()).dropna()
