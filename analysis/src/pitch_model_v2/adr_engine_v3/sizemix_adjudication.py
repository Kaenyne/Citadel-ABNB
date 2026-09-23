"""sizemix_adjudication.py — mitigation A for the ADR line v2.

Two labelled weaknesses of the ADR line are settled here.

(1) THE SIZE-MIX SIGN.  The 10-K annual decomposition (`data/processed/adr/07_full_decomposition.csv`,
    built by `analysis/src/adr/07_assemble.py` off `05_size_mix.py`) carries a 2025 unit-size term of
    -0.251pp.  The H route (`data/processed/q3nowcast/H/adr_history_components.csv`, built by
    `analysis/src/adr/13_party_size_adr.py`) carries +0.739pp for the same year.  A 0.99pp disagreement
    that flips sign, and it drives the entire apparent 2025 step in the 10-K plug's implied
    like-for-like price (2.68 -> 3.93).  This module reproduces both routes from their committed
    files, recomputes the 05 route's own 2025 pairs under fixed base-period weights, prices the only
    filed size metric (the 2Q26 letter's Bedroom Nights Booked) at the measured bedroom elasticity,
    and rebases the plug on the adopted term.

(2) THE BUNDLE'S FILED PROVENANCE.  `X3_x3_bundle_sentences_provenance.md` §8 names the 1Q26 10-Q
    (accession 0001559720-26-000014) as the one filing never read.  `fetch_10q()` fetches it from
    EDGAR (guarded by --fetch; the file is committed under data/raw/), and `tenq_sentences()` searches
    it and the 2Q26 10-Q already on disk for every driver sentence and every magnitude.

NOTHING HERE IS FITTED.  Every coefficient is read from a committed file; the only new arithmetic is
a re-weighting of an existing panel and a multiplication of a filed growth rate by a measured
elasticity.

Outputs
  data/processed/pitch_model_v2/adr_engine/sizemix_routes.csv         both routes + the filed arbiter
  data/processed/pitch_model_v2/adr_engine/sizemix_rebased_plug.csv   the plug under each size term
  data/processed/pitch_model_v2/adr_engine/sizemix_10q_sentences.csv  1Q26 and 2Q26 10-Q sentences

Run
  cd ~/Citadel-ABNB && PYTHONPATH=analysis/src python3 -W ignore -m pitch_model_v2.adr_engine.sizemix_adjudication
  # add --fetch to re-fetch the 1Q26 10-Q from EDGAR (2 requests; needs a User-Agent with an email)
"""
from __future__ import annotations

import html
import re
import sys

import numpy as np
import pandas as pd

from pitch_model_v2.adr_engine import config

ROOT = config.ROOT
OUT = config.OUT

DEC07 = ROOT / "data/processed/adr/07_full_decomposition.csv"
SIZE05_SUMMARY = ROOT / "data/processed/adr/05_size_mix_summary.csv"
SIZE05_PAIRS = ROOT / "data/processed/adr/05_size_mix_pairs.csv"
SIZE08_SUMMARY = ROOT / "data/processed/adr/08_size_mix_extended_summary.csv"
H_COMPONENTS = ROOT / "data/processed/q3nowcast/H/adr_history_components.csv"
I_PARTY_Q = ROOT / "data/processed/adrq3/I/I1_party_size_quarterly.csv"
I_MIX = ROOT / "data/processed/adrq3/I/I_mix_terms_3q26.csv"
RECONCILE = OUT / "reconcile_annual.csv"
REGIONAL_ANNUAL = ROOT / "data/processed/adr/01_regional_annual.csv"

RAW = ROOT / "data/raw/regulatory/quantification"
Q1_10Q = RAW / "abnb_2026q1_10q.html"
Q2_10Q = RAW / "abnb_2026q2_10q.html"

EDGAR_DIR = "https://www.sec.gov/Archives/edgar/data/1559720/000155972026000014/"
EDGAR_PRIMARY = EDGAR_DIR + "abnb-20260331.htm"
UA = "Citadel-ABNB-research theobmachado@gmail.com"

# ---- filed facts, transcribed, not computed -------------------------------------------------
# 2Q26 shareholder letter (8-K 2026-08-06 Ex 99.1), via 02_kpi_panel_long.csv row
# "2Q26,bedroom_nights_yoy_pct,12,...": "Bedroom Nights Booked -- nights booked multiplied by
# bedroom count -- grew over 12%" against Nights and Seats Booked +10%.
FILED_BEDROOM_NIGHTS_YOY = 12.0      # per cent, stated as "over 12%" -> a floor
FILED_NIGHTS_YOY = 10.0              # per cent, 2Q26 Nights and Seats Booked
# FY2025 10-K MD&A, Geographic Mix: "Our total Company average nights per booking, excluding
# experiences and services, was 3.7 in 2025 compared to 3.8 in 2024."
FILED_NPB_2024, FILED_NPB_2025 = 3.8, 3.7
# adr_v1_design / Krish 2026-09-07 §4.4: externally bounded LOS elasticity, not fitted.
LOS_ELASTICITY, LOS_ELASTICITY_LO, LOS_ELASTICITY_HI = -0.15, -0.05, -0.25
BED_ELASTICITY_RANGE = (0.15, 0.30)  # the brief's sensitivity band around the measured 0.23


# ------------------------------------------------------------------ route reproduction
def h_route() -> pd.DataFrame:
    """H / 13 route, annualised exactly as reconcile.py does it: GBV-weighted mean of the
    quarterly terms.  unit_size_pp = 0.592 x d ln(booked capacity per reviewed stay)."""
    h = pd.read_csv(H_COMPONENTS)
    h["year"] = h.quarter.str[2:].astype(int) + 2000
    rows = []
    for y, g in h.groupby("year"):
        if len(g) != 4:
            continue
        w = g.gbv_busd
        rows.append(dict(
            year=int(y), n_quarters=len(g),
            size_pp=float(np.average(g.unit_size_pp, weights=w)),
            los_pp=float(np.average(g.los_mix_pp, weights=w)),
            cap_yoy_pct=float(np.average(g.booked_capacity_yoy_pct, weights=w)),
            within_region_exfx_pp=float(np.average(g.within_region_exfx_pp, weights=w))))
    return pd.DataFrame(rows)


def route05_year() -> pd.DataFrame:
    """The 05 route as 07_assemble.size_by_year() reads it: scope == 'year', quote basis."""
    s = pd.read_csv(SIZE05_SUMMARY)
    y = s[s.scope == "year"].copy()
    y["year"] = pd.to_datetime(y.date_b_min).dt.year
    keep = ["year", "n_pairs", "n_markets", "markets", "date_b_min", "date_b_max",
            "est_nights_a", "est_nights_b", "nights_yoy_pct", "bedroom_nights_yoy_pct",
            "size_wedge_pp", "cap_per_booked_night_a", "cap_per_booked_night_yoy_pct",
            "d_bedrooms", "d_mean_log_capacity", "size_mix_pp_quote_basis",
            "hedonic_bed_coef_quote", "hedonic_lacc_coef_quote"]
    return y[keep].sort_values("year").reset_index(drop=True)


def hedonic_coefs() -> tuple[float, float]:
    y = route05_year().iloc[0]
    return float(y.hedonic_bed_coef_quote), float(y.hedonic_lacc_coef_quote)


def size_pp(d_bed: float, d_mlogcap: float) -> float:
    """05_size_mix.size_pp, reproduced: semi-log hedonic, quote basis."""
    b_bed, b_lacc = hedonic_coefs()
    return (np.exp(b_bed * d_bed + b_lacc * d_mlogcap) - 1) * 100


def route05_reweighted() -> pd.DataFrame:
    """The 05 route's OWN eligible pairs, aggregated three ways.

    `05_size_mix.agg()` pools: it sums est_nights and bedroom_nights over markets on each side and
    takes the growth of the sums, and it forms d_mean_log_capacity as (period-b weighted mean) less
    (period-a weighted mean).  Both legs therefore carry the change in each market's SHARE OF THE
    PANEL, which for Inside Airbnb is scrape coverage, not Airbnb nights.  The fixed-weight variant
    holds each market at its base-period weight, so only the within-market size change survives."""
    p = pd.read_csv(SIZE05_PAIRS)
    g0 = p[p.pair_eligible == True]                                    # noqa: E712
    rows = []
    for y, g in g0.groupby("year_b"):
        na, nb = g.est_nights_a.sum(), g.est_nights_b.sum()
        ba, bb = g.bedroom_nights_a.sum(), g.bedroom_nights_b.sum()
        wa, wb = g.est_nights_a / na, g.est_nights_b / nb
        d_bed_pool = bb / nb - ba / na
        d_ml_pool = (wb * g.mlogcap_b).sum() - (wa * g.mlogcap_a).sum()
        d_bed_fix = (wa * (g.bed_per_night_b - g.bed_per_night_a)).sum()
        d_ml_fix = (wa * (g.mlogcap_b - g.mlogcap_a)).sum()
        rows.append(dict(
            year=int(y), n_pairs=len(g), n_markets=int(g.market.nunique()),
            markets="|".join(sorted(g.market.unique())),
            pairs_all_positive_wedge=bool((g.size_wedge_pp > 0).all()),
            wedge_min_pp=float(g.size_wedge_pp.min()), wedge_max_pp=float(g.size_wedge_pp.max()),
            wedge_pooled_pp=(bb / ba - 1) * 100 - (nb / na - 1) * 100,
            wedge_fixedw_pp=float((wa * g.size_wedge_pp).sum()),
            wedge_equalw_pp=float(g.size_wedge_pp.mean()),
            d_bed_pooled=float(d_bed_pool), d_bed_fixedw=float(d_bed_fix),
            d_bed_between=float(d_bed_pool - d_bed_fix),
            d_ml_pooled=float(d_ml_pool), d_ml_fixedw=float(d_ml_fix),
            size_pp_pooled=float(size_pp(d_bed_pool, d_ml_pool)),
            size_pp_fixedw=float(size_pp(d_bed_fix, d_ml_fix)),
            panel_nights_yoy_pct=(nb / na - 1) * 100))
    return pd.DataFrame(rows).sort_values("year").reset_index(drop=True)


def weight_shift_2025() -> pd.DataFrame:
    """Which market's panel weight moved, and how much bedroom count it carried."""
    p = pd.read_csv(SIZE05_PAIRS)
    g = p[(p.pair_eligible == True) & (p.year_b == 2025)].copy()       # noqa: E712
    g["wa"] = g.est_nights_a / g.est_nights_a.sum()
    g["wb"] = g.est_nights_b / g.est_nights_b.sum()
    m = g.groupby("market").agg(
        w_base=("wa", "sum"), w_current=("wb", "sum"),
        bed_per_night_base=("bed_per_night_a", "mean"),
        bed_per_night_current=("bed_per_night_b", "mean"),
        panel_nights_yoy_pct=("nights_yoy_pct", "mean")).reset_index()
    m["d_weight_pp"] = (m.w_current - m.w_base) * 100
    return m.sort_values("d_weight_pp")


# ------------------------------------------------------------------ the filed arbiter
def bedroom_elasticity() -> pd.DataFrame:
    """Reproduce the 0.23.  In a semi-log hedonic log p = ... + b_bed * bedrooms, the ELASTICITY of
    price to bedroom COUNT at a mean of B bedrooms per booked night is b_bed * B.  Krish's
    2026-09-07 note states 0.2289 on the 12-market panel and 0.2312 on the 29-market panel."""
    b_bed, b_lacc = hedonic_coefs()
    s05 = pd.read_csv(SIZE05_SUMMARY)
    s08 = pd.read_csv(SIZE08_SUMMARY)
    rows = []
    for lab, df, scope in (("12-market (05)", s05, "disclosure_window_2Q26"),
                           ("29-market (08)", s08, "2Q26_panel_extended")):
        r = df[df.scope == scope].iloc[0]
        B = float(r.bed_per_booked_night_a)
        rows.append(dict(panel=lab, n_markets=int(r.n_markets), n_pairs=int(r.n_pairs),
                         bedrooms_per_booked_night=B, b_bed=b_bed,
                         elasticity_adr_to_bedrooms=b_bed * B,
                         bed_per_logcap=np.nan))
    # the H route's own conversion, for the capacity channel
    b_per_lc = 1.0
    s = s08[s08.scope.str.contains("market") & s08.market.notna() & s08.n_pairs.ge(1)]
    s = s.dropna(subset=["d_bedrooms", "d_mean_log_capacity"])
    b_per_lc = float((s.d_bedrooms * s.est_nights_b).sum() / (s.d_mean_log_capacity * s.est_nights_b).sum())
    rows.append(dict(panel="H conversion (13.elasticities, market rows of 08)",
                     n_markets=int(s.market.nunique()), n_pairs=int(s.n_pairs.sum()),
                     bedrooms_per_booked_night=np.nan, b_bed=b_bed,
                     elasticity_adr_to_bedrooms=np.nan, bed_per_logcap=b_per_lc))
    return pd.DataFrame(rows)


def arbiter_rows() -> list[dict]:
    """What the filed Bedroom Nights Booked metric implies for ADR, and what nights-per-booking
    implies for LOS.  Both are read off filings, not estimated here."""
    b_bed, b_lacc = hedonic_coefs()
    el = bedroom_elasticity()
    eps29 = float(el.loc[el.panel == "29-market (08)", "elasticity_adr_to_bedrooms"].iloc[0])
    eps12 = float(el.loc[el.panel == "12-market (05)", "elasticity_adr_to_bedrooms"].iloc[0])
    b_per_lc = float(el.bed_per_logcap.dropna().iloc[0])

    # bedrooms per booked night, y/y, from the two filed growth rates
    d_ln_bed = np.log(1 + FILED_BEDROOM_NIGHTS_YOY / 100) - np.log(1 + FILED_NIGHTS_YOY / 100)
    wedge_simple = FILED_BEDROOM_NIGHTS_YOY - FILED_NIGHTS_YOY
    rows = []
    for lab, eps in (("measured 0.23 (29-mkt 0.2312)", eps29),
                     ("measured 0.23 (12-mkt 0.2289)", eps12),
                     ("low end 0.15", BED_ELASTICITY_RANGE[0]),
                     ("high end 0.30", BED_ELASTICITY_RANGE[1])):
        rows.append(dict(route="filed arbiter: 2Q26 Bedroom Nights Booked", period="2Q26",
                         basis=f"bedroom channel only, elasticity {lab}",
                         panel="Airbnb, global, filed", n_markets=np.nan, n_pairs=np.nan,
                         wedge_pp=wedge_simple, capacity_yoy_pct=np.nan,
                         size_pp=100 * eps * d_ln_bed,
                         note="'over 12%' is a floor, so the implication is a floor too"))
    # the same filed wedge priced through the FULL hedonic: bedrooms plus the capacity that moves
    # with them at the panel's measured 1.37 bedrooms per unit of log capacity.
    d_bed_abs = d_ln_bed * float(el.loc[el.panel == "29-market (08)", "bedrooms_per_booked_night"].iloc[0])
    d_ml = d_bed_abs / b_per_lc
    rows.append(dict(route="filed arbiter: 2Q26 Bedroom Nights Booked", period="2Q26",
                     basis="full hedonic (bedrooms + co-moving capacity)",
                     panel="Airbnb, global, filed", n_markets=np.nan, n_pairs=np.nan,
                     wedge_pp=wedge_simple, capacity_yoy_pct=100 * d_ml,
                     size_pp=float(size_pp(d_bed_abs, d_ml)),
                     note="upper leg of the bracket; this is the mapping the two routes use"))
    # FY25 10-K nights per booking -> the LOS term, the second filed arbiter
    d_ln_npb = np.log(FILED_NPB_2025 / FILED_NPB_2024) * 100
    for lab, e in (("central -0.15", LOS_ELASTICITY),
                   ("low -0.05", LOS_ELASTICITY_LO), ("high -0.25", LOS_ELASTICITY_HI)):
        rows.append(dict(route="filed arbiter: FY25 10-K nights per booking", period="2025",
                         basis=f"LOS elasticity {lab} (bounded, not fitted)",
                         panel="Airbnb, global, filed", n_markets=np.nan, n_pairs=np.nan,
                         wedge_pp=np.nan, capacity_yoy_pct=np.nan, size_pp=np.nan,
                         los_pp=e * d_ln_npb,
                         note=f"3.8 -> 3.7 nights per booking = {d_ln_npb:.2f}%, rounded to 0.1 night"))
    return rows


def npb_geo_check() -> dict:
    """How much of the filed 3.8 -> 3.7 is geographic mix?  Hold each region's own 2025 nights per
    booking fixed and move only the regional nights weights."""
    a = pd.read_csv(REGIONAL_ANNUAL)
    a = a[a.region != "total"]
    npb25 = a[a.year == 2025].set_index("region").alos_nights
    out = {}
    for y in (2024, 2025):
        g = a[a.year == y].set_index("region")
        bookings = (g.nights_m / npb25.reindex(g.index)).sum()
        out[f"npb_geo_only_{y}"] = float(g.nights_m.sum() / bookings)
    out["npb_geo_only_change"] = out["npb_geo_only_2025"] - out["npb_geo_only_2024"]
    out["npb_filed_change"] = FILED_NPB_2025 - FILED_NPB_2024
    out["share_explained_by_geo_pct"] = 100 * out["npb_geo_only_change"] / out["npb_filed_change"]
    return out


# ------------------------------------------------------------------ tables
def routes_table() -> pd.DataFrame:
    r05, rH, rw = route05_year(), h_route(), route05_reweighted()
    dec = pd.read_csv(DEC07)
    rows = [dict(route="10-K annual route (05/07)", period=2023,
                 basis="Inside Airbnb listing dumps, quote-basis hedonic, POOLED sums",
                 panel="Inside Airbnb repo dumps", n_markets=0, n_pairs=0, markets="", window="",
                 weighting="", wedge_pp=np.nan, capacity_yoy_pct=np.nan, d_bedrooms=np.nan,
                 d_mean_log_capacity=np.nan, size_pp=0.0, panel_nights_yoy_pct=np.nan,
                 note="NOT MEASURED: no eligible year-ago pair with date_b in 2023; "
                      "07_assemble.py fills 0.0, so the 2023 term is folded into the plug")]
    for _, y in r05.iterrows():
        rows.append(dict(
            route="10-K annual route (05/07)", period=int(y.year),
            basis="Inside Airbnb listing dumps, quote-basis hedonic, POOLED sums",
            panel="Inside Airbnb repo dumps", n_markets=int(y.n_markets), n_pairs=int(y.n_pairs),
            markets=y.markets, window=f"{y.date_b_min}..{y.date_b_max}",
            weighting="estimated_occupancy_l365d within market; nights-share ACROSS markets, both periods",
            wedge_pp=float(y.size_wedge_pp), capacity_yoy_pct=float(y.cap_per_booked_night_yoy_pct),
            d_bedrooms=float(y.d_bedrooms), d_mean_log_capacity=float(y.d_mean_log_capacity),
            size_pp=float(y.size_mix_pp_quote_basis),
            panel_nights_yoy_pct=float(y.nights_yoy_pct),
            note="this is the term 07_assemble.py carries into the decomposition"))
    for _, y in rw.iterrows():
        rows.append(dict(
            route="10-K annual route, REWEIGHTED", period=int(y.year),
            basis="same pairs, same hedonic, FIXED base-period market weights",
            panel="Inside Airbnb repo dumps", n_markets=int(y.n_markets), n_pairs=int(y.n_pairs),
            markets=y.markets, window="",
            weighting="each market held at its base-period share of panel nights",
            wedge_pp=float(y.wedge_fixedw_pp), capacity_yoy_pct=np.nan,
            d_bedrooms=float(y.d_bed_fixedw), d_mean_log_capacity=float(y.d_ml_fixedw),
            size_pp=float(y.size_pp_fixedw), panel_nights_yoy_pct=float(y.panel_nights_yoy_pct),
            note=(f"all {y.n_pairs} pairs positive: {y.pairs_all_positive_wedge}; "
                  f"between-market part of pooled d_bedrooms {y.d_bed_between:+.5f}")))
    d13 = pd.read_csv(ROOT / "data/processed/adr/13_party_size_adr_quarterly.csv")
    d13 = d13[d13.region == "global"]
    for _, y in rH.iterrows():
        n_rev = d13[d13.quarter.str[-2:] == str(int(y.year))[-2:]].reviews.sum()
        rows.append(dict(
            route="H route (13/H)", period=int(y.year),
            basis="booked capacity per reviewed stay x 0.592 quote-basis elasticity",
            panel="Inside Airbnb reviews, 123 markets", n_markets=123, n_pairs=np.nan,
            markets="123 markets, fixed-2019 weights", window=f"{int(y.year)}Q1..{int(y.year)}Q4",
            weighting="fixed 2019 market shares of reviews; GBV-weighted across quarters",
            wedge_pp=np.nan, capacity_yoy_pct=float(y.cap_yoy_pct),
            d_bedrooms=np.nan, d_mean_log_capacity=np.nan,
            size_pp=float(y.size_pp), los_pp=float(y.los_pp),
            panel_nights_yoy_pct=np.nan,
            note=f"{n_rev:,.0f} reviews in year; I4 series check vs refreshed dumps r 0.97, RMSE 0.062pp"))
    for _, d in dec[dec.year.between(2023, 2025)].iterrows():
        rows.append(dict(route="as filed in 07_full_decomposition.csv", period=int(d.year),
                         basis="05 pooled size + 03 LOS", panel="", n_markets=d.size_n_markets,
                         n_pairs=d.size_n_pairs, markets="", window="", weighting="",
                         wedge_pp=np.nan, capacity_yoy_pct=np.nan, d_bedrooms=np.nan,
                         d_mean_log_capacity=np.nan, size_pp=float(d.size_mix_pp),
                         los_pp=float(d.of_which_los_pp), panel_nights_yoy_pct=np.nan,
                         note=f"within-region ex-FX {d.within_region_exfx_pp:.3f}pp; "
                              f"plug {d.pricing_and_subregional_mix_pp:.3f}pp"))
    rows += arbiter_rows()
    cols = ["route", "period", "basis", "panel", "n_markets", "n_pairs", "markets", "window",
            "weighting", "wedge_pp", "capacity_yoy_pct", "d_bedrooms", "d_mean_log_capacity",
            "size_pp", "los_pp", "panel_nights_yoy_pct", "note"]
    df = pd.DataFrame(rows)
    for c in cols:
        if c not in df:
            df[c] = np.nan
    return df[cols]


def rebased_table() -> pd.DataFrame:
    """The 10-K plug and its implied like-for-like price under each candidate size term.

    plug = within-region ex-FX - size - LOS  (07_assemble.py line 103)
    implied like-for-like price = plug - our sub-regional (country) mix term  (reconcile.py)"""
    dec = pd.read_csv(DEC07).set_index("year")
    rec = pd.read_csv(RECONCILE).set_index("year")
    rH = h_route().set_index("year")
    rw = route05_reweighted().set_index("year")
    rows = []
    for y in (2023, 2024, 2025):
        within = float(dec.loc[y, "within_region_exfx_pp"])
        subgeo = float(rec.loc[y, "our_subgeo_pp"])
        variants = [
            ("A as filed (05 pooled size, 03 LOS)", float(dec.loc[y, "size_mix_pp"]),
             float(dec.loc[y, "of_which_los_pp"])),
            ("B adopted H size, 03 LOS", float(rH.loc[y, "size_pp"]),
             float(dec.loc[y, "of_which_los_pp"])),
            ("C adopted H size and H LOS", float(rH.loc[y, "size_pp"]), float(rH.loc[y, "los_pp"])),
            ("D 05 pairs reweighted, 03 LOS",
             float(rw.loc[y, "size_pp_fixedw"]) if y in rw.index else np.nan,
             float(dec.loc[y, "of_which_los_pp"])),
        ]
        for lab, s, l in variants:
            plug = within - s - l
            rows.append(dict(year=y, variant=lab, within_region_exfx_pp=within,
                             size_pp=s, los_pp=l, plug_pp=plug, our_subgeo_pp=subgeo,
                             implied_lfl_price_pp=plug - subgeo,
                             gbv_wtd_accom_cpi_pct=float(rec.loc[y, "gbv_wtd_accom_cpi_pct"]),
                             price_minus_blend_pp=(plug - subgeo)
                             - float(rec.loc[y, "gbv_wtd_accom_cpi_pct"])))
    df = pd.DataFrame(rows)
    piv = df.pivot(index="variant", columns="year", values="implied_lfl_price_pp")
    df = df.merge(pd.DataFrame({"variant": piv.index,
                                "accel_2025_vs_2024_pp": (piv[2025] - piv[2024]).values}),
                  on="variant", how="left")
    return df


# ------------------------------------------------------------------ the 10-Q search
SEARCH_TERMS = ["basis points", "points of", "Reserve Now", "RNPL", "cancellation", "single fee",
                "service fee", "simplif", "mix shift", "average daily rate", "ADR",
                "constant currency"]
DRIVER_TERMS = ["RNPL", "Reserve Now", "Pay Later", "deferred payment", "flexible payment",
                "cancellation", "single fee", "service fee"]
# the MD&A driver sentences themselves, kept whether or not they name the product, so the CSV
# carries the matched pair: what 2Q26 says about ADR and what 1Q26 says in the same place.
ALWAYS = re.compile(r"the increase in (GBV|Nights and Seats Booked|ADR)|"
                    r"Revenue increased \$|increase in our Average Daily Rate", re.I)
SECTIONS = ["First Quarter Financial Highlights", "Second Quarter Financial Highlights",
            "Macroeconomic and Geopolitical Conditions on our Business",
            "Key Business Metrics and Non-GAAP Financial Measures", "Nights and Seats Booked",
            "Gross Booking Value", "Non-GAAP Financial Measures", "Free Cash Flow Reconciliation",
            "Constant Currency", "Seasonality", "Results of Operations", "Revenue",
            "Liquidity and Capital Resources", "Commitments and Contingencies", "Cash Flows",
            "Quantitative and Qualitative Disclosures About Market Risk"]
MAGNITUDE = re.compile(r"\b\d+(?:\.\d+)?\s*(?:%|percent\b|basis points?\b|points?\b|pts?\b)", re.I)
PRODUCT = re.compile(r"RNPL|Reserve Now|Pay Later|deferred payment|flexible payment|"
                     r"single fee|service fee|cancellation polic", re.I)
DRIVER_CLAIM = re.compile(r"driven (in part )?by|contributed to|primarily due to|"
                          r"benefit(ed)? from|resulted in|results in|impacts? our", re.I)


def html_to_text(path) -> str:
    h = path.read_text(encoding="utf-8", errors="ignore")
    h = re.sub(r"(?is)<(script|style)[^>]*>.*?</\1>", " ", h)
    h = re.sub(r"(?is)<br[^>]*>", "\n", h)
    h = re.sub(r"(?is)</(p|div|tr|td|th|li|h[1-6]|table)>", " ", h)
    t = html.unescape(re.sub(r"(?s)<[^>]+>", " ", h)).replace(" ", " ")
    return re.sub(r"\n\s*\n+", "\n", re.sub(r"[ \t\r\f\v]+", " ", t))


def tenq_sentences() -> tuple[pd.DataFrame, pd.DataFrame]:
    """Sections are taken from the filing's own headings: in the flattened text a heading sits on a
    line of its own, so a short line equal to a known heading opens a section."""
    filings = [("1Q26 10-Q (0001559720-26-000014, abnb-20260331.htm, filed 2026-05-07)", Q1_10Q),
               ("2Q26 10-Q (abnb_2026q2_10q.html, filed 2026-08-06)", Q2_10Q)]
    counts, rows = [], []
    for name, path in filings:
        if not path.exists():
            print(f"  MISSING {path} -- run with --fetch", file=sys.stderr)
            continue
        t = html_to_text(path)
        for term in SEARCH_TERMS + ["Pay Later", "deferred payment", "flexible payment"]:
            counts.append(dict(filing=name, term=term,
                               hits=len(re.findall(re.escape(term), t, re.I))))
        section = "(front matter)"
        for line in t.split("\n"):
            line = line.strip()
            if not line:
                continue
            head = re.sub(r"^Table of Contents\s+", "", line).rstrip(" .:")
            if len(head) <= 80 and head in SECTIONS:
                section = head
                continue
            for s in re.split(r"(?<=[.;:])\s+", line):
                s = s.strip()
                if len(s) < 40:
                    continue
                if not (any(re.search(re.escape(d), s, re.I) for d in DRIVER_TERMS)
                        or ALWAYS.search(s)):
                    continue
                # magnitude_filed answers the brief's question: does a sentence that names the
                # product ALSO carry a number for its contribution?  A revenue growth rate in a
                # sentence that names no product is a number, not a bundle magnitude.
                rows.append(dict(
                    filing=name, section=section, sentence=s,
                    magnitude_filed=("yes" if (PRODUCT.search(s) and MAGNITUDE.search(s))
                                     else "no"),
                    any_number_in_sentence="yes" if MAGNITUDE.search(s) else "no",
                    names_rnpl="yes" if re.search(r"RNPL|Reserve Now|Pay Later", s, re.I) else "no",
                    is_driver_claim="yes" if DRIVER_CLAIM.search(s) else "no",
                    driver_of=("ADR" if re.search(r"\bADR\b|Average Daily Rate", s) else
                               "GBV" if "GBV" in s else
                               "Nights and Seats Booked" if "Nights and Seats Booked" in s else
                               "cash flow / unearned fees" if re.search(r"cash|unearned|FCF", s, re.I)
                               else "definition / risk")))
    return pd.DataFrame(rows), pd.DataFrame(counts)


def fetch_10q(force: bool = False) -> None:
    """EDGAR fetch, guarded.  Two requests: the filing index, then the primary document."""
    import urllib.request
    if Q1_10Q.exists() and not force:
        print(f"  {Q1_10Q.name} already on disk; skipping fetch (use --fetch to force)")
        return
    for url, dest in ((EDGAR_DIR, None), (EDGAR_PRIMARY, Q1_10Q)):
        req = urllib.request.Request(url, headers={"User-Agent": UA,
                                                   "Accept-Encoding": "gzip, deflate"})
        with urllib.request.urlopen(req, timeout=120) as r:
            body = r.read()
        if dest is not None:
            dest.parent.mkdir(parents=True, exist_ok=True)
            dest.write_bytes(body)
            print(f"  fetched {url} -> {dest} ({len(body):,} bytes)")
        else:
            print(f"  fetched index {url} ({len(body):,} bytes); "
                  f"primary document = {EDGAR_PRIMARY.rsplit('/', 1)[1]}")


# ------------------------------------------------------------------ main
def main(argv=None) -> int:
    argv = sys.argv[1:] if argv is None else argv
    if "--fetch" in argv:
        fetch_10q(force=True)

    OUT.mkdir(parents=True, exist_ok=True)
    pd.set_option("display.width", 220)
    pd.set_option("display.max_columns", 40)

    b_bed, b_lacc = hedonic_coefs()
    print(f"hedonic, quote basis: bedrooms {b_bed:.4f}, log capacity {b_lacc:.4f} "
          f"(shared by BOTH routes -- the disagreement is not a price basis)")

    print("\n== 1. the two routes, 2023-2025 ==")
    r05, rH = route05_year().set_index("year"), h_route().set_index("year")
    for y in (2023, 2024, 2025):
        hv = float(rH.loc[y, "size_pp"])
        if y in r05.index:
            v = float(r05.loc[y, "size_mix_pp_quote_basis"])
            src = f"{int(r05.loc[y, 'n_pairs'])} pairs / {int(r05.loc[y, 'n_markets'])} markets: {r05.loc[y, 'markets']}"
        else:
            v, src = 0.0, "NOT MEASURED, 07 fills 0.0"
        print(f"  {y}  05/07 {v:+.3f}pp ({src})   H {hv:+.3f}pp (123 markets)   gap {hv - v:+.3f}pp")

    print("\n== 2. the 05 route's own pairs, reweighted ==")
    rw = route05_reweighted()
    print(rw[["year", "n_pairs", "n_markets", "pairs_all_positive_wedge", "wedge_pooled_pp",
              "wedge_fixedw_pp", "size_pp_pooled", "size_pp_fixedw", "d_bed_between",
              "panel_nights_yoy_pct"]].round(4).to_string(index=False))
    print("\n  2025 panel weight shift (this is the whole mechanism):")
    print(weight_shift_2025().round(4).to_string(index=False))

    print("\n== 3. the filed arbiter ==")
    print(bedroom_elasticity().round(4).to_string(index=False))
    arb = pd.DataFrame(arbiter_rows())
    print(arb[["period", "basis", "size_pp", "los_pp"]].round(3).to_string(index=False))
    g = npb_geo_check()
    print(f"  nights per booking, geo-mix-only move {g['npb_geo_only_change']:+.4f} nights against "
          f"a filed {g['npb_filed_change']:+.2f}: geo explains {g['share_explained_by_geo_pct']:.0f}%")

    print("\n== 4. the rebased plug ==")
    reb = rebased_table()
    piv = reb.pivot(index="variant", columns="year", values="implied_lfl_price_pp")
    print(piv.round(3).to_string())

    routes = routes_table()
    routes.to_csv(OUT / "sizemix_routes.csv", index=False)
    reb.to_csv(OUT / "sizemix_rebased_plug.csv", index=False)
    print(f"\nwrote {OUT / 'sizemix_routes.csv'} ({len(routes)} rows)")
    print(f"wrote {OUT / 'sizemix_rebased_plug.csv'} ({len(reb)} rows)")

    print("\n== 5. the 10-Q search ==")
    sent, counts = tenq_sentences()
    if len(counts):
        print(counts.pivot(index="term", columns="filing", values="hits").to_string())
    if len(sent):
        sent.to_csv(OUT / "sizemix_10q_sentences.csv", index=False)
        print(f"wrote {OUT / 'sizemix_10q_sentences.csv'} ({len(sent)} rows); "
              f"any magnitude filed: {(sent.magnitude_filed == 'yes').any()}")
        for _, r in sent.iterrows():
            print(f"  [{r.filing.split(' ')[0]} | {r.section} | mag {r.magnitude_filed}] {r.sentence[:200]}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
