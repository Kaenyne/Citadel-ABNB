"""
31b. Operating profile: cost lines derived from the revenue drivers.

Part B of workstream 31. Every cash cost line is written as a function of its natural driver
(GBV dollars, nights, revenue, headcount, time), the relationship is estimated on Airbnb's own
2022Q1-2026Q2 history, and the forward margin is that relationship applied to the workstream-29
driver paths plus named, editable structural overlays.

Sections
  A. Panel: quarterly cash cost stack 1Q21-2Q26 + FY2019/FY2020 annual from XBRL. Identity asserted.
  B. Elasticities: log-log per line x driver, seasonal dummies + trend, leave-one-year-out.
  C. Annual margin decomposition FY2019->FY2025 and 1H25->1H26, extending abnb_margin_bridge.csv.
  D. Forward model FY2026E-FY2028E under three profiles (historical / management / base).
  E. Sensitivities.

Inputs  data/processed/overnight/{07_cost_lines_per_night,07_cost_components_annual,
        07_margin_levers_fy26_fy28,02_kpi_panel_quarterly,10_regional_panel_quarterly,
        10_regional_forecast,29_q4_2026_bridge,29_fy27_quarterly_path,29_fx_refresh,
        30_quarterly_pnl}.csv, data/processed/{abnb_margin_bridge,abnb_quarterly_cost_stack_exsbc}.csv,
        data/processed/adr/07_full_decomposition.csv, data/raw/xbrl/ABNB_companyfacts.json
Outputs data/processed/overnight/31b_*.csv, analysis/figures/overnight/31b_*.png
Run     py -3.13 analysis/src/overnight/31b_operating_profile.py
"""
from __future__ import annotations

import json
import warnings
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

warnings.filterwarnings("ignore")

ROOT = Path(__file__).resolve().parents[3]
OUT = ROOT / "data" / "processed" / "overnight"
PROC = ROOT / "data" / "processed"
FIG = ROOT / "analysis" / "figures" / "overnight"
FIG.mkdir(parents=True, exist_ok=True)

SURFACE, INK, MUTED, GRID = "#fcfcfb", "#0b0b0b", "#898781", "#e1e0d9"
BLUE, RED, NEUTRAL = "#2a78d6", "#e34948", "#898781"
plt.rcParams.update({
    "figure.facecolor": SURFACE, "axes.facecolor": SURFACE, "savefig.facecolor": SURFACE,
    "text.color": INK, "axes.labelcolor": INK, "xtick.color": MUTED, "ytick.color": MUTED,
    "axes.edgecolor": GRID, "grid.color": GRID, "grid.linewidth": 0.6, "axes.linewidth": 0.6,
    "font.size": 8.5, "axes.titlesize": 9.5, "figure.dpi": 160,
    "xtick.major.size": 0, "ytick.major.size": 0,
})

SCEN = ["bear", "base", "bull"]
PROFILES = ["historical", "management", "base"]
LINES = {
    "cor":   ("Cost of revenue", "cor_cash_musd"),
    "ops":   ("Operations and support", "ops_cash_musd"),
    "pd":    ("Product development", "pd_cash_musd"),
    "brand": ("Brand and performance marketing", "sm_brand_perf_musd"),
    "field": ("Field operations and policy", "sm_field_ops_musd"),
    "ga":    ("General and administrative", "ga_cash_musd"),
}
NATURAL = {"cor": "gbv", "ops": "nights", "pd": "revenue", "brand": "revenue", "field": "revenue", "ga": "revenue"}


# ================================================================= A. panel
cl = pd.read_csv(OUT / "07_cost_lines_per_night.csv")
stack = pd.read_csv(PROC / "abnb_quarterly_cost_stack_exsbc.csv")[["quarter", "restr", "identity_gap"]]
kpi = pd.read_csv(OUT / "02_kpi_panel_quarterly.csv")
comp = pd.read_csv(OUT / "07_cost_components_annual.csv")
regp = pd.read_csv(OUT / "10_regional_panel_quarterly.csv")

p = cl.merge(stack, on="quarter", how="left")
p["year"] = 2000 + p.quarter.str[2:].astype(int)
p["q"] = p.quarter.str[0].astype(int)
p["t"] = (p.year - 2022) + (p.q - 1) / 4.0
p = p.sort_values(["year", "q"]).reset_index(drop=True)

p["gbv"] = p.gbv_musd
p["nights"] = p.nights_m
p["revenue"] = p.revenue_musd
p["rev_per_night"] = p.revenue / p.nights
p["take_rate"] = p.take_rate_pct / 100.0
for k, (_, col) in LINES.items():
    p[k] = p[col]
p["sm_cash"] = p.sm_cash_musd
# workstream-07 convention: no SBC inside brand and performance, so all S&M SBC comes out of field operations
p["field"] = p.sm_field_ops_musd - p.sm_sbc_musd

HEAD = {}
for c in comp.columns:
    if c.startswith("fy") and "pct" not in c:
        v = comp.loc[comp.component == "employees_dec31", c].iloc[0]
        if str(v) not in ("nan", ""):
            HEAD[int(c[2:])] = float(v)
hy = sorted(HEAD)
p["headcount"] = np.interp(p.year + p.q / 4.0, [y + 1.0 for y in hy], [HEAD[y] for y in hy])
p["time"] = p.t

p["cash_costs"] = p[["cor_cash_musd", "ops_cash_musd", "pd_cash_musd", "sm_cash_musd", "ga_cash_musd"]].sum(axis=1)
assert (p.cash_costs - p.total_cash_cost_musd).abs().max() < 0.6, "cash cost stack does not sum"
p["adj_rebuilt"] = p.revenue - p.cash_costs - p.restr.fillna(0) + p.da_musd + p.other_addbacks_musd
gap = (p.adj_rebuilt - p.adj_ebitda_musd).abs()
assert gap.max() < 5.0, "Adjusted EBITDA identity breaks by $%.1fm" % gap.max()
sp = p.dropna(subset=["brand", "field"])
assert (sp.brand + sp.field - sp.sm_cash).abs().max() < 1.2, "brand + field != S&M cash"
print("[A] panel %d quarters %s-%s; Adj. EBITDA identity max |gap| $%.2fm; S&M split from %s"
      % (len(p), p.quarter.iloc[0], p.quarter.iloc[-1], gap.max(), sp.quarter.iloc[0]))

CF = ROOT / "data" / "raw" / "xbrl" / "ABNB_companyfacts.json"
if not CF.exists():   # data/raw is gitignored repo-wide; workstream 07 depends on the same file
    raise SystemExit("missing %s - copy it from the main checkout (data/raw is gitignored) before running" % CF)
facts = json.load(open(CF, encoding="utf-8"))["facts"]["us-gaap"]


def cyframe(tag):
    if tag not in facts:
        return {}
    out = {}
    for f in facts[tag]["units"]["USD"]:
        fr = f.get("frame", "")
        if fr.startswith("CY") and len(fr) == 6:
            out[int(fr[2:])] = f["val"] / 1e6
    return out


X = {t: cyframe(t) for t in ["CostOfRevenue", "CostsAndExpenses", "ResearchAndDevelopmentExpense",
                             "SellingAndMarketingExpense", "GeneralAndAdministrativeExpense",
                             "RevenueFromContractWithCustomerExcludingAssessedTax", "ShareBasedCompensation",
                             "RestructuringCharges", "OperatingIncomeLoss"]}
EARLY = {2019: dict(nights=326.9, gbv=37964.0, adj_ebitda=-253.3, da=57.2),
         2020: dict(nights=193.2, gbv=23895.0, adj_ebitda=-250.7, da=67.2)}
early_rows = []
for y, d in EARLY.items():
    cor, rd = X["CostOfRevenue"][y], X["ResearchAndDevelopmentExpense"][y]
    sm, ga = X["SellingAndMarketingExpense"][y], X["GeneralAndAdministrativeExpense"][y]
    restr = X["RestructuringCharges"].get(y, 0.0)
    ops = X["CostsAndExpenses"][y] - cor - rd - sm - ga - restr
    rev = X["RevenueFromContractWithCustomerExcludingAssessedTax"][y]
    sbc = X["ShareBasedCompensation"][y]
    early_rows.append(dict(year=y, revenue=rev, nights=d["nights"], gbv=d["gbv"], cor=cor, ops=ops,
                           pd=rd, sm=sm, ga=ga, restr=restr, sbc=sbc, da=d["da"], adj_ebitda=d["adj_ebitda"]))
early = pd.DataFrame(early_rows).set_index("year")
print("[A] FY2019 GAAP lines from XBRL: cor %.0f ops %.0f pd %.0f sm %.0f ga %.0f; SBC %.0f"
      % (early.loc[2019, "cor"], early.loc[2019, "ops"], early.loc[2019, "pd"],
         early.loc[2019, "sm"], early.loc[2019, "ga"], early.loc[2019, "sbc"]))


# ================================================================= B. elasticities
def ols(y, Xm):
    b, _, _, _ = np.linalg.lstsq(Xm, y, rcond=None)
    r = y - Xm @ b
    n, k = Xm.shape
    dof = n - k
    s2 = r @ r / dof
    se = np.sqrt(np.diag(np.linalg.pinv(Xm.T @ Xm)) * s2)
    sst = ((y - y.mean()) ** 2).sum()
    r2 = 1 - (r @ r) / sst
    return b, se, r2, 1 - (1 - r2) * (n - 1) / dof, dof


# year-on-year log differences: seasonality cancels, the level trend is the intercept, and the
# spec is identical to the one section D projects with. Levels-with-trend is reported as a
# secondary spec because log(driver) and the trend are near-collinear on 18 quarters.
for col in list(LINES) + ["revenue", "nights", "gbv", "adr", "headcount", "rev_per_night", "take_rate"]:
    p["d4_" + col] = np.log(p[col]) - np.log(p[col].shift(4))

DIFF = p[p.year >= 2023].dropna(subset=["d4_brand"]).reset_index(drop=True)   # 1Q23-2Q26, n=14
LEVEL = p[p.year >= 2022].dropna(subset=["brand"]).reset_index(drop=True)     # 1Q22-2Q26, n=18
REOPEN = p[p.year == 2021].reset_index(drop=True)
CANDIDATES = {
    "cor":   ["gbv", "nights", "revenue", "adr"],
    "ops":   ["nights", "revenue", "gbv", "headcount"],
    "pd":    ["revenue", "headcount", "nights", "time"],
    "brand": ["revenue", "nights", "gbv", "time"],
    "field": ["revenue", "nights", "headcount", "time"],
    "ga":    ["revenue", "headcount", "nights", "time"],
}
EV = ("primary spec dlog4(cost) = g + b dlog4(driver), OLS on year-on-year log differences of the quarterly "
      "cash (ex-SBC) stack in 07_cost_lines_per_night.csv (1Q23-2Q26); g is the per-unit trend in % per year. "
      "Secondary spec log(cost) = a + b log(driver) + Q2 + Q3 + Q4 + trend on 1Q22-2Q26. Drivers from the same "
      "file and 02_kpi_panel_quarterly.csv; headcount interpolated from the 10-K Dec-31 counts")


def diff_fit(df, line, drv):
    y = df["d4_" + line].values
    Xm = (np.ones((len(df), 1)) if drv == "time"
          else np.column_stack([np.ones(len(df)), df["d4_" + drv].values]))
    b, se, r2, ar2, dof = ols(y, Xm)
    if drv == "time":
        return np.nan, np.nan, b[0], r2, ar2, dof
    return b[1], se[1], b[0], r2, ar2, dof


elas_rows = []
for line, (label, _) in LINES.items():
    for drv in CANDIDATES[line]:
        d = DIFF.dropna(subset=["d4_" + line] + ([] if drv == "time" else ["d4_" + drv]))
        n = len(d)
        el, el_se, g, r2, ar2, dof = diff_fit(d, line, drv)
        loo = []
        for yy in sorted(d.year.unique()):
            s = d[d.year != yy]
            if len(s) > 3:
                loo.append(diff_fit(s, line, drv)[0 if drv != "time" else 2])
        # secondary: levels with seasonal dummies and a trend (collinearity diagnostic below)
        L = LEVEL.dropna(subset=[line] + ([] if drv == "time" else [drv]))
        q = L.q.values
        if drv == "time":
            XL = np.column_stack([np.ones(len(L)), (q == 2), (q == 3), (q == 4), L.t.values]).astype(float)
            bL, seL, r2L, _, _ = ols(np.log(L[line].values), XL)
            el_lev, g_lev, icpt, corr = np.nan, bL[-1], np.nan, np.nan
        else:
            XL = np.column_stack([np.ones(len(L)), np.log(L[drv].values), (q == 2), (q == 3), (q == 4),
                                  L.t.values]).astype(float)
            bL, seL, r2L, _, _ = ols(np.log(L[line].values), XL)
            el_lev, g_lev = bL[1], bL[5]
            XN = np.column_stack([np.ones(len(L)), L[drv].values, (q == 2), (q == 3), (q == 4)]).astype(float)
            bN, _, _, _, _ = ols(L[line].values, XN)
            icpt = 100.0 * bN[0] / L[line].mean()
            corr = float(np.corrcoef(np.log(L[drv].values), L.t.values)[0, 1])
        elas_rows.append(dict(
            line=line, line_label=label, driver=drv, spec="dlog4 (primary)", window="1Q23-2Q26", n=n, dof=dof,
            elasticity=el, elasticity_se=el_se, elasticity_t=(el / el_se if el_se and not np.isnan(el) else np.nan),
            trend_pct_per_year=100.0 * g, r2=r2, adj_r2=ar2, intercept_share_pct=icpt,
            elasticity_loo_min=(min(loo) if loo else np.nan), elasticity_loo_max=(max(loo) if loo else np.nan),
            loo_range=((max(loo) - min(loo)) if loo else np.nan),
            elasticity_levels_spec=el_lev, trend_levels_pct_per_year=100.0 * g_lev, r2_levels=r2L,
            corr_logdriver_trend=corr,
            promote=bool(n >= 12 and not np.isnan(el) and abs(el / el_se) > 2 and (max(loo) - min(loo)) < 0.6),
            is_natural_driver=(drv == NATURAL[line]), evidence=EV))
for line, (label, _) in LINES.items():
    d21 = REOPEN.dropna(subset=[line])
    if len(d21) < 2:
        continue
    d22 = LEVEL[LEVEL.year == 2022]
    elas_rows.append(dict(
        line=line, line_label=label, driver=NATURAL[line], spec="descriptive",
        window="2021 (reopening, descriptive only)", n=len(d21), dof=np.nan, elasticity=np.nan,
        elasticity_se=np.nan, elasticity_t=np.nan, trend_pct_per_year=np.nan, r2=np.nan, adj_r2=np.nan,
        intercept_share_pct=np.nan, elasticity_loo_min=np.nan, elasticity_loo_max=np.nan, loo_range=np.nan,
        elasticity_levels_spec=np.nan, trend_levels_pct_per_year=np.nan, r2_levels=np.nan,
        corr_logdriver_trend=np.nan, promote=False, is_natural_driver=True,
        evidence="2021 mean cash cost per night $%.2f vs 2022 $%.2f; 2021 nights +%.0f%% on a collapsed 2020 base, "
                 "so no elasticity is estimated on it" % ((d21[line] / d21.nights).mean(),
                                                          (d22[line] / d22.nights).mean(),
                                                          100 * (REOPEN.nights.sum() / 193.2 - 1))))
elas = pd.DataFrame(elas_rows)
elas.to_csv(OUT / "31b_line_elasticities.csv", index=False)

FIT = {}
for line in LINES:
    s = elas[(elas.line == line) & (elas.spec == "dlog4 (primary)") & (elas.driver == NATURAL[line])].iloc[0]
    FIT[line] = dict(driver=NATURAL[line], elasticity=float(s.elasticity), trend=float(s.trend_pct_per_year) / 100.0,
                     r2=float(s.r2), n=int(s.n), loo_lo=float(s.elasticity_loo_min), loo_hi=float(s.elasticity_loo_max),
                     fixed_share=float(s.intercept_share_pct), promote=bool(s.promote))
    print("[B] %-6s ~ %-8s elasticity %+.2f (t %+.1f) trend %+.1f%%/yr  R2 %.2f  fixed %+.0f%%  "
          "LOO [%+.2f,%+.2f]  promote=%s"
          % (line, NATURAL[line], s.elasticity, s.elasticity_t, s.trend_pct_per_year, s.r2,
             s.intercept_share_pct, s.elasticity_loo_min, s.elasticity_loo_max, s.promote))

# --- restricted specs: the elasticity is imposed on economic grounds and only the per-unit trend is
#     estimated. These are what section D projects with, because only cost of revenue has an
#     unrestricted elasticity tight enough to use (LOO 0.96-1.11 against 0.41-1.66 for support).
RESTRICT = {  # line -> (driver, imposed elasticity, per-unit basis label)
    "cor":   ("gbv", 1.0, "cash cost per $ of GBV"),
    "ops":   ("nights", 1.0, "cash cost per night"),
    "pd":    (None, 0.0, "own growth rate (headcount-driven)"),
    "brand": (None, 0.0, "own growth rate (discretionary)"),
    "field": (None, 0.0, "own growth rate (programme spend)"),
    "ga":    (None, 0.0, "own growth rate (fixed base)"),
}
rest_rows = []
for line, (drv, e, basis) in RESTRICT.items():
    d = DIFF.dropna(subset=["d4_" + line])
    resid = d["d4_" + line].values - (e * d["d4_" + drv].values if drv else 0.0)
    byyear = {yy: float(np.mean(d[d.year == yy]["d4_" + line].values
                                - (e * d[d.year == yy]["d4_" + drv].values if drv else 0.0)))
              for yy in sorted(d.year.unique())}
    un = elas[(elas.line == line) & (elas.spec == "dlog4 (primary)") & (elas.driver == NATURAL[line])].iloc[0]
    rest_rows.append(dict(
        line=line, line_label=LINES[line][0], driver=(drv or "none (trend only)"), spec="restricted (used forward)",
        window="1Q23-2Q26", n=len(d), dof=len(d) - 1, elasticity=e, elasticity_se=np.nan, elasticity_t=np.nan,
        trend_pct_per_year=100.0 * resid.mean(), r2=np.nan, adj_r2=np.nan,
        intercept_share_pct=float(un.intercept_share_pct),
        elasticity_loo_min=e, elasticity_loo_max=e, loo_range=0.0,
        elasticity_levels_spec=np.nan, trend_levels_pct_per_year=np.nan, r2_levels=np.nan,
        corr_logdriver_trend=np.nan, promote=True, is_natural_driver=True,
        evidence="elasticity imposed at %.1f on %s; trend = mean year-on-year log change in %s over 1Q23-2Q26 "
                 "(%s). Unrestricted estimate %.2f, LOO [%.2f, %.2f]"
                 % (e, drv or "no driver", basis,
                    "; ".join("%d %+.1f%%" % (yy, 100 * v) for yy, v in byyear.items()),
                    un.elasticity, un.elasticity_loo_min, un.elasticity_loo_max)))
elas = pd.concat([elas, pd.DataFrame(rest_rows)], ignore_index=True)
# a promoted elasticity must also carry an admissible sign
elas["sign_admissible"] = elas.elasticity.between(-0.05, 2.5) | elas.elasticity.isna()
elas["promote"] = elas.promote & elas.sign_admissible
elas.to_csv(OUT / "31b_line_elasticities.csv", index=False)

FITR = {}
for line in LINES:
    s = elas[(elas.line == line) & (elas.spec == "restricted (used forward)")].iloc[0]
    FITR[line] = dict(driver=RESTRICT[line][0], elasticity=RESTRICT[line][1], trend=float(s.trend_pct_per_year) / 100.0,
                      basis=RESTRICT[line][2],
                      fixed_share=float(np.clip(s.intercept_share_pct / 100.0, 0.0, 1.0)))
    print("[B] restricted %-6s e=%.1f on %-8s  historical trend %+.1f%%/yr on %s  (fixed share %.0f%%)"
          % (line, RESTRICT[line][1], RESTRICT[line][0] or "-", s.trend_pct_per_year, RESTRICT[line][2],
             100 * FITR[line]["fixed_share"]))


# ================================================================= C. annual decomposition
adrdec = pd.read_csv(PROC / "adr" / "07_full_decomposition.csv").set_index("year")
SBC_FN = ["cor_sbc_musd", "ops_sbc_musd", "pd_sbc_musd", "sm_sbc_musd", "ga_sbc_musd"]
sbc21 = p[p.year == 2021][SBC_FN].sum()
sbc21_share = (sbc21 / sbc21.sum()).values  # cor, ops, pd, sm, ga

ann_rows = []
for y in sorted(p.year.unique()):
    d = p[p.year == y]
    if len(d) < 4:
        continue
    r = dict(period="FY%d" % y, basis="cash (ex-SBC), letters + 10-Q split",
             revenue=d.revenue.sum(), nights=d.nights.sum(), gbv=d.gbv.sum(),
             adj_ebitda=d.adj_ebitda_musd.sum())
    for L in LINES:
        r[L] = d[L].sum()
    ann_rows.append(r)
for y, row in early.iterrows():   # FY2019, FY2020: GAAP lines less SBC allocated on the FY2021 functional split
    alloc = dict(zip(["cor", "ops", "pd", "sm", "ga"], sbc21_share * row.sbc))
    brand_gaap = {2019: 1140.4, 2020: 478.6}[y]        # 10-K S&M split table
    field_gaap = {2019: 481.2, 2020: 696.7}[y]
    ann_rows.append(dict(
        period="FY%d" % y, basis="GAAP less SBC allocated on the FY2021 functional split (SBC $%.0fm)" % row.sbc,
        revenue=row.revenue, nights=row.nights, gbv=row.gbv, adj_ebitda=row.adj_ebitda,
        cor=row.cor - alloc["cor"], ops=row.ops - alloc["ops"], pd=row.pd - alloc["pd"],
        brand=brand_gaap, field=field_gaap - alloc["sm"], ga=row.ga - alloc["ga"]))
# 1H windows
for y in (2025, 2026):
    d = p[(p.year == y) & (p.q <= 2)]
    r = dict(period="1H%d" % y, basis="cash (ex-SBC), letters + 10-Q split",
             revenue=d.revenue.sum(), nights=d.nights.sum(), gbv=d.gbv.sum(), adj_ebitda=d.adj_ebitda_musd.sum())
    for L in LINES:
        r[L] = d[L].sum()
    ann_rows.append(r)
A = pd.DataFrame(ann_rows).set_index("period")
A["cash_costs"] = A[list(LINES)].sum(axis=1)
A["addbacks"] = A.adj_ebitda - (A.revenue - A.cash_costs)   # D&A, other add-backs, restructuring, rounding
A["rpn"] = A.revenue / A.nights
A["adr"] = A.gbv / A.nights
A["takerate"] = A.revenue / A.gbv
A["margin"] = 100.0 * A.adj_ebitda / A.revenue
for L in LINES:
    A[L + "_cpn"] = A[L] / A.nights
print("[C] annual panel:\n" + A[["revenue", "nights", "adr", "takerate", "margin"]].round(2).to_string())

LEGS = [("FY2019", "FY2020"), ("FY2020", "FY2021"), ("FY2021", "FY2022"), ("FY2022", "FY2023"),
        ("FY2023", "FY2024"), ("FY2024", "FY2025"), ("1H2025", "1H2026"),
        ("FY2019", "FY2022"), ("FY2022", "FY2025")]
ADR_CORE = [("of_which_fx_pp", "FX"), ("geo_mix_pp", "Regional mix"), ("of_which_los_pp", "Length of stay"),
            ("interaction_pp", "ADR interaction")]
ADR_FINE = [("size_mix_pp", "Unit-size mix"), ("price_measured_pp", "Like-for-like price (measured)"),
            ("unexplained_pp", "ADR unexplained")]
ADR_EV = ("data/processed/adr/07_full_decomposition.csv (research/notes/2026-09-07_adr-decomposition.md): "
          "FX from the reconstructed regional currency basket, regional mix from the 10-K geographic tables, "
          "unit-size mix from the 29-market Inside Airbnb panel, like-for-like price externally measured; "
          "the unexplained line is reported, not plugged")


def adr_terms_for(y0, y1):
    """pp contributions to the ADR move summed over the years in the leg, or None if unavailable."""
    want = list(range(int(y0[-4:]) + 1, int(y1[-4:]) + 1))
    if any(y not in adrdec.index for y in want) or y0.startswith("1H"):
        return None
    out = {lab: float(adrdec.loc[want, col].sum()) for col, lab in ADR_CORE}
    if all(adrdec.loc[want, c].notna().all() for c, _ in ADR_FINE):
        for col, lab in ADR_FINE:
            out[lab] = float(adrdec.loc[want, col].sum())
    else:
        out["Unit-size mix and like-for-like price (not separated)"] = float(
            adrdec.loc[want, "of_which_size_and_price_pp"].sum())
    return out


# FX points inside ADR for the 1H legs come from the letters directly (no annual decomposition there)
FXA = kpi.set_index("quarter").fx_pts_adr
NGH = kpi.set_index("quarter").nights_m


def fx_pp_half(year):
    qs = ["1Q%d" % (year - 2000), "2Q%d" % (year - 2000)]
    w = NGH[qs] / NGH[qs].sum()
    return float((FXA[qs] * w).sum())


dec_rows = []
for y0, y1 in LEGS:
    a0, a1 = A.loc[y0], A.loc[y1]
    dlrpn = np.log(a1.rpn / a0.rpn)
    dladr = np.log(a1.adr / a0.adr)
    dltake = np.log(a1.takerate / a0.takerate)
    dln = np.log(a1.nights / a0.nights)
    leg = "%s->%s" % (y0, y1)
    basis = ("cash (ex-SBC)" if y0.startswith(("FY202", "1H")) and int(y0[-4:]) >= 2021
             else "GAAP less allocated SBC for FY2019/FY2020, cash thereafter")
    tot_unit = tot_rpn = 0.0
    per_line = {}
    for L in LINES:
        s0 = a0[L + "_cpn"] / a0.rpn
        unit = -(a1[L + "_cpn"] - a0[L + "_cpn"]) / a0.rpn * 100.0
        rpn_e = -a1[L + "_cpn"] * (1.0 / a1.rpn - 1.0 / a0.rpn) * 100.0
        tot_unit += unit
        tot_rpn += rpn_e
        dlc = np.log(a1[L + "_cpn"] / a0[L + "_cpn"])
        f = FITR[L]["fixed_share"]
        parts = {}
        if L == "cor":
            parts["GBV pass-through (ADR on a per-night cost)"] = dladr
        parts["Nights leverage (fixed share %.0f%%)" % (100 * f)] = -f * dln
        parts["Per-unit cost change (%s)" % FITR[L]["basis"]] = dlc - sum(parts.values())
        for k, v in parts.items():
            share = (v / dlc) if abs(dlc) > 1e-9 else (1.0 if k.startswith("Per-unit") else 0.0)
            dec_rows.append(dict(bridge=leg, basis=basis, group="Cost line: " + LINES[L][0], component=k,
                                 margin_pts=unit * share, detail="%s $%.2f -> $%.2f per night"
                                 % (LINES[L][0], a0[L + "_cpn"], a1[L + "_cpn"]),
                                 evidence="unit-cost effect on the abnb_margin_bridge.csv convention (cost per night "
                                          "moved, revenue per night held), split by the fixed share from the levels "
                                          "regression in 31b_line_elasticities.csv"))
        per_line[L] = (unit, rpn_e)
    # revenue-per-night effect, allocated across take rate and the ADR terms
    terms = {"Take rate": dltake}
    at = adr_terms_for(y0, y1)
    if at is not None:
        scale = dladr / (sum(at.values()) / 100.0) if abs(sum(at.values())) > 1e-9 else 1.0
        for lab, pp in at.items():
            terms[lab] = pp / 100.0 * scale
        ev_rpn = ADR_EV
    elif y0.startswith("1H"):
        fxpp = (fx_pp_half(int(y1[-4:])) - 0.0) / 100.0
        terms["FX"] = fxpp
        terms["ADR ex-FX (mix not separated)"] = dladr - fxpp
        ev_rpn = ("FX points inside ADR from the shareholder letters (02_kpi_panel_quarterly.csv fx_pts_adr, "
                  "nights-weighted across Q1 and Q2); the annual ADR decomposition is not built for half years")
    else:
        terms["ADR (FX and mix unallocated)"] = dladr
        ev_rpn = "no annual ADR decomposition for this leg (07_full_decomposition.csv starts at 2021)"
    for lab, v in terms.items():
        share = (v / dlrpn) if abs(dlrpn) > 1e-9 else 0.0
        dec_rows.append(dict(bridge=leg, basis=basis, group="Revenue per night", component=lab,
                             margin_pts=tot_rpn * share,
                             detail="revenue per night $%.2f -> $%.2f" % (a0.rpn, a1.rpn),
                             evidence=(ev_rpn if lab != "Take rate" else
                                       "take rate %.2f%% -> %.2f%% (revenue / GBV, letters)" % (100 * a0.takerate, 100 * a1.takerate))))
    ab = (a1.addbacks / a1.revenue - a0.addbacks / a0.revenue) * 100.0
    dec_rows.append(dict(bridge=leg, basis=basis, group="Add-backs", component="D&A, restructuring and other add-backs",
                         margin_pts=ab, detail="%.1f%% -> %.1f%% of revenue" % (100 * a0.addbacks / a0.revenue,
                                                                               100 * a1.addbacks / a1.revenue),
                         evidence="Adjusted EBITDA reconciliation in the letters, as the residual to the cash stack"))
    tot = tot_unit + tot_rpn + ab
    actual = a1.margin - a0.margin
    assert abs(tot - actual) < 0.02, "%s decomposition off by %.3f pts" % (leg, tot - actual)
    dec_rows.append(dict(bridge=leg, basis=basis, group="TOTAL", component="Change in Adjusted EBITDA margin",
                         margin_pts=actual, detail="%.1f%% -> %.1f%%" % (a0.margin, a1.margin),
                         evidence="identity check: components sum to the actual change within %.3f points" % abs(tot - actual)))
D = pd.DataFrame(dec_rows)
D["margin_pts"] = D.margin_pts.round(3)
D.to_csv(OUT / "31b_margin_decomposition_annual.csv", index=False)
for leg in ["FY2019->FY2022", "FY2022->FY2025", "FY2024->FY2025", "1H2025->1H2026"]:
    s = D[(D.bridge == leg) & (D.group != "TOTAL")].groupby("group").margin_pts.sum()
    print("[C] %-16s total %+.1f pts | %s" % (leg, D[(D.bridge == leg) & (D.group == "TOTAL")].margin_pts.iloc[0],
                                              "  ".join("%s %+.1f" % (k.replace("Cost line: ", ""), v) for k, v in s.items())))


# ================================================================= D. forward driver-based model
q4b = pd.read_csv(OUT / "29_q4_2026_bridge.csv")
ph = pd.read_csv(OUT / "29_fy27_quarterly_path.csv")
fxr = pd.read_csv(OUT / "29_fx_refresh.csv")
rf = pd.read_csv(OUT / "10_regional_forecast.csv")
lev07 = pd.read_csv(OUT / "07_margin_levers_fy26_fy28.csv")
pnl30 = pd.read_csv(OUT / "30_quarterly_pnl.csv")

QS = ["3Q26", "4Q26", "1Q27", "2Q27", "3Q27", "4Q27"]
PY4 = {"3Q26": "3Q25", "4Q26": "4Q25", "1Q27": "1Q26", "2Q27": "2Q26", "3Q27": "3Q26", "4Q27": "4Q26"}
FXPATH = {"bear": "strong_usd", "base": "consensus", "bull": "weak_usd"}


def regt(period, s, col):
    return float(rf[(rf.period == period) & (rf.region == "TOTAL") & (rf.scenario == s)][col].iloc[0])


def lev(item, year, s):
    r = lev07[(lev07.row_type == "lever") & (lev07.year == year) & (lev07.item == item)]
    return float(r[s].iloc[0])


drivers = {}
for s in SCEN:
    def fxq(q, s=s):
        return float(fxr[(fxr.path == FXPATH[s]) & (fxr.quarter == q)].revenue_fx_fit_pp.iloc[0])
    q3g = 15.51 + {"bear": -2.4, "base": 1.0, "bull": 4.9}[s]
    rows = {"3Q26": dict(nights_yoy=regt("3Q26", s, "nights_yoy_pct"), adr_exfx=regt("3Q26", s, "adr_exfx_yoy_pct"),
                         fx_pp=3.0, rev_g=q3g),
            "4Q26": dict(nights_yoy=regt("4Q26", s, "nights_yoy_pct"), adr_exfx=regt("4Q26", s, "adr_exfx_yoy_pct"),
                         fx_pp=fxq("2026Q4"),
                         rev_g=float(q4b[(q4b.scenario == s) & (q4b.kind == "end")].value_pp.iloc[0]))}
    for _, r in ph[ph.scenario == s].iterrows():
        rows["%sQ27" % r.quarter[-1]] = dict(nights_yoy=r.nights_yoy_pct, adr_exfx=r.adr_exfx_pct,
                                             fx_pp=r.fx_pp, rev_g=r.reported_growth_pct)
    drivers[s] = rows

ACT = p.set_index("quarter")
fwd_top = {}
for s in SCEN:
    st = {}
    for q in QS:
        d = drivers[s][q]
        prev = st[PY4[q]] if PY4[q] in st else dict(revenue=float(ACT.loc[PY4[q], "revenue"]),
                                                    nights=float(ACT.loc[PY4[q], "nights"]),
                                                    gbv=float(ACT.loc[PY4[q], "gbv"]))
        rev = prev["revenue"] * (1 + d["rev_g"] / 100.0)
        nights = prev["nights"] * (1 + d["nights_yoy"] / 100.0)
        gbv = prev["gbv"] * (1 + (d["nights_yoy"] + d["adr_exfx"] + d["fx_pp"]) / 100.0)
        st[q] = dict(revenue=rev, nights=nights, gbv=gbv, **d)
    fwd_top[s] = st
for s in SCEN:
    for q in QS:
        r30 = float(pnl30[(pnl30.scenario == s) & (pnl30.quarter == q)].revenue_musd.iloc[0])
        assert abs(fwd_top[s][q]["revenue"] - r30) < 1.0, "%s %s revenue %.1f vs 30 walk %.1f" % (
            s, q, fwd_top[s][q]["revenue"], r30)
print("[D] top line reconciles to 30_quarterly_pnl.csv within $1m for all 18 scenario-quarters")

HIST = {L: 100.0 * FITR[L]["trend"] for L in LINES}
UNIT = {"cor": "% y/y change in cash cost per $ of GBV", "ops": "% y/y change in cash cost per night",
        "pd": "% y/y cash growth", "brand": "% y/y cash growth", "field": "% y/y cash growth",
        "ga": "% y/y cash growth"}
OVERLAY_NAME = {"cor": "ai_hosting_and_payments", "ops": "ai_customer_support",
                "pd": "headcount_productivity_product", "brand": "brand_marketing_ramp",
                "field": "new_business_field_investment", "ga": "headcount_productivity_ga"}
YRS = ["FY2026E", "FY2027E", "FY2028E"]
TARGETS = {
    "historical": {L: {y: HIST[L] for y in YRS} for L in LINES},
    "management": {
        "cor":   {"FY2026E": 0.0, "FY2027E": 0.0, "FY2028E": -0.5},
        "ops":   {"FY2026E": -5.0, "FY2027E": -5.0, "FY2028E": -5.0},
        "pd":    {"FY2026E": 11.0, "FY2027E": 10.0, "FY2028E": 9.5},
        "brand": {"FY2026E": 25.0, "FY2027E": 16.0, "FY2028E": 13.5},
        "field": {"FY2026E": 18.0, "FY2027E": 14.0, "FY2028E": 12.0},
        "ga":    {"FY2026E": 2.0, "FY2027E": 5.5, "FY2028E": 5.0}},
    "base": {
        "cor":   {"FY2026E": 1.0, "FY2027E": 1.0, "FY2028E": 0.5},
        "ops":   {"FY2026E": -4.0, "FY2027E": -4.5, "FY2028E": -4.5},
        "pd":    {"FY2026E": 11.0, "FY2027E": 9.5, "FY2028E": 9.0},
        "brand": {"FY2026E": 27.0, "FY2027E": 15.0, "FY2028E": 12.0},
        "field": {"FY2026E": 18.0, "FY2027E": 13.0, "FY2028E": 11.0},
        "ga":    {"FY2026E": 3.0, "FY2027E": 5.0, "FY2028E": 5.0}},
}
SRC = {
    ("historical", "cor"): "no overlay: the fitted 1Q23-2Q26 trend in cash cost per $ of GBV, applied unchanged",
    ("historical", "ops"): "no overlay: the fitted 1Q23-2Q26 trend in cash cost per night, applied unchanged",
    ("historical", "pd"): "no overlay: the fitted 1Q23-2Q26 mean cash growth, applied unchanged",
    ("historical", "brand"): "no overlay: the fitted 1Q23-2Q26 mean cash growth, applied unchanged",
    ("historical", "field"): "no overlay: the fitted 1Q23-2Q26 mean cash growth, applied unchanged",
    ("historical", "ga"): "no overlay: the fitted 1Q23-2Q26 mean cash growth, applied unchanged",
    ("management", "cor"): "PLACEHOLDER for workstream 31 part A. Airbnb has never given a cost-of-revenue target. "
                           "Used here: 07_margin_levers_fy26_fy28.csv base lever cor_per_gbv (0.0 / 0.0 / -0.5%), "
                           "anchored on merchant fees flat at 1.82-1.89% of GBV since 2022, server costs +$15m in "
                           "1H26 on reserved-instance amortisation, purchase obligations $719m (Dec-24) to $1,749m "
                           "(Dec-25) and a data-hosting commitment of at least $1.7bn through 2031 (10-K Note 13)",
    ("management", "ops"): "PLACEHOLDER for workstream 31 part A. Management statements: support cost per booking "
                           "-10% (1Q26 letter) and -16% (2Q26 letter); AI resolves about 45% of contacts in 50+ "
                           "languages (2Q26); third-party service-provider cost -$17m in 2Q26. Mapped to the line at "
                           "-5.0% per night per year (07 base lever ops_cpn) against a realised -3.8% in 1H26",
    ("management", "pd"): "PLACEHOLDER for workstream 31 part A. 1H26 product development +11%, entirely payroll on "
                          "higher average headcount (10-Q); 2026 headcount growth guided lower than 2025 (+12.3%). "
                          "07 base lever pd_cash 11 / 10 / 9.5%",
    ("management", "brand"): "PLACEHOLDER for workstream 31 part A. Mertz, 4Q24 call: brand marketing is effectively "
                             "a fixed amount of spend for each market and the budget is allowed to expand and be more "
                             "heavily dedicated to expansion markets. 1H26 brand and performance +32% ($1,091m vs "
                             "$824m) on paid growth initiatives in emerging markets and partnerships. 07 base lever "
                             "bpm_cash 25 / 16 / 13.5%",
    ("management", "field"): "PLACEHOLDER for workstream 31 part A. FY2025 field operations and policy +43% to $993m; "
                             "1H26 +24%. 4Q24 letter and call: $200-250m to launch and scale new businesses in 2025, "
                             "refined to about $200m on the 2Q25 call. 07 base lever fop_cash 18 / 14 / 12%",
    ("management", "ga"): "PLACEHOLDER for workstream 31 part A. 1H26 G&A +1% (payroll +$38m offset by non-income "
                          "taxes -$38m). 07 base lever ga_cash 2 / 5.5 / 5%",
    ("base", "cor"): "judgement: +1.0% per $ of GBV in FY26-FY27 and +0.5% in FY28, above 07 at 0.0 / 0.0 / -0.5. The "
                     "data-hosting commitment went from $672m through 2027 to $1.7bn through 2031, roughly $280m a "
                     "year against about $220m, and 1H26 already carries +$15m of server cost. The historical trend "
                     "is -1.3% a year; I take the AI build as stopping that decline rather than merely offsetting it",
    ("base", "ops"): "judgement: -4.0 / -4.5 / -4.5% per night, against 07 at -5.0 flat. The only measured "
                     "line-level outcome is -3.8% in 1H26; the -16% per booking is a sub-component (third-party "
                     "support), and payroll +$41m, customer relations +$14m and insurance +$9m in 1H26 ate most of it",
    ("base", "pd"): "judgement: 11 / 9.5 / 9%, essentially 07's set. Revenue per employee fell 1.8% in 2025 for the "
                    "first time, so the headcount lever is spent and product payroll grows with the plan, not revenue",
    ("base", "brand"): "judgement: +27% FY26 (H2 at about +21% after 1H at +32%), then 15 / 12%. 07 base takes FY26 "
                       "at +25%, which needs H2 at about +17%; nothing in the 1H26 disclosure or the Q3 investment "
                       "timing language supports that sharp a step down inside the year",
    ("base", "field"): "judgement: 18 / 13 / 11%, marginally below 07 in the out years as the Services and "
                       "Experiences launch spend laps and supply acquisition annualises",
    ("base", "ga"): "judgement: 3 / 5 / 5%. 1H26's +1% flatters the line (non-income taxes -$38m); underlying payroll "
                    "is growing, and G&A carries the highest fixed share of any line (61%)",
}
# workstream 31 part A: what management has actually said about each line, and where it is silent
A31 = OUT / "31a_mgmt_implied_profile.csv"
MGMT = {}
if A31.exists():
    _a = pd.read_csv(A31)
    _map = {"cor": "cost_of_revenue", "ops": "ops_support", "pd": "product_dev", "brand": "brand_marketing",
            "field": "field_ops", "ga": "g_and_a"}
    for L, key in _map.items():
        for y in YRS:
            r = _a[(_a.cost_line == key) & (_a.fiscal_year == y[:6])]
            if len(r):
                r = r.iloc[0]
                MGMT[(L, y)] = dict(trajectory=str(r.mgmt_implied_trajectory), confidence=str(r.confidence),
                                    silent=str(r.mgmt_silent), ids=str(r.basis_statement_ids),
                                    n=int(r.n_statements))

ov_rows = []
for prof in PROFILES:
    for L in LINES:
        for y in YRS:
            tgt = TARGETS[prof][L][y]
            m = MGMT.get((L, y), {})
            src = SRC[(prof, L)]
            if prof == "management":
                if m:
                    src = ("31a_mgmt_implied_profile.csv (%s, %s): %s. Confidence %s on %d statement(s) %s. "
                           "Numeric target is the 07_margin_levers_fy26_fy28.csv base lever, because part A finds "
                           "no quantified management figure for this line and year. %s"
                           % (L, y[:6], m["trajectory"], m["confidence"], m["n"], m["ids"],
                              "MANAGEMENT IS SILENT for this year: this row is the house lever set, not a "
                              "management view." if m["silent"] == "yes" or m["confidence"] in ("none", "low")
                              else "")).strip()
                else:
                    src = "31a_mgmt_implied_profile.csv carries no row for this line and year: " + src
            ov_rows.append(dict(profile=prof, overlay=OVERLAY_NAME[L], line=L, line_label=LINES[L][0], year=y,
                                target_pct=round(tgt, 2), historical_trend_pct=round(HIST[L], 2),
                                overlay_pct=round(tgt - HIST[L], 2), unit=UNIT[L],
                                is_judgement=(prof == "base"),
                                mgmt_confidence=(m.get("confidence") if prof == "management" else ""),
                                mgmt_silent=(m.get("silent") if prof == "management" else ""),
                                mgmt_statement_ids=(m.get("ids") if prof == "management" else ""),
                                source=src))
STRUCT = [
    dict(profile="all", overlay="addbacks", line="addbacks", line_label="D&A and other add-backs", year="all",
         target_pct=0.9, historical_trend_pct=np.nan, overlay_pct=np.nan, unit="% of revenue", is_judgement=False,
         source="07_margin_levers_fy26_fy28.csv addback_pct; FY2023-FY2025 D&A about 0.7% of revenue, add-backs 0.9%"),
    dict(profile="all", overlay="take_rate", line="revenue", line_label="Take rate", year="all",
         target_pct=0.0, historical_trend_pct=np.nan, overlay_pct=0.0, unit="bps change vs the 29 driver path",
         is_judgement=False,
         source="held at whatever the workstream-29 revenue path implies (revenue / GBV). Management guides the 2026 "
                "take rate flat: the 15.5% single fee and travel insurance push up, new-business incentives and RNPL "
                "book-versus-stay timing push down. Set this non-zero to test a monetisation case"),
    dict(profile="all", overlay="fx_cost_passthrough", line="cor", line_label="Non-USD share of cost of revenue",
         year="all", target_pct=55.0, historical_trend_pct=np.nan, overlay_pct=np.nan, unit="% of the line",
         is_judgement=True,
         source="margin-drivers section 14: about 55% of revenue is non-USD and cost of revenue (merchant fees) "
                "scales with GBV in local currency; every other cash line is treated as USD. Used in the FX "
                "sensitivity only, because the central path already carries FX inside GBV"),
    dict(profile="all", overlay="expansion_markets", line="brand", line_label="Expansion-market count", year="all",
         target_pct=np.nan, historical_trend_pct=np.nan, overlay_pct=np.nan, unit="count", is_judgement=True,
         source="NOT DISCLOSED. Airbnb has never published a count of expansion markets, only that origin nights in "
                "them have grown at about twice core for ten consecutive quarters (1Q24-2Q26). The fixed-per-market "
                "brand model therefore cannot be identified from public data; the brand overlay carries the whole "
                "effect as a growth rate instead. Workstream 31 part A to supply a count if one exists",),
    dict(profile="all", overlay="brand_fixed_share", line="brand", line_label="Fixed share of brand marketing",
         year="all", target_pct=0.0, historical_trend_pct=np.nan, overlay_pct=np.nan, unit="% of the line",
         is_judgement=False,
         source="levels regression intercept share on 1Q22-2Q26 is -2%, i.e. brand and performance marketing shows "
                "no measurable fixed component against revenue over this window despite the fixed-per-market "
                "language; the spend has grown faster than revenue throughout"),
]
OVR = pd.concat([pd.DataFrame(ov_rows), pd.DataFrame(STRUCT)], ignore_index=True)
OVR.to_csv(OUT / "31b_overlay_parameters.csv", index=False)
ADDBACK_PCT = 0.9
print("[D] overlay parameters: %d rows -> 31b_overlay_parameters.csv" % len(OVR))


# ---- the projection engine
QYEAR = {"3Q26": "FY2026E", "4Q26": "FY2026E", "1Q27": "FY2027E", "2Q27": "FY2027E",
         "3Q27": "FY2027E", "4Q27": "FY2027E"}
H126 = p[(p.year == 2026) & (p.q <= 2)]
FY25A = p[p.year == 2025]
H225A = p[(p.year == 2025) & (p.q >= 3)]
ADDBACK_1H26 = float((H126.da_musd + H126.other_addbacks_musd - H126.restr.fillna(0)).sum())
FY28_LEV = {s: dict(nights=100 * lev("nights", "FY2028E", s), adr_exfx=100 * lev("adr_exfx", "FY2028E", s),
                    fx=100 * lev("fx", "FY2028E", s), take_bps=lev("take_bps", "FY2028E", s)) for s in SCEN}
FY25 = dict(revenue=FY25A.revenue.sum(), nights=FY25A.nights.sum(), gbv=FY25A.gbv.sum(),
            adj_ebitda=FY25A.adj_ebitda_musd.sum(), **{L: FY25A[L].sum() for L in LINES})
FY25["margin"] = 100 * FY25["adj_ebitda"] / FY25["revenue"]
FY25["cash_costs"] = sum(FY25[L] for L in LINES)
FY25["addbacks"] = FY25["adj_ebitda"] - (FY25["revenue"] - FY25["cash_costs"])


def project(profile, scenario, tweak=None, e_cor=1.0, e_ops=1.0):
    """Line-level forecasts by quarter (3Q26-4Q27) and year (FY26E-FY28E).

    An FY2026 target is a full-year figure, so it is converted into the H2 rate that, with the
    reported 1H26, delivers it; FY2027 and FY2028 targets apply to every quarter directly.
    """
    T = {L: dict(TARGETS[profile][L]) for L in LINES}
    dr = {q: dict(drivers[scenario][q]) for q in QS}
    fy28 = dict(FY28_LEV[scenario])
    take_bps_extra = 0.0
    if tweak:
        kind, size = tweak[0], tweak[1]
        scope = tweak[2] if len(tweak) > 2 else "all"       # "all" = every year, "FY2028E" = the final year only
        qtouch = [] if scope == "FY2028E" else QS
        ytouch = ["FY2028E"] if scope == "FY2028E" else YRS
        if kind in ("nights", "adr_exfx", "fx"):
            key = {"nights": "nights_yoy", "adr_exfx": "adr_exfx", "fx": "fx_pp"}[kind]
            for q in qtouch:
                dr[q][key] += size
                dr[q]["rev_g"] += size
            fy28[{"nights": "nights", "adr_exfx": "adr_exfx", "fx": "fx"}[kind]] += size
        elif kind == "take_bps":
            take_bps_extra = size
        elif kind in ("ops_cpn", "brand_g"):
            for y in ytouch:
                T[{"ops_cpn": "ops", "brand_g": "brand"}[kind]][y] += size
        elif kind == "regional_mix":
            adr_hit = size * (0.632 - 1.42)   # ADR index: NA 1.42 out, LatAm 0.68 / APAC 0.59 in (nights-weighted)
            for q in qtouch:
                dr[q]["adr_exfx"] += adr_hit
                dr[q]["rev_g"] += adr_hit
            fy28["adr_exfx"] += adr_hit

    qtouch_ok = not (tweak and len(tweak) > 2 and tweak[2] == "FY2028E")

    # 1. top line, quarter by quarter
    st = {}
    for q in QS:
        d, pq = dr[q], PY4[q]
        prev = st[pq] if pq in st else {k: float(ACT.loc[pq, k]) for k in ("revenue", "nights", "gbv")}
        nights = prev["nights"] * (1 + d["nights_yoy"] / 100.0)
        gbv = prev["gbv"] * (1 + (d["nights_yoy"] + d["adr_exfx"] + d["fx_pp"]) / 100.0)
        rev = prev["revenue"] * (1 + d["rev_g"] / 100.0) + gbv * (take_bps_extra if qtouch_ok else 0.0) / 10000.0
        st[q] = dict(revenue=rev, nights=nights, gbv=gbv)

    # 2. FY2026 line totals from the FY target, then the H2 residual split across Q3 and Q4
    fy26_top = {k: H126[k].sum() + st["3Q26"][k] + st["4Q26"][k] for k in ("revenue", "nights", "gbv")}
    for L in LINES:
        t = T[L]["FY2026E"] / 100.0
        if L == "cor":
            fy_total = FY25[L] * (fy26_top["gbv"] / FY25["gbv"]) ** e_cor * (1 + t)
            w = {q: float(ACT.loc[PY4[q], L]) * (st[q]["gbv"] / float(ACT.loc[PY4[q], "gbv"])) ** e_cor for q in ("3Q26", "4Q26")}
        elif L == "ops":
            fy_total = FY25[L] * (fy26_top["nights"] / FY25["nights"]) ** e_ops * (1 + t)
            w = {q: float(ACT.loc[PY4[q], L]) * (st[q]["nights"] / float(ACT.loc[PY4[q], "nights"])) ** e_ops for q in ("3Q26", "4Q26")}
        else:
            fy_total = FY25[L] * (1 + t)
            w = {q: float(ACT.loc[PY4[q], L]) for q in ("3Q26", "4Q26")}
        h2 = fy_total - H126[L].sum()
        tw = sum(w.values())
        for q in ("3Q26", "4Q26"):
            st[q][L] = h2 * w[q] / tw

    # 3. FY2027 quarters: the annual target applies to each quarter against the same quarter a year earlier
    for q in ("1Q27", "2Q27", "3Q27", "4Q27"):
        pq = PY4[q]
        prev = st[pq] if pq in st else {**{k: float(ACT.loc[pq, k]) for k in ("revenue", "nights", "gbv")},
                                        **{L: float(ACT.loc[pq, L]) for L in LINES}}
        if pq in st and "cor" not in st[pq]:
            raise RuntimeError("prior quarter not costed")
        prev = {**prev, **{L: (st[pq][L] if pq in st else float(ACT.loc[pq, L])) for L in LINES}}
        for L in LINES:
            t = T[L]["FY2027E"] / 100.0
            if L == "cor":
                st[q][L] = prev[L] * (st[q]["gbv"] / prev["gbv"]) ** e_cor * (1 + t)
            elif L == "ops":
                st[q][L] = prev[L] * (st[q]["nights"] / prev["nights"]) ** e_ops * (1 + t)
            else:
                st[q][L] = prev[L] * (1 + t)

    for q in QS:
        r = st[q]
        r["cash_costs"] = sum(r[L] for L in LINES)
        r["addbacks"] = ADDBACK_PCT / 100.0 * r["revenue"]
        r["adj_ebitda"] = r["revenue"] - r["cash_costs"] + r["addbacks"]
        r["margin"] = 100.0 * r["adj_ebitda"] / r["revenue"]

    # 4. annual aggregates
    ann = {}
    a26 = {k: H126[k].sum() + st["3Q26"][k] + st["4Q26"][k] for k in ["revenue", "nights", "gbv"] + list(LINES)}
    a26["addbacks"] = ADDBACK_1H26 + st["3Q26"]["addbacks"] + st["4Q26"]["addbacks"]
    ann["FY2026E"] = a26
    a27 = {k: sum(st[q][k] for q in ("1Q27", "2Q27", "3Q27", "4Q27")) for k in ["revenue", "nights", "gbv"] + list(LINES)}
    a27["addbacks"] = ADDBACK_PCT / 100.0 * a27["revenue"]
    ann["FY2027E"] = a27
    g = fy28
    n28 = a27["nights"] * (1 + g["nights"] / 100.0)
    gbv28 = a27["gbv"] * (1 + (g["nights"] + g["adr_exfx"] + g["fx"]) / 100.0)
    take28 = (a27["revenue"] - (a27["gbv"] * take_bps_extra / 10000.0 if qtouch_ok else 0.0)) / a27["gbv"] + (g["take_bps"] + take_bps_extra) / 10000.0
    a28 = dict(revenue=gbv28 * take28, nights=n28, gbv=gbv28)
    a28["cor"] = a27["cor"] * (gbv28 / a27["gbv"]) ** e_cor * (1 + T["cor"]["FY2028E"] / 100.0)
    a28["ops"] = a27["ops"] * (n28 / a27["nights"]) ** e_ops * (1 + T["ops"]["FY2028E"] / 100.0)
    for L in ("pd", "brand", "field", "ga"):
        a28[L] = a27[L] * (1 + T[L]["FY2028E"] / 100.0)
    a28["addbacks"] = ADDBACK_PCT / 100.0 * a28["revenue"]
    ann["FY2028E"] = a28
    for a in ann.values():
        a["cash_costs"] = sum(a[L] for L in LINES)
        a["adj_ebitda"] = a["revenue"] - a["cash_costs"] + a["addbacks"]
        a["margin"] = 100.0 * a["adj_ebitda"] / a["revenue"]
    return st, ann


FWD = {(pr, s): project(pr, s) for pr in PROFILES for s in SCEN}

fwd_rows = []
for (pr, s), (st, ann) in FWD.items():
    for per, row, ptype in ([(q, st[q], "quarter") for q in QS] + [(y, ann[y], "year") for y in YRS]):
        yr = QYEAR.get(per, per)
        for L in LINES:
            fwd_rows.append(dict(period=per, period_type=ptype, profile=pr, scenario=s, line=L,
                                 line_label=LINES[L][0], value_musd=row[L], per_night=row[L] / row["nights"],
                                 per_100gbv=100 * row[L] / row["gbv"], pct_of_revenue=100 * row[L] / row["revenue"],
                                 driver="%s, imposed elasticity %.1f" % (FITR[L]["driver"] or "trend only",
                                                                        FITR[L]["elasticity"]),
                                 target_pct=TARGETS[pr][L][yr], unit=UNIT[L],
                                 source=("historical fit only (no overlay)" if pr == "historical"
                                         else "31b_overlay_parameters.csv, profile=" + pr)))
        for k, lab in [("revenue", "Revenue"), ("nights", "Nights"), ("gbv", "GBV"),
                       ("cash_costs", "Total cash cost ex-SBC"), ("addbacks", "D&A and other add-backs"),
                       ("adj_ebitda", "Adjusted EBITDA")]:
            fwd_rows.append(dict(period=per, period_type=ptype, profile=pr, scenario=s, line=k, line_label=lab,
                                 value_musd=row[k], per_night=row[k] / row["nights"],
                                 per_100gbv=100 * row[k] / row["gbv"], pct_of_revenue=100 * row[k] / row["revenue"],
                                 driver="memo", target_pct=np.nan, unit="$m",
                                 source="workstream-29 driver path (revenue, nights, GBV); identity for the rest"))
        fwd_rows.append(dict(period=per, period_type=ptype, profile=pr, scenario=s, line="margin",
                             line_label="Adjusted EBITDA margin", value_musd=np.nan, per_night=np.nan,
                             per_100gbv=np.nan, pct_of_revenue=row["margin"], driver="memo", target_pct=np.nan,
                             unit="%", source="revenue less cash costs plus add-backs, over revenue"))
FW = pd.DataFrame(fwd_rows)
FW.to_csv(OUT / "31b_forward_margin_by_profile.csv", index=False)
for pr in PROFILES:
    print("[D] %-11s margin  FY26 %s | FY27 %s | FY28 %s"
          % (pr, " / ".join("%.1f" % FWD[(pr, s)][1]["FY2026E"]["margin"] for s in SCEN),
             " / ".join("%.1f" % FWD[(pr, s)][1]["FY2027E"]["margin"] for s in SCEN),
             " / ".join("%.1f" % FWD[(pr, s)][1]["FY2028E"]["margin"] for s in SCEN)))


# ---- FY25 -> FY26 -> FY27 -> FY28 walk by lever, for each profile
def fy_fx_pp(scenario, year):
    """revenue-weighted FX points on revenue for a forecast year."""
    if year == "FY2026E":
        qs = [("1Q26", 3.0), ("2Q26", 4.0), ("3Q26", drivers[scenario]["3Q26"]["fx_pp"]),
              ("4Q26", drivers[scenario]["4Q26"]["fx_pp"])]
        w = [float(ACT.loc[PY4.get(q, {"1Q26": "1Q25", "2Q26": "2Q25"}.get(q, q)), "revenue"])
             if q in PY4 else float(ACT.loc[{"1Q26": "1Q25", "2Q26": "2Q25"}[q], "revenue"]) for q, _ in qs]
        return float(np.average([v for _, v in qs], weights=w))
    if year == "FY2027E":
        qs = [(q, drivers[scenario][q]["fx_pp"]) for q in ("1Q27", "2Q27", "3Q27", "4Q27")]
        w = [float(ACT.loc[PY4[q], "revenue"]) if PY4[q] in ACT.index else 1.0 for q, _ in qs]
        return float(np.average([v for _, v in qs], weights=w))
    return FY28_LEV[scenario]["fx"]


def walk(a0, a1, fx_pp, bridge, profile, scenario):
    rows = []
    rpn0, rpn1 = a0["revenue"] / a0["nights"], a1["revenue"] / a1["nights"]
    adr0, adr1 = a0["gbv"] / a0["nights"], a1["gbv"] / a1["nights"]
    tk0, tk1 = a0["revenue"] / a0["gbv"], a1["revenue"] / a1["gbv"]
    dlrpn, dladr, dltk = np.log(rpn1 / rpn0), np.log(adr1 / adr0), np.log(tk1 / tk0)
    dln = np.log(a1["nights"] / a0["nights"])
    tot_unit = tot_rpn = 0.0
    for L in LINES:
        c0, c1 = a0[L] / a0["nights"], a1[L] / a1["nights"]
        unit = -(c1 - c0) / rpn0 * 100.0
        rpne = -c1 * (1.0 / rpn1 - 1.0 / rpn0) * 100.0
        tot_unit += unit
        tot_rpn += rpne
        dlc = np.log(c1 / c0)
        f = FITR[L]["fixed_share"]
        parts = {}
        if L == "cor":
            parts["GBV pass-through (ADR on a per-night cost)"] = dladr
        parts["Nights leverage (fixed share %.0f%%)" % (100 * f)] = -f * dln
        parts["Per-unit cost change (%s)" % FITR[L]["basis"]] = dlc - sum(parts.values())
        for k, v in parts.items():
            sh = (v / dlc) if abs(dlc) > 1e-9 else (1.0 if k.startswith("Per-unit") else 0.0)
            rows.append(dict(bridge=bridge, profile=profile, scenario=scenario,
                             group="Cost line: " + LINES[L][0], component=k, margin_pts=unit * sh,
                             detail="$%.2f -> $%.2f per night" % (c0, c1)))
    terms = {"Take rate": dltk, "FX": fx_pp / 100.0, "ADR ex-FX": dladr - fx_pp / 100.0}
    for lab, v in terms.items():
        sh = (v / dlrpn) if abs(dlrpn) > 1e-9 else 0.0
        rows.append(dict(bridge=bridge, profile=profile, scenario=scenario, group="Revenue per night",
                         component=lab, margin_pts=tot_rpn * sh,
                         detail="revenue per night $%.2f -> $%.2f" % (rpn0, rpn1)))
    ab = (a1["addbacks"] / a1["revenue"] - a0["addbacks"] / a0["revenue"]) * 100.0
    rows.append(dict(bridge=bridge, profile=profile, scenario=scenario, group="Add-backs",
                     component="D&A and other add-backs", margin_pts=ab,
                     detail="%.1f%% -> %.1f%% of revenue" % (100 * a0["addbacks"] / a0["revenue"],
                                                            100 * a1["addbacks"] / a1["revenue"])))
    m0 = 100 * a0["adj_ebitda"] / a0["revenue"]
    m1 = 100 * a1["adj_ebitda"] / a1["revenue"]
    tot = sum(r["margin_pts"] for r in rows)
    assert abs(tot - (m1 - m0)) < 0.05, "%s %s walk off by %.3f" % (bridge, profile, tot - (m1 - m0))
    rows.append(dict(bridge=bridge, profile=profile, scenario=scenario, group="TOTAL",
                     component="Change in Adjusted EBITDA margin", margin_pts=m1 - m0,
                     detail="%.2f%% -> %.2f%%" % (m0, m1)))
    return rows


walk_rows = []
for pr in PROFILES:
    for s in SCEN:
        _, ann = FWD[(pr, s)]
        prevs = [("FY2025->FY2026E", FY25, ann["FY2026E"], "FY2026E"),
                 ("FY2026E->FY2027E", ann["FY2026E"], ann["FY2027E"], "FY2027E"),
                 ("FY2027E->FY2028E", ann["FY2027E"], ann["FY2028E"], "FY2028E")]
        for bridge, a0, a1, yr in prevs:
            walk_rows.append(walk(a0, a1, fy_fx_pp(s, yr), bridge, pr, s))
WK = pd.DataFrame([r for g in walk_rows for r in g])
WK["margin_pts"] = WK.margin_pts.round(3)
WK["evidence"] = ("cost lines from 31b_forward_margin_by_profile.csv; the split follows the "
                  "abnb_margin_bridge.csv convention (unit-cost effect at held revenue per night, then the "
                  "revenue-per-night effect allocated log-linearly across take rate, FX and ADR ex-FX); "
                  "fixed shares from the levels regressions in 31b_line_elasticities.csv")
WK.to_csv(OUT / "31b_margin_bridge_fy26_fy28.csv", index=False)
print("[D] margin walks: %d rows -> 31b_margin_bridge_fy26_fy28.csv" % len(WK))


# ================================================================= E. sensitivities
SENS = [
    ("+1pt nights growth", ("nights", 1.0), "%", "workstream-29 nights path shifted by a point in every quarter and FY28"),
    ("+1pt ADR ex-FX", ("adr_exfx", 1.0), "%", "ADR ex-FX shifted by a point; flows to GBV and revenue, and to cost of revenue through GBV"),
    ("+1pt FX on revenue", ("fx", 1.0), "%", "FX points on revenue shifted by one; costs are treated as USD except cost of revenue, which follows GBV"),
    ("+10bp take rate", ("take_bps", 10.0), "bps", "10bp added to revenue over GBV; no cost line moves"),
    ("-10% support cost per night", ("ops_cpn", -10.0), "%", "operations and support per-night target cut by 10 points in every year"),
    ("+5pt brand marketing growth", ("brand_g", 5.0), "%", "brand and performance marketing growth target raised 5 points in every year"),
    ("+1pt nights share to LatAm/APAC", ("regional_mix", 1.0), "pt of share",
     "1 point of nights share out of NA (regional ADR index 1.42) into LatAm and APAC (nights-weighted index 0.632, "
     "10_regional_panel_quarterly.csv); read as a -0.79% hit to blended ADR"),
]
sens_rows = []
for pr in ("base", "management"):
    _, base_ann = FWD[(pr, "base")]
    for lab, tw, unit, ev in SENS:
        for scope, stag in (("all", "shock in every year FY26-FY28"), ("FY2028E", "shock in FY2028 only")):
            _, ann = project(pr, "base", tweak=(tw[0], tw[1], scope))
            for y in YRS:
                if scope == "FY2028E" and y != "FY2028E":
                    continue
                sens_rows.append(dict(profile=pr, scenario="base", shock=lab, unit=unit, scope=stag, year=y,
                                      margin_pts=round(ann[y]["margin"] - base_ann[y]["margin"], 3),
                                      adj_ebitda_delta_musd=round(ann[y]["adj_ebitda"] - base_ann[y]["adj_ebitda"], 1),
                                      revenue_delta_musd=round(ann[y]["revenue"] - base_ann[y]["revenue"], 1),
                                      baseline_margin_pct=round(base_ann[y]["margin"], 2), evidence=ev))
# elasticity uncertainty: the imposed elasticities at their leave-one-year-out bounds
_, base_ann = FWD[("base", "base")]
for lab, kw, ev in (
        ("cost of revenue GBV elasticity 1.00 -> 0.96", dict(e_cor=0.96),
         "leave-one-year-out low for the cost-of-revenue elasticity to GBV (31b_line_elasticities.csv)"),
        ("cost of revenue GBV elasticity 1.00 -> 1.11", dict(e_cor=1.11),
         "leave-one-year-out high for the cost-of-revenue elasticity to GBV"),
        ("support nights elasticity 1.00 -> 0.41", dict(e_ops=0.41),
         "leave-one-year-out low for the operations-and-support elasticity to nights; the unrestricted point "
         "estimate is 1.39 and the LOO range is 0.41 to 1.66, so this line is the least identified in the model"),
        ("support nights elasticity 1.00 -> 1.66", dict(e_ops=1.66),
         "leave-one-year-out high for the operations-and-support elasticity to nights")):
    _, ann = project("base", "base", **kw)
    for y in YRS:
        sens_rows.append(dict(profile="base", scenario="base", shock=lab, unit="elasticity",
                              scope="applies to every year FY26-FY28", year=y,
                              margin_pts=round(ann[y]["margin"] - base_ann[y]["margin"], 3),
                              adj_ebitda_delta_musd=round(ann[y]["adj_ebitda"] - base_ann[y]["adj_ebitda"], 1),
                              revenue_delta_musd=0.0,
                              baseline_margin_pct=round(base_ann[y]["margin"], 2), evidence=ev))
SENS_DF = pd.DataFrame(sens_rows)
SENS_DF.to_csv(OUT / "31b_sensitivities.csv", index=False)
print("[E] sensitivities, base profile (single-year shock in FY2028 | shock in every year FY26-FY28):")
for lab, _, _, _ in SENS:
    a = SENS_DF[(SENS_DF.profile == "base") & (SENS_DF.shock == lab) & (SENS_DF.year == "FY2028E")
                & (SENS_DF.scope == "shock in FY2028 only")].iloc[0]
    b = SENS_DF[(SENS_DF.profile == "base") & (SENS_DF.shock == lab) & (SENS_DF.year == "FY2028E")
                & (SENS_DF.scope == "shock in every year FY26-FY28")].iloc[0]
    print("     %-34s %+5.2f pts (single year) | %+5.2f pts (compounded)  %+7.0f $m"
          % (lab, a.margin_pts, b.margin_pts, b.adj_ebitda_delta_musd))


# ================================================================= F. reconciliation and figures
sum30 = pd.read_csv(OUT / "30_fy_summary.csv").set_index("scenario")
res07 = lev07[lev07.row_type == "result"]


def r07(scn, yr, item):
    r = res07[(res07.scenario == scn.capitalize()) & (res07.year == yr) & (res07.item == item)]
    return float(r.value.iloc[0]) if len(r) else np.nan


rec_rows = []
for pr in PROFILES:
    for s in SCEN:
        _, ann = FWD[(pr, s)]
        for y, item30, item07 in (("FY2026E", "fy26_margin_pct", "FY2026E"), ("FY2027E", "fy27_margin_pct", "FY2027E"),
                                  ("FY2028E", None, "FY2028E")):
            mine = ann[y]["margin"]
            m30 = float(sum30.loc[s, item30]) if item30 else np.nan
            m07 = r07(s, item07, "Adjusted EBITDA margin")
            rec_rows.append(dict(period=y, period_type="reconciliation", profile=pr, scenario=s,
                                 line="margin_vs_30_walk", line_label="This model less the workstream-30 walk",
                                 value_musd=np.nan, per_night=np.nan, per_100gbv=np.nan,
                                 pct_of_revenue=(mine - m30) if not np.isnan(m30) else np.nan, driver="reconciliation",
                                 target_pct=np.nan, unit="margin points",
                                 source="30_fy_summary.csv %s = %.2f%%; this model %.2f%%. Same workstream-29 top "
                                        "line (reconciled to $1m); the difference is the cost set: 30 phases H2 2026 "
                                        "brand marketing +28%%/+10%% by quarter, this model runs an annual target "
                                        "through an H2 residual, and 30's field-ops and G&A quarterly growth rates "
                                        "differ from the annual targets here"
                                        % (y, m30, mine) if not np.isnan(m30) else "30 walk stops at FY2027"))
            rec_rows.append(dict(period=y, period_type="reconciliation", profile=pr, scenario=s,
                                 line="margin_vs_07_levers", line_label="This model less the workstream-07 lever model",
                                 value_musd=np.nan, per_night=np.nan, per_100gbv=np.nan,
                                 pct_of_revenue=(mine - m07) if not np.isnan(m07) else np.nan, driver="reconciliation",
                                 target_pct=np.nan, unit="margin points",
                                 source="07_margin_levers_fy26_fy28.csv %s = %.2f%%; this model %.2f%%. 07 applies "
                                        "its levers to its own revenue build; this model applies them to the "
                                        "workstream-29 quarterly path, so the revenue bases differ "
                                        "(FY28 $%.0fm here against $%.0fm in 07)"
                                        % (y, m07, mine, ann["FY2028E"]["revenue"], r07(s, "FY2028E", "Revenue"))))
FW = pd.concat([FW, pd.DataFrame(rec_rows)], ignore_index=True)
FW.to_csv(OUT / "31b_forward_margin_by_profile.csv", index=False)
for s in SCEN:
    print("[F] %-5s base profile vs 30 walk / 07 levers: FY26 %+.2f / %+.2f | FY27 %+.2f / %+.2f | FY28 n.a. / %+.2f pts"
          % (s,
             FWD[("base", s)][1]["FY2026E"]["margin"] - float(sum30.loc[s, "fy26_margin_pct"]),
             FWD[("base", s)][1]["FY2026E"]["margin"] - r07(s, "FY2026E", "Adjusted EBITDA margin"),
             FWD[("base", s)][1]["FY2027E"]["margin"] - float(sum30.loc[s, "fy27_margin_pct"]),
             FWD[("base", s)][1]["FY2027E"]["margin"] - r07(s, "FY2027E", "Adjusted EBITDA margin"),
             FWD[("base", s)][1]["FY2028E"]["margin"] - r07(s, "FY2028E", "Adjusted EBITDA margin")))


def finish(ax, title, sub=None):
    ax.set_title(title, loc="left", pad=(14 if sub else 6))
    if sub:
        ax.text(0, 1.02, sub, transform=ax.transAxes, color=MUTED, fontsize=7.5, va="bottom")
    for sp in ("top", "right"):
        ax.spines[sp].set_visible(False)


# --- figure 1: elasticities with leave-one-year-out ranges
prim = elas[(elas.spec == "dlog4 (primary)") & (elas.is_natural_driver)].set_index("line")
fig, ax = plt.subplots(figsize=(6.6, 3.4))
LO, HI = -3.0, 3.0
ys = np.arange(len(LINES))[::-1]
labels = []
for i, L in enumerate(LINES):
    r = prim.loc[L]
    y = ys[i]
    lo, hi = max(r.elasticity_loo_min, LO), min(r.elasticity_loo_max, HI)
    ax.plot([lo, hi], [y, y], color=GRID, lw=3.5, solid_capstyle="butt", zorder=1)
    ok = bool(r.promote)
    col = BLUE if ok else NEUTRAL
    e = float(np.clip(r.elasticity, LO, HI))
    ax.plot([e], [y], "o", ms=5, color=col, zorder=3,
            marker=("o" if LO < r.elasticity < HI else ("<" if r.elasticity <= LO else ">")))
    ax.text(HI + 0.15, y, "%+.2f   R2 %.2f   %s" % (r.elasticity, r.r2, "usable" if ok else "not identified"),
            va="center", fontsize=7.2, color=(INK if ok else MUTED))
    labels.append(LINES[L][0] + chr(10) + "~ " + str(r.driver))
ax.axvline(1.0, color=RED, lw=0.8, ls=(0, (4, 3)))
ax.axvline(0.0, color=GRID, lw=0.8)
ax.set_yticks(ys)
ax.set_yticklabels(labels, fontsize=7.2, color=INK)
ax.tick_params(axis="y", pad=2)
ax.set_xlim(LO - 0.1, HI + 2.6)
ax.set_ylim(-0.6, len(LINES) - 0.4)
ax.set_xticks([-3, -2, -1, 0, 1, 2, 3])
ax.set_xlabel("elasticity of the cash cost line to its driver, year-on-year log differences")
ax.grid(axis="x", lw=0.5)
ax.set_axisbelow(True)
ax.text(1.06, len(LINES) - 0.55, "proportional", color=RED, fontsize=7, va="top")
finish(ax, "Only cost of revenue has a driver relationship tight enough to forecast with",
       "point estimate and leave-one-year-out range, 1Q23-2Q26 (n=14); arrows mark estimates outside the axis")
fig.tight_layout()
fig.savefig(FIG / "31b_line_elasticities.png", bbox_inches="tight")
plt.close(fig)

# --- figure 2: annual margin decomposition
GROUPS = [("Revenue per night", BLUE), ("Cost line: Cost of revenue", "#a8c6ef"),
          ("Cost line: Operations and support", "#cfe0f6"), ("Cost line: Product development", "#f6c9c6"),
          ("Cost line: Brand and performance marketing", RED), ("Cost line: Field operations and policy", "#ef8b89"),
          ("GA_AB", NEUTRAL)]
GLAB = {"Revenue per night": "Revenue per night", "Cost line: Cost of revenue": "Cost of revenue",
        "Cost line: Operations and support": "Operations and support",
        "Cost line: Product development": "Product development",
        "Cost line: Brand and performance marketing": "Brand and performance marketing",
        "Cost line: Field operations and policy": "Field operations and policy",
        "GA_AB": "G&A and add-backs (the 2023 Italy reserve nets out inside this pair)"}
agg = D[D.group != "TOTAL"].groupby(["bridge", "group"]).margin_pts.sum().unstack(fill_value=0.0)
agg["GA_AB"] = agg.get("Cost line: General and administrative", 0.0) + agg.get("Add-backs", 0.0)
PANELS = [(["FY2019->FY2022"], ["2019 to 2022"], "the 4,000bp build"),
          (["FY2022->FY2023", "FY2023->FY2024", "FY2024->FY2025", "1H2025->1H2026"],
           ["2022 to 2023", "2023 to 2024", "2024 to 2025", "1H25 to 1H26"], "since then")]
fig, axes = plt.subplots(1, 2, figsize=(8.0, 3.9), gridspec_kw=dict(width_ratios=[1, 3.1]))
for ax, (legs, xlabs, sub) in zip(axes, PANELS):
    xs = np.arange(len(legs))
    pos = np.zeros(len(legs)); neg = np.zeros(len(legs))
    for g, c in GROUPS:
        v = np.array([agg.loc[b, g] if g in agg.columns else 0.0 for b in legs])
        bot = np.where(v >= 0, pos, neg)
        ax.bar(xs, v, 0.55, bottom=bot, color=c, edgecolor=SURFACE, lw=0.6, label=GLAB[g])
        pos = pos + np.where(v >= 0, v, 0); neg = neg + np.where(v < 0, v, 0)
    tot = np.array([D[(D.bridge == b) & (D.group == "TOTAL")].margin_pts.iloc[0] for b in legs])
    ax.plot(xs, tot, "o", color=INK, ms=5, zorder=5)
    for x, t in zip(xs, tot):
        ax.annotate("%+.1f" % t, (x, t), textcoords="offset points", xytext=(0, 9), ha="center",
                    fontsize=7.6, color=INK)
    ax.axhline(0, color=INK, lw=0.7)
    ax.set_xticks(xs); ax.set_xticklabels(xlabs, fontsize=7.5)
    ax.set_xlim(-0.6, len(legs) - 0.4)
    ax.grid(axis="y", lw=0.5); ax.set_axisbelow(True)
    for sp in ("top", "right"):
        ax.spines[sp].set_visible(False)
    ax.text(0, 1.03, sub, transform=ax.transAxes, color=MUTED, fontsize=7.5, va="bottom")
axes[0].set_ylabel("margin points")
h, l = axes[1].get_legend_handles_labels()
axes[1].legend(h, l, frameon=False, fontsize=6.9, ncol=2, loc="upper left", bbox_to_anchor=(-0.36, -0.13),
               handlelength=1.0, borderpad=0.1, columnspacing=1.2)
fig.suptitle("Revenue per night built the margin and has paid for the marketing ramp ever since",
             x=0.005, ha="left", fontsize=9.5, y=1.10)
fig.text(0.005, 1.015, "change in Adjusted EBITDA margin, cash (ex-SBC) stack; black dot is the total",
         color=MUTED, fontsize=7.5, ha="left", va="bottom")
fig.tight_layout()
fig.savefig(FIG / "31b_margin_decomposition_annual.png", bbox_inches="tight")
plt.close(fig)

# --- figure 3: forward margin by profile
fig, ax = plt.subplots(figsize=(6.4, 3.2))
xs = np.arange(4)
hist_m = [FY25["margin"]] + [FWD[("historical", "base")][1][y]["margin"] for y in YRS]
mgmt_m = [FY25["margin"]] + [FWD[("management", "base")][1][y]["margin"] for y in YRS]
base_m = [FY25["margin"]] + [FWD[("base", "base")][1][y]["margin"] for y in YRS]
for ser, col, lab in ((hist_m, RED, "historical: elasticities and trends only"),
                      (mgmt_m, BLUE, "management: what the statements imply"),
                      (base_m, INK, "base: judgement")):
    ax.plot(xs, ser, color=col, lw=1.4, marker="o", ms=3.5)
    ax.annotate("%s  %.1f%%" % (lab, ser[-1]), (xs[-1], ser[-1]), textcoords="offset points", xytext=(6, 0),
                va="center", fontsize=7.3, color=col)
ax.plot([3], [r07("base", "FY2028E", "Adjusted EBITDA margin")], "s", ms=4, color=MUTED)
ax.annotate("07 lever model 37.5%", (3, r07("base", "FY2028E", "Adjusted EBITDA margin")),
            textcoords="offset points", xytext=(-8, 6), ha="right", fontsize=7.0, color=MUTED)
ax.axhline(35.5, color=GRID, lw=0.9, ls=(0, (4, 3)))
ax.text(0.02, 35.6, "FY26 guide floor 35.5%", color=MUTED, fontsize=7)
ax.set_xticks(xs)
ax.set_xticklabels(["FY2025A", "FY2026E", "FY2027E", "FY2028E"], fontsize=7.6)
ax.set_xlim(-0.15, 4.35)
ax.set_ylabel("Adjusted EBITDA margin, %")
ax.grid(axis="y", lw=0.5)
ax.set_axisbelow(True)
finish(ax, "Pure history loses about half a point a year; the gap to management is field ops and G&A",
       "base revenue scenario (workstream-29 driver path) under each cost profile")
fig.tight_layout()
fig.savefig(FIG / "31b_forward_profiles.png", bbox_inches="tight")
plt.close(fig)

# --- figure 4: sensitivity tornado, FY2028E, single-year shock
sv = SENS_DF[(SENS_DF.profile == "base") & (SENS_DF.year == "FY2028E")
             & (SENS_DF.scope == "shock in FY2028 only")].set_index("shock")
order = sv.margin_pts.abs().sort_values().index
fig, ax = plt.subplots(figsize=(6.4, 2.9))
ys = np.arange(len(order))
vals = sv.loc[order, "margin_pts"].values
ax.barh(ys, vals, 0.55, color=[BLUE if v >= 0 else RED for v in vals], edgecolor=SURFACE, lw=0.6)
for y, v, lab in zip(ys, vals, order):
    ax.text(v + (0.03 if v >= 0 else -0.03), y, "%+.2f" % v, va="center",
            ha="left" if v >= 0 else "right", fontsize=7.3, color=INK)
    ax.text(-1.72, y, lab, va="center", ha="left", fontsize=7.3, color=INK)
ax.axvline(0, color=INK, lw=0.7)
ax.set_yticks([])
ax.set_xlim(-1.75, 1.05)
ax.set_xticks([-1.0, -0.5, 0.0, 0.5, 1.0])
ax.set_xlabel("FY2028E Adjusted EBITDA margin, points")
ax.grid(axis="x", lw=0.5)
ax.set_axisbelow(True)
finish(ax, "Support cost per night is still the largest lever management controls",
       "base profile, base revenue scenario; each shock applied in FY2028 alone")
fig.tight_layout()
fig.savefig(FIG / "31b_sensitivities.png", bbox_inches="tight")
plt.close(fig)
print("[F] figures written: 31b_line_elasticities.png, 31b_margin_decomposition_annual.png, "
      "31b_forward_profiles.png, 31b_sensitivities.png")
