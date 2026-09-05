"""Build data/processed/abnb_kpi_vs_category_quarterly.csv: ABNB quarterly KPIs next to the
US lodging category (BEA PCE) and CPI, for the "share test" and real-ADR exhibits.

Inputs:
  research/airbnb_earnings_call_study.md            section 3.1 KPI table (nights, GBV, ADR, revenue,
                                                    adj. EBITDA, take rate) from shareholder letters
  data/raw/bea/bea_pce_travel_monthly_2015_2026.csv          BEA NIPA underlying detail (Table 2.4.x U),
                                                    monthly SAAR; extracted from the BEA underlying-detail workbook (copy of the ABNB-Crossover extract)
  data/raw/fred/CUSR0000SEHB.csv, CUSR0000SETG01.csv, CPIAUCSL.csv   FRED keyless CSV downloads
                                                    (CPI lodging away from home SA, airline fares SA, all items)

Quarterly BEA/CPI values are the mean of the three months; y/y is vs the same quarter a year earlier.
Derived: implied_adr = GBV / nights; adr_real_yoy = ADR y/y deflated by CPI lodging y/y;
share_gap = ABNB nights y/y minus BEA real accommodations y/y (positive = taking share of US lodging volume).
Caveats: BEA accommodations is US-resident spend only (inbound guests sit in "foreign travel in the US");
ABNB KPIs are global, so the comparison is directional. BEA revises; SAAR months are noisy.

Run: python analysis/src/abnb_kpi_vs_category.py
"""
import csv, re, collections
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
STUDY = ROOT / "research/airbnb_earnings_call_study.md"
BEA = ROOT / "data/raw/bea/bea_pce_travel_monthly_2015_2026.csv"
FRED = ROOT / "data/raw/fred"
OUT = ROOT / "data/processed/abnb_kpi_vs_category_quarterly.csv"


def num(s):
    s = s.replace(",", "").replace("−", "-").replace("%", "").replace("$", "").strip()
    return float(s) if s not in ("", "n/a") else None


def kpis():
    rows = {}
    for line in STUDY.read_text(encoding="utf-8").splitlines():
        m = re.match(r"\|\s*([1-4]Q\d\d)\s*\|", line)
        if not m:
            continue
        c = [x.strip() for x in line.strip().strip("|").split("|")]
        if len(c) < 13:  # skip the analyst-sentiment table, which also starts with a quarter label
            continue
        q = f"20{c[0][2:]}Q{c[0][0]}"
        rows[q] = dict(quarter=q, nights_m=num(c[1]), nights_yoy_pct=num(c[2]), gbv_busd=num(c[3]), gbv_yoy_pct=num(c[4]),
                       adr_usd=num(c[5]), revenue_musd=num(c[6]), revenue_yoy_pct=num(c[7]), adj_ebitda_musd=num(c[8]),
                       adj_ebitda_margin_pct=num(c[9]), take_rate_pct=num(c[12]))
    return rows


def quarterly(series_by_month):
    q = collections.defaultdict(list)
    for d, v in series_by_month.items():
        q[f"{d[:4]}Q{(int(d[5:7]) - 1) // 3 + 1}"].append(v)
    return {k: sum(v) / 3 for k, v in q.items() if len(v) == 3}


def yoy(qs, k):
    y, n = int(k[:4]), k[5]
    p = f"{y - 1}Q{n}"
    return round((qs[k] / qs[p] - 1) * 100, 1) if k in qs and p in qs else None


def bea():
    out = collections.defaultdict(dict)
    for r in csv.DictReader(open(BEA, encoding="utf-8")):
        out[(r["series"], r["measure"])][r["date"]] = float(r["value"])
    return {k: quarterly(v) for k, v in out.items()}


def fred(series):
    return quarterly({r["observation_date"]: float(r[series]) for r in csv.DictReader(open(FRED / f"{series}.csv"))
                      if r[series] not in ("", ".")})


def main():
    k = kpis()
    b = bea()
    cpi_lodging, cpi_air, cpi_all = fred("CUSR0000SEHB"), fred("CUSR0000SETG01"), fred("CPIAUCSL")
    cols = ["quarter", "nights_m", "nights_yoy_pct", "gbv_busd", "gbv_yoy_pct", "adr_usd", "implied_adr_usd", "adr_yoy_pct",
            "revenue_musd", "revenue_yoy_pct", "adj_ebitda_musd", "adj_ebitda_margin_pct", "take_rate_pct",
            "bea_accom_nominal_yoy_pct", "bea_accom_real_yoy_pct", "bea_accom_price_yoy_pct",
            "bea_hotels_nominal_yoy_pct", "bea_hotels_real_yoy_pct", "bea_hotels_price_yoy_pct",
            "bea_inbound_foreign_travel_nominal_yoy_pct", "bea_outbound_us_travel_nominal_yoy_pct",
            "cpi_lodging_yoy_pct", "cpi_airfare_yoy_pct", "cpi_all_yoy_pct",
            "adr_real_yoy_pct", "share_gap_nights_vs_bea_real_pct"]
    with open(OUT, "w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=cols)
        w.writeheader()
        for q in sorted(k):
            r = dict(k[q])
            y, n = int(q[:4]), q[5]
            prev = k.get(f"{y - 1}Q{n}")
            r["implied_adr_usd"] = round(r["gbv_busd"] * 1000 / r["nights_m"], 2)
            r["adr_yoy_pct"] = round((r["adr_usd"] / prev["adr_usd"] - 1) * 100, 1) if prev else None
            r["bea_accom_nominal_yoy_pct"] = yoy(b[("accommodations", "nominal_saar_musd")], q)
            r["bea_accom_real_yoy_pct"] = yoy(b[("accommodations", "real_chained_2017_musd")], q)
            r["bea_accom_price_yoy_pct"] = yoy(b[("accommodations", "price_index_2017eq100")], q)
            r["bea_hotels_nominal_yoy_pct"] = yoy(b[("hotels_motels", "nominal_saar_musd")], q)
            r["bea_hotels_real_yoy_pct"] = yoy(b[("hotels_motels", "real_chained_2017_musd")], q)
            r["bea_hotels_price_yoy_pct"] = yoy(b[("hotels_motels", "price_index_2017eq100")], q)
            r["bea_inbound_foreign_travel_nominal_yoy_pct"] = yoy(b[("inbound_foreign_travel_in_us", "nominal_saar_musd")], q)
            r["bea_outbound_us_travel_nominal_yoy_pct"] = yoy(b[("foreign_travel_by_us_residents", "nominal_saar_musd")], q)
            r["cpi_lodging_yoy_pct"] = yoy(cpi_lodging, q)
            r["cpi_airfare_yoy_pct"] = yoy(cpi_air, q)
            r["cpi_all_yoy_pct"] = yoy(cpi_all, q)
            if r["adr_yoy_pct"] is not None and r["cpi_lodging_yoy_pct"] is not None:
                r["adr_real_yoy_pct"] = round(((1 + r["adr_yoy_pct"] / 100) / (1 + r["cpi_lodging_yoy_pct"] / 100) - 1) * 100, 1)
            else:
                r["adr_real_yoy_pct"] = None
            if r["nights_yoy_pct"] is not None and r["bea_accom_real_yoy_pct"] is not None:
                r["share_gap_nights_vs_bea_real_pct"] = round(r["nights_yoy_pct"] - r["bea_accom_real_yoy_pct"], 1)
            else:
                r["share_gap_nights_vs_bea_real_pct"] = None
            w.writerow({c: ("" if r.get(c) is None else r[c]) for c in cols})
    print("wrote", OUT, len(k), "quarters")


if __name__ == "__main__":
    main()
