"""V3: one row per candidate source with the BRIEF verdict, the first failing criterion, the
best walk-forward result and the 3Q26 reading, plus the ranked table for the note.

Workstream V, government data survey, 12 Sep 2026. Krishang Surapaneni (compiled with Claude Code).

Verdict rules (docs/govdata/BRIEF.md), applied in order and stopping at the first failure:
  1 asset class  -> "wrong asset class" only when the series is not a stay or traveller count
  2 coverage     -> "no coverage" unless the series reaches Jul or Aug 2026 today, or Sep 2026 before 5 Nov
  3 history      -> "no history" unless at least 10 quarters from 1Q23 exist (a later start can still corroborate)
  4 access       -> "no access" when the pull was blocked (status recorded in raw/MANIFEST.csv)
  5 test         -> "survivor" beats naive on both windows with wf_n >= 6 on each;
                    "short-window survivor" beats naive on 2023Q1+ only;
                    otherwise "corroboration" (it has, or will have before 5 Nov, a 3Q26 reading we do not hold)
  "duplicate" is used where the series measures the same counts as one already held or pulled here.
Inputs: raw/MANIFEST.csv, V_backtests.csv, V_readings_3q26.csv. Outputs: V_candidates.csv, V_ranked_table.md.
All metadata fields are DESCRIPTIVE (release calendars as observed on 12 Sep 2026); ratios are computed.
"""
from __future__ import annotations

import os

import numpy as np
import pandas as pd

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
OUT = os.path.join(ROOT, "data", "processed", "govdata", "V")

# source key -> metadata. coverage_ok / history_ok / access_ok are the criterion facts.
CANDIDATES = [
    # pulled and tested
    dict(source="statcan_liia", name="StatCan leading indicator of international arrivals (24-10-0056 air by residence, 24-10-0058 vehicles by plate)", region="NA (Canada, US-Canada flows)", asset="border arrivals, daily", freq="daily, summed to months", release_lag="about 10 days (Aug 2026 out 11 Sep)", history="2018-01 (air), 2017-09 (land)", access="free, keyless WDS API", coverage_ok=True, history_ok=True, access_ok=True),
    dict(source="statcan_24100053", name="StatCan international travellers entering or returning to Canada (24-10-0053)", region="NA", asset="border arrivals (overnight split)", freq="monthly", release_lag="about 50 days (Jun 2026 out 20 Aug)", history="1972", access="free, keyless WDS API (full zip is 450 MB)", coverage_ok=False, history_ok=True, access_ok=True, duplicate_of="statcan_liia (same frontier counts, published six weeks earlier)"),
    dict(source="ine_eoap_1998", name="Spain INE EOAP tourist-apartment travellers and overnight stays", region="EMEA (Spain)", asset="tourist-apartment nights (short-term rental class)", freq="monthly", release_lag="about 3 weeks (Jul 2026 out 22 Aug; Sep due about 23 Oct)", history="2009-12", access="free, keyless tempus JSON", coverage_ok=True, history_ok=True, access_ok=True),
    dict(source="eurostat_tour_occ_nim", name="Eurostat tour_occ_nim nights by NACE (I552 holiday and short-stay, I551 hotels), 16 geos", region="EMEA", asset="short-stay accommodation nights (I552) and hotel nights (I551)", freq="monthly", release_lag="about 10 weeks (Jun 2026 today; Jul and Aug due about 27 Oct; Sep after 5 Nov)", history="2015-01 (earlier available)", access="free, keyless JSON API", coverage_ok=False, history_ok=True, access_ok=True),
    dict(source="eurostat_tour_occ_ninat", name="Eurostat tour_occ_ninat nights by residence", region="EMEA", asset="all-accommodation nights by residents / non-residents", freq="annual only (freq dimension A)", release_lag="annual", history="2015", access="free, keyless", coverage_ok=False, history_ok=True, access_ok=True),
    dict(source="eurostat_avia_paoc", name="Eurostat avia_paoc air passengers carried", region="EMEA", asset="air passengers", freq="monthly", release_lag="EU27 aggregate ends 2025-12; country coverage ragged (AT and HR to Jul 2026, ES to Mar 2026)", history="2015-01", access="free, keyless", coverage_ok=False, history_ok=True, access_ok=True),
    dict(source="census_qss", name="US Census Quarterly Services Survey NAICS 721 and 7211 revenue", region="NA (US)", asset="accommodation revenue", freq="quarterly", release_lag="about 70 days (2Q26 out 9 Sep; 3Q26 advance 19 Nov)", history="2013Q1 (2003 for 721 in older vintages)", access="free, keyless zip", coverage_ok=False, history_ok=True, access_ok=True),
    dict(source="jnto_arrivals", name="JNTO visitor arrivals to Japan by market", region="APAC (Japan)", asset="inbound arrivals", freq="monthly", release_lag="about 17 days (Jul 2026 out 19 Aug; Sep due about 15 Oct)", history="2003-01", access="free xlsx on the JNTO site", coverage_ok=True, history_ok=True, access_ok=True),
    dict(source="jta_nights", name="Japan Tourism Agency accommodation survey, total and foreign guest nights", region="APAC (Japan)", asset="all-accommodation guest nights (hotels, ryokan, other lodging)", freq="monthly", release_lag="about 6 weeks preliminary (Jul 2026 out about 29 Aug; Sep due about 31 Oct)", history="2011-01 (methodology break Jan 2026)", access="free xlsx on mlit.go.jp", coverage_ok=True, history_ok=True, access_ok=True),
    dict(source="abs_340101", name="ABS 3401.0 overseas arrivals to Australia (short-term visitors, resident returns)", region="APAC (Australia)", asset="border arrivals", freq="monthly", release_lag="about 6 weeks (Jul 2026 out about 11 Sep; Sep due about 12 Nov)", history="1976-01", access="free xlsx", coverage_ok=True, history_ok=True, access_ok=True),
    dict(source="ntto_country", name="NTTO I-94 arrivals to the US, Canada and Mexico rows", region="NA (Canada and Mexico to US)", asset="I-94 arrivals", freq="monthly", release_lag="Canada and Mexico rows end Jun 2026 (the July preliminary covers overseas only)", history="2000-01", access="free xlsx (same file G pulled)", coverage_ok=False, history_ok=True, access_ok=True),
    dict(source="anac_brazil", name="ANAC Brazil air transport statistics (domestic and international paying passengers)", region="LatAm (Brazil)", asset="air passengers", freq="monthly", release_lag="about 6 weeks (Jul 2026 in the 10-year base on 12 Sep; Sep due late Oct)", history="2016 (10-year base)", access="free 15.7 MB zip", coverage_ok=True, history_ok=True, access_ok=True),
    dict(source="colombia_migracion", name="Migracion Colombia foreign entries (datos.gov.co 96sh-4v8d)", region="LatAm (Colombia)", asset="border arrivals", freq="monthly", release_lag="about 7 weeks (Jun 2026 out 20 Aug; Sep due about 20 Nov)", history="2012-01", access="free Socrata API", coverage_ok=False, history_ok=True, access_ok=True),
    dict(source="ibge_pms_8688", name="IBGE monthly services survey (PMS) volume index, accommodation and food (1.1) and accommodation (1.1.1)", region="LatAm (Brazil)", asset="accommodation and food services volume index (hotel class)", freq="monthly", release_lag="about 6 weeks (Jul 2026 out about 11 Sep; Sep due about 12 Nov)", history="2011-01 (1.1); 2022-01 (1.1.1)", access="free SIDRA API", coverage_ok=True, history_ok=True, access_ok=True),
    dict(source="nz_mbie_adp", name="New Zealand MBIE Accommodation Data Programme guest nights (commercial accommodation)", region="APAC (New Zealand)", asset="commercial accommodation guest nights (hotels, motels, holiday parks, backpackers, lodges; no holiday-home category)", freq="monthly", release_lag="about 4 weeks (Jul 2026 out 26 Aug; Sep due late Oct)", history="2020-06", access="free CSV on teic.mbie.govt.nz (mbie.govt.nz itself is Incapsula-walled)", coverage_ok=True, history_ok=True, access_ok=True),
    dict(source="hawaii_vacation_rental", name="Hawaii DBEDT vacation rental performance (Transparent Intelligence data)", region="NA (Hawaii)", asset="vacation rental unit demand, supply, occupancy, ADR", freq="monthly", release_lag="about 4 weeks (Jul 2026 out late Aug)", history="2024-01 (prior-year columns of the 2025 reports; 2024 report files 404)", access="free xlsx, rate limited (HTTP 429 above about one request per 8 s)", coverage_ok=True, history_ok=False, access_ok=True),
    dict(source="fred_AIRRPMTSID11", name="BTS revenue passenger miles via FRED (domestic and international)", region="NA (US)", asset="air revenue passenger miles", freq="monthly", release_lag="about 3 months", history="2000", access="fredgraph.csv timed out or reset on every attempt on 12 Sep 2026", coverage_ok=False, history_ok=True, access_ok=False),
    # blocked, duplicate or out of class (facts in raw/MANIFEST.csv)
    dict(source="mexico_datatur", name="Mexico SECTUR DATATUR (hotel occupancy, arrivals)", region="LatAm (Mexico)", asset="hotel occupancy and visitor arrivals", freq="monthly", release_lag="unknown (site unreachable)", history="unknown", access="ConnectionError on https and http", coverage_ok=None, history_ok=None, access_ok=False),
    dict(source="mexico_banxico_sie", name="Banxico SIE international visitors", region="LatAm (Mexico)", asset="visitor arrivals", freq="monthly", release_lag="about 7 weeks", history="1980", access="HTTP 400 without a token; free registration required", coverage_ok=None, history_ok=None, access_ok=False),
    dict(source="mexico_upm_boletin", name="Mexico UPM migration bulletin entries", region="LatAm (Mexico)", asset="border entries", freq="monthly", release_lag="unknown", history="unknown", access="ConnectionError", coverage_ok=None, history_ok=None, access_ok=False),
    dict(source="korea_kto_datalab", name="Korea Tourism Organization monthly arrivals", region="APAC (Korea)", asset="inbound arrivals", freq="monthly", release_lag="about 4 weeks", history="long", access="302 to the KNTO index; xlsx behind the datalab login and JS", coverage_ok=None, history_ok=None, access_ok=False),
    dict(source="italy_istat_sdmx", name="ISTAT monthly tourism flows", region="EMEA (Italy)", asset="accommodation nights", freq="monthly", release_lag="about 10 weeks", history="long", access="SDMX endpoint timed out; Italy is in Eurostat tour_occ_nim geo=IT", coverage_ok=None, history_ok=None, access_ok=False, duplicate_of="eurostat_tour_occ_nim geo=IT"),
    dict(source="greece_bank_of_greece", name="Bank of Greece border survey", region="EMEA (Greece)", asset="inbound arrivals and receipts", freq="monthly", release_lag="about 7 weeks", history="long", access="HTTP 403", coverage_ok=None, history_ok=None, access_ok=False),
    dict(source="greece_hcaa", name="Greece HCAA airport statistics", region="EMEA (Greece)", asset="air passengers", freq="monthly", release_lag="about 4 weeks", history="long", access="HTTP 403", coverage_ok=None, history_ok=None, access_ok=False),
    dict(source="croatia_evisitor_htz", name="Croatia eVisitor via HTZ / DZS", region="EMEA (Croatia)", asset="tourist arrivals and nights (all accommodation incl. private)", freq="monthly", release_lag="about 3 weeks", history="2016", access="HTZ pages 404; DZS page has no machine-readable link; Croatia is in Eurostat geo=HR", coverage_ok=None, history_ok=None, access_ok=False, duplicate_of="eurostat_tour_occ_nim geo=HR"),
    dict(source="france_insee_bdm", name="INSEE tourist accommodation occupancy (hotels, other collective accommodation)", region="EMEA (France)", asset="accommodation nights", freq="monthly", release_lag="about 6 weeks", history="long", access="BDM API is keyless but no matching dataflow found; France is in Eurostat geo=FR", coverage_ok=None, history_ok=None, access_ok=False, duplicate_of="eurostat_tour_occ_nim geo=FR"),
    dict(source="portugal_ine_alojamento_local", name="Portugal INE alojamento local nights", region="EMEA (Portugal)", asset="local-lodging (short-term rental class) nights", freq="monthly", release_lag="about 6 weeks", history="long", access="indicator code not resolved (HTTP 500 on guesses); Portugal I552 is in Eurostat geo=PT", coverage_ok=None, history_ok=None, access_ok=False, duplicate_of="eurostat_tour_occ_nim geo=PT I552"),
    dict(source="uk_ons_ott", name="UK ONS overseas travel and tourism", region="EMEA (UK)", asset="inbound visits and nights", freq="annual (monthly discontinued)", release_lag="latest 2023 annual, released 17 May 2024", history="long", access="free", coverage_ok=False, history_ok=None, access_ok=True),
    dict(source="japan_mlit_minpaku", name="Japan MLIT private lodging (minpaku) results", region="APAC (Japan)", asset="private-lodging guest nights (short-term rental class)", freq="bimonthly", release_lag="about 2 months", history="2018", access="PDF only", coverage_ok=None, history_ok=None, access_ok=False),
    dict(source="scotland_stl_licensing", name="Scotland short-term let licensing statistics", region="EMEA (UK)", asset="licence application counts (supply)", freq="quarterly", release_lag="about 3 months", history="2023Q4", access="free", coverage_ok=None, history_ok=None, access_ok=True, wrong_class="licence counts, not stays"),
    dict(source="wales_stl", name="Wales short-term let statistics", region="EMEA (UK)", asset="none published", freq="none", release_lag="none", history="none", access="none", coverage_ok=False, history_ok=None, access_ok=None),
    dict(source="nyc_ose_registry", name="NYC OSE short-term rental registry", region="NA (US)", asset="registered host counts (supply)", freq="ad hoc", release_lag="none", history="2023", access="registration-data page 404", coverage_ok=None, history_ok=None, access_ok=None, wrong_class="registry counts, not stays"),
    dict(source="texas_hot", name="Texas Comptroller local hotel occupancy tax reporting", region="NA (US)", asset="local HOT receipts by municipality", freq="annual", release_lag="annual", history="2018", access="free Socrata", coverage_ok=False, history_ok=None, access_ok=True),
    dict(source="florida_dbpr_vacation_rental", name="Florida DBPR vacation rental licences", region="NA (US)", asset="licence counts (supply)", freq="ad hoc", release_lag="none", history="none", access="not probed", coverage_ok=None, history_ok=None, access_ok=None, wrong_class="licence counts, not stays"),
    dict(source="bts_t100", name="BTS T-100 segment and market (enplanements)", region="NA (US)", asset="air enplanements", freq="monthly", release_lag="about 3 months", history="1990", access="form-gated download; PREZIP 404; FRED mirror timed out", coverage_ok=None, history_ok=None, access_ok=False),
    dict(source="japan_immigration_moj", name="Japan Immigration Services Agency entries", region="APAC (Japan)", asset="inbound entries", freq="monthly", release_lag="about 6 weeks", history="long", access="not pulled", coverage_ok=None, history_ok=None, access_ok=None, duplicate_of="jnto_arrivals (compiled from the same counts)"),
    dict(source="india_mot_fta", name="India Ministry of Tourism foreign tourist arrivals", region="APAC (India)", asset="inbound arrivals", freq="monthly", release_lag="about 6 weeks", history="long", access="PIB press releases, PDF; not probed", coverage_ok=None, history_ok=None, access_ok=False),
    dict(source="statcan_24100045", name="StatCan travel by Canadian residents by destination (24-10-0045)", region="NA (Canada)", asset="resident trips", freq="quarterly", release_lag="cube ends 2025Q4 (released 29 May 2026)", history="2018", access="free", coverage_ok=False, history_ok=None, access_ok=True),
]

# which feature prefixes belong to which source
PREFIX = {
    "statcan_liia": ["ca_liia_"], "statcan_24100053": ["ca_us_", "ca_canadians_", "ca_nonresident_", "ca_other_", "ca_international_"],
    "ine_eoap_1998": ["es_apt_"], "eurostat_tour_occ_nim": ["eurostat_"], "eurostat_avia_paoc": ["avia_"], "census_qss": ["us_qss_"],
    "jnto_arrivals": ["jp_arrivals_"], "jta_nights": ["jp_total_nights", "jp_foreign_nights"], "abs_340101": ["au_"], "ntto_country": ["us_inbound_"],
    "anac_brazil": ["br_air_"], "colombia_migracion": ["co_"], "ibge_pms_8688": ["br_pms_"], "nz_mbie_adp": ["nz_"], "hawaii_vacation_rental": ["hi_vr_"],
    "fred_AIRRPMTSID11": ["us_air_rpm_"],
}


def main():
    bt = pd.read_csv(os.path.join(OUT, "V_backtests.csv"))
    rd = pd.read_csv(os.path.join(OUT, "V_readings_3q26.csv"))
    man = pd.read_csv(os.path.join(OUT, "raw", "MANIFEST.csv"))
    ev = bt[bt.wf_n.fillna(0) >= 6].copy()
    piv = ev.pivot_table(index=["feature", "target"], columns="window", values="wf_ratio_vs_naive").reset_index()
    piv["worse"] = piv[["2022Q1+", "2023Q1+"]].max(axis=1)

    rows = []
    for c in CANDIDATES:
        src = c["source"]
        m = man[man.source == src]
        last = m.last_period.iloc[0] if len(m) and pd.notna(m.last_period.iloc[0]) else ""
        pre = PREFIX.get(src, [])
        sub = piv[piv.feature.map(lambda f: any(f.startswith(p) for p in pre))] if pre else piv.iloc[0:0]
        both = sub[(sub["2022Q1+"] < 1) & (sub["2023Q1+"] < 1)].sort_values("worse")
        short = sub[(sub["2023Q1+"] < 1)].sort_values("2023Q1+")
        best_single = None
        if len(sub):
            k = ev[ev.feature.isin(sub.feature)].sort_values("wf_ratio_vs_naive").iloc[0]
            best_single = k
        # verdict
        if c.get("wrong_class"):
            verdict, crit = "wrong asset class", f"1 asset class: {c['wrong_class']}"
        elif c.get("duplicate_of"):
            verdict, crit = "duplicate", f"duplicate of {c['duplicate_of']}"
        elif c.get("coverage_ok") is False:
            verdict, crit = "no coverage", f"2 coverage: {c['release_lag']}"
        elif c.get("access_ok") is False:
            verdict, crit = "no access", f"4 access: {c['access']}"
        elif c.get("history_ok") is False:
            verdict, crit = "corroboration", f"3 history: starts {c['history']} (fewer than 10 quarters from 1Q23); kept as corroboration"
        elif len(both):
            verdict, crit = "survivor", "5 test: beats naive on both windows"
        elif len(short):
            verdict, crit = "short-window survivor", "5 test: beats naive on 2023Q1+ only"
        elif len(sub):
            verdict, crit = "corroboration", "5 test: does not beat naive on either window"
        else:
            verdict, crit = "corroboration", "5 test: not testable (no scored quarters)"
        bf = both.iloc[0] if len(both) else (short.iloc[0] if len(short) else None)
        row = dict(source=src, name=c["name"], country_or_region=c["region"], asset_class=c["asset"], frequency=c["freq"], last_period=last,
                   release_lag=c["release_lag"], history_start=c["history"], access=c["access"], verdict=verdict, first_failing_criterion=crit)
        if bf is not None:
            k = ev[(ev.feature == bf.feature) & (ev.target == bf.target)]
            k23 = k[k.window == "2023Q1+"].iloc[0] if (k.window == "2023Q1+").any() else k.iloc[0]
            row.update(best_feature=bf.feature, target=bf.target, ratio_2022Q1=bf["2022Q1+"], ratio_2023Q1=bf["2023Q1+"],
                       best_wf_ratio=min(bf["2022Q1+"], bf["2023Q1+"]) if pd.notna(bf["2022Q1+"]) else bf["2023Q1+"],
                       best_window="2022Q1+" if pd.notna(bf["2022Q1+"]) and bf["2022Q1+"] <= bf["2023Q1+"] else "2023Q1+",
                       wf_n_2023=k23.wf_n, perm_p_2023=k23.perm_p, r_2023=k23.r, jk_ratio_max_2023=k23.jk_ratio_max, jk_n_below_1_2023=k23.jk_n_below_1,
                       knowable_before_print=k23.knowable_before_print)
        elif best_single is not None:
            row.update(best_feature=best_single.feature, target=best_single.target, best_wf_ratio=best_single.wf_ratio_vs_naive, best_window=best_single.window,
                       ratio_2022Q1=np.nan, ratio_2023Q1=np.nan, wf_n_2023=best_single.wf_n, perm_p_2023=best_single.perm_p, r_2023=best_single.r,
                       jk_ratio_max_2023=best_single.jk_ratio_max, jk_n_below_1_2023=best_single.jk_n_below_1, knowable_before_print=best_single.knowable_before_print)
        # 3Q26 reading: the observable vintage (m2 preferred, then m1) of the best feature's base, else any m1 of the source
        rr = rd[rd.feature.map(lambda f: any(f.startswith(p) for p in pre)) & rd.feature.str.endswith(("_m1", "_m2"))] if pre else rd.iloc[0:0]
        if len(rr):
            base = row.get("best_feature", "").rsplit("_", 1)[0]
            pick = rr[rr.feature.str.startswith(base + "_m")] if base else rr.iloc[0:0]
            if pick.empty:
                pick = rr
            pick = pick.sort_values("feature", key=lambda s: s.str.endswith("_m2"), ascending=False).iloc[0]
            row.update(reading_3q26_feature=pick.feature, reading_3q26_value_yoy=pick.value_3q26, reading_2q26_value_yoy=pick.value_2q26,
                       reading_delta_pp=pick.delta_pp, reading_insample_pred_total_nights=rd[(rd.feature == pick.feature) & (rd.target == "total_nights_yoy")].insample_pred_3q26.iloc[0] if ((rd.feature == pick.feature) & (rd.target == "total_nights_yoy")).any() else np.nan)
        rows.append(row)
    cand = pd.DataFrame(rows)
    cand["robust"] = (cand.get("jk_ratio_max_2023") < 1) & (cand.get("perm_p_2023") < 0.05) & cand.verdict.isin(["survivor", "short-window survivor"])
    order = {"survivor": 0, "short-window survivor": 1, "corroboration": 2, "duplicate": 3, "no coverage": 4, "no history": 5, "no access": 6, "wrong asset class": 7}
    cand["rank_key"] = cand.verdict.map(order)
    cand = cand.sort_values(["rank_key", "best_wf_ratio"], na_position="last").drop(columns="rank_key").reset_index(drop=True)
    cand.insert(0, "rank", range(1, len(cand) + 1))
    cand.to_csv(os.path.join(OUT, "V_candidates.csv"), index=False)

    # markdown table for the note
    lines = ["| Rank | Source | Region | Asset class | Last period | Verdict | First failing criterion | Best feature | Ratio 22Q1+ / 23Q1+ | Robust | Target | 3Q26 reading (y/y) |", "|---|---|---|---|---|---|---|---|---|---|---|---|"]
    for _, r in cand.iterrows():
        rat = "" if pd.isna(r.get("best_wf_ratio")) else (f"{r.ratio_2022Q1:.2f} / {r.ratio_2023Q1:.2f}" if pd.notna(r.get("ratio_2022Q1")) else f"{r.best_wf_ratio:.2f} ({r.best_window})")
        rdg = "" if pd.isna(r.get("reading_3q26_value_yoy")) else f"{r.reading_3q26_value_yoy:+.1f}% ({r.reading_3q26_feature}, 2Q26 {r.reading_2q26_value_yoy:+.1f}%)"
        lines.append(f"| {r['rank']} | {r['name']} | {r.country_or_region} | {r.asset_class} | {r.last_period} | **{r.verdict}** | {r.first_failing_criterion} | {r.get('best_feature', '') if pd.notna(r.get('best_feature')) else ''} | {rat} | {'yes' if r.robust else ('no' if pd.notna(r.get('best_wf_ratio')) else '')} | {r.get('target', '') if pd.notna(r.get('target')) else ''} | {rdg} |")
    with open(os.path.join(OUT, "V_ranked_table.md"), "w", encoding="utf-8") as f:
        f.write("\n".join(lines))
    print(cand[["rank", "source", "verdict", "best_feature", "ratio_2022Q1", "ratio_2023Q1", "robust", "target", "reading_3q26_value_yoy"]].to_string(index=False))


if __name__ == "__main__":
    main()
