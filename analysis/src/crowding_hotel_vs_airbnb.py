"""Does crowding push travellers from hotels to Airbnb-type rentals?  Two tests.

Test A - Europe, 32 countries x 12 months of 2024 (Eurostat, official):
    platform nights  = tour_ce_omr  (guest nights booked via Airbnb/Booking/Expedia/TripAdvisor, c_resid=TOTAL)
    hotel nights     = tour_occ_nim (nights at hotels & similar, NACE I551)
    hotel bed places = tour_cap_nat (I551, bed places, 2024)
    crowding         = hotel bed occupancy = hotel nights / (bed places x days in month)
    outcome          = platform share = platform nights / (platform + hotel nights)
    Within each country: does platform share rise in the months when hotels are most crowded?
    Pooled with country fixed effects: platform_share ~ hotel_occupancy + C(country).
    Plus annual 2019 vs 2024 cross-section (tour_ce_oam, tour_occ_ninat, tour_cap_nat).

Test B - Hawaii, 4 islands (DBEDT 2024 Annual Visitor Research Report):
    crowding = average daily visitor census / total visitor units (Table 8 / Table 110)
    hotel share of visitors, rental-home share (Tables 57, 59, 62, 63); hotel occupancy & ADR (STR, Tables 105-108)
    Inventory mix: hotel units vs vacation-rental units vs condo-hotel vs timeshare.

Inputs  data/raw/eurostat/*.json (gitignored cache of the raw JSON-stat responses; the script fetches them from the API if absent),
        NOTE: platform nights duplicate Krishang's data/processed/eurostat_platform_nights_monthly.csv (branch krish/eu-platform-backlog);
        what is new here is the HOTEL side (tour_occ_nim, tour_cap_nat) and the share/crowding tests.
        data/processed/eurostat_platform_vs_hotel_by_country_2019_2024.csv,
        data/processed/hawaii_dbedt_2024_crowding_by_island.csv
Outputs data/processed/eurostat_platform_vs_hotel_monthly_2024.csv, ..._crowding_tests.csv
        analysis/figures/11_eu_platform_share_vs_hotel_occupancy_monthly.png, 12_hawaii_crowding_islands.png
Run from repo root: python analysis/src/crowding_hotel_vs_airbnb.py
"""
import json
from pathlib import Path
import numpy as np
import pandas as pd
from scipy import stats
import statsmodels.formula.api as smf
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

ROOT = Path(__file__).resolve().parents[2]
P = ROOT / "data/processed"; R = ROOT / "data/raw/eurostat"; F = ROOT / "analysis/figures"
F.mkdir(parents=True, exist_ok=True)
S1, S2, S3, GRID, INK2, MUTED, SURF = "#2a78d6", "#eb6834", "#1baf7a", "#e1e0d9", "#52514e", "#898781", "#fcfcfb"
plt.rcParams.update({"figure.facecolor": SURF, "axes.facecolor": SURF, "axes.edgecolor": GRID, "axes.grid": True, "grid.color": GRID,
                     "axes.spines.top": False, "axes.spines.right": False, "axes.titleweight": "bold", "axes.titlelocation": "left",
                     "axes.labelcolor": INK2, "xtick.color": INK2, "ytick.color": INK2, "font.size": 10})

# ------------------------------------------------------------------ Test A: Europe monthly
GEO_CE = "EU27_2020,BE,BG,CZ,DK,DE,EE,IE,EL,ES,FR,HR,IT,CY,LV,LT,LU,HU,MT,NL,AT,PL,PT,RO,SI,SK,FI,SE,IS,LI,NO,CH".split(",")
GEO_OCC = "EU27_2020,EU28,EU27_2007,EU25,EA,EA20,BE,BG,CZ,DK,DE,EE,IE,EL,ES,FR,HR,IT,CY,LV,LT,LU,HU,MT,NL,AT,PL,PT,RO,SI,SK,FI,SE,IS,LI,NO,CH,UK,ME,MK,AL,RS,TR,XK".split(",")
API = "https://ec.europa.eu/eurostat/api/dissemination/statistics/1.0/data/"


def eurostat_values(local_name: str, query: str) -> dict:
    """Load the JSON-stat 'value' block from data/raw/eurostat (gitignored); fetch from the API and cache it if missing."""
    R.mkdir(parents=True, exist_ok=True)
    f = R / local_name
    if f.exists():
        return json.load(open(f))["value"]
    import urllib.request
    with urllib.request.urlopen(API + query, timeout=120) as r:
        js = json.load(r)
    json.dump({"_note": "raw JSON-stat from " + API + query, "id": js["id"], "size": js["size"],
               "geo_index": js["dimension"]["geo"]["category"]["index"], "value": js["value"]}, open(f, "w"))
    return js["value"]


ce = eurostat_values("tour_ce_omr_2024_nights_values.json", "tour_ce_omr?format=JSON&lang=EN&sinceTimePeriod=2024-01&untilTimePeriod=2024-12&c_resid=TOTAL")
occ = eurostat_values("tour_occ_nim_2024_hotel_nights_values.json", "tour_occ_nim?format=JSON&lang=EN&sinceTimePeriod=2024-01&untilTimePeriod=2024-12&nace_r2=I551&c_resid=TOTAL&unit=NR")
annual = pd.read_csv(P / "eurostat_platform_vs_hotel_by_country_2019_2024.csv").set_index("geo")
DAYS = [31, 29, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]
rows = []
for gi, g in enumerate(GEO_CE):
    if g not in GEO_OCC:
        continue
    oi = GEO_OCC.index(g)
    beds = annual.loc[g, "hotel_bedplaces_2024"] if g in annual.index else np.nan
    for m in range(12):
        pn = ce.get(str(832 + (m + 1) * 32 + gi)); hn = occ.get(str(oi * 12 + m))
        if pn is None or hn is None:
            continue
        rows.append(dict(geo=g, country=annual.loc[g, "country"] if g in annual.index else g, month=m + 1, platform_nights=pn, hotel_nights=hn,
                         platform_share=pn / (pn + hn), hotel_bed_occupancy=hn / (beds * DAYS[m]) if beds == beds else np.nan))
mo = pd.DataFrame(rows)
mo.to_csv(P / "eurostat_platform_vs_hotel_monthly_2024.csv", index=False)

# within-country: Spearman(platform share, hotel occupancy) over the 12 months
tests = []
for g, d in mo[mo.geo != "EU27_2020"].dropna(subset=["hotel_bed_occupancy"]).groupby("country"):
    if len(d) < 12:
        continue
    rs, p = stats.spearmanr(d.hotel_bed_occupancy, d.platform_share)
    peak = d.nlargest(3, "hotel_bed_occupancy").platform_share.mean(); trough = d.nsmallest(3, "hotel_bed_occupancy").platform_share.mean()
    tests.append(dict(country=g, spearman_share_vs_occupancy=rs, p=p, share_peak3=peak, share_trough3=trough, peak_minus_trough_pts=(peak - trough) * 100,
                      annual_platform_share=d.platform_nights.sum() / (d.platform_nights.sum() + d.hotel_nights.sum()), max_hotel_occ=d.hotel_bed_occupancy.max()))
tests = pd.DataFrame(tests).sort_values("peak_minus_trough_pts", ascending=False)
tests.to_csv(P / "eurostat_crowding_tests_by_country_2024.csv", index=False)
print("Within-country (12 months of 2024): platform share in the 3 most crowded hotel months minus 3 least crowded:")
print(tests.round(3).to_string(index=False))
print(f"\ncountries where share is HIGHER in crowded months: {(tests.peak_minus_trough_pts > 0).sum()} of {len(tests)}; "
      f"significant positive Spearman (p<0.05): {((tests.p < 0.05) & (tests.spearman_share_vs_occupancy > 0)).sum()}; significant negative: {((tests.p < 0.05) & (tests.spearman_share_vs_occupancy < 0)).sum()}")

pan = mo[(mo.geo != "EU27_2020")].dropna(subset=["hotel_bed_occupancy"]).copy()
fe = smf.ols("platform_share ~ hotel_bed_occupancy + C(country)", data=pan).fit(cov_type="cluster", cov_kwds={"groups": pan.country})
fe2 = smf.ols("platform_share ~ hotel_bed_occupancy + C(country) + C(month)", data=pan).fit(cov_type="cluster", cov_kwds={"groups": pan.country})
print(f"\nPooled OLS with country FE (n={int(fe.nobs)}): platform_share on hotel_bed_occupancy beta = {fe.params['hotel_bed_occupancy']:+.3f} "
      f"(SE {fe.bse['hotel_bed_occupancy']:.3f}, p={fe.pvalues['hotel_bed_occupancy']:.3f})  -> +10 pts occupancy = {fe.params['hotel_bed_occupancy']*10:+.1f} pts share")
print(f"With month FE too: beta = {fe2.params['hotel_bed_occupancy']:+.3f} (p={fe2.pvalues['hotel_bed_occupancy']:.3f})")

# cross-section annual
c = annual[annual.index != "EU27_2020"].dropna(subset=["platform_share_2024", "hotel_bed_occupancy_2024"])
rs, p = stats.spearmanr(c.hotel_bed_occupancy_2024, c.platform_share_2024)
print(f"\nCross-country 2024 (n={len(c)}): Spearman(platform share, hotel occupancy) = {rs:+.2f}, p={p:.2f}")
eu = annual.loc["EU27_2020"]
print(f"EU27: platform share {eu.platform_share_2019:.1%} (2019) -> {eu.platform_share_2024:.1%} (2024); hotel bed occupancy {eu.hotel_bed_occupancy_2019:.1%} -> {eu.hotel_bed_occupancy_2024:.1%}; "
      f"platform nights {eu.platform_growth_19_24:+.0%}, hotel nights {eu.hotel_growth_19_24:+.0%}")

# figure 11: EU27 monthly + four example countries
fig, axes = plt.subplots(1, 2, figsize=(12, 4.6))
ax = axes[0]
e = mo[mo.geo == "EU27_2020"]
ax.plot(e.month, e.platform_share * 100, color=S2, lw=2.2, marker="o", label="platform share of nights (%)")
ax.plot(e.month, e.hotel_bed_occupancy * 100, color=S1, lw=2.2, marker="o", label="hotel bed occupancy (%)")
ax.set_xticks(range(1, 13)); ax.set_xticklabels("JFMAMJJASOND"); ax.set_title("EU27 2024: platform share peaks with hotel crowding")
ax.legend(frameon=False, loc="upper left"); ax.set_ylim(0, 70)
ax = axes[1]
ax.barh(tests.country, tests.peak_minus_trough_pts, color=[S2 if v > 0 else S1 for v in tests.peak_minus_trough_pts])
ax.axvline(0, color=MUTED, lw=1); ax.set_xlabel("platform share, 3 most crowded hotel months minus 3 least (pts)")
ax.set_title("Crowded minus quiet hotel months, by country"); ax.tick_params(axis="y", labelsize=8)
fig.text(0.01, 0.01, "Sources: Eurostat tour_ce_omr (platform guest nights, Airbnb/Booking/Expedia/TripAdvisor), tour_occ_nim (hotel nights, NACE I551), tour_cap_nat (hotel bed places). "
         "\nBed occupancy = nights / (bed places x days); it runs ~15-20 pts below room occupancy.", fontsize=7.5, color=MUTED)
fig.tight_layout(rect=(0, 0.07, 1, 1)); fig.savefig(F / "11_eu_platform_share_vs_hotel_occupancy_monthly.png", dpi=160)

# ------------------------------------------------------------------ Test B: Hawaii islands
hi = pd.read_csv(P / "hawaii_dbedt_2024_crowding_by_island.csv")
hi["total_units"] = hi[["hotel_units", "condo_hotel_units", "timeshare_units", "vacation_rental_units", "other_units"]].sum(axis=1)
hi["visitors_per_unit"] = hi.avg_daily_census / hi.total_units
hi["hotel_share_of_units"] = hi.hotel_units / hi.total_units
hi["rental_share_of_units"] = hi.vacation_rental_units / hi.total_units
hi["hotel_visitors_per_hotel_unit"] = hi.avg_daily_census * hi.hotel_share_pct / 100 / hi.hotel_units
hi["rental_visitors_per_rental_unit"] = hi.avg_daily_census * hi.rental_home_share_pct / 100 / hi.vacation_rental_units
print("\nHawaii islands 2024:")
print(hi[["island", "avg_daily_census", "total_units", "visitors_per_unit", "hotel_units", "vacation_rental_units", "hotel_share_of_units", "hotel_share_pct",
          "rental_home_share_pct", "hotel_occupancy_pct", "hotel_adr_usd", "hotel_visitors_per_hotel_unit", "rental_visitors_per_rental_unit"]].round(2).to_string(index=False))
hi.to_csv(P / "hawaii_dbedt_2024_crowding_by_island.csv", index=False)

fig, axes = plt.subplots(1, 2, figsize=(12, 4.6))
ax = axes[0]
x = np.arange(len(hi)); w = 0.38
ax.bar(x - w / 2, hi.hotel_share_of_units * 100, w, color=GRID, edgecolor=MUTED, label="hotel share of lodging units")
ax.bar(x + w / 2, hi.hotel_share_pct, w, color=S1, label="hotel share of visitors")
for i, r in hi.iterrows():
    ax.annotate(f"{r.visitors_per_unit:.1f} visitors/unit\nhotel occ {r.hotel_occupancy_pct:.0f}%", (x[i], max(r.hotel_share_of_units * 100, r.hotel_share_pct) + 2), ha="center", fontsize=8, color=INK2)
ax.set_xticks(x); ax.set_xticklabels(hi.island); ax.set_ylim(0, 100); ax.set_ylabel("%"); ax.legend(frameon=False, loc="upper right")
ax.set_title("Hawaii: hotel share of units vs of visitors")
ax = axes[1]
ax.scatter(hi.hotel_visitors_per_hotel_unit, hi.rental_home_share_pct, s=120, color=S2)
for _, r in hi.iterrows():
    ax.annotate(r.island, (r.hotel_visitors_per_hotel_unit, r.rental_home_share_pct), xytext=(6, 4), textcoords="offset points", fontsize=9, color=INK2)
ax.set_xlabel("hotel-staying visitors per hotel unit (pressure on hotel stock)"); ax.set_ylabel("% of visitors in rental homes")
ax.set_title("Hotel pressure vs rental-home share (n=4)")
fig.text(0.01, 0.01, "Source: Hawaii DBEDT 2024 Annual Visitor Research Report - Tables 8 (daily census), 57/59/62/63 (accommodation), 105-108 (STR hotel occupancy/ADR), 110 (Visitor Plant Inventory).\n"
         "Accommodation shares are 'any use' so a visitor can count in two types; rental units are DBEDT-identified units, far fewer than Inside Airbnb listings.", fontsize=7.2, color=MUTED)
fig.tight_layout(rect=(0, 0.08, 1, 1)); fig.savefig(F / "12_hawaii_crowding_islands.png", dpi=160)
print("\nfigures written")
