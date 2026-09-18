"""Revision-2 partial recode of the metric-persistence matrix (audit A04-02/A04-03).
Run from repo root: py -3.13 docs/pitch-forecasts/questions/bundle-attribution-quantified/datasets/metric_persistence_matrix_v2_recode.py
Reads the revision-1 matrix (left untouched), applies the cell corrections verified against the letters and call
mirrors on 2026-09-17, writes *_v2 matrix, gap ledger and a rates table with both windows (W1 target>=1Q23, W2 target>=1Q24).
Cells not listed in RECODES remain as coded in revision 1 and are NOT certified by this script."""
from pathlib import Path
import pandas as pd
HERE = Path(__file__).resolve().parent
m = pd.read_csv(HERE / "metric_persistence_matrix_4Q20-2Q26.csv").set_index("metric")
RECODES = {
    # (metric, quarter): (new_code, reason)
    ("cancellation rate %", "1Q25"): ("--", "only an analyst question (R. Clarke) mentions cancellation rates; no management figure"),
    ("cancellation rate %", "3Q25"): ("--", "analyst question asks about cancellation rates; management answer has no rate (D006)"),
    ("Middle East conflict (pts)", "2Q26"): ("--", "call says impact 'less than we had anticipated'; qualitative, no points"),
    # Guest Favorites: cumulative nights booked at GF listings, stated in the letter each quarter below (verified 2026-09-17)
    ("Guest Favorites share", "1Q24"): ("L-", "1Q24 letter: 'over 100 million nights booked at Guest Favorite listings since launch'"),
    ("Guest Favorites share", "1Q25"): ("L-", "1Q25 letter: 'over 350 million nights booked at Guest Favorite listings'"),
    ("Guest Favorites share", "2Q25"): ("L-", "2Q25 letter: 'over 400 million nights'"),
    ("Guest Favorites share", "3Q25"): ("L-", "3Q25 letter: 'nearly 500 million nights'"),
    ("Guest Favorites share", "4Q25"): ("L-", "4Q25 letter: 'over 500 million nights' (rev-1 coded call-only)"),
}
v2 = m.copy()
for (met, q), (code, why) in RECODES.items():
    v2.loc[met, q] = code
v2.index.name = "metric"
v2.to_csv(HERE / "metric_persistence_matrix_v2_4Q20-2Q26.csv")
# cumulative metric label fix is descriptive only; the row name is kept so the two matrices align
quarters = list(v2.columns)
def rates(mat):
    rows = []
    for label, start in [("All", 0), ("W1 target>=1Q23", quarters.index("1Q23")), ("W2 target>=1Q24", quarters.index("1Q24"))]:
        k = n = g = h = 0
        for vals in mat.ne("--").to_numpy().tolist():
            for t in range(max(1, start), len(vals)):
                if vals[t-1]:
                    n += 1; k += int(vals[t])
            for t in range(max(2, start), len(vals)):
                if vals[t-2] and not vals[t-1]:
                    h += 1; g += int(vals[t])
        rows.append(dict(window=label, continued=k, eligible=n, continuation=round(k/n, 4), returned=g, gaps=h, return_rate=round(g/h, 4)))
    return pd.DataFrame(rows)
out = []
for name, mat in [("rev1_as_coded", m), ("v2_partial_recode", v2), ("v2_excl_GF_cancel_ME_sensitivity", v2.drop(index=["Guest Favorites share", "cancellation rate %", "Middle East conflict (pts)"]))]:
    r = rates(mat); r.insert(0, "matrix", name); out.append(r)
rates_df = pd.concat(out, ignore_index=True)
rates_df.to_csv(HERE / "persistence_rates_v2.csv", index=False)
# gap ledger v2
gaps = []
for met, vals in v2.ne("--").iterrows():
    v = vals.tolist()
    for t in range(2, len(v)):
        if v[t-2] and not v[t-1]:
            gaps.append(dict(metric=met, last_disclosed=quarters[t-2], gap_quarter=quarters[t-1], next_quarter=quarters[t], returned_next_quarter=bool(v[t])))
g = pd.DataFrame(gaps); g.to_csv(HERE / "metric_gap_events_v2.csv", index=False)
# metric-level counts (each metric = one management decision series)
ml = []
for met, vals in v2.ne("--").iterrows():
    v = vals.tolist(); n = k = 0
    for t in range(1, len(v)):
        if v[t-1]: n += 1; k += int(v[t])
    ml.append(dict(metric=met, eligible=n, continued=k))
pd.DataFrame(ml).to_csv(HERE / "persistence_by_metric_v2.csv", index=False)
print(rates_df.to_string(index=False)); print(); print(g.to_string(index=False)); print(); print(pd.DataFrame(ml).to_string(index=False))
print("GAP RETURNS excluding the retrospectively-selected five:", int(g[~g.metric.isin(['cross-border share %','long-term stays share %','urban/high-density share %','active listings growth %','1BR vs hotel price comparison'])].returned_next_quarter.sum()), "/", int((~g.metric.isin(['cross-border share %','long-term stays share %','urban/high-density share %','active listings growth %','1BR vs hotel price comparison'])).sum()))
