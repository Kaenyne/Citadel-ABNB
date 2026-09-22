"""C6 - adjusted EBITDA and margin, 3Q26 to FY27. Verify-only recompute.

Reads ONLY committed CSVs under data/processed/margin_build/{23_final_model,40_line_build,
02_financial_panel} and writes ONLY into this receipt folder. It runs no margin package and no
scorer (rule 1 of the C6 brief; the 23_final_model MARGIN_VERIFY_ONLY=1 run for this wave is
C4's receipt_23_verify.json, exit 0).

Checks
  A  DEC-0003 identity, every line-build row: revenue - total_cash_costs + da + lodging = adj_ebitda
  B  the calibrated combination's 3Q26 margin rebuilt from the committed member weights x points
  C  the adopted dollar object = that margin x the bridge-v3 revenue leg
  D  P(beat Street) from the SAME object's conformal qhat80 (Gaussian, sd = qhat80/1.2816)
  E  annual aggregation, both builds: FY26 = 1H26 actual + 3Q26 + 4Q26, FY27 = sum of four
  F  what the Street's FY27 36.45% requires, on the line build's other four cost lines
  G  the stale-orphan check on 40_vs_run_and_street.csv
Writes c6_ebitda_scenarios.csv, c6_checks.csv, c6_fy27_bridge.csv.
"""
from __future__ import annotations
from pathlib import Path
import math
import pandas as pd

ROOT = Path(__file__).resolve().parents[5]
MB = ROOT / "data/processed/margin_build"
OUT = ROOT / "data/processed/pitch_model_v2/receipts/C6"
TOL_PP, TOL_M = 0.005, 0.5

lines = pd.read_csv(MB / "40_line_build/40_lines_quarterly.csv")
annual = pd.read_csv(MB / "40_line_build/40_annual.csv")
short_q = pd.read_csv(MB / "40_line_build/40_short_case_quarterly.csv")
short_s = pd.read_csv(MB / "40_line_build/40_short_case_summary.csv")
fq = pd.read_csv(MB / "23_final_model/23_forecast_quarterly.csv")
fa = pd.read_csv(MB / "23_final_model/23_forecast_annual.csv")
live = pd.read_csv(MB / "23_final_model/23_combination_live.csv")
dlive = pd.read_csv(MB / "23_final_model/23_dollar_from_margin_live.csv")
card = pd.read_csv(MB / "23_final_model/23_card_5nov.csv")
cons = pd.read_csv(MB / "23_final_model/23_vs_consensus.csv")
pan = pd.read_csv(MB / "02_financial_panel/02_panel_quarterly.csv").set_index("quarter")

checks: list[dict] = []
def chk(name, got, want, tol, unit, note=""):
    ok = (got is not None and want is not None and abs(got - want) <= tol)
    checks.append(dict(check=name, recomputed=got, committed=want, diff=(None if got is None or want is None else got - want),
                       tolerance=tol, unit=unit, match=("yes" if ok else "no"), note=note))
    return ok

# --- A. DEC-0003 identity on every line-build row (base + 7 scenarios, and the short case) ------
for lab, df in (("line build", lines), ("short case", short_q)):
    resid = (df.revenue - df.total_cash_costs + df.da + df.lodging_reserves - df.adj_ebitda).abs().max()
    chk(f"A. DEC-0003 identity, max |resid| ({lab}, n={len(df)})", float(resid), 0.0, 1e-6, "USD m",
        "revenue - cash costs + D&A + lodging reserves = adj EBITDA")
    mres = (df.adj_ebitda / df.revenue * 100 - df.adj_ebitda_margin_pct).abs().max()
    chk(f"A. margin = EBITDA/revenue, max |resid| ({lab})", float(mres), 0.0, 1e-9, "pp")
# and on the calibrated run (D&A is inside addbacks there)
r = fq[fq.scenario == "base"]
chk("A. 23 run: five lines - D&A add-back = total cash costs", float((r.sum_five_lines_musd - r.addbacks_musd - r.total_cash_costs_musd).abs().max()), 0.0, 1e-6, "USD m")
chk("A. 23 run: revenue - total cash costs = adj EBITDA", float((r.revenue_musd - r.total_cash_costs_musd - r.adj_ebitda_musd).abs().max()), 0.0, 1e-6, "USD m")
chk("A. 23 run: D&A add-back equals the line build's D&A", float(r.set_index("quarter").loc["2026Q3", "addbacks_musd"]),
    float(lines.set_index(["quarter", "scenario"]).loc[("3Q26", "base"), "da"]), 1e-9, "USD m")

# DEC-0003 on the printed history (1Q23-2Q26): the panel is rounded to whole USD m, so the same
# identity that is exact (1e-13) on the forecast holds only to the rounding on actuals.
hist = pd.read_csv(MB / "02_financial_panel/02_panel_quarterly.csv")
hist = hist[hist.quarter.str.slice(2).astype(int).between(23, 26) & ~hist.pre_ipo]
resid = (hist.revenue - hist.total_cash_costs + hist.da + hist.lodging_tax_reserves - hist.adj_ebitda_reported).abs()
chk(f"A. DEC-0003 NARROW form on printed actuals 1Q23-2Q26 (n={len(hist)}), max |resid|", float(resid.max()), 0.0, 2.0, "USD m",
    "FAILS on history: residual = -(acquisition impacts + IPO settlement); worst 2Q23 15.0, mean %.2f" % resid.mean())
resid_full = (hist.revenue - hist.total_cash_costs + hist.da + hist.other_addbacks_total - hist.adj_ebitda_reported).abs()
chk(f"A. DEC-0003 FULL form (add-backs = lodging + acq + IPO + restr) on actuals 1Q23-2Q26 (n={len(hist)})",
    float(resid_full.max()), 0.0, 1e-9, "USD m", "exact; forward the extra add-backs are zero so the two forms coincide")
chk("A. forward acquisition/IPO add-backs are zero in both builds", float(lines.lodging_reserves.abs().max()), 0.0, 1e-12, "USD m",
    "40_params lodging_reserves_fwd = 0; no acq/IPO term exists forward")

# --- B. the 3Q26 combination margin from committed member weights x points ---------------------
row = live[(live.target == "adj_ebitda_margin_pct") & (live.quarter == "2026Q3") & (live.spec_id == "stack_clip")].iloc[0]
members = [c[3:] for c in live.columns if c.startswith("w__")]
wsum = ptsum = 0.0
mem_rows = []
for m in members:
    w, p = row.get(f"w__{m}"), row.get(f"p__{m}")
    if pd.isna(w) or pd.isna(p):
        continue
    wsum += float(w); ptsum += float(w) * float(p)
    mem_rows.append(dict(member=m, weight=float(w), member_point_pct=float(p), contribution_pp=float(w) * float(p)))
chk("B. member weights sum to 1", wsum, 1.0, 1e-9, "-", f"{len(mem_rows)} members")
q3_margin = ptsum / wsum
chk("B. 3Q26 combination margin (stack_clip), rebuilt", q3_margin, float(row.point), TOL_PP, "pct",
    f"clip status {row.clip}; sentence ceiling {row.sentence_level}")
chk("B. clip did not bind (raw == clipped)", float(row.raw_point), float(row.point), 1e-12, "pct")
chk("B. raw point is below the sentence ceiling", float(row.sentence_level) - float(row.raw_point), 0.1455, 0.01, "pp",
    "3Q25 50.0855 - our 49.9399")

# --- C. the adopted dollar object --------------------------------------------------------------
d = dlive[(dlive.quarter == "2026Q3") & (dlive.spec_id == "stack_clip")].iloc[0]
chk("C. 3Q26 adj EBITDA = margin x bridge-v3 revenue", q3_margin / 100 * float(d.revenue_musd), float(d.point), TOL_M, "USD m",
    f"revenue leg {d.revenue_musd}")
q3_dollar = float(d.point)
qhat80 = float(d.qhat80)
chk("C. 80% band low", q3_dollar - qhat80, 2337.0, 0.6, "USD m")
chk("C. 80% band high", q3_dollar + qhat80, 2462.0, 0.6, "USD m")
# the four-member dollar combination is the labelled cross-check, not the quoted object
x = live[(live.target == "adj_ebitda_musd") & (live.quarter == "2026Q3") & (live.spec_id == "stack_clip")].iloc[0]
chk("C. four-member dollar cross-check (NOT the quoted object)", float(x.point), 2411.0, 1.0, "USD m")

# --- D. P(beat) on the same object -------------------------------------------------------------
street_q3 = float(cons[cons.period == "2026Q3"].model_ebitda_musd.iloc[0] - cons[cons.period == "2026Q3"].gap_ebitda_musd.iloc[0])
sd = qhat80 / 1.2816
p_beat = 0.5 * (1 + math.erf((q3_dollar - street_q3) / (sd * math.sqrt(2))))
card_p = float(card[card["item"].str.startswith("P(3Q26 adj EBITDA beats")]["value"].iloc[0])
chk("D. P(3Q26 adj EBITDA beats Street)", p_beat, card_p, 0.002, "probability", f"sd = qhat80/1.2816 = {sd:.1f}")
chk("D. beat vs Street, dollars", q3_dollar - street_q3, float(card[card["item"] == "3Q26 beat vs Street, $"]["value"].iloc[0]), TOL_M, "USD m")

# --- E. annual aggregation ---------------------------------------------------------------------
h1_rev = float(pan.loc["1Q26", "revenue"] + pan.loc["2Q26", "revenue"])
h1_eb = float(pan.loc["1Q26", "adj_ebitda_reported"] + pan.loc["2Q26", "adj_ebitda_reported"])
h1_da = float(pan.loc["1Q26", "da"] + pan.loc["2Q26", "da"])
chk("E. 1H26 actual revenue", h1_rev, 6286.0, 0.01, "USD m", "02_panel_quarterly")
chk("E. 1H26 actual adj EBITDA", h1_eb, 1780.0, 0.01, "USD m", "02_panel_quarterly")

def fy(df, scen, per, ebcol, revcol, dacol, quarters):
    s = df[df.scenario == scen].set_index("quarter")
    eb = s.loc[quarters, ebcol].sum(); rev = s.loc[quarters, revcol].sum(); da = s.loc[quarters, dacol].sum()
    if per == "FY26":
        eb += h1_eb; rev += h1_rev; da += h1_da
    return float(eb), float(rev), float(da)

lb26 = fy(lines, "base", "FY26", "adj_ebitda", "revenue", "da", ["3Q26", "4Q26"])
lb27 = fy(lines, "base", "FY27", "adj_ebitda", "revenue", "da", ["1Q27", "2Q27", "3Q27", "4Q27"])
a = annual.set_index(["period", "scenario"])
chk("E. line build FY26 adj EBITDA", lb26[0], float(a.loc[("FY26", "base"), "adj_ebitda"]), TOL_M, "USD m")
chk("E. line build FY26 margin", lb26[0] / lb26[1] * 100, float(a.loc[("FY26", "base"), "adj_ebitda_margin_pct"]), TOL_PP, "pct")
chk("E. line build FY26 D&A", lb26[2], float(a.loc[("FY26", "base"), "da"]), 1e-6, "USD m")
chk("E. line build FY27 adj EBITDA", lb27[0], float(a.loc[("FY27", "base"), "adj_ebitda"]), TOL_M, "USD m")
chk("E. line build FY27 margin", lb27[0] / lb27[1] * 100, float(a.loc[("FY27", "base"), "adj_ebitda_margin_pct"]), TOL_PP, "pct")
fa_i = fa.set_index(["period", "scenario"])
cc26 = h1_eb + float(fq[(fq.scenario == "base") & (fq.quarter == "2026Q3")].adj_ebitda_musd.iloc[0]) + float(fq[(fq.scenario == "base") & (fq.quarter == "2026Q4")].adj_ebitda_musd.iloc[0])
chk("E. combination FY26 adj EBITDA (1H26 actual + 3Q26 comb + 4Q26 Street)", cc26, float(fa_i.loc[("FY26", "base"), "adj_ebitda_musd"]), TOL_M, "USD m")
cc27 = float(fq[(fq.scenario == "base") & (fq.quarter.str.startswith("2027"))].adj_ebitda_musd.sum())
chk("E. combination FY27 adj EBITDA (sum of the four 2027 quarters)", cc27, float(fa_i.loc[("FY27", "base"), "adj_ebitda_musd"]), TOL_M, "USD m")
chk("E. combination FY27 margin", cc27 / float(fa_i.loc[("FY27", "base"), "revenue_musd"]) * 100, float(fa_i.loc[("FY27", "base"), "adj_ebitda_margin_pct"]), TOL_PP, "pct")
chk("E. 4Q26 combination point equals the Street's margin (h=1 rule)",
    float(fq[(fq.scenario == "base") & (fq.quarter == "2026Q4")].adj_ebitda_margin_pct.iloc[0]),
    float(cons[cons.period == "2026Q4"].lseg_margin_pct.iloc[0]), 1e-6, "pct", "pre-registered secondary test failed at h=1")

# --- F. what the Street's FY27 36.45% requires --------------------------------------------------
lb27_rev = lb27[1]
st = cons[cons.period == "FY27"].iloc[0]
st_eb, st_rev, st_mgn = float(st.lseg_ebitda_musd), float(st.lseg_revenue_musd), float(st.lseg_margin_pct)
lb = a.loc[("FY27", "base")]
other4 = float(lb.cor_cash + lb.ops_cash + lb.pd_cash + lb.ga_cash)
sm_needed_own = st_mgn / 100 * lb27_rev  # Street margin on OUR revenue
bridge = []
fy26_sm = float(a.loc[("FY26", "base"), "sm_cash"])
fy26_cc = float(a.loc[("FY26", "base"), "total_cash_costs"])
def brow(label, eb, rev, eb26, rev26, sm26=None):
    """Each row's incremental margin is measured against ITS OWN FY26 base (the SYNTHESIS
    convention: 24.7% for the combination, 43.7% for the Street). implied_sm holds the line
    build's other four FY27 cost lines and its D&A fixed and solves S&M as the residual."""
    mgn = eb / rev * 100
    sm = rev - eb + float(lb.da) - other4
    bridge.append(dict(label=label, fy27_revenue_musd=rev, fy27_adj_ebitda_musd=eb, fy27_margin_pct=mgn,
                       fy26_adj_ebitda_musd=eb26, fy26_margin_pct=eb26 / rev26 * 100,
                       implied_sm_musd=sm, implied_sm_pct_rev=sm / rev * 100,
                       implied_sm_yoy_pct=(sm / (sm26 if sm26 else fy26_sm) - 1) * 100,
                       implied_total_cash_costs_musd=rev - eb + float(lb.da),
                       implied_total_cash_costs_yoy_pct=((rev - eb + float(lb.da)) / fy26_cc - 1) * 100,
                       incremental_margin_pct=(eb - eb26) / (rev - rev26) * 100))
brow("line build base", lb27[0], lb27_rev, lb26[0], lb26[1])
brow("calibrated combination (scenario)", cc27, float(fa_i.loc[("FY27", "base"), "revenue_musd"]), cc26, float(fa_i.loc[("FY26", "base"), "revenue_musd"]))
brow("Street, on the Street's own revenue", st_eb, st_rev, float(cons[cons.period == "FY26"].lseg_ebitda_musd.iloc[0]), float(cons[cons.period == "FY26"].lseg_revenue_musd.iloc[0]))
brow("Street margin, on our revenue", sm_needed_own, lb27_rev, lb26[0], lb26[1])
sh = short_s.set_index("case").loc["short_costs_at_budget"]
brow("short (costs at budget)", float(sh.fy27_ebitda), float(sh.fy27_revenue), float(sh.fy26_ebitda), float(sh.fy26_revenue))
brow("breaker (ramp pauses)", float(a.loc[("FY27", "cost_bull"), "adj_ebitda"]), float(a.loc[("FY27", "cost_bull"), "revenue"]),
     float(a.loc[("FY26", "cost_bull"), "adj_ebitda"]), float(a.loc[("FY26", "cost_bull"), "revenue"]), float(a.loc[("FY26", "cost_bull"), "sm_cash"]))
bdf = pd.DataFrame(bridge)
chk("F. Street FY27 margin", st_mgn, 36.449684038762676, 1e-6, "pct", "LSEG n 44, EBITDA sd 154.2")
chk("F. combination FY27 incremental margin (SYNTHESIS 24.7)", float(bdf.loc[1, "incremental_margin_pct"]), 24.7, 0.1, "pct", "own FY26 base")
chk("F. Street FY27 incremental margin (SYNTHESIS 43.7)", float(bdf.loc[2, "incremental_margin_pct"]), 43.7, 0.1, "pct", "Street FY26 base")
chk("F. Street-implied FY27 S&M (C4/DEC-0011 3328)", float(bdf.loc[2, "implied_sm_musd"]), 3328.0, 1.0, "USD m", "line build other four lines held")

# --- G. the stale orphan -----------------------------------------------------------------------
vs_now = pd.read_csv(MB / "40_line_build/40_vs_run.csv")
vs_old = pd.read_csv(MB / "40_line_build/40_vs_run_and_street.csv")
n0 = float(vs_now[(vs_now.quarter == "3Q26") & (vs_now.line == "adj_ebitda")].line_build.iloc[0])
o0 = float(vs_old[(vs_old.quarter == "3Q26") & (vs_old.line == "adj_ebitda")].line_build.iloc[0])
chk("G. 40_vs_run.csv 3Q26 line_build EBITDA == 40_lines_quarterly base", n0, float(lines.set_index(["quarter", "scenario"]).loc[("3Q26", "base"), "adj_ebitda"]), 1e-9, "USD m")
near = lines[lines.quarter == "3Q26"].assign(gap=lambda t: (t.adj_ebitda - o0).abs()).sort_values("gap").iloc[0]
chk("G. 40_vs_run_and_street.csv 3Q26 matches SOME committed scenario", float(near.gap), 0.0, 1.0, "USD m",
    f"closest committed scenario {near.scenario} at {near.adj_ebitda:.1f}; orphan says {o0:.1f} - STALE, not written by the current run.py")

# --- the scenario table -------------------------------------------------------------------------
rows = []
def srow(scen_label, per, eb, rev, da, src):
    rows.append(dict(scenario=scen_label, period=per, adj_ebitda_musd=round(eb, 1), adj_ebitda_margin_pct=round(eb / rev * 100, 3),
                     revenue_musd=round(rev, 1), da_musd=round(da, 3), source=src))
for per, qs in (("3Q26", ["3Q26"]), ("4Q26", ["4Q26"]), ("FY26", ["3Q26", "4Q26"]), ("FY27", ["1Q27", "2Q27", "3Q27", "4Q27"])):
    for lbl, scen, df in (("base (line build)", "base", lines), ("breaker (ramp pauses)", "cost_bull", lines),
                          ("short", "short_costs_at_budget", short_q)):
        eb, rev, da = fy(df, scen, per, "adj_ebitda", "revenue", "da", qs)
        srow(lbl, per, eb, rev, da, f"40_line_build scenario {scen}")
# calibrated combination
for per, val in (("3Q26", fq[(fq.scenario == "base") & (fq.quarter == "2026Q3")]), ("4Q26", fq[(fq.scenario == "base") & (fq.quarter == "2026Q4")])):
    srow("alt_combination (5 Nov card)", per, float(val.adj_ebitda_musd.iloc[0]), float(val.revenue_musd.iloc[0]), float(val.da_musd.iloc[0]), "23_final_model stack_clip")
srow("alt_combination (5 Nov card)", "FY26", cc26, float(fa_i.loc[("FY26", "base"), "revenue_musd"]), float(fa_i.loc[("FY26", "base"), "da_musd"]), "23_forecast_annual")
srow("alt_combination (5 Nov card)", "FY27", cc27, float(fa_i.loc[("FY27", "base"), "revenue_musd"]), float(fa_i.loc[("FY27", "base"), "da_musd"]), "23_forecast_annual (SCENARIO: h>=2 fails)")
for per, key in (("3Q26", "2026Q3"), ("4Q26", "2026Q4"), ("FY26", "FY26"), ("FY27", "FY27")):
    c = cons[cons.period == key].iloc[0]
    srow("street (LSEG)", per, float(c.lseg_ebitda_musd), float(c.lseg_revenue_musd), float("nan"), f"23_vs_consensus n={c.lseg_n:.0f}")
sdf = pd.DataFrame(rows)

pd.DataFrame(mem_rows).to_csv(OUT / "c6_member_recompute.csv", index=False)
sdf.to_csv(OUT / "c6_ebitda_scenarios.csv", index=False)
bdf.to_csv(OUT / "c6_fy27_bridge.csv", index=False)
cdf = pd.DataFrame(checks)
cdf.to_csv(OUT / "c6_checks.csv", index=False)

pd.set_option("display.width", 220); pd.set_option("display.max_columns", 30)
print("=== CHECKS ==="); print(cdf.to_string(index=False))
print("\n=== SCENARIOS ==="); print(sdf.to_string(index=False))
print("\n=== FY27 BRIDGE ==="); print(bdf.to_string(index=False))
print("\n=== MEMBER RECOMPUTE (3Q26 margin) ==="); print(pd.DataFrame(mem_rows).to_string(index=False))
bad = cdf[cdf.match == "no"]
print(f"\n{len(cdf) - len(bad)}/{len(cdf)} checks match.")
if len(bad):
    print("MISMATCHES:"); print(bad.to_string(index=False))
raise SystemExit(0)
