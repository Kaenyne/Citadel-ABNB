"""
42_margin_reaction: does margin news move ABNB, and by how much? Post-print returns against the forward (NTM) consensus revisions each
print caused, split into revenue and margin, plus the stock arithmetic of a FY27 margin reset.

Run:  py -3.13 analysis/src/margin_build/42_margin_reaction/run.py   (exit 0; writes data/processed/margin_build/42_margin_reaction/)

Pre-registration: docs/margin-build/notes/41_42_prereg.md (committed f6d01166 before this script existed): R1, R2, R3 and the scenario.
Returns: data/processed/abnb_earnings_reactions.csv (close-to-close from the pre-print close; prints are after the close), re-verified
against Yahoo closes when yfinance is reachable (42_return_check.csv). Revisions: LSEG FY means the day before the print and 5 trading
days after (03_consensus_at_dates.csv, fy_{current,next}_{pre_guide,post_guide_5td}); the builder already rolls FY1 at February prints.
NTM blend: weight on the current fiscal year = days left in it at the print date / 365.
"""
from __future__ import annotations
from pathlib import Path
import numpy as np
import pandas as pd
import statsmodels.api as sm
from scipy import stats

ROOT = Path(__file__).resolve().parents[4]
MB = ROOT / "data/processed/margin_build"
OUT = MB / "42_margin_reaction"; OUT.mkdir(parents=True, exist_ok=True)
REACT = ROOT / "data/processed/abnb_earnings_reactions.csv"
CAD = MB / "03_consensus_pit/03_consensus_at_dates.csv"
SURP = MB / "03_consensus_pit/03_surprise_history.csv"
GUIDE = ROOT / "data/processed/abnb_guidance_reaction_panel.csv"
CUR = MB / "03_consensus_pit/03_current_consensus.csv"
W1 = ("2023Q1", "2026Q2"); W2 = ("2024Q1", "2026Q2")
PRICE, PRICE_DATE, SHARES, NET_CASH = 167.51, "2026-09-16", 597.0, 9600.0   # DEC-0015 provisional spot; memo v3 share count and net cash ex-float

# ----------------------------------------------------------------------------------------------------------------------
# 1. Panel: returns, surprises, NTM revisions, guidance features
# ----------------------------------------------------------------------------------------------------------------------
r = pd.read_csv(REACT).rename(columns={"quarter": "print_quarter"})
s = pd.read_csv(SURP)[["print_quarter", "print_date", "ebitda_surprise_pct", "revenue_surprise_pct", "actual_margin_pct", "street_margin_pct"]]
s["margin_surprise_pts"] = s.actual_margin_pct - s.street_margin_pct
cad = pd.read_csv(CAD); fy = cad[cad.target_role.str.startswith("fy_")]
def val(q, role, col):
    x = fy[(fy.printed_quarter == q) & (fy.target_role == role)]
    return (float(x[col].iloc[0]), x.target_period.iloc[0]) if len(x) and pd.notna(x[col].iloc[0]) else (np.nan, None)
rows = []
for q, pdte in zip(s.print_quarter, s.print_date):
    e_cp, fyc = val(q, "fy_current_pre_guide", "ebitda_mean"); e_ca, _ = val(q, "fy_current_post_guide_5td", "ebitda_mean")
    e_np, fyn = val(q, "fy_next_pre_guide", "ebitda_mean"); e_na, _ = val(q, "fy_next_post_guide_5td", "ebitda_mean")
    r_cp, _ = val(q, "fy_current_pre_guide", "revenue_mean"); r_ca, _ = val(q, "fy_current_post_guide_5td", "revenue_mean")
    r_np, _ = val(q, "fy_next_pre_guide", "revenue_mean"); r_na, _ = val(q, "fy_next_post_guide_5td", "revenue_mean")
    if fyc is None: continue
    w = max(0.0, (pd.Timestamp(f"{fyc[2:]}-12-31") - pd.Timestamp(pdte)).days / 365)
    ntm = lambda a, b: w * a + (1 - w) * b
    e_pre, e_post, v_pre, v_post = ntm(e_cp, e_np), ntm(e_ca, e_na), ntm(r_cp, r_np), ntm(r_ca, r_na)
    rows.append(dict(print_quarter=q, print_date=pdte, fy_current=fyc, fy_next=fyn, w_current=w,
                     ntm_ebitda_pre=e_pre, ntm_ebitda_post=e_post, ntm_ebitda_rev_pct=(e_post / e_pre - 1) * 100,
                     ntm_revenue_rev_pct=(v_post / v_pre - 1) * 100, ntm_margin_pre_pct=e_pre / v_pre * 100,
                     ntm_margin_rev_pts=(e_post / v_post - e_pre / v_pre) * 100,
                     fy_next_ebitda_rev_pct=(e_na / e_np - 1) * 100, fy_next_revenue_rev_pct=(r_na / r_np - 1) * 100,
                     fy_next_margin_rev_pts=(e_na / r_na - e_np / r_np) * 100))
rev = pd.DataFrame(rows)
g = pd.read_csv(GUIDE)[["print_quarter", "fy_margin_action", "fy_margin_delta_pts", "nq_margin_dir", "new_investment_flag", "guide_vs_street_pct", "nq_nights_dir"]]
panel = r.merge(s, on="print_quarter", how="left").merge(rev, on=["print_quarter", "print_date"], how="left").merge(g, on="print_quarter", how="left")

# optional re-verification of the return file against Yahoo closes
try:
    import yfinance as yf
    px = yf.download(["ABNB", "QQQ"], start="2021-02-01", end="2026-09-22", auto_adjust=False, progress=False)["Close"].dropna()
    chk = []
    for _, row in panel.iterrows():
        d = pd.Timestamp(row.reaction_date); i = px.index.get_indexer([d])[0]
        if i <= 0: continue
        a1 = (px.ABNB.iloc[i] / px.ABNB.iloc[i - 1] - 1) * 100; q1 = (px.QQQ.iloc[i] / px.QQQ.iloc[i - 1] - 1) * 100
        j = min(i + 4, len(px) - 1); a5 = (px.ABNB.iloc[j] / px.ABNB.iloc[i - 1] - 1) * 100; q5 = (px.QQQ.iloc[j] / px.QQQ.iloc[i - 1] - 1) * 100
        chk.append(dict(print_quarter=row.print_quarter, reaction_date=row.reaction_date, file_1d=row.abnb_1d_pct, yahoo_1d=a1, file_excess_1d=row.excess_1d_pct,
                        yahoo_excess_1d=a1 - q1, file_excess_5d=row.excess_5d_pct, yahoo_excess_5d=a5 - q5))
    chk = pd.DataFrame(chk); chk["abs_diff_1d"] = (chk.file_1d - chk.yahoo_1d).abs(); chk["abs_diff_excess_5d"] = (chk.file_excess_5d - chk.yahoo_excess_5d).abs()
    chk.to_csv(OUT / "42_return_check.csv", index=False)
    latest = (float(px.ABNB.iloc[-1]), str(px.index[-1].date()))
except Exception as exc:                                                    # offline: keep the file's returns, say so
    chk = None; latest = None; print("return re-verification skipped:", exc)
panel.to_csv(OUT / "42_panel.csv", index=False)

# ----------------------------------------------------------------------------------------------------------------------
# 2. Pre-registered regressions R1-R3 (HC1, one-sided p for a positive coefficient), windows W1 and W2, plus 2022Q1+ descriptive
# ----------------------------------------------------------------------------------------------------------------------
def fit(df, y, xs):
    d = df.dropna(subset=[y] + xs)
    m = sm.OLS(d[y], sm.add_constant(d[xs])).fit(cov_type="HC1")
    return m, len(d)
res = []
for wname, w in [("W1", W1), ("W2", W2), ("2022Q1+", ("2022Q1", "2026Q2"))]:
    d = panel[(panel.print_quarter >= w[0]) & (panel.print_quarter <= w[1])]
    for rid, y, xs in [("R1", "excess_5d_pct", ["ntm_ebitda_rev_pct"]), ("R2", "excess_5d_pct", ["ntm_revenue_rev_pct", "ntm_margin_rev_pts"]),
                       ("R3", "excess_1d_pct", ["ntm_ebitda_rev_pct"]), ("R2_day1", "excess_1d_pct", ["ntm_revenue_rev_pct", "ntm_margin_rev_pts"])]:
        m, n = fit(d, y, xs)
        for x in xs:
            t = float(m.tvalues[x]); res.append(dict(test=rid, window=wname, y=y, x=x, n=n, coef=float(m.params[x]), se=float(m.bse[x]), t=t,
                                                      p_one_sided=float(stats.norm.sf(t)), r2=float(m.rsquared), intercept=float(m.params["const"])))
res = pd.DataFrame(res)
def verdict(rid, x):
    sub = res[(res.test == rid) & (res.x == x) & res.window.isin(["W1", "W2"])]
    return "PASS" if ((sub.coef > 0) & (sub.p_one_sided <= 0.10)).all() and len(sub) == 2 else "FAIL"
for rid, x in [("R1", "ntm_ebitda_rev_pct"), ("R2", "ntm_margin_rev_pts"), ("R2", "ntm_revenue_rev_pct"), ("R3", "ntm_ebitda_rev_pct"),
               ("R2_day1", "ntm_margin_rev_pts"), ("R2_day1", "ntm_revenue_rev_pct")]:
    res.loc[(res.test == rid) & (res.x == x), "verdict_both_windows"] = verdict(rid, x)
res.to_csv(OUT / "42_regressions.csv", index=False)

# ----------------------------------------------------------------------------------------------------------------------
# 3. The FY27 margin-reset scenario (pre-registered): 100/150/200bp below the Street's 36.45% x revenue 0/-2/-4%
# ----------------------------------------------------------------------------------------------------------------------
cur = pd.read_csv(CUR); cur = cur[cur.vendor == "LSEG"].set_index("period")
E26, E27, E28 = (float(cur.loc[p, "ebitda_mean"]) for p in ["FY26", "FY27", "FY28"])
R27 = float(cur.loc["FY27", "revenue_mean"]); M27 = E27 / R27
b1 = res[(res.test == "R1") & (res.window == "W1")].coef.iloc[0]; b2 = res[(res.test == "R1") & (res.window == "W2")].coef.iloc[0]
r1_pass = verdict("R1", "ntm_ebitda_rev_pct") == "PASS"
ev = PRICE * SHARES - NET_CASH; mult = ev / E27
sc = []
for when, w_cur, pre in [("5 Nov 2026 print", (pd.Timestamp("2026-12-31") - pd.Timestamp("2026-11-05")).days / 365, (E26, E27)),
                         ("Feb 2027 print", (pd.Timestamp("2027-12-31") - pd.Timestamp("2027-02-11")).days / 365, (E27, E28))]:
    for cut_bp in [100, 150, 200]:
        for rev_cut in [0.0, 2.0, 4.0]:
            e27_new = R27 * (1 - rev_cut / 100) * (M27 - cut_bp / 1e4); d27 = e27_new - E27
            if when.startswith("5 Nov"):
                ntm_pre = w_cur * E26 + (1 - w_cur) * E27; ntm_rev = (1 - w_cur) * d27 / ntm_pre * 100
            else:
                ntm_pre = w_cur * E27 + (1 - w_cur) * E28; ntm_rev = w_cur * d27 / ntm_pre * 100       # FY28 held at consensus: optimistic for bulls
            const_px = d27 * mult / SHARES; const_pct = const_px / PRICE * 100
            sc.append(dict(when=when, margin_cut_bp=cut_bp, fy27_revenue_cut_pct=rev_cut, fy27_ebitda_new=e27_new, d_fy27_ebitda=d27,
                           d_fy27_ebitda_pct=d27 / E27 * 100, ntm_ebitda_rev_pct=ntm_rev,
                           move_r1_W1_pct=b1 * ntm_rev if r1_pass else np.nan, move_r1_W2_pct=b2 * ntm_rev if r1_pass else np.nan,
                           move_constant_multiple_pct=const_pct, price_constant_multiple=PRICE + const_px, ev_ebitda_multiple=mult))
sc = pd.DataFrame(sc); sc.to_csv(OUT / "42_scenarios.csv", index=False)

pd.set_option("display.width", 260); pd.set_option("display.max_columns", 40)
show = ["print_quarter", "reaction_date", "abnb_1d_pct", "excess_1d_pct", "excess_5d_pct", "ebitda_surprise_pct", "margin_surprise_pts",
        "ntm_ebitda_rev_pct", "ntm_revenue_rev_pct", "ntm_margin_rev_pts", "fy_margin_action", "new_investment_flag"]
print(panel[show].round(2).to_string(index=False))
if chk is not None: print("\nreturn check: max |1d diff|", round(chk.abs_diff_1d.max(), 2), "max |5d excess diff|", round(chk.abs_diff_excess_5d.max(), 2), "latest", latest)
print("\n=== regressions ===\n", res.round(4).to_string(index=False))
print("\n=== scenarios ===\n", sc.round(2).to_string(index=False))
print("\nwrote", OUT)
