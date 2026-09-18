"""R11 revision 2 (A12 audit response, 2026-09-17).

P(CoStar/STR US hotel RevPAR y/y for 4Q26 (Oct-Dec) >= +4.0%), published as ONE distribution jointly
with B15 (P(<= +1.0%)).

Inputs  us_revpar_monthly_yoy_measured.csv   <- r11_extract_lodging_monthly.py, which PARSES the 57
                                               saved Lodging Magazine reprints in ../sources/lodging_monthly/
        (no RevPAR number in this file is typed by hand; the only hand-carried monthly is March 2026,
         which is taken from the repo note and flagged, and the December-2025 implied value, also flagged)
Outputs r11_v2_quarterly_base_rate.csv, r11_v2_path.csv, r11_v2_views.csv, r11_v2_sensitivity.csv,
        r11_v2_joint_object.json
Run     py -3.13 docs/pitch-forecasts/questions/risk-q4-us-revpar-strong/datasets/r11_model_v2.py

Changes vs revision 1 (finding ids in research-log.md section 10):
  A12-03  the base rate is no longer the hand-typed list at r11_model.py:36. It is computed from 28
          machine-parsed monthly CoStar releases, each with its publication date and its snapshot file.
          Quarters carry n_months; quarters with fewer than 2 saved months are excluded.
  A12-04  the +0.8pp "easy 4Q25 comp" credit is removed from the FY-implied leg (a published FY26
          forecast already embeds the 4Q25 base). A SMALLER, MEASURED credit (+0.3 on the AR leg only)
          replaces it: 4Q25 printed about 0.3pp weaker than 3Q25 on the parsed series, so a y/y AR step
          from Q3 to Q4 faces a comp that is easier by that much and by nothing more.
  A12-17  the AR leg is labelled one step (it always was); phi and the long run are hand-set and are
          bracketed in the sensitivity grid; a second start from the mid-August clean exit rate is added.
  A12-10  R11 and B15 publish one object: 0.90 x N(trend, sd) + 0.10 x N(0.8, 1.8), B15's mixture form.
  A12-11  the anchor is re-cited to the repo note plus the saved 10 Aug 2026 trade-press snapshots in
          ../sources/; Q1 and Q2 2026 enter as measured months, not as the rev-1 4.5-6.0 assumption grid.
"""
import csv, json, os, math
import numpy as np
from scipy.stats import norm

os.chdir(os.path.dirname(os.path.abspath(__file__)))

# ---------------------------------------------------------------- 1. measured monthly series
meas = list(csv.DictReader(open("us_revpar_monthly_yoy_measured.csv", encoding="utf-8")))
monthly = {r["month"]: float(r["revpar_yoy_pct"]) for r in meas}
n_parsed = len(monthly)

# Two months are NOT in the parsed set and are carried explicitly, each flagged in the output:
#   2026-03 +5.9  the March 2026 release was not among the Lodging snapshots; the figure is the repo
#                 note's (research/notes/overnight/06_consumer-choice-and-willingness-to-pay.md 1.2)
#   2025-12 -2.2  never published in a snapshot we hold; implied by FY2025 RevPAR -0.3% (the annual
#                 release, saved as ../sources/hoteldive_fy2025_us_hotel_performance_*.html) net of the
#                 three measured 2025 quarters at equal weights
CARRIED = {"2026-03": (5.9, "repo note 06_consumer-choice 1.2; CoStar March 2026 release not snapshotted"),
           "2025-12": (None, "implied below from FY2025 -0.3%")}

def quarter_of(m):
    y, mo = m.split("-")
    return "%sQ%d" % (y, (int(mo) - 1) // 3 + 1)

qmonths = {}
for m, v in sorted({**monthly, "2026-03": CARRIED["2026-03"][0]}.items()):
    qmonths.setdefault(quarter_of(m), []).append((m, v))

q_measured = {k: float(np.mean([v for _, v in vs])) for k, vs in qmonths.items()}
# December 2025 implied from the annual release
fy2025 = -0.3
q25 = [q_measured["2025Q1"], q_measured["2025Q2"], q_measured["2025Q3"]]
q4_25_implied = 4 * fy2025 - sum(q25)                      # equal-weighted quarters
dec25_implied = 3 * q4_25_implied - sum(v for _, v in qmonths["2025Q4"])
qmonths["2025Q4"].append(("2025-12", round(dec25_implied, 2)))
q_measured["2025Q4"] = float(np.mean([v for _, v in qmonths["2025Q4"]]))

rows = []
for k in sorted(qmonths):
    vs = qmonths[k]
    n_snap = sum(1 for m, _ in vs if m in monthly)
    note = []
    if k == "2026Q3":
        note.append("current quarter, July only: excluded from the base rate")
    if any(m == "2026-03" for m, _ in vs):
        note.append("March 2026 from the repo note, not a saved snapshot")
    if any(m == "2025-12" for m, _ in vs):
        note.append("December 2025 implied from FY2025 -0.3%% (%.2f), not a saved snapshot" % dec25_implied)
    if n_snap < 2:
        note.append("fewer than two saved months: excluded from the base rate")
    rows.append((k, round(q_measured[k], 2), len(vs), n_snap, "; ".join(note)))

BASE = [r for r in rows if r[0] <= "2026Q2" and (r[3] >= 2 or r[0] in ("2025Q4",))]
vals = np.array([r[1] for r in BASE])
n = len(vals)
ge4 = int((vals >= 4).sum())
le1 = int((vals <= 1).sum())
full = [r for r in BASE if r[2] == 3 and r[3] == 3]
fvals = np.array([r[1] for r in full])
ge4_f, le1_f, nf = int((fvals >= 4).sum()), int((fvals <= 1).sum()), len(fvals)

with open("r11_v2_quarterly_base_rate.csv", "w", newline="", encoding="utf-8") as f:
    w = csv.writer(f)
    w.writerow(["quarter", "revpar_yoy_mean_pct", "n_months_used", "n_months_from_snapshot", "note"])
    w.writerows(rows)
    w.writerow([])
    w.writerow(["base-rate window", "2023Q3-2026Q2, quarters with >=2 saved months", n, "", "%s" % [r[0] for r in BASE]])
    w.writerow([">= +4.0", "%d of %d" % (ge4, n), round(ge4 / n, 3), round((ge4 + 1) / (n + 2), 3), "raw; Laplace"])
    w.writerow(["<= +1.0 (B15 mirror)", "%d of %d" % (le1, n), round(le1 / n, 3), round((le1 + 1) / (n + 2), 3), "raw; Laplace"])
    w.writerow(["complete quarters only (3 saved months)", "%d of %d >=4; %d of %d <=1" % (ge4_f, nf, le1_f, nf),
                round(ge4_f / nf, 3), round((ge4_f + 1) / (nf + 2), 3), "%s" % [r[0] for r in full]])
    w.writerow(["rev-1 hand list (r11_model.py:36)", "1 of 13 >=4; 6 of 13 <=1", "", "", "WITHDRAWN (A12-03): not a series, not sourced"])

base_rate_ge4 = 0.5 * ((ge4 + 1) / (n + 2) + (ge4_f + 1) / (nf + 2))
base_rate_le1 = 0.5 * ((le1 + 1) / (n + 2) + (le1_f + 1) / (nf + 2))

# ---------------------------------------------------------------- 2. FY-implied 4Q26 (the anchor)
W = np.array([0.23, 0.26, 0.27, 0.24])          # RevPAR-weighted quarter shares (Q3 highest, Q4 lowest)
q1_26 = q_measured["2026Q1"]                    # 0.4, 4.3, 5.9
q2_26 = q_measured["2026Q2"]                    # 4.4, 4.0, 8.4
Q3_CASES = {"Q3 +5.0 (Jul 8.2 actual, Aug ~5.0, Sep ~2)": 5.0,
            "Q3 +5.5 (Jul 8.2 actual, Aug ~5.5, Sep ~3)": 5.5,
            "Q3 +6.0 (Jul 8.2 actual, Aug ~6.0, Sep ~4)": 6.0}

def fy_implied(fy, q3):
    return (fy - W[0] * q1_26 - W[1] * q2_26 - W[2] * q3) / W[3]

path = [(lbl, q3, fy, round(fy_implied(fy, q3), 2))
        for lbl, q3 in Q3_CASES.items() for fy in (4.0, 4.4, 4.8)]
with open("r11_v2_path.csv", "w", newline="", encoding="utf-8") as f:
    w = csv.writer(f)
    w.writerow(["q3_case", "q3_assumed", "fy26_forecast", "implied_q4"])
    w.writerows(path)
    w.writerow(["measured 2026Q1", q1_26, "", "mean of Jan +0.4, Feb +4.3, Mar +5.9 (Mar from the repo note)"])
    w.writerow(["measured 2026Q2", q2_26, "", "mean of Apr +4.4, May +4.0, Jun +8.4 (all snapshotted)"])
c_fy = float(np.mean([r[3] for r in path if r[2] == 4.4]))

# ---------------------------------------------------------------- 3. AR(1) leg, ONE step (A12-17)
PHI, LR = 0.6, 2.25     # LR: TE FY2027 +2.1 is depressed by the June-2027 World Cup comp (-0.8 on that
                        # month); 2.25 is the midpoint of +2.1 as published and +2.4 ex that comp
def ar1(start, phi=PHI, lr=LR):
    return lr + phi * (start - lr)

c_ar_q3 = ar1(5.5)      # from the Q3 average
c_ar_exit = ar1(4.4)    # from the mid-August clean exit rate (w/e 22 Aug; the Labor-Day pair 1.7/16.1 excluded)
c_ar = 0.5 * (c_ar_q3 + c_ar_exit)

# ---------------------------------------------------------------- 4. calendar and comp adjustments
# midterm week 3 Nov 2026: the w/e 8 Nov 2025 printed +6.2% "from a straightforward comparison" with
# the 2024 election week; 2026 gives that back. One week at about -5% over a 13-week quarter = -0.4pp.
ADJ_ELECTION = -0.4
# CR expires 11 Dec 2026. The 2025 shutdown cost ~1.5m room-nights and STR called the disruption
# minimal; at P(shutdown) ~0.3 x -0.7pp on the quarter the expected value is -0.2pp.
ADJ_CR = -0.2
# comp: 4Q25 printed %.2f vs 3Q25 %.2f, so a y/y AR step into Q4 faces a comp easier by that gap. The
# credit applies to the AR leg ONLY (the FY-implied leg already embeds the 4Q25 base: A12-04), i.e.
# half of it on the 50/50 blend. Revision 1 credited +0.8 to the whole blend.
COMP_AR = round(q_measured["2025Q3"] - q_measured["2025Q4"], 2)
ADJ_COMP_BLEND = 0.5 * COMP_AR
ADJ = ADJ_ELECTION + ADJ_CR + ADJ_COMP_BLEND
centre = 0.5 * c_fy + 0.5 * c_ar + ADJ

# ---------------------------------------------------------------- 5. spread
# One-quarter-ahead dispersion, measured on the base-rate quarters: the sd of the quarter-over-quarter
# change in the y/y rate, which is what a one-step AR leaves unexplained.
seq = np.diff(np.array([r[1] for r in sorted(BASE)]))
SD_SEQ = float(np.std(seq, ddof=1))
S_TREND = 1.8          # between the AR-residual scale above and STR's own two-month FY revision (1.6pp
                       # on an FY number, more on a quarter); the quarter has not started
W_SHOCK, C_SHOCK, S_SHOCK = 0.10, 0.8, 1.8      # B15's shock branch, unchanged (A12-10)

def mixture(mean, s1=S_TREND, w=W_SHOCK, c2=C_SHOCK, s2=S_SHOCK):
    c1 = (mean - w * c2) / (1 - w)
    def P(th, lo):
        a = norm.cdf((th - c1) / s1); b = norm.cdf((th - c2) / s2)
        return ((1 - w) * a + w * b) if lo else ((1 - w) * (1 - a) + w * (1 - b))
    p_ge4, p_le1, p_le0 = P(4.0, False), P(1.0, True), P(0.0, True)
    z1, z2 = (4 - c1) / s1, (4 - c2) / s2
    e_ge4 = ((1 - w) * (1 - norm.cdf(z1)) * (c1 + s1 * norm.pdf(z1) / max(1 - norm.cdf(z1), 1e-12))
             + w * (1 - norm.cdf(z2)) * (c2 + s2 * norm.pdf(z2) / max(1 - norm.cdf(z2), 1e-12))) / p_ge4
    y1, y2 = (1 - c1) / s1, (1 - c2) / s2
    e_le1 = ((1 - w) * norm.cdf(y1) * (c1 - s1 * norm.pdf(y1) / max(norm.cdf(y1), 1e-12))
             + w * norm.cdf(y2) * (c2 - s2 * norm.pdf(y2) / max(norm.cdf(y2), 1e-12))) / p_le1
    sd = float(np.sqrt((1 - w) * (s1 ** 2 + c1 ** 2) + w * (s2 ** 2 + c2 ** 2) - mean ** 2))
    return dict(mean=mean, trend_centre=c1, trend_sd=s1, shock_w=w, shock_centre=c2, shock_sd=s2,
                sd=sd, p_ge4=p_ge4, p_le1=p_le1, p_le0=p_le0, e_ge4=e_ge4, e_le1=e_le1)

dec = mixture(centre)
anchor = mixture(c_fy)          # CoStar/TE FY26-implied Q4, no calendar or comp adjustment
WV = dict(decomposition=0.5, anchor=0.3, base_rate=0.2)
final_ge4 = WV["decomposition"] * dec["p_ge4"] + WV["anchor"] * anchor["p_ge4"] + WV["base_rate"] * base_rate_ge4
final_le1 = WV["decomposition"] * dec["p_le1"] + WV["anchor"] * anchor["p_le1"] + WV["base_rate"] * base_rate_le1

# ONE published distribution for R11 and B15. The blend of three views is matched on BOTH tails, not
# just on R11's own: the two free parameters of the trend branch (centre and sd) are solved so that
# P(>= 4) = the blended 0.5/0.3/0.2 upper tail and P(<= 1) = the blended lower tail. Matching only the
# upper tail (revision 1's habit, and what a single re-centring does) would hand B15 a number the blend
# does not imply. The solved sd is the dispersion the disagreement between the three views implies.
def tails(c1, s1):
    p4 = (1 - W_SHOCK) * (1 - norm.cdf((4.0 - c1) / s1)) + W_SHOCK * (1 - norm.cdf((4.0 - C_SHOCK) / S_SHOCK))
    p1 = (1 - W_SHOCK) * norm.cdf((1.0 - c1) / s1) + W_SHOCK * norm.cdf((1.0 - C_SHOCK) / S_SHOCK)
    return p4, p1

from scipy.optimize import fsolve
SOL = fsolve(lambda x: [tails(x[0], x[1])[0] - final_ge4, tails(x[0], x[1])[1] - final_le1],
             [centre, S_TREND])
TREND_C, TREND_SD = float(SOL[0]), float(SOL[1])
joint = mixture((1 - W_SHOCK) * TREND_C + W_SHOCK * C_SHOCK, s1=TREND_SD)

with open("r11_v2_views.csv", "w", newline="", encoding="utf-8") as f:
    w = csv.writer(f)
    w.writerow(["view", "centre_or_mean", "sd", "p_ge_4", "p_le_1", "note"])
    w.writerow(["FY-implied 4Q26 at FY26 +4.4 (mean over the three Q3 cases)", round(c_fy, 3), "", "", "",
                "measured Q1 %.2f, Q2 %.2f; weights %s" % (q1_26, q2_26, list(W))])
    w.writerow(["AR(1) one step from the Q3 average +5.5", round(c_ar_q3, 3), "", "", "", "phi %.1f, long run %.2f" % (PHI, LR)])
    w.writerow(["AR(1) one step from the mid-Aug exit rate +4.4", round(c_ar_exit, 3), "", "", "", ""])
    w.writerow(["calendar + comp adjustment", round(ADJ, 3), "", "", "",
                "election %.1f, CR %.1f, comp credit %+.2f on the AR leg only (=%+.2f on the blend)" % (ADJ_ELECTION, ADJ_CR, COMP_AR, ADJ_COMP_BLEND)])
    w.writerow(["decomposition (weight %.1f)" % WV["decomposition"], round(dec["mean"], 3), round(dec["sd"], 3),
                round(dec["p_ge4"], 4), round(dec["p_le1"], 4), ""])
    w.writerow(["anchor: CoStar/TE FY26 +4.4 implied Q4, unadjusted (weight %.1f)" % WV["anchor"],
                round(anchor["mean"], 3), round(anchor["sd"], 3), round(anchor["p_ge4"], 4), round(anchor["p_le1"], 4), ""])
    w.writerow(["base rate: parsed quarters %s (weight %.1f)" % ([r[0] for r in BASE][0] + "-" + [r[0] for r in BASE][-1], WV["base_rate"]),
                round(float(vals.mean()), 3), round(float(vals.std(ddof=1)), 3), round(base_rate_ge4, 4), round(base_rate_le1, 4),
                "%d of %d >=4, %d of %d <=1; Laplace, averaged with the complete-quarter subset" % (ge4, n, le1, n)])
    w.writerow(["blend %.1f/%.1f/%.1f" % tuple(WV.values()), "", "", round(final_ge4, 4), round(final_le1, 4), ""])
    w.writerow(["PUBLISHED joint object (mixture matched to the blend)", round(joint["mean"], 3), round(joint["sd"], 3),
                round(joint["p_ge4"], 4), round(joint["p_le1"], 4),
                "trend centre %.3f sd %.3f, shock %.2f at N(%.1f, %.1f); both tails matched to the blend" % (TREND_C, TREND_SD, W_SHOCK, C_SHOCK, S_SHOCK)])
    w.writerow(["rev-1 normal N(3.517, 1.676)", 3.517, 1.676, round(1 - norm.cdf((4 - 3.517) / 1.676), 4),
                round(norm.cdf((1 - 3.517) / 1.676), 4), "WITHDRAWN"])
    w.writerow(["audit A12 independent number", 3.0, 1.8, 0.289, 0.16, "N(3.0,1.8) + B15 shock branch"])

# ---------------------------------------------------------------- 6. sensitivity
cases = [("base (published)", centre),
         ("rev-1 comp credit +0.8 on the whole blend restored", centre + 0.8 - ADJ_COMP_BLEND),
         ("no comp credit at all (the audit's route)", centre - ADJ_COMP_BLEND),
         ("no calendar drag (no election, no CR)", centre - ADJ_ELECTION - ADJ_CR),
         ("December shutdown realised (CR row -1.0 instead of -0.2)", centre - 0.8),
         ("election drag -0.7 (the audit's figure)", centre - 0.3),
         ("AR from the Q3 average only", 0.5 * c_fy + 0.5 * c_ar_q3 + ADJ),
         ("AR from the exit rate only", 0.5 * c_fy + 0.5 * c_ar_exit + ADJ),
         ("AR phi 0.8", 0.5 * c_fy + 0.5 * (0.5 * ar1(5.5, 0.8) + 0.5 * ar1(4.4, 0.8)) + ADJ),
         ("AR phi 0.4", 0.5 * c_fy + 0.5 * (0.5 * ar1(5.5, 0.4) + 0.5 * ar1(4.4, 0.4)) + ADJ),
         ("AR long run 2.1 (TE FY27 as published)", 0.5 * c_fy + 0.5 * (0.5 * ar1(5.5, lr=2.1) + 0.5 * ar1(4.4, lr=2.1)) + ADJ),
         ("AR long run 3.0", 0.5 * c_fy + 0.5 * (0.5 * ar1(5.5, lr=3.0) + 0.5 * ar1(4.4, lr=3.0)) + ADJ),
         ("FY26 cut to +4.0 in November", 0.5 * float(np.mean([fy_implied(4.0, v) for v in Q3_CASES.values()])) + 0.5 * c_ar + ADJ),
         ("FY26 raised to +4.8", 0.5 * float(np.mean([fy_implied(4.8, v) for v in Q3_CASES.values()])) + 0.5 * c_ar + ADJ),
         ("Q3 prints +6.5 (September holds +6), FY held", 0.5 * fy_implied(4.4, 6.5) + 0.5 * (0.5 * ar1(6.5) + 0.5 * ar1(6.0)) + ADJ),
         ("Q3 prints +4.5 (September fades to +2)", 0.5 * fy_implied(4.4, 4.5) + 0.5 * (0.5 * ar1(4.5) + 0.5 * ar1(3.0)) + ADJ),
         ("the audit's centre +3.0", 3.0),
         ("joint bull (Q3 6.5, FY 4.8, no drag, phi .8, lr 3.0)", 0.5 * fy_implied(4.8, 6.5) + 0.5 * (0.5 * ar1(6.5, 0.8, 3.0) + 0.5 * ar1(6.0, 0.8, 3.0)) + ADJ_COMP_BLEND),
         ("joint bear (Q3 4.5, FY 4.0, shutdown)", 0.5 * fy_implied(4.0, 4.5) + 0.5 * (0.5 * ar1(4.5) + 0.5 * ar1(3.0)) + ADJ - 0.8)]
with open("r11_v2_sensitivity.csv", "w", newline="", encoding="utf-8") as f:
    w = csv.writer(f)
    w.writerow(["case", "mixture_mean", "p_ge_4", "p_le_1", "blended_final_ge4", "blended_final_le1"])
    for name, c in cases:
        mx = mixture(c)
        w.writerow([name, round(c, 3), round(mx["p_ge4"], 4), round(mx["p_le1"], 4),
                    round(WV["decomposition"] * mx["p_ge4"] + WV["anchor"] * anchor["p_ge4"] + WV["base_rate"] * base_rate_ge4, 4),
                    round(WV["decomposition"] * mx["p_le1"] + WV["anchor"] * anchor["p_le1"] + WV["base_rate"] * base_rate_le1, 4)])
    for name, kw in [("trend sd 1.4", dict(s1=1.4)), ("trend sd 2.2", dict(s1=2.2)),
                     ("shock weight 0.05", dict(w=0.05)), ("shock weight 0.20", dict(w=0.20)),
                     ("shock centre 0.0", dict(c2=0.0))]:
        mx = mixture(centre, **kw)
        w.writerow([name, round(centre, 3), round(mx["p_ge4"], 4), round(mx["p_le1"], 4),
                    round(WV["decomposition"] * mx["p_ge4"] + WV["anchor"] * anchor["p_ge4"] + WV["base_rate"] * base_rate_ge4, 4),
                    round(WV["decomposition"] * mx["p_le1"] + WV["anchor"] * anchor["p_le1"] + WV["base_rate"] * base_rate_le1, 4)])
    for name, wv in [("weights 0.6/0.3/0.1", dict(decomposition=0.6, anchor=0.3, base_rate=0.1)),
                     ("weights 0.4/0.3/0.3", dict(decomposition=0.4, anchor=0.3, base_rate=0.3)),
                     ("base rate dropped (0.6/0.4/0)", dict(decomposition=0.6, anchor=0.4, base_rate=0.0))]:
        w.writerow([name, "", "", "",
                    round(wv["decomposition"] * dec["p_ge4"] + wv["anchor"] * anchor["p_ge4"] + wv["base_rate"] * base_rate_ge4, 4),
                    round(wv["decomposition"] * dec["p_le1"] + wv["anchor"] * anchor["p_le1"] + wv["base_rate"] * base_rate_le1, 4)])

# ---------------------------------------------------------------- 7. the published object
obj = {
 "object": "Adopted 4Q26 US hotel RevPAR y/y distribution (R11 revision 2, 2026-09-17). R11 and B15 read this file; R11's revision-1 normal N(3.517, 1.676) and B15's revision-1 mixture 0.90 N(3.7,1.6) + 0.10 N(0.8,1.8) are withdrawn.",
 "provenance": "questions/risk-q4-us-revpar-strong/datasets/r11_model_v2.py, over us_revpar_monthly_yoy_measured.csv (r11_extract_lodging_monthly.py parses ../sources/lodging_monthly/*.html); audit A12 findings 03/04/10/11/17; response audits/A12-audit-response.md",
 "parametric": {
   "form": "0.90 x N(trend_centre, trend_sd) + 0.10 x N(0.8, 1.8) on 4Q26 US RevPAR y/y (%), resolved as the mean of the three CoStar monthly y/y figures (convention 1); the two trend parameters are solved so that both tails equal the three-view blend",
   "trend_centre": round(joint["trend_centre"], 3), "trend_sd": round(TREND_SD, 3),
   "shock_weight": W_SHOCK, "shock_centre": C_SHOCK, "shock_sd": S_SHOCK,
   "mean": round(joint["mean"], 3), "sd": round(joint["sd"], 3),
   "how_set": ("the decomposition mixture (FY-implied 4Q26 %.2f and the two-start AR leg %.2f averaged, "
               "%+.2f calendar and comp) has its trend centre AND trend sd solved so that BOTH tails equal "
               "the 0.5/0.3/0.2 blend: upper from decomposition %.3f, anchor %.3f, base rate %.3f = %.4f; "
               "lower from %.3f / %.3f / %.3f = %.4f"
               % (c_fy, c_ar, ADJ, dec["p_ge4"], anchor["p_ge4"], base_rate_ge4, final_ge4,
                  dec["p_le1"], anchor["p_le1"], base_rate_le1, final_le1))},
 "events": {"R11_ge_4_0": round(joint["p_ge4"], 4), "B15_le_1_0": round(joint["p_le1"], 4),
            "between_1_and_4": round(1 - joint["p_ge4"] - joint["p_le1"], 4), "le_0": round(joint["p_le0"], 4)},
 "conditional_means_pct": {"given_ge_4": round(joint["e_ge4"], 3), "given_le_1": round(joint["e_le1"], 3)},
 "inputs": {
   "monthly_months_parsed": n_parsed,
   "q1_2026": [round(q1_26, 3), "Jan +0.4, Feb +4.3, Mar +5.9 (March from the repo note, not snapshotted)"],
   "q2_2026": [round(q2_26, 3), "Apr +4.4, May +4.0, Jun +8.4, all snapshotted"],
   "q3_2026_assumed": "5.0-6.0 (Jul +8.2 measured; Aug ~5.5 from the weekly tape; Sep ~3)",
   "fy26_forecast": 4.4, "fy_implied_q4_at_4_4": round(c_fy, 3),
   "ar_from_q3_avg": round(c_ar_q3, 3), "ar_from_exit_rate": round(c_ar_exit, 3),
   "calendar_adj": {"election_week": ADJ_ELECTION, "cr_expiry": ADJ_CR,
                    "comp_credit_ar_leg_only": COMP_AR, "comp_credit_on_blend": ADJ_COMP_BLEND, "total": round(ADJ, 3)},
   "quarterly_base_rate": {"window": "%s-%s, quarters with >=2 saved months" % (BASE[0][0], BASE[-1][0]),
                           "n": n, "ge4": "%d of %d" % (ge4, n), "le1": "%d of %d" % (le1, n),
                           "complete_quarters": "%d of %d >=4, %d of %d <=1" % (ge4_f, nf, le1_f, nf),
                           "p_ge4_used": round(base_rate_ge4, 4), "p_le1_used": round(base_rate_le1, 4)},
   "sd_of_sequential_change_in_yoy": round(SD_SEQ, 3)},
 "must_adopt": ["R11 (this log, revision 2): P(>= +4.0) = %.3f" % joint["p_ge4"],
                "B15 bonus-q4-us-revpar-soft (batch A18): P(<= +1.0) = %.3f (revision 1: 0.10); and its base-rate row '6 of 13 <= +1' must become '%d of %d' on the parsed quarters" % (joint["p_le1"], le1, n),
                "X01 scenario MC"],
 "superseded": {"R11_rev1": 0.38, "B15_rev1": 0.10, "rev1_p_le1_quoted_inside_R11": 0.07,
                "rev1_base_rate_hand_list": "1 of 13 >= +4, 6 of 13 <= +1 (r11_model.py:36)"}}
json.dump(obj, open("r11_v2_joint_object.json", "w", encoding="utf-8"), indent=1)

for fn in ("r11_v2_quarterly_base_rate.csv", "r11_v2_views.csv"):
    print("----", fn)
    print(open(fn, encoding="utf-8").read())
print("Dec-2025 implied %.2f (4Q25 %.2f); comp gap 3Q25->4Q25 %+.2f" % (dec25_implied, q4_25_implied, COMP_AR))
print("sd of sequential change in the quarterly y/y rate: %.2f (n %d)" % (SD_SEQ, len(seq)))
print("centre %.3f -> published P(>=4) %.4f  P(<=1) %.4f  E[x|>=4] %.2f  E[x|<=1] %.2f"
      % (centre, joint["p_ge4"], joint["p_le1"], joint["e_ge4"], joint["e_le1"]))
