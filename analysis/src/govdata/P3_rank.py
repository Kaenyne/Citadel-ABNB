"""
WS-P step 3: one row per candidate source with the BRIEF verdict, the first failing criterion,
the best walk-forward ratio, and the 3Q26 reading. Verdict order follows docs/govdata/BRIEF.md:
asset class, coverage, history, access, test. A candidate is a source-level object (one official
series family); the best test across its features is reported and the feature named.

Verdict rules (BRIEF vocabulary)
  survivor              some (feature, transform, lag, target) beats naive on BOTH windows, wf_n >= 6
  short-window survivor beats naive on 2023Q1+ only (the residual target only has the short window)
  corroboration         has a 3Q26 reading we do not already hold; does not beat naive or cannot be tested
  duplicate             measures the same thing as a series already held (named)
  no coverage / no history / no access / wrong asset class  eliminated on the stated fact

Run: py -3.13 analysis/src/govdata/P3_rank.py
"""
from __future__ import annotations

import os

import numpy as np
import pandas as pd

HERE = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
OUT = os.path.join(HERE, "data", "processed", "govdata", "P")
tests = pd.read_csv(os.path.join(OUT, "P_backtests.csv"))
readings = pd.read_csv(os.path.join(OUT, "P_readings_3q26.csv"))
meta = pd.read_csv(os.path.join(OUT, "P_feature_meta.csv"))
man = pd.read_csv(os.path.join(OUT, "raw", "MANIFEST.csv"))

# candidate -> feature prefix(es) it owns, plus hand-coded metadata (sourced from the release pages, see note)
CANDS = [
    # id, name, country/region, asset class rank (1 STR, 2 other/platform, 3 hotel, 4 arrivals/other), frequency, release lag, history start, access, feature prefixes, duplicate_of, notes
    dict(id="hawaii_vr_adr", name="Hawaii DBEDT vacation rental performance report (Transparent, then Lighthouse data): unit ADR", region="US-HI (NA)", asset="short-term rental", rank=1, freq="monthly", lag="about 25 days (July 2026 report dated 21 Aug 2026)", hist="reports from 2019-09; pulled 2023-06 to 2026-07 (2019-09 to 2023-05 blocked by HTTP 429 today)", access="free, pdf and xlsx on files.hawaii.gov; Cloudflare 429 after about 70 fetches", pref=["hawaii_vr_adr_"], dup="",
         verdict="corroboration", fail="history: two comparison-basis breaks inside the held window (the Aug 2025 vintage restates the 2024 base about 45 percent higher when the data provider changed; the May 2026 vintage reverts the 2025 base about 25 percent lower), so the within-vintage y/y flips sign on basis, not price; the 2023-06 to 2026-07 series cannot be tested as one history (best ratio 1.08 on 8 to 9 scored quarters is reported for the record)"),
    dict(id="ine_hdpi", name="INE Spain holiday dwellings price index (IPAP/HDPI), tourist apartments", region="ES (EMEA)", asset="short-term rental (tourist apartments)", rank=1, freq="monthly", lag="about 23 days", hist="2015-01 or earlier (150 months pulled)", access="free JSON API", pref=["ine_hdpi_holiday_dwellings_EOT8077"], dup=""),
    dict(id="hicp_cp11209", name="Eurostat HICP CP11209 other accommodation services (ECOICOP v2 5-digit), by country", region="EU, EA and 20 countries (EMEA)", asset="other accommodation incl short-term lets", rank=2, freq="monthly", lag="flash ~1 day after month end (aggregates), final ~17 days", hist="2015-01 or later by country (v2 series from 2020 for some)", access="free JSON API", pref=["hicp_CP11209_"], dup=""),
    dict(id="hicp_cp11202", name="Eurostat HICP CP11202 holiday centres, camping sites, hostels, by country", region="EU, EA and countries (EMEA)", asset="other accommodation", rank=2, freq="monthly", lag="~17 days", hist="2015-01 or later", access="free JSON API", pref=["hicp_CP11202_"], dup=""),
    dict(id="hicp_cp112_countries", name="Eurostat HICP CP112 accommodation services, by country (EA aggregate already held)", region="EU27, 20 countries (EMEA)", asset="accommodation, all", rank=2, freq="monthly", lag="~17 days", hist="2015-01", access="free JSON API", pref=["hicp_CP112_"], dup="EA aggregate held in data/raw/external_prices (J2 hicp_ea_accommodation); country series new"),
    dict(id="hicp_cp11201", name="Eurostat HICP CP11201 hotels, motels, inns, by country", region="EU, EA and countries (EMEA)", asset="hotel", rank=3, freq="monthly", lag="~17 days", hist="2015-01 or later", access="free JSON API", pref=["hicp_CP11201_"], dup=""),
    dict(id="ons_cpi_11203", name="UK ONS CPI 11.2.0.3 accommodation services of other establishments", region="UK (EMEA)", asset="other accommodation", rank=2, freq="monthly", lag="~20 days", hist="2015-01", access="free JSON API", pref=["ons_cpi_11203_other_establishments_index"], dup=""),
    dict(id="ons_cpi_112", name="UK ONS CPI 11.2 accommodation services and 11.2.0.1 hotels", region="UK (EMEA)", asset="accommodation, all / hotel", rank=3, freq="monthly", lag="~20 days", hist="1996-01 (11.2), 2015-01 (hotels)", access="free JSON API", pref=["ons_cpi_112_accommodation_index", "ons_cpi_11201_hotels_index"], dup=""),
    dict(id="ine_rtapi", name="INE Spain rural tourism accommodation price index", region="ES (EMEA)", asset="other accommodation (rural houses)", rank=2, freq="monthly", lag="~23 days", hist="2015 or earlier", access="free JSON API", pref=["ine_rtapi_rural_EOT12767"], dup=""),
    dict(id="ine_tcpi", name="INE Spain tourist campsite price index", region="ES (EMEA)", asset="other accommodation (campsites)", rank=2, freq="monthly", lag="~23 days", hist="2015 or earlier", access="free JSON API", pref=["ine_tcpi_campsite_"], dup=""),
    dict(id="ine_hotel_adr", name="INE Spain hotel ADR and RevPAR (IRSH), national", region="ES (EMEA)", asset="hotel", rank=3, freq="monthly", lag="~23 days", hist="2015 or earlier", access="free JSON API", pref=["ine_hotel_adr_EOT16415", "ine_hotel_revpar_"], dup="INE hotel price index (IPH) already held (J2 ine_iph_spain); ADR is a realised rate, not a price index"),
    dict(id="eurostat_sppi_i55", name="Eurostat services producer price index, NACE I55 accommodation, by country", region="EU, EA and countries (EMEA)", asset="accommodation (producer price)", rank=2, freq="quarterly", lag="~75 days; 3Q26 publishes in December", hist="2015-Q1 or later by country", access="free JSON API", pref=["sppi_I55_"], dup="",
         verdict="no coverage", fail="coverage: 3Q26 value publishes in December 2026, after the 5 Nov print (2Q26 is the last today); recorded because Portugal I55 beats naive on both windows against EMEA ex-FX (0.68 and 0.78, 9 scored quarters), a backtest-only finding"),
    dict(id="abs_cpi_holiday", name="ABS CPI holiday travel and accommodation (domestic, international, total), quarterly and monthly", region="AU (APAC)", asset="holiday travel and accommodation (bundles airfares and accommodation)", rank=2, freq="quarterly (and monthly from 2022-09)", lag="~28 days", hist="quarterly long history; monthly 2022-09", access="free SDMX API", pref=["abs_cpi_"], dup=""),
    dict(id="nz_cpi_accommodation", name="Stats NZ CPI accommodation services and domestic accommodation services", region="NZ (APAC)", asset="accommodation services (CPI)", rank=2, freq="quarterly", lag="~20 days", hist="1999 or earlier", access="free csv on stats.govt.nz", pref=["nz_cpi_"], dup=""),
    dict(id="japan_cpi_hotel", name="Japan CPI hotel charges (宿泊料), 2025 base", region="JP (APAC)", asset="hotel (CPI hotel charges)", rank=3, freq="monthly", lag="~20 days (national)", hist="1970-01", access="free xlsx on e-Stat, keyless", pref=["japan_cpi_hotel_charges_index"], dup=""),
    dict(id="bls_ppi_hotels", name="BLS PPI hotels and motels (721110) and traveler accommodation (7211)", region="US (NA)", asset="hotel (producer price)", rank=3, freq="monthly", lag="~14 days", hist="2012 or earlier", access="free JSON API (keyless, 25 queries/day)", pref=["bls_PCU"], dup=""),
    dict(id="bls_cpi_sehb02", name="BLS CPI other lodging away from home incl hotels and motels (SEHB02, NSA and SA)", region="US (NA)", asset="hotel (CPI)", rank=3, freq="monthly", lag="~13 days", hist="2012 or earlier", access="free JSON API", pref=["bls_CUUR0000SEHB02", "bls_CUSR0000SEHB02"], dup="CPI SEHB lodging away from home and SS62031 held (G, J2); SEHB02 is the same stratum family"),
    dict(id="statcan_cpi_trav_acc", name="StatCan CPI traveller accommodation, Canada", region="CA (NA)", asset="hotel (CPI traveller accommodation)", rank=3, freq="monthly", lag="~20 days", hist="2012 or earlier", access="free WDS API", pref=["statcan_cpi_traveller_accommodation"], dup=""),
    dict(id="ibge_ipca_hosped", name="IBGE IPCA hospedagem (hotel), Brazil", region="BR (LatAm)", asset="hotel (CPI)", rank=3, freq="monthly", lag="~10 days", hist="2012-01", access="free SIDRA API", pref=["ibge_ipca_hospedagem_yoy12m"], dup=""),
    dict(id="bea_travel_xm_price", name="BEA NIPA price indexes, exports and imports of travel (via FRED)", region="US (NA)", asset="travel deflators (inbound and outbound spend)", rank=4, freq="quarterly", lag="~30 days (advance)", hist="1967", access="free FRED csv", pref=["bea_export_travel_price", "bea_import_travel_price"], dup=""),
    dict(id="bea_pce_accom_travel", name="BEA PCE price indexes: accommodations, foreign travel by US residents, inbound foreign travel (held, untested)", region="US (NA)", asset="accommodation, all / travel deflators", rank=2, freq="monthly", lag="~30 days", hist="2015-01", access="held under data/raw/bea", pref=["bea_pce_"], dup="hotels and motels PCE price already tested (J2 bea_hotels_price); accommodations and travel lines new"),
    # record-only
    dict(id="portugal_ine_adr", name="INE Portugal monthly ADR and RevPAR, tourist accommodation (incl local accommodation)", region="PT (EMEA)", asset="accommodation, all (hotels plus local accommodation with 10+ beds)", rank=2, freq="monthly", lag="~30 days", hist="2016", access="API keyed by indicator id not discoverable; monthly flash PDF only", pref=[], dup="", verdict="corroboration", fail="access: json_indicador API needs a varcd the public catalogue does not list, so no history to test; the July 2026 flash (published late Aug) gives national ADR EUR 154.9, +3.2% y/y, RevPAR +1.8%, nights +2.1% (sourced via press coverage of the INE release)", reading=3.2, reading_note="Jul 2026 national ADR y/y, INE flash via press"),
    dict(id="statcan_taspi", name="StatCan traveller accommodation services price index (TASPI)", region="CA (NA)", asset="hotel (producer price)", rank=3, freq="quarterly", lag="n/a", hist="2001", access="free WDS API", pref=[], dup="", verdict="no coverage", fail="coverage: cube end date 2019-10-01, no longer updated"),
    dict(id="mexico_inpc_hotel", name="INEGI INPC hoteles (Mexico CPI hotel component)", region="MX (LatAm)", asset="hotel (CPI)", rank=3, freq="monthly", lag="~9 days", hist="long", access="INEGI and Banxico APIs both require a free registration token (400 without token)", pref=[], dup="", verdict="no access", fail="access: token required, not held; registration is free so this is recoverable"),
    dict(id="lvcva_adr", name="LVCVA Las Vegas monthly hotel ADR", region="US-NV (NA)", asset="hotel", rank=3, freq="monthly", lag="~30 days", hist="long", access="site returns 403 to fetchers", pref=[], dup="", verdict="no access", fail="access: lvcva.com 403 (Cloudflare); hotel class anyway"),
    dict(id="singapore_stb_arr", name="Singapore STB monthly hotel average room rate", region="SG (APAC)", asset="hotel", rank=3, freq="monthly", lag="~30 days", hist="long", access="Tableau dashboard; page moved (404); not on data.gov.sg", pref=[], dup="", verdict="no access", fail="access: no machine-readable endpoint found"),
    dict(id="hongkong_hktb_arr", name="Hong Kong Tourism Board hotel achieved room rate", region="HK (APAC)", asset="hotel", rank=3, freq="monthly", lag="~30 days", hist="long", access="PartnerNet login", pref=[], dup="", verdict="no access", fail="access: login wall"),
    dict(id="nz_mbie_adp", name="NZ MBIE Accommodation Data Programme", region="NZ (APAC)", asset="volume (guest nights, occupancy, capacity)", rank=4, freq="monthly", lag="~40 days", hist="2019", access="free", pref=[], dup="", verdict="wrong asset class", fail="asset class: no price or rate measure published (guest nights, occupancy, capacity only)"),
    dict(id="croatia_evisitor", name="Croatia eVisitor arrivals and nights", region="HR (EMEA)", asset="volume", rank=4, freq="daily/monthly", lag="days", hist="2016", access="free", pref=[], dup="", verdict="wrong asset class", fail="asset class: arrivals and nights, no price (volume workstream V)"),
    dict(id="japan_mlit_minpaku", name="Japan MLIT minpaku notification-system reports", region="JP (APAC)", asset="volume", rank=4, freq="bimonthly", lag="~60 days", hist="2018", access="free PDF", pref=[], dup="", verdict="wrong asset class", fail="asset class: nights and guests only, no price"),
    dict(id="ons_stl_pilot", name="UK ONS short-term lets (platform data) pilot", region="UK (EMEA)", asset="volume", rank=4, freq="monthly", lag="~90 days", hist="2023", access="free xlsx", pref=[], dup="", verdict="wrong asset class", fail="asset class: nights and guests, no price (volume workstream V)"),
    dict(id="lodging_tax_us", name="US state and city lodging-tax collections (Florida DOR TDT, Texas HOT, NYC hotel tax, Colorado, Vermont M&R incl STR line)", region="US (NA)", asset="tax base, dollars", rank=4, freq="monthly/quarterly", lag="30-90 days", hist="long", access="free pages, several moved (404s recorded)", pref=[], dup="", verdict="wrong asset class", fail="asset class: dollars without nights, so no price can be formed; a GBV-type proxy at best"),
    dict(id="tourist_tax_eu", name="Italy imposta di soggiorno and France taxe de sejour collections", region="IT, FR (EMEA)", asset="tax base, dollars", rank=4, freq="annual", lag="12+ months", hist="long", access="free", pref=[], dup="", verdict="wrong asset class", fail="asset class: dollars without nights; annual as well"),
    dict(id="us_census_qss_721", name="US Census QSS NAICS 721 accommodation revenue", region="US (NA)", asset="revenue", rank=4, freq="quarterly", lag="~80 days; 3Q26 advance 19 Nov", hist="2009", access="free", pref=[], dup="", verdict="wrong asset class", fail="asset class: revenue, not price; and 3Q26 publishes after the print"),
    dict(id="bls_ipp_air_fares", name="BLS import and export air passenger fare indexes", region="US (NA)", asset="airfares", rank=4, freq="monthly", lag="~14 days", hist="2001", access="free but series ids not identified within budget", pref=[], dup="", verdict="wrong asset class", fail="asset class: airfares, not accommodation"),
]

BEST_COLS = ["feature", "transform", "lag", "target", "window", "wf_n", "wf_ratio_vs_naive", "wf_ratio_vs_ar1", "pearson_r", "perm_p", "p_bonferroni", "jk_ratio_min", "jk_ratio_max", "beats_both_windows", "beats_short", "beats_long", "has_long"]
rows = []
for c in CANDS:
    feats = [f for f in meta.feature if any(f.startswith(p) for p in c["pref"])] if c["pref"] else []
    t = tests[tests.feature.isin(feats) & (tests.wf_n >= 6)] if feats else tests.iloc[0:0]
    rd = readings[readings.feature.isin(feats)] if feats else readings.iloc[0:0]
    mt = meta[meta.feature.isin(feats)]
    last = mt.last_period.dropna().astype(str).max() if len(mt) and mt.last_period.notna().any() else ""
    histq = int(mt.hist_quarters_from_1q23.max()) if len(mt) and mt.hist_quarters_from_1q23.notna().any() else 0
    best = t.sort_values("wf_ratio_vs_naive").head(1)
    row = dict(candidate=c["id"], source=c["name"], country_or_region=c["region"], asset_class=c["asset"], asset_rank=c["rank"], frequency=c["freq"],
               last_period=last, release_lag=c["lag"], history_start=c["hist"], access=c["access"], n_features=len(feats), n_tests=int(len(t)),
               duplicate_of=c["dup"])
    # readings
    rd3 = rd[rd.reading_3q26_yoy_pct.notna()]
    if len(rd3):
        pref_order = rd3.feature.str.contains("state|_EA_|EU27|EOT8077|30033|CPIQ.SE9096_|CUUR0000SEHB02|721110|_112_acc").astype(int)
        r0 = rd3.assign(_p=pref_order.values).sort_values(["_p", "feature"], ascending=[False, True]).iloc[0]
        row["reading_3q26_yoy_pct"] = round(float(r0.reading_3q26_yoy_pct), 2)
        row["reading_feature"] = r0.feature
        row["reading_months_in"] = r0.months_in
        row["reading_2q26"] = round(float(r0.last_2q26_full_quarter), 2) if np.isfinite(r0.last_2q26_full_quarter) else np.nan
    elif "reading" in c:
        row["reading_3q26_yoy_pct"] = c["reading"]; row["reading_feature"] = "hand-keyed"; row["reading_months_in"] = c["reading_note"]; row["reading_2q26"] = np.nan
    else:
        row["reading_3q26_yoy_pct"] = np.nan; row["reading_feature"] = ""; row["reading_months_in"] = ""; row["reading_2q26"] = np.nan
    # verdict
    if "verdict" in c:
        row["verdict"], row["first_failing_criterion"] = c["verdict"], c["fail"]
        if len(t):
            both = t[t.beats_both_windows]
            best = (both if len(both) else t).sort_values("wf_ratio_vs_naive").head(1)
    elif not feats:
        row["verdict"], row["first_failing_criterion"] = "no access", "access: pull returned no series (see MANIFEST)"
    else:
        reaches = str(last) >= "2026-07"
        if not reaches and not (c["freq"].startswith("quarterly") and str(last) >= "2026-Q2"):
            row["verdict"], row["first_failing_criterion"] = "no coverage", f"coverage: last period {last}"
        elif histq < 10:
            row["verdict"], row["first_failing_criterion"] = ("corroboration" if len(rd3) else "no history"), f"history: {histq} quarters from 1Q23 (need 10); kept as corroboration" if len(rd3) else f"history: {histq} quarters from 1Q23"
        elif len(t) == 0:
            row["verdict"], row["first_failing_criterion"] = "corroboration", "test: no walk-forward with 6 scored quarters"
        else:
            both = t[t.beats_both_windows]
            short_only = t[(t.window == "2023Q1+") & t.beats_naive & ~t.beats_both_windows]
            if len(both):
                row["verdict"] = "survivor"; best = both.sort_values("wf_ratio_vs_naive").head(1); row["first_failing_criterion"] = "none (beats naive on both windows)"
            elif len(short_only):
                row["verdict"] = "short-window survivor"; best = short_only.sort_values("wf_ratio_vs_naive").head(1); row["first_failing_criterion"] = "test: beats naive on 2023Q1+ only"
            else:
                row["verdict"] = "corroboration" if len(rd3) else "no reading"
                row["first_failing_criterion"] = f"test: best walk-forward ratio vs naive {float(best.wf_ratio_vs_naive.iloc[0]):.2f} (does not beat naive)" if len(best) else "test: no evaluable walk-forward"
            if c["dup"] and row["verdict"] in ("corroboration", "no reading"):
                pass
    if len(best):
        b = best.iloc[0]
        for k in BEST_COLS:
            row[f"best_{k}"] = b[k]
        row["best_sign"] = "positive" if b["pearson_r"] > 0 else "negative (wrong sign for a price proxy)"
        # residual-specific best, and regional best, for the note
        tr = t[t.target == "residual_pricing_pp"].sort_values("wf_ratio_vs_naive").head(1)
        row["best_residual_ratio"] = float(tr.wf_ratio_vs_naive.iloc[0]) if len(tr) else np.nan
        row["best_residual_feature"] = tr.feature.iloc[0] if len(tr) else ""
        te = t[t.target == "adr_exfx_yoy_pp"].sort_values("wf_ratio_vs_naive").head(1)
        row["best_exfx_ratio"] = float(te.wf_ratio_vs_naive.iloc[0]) if len(te) else np.nan
        row["best_exfx_window"] = te.window.iloc[0] if len(te) else ""
        tg = t[t.target.str.startswith("adr_exfx_") & ~t.target.eq("adr_exfx_yoy_pp")].sort_values("wf_ratio_vs_naive").head(1)
        row["best_regional_ratio"] = float(tg.wf_ratio_vs_naive.iloc[0]) if len(tg) else np.nan
        row["best_regional_target"] = tg.target.iloc[0] if len(tg) else ""
        row["best_regional_window"] = tg.window.iloc[0] if len(tg) else ""
        row["best_regional_both_windows"] = bool(tg.beats_both_windows.iloc[0]) if len(tg) else False
    rows.append(row)
cand = pd.DataFrame(rows)
order = {"survivor": 0, "short-window survivor": 1, "corroboration": 2, "duplicate": 3, "no reading": 4, "no history": 5, "no coverage": 6, "no access": 7, "wrong asset class": 8}
cand["verdict_rank"] = cand.verdict.map(order)
cand = cand.sort_values(["verdict_rank", "asset_rank", "best_wf_ratio_vs_naive"], na_position="last").drop(columns="verdict_rank")
cand.to_csv(os.path.join(OUT, "P_candidates.csv"), index=False)
pd.set_option("display.width", 250)
print(cand[["candidate", "verdict", "asset_class", "last_period", "best_wf_ratio_vs_naive", "best_window", "best_target", "best_feature", "reading_3q26_yoy_pct", "first_failing_criterion"]].round(3).to_string())
