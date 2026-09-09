"""05. Unit-size mix: an independent test of Airbnb's "half of ADR growth is size" claim.

The question
  Airbnb disclosed exactly one data point on unit size (2Q26 letter): "Bedroom Nights
  Booked" -- nights booked multiplied by the listing's bedroom count -- "grew over 12%"
  against Nights and Seats Booked +10%, with more than 1 billion bedroom nights over the
  trailing twelve months against ~560m LTM nights. That is a ~+2pp wedge and it is the
  entire public evidence base for the claim that roughly half of ADR growth is the mix of
  bigger homes rather than price. Workstream 03 leaves size and like-for-like price fused
  in one +3.6pp residual for 2025. This step splits them.

What is built
  A booking-weighted size distribution from Inside Airbnb listing dumps, its year-over-year
  change, and the implied ADR contribution through the existing hedonic coefficients.

The one methodological point that matters
  `estimated_occupancy_l365d` is ESTIMATED NIGHTS BOOKED over the last 365 days -- a count
  bounded at 0.7*365 = 255.5 -- not an occupancy percentage. Weighting listings by it turns
  a supply-side size distribution into an approximation of a BOOKED size distribution, which
  is what ADR actually reflects. A supply-weighted mean answers "what is listed"; ADR is set
  by "what is sold", and studios and large houses sell at very different rates.
  Inside Airbnb only publishes the field from the 2025 dumps onward. For the 19 earlier
  dumps it is reconstructed with Inside Airbnb's own occupancy model,
  reviews_ltm/0.5 * max(3, min_nights) capped at 0.7*365. Measured against the published
  field on the dumps that carry both, it gives a mean correlation of 0.987 and 71% exact
  agreement (0.9997 and 88% on the Rome Aug 2026 dump alone); the residual is the model's
  own rounding. The figures are recomputed on every run and written to the evidence file.

Why the wedge survives the problems that broke earlier workstreams
  The disclosed statistic is a RATIO OF GROWTH RATES: bedroom-nights growth minus nights
  growth. Both legs scale with scrape coverage, so a partial-scope Inside Airbnb dump --
  which WS21 showed is a roughly uniform subsample, not a geographic truncation -- largely
  cancels out of the wedge even though it destroys any level series. That is tested here
  rather than assumed (partial_scope_probe, written to the evidence file), and the repo's
  `pair_eligible` convention is applied on top regardless.
  The 2026 price-basis break (listed nightly rate -> fee-inclusive quote per night) does not
  touch the size series at all: no price field is read from the dumps. It does bear on the
  hedonic coefficients, which were fitted separately per basis, so both bases are carried.

The `bedrooms` field is not stable, and that had to be fixed before anything else
  Inside Airbnb's population of `bedrooms` changes regime inside the test window. In the
  London dumps the field is non-null on 99.8% of listings in Jan 2026 and 68.7% in Aug 2026.
  Almost all of the swing is PRIVATE ROOMS: 99.9% of London private rooms carry a bedroom
  count in Jan 2026 (modal value 1, mean 1.07) against 15% in Aug 2026. Entire homes are far
  steadier (95.7-99.9% in London) but not fixed either, and two dumps -- Paris 2023-12-12 and
  Rome 2023-12-15 -- carry the field on 0.05% and 0.11% of entire homes, i.e. not at all.
  A naive fill therefore manufactures a size trend out of a metadata change. Three defences:
    - a private/shared/hotel room is counted as exactly one bedroom whether or not the field
      is populated, which is what the populated values overwhelmingly say anyway;
    - an entire home with a missing count is imputed from the within-dump median bedroom
      count at its own guest capacity, so the fill tracks the dump it came from;
    - dumps below 80% entire-home coverage are dropped, and a year-ago pair whose two
      endpoints differ by more than 10pp of entire-home coverage is dropped.
  The uncorrected hedonic-style measure is still computed and reported as a REJECTED
  variant, because the size of the artefact is itself the finding.

Size measures, and why there are three
  bedrooms_abnb  Airbnb's own metric convention, built coverage-robustly as above. This is
                 the series comparable to "Bedroom Nights Booked".
  bedrooms_f     The definition used verbatim by the existing hedonic regression
                 (bedrooms filled with round(min(accommodates,8)/2), clipped to [0.5, 8]).
                 Carried for comparability only: it is the measure the private-room coverage
                 regime contaminates, and it is NOT used for the headline conversion.
  accommodates   Guest capacity. 100% populated in every dump, so it is the one size measure
                 with no imputation anywhere, immune to all of the above, and it is the
                 measure the UK Lighthouse / VisitBritain corroboration is stated in.

Outputs
  data/processed/adr/05_size_mix_panel.csv    one row per dump: booking-weighted and
                                              unweighted size, scope flags, weight provenance
  data/processed/adr/05_size_mix_summary.csv  the year-over-year wedge by city, region,
                                              quarter and panel, and the ADR effect in pp
  data/processed/adr/05_size_mix_pairs.csv    per-pair audit trail behind the summary
  data/processed/adr/05_size_evidence.csv     every sourced figure used or produced here

Run
  py -3.13 analysis/src/adr/05_size_mix.py            full rebuild from 196 dumps (~5 min)
  py -3.13 analysis/src/adr/05_size_mix.py --cache    reuse the per-dump aggregate cache
"""

import glob
import os
import re
import sys
import time

import numpy as np
import pandas as pd

RAW = "data/raw/inside_airbnb"
OD = "data/raw/theo_onedrive/AIRBNB DATA/raw/inside_airbnb"
OUT = "data/processed/adr"
SNAP = "data/processed/inside_airbnb_city_snapshots.csv"
HED = "data/processed/overnight/06_wtp_hedonic_coefs.csv"
CACHE = "data/processed/adr/.05_size_cache.csv"

# Lowercase codes, matching 01_regional_annual.csv and 03_annual_decomposition.csv. Also
# avoids the trap that the string "NA" is read back from CSV as a missing value by default.
REGION = {"new-york-city": "na", "los-angeles": "na", "chicago": "na", "austin": "na",
          "nashville": "na", "new-orleans": "na", "san-diego": "na", "paris": "emea",
          "london": "emea", "barcelona": "emea", "rome": "emea", "sydney": "apac",
          "mexico-city": "latam"}
# ABNB reports four regions; the OneDrive pull is organised by country.
COUNTRY_REGION = {"argentina": "latam", "brazil": "latam", "chile": "latam", "belize": "latam",
                  "mexico": "latam", "australia": "apac", "china": "apac", "canada": "na",
                  "united-states": "na", "austria": "emea", "belgium": "emea", "denmark": "emea",
                  "czech-republic": "emea", "france": "emea", "germany": "emea", "greece": "emea",
                  "ireland": "emea", "italy": "emea", "spain": "emea", "united-kingdom": "emea"}

USE = ["room_type", "accommodates", "bedrooms", "minimum_nights", "number_of_reviews_ltm",
       "estimated_occupancy_l365d"]
CAP = 0.7 * 365            # Inside Airbnb's own ceiling on estimated nights booked
YOY_LO, YOY_HI = 300, 430  # days that count as a "year-ago" pair
EH_COV_MIN = 0.80          # a dump must declare bedrooms on >=80% of its whole homes
EH_COV_DRIFT = 0.10        # and the two endpoints of a pair must be within 10pp of each other


def log(m):
    print(f"{time.strftime('%H:%M:%S')} {m}", flush=True)


# ------------------------------------------------------------------ size measures
def est_nights(df):
    """Inside Airbnb's occupancy model, used to backfill estimated_occupancy_l365d."""
    per_stay = np.maximum(3, df["minimum_nights"].fillna(1).clip(upper=30))
    return np.minimum(df["number_of_reviews_ltm"].fillna(0) / 0.5 * per_stay, CAP)


def size_fields(df):
    """The size measures. Every imputation is explicit, self-contained within the dump, and
    built so that a change in Inside Airbnb's `bedrooms` population regime cannot move it."""
    rt = df["room_type"]
    home = rt.eq("Entire home/apt") | rt.eq("Hotel room")
    entire = rt.eq("Entire home/apt")
    bed = pd.to_numeric(df["bedrooms"], errors="coerce")
    acc = pd.to_numeric(df["accommodates"], errors="coerce")

    # -- Airbnb-metric convention, made robust to the coverage regime.
    # A private or shared room is one bedroom. That is not an assumption of convenience: in
    # the London Jan 2026 dump, where the field IS populated for 99.9% of private rooms, the
    # modal value is 1 and the mean 1.07. Pinning it removes the entire private-room
    # coverage swing from the series.
    b = pd.Series(np.nan, index=df.index, dtype=float)
    b[~home] = 1.0
    # A whole home declaring zero bedrooms is a studio: one bedroom, not imputed.
    b[home & bed.eq(0)] = 1.0
    obs = bed.where(home & bed.gt(0))
    b[home & bed.gt(0)] = obs[home & bed.gt(0)]
    # Missing whole-home counts: the within-dump median bedroom count at the same guest
    # capacity, so the fill is drawn from the dump it belongs to rather than a global rule.
    med = obs.groupby(acc.fillna(-1)).transform("median")
    fallback = (acc.clip(upper=8) / 2).round().clip(lower=1)
    b[home & b.isna()] = med[home & b.isna()].fillna(fallback[home & b.isna()])
    b_abnb = b.fillna(1.0)

    # -- The hedonic's own definition, copied verbatim from 06_wtp_hedonics.py. Reported for
    # comparability and REJECTED for the headline conversion: its acc/2 fallback fires on
    # 85% of private rooms in Aug 2026 and on 0.1% of them in Jan 2026, so it moves with the
    # metadata regime rather than with the market.
    b_f = bed.fillna((acc.clip(upper=8) / 2).round()).clip(0.5, 8)

    # -- Complete cases: whole homes that actually declare a count. No imputation at all,
    # hence fully neutral to coverage, at the cost of dropping private rooms entirely.
    b_cc = bed.where(entire & bed.gt(0))

    return b_abnb, b_f, b_cc, acc, home, entire


def booking_weight(df):
    """Estimated nights booked over the trailing 365 days, per listing."""
    disclosed = pd.to_numeric(df["estimated_occupancy_l365d"], errors="coerce")
    have = float(disclosed.notna().mean())
    if have >= 0.5:
        return disclosed.fillna(0).clip(0, CAP), "disclosed", have
    return est_nights(df), "reconstructed_ia_model", have


def size_row(df, key):
    """Booking-weighted and unweighted size aggregates for one dump."""
    b_abnb, b_f, b_cc, acc, home, entire = size_fields(df)
    w, wsrc, have = booking_weight(df)

    lacc = np.log(acc.clip(lower=1))
    ok = acc.notna()

    def wm(x):
        m = ok & x.notna()
        tot = w[m].sum()
        return float((w[m] * x[m]).sum() / tot) if tot > 0 else np.nan

    def um(x):
        m = ok & x.notna()
        return float(x[m].mean()) if m.any() else np.nan

    r = dict(key)
    r.update(
        listings=len(df),
        listings_with_bookings=int((w > 0).sum()),
        weight_source=wsrc,
        occ_field_nonnull_share=round(have, 4),
        bedrooms_field_nonnull_share=round(float(pd.to_numeric(df["bedrooms"], errors="coerce").notna().mean()), 4),
        # the gate: whole-home coverage is what the imputation actually depends on
        bedrooms_eh_nonnull_share=round(float(pd.to_numeric(df["bedrooms"], errors="coerce")[entire].notna().mean()), 4)
        if entire.any() else np.nan,
        bedrooms_priv_nonnull_share=round(float(pd.to_numeric(df["bedrooms"], errors="coerce")[~home].notna().mean()), 4)
        if (~home).any() else np.nan,
        est_nights_ltm=float(w.sum()),
        # the disclosure analogue: nights x bedroom count, summed
        bedroom_nights_ltm=float((w * b_abnb).sum()),
        bedrooms_per_booked_night=wm(b_abnb),
        bedrooms_per_listing=um(b_abnb),
        bedrooms_cc_per_booked_night=wm(b_cc),      # complete cases, whole homes only
        bedrooms_f_per_booked_night=wm(b_f),        # contaminated variant, reported not used
        bedrooms_f_per_listing=um(b_f),
        capacity_per_booked_night=wm(acc),
        capacity_per_listing=um(acc),
        mean_log_capacity_booked=wm(lacc),
        mean_log_capacity_listing=um(lacc),
        share_bed_ge3_booked=wm((b_abnb >= 3).astype(float)),
        share_bed_ge4_booked=wm((b_abnb >= 4).astype(float)),
        share_cap_ge6_booked=wm((acc >= 6).astype(float)),
        share_cap_le2_booked=wm((acc <= 2).astype(float)),
        share_cap_ge6_listing=um((acc >= 6).astype(float)),
        share_cap_le2_listing=um((acc <= 2).astype(float)),
        share_entire_booked=wm(home.astype(float)),
        share_entire_listing=um(home.astype(float)),
    )
    return r


# ------------------------------------------------------------------ ingest
def repo_dumps():
    out = []
    for f in sorted(glob.glob(f"{RAW}/*_listings.parquet")):
        m = re.match(r"(.+)_(\d{4}-\d{2}-\d{2})_listings\.parquet", os.path.basename(f))
        out.append((f, m.group(1), m.group(2)))
    return out


def onedrive_dumps():
    """<country>/<region>/<market>/<date>/listings.csv.gz -- one vintage per market."""
    out = []
    for f in sorted(glob.glob(f"{OD}/*/*/*/*/listings.csv.gz")):
        p = f.replace("\\", "/").split("/")
        out.append((f, p[-5], p[-4], p[-3], p[-2]))
    return out


def build_panel():
    rows = []
    for f, city, d in repo_dumps():
        df = pd.read_parquet(f, columns=USE)
        rows.append(size_row(df, dict(source="repo_inside_airbnb", market=city,
                                      country="", subregion="", dump_date=d,
                                      abnb_region=REGION.get(city, "?"))))
    log(f"repo dumps: {len(rows)}")

    n0 = len(rows)
    for f, country, subregion, market, d in onedrive_dumps():
        try:
            head = pd.read_csv(f, nrows=0).columns
            df = pd.read_csv(f, usecols=[c for c in USE if c in head], low_memory=False)
            for c in USE:
                if c not in df:
                    df[c] = np.nan
        except Exception as e:                       # a corrupt member must not kill the run
            log(f"  SKIP {country}/{market} {d}: {type(e).__name__}: {e}"[:160])
            continue
        rows.append(size_row(df, dict(source="onedrive_inside_airbnb", market=market,
                                      country=country, subregion=subregion, dump_date=d,
                                      abnb_region=COUNTRY_REGION.get(country, "?"))))
    log(f"onedrive dumps: {len(rows) - n0}")

    p = pd.DataFrame(rows)
    p["dump_date"] = pd.to_datetime(p.dump_date)
    return p.sort_values(["source", "market", "dump_date"]).reset_index(drop=True)


def attach_scope(p):
    """WS21 scope flags, joined by city-date. The OneDrive markets have a single dump each,
    so coverage cannot be judged at all -- they are marked unverifiable, never silently
    clean, and they never enter a year-over-year pair."""
    s = pd.read_csv(SNAP, usecols=["city", "dump_date", "listings", "scope_vs_peer",
                                   "partial_scope", "partial_scope_pit",
                                   "partial_scope_pit_long", "scope_unverified"])
    s["dump_date"] = pd.to_datetime(s.dump_date)
    p = p.merge(s.rename(columns={"city": "market", "listings": "listings_snapshot"}),
                on=["market", "dump_date"], how="left")
    for c in ("partial_scope", "partial_scope_pit", "partial_scope_pit_long"):
        p[c] = p[c].astype("boolean")
    p["scope_unverified"] = p.scope_unverified.astype("boolean").fillna(
        p.source.eq("onedrive_inside_airbnb"))
    return p


# ------------------------------------------------------------------ year-over-year wedge
def pairs(p):
    """Year-ago pairs within a market."""
    out = []
    r = p[p.source.eq("repo_inside_airbnb")]
    for mkt, g in r.groupby("market"):
        g = g.sort_values("dump_date").reset_index(drop=True)
        for j in range(len(g)):
            b = g.iloc[j]
            gap = (b.dump_date - g.dump_date).dt.days
            cand = g[(gap >= YOY_LO) & (gap <= YOY_HI)]
            if cand.empty:
                continue
            a = cand.iloc[int((b.dump_date - cand.dump_date).dt.days.sub(365).abs().values.argmin())]
            row = dict(
                market=mkt, abnb_region=b.abnb_region, date_a=a.dump_date, date_b=b.dump_date,
                days=(b.dump_date - a.dump_date).days,
                weight_source_a=a.weight_source, weight_source_b=b.weight_source,
                listings_a=a.listings, listings_b=b.listings,
                est_nights_a=a.est_nights_ltm, est_nights_b=b.est_nights_ltm,
                bedroom_nights_a=a.bedroom_nights_ltm, bedroom_nights_b=b.bedroom_nights_ltm,
                bed_per_night_a=a.bedrooms_per_booked_night, bed_per_night_b=b.bedrooms_per_booked_night,
                bed_cc_per_night_a=a.bedrooms_cc_per_booked_night, bed_cc_per_night_b=b.bedrooms_cc_per_booked_night,
                bed_f_per_night_a=a.bedrooms_f_per_booked_night, bed_f_per_night_b=b.bedrooms_f_per_booked_night,
                eh_cov_a=a.bedrooms_eh_nonnull_share, eh_cov_b=b.bedrooms_eh_nonnull_share,
                cap_per_night_a=a.capacity_per_booked_night, cap_per_night_b=b.capacity_per_booked_night,
                mlogcap_a=a.mean_log_capacity_booked, mlogcap_b=b.mean_log_capacity_booked,
                share_entire_a=a.share_entire_booked, share_entire_b=b.share_entire_booked,
                share_cap_ge6_a=a.share_cap_ge6_booked, share_cap_ge6_b=b.share_cap_ge6_booked,
                share_cap_le2_a=a.share_cap_le2_booked, share_cap_le2_b=b.share_cap_le2_booked,
                bed_per_listing_a=a.bedrooms_per_listing, bed_per_listing_b=b.bedrooms_per_listing,
                cap_per_listing_a=a.capacity_per_listing, cap_per_listing_b=b.capacity_per_listing)
            bad_a = None if pd.isna(a.partial_scope) else bool(a.partial_scope)
            bad_b = None if pd.isna(b.partial_scope) else bool(b.partial_scope)
            pit_a = None if pd.isna(a.partial_scope_pit) else bool(a.partial_scope_pit or a.partial_scope_pit_long)
            pit_b = None if pd.isna(b.partial_scope_pit) else bool(b.partial_scope_pit or b.partial_scope_pit_long)
            # The bedrooms-field gate comes FIRST: a metadata regime change is a worse
            # contaminant here than a partial scrape, because it moves the size measure
            # directly rather than only the level counts.
            ca, cb = a.bedrooms_eh_nonnull_share, b.bedrooms_eh_nonnull_share
            reason = ("bedrooms_field_absent_a" if not (ca >= EH_COV_MIN)
                      else "bedrooms_field_absent_b" if not (cb >= EH_COV_MIN)
                      else "bedrooms_coverage_shift" if abs(cb - ca) > EH_COV_DRIFT
                      else "scope_missing" if bad_a is None or bad_b is None
                      else "partial_scope_a" if bad_a else "partial_scope_b" if bad_b else "")
            row.update(partial_a=bad_a, partial_b=bad_b, eh_cov_drift=cb - ca,
                       pair_eligible=(reason == ""), exclusion_reason=reason,
                       pair_eligible_pit=(reason == "" and pit_a is False and pit_b is False))
            out.append(row)
    q = pd.DataFrame(out)
    q["nights_yoy_pct"] = (q.est_nights_b / q.est_nights_a - 1) * 100
    q["bedroom_nights_yoy_pct"] = (q.bedroom_nights_b / q.bedroom_nights_a - 1) * 100
    q["size_wedge_pp"] = q.bedroom_nights_yoy_pct - q.nights_yoy_pct
    q["bed_per_night_yoy_pct"] = (q.bed_per_night_b / q.bed_per_night_a - 1) * 100
    q["cap_per_night_yoy_pct"] = (q.cap_per_night_b / q.cap_per_night_a - 1) * 100
    q["bed_per_listing_yoy_pct"] = (q.bed_per_listing_b / q.bed_per_listing_a - 1) * 100
    q["cap_per_listing_yoy_pct"] = (q.cap_per_listing_b / q.cap_per_listing_a - 1) * 100
    q["bed_cc_per_night_yoy_pct"] = (q.bed_cc_per_night_b / q.bed_cc_per_night_a - 1) * 100
    q["d_bedrooms"] = q.bed_per_night_b - q.bed_per_night_a          # used for the ADR conversion
    q["d_bedrooms_f"] = q.bed_f_per_night_b - q.bed_f_per_night_a    # contaminated, reported only
    q["d_mean_log_cap"] = q.mlogcap_b - q.mlogcap_a
    q["abnb_quarter"] = q.date_b.dt.quarter.astype(str) + "Q" + q.date_b.dt.strftime("%y")
    q["year_b"] = q.date_b.dt.year
    return q


# ------------------------------------------------------------------ hedonic conversion
def hedonic():
    h = pd.read_csv(HED)
    out = {}
    for basis, g in h.groupby("price_basis"):
        g = g.set_index("term")
        out[basis] = dict(b_bed=float(g.loc["bedrooms_f", "coef"]), se_bed=float(g.loc["bedrooms_f", "se"]),
                          b_lacc=float(g.loc["lacc", "coef"]), se_lacc=float(g.loc["lacc", "se"]),
                          b_priv=float(g.loc['C(room_type, Treatment("Entire home/apt"))[T.Private room]', "coef"]),
                          n=int(g.loc["lacc", "n"]))
    return out


def size_pp(d_bed, d_mlogcap, c):
    """Semi-log hedonic: log p = ... + b_bed*bedrooms_f + b_lacc*log(accommodates) + ...
    A mix shift of d_bed bedrooms and d_mlogcap in mean log capacity moves log ADR by the
    sum of the two terms. Room type is a separate control in that regression, so this is
    unit size only and excludes any private-room / entire-home shift."""
    return (np.exp(c["b_bed"] * d_bed + c["b_lacc"] * d_mlogcap) - 1) * 100


# ------------------------------------------------------------------ aggregation
def agg(q, keys, label, hc):
    """Nights-weighted aggregation, which is how Airbnb's own global metric is formed: sum
    bedroom-nights and nights over markets, then take growth rates of the sums."""
    rows = []
    for k, g in q.groupby(keys, dropna=False):
        k = k if isinstance(k, tuple) else (k,)
        na, nb = g.est_nights_a.sum(), g.est_nights_b.sum()
        ba, bb = g.bedroom_nights_a.sum(), g.bedroom_nights_b.sum()
        nyoy, byoy = (nb / na - 1) * 100, (bb / ba - 1) * 100
        wa, wb = g.est_nights_a, g.est_nights_b
        d_bed = (bb / nb) - (ba / na)          # coverage-robust bedrooms per booked night
        d_bed_f = ((g.bed_f_per_night_b * wb).sum() / wb.sum()
                   - (g.bed_f_per_night_a * wa).sum() / wa.sum())
        d_ml = ((g.mlogcap_b * wb).sum() / wb.sum() - (g.mlogcap_a * wa).sum() / wa.sum())
        cap_a = (g.cap_per_night_a * wa).sum() / wa.sum()
        cap_b = (g.cap_per_night_b * wb).sum() / wb.sum()
        cc_a = (g.bed_cc_per_night_a * wa).sum() / wa.sum()
        cc_b = (g.bed_cc_per_night_b * wb).sum() / wb.sum()
        r = dict(zip(["scope"] + list(keys), (label,) + k))
        r.update(n_pairs=len(g), n_markets=int(g.market.nunique()),
                 markets="|".join(sorted(g.market.unique())),
                 date_b_min=str(g.date_b.min().date()), date_b_max=str(g.date_b.max().date()),
                 est_nights_a=na, est_nights_b=nb, bedroom_nights_a=ba, bedroom_nights_b=bb,
                 nights_yoy_pct=nyoy, bedroom_nights_yoy_pct=byoy, size_wedge_pp=byoy - nyoy,
                 bed_per_booked_night_a=ba / na, bed_per_booked_night_b=bb / nb,
                 cap_per_booked_night_a=cap_a, cap_per_booked_night_b=cap_b,
                 cap_per_booked_night_yoy_pct=(cap_b / cap_a - 1) * 100,
                 bed_cc_per_booked_night_a=cc_a, bed_cc_per_booked_night_b=cc_b,
                 bed_cc_yoy_pct=(cc_b / cc_a - 1) * 100,
                 wedge_pp_market_min=g.size_wedge_pp.min(), wedge_pp_market_max=g.size_wedge_pp.max(),
                 d_bedrooms=d_bed, d_mean_log_capacity=d_ml, d_bedrooms_f_rejected=d_bed_f,
                 size_mix_pp_quote_basis=size_pp(d_bed, d_ml, hc["quote_per_night"]),
                 size_mix_pp_listed_basis=size_pp(d_bed, d_ml, hc["listed_nightly"]),
                 size_mix_pp_bedrooms_only_quote=size_pp(d_bed, 0.0, hc["quote_per_night"]),
                 size_mix_pp_capacity_only_quote=size_pp(0.0, d_ml, hc["quote_per_night"]),
                 # what the contaminated hedonic-native measure would have said
                 size_mix_pp_quote_rejected_bedrooms_f=size_pp(d_bed_f, d_ml, hc["quote_per_night"]))
        rows.append(r)
    return pd.DataFrame(rows)


# ------------------------------------------------------------------ checks and controls
def occ_validation():
    """Does the reconstructed weight reproduce the published field? 19 of 168 repo dumps
    predate estimated_occupancy_l365d and are backfilled, so this has to be measured."""
    rs, tot, exact, n = [], 0, 0, 0
    for f, city, d in repo_dumps()[::7]:            # every 7th dump
        df = pd.read_parquet(f, columns=USE)
        o = pd.to_numeric(df.estimated_occupancy_l365d, errors="coerce")
        if o.notna().mean() < 0.5:
            continue
        e = est_nights(df)
        m = o.notna()
        rs.append(np.corrcoef(e[m], o[m])[0, 1])
        exact += int((e[m].round(3) == o[m].round(3)).sum())
        tot += int(m.sum())
        n += 1
    return float(np.mean(rs)), exact / tot, tot, n


def partial_scope_probe(p):
    """WS21 showed partial scrapes are uniform subsamples, not geographic truncations. If
    that holds, the size RATIO is close to unbiased in a partial dump even though the level
    count is not. Tested by comparing each partial dump's bedrooms-per-booked-night with its
    own city's clean dumps."""
    r = p[p.source.eq("repo_inside_airbnb") & p.partial_scope.notna()].copy()
    r["partial_scope"] = r.partial_scope.astype(bool)
    clean = r[~r.partial_scope].groupby("market").bedrooms_per_booked_night.agg(["mean", "std"])
    bad = r[r.partial_scope].merge(clean, left_on="market", right_index=True, how="left")
    bad = bad[bad["std"].notna() & bad["std"].gt(0)]
    ratio = bad.bedrooms_per_booked_night / bad["mean"]
    # z is reported but is not the headline: a city with only two clean dumps has a tiny
    # denominator, which produces absurd z values on a 1% level difference.
    z = (bad.bedrooms_per_booked_night - bad["mean"]) / bad["std"]
    return dict(n_partial=len(bad), median_ratio=float(ratio.median()),
                mean_ratio=float(ratio.mean()), p10_ratio=float(ratio.quantile(0.10)),
                p90_ratio=float(ratio.quantile(0.90)), median_z=float(z.median()),
                max_abs_z=float(z.abs().max()))


def within_between(q, lo, hi):
    """Is the wedge guests moving onto bigger homes, or the listing base drifting bigger?

    For every eligible pair in the window, the wedge is recomputed on the listings present
    in BOTH dumps. Those listings cannot change the size of the housing stock, so whatever
    wedge they show is booking volume reallocating across sizes -- demand. The difference
    between the full wedge and the matched wedge is what entry and exit of listings did.
    Both belong in ADR; the split says which story the number is telling."""
    sel = q[q.pair_eligible & q.date_b.ge(lo) & q.date_b.le(hi)]
    cache, rows = {}, []

    def load(market, d):
        k = (market, d)
        if k not in cache:
            df = pd.read_parquet(f"{RAW}/{market}_{d}_listings.parquet", columns=["id"] + USE)
            b_abnb, *_ = size_fields(df)
            w, _, _ = booking_weight(df)
            cache[k] = (pd.DataFrame({"id": df["id"], "w": w, "bw": w * b_abnb})
                        .groupby("id", as_index=True).sum())
        return cache[k]

    for r in sel.itertuples():
        A = load(r.market, r.date_a.strftime("%Y-%m-%d"))
        B = load(r.market, r.date_b.strftime("%Y-%m-%d"))
        m = A.index.intersection(B.index)
        Am, Bm = A.loc[m], B.loc[m]
        if Am.w.sum() <= 0 or Bm.w.sum() <= 0:
            continue
        wm = ((Bm.bw.sum() / Bm.w.sum()) / (Am.bw.sum() / Am.w.sum()) - 1) * 100
        tot = ((B.bw.sum() / B.w.sum()) / (A.bw.sum() / A.w.sum()) - 1) * 100
        rows.append(dict(market=r.market, abnb_region=r.abnb_region,
                         date_a=r.date_a, date_b=r.date_b,
                         matched_listings=len(m), matched_share_nights_b=Bm.w.sum() / B.w.sum(),
                         wedge_total_pp=tot, wedge_matched_pp=wm, wedge_churn_pp=tot - wm,
                         nights_b=B.w.sum(), nights_a=A.w.sum()))
    d = pd.DataFrame(rows)
    if not len(d):
        return d, {}
    wa, wb = d.nights_a, d.nights_b
    summ = dict(n_pairs=len(d), n_markets=int(d.market.nunique()),
                matched_share=float((d.matched_share_nights_b * wb).sum() / wb.sum()),
                wedge_total_pp=float((d.wedge_total_pp * wb).sum() / wb.sum()),
                wedge_matched_pp=float((d.wedge_matched_pp * wb).sum() / wb.sum()),
                wedge_churn_pp=float((d.wedge_churn_pp * wb).sum() / wb.sum()))
    return d, summ


def cc_test():
    """Common Crawl listing panel as a longer size series. Prior workstreams found it is a
    supply-quality panel; tested here for a size signal rather than assumed dead."""
    f = "data/processed/cc_listing_panel.csv"
    if not os.path.exists(f):
        return None, None
    d = pd.read_csv(f, low_memory=False)
    a = d[d.side.eq("a")].copy()                    # first observation = the crawl snapshot
    a = a[a.person_capacity.notna()]
    g = a.groupby("year").person_capacity.agg(["size", "mean", "std"])
    g["se"] = g["std"] / np.sqrt(g["size"])
    b = a[a.region.notna()]
    X = pd.get_dummies(b.region, drop_first=True, dtype=float)
    X["year"] = b.year.astype(float) - 2021
    X.insert(0, "const", 1.0)
    y = b.person_capacity.values.astype(float)
    beta, *_ = np.linalg.lstsq(X.values, y, rcond=None)
    resid = y - X.values @ beta
    dof = len(b) - X.shape[1]
    cov = (resid @ resid) / dof * np.linalg.pinv(X.values.T @ X.values)
    k = list(X.columns).index("year")
    return g, (float(beta[k]), float(np.sqrt(cov[k, k])), int(len(b)))


def region_levels(p, mask, label):
    g = p[mask]
    if not len(g):
        return pd.DataFrame()
    return g.groupby("abnb_region").apply(
        lambda x: pd.Series({
            "bed_per_booked_night": x.bedroom_nights_ltm.sum() / x.est_nights_ltm.sum(),
            "cap_per_booked_night": np.average(x.capacity_per_booked_night, weights=x.est_nights_ltm),
            "share_cap_ge6_booked": np.average(x.share_cap_ge6_booked, weights=x.est_nights_ltm),
            "share_entire_booked": np.average(x.share_entire_booked, weights=x.est_nights_ltm),
            "n_dumps": len(x), "leg": label}), include_groups=False)


# ------------------------------------------------------------------ main
def main():
    os.makedirs(OUT, exist_ok=True)
    hc = hedonic()

    if "--cache" in sys.argv and os.path.exists(CACHE):
        p = pd.read_csv(CACHE, parse_dates=["dump_date"], keep_default_na=True,
                        dtype={"abnb_region": "string"})
        log(f"panel from cache: {len(p)} dumps")
    else:
        p = build_panel()
        p.to_csv(CACHE, index=False)
    p = attach_scope(p)

    p.assign(dump_date=p.dump_date.dt.strftime("%Y-%m-%d")).to_csv(
        f"{OUT}/05_size_mix_panel.csv", index=False)
    log(f"panel written: {len(p)} dumps, {p.market.nunique()} markets; "
        f"weight source {p.weight_source.value_counts().to_dict()}")

    q = pairs(p)
    ok = q[q.pair_eligible]
    log(f"year-ago pairs: {len(q)}, eligible {len(ok)}; "
        f"exclusions {q[~q.pair_eligible].exclusion_reason.value_counts().to_dict()}")

    parts = [
        agg(ok, ["market"], "market", hc),
        agg(ok, ["abnb_region"], "region", hc),
        agg(ok, ["abnb_quarter"], "quarter", hc),
        agg(ok, ["year_b"], "year", hc),
        agg(ok, ["abnb_quarter", "abnb_region"], "quarter_region", hc),
        agg(ok.assign(all_="panel"), ["all_"], "panel_all_periods", hc),
    ]
    # The 2Q26 disclosure window. estimated_occupancy_l365d is an LTM measure, so a dump
    # landing in Jun-Aug 2026 against one a year earlier compares two LTM windows -- the
    # same construction as Airbnb's LTM bedroom-nights figure.
    w26 = ok[(ok.date_b >= "2026-04-01") & (ok.date_b <= "2026-08-31")]
    if len(w26):
        parts.append(agg(w26.assign(all_="2Q26_window"), ["all_"], "disclosure_window_2Q26", hc))
        parts.append(agg(w26, ["abnb_region"], "disclosure_window_2Q26_region", hc))
        parts.append(agg(w26, ["market"], "disclosure_window_2Q26_market", hc))
    # Sensitivity: include the pairs the scope rule rejects, since the wedge is a ratio of
    # growth rates and should be much less scope-sensitive than a level series.
    parts.append(agg(q.assign(all_="all_pairs"), ["all_"], "sensitivity_ignore_scope_flags", hc))
    if len(q[(q.date_b >= "2026-04-01") & (q.date_b <= "2026-08-31")]):
        parts.append(agg(q[(q.date_b >= "2026-04-01") & (q.date_b <= "2026-08-31")].assign(all_="2Q26_all"),
                         ["all_"], "sensitivity_2Q26_ignore_scope_flags", hc))
    # Unweighted across markets, so the answer is not one large city.
    m = agg(ok, ["market"], "market", hc)
    parts.append(pd.DataFrame([dict(
        scope="panel_market_unweighted", n_pairs=int(m.n_pairs.sum()), n_markets=len(m),
        markets="|".join(sorted(m.market)), nights_yoy_pct=m.nights_yoy_pct.mean(),
        bedroom_nights_yoy_pct=m.bedroom_nights_yoy_pct.mean(),
        size_wedge_pp=m.size_wedge_pp.mean(),
        wedge_pp_market_min=m.size_wedge_pp.min(), wedge_pp_market_max=m.size_wedge_pp.max(),
        d_bedrooms=m.d_bedrooms.mean(), d_mean_log_capacity=m.d_mean_log_capacity.mean(),
        size_mix_pp_quote_basis=size_pp(m.d_bedrooms.mean(), m.d_mean_log_capacity.mean(), hc["quote_per_night"]),
        size_mix_pp_listed_basis=size_pp(m.d_bedrooms.mean(), m.d_mean_log_capacity.mean(), hc["listed_nightly"]))]))

    # ---- split WS03's fused "size and price" residual -------------------------------
    # This is the point of the whole build: 03_annual_decomposition.csv leaves unit size and
    # like-for-like price inside one number. Subtracting the size estimate leaves price.
    dec_path = f"{OUT}/03_annual_decomposition.csv"
    if os.path.exists(dec_path):
        dec = pd.read_csv(dec_path)
        yr = agg(ok, ["year_b"], "year", hc).set_index("year_b")
        for _, d in dec.iterrows():
            y = int(d.year)
            if y not in yr.index:
                continue
            g = yr.loc[y]
            for lab, sz in (("central_quote_basis", g.size_mix_pp_quote_basis),
                            ("alt_listed_basis", g.size_mix_pp_listed_basis)):
                parts.append(pd.DataFrame([dict(
                    scope="ws03_residual_split", year_b=y, n_pairs=int(g.n_pairs),
                    n_markets=int(g.n_markets), markets=g.markets,
                    size_wedge_pp=g.size_wedge_pp, d_bedrooms=g.d_bedrooms,
                    d_mean_log_capacity=g.d_mean_log_capacity,
                    size_and_price_pp_ws03=d["of_which_size_and_price_pp"],
                    size_mix_pp_quote_basis=sz,
                    lfl_price_pp_implied=d["of_which_size_and_price_pp"] - sz,
                    basis_variant=lab,
                    caveat=(f"size term measured on {int(g.n_markets)} urban market(s) "
                            f"({g.markets}) against a global disclosed residual; the panel does "
                            "not cover the non-urban and emerging markets where Airbnb's nights "
                            "growth is concentrated, so this is indicative, not a global split. "
                            + ("SINGLE CITY -- treat as a placeholder only. " if g.n_markets < 3 else "")
                            + "The price line is what is left, not an independent measurement"))]))

    s = pd.concat(parts, ignore_index=True)
    s.insert(1, "hedonic_bed_coef_quote", hc["quote_per_night"]["b_bed"])
    s.insert(2, "hedonic_lacc_coef_quote", hc["quote_per_night"]["b_lacc"])
    s["disclosed_2Q26_wedge_pp"] = 2.0
    s["basis_note"] = ("no price field is read from the dumps, so the 2026 fee-inclusive price-basis "
                       "break does not enter the size series; it enters only through the choice of "
                       "hedonic coefficient, and both bases are reported")
    s.to_csv(f"{OUT}/05_size_mix_summary.csv", index=False)

    q.assign(date_a=q.date_a.dt.strftime("%Y-%m-%d"),
             date_b=q.date_b.dt.strftime("%Y-%m-%d")).to_csv(f"{OUT}/05_size_mix_pairs.csv", index=False)

    # ---------------------------------------------------------------- evidence
    corr, exact, nrows, ndumps = occ_validation()
    probe = partial_scope_probe(p)
    ccg, ccfit = cc_test()
    wb_detail, wb = within_between(q, "2026-04-01", "2026-08-31")
    if len(wb_detail):
        wb_detail.assign(date_a=wb_detail.date_a.dt.strftime("%Y-%m-%d"),
                         date_b=wb_detail.date_b.dt.strftime("%Y-%m-%d")).to_csv(
            f"{OUT}/05_size_within_between.csv", index=False)
        log(f"within/between: matched wedge {wb['wedge_matched_pp']:+.3f}pp, "
            f"churn {wb['wedge_churn_pp']:+.3f}pp, total {wb['wedge_total_pp']:+.3f}pp")

    pan = s[s.scope.eq("panel_all_periods")].iloc[0]
    hlq = s[s.scope.eq("disclosure_window_2Q26")]
    hl = hlq.iloc[0] if len(hlq) else None
    odr = region_levels(p, p.source.eq("onedrive_inside_airbnb"), "onedrive")
    win = p.dump_date.ge("2026-06-01") & p.dump_date.le("2026-07-31")
    rpr = region_levels(p, p.source.eq("repo_inside_airbnb") & win, "repo")

    E = []

    def ev(kind, metric, value, unit, scope, period, source, note):
        E.append(dict(kind=kind, metric=metric, value=value, unit=unit, scope=scope,
                      period=period, source=source, note=note))

    # -- what Airbnb actually disclosed
    ev("disclosed", "Bedroom Nights Booked y/y", 12.0, "pct", "Airbnb global", "2Q26",
       "ABNB 2Q26 shareholder letter (data/raw/letters/2Q26_d70413dex991.htm)",
       "'grew over 12%'; the only unit-size figure Airbnb has ever published")
    ev("disclosed", "Nights and Seats Booked y/y", 10.0, "pct", "Airbnb global", "2Q26",
       "ABNB 2Q26 shareholder letter", "the denominator of the wedge")
    ev("disclosed", "size wedge (bedroom nights less nights)", 2.0, "pp", "Airbnb global", "2Q26",
       "derived from the two rows above",
       "'over 12%' against 10% makes this a lower bound, so >=2pp; the entire management claim "
       "that roughly half of ADR growth is size rests on this one number")
    ev("disclosed", "Bedroom Nights Booked LTM", 1000.0, "million", "Airbnb global", "LTM to 2Q26",
       "ABNB 2Q26 letter, 'more than 1 billion'", "against ~560m LTM nights")
    ev("derived", "bedrooms per booked night implied by disclosure", 1.786, "bedrooms",
       "Airbnb global", "LTM to 2Q26", "1000 / 560.0 (data/processed/overnight/15_claim_checks.csv)",
       "a lower bound: 'more than 1 billion' over an LTM nights figure")
    ev("derived", "ADR per bedroom-night implied by disclosure", 102.9, "USD", "Airbnb global",
       "2Q26", "ADR 183.73 / 1.786", "upper bound; US hotel ADR ~172 over the same window")

    # -- method
    ev("method", "estimated_occupancy_l365d is a nights count, not a percentage", CAP, "nights",
       "Inside Airbnb, all 168 repo dumps", "2025-2026",
       "observed field maximum 255 = 0.7 * 365",
       "the ceiling is Inside Airbnb's own 70% cap on estimated nights booked; a percentage "
       "field could not exceed 100. Weighting by it converts a supply-side size distribution "
       "into an approximate booked size distribution")
    ev("method", "reconstructed weight vs published field, correlation", round(corr, 4), "r",
       f"{ndumps} dumps, {nrows:,} listings", "2025-2026",
       "reviews_ltm/0.5 * max(3, min_nights) capped at 0.7*365, vs estimated_occupancy_l365d",
       f"exact agreement {exact:.1%}; validates the backfill used on the 19 pre-2025 dumps "
       "(Austin, Nashville, Paris and Rome before 2025)")
    ev("method", "partial-scope dumps: bedrooms per booked night vs own-city clean mean",
       round(probe["median_ratio"], 4), "ratio", f"{probe['n_partial']} partial dumps", "2022-2026",
       "this build, partial_scope_probe()",
       f"p10-p90 {probe['p10_ratio']:.3f}-{probe['p90_ratio']:.3f}, median z {probe['median_z']:+.2f}. "
       "Consistent with WS21's "
       "finding that partial scrapes are uniform subsamples, so the size RATIO largely survives "
       "them even though level counts do not. The headline series still uses pair_eligible only; "
       "the ignore-flags sensitivity row in the summary shows how little it moves")

    rp = p[p.source.eq("repo_inside_airbnb")]
    ev("method", "private-room `bedrooms` population, range across repo dumps",
       f"{rp.bedrooms_priv_nonnull_share.min():.3f}-{rp.bedrooms_priv_nonnull_share.max():.3f}",
       "non-null share", f"{len(rp)} dumps, 13 cities", "2022-2026", "this build, panel file",
       "Inside Airbnb populates `bedrooms` on private rooms in some dumps and not others, and the "
       "regime changes twice inside the 2026 test window. Any measure that imputes a missing value "
       "will read the metadata change as a size trend. Handled by pinning a private room at one "
       "bedroom regardless of the field")
    ev("method", "whole-home `bedrooms` population, range across repo dumps",
       f"{rp.bedrooms_eh_nonnull_share.min():.3f}-{rp.bedrooms_eh_nonnull_share.max():.3f}",
       "non-null share", f"{len(rp)} dumps, 13 cities", "2022-2026", "this build, panel file",
       f"median {rp.bedrooms_eh_nonnull_share.median():.3f}. Far steadier than private rooms, but two "
       "dumps (Paris 2023-12-12, Rome 2023-12-15) carry the field on ~0.1% of whole homes and "
       "Barcelona falls to 0.66 by Jul 2026. Dumps below "
       f"{EH_COV_MIN:.0%} are excluded and pairs whose endpoints differ by more than "
       f"{EH_COV_DRIFT:.0%} are excluded")
    if hl is not None:
        ev("negative_result", "size-mix ADR contribution using the hedonic's own bedrooms_f",
           round(hl.size_mix_pp_quote_rejected_bedrooms_f, 3), "pp", hl.markets, hl.date_b_max,
           "this build, rejected variant",
           f"against {hl.size_mix_pp_quote_basis:.3f}pp on the coverage-robust measure. REJECTED: "
           "bedrooms_f falls back to round(accommodates/2) whenever the field is missing, which is "
           "0.1% of private rooms in one dump and 85% in another, so the difference between the two "
           "numbers is Inside Airbnb metadata, not market size. Recorded because the size of the "
           "artefact is the reason the headline measure had to be rebuilt")

    # -- the independent series
    ev("independent", "size wedge, panel, all eligible year-ago pairs",
       round(pan.size_wedge_pp, 3), "pp", pan.markets, f"{pan.date_b_min}..{pan.date_b_max}",
       "this build, Inside Airbnb booking-weighted",
       f"bedroom nights {pan.bedroom_nights_yoy_pct:+.1f}% vs nights {pan.nights_yoy_pct:+.1f}% "
       f"on {int(pan.n_pairs)} pairs across {int(pan.n_markets)} cities; market-level wedges span "
       f"{pan.wedge_pp_market_min:+.1f} to {pan.wedge_pp_market_max:+.1f}pp")
    if hl is not None:
        ev("independent", "size wedge, 2Q26 disclosure window", round(hl.size_wedge_pp, 3), "pp",
           hl.markets, f"{hl.date_b_min}..{hl.date_b_max}",
           "this build; the direct test of the disclosed +2pp",
           f"bedroom nights {hl.bedroom_nights_yoy_pct:+.1f}% vs nights {hl.nights_yoy_pct:+.1f}%; "
           f"Airbnb disclosed +12% vs +10%. Market-level wedges span "
           f"{hl.wedge_pp_market_min:+.1f} to {hl.wedge_pp_market_max:+.1f}pp")
        ev("independent", "bedrooms per booked night, level, 2Q26 window",
           round(hl.bed_per_booked_night_b, 3), "bedrooms", hl.markets, hl.date_b_max, "this build",
           "Airbnb's disclosed global figure is >=1.786; these are dense urban markets, which skew "
           "small, so a level below the global figure is expected and is not a contradiction")
        ev("independent", "capacity per booked night y/y, 2Q26 window",
           round(hl.cap_per_booked_night_yoy_pct, 3), "pct", hl.markets, hl.date_b_max, "this build",
           f"level {hl.cap_per_booked_night_b:.3f} guests; capacity is the one size measure with no "
           "imputation anywhere in it")
        ev("independent", "size-mix contribution to ADR, 2Q26 window, quote basis",
           round(hl.size_mix_pp_quote_basis, 3), "pp", hl.markets, hl.date_b_max,
           "this build x data/processed/overnight/06_wtp_hedonic_coefs.csv",
           f"d bedrooms {hl.d_bedrooms:+.4f} x {hc['quote_per_night']['b_bed']:.4f} plus "
           f"d mean log capacity {hl.d_mean_log_capacity:+.5f} x {hc['quote_per_night']['b_lacc']:.4f}; "
           f"listed-nightly basis gives {hl.size_mix_pp_listed_basis:+.3f}pp")

    if wb:
        ev("independent", "size wedge on listings present in both dumps (demand reallocation)",
           round(wb["wedge_matched_pp"], 3), "pp", f"{wb['n_markets']} cities, {wb['n_pairs']} pairs",
           "2Q26 window", "this build, within_between()",
           f"matched listings carry {wb['matched_share']:.0%} of the later dump's booked nights; "
           f"the remaining {wb['wedge_churn_pp']:+.3f}pp of the {wb['wedge_total_pp']:+.3f}pp total "
           "comes from listings entering and leaving the panel, i.e. the housing stock changing "
           "rather than guests choosing differently")
        ev("independent", "size wedge from listing entry and exit", round(wb["wedge_churn_pp"], 3),
           "pp", f"{wb['n_markets']} cities", "2Q26 window", "this build, within_between()",
           "both halves are real for ADR; the split only says which mechanism produced it")

    # -- hedonic coefficients used
    ev("hedonic", "extra bedroom holding capacity fixed, quote basis",
       round((np.exp(hc["quote_per_night"]["b_bed"]) - 1) * 100, 2), "pct", "13 cities, 76 dumps",
       "2026", "data/processed/overnight/06_wtp_hedonic_coefs.csv, term bedrooms_f",
       f"coef {hc['quote_per_night']['b_bed']:.4f} (se {hc['quote_per_night']['se_bed']:.4f}), "
       f"n={hc['quote_per_night']['n']:,}. USED AS CENTRAL: the fee-inclusive quote is the price "
       "basis in force over the 2026 test window, so it is the basis on which a mix shift would "
       "actually show up in reported ADR")
    ev("hedonic", "extra bedroom holding capacity fixed, listed-nightly basis",
       round((np.exp(hc["listed_nightly"]["b_bed"]) - 1) * 100, 2), "pct", "13 cities, 47 dumps",
       "to Sep 2025", "same file",
       f"coef {hc['listed_nightly']['b_bed']:.4f}; carried as the upper alternative")
    ev("hedonic", "capacity elasticity, quote basis", round(hc["quote_per_night"]["b_lacc"], 4),
       "d log price / d log accommodates", "13 cities", "2026", "same file, term lacc",
       f"listed-nightly basis is {hc['listed_nightly']['b_lacc']:.4f}. NOTE: the task brief quoted "
       "+0.49% per 1%; no 0.49 appears in the coefficient file on either basis")
    ev("hedonic", "caveat on using these coefficients", np.nan, "qualitative", "13 cities", "2026",
       "06_wtp_hedonic_coefs.csv", "the hedonic is a cross-sectional ASKING-price relationship fitted "
       "on the same Inside Airbnb panel that produces the size series here, so the ADR conversion is "
       "internally consistent but not independent evidence, and it is not causal")

    # -- geographic breadth
    for r, row in odr.iterrows():
        ev("external_breadth", "bedrooms per booked night, OneDrive markets",
           round(row.bed_per_booked_night, 3), "bedrooms", f"{r}, {int(row.n_dumps)} markets",
           "Jun-Jul 2026", "data/raw/theo_onedrive/AIRBNB DATA/raw/inside_airbnb, booking-weighted",
           f"capacity {row.cap_per_booked_night:.2f} guests, {row.share_cap_ge6_booked:.1%} of booked "
           "nights in 6+ capacity units. Single vintage per market, so no y/y is possible from this leg")
    for r, row in rpr.iterrows():
        ev("repo_level", "bedrooms per booked night, repo cities", round(row.bed_per_booked_night, 3),
           "bedrooms", f"{r}, {int(row.n_dumps)} dumps", "Jun-Jul 2026",
           "repo Inside Airbnb, booking-weighted",
           f"capacity {row.cap_per_booked_night:.2f} guests, {row.share_cap_ge6_booked:.1%} in 6+ "
           "capacity units; comparison base for the OneDrive breadth rows")

    # -- external corroboration
    ev("external", "UK short-term-rental bookings, capacity 1-2 guests", 43.0, "pct of bookings",
       "United Kingdom", "June 2019", "Lighthouse / VisitBritain short-term rental data",
       "paired with the June 2026 row; the only external booked-by-size time series located")
    ev("external", "UK short-term-rental bookings, capacity 1-2 guests", 29.0, "pct of bookings",
       "United Kingdom", "June 2026", "Lighthouse / VisitBritain", "-14pp over seven years")
    ev("external", "UK short-term-rental bookings, capacity 6+ guests", 21.0, "pct of bookings",
       "United Kingdom", "June 2019", "Lighthouse / VisitBritain", "")
    ev("external", "UK short-term-rental bookings, capacity 6+ guests", 30.0, "pct of bookings",
       "United Kingdom", "June 2026", "Lighthouse / VisitBritain",
       "+9pp; large units overtook small ones. Corroborates direction and rough pace, but it is "
       "UK-only, whole short-term-rental-market rather than Airbnb-only, and spans seven years "
       "rather than one, so it cannot calibrate an annual pp contribution")
    ev("external", "4+ bedroom homes fastest-growing listing category", np.nan, "qualitative",
       "Airbnb global", "2Q26", "ABNB 2Q26 earnings call via data/processed/airbnb_party_size_evidence.csv",
       "management colour, consistent with the wedge, not quantified")
    ev("external", "booked stays by listing capacity: room/1-2/3-4/5-6/7+", "13/12/23/20/33",
       "pct of booked runs", "Inside Airbnb, 8 US cities", "June 2026",
       "data/processed/airbnb_party_size_evidence.csv",
       "cross-sectional only; an existing repo figure, consistent with the capacity distribution here")

    # -- negative results
    if ccfit is not None:
        b, se, n = ccfit
        sig = abs(b / se) > 2
        ev("negative_result", "Common Crawl person_capacity trend, year coefficient", round(b, 4),
           "guests per year", "CC listing panel, region fixed effects", "2021-2026",
           "data/processed/cc_listing_panel.csv",
           f"t={b/se:.2f}, n={n}. "
           + ("Nominally significant, but REJECTED as a size series: it is 250-1129 first-observations "
              "per year, the crawled listing set is redrawn every year so the composition change is "
              "not a market change, there is no booking weight, `bedrooms` is missing for most of "
              "2021-22, and North America is absent from the panel entirely. NOT USED."
              if sig else
              "Not significant, and REJECTED as a size series in any case: n per year is 250-1129 "
              "first-observations, the crawled set is redrawn annually, there is no booking weight, "
              "and North America is absent. NOT USED."))
        for y, row in ccg.iterrows():
            ev("negative_result", "Common Crawl mean person_capacity", round(row["mean"], 3), "guests",
               f"n={int(row['size'])}", str(y), "data/processed/cc_listing_panel.csv",
               f"se {row['se']:.3f}; supply-quality panel, recorded for completeness, not used")
    ev("negative_result", "booking_curves_by_market.csv as a size series", np.nan, "n/a",
       "120 markets", "one vintage, 2026", "data/processed/booking_curves_by_market.csv",
       "REJECTED: the file carries country/region/market/snapshot_date/horizon/listing_nights/"
       "listings/blocked_nights/blocked_rate/median_min_nights and has no bedroom or capacity "
       "dimension at all, so it cannot contribute to a size series. It is also one vintage, so no "
       "y/y exists even if a size field were added")
    ev("negative_result", "calendar_daily.csv.gz as a booked-size weight", np.nan, "n/a",
       "5,816,795 rows", "2019-2020", "data/raw/theo_onedrive/.../airbnb_quant_panel_v1/calendar_daily.csv.gz",
       "REJECTED: scanned in full. Every row is source_family=legacy_inside_airbnb from the lrakla "
       "GitHub San Francisco mirror, country USA/United States only, dated 2019-2020. It contains no "
       "current Inside Airbnb calendar data, no non-US market, and no bedroom or capacity column, so "
       "it cannot produce a booked-size weight for any period relevant here")

    pd.DataFrame(E).to_csv(f"{OUT}/05_size_evidence.csv", index=False)

    # ---------------------------------------------------------------- console
    pd.set_option("display.width", 260)
    pd.set_option("display.max_columns", 40)
    print("\n=== weight validation ===")
    print(f"reconstructed vs published estimated_occupancy_l365d: r={corr:.4f}, exact={exact:.1%}, "
          f"n={nrows:,} listings over {ndumps} dumps")
    print(f"partial-scope probe: {probe['n_partial']} partial dumps, median ratio to own-city clean "
          f"mean {probe['median_ratio']:.4f} (p10 {probe['p10_ratio']:.3f}, p90 {probe['p90_ratio']:.3f}), "
          f"median z {probe['median_z']:+.2f}")

    cols = [c for c in ["scope", "abnb_quarter", "year_b", "abnb_region", "market", "n_pairs",
                        "n_markets", "nights_yoy_pct", "bedroom_nights_yoy_pct", "size_wedge_pp",
                        "bed_per_booked_night_b", "cap_per_booked_night_yoy_pct", "bed_cc_yoy_pct", "d_bedrooms",
                        "size_and_price_pp_ws03", "lfl_price_pp_implied", "basis_variant",
                        "d_mean_log_capacity", "size_mix_pp_quote_basis", "size_mix_pp_listed_basis"]
            if c in s.columns]
    for lab in ("panel_all_periods", "disclosure_window_2Q26", "sensitivity_ignore_scope_flags",
                "sensitivity_2Q26_ignore_scope_flags", "panel_market_unweighted",
                "disclosure_window_2Q26_region", "disclosure_window_2Q26_market",
                "ws03_residual_split", "region", "year", "quarter", "market"):
        sub = s[s.scope.eq(lab)]
        if len(sub):
            print(f"\n-- {lab}")
            print(sub[cols].to_string(index=False))

    if wb:
        print("\n=== within vs between (2Q26 window) ===")
        print(f"total {wb['wedge_total_pp']:+.3f}pp = matched listings {wb['wedge_matched_pp']:+.3f}pp "
              f"+ entry/exit {wb['wedge_churn_pp']:+.3f}pp; matched listings are "
              f"{wb['matched_share']:.0%} of later-dump booked nights, {wb['n_pairs']} pairs")

    print("\n=== booking-weighted size by region, Jun-Jul 2026 ===")
    print("OneDrive leg (adds LatAm and APAC breadth):")
    print(odr.to_string())
    print("Repo 13-city leg, same window:")
    print(rpr.to_string())
    if ccg is not None:
        print("\n=== Common Crawl (negative control) ===")
        print(ccg.to_string())
        print("year coefficient (region FE):", ccfit)
    log("done")


if __name__ == "__main__":
    main()
