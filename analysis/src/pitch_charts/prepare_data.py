"""
pitch_charts / prepare_data.py: datasets behind the two-pager chart candidates (stock reaction, revenue drivers, nights and RNPL).

Run:  py -3.13 analysis/src/pitch_charts/prepare_data.py   (exit 0; writes data/processed/pitch_charts/)
Then: Rscript analysis/src/pitch_charts/charts.R

Every number is read from a committed file on main (paths in SOURCES below) or quoted from a committed note with its
section; nothing is re-estimated here except descriptive statistics (group means, OLS fits, rank-sum tests).
"""
from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pandas as pd
from scipy import stats

ROOT = Path(__file__).resolve().parents[3]
OUT = ROOT / "data/processed/pitch_charts"
OUT.mkdir(parents=True, exist_ok=True)
SOURCES: dict[str, str] = {}


def qkey(q: str) -> int:
    """'3Q24' -> 20243 for sorting."""
    return 2000_0 + int(q[2:]) * 10 + int(q[0])


def save(df: pd.DataFrame, name: str, src: str) -> None:
    df.to_csv(OUT / name, index=False)
    SOURCES[name] = src
    print(f"wrote {name} ({len(df)} rows)")


# ======================================================================================================================
# 1. Stock reaction at prints
# ======================================================================================================================
PANEL = "data/processed/abnb_guidance_reaction_panel.csv"
HIST = "model/ABNB_historicals.xlsx"
C01 = "docs/pitch-forecasts/SYNTHESIS.md (C01) and forecast_table.csv"

pan = pd.read_csv(ROOT / PANEL)
earn = pd.read_excel(ROOT / HIST, sheet_name="Earnings", header=3)
earn = earn[earn["Print"].astype(str).str.match(r"^\dQ\d\d$")]
earn = earn.rename(columns={"Print": "quarter", "Excess 20d": "exc_20d_frac", "Rev vs Street": "rev_vs_street"})[
    ["quarter", "exc_20d_frac", "rev_vs_street"]]
r = pan.merge(earn, on="quarter", how="left")
r["exc_20d"] = r.exc_20d_frac * 100
# nights direction of the next-quarter guide: coded direction, else the sign of the numeric guide-implied change
nd = r.nq_nights_dir.copy()
fill = nd.isna() & r.nq_nights_guide_pts.notna()
nd[fill] = np.sign(r.nq_nights_guide_pts[fill])
r["nights_guide_down"] = np.where(nd.isna(), np.nan, (nd < 0).astype(float))
r["guide_group"] = np.select([r.guide_vs_street_pct > 0, r.guide_vs_street_pct < 0], ["above", "below"], "none")
r["order"] = r.quarter.map(qkey).rank().astype(int)
cols = ["quarter", "order", "print_date", "exc_1d", "exc_5d", "exc_20d", "rev_surprise", "rev_vs_street", "nights_surprise",
        "guide_vs_street_pct", "guide_group", "nights_guide_down", "nq_nights_dir", "nq_nights_guide_pts"]
save(r[cols], "s01_prints.csv", f"{PANEL}; {HIST} sheet Earnings (Excess 20d, Rev vs Street)")

g = r[r.guide_group != "none"]
rows = []
for h in ("exc_1d", "exc_5d", "exc_20d"):
    a, b = g[g.guide_group == "above"][h], g[g.guide_group == "below"][h]
    p = stats.mannwhitneyu(a, b).pvalue
    for grp, x in (("above", a), ("below", b)):
        rows.append(dict(horizon=h, group=grp, n=len(x), mean=x.mean(), median=x.median(), n_neg=int((x < 0).sum()),
                         se=x.std(ddof=1) / np.sqrt(len(x)), rank_sum_p=p))
save(pd.DataFrame(rows), "s02_group_horizons.csv", "s01_prints.csv; Wilcoxon rank-sum (Mann-Whitney U) per horizon")

fits = []
for lab, d in (("all", g), ("ex_4Q21", g[g.quarter != "4Q21"])):
    f = stats.linregress(d.guide_vs_street_pct, d.exc_1d)
    fits.append(dict(sample=lab, x="guide_vs_street_pct", n=len(d), slope=f.slope, intercept=f.intercept, r2=f.rvalue ** 2, p=f.pvalue))
f = stats.linregress(r.rev_surprise, r.exc_1d)
fits.append(dict(sample="all", x="rev_surprise", n=len(r), slope=f.slope, intercept=f.intercept, r2=f.rvalue ** 2, p=f.pvalue))
d22 = r[r.quarter.map(qkey) >= qkey("1Q22")]  # same prints in both panels of the beat-vs-guide chart
for x in ("rev_surprise", "guide_vs_street_pct"):
    f = stats.linregress(d22[x], d22.exc_1d)
    fits.append(dict(sample="1Q22_on", x=x, n=len(d22), slope=f.slope, intercept=f.intercept, r2=f.rvalue ** 2, p=f.pvalue))
save(pd.DataFrame(fits), "s03_fits.csv", "s01_prints.csv; OLS day-1 excess return on each x")

cells = []
for gg in ("below", "above"):
    for down in (1.0, 0.0):
        d = g[(g.guide_group == gg) & (g.nights_guide_down == down)]
        cells.append(dict(guide=gg, nights_down=int(down), n=len(d), mean=d.exc_1d.mean(), n_neg=int((d.exc_1d < 0).sum()),
                          prints=" ".join(f"{q} {v:+.1f}" for q, v in zip(d.quarter, d.exc_1d))))
uncoded = g[g.nights_guide_down.isna()].quarter.tolist()
cells.append(dict(guide="uncoded", nights_down=-1, n=len(uncoded), mean=np.nan, n_neg=0, prints=" ".join(uncoded)))
save(pd.DataFrame(cells), "s04_two_gates.csv", "s01_prints.csv; nights direction = nq_nights_dir, else sign of nq_nights_guide_pts")

# 5 Nov: our 4Q26 revenue-guide call (pitch-forecasts C01, audited) against the LSEG-family Street mean
street_4q26 = 3161.0
call = dict(p5=2945.0, p50=3100.0, p95=3265.0, p_below=0.72)   # audited on bridge-v3 GBV; re-marked below for the ADR line


# ======================================================================================================================
# 2. Revenue growth drivers: nights x ADR ex-FX x FX x take rate
# ======================================================================================================================
# Exact identity: revenue = nights x ADR x take rate, with ADR y/y = ex-FX ADR y/y + FX (the letters' convention:
# FX = reported minus ex-FX ADR growth). Contributions are log shares scaled so the four bars sum to reported revenue
# growth exactly. History: letters (ex-FX ADR in whole points) and the 02 KPI panel. Forecast: the official model on
# main (model/ABNB_official_model_complete.xlsx, DEC-0042); ADR ex-FX / FX split from the ADR engine.
# ADR_LINE picks the ADR path; revenue is recomputed as nights x ADR x take rate (DEC-0018) and adjusted EBITDA as
# revenue less the official model's cash costs, carried flat in dollars (DEC-0022), so margin is an output:
#   kl        default: snapshot of PR #67's engine v3 with fixes (k) LOS nowcast and (l) World Cup out of the core,
#             copied from the ../citadel-abnb-adrfix working tree at 23 Sep 19:16 (inputs/README.txt)
#   main      engine v2 on main (reproduces the official workbook exactly)
#   v3        PR #67 as committed (origin/krish/adr-audit-fixes, through fix j)
#   worktree  PR #67's live working tree, or set ADR_FILE to any adr_path.csv
import os
import subprocess

KPI = "data/processed/overnight/02_kpi_panel_quarterly.csv"
OFFICIAL = "model/ABNB_official_model_complete.xlsx"
ADR_LINE = os.environ.get("ADR_LINE", "kl")
ADR_MAIN = "data/processed/pitch_model_v2/adr_engine/adr_path.csv"
ADR_PATH = {"kl": "data/processed/pitch_charts/inputs/adr_path_v3_kl_2026-09-23.csv",
            "main": ADR_MAIN,
            "v3": "origin/krish/adr-audit-fixes:data/processed/pitch_model_v2/adr_engine_v3/adr_path.csv",
            "worktree": os.environ.get("ADR_FILE", str(ROOT.parent / "citadel-abnb-adrfix/data/processed/pitch_model_v2/adr_engine_v3/adr_path.csv"))}[ADR_LINE]
ADR_LABEL = {"kl": "ADR engine v3 with fixes (k) LOS and (l) World Cup, 23 Sep (PR #67 working tree)",
             "main": "ADR engine v2 (main)", "v3": "ADR engine v3 through fix (j) (PR #67 as committed)",
             "worktree": "ADR engine v3, PR #67 live working tree"}[ADR_LINE]
PATH06 = "data/processed/margin_build/06_fy27_path_v2/06_revenue_path_3q26_4q27_v2b.csv"
STREET_E = "data/processed/reverse_dcf/E/E_street_distribution_vs_team.csv"
STREET_REV = {"3Q26": 4744.32, "4Q26": 3161.82}  # LSEG family, 13 Sep 2026 pull (official model row 39; DEC-0013)
FQ = ["3Q26", "4Q26", "1Q27", "2Q27", "3Q27", "4Q27"]

kpi = pd.read_csv(ROOT / KPI).set_index("quarter")
kpi["tr"] = kpi.revenue_musd / (kpi.gbv_busd * 1000) * 100

ws = pd.read_excel(ROOT / OFFICIAL, sheet_name="Income_Statement", header=None)
hdr = ws.iloc[3].tolist()
col = {q: hdr.index(f"{q}E") for q in FQ}
row = {lab: i for i, lab in enumerate(ws.iloc[:, 0].astype(str))}
def ofc(label: str, q: str) -> float:
    return float(ws.iloc[row[label], col[q]])
if ADR_LINE == "v3":
    from io import StringIO
    adr = pd.read_csv(StringIO(subprocess.run(["git", "show", ADR_PATH], cwd=ROOT, capture_output=True, text=True, check=True).stdout)).set_index("quarter")
else:
    adr = pd.read_csv(Path(ADR_PATH) if Path(ADR_PATH).is_absolute() else ROOT / ADR_PATH).set_index("quarter")
adr_main = pd.read_csv(ROOT / ADR_MAIN).set_index("quarter")
print(f"ADR line: {ADR_LINE} ({ADR_PATH}); 3Q26 ${adr.loc['3Q26', 'adr_usd']:.2f}, 4Q26 ${adr.loc['4Q26', 'adr_usd']:.2f}")

def prev(q: str) -> str:
    return f"{q[0]}Q{int(q[2:]) - 1}"

lev = {q: dict(nights=kpi.loc[q, "nights_m"], adr=kpi.loc[q, "adr_usd"], tr=kpi.loc[q, "tr"], rev=kpi.loc[q, "revenue_musd"]) for q in kpi.index}
for q in FQ:
    n = ofc("Nights & seats booked (m)", q)
    a = float(adr.loc[q, "adr_usd"])
    t = ofc("    Take rate (revenue / GBV)", q) * 100
    lev[q] = dict(nights=n, adr=a, tr=t, rev=n * a * t / 100)
    if ADR_LINE == "main":
        assert abs(lev[q]["rev"] - ofc("Revenue", q)) < 0.5, (q, lev[q]["rev"], ofc("Revenue", q))

HISTQ = ["1Q23", "2Q23", "3Q23", "4Q23", "1Q24", "2Q24", "3Q24", "4Q24", "1Q25", "2Q25", "3Q25", "4Q25", "1Q26", "2Q26"]
rows = []
for q in HISTQ + FQ:
    p = prev(q)
    g = {k: lev[q][k] / lev[p][k] for k in ("nights", "adr", "tr", "rev")}
    if q in FQ:
        adr_x = float(adr.loc[q, "adr_yoy_exfx_pct"])
        kind = "forecast"
    else:
        adr_x = float(kpi.loc[q, "adr_yoy_exfx_pct"])
        kind = "reported"
    adr_rep = (g["adr"] - 1) * 100
    L = np.log(g["rev"])
    parts = dict(nights=np.log(g["nights"]), adr_exfx=np.log(1 + adr_x / 100), fx=np.log(g["adr"]) - np.log(1 + adr_x / 100), take_rate=np.log(g["tr"]))
    scale = (g["rev"] - 1) * 100 / L
    rows.append(dict(quarter=q, kind=kind, revenue_yoy=(g["rev"] - 1) * 100, nights_yoy=(g["nights"] - 1) * 100, adr_yoy=adr_rep,
                     adr_exfx_yoy=adr_x, adr_fx_pp=adr_rep - adr_x, take_rate_yoy=(g["tr"] - 1) * 100, revenue_musd=lev[q]["rev"],
                     **{f"c_{k}": v * scale for k, v in parts.items()},
                     fx_rev_letter=float(kpi.loc[q, "fx_pts_revenue"]) if q in kpi.index else np.nan))
rd = pd.DataFrame(rows)
p06 = pd.read_csv(ROOT / PATH06)
p06 = p06[(p06.scenario == "base") & (p06.line == "fx_pts_revenue_memo")].set_index("quarter").value
rd["fx_rev_line"] = rd.quarter.map(p06)
save(rd, "r01_revenue_decomposition.csv",
     f"{KPI} (history, letters' ex-FX ADR); {OFFICIAL} Income_Statement (forecast nights, take rate, revenue); {ADR_PATH} (ADR ex-FX/FX, ADR_LINE={ADR_LINE}); "
     f"{PATH06} fx_pts_revenue_memo (team revenue-FX line, DEC-0010)")

# Street for 3Q26/4Q26: nights and ADR (Bloomberg MODL, 12 Sep), revenue (LSEG), take rate implied (DEC-0018)
se = pd.read_csv(ROOT / STREET_E)
srows = []
for q in ("3Q26", "4Q26"):
    n = float(se[(se.quarter == q) & (se.metric == "nights_m")].street_mean.iloc[0])
    a = float(se[(se.quarter == q) & (se.metric == "adr_usd")].street_mean.iloc[0])
    r = STREET_REV[q]
    t = r / (n * a) * 100
    p = prev(q)
    g = dict(nights=n / lev[p]["nights"], adr=a / lev[p]["adr"], tr=t / lev[p]["tr"], rev=r / lev[p]["rev"])
    ours = rd.set_index("quarter").loc[q]
    srows.append(dict(quarter=q, source="Street", nights_yoy=(g["nights"] - 1) * 100, adr_yoy=(g["adr"] - 1) * 100,
                      take_rate_yoy=(g["tr"] - 1) * 100, revenue_yoy=(g["rev"] - 1) * 100, revenue_musd=r))
    srows.append(dict(quarter=q, source="Ours", nights_yoy=ours.nights_yoy, adr_yoy=ours.adr_yoy, take_rate_yoy=ours.take_rate_yoy,
                      revenue_yoy=ours.revenue_yoy, revenue_musd=ours.revenue_musd))
save(pd.DataFrame(srows), "r02_ours_vs_street.csv", f"{STREET_E} (Bloomberg MODL 12 Sep 2026, nights/ADR means); LSEG revenue {STREET_REV}; ours from r01")

# What the ADR line moves: revenue, adjusted EBITDA and margin, this line vs main's engine v2 vs the Street.
# EBITDA = revenue - total cash costs + D&A + add-backs (official workbook rows; costs carried flat in dollars, DEC-0022).
STREET_IS = {  # official workbook rows 39 and 41: LSEG 13 Sep 2026 pull
    "rev": {"3Q26": 4744.32, "4Q26": 3161.82, "1Q27": 3010.32, "2Q27": 4036.94, "3Q27": 5269.97, "4Q27": 3528.92},
    "ebitda": {"3Q26": 2361.52, "4Q26": 913.68, "1Q27": 610.73, "2Q27": 1451.71, "3Q27": 2695.55, "4Q27": 1068.40}}
ADDBACK_I = row["    Adjusted EBITDA margin"] + 1      # add-back memo row (label sits outside column A); 0 in every forecast quarter
def addback(q: str) -> float:
    v = ws.iloc[ADDBACK_I, col[q]]
    return 0.0 if pd.isna(v) else float(v)
H1 = {"rev": 2678.0 + 3608.0, "ebitda": 519.0 + 1261.0}          # 1Q26 + 2Q26 reported
def income(adr_path: pd.DataFrame) -> dict:
    out = {}
    for q in FQ:
        rev = ofc("Nights & seats booked (m)", q) * float(adr_path.loc[q, "adr_usd"]) * ofc("    Take rate (revenue / GBV)", q)
        e = rev - ofc("Total cash costs", q) + ofc("    Depreciation & amortisation", q) + addback(q)
        out[q] = dict(rev=rev, ebitda=e, adr=float(adr_path.loc[q, "adr_usd"]),
                      gbv=ofc("Nights & seats booked (m)", q) * float(adr_path.loc[q, "adr_usd"]))
    return out
inc_new, inc_main = income(adr), income(adr_main)
for q in FQ:   # the recalculation reproduces the official workbook on main's line
    assert abs(inc_main[q]["ebitda"] - ofc("Adjusted EBITDA", q)) < 0.5, (q, inc_main[q]["ebitda"], ofc("Adjusted EBITDA", q))
def periods(inc: dict) -> dict:
    p = {q: dict(rev=inc[q]["rev"], ebitda=inc[q]["ebitda"], adr=inc[q]["adr"]) for q in ("3Q26", "4Q26")}
    p["FY26"] = dict(rev=H1["rev"] + inc["3Q26"]["rev"] + inc["4Q26"]["rev"], ebitda=H1["ebitda"] + inc["3Q26"]["ebitda"] + inc["4Q26"]["ebitda"], adr=np.nan)
    q27 = ["1Q27", "2Q27", "3Q27", "4Q27"]
    p["FY27"] = dict(rev=sum(inc[q]["rev"] for q in q27), ebitda=sum(inc[q]["ebitda"] for q in q27), adr=np.nan)
    return p
pn, pm = periods(inc_new), periods(inc_main)
st_p = {q: dict(rev=STREET_IS["rev"][q], ebitda=STREET_IS["ebitda"][q]) for q in ("3Q26", "4Q26")}
st_p["FY26"] = dict(rev=H1["rev"] + STREET_IS["rev"]["3Q26"] + STREET_IS["rev"]["4Q26"], ebitda=H1["ebitda"] + STREET_IS["ebitda"]["3Q26"] + STREET_IS["ebitda"]["4Q26"])
st_p["FY27"] = dict(rev=15819.3, ebitda=15819.3 * 0.3645)                   # LSEG FY27 revenue, 36.45% implied margin (DEC-0013)
street_adr = {"3Q26": 177.06, "4Q26": 171.33}
wm = []
for per in ("3Q26", "4Q26", "FY26", "FY27"):
    for src, d in (("this_line", pn[per]), ("main_v2", pm[per]), ("street", st_p[per])):
        wm.append(dict(period=per, source=src, revenue=d["rev"], ebitda=d["ebitda"], margin=d["ebitda"] / d["rev"] * 100,
                       adr=d.get("adr", street_adr.get(per, np.nan)) if src != "street" else street_adr.get(per, np.nan)))
save(pd.DataFrame(wm), "r03_what_moved.csv",
     f"{OFFICIAL} Income_Statement (nights, take rate, cash costs, D&A, add-backs); ADR {ADR_PATH} vs {ADR_MAIN}; Street LSEG rows 39/41, FY27 15,819.3 at 36.45% (DEC-0013); 1H26 reported")
qrows = []
for q in FQ:
    for src, d in (("this_line", inc_new[q]), ("main_v2", inc_main[q])):
        qrows.append(dict(quarter=q, source=src, revenue=d["rev"], street=STREET_IS["rev"][q], vs_street_pct=(d["rev"] / STREET_IS["rev"][q] - 1) * 100,
                          ebitda=d["ebitda"], street_ebitda=STREET_IS["ebitda"][q]))
save(pd.DataFrame(qrows), "r04_revenue_vs_street_quarterly.csv", f"as r03; Street LSEG quarterly means (13 Sep 2026 pull)")
save(pd.DataFrame([dict(adr_line=ADR_LINE, adr_label=ADR_LABEL, adr_path=ADR_PATH,
                        adr_3q26=adr.loc["3Q26", "adr_usd"], adr_4q26=adr.loc["4Q26", "adr_usd"],
                        adr_main_3q26=adr_main.loc["3Q26", "adr_usd"], adr_main_4q26=adr_main.loc["4Q26", "adr_usd"])]),
     "r00_meta.csv", "which ADR line the revenue and guide charts are drawn on")

# Margin bridge, Street to our model, 3Q26 / 4Q26 / FY27: a copy of margin_build/46_margin_bridge/run.py (krish/cost-leg
# 32ceee0e) with our revenue and EBITDA taken from this ADR line instead of the official workbook. Every other input is
# the same file on main. Checked below: on main's ADR line it reproduces 46_bridge.csv.
MB = ROOT / "data/processed/margin_build"
K_FLEX = 0.364
pan02 = pd.read_csv(MB / "02_financial_panel/02_panel_quarterly.csv").set_index("quarter")
lb40 = pd.read_csv(MB / "40_line_build/40_lines_quarterly.csv"); lb40 = lb40[lb40.scenario == "base"].set_index("quarter")
prm40 = pd.read_csv(MB / "40_line_build/40_params.csv").set_index("name")["base"]
cq06 = pd.read_csv(MB / "06_fy27_path_v2/06_consensus_quarterly_2027.csv").set_index("quarter")
V_OPS, G_FIX = float(prm40["ops_variable_share"]), float(prm40["ops_fixed_growth"]) / 100
NPB = {"3Q25": 3.7, "4Q25": 3.7, "1Q26": 3.65, "2Q26": 3.65}
PREVQ = {"3Q26": "3Q25", "4Q26": "4Q25", "1Q27": "1Q26", "2Q27": "2Q26", "3Q27": "3Q26", "4Q27": "4Q26"}
Q27 = ["1Q27", "2Q27", "3Q27", "4Q27"]
LINES = ["cor_cash", "ops_cash", "pd_cash", "sm_cash", "ga_cash"]
HOST_BASE = {"3Q25": 224.0 / 4, "4Q25": 224.0 / 4, "1H26": 112.0 + 15.0}
def _act(q):
    r = pan02.loc[q]
    return dict(cor_cash=float(r.cor_cash), ops_cash=float(r.ops_cash), pd_cash=float(r.pd_cash), sm_cash=float(r.sm_cash), ga_cash=float(r.ga_cash_ex_lodging))
def _lb(q): return {c: float(lb40.loc[q, c]) for c in LINES}
def _bk(q): return float(pan02.loc[q, "nights_m"]) / NPB[q] if q in NPB else float(lb40.loc[q, "bookings_m"])
def _opsp(q): return float(pan02.loc[q, "ops_cash"]) if q in NPB else float(lb40.loc[q, "ops_cash"])
def _ops_noai(q):
    p = PREVQ[q]
    return _opsp(p) * (V_OPS * float(lb40.loc[q, "bookings_m"]) / _bk(p) + (1 - V_OPS) * (1 + G_FIX))
BR_LABEL = {"Revenue below the Street, costs flexing at the historical rate": "Lower revenue (costs flex down)",
            "Payments & other cost of revenue": "Payments & other cost of revenue", "Hosting & AI compute": "Hosting & AI compute",
            "Ops & support: AI support automation": "AI support automation", "Ops & support: payroll, make-goods, insurance": "Ops & support: payroll, other",
            "Product development": "Product development", "Sales & marketing": "Sales & marketing", "General & administrative": "G&A"}
def margin_bridge(inc: dict) -> pd.DataFrame:
    out = []
    for period in ("3Q26", "4Q26", "FY27"):
        if period in ("3Q26", "4Q26"):
            base = _act(PREVQ[period]); ours = _lb(period); da = float(lb40.loc[period, "da"])
            host_b = HOST_BASE[PREVQ[period]]; host_o = float(lb40.loc[period, "cor_hosting"]); ops_noai = _ops_noai(period)
            st_rev, st_e = float(cq06.loc[period, "revenue_mean_musd"]), float(cq06.loc[period, "ebitda_mean_musd"])
            rev, e_off = inc[period]["rev"], inc[period]["ebitda"]
        else:
            base = {c: sum(_act(q)[c] for q in ("1Q26", "2Q26")) + sum(_lb(q)[c] for q in ("3Q26", "4Q26")) for c in LINES}
            ours = {c: sum(_lb(q)[c] for q in Q27) for c in LINES}; da = float(lb40.loc[Q27, "da"].sum())
            host_b = HOST_BASE["1H26"] + float(lb40.loc[["3Q26", "4Q26"], "cor_hosting"].sum()); host_o = float(lb40.loc[Q27, "cor_hosting"].sum())
            ops_noai = sum(_ops_noai(q) for q in Q27)
            st_rev, st_e = float(cq06.loc["FY27", "revenue_mean_musd"]), float(cq06.loc["FY27", "ebitda_mean_musd"])
            rev, e_off = sum(inc[q]["rev"] for q in Q27), sum(inc[q]["ebitda"] for q in Q27)
        m_st = st_e / st_rev * 100
        gap = rev / st_rev - 1
        st_costs_flex = (st_rev - st_e) * (1 + K_FLEX * gap)
        m_flex = (rev - st_costs_flex) / rev * 100
        f = (st_costs_flex + da) / sum(base.values())
        cf = {c: base[c] * f for c in LINES}
        pp = lambda usd: -usd / rev * 100
        steps = [("Street consensus", "total", m_st),
                 ("Revenue below the Street, costs flexing at the historical rate", "step", m_flex - m_st),
                 ("Payments & other cost of revenue", "step", pp((ours["cor_cash"] - host_o) - (cf["cor_cash"] - host_b * f))),
                 ("Hosting & AI compute", "step", pp(host_o - host_b * f)),
                 ("Ops & support: AI support automation", "step", pp(ours["ops_cash"] - ops_noai)),
                 ("Ops & support: payroll, make-goods, insurance", "step", pp(ops_noai - cf["ops_cash"])),
                 ("Product development", "step", pp(ours["pd_cash"] - cf["pd_cash"])),
                 ("Sales & marketing", "step", pp(ours["sm_cash"] - cf["sm_cash"])),
                 ("General & administrative", "step", pp(ours["ga_cash"] - cf["ga_cash"]))]
        run = None
        for name, kind, v in steps:
            if kind == "total":
                run = v; out.append(dict(period=period, item=name, label="Street consensus", kind=kind, value_pp=v, start=0.0, end=v))
            else:
                out.append(dict(period=period, item=name, label=BR_LABEL[name], kind=kind, value_pp=v, start=run, end=run + v)); run += v
        m_ours = e_off / rev * 100
        assert abs(run - m_ours) < 1e-6, (period, run, m_ours)
        out.append(dict(period=period, item="Our model (official income statement)", label="Our model", kind="total", value_pp=m_ours, start=0.0, end=m_ours))
    return pd.DataFrame(out)
_chk = margin_bridge(inc_main)
_ref = MB.parent / "margin_build" / "46_margin_bridge" / "46_bridge.csv"
_ref = ROOT.parent / "citadel-abnb-marginaudit/data/processed/margin_build/46_margin_bridge/46_bridge.csv"
if _ref.exists():
    _r = pd.read_csv(_ref)
    print("bridge on main's ADR line vs 46_bridge.csv, max |diff| pp:", float((_r.value_pp.values - _chk.value_pp.values).__abs__().max()))
save(margin_bridge(inc_new), "r05_margin_bridge.csv",
     f"copy of margin_build/46_margin_bridge (krish/cost-leg 32ceee0e) on main's 02 panel, 40 line build and 06 consensus; our revenue and EBITDA from {ADR_LABEL}")

# 5 Nov: our 4Q26 revenue-guide call. C01 (audited) was set on bridge-v3 GBV. Re-mark it for the ADR line with the team's
# C1 guide model (R4C): guide = exp(season_Q4) x (X/10,000)^beta, X = 0.4 GBV_4Q26 + 0.4 GBV_3Q26 + 0.2 GBV_2Q26 ($M).
# The whole C01 distribution is scaled by the model's guide ratio; P(below) is re-read on a normal fitted to C01's p5-p95.
from scipy.stats import norm
BETA, X_BRIDGE_V3, GBV_2Q26 = 1.0432632149063203, 25046.09, 27247.2
x_line = 0.4 * inc_new["4Q26"]["gbv"] + 0.4 * inc_new["3Q26"]["gbv"] + 0.2 * GBV_2Q26
ratio = (x_line / X_BRIDGE_V3) ** BETA
sd = (call["p95"] - call["p5"]) / (2 * 1.6449)
rem = {k: call[k] * ratio for k in ("p5", "p50", "p95")}
p_below_rem = float(norm.cdf((street_4q26 - rem["p50"]) / (sd * ratio)))
p_below_norm_c01 = float(norm.cdf((street_4q26 - call["p50"]) / sd))
save(pd.DataFrame([dict(quarter="4Q26E", street=street_4q26, **rem, p_below=p_below_rem, c01_p5=call["p5"], c01_p50=call["p50"], c01_p95=call["p95"],
                        c01_p_below=call["p_below"], c01_p_below_normal=p_below_norm_c01, c1_ratio=ratio, x_line=x_line,
                        p5_pct=(rem["p5"] / street_4q26 - 1) * 100, p50_pct=(rem["p50"] / street_4q26 - 1) * 100,
                        p95_pct=(rem["p95"] / street_4q26 - 1) * 100)]),
     "s05_guide_call.csv", C01 + f" row C01 ($2,945/3,100/3,265M, P 0.72, set on bridge-v3 GBV X=25,046.09) scaled by the C1 guide model ratio "
     f"(docs/pitch-model-v2/dossiers/R4C_r4c_c1_coefficients.md) at this ADR line's GBV ({ADR_LABEL})")

# ======================================================================================================================
# 3. Nights: the product bundle, the World Cup, RNPL cancellations
# ======================================================================================================================
DESIGN = "docs/pitch-model-v2/lines/nights_v2_design.md §2.1"
FINAL_N = "docs/pitch-model-v2/lines/final_nights.md §1, §6"
COHORT = "data/processed/rnpl_short_audit/rnpl_nights_module_cohort_matrix.csv"
MODULE = "data/processed/rnpl_short_audit/rnpl_nights_module.csv"
STATE = "data/processed/rnpl_short_audit/rnpl_nights_module_state.csv"
UFGAP = "data/processed/rnpl_short_audit/verify_bs_yoy_gap_table.csv"

NQ = ["1Q24", "2Q24", "3Q24", "4Q24", "1Q25", "2Q25", "3Q25", "4Q25", "1Q26", "2Q26"] + FQ
base_path = {"3Q26": 9.89, "4Q26": 8.12, "1Q27": 8.206, "2Q27": 5.934, "3Q27": 6.229, "4Q27": 6.045}   # DEC-0029/0019/0025
base_m = {"3Q26": 146.813, "4Q26": 131.798, "1Q27": 169.018, "2Q27": 157.100, "3Q27": 155.958, "4Q27": 139.766}
envelope = {"3Q26": (146.04, 148.23), "4Q26": (131.57, 132.94), "1Q27": (166.9, 170.9), "2Q27": (156.3, 160.2),
            "3Q27": (154.7, 159.4), "4Q27": (139.1, 142.7)}                                                     # final_nights §1
street_n = {"3Q26": (149.0, 11.53), "4Q26": (134.0, 9.93)}                                                      # Bloomberg MODL 12 Sep
# short case: judgement path, krish/cost-leg 3065e2f2, analysis/src/margin_build/44_short_case_v2/run.py (SHORT dict)
short_case = {"3Q26": 8.5, "4Q26": 5.0, "1Q27": 4.0, "2Q27": 2.0, "3Q27": 3.0, "4Q27": 4.0}
# prior-year NA share of nights (WS10 estimate; design §2.1)
s_na = {"3Q25": 0.307, "4Q25": 0.300, "1Q26": 0.293, "2Q26": 0.293, "3Q26": 0.288, "4Q26": 0.282}
EXNA = 1.649  # ex-NA bundle, points of total nights: 3.0 (management, 1Q26 call) - 0.288 x 4.69 (design §2.1)

def legs(q: str) -> dict:
    """Bundle contribution to y/y nights growth, points of total nights, by leg (design §2.1 and the lap schedule)."""
    s = s_na.get(q, 0.0)
    na_rnpl = s * 2.40 if q in ("3Q25", "4Q25", "1Q26", "2Q26") else 0.0         # US launch mid-Aug 2025; lapped 3Q26
    na_fee = s * 2.29 if q in ("4Q25", "1Q26", "2Q26", "3Q26") else 0.0          # Oct 2025 legs; lapped 4Q26
    exna_fee = {"4Q25": 0.45 * 1.752}.get(q, 0.45 * EXNA if q in ("1Q26", "2Q26", "3Q26") else 0.0)
    exna_rnpl = {"1Q26": 1, "2Q26": 1, "3Q26": 1, "4Q26": 1, "1Q27": 0.6}.get(q, 0.0) * 0.55 * EXNA  # Feb 2026; 40% lapped 1Q27
    return dict(na_rnpl=na_rnpl, na_fee=na_fee, exna_fee=exna_fee, exna_rnpl=exna_rnpl)

me = {"1Q26": -1.0, "1Q27": 1.0}        # Middle East: ~100bp headwind (1Q26 letter), lapped 1Q27
wc = {"2Q26": 0.5, "2Q27": -0.5}        # World Cup: 06 build's assumed 2Q27 lap (judgement); 2Q26 = the same size, unsized by management
rows = []
for q in NQ:
    tot = base_path[q] if q in FQ else float(kpi.loc[q, "nights_yoy_pct"])
    L = legs(q)
    b = sum(L.values())
    rows.append(dict(quarter=q, kind="forecast" if q in FQ else "reported", total=tot, bundle=b, **L,
                     me=me.get(q, 0.0), wc=wc.get(q, 0.0), underlying=tot - b - me.get(q, 0.0) - wc.get(q, 0.0),
                     nights_m=base_m.get(q, float(kpi.loc[q, "nights_m"]) if q in kpi.index else np.nan),
                     env_lo_pct=(envelope[q][0] / lev[prev(q)]["nights"] - 1) * 100 if q in envelope else np.nan,
                     env_hi_pct=(envelope[q][1] / lev[prev(q)]["nights"] - 1) * 100 if q in envelope else np.nan,
                     street=street_n.get(q, (np.nan, np.nan))[1], short_case=short_case.get(q, np.nan)))
nd = pd.DataFrame(rows)

# cancellation tail: excess RNPL cancellations recognised in the quarter (cohort matrix), net of rebooking, as a
# y/y drag on nights growth = (X_q - X_q-4) x (1 - rebook) / nights_q-4. Reproduces the module's M3+M4 within ~0.05pp.
cm = pd.read_csv(ROOT / COHORT)
st = pd.read_csv(ROOT / STATE)
rebook = st.groupby("scenario").rebook_offset.first().to_dict()
CQ = ["3Q25", "4Q25", "1Q26", "2Q26"] + FQ
xrec, xsame = {}, {}
for sc in ("base", "bear", "bull"):
    c = cm[cm.scenario == sc]
    tot_row = c[c.booking_quarter == "RECOGNISED IN QUARTER"].iloc[0]
    xrec[sc] = {q: float(tot_row[q]) for q in CQ}
    xsame[sc] = {q: float(c[c.booking_quarter == q][q].iloc[0]) for q in CQ}
nights_level = {q: lev[q]["nights"] for q in lev}
nights_level.update(base_m)
crow = []
for sc in ("base", "bear", "bull"):
    for q in CQ:
        p = prev(q)
        drag = (xrec[sc][q] - xrec[sc].get(p, 0.0)) * (1 - rebook[sc]) / nights_level[p] * 100
        crow.append(dict(scenario=sc, quarter=q, excess_cancels_m=xrec[sc][q], same_quarter_m=xsame[sc][q],
                         earlier_cohorts_m=xrec[sc][q] - xsame[sc][q], rebook=rebook[sc], drag_pp=-drag))
cd = pd.DataFrame(crow)
mod = pd.read_csv(ROOT / MODULE)
mod = mod[mod.quarter.isin(FQ)][["scenario", "quarter", "m3_plus_m4_tail_pts"]]
cd = cd.merge(mod, on=["scenario", "quarter"], how="left")
chk = cd[cd.quarter.isin(["3Q26", "4Q26"])]
print("rule vs module M3+M4, 3Q26-4Q26, max abs diff:", round(float((chk.drag_pp - chk.m3_plus_m4_tail_pts).abs().max()), 3))
cd["drag_rule_pp"] = cd.drag_pp
cd["drag_pp"] = cd.m3_plus_m4_tail_pts.fillna(cd.drag_rule_pp)   # module where it exists (3Q26+), the rule for 3Q25-2Q26
save(cd, "n02_cancellation_tail.csv", f"{COHORT} (RECOGNISED IN QUARTER, diagonal = same-quarter cohort); {STATE} rebook_offset; {MODULE} M3+M4 for comparison")

tail = cd[cd.scenario == "base"].set_index("quarter").drag_pp
tail_bear = cd[cd.scenario == "bear"].set_index("quarter").drag_pp
nd["with_tail"] = nd.apply(lambda r: r.total + tail[r.quarter] if r.kind == "forecast" else np.nan, axis=1)
nd["with_tail_bear"] = nd.apply(lambda r: r.total + tail_bear[r.quarter] if r.kind == "forecast" else np.nan, axis=1)
save(nd, "n01_nights_decomposition.csv",
     f"{DESIGN} (NA share, legs, laps, events); {FINAL_N} (base path, envelopes, Street 149.0/134.0 Bloomberg MODL 12 Sep); printed nights {KPI}; "
     "short case = judgement path, krish/cost-leg 3065e2f2 44_short_case_v2/run.py; 4Q25 carries the NA fee+cancellation legs (launched Oct 2025) as in "
     "the D1 cross-check, giving 2.2pts against management's 'over 200 basis points' (the design table carries 1.51)")

# implied platform cancellation rate: 16% historical (management, 4Q25 call, D018) + RNPL share of nights x excess propensity
share_hist = {"3Q25": 4.0, "4Q25": 9.0, "1Q26": 20.0}     # RNPL share of GBV: assumed, assumed, letter ("roughly 20%")
ratio = 21.0 / 16.66                                       # module: GBV share / nights share at 2Q26
prow = []
for sc, dpp in (("bull", 2.0), ("base", 4.0), ("bear", 6.0)):
    s2 = st[st.scenario == sc].assign(q=lambda d: d.quarter.str.slice(0, 4)).set_index("q").rnpl_nights_share_pct.to_dict()
    for q in CQ:
        sh = s2.get(q, share_hist.get(q, np.nan) / ratio)
        prow.append(dict(scenario=sc, propensity_pp=dpp, quarter=q, rnpl_nights_share_pct=sh, platform_cancel_rate_pct=16.0 + sh * dpp / 100))
save(pd.DataFrame(prow), "n03_cancel_rate.csv",
     f"{STATE} (RNPL nights share, propensity); 16% historical and '17%' from management (4Q25 call, ledger D018, transcript mirror); 3Q25/4Q25 shares assumed, 1Q26 letter")

uf = pd.read_csv(ROOT / UFGAP)
save(uf, "n04_unearned_fees_vs_gbv.csv", f"{UFGAP} (10-Q/10-K balance sheets; GBV from letters)")

# World Cup: host vs control markets, Inside Airbnb review counts y/y (uncommitted branch krish/worldcup-premium,
# data/processed/worldcup_premium/40_v4_reviews.csv, 22 Sep 2026; 19 host and 19 control markets)
wcr = pd.DataFrame(dict(month=["2026-03", "2026-04", "2026-05", "2026-06", "2026-07"] * 2,
                        cls=["host"] * 5 + ["control"] * 5,
                        yoy_pct=[6.786, 8.040, 17.307, 15.677, 14.263, 2.610, 3.355, 8.244, -2.053, 3.973]))
save(wcr, "n05_worldcup_reviews.csv", "krish/worldcup-premium (uncommitted) data/processed/worldcup_premium/40_v4_reviews.csv; RESULTS.md §3c: ~0.1pt of global 2Q26 nights")


if __name__ == "__main__":
    (OUT / "SOURCES.json").write_text(json.dumps(SOURCES, indent=1))
    print("done:", OUT)
