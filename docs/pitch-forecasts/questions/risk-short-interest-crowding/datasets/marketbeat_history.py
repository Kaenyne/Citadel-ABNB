"""Extend the short-interest history to 2022 from the MarketBeat page's embedded dollar-value series
(short interest x price), converted to shares with the repo's daily closes and to % of shares outstanding
with the capital-return share counts. Writes si_history_2022_2026.csv."""
import re, pathlib, pandas as pd, numpy as np
ROOT = pathlib.Path(__file__).resolve().parents[5]; HERE = pathlib.Path(__file__).resolve().parent
html = (HERE.parent/"sources/marketbeat_short_interest_20260917.html").read_text(encoding="utf-8", errors="ignore")
pairs = re.findall(r"(\d{2}/\d{2}/\d{4}),\d{2}/\d{2}/\d{4},MONTH,(\d+),\$", html)
mb = pd.DataFrame(pairs, columns=["date","usd"]); mb["date"]=pd.to_datetime(mb.date); mb["usd"]=mb.usd.astype(float)
mb = mb.drop_duplicates("date").sort_values("date")
px = pd.read_csv(ROOT/"data/processed/abnb_daily_close.csv"); px.columns=[c.lower() for c in px.columns]
dcol=[c for c in px.columns if "date" in c][0]; ccol=[c for c in px.columns if "close" in c][0]
px[dcol]=pd.to_datetime(px[dcol]); px=px.sort_values(dcol)
mb = pd.merge_asof(mb, px[[dcol,ccol]].rename(columns={dcol:"date",ccol:"close"}), on="date", direction="backward")
mb["shares_m_est"] = mb.usd/mb.close/1e6
# check against the known series (Feb 2023+)
known = pd.read_csv(ROOT/"data/processed/overnight/09_positioning_short_interest.csv"); known["settlement_date"]=pd.to_datetime(known.settlement_date)
m = mb.merge(known[["settlement_date","short_interest_shares","shares_out_m","si_pct_shares"]], left_on="date", right_on="settlement_date", how="left")
m["ratio_est_to_known"] = m.shares_m_est/(m.short_interest_shares/1e6)
print("calibration (est/known) on overlapping settlements:", m.ratio_est_to_known.describe().round(3).to_dict())
# shares outstanding for 2022: use the file's earliest count (636m) for 2022 (basic shares were ~640m; 2022 buyback started Aug 2022)
m["shares_out_m"] = m.shares_out_m.fillna(640.0)
m["si_pct_est"] = m.shares_m_est/m.shares_out_m*100
m["si_pct_used"] = m.si_pct_shares.fillna(m.si_pct_est)
out = m[["date","usd","close","shares_m_est","short_interest_shares","shares_out_m","si_pct_est","si_pct_shares","si_pct_used"]]
out.to_csv(HERE/"si_history_2022_2026.csv", index=False)
print(out[out.date<"2023-03-01"].round(2).to_string())
x = out.si_pct_used.values; print("\n2022 max %.2f, 2022 mean %.2f; overall max %.2f; n %d" % (out[out.date<"2023"].si_pct_used.max(), out[out.date<"2023"].si_pct_used.mean(), x.max(), len(x)))
W=8; mx=[x[i:i+W].max() for i in range(len(x)-W+1)]; prev=[x[i-1] if i>0 else np.nan for i in range(len(x)-W+1)]
w=pd.DataFrame({"prev":prev,"max":mx}); print("windows n %d P(max>=5) %.3f P(max>=4) %.3f; start<2.5: n %d P(max>=5) %.3f P(max>=4) %.3f max %.2f" % (len(w),(w["max"]>=5).mean(),(w["max"]>=4).mean(),(w.prev<2.5).sum(),(w[w.prev<2.5]["max"]>=5).mean(),(w[w.prev<2.5]["max"]>=4).mean(),w[w.prev<2.5]["max"].max()))
