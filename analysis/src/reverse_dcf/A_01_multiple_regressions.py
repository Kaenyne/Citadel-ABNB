"""
Workstream A, step 1: re-estimate the multiple-vs-growth relationship that the joint solve needs.

Dependent: EV / NTM adj. EBITDA (monthly point-in-time, WS12 panel 12_abnb_multiples_monthly.csv; NTM EBITDA there is
NTM revenue proxy x LTM margin, so M(g) x base x (1+g) x margin is exactly the structure the panel was built with).
Regressor of interest: NTM revenue growth proxy (guide-based, WS12 caveat C2).

Runs: levels (with / without margin, rates, NDX), 12-month changes, alternative windows, quarterly panel, log form,
leave-one-month-out, block leave-one-quarter-out, rolling 24m and expanding walk-forward windows. For every fit it also
reports the FY27 growth the $170.19 EV would imply (see A_02 for the solve itself), so the stability of the *answer*
is visible, not just of the coefficient.

Run from the repo root:  py -3.13 analysis/src/reverse_dcf/A_01_multiple_regressions.py
Outputs: data/processed/reverse_dcf/A/A_regression_specs.csv, A_regression_loo.csv, A_regression_rolling.csv,
         A_ntm_proxy_vs_realised.csv
"""
import os
import sys
import numpy as np
import pandas as pd

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from A_common import ROOT, OUT, PRICE, ev_spot, FY26_REV_BASE, MARGIN_BASE, LTM_REV, LTM_MARGIN, NTM_TO_FY27_SPREAD_PP, ols_nw, solve_joint_linear, solve_joint_log  # noqa: E402

EV_TODAY = ev_spot(PRICE)            # 92,010 at $170.19
FY26_REV_DELIVERED = FY26_REV_BASE   # management delivered case (mgmt_implied_summary.csv)
MARGIN_FY27 = MARGIN_BASE


def implied_growth_linear(a, b, ev, base_rev, margin):
    return solve_joint_linear(a, b, ev, base_rev, margin)


def implied_growth_log(a, b, ev, base_rev, margin):
    return solve_joint_log(a, b, ev, base_rev, margin)


# ---- data ------------------------------------------------------------------------------------------------------------
m = pd.read_csv(os.path.join(ROOT, "data", "processed", "overnight", "12_abnb_multiples_monthly.csv"), parse_dates=["month_end"])
m = m.dropna(subset=["ev_ntm_ebitda_x", "ntm_growth_proxy_pct"]).reset_index(drop=True)
m["log_ev_ntm_ebitda"] = np.log(m["ev_ntm_ebitda_x"])
for c in ["ev_ntm_ebitda_x", "ntm_growth_proxy_pct", "ltm_ebitda_margin_pct", "dgs10_pct", "ndx_fwd_pe", "ev_ltm_ebitda_x"]:
    m[c + "_d12"] = m[c] - m[c].shift(12)

q = pd.read_csv(os.path.join(ROOT, "data", "processed", "overnight", "12_abnb_multiples_history.csv"))
q = q.dropna(subset=["ev_ntm_ebitda_x", "ntm_growth_proxy_pct"])
q = q[q["quarter"] != "3Q26"]  # 3Q26 row is the 4 Sep spot on 2Q26 fundamentals, duplicate of the monthly panel's last row


def margin_eval(spec_has_margin):
    return LTM_MARGIN * 100 if spec_has_margin else None


def fit_spec(label, df, dep, regs, lags, window_note, log_dep=False):
    d = df.dropna(subset=[dep] + regs)
    X = np.column_stack([np.ones(len(d))] + [d[r].values for r in regs])
    r = ols_nw(d[dep].values, X, lags)
    out = dict(spec=label, window=window_note, dependent=dep, regressors="+".join(regs), n=r["n"], r2=round(r["r2"], 3),
               adj_r2=round(r["adj_r2"], 3), durbin_watson=round(r["dw"], 2), b_const=round(r["b"][0], 3), t_const=round(r["t"][0], 2))
    for i, reg in enumerate(regs):
        out[f"b_{reg}"] = round(r["b"][i + 1], 4)
        out[f"t_{reg}"] = round(r["t"][i + 1], 2)
    # implied growth at $170.19: evaluate the fitted multiple as a function of growth, other regressors at their latest value
    g_reg = [x for x in regs if "growth" in x]
    if g_reg and not dep.endswith("_d12"):
        a = r["b"][0]
        bg = r["b"][1 + regs.index(g_reg[0])]
        for i, reg in enumerate(regs):
            if reg != g_reg[0]:
                a += r["b"][i + 1] * d[reg].iloc[-1]      # hold margin / 10y / NDX at the latest observation
        if log_dep:
            g27 = implied_growth_log(a, bg, EV_TODAY, FY26_REV_DELIVERED, MARGIN_FY27)
            gntm = implied_growth_log(a, bg, EV_TODAY, LTM_REV, LTM_MARGIN)
            m_at_12 = np.exp(a + bg * 12.6)
        else:
            g27 = implied_growth_linear(a, bg, EV_TODAY, FY26_REV_DELIVERED, MARGIN_FY27)
            gntm = implied_growth_linear(a, bg, EV_TODAY, LTM_REV, LTM_MARGIN)
            m_at_12 = a + bg * 12.6
        out["intercept_at_latest_controls"] = round(a, 3)
        out["fitted_multiple_at_12.6pct_growth_x"] = round(m_at_12, 2)
        # implied_fy27_growth_at_170.19_pct = NTM solve mapped proportionally to FY27 (NTM growth less the Delivered NTM-to-FY27 spread of 1.42pp),
        # the note's headline convention (audit finding 9). The direct FY27-basis solve (NTM-fitted multiple applied to FY27 EBITDA at 36.2%) is
        # a mis-specification kept in its own column to show the ~2pp gap it produces.
        out["implied_fy27_growth_at_170.19_pct"] = round(gntm - NTM_TO_FY27_SPREAD_PP, 2) if not np.isnan(gntm) else np.nan
        out["implied_fy27_growth_direct_basis_at_170.19_pct"] = round(g27, 2) if not np.isnan(g27) else np.nan
        out["implied_ntm_growth_at_170.19_pct"] = round(gntm, 2) if not np.isnan(gntm) else np.nan
    return out, r


specs = []
W = {
    "2023-26": (m["month_end"] >= "2023-01-01"),
    "2022-11 to 2026-09": (m["month_end"] >= "2022-11-01"),
    "2024-26": (m["month_end"] >= "2024-01-01"),
    "2023-26 ex Aug-Sep 2026": (m["month_end"] >= "2023-01-01") & (m["month_end"] < "2026-08-01"),
    "2023-25 (no 2026)": (m["month_end"] >= "2023-01-01") & (m["month_end"] < "2026-01-01"),
    "2023-26 ex Jul 2023 (27.3x)": (m["month_end"] >= "2023-01-01") & (m["month_end"] != "2023-07-31"),
    "2023-26 ex 2Q26-print months (Aug-Sep 2026) and Jul 2023": (m["month_end"] >= "2023-01-01") & (m["month_end"] < "2026-08-01") & (m["month_end"] != "2023-07-31"),
}
rows = []
for wname, mask in W.items():
    d = m[mask]
    rows.append(fit_spec("levels: growth only", d, "ev_ntm_ebitda_x", ["ntm_growth_proxy_pct"], 6, wname)[0])
    rows.append(fit_spec("levels: growth + margin", d, "ev_ntm_ebitda_x", ["ntm_growth_proxy_pct", "ltm_ebitda_margin_pct"], 6, wname)[0])
    if wname == "2023-26":
        rows.append(fit_spec("levels: growth + margin + 10y + NDX (WS12 replication)", d, "ev_ntm_ebitda_x",
                             ["ntm_growth_proxy_pct", "ltm_ebitda_margin_pct", "dgs10_pct", "ndx_fwd_pe"], 6, wname)[0])
        rows.append(fit_spec("levels: growth + 10y + NDX", d, "ev_ntm_ebitda_x", ["ntm_growth_proxy_pct", "dgs10_pct", "ndx_fwd_pe"], 6, wname)[0])
        rows.append(fit_spec("levels (log multiple): growth only", d, "log_ev_ntm_ebitda", ["ntm_growth_proxy_pct"], 6, wname, log_dep=True)[0])
        rows.append(fit_spec("levels: EV/LTM EBITDA on NTM growth (WS12 +0.74 spec, no controls)", d, "ev_ltm_ebitda_x", ["ntm_growth_proxy_pct"], 6, wname)[0])
        rows.append(fit_spec("levels: EV/LTM EBITDA on LTM growth (WS12 headline +0.48 spec, no controls)", d, "ev_ltm_ebitda_x", ["ltm_revenue_growth_pct"], 6, wname)[0])
# 12-month changes
d12 = m[m["month_end"] >= "2023-01-01"].dropna(subset=["ev_ntm_ebitda_x_d12", "ntm_growth_proxy_pct_d12"])
rows.append(fit_spec("12m changes: d growth only", d12, "ev_ntm_ebitda_x_d12", ["ntm_growth_proxy_pct_d12"], 12, "Jan 2023 to Sep 2026 (series starts Nov 2021)")[0])
rows.append(fit_spec("12m changes: d growth + d margin", d12, "ev_ntm_ebitda_x_d12", ["ntm_growth_proxy_pct_d12", "ltm_ebitda_margin_pct_d12"], 12, "2023-26")[0])
rows.append(fit_spec("12m changes: d growth + d margin + d 10y + d NDX", d12, "ev_ntm_ebitda_x_d12",
                     ["ntm_growth_proxy_pct_d12", "ltm_ebitda_margin_pct_d12", "dgs10_pct_d12", "ndx_fwd_pe_d12"], 12, "2023-26")[0])
rows.append(fit_spec("12m changes: d EV/LTM EBITDA on d NTM growth (WS12 +0.49 spec, no controls)", d12, "ev_ltm_ebitda_x_d12", ["ntm_growth_proxy_pct_d12"], 12, "2023-26")[0])
d12b = d12[d12["month_end"] < "2026-08-01"]
rows.append(fit_spec("12m changes: d growth only, ex Aug-Sep 2026", d12b, "ev_ntm_ebitda_x_d12", ["ntm_growth_proxy_pct_d12"], 12, "2023-26 ex Aug-Sep 2026")[0])
# quarterly as-reported panel (one obs per print)
qq = q[q["quarter"].isin(["4Q22", "1Q23", "2Q23", "3Q23", "4Q23", "1Q24", "2Q24", "3Q24", "4Q24", "1Q25", "2Q25", "3Q25", "4Q25", "1Q26", "2Q26"])]
rows.append(fit_spec("quarterly as-reported (quarter-end price): growth only", qq, "ev_ntm_ebitda_x", ["ntm_growth_proxy_pct"], 2, "4Q22-2Q26, n=15")[0])
rows.append(fit_spec("quarterly as-reported: growth + margin", qq, "ev_ntm_ebitda_x", ["ntm_growth_proxy_pct", "ltm_ebitda_margin_pct"], 2, "4Q22-2Q26, n=15")[0])
# one observation per reported quarter from the monthly panel (first month after each print) = the independent-obs version
first = m[m["month_end"] >= "2023-01-01"].groupby("last_reported_quarter", sort=False).first().reset_index()
first = first.sort_values("month_end")
rows.append(fit_spec("monthly panel, first month after each print only (independent obs)", first, "ev_ntm_ebitda_x", ["ntm_growth_proxy_pct"], 2, "2023-26, n=%d" % len(first))[0])
last = m[m["month_end"] >= "2023-01-01"].groupby("last_reported_quarter", sort=False).last().reset_index().sort_values("month_end")
rows.append(fit_spec("monthly panel, last month before each print only (independent obs)", last, "ev_ntm_ebitda_x", ["ntm_growth_proxy_pct"], 2, "2023-26, n=%d" % len(last))[0])

specs = pd.DataFrame(rows)
specs.to_csv(os.path.join(OUT, "A_regression_specs.csv"), index=False)

# ---- leave-one-out and block leave-one-quarter-out on the two primary specs ------------------------------------------
base = m[m["month_end"] >= "2023-01-01"].reset_index(drop=True)
loo_rows = []
for spec_name, regs in [("levels: growth only", ["ntm_growth_proxy_pct"]), ("levels: growth + margin", ["ntm_growth_proxy_pct", "ltm_ebitda_margin_pct"])]:
    for i in range(len(base)):
        d = base.drop(index=i)
        o, _ = fit_spec(spec_name, d, "ev_ntm_ebitda_x", regs, 6, "LOO month")
        loo_rows.append(dict(spec=spec_name, scheme="leave one month out", dropped=str(base.loc[i, "month_end"].date()), n=o["n"],
                             b_growth=o["b_ntm_growth_proxy_pct"], t_growth=o["t_ntm_growth_proxy_pct"], r2=o["r2"],
                             implied_fy27_growth_at_170_pct=o["implied_fy27_growth_at_170.19_pct"], implied_ntm_growth_at_170_pct=o["implied_ntm_growth_at_170.19_pct"]))
    for qtr in base["last_reported_quarter"].unique():
        d = base[base["last_reported_quarter"] != qtr]
        o, _ = fit_spec(spec_name, d, "ev_ntm_ebitda_x", regs, 6, "LOO quarter block")
        loo_rows.append(dict(spec=spec_name, scheme="leave one reported-quarter block out", dropped=qtr, n=o["n"],
                             b_growth=o["b_ntm_growth_proxy_pct"], t_growth=o["t_ntm_growth_proxy_pct"], r2=o["r2"],
                             implied_fy27_growth_at_170_pct=o["implied_fy27_growth_at_170.19_pct"], implied_ntm_growth_at_170_pct=o["implied_ntm_growth_at_170.19_pct"]))
loo = pd.DataFrame(loo_rows)
loo.to_csv(os.path.join(OUT, "A_regression_loo.csv"), index=False)

# ---- rolling 24-month and expanding windows -------------------------------------------------------------------------
roll_rows = []
for spec_name, regs in [("levels: growth only", ["ntm_growth_proxy_pct"]), ("levels: growth + margin", ["ntm_growth_proxy_pct", "ltm_ebitda_margin_pct"])]:
    for end in range(23, len(base)):
        d = base.iloc[end - 23:end + 1]
        o, _ = fit_spec(spec_name, d, "ev_ntm_ebitda_x", regs, 6, "rolling 24m")
        roll_rows.append(dict(spec=spec_name, scheme="rolling 24 months", window_end=str(base.loc[end, "month_end"].date()), n=o["n"],
                              b_growth=o["b_ntm_growth_proxy_pct"], t_growth=o["t_ntm_growth_proxy_pct"], r2=o["r2"],
                              implied_fy27_growth_at_170_pct=o["implied_fy27_growth_at_170.19_pct"], implied_ntm_growth_at_170_pct=o["implied_ntm_growth_at_170.19_pct"]))
    for end in range(17, len(base)):
        d = base.iloc[:end + 1]
        o, _ = fit_spec(spec_name, d, "ev_ntm_ebitda_x", regs, 6, "expanding")
        roll_rows.append(dict(spec=spec_name, scheme="expanding from Jan 2023", window_end=str(base.loc[end, "month_end"].date()), n=o["n"],
                              b_growth=o["b_ntm_growth_proxy_pct"], t_growth=o["t_ntm_growth_proxy_pct"], r2=o["r2"],
                              implied_fy27_growth_at_170_pct=o["implied_fy27_growth_at_170.19_pct"], implied_ntm_growth_at_170_pct=o["implied_ntm_growth_at_170.19_pct"]))
roll = pd.DataFrame(roll_rows)
roll.to_csv(os.path.join(OUT, "A_regression_rolling.csv"), index=False)

# ---- influence of the 2Q26 re-rating: fit with / without, and the residual of the Aug-Sep 2026 points -----------------
o_all, r_all = fit_spec("levels: growth only", base, "ev_ntm_ebitda_x", ["ntm_growth_proxy_pct"], 6, "2023-26")
base["fitted_multiple_x"] = r_all["b"][0] + r_all["b"][1] * base["ntm_growth_proxy_pct"]
base["residual_x"] = base["ev_ntm_ebitda_x"] - base["fitted_multiple_x"]
base[["month_end", "last_reported_quarter", "price", "ev_ntm_ebitda_x", "ntm_growth_proxy_pct", "ltm_ebitda_margin_pct", "fitted_multiple_x", "residual_x"]].round(3).to_csv(
    os.path.join(OUT, "A_regression_fitted_residuals.csv"), index=False)

# ---- NTM growth proxy vs realised NTM growth ------------------------------------------------------------------------
kpi = pd.read_csv(os.path.join(ROOT, "data", "processed", "overnight", "02_kpi_panel_quarterly.csv"))
rev = dict(zip(kpi["quarter"], kpi["revenue_musd"]))
order = list(kpi["quarter"])


def next4(qtr):
    i = order.index(qtr)
    nxt = order[i + 1:i + 5]
    if len(nxt) < 4 or any(pd.isna(rev[x]) for x in nxt):
        return np.nan
    return sum(rev[x] for x in nxt)


pr = m[m["month_end"] >= "2022-11-01"][["month_end", "last_reported_quarter", "ntm_growth_proxy_pct", "ltm_revenue_musd", "ntm_revenue_proxy_musd"]].copy()
pr["realised_ntm_revenue_musd"] = pr["last_reported_quarter"].map(next4)
pr["realised_ntm_growth_pct"] = (pr["realised_ntm_revenue_musd"] / pr["ltm_revenue_musd"] - 1) * 100
pr["proxy_minus_realised_pp"] = pr["ntm_growth_proxy_pct"] - pr["realised_ntm_growth_pct"]
pr.round(3).to_csv(os.path.join(OUT, "A_ntm_proxy_vs_realised.csv"), index=False)
pv = pr.dropna(subset=["realised_ntm_growth_pct"]).groupby("last_reported_quarter", sort=False).first()

# ---- console ---------------------------------------------------------------------------------------------------------
pd.set_option("display.width", 250)
print("EV today at $%.2f: $%.0fM" % (PRICE, EV_TODAY))
cols = ["spec", "window", "n", "r2", "durbin_watson", "b_const", "b_ntm_growth_proxy_pct", "t_ntm_growth_proxy_pct", "b_ltm_ebitda_margin_pct", "t_ltm_ebitda_margin_pct",
        "fitted_multiple_at_12.6pct_growth_x", "implied_fy27_growth_at_170.19_pct", "implied_ntm_growth_at_170.19_pct"]
print(specs[[c for c in cols if c in specs.columns]].to_string())
print("\nLOO summary (implied FY27 growth at $170.19):")
print(loo.groupby(["spec", "scheme"]).agg(b_min=("b_growth", "min"), b_max=("b_growth", "max"), g_min=("implied_fy27_growth_at_170_pct", "min"),
                                          g_max=("implied_fy27_growth_at_170_pct", "max"), g_med=("implied_fy27_growth_at_170_pct", "median")).round(2).to_string())
print("\nBlock LOO detail, growth only:")
print(loo[(loo.spec == "levels: growth only") & (loo.scheme.str.startswith("leave one reported"))].to_string())
print("\nRolling / expanding summary:")
print(roll.groupby(["spec", "scheme"]).agg(b_min=("b_growth", "min"), b_max=("b_growth", "max"), g_min=("implied_fy27_growth_at_170_pct", "min"),
                                           g_max=("implied_fy27_growth_at_170_pct", "max")).round(2).to_string())
print(roll[roll.scheme == "expanding from Jan 2023"].tail(12).to_string())
print("\nResiduals, last 8 months:")
print(base[["month_end", "price", "ev_ntm_ebitda_x", "ntm_growth_proxy_pct", "fitted_multiple_x", "residual_x"]].tail(8).round(2).to_string())
print("\nNTM proxy vs realised (one row per reported quarter):")
print(pv[["ntm_growth_proxy_pct", "realised_ntm_growth_pct", "proxy_minus_realised_pp"]].round(2).to_string())
print("mean error %.2f pp, RMSE %.2f pp, n %d" % (pv["proxy_minus_realised_pp"].mean(), np.sqrt((pv["proxy_minus_realised_pp"] ** 2).mean()), len(pv)))
