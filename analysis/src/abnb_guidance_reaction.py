"""Which guidance items move ABNB after a print? Day-1 and 5-session moves regressed on the guidance issued AT each print.

Features are built from data/processed/overnight/02_guidance_ledger.csv (statements issued at print P) and the
consensus file (next-quarter Street revenue at P). Reported-quarter beats from abnb_earnings_regressions are added
for comparison, so guidance and the reported quarter can be raced against each other.

Next-quarter guidance issued at P (target = P+1):
  nq_rev_guide_growth      guided revenue growth, midpoint of the range vs the target quarter's prior-year revenue (%)
  nq_guide_accel_pts       guided growth minus the growth just reported at P (pts)   "is the guide an acceleration?"
  guide_vs_street_pct      guide midpoint vs next-quarter Street revenue consensus (%)
  guide_below_street       1 if the midpoint is below the Street
  nq_range_width_pct       (high - low) / mid
  nq_nights_guide_pts      implied nights acceleration: bucket midpoint minus current nights growth, or +1/0/-1 x 2 for above/stable/below
  nq_nights_dir            +1 above, 0 stable/approx, -1 below (directional or bucket vs current growth)
  nq_margin_dir            +1 margin up (floor >= 0), 0 flat (point 0 or ceiling/floor at 0 both), -1 down (ceiling <= 0)
  nq_margin_guide_pts      guided y/y margin change where numeric (floor low / ceiling high / point)
  nq_adr_dir, nq_take_rate_dir   same +1/0/-1 encoding
Full-year guidance issued at P:
  fy_margin_delta_pts      change in the FY Adjusted EBITDA margin guide vs the prior statement (0 reiterated, NaN -> treated as 0 with fy_first_guide = 1)
  fy_margin_action         raised / reiterated / lowered / first
  fy_rev_delta_pts         change in the FY revenue-growth guide vs prior statement
  fy_rev_action            raised / reiterated / lowered / first / none
  fy_numeric_present       1 if any FY-target guide with a number was issued at P
  fy_margin_floor_vs_prior_fy   FY margin floor/point minus the prior fiscal year's actual margin (pts)
  new_investment_flag      1 if a new-business investment budget was guided at P
  sbc_guide_pct            FY SBC growth guide where given

Outputs: data/processed/abnb_guidance_reaction_panel.csv, data/processed/abnb_guidance_reaction_results.csv
Run: py -3.13 analysis/src/abnb_guidance_reaction.py
"""
from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pandas as pd
import statsmodels.api as sm
from scipy import stats

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "analysis/src"))
import abnb_earnings_regressions as reg  # noqa: E402

OUT_PANEL = ROOT / "data/processed/abnb_guidance_reaction_panel.csv"
OUT_RES = ROOT / "data/processed/abnb_guidance_reaction_results.csv"

QUARTERS = ["3Q20", "4Q20", "1Q21", "2Q21", "3Q21", "4Q21", "1Q22", "2Q22", "3Q22", "4Q22", "1Q23", "2Q23", "3Q23", "4Q23",
            "1Q24", "2Q24", "3Q24", "4Q24", "1Q25", "2Q25", "3Q25", "4Q25", "1Q26", "2Q26"]


def next_q(q: str) -> str:
    n, yy = int(q[0]), int(q[2:])
    return f"{n + 1}Q{yy}" if n < 4 else f"1Q{yy + 1}"


def dir_code(row) -> float:
    t, d = row.guide_type, str(row.direction)
    if t == "floor":
        return 1.0 if row.value_low >= 0 else 0.0
    if t == "ceiling":
        return -1.0 if row.value_high <= 0 else 0.0
    if t == "point":
        return float(np.sign(row.value_mid)) if pd.notna(row.value_mid) else 0.0
    if t in ("directional", "bucket", "qualitative"):
        if d in ("above", "up", "above_seq", "accelerate_vs_prior_q"):
            return 1.0
        if d in ("below", "down", "below_seq", "down_risk", "below_revenue_growth"):
            return -1.0
        if d in ("stable", "approx", "approx_seq"):
            return 0.0
    return np.nan


def build_panel() -> pd.DataFrame:
    base = reg.build_panel().set_index("quarter")
    kpi = pd.read_csv(ROOT / "data/processed/overnight/02_kpi_panel_quarterly.csv").set_index("quarter")
    ledger = pd.read_csv(ROOT / "data/processed/overnight/02_guidance_ledger.csv")
    rows = []
    for q in base.index:
        b = base.loc[q]
        nq = next_q(q)
        at_print = ledger[ledger.print_quarter == q]
        nxt = at_print[(at_print.target_period == nq)]
        fy = at_print[at_print.target_period.str.startswith("FY")]
        d = dict(print_quarter=b.print_quarter, quarter=q, print_date=b.print_date,
                 ret_1d=b.ret_1d, exc_1d=b.exc_1d, ret_5d=b.ret_5d, exc_5d=b.exc_5d,
                 rev_beat=b.rev_beat, nights_beat=b.nights_beat, rev_surprise=b.rev_surprise, nights_surprise=b.nights_surprise,
                 guide_vs_street_pct=b.guide_vs_street, guide_below_street=b.guide_below_street)
        # next-quarter revenue range
        rr = nxt[(nxt.metric == "revenue_usd_m") & (nxt.guide_type == "range")]
        i = QUARTERS.index(q)
        prior_year_of_target = QUARTERS[i - 3] if i >= 3 else None
        if not rr.empty and prior_year_of_target in kpi.index:
            g = rr.iloc[0]
            base_rev = kpi.loc[prior_year_of_target, "revenue_musd"]
            d["nq_rev_guide_mid"] = g.value_mid
            d["nq_rev_guide_growth"] = (g.value_mid / base_rev - 1) * 100
            d["nq_range_width_pct"] = (g.value_high - g.value_low) / g.value_mid * 100
            reported = kpi.loc[q, "revenue_yoy_reported_pct"]
            d["nq_guide_accel_pts"] = d["nq_rev_guide_growth"] - reported if pd.notna(reported) else np.nan
        else:
            d.update(nq_rev_guide_mid=np.nan, nq_rev_guide_growth=np.nan, nq_range_width_pct=np.nan, nq_guide_accel_pts=np.nan)
        # nights guide
        ng = nxt[nxt.metric.isin(["nights_yoy_pct", "nights_m"])]
        cur_nights = kpi.loc[q, "nights_yoy_pct"]
        if not ng.empty:
            g = ng.sort_values("guide_type").iloc[0]  # bucket before directional alphabetically
            code = dir_code(g)
            d["nq_nights_dir"] = code
            if g.guide_type == "bucket" and pd.notna(g.value_mid) and pd.notna(cur_nights):
                d["nq_nights_guide_pts"] = g.value_mid - cur_nights
            else:
                d["nq_nights_guide_pts"] = code * 2.0 if pd.notna(code) else np.nan
        else:
            d["nq_nights_dir"] = np.nan
            d["nq_nights_guide_pts"] = np.nan
        # margin guide (y/y points or level)
        mg = nxt[nxt.metric.isin(["adj_ebitda_margin_yoy_pts", "adj_ebitda_margin_pct"])]
        d["nq_margin_dir"], d["nq_margin_guide_pts"] = np.nan, np.nan
        if not mg.empty:
            g = mg.iloc[0]
            if g.metric == "adj_ebitda_margin_yoy_pts":
                d["nq_margin_dir"] = dir_code(g)
                d["nq_margin_guide_pts"] = g.value_low if g.guide_type == "floor" else g.value_high if g.guide_type == "ceiling" else g.value_mid
            else:  # level guide: compare to prior-year margin of the target quarter
                lvl = g.value_low if g.guide_type == "floor" else g.value_high if g.guide_type == "ceiling" else g.value_mid
                py_m = kpi.loc[prior_year_of_target, "adj_ebitda_margin_pct"] if prior_year_of_target in kpi.index else np.nan
                if pd.notna(lvl) and pd.notna(py_m):
                    d["nq_margin_guide_pts"] = lvl - py_m
                    d["nq_margin_dir"] = float(np.sign(lvl - py_m))
                else:
                    d["nq_margin_dir"] = dir_code(g)
        for key, metrics in [("nq_adr_dir", ["adr_yoy_pct", "adr_usd_seq"]), ("nq_take_rate_dir", ["take_rate_yoy_pts", "take_rate_pct_seq"]),
                             ("nq_gbv_dir", ["gbv_yoy_pct", "gbv_usd_b"])]:
            x = nxt[nxt.metric.isin(metrics)]
            d[key] = dir_code(x.iloc[0]) if not x.empty else np.nan
        # full-year items
        fm = fy[fy.metric == "adj_ebitda_margin_pct"]
        if fm.empty:
            fm = fy[fy.metric == "adj_ebitda_margin_yoy_pts"]
        if not fm.empty:
            g = fm.iloc[0]
            delta = g.revision_delta
            d["fy_margin_delta_pts"] = 0.0 if pd.isna(delta) else float(delta)
            d["fy_margin_action"] = "first" if pd.isna(delta) else ("raised" if delta > 0 else "lowered" if delta < 0 else "reiterated")
            lvl = g.value_low if g.guide_type == "floor" else g.value_mid if g.guide_type == "point" else g.value_high
            fy_yr = int(g.target_period[-2:])
            prior_fy_q = [f"{k}Q{fy_yr - 1}" for k in range(1, 5)]
            if g.metric == "adj_ebitda_margin_pct" and pd.notna(lvl) and all(p in kpi.index for p in prior_fy_q):
                prior_m = kpi.loc[prior_fy_q, "adj_ebitda_musd"].sum() / kpi.loc[prior_fy_q, "revenue_musd"].sum() * 100
                d["fy_margin_floor_vs_prior_fy"] = lvl - prior_m
            else:
                d["fy_margin_floor_vs_prior_fy"] = np.nan
        else:
            d.update(fy_margin_delta_pts=np.nan, fy_margin_action="none", fy_margin_floor_vs_prior_fy=np.nan)
        fr = fy[fy.metric == "revenue_yoy_pct"]
        if not fr.empty:
            g = fr.iloc[0]
            delta = g.revision_delta
            d["fy_rev_delta_pts"] = 0.0 if pd.isna(delta) else float(delta)
            d["fy_rev_action"] = "first" if pd.isna(delta) else ("raised" if delta > 0 else "lowered" if delta < 0 else "reiterated")
            d["fy_rev_guide_mid"] = g.value_mid
        else:
            d.update(fy_rev_delta_pts=np.nan, fy_rev_action="none", fy_rev_guide_mid=np.nan)
        numeric_fy = fy[fy.guide_type.isin(["range", "floor", "ceiling", "point", "bucket"]) & fy[["value_low", "value_high", "value_mid"]].notna().any(axis=1)]
        d["fy_numeric_present"] = float(not numeric_fy.empty)
        d["fy_items_count"] = float(len(fy))
        d["new_investment_flag"] = float(not fy[fy.metric == "new_business_investment_usd_m"].empty)
        sb = fy[fy.metric == "sbc_yoy_pct"]
        d["sbc_guide_pct"] = sb.iloc[0].value_mid if not sb.empty else np.nan
        d["fy_margin_raised"] = float(d["fy_margin_action"] == "raised") if d["fy_margin_action"] != "none" else np.nan
        d["fy_rev_raised"] = float(d["fy_rev_action"] == "raised") if d["fy_rev_action"] != "none" else np.nan
        rows.append(d)
    return pd.DataFrame(rows)


FEATURES = [
    ("Next-Q revenue guide", "nq_rev_guide_growth", "guided revenue growth (%)", "num"),
    ("Next-Q revenue guide", "nq_guide_accel_pts", "guided growth minus just-reported growth (pts)", "num"),
    ("Next-Q revenue guide", "guide_vs_street_pct", "guide midpoint vs Street (%)", "num"),
    ("Next-Q revenue guide", "guide_below_street", "guide below Street (1/0)", "dummy"),
    ("Next-Q revenue guide", "nq_range_width_pct", "range width (% of mid)", "num"),
    ("Next-Q nights guide", "nq_nights_guide_pts", "implied nights acceleration (pts; +/-2 for above/below)", "num"),
    ("Next-Q nights guide", "nq_nights_dir", "direction (+1 above, 0 stable, -1 below)", "num"),
    ("Next-Q margin guide", "nq_margin_dir", "direction (+1 up, 0 flat, -1 down)", "num"),
    ("Next-Q margin guide", "nq_margin_guide_pts", "guided y/y margin change (pts)", "num"),
    ("Next-Q ADR guide", "nq_adr_dir", "direction (+1 up, 0 flat, -1 down)", "num"),
    ("Next-Q take-rate guide", "nq_take_rate_dir", "direction (+1 up, 0 flat, -1 down)", "num"),
    ("Next-Q GBV guide", "nq_gbv_dir", "direction (+1 up, 0 flat, -1 below)", "num"),
    ("FY margin guide", "fy_margin_delta_pts", "change vs prior statement (pts; first = 0)", "num"),
    ("FY margin guide", "fy_margin_raised", "raised (1) vs reiterated/first/lowered (0)", "dummy"),
    ("FY margin guide", "fy_margin_floor_vs_prior_fy", "FY floor minus prior FY actual margin (pts)", "num"),
    ("FY revenue guide", "fy_rev_delta_pts", "change vs prior statement (pts; first = 0)", "num"),
    ("FY revenue guide", "fy_rev_raised", "raised (1) vs other (0)", "dummy"),
    ("FY framework", "fy_numeric_present", "any numeric FY guide issued (1/0)", "dummy"),
    ("FY framework", "fy_items_count", "number of FY guidance items issued", "num"),
    ("FY investment budget", "new_investment_flag", "new-business investment budget announced (1/0)", "dummy"),
    ("Reported quarter (for comparison)", "nights_beat", "nights beat consensus (1/0)", "dummy"),
    ("Reported quarter (for comparison)", "rev_beat", "revenue beat consensus (1/0)", "dummy"),
]
DEPS = [("ret_1d", "Day 1, raw"), ("exc_1d", "Day 1, excess vs QQQ"), ("ret_5d", "5 sessions, raw"), ("exc_5d", "5 sessions, excess vs QQQ")]
WINDOWS = [("all prints", lambda p: p), ("2023 onward", lambda p: p[p.print_quarter >= "2023Q1"])]


def univariate(panel: pd.DataFrame) -> pd.DataFrame:
    out = []
    for win, sel in WINDOWS:
        sub = sel(panel)
        for item, col, label, kind in FEATURES:
            for dep, dl in DEPS:
                d = sub[[col, dep]].dropna()
                n = len(d)
                rec = dict(item=item, feature=label, horizon=dl, window=win, n=n)
                if n >= 6 and d[col].nunique() > 1:
                    m = sm.OLS(d[dep].values, sm.add_constant(d[col].values)).fit()
                    rec.update(slope=m.params[1], t=m.tvalues[1], p=m.pvalues[1], r2=m.rsquared)
                    rho, rp = stats.spearmanr(d[col], d[dep])
                    rec.update(spearman=rho)
                    if kind == "dummy" or set(d[col].unique()) <= {-1.0, 0.0, 1.0}:
                        for val, key in [(1.0, "if_1"), (0.0, "if_0"), (-1.0, "if_minus1")]:
                            s = d.loc[d[col] == val, dep]
                            if len(s):
                                rec[f"mean_{key}"] = s.mean()
                                rec[f"n_{key}"] = len(s)
                                rec[f"pos_share_{key}"] = (s > 0).mean()
                        a, b = d.loc[d[col] == 1.0, dep], d.loc[d[col] != 1.0, dep]
                        if len(a) >= 2 and len(b) >= 2:
                            rec["welch_p_1_vs_rest"] = stats.ttest_ind(a, b, equal_var=False).pvalue
                out.append(rec)
    return pd.DataFrame(out)


MULTI = [
    ("Guide vs Street + nights beat", ["guide_vs_street_pct", "nights_beat"]),
    ("Guide acceleration + nights beat", ["nq_guide_accel_pts", "nights_beat"]),
    ("Guide vs Street + FY margin delta", ["guide_vs_street_pct", "fy_margin_delta_pts"]),
    ("Guide vs Street + nights guide", ["guide_vs_street_pct", "nq_nights_guide_pts"]),
    ("Guide vs Street + revenue beat", ["guide_vs_street_pct", "rev_beat"]),
    ("Nights guide + FY margin delta + guide vs Street", ["nq_nights_guide_pts", "fy_margin_delta_pts", "guide_vs_street_pct"]),
]


def multivariate(panel: pd.DataFrame) -> pd.DataFrame:
    out = []
    for win, sel in WINDOWS:
        sub = sel(panel)
        for label, cols in MULTI:
            for dep, dl in DEPS:
                d = sub[cols + [dep]].dropna()
                n = len(d)
                rec = dict(item="Multivariate", feature=label, horizon=dl, window=win, n=n)
                if n >= len(cols) + 5:
                    m = sm.OLS(d[dep].values, sm.add_constant(d[cols].values)).fit()
                    rec.update(r2=m.rsquared, adj_r2=m.rsquared_adj)
                    for k, c in enumerate(cols, start=1):
                        rec[f"coef_{k}"] = m.params[k]
                        rec[f"t_{k}"] = m.tvalues[k]
                        rec[f"var_{k}"] = c
                out.append(rec)
    return pd.DataFrame(out)


def run():
    panel = build_panel()
    res = pd.concat([univariate(panel), multivariate(panel)], ignore_index=True)
    panel.to_csv(OUT_PANEL, index=False)
    res.round(4).to_csv(OUT_RES, index=False)
    return panel, res


if __name__ == "__main__":
    panel, res = run()
    pd.set_option("display.width", 260)
    pd.set_option("display.max_rows", 400)
    pd.set_option("display.max_colwidth", 48)
    show = res[res.horizon.str.contains("excess")]
    cols = ["item", "feature", "horizon", "window", "n", "slope", "t", "p", "r2", "mean_if_1", "n_if_1", "mean_if_0", "n_if_0", "mean_if_minus1", "n_if_minus1", "welch_p_1_vs_rest"]
    print(show[[c for c in cols if c in show.columns]].round(2).to_string())
    mv = res[res.item == "Multivariate"]
    print(mv[[c for c in ["feature", "horizon", "window", "n", "r2", "adj_r2", "coef_1", "t_1", "coef_2", "t_2", "coef_3", "t_3"] if c in mv.columns]].round(2).to_string())
    print(panel[["quarter", "exc_1d", "exc_5d", "nq_rev_guide_growth", "nq_guide_accel_pts", "guide_vs_street_pct", "nq_nights_guide_pts", "nq_margin_dir",
                 "fy_margin_action", "fy_margin_delta_pts", "fy_rev_action", "fy_numeric_present", "new_investment_flag"]].round(1).to_string())
