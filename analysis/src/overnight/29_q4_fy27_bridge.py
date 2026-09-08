"""
29. The Q4 2026 and FY27 revenue-growth bridge.

Walks reported revenue growth from the 3Q26 guide to a 4Q26 base, and from FY26 to FY27, one named
term at a time, so every point of the step-down has a cause and a date. Terms:

    reported revenue growth = nights growth + ADR ex-FX growth + take-rate/timing residual + FX (after hedging)

Where the numbers come from (nothing here is newly sourced; the assumptions table in the output carries a source per row):
  * actuals                 data/processed/overnight/02_kpi_panel_quarterly.csv (letters, XBRL)
  * FX                      fresh FRED DEXUSEU / DTWEXBGS pull, applied through the workstream-05 revenue-FX fit
                            (EUR/USD y/y averaged over the two prior quarters, ex-2021 window; 05_fx_fits.csv) and
                            the three workstream-05 EUR/USD paths; hedge memo from 28_fx_hedge_forward.csv
  * nights, ADR ex-FX       workstream-10 regional bottom-up (10_regional_forecast.csv), bear / base / bull
  * product laps            management's own attribution (1Q26 call: "these three features delivered approximately
                            3 points of nights booked growth and approximately 4 points of GBV growth in Q1";
                            4Q25 call ~2 / ~3 points), used to *label* the nights step-down, not to subtract it twice
  * Street                  04_current_consensus.csv (Zacks 4 Sep 2026, S&P Global 3 Sep 2026) - a comparison column,
                            never an input

Run:  py -3.13 analysis/src/overnight/29_q4_fy27_bridge.py
Writes: data/processed/overnight/29_*.csv, analysis/figures/overnight/29_q4_fy27_bridge.png
"""
from __future__ import annotations

import datetime as dt
import io
import sys
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import requests

ROOT = Path(__file__).resolve().parents[3]
OUT = ROOT / "data" / "processed" / "overnight"
FIG = ROOT / "analysis" / "figures" / "overnight"
CACHE = OUT / "29_fred_cache"
CACHE.mkdir(exist_ok=True, parents=True)
TODAY = dt.date.today()

# ----------------------------------------------------------------------------------------------------------
# 1. Inputs already in the repo
# ----------------------------------------------------------------------------------------------------------
kpi = pd.read_csv(OUT / "02_kpi_panel_quarterly.csv").set_index("quarter")
fits = pd.read_csv(OUT / "05_fx_fits.csv")
sched05 = pd.read_csv(OUT / "05_fx_schedule.csv")
hedge = pd.read_csv(OUT / "28_fx_hedge_forward.csv").set_index("quarter")
reg = pd.read_csv(OUT / "10_regional_forecast.csv")
cons = pd.read_csv(OUT / "04_current_consensus.csv")

# the revenue-FX forecasting spec workstream 05 selected: EUR/USD y/y averaged over the two prior quarters,
# ex-2021 window (n 17, r 0.80). Recovered from 05_fx_fits.csv rather than hard-coded.
spec = fits[(fits.target == "rev_fx") & (fits.driver == "eurusd_avg12") & (fits.window == "ex21")].iloc[0]
SLOPE, INTERCEPT, LOO = float(spec.slope), float(spec.intercept), float(spec.loo_rmse)
# sanity: the schedule's 3Q26 value must reproduce from the same spec
_s05 = sched05[sched05.path == "consensus"].set_index("quarter")
_chk_drv = np.mean([_s05.loc["2026Q2", "eurusd_yoy_pct"], _s05.loc["2026Q1", "eurusd_yoy_pct"]])   # two prior quarters
assert abs((INTERCEPT + SLOPE * _chk_drv) - _s05.loc["2026Q3", "revenue_fx_fit_pp"]) < 0.05, "05 spec mismatch"

# ----------------------------------------------------------------------------------------------------------
# 2. Fresh FX pull (keyless FRED CSV), quarterly means, y/y, and the three EUR/USD paths from workstream 05
# ----------------------------------------------------------------------------------------------------------
def fred(sid: str) -> pd.Series:
    p = CACHE / f"{sid}_{TODAY.isoformat()}.csv"
    if not p.exists():
        r = requests.get(f"https://fred.stlouisfed.org/graph/fredgraph.csv?id={sid}", timeout=60)
        r.raise_for_status()
        p.write_text(r.text)
    df = pd.read_csv(io.StringIO(p.read_text()))
    df.columns = ["date", "value"]
    df["date"] = pd.to_datetime(df["date"])
    df["value"] = pd.to_numeric(df["value"], errors="coerce")
    return df.set_index("date")["value"].dropna()

eur_d = fred("DEXUSEU")
usd_d = fred("DTWEXBGS")
fx_asof = eur_d.index.max().date()

def quarterly(s: pd.Series) -> pd.Series:
    q = s.resample("QE").mean()
    q.index = q.index.to_period("Q")
    return q

eur_q = quarterly(eur_d)
usd_q = quarterly(usd_d)
CUR = pd.Period(fx_asof, "Q")               # the quarter that is currently partial
FUTURE = [pd.Period(p, "Q") for p in ("2026Q4", "2027Q1", "2027Q2", "2027Q3", "2027Q4")]
# EUR/USD level paths, identical to 05_macro_transmission.py (Reuters poll 2 Sep 2026; bank-survey bull and bear camps)
PATHS = {
    "consensus":  [1.160, 1.165, 1.170, 1.175, 1.180],
    "strong_usd": [1.130, 1.100, 1.090, 1.090, 1.100],
    "weak_usd":   [1.190, 1.210, 1.230, 1.240, 1.250],
}
# share of each quarter's driver (mean of the two prior quarters' EUR y/y) that is already observed today
def realised(q: pd.Period) -> float:
    if q < CUR:
        return 1.0
    if q == CUR:
        days_in = (fx_asof - CUR.start_time.date()).days + 1
        return round(min(1.0, days_in / ((CUR.end_time.date() - CUR.start_time.date()).days + 1)), 2)
    return 0.0

fx_rows = []
for pname, levels in PATHS.items():
    e = eur_q.copy()
    for q, v in zip(FUTURE, levels):
        if q > CUR:
            e.loc[q] = v
    e = e.sort_index()
    yoy = e.pct_change(4) * 100
    drv = (yoy.shift(1) + yoy.shift(2)) / 2
    for q in [pd.Period(p, "Q") for p in ("2025Q3", "2025Q4", "2026Q1", "2026Q2", "2026Q3")] + FUTURE:
        stated = kpi["fx_pts_revenue"].get(f"{q.quarter}Q{str(q.year)[2:]}", np.nan)
        fx_rows.append(dict(
            path=pname, quarter=str(q), eurusd_level=round(float(e.loc[q]), 4), eurusd_yoy_pct=round(float(yoy.loc[q]), 2),
            driver_two_prior_q_avg=round(float(drv.loc[q]), 2),
            revenue_fx_fit_pp=round(INTERCEPT + SLOPE * float(drv.loc[q]), 2),
            revenue_fx_stated_pp=stated,
            hedge_reclass_pp=hedge["hedge_effect_on_revenue_growth_pp"].get(f"{q.quarter}Q{str(q.year)[2:]}", np.nan),
            driver_realised_share=round(float(np.mean([realised(q - 1), realised(q - 2)])), 2),
            status="actual" if q < CUR else (f"quarter-to-date to {fx_asof}" if q == CUR else "path"),
        ))
fx = pd.DataFrame(fx_rows)
fx.to_csv(OUT / "29_fx_refresh.csv", index=False)

def fxfit(path: str, q: str) -> float:
    return float(fx[(fx.path == path) & (fx.quarter == q)].revenue_fx_fit_pp.iloc[0])

# ----------------------------------------------------------------------------------------------------------
# 3. Assumptions, each with a source. Nights and ADR ex-FX are workstream 10's bear/base/bull.
# ----------------------------------------------------------------------------------------------------------
def reg_total(period: str, scen: str, col: str) -> float:
    r = reg[(reg.period == period) & (reg.region == "TOTAL") & (reg.scenario == scen)]
    return float(r[col].iloc[0])

Q3_GUIDE = dict(low=4690.0, high=4770.0, mid=4730.0, growth_low=15.0, growth_high=17.0, fx_pp=3.0,
                nights_bucket="low double-digit (10-12)", nights_mid=11.0, base_3q25=4095.0)
Q3_GUIDE["growth_mid"] = round(Q3_GUIDE["mid"] / Q3_GUIDE["base_3q25"] * 100 - 100, 2)      # 15.5
# the guide's implied ex-FX growth and residual (nights 11 + ADR ex-FX ~3 + residual = ex-FX growth)
Q3_EXFX = Q3_GUIDE["growth_mid"] - Q3_GUIDE["fx_pp"]                                          # 12.5
Q3_ADR_EXFX = 3.0                                                                              # "moderate increase in ADR"; letters 3-4% ex-FX
Q3_RESID = round(Q3_EXFX - Q3_GUIDE["nights_mid"] - Q3_ADR_EXFX, 2)                          # -1.5

# realised take-rate / timing residual = ex-FX revenue growth - nights - ADR ex-FX, last eight quarters
hist = []
for q in ["3Q24", "4Q24", "1Q25", "2Q25", "3Q25", "4Q25", "1Q26", "2Q26"]:
    r = kpi.loc[q]
    hist.append(dict(quarter=q, revenue_yoy_pct=r.revenue_yoy_pct, revenue_yoy_exfx_pct=r.revenue_yoy_exfx_pct,
                     fx_pts_revenue=r.fx_pts_revenue, nights_yoy_pct=r.nights_yoy_pct, adr_yoy_exfx_pct=r.adr_yoy_exfx_pct,
                     residual_pp=round(r.revenue_yoy_exfx_pct - r.nights_yoy_pct - r.adr_yoy_exfx_pct, 2),
                     rev_minus_gbv_gap_pp=round(r.revenue_yoy_pct - r.gbv_yoy_pct, 2)))
hist = pd.DataFrame(hist)
hist.to_csv(OUT / "29_residual_history.csv", index=False)
RESID_TTM = round(float(hist.tail(4).residual_pp.mean()), 2)

PY = dict(q4=2778.0, q1=2678.0, q2=3608.0, fy25=12241.0, h1_26=6286.0)     # prior-year revenue bases, $m (letters)
SCEN = ["bear", "base", "bull"]
A = {}   # assumptions by scenario
for s in SCEN:
    A[s] = dict(
        q3_nights=reg_total("3Q26", s, "nights_yoy_pct"), q3_adr=reg_total("3Q26", s, "adr_exfx_yoy_pct"),
        q4_nights=reg_total("4Q26", s, "nights_yoy_pct"), q4_adr=reg_total("4Q26", s, "adr_exfx_yoy_pct"),
        fy27_nights=reg_total("FY27", s, "nights_yoy_pct"), fy27_adr=reg_total("FY27", s, "adr_exfx_yoy_pct"),
        # residual: base carries the trailing-four mean; bear the RNPL-era low; bull the 2Q26 high
        q4_resid={"bear": -2.0, "base": RESID_TTM, "bull": 1.0}[s],
        fy27_resid={"bear": -1.0, "base": 0.0, "bull": 0.5}[s],
        fx_path={"bear": "strong_usd", "base": "consensus", "bull": "weak_usd"}[s],
    )

assumptions = [
    ("3Q26 guide", "revenue $4,690-4,770m, +15-17%, ~3pp FX after hedging, nights low double-digit, GBV mid-teens", "2Q26 letter and call, 6 Aug 2026 (transcript line 275)"),
    ("3Q26 implied ex-FX growth", f"{Q3_EXFX:+.1f}pp = midpoint growth {Q3_GUIDE['growth_mid']:+.1f} less FX {Q3_GUIDE['fx_pp']:+.1f}", "arithmetic on the guide"),
    ("3Q26 implied residual", f"{Q3_RESID:+.1f}pp = ex-FX growth less nights 11.0 less ADR ex-FX 3.0", "arithmetic; the guide assumes the timing gap stays close to 2Q26's"),
    ("Revenue-FX spec", f"FX pp = {INTERCEPT:.3f} + {SLOPE:.3f} x mean(EUR/USD y/y, two prior quarters); LOO RMSE {LOO:.1f}pp", "05_fx_fits.csv, eurusd_avg12, ex-2021 window, n 17; mechanism in 28_fx-hedge-disclosures.md"),
    ("FX data", f"FRED DEXUSEU and DTWEXBGS through {fx_asof}; {CUR} is {realised(CUR):.0%} observed", "fresh pull, cached in 29_fred_cache/"),
    ("EUR/USD paths", "consensus 1.16-1.18 (Reuters poll 2 Sep 2026); strong USD 1.13-1.09; weak USD 1.19-1.25", "05_macro_transmission.py PATHS, unchanged"),
    ("Hedge memo", "-0.21 / -0.21 / -0.18 / -0.18pp for 3Q26-2Q27, already inside the after-hedge FX number", "2Q26 10-Q derivatives note via 28_fx_hedge_forward.csv"),
    ("Nights, ADR ex-FX", "workstream 10 regional bottom-up bear/base/bull for 3Q26, 4Q26, FY27", "10_regional_forecast.csv TOTAL rows"),
    ("Take-rate / timing residual", f"base = trailing-four mean {RESID_TTM:+.2f}pp; bear -2.0 (RNPL-era low); bull +1.0; FY27 base 0", "29_residual_history.csv; take rate guided flat for 2026"),
    ("Product laps (label only)", "three features ~2pt nights 4Q25, ~3pt 1Q26 (RNPL US 3Q25, merchandising 4Q25, global + cancellation + fee 1Q26)", "4Q25 and 1Q26 calls; CONF-12: not RNPL alone"),
    ("World Cup", "booked 2Q26, stayed 2Q/3Q26, never sized by Airbnb; a 2Q27 comparison", "1Q26 call; 05 §4.6; STR June 2027 RevPAR -0.8%"),
    ("Prior-year bases", "4Q25 $2,778m; 1Q26 $2,678m; 2Q26 $3,608m; 1H26 $6,286m; FY25 $12,241m", "letters via 02_kpi_panel_quarterly.csv"),
    ("Street", "Q3 $4,740m; Q4 $3,200m (range 3,050-3,700); FY26 $14,100-14,160m; FY27 $15,730-15,760m", "04_current_consensus.csv, Zacks 4 Sep / S&P Global 3 Sep 2026; comparison only"),
]
pd.DataFrame(assumptions, columns=["item", "value", "source"]).to_csv(OUT / "29_bridge_assumptions.csv", index=False)

# ----------------------------------------------------------------------------------------------------------
# 4. The Q4 2026 bridge: from the 3Q26 guide midpoint to a 4Q26 growth rate, per scenario
# ----------------------------------------------------------------------------------------------------------
def q4_bridge(s: str) -> list[dict]:
    a = A[s]
    fx_q4 = fxfit(a["fx_path"], "2026Q4")
    steps = [
        ("3Q26 guide midpoint, reported growth", Q3_GUIDE["growth_mid"], "start", "2Q26 letter: $4,730m on $4,095m"),
        ("FX after hedging: +3.0 guided in Q3 to fitted Q4", round(fx_q4 - Q3_GUIDE["fx_pp"], 2), "step",
         f"Q4 fit {fx_q4:+.2f}pp on EUR y/y of {fx.loc[(fx.path==a['fx_path'])&(fx.quarter=='2026Q4'),'driver_two_prior_q_avg'].iloc[0]:+.2f}% averaged over 2Q26-3Q26; "
         f"{fx.loc[(fx.path==a['fx_path'])&(fx.quarter=='2026Q4'),'driver_realised_share'].iloc[0]:.0%} of that driver is already observed; identical across FX paths"),
        ("Nights: guide 'low double-digit' (11) to Q4 regional build", round(a["q4_nights"] - Q3_GUIDE["nights_mid"], 2), "step",
         f"4Q26 {s} {a['q4_nights']:.1f}% (10_regional_forecast); the step is the RNPL US lap (3Q25 launch, 4Q25 merchandising) plus a 4Q25 comp of +9.8%"),
        ("ADR ex-FX: 3.0 to Q4 regional build", round(a["q4_adr"] - Q3_ADR_EXFX, 2), "step", f"4Q26 {s} ADR ex-FX {a['q4_adr']:.1f}%; letters ran +3 / +4 / +4% in 4Q25-2Q26"),
        ("Take-rate / timing residual: guide-implied to Q4 assumption", round(a["q4_resid"] - Q3_RESID, 2), "step",
         f"Q3 guide implies {Q3_RESID:+.1f}pp; Q4 {s} {a['q4_resid']:+.1f}pp (trailing-four mean {RESID_TTM:+.2f}); the least certain term - RNPL book-vs-stay timing and flat take rate"),
    ]
    total = round(sum(v for _, v, k, _ in steps), 2)
    rev = round(PY["q4"] * (1 + total / 100), 0)
    street = 3200.0
    steps.append(("4Q26 reported growth, this scenario", total, "end", f"${rev:,.0f}m on 4Q25 $2,778m; Street $3,200m = +15.2%; gap to Street {rev/street*100-100:+.1f}%"))
    return [dict(scenario=s, order=i, term=t, value_pp=v, kind=k, note=n) for i, (t, v, k, n) in enumerate(steps)]

q4 = pd.DataFrame(sum((q4_bridge(s) for s in SCEN), []))
q4.to_csv(OUT / "29_q4_2026_bridge.csv", index=False)

# also: the FX step-down stated two ways (guide-anchored and fit-to-fit), so the "roughly three points" has a range
fx_q3_fit = fxfit("consensus", "2026Q3")
fx_q4_fit = fxfit("consensus", "2026Q4")
fx_step = dict(guide_anchored_pp=round(fx_q4_fit - Q3_GUIDE["fx_pp"], 2), fit_to_fit_pp=round(fx_q4_fit - fx_q3_fit, 2),
               q3_fit_pp=round(fx_q3_fit, 2), q3_guided_pp=Q3_GUIDE["fx_pp"], q4_fit_pp=round(fx_q4_fit, 2),
               q4_fit_minus_loo_pp=round(fx_q4_fit - LOO, 2), q4_fit_plus_loo_pp=round(fx_q4_fit + LOO, 2),
               q4_driver_realised_share=float(fx.loc[(fx.path == "consensus") & (fx.quarter == "2026Q4"), "driver_realised_share"].iloc[0]))
pd.DataFrame([fx_step]).to_csv(OUT / "29_fx_step_down.csv", index=False)

# ----------------------------------------------------------------------------------------------------------
# 5. FY26 assembly and the FY27 bridge (annual), plus a quarterly FY27 phasing per scenario
# ----------------------------------------------------------------------------------------------------------
rows_fy = []
phase = []
for s in SCEN:
    a = A[s]
    q3_g = Q3_GUIDE["growth_mid"] + {"bear": -2.4, "base": 1.0, "bull": 4.9}[s]   # 10 note: bear $4,633m, base $4,775m, bull $4,932m
    q3_rev = round(Q3_GUIDE["base_3q25"] * (1 + q3_g / 100), 0)
    q4_g = float(q4[(q4.scenario == s) & (q4.kind == "end")].value_pp.iloc[0])
    q4_rev = round(PY["q4"] * (1 + q4_g / 100), 0)
    fy26_rev = PY["h1_26"] + q3_rev + q4_rev
    fy26_g = round(fy26_rev / PY["fy25"] * 100 - 100, 2)
    # FY26 decomposition (weighted, approximate): nights and ADR ex-FX from 07's FY26 levers, FX from the stated quarterly points
    fy26_fx = round((0.0 * 0 + 3.0 * PY["q1"] + 4.0 * PY["q2"] + Q3_GUIDE["fx_pp"] * Q3_GUIDE["base_3q25"] + fxfit(a["fx_path"], "2026Q4") * PY["q4"]) / PY["fy25"], 2)
    fy26_nights = {"bear": 9.5, "base": 10.0, "bull": 10.3}[s]      # 07 levers; 1H26 actual +9.7%
    fy26_adr = {"bear": 3.0, "base": 3.5, "bull": 4.0}[s]
    fy26_resid = round(fy26_g - fy26_fx - fy26_nights - fy26_adr, 2)
    # FY27 quarterly phasing: nights phased around the FY27 regional total (heavier lap in 1H27), FX from the path, residual per scenario
    n27 = a["fy27_nights"]
    nights_q = {"2027Q1": n27 - 1.2, "2027Q2": n27 - 0.7, "2027Q3": n27 + 0.4, "2027Q4": n27 + 1.3}
    lap_note = {"2027Q1": "global three-feature lap (1Q26 +3pt nights, mgmt) and Middle East base", "2027Q2": "World Cup booking lap (2Q26), RNPL eligibility expansion lap (Jul 2026)",
                "2027Q3": "clean comp; hotels and AI pricing are the swing", "2027Q4": "clean comp"}
    base_rev = {"2027Q1": PY["q1"], "2027Q2": PY["q2"], "2027Q3": q3_rev, "2027Q4": q4_rev}   # 1Q26 and 2Q26 actuals, 3Q26 and 4Q26 this scenario
    fy27_rev = 0.0
    for q in ["2027Q1", "2027Q2", "2027Q3", "2027Q4"]:
        g = nights_q[q] + a["fy27_adr"] + a["fy27_resid"] + fxfit(a["fx_path"], q)
        rev = base_rev[q] * (1 + g / 100)
        fy27_rev += rev
        phase.append(dict(scenario=s, quarter=q, nights_yoy_pct=round(nights_q[q], 2), adr_exfx_pct=a["fy27_adr"], residual_pp=a["fy27_resid"],
                          fx_pp=fxfit(a["fx_path"], q), hedge_memo_pp=hedge["hedge_effect_on_revenue_growth_pp"].get(f"{q[-1]}Q27", np.nan),
                          reported_growth_pct=round(g, 2), prior_year_revenue_musd=round(base_rev[q], 0), revenue_musd=round(rev, 0),
                          fx_path=a["fx_path"], lap=lap_note[q]))
    fy27_g = round(fy27_rev / fy26_rev * 100 - 100, 2)
    fy27_fx = round(sum(fxfit(a["fx_path"], q) * base_rev[q] for q in base_rev) / sum(base_rev.values()), 2)
    fy27_nights_w = round(sum(nights_q[q] * base_rev[q] for q in base_rev) / sum(base_rev.values()), 2)
    steps = [
        ("FY26 reported growth, this scenario", fy26_g, "start", f"1H26 actual $6,286m + 3Q26 {s} ${q3_rev:,.0f}m + 4Q26 {s} ${q4_rev:,.0f}m = ${fy26_rev:,.0f}m on FY25 $12,241m; Street $14,100-14,160m"),
        ("FX after hedging: FY26 stated points to FY27 path", round(fy27_fx - fy26_fx, 2), "step", f"FY26 {fy26_fx:+.1f}pp (0 / +3 / +4 / +3 stated, Q4 fitted) to FY27 {fy27_fx:+.1f}pp on the {a['fx_path']} path; hedge memo about -0.2pp a quarter inside it"),
        ("Nights: FY26 to FY27 regional build", round(fy27_nights_w - fy26_nights, 2), "step", f"FY26 {fy26_nights:.1f}% to FY27 {s} {n27:.1f}% (10_regional_forecast), phased heavier in 1H27 for the global three-feature and World Cup laps"),
        ("ADR ex-FX", round(a["fy27_adr"] - fy26_adr, 2), "step", f"FY26 {fy26_adr:.1f}% to FY27 {a['fy27_adr']:.1f}%; hotel CPI re-accelerated in 2Q26 and the 2025-26 Airbnb-specific ADR premium is closing"),
        ("Take-rate / timing residual", round(a["fy27_resid"] - fy26_resid, 2), "step", f"FY26 implied {fy26_resid:+.1f}pp (RNPL timing plus FY26 revenue beats) to FY27 {a['fy27_resid']:+.1f}pp; take rate modelled flat"),
    ]
    steps.append(("FY27 reported growth, this scenario", round(sum(v for _, v, _, _ in steps), 2), "end",
                  f"${fy27_rev:,.0f}m; Street $15,730-15,760m (+11.3-11.5% on its own FY26); regional note FY27 {s} " + {"bear": "+4.9%", "base": "+12.4%", "bull": "+16.9%"}[s] + " with FX at " + {"bear": "-2", "base": "0", "bull": "+1"}[s] + "pp"))
    assert abs(steps[-1][1] - fy27_g) < 0.05, (s, steps[-1][1], fy27_g)
    rows_fy += [dict(scenario=s, order=i, term=t, value_pp=v, kind=k, note=n) for i, (t, v, k, n) in enumerate(steps)]

fy = pd.DataFrame(rows_fy)
fy.to_csv(OUT / "29_fy27_bridge.csv", index=False)
ph = pd.DataFrame(phase)
ph.to_csv(OUT / "29_fy27_quarterly_path.csv", index=False)

# ----------------------------------------------------------------------------------------------------------
# 6. Figure: two waterfalls, base case. Palette: dataviz reference instance (diverging blue/red, neutral totals).
# ----------------------------------------------------------------------------------------------------------
INK, INK2, MUTED, GRID, SURF = "#0b0b0b", "#52514e", "#898781", "#e1e0d9", "#fcfcfb"
POS, NEG, TOT = "#2a78d6", "#e34948", "#898781"

def waterfall(ax, df: pd.DataFrame, title: str, labels: list[str]):
    vals = df.value_pp.tolist(); kinds = df.kind.tolist()
    run = 0.0
    for i, (v, k) in enumerate(zip(vals, kinds)):
        if k in ("start", "end"):
            bottom, height, color = 0.0, v, TOT
            run = v
        else:
            bottom, height = (run, v) if v >= 0 else (run + v, -v)
            color = POS if v >= 0 else NEG
            run += v
        ax.bar(i, height, bottom=bottom, width=0.62, color=color, edgecolor=SURF, linewidth=1.5, zorder=3)
        y = bottom + height + 0.25
        txt = f"{v:+.1f}" if k == "step" else f"{v:.1f}%"
        ax.text(i, y, txt, ha="center", va="bottom", fontsize=9.5, color=INK, zorder=4)
        if i < len(vals) - 1 and k != "end":
            ax.plot([i + 0.31, i + 1 - 0.31], [run, run], color=MUTED, linewidth=0.8, linestyle=(0, (2, 2)), zorder=2)
    ax.set_xticks(range(len(vals)))
    ax.set_xticklabels(labels, fontsize=8.5, color=INK2)
    ax.set_title(title, loc="left", fontsize=11, color=INK, pad=10)
    ax.set_ylabel("reported revenue growth, % y/y", fontsize=9, color=INK2)
    ax.set_ylim(0, max(vals[0], vals[-1]) + 4.5)
    ax.yaxis.grid(True, color=GRID, linewidth=0.8, zorder=0)
    ax.set_axisbelow(True)
    for sp in ("top", "right", "left"):
        ax.spines[sp].set_visible(False)
    ax.spines["bottom"].set_color("#c3c2b7")
    ax.tick_params(axis="y", colors=MUTED, labelsize=8.5, length=0)
    ax.tick_params(axis="x", length=0)
    ax.set_facecolor(SURF)

fig, axes = plt.subplots(1, 2, figsize=(14, 5.6), facecolor=SURF)
b = q4[q4.scenario == "base"]
waterfall(axes[0], b, "Q4 2026: from the Q3 guide midpoint to our base, by term",
          ["Q3 guide\nmidpoint", "FX after\nhedging", "Nights\n(RNPL US lap)", "ADR\nex-FX", "Take-rate /\ntiming", "Q4 2026\nbase"])
b2 = fy[fy.scenario == "base"]
waterfall(axes[1], b2, "FY27: from FY26 base to FY27 base, by term",
          ["FY26\nbase", "FX after\nhedging", "Nights\n(global lap,\nWorld Cup)", "ADR\nex-FX", "Take-rate /\ntiming", "FY27\nbase"])
# Street reference lines
axes[0].axhline(3200 / 2778 * 100 - 100, color=INK2, linewidth=1, linestyle=(0, (4, 3)), zorder=2)
axes[0].text(5.35, 3200 / 2778 * 100 - 100 + 0.2, "Street Q4 $3.20bn = +15.2%", ha="right", va="bottom", fontsize=8.5, color=INK2)
axes[1].axhline(11.4, color=INK2, linewidth=1, linestyle=(0, (4, 3)), zorder=2)
axes[1].text(5.35, 13.3, "Street FY27 +11.3 to +11.5% (dashed)", ha="right", va="bottom", fontsize=8.5, color=INK2)
from matplotlib.patches import Patch
fig.legend(handles=[Patch(color=NEG, label="reduces growth"), Patch(color=POS, label="adds to growth"), Patch(color=TOT, label="level")],
           loc="lower center", ncol=3, frameon=False, fontsize=9, bbox_to_anchor=(0.5, 0.035))
fig.text(0.01, 0.002, f"FX: FRED DEXUSEU to {fx_asof}, workstream-05 lagged fit, consensus EUR/USD path. Nights/ADR: workstream-10 regional base. "
         f"Residual base = trailing-four mean. Hedge (-0.2pp/qtr) sits inside the FX bar. Street is a comparison, not an input.",
         fontsize=7.5, color=MUTED)
plt.tight_layout(rect=(0, 0.09, 1, 1))
FIG.mkdir(exist_ok=True, parents=True)
fig.savefig(FIG / "29_q4_fy27_bridge.png", dpi=160, facecolor=SURF)

# ----------------------------------------------------------------------------------------------------------
# 7. Console summary
# ----------------------------------------------------------------------------------------------------------
pd.set_option("display.width", 200)
print(f"FX data through {fx_asof}; {CUR} {realised(CUR):.0%} observed; spec slope {SLOPE:.3f} intercept {INTERCEPT:.3f} LOO {LOO:.2f}")
print("\nFX refresh (consensus path):")
print(fx[fx.path == "consensus"][["quarter", "eurusd_yoy_pct", "driver_two_prior_q_avg", "revenue_fx_fit_pp", "revenue_fx_stated_pp", "hedge_reclass_pp", "driver_realised_share", "status"]].to_string(index=False))
print("\nFX step-down 3Q26 -> 4Q26:", fx_step)
print("\nResidual history:"); print(hist.to_string(index=False))
print("\nQ4 2026 bridge:"); print(q4[["scenario", "term", "value_pp", "kind"]].to_string(index=False))
print("\nFY27 bridge:"); print(fy[["scenario", "term", "value_pp", "kind"]].to_string(index=False))
print("\nFY27 quarterly path:"); print(ph[["scenario", "quarter", "nights_yoy_pct", "adr_exfx_pct", "residual_pp", "fx_pp", "reported_growth_pct", "revenue_musd"]].to_string(index=False))
print("\nwrote 29_fx_refresh, 29_fx_step_down, 29_residual_history, 29_bridge_assumptions, 29_q4_2026_bridge, 29_fy27_bridge, 29_fy27_quarterly_path; figure 29_q4_fy27_bridge.png")
