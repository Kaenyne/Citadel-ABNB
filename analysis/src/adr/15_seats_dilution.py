"""15. Seats dilution: what Experiences, Services and hotels do to reported ADR.

The problem
  Since the 2Q25 letter the KPI is "Nights and Seats Booked": nights booked for stays plus
  seats booked for experiences and services, net of cancellations (the 1Q25 letter still said
  "Nights and Experiences Booked", which already carried experiences seats, so the rename
  added Services and relaunched Experiences rather than changing the arithmetic). ADR is GBV
  divided by that denominator, and the FY2025 10-K's regional table is on the same basis.
  A seat is one unit of the denominator at a fraction of a night's GBV, and a hotel night is
  one unit at ~0.75x the blended ADR. If those units grow faster than home nights, reported
  ADR is dragged down with no change in lodging pricing. Airbnb discloses none of the
  volumes, so this is a scenario build, not a measurement.

Method
  Components of the denominator: home nights, hotel nights, experiences seats, services
  seats. Volumes come from the overnight new-business revenue scenarios
  (`11_new_business_scenarios.csv`: hotels 18.7m nights FY25 at ~$140 ADR and ~11% commission,
  experiences GBV = revenue / 20% host fee, services GBV = revenue / 15% host fee) and an
  average ticket per seat, which is the one assumption Airbnb has never anchored (newsroom:
  "numerous experiences under $100 per person"; Icons "under $100 per guest"). Price ratios
  to the blend are held at their FY25 level, so the drag is a pure unit-mix effect:

      dilution ratio_t = reported ADR / homes-only ADR
                       = [1 + sum_i s_i (rho_i - 1)] / [1 - sum_i s_i] ... exactly, from units
      drag_t, pp       = (ratio_t / ratio_{t-1} - 1) x 100

  where s_i is component i's share of the denominator and rho_i its price relative to homes.
  Cases: the new-business scenario cases (bear / base / bull) are BUSINESS cases; for ADR the
  bull business case is the bear ADR case. Both labels are carried. Ticket sensitivity is
  gridded.

Outputs
  data/processed/adr/15_seats_dilution_annual.csv      FY24-FY28 by case: shares, ratios, drag
  data/processed/adr/15_seats_dilution_quarterly.csv   3Q26-4Q27 by case, seasonality = nights
  data/processed/adr/15_seats_dilution_sensitivity.csv ticket and FY24-base grid
Run
  py -3.13 analysis/src/adr/15_seats_dilution.py
"""
import numpy as np
import pandas as pd

OUT = "data/processed/adr"
HIST = "data/processed/adr/02b_adr_history_extended.csv"
NB = "data/processed/overnight/11_new_business_scenarios.csv"

# ---- assumptions (every number here is an assumption; sources in the docstring) ---------
TAKE = dict(experiences=0.20, services=0.15, hotels=0.11)
TICKET = dict(experiences=75.0, services=120.0)      # $ GBV per seat, central
TICKET_GRID = dict(experiences=(50.0, 75.0, 100.0), services=(80.0, 120.0, 180.0))
HOTEL_ADR_FY25 = 140.0
HOTEL_NIGHTS_FY25_M = 18.7                            # 3.5% of FY25 nights, per 11's assumption
HOTEL_GROWTH = dict(bear=(0.20, 0.16, 0.16), base=(0.35, 0.30, 0.25), bull=(0.50, 0.45, 0.40))
EXP_GBV_FY24_M = 400.0                                # pre-relaunch base; experiences were
                                                      # paused for new hosts 2023-25. Gridded.
HOME_NIGHTS_GROWTH = dict(bear=0.06, base=0.08, bull=0.10)   # FY26-28 home nights, placeholder
YEARS = [2024, 2025, 2026, 2027, 2028]


def history():
    h = pd.read_csv(HIST)
    h["year"] = h.quarter.str[2:].astype(int) + 2000
    a = h.groupby("year").agg(units_m=("nights_m", "sum"), gbv_busd=("gbv_busd", "sum"))
    a["adr"] = a.gbv_busd * 1e3 / a.units_m
    return h, a


def build(case, t_exp, t_svc, exp_fy24, hist_a):
    nb = pd.read_csv(NB)
    nb = nb[nb.case.eq(case)].set_index("business")
    rev = {b: [float(nb.loc[b, f"fy{y % 100}_rev_musd"]) for y in (2025, 2026, 2027, 2028)]
           for b in ("experiences", "services", "hotels")}
    rows = []
    d24, d25 = hist_a.loc[2024, "units_m"], hist_a.loc[2025, "units_m"]
    adr25 = hist_a.loc[2025, "adr"]
    # units by component
    exp_gbv = [exp_fy24] + [r / TAKE["experiences"] for r in rev["experiences"]]
    svc_gbv = [0.0] + [r / TAKE["services"] for r in rev["services"]]
    exp_u = [g / t_exp for g in exp_gbv]
    svc_u = [g / t_svc for g in svc_gbv]
    hot_u = [HOTEL_NIGHTS_FY25_M / 1.30, HOTEL_NIGHTS_FY25_M]
    for g in HOTEL_GROWTH[case]:
        hot_u.append(hot_u[-1] * (1 + g))
    # home nights: history from the denominator less the other units, then grown
    home_u = [d24 - exp_u[0] - hot_u[0], d25 - exp_u[1] - svc_u[1] - hot_u[1]]
    for _ in range(3):
        home_u.append(home_u[-1] * (1 + HOME_NIGHTS_GROWTH[case]))
    # price ratios to homes, fixed at FY25
    home_gbv25 = hist_a.loc[2025, "gbv_busd"] * 1e3 - exp_gbv[1] - svc_gbv[1] - hot_u[1] * HOTEL_ADR_FY25
    p_home = home_gbv25 / home_u[1]
    rho = dict(hotels=HOTEL_ADR_FY25 / p_home, experiences=t_exp / p_home, services=t_svc / p_home)
    prev_ratio = None
    for i, y in enumerate(YEARS):
        D = home_u[i] + hot_u[i] + exp_u[i] + svc_u[i]
        s = dict(hotels=hot_u[i] / D, experiences=exp_u[i] / D, services=svc_u[i] / D)
        ratio = (home_u[i] + sum(u * rho[k] for k, u in
                                  (("hotels", hot_u[i]), ("experiences", exp_u[i]), ("services", svc_u[i])))) / D
        drag = (ratio / prev_ratio - 1) * 100 if prev_ratio else np.nan
        rows.append(dict(case_business=case, year=y, denominator_m=D, home_nights_m=home_u[i],
                         hotel_nights_m=hot_u[i], experiences_seats_m=exp_u[i], services_seats_m=svc_u[i],
                         share_hotels=s["hotels"], share_experiences=s["experiences"], share_services=s["services"],
                         share_seats=s["experiences"] + s["services"],
                         rho_hotels=rho["hotels"], rho_experiences=rho["experiences"], rho_services=rho["services"],
                         dilution_ratio=ratio, dilution_drag_pp=drag,
                         drag_hotels_pp=np.nan, drag_seats_pp=np.nan,
                         ticket_experiences=t_exp, ticket_services=t_svc, exp_gbv_fy24_m=exp_fy24,
                         p_home_fy25=p_home))
        prev_ratio = ratio
    df = pd.DataFrame(rows)
    # attribute the drag between hotels and seats by holding the other at its prior share
    for i in range(1, len(df)):
        a, b = df.iloc[i - 1], df.iloc[i]
        def ratio_of(sh, se_e, se_s, home_share=None):
            hs = 1 - sh - se_e - se_s
            return hs + sh * rho["hotels"] + se_e * rho["experiences"] + se_s * rho["services"]
        r_prev = ratio_of(a.share_hotels, a.share_experiences, a.share_services)
        r_hot = ratio_of(b.share_hotels, a.share_experiences, a.share_services)
        r_seat = ratio_of(a.share_hotels, b.share_experiences, b.share_services)
        df.loc[df.index[i], "drag_hotels_pp"] = (r_hot / r_prev - 1) * 100
        df.loc[df.index[i], "drag_seats_pp"] = (r_seat / r_prev - 1) * 100
    return df


def main():
    hist_q, hist_a = history()
    ann = pd.concat([build(c, TICKET["experiences"], TICKET["services"], EXP_GBV_FY24_M, hist_a)
                     for c in ("bear", "base", "bull")], ignore_index=True)
    ann["case_adr"] = ann.case_business.map({"bear": "bull", "base": "base", "bull": "bear"})
    ann.to_csv(f"{OUT}/15_seats_dilution_annual.csv", index=False)

    # quarterly: spread each year's drag by the quarter's share of the year's denominator, so a
    # summer-heavy seat mix would be understated (flagged in the note)
    qshare = hist_q[hist_q.quarter.str.endswith(("23", "24", "25"))].copy()
    qshare["qn"] = qshare.quarter.str[0].astype(int)
    qshare["year"] = qshare.quarter.str[2:].astype(int) + 2000
    qshare["sh"] = qshare.nights_m / qshare.groupby("year").nights_m.transform("sum")
    season = qshare.groupby("qn").sh.mean()
    qrows = []
    for c in ("bear", "base", "bull"):
        a = ann[ann.case_business.eq(c)].set_index("year")
        for y in (2026, 2027):
            for qn in (1, 2, 3, 4):
                if y == 2026 and qn < 3:
                    continue
                # y/y drag in a quarter = the annual unit-mix drift, assumed uniform through the year
                qrows.append(dict(case_business=c, case_adr=a.loc[y, "case_adr"], quarter=f"{qn}Q{y % 100}",
                                  dilution_drag_pp=a.loc[y, "dilution_drag_pp"],
                                  drag_hotels_pp=a.loc[y, "drag_hotels_pp"], drag_seats_pp=a.loc[y, "drag_seats_pp"],
                                  share_seats=a.loc[y, "share_seats"], share_hotels=a.loc[y, "share_hotels"],
                                  seasonal_share_of_year=season[qn]))
    pd.DataFrame(qrows).to_csv(f"{OUT}/15_seats_dilution_quarterly.csv", index=False)

    # sensitivity: ticket grid x FY24 experiences base, base business case, FY26 and FY27 drag
    srows = []
    for te in TICKET_GRID["experiences"]:
        for ts in TICKET_GRID["services"]:
            for e24 in (250.0, 400.0, 550.0):
                for c in ("bear", "base", "bull"):
                    d = build(c, te, ts, e24, hist_a).set_index("year")
                    srows.append(dict(case_business=c, ticket_experiences=te, ticket_services=ts, exp_gbv_fy24_m=e24,
                                      drag_fy25_pp=d.loc[2025, "dilution_drag_pp"], drag_fy26_pp=d.loc[2026, "dilution_drag_pp"],
                                      drag_fy27_pp=d.loc[2027, "dilution_drag_pp"], share_seats_fy27=d.loc[2027, "share_seats"]))
    sens = pd.DataFrame(srows)
    sens.to_csv(f"{OUT}/15_seats_dilution_sensitivity.csv", index=False)

    pd.set_option("display.width", 250)
    cols = ["case_business", "case_adr", "year", "share_hotels", "share_experiences", "share_services",
            "dilution_ratio", "dilution_drag_pp", "drag_hotels_pp", "drag_seats_pp"]
    print(ann[cols].round(4).to_string())
    print(sens.groupby("case_business")[["drag_fy26_pp", "drag_fy27_pp"]].agg(["min", "median", "max"]).round(2).to_string())
    print("FY25 price of a home night implied:", round(float(ann.p_home_fy25.iloc[0]), 2),
          "rho hotels/exp/svc:", ann[["rho_hotels", "rho_experiences", "rho_services"]].iloc[0].round(3).to_dict())


if __name__ == "__main__":
    main()
