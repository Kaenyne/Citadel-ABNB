"""A07-12: measure the actual 15 Dec -> pre-release window (close on 15 Dec, or the last session before it, to the close
of the session before the Q4 reaction day) for every Q4 print, raw and QQQ-excess, separated from the earnings day.
Replaces the calendar-month Jan + Feb seasonal (which contained the reaction day and the post-release sessions).
Writes dec_to_prerelease_window.csv. Run from the repo root:
  py -3.13 docs/pitch-forecasts/questions/close-12feb-2027/datasets/dec_to_prerelease_window.py
"""
import json, pathlib
import pandas as pd
here = pathlib.Path(__file__).resolve().parent
root = here.parents[4]
px = pd.read_csv(root / "data/processed/overnight/09_prices_daily.csv", parse_dates=["Date"]).set_index("Date").dropna(subset=["ABNB"])
rx = pd.read_csv(root / "data/processed/abnb_earnings_reactions.csv", parse_dates=["reaction_date"])
rows = []
for _, e in rx[rx.quarter.str.endswith("Q4")].iterrows():
    i = px.index.get_loc(e.reaction_date); pre = px.index[i - 1]
    d15 = px.index[px.index.get_indexer([pd.Timestamp(f"{e.reaction_date.year - 1}-12-15")], method="pad")[0]]
    a, b = px.loc[d15], px.loc[pre]
    rows.append(dict(quarter=e.quarter, dec15_session=d15.date(), pre_release_session=pre.date(), sessions=int(px.index.get_loc(pre) - px.index.get_loc(d15)),
                     abnb_pct=100 * (b.ABNB / a.ABNB - 1), qqq_pct=100 * (b.QQQ / a.QQQ - 1), excess_pct=100 * (b.ABNB / a.ABNB - b.QQQ / a.QQQ),
                     reaction_day_raw_pct=e.abnb_1d_pct))
o = pd.DataFrame(rows); o.to_csv(here / "dec_to_prerelease_window.csv", index=False)
ex = o[o.quarter != "2020Q4"]
summary = {"all_n6": dict(mean_excess=o.excess_pct.mean(), median_excess=o.excess_pct.median(), sd_excess=o.excess_pct.std(), positive=int((o.excess_pct > 0).sum()), mean_raw=o.abnb_pct.mean()),
           "ex_2020Q4_n5": dict(mean_excess=ex.excess_pct.mean(), median_excess=ex.excess_pct.median(), sd_excess=ex.excess_pct.std(), positive=int((ex.excess_pct > 0).sum()), mean_raw=ex.abnb_pct.mean()),
           "note": "2020Q4 window starts five sessions after the IPO (Dec 2020, +46% raw); excluded from the carried figure"}
print(o.round(2).to_string()); print(json.dumps(summary, indent=1, default=float))
json.dump(summary, open(here / "dec_to_prerelease_window.json", "w"), indent=1, default=float)
