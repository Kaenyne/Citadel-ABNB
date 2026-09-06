"""Two builds on Theo's alt-data acquisition (PR #10): the Eurostat platform-nights benchmark and the
bookings-backlog indicators from XBRL.

A. Eurostat `tour_ce_omr` (experimental statistics): guest nights at short-stay accommodation booked through
   Airbnb, Booking, Expedia and TripAdvisor, supplied by the platforms under agreement with Eurostat; monthly,
   2018 to the latest published month, EU27 and 31 countries. This is the official size of the European
   platform category, so Airbnb's EMEA growth against it is a share test, and country growth across
   regulatory regimes (Spain, Italy, Portugal, Greece, Netherlands) is a regulatory-impact read. Also the
   domestic / foreign guest split (c_resid) and, from `tour_ce_oam` (annual), entire-home versus shared.
   Public API, no key: https://ec.europa.eu/eurostat/api/dissemination/statistics/1.0/data/<dataset>
   Cached raw JSON in data/raw/eurostat/ (gitignored). Licence: Eurostat re-use policy, attribute Eurostat.

B. Backlog indicators from SEC XBRL company facts (CIK 1559720): unearned fees (deferred revenue,
   `ContractWithCustomerLiabilityCurrent`) and funds held for clients (`FundsHeldForClients`) at quarter end,
   against next-quarter revenue. Theo's handoff flags the trap: from Q3 2025 Reserve Now Pay Later defers guest
   payment toward check-in, so unearned fees stop tracking bookings (CFO, Q2 2026 call). The regression is fit
   on the pre-RNPL quarters and the 2026 gap is reported as the RNPL effect, not as demand.

Outputs (data/processed/):
  eurostat_platform_nights_monthly.csv     EU27 and country nights, monthly, with y/y
  eurostat_platform_nights_quarterly.csv   EU27 quarterly nights, y/y, next to Airbnb EMEA revenue y/y and total nights y/y
  eurostat_platform_nights_by_country.csv  2019 to 2025 annual nights and growth by country, plus latest quarter
  abnb_backlog_indicators.csv              quarterly unearned fees, funds held, y/y, next-quarter revenue and fit
Figures (analysis/figures/): eurostat_platform_vs_abnb_emea.png, eurostat_platform_country_growth.png, abnb_backlog_indicators.png
Run: py -3.13 analysis/src/abnb_eu_platform_and_backlog.py
"""
import json, sys
from pathlib import Path
import numpy as np, pandas as pd, requests
import statsmodels.api as sm

ROOT = Path(__file__).resolve().parents[2]
RAW = ROOT / "data/raw/eurostat"
RAWX = ROOT / "data/raw/xbrl"
PROC = ROOT / "data/processed"
FIG = ROOT / "analysis/figures"
UA = {"User-Agent": "Citadel-ABNB student research ksurapaneni@ufl.edu"}
EUROSTAT = "https://ec.europa.eu/eurostat/api/dissemination/statistics/1.0/data/{ds}"
REGIONAL_REVENUE = ROOT / "citadel-abnb-files 2/data/processed/airbnb_regional_revenue_quarterly.csv"  # 10-Q geographic revenue (Jessie)
RNPL_FIRST_QUARTER = "3Q25"  # US launch of Reserve Now Pay Later; >70% of eligible US bookings by 4Q25, >20% of GBV by 2Q26


def log(m):
    print(m, flush=True)


# ------------------------------------------------------------------------------------------- Eurostat
def eurostat(ds, params, cache):
    p = RAW / cache
    if p.exists():
        return json.loads(p.read_text(encoding="utf-8"))
    r = requests.get(EUROSTAT.format(ds=ds), params={"format": "JSON", "lang": "EN", **params}, headers=UA, timeout=180)
    r.raise_for_status()
    RAW.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(r.json()), encoding="utf-8")
    return r.json()


def jsonstat_to_frame(j):
    dims, sizes = j["id"], j["size"]
    cats = {d: list(j["dimension"][d]["category"]["index"].keys()) for d in dims}
    strides = [int(np.prod(sizes[i + 1:])) if i + 1 < len(sizes) else 1 for i in range(len(sizes))]
    rows = []
    for key, v in j["value"].items():
        k = int(key); idx = []
        for s in strides:
            idx.append(k // s); k %= s
        rec = {d: cats[d][ix] for d, ix in zip(dims, idx)}; rec["value"] = v; rows.append(rec)
    return pd.DataFrame(rows)


def platform_nights():
    j = eurostat("tour_ce_omr", {"indic_to": "NGT_SP", "unit": "NR"}, "tour_ce_omr_ngt_sp_all_resid.json")
    d = jsonstat_to_frame(j)
    d = d[d.month != "TOTAL"].copy()
    d["date"] = pd.to_datetime(d.time + "-" + d.month.str[1:] + "-01")
    tot = d[d.c_resid == "TOTAL"].pivot_table(index="date", columns="geo", values="value").sort_index()
    resid = d[d.geo == "EU27_2020"].pivot_table(index="date", columns="c_resid", values="value").sort_index()
    m = pd.DataFrame({"eu27_nights": tot["EU27_2020"], "eu27_domestic": resid.get("DOM"), "eu27_foreign": resid.get("FOR")})
    m["eu27_yoy_pct"] = (m.eu27_nights / m.eu27_nights.shift(12) - 1) * 100
    m["eu27_domestic_yoy_pct"] = (m.eu27_domestic / m.eu27_domestic.shift(12) - 1) * 100
    m["eu27_foreign_yoy_pct"] = (m.eu27_foreign / m.eu27_foreign.shift(12) - 1) * 100
    m["foreign_share_pct"] = m.eu27_foreign / m.eu27_nights * 100
    for c in tot.columns:
        if c != "EU27_2020":
            m[f"{c}_nights"] = tot[c]
    m.index.name = "month"
    # quarterly EU27
    q = tot["EU27_2020"].resample("QE").sum()
    cnt = tot["EU27_2020"].resample("QE").count()
    q = q[cnt == 3]
    qdf = pd.DataFrame({"eu27_nights": q}); qdf["eu27_yoy_pct"] = (qdf.eu27_nights / qdf.eu27_nights.shift(4) - 1) * 100
    qdf["quarter"] = [f"{p.quarter}Q{str(p.year)[2:]}" for p in qdf.index]
    # country table: annual nights, growth 2024 and 2025, Q1 2026 y/y, share of EU 2025
    a = tot.resample("YE").sum(); acnt = tot.resample("YE").count(); a = a.where(acnt == 12)
    a.index = a.index.year
    rows = []
    q1_26 = tot.loc["2026-01":"2026-03"].sum(); q1_25 = tot.loc["2025-01":"2025-03"].sum()
    q1_ok = tot.loc["2026-01":"2026-03"].notna().all()
    for c in tot.columns:
        rows.append(dict(geo=c, nights_2019_m=a.loc[2019, c] / 1e6 if 2019 in a.index else None, nights_2023_m=a.loc[2023, c] / 1e6, nights_2024_m=a.loc[2024, c] / 1e6, nights_2025_m=a.loc[2025, c] / 1e6,
                         growth_2024_pct=(a.loc[2024, c] / a.loc[2023, c] - 1) * 100, growth_2025_pct=(a.loc[2025, c] / a.loc[2024, c] - 1) * 100,
                         growth_2025_vs_2019_pct=(a.loc[2025, c] / a.loc[2019, c] - 1) * 100 if 2019 in a.index and a.loc[2019, c] > 0 else None,
                         q1_2026_yoy_pct=(q1_26[c] / q1_25[c] - 1) * 100 if q1_ok[c] and q1_25[c] > 0 else None,
                         share_of_eu27_2025_pct=a.loc[2025, c] / a.loc[2025, "EU27_2020"] * 100 if c != "EU27_2020" else 100.0))
    ctry = pd.DataFrame(rows).sort_values("nights_2025_m", ascending=False)
    return m, qdf, ctry


def compare_with_airbnb(qdf):
    rr = pd.read_csv(REGIONAL_REVENUE)
    rr["quarter"] = [f"{q[-1]}Q{q[2:4]}" for q in rr.quarter]
    rr = rr.sort_values("quarter", key=lambda s: s.map(lambda q: (int(q[2:]), int(q[0]))))
    rr["emea_yoy_pct"] = (rr.emea_usd_m / rr.emea_usd_m.shift(4) - 1) * 100
    rr["total_rev_yoy_pct"] = (rr.total_usd_m / rr.total_usd_m.shift(4) - 1) * 100
    k = pd.read_csv(PROC / "abnb_quarterly_kpis_from_study.csv")
    k["nights_yoy_pct"] = (k.nights_m / k.nights_m.shift(4) - 1) * 100
    out = qdf.merge(rr[["quarter", "emea_usd_m", "emea_yoy_pct", "total_rev_yoy_pct"]], on="quarter", how="left").merge(k[["quarter", "nights_yoy_pct"]], on="quarter", how="left")
    out["emea_minus_platform_pts"] = out.emea_yoy_pct - out.eu27_yoy_pct
    return out


# ------------------------------------------------------------------------------------------- XBRL backlog
def xbrl_facts():
    RAWX.mkdir(parents=True, exist_ok=True)
    p = RAWX / "ABNB_companyfacts.json"
    if not p.exists():
        r = requests.get("https://data.sec.gov/api/xbrl/companyfacts/CIK0001559720.json", headers=UA, timeout=120); r.raise_for_status()
        p.write_text(r.text, encoding="utf-8")
    return json.loads(p.read_text(encoding="utf-8"))["facts"]["us-gaap"]


def series(f, tags):
    for t in tags:
        if t in f:
            u = f[t]["units"]["USD"]
            rows = {}
            for r in u:
                if r.get("form") in ("10-Q", "10-K") and "start" not in r:
                    rows[r["end"]] = r["val"] / 1e6
            if rows:
                s = pd.Series(rows).sort_index(); s.index = pd.to_datetime(s.index); return s, t
    return None, None


def backlog():
    f = xbrl_facts()
    unearned, tag_u = series(f, ["ContractWithCustomerLiabilityCurrent", "DeferredRevenueCurrent", "ContractWithCustomerLiability"])
    funds, tag_f = series(f, ["FundsHeldForClients"])
    k = pd.read_csv(PROC / "abnb_quarterly_kpis_from_study.csv")
    k["end"] = [pd.Timestamp(2000 + int(q[2:4]), int(q[0]) * 3, 1) + pd.offsets.MonthEnd(0) for q in k.quarter]
    b = pd.DataFrame({"unearned_fees_musd": unearned, "funds_held_musd": funds})
    b.index.name = "quarter_end"; b = b.reset_index()
    b["quarter"] = [f"{p.quarter}Q{str(p.year)[2:]}" for p in b.quarter_end]
    b = b.merge(k[["quarter", "revenue_musd", "gbv_b", "nights_m"]], on="quarter", how="left")
    b["gbv_musd"] = b.gbv_b * 1000
    for c in ("unearned_fees_musd", "funds_held_musd", "revenue_musd", "gbv_musd"):
        b[c + "_yoy_pct"] = (b[c] / b[c].shift(4) - 1) * 100
    b["next_q_revenue_musd"] = b.revenue_musd.shift(-1)
    b["next_q_revenue_yoy_pct"] = b.revenue_musd_yoy_pct.shift(-1)
    b["unearned_to_next_q_revenue"] = b.unearned_fees_musd / b.next_q_revenue_musd
    b["rnpl_era"] = b.quarter.map(lambda q: (int(q[2:]), int(q[0])) >= (25, 3))
    b["unearned_tag"], b["funds_tag"] = tag_u, tag_f
    # fit: next-quarter revenue y/y on unearned-fees y/y, pre-RNPL quarters with a full year of history
    fit = b[(~b.rnpl_era) & b.unearned_fees_musd_yoy_pct.notna() & b.next_q_revenue_yoy_pct.notna() & (b.quarter_end >= "2022-03-31")]
    X = sm.add_constant(fit.unearned_fees_musd_yoy_pct.astype(float)); m = sm.OLS(fit.next_q_revenue_yoy_pct.astype(float), X).fit()
    b["fitted_next_q_revenue_yoy_pct"] = m.params["const"] + m.params["unearned_fees_musd_yoy_pct"] * b.unearned_fees_musd_yoy_pct
    b["rnpl_gap_pts"] = np.where(b.rnpl_era, b.next_q_revenue_yoy_pct - b.fitted_next_q_revenue_yoy_pct, np.nan)
    stats = dict(n=int(m.nobs), r2=m.rsquared, const=m.params["const"], slope=m.params["unearned_fees_musd_yoy_pct"], t_slope=m.tvalues["unearned_fees_musd_yoy_pct"], p_slope=m.pvalues["unearned_fees_musd_yoy_pct"])
    fit2 = b[b.funds_held_musd_yoy_pct.notna() & b.next_q_revenue_yoy_pct.notna() & (b.quarter_end >= "2022-03-31")]
    X2 = sm.add_constant(fit2.funds_held_musd_yoy_pct.astype(float)); m2 = sm.OLS(fit2.next_q_revenue_yoy_pct.astype(float), X2).fit()
    stats2 = dict(n=int(m2.nobs), r2=m2.rsquared, const=m2.params["const"], slope=m2.params["funds_held_musd_yoy_pct"], t_slope=m2.tvalues["funds_held_musd_yoy_pct"], p_slope=m2.pvalues["funds_held_musd_yoy_pct"])
    b["fitted_next_q_revenue_yoy_funds_pct"] = m2.params["const"] + m2.params["funds_held_musd_yoy_pct"] * b.funds_held_musd_yoy_pct
    return b, stats, stats2


# ------------------------------------------------------------------------------------------- figures
def figures(m, cmp_, ctry, b):
    import matplotlib; matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    FIG.mkdir(parents=True, exist_ok=True)
    foot_e = "Source: Eurostat tour_ce_omr (experimental: nights booked via Airbnb, Booking, Expedia, TripAdvisor); Airbnb 10-Q geographic revenue; Citadel-ABNB analysis"
    c = cmp_.dropna(subset=["emea_yoy_pct"])
    fig, ax = plt.subplots(figsize=(10, 5))
    x = np.arange(len(c))
    ax.bar(x - 0.2, c.eu27_yoy_pct, width=0.4, color="#4C72B0", label="EU27 platform nights y/y (all four platforms)")
    ax.bar(x + 0.2, c.emea_yoy_pct, width=0.4, color="#DD8452", label="Airbnb EMEA revenue y/y (USD, reported)")
    ax.plot(x, c.nights_yoy_pct, "k_", ms=16, mew=2, label="Airbnb global nights y/y")
    ax.set_xticks(x); ax.set_xticklabels(c.quarter); ax.axhline(0, color="grey", lw=0.8); ax.set_ylabel("%"); ax.grid(alpha=0.3, axis="y"); ax.legend(frameon=False, fontsize=8)
    ax.set_title("Airbnb EMEA against the official European platform category", loc="left", fontweight="bold", fontsize=11)
    fig.text(0.01, 0.005, foot_e, fontsize=7, color="grey"); fig.tight_layout(); fig.savefig(FIG / "eurostat_platform_vs_abnb_emea.png", dpi=150); plt.close(fig)
    top = ctry[(ctry.geo != "EU27_2020")].head(14).sort_values("growth_2025_pct")
    fig, ax = plt.subplots(figsize=(10, 5.5))
    y = np.arange(len(top))
    ax.barh(y - 0.2, top.growth_2024_pct, height=0.4, color="#A6BDDB", label="2024")
    ax.barh(y + 0.2, top.growth_2025_pct, height=0.4, color="#4C72B0", label="2025")
    ax.plot(top.q1_2026_yoy_pct, y, "o", color="#DD8452", label="Q1 2026 y/y")
    ax.set_yticks(y); ax.set_yticklabels([f"{g} ({s:.0f}%)" for g, s in zip(top.geo, top.share_of_eu27_2025_pct)]); ax.axvline(0, color="grey", lw=0.8); ax.set_xlabel("platform nights growth, %"); ax.grid(alpha=0.3, axis="x"); ax.legend(frameon=False, fontsize=8)
    ax.set_title("Platform nights growth by country, 14 largest markets (share of EU27 nights in brackets)", loc="left", fontweight="bold", fontsize=11)
    fig.text(0.01, 0.005, foot_e, fontsize=7, color="grey"); fig.tight_layout(); fig.savefig(FIG / "eurostat_platform_country_growth.png", dpi=150); plt.close(fig)
    bb = b[b.unearned_fees_musd_yoy_pct.notna() & (b.quarter_end >= "2022-03-31")]
    fig, ax = plt.subplots(figsize=(10, 5))
    x = np.arange(len(bb))
    ax.plot(x, bb.unearned_fees_musd_yoy_pct, marker="o", color="#4C72B0", label="Unearned fees y/y (quarter end)")
    ax.plot(x, bb.funds_held_musd_yoy_pct, marker="s", color="#55A868", label="Funds held for clients y/y")
    ax.plot(x, bb.next_q_revenue_yoy_pct, marker="^", color="#DD8452", label="Next-quarter revenue y/y")
    first = bb.index[bb.rnpl_era].min()
    if pd.notna(first):
        ax.axvspan(list(bb.index).index(first) - 0.5, len(bb) - 0.5, color="#C44E52", alpha=0.08); ax.text(list(bb.index).index(first) - 0.4, ax.get_ylim()[1] * 0.92, "RNPL era: unearned fees stop tracking bookings", fontsize=8, color="#C44E52")
    ax.set_xticks(x); ax.set_xticklabels(bb.quarter); ax.axhline(0, color="grey", lw=0.8); ax.set_ylabel("%"); ax.grid(alpha=0.3, axis="y"); ax.legend(frameon=False, fontsize=8)
    ax.set_title("Bookings backlog indicators against the revenue they precede", loc="left", fontweight="bold", fontsize=11)
    fig.text(0.01, 0.005, "Source: SEC XBRL company facts (CIK 1559720); shareholder letters; Citadel-ABNB analysis", fontsize=7, color="grey"); fig.tight_layout(); fig.savefig(FIG / "abnb_backlog_indicators.png", dpi=150); plt.close(fig)


def main():
    m, qdf, ctry = platform_nights()
    cmp_ = compare_with_airbnb(qdf)
    b, st, st2 = backlog()
    m.round(2).to_csv(PROC / "eurostat_platform_nights_monthly.csv")
    cmp_.round(2).to_csv(PROC / "eurostat_platform_nights_quarterly.csv", index=False)
    ctry.round(2).to_csv(PROC / "eurostat_platform_nights_by_country.csv", index=False)
    b.round(3).to_csv(PROC / "abnb_backlog_indicators.csv", index=False)
    figures(m, cmp_, ctry, b)
    pd.set_option("display.width", 250); pd.set_option("display.max_columns", 30)
    log(f"Eurostat: months {m.index.min():%Y-%m} to {m.index.max():%Y-%m}; last EU27 y/y {m.eu27_yoy_pct.dropna().iloc[-1]:.1f}%")
    log(m[["eu27_nights", "eu27_yoy_pct", "eu27_domestic_yoy_pct", "eu27_foreign_yoy_pct", "foreign_share_pct"]].tail(15).round(1).to_string())
    log(cmp_.round(1).to_string(index=False))
    log(ctry.head(16).round(1).to_string(index=False))
    log(b[["quarter", "unearned_fees_musd", "unearned_fees_musd_yoy_pct", "funds_held_musd", "funds_held_musd_yoy_pct", "revenue_musd_yoy_pct", "next_q_revenue_yoy_pct", "fitted_next_q_revenue_yoy_pct", "rnpl_gap_pts", "unearned_to_next_q_revenue"]].round(1).to_string(index=False))
    log(f"fit unearned: {st}"); log(f"fit funds held: {st2}")


if __name__ == "__main__":
    sys.exit(main())
