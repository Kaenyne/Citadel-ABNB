"""Austin daily active short-term-rental licence counts -> insights + figures.

Source: City of Austin Development Services, Socrata dataset mydx-h5dy
("Active Short Term Rental Counts"). One row per process_date x str_type x
council_district; `count` = active licences. Daily process dates from
2025-02-28 (one date), then 2025-03-13 onward (527 dates through 2026-09-05).

Inputs (data/processed/):
  austin_active_str_daily.csv              date, total active licences
  austin_str_by_type_monthly_raw.csv       sum of daily counts per month x type
  austin_str_by_district_type_snapshots.csv 2025-03-13 vs 2026-09-05 by district x type

SoQL used to pull them (paste into a browser, no auth needed):
  https://data.austintexas.gov/resource/mydx-h5dy.json?$select=process_date,sum(count) as total&$group=process_date&$order=process_date&$limit=1000
  https://data.austintexas.gov/resource/mydx-h5dy.json?$select=date_trunc_ym(process_date) as month,str_type,sum(count) as total&$group=month,str_type&$order=month,str_type
  https://data.austintexas.gov/resource/mydx-h5dy.json?$select=council_district,str_type,sum(count) as total&$where=process_date='2026-09-05'&$group=council_district,str_type

Outputs: analysis/figures/05_austin_daily_active_str.png,
         06_austin_str_by_type.png, 07_austin_str_by_district.png
         and data/processed/austin_str_by_type_monthly_avg.csv

Run from repo root:  python analysis/src/austin_str_daily.py
"""
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
P = ROOT / "data" / "processed"
FIG = ROOT / "analysis" / "figures"
FIG.mkdir(parents=True, exist_ok=True)

S1, S2, S3, S4 = "#2a78d6", "#eb6834", "#1baf7a", "#a35bd6"
SURF, GRID, INK, INK2, MUTED = "#fcfcfb", "#e1e0d9", "#0b0b0b", "#52514e", "#898781"

plt.rcParams.update({
    "figure.facecolor": SURF, "axes.titlesize": 12.5, "axes.facecolor": SURF, "axes.edgecolor": GRID,
    "axes.grid": True, "grid.color": GRID, "grid.linewidth": 0.8,
    "axes.spines.top": False, "axes.spines.right": False,
    "text.color": INK, "axes.labelcolor": INK2, "xtick.color": INK2, "ytick.color": INK2,
    "font.size": 10, "axes.titleweight": "bold", "axes.titlelocation": "left",
})

# ---------------------------------------------------------------- daily total
daily = pd.read_csv(P / "austin_active_str_daily.csv", parse_dates=["date"]).sort_values("date")
first, last = daily.iloc[1], daily.iloc[-1]          # iloc[1] = 2025-03-13, first daily date
growth = last.active_str_licenses / first.active_str_licenses - 1
print(f"{first.date.date()} {first.active_str_licenses:,} -> {last.date.date()} {last.active_str_licenses:,}  ({growth:+.1%})")

# month-end values and monthly step
me = daily.set_index("date").resample("ME").last()
me["chg"] = me.active_str_licenses.diff()
print("\nMonth-end levels and monthly change:")
print(me.to_string())

fig, ax = plt.subplots(figsize=(10, 4.6))
ax.plot(daily.date, daily.active_str_licenses, color=S1, lw=1.8)
ax.set_title("Austin: active short-term-rental licences, daily")
ax.set_ylabel("licences")
ax.yaxis.set_major_formatter(matplotlib.ticker.FuncFormatter(lambda v, _: f"{v:,.0f}"))
ax.set_ylim(2000, 3050)
for x, txt, y in [
    (pd.Timestamp("2025-10-01"), "Oct 2025: revised STR ordinance\ntakes effect (2-yr licences,\ntenants may operate, no CO needed)", 3010),
    (pd.Timestamp("2025-12-16"), "11-19 Dec 2025:\n+129 in eight days", 2870),
]:
    ax.axvline(x, color=MUTED, lw=0.9, ls="--")
    ax.annotate(txt, (x, y), xytext=(6, 0), textcoords="offset points", fontsize=8.5, color=INK2, va="top")
ax.annotate(f"{first.active_str_licenses:,}", (first.date, first.active_str_licenses), xytext=(10, -4),
            textcoords="offset points", ha="left", fontsize=9, color=S1, fontweight="bold")
ax.annotate(f"{last.active_str_licenses:,}  ({growth:+.0%} in 18 mo)", (last.date, last.active_str_licenses),
            xytext=(-6, 8), textcoords="offset points", ha="right", fontsize=9, color=S1, fontweight="bold")
fig.text(0.01, 0.01, "Source: City of Austin Development Services, Socrata mydx-h5dy (527 daily dates, 2025-03-13 to 2026-09-05). "
         "Counts are licences, not listings: unlicensed units are not in this data.", fontsize=7.5, color=MUTED)
fig.tight_layout(rect=(0, 0.04, 1, 1))
fig.savefig(FIG / "05_austin_daily_active_str.png", dpi=160)

# ---------------------------------------------------------------- by type, monthly average
raw = pd.read_csv(P / "austin_str_by_type_monthly_raw.csv")
days = daily.assign(month=daily.date.dt.strftime("%Y-%m")).groupby("month").size().rename("days")
raw = raw.merge(days, left_on="month", right_index=True)
raw["avg_active"] = raw.sum_of_daily_counts / raw.days
wide = raw.pivot(index="month", columns="str_type", values="avg_active").round(1)
wide.to_csv(P / "austin_str_by_type_monthly_avg.csv")
print("\nMonthly average active licences by type:")
print(wide.to_string())

order = ["Type 1", "Type 1-A", "Type 1-Secondary", "Type 2 Commercial", "Type 2 Residential", "Type 3"]
labels = {"Type 1": "Type 1\nowner-occupied", "Type 1-A": "Type 1-A", "Type 1-Secondary": "Type 1-Secondary\n(ADU on owner lot)",
          "Type 2 Commercial": "Type 2\nCommercial", "Type 2 Residential": "Type 2 Residential\nnon-owner-occupied", "Type 3": "Type 3\nmultifamily"}
snap = pd.read_csv(P / "austin_str_by_district_type_snapshots.csv")
bytype = snap.groupby(["snapshot_date", "str_type"]).active_licenses.sum().unstack(0).reindex(order)
bytype["chg_pct"] = bytype["2026-09-05"] / bytype["2025-03-13"] - 1
print("\nBy type, 2025-03-13 vs 2026-09-05:")
print(bytype.to_string())

fig, ax = plt.subplots(figsize=(10, 5.0))
x = np.arange(len(order)); w = 0.38
b1 = ax.bar(x - w / 2, bytype["2025-03-13"], w, color=GRID, edgecolor=MUTED, label="13 Mar 2025")
b2 = ax.bar(x + w / 2, bytype["2026-09-05"], w, color=[S2 if t.startswith("Type 2 Res") or t == "Type 3" else S1 for t in order], label="5 Sep 2026")
for i, t in enumerate(order):
    ax.annotate(f"{bytype.loc[t, 'chg_pct']:+.0%}", (x[i] + w / 2, bytype.loc[t, '2026-09-05']), xytext=(0, 4),
                textcoords="offset points", ha="center", fontsize=9.5, fontweight="bold",
                color=S2 if bytype.loc[t, 'chg_pct'] > 0.2 else INK2)
ax.set_xticks(x); ax.set_xticklabels([labels[t] for t in order], fontsize=8.5)
ax.set_title("Austin STR licences by type: growth is investor + multifamily supply, not owner-occupied")
ax.set_ylabel("active licences"); ax.legend(frameon=False)
fig.text(0.01, 0.01, "Type labels per Austin Land Development Code 25-2-788..791 (Type 1 owner-occupied, Type 2 not owner-occupied, Type 3 multifamily);\n"
         "sub-type definitions are not in the dataset metadata. Source: City of Austin, Socrata mydx-h5dy.", fontsize=7.5, color=MUTED)
fig.tight_layout(rect=(0, 0.06, 1, 1))
fig.savefig(FIG / "06_austin_str_by_type.png", dpi=160)

# ---------------------------------------------------------------- by council district
byd = snap.groupby(["snapshot_date", "council_district"]).active_licenses.sum().unstack(0)
byd["chg"] = byd["2026-09-05"] - byd["2025-03-13"]
byd["chg_pct"] = byd["2026-09-05"] / byd["2025-03-13"] - 1
print("\nBy council district:")
print(byd.to_string())

fig, ax = plt.subplots(figsize=(10, 4.4))
xd = np.arange(len(byd)); w = 0.38
ax.bar(xd - w / 2, byd["2025-03-13"], w, color=GRID, edgecolor=MUTED, label="13 Mar 2025")
ax.bar(xd + w / 2, byd["2026-09-05"], w, color=S1, label="5 Sep 2026")
for i, (d, r) in enumerate(byd.iterrows()):
    ax.annotate(f"{r.chg:+.0f}", (xd[i] + w / 2, r["2026-09-05"]), xytext=(0, 4), textcoords="offset points",
                ha="center", fontsize=9, color=S2 if r.chg > 100 else INK2, fontweight="bold" if r.chg > 100 else "normal")
ax.set_xticks(xd); ax.set_xticklabels([f"D{int(d)}" for d in byd.index])
ax.set_title("Austin STR licences by council district: D3 and D1 add the most; D9 (downtown) still largest")
ax.set_ylabel("active licences"); ax.legend(frameon=False)
fig.text(0.01, 0.01, "Source: City of Austin, Socrata mydx-h5dy. District descriptions are approximate.", fontsize=7.5, color=MUTED)
fig.tight_layout(rect=(0, 0.04, 1, 1))
fig.savefig(FIG / "07_austin_str_by_district.png", dpi=160)
print("\nfigures written to", FIG)
