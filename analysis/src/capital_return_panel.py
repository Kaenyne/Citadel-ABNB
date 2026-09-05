"""Capital-return panel: ABNB quarterly SBC, buybacks, RSU tax withholding, FCF and share count,
plus an annual "cannibal scorecard" for ABNB against BKNG, EXPE, META, NFLX, UBER and DASH.

Source: SEC XBRL company facts (https://data.sec.gov/api/xbrl/companyfacts/CIK##########.json), cached in
data/raw/xbrl/<TICKER>.json (gitignored; re-downloaded if missing). Cash-flow items are reported year to date,
so quarters are differenced (Q1 = 3M, Q2 = 6M - 3M, Q3 = 9M - 6M, Q4 = FY - 9M). Weighted diluted shares are
reported per quarter. SBC is the income-statement allocation (AllocatedShareBasedCompensationExpense) with the
cash-flow add-back as fallback.

The cannibal test: a buyback only returns capital to the extent it exceeds the shares issued to employees.
  net cash return   = buybacks + RSU tax withholding - SBC         (what is left after paying for dilution)
  buyback per 1% cut = cumulative buybacks / cumulative % reduction in diluted shares
  per-share test     = FCF per diluted share growth minus FCF growth (positive = the share count helped)

Outputs: data/processed/abnb_capital_return_quarterly.csv, data/processed/capital_return_scorecard_annual.csv
Run: python analysis/src/capital_return_panel.py
"""
import csv, datetime as dt, json, os, sys, time, urllib.request

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..")
RAW = os.path.join(ROOT, "data", "raw", "xbrl")
OUT_Q = os.path.join(ROOT, "data", "processed", "abnb_capital_return_quarterly.csv")
OUT_A = os.path.join(ROOT, "data", "processed", "capital_return_scorecard_annual.csv")
UA = {"User-Agent": os.environ.get("SEC_USER_AGENT", "Citadel-ABNB student research ksurapaneni@ufl.edu")}
CIKS = {"ABNB": "0001559720", "BKNG": "0001075531", "EXPE": "0001324424", "META": "0001326801",
        "NFLX": "0001065280", "UBER": "0001543151", "DASH": "0001792789"}
TAGS = {"rev": ["RevenueFromContractWithCustomerExcludingAssessedTax", "Revenues"],
        "sbc": ["AllocatedShareBasedCompensationExpense", "ShareBasedCompensation"],
        "buyback": ["PaymentsForRepurchaseOfCommonStock"],
        "withhold": ["PaymentsRelatedToTaxWithholdingForShareBasedCompensation"],
        "cfo": ["NetCashProvidedByUsedInOperatingActivities"],
        "capex": ["PaymentsToAcquirePropertyPlantAndEquipment"],
        "dil": ["WeightedAverageNumberOfDilutedSharesOutstanding"],
        "basic": ["WeightedAverageNumberOfSharesOutstandingBasic"],
        "ni": ["NetIncomeLoss"]}
YEARS = [2021, 2022, 2023, 2024, 2025]

# Airbnb stopped tagging capex separately after FY2022, so quarterly FCF from 1Q23 is keyed from the letters'
# Free Cash Flow reconciliation tables (4Q25 letter for 1Q23-4Q25, 1Q26 and 2Q26 letters). CFO - FCF = capex.
ABNB_FCF_LETTERS = {"1Q23": (1587, 1581), "2Q23": (909, 900), "3Q23": (1325, 1310), "4Q23": (63, 46),
                    "1Q24": (1923, 1909), "2Q24": (1051, 1043), "3Q24": (1078, 1074), "4Q24": (466, 458),
                    "1Q25": (1789, 1781), "2Q25": (975, 962), "3Q25": (1356, 1349), "4Q25": (526, 521),
                    "1Q26": (1708, 1704), "2Q26": (1270, 1253)}   # (CFO, FCF) in $M


def facts(ticker):
    os.makedirs(RAW, exist_ok=True)
    p = os.path.join(RAW, f"{ticker}.json")
    if not os.path.exists(p):
        req = urllib.request.Request(f"https://data.sec.gov/api/xbrl/companyfacts/CIK{CIKS[ticker]}.json", headers=UA)
        open(p, "wb").write(urllib.request.urlopen(req, timeout=60).read())
        time.sleep(0.3)
    return json.load(open(p))["facts"]["us-gaap"]


# Share splits: (effective date, factor). Values reported in filings before the split are scaled so the series is
# on the current share basis. Netflix split 10-for-1 in November 2025.
SPLITS = {"NFLX": (dt.date(2025, 11, 17), 10.0)}


def series(g, key, ticker=None):
    """(start, end) -> value. Later filings overwrite earlier ones (restatements win). All candidate tags are
    merged, the first-listed tag winning where both report a period (a tag can carry only partial periods).
    Share counts are split-adjusted via SPLITS."""
    merged = {}
    for tag in reversed(TAGS[key]):
        if tag not in g:
            continue
        units = g[tag]["units"]
        u = "USD" if "USD" in units else ("shares" if "shares" in units else list(units)[0])
        out, filed = {}, {}
        for f in sorted(units[u], key=lambda x: x["filed"]):
            if "start" in f:
                k = (dt.date.fromisoformat(f["start"]), dt.date.fromisoformat(f["end"]))
                out[k], filed[k] = f["val"], dt.date.fromisoformat(f["filed"])
        if u == "shares" and ticker in SPLITS:
            sd, fac = SPLITS[ticker]
            out = {k: (v * fac if filed[k] < sd else v) for k, v in out.items()}
        merged.update(out)
    return merged


def span(s, a, b):
    return s.get((a, b))


def fy(s, y):
    return span(s, dt.date(y, 1, 1), dt.date(y, 12, 31))


def quarter(s, y, q, flow=True):
    """Discrete quarter from a (start,end) series. Flow items are YTD-differenced; shares are read directly."""
    j1 = dt.date(y, 1, 1)
    ends = {1: dt.date(y, 3, 31), 2: dt.date(y, 6, 30), 3: dt.date(y, 9, 30), 4: dt.date(y, 12, 31)}
    starts = {1: j1, 2: dt.date(y, 4, 1), 3: dt.date(y, 7, 1), 4: dt.date(y, 10, 1)}
    v = span(s, starts[q], ends[q])
    if v is not None:
        return v
    if not flow:
        return None
    if q == 1:
        return span(s, j1, ends[1])
    a, b = span(s, j1, ends[q]), span(s, j1, ends[q - 1])
    return None if a is None or b is None else a - b


def m(v):
    return "" if v is None else round(v / 1e6, 1)


def main():
    # ---------------- ABNB quarterly panel
    g = facts("ABNB")
    S = {k: series(g, k, "ABNB") for k in TAGS}
    rows = []
    prev_dil = {}
    for y in range(2021, dt.date.today().year + 1):
        for q in range(1, 5):
            rev = quarter(S["rev"], y, q)
            if rev is None:
                continue
            r = {"quarter": f"{q}Q{str(y)[2:]}", "revenue_musd": m(rev)}
            sbc, bb, wh = quarter(S["sbc"], y, q), quarter(S["buyback"], y, q), quarter(S["withhold"], y, q)
            cfo, capex = quarter(S["cfo"], y, q), quarter(S["capex"], y, q)
            dil, basic = quarter(S["dil"], y, q, flow=False), quarter(S["basic"], y, q, flow=False)
            fcf = None if cfo is None or capex is None else cfo - capex
            lab = f"{q}Q{str(y)[2:]}"
            if fcf is None and lab in ABNB_FCF_LETTERS:
                cfo, fcf = ABNB_FCF_LETTERS[lab][0] * 1e6, ABNB_FCF_LETTERS[lab][1] * 1e6
                capex = cfo - fcf
            if q == 4:  # Q4 weighted shares are not tagged; approximate from the FY average and Q1-Q3
                for key in ("dil", "basic"):
                    fyv = fy(S[key], y)
                    q13 = [quarter(S[key], y, k, flow=False) for k in (1, 2, 3)]
                    if fyv and all(q13):
                        if key == "dil":
                            dil = 4 * fyv - sum(q13)
                        else:
                            basic = 4 * fyv - sum(q13)
            r.update({"sbc_musd": m(sbc), "buybacks_musd": m(bb), "rsu_tax_withholding_musd": m(wh), "cfo_musd": m(cfo),
                      "capex_musd": m(capex), "fcf_musd": m(fcf), "diluted_wa_shares_m": m(dil), "basic_wa_shares_m": m(basic)})
            if sbc is not None and rev:
                r["sbc_pct_rev"] = round(100 * sbc / rev, 1)
            if fcf and sbc is not None:
                r["sbc_pct_fcf"] = round(100 * sbc / fcf, 1)
                r["buyback_pct_fcf"] = round(100 * (bb or 0) / fcf, 1)
                r["net_cash_return_musd"] = m((bb or 0) + (wh or 0) - sbc)
            if dil and (y - 1, q) in prev_dil and prev_dil[(y - 1, q)]:
                r["diluted_shares_yoy_pct"] = round(100 * (dil / prev_dil[(y - 1, q)] - 1), 2)
            if dil and fcf is not None:
                r["fcf_per_diluted_share"] = round(fcf / dil, 2)
            prev_dil[(y, q)] = dil
            rows.append(r)
    keys = ["quarter", "revenue_musd", "sbc_musd", "buybacks_musd", "rsu_tax_withholding_musd", "cfo_musd", "capex_musd", "fcf_musd",
            "diluted_wa_shares_m", "basic_wa_shares_m", "sbc_pct_rev", "sbc_pct_fcf", "buyback_pct_fcf", "net_cash_return_musd",
            "diluted_shares_yoy_pct", "fcf_per_diluted_share"]
    with open(OUT_Q, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=keys); w.writeheader(); w.writerows(rows)
    print(f"ABNB quarterly panel: {len(rows)} quarters -> {os.path.normpath(OUT_Q)}")
    print("q | rev | SBC | buyback | withhold | FCF | dil shares | SBC%rev | SBC%FCF | BB%FCF | net return | dil yoy")
    for r in rows:
        print(" | ".join(str(r.get(k, "")) for k in ["quarter", "revenue_musd", "sbc_musd", "buybacks_musd", "rsu_tax_withholding_musd", "fcf_musd",
                                                      "diluted_wa_shares_m", "sbc_pct_rev", "sbc_pct_fcf", "buyback_pct_fcf", "net_cash_return_musd", "diluted_shares_yoy_pct"]))

    # ---------------- annual cannibal scorecard
    out = []
    print("\nTicker | FY | rev | SBC | buyback | withhold | FCF | dil shares | SBC%rev | SBC%FCF | (BB+WH)%FCF | net return %FCF | dil yoy% | FCF/sh")
    for t in CIKS:
        g = facts(t)
        S = {k: series(g, k, t) for k in TAGS}
        hist = {}
        for y in YEARS:
            rev, sbc, bb, wh = fy(S["rev"], y), fy(S["sbc"], y), fy(S["buyback"], y), fy(S["withhold"], y)
            cfo, capex, dil, ni = fy(S["cfo"], y), fy(S["capex"], y), fy(S["dil"], y), fy(S["ni"], y)
            if rev is None or dil is None:
                continue
            fcf = None if cfo is None or capex is None else cfo - capex
            if fcf is None and t == "ABNB":
                fy_l = [v for k, v in ABNB_FCF_LETTERS.items() if k.endswith(str(y)[2:]) and k[0] in "1234"]
                if len(fy_l) == 4:
                    cfo, fcf = sum(v[0] for v in fy_l) * 1e6, sum(v[1] for v in fy_l) * 1e6
            bb, wh = bb or 0.0, wh or 0.0
            hist[y] = {"rev": rev, "sbc": sbc, "bb": bb, "wh": wh, "fcf": fcf, "dil": dil}
            r = {"ticker": t, "fy": y, "revenue_musd": m(rev), "sbc_musd": m(sbc), "buybacks_musd": m(bb), "rsu_tax_withholding_musd": m(wh),
                 "fcf_musd": m(fcf), "net_income_musd": m(ni), "diluted_wa_shares_m": m(dil),
                 "sbc_pct_rev": round(100 * sbc / rev, 1) if sbc else "",
                 "sbc_pct_fcf": round(100 * sbc / fcf, 1) if sbc and fcf else "",
                 "buyback_plus_withholding_pct_fcf": round(100 * (bb + wh) / fcf, 1) if fcf else "",
                 "net_cash_return_pct_fcf": round(100 * (bb + wh - sbc) / fcf, 1) if fcf and sbc is not None else "",
                 "diluted_shares_yoy_pct": round(100 * (dil / hist[y - 1]["dil"] - 1), 2) if (y - 1) in hist else "",
                 "fcf_per_diluted_share": round(fcf / dil, 2) if fcf else ""}
            out.append(r)
            print(" | ".join(str(r[k]) for k in ["ticker", "fy", "revenue_musd", "sbc_musd", "buybacks_musd", "rsu_tax_withholding_musd", "fcf_musd", "diluted_wa_shares_m",
                                                  "sbc_pct_rev", "sbc_pct_fcf", "buyback_plus_withholding_pct_fcf", "net_cash_return_pct_fcf", "diluted_shares_yoy_pct", "fcf_per_diluted_share"]))
        # 2022 -> 2025 summary
        if 2022 in hist and 2025 in hist and all(hist[y]["fcf"] for y in (2022, 2023, 2024, 2025)):
            cum_bb = sum(hist[y]["bb"] + hist[y]["wh"] for y in (2023, 2024, 2025))
            cum_sbc = sum(hist[y]["sbc"] or 0 for y in (2023, 2024, 2025))
            cut = 100 * (1 - hist[2025]["dil"] / hist[2022]["dil"])
            fcf_g = (hist[2025]["fcf"] / hist[2022]["fcf"] - 1) if hist[2022]["fcf"] and hist[2025]["fcf"] else None
            fps_g = ((hist[2025]["fcf"] / hist[2025]["dil"]) / (hist[2022]["fcf"] / hist[2022]["dil"]) - 1) if fcf_g is not None else None
            summ = {"ticker": t, "fy": "2023-2025 cumulative", "buybacks_musd": m(cum_bb), "sbc_musd": m(cum_sbc),
                    "net_cash_return_pct_fcf": round(100 * (cum_bb - cum_sbc) / sum(hist[y]["fcf"] for y in (2023, 2024, 2025)), 1),
                    "diluted_shares_yoy_pct": round(-cut, 2),
                    "revenue_musd": "", "rsu_tax_withholding_musd": "", "fcf_musd": "", "net_income_musd": "", "diluted_wa_shares_m": "",
                    "sbc_pct_rev": "", "sbc_pct_fcf": "", "buyback_plus_withholding_pct_fcf": "", "fcf_per_diluted_share": ""}
            summ["buyback_musd_per_1pct_share_cut"] = round(cum_bb / 1e6 / cut, 0) if cut > 0 else "n/a (count rose)"
            summ["fcf_growth_22_25_pct"] = round(100 * fcf_g, 1) if fcf_g is not None else ""
            summ["fcf_per_share_growth_22_25_pct"] = round(100 * fps_g, 1) if fps_g is not None else ""
            out.append(summ)
            print(f"  {t} 2022->2025: diluted shares {-cut:+.1f}%, buybacks+withholding ${cum_bb/1e9:.1f}B vs SBC ${cum_sbc/1e9:.1f}B, "
                  f"${summ['buyback_musd_per_1pct_share_cut']}M per 1% cut, FCF {summ['fcf_growth_22_25_pct']}% vs FCF/share {summ['fcf_per_share_growth_22_25_pct']}%")
    keys = ["ticker", "fy", "revenue_musd", "sbc_musd", "buybacks_musd", "rsu_tax_withholding_musd", "fcf_musd", "net_income_musd", "diluted_wa_shares_m",
            "sbc_pct_rev", "sbc_pct_fcf", "buyback_plus_withholding_pct_fcf", "net_cash_return_pct_fcf", "diluted_shares_yoy_pct", "fcf_per_diluted_share",
            "buyback_musd_per_1pct_share_cut", "fcf_growth_22_25_pct", "fcf_per_share_growth_22_25_pct"]
    with open(OUT_A, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=keys, extrasaction="ignore"); w.writeheader(); w.writerows(out)
    print(f"\nscorecard -> {os.path.normpath(OUT_A)}")


if __name__ == "__main__":
    sys.exit(main())
