"""G3: rank every external source by (coverage of Jul-Sep 2026) x (backtest quality).

Workstream G, Q3 2026 nowcast run. Krishang Surapaneni (compiled with Claude Code).

Inputs (all produced by G1/G2 or hand-curated from web research with URLs recorded):
  data/processed/q3nowcast/G/source_inventory_raw.csv   (G1: machine-pulled series)
  data/processed/q3nowcast/G/G_backtests_all.csv        (G2: note-08 walk-forward)
  data/processed/q3nowcast/G/str_weekly_us_3q26.csv     (CoStar/STR weekly, hand-keyed)
  data/processed/q3nowcast/G/intra_quarter_commentary.csv

Output: source_inventory.csv, the ranked table that goes in the note.

Scoring, both 0-3 and both DESCRIPTIVE (a scoring rule I chose, not estimated):
  coverage_score  3 = covers Jul, Aug and at least part of Sep 2026 today
                  2 = Jul and Aug today, Sep arrives before the 5 Nov print
                  1 = Jul only today
                  0 = does not reach 3Q26 at all
  backtest_score  3 = best walk-forward RMSE ratio vs naive below 0.80 on nights
                  2 = 0.80 to 0.95
                  1 = 0.95 to 1.00
                  0 = never beats naive, or no quarterly history to test
"""
from __future__ import annotations

import os

import numpy as np
import pandas as pd

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
OUT = os.path.join(ROOT, "data", "processed", "q3nowcast", "G")
ACCESS = "2026-09-11"

# Sources that are not machine-pulled series. Every row carries its URL and what
# it measures; "tested" says whether G2 could backtest it at all.
MANUAL = [
    dict(source="CoStar/STR US weekly hotel RevPAR", family="Hotel RevPAR",
         measures="US hotel occupancy, ADR, RevPAR y/y, Top 25 markets",
         basis="hotel", nearest_abnb="nights (occupancy) and ADR (rate)",
         frequency="weekly", lag_days=6, coverage_end="2026-09-05",
         free="yes (trade-press reprint; costar.com 403s)",
         hist_to_2023="yes", tested="proxied by MAR/HLT quarterly RevPAR in G2",
         url="https://lodgingmagazine.com/costar-u-s-hotel-industry-continues-to-report-positive-year-over-year-comparisons-september-1/"),
    dict(source="CoStar/STR US monthly hotel RevPAR", family="Hotel RevPAR",
         measures="US hotel occupancy, ADR, RevPAR y/y, full month",
         basis="hotel", nearest_abnb="nights and ADR", frequency="monthly",
         lag_days=26, coverage_end="2026-07-31", free="yes",
         hist_to_2023="yes", tested="proxied by MAR/HLT quarterly RevPAR in G2",
         url="https://lodgingmagazine.com/costar-reports-positive-u-s-hotel-industry-performance-results-in-july/"),
    dict(source="AirDNA free monthly Europe/US STR market review", family="STR platform",
         measures="short-term-rental demand nights, ADR, RevPAR, occupancy y/y plus 1-2 month forward pacing",
         basis="platform STR", nearest_abnb="nights AND ADR, same asset class",
         frequency="monthly", lag_days=13, coverage_end="2026-07-31",
         free="yes", hist_to_2023="not in a free machine-readable archive",
         tested="NO: free releases are snippets, no continuous series to backtest",
         url="https://www.airdna.co/monthly-market-review"),
    dict(source="BofA Institute Consumer Checkpoint", family="Card spend",
         measures="card spend per household, total and by income cohort; lodging and airline PLOTTED ONLY",
         basis="spend", nearest_abnb="GBV (US lodging spend)", frequency="monthly",
         lag_days=11, coverage_end="2026-07-31", free="yes (PDF)",
         hist_to_2023="yes in the PDFs, not as a series",
         tested="NO: the lodging y/y is a chart bar with no printed value",
         url="https://institute.bankofamerica.com/consumer-checkpoint.html"),
    dict(source="Mastercard SpendingPulse monthly US", family="Card spend",
         measures="retail ex-auto, restaurant, lodging, airline y/y",
         basis="spend", nearest_abnb="GBV", frequency="holiday season only now",
         lag_days=np.nan, coverage_end="2025-12-24", free="press releases only",
         hist_to_2023="no", tested="NO: no free monthly release since ~2022",
         url="https://www.mastercard.com/news/press/"),
    dict(source="AAA holiday travel forecasts", family="Trips",
         measures="US travellers 50+ miles by mode", basis="trips",
         nearest_abnb="nights (US domestic)", frequency="5-6 per year",
         lag_days=np.nan, coverage_end="2026-07-05", free="yes",
         hist_to_2023="yes for holidays",
         tested="NO: 5 irregular observations per year, not quarterly",
         url="https://newsroom.aaa.com/2026/06/72-2-million-americans-expected-to-travel-over-july-4th-week/"),
    dict(source="Airlines for America summer/Labor Day forecast", family="Trips",
         measures="US airline passengers and y/y", basis="flights",
         nearest_abnb="nights", frequency="discontinued", lag_days=np.nan,
         coverage_end="2024-05", free="yes but NOT PUBLISHED in 2026",
         hist_to_2023="no", tested="NO: does not exist for 2026",
         url="https://www.airlines.org/news/"),
    dict(source="IATA Air Passenger Market Analysis", family="Flights",
         measures="global and regional RPK, ASK, load factor y/y", basis="flights",
         nearest_abnb="nights (very loose)", frequency="monthly", lag_days=31,
         coverage_end="2026-07-31", free="yes (press release)",
         hist_to_2023="yes in releases, not free as a series",
         tested="NO: not pulled as a series; TSA is the tested air proxy",
         url="https://www.iata.org/en/pressroom/2026-releases/08-31-air-passenger-demand-grows-july/"),
    dict(source="Airbnb newsroom travel-trend posts", family="Company PR",
         measures="search and wishlist growth, event-level booking anecdotes",
         basis="company-selected", nearest_abnb="searches, not nights",
         frequency="ad hoc", lag_days=0, coverage_end="2026-09-10", free="yes",
         hist_to_2023="no", tested="NO: no aggregate nights or GBV figure is ever published",
         url="https://news.airbnb.com/"),
    dict(source="JNTO Japan inbound visitor arrivals", family="Asia arrivals",
         measures="foreign visitor arrivals to Japan and y/y", basis="arrivals",
         nearest_abnb="APAC nights (Japan only)", frequency="monthly", lag_days=19,
         coverage_end="2026-07-31", free="yes",
         hist_to_2023="yes", tested="NO: landing page cached only, series not machine-pulled",
         url="https://statistics.jnto.go.jp/en/"),
    dict(source="UK ONS overseas travel and tourism (monthly)", family="EMEA arrivals",
         measures="UK inbound visits and spend", basis="arrivals",
         nearest_abnb="EMEA nights", frequency="DISCONTINUED", lag_days=np.nan,
         coverage_end="2022-12", free="yes",
         hist_to_2023="no", tested="NO: the monthly series stopped in 2023",
         url="https://www.ons.gov.uk/peoplepopulationandcommunity/leisureandtourism/bulletins/overseastravelandtourism/latest"),
    dict(source="Eurocontrol European daily flight traffic", family="Flights",
         measures="European network flights per day", basis="flights",
         nearest_abnb="EMEA nights (loose)", frequency="daily", lag_days=1,
         coverage_end="2026-09-03", free="yes but JS-rendered, no scrapable values",
         hist_to_2023="yes on the dashboard", tested="NO: could not extract a series",
         url="https://www.eurocontrol.int/Economics/DailyTrafficVariation-States.html"),
    dict(source="Similarweb free tier airbnb.com visits", family="Web traffic",
         measures="airbnb.com monthly visits and engagement", basis="web",
         nearest_abnb="bookings funnel", frequency="monthly, released by the 10th",
         lag_days=11, coverage_end="2026-08-31 (3-month tile only)",
         free="partly, history gated", hist_to_2023="no at the free tier",
         tested="NO: no free time series; the tile is a 3-month aggregate",
         url="https://www.similarweb.com/website/airbnb.com/"),
    dict(source="Apple App Store US Travel top free chart", family="App rank",
         measures="Airbnb rank in US iOS Travel (3 on 11 Sep 2026)", basis="app",
         nearest_abnb="installs, not nights", frequency="live snapshot", lag_days=0,
         coverage_end="2026-09-11", free="yes",
         hist_to_2023="no", tested="NO: point-in-time only, no history on the page",
         url="https://apps.apple.com/us/charts/iphone/travel-apps/6003"),
    dict(source="US Travel Association Insights Dashboard", family="Composite",
         measures="US travel spend, hotel demand AND an explicit short-term-rental demand series",
         basis="mixed", nearest_abnb="nights (the STR demand line)", frequency="monthly",
         lag_days=33, coverage_end="2026-07-31",
         free="yes but the page 403s to fetchers; verify in a browser",
         hist_to_2023="yes", tested="NO: captured via search index, not pulled",
         url="https://www.ustravel.org/research/travel-recovery-insights-dashboard"),
    dict(source="Census QSS NAICS 721 Accommodation revenue", family="Official revenue",
         measures="US accommodation sector revenue, quarterly", basis="revenue",
         nearest_abnb="US GBV", frequency="quarterly", lag_days=49,
         coverage_end="2026Q2 (released 9 Sep 2026)", free="yes",
         hist_to_2023="yes",
         tested="NO: not pulled; 3Q26 advance lands 19 Nov, after the print",
         url="https://www.census.gov/services/qss/qss-current.pdf"),
    dict(source="Spain INE EOAT tourist-apartment nights and IPAP price index", family="Spain INE",
         measures="tourist-apartment nights and a tourist-apartment PRICE index",
         basis="platform-adjacent nights and price", nearest_abnb="nights AND ADR, Spain",
         frequency="monthly", lag_days=31, coverage_end="2026-07-31", free="yes",
         hist_to_2023="yes",
         tested="PARTLY: G2 tested INE hotel and Frontur tables; EOAT apartments not yet pulled",
         url="https://www.ine.es/dyngs/Prensa/en/EOAT0726.htm"),
    dict(source="Eurostat tour_occ_nim NACE I552 holiday/short-stay nights", family="Eurostat",
         measures="EU27 nights in holiday and other short-stay accommodation",
         basis="nights", nearest_abnb="nights (EU)", frequency="monthly", lag_days=62,
         coverage_end="2026-06-30 (I552)", free="yes", hist_to_2023="yes",
         tested="NO: G2 tested tour_ce_omr only; this is the faster sibling and is the next pull",
         url="https://ec.europa.eu/eurostat/databrowser/view/tour_occ_nim"),
    dict(source="Inside Airbnb August 2026 CDN batch", family="Platform scrape",
         measures="matched-listing review velocity (nights proxy) and late-Aug price quotes",
         basis="listing scrape", nearest_abnb="nights (stayed, not booked) and a noisy ADR quote",
         frequency="roughly twice a year (Jun then Aug)", lag_days=12,
         coverage_end="2026-08-31 (reviews through 30 Aug)", free="yes, CC BY 4.0",
         hist_to_2023="yes but composition breaks it",
         tested="NO and note 08 found n=0 usable year-ago quarters on the fixed 13 cities",
         url="https://data.insideairbnb.com/"),
]

COV = {  # coverage_score, with the reason recorded
    3: "covers Jul, Aug and part of Sep 2026 today",
    2: "Jul and Aug today; Sep arrives before the 5 Nov print",
    1: "Jul 2026 only today",
    0: "does not reach 3Q26",
}


def coverage_score(end: str, freq: str) -> int:
    if not isinstance(end, str) or not end:
        return 0
    e = end[:10]
    if len(e) == 7 and e[4] == "-":      # "2026-07" means the whole month is published
        e = e + "-28"
    if e >= "2026-09-01" or "2026Q3" in e:
        return 3
    if e >= "2026-08-01":
        return 2
    if e >= "2026-07-01":
        return 1 if "quarter" in str(freq).lower() else 2
    return 0


def main():
    raw = pd.read_csv(os.path.join(OUT, "source_inventory_raw.csv"))
    bt = pd.read_csv(os.path.join(OUT, "G_backtests_all.csv"))

    # G_backtests_all.csv carries no family column; derive it the same way G2 did
    def fam_of(f: str) -> str:
        for k, v in [("tsa", "TSA air throughput"), ("cpi", "BLS CPI price"),
                     ("ntto", "NTTO US inbound"), ("es_", "Spain INE"),
                     ("eu_", "Eurostat platform"), ("mar_", "Hotel RevPAR"),
                     ("hlt_", "Hotel RevPAR"), ("bkng_", "OTA room nights"),
                     ("expe_", "OTA room nights")]:
            if str(f).startswith(k):
                return v
        return "other"

    bt["family"] = bt.feature.map(fam_of)
    # best walk-forward ratio per family, on nights, knowable before the print
    bt = bt[bt.wf_n.notna() & (bt.wf_n >= 6)]
    nights = bt[bt.target == "nights_m_yoy_pct"]
    best = (nights.groupby("family")
            .agg(best_wf_ratio_nights=("wf_ratio_vs_naive", "min"),
                 n_tests=("feature", "size"),
                 n_beat_naive=("wf_ratio_vs_naive", lambda s: int((s < 1).sum())))
            .reset_index())
    bestrev = (bt[bt.target == "revenue_musd_yoy_pct"].groupby("family")
               .agg(best_wf_ratio_revenue=("wf_ratio_vs_naive", "min")).reset_index())
    best = best.merge(bestrev, on="family", how="outer")

    fam_map = {"tsa": "TSA air throughput", "bls": "BLS CPI price",
               "ine": "Spain INE", "eurostat": "Eurostat platform",
               "ntto": "NTTO US inbound", "jnto": "Asia arrivals"}

    rows = []
    for _, r in raw.iterrows():
        fam = next((v for k, v in fam_map.items() if str(r.series).startswith(k)), "other")
        rows.append(dict(source=r.series, family=fam, measures=r.measures, basis=r.basis,
                         nearest_abnb=r.nearest_abnb_series, frequency=r.frequency,
                         coverage_end=r.coverage_end, free="yes", hist_to_2023="yes",
                         tested="yes (G2)", url=r.url, lag_days=np.nan,
                         source_kind="machine-pulled series"))
    for m in MANUAL:
        m = dict(m)
        m["source_kind"] = "press release or hand-keyed"
        m["nearest_abnb"] = m.pop("nearest_abnb")
        rows.append(m)

    inv = pd.DataFrame(rows)
    inv = inv.merge(best, on="family", how="left")
    inv["coverage_score"] = [coverage_score(e, f) for e, f in zip(inv.coverage_end, inv.frequency)]
    inv["coverage_note"] = inv.coverage_score.map(COV)

    def bscore(r):
        v = r.best_wf_ratio_nights
        if pd.isna(v):
            return 0
        if v < 0.80:
            return 3
        if v < 0.95:
            return 2
        if v < 1.00:
            return 1
        return 0

    inv["backtest_score"] = inv.apply(bscore, axis=1)
    inv["rank_score"] = inv.coverage_score * inv.backtest_score
    inv["access_date"] = ACCESS
    inv = inv.sort_values(["rank_score", "coverage_score", "backtest_score"],
                          ascending=False).reset_index(drop=True)
    inv.insert(0, "rank", range(1, len(inv) + 1))

    cols = ["rank", "source", "family", "source_kind", "measures", "basis", "nearest_abnb",
            "frequency", "lag_days", "coverage_end", "coverage_score", "coverage_note",
            "best_wf_ratio_nights", "best_wf_ratio_revenue", "n_tests", "n_beat_naive",
            "backtest_score", "rank_score", "free", "hist_to_2023", "tested",
            "url", "access_date"]
    inv = inv[[c for c in cols if c in inv.columns]]
    p = os.path.join(OUT, "source_inventory.csv")
    inv.to_csv(p, index=False)
    print(f"wrote {p} ({len(inv)} sources)")
    show = ["rank", "source", "coverage_score", "best_wf_ratio_nights",
            "backtest_score", "rank_score", "coverage_end"]
    print(inv[show].head(28).to_string(index=False))

    # sanity check on the commentary file
    c = pd.read_csv(os.path.join(OUT, "intra_quarter_commentary.csv"))
    print(f"\ncommentary rows {len(c)}, companies {c.company.nunique()}, "
          f"dates {c.date.min()} to {c.date.max()}")
    print(c.groupby("source_type").size().to_string())
    s = pd.read_csv(os.path.join(OUT, "str_weekly_us_3q26.csv"))
    print(f"\nSTR rows {len(s)}, revpar yoy path: "
          f"{[x for x in s.revpar_yoy_pct.tolist()]}")


if __name__ == "__main__":
    main()
