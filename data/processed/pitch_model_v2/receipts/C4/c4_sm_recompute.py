"""C4 — independent recompute of the sales & marketing line from 40_params.csv,
plus the three pitch scenarios (base / short / breaker) for 3Q26, 4Q26, FY26, FY27.

Read-only. Writes only into this receipt folder.
  PYTHONPATH=analysis/src python3 data/processed/pitch_model_v2/receipts/C4/c4_sm_recompute.py

Method. The S&M line in analysis/src/margin_build/40_line_build/run.py is a closed-form
chain on six named parameters plus the 2H26 reconciliation step. This script re-implements
that chain from the committed parameter sheet and checks it against the committed line
outputs, then re-solves it under the "ramp pauses" parameterisations. The reconciliation gap
(a property of the whole cost stack, not of S&M) is read from the committed lines file rather
than re-derived, so this is a check of the S&M line, not of the whole build.
"""
from __future__ import annotations
import pandas as pd
from pathlib import Path

ROOT = Path(__file__).resolve().parents[5]
LB = ROOT / "data/processed/margin_build/40_line_build"
PAN = ROOT / "data/processed/margin_build/02_financial_panel/02_panel_quarterly.csv"
RUN23 = ROOT / "data/processed/margin_build/23_final_model/23_lines_quarterly.csv"
OUT = Path(__file__).resolve().parent

# constants copied from 40_line_build/run.py (2023-25 mean quarterly shares, WS02 02_seasonality)
SHARE_SM = {1: .2397, 2: .2703, 3: .2370, 4: .2530}
H2_SM = SHARE_SM[3] + SHARE_SM[4]
Q_ORDER = ["3Q26", "4Q26", "1Q27", "2Q27", "3Q27", "4Q27"]
QN = {q: int(q[0]) for q in Q_ORDER}

params = pd.read_csv(LB / "40_params.csv").set_index("name")
PV = {c: params[c].to_dict() for c in ("base", "bear", "bull")}
pan = pd.read_csv(PAN).set_index("quarter")
lines = pd.read_csv(LB / "40_lines_quarterly.csv")
short_q = pd.read_csv(LB / "40_short_case_quarterly.csv")
short_sum = pd.read_csv(LB / "40_short_case_summary.csv").set_index("case")

SM_1H26 = float(pan.loc["1Q26", "sm_cash"] + pan.loc["2Q26", "sm_cash"])          # 696 + 808
SM_2H25 = float(pan.loc["3Q25", "sm_cash"] + pan.loc["4Q25", "sm_cash"])          # 585 + 633
SM_FY25 = 2376.0   # FY25 10-K S&M 2,588 less S&M SBC 212 (WS02); sm_share_history_annual.csv


def sm_line(p: dict, mkt_q3_step: float, q4_cut: float = 0.0) -> dict:
    """The S&M chain of 40_line_build/run.py build(), for the six forecast quarters."""
    mkt_1h26 = p["marketing_fy25"] * p["marketing_1h_share"] * (1 + p["marketing_growth_1h26"] / 100)
    mkt_2h26 = p["marketing_fy25"] * (1 - p["marketing_1h_share"]) * (1 + p["marketing_growth_2h26"] / 100)
    fld_1h26 = SM_1H26 - mkt_1h26
    fld_fy26 = p["field_cash_fy25"] * (1 + p["field_growth_fy26"] / 100)
    fld_2h26 = fld_fy26 - fld_1h26
    fld_fy27 = fld_fy26 * (1 + p["field_growth_fy27"] / 100)
    mkt_fy27 = (mkt_1h26 + mkt_2h26 + mkt_q3_step) * (1 + p["marketing_growth_fy27"] / 100)
    out = {}
    for q in Q_ORDER:
        qn, is27 = QN[q], q.endswith("27")
        if is27:
            mkt = mkt_fy27 * SHARE_SM[qn]
            fld = fld_fy27 * SHARE_SM[qn]
        else:
            mkt = mkt_2h26 * SHARE_SM[qn] / H2_SM + (mkt_q3_step if qn == 3 else 0.0) - (q4_cut if q == "4Q26" else 0.0)
            fld = fld_2h26 * SHARE_SM[qn] / H2_SM
        out[q] = mkt + fld
    out["_mkt_fy27"], out["_fld_fy27"] = mkt_fy27, fld_fy27
    out["_mkt_2h26"], out["_fld_2h26"], out["_mkt_q3_step"] = mkt_2h26, fld_2h26, mkt_q3_step
    return out


def committed(scn: str) -> dict:
    d = lines[lines.scenario == scn].set_index("quarter")
    return {q: float(d.loc[q, "sm_cash"]) for q in Q_ORDER} | {"_gap": float(d.loc["3Q26", "recon_gap_3q26_musd"])}


checks = []
recomputed = {}
for scn, col in (("base", "base"), ("cost_bull", "bull"), ("cost_bear", "bear"), ("evidence_only", "base")):
    c = committed(scn)
    gap = c["_gap"]
    step = gap * PV[col]["recon_share_to_marketing"] if scn != "evidence_only" else 0.0
    r = sm_line(PV[col], step)
    recomputed[scn] = r
    for q in Q_ORDER:
        checks.append(dict(scenario=scn, quarter=q, recomputed=r[q], committed=c[q], abs_diff=abs(r[q] - c[q])))

chk = pd.DataFrame(checks)
chk.to_csv(OUT / "c4_sm_line_recompute_check.csv", index=False)
print("=== S&M line recompute vs committed 40_lines_quarterly.csv ===")
print(chk.groupby("scenario").abs_diff.max().to_string())
print(f"max |diff| over all 24 cells: {chk.abs_diff.max():.3e} USD m")

# ------------------------------------------------------------------ scenarios
rev = {}
for scn in ("base",):
    d = lines[lines.scenario == scn].set_index("quarter")
    rev[scn] = {q: float(d.loc[q, "revenue"]) for q in Q_ORDER}
sd = short_q.set_index("quarter")
rev["short"] = {q: float(sd.loc[q, "revenue"]) for q in Q_ORDER}
sm_short = {q: float(sd.loc[q, "sm_cash"]) for q in Q_ORDER}

REV_1H26 = float(pan.loc["1Q26", "revenue"] + pan.loc["2Q26", "revenue"])
REV_FY25 = 12241.0

# breaker: the ramp pauses. Headline = the line build's own documented bull cost column
# (2H26 marketing +18% not +25%, FY27 marketing +10% not +15%, field +14%/+8% not +18%/+11%).
sm_breaker = {q: recomputed["cost_bull"][q] for q in Q_ORDER}

# breaker variants, for the dossier's sensitivity block
p0 = dict(PV["base"])
gap_base = committed("base")["_gap"]
step_base = gap_base * p0["recon_share_to_marketing"]
hard = sm_line({**p0, "marketing_growth_fy27": 0.0, "field_growth_fy27": 0.0}, step_base)  # FY27 S&M flat on FY26 dollars
evid = recomputed["evidence_only"]
cut = float(short_sum.loc["short_with_q4_marketing_cut", "q4_marketing_cut_musd"])


def agg(sm: dict, revd: dict) -> dict:
    fy26_sm = SM_1H26 + sm["3Q26"] + sm["4Q26"]
    fy27_sm = sum(sm[q] for q in ("1Q27", "2Q27", "3Q27", "4Q27"))
    fy26_rev = REV_1H26 + revd["3Q26"] + revd["4Q26"]
    fy27_rev = sum(revd[q] for q in ("1Q27", "2Q27", "3Q27", "4Q27"))
    return dict(
        sm_3q26=sm["3Q26"], pct_3q26=sm["3Q26"] / revd["3Q26"] * 100, yoy_3q26=sm["3Q26"] / 585.0 * 100 - 100,
        sm_4q26=sm["4Q26"], pct_4q26=sm["4Q26"] / revd["4Q26"] * 100, yoy_4q26=sm["4Q26"] / 633.0 * 100 - 100,
        sm_fy26=fy26_sm, pct_fy26=fy26_sm / fy26_rev * 100, yoy_fy26=fy26_sm / SM_FY25 * 100 - 100,
        sm_fy27=fy27_sm, pct_fy27=fy27_sm / fy27_rev * 100, yoy_fy27=fy27_sm / fy26_sm * 100 - 100,
    )


rows = [
    dict(scenario="base (line build 40)", **agg(recomputed["base"], rev["base"])),
    dict(scenario="short (40 sec 8b, costs at budget)", **agg(sm_short, rev["short"])),
    dict(scenario="breaker (ramp pauses = 40 bull cost column)", **agg(sm_breaker, rev["base"])),
    dict(scenario="variant: evidence-only (no 3Q26 step)", **agg(evid, rev["base"])),
    dict(scenario="variant: hard pause (FY27 S&M flat on FY26)", **agg(hard, rev["base"])),
    dict(scenario="variant: short + 4Q26 marketing cut", **agg({**sm_short, "4Q26": sm_short["4Q26"] - cut}, rev["short"])),
]

# the calibrated combination's own allocated S&M (23_final_model), base only
r23 = pd.read_csv(RUN23)
r23 = r23[r23.scenario == "base"].set_index("quarter")
qmap = {"3Q26": "2026Q3", "4Q26": "2026Q4", "1Q27": "2027Q1", "2Q27": "2027Q2", "3Q27": "2027Q3", "4Q27": "2027Q4"}
sm23 = {q: float(r23.loc[qmap[q], "sm_cash_musd"]) for q in Q_ORDER}
rev23 = {q: float(r23.loc[qmap[q], "revenue_musd"]) for q in Q_ORDER}
rows.insert(1, dict(scenario="base (calibrated combination 23, allocated)", **agg(sm23, rev23)))

out = pd.DataFrame(rows)
out.to_csv(OUT / "c4_sm_scenarios.csv", index=False)
pd.set_option("display.width", 220)
print("\n=== C4 sales & marketing by scenario (USD m and % of revenue) ===")
print(out.round(2).to_string(index=False))

# what the Street's FY27 EBITDA implies for S&M, and the growth that gets there
street = dict(rev=15819.3, ebitda=5766.0, da=82.536, other_four=2760 + 1378 + 1625 + 1045)
street_sm = street["rev"] - street["ebitda"] + street["da"] - street["other_four"]
base_fy26_sm = SM_1H26 + recomputed["base"]["3Q26"] + recomputed["base"]["4Q26"]
print(f"\nStreet-implied FY27 S&M  ${street_sm:,.1f}M = {street_sm / street['rev'] * 100:.2f}% of revenue"
      f"  (= {street_sm / base_fy26_sm * 100 - 100:+.1f}% y/y on the line build's FY26 ${base_fy26_sm:,.1f}M)")
print(f"Line build FY27 S&M      ${out.loc[0, 'sm_fy27']:,.1f}M = {out.loc[0, 'pct_fy27']:.2f}%   ({out.loc[0, 'yoy_fy27']:+.1f}% y/y)")
print(f"Combination FY27 S&M     ${out.loc[1, 'sm_fy27']:,.1f}M = {out.loc[1, 'pct_fy27']:.2f}%   ({out.loc[1, 'yoy_fy27']:+.1f}% y/y)")
print(f"Breaker FY27 S&M         ${out.loc[3, 'sm_fy27']:,.1f}M = {out.loc[3, 'pct_fy27']:.2f}%   ({out.loc[3, 'yoy_fy27']:+.1f}% y/y)")
print(f"\nFY27 S&M gap, combination less line build: ${out.loc[1, 'sm_fy27'] - out.loc[0, 'sm_fy27']:,.1f}M "
      f"= {(out.loc[1, 'sm_fy27'] - out.loc[0, 'sm_fy27']) / 15828.607 * 100:.2f}pp of FY27 revenue")
print(f"FY27 S&M gap, line build less Street:      ${out.loc[0, 'sm_fy27'] - street_sm:,.1f}M "
      f"= {(out.loc[0, 'sm_fy27'] - street_sm) / 15828.607 * 100:.2f}pp of FY27 revenue")
print(f"4Q26 marketing cut that holds the 35.5% floor in the short case: ${cut:,.1f}M")
