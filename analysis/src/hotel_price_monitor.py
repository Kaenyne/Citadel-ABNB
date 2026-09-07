"""Monthly hotel-price monitor: US lodging CPI and BEA hotel price index y/y next to Airbnb's quarterly ADR growth.

Inputs
  data/raw/fred/CUSR0000SEHB.csv                      CPI lodging away from home, SA, monthly (FRED keyless CSV)
  data/raw/bea/bea_pce_travel_monthly_2015_2026.csv    BEA PCE hotels and motels price index (2017 = 100), monthly
  data/processed/abnb_quarterly_cost_stack_exsbc.csv   ABNB ADR by quarter (shareholder letters)

ADR y/y is computed from the letters' ADR and placed on the quarter-end month. ADR ex-FX is stated by management in the
letters only for recent quarters (ADR_EXFX below). Oct 2025 CPI is missing at source (shutdown gap), so y/y for
2025-10 and 2026-10 is blank.

Output: data/processed/hotel_price_monitor_monthly.csv, 2023-01 to the latest month with data
Run: python analysis/src/hotel_price_monitor.py
"""
import csv, os, sys

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..")
OUT = os.path.join(ROOT, "data", "processed", "hotel_price_monitor_monthly.csv")
START = "2023-01"
# Reported ADR y/y and ex-FX ADR y/y as stated in the shareholder letters (percent). 4Q25 letter: "+6% ... +3% ex-FX";
# 1Q26: "+9% ... +4% ex-FX"; 2Q26: "+5% ... +4% ex-FX".
ADR_EXFX = {"4Q25": (6, 3), "1Q26": (9, 4), "2Q26": (5, 4)}


def yoy(series):
    out = {}
    for d, v in series.items():
        p = f"{int(d[:4]) - 1}{d[4:]}"
        if p in series and series[p]:
            out[d] = round(100 * (v / series[p] - 1), 1)
    return out


def main():
    cpi = {r["observation_date"][:7]: float(r["CUSR0000SEHB"]) for r in csv.DictReader(open(os.path.join(ROOT, "data/raw/fred/CUSR0000SEHB.csv")))
           if r["CUSR0000SEHB"] not in ("", ".")}
    bea = {r["date"][:7]: float(r["value"]) for r in csv.DictReader(open(os.path.join(ROOT, "data/raw/bea/bea_pce_travel_monthly_2015_2026.csv"), encoding="utf-8"))
           if r["series"] == "hotels_motels" and r["measure"] == "price_index_2017eq100"}
    cpi_y, bea_y = yoy(cpi), yoy(bea)
    stack = {r["quarter"]: float(r["adr"]) for r in csv.DictReader(open(os.path.join(ROOT, "data/processed/abnb_quarterly_cost_stack_exsbc.csv")))}
    adr = {}
    for q, v in stack.items():
        prev = stack.get(f"{q[0]}Q{int(q[2:]) - 1:02d}")
        if prev:
            month = f"20{q[2:]}-{3 * int(q[0]):02d}"
            adr[month] = {"quarter": q, "abnb_adr_yoy_pct": round(100 * (v / prev - 1), 1),
                          "abnb_adr_yoy_letter_pct": ADR_EXFX.get(q, (None, None))[0], "abnb_adr_exfx_yoy_pct": ADR_EXFX.get(q, (None, None))[1]}
    months = sorted(m for m in set(cpi) | set(bea) if m >= START)
    cols = ["month", "cpi_lodging_yoy_pct", "bea_hotels_price_yoy_pct", "abnb_quarter", "abnb_adr_yoy_pct", "abnb_adr_yoy_letter_pct", "abnb_adr_exfx_yoy_pct"]
    with open(OUT, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=cols)
        w.writeheader()
        for m in months:
            a = adr.get(m, {})
            w.writerow({"month": m, "cpi_lodging_yoy_pct": cpi_y.get(m, ""), "bea_hotels_price_yoy_pct": bea_y.get(m, ""),
                        "abnb_quarter": a.get("quarter", ""), "abnb_adr_yoy_pct": a.get("abnb_adr_yoy_pct", ""),
                        "abnb_adr_yoy_letter_pct": a.get("abnb_adr_yoy_letter_pct") or "", "abnb_adr_exfx_yoy_pct": a.get("abnb_adr_exfx_yoy_pct") or ""})
    print(f"wrote {len(months)} months to {os.path.normpath(OUT)}")
    print("month | CPI lodging y/y | BEA hotels price y/y | ABNB ADR y/y (ex-FX)")
    for m in months[-20:]:
        a = adr.get(m, {})
        print(f"{m} | {cpi_y.get(m, ''):>5} | {bea_y.get(m, ''):>5} | {a.get('abnb_adr_yoy_pct', '')} {('(' + str(a['abnb_adr_exfx_yoy_pct']) + ' ex-FX)') if a.get('abnb_adr_exfx_yoy_pct') else ''}")


if __name__ == "__main__":
    sys.exit(main())
