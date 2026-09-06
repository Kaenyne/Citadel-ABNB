"""Workstream 10, part 4: bottom-up regional nights forecast for 3Q26, 4Q26 and FY27, aggregated to total nights,
GBV and revenue, and checked against the 3Q26 guide and the driver model's FY27 base.

Reads
  data/processed/overnight/10_regional_panel_quarterly.csv   regional nights growth, shares, reconciliation residual
  data/processed/overnight/10_regional_benchmarks.csv        aligned external benchmarks
  data/processed/overnight/10_regional_adr_fx.csv            reported vs ex-FX regional ADR and the FX basket
  data/processed/overnight/10_fx_basket.csv                  regional FX baskets, 3Q26 QTD to 28 Aug 2026
  data/processed/abnb_driver_history_quarterly.csv           reported nights / GBV / ADR / revenue / take rate
Writes
  data/processed/overnight/10_regional_fx_passthrough.csv    FX-basket -> reported-ADR pass-through by region (slope, r, n)
  data/processed/overnight/10_regional_forecast.csv          nights growth by region x period x scenario, plus aggregates
  analysis/figures/overnight/10_regional_forecast.png
Run: py -3.13 analysis/src/overnight/10_regional_forecast.py

Method
  * Nights shares are carried forward from the 2Q26 estimate by extrapolating the observed drift of the last four
    quarters (NA and EMEA losing share to LatAm and APAC), then renormalised.
  * Regional growth is set in the same units the letters use (bucket midpoints). Those midpoints have run about
    0.4pp hot against reported total nights over the last four quarters, so the aggregate carries an explicit
    calibration of -0.41pp (the trailing-four-quarter mean reconciliation residual).
  * Revenue = nights x ADR ex-FX x FX x take rate. The FX line uses the regional baskets weighted by revenue share,
    with the caveat that the 3Q26 guide's "approximately three percentage point FX tailwind after factoring in our
    hedging program" is larger than spot implies, because hedges and check-in-basis recognition lag spot.
"""
import os
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
OUT = os.path.join(ROOT, "data", "processed", "overnight")
FIG = os.path.join(ROOT, "analysis", "figures", "overnight")
os.makedirs(FIG, exist_ok=True)
REGIONS = ["na", "emea", "latam", "apac"]

panel = pd.read_csv(os.path.join(OUT, "10_regional_panel_quarterly.csv")).set_index("quarter")
drv = pd.read_csv(os.path.join(ROOT, "data", "processed", "abnb_driver_history_quarterly.csv")).set_index("quarter")

# ------------------------------------------------------------------ 1. FX basket -> reported ADR pass-through
adrfx = pd.read_csv(os.path.join(OUT, "10_regional_adr_fx.csv")).dropna(subset=["fx_gap_pp", "basket_fx_yoy_pct"])
rows = []
for r, g in adrfx.groupby("region"):
    slope, intercept = np.polyfit(g.basket_fx_yoy_pct, g.fx_gap_pp, 1)
    rr = float(np.corrcoef(g.basket_fx_yoy_pct, g.fx_gap_pp)[0, 1])
    rows.append(dict(region=r, n=len(g), r=round(rr, 3), slope_pp_per_pp=round(float(slope), 3),
                     intercept_pp=round(float(intercept), 2),
                     basket_range_pp=round(float(g.basket_fx_yoy_pct.max() - g.basket_fx_yoy_pct.min()), 1),
                     first_quarter=g.quarter.iloc[0], last_quarter=g.quarter.iloc[-1]))
slope_p, int_p = np.polyfit(adrfx.basket_fx_yoy_pct, adrfx.fx_gap_pp, 1)
rows.append(dict(region="pooled", n=len(adrfx), r=round(float(np.corrcoef(adrfx.basket_fx_yoy_pct, adrfx.fx_gap_pp)[0, 1]), 3),
                 slope_pp_per_pp=round(float(slope_p), 3), intercept_pp=round(float(int_p), 2),
                 basket_range_pp=round(float(adrfx.basket_fx_yoy_pct.max() - adrfx.basket_fx_yoy_pct.min()), 1),
                 first_quarter=adrfx.quarter.min(), last_quarter=adrfx.quarter.max()))
fxpt = pd.DataFrame(rows)
fxpt["note"] = np.where(fxpt.region == "na",
                        "not identified: the NA basket moves less than 1.5pp across the sample, so the slope is noise",
                        "reported-ADR minus ex-FX-ADR gap regressed on the region's FX basket y/y")
fxpt.to_csv(os.path.join(OUT, "10_regional_fx_passthrough.csv"), index=False)
print(fxpt.to_string(index=False))
PASS = {r: float(fxpt.loc[fxpt.region == r, "slope_pp_per_pp"].iloc[0]) for r in REGIONS}
PASS["na"] = 1.0   # not identified from the data; assume full pass-through on the ~10% of NA GBV that is not USD

# ------------------------------------------------------------------ 2. share drift and reconciliation calibration
sh_now = {r: float(panel.loc["2Q26", f"{r}_nights_share_est_pct"]) for r in REGIONS}
drift = {r: (float(panel.loc["2Q26", f"{r}_nights_share_est_pct"]) - float(panel.loc["2Q25", f"{r}_nights_share_est_pct"])) / 4
         for r in REGIONS}   # pp per quarter over the last year


def shares(qtrs_ahead):
    s = {r: sh_now[r] + drift[r] * qtrs_ahead for r in REGIONS}
    t = sum(s.values())
    return {r: s[r] / t * 100 for r in s}


CALIB = float(panel.loc[["3Q25", "4Q25", "1Q26", "2Q26"], "residual_vs_total_pp"].mean())
print("\nshare drift pp/qtr:", {k: round(v, 3) for k, v in drift.items()},
      "\ncalibration (mean residual, last 4q):", round(CALIB, 2), "pp")

# ------------------------------------------------------------------ 3. scenario assumptions
# nights y/y % in letter-bucket units, by period x region x scenario
F = {
 "3Q26": {
   "na":    dict(bear=5, base=7, bull=9,
                 rationale="2Q26 +8% (high-single, best in ~3 years). Tailwinds: Canadian returns from the US turned positive (StatCan Apr +1.8%, May +9.9%, Jun +5.0% vs -28/-31/-28% a year earlier) and BEA inbound foreign travel in the US is back to -0.6% in Jul 2026 from -9.9% in 3Q25. Headwinds: 3Q25 was itself the Reserve Now Pay Later acceleration quarter, and World Cup stay nights were BOOKED in 4Q25-2Q26, so 3Q26 nights booked gets no event lift."),
   "emea":  dict(bear=6, base=8, bull=10,
                 rationale="2Q26 +8% and accelerating; Middle East cancellations that cost ~100bp of group nights in 1Q26 have unwound. Easy comp: 3Q25 was mid-single with an unfavourable Paris-2024 base. No public read on 3Q26: Eurostat platform nights stop at Mar 2026 and run ~150 days late; the first external check is BKNG's late-October print."),
   "latam": dict(bear=15, base=18, bull=21,
                 rationale="2Q26 ~20% with Brazil origin net nights >30% and Mexico helped by June installment payments. Comp tightens (3Q25 low-20s) and the BRL/MXN basket tailwind halves to +6.4% y/y in 3Q26 QTD from +11.4% in 2Q26."),
   "apac":  dict(bear=14, base=17, bull=19,
                 rationale="2Q26 high-teens on India origin +60% and Japan origin high-teens. Risk flag: JNTO inbound arrivals to Japan are now roughly flat (Jul 2026 +0.1%, 2Q26 -5.3%) on a China collapse (-45 to -60% y/y Jan-Mar), so the region's growth is entirely origin/domestic, not inbound."),
 },
 "4Q26": {
   "na":    dict(bear=4, base=7, bull=9, rationale="Canada comp stays easy (4Q25 Canadian returns from the US -25%); US inbound comp turns neutral. Underlying NA demand mid-single with product-led lift."),
   "emea":  dict(bear=5, base=7, bull=9, rationale="4Q25 was high-single, the toughest EMEA comp of the last two years; FX turns from tailwind to small headwind (EUR -1.6% y/y in 3Q26 QTD)."),
   "latam": dict(bear=14, base=18, bull=21, rationale="Brazil origin has run >20% for five consecutive quarters and accelerated to >30% in 2Q26; expansion-market playbook plus installments in Brazil and Mexico. Comp 4Q25 high-teens."),
   "apac":  dict(bear=13, base=17, bull=19, rationale="India origin ~50-60% off a small base, Japan origin high-teens; comp 4Q25 mid-teens."),
 },
 "FY27": {
   "na":    dict(bear=3, base=6, bull=8, rationale="Canada/inbound base effects are fully lapped by 2Q27, so FY27 NA is underlying demand plus product. Structural ceiling: NA is ~29% of nights and the most penetrated region."),
   "emea":  dict(bear=4, base=7, bull=9, rationale="Eurostat EU27 platform nights have run +8 to +11% y/y through 1Q26, above ABNB EMEA's mid-to-high single digit, i.e. ABNB has been losing share of EU platform nights; base assumes that gap stops widening, bear assumes it continues."),
   "latam": dict(bear=12, base=16, bull=19, rationale="Expansion markets have grown at roughly twice core for ten consecutive quarters. Base decays LatAm from ~20% toward 16% as the base grows; bull keeps the Brazil/Mexico engine near 19%."),
   "apac":  dict(bear=11, base=15, bull=18, rationale="India is the fastest-growing origin country; Japan domestic remains strong. Bear reflects the Japan inbound rollover spreading to intra-APAC travel."),
 },
}
AHEAD = {"3Q26": 1, "4Q26": 2, "FY27": 5}   # quarters beyond 2Q26 for the share extrapolation (FY27 midpoint)

# ADR ex-FX, FX and take-rate assumptions for the revenue bridge (global)
BRIDGE = {
 "3Q26": dict(bear=(2, 3.0), base=(3, 3.0), bull=(4, 3.5)),   # (ADR ex-FX y/y %, FX pp on revenue)
 "4Q26": dict(bear=(2, 0.5), base=(3, 1.0), bull=(4, 1.5)),
 "FY27": dict(bear=(1, -2.0), base=(3, 0.0), bull=(4, 1.0)),
}
# base revenue for the dollar translation
BASE_REV = {"3Q26": 4095.0, "4Q26": 2778.0, "FY27": None}   # 3Q25 and 4Q25 actual revenue, USD m
GUIDE = {"3Q26": "guide $4,690-4,770m (mid $4,730m = +15.5% on 3Q25's $4,095m; the letter states 15-17%). "
                 "Revenue has beaten the guide midpoint by a mean 2.2% over the last 12 quarters but by only "
                 "0.9% in each of the last two third quarters, so a Q3 beat of about 1% is the base.",
         "4Q26": "no 4Q26 guide yet; FY26 guide is revenue growth of at least mid teens, which the base case meets at +16.3%.",
         "FY27": "driver model base is +12% revenue (research/notes/2026-09-05_driver-model.md), bear +4%, bull +15%."}
FX_NOTE = {"3Q26": "guide says ~3pp FX tailwind to revenue after hedging; spot regional baskets weighted by revenue are only +0.3% y/y QTD to 28 Aug, so the tailwind is hedge and check-in-timing, not spot",
           "4Q26": "spot baskets imply roughly flat to +1pp; EUR is -1.6% y/y in 3Q26 QTD",
           "FY27": "no view on spot; base carries FX at zero, bear -2pp, bull +1pp"}

rows = []
for period, spec in F.items():
    sh = shares(AHEAD[period])
    for scen in ["bear", "base", "bull"]:
        wa = sum(sh[r] / 100 * spec[r][scen] for r in REGIONS)
        for r in REGIONS:
            rows.append(dict(period=period, region=r, scenario=scen, nights_yoy_pct=spec[r][scen],
                             nights_share_est_pct=round(sh[r], 1),
                             contribution_pp=round(sh[r] / 100 * spec[r][scen], 2),
                             rationale=spec[r]["rationale"]))
        total = wa + CALIB
        adr_exfx, fx_pp = BRIDGE[period][scen]
        gbv = (1 + total / 100) * (1 + adr_exfx / 100) - 1
        gbv_rep = gbv * 100 + fx_pp
        rows.append(dict(period=period, region="TOTAL", scenario=scen, nights_yoy_pct=round(total, 2),
                         nights_share_est_pct=100.0, contribution_pp=round(wa, 2),
                         rationale=(f"share-weighted regional nights {wa:.2f}% plus calibration {CALIB:+.2f}pp "
                                    f"(mean 3Q25-2Q26 reconciliation residual)"),
                         adr_exfx_yoy_pct=adr_exfx, fx_pp_on_revenue=fx_pp,
                         gbv_yoy_pct_exfx=round(gbv * 100, 2), gbv_yoy_pct_reported=round(gbv_rep, 2),
                         revenue_yoy_pct=round(gbv_rep, 2),
                         revenue_musd=(round(BASE_REV[period] * (1 + gbv_rep / 100)) if BASE_REV[period] else np.nan),
                         fx_note=FX_NOTE[period], guide_check=GUIDE[period]))
fc = pd.DataFrame(rows)

# benchmarks in hand at 6 Sep 2026, attached to the 3Q26 rows
PUBLIC = {
 "na": "BEA inbound foreign travel in the US Jun -1.4%, Jul -0.6% real y/y (3Q25 was -9.9%); BEA accommodations real Jun +1.5%, Jul +1.8%; StatCan Canadian returns from the US Apr +1.8%, May +9.9%, Jun +5.0%; Google Trends 'airbnb' US Jul -8.6%, Aug -4.5% y/y",
 "emea": "no 3Q26 read exists: Eurostat platform nights end Mar 2026 (1Q26 EU27 +9.7% y/y, foreign +10.1%); EUR/USD -1.6% y/y and GBP -0.2% y/y in 3Q26 QTD to 28 Aug",
 "latam": "BRL +6.2% and MXN +7.9% y/y in 3Q26 QTD (vs +12.3% and +12.2% in 2Q26): the LatAm reported-ADR FX tailwind roughly halves",
 "apac": "JNTO Japan inbound arrivals Jul 2026 +0.1% y/y (Jun -6.8%, May -3.6%); AUD +7.5%, JPY -8.2%, INR -8.7% y/y in 3Q26 QTD",
 "TOTAL": "3Q26 guide (2Q26 letter, 6 Aug 2026): revenue $4.69-4.77bn, +15-17% y/y including ~3pp FX tailwind after hedging; low double-digit Nights and Seats Booked growth; moderate ADR increase; FY26 revenue growth at least mid teens",
}
fc["public_benchmarks_as_of_2026_09_06"] = np.where(fc.period == "3Q26", fc.region.map(PUBLIC), "")
fc.to_csv(os.path.join(OUT, "10_regional_forecast.csv"), index=False)

t = fc[fc.region == "TOTAL"].set_index(["period", "scenario"])
print("\n" + t[["nights_yoy_pct", "adr_exfx_yoy_pct", "fx_pp_on_revenue", "gbv_yoy_pct_reported", "revenue_yoy_pct", "revenue_musd"]].to_string())
fy26 = 2678 + 3608 + float(t.loc[("3Q26", "base"), "revenue_musd"]) + float(t.loc[("4Q26", "base"), "revenue_musd"])
print("implied FY26 revenue (base):", round(fy26), "USD m, +" + str(round(fy26 / 12241 * 100 - 100, 1)), "% vs FY25 12,241")
print("\n3Q26 guide: nights low double-digit (10-12%), revenue +15-17%.")
print("FY27 driver-model base +12% revenue (research/notes/2026-09-05_driver-model.md); bottom-up base",
      round(float(t.loc[("FY27", "base"), "revenue_yoy_pct"]), 1), "%")

# ------------------------------------------------------------------ 4. figure
ORDER = list(panel.index)
hist = ORDER[ORDER.index("4Q22"):]   # positional: string comparison would keep only the fourth quarters
fig, axes = plt.subplots(1, 2, figsize=(13, 5))
ax = axes[0]
cols = {"na": "#1f4e79", "emea": "#2e8b57", "latam": "#c0392b", "apac": "#8e44ad"}
for r, c in cols.items():
    ax.plot(hist, panel.loc[hist, f"{r}_nights_yoy_mid"], marker="o", ms=3, color=c, label=r.upper())
    xs = ["3Q26", "4Q26"]
    base = [F[p][r]["base"] for p in xs]
    lo = [F[p][r]["bear"] for p in xs]
    hi = [F[p][r]["bull"] for p in xs]
    ax.plot([hist[-1]] + xs, [panel.loc[hist[-1], f"{r}_nights_yoy_mid"]] + base, ls="--", color=c)
    ax.fill_between(xs, lo, hi, color=c, alpha=0.15)
ax.plot(hist, panel.loc[hist, "total_nights_yoy_pct"], color="black", lw=2, label="Total (reported)")
ax.axvline(len(hist) - 0.5, color="grey", lw=0.8)
ax.set_ylabel("Nights booked y/y, %"); ax.set_title("Regional nights: history and 3Q26/4Q26 scenarios")
ax.legend(fontsize=8); ax.grid(alpha=0.3); ax.tick_params(axis="x", rotation=60)

ax = axes[1]
bm = pd.read_csv(os.path.join(OUT, "10_regional_benchmarks.csv")).set_index("quarter")
qs = list(bm.index)[list(bm.index).index("4Q23"):]
ax.plot(qs, bm.loc[qs, "na_nights_yoy_mid"], marker="o", ms=3, color="#1f4e79", label="ABNB NA nights y/y")
ax.plot(qs, bm.loc[qs, "bea_inbound_foreign_travel_in_us_real_yoy_pct"], color="#e67e22", label="BEA inbound foreign travel in US, real")
ax.plot(qs, bm.loc[qs, "statcan_cdn_returning_from_us_yoy_pct"], color="#7f8c8d", label="Canadians returning from the US (StatCan)")
ax.axhline(0, color="black", lw=0.6)
ax.set_ylabel("y/y, %"); ax.set_title("North America: the inbound-to-US drag and its reversal")
ax.legend(fontsize=8); ax.grid(alpha=0.3); ax.tick_params(axis="x", rotation=60)
fig.text(0.01, 0.005, "Source: Airbnb shareholder letters; BEA monthly PCE travel; Statistics Canada 24-10-0053; Citadel-ABNB analysis", fontsize=7, color="grey")
fig.tight_layout()
fig.savefig(os.path.join(FIG, "10_regional_forecast.png"), dpi=150)
plt.close(fig)
print("\nwrote", os.path.join(FIG, "10_regional_forecast.png"))
