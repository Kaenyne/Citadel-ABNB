"""WS03 build: derive the point-in-time consensus panel, surprise history, revision paths, surprise
statistics, current consensus and the Bloomberg anchoring test from the raw LSEG pulls.

Runs under the repo venv (pandas 3) or py -3.13 (pandas 2.3). No licensed raw rows leave data/raw:
only values stamped at guide/print dates, per-quarter summaries and statistics are written to
data/processed/margin_build/03_consensus_pit/. The daily derived path (licensed) stays in data/raw.
"""
from __future__ import annotations

import datetime as dt
import json
import re
import sys
from pathlib import Path

import numpy as np
import pandas as pd

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[3]
RAW = REPO / "data" / "raw" / "margin_build" / "03_consensus_pit"
OUT = REPO / "data" / "processed" / "margin_build" / "03_consensus_pit"
OUT.mkdir(parents=True, exist_ok=True)

CALENDAR = REPO / "data" / "processed" / "forecast_methods" / "harness" / "calendar.csv"
COST_STACK = REPO / "data" / "processed" / "abnb_quarterly_cost_stack_exsbc.csv"
KPI = REPO / "data" / "processed" / "overnight" / "02_kpi_panel_quarterly.csv"
LEDGER = REPO / "data" / "processed" / "overnight" / "02_guidance_ledger.csv"
CONS16 = REPO / "data" / "processed" / "overnight" / "16_consensus_at_print_merged.csv"
L0 = REPO / "data" / "processed" / "forecast_methods" / "L0" / "L0_vintage_register.csv"
BBG = (REPO / "data" / "raw" / "theo_onedrive" / "AIRBNB DATA" / "raw_expansion_licensed" / "v2_2026-09-05"
       / "bloomberg" / "bbg_extracted_long.csv")

TODAY = dt.date(2026, 9, 12)
MUSD = ["ebitdamean", "ebitdamedian", "ebitdahigh", "ebitdalow", "ebitdastddev", "ebitdareportedmean",
        "revenuemean", "revenuemedian", "revenuehigh", "revenuelow", "revenuestddev",
        "ebitmean", "netprofitmean", "fcfmean", "cogsmean", "grossincomemean", "pretaxprofitmean", "capexmean",
        "ebitdaactvalue", "revenueactvalue", "ebitactvalue", "netprofitactvalue", "fcfactvalue"]

# --------------------------------------------------------------------------------------- helpers

def canon_fperiod(s: str) -> str:
    """'FY2023Q1' -> '2023Q1'; 'FY2026' -> 'FY2026'."""
    if not isinstance(s, str):
        return None
    m = re.match(r"^FY(\d{4})Q([1-4])$", s)
    if m:
        return f"{m.group(1)}Q{m.group(2)}"
    m = re.match(r"^FY(\d{4})$", s)
    if m:
        return f"FY{m.group(1)}"
    return s


def short_q(q: str) -> str:
    return f"{q[5]}Q{q[2:4]}"


def long_q(q: str) -> str:
    m = re.match(r"^([1-4])Q(\d{2})$", q)
    return f"20{m.group(2)}Q{m.group(1)}"


def qshift(q: str, k: int) -> str:
    y, n = int(q[:4]), int(q[5])
    i = y * 4 + n - 1 + k
    return f"{i // 4}Q{i % 4 + 1}"


def load_group(ric: str, grp: str, period: str, frq: str) -> pd.DataFrame | None:
    p = RAW / f"{ric}_{grp}_{period}_{frq}.csv"
    if not p.exists():
        return None
    df = pd.read_csv(p)
    for c in df.columns:
        if c.endswith("_date") or c.endswith("_calcdate") or c.endswith("_pe"):
            df[c] = pd.to_datetime(df[c], errors="coerce")
    first = [c for c in df.columns if c.endswith("_calcdate")][0]
    df = df.rename(columns={first: "calcdate",
                            first.replace("_calcdate", "_fperiod"): "fperiod",
                            first.replace("_calcdate", "_pe"): "period_end"})
    df["period"] = df["fperiod"].map(canon_fperiod)
    for c in MUSD:
        if c in df.columns:
            df[c] = pd.to_numeric(df[c], errors="coerce") / 1e6
    return df


def load_abnb_panel() -> pd.DataFrame:
    """Long panel keyed by (calcdate, period) with every consensus field, built from all period labels."""
    frames = []
    for period in ["FQ1", "FQ2", "FQ3", "FQ4", "FY1", "FY2", "FY3"]:
        parts = []
        for grp in ["ebitda", "reveps", "other", "other_n"]:
            g = load_group("abnb", grp, period, "D")
            if g is None:
                continue
            g = g.drop(columns=[c for c in ["ric", "frq"] if c in g.columns])
            if parts:
                g = g.drop(columns=[c for c in ["fperiod", "period_end", "period", "period_label"] if c in g.columns])
            parts.append(g)
        if not parts:
            continue
        m = parts[0]
        for g in parts[1:]:
            m = m.merge(g, on="calcdate", how="outer")
        frames.append(m)
    panel = pd.concat(frames, ignore_index=True)
    panel = panel.dropna(subset=["calcdate", "period"])
    # rank labels so that the nearest label wins if the same (calcdate, period) appears twice
    rank = {"FQ1": 1, "FQ2": 2, "FQ3": 3, "FQ4": 4, "FY1": 1, "FY2": 2, "FY3": 3}
    panel["_r"] = panel["period_label"].map(rank)
    panel = panel.sort_values(["calcdate", "period", "_r"]).drop_duplicates(["calcdate", "period"], keep="first")
    panel = panel.drop(columns="_r").reset_index(drop=True)
    panel["implied_margin_pct"] = 100 * panel["ebitdamean"] / panel["revenuemean"]
    return panel


def load_actuals() -> pd.DataFrame:
    parts = []
    for period in ["FQ0", "FY0"]:
        g = load_group("abnb", "actual", period, "D")
        if g is None:
            continue
        keep = ["period", "period_end"] + [c for c in g.columns if "actvalue" in c]
        g = g[keep].dropna(subset=["period"]).drop_duplicates("period", keep="last")
        parts.append(g)
    a = pd.concat(parts, ignore_index=True)
    a = a.rename(columns={"ebitdaactvalue": "lseg_act_ebitda", "ebitdaactvalue_date": "lseg_act_ebitda_reported",
                          "revenueactvalue": "lseg_act_revenue", "revenueactvalue_date": "lseg_act_revenue_reported",
                          "epsactvalue": "lseg_act_eps", "epsactvalue_date": "lseg_act_eps_reported",
                          "ebitactvalue": "lseg_act_ebit", "ebitactvalue_date": "lseg_act_ebit_reported",
                          "netprofitactvalue": "lseg_act_netprofit", "netprofitactvalue_date": "lseg_act_netprofit_reported",
                          "fcfactvalue": "lseg_act_fcf", "fcfactvalue_date": "lseg_act_fcf_reported"})
    return a


class PIT:
    """Point-in-time lookups on the ABNB panel."""

    def __init__(self, panel: pd.DataFrame):
        self.panel = panel
        self.tdays = panel["calcdate"].drop_duplicates().sort_values().to_numpy(dtype="datetime64[ns]")
        self.by = {k: v.set_index("calcdate").sort_index() for k, v in panel.groupby("period")}

    def tday_on_or_before(self, d) -> pd.Timestamp:
        if d is None or pd.isna(d):
            return None
        d64 = pd.Timestamp(d).to_datetime64().astype("datetime64[ns]")
        i = int(np.searchsorted(self.tdays, d64, side="right")) - 1
        return pd.Timestamp(self.tdays[i]) if i >= 0 else None

    def tday_offset(self, d, k: int) -> pd.Timestamp:
        """k trading days after (k>0) / before (k<0) the last trading day on or before d."""
        base = self.tday_on_or_before(d)
        if base is None:
            return None
        i = int(np.searchsorted(self.tdays, base.to_datetime64().astype("datetime64[ns]"))) + k
        i = min(max(i, 0), len(self.tdays) - 1)
        return pd.Timestamp(self.tdays[i])

    def at(self, period: str, d) -> pd.Series | None:
        """Row for `period` at the last trading day on or before d (exact row date match)."""
        if period not in self.by:
            return None
        tbl = self.by[period]
        td = self.tday_on_or_before(d)
        if td is None or td not in tbl.index:
            return None
        r = tbl.loc[td].copy()
        r["calcdate_used"] = td
        return r


def stamp(r: pd.Series | None, prefix: str, ref_date) -> dict:
    """Flatten a panel row into the at-dates schema."""
    o = {}
    if r is None:
        return o
    ref = pd.Timestamp(ref_date)
    o["calcdate_used"] = r.get("calcdate_used")
    for f, name in [("ebitda", "ebitda"), ("revenue", "revenue"), ("eps", "eps")]:
        o[f"{name}_mean"] = r.get(f"{f}mean")
        o[f"{name}_median"] = r.get(f"{f}median")
        o[f"{name}_n"] = r.get(f"{f}numofest")
        o[f"{name}_sd"] = r.get(f"{f}stddev")
        if f != "eps":
            o[f"{name}_high"] = r.get(f"{f}high")
            o[f"{name}_low"] = r.get(f"{f}low")
        od = r.get(f"{f}mean_date")
        o[f"{name}_obs_date"] = od
        o[f"{name}_staleness_days"] = (ref - pd.Timestamp(od)).days if pd.notna(od) else np.nan
    o["implied_margin_pct"] = 100 * r.get("ebitdamean") / r.get("revenuemean") if pd.notna(r.get("revenuemean")) else np.nan
    o["lseg_margin_mean_pct"] = r.get("ebitdamarginmean")
    o["ebitda_reported_mean"] = r.get("ebitdareportedmean")
    for f in ["ebit", "netprofit", "fcf", "cogs", "grossincome", "pretaxprofit", "capex"]:
        o[f"{f}_mean"] = r.get(f"{f}mean")
        o[f"{f}_obs_date"] = r.get(f"{f}mean_date")
        if f"{f}numofest" in r.index:
            o[f"{f}_n"] = r.get(f"{f}numofest")
    return o


# --------------------------------------------------------------------------------------- build

def build():
    panel = load_abnb_panel()
    actuals = load_actuals()
    pit = PIT(panel)
    cal = pd.read_csv(CALENDAR, parse_dates=["print_date", "guide_date"])
    cal = cal[cal["print_date"] <= pd.Timestamp("2026-08-06")].copy()
    cost = pd.read_csv(COST_STACK)
    cost["quarter_l"] = cost["quarter"].map(long_q)
    kpi = pd.read_csv(KPI)
    kpi["quarter_l"] = kpi["quarter"].map(long_q)
    ledger = pd.read_csv(LEDGER, parse_dates=["print_date"])
    c16 = pd.read_csv(CONS16, parse_dates=["print_date"])

    # ---- 1. consensus at dates ---------------------------------------------------------------
    rows = []
    events = [(r.print_date, r.print_quarter, "print+guide") for r in cal.itertuples()]
    events.append((pd.Timestamp(TODAY), "2026Q2", "current"))
    for d, printed_q, kind in events:
        guided_q = qshift(printed_q, 1)
        fy_cur = f"FY{guided_q[:4]}"
        fy_next = f"FY{int(guided_q[:4]) + 1}"
        fy_next2 = f"FY{int(guided_q[:4]) + 2}"
        d_prev = pit.tday_offset(d, -1)
        d_p5 = pit.tday_offset(d, 5)
        targets = []
        if kind == "print+guide":
            targets += [(printed_q, "printed_q_at_print", d_prev),
                        (guided_q, "guided_q_pre_guide", d_prev),
                        (guided_q, "guided_q_print_day", d),
                        (guided_q, "guided_q_post_guide_5td", d_p5),
                        (qshift(guided_q, 1), "next_q_pre_guide", d_prev),
                        (qshift(guided_q, 1), "next_q_post_guide_5td", d_p5),
                        (fy_cur, "fy_current_pre_guide", d_prev),
                        (fy_cur, "fy_current_post_guide_5td", d_p5),
                        (fy_next, "fy_next_pre_guide", d_prev),
                        (fy_next, "fy_next_post_guide_5td", d_p5)]
            if printed_q.endswith("Q4"):
                targets.append((f"FY{printed_q[:4]}", "printed_fy_at_print", d_prev))
        else:
            targets += [(guided_q, "current_q", d), (qshift(guided_q, 1), "current_next_q", d),
                        (fy_cur, "current_fy", d), (fy_next, "current_fy_next", d), (fy_next2, "current_fy_next2", d)]
        for tp, role, dd in targets:
            r = pit.at(tp, dd)
            o = {"date": d.date(), "date_kind": kind, "printed_quarter": printed_q, "guided_quarter": guided_q,
                 "target_period": tp, "target_role": role, "lookup_date": pd.Timestamp(dd).date(),
                 "vendor": "LSEG", "field_basis": "TR.<Metric>Mean via lseg-data desktop; period from .fperiod",
                 "found": r is not None}
            o.update(stamp(r, "", dd))
            rows.append(o)
    at_dates = pd.DataFrame(rows)
    at_dates.to_csv(OUT / "03_consensus_at_dates.csv", index=False)

    # ---- 2. surprise history ------------------------------------------------------------------
    sh = []
    prints = cal[(cal["print_quarter"] >= "2021Q1")].copy()
    for r in prints.itertuples():
        q, d = r.print_quarter, r.print_date
        d_prev = pit.tday_offset(d, -1)
        c_print = pit.at(q, d_prev)
        # prior guide date = the previous print in the calendar
        prev = cal[cal["print_quarter"] == qshift(q, -1)]
        g_date = prev["print_date"].iloc[0] if len(prev) else None
        c_guide = pit.at(q, pit.tday_offset(g_date, -1)) if g_date is not None else None
        c_post = pit.at(q, pit.tday_offset(g_date, 5)) if g_date is not None else None
        cs = cost[cost["quarter_l"] == q]
        kp = kpi[kpi["quarter_l"] == q]
        act_e = float(cs["adj_ebitda"].iloc[0]) if len(cs) else (float(kp["adj_ebitda_musd"].iloc[0]) if len(kp) else np.nan)
        act_r = float(cs["revenue_musd"].iloc[0]) if len(cs) else (float(kp["revenue_musd"].iloc[0]) if len(kp) else np.nan)
        act_fcf = float(kp["fcf_musd"].iloc[0]) if len(kp) and pd.notna(kp["fcf_musd"].iloc[0]) else np.nan
        act_oi = float(kp["operating_income_musd"].iloc[0]) if len(kp) and pd.notna(kp["operating_income_musd"].iloc[0]) else np.nan
        la = actuals[actuals["period"] == q]
        o = {"print_quarter": q, "print_date": d.date(), "prior_guide_date": g_date.date() if g_date is not None else None,
             "actual_adj_ebitda_musd": act_e, "actual_revenue_musd": act_r, "actual_margin_pct": 100 * act_e / act_r,
             "actual_fcf_musd": act_fcf, "actual_operating_income_musd": act_oi,
             "lseg_act_ebitda_musd": float(la["lseg_act_ebitda"].iloc[0]) if len(la) else np.nan,
             "lseg_act_eps_usd": float(la["lseg_act_eps"].iloc[0]) if len(la) else np.nan,
             "lseg_act_fcf_musd": float(la["lseg_act_fcf"].iloc[0]) if len(la) else np.nan,
             "lseg_report_timestamp": la["lseg_act_ebitda_reported"].iloc[0] if len(la) else None}
        if c_print is not None:
            o.update({"cons_ebitda_at_print_musd": c_print["ebitdamean"], "cons_ebitda_median_musd": c_print["ebitdamedian"],
                      "cons_ebitda_n": c_print["ebitdanumofest"], "cons_ebitda_sd_musd": c_print["ebitdastddev"],
                      "cons_ebitda_obs_date": c_print["ebitdamean_date"].date() if pd.notna(c_print["ebitdamean_date"]) else None,
                      "cons_ebitda_staleness_days": (d_prev - c_print["ebitdamean_date"]).days if pd.notna(c_print["ebitdamean_date"]) else np.nan,
                      "cons_revenue_at_print_musd": c_print["revenuemean"], "cons_revenue_n": c_print["revenuenumofest"],
                      "cons_revenue_obs_date": c_print["revenuemean_date"].date() if pd.notna(c_print["revenuemean_date"]) else None,
                      "cons_eps_at_print_usd": c_print["epsmean"], "cons_fcf_at_print_musd": c_print.get("fcfmean"),
                      "cons_ebit_at_print_musd": c_print.get("ebitmean"),
                      "street_margin_pct": 100 * c_print["ebitdamean"] / c_print["revenuemean"],
                      "lseg_margin_mean_field_pct": c_print.get("ebitdamarginmean"),
                      "lookup_date_at_print": d_prev.date()})
        if c_guide is not None:
            o.update({"cons_ebitda_at_guide_musd": c_guide["ebitdamean"], "cons_revenue_at_guide_musd": c_guide["revenuemean"],
                      "street_margin_at_guide_pct": 100 * c_guide["ebitdamean"] / c_guide["revenuemean"]})
        if c_post is not None:
            o.update({"cons_ebitda_post_guide_5td_musd": c_post["ebitdamean"], "cons_revenue_post_guide_5td_musd": c_post["revenuemean"],
                      "street_margin_post_guide_pct": 100 * c_post["ebitdamean"] / c_post["revenuemean"]})
        sh.append(o)
    sh = pd.DataFrame(sh)
    sh["ebitda_surprise_musd"] = sh["actual_adj_ebitda_musd"] - sh["cons_ebitda_at_print_musd"]
    sh["ebitda_surprise_pct"] = 100 * sh["ebitda_surprise_musd"] / sh["cons_ebitda_at_print_musd"].abs()
    sh["revenue_surprise_musd"] = sh["actual_revenue_musd"] - sh["cons_revenue_at_print_musd"]
    sh["revenue_surprise_pct"] = 100 * sh["revenue_surprise_musd"] / sh["cons_revenue_at_print_musd"]
    sh["margin_surprise_pts"] = sh["actual_margin_pct"] - sh["street_margin_pct"]
    sh["implied_incremental_margin_pct"] = np.where(sh["revenue_surprise_musd"].abs() >= 10,
                                                    100 * sh["ebitda_surprise_musd"] / sh["revenue_surprise_musd"], np.nan)
    sh["street_revision_incremental_margin_pct"] = np.where(
        (sh["cons_revenue_at_print_musd"] - sh["cons_revenue_at_guide_musd"]).abs() >= 10,
        100 * (sh["cons_ebitda_at_print_musd"] - sh["cons_ebitda_at_guide_musd"]) /
        (sh["cons_revenue_at_print_musd"] - sh["cons_revenue_at_guide_musd"]), np.nan)
    sh["eps_surprise_usd"] = sh["lseg_act_eps_usd"] - sh["cons_eps_at_print_usd"]
    sh["fcf_surprise_musd"] = sh["actual_fcf_musd"] - sh["cons_fcf_at_print_musd"]
    sh["lseg_vs_letter_ebitda_diff_musd"] = sh["lseg_act_ebitda_musd"] - sh["actual_adj_ebitda_musd"]
    # guide-implied margin from the ledger
    gi = []
    for r in sh.itertuples():
        q = r.print_quarter
        rows_l = ledger[(ledger["target_period"] == short_q(q)) &
                        (ledger["metric"].isin(["adj_ebitda_margin_pct", "adj_ebitda_margin_yoy_pts", "adj_ebitda_usd_m"])) &
                        (ledger["print_date"] < pd.Timestamp(r.print_date))]
        prior = cost[cost["quarter_l"] == qshift(q, -4)]
        m_ly = float(prior["adj_ebitda_margin_pct"].iloc[0]) if len(prior) else (float(kpi[kpi["quarter_l"] == qshift(q, -4)]["adj_ebitda_margin_pct"].iloc[0]) if len(kpi[kpi["quarter_l"] == qshift(q, -4)]) else np.nan)
        val, typ, qt = np.nan, None, None
        for g in rows_l.sort_values("print_date").itertuples():
            v = g.value_mid if pd.notna(g.value_mid) else (g.value_low if pd.notna(g.value_low) else g.value_high)
            if g.metric == "adj_ebitda_margin_pct" and pd.notna(v):
                val, typ, qt = v, f"{g.guide_type}:margin_pct", g.quote
            elif g.metric == "adj_ebitda_margin_yoy_pts" and pd.notna(v) and pd.notna(m_ly):
                val, typ, qt = m_ly + v, f"{g.guide_type}:yoy_pts(+{v} on {m_ly:.1f})", g.quote
            elif g.metric == "adj_ebitda_usd_m" and pd.notna(v):
                rev_mid = cal[cal["next_quarter_guided"] == q]["guide_mid"]
                if len(rev_mid) and pd.notna(rev_mid.iloc[0]):
                    val, typ, qt = 100 * v / float(rev_mid.iloc[0]), f"{g.guide_type}:usd_m/{rev_mid.iloc[0]:.0f} guide mid", g.quote
            elif g.metric == "adj_ebitda_margin_yoy_pts" and pd.isna(v):
                typ = typ or f"{g.guide_type}:directional"
                qt = qt or g.quote
        gi.append({"guide_implied_margin_pct": val, "guide_implied_type": typ, "guide_quote": qt, "margin_ly_pct": m_ly})
    sh = pd.concat([sh, pd.DataFrame(gi)], axis=1)
    sh["actual_vs_guide_implied_pts"] = sh["actual_margin_pct"] - sh["guide_implied_margin_pct"]
    sh["street_vs_guide_implied_pts"] = sh["street_margin_pct"] - sh["guide_implied_margin_pct"]
    # repo comparison (16_consensus_at_print_merged)
    c16m = c16[["print_quarter", "cons_adj_ebitda_musd", "cons_revenue_musd", "cons_eps_usd", "cons_revenue_vendor"]].rename(
        columns={"cons_adj_ebitda_musd": "repo16_cons_ebitda_musd", "cons_revenue_musd": "repo16_cons_revenue_musd",
                 "cons_eps_usd": "repo16_cons_eps_usd", "cons_revenue_vendor": "repo16_vendor"})
    sh = sh.merge(c16m, on="print_quarter", how="left")
    sh["lseg_vs_repo16_ebitda_pct"] = 100 * (sh["cons_ebitda_at_print_musd"] / sh["repo16_cons_ebitda_musd"] - 1)
    sh["lseg_vs_repo16_revenue_pct"] = 100 * (sh["cons_revenue_at_print_musd"] / sh["repo16_cons_revenue_musd"] - 1)
    sh["quarter_of_year"] = sh["print_quarter"].str[-1].astype(int)
    sh["in_W1"] = sh["print_quarter"].between("2023Q1", "2026Q2")
    sh["in_W2"] = sh["print_quarter"].between("2024Q1", "2026Q2")
    sh.to_csv(OUT / "03_surprise_history.csv", index=False)

    # ---- 3. revision paths -----------------------------------------------------------------------
    rp, daily = [], []
    for r in cal[cal["print_quarter"] >= "2021Q3"].itertuples():
        g_date, q = r.print_date, qshift(r.print_quarter, 1)
        nxt = cal[cal["print_quarter"] == q]
        p_date = nxt["print_date"].iloc[0] if len(nxt) else None
        tbl = pit.by.get(q)
        if tbl is None:
            continue
        end = pit.tday_offset(p_date, -1) if p_date is not None else pit.tday_on_or_before(TODAY)
        seg = tbl.loc[pit.tday_offset(g_date, -1):end]
        if seg.empty:
            continue
        v0 = seg["ebitdamean"].iloc[0]
        rv0 = seg["revenuemean"].iloc[0]
        def _at(k):
            dd = pit.tday_offset(g_date, k)
            return seg.loc[dd] if dd in seg.index else None
        a1, a5, a20 = _at(1), _at(5), _at(20)
        vend = seg["ebitdamean"].iloc[-1]
        rvend = seg["revenuemean"].iloc[-1]
        rp.append({"target_quarter": q, "guide_date": g_date.date(), "print_date": p_date.date() if p_date is not None else None,
                   "path_start": seg.index[0].date(), "path_end": seg.index[-1].date(), "n_trading_days": len(seg),
                   "ebitda_pre_guide_musd": v0,
                   "ebitda_post_guide_1td_musd": a1["ebitdamean"] if a1 is not None else np.nan,
                   "ebitda_post_guide_5td_musd": a5["ebitdamean"] if a5 is not None else np.nan,
                   "ebitda_post_guide_20td_musd": a20["ebitdamean"] if a20 is not None else np.nan,
                   "ebitda_at_print_musd": vend,
                   "guide_jump_5td_pct": 100 * (a5["ebitdamean"] / v0 - 1) if a5 is not None and v0 else np.nan,
                   "drift_post_guide_to_print_pct": 100 * (vend / a5["ebitdamean"] - 1) if a5 is not None and a5["ebitdamean"] else np.nan,
                   "total_drift_pct": 100 * (vend / v0 - 1) if v0 else np.nan,
                   "revenue_pre_guide_musd": rv0, "revenue_post_guide_5td_musd": a5["revenuemean"] if a5 is not None else np.nan,
                   "revenue_at_print_musd": rvend,
                   "revenue_guide_jump_5td_pct": 100 * (a5["revenuemean"] / rv0 - 1) if a5 is not None else np.nan,
                   "revenue_total_drift_pct": 100 * (rvend / rv0 - 1),
                   "margin_pre_guide_pct": 100 * v0 / rv0, "margin_post_guide_5td_pct": 100 * a5["ebitdamean"] / a5["revenuemean"] if a5 is not None else np.nan,
                   "margin_at_print_pct": 100 * vend / rvend,
                   "n_est_pre_guide": seg["ebitdanumofest"].iloc[0], "n_est_at_print": seg["ebitdanumofest"].iloc[-1],
                   "n_mean_changes": int((seg["ebitdamean"].diff().fillna(0) != 0).sum())})
        s = seg[["ebitdamean", "revenuemean", "ebitdanumofest", "ebitdamean_date"]].copy()
        s.insert(0, "target_period", q)
        s.insert(1, "path", "quarter")
        s["ebitda_index"] = 100 * s["ebitdamean"] / v0
        daily.append(s.reset_index())
    # FY paths: from the trading day before the prior-year Q4 print (pre-guide) to the day before the FY print
    for fy in range(2021, 2027):
        q4_prev = cal[cal["print_quarter"] == f"{fy - 1}Q4"]
        q4_this = cal[cal["print_quarter"] == f"{fy}Q4"]
        tbl = pit.by.get(f"FY{fy}")
        if tbl is None:
            continue
        start = pit.tday_offset(q4_prev["print_date"].iloc[0], -1) if len(q4_prev) else tbl.index[0]
        end = pit.tday_offset(q4_this["print_date"].iloc[0], -1) if len(q4_this) else pit.tday_on_or_before(TODAY)
        seg = tbl.loc[start:end]
        if seg.empty:
            continue
        v0, rv0 = seg["ebitdamean"].iloc[0], seg["revenuemean"].iloc[0]
        marks = {}
        for r in cal[(cal["print_date"] >= start) & (cal["print_date"] <= end)].itertuples():
            dd = pit.tday_offset(r.print_date, 5)
            if dd in seg.index:
                marks[f"after_{r.print_quarter}_print_musd"] = seg.loc[dd, "ebitdamean"]
                marks[f"after_{r.print_quarter}_print_margin_pct"] = 100 * seg.loc[dd, "ebitdamean"] / seg.loc[dd, "revenuemean"]
        act = actuals[actuals["period"] == f"FY{fy}"]
        rp.append({"target_quarter": f"FY{fy}", "guide_date": q4_prev["print_date"].iloc[0].date() if len(q4_prev) else None,
                   "print_date": q4_this["print_date"].iloc[0].date() if len(q4_this) else None,
                   "path_start": seg.index[0].date(), "path_end": seg.index[-1].date(), "n_trading_days": len(seg),
                   "ebitda_pre_guide_musd": v0, "ebitda_at_print_musd": seg["ebitdamean"].iloc[-1],
                   "total_drift_pct": 100 * (seg["ebitdamean"].iloc[-1] / v0 - 1),
                   "revenue_pre_guide_musd": rv0, "revenue_at_print_musd": seg["revenuemean"].iloc[-1],
                   "revenue_total_drift_pct": 100 * (seg["revenuemean"].iloc[-1] / rv0 - 1),
                   "margin_pre_guide_pct": 100 * v0 / rv0, "margin_at_print_pct": 100 * seg["ebitdamean"].iloc[-1] / seg["revenuemean"].iloc[-1],
                   "n_est_pre_guide": seg["ebitdanumofest"].iloc[0], "n_est_at_print": seg["ebitdanumofest"].iloc[-1],
                   "n_mean_changes": int((seg["ebitdamean"].diff().fillna(0) != 0).sum()),
                   "lseg_actual_ebitda_musd": float(act["lseg_act_ebitda"].iloc[0]) if len(act) else np.nan,
                   **marks})
        s = seg[["ebitdamean", "revenuemean", "ebitdanumofest", "ebitdamean_date"]].copy()
        s.insert(0, "target_period", f"FY{fy}")
        s.insert(1, "path", "fy")
        s["ebitda_index"] = 100 * s["ebitdamean"] / v0
        daily.append(s.reset_index())
    rp = pd.DataFrame(rp)
    rp.to_csv(OUT / "03_revision_paths.csv", index=False)
    pd.concat(daily, ignore_index=True).to_csv(RAW / "derived_daily_revision_paths_LICENSED.csv", index=False)

    # ---- 4. surprise stats ---------------------------------------------------------------------
    stats = surprise_stats(sh, rp, pit, cal, ledger)
    with open(OUT / "03_surprise_stats.json", "w") as fh:
        json.dump(stats, fh, indent=2, default=str)
    stats_tables_to_csv(stats)

    # ---- 5. current consensus ------------------------------------------------------------------
    current_consensus(pit, ledger)

    # ---- 6. L0 append candidates ----------------------------------------------------------------
    l0_candidates(sh, at_dates)

    # ---- 7. Bloomberg anchoring test ------------------------------------------------------------
    bloomberg_test(pit)

    # ---- 8. peers --------------------------------------------------------------------------------
    peers(pit)

    # ---- pass line --------------------------------------------------------------------------------
    pass_line(sh)
    return 0


# --------------------------------------------------------------------------------------- stats

def wmean(x, w):
    x, w = np.asarray(x, float), np.asarray(w, float)
    m = ~np.isnan(x)
    return float(np.sum(x[m] * w[m]) / np.sum(w[m])) if m.any() else np.nan


def wsd(x, w):
    x, w = np.asarray(x, float), np.asarray(w, float)
    m = ~np.isnan(x)
    if m.sum() < 2:
        return np.nan
    mu = wmean(x, w)
    return float(np.sqrt(np.sum(w[m] * (x[m] - mu) ** 2) / np.sum(w[m]) * m.sum() / (m.sum() - 1)))


def ols(y, x, w=None):
    y, x = np.asarray(y, float), np.asarray(x, float)
    m = ~(np.isnan(y) | np.isnan(x))
    y, x = y[m], x[m]
    n = len(y)
    if n < 4:
        return {"n": n}
    w = np.ones(n) if w is None else np.asarray(w, float)[m]
    X = np.column_stack([np.ones(n), x])
    W = np.diag(w)
    beta = np.linalg.solve(X.T @ W @ X, X.T @ W @ y)
    res = y - X @ beta
    s2 = (res @ (w * res)) / (n - 2)
    cov = s2 * np.linalg.inv(X.T @ W @ X)
    se = np.sqrt(np.diag(cov))
    yhat = X @ beta
    r2 = 1 - np.sum(w * res ** 2) / np.sum(w * (y - np.average(y, weights=w)) ** 2)
    return {"n": n, "alpha": float(beta[0]), "beta": float(beta[1]), "se_beta": float(se[1]),
            "t_beta": float(beta[1] / se[1]) if se[1] > 0 else np.nan, "r2": float(r2)}


def surprise_stats(sh: pd.DataFrame, rp: pd.DataFrame, pit: "PIT", cal: pd.DataFrame, ledger: pd.DataFrame) -> dict:
    s = sh.dropna(subset=["margin_surprise_pts"]).copy()
    s = s.sort_values("print_quarter").reset_index(drop=True)
    age = (len(s) - 1 - np.arange(len(s)))  # quarters back from the latest print
    s["w_recency"] = 0.5 ** (age / 4.0)
    out = {"n_prints": int(len(s)), "first": s["print_quarter"].iloc[0], "last": s["print_quarter"].iloc[-1]}

    def block(df, name):
        w = df["w_recency"].values
        return {"n": int(len(df)),
                "margin_surprise_mean_pts_ew": float(df["margin_surprise_pts"].mean()),
                "margin_surprise_sd_pts_ew": float(df["margin_surprise_pts"].std(ddof=1)) if len(df) > 1 else np.nan,
                "margin_surprise_mean_pts_rw": wmean(df["margin_surprise_pts"], w),
                "margin_surprise_sd_pts_rw": wsd(df["margin_surprise_pts"], w),
                "ebitda_surprise_mean_pct_ew": float(df["ebitda_surprise_pct"].mean()),
                "ebitda_surprise_sd_pct_ew": float(df["ebitda_surprise_pct"].std(ddof=1)) if len(df) > 1 else np.nan,
                "ebitda_surprise_mean_pct_rw": wmean(df["ebitda_surprise_pct"], w),
                "ebitda_surprise_mean_musd_ew": float(df["ebitda_surprise_musd"].mean()),
                "revenue_surprise_mean_pct_ew": float(df["revenue_surprise_pct"].mean()),
                "revenue_surprise_sd_pct_ew": float(df["revenue_surprise_pct"].std(ddof=1)) if len(df) > 1 else np.nan,
                "share_ebitda_beats": float((df["ebitda_surprise_musd"] > 0).mean()),
                "share_margin_beats": float((df["margin_surprise_pts"] > 0).mean()),
                "mean_abs_margin_surprise_pts": float(df["margin_surprise_pts"].abs().mean()),
                "median_margin_surprise_pts": float(df["margin_surprise_pts"].median())}

    out["all"] = block(s, "all")
    out["W1_2023Q1_2026Q2"] = block(s[s["in_W1"]], "W1")
    out["W2_2024Q1_2026Q2"] = block(s[s["in_W2"]], "W2")
    out["by_quarter_of_year"] = {f"Q{k}": block(g, f"Q{k}") for k, g in s.groupby("quarter_of_year")}
    out["by_year"] = {str(k): block(g, str(k)) for k, g in s.groupby(s["print_quarter"].str[:4])}
    # flow-through regressions
    out["flowthrough_musd_all"] = ols(s["ebitda_surprise_musd"], s["revenue_surprise_musd"])
    out["flowthrough_musd_all_rw"] = ols(s["ebitda_surprise_musd"], s["revenue_surprise_musd"], s["w_recency"])
    out["flowthrough_musd_W1"] = ols(s[s.in_W1]["ebitda_surprise_musd"], s[s.in_W1]["revenue_surprise_musd"])
    out["flowthrough_musd_W2"] = ols(s[s.in_W2]["ebitda_surprise_musd"], s[s.in_W2]["revenue_surprise_musd"])
    out["flowthrough_pct_all"] = ols(s["ebitda_surprise_pct"], s["revenue_surprise_pct"])
    out["flowthrough_pct_W1"] = ols(s[s.in_W1]["ebitda_surprise_pct"], s[s.in_W1]["revenue_surprise_pct"])
    out["flowthrough_pct_W2"] = ols(s[s.in_W2]["ebitda_surprise_pct"], s[s.in_W2]["revenue_surprise_pct"])
    out["margin_pts_on_rev_pct_all"] = ols(s["margin_surprise_pts"], s["revenue_surprise_pct"])
    out["margin_pts_on_rev_pct_W1"] = ols(s[s.in_W1]["margin_surprise_pts"], s[s.in_W1]["revenue_surprise_pct"])
    out["margin_pts_on_rev_pct_W2"] = ols(s[s.in_W2]["margin_surprise_pts"], s[s.in_W2]["revenue_surprise_pct"])
    # implied incremental margins
    ii = s.dropna(subset=["implied_incremental_margin_pct"])
    out["implied_incremental_margin_on_surprise"] = {
        "n": int(len(ii)), "median_pct": float(ii["implied_incremental_margin_pct"].median()),
        "mean_pct": float(ii["implied_incremental_margin_pct"].mean()),
        "iqr_pct": [float(ii["implied_incremental_margin_pct"].quantile(.25)), float(ii["implied_incremental_margin_pct"].quantile(.75))],
        "n_W2": int(ii["in_W2"].sum()), "median_pct_W2": float(ii[ii.in_W2]["implied_incremental_margin_pct"].median()) if ii["in_W2"].any() else np.nan}
    sr = s.dropna(subset=["street_revision_incremental_margin_pct"])
    out["street_revision_incremental_margin_guide_to_print"] = {
        "n": int(len(sr)), "median_pct": float(sr["street_revision_incremental_margin_pct"].median()),
        "mean_pct": float(sr["street_revision_incremental_margin_pct"].mean()),
        "iqr_pct": [float(sr["street_revision_incremental_margin_pct"].quantile(.25)), float(sr["street_revision_incremental_margin_pct"].quantile(.75))]}
    # actual y/y incremental margin for comparison (from actuals)
    a = s.set_index("print_quarter")
    inc = []
    for q in a.index:
        q4 = qshift(q, -4)
        if q4 in a.index:
            de = a.loc[q, "actual_adj_ebitda_musd"] - a.loc[q4, "actual_adj_ebitda_musd"]
            dr = a.loc[q, "actual_revenue_musd"] - a.loc[q4, "actual_revenue_musd"]
            inc.append(100 * de / dr if abs(dr) > 10 else np.nan)
    out["actual_yoy_incremental_margin"] = {"n": int(np.sum(~np.isnan(inc))), "median_pct": float(np.nanmedian(inc)),
                                           "mean_pct": float(np.nanmean(inc))}
    # autocorrelation of the margin error
    e = s["margin_surprise_pts"].values
    def acf(x, k):
        x = x - np.nanmean(x)
        return float(np.sum(x[k:] * x[:-k]) / np.sum(x * x)) if len(x) > k + 2 else np.nan
    out["margin_error_autocorr"] = {"n": int(len(e)), "lag1": acf(e, 1), "lag4": acf(e, 4),
                                    "sign_persistence_lag1": float(np.mean(np.sign(e[1:]) == np.sign(e[:-1]))),
                                    "sign_persistence_lag4": float(np.mean(np.sign(e[4:]) == np.sign(e[:-4]))),
                                    "lag1_W2": acf(s[s.in_W2]["margin_surprise_pts"].values, 1),
                                    "lag4_W2": acf(s[s.in_W2]["margin_surprise_pts"].values, 4),
                                    "approx_se_under_null": float(1 / np.sqrt(len(e)))}
    # EBITDA % surprise autocorr
    e2 = s["ebitda_surprise_pct"].values
    out["ebitda_pct_error_autocorr"] = {"lag1": acf(e2, 1), "lag4": acf(e2, 4)}
    # street margin vs guide-implied
    g = s.dropna(subset=["guide_implied_margin_pct"])
    out["street_vs_guide_implied"] = {"n": int(len(g)),
                                      "mean_street_minus_guide_pts": float(g["street_vs_guide_implied_pts"].mean()),
                                      "mean_actual_minus_guide_pts": float(g["actual_vs_guide_implied_pts"].mean()),
                                      "share_actual_above_guide_implied": float((g["actual_vs_guide_implied_pts"] > 0).mean()),
                                      "share_street_above_guide_implied": float((g["street_vs_guide_implied_pts"] > 0).mean()),
                                      "rows": g[["print_quarter", "guide_implied_type", "guide_implied_margin_pct", "street_margin_pct",
                                                 "actual_margin_pct"]].round(2).to_dict("records")}
    # FY floor anchoring: FY1 consensus margin vs the numeric FY floor in force at each date
    floors = ledger[(ledger["metric"] == "adj_ebitda_margin_pct") & (ledger["target_period"].str.startswith("FY")) &
                    (ledger["guide_type"].isin(["floor", "point"]))].copy()
    floors["floor"] = floors["value_low"].fillna(floors["value_mid"])
    anchor_rows = []
    for r in floors.sort_values("print_date").itertuples():
        fy = r.target_period
        tbl = pit.by.get(fy)
        if tbl is None:
            continue
        for k, lab in [(-1, "pre_guide"), (5, "post_guide_5td"), (60, "post_guide_60td")]:
            dd = pit.tday_offset(r.print_date, k)
            if dd in tbl.index:
                row = tbl.loc[dd]
                anchor_rows.append({"fy": fy, "guide_date": r.print_date.date(), "guide_type": r.guide_type, "floor_pct": r.floor,
                                    "when": lab, "lookup_date": dd.date(), "cons_margin_pct": 100 * row["ebitdamean"] / row["revenuemean"],
                                    "lseg_margin_mean_field_pct": row.get("ebitdamarginmean"),
                                    "gap_to_floor_pts": 100 * row["ebitdamean"] / row["revenuemean"] - r.floor,
                                    "cons_ebitda_musd": row["ebitdamean"], "cons_revenue_musd": row["revenuemean"], "n_est": row["ebitdanumofest"]})
    an = pd.DataFrame(anchor_rows)
    an.to_csv(OUT / "03_fy_floor_anchoring.csv", index=False)
    fy_act = {"FY2024": 36.4, "FY2025": 35.1}
    an5 = an[an["when"] == "post_guide_5td"]
    out["fy_floor_anchoring"] = {"n_guide_events": int(len(an5)),
                                 "mean_gap_post_guide_5td_pts": float(an5["gap_to_floor_pts"].mean()),
                                 "share_within_0p5pt_of_floor": float((an5["gap_to_floor_pts"].abs() <= 0.5).mean()),
                                 "share_within_1pt_of_floor": float((an5["gap_to_floor_pts"].abs() <= 1.0).mean()),
                                 "actual_minus_floor_pts": {k: v - float(floors[floors.target_period == k]["floor"].iloc[0]) for k, v in fy_act.items()
                                                            if (floors.target_period == k).any()},
                                 "rows": an5[["fy", "guide_date", "floor_pct", "cons_margin_pct", "gap_to_floor_pts", "n_est"]].round(2).to_dict("records")}
    # revision path summary
    q = rp[~rp["target_quarter"].str.startswith("FY")]
    out["revision_paths_quarters"] = {"n": int(len(q)), "median_guide_jump_5td_pct": float(q["guide_jump_5td_pct"].median()),
                                      "median_drift_post_guide_to_print_pct": float(q["drift_post_guide_to_print_pct"].median()),
                                      "mean_drift_post_guide_to_print_pct": float(q["drift_post_guide_to_print_pct"].mean()),
                                      "share_drift_negative": float((q["drift_post_guide_to_print_pct"] < 0).mean()),
                                      "median_total_drift_pct": float(q["total_drift_pct"].median()),
                                      "median_margin_change_guide_to_print_pts": float((q["margin_at_print_pct"] - q["margin_pre_guide_pct"]).median()),
                                      "median_n_trading_days": float(q["n_trading_days"].median())}
    f = rp[rp["target_quarter"].str.startswith("FY")]
    out["revision_paths_fy"] = f[["target_quarter", "ebitda_pre_guide_musd", "ebitda_at_print_musd", "total_drift_pct",
                                  "margin_pre_guide_pct", "margin_at_print_pct", "lseg_actual_ebitda_musd"]].round(2).to_dict("records")
    return out


def stats_tables_to_csv(stats: dict) -> None:
    rows = []
    for k in ["all", "W1_2023Q1_2026Q2", "W2_2024Q1_2026Q2"]:
        rows.append({"slice": k, **stats[k]})
    for k, v in stats["by_quarter_of_year"].items():
        rows.append({"slice": f"quarter_of_year_{k}", **v})
    for k, v in stats["by_year"].items():
        rows.append({"slice": f"year_{k}", **v})
    pd.DataFrame(rows).to_csv(OUT / "03_surprise_stats.csv", index=False)
    reg = []
    for k, v in stats.items():
        if k.startswith("flowthrough") or k.startswith("margin_pts_on"):
            reg.append({"regression": k, **v})
    pd.DataFrame(reg).to_csv(OUT / "03_flowthrough_regressions.csv", index=False)


def current_consensus(pit: "PIT", ledger: pd.DataFrame) -> None:
    d = pit.tday_on_or_before(TODAY)
    rows = []
    for tp, lab in [("2026Q3", "3Q26"), ("2026Q4", "4Q26"), ("FY2026", "FY26"), ("FY2027", "FY27"), ("FY2028", "FY28")]:
        r = pit.at(tp, d)
        if r is None:
            rows.append({"period": lab, "vendor": "LSEG", "found": False})
            continue
        o = {"period": lab, "vendor": "LSEG", "as_of_row_date": d.date(), "found": True}
        o.update({k: v for k, v in stamp(r, "", d).items()})
        rows.append(o)
    lseg = pd.DataFrame(rows)
    # Bloomberg side (local licensed file; only the current values are copied out)
    b = pd.read_csv(BBG)
    b = b[(b.sheet == "1_Consensus_TS") & (b.ticker == "ABNB US Equity")]
    last = b[b.obs_date == b.obs_date.max()]
    bmap = {"1FQ": "3Q26", "2FQ": "4Q26", "1FY": "FY26", "2FY": "FY27"}
    brows = []
    for fp, lab in bmap.items():
        x = last[last.fperiod == fp].set_index("field")["value"]
        brows.append({"period": lab, "vendor": "Bloomberg BEST (pull 2026-09-05, obs_date label 2026-09-30)",
                      "ebitda_mean": x.get("BEST_EBITDA"), "revenue_mean": x.get("BEST_SALES"), "eps_mean": x.get("BEST_EPS"),
                      "implied_margin_pct": 100 * x.get("BEST_EBITDA") / x.get("BEST_SALES") if pd.notna(x.get("BEST_EBITDA")) and pd.notna(x.get("BEST_SALES")) else np.nan,
                      "as_of_row_date": "2026-09-05 (pull date; series label 2026-09-30)", "found": True,
                      "ebitda_n": np.nan, "revenue_n": np.nan, "eps_n": np.nan})
    bbg = pd.DataFrame(brows)
    # management guide rows
    g = ledger[(ledger["print_date"] == pd.Timestamp("2026-08-06")) & (ledger["metric"].str.contains("ebitda|revenue", case=False))]
    grows = []
    for r in g.itertuples():
        grows.append({"period": r.target_period, "vendor": "Management guide (2Q26 letter, 2026-08-06)", "metric": r.metric,
                      "guide_type": r.guide_type, "value_low": r.value_low, "value_high": r.value_high, "value_mid": r.value_mid,
                      "unit": r.unit, "quote": r.quote, "found": True})
    mg = pd.DataFrame(grows)
    cur = pd.concat([lseg, bbg, mg], ignore_index=True)
    cur.to_csv(OUT / "03_current_consensus.csv", index=False)


def l0_candidates(sh: pd.DataFrame, at_dates: pd.DataFrame) -> None:
    cols = ["register_id", "vendor", "period", "metric", "value", "unit", "n_estimates", "as_of_timestamp", "url",
            "source_path", "role", "pit_usable", "vendor_attributed", "note"]
    src = "data/processed/margin_build/03_consensus_pit/03_consensus_at_dates.csv"
    rows = []
    for r in at_dates[at_dates["found"] == True].itertuples():  # noqa: E712
        role = {"printed_q_at_print": "at_print", "printed_fy_at_print": "at_print", "guided_q_pre_guide": "pre_guide",
                "fy_current_pre_guide": "pre_guide", "current_q": "current", "current_next_q": "current", "current_fy": "current",
                "current_fy_next": "current", "current_fy_next2": "current"}.get(r.target_role)
        if role is None:
            continue
        for metric, val, n, od, unit, field in [
                ("adj_ebitda", r.ebitda_mean, r.ebitda_n, r.ebitda_obs_date, "musd", "TR.EBITDAMean"),
                ("revenue", r.revenue_mean, r.revenue_n, r.revenue_obs_date, "musd", "TR.RevenueMean"),
                ("eps_adj", r.eps_mean, r.eps_n, r.eps_obs_date, "usd", "TR.EPSMean"),
                ("free_cash_flow", r.fcf_mean, getattr(r, "fcf_n", np.nan), r.fcf_obs_date, "musd", "TR.FCFMean"),
                ("operating_income", r.ebit_mean, getattr(r, "ebit_n", np.nan), r.ebit_obs_date, "musd", "TR.EBITMean")]:
            if pd.isna(val):
                continue
            rows.append({"register_id": f"LSEG-{role.upper()}-{r.target_period}-{metric}-{pd.Timestamp(r.lookup_date):%Y%m%d}",
                         "vendor": "LSEG", "period": r.target_period, "metric": metric, "value": round(float(val), 3), "unit": unit,
                         "n_estimates": n if pd.notna(n) else "", "as_of_timestamp": pd.Timestamp(od).date() if pd.notna(od) else pd.Timestamp(r.lookup_date).date(),
                         "url": f"lseg://desktop/get_data/{field}", "source_path": src, "role": role, "pit_usable": True, "vendor_attributed": True,
                         "note": f"WS03 LSEG desktop pull 2026-09-13; row date {pd.Timestamp(r.lookup_date).date()} ({r.target_role}); "
                                 f"field last changed {pd.Timestamp(od).date() if pd.notna(od) else 'n/a'}; $ fields in USD m; EBITDA is the Street adjusted basis"})
    pd.DataFrame(rows, columns=cols).to_csv(OUT / "03_L0_append_candidates.csv", index=False)


def bloomberg_test(pit: "PIT") -> None:
    """Is the Bloomberg obs_date series a rolling point-in-time series or a pull-date-anchored fixed period?"""
    b = pd.read_csv(BBG)
    b = b[(b.sheet == "1_Consensus_TS") & (b.ticker == "ABNB US Equity") &
          (b.field.isin(["BEST_EBITDA", "BEST_SALES", "BEST_EPS"])) & (b.fperiod.isin(["1FQ", "2FQ", "1FY", "2FY"]))].copy()
    b["obs_date"] = pd.to_datetime(b["obs_date"])
    fixed = {"1FQ": "2026Q3", "2FQ": "2026Q4", "1FY": "FY2026", "2FY": "FY2027"}
    fld = {"BEST_EBITDA": "ebitdamean", "BEST_SALES": "revenuemean", "BEST_EPS": "epsmean"}
    rows = []
    for r in b.itertuples():
        d = pit.tday_on_or_before(r.obs_date)
        if d is None:
            continue
        # hypothesis A: rolling (1FQ = LSEG FQ1 at that date, 1FY = FY1 ...)
        lab = {"1FQ": "FQ1", "2FQ": "FQ2", "1FY": "FY1", "2FY": "FY2"}[r.fperiod]
        pa = pit.panel[(pit.panel.calcdate == d) & (pit.panel.period_label == lab)]
        va = float(pa[fld[r.field]].iloc[0]) if len(pa) and pd.notna(pa[fld[r.field]].iloc[0]) else np.nan
        # hypothesis B: fixed period at pull date
        rb = pit.at(fixed[r.fperiod], d)
        vb = float(rb[fld[r.field]]) if rb is not None and pd.notna(rb.get(fld[r.field])) else np.nan
        rows.append({"obs_date": r.obs_date.date(), "field": r.field, "fperiod": r.fperiod, "bbg_value": r.value,
                     "lseg_rolling_period": pa["period"].iloc[0] if len(pa) else None, "lseg_rolling_value": va,
                     "lseg_fixed_period": fixed[r.fperiod], "lseg_fixed_value": vb,
                     "pct_diff_rolling": 100 * (r.value / va - 1) if va else np.nan,
                     "pct_diff_fixed": 100 * (r.value / vb - 1) if vb else np.nan})
    t = pd.DataFrame(rows)
    summ = t.groupby(["field", "fperiod"]).agg(n=("bbg_value", "size"),
                                                n_rolling=("pct_diff_rolling", lambda x: int(x.notna().sum())),
                                                mape_rolling=("pct_diff_rolling", lambda x: float(x.abs().mean())),
                                                n_fixed=("pct_diff_fixed", lambda x: int(x.notna().sum())),
                                                mape_fixed=("pct_diff_fixed", lambda x: float(x.abs().mean())),
                                                median_abs_fixed=("pct_diff_fixed", lambda x: float(x.abs().median()))).reset_index()
    t.to_csv(OUT / "03_bloomberg_anchoring_test_rows.csv", index=False)
    summ.to_csv(OUT / "03_bloomberg_anchoring_test.csv", index=False)


def peers(pit: "PIT") -> None:
    rows = []
    for ric in ["bkng", "expe"]:
        for period in ["FQ1", "FY1", "FY2"]:
            g = load_group(ric, "peer", period, "M")
            if g is None:
                continue
            g["implied_margin_pct"] = 100 * g["ebitdamean"] / g["revenuemean"]
            g["ticker"] = ric.upper()
            rows.append(g[["ticker", "period_label", "calcdate", "period", "ebitdamean", "ebitdanumofest", "revenuemean",
                           "ebitdamarginmean", "implied_margin_pct", "ebitdamean_date"]])
    # ABNB sampled at month ends from the daily panel
    a = pit.panel[pit.panel.period_label.isin(["FQ1", "FY1", "FY2"])].copy()
    a["ym"] = a["calcdate"].dt.to_period("M")
    a = a.sort_values("calcdate").groupby(["period_label", "ym"]).tail(1)
    a["ticker"] = "ABNB"
    rows.append(a[["ticker", "period_label", "calcdate", "period", "ebitdamean", "ebitdanumofest", "revenuemean",
                   "ebitdamarginmean", "implied_margin_pct", "ebitdamean_date"]])
    p = pd.concat(rows, ignore_index=True).rename(columns={"calcdate": "row_date", "ebitdamean": "ebitda_mean_musd",
                                                            "ebitdanumofest": "ebitda_n", "revenuemean": "revenue_mean_musd",
                                                            "ebitdamarginmean": "lseg_margin_mean_pct", "ebitdamean_date": "ebitda_obs_date"})
    p.to_csv(OUT / "03_peer_consensus_monthly.csv", index=False)


def pass_line(sh: pd.DataFrame) -> None:
    s = sh[(sh.print_quarter >= "2021Q1") & (sh.print_quarter <= "2026Q2")]
    fresh = s[(s["cons_ebitda_staleness_days"] <= 7)]
    cmp_ = s.dropna(subset=["repo16_cons_ebitda_musd"])
    within = cmp_[cmp_["lseg_vs_repo16_ebitda_pct"].abs() <= 3]
    res = {"prints_1Q21_2Q26": int(len(s)), "with_consensus": int(s["cons_ebitda_at_print_musd"].notna().sum()),
           "fresh_le_7d": int(len(fresh)), "pass_fresh_ge_18": bool(len(fresh) >= 18),
           "repo16_rows_compared": int(len(cmp_)), "within_3pct": int(len(within)),
           "pass_agree": bool(len(within) == len(cmp_)),
           "disagreements": cmp_[cmp_["lseg_vs_repo16_ebitda_pct"].abs() > 3][["print_quarter", "cons_ebitda_at_print_musd", "repo16_cons_ebitda_musd", "lseg_vs_repo16_ebitda_pct"]].round(2).to_dict("records"),
           "max_staleness_days": float(s["cons_ebitda_staleness_days"].max()),
           "stale_rows": s[s["cons_ebitda_staleness_days"] > 7][["print_quarter", "cons_ebitda_obs_date", "cons_ebitda_staleness_days"]].to_dict("records")}
    with open(OUT / "03_pass_line.json", "w") as fh:
        json.dump(res, fh, indent=2, default=str)
    print("PASS LINE:", json.dumps(res, default=str)[:600])


if __name__ == "__main__":
    sys.exit(build())
