"""A3 (1/2): freeze the fee-deadline listing sample.

Why this sample exists
  Airbnb's single 15.5% host fee becomes mandatory on two dates that differ by host
  residence: 15 Sep 2026 outside the EEA, 13 Oct 2026 inside the EEA + Switzerland
  (Airbnb Resource Center article 771, see docs/.../A3_fee_panels.md). Between those
  two dates EEA hosts are an untreated CONTROL for non-EEA hosts, which is what makes
  theta -- the share of the payout-neutral +14.8% reprice that hosts actually pass
  through -- identifiable at all. The existing estimate (data/processed/adr/
  12_reprice_summary.csv) is bounded by its own detection window and is not.

What it does
  Reads the most recent Inside Airbnb detailed dump per city for the 13 markets that
  carry the Mar-Aug 2026 quote panel (06_quote_line_items.csv), keeps listings that
  could actually be quoted for a fixed 3-night stay, stratifies by room type x bedroom
  bucket x host professionalisation, and draws up to 200 per city with a fixed seed.

  Host professionalisation matters for more than balance: hosts on property-management
  software migrated in late 2025 and a residual cohort on 13 Oct 2026, so multi-listing
  hosts are partly ALREADY TREATED. They are kept and flagged, not dropped -- the
  already-migrated cohort is the placebo arm (it should not jump on 15 Sep).

Writes
  data/processed/forecast_methods/fee_panels/sample_ids.csv
Run
  python analysis/src/forecast_methods/fee_panels/build_sample.py --dumps <dir>
"""
import argparse
import hashlib
import os
import re
import sys

import numpy as np
import pandas as pd

ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "..", ".."))
OUT = os.path.join(ROOT, "data", "processed", "forecast_methods", "fee_panels")

# The 13 markets in the 2026 quote panel (data/processed/overnight/06_quote_line_items.csv),
# with the most recent Inside Airbnb dump as at 2026-09-11 and the host-fee geography.
# eea_flag follows the DEADLINE grouping in Airbnb article 771: EEA *plus Switzerland*
# take 13 Oct; everyone else takes 15 Sep. The UK left the EEA in 2020, so London is
# a non-EEA (15 Sep) market -- that is deliberate, not an oversight.
MARKETS = [
    # city, country, iso2, eea_flag, dump_date, single_fee_pct
    ("austin",         "United States",  "US", 0, "2026-08-25", 15.5),
    ("chicago",        "United States",  "US", 0, "2026-08-27", 15.5),
    ("los-angeles",    "United States",  "US", 0, "2026-08-10", 15.5),
    ("nashville",      "United States",  "US", 0, "2026-08-27", 15.5),
    ("new-orleans",    "United States",  "US", 0, "2026-08-15", 15.5),
    ("new-york-city",  "United States",  "US", 0, "2026-08-10", 15.5),
    ("san-diego",      "United States",  "US", 0, "2026-08-29", 15.5),
    ("london",         "United Kingdom", "GB", 0, "2026-08-18", 15.5),
    ("sydney",         "Australia",      "AU", 0, "2026-08-15", 15.5),
    ("mexico-city",    "Mexico",         "MX", 0, "2026-08-30", 16.0),  # 16% per article 771
    ("barcelona",      "Spain",          "ES", 1, "2026-08-23", 15.5),
    ("paris",          "France",         "FR", 1, "2026-08-15", 15.5),
    ("rome",           "Italy",          "IT", 1, "2026-08-25", 15.5),
]

# FIXED stay dates -- identical on every capture run, so a change in a quote is a
# change in price, never a change in the question. Both are Friday check-in / Monday
# check-out 3-night stays so day-of-week mix is constant, both fall after the last
# capture run (16 Oct 2026) so lead time stays positive throughout, and both avoid US
# Thanksgiving (26 Nov) and the Christmas peak.
STAYS = [
    ("W1", "2026-11-13", "2026-11-16"),   # 28 days after the last run
    ("W2", "2026-12-11", "2026-12-14"),   # 56 days after the last run
]
ADULTS = 2
PER_CITY = 200
SEED = 20260911

USECOLS = ["id", "listing_url", "host_id", "host_location", "host_is_superhost",
           "host_listings_count", "host_total_listings_count", "room_type", "property_type",
           "accommodates", "bedrooms", "beds", "price", "minimum_nights", "maximum_nights",
           "has_availability", "availability_90", "number_of_reviews", "number_of_reviews_ltm",
           "estimated_occupancy_l365d", "license", "instant_bookable",
           "calculated_host_listings_count", "price_quote_raw", "last_scraped"]

# EEA member states + Switzerland, for reading free-text host_location. Only used to
# FLAG likely misassignment: the deadline follows where the host lives, not where the
# listing is (article 771: "if you live outside the European Economic Area").
EEA_CH = [
    "austria", "belgium", "bulgaria", "croatia", "cyprus", "czech", "denmark", "estonia",
    "finland", "france", "germany", "greece", "hungary", "iceland", "ireland", "italy",
    "latvia", "liechtenstein", "lithuania", "luxembourg", "malta", "netherlands", "norway",
    "poland", "portugal", "romania", "slovakia", "slovenia", "spain", "sweden",
    "switzerland", "suisse", "schweiz", "espana", "españa", "deutschland", "italia",
]
NON_EEA = [
    "united states", "usa", "u.s.", "canada", "united kingdom", "england", "scotland",
    "wales", "australia", "new zealand", "mexico", "brazil", "brasil", "japan", "china",
    "hong kong", "singapore", "india", "israel", "turkey", "united arab", "south africa",
    "argentina", "chile", "colombia", "peru", "russia", "korea", "thailand", "vietnam",
]
US_STATE = re.compile(r",\s*(A[KLRZ]|C[AOT]|D[CE]|FL|GA|HI|I[ADLN]|K[SY]|LA|M[ADEINOST]|"
                      r"N[CDEHJMVY]|O[HKR]|P[AR]|RI|S[CD]|T[NX]|UT|V[AT]|W[AIVY])\b")


def host_region(loc, city_iso):
    """Coarse read of the free-text host_location: 'eea_ch', 'non_eea', or 'unknown'."""
    if not isinstance(loc, str) or not loc.strip():
        return "unknown"
    s = loc.lower()
    if US_STATE.search(loc):
        return "non_eea"
    for k in EEA_CH:
        if k in s:
            return "eea_ch"
    for k in NON_EEA:
        if k in s:
            return "non_eea"
    return "unknown"


def bedroom_bucket(b):
    if pd.isna(b):
        return "unknown"
    b = float(b)
    if b <= 1:
        return "0-1"
    if b == 2:
        return "2"
    return "3+"


def host_class(n):
    """Professional vs individual. Inside Airbnb has no PMS flag, so listing count is the
    proxy -- and it doubles as the already-migrated indicator (PMS hosts migrated first)."""
    if pd.isna(n):
        return "unknown"
    n = float(n)
    if n <= 1:
        return "individual"
    if n <= 4:
        return "small_multi"
    return "professional"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dumps", required=True, help="directory of <city>_<date>_listings.csv.gz")
    ap.add_argument("--per-city", type=int, default=PER_CITY)
    a = ap.parse_args()

    rng = np.random.default_rng(SEED)
    frames, audit = [], []

    for city, country, iso2, eea, dump, fee in MARKETS:
        f = os.path.join(a.dumps, f"{city}_{dump}_listings.csv.gz")
        if not os.path.exists(f):
            print(f"MISSING {f}", file=sys.stderr)
            continue
        d = pd.read_csv(f, usecols=lambda c: c in USECOLS, low_memory=False)
        n_raw = len(d)

        # Eligibility for a 3-night quote on a fixed date.
        d["minimum_nights"] = pd.to_numeric(d["minimum_nights"], errors="coerce")
        d["maximum_nights"] = pd.to_numeric(d["maximum_nights"], errors="coerce")
        elig = (
            d["minimum_nights"].le(3)
            & d["maximum_nights"].ge(3)
            & d["has_availability"].astype(str).str.lower().isin(["t", "true", "1"])
            & d["room_type"].notna()
            & pd.to_numeric(d["availability_90"], errors="coerce").gt(0)
            # was actually quotable in the dump -- the strongest predictor of a live quote
            & d["price_quote_raw"].notna()
        )
        e = d[elig].copy()
        n_elig = len(e)
        if n_elig == 0:
            print(f"{city}: 0 eligible of {n_raw}", file=sys.stderr)
            continue

        e["bedroom_bucket"] = e["bedrooms"].map(bedroom_bucket)
        e["host_class"] = e["calculated_host_listings_count"].map(host_class)
        e["stratum"] = e["room_type"] + " | " + e["bedroom_bucket"] + " | " + e["host_class"]

        # Proportional allocation with a floor of 1 per stratum that exists, then a
        # deterministic draw. Sorting by id first makes the draw reproducible regardless
        # of row order in the dump.
        e = e.sort_values("id").reset_index(drop=True)
        target = min(a.per_city, n_elig)
        share = e["stratum"].value_counts(normalize=True)
        alloc = (share * target).apply(np.floor).astype(int).clip(lower=1)
        while alloc.sum() > target:                      # trim the biggest strata first
            alloc[alloc.idxmax()] -= 1
        rem = target - alloc.sum()
        if rem > 0:                                      # hand the remainder back by size
            for s in share.index:
                if rem == 0:
                    break
                room = int(share[s] * n_elig) - alloc[s]
                if room > 0:
                    take = min(rem, room)
                    alloc[s] += take
                    rem -= take

        picks = []
        for s, k in alloc.items():
            g = e[e["stratum"] == s]
            k = int(min(k, len(g)))
            if k > 0:
                picks.append(g.iloc[rng.choice(len(g), size=k, replace=False)])
        sel = pd.concat(picks).sort_values("id").reset_index(drop=True)

        sel["city"] = city
        sel["country"] = country
        sel["country_iso2"] = iso2
        sel["eea_flag"] = eea
        sel["deadline"] = "2026-10-13" if eea else "2026-09-15"
        sel["single_fee_pct"] = fee
        sel["dump_date"] = dump
        sel["host_region_guess"] = [host_region(l, iso2) for l in sel["host_location"]]
        # control contamination: an EEA-city listing whose host plainly lives outside the
        # EEA migrates on 15 Sep, i.e. it is treated, not control (and vice versa).
        sel["geo_conflict"] = np.where(
            (sel["eea_flag"] == 1) & (sel["host_region_guess"] == "non_eea"), 1,
            np.where((sel["eea_flag"] == 0) & (sel["host_region_guess"] == "eea_ch"), 1, 0))

        frames.append(sel)
        audit.append({"city": city, "country": country, "eea_flag": eea, "dump_date": dump,
                      "listings_in_dump": n_raw, "eligible": n_elig, "sampled": len(sel),
                      "strata": sel["stratum"].nunique(),
                      "geo_conflict": int(sel["geo_conflict"].sum())})
        print(f"{city:15s} raw {n_raw:6d}  eligible {n_elig:6d}  sampled {len(sel):4d}  "
              f"strata {sel['stratum'].nunique():3d}  geo_conflict {int(sel['geo_conflict'].sum()):3d}")

    if not frames:
        sys.exit("no cities built")
    s = pd.concat(frames, ignore_index=True)

    # cross the listing sample with the fixed stay windows -> one row per quote to capture
    rows = []
    for w, ci, co in STAYS:
        t = s.copy()
        t["stay_window"] = w
        t["checkin"] = ci
        t["checkout"] = co
        t["nights"] = (pd.Timestamp(co) - pd.Timestamp(ci)).days
        t["adults"] = ADULTS
        rows.append(t)
    out = pd.concat(rows, ignore_index=True)

    cols = ["city", "country", "country_iso2", "eea_flag", "deadline", "single_fee_pct",
            "listing_id", "listing_url", "host_id", "host_location", "host_region_guess",
            "geo_conflict", "room_type", "property_type", "bedrooms", "bedroom_bucket",
            "accommodates", "beds", "host_class", "calculated_host_listings_count",
            "host_is_superhost", "instant_bookable", "license", "minimum_nights",
            "number_of_reviews_ltm", "estimated_occupancy_l365d", "stratum",
            "stay_window", "checkin", "checkout", "nights", "adults",
            "dump_date", "dump_price"]
    out = out.rename(columns={"id": "listing_id", "price": "dump_price"})
    out["listing_url"] = "https://www.airbnb.com/rooms/" + out["listing_id"].astype(str)
    out = out[[c for c in cols if c in out.columns]]

    os.makedirs(OUT, exist_ok=True)
    p = os.path.join(OUT, "sample_ids.csv")
    out.to_csv(p, index=False)
    ap_ = pd.DataFrame(audit)
    ap_.to_csv(os.path.join(OUT, "sample_audit.csv"), index=False)

    h = hashlib.sha256(open(p, "rb").read()).hexdigest()
    print(f"\nwrote {p}\n  rows {len(out)}  listings {out['listing_id'].nunique()}  sha256 {h}")
    print(f"  by eea_flag (listings): "
          f"{out.drop_duplicates('listing_id').groupby('eea_flag').size().to_dict()}")


if __name__ == "__main__":
    main()
