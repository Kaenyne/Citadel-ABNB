"""adr_engine / od_layer.py — ADR upgrade 2: origin -> destination-region allocation, measured where the
tourism-board files allow it, and the destination tilt it implies for the four-region geo-mix term.

The v1 geo-mix term (adr_v1_design.md 3.3 / 3.3b, exfx.geo_mix_pp) splits the nights line's ex-NA growth
across EMEA / LatAm / APAC with EXNA_PATTERN = 8 / 20 / 18, the 2Q26 letter bucket midpoints. That pattern
is a judgement. Management's origin statements (India +60%, Brazil +31%, Japan high-teens, Mexico
double-digit, 2Q26) are filed, but they are ORIGIN statements and the ADR lever is a DESTINATION lever, so
they only bite through an origin -> destination allocation. This module measures that allocation as far as
the cached agency payloads under data/processed/govdata/V/raw/ allow, states every cell that they cannot
identify, and prices the resulting tilt with the same arithmetic the line already uses.

Run:  cd ~/Citadel-ABNB && PYTHONPATH=analysis/src python3 -W ignore -m pitch_model_v2.adr_engine.od_layer

Writes data/processed/pitch_model_v2/adr_engine/od_*.csv.  Nothing here is fitted.
"""
from __future__ import annotations

import numpy as np
import pandas as pd

from . import config as C
from . import exfx

RAW = C.ROOT / "data/processed/govdata/V/raw"
PANEL = C.ROOT / "data/processed/overnight/10_regional_panel_quarterly.csv"
QUOTES = C.ROOT / "data/processed/overnight/10_regional_quotes.csv"
WIDE = C.ROOT / "data/processed/adr/04_regional_quarterly_wide.csv"
RGF = C.OUT / "regional_growth_forward.csv"
TILT = C.OUT / "geo_mix_tilt_sensitivity.csv"

EXNA = ["emea", "latam", "apac"]
BASE_Q = "2Q26"                       # the quarter the letter buckets 8 / 20 / 18 describe


# =====================================================================================================
# 1. the cached agency payloads, aggregated to quarters
# =====================================================================================================
def _qagg(df: pd.DataFrame, key: str, val: str) -> pd.DataFrame:
    d = df.copy()
    d["q"] = pd.PeriodIndex(d.period, freq="M").asfreq("Q")
    t = d.pivot_table(index="q", columns=key, values=val, aggfunc="sum")
    n = d.groupby([key, "q"]).period.count().unstack(0)
    return t[n.max(axis=1) == 3]                       # complete quarters only


def sources() -> dict:
    """Every origin-resolved or denominator-bearing series this layer can use, quarterly."""
    s = {}
    s["ntto"] = _qagg(pd.read_csv(RAW / "ntto_arrivals_by_country_monthly.csv"), "country", "arrivals")
    s["jnto"] = _qagg(pd.read_csv(RAW / "jnto_arrivals_monthly.csv"), "market", "arrivals")
    s["abs"] = _qagg(pd.read_csv(RAW / "abs_340101_arrivals_monthly.csv"), "series", "value")
    s["statcan"] = _qagg(pd.read_csv(RAW / "statcan_24100053_monthly.csv"), "series", "value")
    s["anac"] = _qagg(pd.read_csv(RAW / "anac_brazil_passengers_monthly.csv"), "nature", "paying_passengers")
    s["jta"] = _qagg(pd.read_csv(RAW / "jta_accommodation_nights_monthly.csv"), "series", "value")
    ine = pd.read_csv(RAW / "ine_eoap_1998_monthly.csv")
    ine["name"] = ine.name.str.strip()
    s["ine"] = _qagg(ine, "name", "value")
    s["colombia"] = _qagg(pd.read_csv(RAW / "colombia_foreign_entries_monthly.csv").assign(k="co"), "k", "foreign_entries")
    e = pd.read_csv(RAW / "eurostat_tour_occ_ninat_annual.csv")
    s["eurostat_ninat"] = e[e.geo == "EU27_2020"].pivot(index="period", columns="c_resid", values="value")
    return s


def measured_cells() -> pd.DataFrame:
    """Every origin x destination cell that a cached payload actually observes: level at 2Q26, y/y, and the
    denominator (origin total travel) where one exists. This is the evidence the allocation is built on."""
    s = sources()
    bq = pd.Period("2026Q2", freq="Q")
    rows = []

    def add(origin, dest, proxy, series, src, denom=None, denom_src=None, note=""):
        lvl = float(series.loc[bq]) if bq in series.index else np.nan
        yoy = float(series.loc[bq] / series.loc[bq - 4] - 1) * 100 if (bq in series.index and bq - 4 in series.index) else np.nan
        d = float(denom.loc[bq]) if (denom is not None and bq in denom.index) else np.nan
        rows.append({"origin": origin, "dest_region": dest, "destination_proxy": proxy,
                     "level_2Q26": lvl, "yoy_2Q26_pct": yoy, "origin_denominator_2Q26": d,
                     "share_of_denominator_pct": (lvl / d * 100) if (d == d and d) else np.nan,
                     "source_file": src, "denominator_source": denom_src or "", "note": note})

    ntto, jnto, abs_, sc, anac, jta = s["ntto"], s["jnto"], s["abs"], s["statcan"], s["anac"], s["jta"]
    au_out = abs_["st_residents_returning"]
    ca_out = sc["canadians_returning_from_us_total"] + sc["canadians_returning_from_other_total"]
    br_trips = anac["DOMÉSTICA"] / 2 + anac["INTERNACIONAL"] / 2 * 0.60       # 0.60 = resident share, ASSUMED

    N = "ntto_arrivals_by_country_monthly.csv (NTTO I-94, arrivals to the US)"
    J = "jnto_arrivals_monthly.csv (JNTO, arrivals to Japan)"
    for o, col in [("India", "INDIA"), ("Brazil", "BRAZIL"), ("China", "CHINA"), ("UK", "UNITED KINGDOM"),
                   ("Germany", "GERMANY"), ("Japan", "JAPAN"), ("Mexico", "MEXICO"), ("Australia", "AUSTRALIA"),
                   ("Canada", "CANADA"), ("France", "FRANCE")]:
        den, dsrc = (None, None)
        if o == "Australia": den, dsrc = au_out, "abs_340101_arrivals_monthly.csv st_residents_returning"
        if o == "Canada": den, dsrc = ca_out, "statcan_24100053_monthly.csv canadians_returning_from_us+other"
        if o == "Brazil": den, dsrc = br_trips, "anac_brazil_passengers_monthly.csv (pax/2; resident share 0.60 ASSUMED)"
        add(o, "na", "United States only", ntto[col], N, den, dsrc,
            "US only: arrivals to Canada and Mexico are not in this file, so the NA cell is a lower bound")
    for o, col in [("China", "china"), ("Korea", "korea"), ("US", "usa"), ("Australia", "australia"),
                   ("Hong Kong", "hong_kong"), ("Taiwan", "taiwan")]:
        den, dsrc = (au_out, "abs_340101_arrivals_monthly.csv st_residents_returning") if o == "Australia" else (None, None)
        add(o, "apac", "Japan only", jnto[col], J, den, dsrc,
            "Japan only: the rest of APAC (and all domestic travel) is not in this file, so the APAC cell is a lower bound")
    add("US", "na", "Canada only (overnight)", sc["us_residents_entering_overnight"],
        "statcan_24100053_monthly.csv us_residents_entering_overnight", None, None,
        "US->Canada only; US domestic travel, by far the largest NA flow, is in no file here")
    add("Canada", "na", "United States, share of ALL Canadian outbound", sc["canadians_returning_from_us_total"],
        "statcan_24100053_monthly.csv", ca_out, "statcan_24100053_monthly.csv (US + other)",
        "the one fully measured origin NA share in the set; excludes Canadian domestic travel")
    add("Brazil", "latam", "Brazil domestic air travel", anac["DOMÉSTICA"] / 2,
        "anac_brazil_passengers_monthly.csv DOMESTICA", br_trips,
        "anac_brazil_passengers_monthly.csv", "air only: road travel, the larger domestic mode, is not counted, so this is a lower bound")
    add("Japan", "apac", "Japan domestic accommodation nights", jta["total_nights"] - jta["foreign_nights"],
        "jta_accommodation_nights_monthly.csv (total - foreign)", None, None,
        "destination-side: Japanese domestic nights; Japanese OUTBOUND travel is in no file here")
    d = pd.DataFrame(rows)
    return d


# =====================================================================================================
# 2. the allocation matrix
# =====================================================================================================
# tier vocabulary:
#   MEASURED   - the cell is a ratio of two cached agency series (numerator and denominator both observed)
#   PARTIAL    - the numerator is observed but only for one destination country, or the denominator is a proxy
#   ASSUMED    - no file observes it; the number is my judgement, and the lo/hi band is what I will defend
#   UNIDENTIFIED - no file bears on it at all; lo/hi is a full bound, not a band
ALLOC = [
    # origin, dest, mid, lo, hi, tier, source
    ("India", "na", 0.060, 0.030, 0.100, "ASSUMED",
     "level and direction MEASURED (NTTO India->US 601,740 in 2Q26, -8.0% y/y, -16.1% in 1Q26); the SHARE needs India's total outbound, which no file here carries (india_mot_fta is PDF-only, MANIFEST 'no access')"),
    ("India", "emea", 0.200, 0.000, 0.400, "UNIDENTIFIED",
     "nothing in these files observes Indian travel to the Gulf, the UK or Europe; Airbnb's EMEA includes the Middle East, where most Indian outbound lands"),
    ("India", "latam", 0.005, 0.000, 0.020, "ASSUMED", "no file; negligible on any reading"),
    ("India", "apac", 0.735, 0.535, 0.965, "UNIDENTIFIED",
     "residual of the India row; includes Indian DOMESTIC travel (an APAC destination for Airbnb) and SE Asia, neither observed here. JNTO has no India row"),
    ("Brazil", "na", 0.032, 0.020, 0.050, "PARTIAL",
     "NTTO Brazil->US 460,830 (-2.7% y/y) over ANAC Brazilian air trips (pax/2, resident share 0.60 ASSUMED)"),
    ("Brazil", "emea", 0.030, 0.015, 0.090, "ASSUMED", "residual of the Brazil row after the measured LatAm floor; no file observes Brazil->Europe"),
    ("Brazil", "latam", 0.933, 0.860, 0.960, "PARTIAL",
     "ANAC domestic share of Brazilian air trips 78.3% in 2Q26 is a FLOOR (road travel, the larger domestic mode, is uncounted); intra-LatAm international is unobserved and added by judgement"),
    ("Brazil", "apac", 0.005, 0.000, 0.020, "ASSUMED", "no file; negligible"),
    ("Mexico", "na", 0.300, 0.200, 0.450, "ASSUMED",
     "level and direction MEASURED (NTTO Mexico->US 4,866,826 in 2Q26, +15.8% y/y, +13.4% in 1Q26 - the only named origin whose US-bound travel is ACCELERATING); no denominator for Mexican total travel in any file here"),
    ("Mexico", "emea", 0.020, 0.005, 0.040, "ASSUMED", "no file"),
    ("Mexico", "latam", 0.675, 0.510, 0.790, "ASSUMED", "residual; Mexican domestic travel is in no file here (datatur / banxico / upm all 'no access' in MANIFEST)"),
    ("Mexico", "apac", 0.005, 0.000, 0.020, "ASSUMED", "no file"),
    ("Japan", "na", 0.050, 0.030, 0.080, "ASSUMED",
     "level and direction MEASURED (NTTO Japan->US 422,551, +4.5% y/y); no Japanese-outbound denominator in any file here (JNTO is INBOUND to Japan)"),
    ("Japan", "emea", 0.030, 0.015, 0.060, "ASSUMED", "no file"),
    ("Japan", "latam", 0.005, 0.000, 0.020, "ASSUMED", "no file"),
    ("Japan", "apac", 0.915, 0.840, 0.955, "ASSUMED",
     "JTA measures Japanese DOMESTIC nights (28.2% foreign share in 2Q26, domestic nights -4.1% y/y) but not Japanese outbound, so the domestic-vs-outbound split is judgement"),
    # measured reference rows, not used in the tilt (no disclosed Airbnb origin growth for them)
    ("Canada", "na", 0.677, 0.677, 0.950, "MEASURED",
     "StatCan 24-10-0053: US share of ALL Canadian outbound trips, 67.7% in 2Q26 (76.1% in 2Q24, 67.0% in 2Q25). Lower bound on the NA cell because Canadian domestic travel is not in the file"),
    ("Canada", "emea", np.nan, 0.000, 0.323, "UNIDENTIFIED", "'returning from other countries' is a single undifferentiated series; no destination split"),
    ("Canada", "latam", np.nan, 0.000, 0.323, "UNIDENTIFIED", "same series"),
    ("Canada", "apac", np.nan, 0.000, 0.323, "UNIDENTIFIED", "same series"),
    ("Australia", "na", 0.085, 0.085, 0.130, "MEASURED",
     "NTTO Australia->US 249,259 over ABS resident short-term returns 2,932,340 = 8.50% of all Australian outbound (10.43% in 2Q24, 9.10% in 2Q25). US only, so a lower bound on NA"),
    ("Australia", "apac", 0.085, 0.085, 0.700, "PARTIAL",
     "JNTO Australia->Japan 248,653 over the same ABS denominator = 8.48% (7.93% in 2Q24, 8.66% in 2Q25). Japan only; NZ, Indonesia, Thailand and Australian domestic travel are not in these files"),
    ("Australia", "emea", np.nan, 0.000, 0.830, "UNIDENTIFIED", "no file observes Australian travel to Europe"),
    ("Australia", "latam", np.nan, 0.000, 0.830, "UNIDENTIFIED", "no file"),
    ("US", "na", 0.900, 0.750, 0.960, "ASSUMED",
     "US domestic travel is in no file here; the two measured US outbound cells are US->Canada (StatCan, 3,807,419 overnight, +6.3% y/y) and US->Japan (JNTO, 1,018,248, +3.4%; +27.5% in 2Q25)"),
    ("US", "apac", 0.025, 0.010, 0.060, "PARTIAL", "JNTO US->Japan measured as a level and a growth rate; no denominator"),
    ("US", "emea", np.nan, 0.000, 0.250, "UNIDENTIFIED", "no file observes US->Europe (UK ONS series discontinued, MANIFEST 'no coverage')"),
    ("US", "latam", np.nan, 0.000, 0.250, "UNIDENTIFIED", "no file"),
    ("China", "na", np.nan, 0.000, 1.000, "UNIDENTIFIED",
     "MEASURED as a level only: NTTO China->US 348,751, -0.2% y/y. No Chinese outbound denominator in any file here"),
    ("China", "apac", np.nan, 0.000, 1.000, "UNIDENTIFIED",
     "MEASURED as a level only: JNTO China->Japan 984,599, -58.2% y/y in 2Q26 (-54.6% in 1Q26). Both measured Chinese cells are flat or collapsing"),
    ("China", "emea", np.nan, 0.000, 1.000, "UNIDENTIFIED", "no file"),
    ("China", "latam", np.nan, 0.000, 1.000, "UNIDENTIFIED", "no file"),
    ("Korea", "apac", np.nan, 0.000, 1.000, "UNIDENTIFIED",
     "MEASURED as a level only: JNTO Korea->Japan 2,617,007, +14.9% y/y. NTTO has no Korea row; KTO datalab 'no access' in MANIFEST"),
    ("UK", "na", np.nan, 0.000, 1.000, "UNIDENTIFIED",
     "MEASURED as a level only: NTTO UK->US 1,028,895, -2.2% y/y. UK ONS overseas travel series discontinued after 2023"),
    ("Germany", "na", np.nan, 0.000, 1.000, "UNIDENTIFIED",
     "MEASURED as a level only: NTTO Germany->US 368,401, -22.8% y/y"),
]

TILT_ORIGINS = ["India", "Brazil", "Mexico", "Japan"]        # the four with a disclosed Airbnb origin growth rate

# origin size weight W = share of GLOBAL Airbnb nights booked on an origin basis. Not disclosed anywhere.
# mid / lo / hi are judgement, anchored on the disclosed destination-region shares (LatAm 17.9% of nights in
# 2Q26) and on the letters' ranking of the expansion markets. This is the binding unknown of the whole layer.
W_MID = {"India": 0.010, "Brazil": 0.055, "Mexico": 0.030, "Japan": 0.030}
W_LO = {"India": 0.005, "Brazil": 0.040, "Mexico": 0.020, "Japan": 0.020}
W_HI = {"India": 0.015, "Brazil": 0.070, "Mexico": 0.040, "Japan": 0.040}


def allocation_frame() -> pd.DataFrame:
    d = pd.DataFrame(ALLOC, columns=["origin", "dest_region", "share_mid", "share_lo", "share_hi", "tier", "source"])
    d["used_in_tilt"] = d.origin.isin(TILT_ORIGINS)
    d["W_mid_pct_of_global_nights"] = [W_MID.get(o, np.nan) * 100 for o in d.origin]
    d["W_lo_pct"] = [W_LO.get(o, np.nan) * 100 for o in d.origin]
    d["W_hi_pct"] = [W_HI.get(o, np.nan) * 100 for o in d.origin]
    return d


def alloc_dict(india_emea: float) -> dict:
    """The four tilt origins' allocation vectors, with the one unidentified degree of freedom (India's
    EMEA share) passed in explicitly. India's APAC cell is the residual."""
    a = {o: {} for o in TILT_ORIGINS}
    for o, dst, mid, lo, hi, tier, _ in ALLOC:
        if o in TILT_ORIGINS:
            a[o][dst] = mid
    a["India"]["emea"] = india_emea
    a["India"]["apac"] = 1.0 - a["India"]["na"] - a["India"]["emea"] - a["India"]["latam"]
    for o in TILT_ORIGINS:                              # renormalise the judgement rows to exactly 1
        t = sum(a[o].values())
        a[o] = {k: v / t for k, v in a[o].items()}
    return a


# =====================================================================================================
# 3. disclosed origin growth
# =====================================================================================================
def origin_growth_panel() -> pd.DataFrame:
    """Disclosed Airbnb origin-nights growth by quarter. Panel columns where they exist, letter quotes where
    the panel has none, forward-filled with a staleness flag."""
    p = pd.read_csv(PANEL).set_index("quarter")
    qs = ["4Q24", "1Q25", "2Q25", "3Q25", "4Q25", "1Q26", "2Q26"]
    # quote-sourced values the panel does not carry (10_regional_quotes.csv)
    QUOTE = {("Japan", "2Q26"): (18.0, "2Q26 letter: Japan origin net nights 'grew in the high-teens'"),
             ("Mexico", "4Q25"): (18.0, "4Q25 letter: Mexico origin nights 'up high-teens'"),
             ("Mexico", "1Q26"): (12.0, "1Q26 letter: 'continued double-digit nights growth in Mexico' (floor)"),
             ("Mexico", "2Q26"): (12.0, "2Q26 letter: 'continued strength from bookers in Mexico', no number: 1Q26 floor carried")}
    COL = {"India": "india_origin_growth_pct", "Brazil": "brazil_origin_growth_pct", "Japan": "japan_domestic_growth_pct"}
    rows = []
    for o in TILT_ORIGINS:
        last, lastq = np.nan, ""
        for q in qs:
            v, src = np.nan, ""
            if o in COL and q in p.index and pd.notna(p.loc[q, COL[o]]):
                v, src = float(p.loc[q, COL[o]]), f"10_regional_panel_quarterly.csv {COL[o]}"
            if (o, q) in QUOTE:
                v, src = QUOTE[(o, q)]
                src = "10_regional_quotes.csv: " + src
            fresh = pd.notna(v)
            if fresh:
                last, lastq = v, q
            rows.append({"quarter": q, "origin": o, "growth_yoy_pct": last if pd.notna(last) else np.nan,
                         "fresh_this_quarter": bool(fresh), "as_of_quarter": lastq,
                         "source": src if fresh else (f"carried from {lastq}" if lastq else "no disclosure at or before this quarter")})
    d = pd.DataFrame(rows)
    d["in_named_set"] = d.growth_yoy_pct.notna()
    return d


# =====================================================================================================
# 4. the implied ex-NA destination pattern
# =====================================================================================================
def _shares(q: str) -> dict:
    w = pd.read_csv(WIDE).set_index("quarter")
    return {r: float(w.loc[q, f"nights_share_{r}_pct"]) / 100.0 for r in C.REGIONS}


def implied_pattern(growth: dict, shares: dict, exna_target: float, alloc: dict, W: dict) -> dict:
    """Ex-NA destination growth implied by named-origin growth, with every unnamed origin growing at one
    common rate g_rest solved so the ex-NA aggregate lands on exna_target.

        g_d = [ sum_o W_o a_od g_o + R_d g_rest ] / S_d ,   R_d = S_d - sum_o W_o a_od

    Only ratios matter downstream (the forward k-scaling rescales the triple), but the level is kept so the
    numbers are readable next to the 8 / 20 / 18 buckets."""
    named = [o for o in alloc if o in growth and pd.notna(growth[o])]
    V = {d: {o: W[o] * alloc[o][d] for o in named} for d in EXNA}
    S = {d: shares[d] for d in EXNA}
    R = {d: S[d] - sum(V[d].values()) for d in EXNA}
    if min(R.values()) <= 0:
        raise ValueError(f"named origins over-fill a destination region: R={R}")
    num = sum(sum(V[d][o] * growth[o] for o in named) for d in EXNA)
    S_ex = sum(S.values())
    g_rest = (exna_target * S_ex - num) / sum(R.values())
    g = {d: (sum(V[d][o] * growth[o] for o in named) + R[d] * g_rest) / S[d] for d in EXNA}
    contrib = {d: (sum(V[d][o] * growth[o] for o in named) - g_rest * sum(V[d].values())) / S[d] for d in EXNA}
    out = {f"g_{d}": g[d] for d in EXNA}
    out.update({f"named_contrib_{d}_pp": contrib[d] for d in EXNA})
    out.update({f"named_mass_{d}_pct_of_region": sum(V[d].values()) / S[d] * 100 for d in EXNA})
    out["g_rest"] = g_rest
    out["exna_check"] = sum(S[d] * g[d] for d in EXNA) / S_ex
    return out


def base_quarter_inputs():
    p = pd.read_csv(PANEL).set_index("quarter")
    sh = _shares(BASE_Q)
    mids = {r: float(p.loc[BASE_Q, f"{r}_nights_yoy_mid"]) for r in C.REGIONS}
    exna = sum(sh[d] * mids[d] for d in EXNA) / sum(sh[d] for d in EXNA)
    return sh, mids, exna


def implied_tilt() -> pd.DataFrame:
    """The measured tilt as a replacement for EXNA_PATTERN 8 / 20 / 18, with the band from the two
    unidentified inputs: the origin size weights W and India's EMEA/APAC split."""
    sh, mids, exna = base_quarter_inputs()
    gp = origin_growth_panel()
    growth = {o: float(gp[(gp.origin == o) & (gp.quarter == BASE_Q)].growth_yoy_pct.iloc[0]) for o in TILT_ORIGINS}
    rows = []

    def run(label, W, ie, kind):
        r = implied_pattern(growth, sh, exna, alloc_dict(ie), W)
        r.update({"scenario": label, "kind": kind, "india_emea_share": ie,
                  **{f"W_{o}_pct": W[o] * 100 for o in TILT_ORIGINS}})
        rows.append(r)

    run("central (W mid, India EMEA 0.20)", W_MID, 0.20, "central")
    for ie, nm in [(0.00, "India all-APAC (EMEA 0.00)"), (0.40, "India all-EMEA-bound (EMEA 0.40)")]:
        run(f"India split corner: {nm}", W_MID, ie, "india_corner")
    for nm, W in [("W lo (named origins 11.5% -> 8.5% of nights)", W_LO), ("W hi (named origins 16.5% of nights)", W_HI)]:
        for ie in (0.00, 0.20, 0.40):
            run(f"{nm}, India EMEA {ie:.2f}", W, ie, "W_corner")
    run("stress: named origins at 2x the central weights", {o: 2 * W_MID[o] for o in W_MID}, 0.20, "stress")
    d = pd.DataFrame(rows)
    d["letter_emea"], d["letter_latam"], d["letter_apac"] = mids["emea"], mids["latam"], mids["apac"]
    d["exna_target"] = exna
    cols = ["scenario", "kind", "g_emea", "g_latam", "g_apac", "g_rest", "exna_check", "exna_target",
            "letter_emea", "letter_latam", "letter_apac", "india_emea_share"] + \
           [f"W_{o}_pct" for o in TILT_ORIGINS] + \
           [f"named_contrib_{d_}_pp" for d_ in EXNA] + [f"named_mass_{d_}_pct_of_region" for d_ in EXNA]
    return d[cols]


def letter_bucket_decomposition() -> pd.DataFrame:
    """Inverse question: holding the LETTER buckets 8 / 20 / 18, what growth do the UNNAMED origins have to
    deliver into each region? Shows how much of the disclosed dispersion the origin statements explain."""
    sh, mids, exna = base_quarter_inputs()
    gp = origin_growth_panel()
    growth = {o: float(gp[(gp.origin == o) & (gp.quarter == BASE_Q)].growth_yoy_pct.iloc[0]) for o in TILT_ORIGINS}
    a, rows = alloc_dict(0.20), []
    for d_ in EXNA:
        V = {o: W_MID[o] * a[o][d_] for o in TILT_ORIGINS}
        S, m = sh[d_], sum(V.values())
        named_pp = sum(V[o] * growth[o] for o in TILT_ORIGINS) / S
        rows.append({"dest_region": d_, "letter_bucket_pct": mids[d_], "region_share_of_nights_pct": S * 100,
                     "named_origin_mass_pct_of_region": m / S * 100, "named_origin_pp_of_region_growth": named_pp,
                     "implied_unnamed_origin_growth_pct": (S * mids[d_] - sum(V[o] * growth[o] for o in TILT_ORIGINS)) / (S - m)})
    d = pd.DataFrame(rows)
    b = d.set_index("dest_region")
    d["gap_vs_emea_letter_pp"] = d.letter_bucket_pct - b.loc["emea", "letter_bucket_pct"]
    d["gap_vs_emea_explained_by_named_pp"] = d.named_origin_pp_of_region_growth - b.loc["emea", "named_origin_pp_of_region_growth"]
    d["share_of_gap_explained_pct"] = np.where(d.gap_vs_emea_letter_pp != 0,
                                               d.gap_vs_emea_explained_by_named_pp / d.gap_vs_emea_letter_pp * 100, np.nan)
    return d


# =====================================================================================================
# 5. pricing the tilt through exfx.geo_mix_pp
# =====================================================================================================
def _adr_levels_by_forward_quarter(rgf: pd.DataFrame) -> dict:
    """Same rule as exfx.geo_mix_forward: anchored regional ADRs at the base quarter, carried when the base
    quarter is itself a modelled quarter (3Q27 / 4Q27)."""
    w = pd.read_csv(WIDE).set_index("quarter")
    lv, cur = {}, None
    for q, r in rgf.iterrows():
        bq = r.base_quarter
        if bq in w.index:
            cur = {rr: float(w.loc[bq, f"adr_{rr}_usd_anchored"]) for rr in C.REGIONS}
        lv[q] = cur
    return lv


def price_pattern(pattern: dict, rgf: pd.DataFrame, adr: dict) -> pd.DataFrame:
    """Scale an ex-NA pattern to each forward quarter's ex-NA rate on that quarter's base shares (the
    EXNA_PATTERN convention), then price the four-region mix with exfx.geo_mix_pp."""
    out = {}
    for q, r in rgf.iterrows():
        wv = np.array([r[f"share_{d}"] for d in EXNA])
        pv = np.array([pattern[d] for d in EXNA])
        k = r.exna_yoy / float((wv * pv).sum() / wv.sum())
        growth = {"na": float(r.g_na), **{d: k * pattern[d] for d in EXNA}}
        shares = {rr: float(r[f"share_{rr}"]) for rr in C.REGIONS}
        out[q] = {"geo_mix_pp": exfx.geo_mix_pp(shares, adr[q], growth), "k_scale": k,
                  **{f"g_{d}": growth[d] for d in EXNA}}
    return pd.DataFrame(out).T


def lambda_to_reproduce_letters() -> dict:
    """How large would the four named origins have to be, as a share of global nights, for their disclosed
    growth to generate the letter buckets 8 / 20 / 18 on its own? Solved on the LatAm-minus-EMEA gap."""
    sh, mids, exna = base_quarter_inputs()
    gp = origin_growth_panel()
    g = {o: float(gp[(gp.origin == o) & (gp.quarter == BASE_Q)].growth_yoy_pct.iloc[0]) for o in TILT_ORIGINS}
    a = alloc_dict(0.20)
    target = mids["latam"] - mids["emea"]
    # feasibility cap: named origins cannot fill more than 100% of any destination region
    cap = min(sh[d] / sum(W_MID[o] * a[o][d] for o in TILT_ORIGINS) for d in EXNA) * 0.999
    lo, hi = 0.05, cap
    for _ in range(80):
        mid = (lo + hi) / 2
        r = implied_pattern(g, sh, exna, a, {o: mid * W_MID[o] for o in W_MID})
        (lo, hi) = (mid, hi) if (r["g_latam"] - r["g_emea"]) < target else (lo, mid)
    lam = (lo + hi) / 2
    r = implied_pattern(g, sh, exna, a, {o: lam * W_MID[o] for o in W_MID})
    return {"lambda": lam, "feasibility_cap_lambda": cap,
            "reached_target": bool(abs((r["g_latam"] - r["g_emea"]) - target) < 0.05),
            "gap_at_lambda_pp": r["g_latam"] - r["g_emea"], "target_gap_pp": target,
            "named_share_of_global_nights_pct": lam * sum(W_MID.values()) * 100,
            "central_named_share_pct": sum(W_MID.values()) * 100,
            "plausible_ceiling_pct": sum(W_HI.values()) * 100,
            **{f"g_{d}": r[f"g_{d}"] for d in EXNA}, "g_rest": r["g_rest"]}


def geo_mix_measured_tilt() -> pd.DataFrame:
    rgf = pd.read_csv(RGF).set_index("quarter")
    adr = _adr_levels_by_forward_quarter(rgf)
    t = implied_tilt().set_index("scenario")
    cen = t[t.kind == "central"].iloc[0]
    pats = {"base pattern EMEA 8 / LatAm 20 / APAC 18 (2Q26 letter buckets)": {"emea": 8.0, "latam": 20.0, "apac": 18.0},
            "tilt B: EMEA 5 / LatAm 30 / APAC 25 (the v1 scenario)": {"emea": 5.0, "latam": 30.0, "apac": 25.0},
            "measured OD tilt (central)": {d: float(cen[f"g_{d}"]) for d in EXNA}}
    band = t[t.kind.isin(["central", "india_corner", "W_corner"])]
    for nm, ix in [("measured OD tilt (band: most EMEA-tilted corner)", band.g_emea.idxmax()),
                   ("measured OD tilt (band: most LatAm/APAC-tilted corner)", band.g_emea.idxmin())]:
        pats[nm] = {d: float(band.loc[ix, f"g_{d}"]) for d in EXNA}
    st = t[t.kind == "stress"].iloc[0]
    pats["stress: named origins at 2x weight"] = {d: float(st[f"g_{d}"]) for d in EXNA}
    rows = []
    for nm, p in pats.items():
        pr = price_pattern(p, rgf, adr)
        for q in pr.index:
            rows.append({"quarter": q, "pattern": nm, "p_emea": p["emea"], "p_latam": p["latam"], "p_apac": p["apac"],
                         "g_emea": pr.loc[q, "g_emea"], "g_latam": pr.loc[q, "g_latam"], "g_apac": pr.loc[q, "g_apac"],
                         "g_na": float(rgf.loc[q, "g_na"]), "exna_yoy": float(rgf.loc[q, "exna_yoy"]),
                         "geo_mix_pp": pr.loc[q, "geo_mix_pp"]})
    d = pd.DataFrame(rows)
    b = d[d.pattern.str.startswith("base pattern")].set_index("quarter").geo_mix_pp
    d["delta_vs_base_pp"] = [r.geo_mix_pp - b[r.quarter] for _, r in d.iterrows()]
    # self-check: the base pattern priced here must reproduce the line's own geo_mix_forward.csv exactly
    gmf = pd.read_csv(C.OUT / "geo_mix_forward.csv").set_index("quarter").geo_mix_nights_linked_pp
    err = max(abs(b[q] - gmf[q]) for q in b.index)
    assert err < 1e-9, f"replication of geo_mix_forward failed, max |diff| = {err}"
    d.attrs["replication_max_abs_diff_pp"] = err
    return d


# =====================================================================================================
# 6. validation on history
# =====================================================================================================
def validation() -> pd.DataFrame:
    """Does a region's exposure to the named high-growth origins predict how far its disclosed bucket sits
    above or below the ex-NA average, quarter by quarter? x = named-origin-weighted growth into the region,
    y = disclosed bucket mid minus that quarter's disclosed ex-NA rate. Both demeaned within a quarter."""
    p = pd.read_csv(PANEL).set_index("quarter")
    gp = origin_growth_panel()
    w = pd.read_csv(WIDE).set_index("quarter")
    a = alloc_dict(0.20)
    rows = []
    for q in sorted(gp.quarter.unique(), key=C.qlabel_to_period):
        if q not in p.index or q not in w.index or pd.isna(p.loc[q, "emea_nights_yoy_mid"]):
            continue
        sh = {r: float(w.loc[q, f"nights_share_{r}_pct"]) / 100.0 for r in C.REGIONS}
        mids = {r: float(p.loc[q, f"{r}_nights_yoy_mid"]) for r in C.REGIONS}
        exna = sum(sh[d] * mids[d] for d in EXNA) / sum(sh[d] for d in EXNA)
        g = {o: float(gp[(gp.origin == o) & (gp.quarter == q)].growth_yoy_pct.iloc[0]) for o in TILT_ORIGINS}
        g = {o: v for o, v in g.items() if pd.notna(v)}
        fresh = int(gp[(gp.quarter == q) & gp.fresh_this_quarter].shape[0])
        if not g:
            continue
        x = {d: sum(W_MID[o] * a[o][d] * g[o] for o in g) / sh[d] for d in EXNA}
        try:
            imp = implied_pattern(g, sh, exna, {o: a[o] for o in g}, W_MID)
        except ValueError:
            imp = {f"g_{d}": np.nan for d in EXNA}
        xm, ym = np.mean(list(x.values())), np.mean([mids[d] - exna for d in EXNA])
        for d in EXNA:
            rows.append({"quarter": q, "dest_region": d, "n_origins_disclosed": len(g), "n_fresh_this_quarter": fresh,
                         "named_origin_pp_into_region": x[d], "x_demeaned": x[d] - xm,
                         "disclosed_bucket_mid_pct": mids[d], "exna_disclosed_pct": exna,
                         "y_bucket_minus_exna_pp": mids[d] - exna, "y_demeaned": (mids[d] - exna) - ym,
                         "implied_g_common_residual_pct": imp.get(f"g_{d}", np.nan)})
    return pd.DataFrame(rows)


def validation_scores(v: pd.DataFrame) -> pd.DataFrame:
    out = []
    xy = v.dropna(subset=["x_demeaned", "y_demeaned"])
    nq = xy.quarter.nunique()
    out.append({"test": "pooled region-quarter: named-origin exposure vs bucket deviation from ex-NA (demeaned within quarter)",
                "n": len(xy), "pearson_r": float(np.corrcoef(xy.x_demeaned, xy.y_demeaned)[0, 1]),
                "spearman_r": float(pd.Series(xy.x_demeaned).rank().corr(pd.Series(xy.y_demeaned).rank())),
                "sign_agreement_pct": float((np.sign(xy.x_demeaned) == np.sign(xy.y_demeaned)).mean() * 100),
                "value": np.nan,
                "caveat": f"NOT {len(xy)} independent observations: the cross-section is the same ordering repeated in {nq} quarters, "
                          f"so the effective n is {nq}. Read it with the ordering test below, not on its own."})
    # the honest version of the same test: does the implied ORDERING match the disclosed ordering, quarter by quarter?
    ok, hit, miss, tied = 0, [], [], []
    for q, s_ in xy.groupby("quarter"):
        a_ = list(s_.sort_values("named_origin_pp_into_region", ascending=False).dest_region)
        b_ = list(s_.sort_values("y_bucket_minus_exna_pp", ascending=False).dest_region)
        if s_.disclosed_bucket_mid_pct.duplicated().any():       # two buckets tied: the ordering is not identified
            tied.append(q)
        (hit if a_ == b_ else miss).append(f"{q}[{'>'.join(b_)}]")
        ok += int(a_ == b_)
    from math import comb
    pval = sum(comb(nq, k) * (1 / 6) ** k * (5 / 6) ** (nq - k) for k in range(ok, nq + 1))
    out.append({"test": "ordering test: implied region ranking == disclosed bucket ranking, per quarter",
                "n": nq, "pearson_r": np.nan, "spearman_r": np.nan,
                "sign_agreement_pct": ok / nq * 100, "value": ok,
                "caveat": f"{ok} of {nq} quarters exact. Binomial tail against 1/6 (a random ranking of 3 regions): p = {pval:.3f}. "
                          f"hits {'; '.join(hit)} | misses {'; '.join(miss)} | quarters where two disclosed buckets are TIED "
                          f"so the ordering is not identified: {', '.join(tied) if tied else 'none'}"})
    nq2 = nq - len(tied)
    ok2 = ok + sum(1 for m in miss if m.split("[")[0] in tied)
    out.append({"test": "ordering test, quarters with two tied disclosed buckets dropped",
                "n": nq2, "pearson_r": np.nan, "spearman_r": np.nan, "sign_agreement_pct": ok / nq2 * 100 if nq2 else np.nan,
                "value": ok, "caveat": f"{ok} of {nq2} quarters exact once {', '.join(tied) if tied else 'no quarter'} is dropped; "
                                       f"binomial tail p = {sum(comb(nq2, k) * (1/6)**k * (5/6)**(nq2-k) for k in range(ok, nq2 + 1)):.3f}"})
    for d in EXNA:
        s = v[v.dest_region == d].dropna(subset=["named_origin_pp_into_region", "y_bucket_minus_exna_pp"])
        out.append({"test": f"TIME SERIES {d}: named-origin pp into region vs bucket minus ex-NA, across quarters", "n": len(s),
                    "pearson_r": float(np.corrcoef(s.named_origin_pp_into_region, s.y_bucket_minus_exna_pp)[0, 1]) if len(s) > 2 else np.nan,
                    "spearman_r": float(s.named_origin_pp_into_region.rank().corr(s.y_bucket_minus_exna_pp.rank())) if len(s) > 2 else np.nan,
                    "sign_agreement_pct": np.nan, "value": np.nan,
                    "caveat": "the allocation carries no time-series information: it is a fixed matrix, so this only tests whether "
                              "quarter-to-quarter moves in disclosed origin growth track quarter-to-quarter moves in the bucket"})
    p = pd.read_csv(PANEL).set_index("quarter")
    gp = origin_growth_panel()
    for o, d in [("Brazil", "latam"), ("India", "apac"), ("Japan", "apac"), ("Mexico", "latam")]:
        s = gp[(gp.origin == o) & gp.growth_yoy_pct.notna()].set_index("quarter")
        qs = [q for q in s.index if q in p.index and pd.notna(p.loc[q, f"{d}_nights_yoy_mid"])]
        x = s.loc[qs, "growth_yoy_pct"].astype(float).values
        y = np.array([float(p.loc[q, f"{d}_nights_yoy_mid"]) for q in qs])
        r = float(np.corrcoef(x, y)[0, 1]) if len(qs) > 2 and x.std() > 0 and y.std() > 0 else np.nan
        out.append({"test": f"direct: disclosed {o} origin growth vs disclosed {d} bucket mid", "n": len(qs),
                    "pearson_r": r, "spearman_r": float(pd.Series(x).rank().corr(pd.Series(y).rank())) if len(qs) > 2 else np.nan,
                    "sign_agreement_pct": np.nan, "value": np.nan,
                    "caveat": f"the {d} bucket mid takes {len(set(y))} distinct values in these {len(qs)} quarters (V survey point 6: "
                              f"a management bucket is a step function), so a correlation on it is near-meaningless"})
    # the market-vs-Airbnb sanity check the V survey already flagged
    s = sources()
    jta = s["jta"]["total_nights"] - s["jta"]["foreign_nights"]
    bq = pd.Period("2026Q2", freq="Q")
    out.append({"test": "context: Japan DOMESTIC accommodation nights y/y 2Q26 (JTA), against Airbnb Japan origin +18%",
                "n": 1, "pearson_r": np.nan, "spearman_r": np.nan, "sign_agreement_pct": np.nan,
                "value": float(jta.loc[bq] / jta.loc[bq - 4] - 1) * 100,
                "caveat": "the destination market is shrinking while Airbnb's origin nights grow high-teens: these files measure "
                          "markets, Airbnb's growth is share, so they can inform the ALLOCATION and never the LEVEL"})
    nt = s["ntto"]["CANADA"].loc[bq]
    st = s["statcan"]["canadians_returning_from_us_total"].loc[bq]
    out.append({"test": "cross-source consistency: the SAME flow (Canadians to the US, 2Q26) as NTTO counts it vs as StatCan counts it",
                "n": 2, "pearson_r": np.nan, "spearman_r": np.nan, "sign_agreement_pct": np.nan, "value": float(st / nt),
                "caveat": f"StatCan {st:,.0f} returns vs NTTO {nt:,.0f} arrivals = a ratio of {st/nt:.2f}x on one flow. Any share built "
                          f"by dividing one agency's numerator by another agency's denominator (Australia, Brazil) inherits an error of this size."})
    return pd.DataFrame(out)


# =====================================================================================================
def main() -> int:
    C.OUT.mkdir(parents=True, exist_ok=True)
    mc = measured_cells(); mc.to_csv(C.OUT / "od_measured_cells.csv", index=False)
    al = allocation_frame(); al.to_csv(C.OUT / "od_origin_allocation.csv", index=False)
    og = origin_growth_panel(); og.to_csv(C.OUT / "od_origin_growth_panel.csv", index=False)
    it = implied_tilt(); it.to_csv(C.OUT / "od_implied_tilt.csv", index=False)
    lb = letter_bucket_decomposition(); lb.to_csv(C.OUT / "od_letter_bucket_decomposition.csv", index=False)
    gm = geo_mix_measured_tilt(); gm.to_csv(C.OUT / "od_geo_mix_measured_tilt.csv", index=False)
    va = validation(); va.to_csv(C.OUT / "od_validation.csv", index=False)
    vs = validation_scores(va); vs.to_csv(C.OUT / "od_validation_scores.csv", index=False)
    lam = lambda_to_reproduce_letters()
    pd.DataFrame([lam]).to_csv(C.OUT / "od_letter_bucket_lambda.csv", index=False)

    pd.set_option("display.width", 220)
    print("=== measured origin x destination cells (2Q26) ===")
    print(mc[["origin", "dest_region", "destination_proxy", "level_2Q26", "yoy_2Q26_pct", "share_of_denominator_pct"]].round(2).to_string(index=False))
    print("\n=== allocation tiers ===")
    print(al.groupby("tier").size().to_string())
    print("\n=== disclosed origin growth used (2Q26) ===")
    print(og[og.quarter == BASE_Q][["origin", "growth_yoy_pct", "fresh_this_quarter", "source"]].to_string(index=False))
    print("\n=== implied ex-NA pattern vs the 8 / 20 / 18 letter buckets ===")
    print(it[["scenario", "g_emea", "g_latam", "g_apac", "g_rest"]].round(2).to_string(index=False))
    print("\n=== what the letter buckets require of the UNNAMED origins ===")
    print(lb.round(2).to_string(index=False))
    print("\n=== priced geo mix (pp of blended ADR) ===")
    print(gm.pivot(index="quarter", columns="pattern", values="geo_mix_pp").round(3).to_string())
    print("\n=== named-origin weight that would reproduce the letter buckets on its own ===")
    print({k: round(v, 3) for k, v in lam.items()})
    print("\n=== validation ===")
    print(vs[["test", "n", "pearson_r", "spearman_r", "sign_agreement_pct", "value"]].round(3).to_string(index=False))
    print("\nwrote:", ", ".join(sorted(p.name for p in C.OUT.glob("od_*.csv"))))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
