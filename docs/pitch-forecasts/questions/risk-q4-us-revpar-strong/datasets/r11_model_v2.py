"""R11 revision 2 (A12 audit response, 2026-09-17): P(CoStar/STR US hotel RevPAR y/y for 4Q26 (Oct-Dec) >= +4.0%), and the joint object with B15 (P(<= +1.0%)).
numpy/scipy only. Writes us_revpar_monthly_yoy_reconstructed.csv, r11_v2_quarterly_base_rate.csv, r11_v2_path.csv, r11_v2_views.csv, r11_v2_sensitivity.csv, r11_v2_joint_object.json.
Revision-1 r11_model.py and its CSVs are left untouched.
Changes vs revision 1 (finding ids in research-log.md section 10):
  A12-03  the base rate is now a dated, saved series: CoStar monthly US releases as reprinted by Lodging Magazine (sources/lodging_monthly/*.html, 25 months
          Jul 2023 - Jul 2026, each with its publication date) plus the FY2023 and FY2025 annual releases; months not saved are left blank, quarters carry n_months
  A12-04  the +0.8 easy-comp credit is removed (the CoStar FY26 forecast already embeds the 4Q25 base); tested in both directions
  A12-17  the AR leg is one step, phi and the long run are hand-set and bracketed; a second AR start from the mid-August clean exit rate is added (missed by the audit)
  A12-10  one object with B15: 0.90 x N(trend) + 0.10 x N(0.8, 1.8) shock branch (B15's form), both tails published from it
  A12-11  anchor re-cited to the saved 10 Aug 2026 forecast article and the repo note; Q2 2026 actual months replace the rev-1 assumed 4.5-6.0 grid
"""
import numpy as np, csv, os, json
from scipy.stats import norm
os.chdir(os.path.dirname(os.path.abspath(__file__)))
# ---- 1. monthly US RevPAR y/y (%), CoStar monthly releases (Lodging Magazine reprints, saved under sources/lodging_monthly/; publication date = Lodging post date)
monthly = [  # month, revpar_yoy, published, snapshot file
 ("2023-07", 0.8, "2023-08-22", "costar-u-s-hotel-industry-showed-mixed-month-over-month-performance-in-july.html"),
 ("2023-08", 1.5, "2023-09-21", "costar-august-2023-u-s-hotel-performance-improved-year-over-year.html"),
 ("2023-11", 2.4, "2023-12-26", "costar-u-s-hotel-industry-reports-lower-performance-from-november.html"),
 ("2024-01", 0.9, "2024-02-22", "u-s-hotel-performance-lowered-in-january-2024.html"),
 ("2024-04", 2.0, "2024-05-22", "costar-u-s-hotel-performance-showed-mixed-results-in-april-2024.html"),
 ("2024-05", 4.0, "2024-06-20", "costar-may-u-s-hotel-performance-improves-from-previous-month.html"),
 ("2024-06", 1.5, "2024-07-24", "costar-u-s-hotel-industry-improves-monthly-performance.html"),
 ("2024-07", 0.0, "2024-08-26", "costar-u-s-hotel-performance-remained-mostly-flat-in-july.html"),
 ("2024-08", 3.9, "2024-09-24", "costar-u-s-hotel-industry-showed-mixed-performance-during-august.html"),
 ("2024-09", -1.3, "2024-10-21", "costar-september-reports-mixed-u-s-hotel-performance-results.html"),
 ("2024-12", 4.4, "2025-01-27", "costar-december-2024-shows-mixed-performance-results.html"),
 ("2025-01", 4.5, "2025-02-25", "costar-u-s-hotel-industry-reports-lower-performance-from-january.html"),
 ("2025-02", 1.9, "2025-03-21", "costar-february-2025-reports-mixed-u-s-hotel-industry-performance-results.html"),
 ("2025-03", 0.8, "2025-04-24", "costar-mixed-u-s-hotel-industry-performance-results-in-march.html"),
 ("2025-04", -0.1, "2025-05-21", "costar-continues-to-report-mixed-monthly-performance-results.html"),
 ("2025-05", 0.1, "2025-06-20", "costar-steady-u-s-hotel-industry-performance-results-in-may.html"),
 ("2025-06", -1.2, "2025-07-22", "costar-reports-mixed-u-s-hotel-industry-performance-results-in-june.html"),
 ("2025-07", -1.1, "2025-08-28", "costar-reports-negative-u-s-hotel-industry-performance-results-in-july.html"),
 ("2025-08", -1.0, "2025-09-19", "costar-reports-mixed-u-s-hotel-industry-performance-results-in-august.html"),
 ("2025-09", -2.1, "2025-10-21", "costar-reports-negative-u-s-hotel-industry-performance-results-in-september.html"),
 ("2025-10", -0.9, "2025-11-19", "costar-reports-mixed-u-s-hotel-industry-performance-results-in-october.html"),
 ("2025-11", -2.3, "2025-12-22", "costar-reports-mixed-u-s-hotel-industry-performance-results-in-november.html"),
 ("2026-01", 0.4, "2026-02-26", "costar-reports-mostly-positive-u-s-hotel-industry-performance-results-in-january.html"),
 ("2026-02", 4.3, "2026-04-01", "costar-reports-positive-u-s-hotel-industry-performance-results-in-february.html"),
 ("2026-03", 5.9, "2026-04 (repo note 06_consumer-choice section 1.2; STR release not saved)", "UNSAVED: research/notes/overnight/06_consumer-choice-and-willingness-to-pay.md"),
 ("2026-04", 4.4, "2026-06-09", "costar-reports-positive-u-s-hotel-industry-performance-results-in-april.html"),
 ("2026-05", 4.0, "2026-06-24", "costar-reports-positive-u-s-hotel-industry-performance-results-in-may.html"),
 ("2026-06", 8.4, "2026-07-27", "costar-reports-positive-u-s-hotel-industry-performance-results-in-june.html"),
 ("2026-07", 8.2, "2026-08-26", "costar-reports-positive-u-s-hotel-industry-performance-results-in-july.html")]
annual = {"2023": (4.9, "lodging_costar_fy2023_annual.html, published 2024-01-18"), "2025": (-0.3, "hoteldive_fy2025_us_hotel_performance_*.html, published 2026-01-22")}
with open('us_revpar_monthly_yoy_reconstructed.csv', 'w', newline='') as f:
    w = csv.writer(f); w.writerow(['month', 'revpar_yoy_pct', 'published', 'snapshot']); w.writerows(monthly)
    for y, (v, s) in annual.items(): w.writerow([f"FY{y}", v, s.split(', published ')[1], s.split(',')[0]])
# ---- 2. quarterly means of the saved months (n_months shown); 2023Q1-Q2 are the recovery quarters and are not reconstructed
q = {}
for m, v, _, _ in monthly:
    y, mo = m.split('-'); k = f"{y}Q{(int(mo) - 1) // 3 + 1}"; q.setdefault(k, []).append(v)
# 2025Q4: Dec 2025 not saved; FY2025 -0.3 with Q1 +2.4, Q2 -0.4, Q3 -1.4 (equal weights) implies Q4 about -1.8 -> Dec about -2.2; carried as an annual-implied value
q_rows = []
for k in sorted(q):
    vals = q[k]; note = ''
    if k == '2025Q4': vals = vals + [-2.2]; note = 'Dec 2025 implied from FY2025 -0.3 (annual release) and the three reconstructed quarters'
    q_rows.append((k, round(float(np.mean(vals)), 2), len(q[k]), note))
q_rows = [(k, v, nm, (note + '; ' if note else '') + ('n = 1: December 2024 alone, boosted by the New Year calendar shift; the quarter is probably +2.5 to +3 (FY2024 about +1.8 per CoStar, annual release not saved): counted as uncertain' if k == '2024Q4' else 'n = 1: January 2024 alone (Feb/Mar 2024 not saved; Easter shift)' if k == '2024Q1' else 'current quarter, July only: excluded from the base rate' if k == '2026Q3' else '')) for k, v, nm, note in q_rows]
with open('r11_v2_quarterly_base_rate.csv', 'w', newline='') as f:
    w = csv.writer(f); w.writerow(['quarter', 'revpar_yoy_mean_pct', 'n_months_saved', 'note']); w.writerows(q_rows)
    br = [r for r in q_rows if r[0] <= '2026Q2']
    vals = np.array([r[1] for r in br]); n = len(vals); ge4 = int((vals >= 4).sum()); le1 = int((vals <= 1).sum())
    w.writerow(['quarters 2023Q3-2026Q2 reconstructed', n, '', 'all three months saved for 2024Q2, 2024Q3, 2025Q1, 2025Q2, 2025Q3, 2026Q1, 2026Q2; the rest are 1-2 months'])
    w.writerow(['share >= +4 (as reconstructed)', round(ge4 / n, 3), f'{ge4} of {n}', f'Laplace {(ge4 + 1) / (n + 2):.3f}; 2024Q4 (n 1) is the uncertain count'])
    w.writerow(['share >= +4 (2024Q4 counted below 4)', round((ge4 - 1) / n, 3), f'{ge4 - 1} of {n}', f'Laplace {ge4 / (n + 2):.3f}'])
    w.writerow(['share <= +1 (B15 mirror, as reconstructed)', round(le1 / n, 3), f'{le1} of {n}', f'Laplace {(le1 + 1) / (n + 2):.3f}; 2024Q1 (n 1) is the uncertain count; rev-1 B15 claimed 6 of 13'])
    w.writerow(['rev-1 hand list (r11_model.py:36) 2023Q2-2026Q2', '', '1 of 13 >= 4; 6 of 13 <= 1', 'withdrawn (A12-03)'])
base_rate_ge4 = 0.5 * ((ge4 + 1) / (n + 2) + ge4 / (n + 2)); base_rate_le1 = 0.5 * ((le1 + 1) / (n + 2) + le1 / (n + 2))
# ---- 3. FY-implied 4Q26 from the CoStar/TE FY2026 forecast (+4.4, 7-10 Aug 2026), with the ACTUAL Q1 and Q2 months
w4 = np.array([0.23, 0.26, 0.27, 0.24])   # RevPAR-weighted quarter weights (Q3 highest RevPAR, Q4 lowest)
q1 = float(np.mean([0.4, 4.3, 5.9])); q2 = float(np.mean([4.4, 4.0, 8.4]))   # 3.53, 5.60
q3_cases = {'Q3 5.0 (Jul 8.2, Aug 5.0, Sep 2)': 5.0, 'Q3 5.5 (Jul 8.2, Aug 5.5, Sep 3)': 5.5, 'Q3 6.0 (Jul 8.2, Aug 6.0, Sep 4)': 6.0}
rows = []
for lbl, q3v in q3_cases.items():
    for fy in (4.0, 4.4, 4.8):
        rows.append((lbl, q3v, fy, round((fy - w4[0] * q1 - w4[1] * q2 - w4[2] * q3v) / w4[3], 2)))
with open('r11_v2_path.csv', 'w', newline='') as f:
    w = csv.writer(f); w.writerow(['q3_case', 'q3_assumed', 'fy26_forecast', 'implied_q4']); w.writerows(rows)
implied_44 = np.array([r[3] for r in rows if r[2] == 4.4]); c_fy = float(implied_44.mean())          # ~2.7 at FY 4.4
# ---- 4. AR(1) leg, one step (A12-17). Two starts: the Q3 average (5.5) and the mid-August clean exit rate (+4.4, w/e 22 Aug; the Labor-Day pair 1.7 / 16.1 is excluded)
def ar1(start, phi=0.6, lr=2.25): return lr + phi * (start - lr)   # lr 2.25 = mean of TE FY27 +2.1 (depressed by the June-2027 World Cup comp) and +2.4
c_ar_q3 = ar1(5.5); c_ar_exit = ar1(4.4); c_ar = 0.5 * (c_ar_q3 + c_ar_exit)
# ---- 5. calendar adjustments (no comp credit: A12-04): midterm election week vs the Nov-2025 easy comp -0.5; CR expiry 11 Dec shutdown risk -0.2 (expected value)
adj = -0.5 - 0.2
centre = 0.5 * c_fy + 0.5 * c_ar + adj
# ---- 6. one object with B15: trend N(c1, 1.7) at 0.90 + shock N(0.8, 1.8) at 0.10, with the mixture mean set to the centre
W_SHOCK, C_SHOCK, S_SHOCK, S_TREND = 0.10, 0.8, 1.8, 1.7
def mixture(mean, s1=S_TREND, w=W_SHOCK, c2=C_SHOCK, s2=S_SHOCK):
    c1 = (mean - w * c2) / (1 - w)
    p_ge4 = (1 - w) * (1 - norm.cdf((4 - c1) / s1)) + w * (1 - norm.cdf((4 - c2) / s2))
    p_le1 = (1 - w) * norm.cdf((1 - c1) / s1) + w * norm.cdf((1 - c2) / s2)
    p_le0 = (1 - w) * norm.cdf((0 - c1) / s1) + w * norm.cdf((0 - c2) / s2)
    # conditional means by simulation-free formulas (truncated normal per component)
    z1 = (4 - c1) / s1; z2 = (4 - c2) / s2
    e_ge4 = ((1 - w) * (1 - norm.cdf(z1)) * (c1 + s1 * norm.pdf(z1) / max(1 - norm.cdf(z1), 1e-12)) + w * (1 - norm.cdf(z2)) * (c2 + s2 * norm.pdf(z2) / max(1 - norm.cdf(z2), 1e-12))) / p_ge4
    y1 = (1 - c1) / s1; y2 = (1 - c2) / s2
    e_le1 = ((1 - w) * norm.cdf(y1) * (c1 - s1 * norm.pdf(y1) / max(norm.cdf(y1), 1e-12)) + w * norm.cdf(y2) * (c2 - s2 * norm.pdf(y2) / max(norm.cdf(y2), 1e-12))) / p_le1
    sd = float(np.sqrt((1 - w) * (s1 ** 2 + c1 ** 2) + w * (s2 ** 2 + c2 ** 2) - mean ** 2))
    return dict(mean=mean, trend_centre=c1, trend_sd=s1, shock_w=w, shock_centre=c2, shock_sd=s2, sd=sd, p_ge4=p_ge4, p_le1=p_le1, p_le0=p_le0, e_ge4=e_ge4, e_le1=e_le1)
dec = mixture(centre)
anchor = mixture(c_fy)                       # CoStar/TE FY26-implied Q4, no calendar adjustment, same spread
views = {'decomposition (FY-implied + AR two-start, -0.7 calendar, no comp credit)': dec, 'anchor: CoStar/TE FY26 +4.4 implied Q4, unadjusted': anchor,
         'base rate: reconstructed quarters 2023Q3-2026Q2 (Laplace)': dict(p_ge4=base_rate_ge4, p_le1=base_rate_le1, mean=float(vals.mean()), sd=float(vals.std(ddof=1)))}
WV = {'decomposition': 0.5, 'anchor': 0.3, 'base_rate': 0.2}
final_ge4 = WV['decomposition'] * dec['p_ge4'] + WV['anchor'] * anchor['p_ge4'] + WV['base_rate'] * base_rate_ge4
final_le1 = WV['decomposition'] * dec['p_le1'] + WV['anchor'] * anchor['p_le1'] + WV['base_rate'] * base_rate_le1
# published joint object: the decomposition mixture re-centred so that its P(>=4) equals the blended final (one distribution for R11 and B15)
lo, hi = -2.0, 6.0
for _ in range(60):
    mid = (lo + hi) / 2
    if mixture(mid)['p_ge4'] > final_ge4: hi = mid
    else: lo = mid
joint = mixture((lo + hi) / 2)
with open('r11_v2_views.csv', 'w', newline='') as f:
    w = csv.writer(f); w.writerow(['view', 'centre_or_mean', 'sd', 'p_ge_4', 'p_le_1'])
    w.writerow(['FY-implied Q4 at FY 4.4 (mean over Q3 cases)', round(c_fy, 3), '', '', ''])
    w.writerow(['AR(1) one step from Q3 avg 5.5 (phi .6, lr 2.25)', round(c_ar_q3, 3), '', '', ''])
    w.writerow(['AR(1) one step from mid-Aug exit 4.4', round(c_ar_exit, 3), '', '', ''])
    w.writerow(['calendar adjustment (election -0.5, CR -0.2, comp credit 0)', adj, '', '', ''])
    for k, v in views.items(): w.writerow([k, round(v['mean'], 3), round(v['sd'], 3), round(v['p_ge4'], 4), round(v['p_le1'], 4)])
    w.writerow(['blend 0.5/0.3/0.2', '', '', round(final_ge4, 4), round(final_le1, 4)])
    w.writerow(['published joint object (mixture matched to the blend)', round(joint['mean'], 3), round(joint['sd'], 3), round(joint['p_ge4'], 4), round(joint['p_le1'], 4)])
    w.writerow(['rev-1 normal N(3.517, 1.676)', 3.517, 1.676, round(1 - norm.cdf((4 - 3.517) / 1.676), 4), round(norm.cdf((1 - 3.517) / 1.676), 4)])
    w.writerow(['rev-1 with the comp credit removed (audit A12-04)', 2.717, 1.676, round(1 - norm.cdf((4 - 2.717) / 1.676), 4), round(norm.cdf((1 - 2.717) / 1.676), 4)])
sens = [('base', centre)]
def fyq4(fy, q3v): return (fy - w4[0] * q1 - w4[1] * q2 - w4[2] * q3v) / w4[3]
for name, c in [('comp credit +0.8 restored (rev 1)', centre + 0.8), ('comp credit +0.4 on the AR leg only', centre + 0.2), ('no calendar drag', centre + 0.7),
                ('December shutdown realised (adj -1.5)', centre - 0.8), ('AR from Q3 average only (no exit-rate start)', 0.5 * c_fy + 0.5 * c_ar_q3 + adj),
                ('AR from the exit rate only', 0.5 * c_fy + 0.5 * c_ar_exit + adj), ('AR phi 0.8', 0.5 * c_fy + 0.5 * (0.5 * ar1(5.5, 0.8) + 0.5 * ar1(4.4, 0.8)) + adj),
                ('AR phi 0.4', 0.5 * c_fy + 0.5 * (0.5 * ar1(5.5, 0.4) + 0.5 * ar1(4.4, 0.4)) + adj), ('AR long run 2.0 (TE FY27 as is)', 0.5 * c_fy + 0.5 * (0.5 * ar1(5.5, lr=2.0) + 0.5 * ar1(4.4, lr=2.0)) + adj),
                ('AR long run 3.0', 0.5 * c_fy + 0.5 * (0.5 * ar1(5.5, lr=3.0) + 0.5 * ar1(4.4, lr=3.0)) + adj),
                ('FY26 forecast cut to 4.0 in November', 0.5 * float(np.mean([fyq4(4.0, v) for v in q3_cases.values()])) + 0.5 * c_ar + adj),
                ('FY26 forecast raised to 4.8', 0.5 * float(np.mean([fyq4(4.8, v) for v in q3_cases.values()])) + 0.5 * c_ar + adj),
                ('Q3 prints 6.5 (Sep holds +6), FY held', 0.5 * fyq4(4.4, 6.5) + 0.5 * (0.5 * ar1(6.5) + 0.5 * ar1(6.0)) + adj),
                ('Q3 prints 4.5 (Sep fades to +2)', 0.5 * fyq4(4.4, 4.5) + 0.5 * (0.5 * ar1(4.5) + 0.5 * ar1(3.0)) + adj),
                ("audit's centre 3.0", 3.0), ('joint bull (Q3 6.5, FY 4.8, no drag, phi .8, lr 3)', 0.5 * fyq4(4.8, 6.5) + 0.5 * (0.5 * ar1(6.5, 0.8, 3.0) + 0.5 * ar1(6.0, 0.8, 3.0))),
                ('joint bear (Q3 4.5, FY 4.0, shutdown)', 0.5 * fyq4(4.0, 4.5) + 0.5 * (0.5 * ar1(4.5) + 0.5 * ar1(3.0)) - 1.5)]:
    sens.append((name, c))
with open('r11_v2_sensitivity.csv', 'w', newline='') as f:
    w = csv.writer(f); w.writerow(['case', 'mixture_mean', 'p_ge_4', 'p_le_1', 'final_ge4_if_decomp_moves', 'final_le1_if_decomp_moves'])
    for name, c in sens:
        mx = mixture(c); w.writerow([name, round(c, 3), round(mx['p_ge4'], 4), round(mx['p_le1'], 4),
                                     round(WV['decomposition'] * mx['p_ge4'] + WV['anchor'] * anchor['p_ge4'] + WV['base_rate'] * base_rate_ge4, 4),
                                     round(WV['decomposition'] * mx['p_le1'] + WV['anchor'] * anchor['p_le1'] + WV['base_rate'] * base_rate_le1, 4)])
    for name, kw in [('trend sd 1.2', dict(s1=1.2)), ('trend sd 2.2', dict(s1=2.2)), ('shock weight 0.05', dict(w=0.05)), ('shock weight 0.20', dict(w=0.20)), ('shock centre 0.0', dict(c2=0.0))]:
        mx = mixture(centre, **kw); w.writerow([name, round(centre, 3), round(mx['p_ge4'], 4), round(mx['p_le1'], 4),
                                                round(WV['decomposition'] * mx['p_ge4'] + WV['anchor'] * anchor['p_ge4'] + WV['base_rate'] * base_rate_ge4, 4),
                                                round(WV['decomposition'] * mx['p_le1'] + WV['anchor'] * anchor['p_le1'] + WV['base_rate'] * base_rate_le1, 4)])
obj = {"object": "Adopted 4Q26 US hotel RevPAR y/y distribution (R11 revision 2, 2026-09-17). R11 and B15 read this file; the rev-1 normal N(3.517, 1.676) and B15's rev-1 mixture (0.9 N(3.7,1.6) + 0.1 N(0.8,1.8)) are withdrawn.",
       "provenance": "questions/risk-q4-us-revpar-strong/datasets/r11_model_v2.py; audit A12 findings 03/04/10/11/17; response audits/A12-audit-response.md",
       "parametric": {"form": "0.90 x N(trend_centre, 1.7) + 0.10 x N(0.8, 1.8) on 4Q26 US RevPAR y/y (%), the mean of the three CoStar monthly y/y figures (convention 1)",
                      "trend_centre": round(joint['trend_centre'], 3), "trend_sd": S_TREND, "shock_weight": W_SHOCK, "shock_centre": C_SHOCK, "shock_sd": S_SHOCK,
                      "mean": round(joint['mean'], 3), "sd": round(joint['sd'], 3),
                      "how_set": "the decomposition mixture (FY-implied 4Q26 %.2f and the two-start AR leg %.2f averaged, -0.7 calendar, no comp credit) re-centred so that P(>= 4) equals the 0.5/0.3/0.2 blend of decomposition %.3f, anchor %.3f and base rate %.3f" % (c_fy, c_ar, dec['p_ge4'], anchor['p_ge4'], base_rate_ge4)},
       "events": {"R11_ge_4_0": round(joint['p_ge4'], 4), "B15_le_1_0": round(joint['p_le1'], 4), "between_1_and_4": round(1 - joint['p_ge4'] - joint['p_le1'], 4), "le_0": round(joint['p_le0'], 4)},
       "conditional_means_pct": {"given_ge_4": round(joint['e_ge4'], 3), "given_le_1": round(joint['e_le1'], 3)},
       "inputs": {"q1_2026_actual_months": [0.4, 4.3, 5.9], "q2_2026_actual_months": [4.4, 4.0, 8.4], "q3_2026_assumed": "5.0-6.0 (Jul 8.2 actual; Aug ~5.5 from the weekly tape; Sep ~3)", "fy26_forecast": 4.4,
                  "fy_implied_q4_at_4_4": round(c_fy, 3), "ar_from_q3_avg": round(c_ar_q3, 3), "ar_from_exit_rate": round(c_ar_exit, 3), "calendar_adj": adj, "comp_credit": 0.0,
                  "base_rate_quarters": [list(r[:3]) for r in q_rows], "base_rate_ge4_laplace": round(base_rate_ge4, 4), "base_rate_le1_laplace": round(base_rate_le1, 4)},
       "must_adopt": ["R11 (this log, revision 2)", "B15 bonus-q4-us-revpar-soft (batch A18): P(<= 1.0) = %.3f (rev 1: 0.10); base-rate row '6 of 13' -> '%d of %d'" % (joint['p_le1'], le1, n)],
       "superseded": {"R11_rev1": 0.38, "B15_rev1": 0.10, "rev1_p_le1_in_R11_log": 0.07}}
json.dump(obj, open('r11_v2_joint_object.json', 'w'), indent=1)
for fn in ['r11_v2_quarterly_base_rate.csv', 'r11_v2_views.csv', 'r11_v2_sensitivity.csv']: print(open(fn).read())
print(json.dumps(obj['events']), json.dumps(obj['conditional_means_pct']), 'trend centre', round(joint['trend_centre'], 3), 'mean', round(joint['mean'], 3))
