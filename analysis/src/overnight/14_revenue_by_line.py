"""Workstream 14: the revenue model restructured by business line.

WHY
  The driver model (13) forecasts revenue as printed-KPI arithmetic: Nights and Seats Booked x
  blended ADR x blended take rate, plus a "new business outside GBV" line for Services and ads.
  That works while the mix is stable and breaks as it moves: hotel nights (~0.8x a home night,
  ~11% commission), Experiences seats (~0.4x, 20% host fee) and Services seats (~0.7x, 15% host
  fee) are all inside the printed nights, GBV and take-rate figures, so every blended input is
  moving for mix reasons at once. This build runs the economics by line and lets the printed
  KPIs fall out as outputs:

      stays        home nights      x home ADR      x stays take rate   (x revenue-FX wedge)
      hotels       hotel nights     x hotel ADR     x hotel commission
      experiences  seats            x ticket        x 20%
      services     seats            x ticket        x 15%
      ads          sponsored listings, outside GBV (WS11)
      ---------------------------------------------------------------
      Nights and Seats Booked = sum of units;  GBV = sum of unit x price;  blended ADR and
      blended take rate are outputs, reported next to the driver model's for reconciliation.

WHAT IT SHARES WITH 13
  The printed Nights and Seats total per quarter comes from 13's regional build, unchanged,
  because WS10's regional growth buckets are read off the printed KPI. Home nights are the
  residual after hotels and seats. Home ADR ex-FX defaults to 13's blended ADR ex-FX plus the
  seats-dilution drag (15), so the printed ADR reconciles to 13; the ADR workbook's own case
  path (5_Forecast, ex the new-business row) can be substituted with --adr-workbook.
  FX, take-rate bps, hotel/seat volumes and tickets come from 13, 15 and 11.

READS
  analysis/src/overnight/13_driver_model.py       (imported: actuals, inputs, build_quarters)
  data/processed/adr/15_seats_dilution_annual.csv (hotel nights, seats, price ratios by case)
  data/processed/overnight/11_new_business_scenarios.csv
  data/processed/overnight/13_model_quarterly.csv, 13_model_annual.csv (reconciliation)

WRITES
  data/processed/overnight/14_revenue_by_line_quarterly.csv   3Q26-4Q27 x case x line
  data/processed/overnight/14_revenue_by_line_annual.csv      FY24-FY28 x case x line
  data/processed/overnight/14_revenue_by_line_kpis.csv        printed KPIs implied, vs 13
  model/ABNB_revenue_by_line.xlsx                             live-formula workbook

RUN   py -3.13 analysis/src/overnight/14_revenue_by_line.py [--adr-workbook]
"""
from __future__ import annotations

import argparse
import importlib.util
import os
import sys

import pandas as pd
import xlsxwriter

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
P = lambda *a: os.path.join(ROOT, *a)
OD = lambda n: P("data", "processed", "overnight", n)

spec = importlib.util.spec_from_file_location("dm", P("analysis", "src", "overnight", "13_driver_model.py"))
dm = importlib.util.module_from_spec(spec)
spec.loader.exec_module(dm)

SCEN = ["Bear", "Base", "Bull"]
BIZ = {"Bear": "bear", "Base": "base", "Bull": "bull"}       # 11's case labels
FQ, PRIOR_Q, QYEAR = dm.FQ, dm.PRIOR_Q, dm.QYEAR
LINES = ["stays", "hotels", "experiences", "services", "ads"]

# ---- line economics (11_new_business_scenarios assumptions; 15 for tickets and hotel path) --------
TAKE = dict(hotels=0.11, experiences=0.20, services=0.15)
TICKET = dict(experiences=75.0, services=120.0)
HOTEL_ADR_FY25 = 140.0
HOTEL_NIGHTS_FY25 = 18.7
HOTEL_GROWTH = dict(Bear=(0.20, 0.16, 0.16), Base=(0.35, 0.30, 0.25), Bull=(0.50, 0.45, 0.40))
EXP_GBV_FY24 = 400.0
# ADR-workbook home ADR ex-FX path (5_Forecast rows summed EX the new-business mix row), FY27 avg
ADR_WB_HOME_EXFX = dict(Bear=-1.15, Base=1.94, Bull=4.23)

# quarter share of a year's nights, 2023-25 mean, from 13 (used to spread seats and hotel nights)
SEAS = {qn: dm.SEAS_SHARE[qn][0] / 100.0 for qn in ["1Q", "2Q", "3Q", "4Q"]}


def nb_rev(case, biz, year):
    nb = pd.read_csv(OD("11_new_business_scenarios.csv"))
    r = nb[nb.business.eq(biz) & nb.case.eq(BIZ[case])]
    return float(r[f"fy{year % 100}_rev_musd"].iloc[0]) if len(r) else 0.0


def annual_units(case):
    """Hotel nights, experiences seats, services seats by year FY24-FY28, $M GBV and units (M)."""
    out = {}
    hot = [HOTEL_NIGHTS_FY25 / 1.30, HOTEL_NIGHTS_FY25]
    for g in HOTEL_GROWTH[case]:
        hot.append(hot[-1] * (1 + g))
    for i, y in enumerate([2024, 2025, 2026, 2027, 2028]):
        exp_gbv = EXP_GBV_FY24 if y == 2024 else nb_rev(case, "experiences", y) / TAKE["experiences"]
        svc_gbv = 0.0 if y == 2024 else nb_rev(case, "services", y) / TAKE["services"]
        out[y] = dict(hotel_nights=hot[i], exp_gbv=exp_gbv, exp_seats=exp_gbv / TICKET["experiences"],
                      svc_gbv=svc_gbv, svc_seats=svc_gbv / TICKET["services"],
                      ads_rev=nb_rev(case, "sponsored_listings_ads", y) if y >= 2025 else 0.0)
    return out


def base_quarters(case):
    """3Q25-2Q26 actual quarters split into lines (component volumes are assumptions, flagged)."""
    U = annual_units(case)
    rows = {}
    for q in ["3Q25", "4Q25", "1Q26", "2Q26"]:
        y = 2000 + int(q[2:])
        qn = q[:2]
        b = dm.QB[q]
        # within-year seasonal spread; 2026 quarters get 2026 annual units x seasonal share
        hot_n = U[y]["hotel_nights"] * SEAS[qn]
        exp_s = U[y]["exp_seats"] * SEAS[qn]
        svc_s = U[y]["svc_seats"] * SEAS[qn]
        hot_adr = HOTEL_ADR_FY25 * (b["adr"] / dm.FY25["adr"])   # hotel ADR moves with the blend
        hot_gbv = hot_n * hot_adr
        exp_gbv = exp_s * TICKET["experiences"]
        svc_gbv = svc_s * TICKET["services"]
        home_n = b["nights"] - hot_n - exp_s - svc_s
        home_gbv = b["gbv"] - hot_gbv - exp_gbv - svc_gbv
        ads = U[y]["ads_rev"] * SEAS[qn]
        line_rev = dict(hotels=hot_gbv * TAKE["hotels"], experiences=exp_gbv * TAKE["experiences"],
                        services=svc_gbv * TAKE["services"], ads=ads)
        stays_rev = b["rev"] - sum(line_rev.values())
        rows[q] = dict(quarter=q, nights_total=b["nights"], gbv_total=b["gbv"], rev_total=b["rev"],
                       home_nights=home_n, home_adr=home_gbv / home_n, home_gbv=home_gbv,
                       stays_take=stays_rev / home_gbv, stays_rev=stays_rev,
                       hotel_nights=hot_n, hotel_adr=hot_adr, hotel_gbv=hot_gbv, hotels_rev=line_rev["hotels"],
                       exp_seats=exp_s, exp_gbv=exp_gbv, experiences_rev=line_rev["experiences"],
                       svc_seats=svc_s, svc_gbv=svc_gbv, services_rev=line_rev["services"], ads_rev=ads)
    return rows


def forecast_quarters(case, adr_workbook=False):
    U = annual_units(case)
    base = base_quarters(case)
    q13 = {r["quarter"]: r for r in dm.build_quarters(case)}
    seats = pd.read_csv(P("data", "processed", "adr", "15_seats_dilution_annual.csv"))
    seats = seats[seats.case_business.eq(BIZ[case])].set_index("year")
    out = []
    known = dict(base)
    for q in FQ:
        pq, y, qn = PRIOR_Q[q], QYEAR[q], q[:2]
        b = known[pq]
        total = q13[q]["nights"]                                    # printed Nights and Seats, from 13
        hot_n = U[y]["hotel_nights"] * SEAS[qn]
        exp_s = U[y]["exp_seats"] * SEAS[qn]
        svc_s = U[y]["svc_seats"] * SEAS[qn]
        home_n = total - hot_n - exp_s - svc_s
        rev_fx, adr_fx = [x / 100.0 for x in dm.FX_Q[q][case]]
        if adr_workbook:
            home_exfx = ADR_WB_HOME_EXFX[case] / 100.0
        else:
            home_exfx = dm.ADR_EXFX_Q[q][case] / 100.0 - float(seats.loc[y, "dilution_drag_pp"]) / 100.0
        home_adr = b["home_adr"] * (1 + home_exfx) * (1 + adr_fx)
        hot_adr = b["hotel_adr"] * (1 + home_exfx) * (1 + adr_fx)
        home_gbv, hot_gbv = home_n * home_adr, hot_n * hot_adr
        exp_gbv, svc_gbv = exp_s * TICKET["experiences"], svc_s * TICKET["services"]
        gbv = home_gbv + hot_gbv + exp_gbv + svc_gbv
        stays_take = b["stays_take"] + dm.pick(dm.ANNUAL_INPUTS[y]["take_bps"], case) / 10000.0
        wedge = (1 + rev_fx) / (1 + adr_fx)
        stays_rev = home_gbv * stays_take * wedge
        hotels_rev = hot_gbv * TAKE["hotels"] * wedge
        exp_rev = exp_gbv * TAKE["experiences"]
        svc_rev = svc_gbv * TAKE["services"]
        ads = U[y]["ads_rev"] * SEAS[qn]
        rev = stays_rev + hotels_rev + exp_rev + svc_rev + ads
        row = dict(quarter=q, scenario=case, year=y, nights_total=total,
                   nights_total_yoy_pct=100 * (total / b["nights_total"] - 1),
                   home_nights=home_n, home_nights_yoy_pct=100 * (home_n / b["home_nights"] - 1),
                   home_adr=home_adr, home_adr_exfx_pct=100 * home_exfx, adr_fx_pp=100 * adr_fx,
                   home_gbv=home_gbv, stays_take_pct=100 * stays_take, stays_rev=stays_rev,
                   hotel_nights=hot_n, hotel_adr=hot_adr, hotel_gbv=hot_gbv, hotels_rev=hotels_rev,
                   exp_seats=exp_s, exp_gbv=exp_gbv, experiences_rev=exp_rev,
                   svc_seats=svc_s, svc_gbv=svc_gbv, services_rev=svc_rev, ads_rev=ads,
                   gbv_total=gbv, gbv_yoy_pct=100 * (gbv / b["gbv_total"] - 1),
                   blended_adr=gbv / total, blended_adr_yoy_pct=100 * (gbv / total / (b["gbv_total"] / b["nights_total"]) - 1),
                   blended_take_pct=100 * (rev - ads) / gbv, rev_total=rev,
                   rev_yoy_pct=100 * (rev / b["rev_total"] - 1),
                   seats_share_pct=100 * (exp_s + svc_s) / total, hotel_share_pct=100 * hot_n / total,
                   dm13_nights=q13[q]["nights"], dm13_adr=q13[q]["adr"], dm13_gbv=q13[q]["gbv"],
                   dm13_core_revenue=q13[q]["core_revenue"])
        out.append(row)
        known[q] = dict(nights_total=total, gbv_total=gbv, rev_total=rev, home_nights=home_n, home_adr=home_adr,
                        hotel_adr=hot_adr, stays_take=stays_take, hotel_nights=hot_n, exp_seats=exp_s, svc_seats=svc_s)
    return out, base


def annual_rows(case, qrows, base):
    """FY24/FY25 (split assumptions), FY26 = 1H26 base + 3Q/4Q, FY27 = four quarters, FY28 = annual growth."""
    U = annual_units(case)
    a13 = {int(r["year"]): r for r in dm.build_annual(case)}
    rows = []
    # FY25 actual split
    fy25 = dm.FY25
    hot_gbv = U[2025]["hotel_nights"] * HOTEL_ADR_FY25
    exp_gbv, svc_gbv = U[2025]["exp_gbv"], U[2025]["svc_gbv"]
    home_n = fy25["nights"] - U[2025]["hotel_nights"] - U[2025]["exp_seats"] - U[2025]["svc_seats"]
    home_gbv = fy25["gbv"] - hot_gbv - exp_gbv - svc_gbv
    line_rev = dict(hotels=hot_gbv * TAKE["hotels"], experiences=exp_gbv * TAKE["experiences"],
                    services=svc_gbv * TAKE["services"], ads=0.0)
    stays_rev = fy25["rev"] - sum(line_rev.values())
    rows.append(dict(scenario=case, year=2025, basis="actual total; line split assumed",
                     nights_total=fy25["nights"], home_nights=home_n, hotel_nights=U[2025]["hotel_nights"],
                     exp_seats=U[2025]["exp_seats"], svc_seats=U[2025]["svc_seats"],
                     home_adr=home_gbv / home_n, hotel_adr=HOTEL_ADR_FY25, home_gbv=home_gbv, hotel_gbv=hot_gbv,
                     exp_gbv=exp_gbv, svc_gbv=svc_gbv, gbv_total=fy25["gbv"],
                     stays_take_pct=100 * stays_rev / home_gbv, stays_rev=stays_rev, hotels_rev=line_rev["hotels"],
                     experiences_rev=line_rev["experiences"], services_rev=line_rev["services"], ads_rev=0.0,
                     rev_total=fy25["rev"], blended_adr=fy25["gbv"] / fy25["nights"],
                     blended_take_pct=100 * fy25["rev"] / fy25["gbv"], dm13_revenue=fy25["rev"]))
    prev = rows[-1]
    for y in (2026, 2027):
        qs = [r for r in qrows if r["year"] == y]
        if y == 2026:
            h1 = [base["1Q26"], base["2Q26"]]
            add = lambda k, alt=None: sum(r[k] for r in qs) + sum(r[alt or k] for r in h1)
            rev = add("rev_total")
            tot = add("nights_total"); hn = add("home_nights"); hgbv = add("home_gbv"); srev = add("stays_rev")
            hotn = add("hotel_nights"); hotg = add("hotel_gbv"); hrev = add("hotels_rev")
            es = add("exp_seats"); eg = add("exp_gbv"); erev = add("experiences_rev")
            ss = add("svc_seats"); sg = add("svc_gbv"); srv = add("services_rev"); ads = add("ads_rev")
        else:
            add = lambda k: sum(r[k] for r in qs)
            rev = add("rev_total"); tot = add("nights_total"); hn = add("home_nights"); hgbv = add("home_gbv")
            srev = add("stays_rev"); hotn = add("hotel_nights"); hotg = add("hotel_gbv"); hrev = add("hotels_rev")
            es = add("exp_seats"); eg = add("exp_gbv"); erev = add("experiences_rev")
            ss = add("svc_seats"); sg = add("svc_gbv"); srv = add("services_rev"); ads = add("ads_rev")
        gbv = hgbv + hotg + eg + sg
        rows.append(dict(scenario=case, year=y, basis="1H26 actual + forecast" if y == 2026 else "forecast",
                         nights_total=tot, home_nights=hn, hotel_nights=hotn, exp_seats=es, svc_seats=ss,
                         home_adr=hgbv / hn, hotel_adr=hotg / hotn, home_gbv=hgbv, hotel_gbv=hotg, exp_gbv=eg,
                         svc_gbv=sg, gbv_total=gbv, stays_take_pct=100 * srev / hgbv, stays_rev=srev,
                         hotels_rev=hrev, experiences_rev=erev, services_rev=srv, ads_rev=ads, rev_total=rev,
                         blended_adr=gbv / tot, blended_take_pct=100 * (rev - ads) / gbv,
                         dm13_revenue=a13[y]["revenue"]))
        prev = rows[-1]
    # FY28: annual growth off FY27 (13's FY28 conventions), lines from 11 and the hotel path
    y = 2028
    g = dm.pick(dm.NIGHTS_2028, case)
    adr_exfx = dm.pick(dm.ADR_EXFX_2028, case)
    seats = pd.read_csv(P("data", "processed", "adr", "15_seats_dilution_annual.csv"))
    drag = float(seats[seats.case_business.eq(BIZ[case]) & seats.year.eq(2028)].dilution_drag_pp.iloc[0]) / 100
    tot = prev["nights_total"] * (1 + g)
    hotn, es, ss = U[2028]["hotel_nights"], U[2028]["exp_seats"], U[2028]["svc_seats"]
    hn = tot - hotn - es - ss
    home_adr = prev["home_adr"] * (1 + adr_exfx - drag)
    hgbv, hotg = hn * home_adr, hotn * prev["hotel_adr"] * (1 + adr_exfx - drag)
    eg, sg = U[2028]["exp_gbv"], U[2028]["svc_gbv"]
    take = prev["stays_take_pct"] / 100 + dm.pick(dm.ANNUAL_INPUTS[2028]["take_bps"], case) / 10000
    srev, hrev = hgbv * take, hotg * TAKE["hotels"]
    erev, srv, ads = eg * TAKE["experiences"], sg * TAKE["services"], U[2028]["ads_rev"]
    gbv = hgbv + hotg + eg + sg
    rev = srev + hrev + erev + srv + ads
    rows.append(dict(scenario=case, year=y, basis="annual growth (13 FY28 conventions)", nights_total=tot,
                     home_nights=hn, hotel_nights=hotn, exp_seats=es, svc_seats=ss, home_adr=home_adr,
                     hotel_adr=hotg / hotn, home_gbv=hgbv, hotel_gbv=hotg, exp_gbv=eg, svc_gbv=sg, gbv_total=gbv,
                     stays_take_pct=100 * take, stays_rev=srev, hotels_rev=hrev, experiences_rev=erev,
                     services_rev=srv, ads_rev=ads, rev_total=rev, blended_adr=gbv / tot,
                     blended_take_pct=100 * (rev - ads) / gbv, dm13_revenue=a13[y]["revenue"]))
    for i in range(1, len(rows)):
        for k in ("nights_total", "home_nights", "rev_total", "gbv_total", "blended_adr", "home_adr", "stays_rev",
                  "hotels_rev", "experiences_rev", "services_rev"):
            rows[i][f"{k}_yoy_pct"] = 100 * (rows[i][k] / rows[i - 1][k] - 1) if rows[i - 1][k] else float("nan")
        rows[i]["seats_share_pct"] = 100 * (rows[i]["exp_seats"] + rows[i]["svc_seats"]) / rows[i]["nights_total"]
        rows[i]["hotel_share_pct"] = 100 * rows[i]["hotel_nights"] / rows[i]["nights_total"]
        rows[i]["new_business_rev_share_pct"] = 100 * (rows[i]["hotels_rev"] + rows[i]["experiences_rev"]
                                                       + rows[i]["services_rev"] + rows[i]["ads_rev"]) / rows[i]["rev_total"]
        rows[i]["rev_vs_dm13_musd"] = rows[i]["rev_total"] - rows[i]["dm13_revenue"]
    return rows


def write_workbook(qrows_all, arows_all, path):
    """Live-formula workbook: Inputs (yellow) -> By_line (blue formulas) per case."""
    wb = xlsxwriter.Workbook(path)
    inp = wb.add_format({"bg_color": "#FEF3C7", "border": 1, "num_format": "0.00"})
    out = wb.add_format({"bg_color": "#DBEAFE", "border": 1, "num_format": "#,##0.0"})
    pct = wb.add_format({"bg_color": "#DBEAFE", "border": 1, "num_format": "0.0"})
    hdr = wb.add_format({"bold": True, "bg_color": "#2D3748", "font_color": "white", "border": 1})
    bold = wb.add_format({"bold": True})
    note = wb.add_format({"italic": True, "font_color": "#4A5568", "text_wrap": True, "valign": "top"})
    ws0 = wb.add_worksheet("README")
    ws0.set_column("A:A", 110)
    for i, t in enumerate([
        "ABNB revenue by business line (WS14). Python mirror: analysis/src/overnight/14_revenue_by_line.py.",
        "Each case sheet: yellow cells are inputs, blue cells are formulas. Rows are forecast quarters 3Q26-4Q27.",
        "Lines: stays (home nights x home ADR x stays take), hotels (nights x hotel ADR x 11%), experiences (seats x $75 x 20%), "
        "services (seats x $120 x 15%), ads (outside GBV). Printed KPIs (Nights and Seats, GBV, blended ADR, blended take) are outputs.",
        "Printed Nights and Seats per quarter is the driver model's regional build (13). Home nights are the residual after hotels and seats.",
        "Home ADR ex-FX defaults to 13's blended ADR ex-FX plus the seats-dilution drag (15), so the printed ADR reconciles to 13. "
        "Overwrite the yellow home-ADR cells with the ADR workbook path (5_Forecast ex the new-business row) to run the ADR build through.",
        "Hotel nights, seats and tickets are assumptions (Airbnb discloses none of them); see 15_seats_dilution and 11_new_business_scenarios.",
    ]):
        ws0.write(i, 0, t, note)
    for case in SCEN:
        ws = wb.add_worksheet(case)
        ws.set_column("A:A", 34); ws.set_column("B:H", 13)
        qs = [r for r in qrows_all if r["scenario"] == case]
        ws.write(0, 0, f"{case} case: revenue by line, 3Q26-4Q27", bold)
        ws.write(2, 0, "Inputs", hdr)
        for j, r in enumerate(qs):
            ws.write(2, 1 + j, r["quarter"], hdr)
        inputs = [
            ("Nights and Seats Booked, M (from 13)", "nights_total", 1),
            ("Hotel nights, M", "hotel_nights", 1),
            ("Experiences seats, M", "exp_seats", 1),
            ("Services seats, M", "svc_seats", 1),
            ("Prior-year home ADR, $", None, 1),
            ("Home ADR ex-FX y/y, %", "home_adr_exfx_pct", 1),
            ("ADR FX, pp", "adr_fx_pp", 1),
            ("Prior-year hotel ADR, $", None, 1),
            ("Experiences ticket, $/seat", None, TICKET["experiences"]),
            ("Services ticket, $/seat", None, TICKET["services"]),
            ("Stays take rate, %", "stays_take_pct", 1),
            ("Hotel commission, %", None, 100 * TAKE["hotels"]),
            ("Experiences host fee, %", None, 100 * TAKE["experiences"]),
            ("Services host fee, %", None, 100 * TAKE["services"]),
            ("Revenue-FX wedge, ratio", None, 1),
            ("Ads revenue, $M", "ads_rev", 1),
        ]
        R = {}
        r0 = 3
        for i, (label, key, const) in enumerate(inputs):
            rr = r0 + i
            R[label] = rr + 1
            ws.write(rr, 0, label)
            for j, r in enumerate(qs):
                if key:
                    v = r[key]
                elif label.startswith("Prior-year home"):
                    v = r["home_adr"] / (1 + r["home_adr_exfx_pct"] / 100) / (1 + r["adr_fx_pp"] / 100)
                elif label.startswith("Prior-year hotel"):
                    v = r["hotel_adr"] / (1 + r["home_adr_exfx_pct"] / 100) / (1 + r["adr_fx_pp"] / 100)
                elif label.startswith("Revenue-FX"):
                    v = (1 + dm.FX_Q[r["quarter"]][case][0] / 100) / (1 + dm.FX_Q[r["quarter"]][case][1] / 100)
                else:
                    v = const
                ws.write_number(rr, 1 + j, v, inp)
        rr = r0 + len(inputs) + 1
        ws.write(rr, 0, "By line", hdr); rr += 1
        C = lambda j: xlsxwriter.utility.xl_col_to_name(1 + j)
        F = {}
        formulas = [
            ("Home nights, M", lambda c: f"={c}{R['Nights and Seats Booked, M (from 13)']}-{c}{R['Hotel nights, M']}-{c}{R['Experiences seats, M']}-{c}{R['Services seats, M']}", out),
            ("Home ADR, $", lambda c: f"={c}{R['Prior-year home ADR, $']}*(1+{c}{R['Home ADR ex-FX y/y, %']}/100)*(1+{c}{R['ADR FX, pp']}/100)", out),
            ("Home GBV, $M", lambda c: f"={c}{F['Home nights, M']}*{c}{F['Home ADR, $']}", out),
            ("Stays revenue, $M", lambda c: f"={c}{F['Home GBV, $M']}*{c}{R['Stays take rate, %']}/100*{c}{R['Revenue-FX wedge, ratio']}", out),
            ("Hotel ADR, $", lambda c: f"={c}{R['Prior-year hotel ADR, $']}*(1+{c}{R['Home ADR ex-FX y/y, %']}/100)*(1+{c}{R['ADR FX, pp']}/100)", out),
            ("Hotel GBV, $M", lambda c: f"={c}{R['Hotel nights, M']}*{c}{F['Hotel ADR, $']}", out),
            ("Hotels revenue, $M", lambda c: f"={c}{F['Hotel GBV, $M']}*{c}{R['Hotel commission, %']}/100*{c}{R['Revenue-FX wedge, ratio']}", out),
            ("Experiences GBV, $M", lambda c: f"={c}{R['Experiences seats, M']}*{c}{R['Experiences ticket, $/seat']}", out),
            ("Experiences revenue, $M", lambda c: f"={c}{F['Experiences GBV, $M']}*{c}{R['Experiences host fee, %']}/100", out),
            ("Services GBV, $M", lambda c: f"={c}{R['Services seats, M']}*{c}{R['Services ticket, $/seat']}", out),
            ("Services revenue, $M", lambda c: f"={c}{F['Services GBV, $M']}*{c}{R['Services host fee, %']}/100", out),
            ("Total revenue, $M", lambda c: f"={c}{F['Stays revenue, $M']}+{c}{F['Hotels revenue, $M']}+{c}{F['Experiences revenue, $M']}+{c}{F['Services revenue, $M']}+{c}{R['Ads revenue, $M']}", out),
            ("GBV, $M (printed)", lambda c: f"={c}{F['Home GBV, $M']}+{c}{F['Hotel GBV, $M']}+{c}{F['Experiences GBV, $M']}+{c}{F['Services GBV, $M']}", out),
            ("Blended ADR, $ (printed)", lambda c: f"={c}{F['GBV, $M (printed)']}/{c}{R['Nights and Seats Booked, M (from 13)']}", out),
            ("Blended take rate, % (printed)", lambda c: f"=({c}{F['Total revenue, $M']}-{c}{R['Ads revenue, $M']})/{c}{F['GBV, $M (printed)']}*100", pct),
            ("Seats share of denominator, %", lambda c: f"=({c}{R['Experiences seats, M']}+{c}{R['Services seats, M']})/{c}{R['Nights and Seats Booked, M (from 13)']}*100", pct),
            ("New-business share of revenue, %", lambda c: f"=({c}{F['Total revenue, $M']}-{c}{F['Stays revenue, $M']})/{c}{F['Total revenue, $M']}*100", pct),
        ]
        for label, fn, fmt in formulas:
            F[label] = rr + 1
            ws.write(rr, 0, label)
            for j, _ in enumerate(qs):
                ws.write_formula(rr, 1 + j, fn(C(j)), fmt)
            rr += 1
        rr += 1
        ws.write(rr, 0, "Driver model (13) for reconciliation", hdr); rr += 1
        for label, key in [("13 revenue (core), $M", "dm13_core_revenue"), ("13 blended ADR, $", "dm13_adr"), ("13 GBV, $M", "dm13_gbv")]:
            ws.write(rr, 0, label)
            for j, r in enumerate(qs):
                ws.write_number(rr, 1 + j, r[key], out)
            rr += 1
    ws = wb.add_worksheet("Annual")
    ws.set_column("A:A", 12); ws.set_column("B:Z", 13)
    cols = ["scenario", "year", "basis", "nights_total", "home_nights", "hotel_nights", "exp_seats", "svc_seats",
            "home_adr", "blended_adr", "gbv_total", "stays_take_pct", "blended_take_pct", "stays_rev", "hotels_rev",
            "experiences_rev", "services_rev", "ads_rev", "rev_total", "rev_total_yoy_pct", "new_business_rev_share_pct",
            "seats_share_pct", "dm13_revenue", "rev_vs_dm13_musd"]
    for j, c in enumerate(cols):
        ws.write(0, j, c, hdr)
    for i, r in enumerate(arows_all):
        for j, c in enumerate(cols):
            v = r.get(c, "")
            if isinstance(v, (int, float)):
                ws.write_number(i + 1, j, v, out)
            else:
                ws.write(i + 1, j, v)
    wb.close()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--adr-workbook", action="store_true", help="use the ADR workbook home-ADR path instead of 13's")
    a = ap.parse_args()
    qrows_all, arows_all = [], []
    for case in SCEN:
        q, base = forecast_quarters(case, a.adr_workbook)
        qrows_all += q
        arows_all += annual_rows(case, q, base)
    pd.DataFrame(qrows_all).to_csv(OD("14_revenue_by_line_quarterly.csv"), index=False)
    pd.DataFrame(arows_all).to_csv(OD("14_revenue_by_line_annual.csv"), index=False)
    k = pd.DataFrame(arows_all)[["scenario", "year", "basis", "nights_total", "blended_adr", "blended_take_pct",
                                  "rev_total", "dm13_revenue", "rev_vs_dm13_musd", "new_business_rev_share_pct",
                                  "seats_share_pct", "hotel_share_pct"]]
    k.to_csv(OD("14_revenue_by_line_kpis.csv"), index=False)
    write_workbook(qrows_all, arows_all, P("model", "ABNB_revenue_by_line.xlsx"))
    pd.set_option("display.width", 250)
    A = pd.DataFrame(arows_all)
    print(A[["scenario", "year", "stays_rev", "hotels_rev", "experiences_rev", "services_rev", "ads_rev", "rev_total",
             "rev_total_yoy_pct", "dm13_revenue", "rev_vs_dm13_musd", "blended_adr", "blended_take_pct",
             "stays_take_pct", "new_business_rev_share_pct"]].round(1).to_string())
    Q = pd.DataFrame(qrows_all)
    print(Q[Q.scenario.eq("Base")][["quarter", "nights_total", "home_nights", "home_adr", "blended_adr", "blended_adr_yoy_pct",
                                    "dm13_adr", "stays_take_pct", "blended_take_pct", "rev_total", "dm13_core_revenue"]].round(2).to_string())


if __name__ == "__main__":
    main()
