"""Forward exhibits for the SIG pitch (built 2026-09-01).

Exhibit 1 — quarterly KPI panel FY25 Q1 -> FY27 Q1 from the earnings calls,
             with the derived implied-unit-comp series and the AUR-vs-merch-margin scissors.
Exhibit 2 — gold ledger: monthly gold -> weighted-average-cost blended COGS gold by fiscal
             quarter, the hedge book from the 10-K / 10-Q, and a holiday scenario strip for
             H2 FY27 merchandise margin.

Every hard-coded number carries a source tag (transcript file:line or filing) in the CSVs.
Run:  python forward_exhibits.py   (from SIG/research/data)
Outputs: kpi_panel_quarterly.csv, gold_ledger_quarterly.csv, gold_scenarios_h2fy27.csv,
         exhibit_kpi_scissors.png, exhibit_implied_units.png, exhibit_gold_bridge.png
"""
import math
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch

HERE = r"C:\Users\krish\BAM_comp\SIG\research\data"

# ---------------------------------------------------------------- palette (dataviz reference, validated 2026-09-01)
SURFACE, INK, INK2, GRID = "#fcfcfb", "#0b0b0b", "#52514e", "#e6e5e1"
BLUE, ORANGE, AQUA, RED = "#2a78d6", "#eb6834", "#1baf7a", "#e34948"   # slots 1-3 + diverging red pole
BLUE_L = "#9ec5f4"                                                    # sequential blue step 200

# ---------------------------------------------------------------- fiscal calendar
def fq_of(d):
    """Signet fiscal quarter of a calendar date. FY27 Q1 = Feb-Apr 2026."""
    m, y = d.month, d.year
    if m in (2, 3, 4):   return (y + 1, 1)
    if m in (5, 6, 7):   return (y + 1, 2)
    if m in (8, 9, 10):  return (y + 1, 3)
    return (y + 1 if m >= 11 else y, 4)

def fq_label(t):
    return f"FY{t[0]}Q{t[1]}"

# ================================================================ EXHIBIT 1 — KPI PANEL
# Sources: Bloomberg FINAL transcripts in SIG/transcripts (file:line), Q1 FY27 10-Q, FY26 10-K,
# business_model_kpis.md §2 (revenue), trends_vs_comps_backtest.csv (SEC-sourced SSS).
NA = np.nan
rows = [
 # quarter, call date, SSS %, revenue $M, merch AUR %, fashion AUR %, bridal AUR %, bridal AUR text,
 # units stated, merch margin bps, gross margin bps, LGD fashion pen %, LGD bridal pen %,
 # ESA attach change bps, inventory $M, inventory y/y text, services growth text, buyback note, source
 ("FY2025Q1","2024-06-13",-8.9,1510.8, NA, NA, NA,"n/a (ATV era)","ATV down slightly",
   +100, 0,   NA, NA, +550, 2000,"-9% y/y","services +1.3%","48M diluted shares (-10% vs FY24 end)",
   "FY2025_Q1.txt:205-208 merch margin +100bps; :161 attach +550bps; :217 inventory $2.0B -9%; SSS from 8-K Ex99.1"),
 ("FY2025Q2","2024-09-12",-3.4,1491.0, NA, NA, NA,"n/a (ATV era)","ATV up (NA bridal ATV ~flat, fashion +MSD)",
   +120, NA,  NA, NA, +210, 1990,"-5%+ y/y","services +1.4%","share count -15% annualised",
   "FY2025_Q2.txt:182-184 merch margin +120bps; :99 attach +210bps; :207 inventory <$2.0B"),
 ("FY2025Q3","2024-12-05",-0.7,1349.4, NA, NA, NA,"n/a (ATV era)","NA fashion ATV +MSD, NA bridal ATV -MSD",
   0,   0,    NA, NA, +170, 2100,"+2% y/y","services ~+2%","$118M YTD; 43.5M diluted at YE (guide)",
   "FY2025_Q3.txt:166-167 merch margin flat (cycling +250bps); :118 attach +170bps; :174 inventory $2.1B +2%"),
 ("FY2025Q4","2025-03-19",-1.1,2352.6,  7.0, 8.0, 2.0,"+2% (best in 2 yrs)","not stated (53rd-week lap ~4pts)",
   NA, -70,   NA, NA, NA, 2006.5,"FY-end $2,006.5M (10-Q comparative)","n/a","diluted count -~20% (preferred retired)",
   "FY2025_Q4.txt:240-242 AUR +7%, bridal +2%, fashion +8%; :244-247 GM -70bps with 'modest merchandise margin expansion'"),
 ("FY2026Q1","2025-06-03", 2.5,1541.6,  8.0,10.0, 1.0,"up slightly","not stated",
   +50, +100, 20.0, NA, NA, 2000,"+~1% y/y (below +2% revenue)","n/a","2.3M sh YTD, >5%",
   "FY2026_Q1.txt:184-186 AUR ~+8%, fashion +10%, bridal slightly up; :191 GM +100bps; :529-530 GMM +50bps; :503-504 total LGD penetration ~20% (+5pts); :205 inventory $2.0B +1%. SSS +2.5% as printed (restated +2.7% under FY27 definition)"),
 ("FY2026Q2","2025-09-02", 2.0,1535.1,  9.0,12.0, 4.0,"+4%","units -7% (largely Banter)",
   +30, +60,  14.0, NA, NA, 2000,"flat y/y despite gold +30%","services >+7%","$150M YTD, 6% of shares; auth $570M",
   "FY2026_Q2.txt:198 AUR ~+9%, fashion +12%, bridal +4%; :205 units -7%; :208-216 GM +60bps, GMM +30bps (+80 promo/architecture, +20 services, -70 wholesaling/write-down); :73-74 LGD fashion 14%; :227-228 inventory $2.0B flat, gold +30%"),
 ("FY2026Q3","2025-12-02", 3.0,1391.8,  7.0, 8.0, 6.0,"+6%","down, improved sequentially (Banter, Zales)",
   +80, +130, 15.0, 40.0, +150, 2100,"-1% y/y despite gold +~50%","services HSD","$180M YTD, 2.8M sh, >6%; auth $545M",
   "FY2026_Q3.txt:144-145 comp +3%, AUR +7%, units down improved; :151-153 fashion AUR +8%, bridal +6%; :156-157 attach +1.5pts; :98-103 merch margin +80bps (YTD +50); :158 GM +130bps; :82-83 LGD fashion 15%; :388-389 LGD ~40% of bridal; :179-180 inventory $2.1B -1%, gold +~50%"),
 ("FY2026Q4","2026-03-19",-0.7,2345.1,  5.0, NA,  NA,"up","LSD declines in bridal and fashion",
   -30, -60,  20.5, 48.0, NA, 1900,"flat y/y","services MSD comp","FY $205M, 3M+ sh, >7%, avg ~$66; auth $518M",
   "FY2026_Q4.txt:213-215 comp -0.7%, AUR +5% all categories, LSD unit declines; :216-218 GM -60bps, merch margin -30bps; :387-390 LGD 'under 50%' bridal, fashion 'just north of 20%' (run-rate ~15%); :225 inventory $1.9B flat"),
 ("FY2027Q1","2026-06-02", 1.8,1553.6,  4.5, NA,  8.0,"up high-single-digit","unit comps +3pts sequential vs Q4",
   -70, -100, NA, NA, NA, 1994.0,"roughly flat y/y ($2,006.5M LY)","services +5.2% (10-Q)","1.3M sh/$114M through 6/2 + $50M ASR; auth ~$355M",
   "FY2027_Q1.txt:206-215 comp +1.8% (JA -1pt), AUR ~+5% (10-Q: 4.5%), bridal +HSD, GM -~100bps, merch margin -70bps (gold), occupancy +20bps; :63-66 unit comps +3pts seq; :230-231 inventory $2.0B flat; 10-Q: NA AUR +5.1%, NA units -4.5%"),
]
cols = ["quarter","call_date","sss_pct","revenue_musd","merch_aur_pct","fashion_aur_pct","bridal_aur_pct",
        "bridal_aur_text","units_stated","merch_margin_bps_yoy","gross_margin_bps_yoy","lgd_fashion_pen_pct",
        "lgd_bridal_pen_pct","esa_attach_change_bps","inventory_musd","inventory_text","services_text",
        "buyback_text","source"]
kpi = pd.DataFrame(rows, columns=cols)

# derived: implied unit comp = (1+SSS)/(1+AUR) - 1   (comps include services ~12% of sales -> merch units ~0.5-1pt worse)
kpi["implied_units_pct"] = ((1 + kpi["sss_pct"] / 100) / (1 + kpi["merch_aur_pct"] / 100) - 1) * 100
# management check column (what they said the same quarter)
check = {"FY2026Q2": "stated units -7%", "FY2026Q3": "stated down, improved seq.",
         "FY2026Q4": "stated LSD declines", "FY2027Q1": "stated +3pts seq (Q4 -5.4 -> ~-2.4)"}
kpi["units_reconciliation"] = kpi["quarter"].map(check)

# ---- joins: gold (spot + blended), promo, Tenoris ------------------------------------------------
gold = pd.read_csv(f"{HERE}\\gold_monthly_avg.csv")
gold["Date"] = pd.to_datetime(gold["Date"])
gold = gold.set_index("Date")["gold_usd_oz"].rename("gold")

def blended(series, tau_days):
    """Weighted-average-cost proxy: EWMA of monthly purchase price with time constant tau (days).
    Under perpetual average cost with steady throughput, the inventory pool is an exponentially
    weighted average of purchase prices whose mean age = inventory / throughput."""
    tau_m = tau_days / 30.4
    alpha = 1 - math.exp(-1 / tau_m)
    return series.ewm(alpha=alpha, adjust=False).mean()

def fq_table(series):
    df = series.to_frame("v")
    df["fq"] = [fq_label(fq_of(d)) for d in df.index]
    q = df.groupby("fq")["v"].mean()
    order = sorted(q.index, key=lambda s: (int(s[2:6]), int(s[-1])))
    q = q.loc[order]
    return pd.DataFrame({"avg": q, "yoy": (q / q.shift(4) - 1) * 100})

g_spot = fq_table(gold)
g_110 = fq_table(blended(gold, 110))
g_180 = fq_table(blended(gold, 180))
kpi["gold_avg_spot"] = kpi["quarter"].map(g_spot["avg"]).round(0)
kpi["gold_yoy_spot_pct"] = kpi["quarter"].map(g_spot["yoy"]).round(1)
kpi["gold_yoy_blended110_pct"] = kpi["quarter"].map(g_110["yoy"]).round(1)
kpi["gold_yoy_blended180_pct"] = kpi["quarter"].map(g_180["yoy"]).round(1)

promo = pd.read_csv(f"{HERE}\\promo_intensity.csv")
promo = promo[promo["comparable"] == 1].copy()
promo["fq"] = [fq_label(fq_of(d)) for d in pd.to_datetime(promo["date"])]
pk = promo[promo["banner"] == "kay"].groupby("fq").agg(kay_promo_depth=("event_depth", "mean"),
                                                        kay_sitewide_freq=("sitewide", "mean"), kay_n=("event_depth", "size"))
pz = promo[promo["banner"] == "zales"].groupby("fq").agg(zales_promo_depth=("event_depth", "mean"), zales_n=("event_depth", "size"))
for c in pk.columns: kpi[c] = kpi["quarter"].map(pk[c]).round(2)
for c in pz.columns: kpi[c] = kpi["quarter"].map(pz[c]).round(2)

ten = pd.read_csv(f"{HERE}\\tenoris_series.csv")
ten = ten[ten["period_type"] == "month"].copy()
ten["fq"] = [fq_label(fq_of(d)) for d in pd.to_datetime(ten["period"] + "-01")]
tq = ten.groupby("fq").agg(tenoris_sales_yoy=("total_sales_yoy_pct", "mean"),
                           tenoris_units_yoy=("total_units_yoy_pct", "mean"),
                           tenoris_spend_unit_yoy=("avg_spend_per_unit_yoy_pct", "mean"))
for c in tq.columns: kpi[c] = kpi["quarter"].map(tq[c]).round(1)
kpi["tenoris_minus_sss_pts"] = (kpi["tenoris_sales_yoy"] - kpi["sss_pct"]).round(1)

# ESP plans sold (10-K Note 3 / 10-Q): only annual + Q1 comparables exist in the folder
esp = {"FY2026Q1": 135.0, "FY2027Q1": 138.9}
kpi["esp_plans_sold_musd"] = kpi["quarter"].map(esp)

# next-quarter guide row for reference (not a data row)
guide_row = {"quarter": "FY2027Q2 (guide)", "call_date": "2026-09-09", "sss_pct": np.nan, "revenue_musd": np.nan,
             "units_stated": "guide: AUR growth across categories with modest unit declines (FY2027_Q1.txt:244-245)",
             "merch_margin_bps_yoy": np.nan,
             "source": "Q2 guide: SSS +0.5% to +2.5%; adj OI $79-93M; merch margin 'somewhat lower' (FY2027_Q1.txt:267-270); FY: 'flat to slightly down... down in H1, flat to slightly up in H2' (:774-777)",
             "gold_avg_spot": round(g_spot.loc["FY2027Q2", "avg"]), "gold_yoy_spot_pct": round(g_spot.loc["FY2027Q2", "yoy"], 1),
             "gold_yoy_blended110_pct": round(g_110.loc["FY2027Q2", "yoy"], 1), "gold_yoy_blended180_pct": round(g_180.loc["FY2027Q2", "yoy"], 1),
             "kay_promo_depth": pk.loc["FY2027Q2", "kay_promo_depth"] if "FY2027Q2" in pk.index else np.nan,
             "kay_sitewide_freq": pk.loc["FY2027Q2", "kay_sitewide_freq"] if "FY2027Q2" in pk.index else np.nan,
             "zales_promo_depth": pz.loc["FY2027Q2", "zales_promo_depth"] if "FY2027Q2" in pz.index else np.nan,
             "tenoris_sales_yoy": tq.loc["FY2027Q2", "tenoris_sales_yoy"] if "FY2027Q2" in tq.index else np.nan,
             "tenoris_units_yoy": tq.loc["FY2027Q2", "tenoris_units_yoy"] if "FY2027Q2" in tq.index else np.nan,
             "tenoris_spend_unit_yoy": tq.loc["FY2027Q2", "tenoris_spend_unit_yoy"] if "FY2027Q2" in tq.index else np.nan}
kpi_out = pd.concat([kpi, pd.DataFrame([guide_row])], ignore_index=True)
kpi_out.to_csv(f"{HERE}\\kpi_panel_quarterly.csv", index=False)

# ================================================================ EXHIBIT 2 — GOLD LEDGER + H2 BRIDGE
# Hedge book (primary: FY26 10-K Note 19 / Item 7A; Q1 FY27 10-Q derivatives note; FY23-FY25 10-Ks)
hedge = pd.DataFrame([
 # period end, oz notional, open FV asset, open FV liab, AOCI pre-tax, OCI gains in period, reclass to COGS in period, expected 12m reclass, source
 ("FY2023 (1/28/23)",      0,   0.0,  0.0,  0.0,  0.0,  0.4,  0.0, "FY23 10-K: trading suspended FY22; FY22 reclass loss $0.4M (last trace of prior program)"),
 ("FY2024 (2/3/24)",       0,   0.0,  0.0,  0.0,  0.0,  0.0,  0.0, "FY24 10-K: 'no commodity derivative contracts outstanding as of February 3, 2024 and January 28, 2023'"),
 ("FY2025 (2/1/25)",       0,   0.0,  0.0,  0.0,  0.0,  0.0,  0.4, "FY25 10-K: commodity contracts '—'; $0.4M expected 12m reclass is FX"),
 ("Q2 FY26 (8/2/25)",     NA,    NA,   NA,   NA,   NA,   NA,   NA, "hedging 'began during the second quarter of Fiscal 2026' (FY26 10-K); 10-Q not in folder — fetch from EDGAR"),
 ("Q3 FY26 (11/1/25)",    NA,    NA,   NA,   NA,   NA,   NA,   NA, "10-Q not in folder — fetch from EDGAR"),
 ("FY2026 (1/31/26)", 35000,  26.8, -0.6, 35.8, 38.7,  2.9, 30.3, "FY26 10-K Note 19: ~35,000 oz forwards, cash-flow hedges, settle over next 11 months; OCI gains $38.7M; reclass to COGS $(2.9)M; AOCI $35.8M; FV asset $26.8M / liab $(0.6)M; 'approximately $30.3 million... within the next 12 months'. Item 7A: 10% gold depreciation = $(17.0)M on commodity contracts (FV $26.2M) -> notional ~$170M"),
 ("Q1 FY27 (5/2/26)",  26000,  11.5, -1.8, 32.6, -0.9,  2.3, 30.3, "Q1 FY27 10-Q: ~26,000 oz (Jan 31: 35,000), settle over next 11 months; FV asset $11.5M / liab $(1.8)M; OCI $(0.9)M; reclass to COGS $(2.3)M; AOCI $32.6M pre-tax ($23.9M after tax); still ~$30.3M expected within 12 months; market-risk profile 'not materially changed'"),
], columns=["period_end","oz_notional","fv_asset_musd","fv_liab_musd","aoci_pretax_musd","oci_in_period_musd","reclass_to_cogs_musd","expected_12m_reclass_musd","source"])
hedge.to_csv(f"{HERE}\\gold_hedge_book.csv", index=False)

# cover arithmetic (labelled assumptions)
merch_expense_fy26 = 2508.9 + 168.6 + 41.4          # FY26 10-K segment expense table ($M)
gold_share_range = (0.20, 0.25, 0.30)                # expert inference (VIC: 25-30% pre-runup; Helzberg '80% gold+labor'); NOT disclosed
oz_per_month_settling = 26000 / 11
cover = {}
for s in gold_share_range:
    need_oz_yr = merch_expense_fy26 * 1e6 * s / 4400  # at ~$4,400/oz
    cover[s] = oz_per_month_settling / (need_oz_yr / 12) * 100
aoci_locked = 32.6 - (11.5 - 1.8)                     # gains on settled contracts not yet in COGS (sitting in inventory)

# quarterly gold ledger with scenarios --------------------------------------------------------------
last_actual = gold.index.max()                        # 2026-08-31
scen_prices = {"gold $3,800": 3800, "gold $4,400 (~spot)": 4400, "gold $5,000": 5000}
future_idx = pd.date_range("2026-09-30", "2027-01-31", freq="ME")
ledger_rows = []
scen_tables = {}
for name, px in scen_prices.items():
    path = pd.concat([gold, pd.Series([px] * len(future_idx), index=future_idx)])
    spot_q = fq_table(path); b110 = fq_table(blended(path, 110)); b180 = fq_table(blended(path, 180))
    scen_tables[name] = (spot_q, b110, b180)

# calibrate the net gold drag on Q1 FY27 (observed -70 bps) and scale linearly with blended y/y
base_q = "FY2027Q1"; obs_bps = -70.0
merch_margin_rate = 0.55                              # computable NA merch margin, FY26 10-K basis
def unmitigated_bps(g_yoy_pct, s):                    # -(1-m) * s * g
    return -(1 - merch_margin_rate) * s * (g_yoy_pct / 100) * 1e4

q_sales = {"FY2027Q2": 1535.1, "FY2027Q3": 1391.8, "FY2027Q4": 2345.1}   # prior-year quarterly revenue as the base
merch_share_of_sales = 1268.1 / 1463.0                # NA merchandise-type sales / NA sales, Q1 FY27 10-Q (~0.87)
reclass_total = 30.3
# Two phasing assumptions for the $30.3M expected in COGS within 12 months of 5/2/26:
#  (a) H2-weighted 20/40/40 (management: "the back half begins to neutralize", FY2026_Q4.txt:293-298)
#  (b) sales-weighted over the four quarters May-26 -> Apr-27 (Q2/Q3/Q4 FY27 + Q1 FY28)
q_rev_4 = {"FY2027Q2": 1535.1, "FY2027Q3": 1391.8, "FY2027Q4": 2345.1, "FY2028Q1": 1553.6}
tot4 = sum(q_rev_4.values())
phasing = {"H2-weighted 20/40/40": {"FY2027Q2": 0.20, "FY2027Q3": 0.40, "FY2027Q4": 0.40},
           "sales-weighted 12 mo": {q: v / tot4 for q, v in q_rev_4.items()}}

out = []
for name, (spot_q, b110, b180) in scen_tables.items():
    g_base = b110.loc[base_q, "yoy"]
    for q in ["FY2027Q1", "FY2027Q2", "FY2027Q3", "FY2027Q4"]:
        g110 = b110.loc[q, "yoy"]; g180 = b180.loc[q, "yoy"]; gs = spot_q.loc[q, "yoy"]
        net_gold = obs_bps * (g110 / g_base)           # linear scaling of the observed, mitigated Q1 drag
        unmit = {s_: unmitigated_bps(g110, s_) for s_ in gold_share_range}
        offset = (1 - obs_bps / unmit[0.25]) if q == base_q else np.nan
        sales = 1553.6 if q == base_q else q_sales[q]
        merch_sales = sales * merch_share_of_sales
        base_reclass_bps = (2.9 / (2345.1 * merch_share_of_sales) * 1e4) if q == "FY2027Q4" else 0.0
        # Q2 FY26 merch margin carried a -70 bps one-off (loose-stone wholesaling + discontinued-product
        # write-down, FY2026_Q2.txt:213-216); lapping it is +70 bps in Q2 FY27 IF the wholesaling does not recur.
        lap_bps = 70.0 if q == "FY2027Q2" else 0.0
        # tariff y/y: Sec-232/IEEPA started late Aug 2025 -> Q2 FY27 still laps a no-tariff base (UBS: -20 bps);
        # Q3/Q4 lap the Aug-2025 start at a lower Indian rate (10-15.5% vs 25-50%) -> ~0 (open_items_regulatory.md)
        tariff_bps = -20.0 if q == "FY2027Q2" else 0.0
        rec = {}
        for ph, sched in phasing.items():
            musd = 2.3 if q == base_q else reclass_total * sched[q]
            bps = musd / merch_sales * 1e4
            rec[ph] = (musd, bps, net_gold + bps - base_reclass_bps + lap_bps + tariff_bps)
        out.append({"scenario": name, "quarter": q, "gold_avg_spot": round(spot_q.loc[q, "avg"]),
                    "gold_yoy_spot_pct": round(gs, 1), "gold_yoy_blended110_pct": round(g110, 1),
                    "gold_yoy_blended180_pct": round(g180, 1),
                    "unmitigated_bps_s20": round(unmit[0.20]), "unmitigated_bps_s25": round(unmit[0.25]), "unmitigated_bps_s30": round(unmit[0.30]),
                    "offset_ratio_calibrated_s25": (round(offset, 3) if not np.isnan(offset) else np.nan),
                    "net_gold_drag_bps": round(net_gold),
                    "hedge_reclass_musd_h2w": round(rec["H2-weighted 20/40/40"][0], 1), "hedge_reclass_bps_h2w": round(rec["H2-weighted 20/40/40"][1]),
                    "hedge_reclass_musd_salesw": round(rec["sales-weighted 12 mo"][0], 1), "hedge_reclass_bps_salesw": round(rec["sales-weighted 12 mo"][1]),
                    "prior_year_reclass_bps": round(base_reclass_bps),
                    "one_off_lap_bps": round(lap_bps), "tariff_yoy_bps": round(tariff_bps),
                    "modelled_bps_before_promo_h2w": round(rec["H2-weighted 20/40/40"][2]),
                    "modelled_bps_before_promo_salesw": round(rec["sales-weighted 12 mo"][2]),
                    "guide_language": {"FY2027Q1": "actual -70 bps", "FY2027Q2": "'somewhat lower'",
                                       "FY2027Q3": "'flat to slightly up' (H2)", "FY2027Q4": "'flat to slightly up' (H2)"}[q]})
scen = pd.DataFrame(out)
scen.to_csv(f"{HERE}\\gold_scenarios_h2fy27.csv", index=False)

# full quarterly ledger (actual gold, blended, y/y, merch margin, hedge) FY25Q1 -> FY27Q2
ledger = pd.DataFrame({"quarter": g_spot.index})
ledger["gold_avg_spot"] = g_spot["avg"].values.round(0)
ledger["gold_yoy_spot_pct"] = g_spot["yoy"].values.round(1)
ledger["gold_avg_blended110"] = g_110["avg"].values.round(0)
ledger["gold_yoy_blended110_pct"] = g_110["yoy"].values.round(1)
ledger["gold_yoy_blended180_pct"] = g_180["yoy"].values.round(1)
ledger = ledger[ledger["quarter"].isin([f"FY{y}Q{q}" for y in (2025, 2026, 2027) for q in (1, 2, 3, 4)])]
ledger = ledger.merge(kpi[["quarter", "merch_margin_bps_yoy", "gross_margin_bps_yoy", "merch_aur_pct", "sss_pct"]], on="quarter", how="left")
hedge_q = {"FY2026Q4": "35,000 oz; AOCI $35.8M; reclass $2.9M FY", "FY2027Q1": "26,000 oz; AOCI $32.6M; reclass $2.3M; $30.3M queued"}
ledger["hedge_book"] = ledger["quarter"].map(hedge_q)
ledger.to_csv(f"{HERE}\\gold_ledger_quarterly.csv", index=False)

# ================================================================ CHARTS
import textwrap
plt.rcParams.update({"font.family": "DejaVu Sans", "axes.edgecolor": INK2, "axes.labelcolor": INK2,
                     "xtick.color": INK2, "ytick.color": INK2})

def style(ax, ylabel=None):
    ax.set_facecolor(SURFACE)
    for sp in ("top", "right", "left"): ax.spines[sp].set_visible(False)
    ax.spines["bottom"].set_alpha(0.4)
    ax.grid(axis="y", color=GRID, linewidth=0.8, zorder=0)
    ax.tick_params(length=0, labelsize=9)
    if ylabel: ax.set_ylabel(ylabel, fontsize=9, color=INK2)

def esc(t):  # matplotlib treats $...$ as mathtext
    return t.replace("$", r"\$")

def wrap(t, n=175):
    return "\n".join(textwrap.wrap(t, n))

qlabels = [q.replace("FY20", "FY").replace("Q", " Q") for q in kpi["quarter"]]
x = np.arange(len(kpi))

# ---------------- Exhibit 1a: the scissors (three small multiples, one axis each) ----------------
fig, axes = plt.subplots(3, 1, figsize=(12.5, 9.2), dpi=200, sharex=True,
                         gridspec_kw={"height_ratios": [1.15, 1, 1], "hspace": 0.30})
fig.patch.set_facecolor(SURFACE)

ax = axes[0]; style(ax, "merch. margin, bps y/y")
mm = kpi["merch_margin_bps_yoy"].values
colors = [BLUE if (not np.isnan(v) and v >= 0) else RED for v in mm]
ax.bar(x, np.nan_to_num(mm), width=0.55, color=colors, zorder=3, linewidth=0)
for i, v in enumerate(mm):
    if np.isnan(v):
        ax.text(x[i], 6, "modest\nexpansion\n(no number)", ha="center", va="bottom", fontsize=8, color=INK2)
    else:
        ax.text(x[i], v + (8 if v >= 0 else -8), f"{v:+.0f}", ha="center", va="bottom" if v >= 0 else "top", fontsize=9, color=INK)
ax.axhline(0, color=INK2, linewidth=0.8, alpha=0.6, zorder=2)
ax.set_ylim(-110, 150); ax.set_xlim(-0.6, len(kpi) - 0.4 + 1.3)
ax.set_title("Merchandise margin expanded through +40% gold, then broke when gold in inventory cost passed +50%",
             loc="left", fontsize=12.5, fontweight="bold", color=INK, pad=10)
ax.text(x[-1] + 0.5, 130, "Q2 FY27 guide:\n“somewhat lower”\nH2 FY27 guide:\n“flat to slightly up”", fontsize=8.5, color=INK2, va="top")

ax = axes[1]; style(ax, "merchandise AUR, % y/y")
aur = kpi["merch_aur_pct"].values
mask = ~np.isnan(aur)
ax.plot(x[mask], aur[mask], color=BLUE, linewidth=2, marker="o", markersize=7, markeredgecolor=SURFACE, markeredgewidth=1.5, zorder=3)
for i in np.where(mask)[0]:
    ax.text(x[i], aur[i] + 0.55, "+4.5%" if aur[i] == 4.5 else f"+{aur[i]:.0f}%", ha="center", fontsize=9, color=INK)
ax.text(-0.45, 1.2, "ATV era, no AUR disclosed:\nQ1 ATV down slightly · Q2 ATV up\nQ3 fashion ATV +MSD, bridal ATV −MSD",
        ha="left", va="bottom", fontsize=7.6, color=INK2, linespacing=1.25)
ax.set_ylim(0, 11)
ax.text(3.0, 9.9, "AUR-era disclosure begins Q4 FY25", fontsize=8, color=INK2, ha="center")

ax = axes[2]; style(ax, "gold, % y/y")
gs_ = kpi["gold_yoy_spot_pct"].values; gb = kpi["gold_yoy_blended110_pct"].values
ax.plot(x, gs_, color=ORANGE, linewidth=2, marker="o", markersize=6, markeredgecolor=SURFACE, markeredgewidth=1.5, zorder=3, label="spot, fiscal-quarter average")
ax.plot(x, gb, color=BLUE, linewidth=2, marker="s", markersize=6, markeredgecolor=SURFACE, markeredgewidth=1.5, zorder=3, label="in inventory cost (weighted-average proxy, 110-day pool)")
ax.text(x[-1] + 0.15, gs_[-1] + 4, f"+{gs_[-1]:.0f}% spot", fontsize=8.5, color=INK, va="center")
ax.text(x[-1] + 0.15, gb[-1] - 5, f"+{gb[-1]:.0f}% in cost", fontsize=8.5, color=INK, va="center")
ax.legend(loc="upper left", fontsize=8.5, frameon=False)
ax.set_ylim(0, 80)
ax.set_xticks(x); ax.set_xticklabels(qlabels, fontsize=9)
fig.text(0.125, 0.015, wrap(esc(
    "Sources: Signet earnings calls FY25 Q1–FY27 Q1 (Bloomberg transcripts; line references in kpi_panel_quarterly.csv); Q1 FY27 10-Q; COMEX GC=F monthly averages. "
    "Q4 FY25 merchandise margin was described as 'modest expansion' without a number. Blended gold = EWMA of monthly gold with a 110-day time constant (Signet uses weighted-average cost).")),
    fontsize=7.4, color=INK2)
fig.savefig(f"{HERE}\\exhibit_kpi_scissors.png", facecolor=SURFACE, bbox_inches="tight", pad_inches=0.25)
plt.close(fig)

# ---------------- Exhibit 1b: implied unit comps ----------------
fig, ax = plt.subplots(figsize=(11.5, 5.4), dpi=200); fig.patch.set_facecolor(SURFACE); style(ax, "% y/y")
sub = kpi[~kpi["implied_units_pct"].isna()].reset_index(drop=True)
xs = np.arange(len(sub))
iu = sub["implied_units_pct"].values
ax.bar(xs - 0.18, iu, width=0.34, color=BLUE, zorder=3, linewidth=0, label="Signet implied unit comp = (1+comp)/(1+AUR) − 1")
tu = sub["tenoris_units_yoy"].values
ax.bar(xs + 0.18, np.nan_to_num(tu), width=0.34, color=ORANGE, zorder=3, linewidth=0, label="Tenoris independent-jeweler units (category, ex-Signet)")
for i, v in enumerate(iu):
    ax.text(xs[i] - 0.18, v - 0.35, f"{v:+.1f}%", ha="center", va="top", fontsize=9, color=INK)
for i, v in enumerate(tu):
    if not np.isnan(v):
        ax.text(xs[i] + 0.18, v - 0.35, f"{v:+.0f}%", ha="center", va="top", fontsize=8.5, color=INK2)
    else:
        ax.text(xs[i] + 0.18, -0.6, "n/a", ha="center", va="top", fontsize=8, color=INK2)
notes = {"FY2026Q2": "mgmt: units −7%", "FY2026Q3": "mgmt: down,\nimproved seq.",
         "FY2026Q4": "mgmt: LSD\ndeclines", "FY2027Q1": "mgmt: +3 pts\nvs Q4 (≈−2.4)"}
for i, r in sub.iterrows():
    if r["quarter"] in notes:
        ax.text(xs[i] - 0.18, 0.4, notes[r["quarter"]], ha="center", va="bottom", fontsize=7.6, color=INK2, linespacing=1.2)
ax.axhline(0, color=INK2, linewidth=0.8, alpha=0.6, zorder=2)
ax.set_ylim(-12.5, 3.2); ax.set_xlim(-0.6, len(sub) - 0.4)
ax.set_xticks(xs); ax.set_xticklabels([q.replace("FY20", "FY").replace("Q", " Q") for q in sub["quarter"]], fontsize=9.5)
ax.legend(loc="lower left", fontsize=8.5, frameon=False)
ax.set_title("Derived unit comps reconcile to management's words and improved from −7.6% to −2.6%;\nthe first print ≥ 0 retires the 'pricing masking volume' bear",
             loc="left", fontsize=11.5, fontweight="bold", color=INK, pad=10)
fig.text(0.125, 0.005, wrap(esc(
    "Sources: same-store sales from 8-K Ex-99.1 releases; merchandise AUR from the calls (Q1 FY27 uses the 10-Q's 4.5%); Tenoris monthly posts averaged by Signet fiscal quarter (panel excludes Signet banners). "
    "Comps include services (~12% of sales, growing HSD), so merchandise units run ~0.5–1 pt worse than shown."), 150), fontsize=7.4, color=INK2)
fig.savefig(f"{HERE}\\exhibit_implied_units.png", facecolor=SURFACE, bbox_inches="tight", pad_inches=0.25)
plt.close(fig)

# ---------------- Exhibit 2: gold ledger + H2 bridge ----------------
fig = plt.figure(figsize=(13.5, 7.4), dpi=200); fig.patch.set_facecolor(SURFACE)
fig.text(0.05, 0.955, "The gold headwind in Signet's cost of goods peaks in Q1–Q2 FY27 and is close to zero by the holiday quarter at spot",
         fontsize=12.5, fontweight="bold", color=INK, va="top")
axl = fig.add_axes([0.05, 0.16, 0.50, 0.70]); style(axl, "gold in inventory cost, % y/y (110-day pool)")
qs = ["FY2026Q1", "FY2026Q2", "FY2026Q3", "FY2026Q4", "FY2027Q1", "FY2027Q2", "FY2027Q3", "FY2027Q4"]
xl = np.arange(len(qs))
base_tab = scen_tables["gold $4,400 (~spot)"][1]
actual_b = [base_tab.loc[q, "yoy"] for q in qs]
axl.plot(xl[:6], actual_b[:6], color=BLUE, linewidth=2.2, marker="s", markersize=6, markeredgecolor=SURFACE, markeredgewidth=1.5, zorder=4, label="actual (Q2 FY27 uses May–Jul actual gold)")
for name, col in zip(scen_prices, (AQUA, BLUE, ORANGE)):
    t = scen_tables[name][1]
    ys = [t.loc[q, "yoy"] for q in qs]
    axl.plot(xl[5:], ys[5:], color=col, linewidth=2, linestyle="--", marker="o", markersize=5.5, markeredgecolor=SURFACE, markeredgewidth=1.5, zorder=3, label=esc(f"{name} from Sept"))
    axl.text(xl[-1] + 0.12, ys[-1], f"{ys[-1]:+.0f}%", fontsize=8.5, color=INK, va="center")
mmv = kpi.set_index("quarter")["merch_margin_bps_yoy"]
for i, q in enumerate(qs[:5]):
    v = mmv.get(q, np.nan)
    if not np.isnan(v):
        if i == 3:
            axl.text(xl[i] - 0.12, actual_b[i] + 1.0, f"margin {v:+.0f} bps", fontsize=7.8, color=INK2, ha="right", va="center")
        else:
            axl.text(xl[i], actual_b[i] + 3.5, f"margin {v:+.0f} bps", fontsize=7.8, color=INK2, ha="center")
axl.axhline(0, color=INK2, linewidth=0.8, alpha=0.6)
axl.set_xticks(xl); axl.set_xticklabels([q.replace("FY20", "FY").replace("Q", " Q") for q in qs], fontsize=8.5)
axl.set_ylim(-15, 75); axl.set_xlim(-0.5, 7.9)
axl.legend(loc="upper left", fontsize=8, frameon=False)
axl.axvspan(5.5, 7.5, color=BLUE_L, alpha=0.18, zorder=0)
axl.text(6.5, 70, "H2 FY27: guide ‘flat to slightly up’", ha="center", fontsize=8.5, color=INK2)

axr = fig.add_axes([0.60, 0.05, 0.39, 0.86]); axr.axis("off"); axr.set_xlim(0, 1); axr.set_ylim(0, 1)
tiles = [
    ("0 oz → 35k → 26k", "hedged gold: none FY22–FY25; program restarted Q2 FY26; 35,000 oz at\n1/31/26 and 26,000 oz at 5/2/26, settling over the next 11 months"),
    (f"~{cover[0.25]:.0f}% of purchases", f"cover while contracts run (to ~Apr 2027): 2,364 oz/month vs ~{merch_expense_fy26*0.25/4400/12*1000:.0f}k oz/month\nneeded at a 25% gold share of merchandise cost (range {cover[0.30]:.0f}–{cover[0.20]:.0f}% for 30–20%)"),
    ("$30.3M queued", f"pre-tax hedge gains expected to reach COGS within 12 months of 5/2/26;\n${aoci_locked:.1f}M of the $32.6M in AOCI is on settled contracts (sits in inventory)"),
    ("−70 bps ⇒ ~89% offset", "Q1 FY27: gold in cost +60% y/y ⇒ ~−670 bps unmitigated at a 25% gold share;\nobserved −70 bps ⇒ pricing / mix / melt offset ~89% of it"),
]
y0 = 0.92
for big, small in tiles:
    axr.text(0.0, y0, esc(big), fontsize=12, color=BLUE, fontweight="bold", va="top")
    axr.text(0.0, y0 - 0.05, esc(small), fontsize=7.3, color=INK2, va="top", linespacing=1.3)
    y0 -= 0.122
axr.text(0.0, 0.405, esc("Modelled merch-margin y/y before promo / mix lapping (bps), gold $4,400 from Sept"), fontsize=8.2, color=INK, fontweight="bold", va="top")
sb = scen[scen["scenario"] == "gold $4,400 (~spot)"].set_index("quarter")
Q = ("FY2027Q2", "FY2027Q3", "FY2027Q4")
rowsT = [("gold in inventory cost, y/y", [f"{sb.loc[q,'gold_yoy_blended110_pct']:+.0f}%" for q in Q], False),
         ("net gold drag (scaled from Q1's −70)", [f"{sb.loc[q,'net_gold_drag_bps']:+.0f}" for q in Q], False),
         ("hedge reclass, H2-weighted 20/40/40", [f"{sb.loc[q,'hedge_reclass_bps_h2w']:+.0f}" for q in Q], False),
         ("hedge reclass, sales-weighted 12 mo", [f"{sb.loc[q,'hedge_reclass_bps_salesw']:+.0f}" for q in Q], False),
         ("lap of Q2 FY26 one-off (−70) / tariff y/y", [f"{sb.loc[q,'one_off_lap_bps']:+.0f} / {sb.loc[q,'tariff_yoy_bps']:+.0f}" for q in Q], False),
         ("= modelled, H2-weighted", [f"{sb.loc[q,'modelled_bps_before_promo_h2w']:+.0f}" for q in Q], True),
         ("= modelled, sales-weighted", [f"{sb.loc[q,'modelled_bps_before_promo_salesw']:+.0f}" for q in Q], True),
         ("guide language", ["lower", "flat to up", "flat to up"], False)]
yy = 0.355
for j, h in enumerate(("Q2 FY27", "Q3 FY27", "Q4 FY27")):
    axr.text(0.56 + j * 0.15, yy, h, fontsize=8, color=INK2, ha="center")
for label, vals, bold in rowsT:
    yy -= 0.035
    axr.text(0.0, yy, esc(label), fontsize=7.9, color=INK, fontweight="bold" if bold else "normal")
    for j, v in enumerate(vals):
        axr.text(0.56 + j * 0.15, yy, v, fontsize=7.9, color=INK, ha="center", fontweight="bold" if bold else "normal")
fig.text(0.05, 0.02, wrap(esc(
    "Sources: FY23–FY26 10-Ks and Q1 FY27 10-Q (derivatives notes, Item 7A, segment expense); earnings calls; COMEX GC=F. Gold share of merchandise cost is NOT disclosed (25% is expert inference; the projection is insensitive to it because the drag is scaled from the observed Q1 print). "
    "Reclass phasing is an assumption ('the back half begins to neutralize', Q4 FY26 call). Tariff y/y is roughly neutral from Q3 (lapping the Aug-2025 start). Not modelled: promo lapping, mix, melt — the residual the guide requires."), 200),
    fontsize=7.2, color=INK2)
fig.savefig(f"{HERE}\\exhibit_gold_bridge.png", facecolor=SURFACE, bbox_inches="tight", pad_inches=0.25)
plt.close(fig)

# ---------------- console summary ----------------
pd.set_option("display.width", 240); pd.set_option("display.max_columns", 40)
print("SCENARIOS:")
print(scen[["scenario","quarter","gold_avg_spot","gold_yoy_spot_pct","gold_yoy_blended110_pct","gold_yoy_blended180_pct","unmitigated_bps_s25","offset_ratio_calibrated_s25","net_gold_drag_bps","hedge_reclass_bps_h2w","hedge_reclass_bps_salesw","prior_year_reclass_bps","one_off_lap_bps","tariff_yoy_bps","modelled_bps_before_promo_h2w","modelled_bps_before_promo_salesw","guide_language"]].to_string(index=False))
print(f"\ncover by gold share: { {k: round(v,1) for k,v in cover.items()} }  aoci locked in inventory: {aoci_locked:.1f}  merch expense FY26 {merch_expense_fy26}")
