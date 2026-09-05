"""Inside Airbnb listing-level supply panel (plan-of-attack branch 1, built 2026-09-05).

Source: Inside Airbnb (https://insideairbnb.com/get-the-data/), CC-BY 4.0, "listings.csv.gz" per city and dump
date. Inside Airbnb publishes only the latest dump on its page, but older quarterly files stay on the CDN for a
while (about 12 months for most cities, longer for Paris). KNOWN_DATES below were harvested from Wayback
captures of the get-the-data page (Jan 2023 to Feb 2026); `discover` HEAD-checks each and probes the gap months
day by day so the manifest lists exactly what is downloadable today. NYC pre/post Local Law 18 (Sep 2023) is
NOT on the CDN any more; request archived dumps from Inside Airbnb (data request form) for that series.

Steps:
  py -3.13 analysis/src/inside_airbnb_supply_panel.py discover   -> data/raw/inside_airbnb/manifest.csv
  py -3.13 analysis/src/inside_airbnb_supply_panel.py download   -> data/raw/inside_airbnb/<city>_<date>_listings.csv.gz
                                                                    + .parquet cache with the columns used here
  py -3.13 analysis/src/inside_airbnb_supply_panel.py build      -> data/processed/inside_airbnb_city_snapshots.csv
                                                                    data/processed/inside_airbnb_like_for_like.csv
                                                                    data/processed/inside_airbnb_host_concentration.csv
  py -3.13 analysis/src/inside_airbnb_supply_panel.py figures    -> analysis/figures/inside_airbnb_*.png
  py -3.13 analysis/src/inside_airbnb_supply_panel.py all

Definitions (see research/notes/2026-09-05_inside-airbnb-supply-panel.md for the write-up):
  price            Inside Airbnb's nightly price for the listing's first available night in the calendar scrape;
                   null when the calendar shows no availability. Cleaned: numeric, 10 <= price <= 10,000 local
                   currency, entire-home only for the headline series, per-city 1st/99th percentile winsor.
  like-for-like    matched listing ids between two dumps of the same city: median of log(price_b/price_a) on
                   listings priced in both (same-listing price change, the Evidence-Lab style series), plus
                   retention (share of dump-A ids still present in dump-B) and new-listing share.
  reviews_ltm      number_of_reviews_ltm summed over listings: a bookings-velocity proxy (reviews lag stays).
  est_nights_ltm   Inside Airbnb's own occupancy model: reviews_ltm / 0.5 review rate x max(3, minimum_nights)
                   nights per stay, capped at 70% of 365. "Exposed nights" for the regulatory tracker = the same
                   quantity restricted to entire homes with minimum_nights < 30 (the listings STR rules target).
  multi-listing    calculated_host_listings_count > 1 (host has more than one listing in this city dump);
                   professional = >= 5.
"""
import argparse, concurrent.futures, datetime as dt, gzip, io, json, os, sys, time
from pathlib import Path
import numpy as np, pandas as pd, requests

ROOT = Path(__file__).resolve().parents[2]
RAW = ROOT / "data/raw/inside_airbnb"
PROC = ROOT / "data/processed"
FIG = ROOT / "analysis/figures"
UA = {"User-Agent": "Citadel-ABNB student research ksurapaneni@ufl.edu"}
CDN = "https://data.insideairbnb.com/{path}/{date}/data/listings.csv.gz"

# city -> (CDN path, dump dates seen on the get-the-data page in Wayback captures Jan 2023 - Feb 2026, plus the
# current page on 2026-09-05). Regions follow Airbnb's reporting segments.
KNOWN_DATES = {
    "new-york-city": ("united-states/ny/new-york-city", ["2022-12-04", "2023-03-06", "2023-06-05", "2023-10-01", "2023-11-01", "2024-01-05", "2024-03-07", "2024-05-03", "2024-07-05", "2024-09-04", "2024-11-04", "2025-01-03", "2025-03-01", "2025-05-01", "2025-06-17", "2025-08-01", "2025-10-01", "2025-12-04", "2026-08-10"]),
    "los-angeles": ("united-states/ca/los-angeles", ["2022-12-06", "2023-03-07", "2023-06-06", "2023-09-03", "2023-12-03", "2024-03-11", "2024-06-07", "2024-09-04", "2024-12-06", "2025-03-01", "2025-06-17", "2025-09-01", "2025-12-04", "2026-06-15"]),
    "chicago": ("united-states/il/chicago", ["2022-12-20", "2023-03-19", "2023-06-18", "2023-09-12", "2023-12-18", "2024-03-23", "2024-06-21", "2024-09-17", "2024-12-18", "2025-03-11", "2025-06-17", "2025-09-22", "2026-06-24"]),
    "austin": ("united-states/tx/austin", ["2022-12-15", "2023-03-16", "2023-06-10", "2023-09-10", "2023-12-15", "2024-03-23", "2024-06-17", "2024-09-13", "2024-12-14", "2025-03-06", "2025-06-13", "2025-09-16", "2026-06-22"]),
    "nashville": ("united-states/tn/nashville", ["2022-12-21", "2023-03-19", "2023-06-22", "2023-09-16", "2023-12-18", "2024-03-24", "2024-06-22", "2024-09-18", "2024-12-21", "2025-03-15", "2025-06-19", "2025-09-23", "2026-06-26"]),
    "new-orleans": ("united-states/la/new-orleans", ["2022-12-06", "2023-03-09", "2023-06-06", "2023-09-03", "2023-12-03", "2024-03-11", "2024-06-10", "2024-09-05", "2024-12-08", "2025-03-02", "2025-06-09", "2025-09-11", "2026-06-16"]),
    "san-diego": ("united-states/ca/san-diego", ["2022-12-24", "2023-03-24", "2023-06-24", "2023-09-18", "2023-12-04", "2024-03-25", "2024-06-24", "2024-09-21", "2024-12-23", "2025-03-16", "2025-06-21", "2025-09-25", "2026-06-27"]),
    "paris": ("france/ile-de-france/paris", ["2022-12-10", "2023-03-13", "2023-06-06", "2023-09-04", "2023-12-12", "2024-03-16", "2024-06-10", "2024-09-06", "2024-12-06", "2025-03-03", "2025-06-06", "2025-09-12", "2026-06-16"]),
    "london": ("united-kingdom/england/london", ["2022-12-10", "2023-03-14", "2023-06-08", "2023-09-06", "2023-12-10", "2024-03-19", "2024-06-14", "2024-09-06", "2024-12-11", "2025-03-04", "2025-06-10", "2025-09-14", "2026-06-19"]),
    "barcelona": ("spain/catalonia/barcelona", ["2022-12-11", "2023-03-14", "2023-06-10", "2023-09-06", "2023-12-13", "2024-03-20", "2024-06-15", "2024-09-06", "2024-12-12", "2025-03-05", "2025-06-12", "2025-09-14", "2026-06-24"]),
    "rome": ("italy/lazio/rome", ["2022-12-13", "2023-03-15", "2023-06-10", "2023-09-07", "2023-12-15", "2024-03-22", "2024-06-15", "2024-09-11", "2024-12-12", "2025-03-05", "2025-06-12", "2025-09-14", "2026-06-20"]),
    "sydney": ("australia/nsw/sydney", ["2022-12-10", "2023-03-13", "2023-06-06", "2023-09-04", "2023-12-12", "2024-03-16", "2024-06-10", "2024-09-05", "2024-12-08", "2025-03-03", "2025-06-10", "2025-09-12", "2026-06-16"]),
    "mexico-city": ("mexico/df/mexico-city", ["2022-12-29", "2023-03-29", "2023-06-27", "2023-09-22", "2023-12-26", "2024-06-27", "2024-09-25", "2024-12-27", "2025-03-19", "2025-06-25", "2025-09-27", "2026-06-15"]),
}
REGION = {"new-york-city": "NA", "los-angeles": "NA", "chicago": "NA", "austin": "NA", "nashville": "NA", "new-orleans": "NA", "san-diego": "NA",
          "paris": "EMEA", "london": "EMEA", "barcelona": "EMEA", "rome": "EMEA", "sydney": "APAC", "mexico-city": "LatAm"}
# months to probe day by day for dumps that were never captured by Wayback (late 2025 to mid 2026)
PROBE_MONTHS = ["2025-12", "2026-01", "2026-02", "2026-03", "2026-04", "2026-05", "2026-06", "2026-07", "2026-08"]

COLS = ["id", "host_id", "host_since", "host_is_superhost", "host_total_listings_count", "calculated_host_listings_count",
        "calculated_host_listings_count_entire_homes", "neighbourhood_cleansed", "neighbourhood_group_cleansed", "latitude",
        "longitude", "room_type", "accommodates", "bedrooms", "price", "minimum_nights", "has_availability", "availability_30",
        "availability_90", "availability_365", "number_of_reviews", "number_of_reviews_ltm", "number_of_reviews_l30d", "first_review",
        "last_review", "review_scores_rating", "instant_bookable", "license", "estimated_occupancy_l365d", "estimated_revenue_l365d",
        # added by Inside Airbnb in the 2026 dumps: a fee-inclusive price quote for a specific stay, and host tenure
        "price_quote_checkin_date", "price_quote_checkout_date", "price_quote_total_price", "price_quote_price_per_night",
        "hosts_time_as_host_years", "hosts_time_as_host_months"]
NUMERIC = ["host_total_listings_count", "calculated_host_listings_count", "calculated_host_listings_count_entire_homes", "accommodates", "bedrooms",
           "minimum_nights", "availability_30", "availability_90", "availability_365", "number_of_reviews", "number_of_reviews_ltm", "number_of_reviews_l30d",
           "review_scores_rating", "estimated_occupancy_l365d", "estimated_revenue_l365d", "latitude", "longitude", "price_quote_total_price",
           "price_quote_price_per_night", "hosts_time_as_host_years", "hosts_time_as_host_months"]


def log(m):
    print(f"{time.strftime('%H:%M:%S')} {m}", flush=True)


# ----------------------------------------------------------------------------------------------------- discover
def head(sess, url):
    for attempt in range(3):
        try:
            r = sess.head(url, timeout=60, allow_redirects=True)
            if r.status_code in (200, 403, 404):
                return r.status_code, int(r.headers.get("Content-Length") or 0)
        except requests.RequestException:
            pass
        time.sleep(2 * (attempt + 1))
    return None, 0


def discover(args):
    RAW.mkdir(parents=True, exist_ok=True)
    sess = requests.Session(); sess.headers.update(UA)
    cands = []
    for city, (path, dates) in KNOWN_DATES.items():
        known = set(dates)
        for d in dates:
            cands.append((city, d, "wayback_or_current"))
        for ym in PROBE_MONTHS:  # daily probe of the uncaptured months
            y, m = map(int, ym.split("-"))
            ndays = (dt.date(y + (m == 12), m % 12 + 1, 1) - dt.date(y, m, 1)).days
            for day in range(1, ndays + 1):
                d = f"{ym}-{day:02d}"
                if d not in known:
                    cands.append((city, d, "date_probe"))
    log(f"HEAD-checking {len(cands)} candidate dump urls with {args.workers} workers")
    rows = []
    def work(c):
        city, d, how = c
        url = CDN.format(path=KNOWN_DATES[city][0], date=d)
        st, n = head(sess, url)
        return dict(city=city, region=REGION[city], dump_date=d, url=url, http_status=st, bytes=n, found_via=how)
    with concurrent.futures.ThreadPoolExecutor(max_workers=args.workers) as ex:
        for i, r in enumerate(ex.map(work, cands)):
            rows.append(r)
            if r["http_status"] == 200 and r["found_via"] == "date_probe":
                log(f"  new dump found by probe: {r['city']} {r['dump_date']} ({r['bytes']/1e6:.1f} MB)")
    m = pd.DataFrame(rows)
    m = m[(m.http_status == 200) | (m.found_via != "date_probe")].sort_values(["city", "dump_date"])
    m["live"] = m.http_status == 200
    m.to_csv(RAW / "manifest.csv", index=False)
    live = m[m.live]
    log(f"manifest: {len(m)} known dumps, {len(live)} live, {live.bytes.sum()/1e9:.2f} GB")
    print(live.groupby("city").agg(first=("dump_date", "min"), last=("dump_date", "max"), n=("dump_date", "size")).to_string())


# ----------------------------------------------------------------------------------------------------- download
def gz_path(city, d):
    return RAW / f"{city}_{d}_listings.csv.gz"


def read_dump(city, d):
    """Parquet cache of the columns used here; built from the gz on first call."""
    pq = RAW / f"{city}_{d}_listings.parquet"
    if pq.exists():
        df = pd.read_parquet(pq)
        if "price_basis" in df.columns:
            return df
    p = gz_path(city, d)
    with gzip.open(p, "rb") as f:
        header = pd.read_csv(f, nrows=0).columns
    use = [c for c in COLS if c in header]
    df = pd.read_csv(p, usecols=use, low_memory=False, dtype={"license": "string", "price": "string"})
    for c in COLS:
        if c not in df:
            df[c] = pd.NA
    df["price"] = pd.to_numeric(df["price"].astype("string").str.replace(r"[$,]", "", regex=True), errors="coerce")
    for c in ("host_is_superhost", "has_availability", "instant_bookable"):
        df[c] = df[c].map({"t": True, "f": False})
    for c in NUMERIC:
        df[c] = pd.to_numeric(df[c], errors="coerce")
    # price basis: dumps to Sep 2025 carry the listing's nightly rate for the first available night ("listed_nightly");
    # the Dec 2025 - Feb 2026 monthly dumps carry no price; from Mar 2026 "price" equals price_quote_price_per_night,
    # a fee-inclusive quote for a specific stay divided by nights ("quote_per_night"). Not comparable across bases.
    has_quote = "price_quote_price_per_night" in header
    if df["price"].notna().mean() < 0.01:
        basis = "none"
    elif has_quote and df["price_quote_price_per_night"].notna().any():
        basis = "quote_per_night"
    else:
        basis = "listed_nightly"
    df["price_basis"] = basis
    df["id"] = pd.to_numeric(df["id"], errors="coerce").astype("Int64")
    df["host_id"] = pd.to_numeric(df["host_id"], errors="coerce").astype("Int64")
    df["city"], df["dump_date"] = city, d
    df = df[["city", "dump_date", "price_basis"] + COLS]
    df.to_parquet(pq, index=False)
    return df


def download(args):
    m = pd.read_csv(RAW / "manifest.csv")
    m = m[m.live]
    if args.cities:
        m = m[m.city.isin(args.cities)]
    sess = requests.Session(); sess.headers.update(UA)
    todo = [r for r in m.itertuples() if not (gz_path(r.city, r.dump_date).exists() and gz_path(r.city, r.dump_date).stat().st_size >= r.bytes * 0.99)]
    log(f"{len(m)} live dumps, {len(todo)} to download ({sum(r.bytes for r in todo)/1e9:.2f} GB), {args.workers} workers")
    def work(r):
        p = gz_path(r.city, r.dump_date)
        for attempt in range(3):
            try:
                with sess.get(r.url, timeout=600, stream=True) as resp:
                    resp.raise_for_status()
                    tmp = p.with_suffix(".part")
                    with open(tmp, "wb") as f:
                        for chunk in resp.iter_content(1 << 20):
                            f.write(chunk)
                    os.replace(tmp, p)
                return r.city, r.dump_date, p.stat().st_size, None
            except Exception as e:
                err = f"{type(e).__name__}: {e}"[:120]; time.sleep(5 * (attempt + 1))
        return r.city, r.dump_date, 0, err
    with concurrent.futures.ThreadPoolExecutor(max_workers=args.workers) as ex:
        for city, d, n, err in ex.map(work, todo):
            log(f"  {city} {d}: {'%.1f MB' % (n/1e6) if n else err}")
    # build parquet caches
    for r in m.itertuples():
        if gz_path(r.city, r.dump_date).exists() and not (RAW / f"{r.city}_{r.dump_date}_listings.parquet").exists():
            df = read_dump(r.city, r.dump_date)
            log(f"  cached {r.city} {r.dump_date}: {len(df):,} rows, price non-null {df.price.notna().mean():.0%}")


# ----------------------------------------------------------------------------------------------------- build
def clean_price(df):
    p = df["price"].where((df["price"] >= 10) & (df["price"] <= 10000))
    lo, hi = p.quantile(0.01), p.quantile(0.99)
    return p.clip(lo, hi)


def est_nights(df):
    """Inside Airbnb occupancy model: reviews_ltm / 0.5 x max(3, minimum_nights), capped at 70% of 365."""
    per_stay = np.maximum(3, df["minimum_nights"].fillna(1).clip(upper=30))
    return np.minimum(df["number_of_reviews_ltm"].fillna(0) / 0.5 * per_stay, 0.7 * 365)


def snapshot_row(df):
    home = df.room_type.eq("Entire home/apt")
    short = df.minimum_nights.lt(30)
    active = df.has_availability.fillna(False) & df.availability_365.gt(0)
    reviewed = df.number_of_reviews_ltm.gt(0)
    price = clean_price(df)
    ph = price.where(home)
    ph_avail = ph.where(active)
    nights = est_nights(df)
    hosts = df.groupby("host_id").size().sort_values(ascending=False)
    sh = df.host_is_superhost
    row = dict(
        listings=len(df), entire_home=int(home.sum()), share_entire_home=home.mean(),
        active_listings=int(active.sum()), reviewed_ltm_listings=int(reviewed.sum()), share_reviewed_ltm=reviewed.mean(),
        short_min_nights_share=short.mean(), short_entire_home=int((short & home).sum()),
        licensed_share=df.license.notna().mean(),
        reviews_ltm_sum=int(df.number_of_reviews_ltm.fillna(0).sum()), reviews_l30d_sum=int(df.number_of_reviews_l30d.fillna(0).sum()) if df.number_of_reviews_l30d.notna().any() else None,
        reviews_ltm_per_reviewed=df.loc[reviewed, "number_of_reviews_ltm"].mean(),
        est_nights_ltm=float(nights.sum()), exposed_nights_short_entire=float(nights[short & home].sum()),
        est_revenue_l365d=float(df.estimated_revenue_l365d.sum()) if df.estimated_revenue_l365d.notna().any() else None,
        superhost_share=sh.mean() if sh.notna().any() else None, superhost_share_reviewed=sh[reviewed].mean() if sh.notna().any() else None,
        multi_listing_share=df.calculated_host_listings_count.gt(1).mean(), professional_share_5plus=df.calculated_host_listings_count.ge(5).mean(),
        hosts=int(df.host_id.nunique()), top10_host_share=hosts.head(10).sum() / len(df), top100_host_share=hosts.head(100).sum() / len(df),
        price_non_null_share=df.price.notna().mean(),
        median_price_entire=ph.median(), mean_price_entire=ph.mean(), median_price_entire_active=ph_avail.median(),
        median_price_private=price.where(df.room_type.eq("Private room")).median(),
        median_price_entire_1br=ph.where(df.bedrooms.le(1)).median(), median_price_entire_2br=ph.where(df.bedrooms.eq(2)).median(),
        median_availability_365=df.availability_365.median(), mean_availability_90=df.availability_90.mean(),
        instant_book_share=df.instant_bookable.mean() if df.instant_bookable.notna().any() else None,
        median_rating=df.review_scores_rating.median(),
        price_basis=df.price_basis.iloc[0],
        quote_stay_nights=(pd.to_datetime(df.price_quote_checkout_date, errors="coerce") - pd.to_datetime(df.price_quote_checkin_date, errors="coerce")).dt.days.median() if df.price_quote_checkin_date.notna().any() else None,
        quote_lead_days=(pd.to_datetime(df.price_quote_checkin_date, errors="coerce") - pd.Timestamp(df.dump_date.iloc[0])).dt.days.median() if df.price_quote_checkin_date.notna().any() else None,
        median_quote_total_entire=df.price_quote_total_price.where(home).median() if df.price_quote_total_price.notna().any() else None,
        host_tenure_years_median=(df.hosts_time_as_host_years.fillna(0) + df.hosts_time_as_host_months.fillna(0) / 12).median() if df.hosts_time_as_host_years.notna().any() else None,
        new_hosts_share=None,
    )
    # host tenure: host_since (dumps to 2025) or hosts_time_as_host_years/months (2026 dumps, host_since blank)
    dump = pd.Timestamp(df.dump_date.iloc[0])
    if df.host_since.notna().mean() > 0.5:
        tenure_years = (dump - pd.to_datetime(df.host_since, errors="coerce")).dt.days / 365.25
    else:
        tenure_years = df.hosts_time_as_host_years.fillna(0) + df.hosts_time_as_host_months.fillna(0) / 12
        tenure_years = tenure_years.where(df.hosts_time_as_host_years.notna() | df.hosts_time_as_host_months.notna())
    row["new_hosts_share"] = (tenure_years < 1).mean() if tenure_years.notna().any() else None
    row["host_tenure_years_median"] = tenure_years.median() if tenure_years.notna().any() else None
    return row


def pair_row(a, b):
    """Like-for-like metrics between dump a (earlier) and dump b (later) of the same city."""
    a = a.set_index("id"); b = b.set_index("id")
    ida, idb = set(a.index.dropna()), set(b.index.dropna())
    common = sorted(ida & idb)
    out = dict(ids_a=len(ida), ids_b=len(idb), matched=len(common), retention=len(common) / len(ida) if ida else None,
               new_share_b=1 - len(common) / len(idb) if idb else None, gross_adds=len(idb - ida), exits=len(ida - idb))
    if not common:
        return out
    ca, cb = a.loc[common], b.loc[common]
    home = ca.room_type.eq("Entire home/apt") & cb.room_type.eq("Entire home/apt")
    pa, pb = clean_price(ca), clean_price(cb)
    basis_a, basis_b = ca.price_basis.iloc[0], cb.price_basis.iloc[0]
    comparable = bool(basis_a == basis_b and basis_a != "none")
    out.update(price_basis_a=basis_a, price_basis_b=basis_b, price_comparable=comparable)
    ok = home & pa.notna() & pb.notna() & comparable
    lr = np.log(pb[ok] / pa[ok])
    out.update(matched_priced_entire=int(ok.sum()), lfl_price_chg_median=float(np.expm1(lr.median())) if ok.any() else None,
               lfl_price_chg_mean=float(np.expm1(lr.mean())) if ok.any() else None,
               lfl_price_up_share=float((lr > 0.005).mean()) if ok.any() else None, lfl_price_down_share=float((lr < -0.005).mean()) if ok.any() else None,
               lfl_median_price_a=float(pa[ok].median()) if ok.any() else None, lfl_median_price_b=float(pb[ok].median()) if ok.any() else None)
    # reviews: matched listings' reviews_ltm in b vs a (same-listing bookings velocity)
    ra, rb = ca.number_of_reviews_ltm.fillna(0), cb.number_of_reviews_ltm.fillna(0)
    out.update(matched_reviews_ltm_a=int(ra.sum()), matched_reviews_ltm_b=int(rb.sum()),
               matched_reviews_ltm_chg=float(rb.sum() / ra.sum() - 1) if ra.sum() else None)
    # exits: what left (were they reviewed / professional / entire home?)
    gone = a.loc[sorted(ida - idb)]
    out.update(exit_reviewed_ltm_share=float(gone.number_of_reviews_ltm.gt(0).mean()) if len(gone) else None,
               exit_entire_home_share=float(gone.room_type.eq("Entire home/apt").mean()) if len(gone) else None,
               exit_multi_listing_share=float(gone.calculated_host_listings_count.gt(1).mean()) if len(gone) else None)
    added = b.loc[sorted(idb - ida)]
    out.update(add_entire_home_share=float(added.room_type.eq("Entire home/apt").mean()) if len(added) else None,
               add_multi_listing_share=float(added.calculated_host_listings_count.gt(1).mean()) if len(added) else None)
    # superhost transitions among matched
    if ca.host_is_superhost.notna().any():
        out.update(matched_superhost_a=float(ca.host_is_superhost.mean()), matched_superhost_b=float(cb.host_is_superhost.mean()))
    return out


def build(args):
    m = pd.read_csv(RAW / "manifest.csv")
    m = m[m.live & m.apply(lambda r: gz_path(r.city, r.dump_date).exists(), axis=1)].sort_values(["city", "dump_date"])
    snaps, pairs, hosts = [], [], []
    for city, g in m.groupby("city"):
        dumps = {}
        for d in g.dump_date:
            df = read_dump(city, d)
            dumps[d] = df
            r = dict(city=city, region=REGION[city], dump_date=d, **snapshot_row(df))
            snaps.append(r)
            # host concentration table: top hosts by listings in the latest dump only (keeps the file small)
            if d == g.dump_date.max():
                h = df.groupby("host_id").agg(listings=("id", "size"), entire=("room_type", lambda s: s.eq("Entire home/apt").sum()),
                                             reviews_ltm=("number_of_reviews_ltm", "sum")).sort_values("listings", ascending=False).head(25)
                for hid, hr in h.iterrows():
                    hosts.append(dict(city=city, dump_date=d, host_id=hid, listings=int(hr.listings), entire_home=int(hr.entire), reviews_ltm=int(hr.reviews_ltm), share_of_city=hr.listings / len(df)))
            log(f"{city} {d}: {len(df):,} listings, median entire-home price {r['median_price_entire']}, price non-null {r['price_non_null_share']:.0%}")
        dates = sorted(dumps)
        for i, d in enumerate(dates):
            # sequential pair
            if i > 0:
                pr = pair_row(dumps[dates[i - 1]], dumps[d])
                pairs.append(dict(city=city, region=REGION[city], pair_type="sequential", date_a=dates[i - 1], date_b=d, **pr))
            # year-ago pair: nearest earlier dump 9 to 15 months back
            tb = pd.Timestamp(d)
            cands = [x for x in dates[:i] if 270 <= (tb - pd.Timestamp(x)).days <= 460]
            if cands:
                basis_b = dumps[d].price_basis.iloc[0]
                same = [x for x in cands if dumps[x].price_basis.iloc[0] == basis_b and basis_b != "none"]
                best = min(same or cands, key=lambda x: abs((tb - pd.Timestamp(x)).days - 365))
                pr = pair_row(dumps[best], dumps[d])
                pairs.append(dict(city=city, region=REGION[city], pair_type="year_ago", date_a=best, date_b=d, **pr))
        del dumps
    PROC.mkdir(parents=True, exist_ok=True)
    s = pd.DataFrame(snaps); p = pd.DataFrame(pairs); h = pd.DataFrame(hosts)
    # scope flag: the Dec 2025 - May 2026 monthly dumps cover a subset of listings in several cities. A dump whose
    # listing count is under 80% of the largest dump of the same city within +/- 200 days is marked partial_scope.
    s["dump_date"] = pd.to_datetime(s["dump_date"])
    ref = []
    for r in s.itertuples():
        w = s[(s.city == r.city) & ((s.dump_date - r.dump_date).abs() <= pd.Timedelta(days=200))]
        ref.append(w.listings.max())
    s["scope_vs_peer"] = s.listings / pd.Series(ref, index=s.index)
    s["partial_scope"] = s.scope_vs_peer < 0.8
    for df in (s, p):
        df["date_b" if "date_b" in df else "dump_date"] = pd.to_datetime(df["date_b" if "date_b" in df else "dump_date"])
    p["days_apart"] = (pd.to_datetime(p.date_b) - pd.to_datetime(p.date_a)).dt.days
    p["lfl_price_chg_annualized"] = np.expm1(np.log1p(p.lfl_price_chg_median) * 365 / p.days_apart)
    s.round(4).to_csv(PROC / "inside_airbnb_city_snapshots.csv", index=False)
    p.round(4).to_csv(PROC / "inside_airbnb_like_for_like.csv", index=False)
    h.round(4).to_csv(PROC / "inside_airbnb_host_concentration.csv", index=False)
    log(f"wrote {len(s)} snapshots, {len(p)} pairs, {len(h)} host rows")
    pd.set_option("display.width", 250); pd.set_option("display.max_columns", 30)
    print(p[p.pair_type == "year_ago"][["city", "date_a", "date_b", "matched", "retention", "price_comparable", "matched_priced_entire", "lfl_price_chg_median", "matched_reviews_ltm_chg"]].to_string(index=False))


# ----------------------------------------------------------------------------------------------------- figures
def figures(args):
    import matplotlib; matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    FIG.mkdir(parents=True, exist_ok=True)
    s = pd.read_csv(PROC / "inside_airbnb_city_snapshots.csv", parse_dates=["dump_date"])
    p = pd.read_csv(PROC / "inside_airbnb_like_for_like.csv", parse_dates=["date_a", "date_b"])
    cities = list(KNOWN_DATES)
    colors = {c: plt.cm.tab20(i / 20) for i, c in enumerate(cities)}
    def panel(df, x, y, title, ylabel, fname, pct=True, hline=None):
        fig, ax = plt.subplots(figsize=(10, 5.5))
        for c, g in df.groupby("city"):
            g = g.sort_values(x)
            ax.plot(g[x], g[y] * (100 if pct else 1), marker="o", ms=3, lw=1.4, label=c, color=colors.get(c))
        if hline is not None:
            ax.axhline(hline, color="grey", lw=0.8, ls="--")
        ax.set_title(title, loc="left", fontsize=12, fontweight="bold"); ax.set_ylabel(ylabel); ax.grid(alpha=0.3)
        ax.legend(ncol=3, fontsize=8, frameon=False); fig.text(0.01, 0.005, "Source: Inside Airbnb (CC-BY 4.0), listings.csv.gz dumps; Citadel-ABNB analysis", fontsize=7, color="grey")
        fig.tight_layout(); fig.savefig(FIG / fname, dpi=150); plt.close(fig)
    ya = p[p.pair_type == "year_ago"]
    full = s[~s.partial_scope]
    panel(ya[ya.price_comparable & (ya.matched_priced_entire >= 500)], "date_b", "lfl_price_chg_median", "Like-for-like nightly price, year over year (matched entire-home listings, same price basis only)", "median same-listing price change, %", "inside_airbnb_lfl_price_yoy.png", hline=0)
    panel(ya, "date_b", "retention", "Listing retention: share of year-ago listing ids still present", "retention, %", "inside_airbnb_retention_yoy.png")
    panel(ya, "date_b", "matched_reviews_ltm_chg", "Same-listing reviews LTM, year over year (bookings-velocity proxy)", "matched listings, reviews LTM change %", "inside_airbnb_reviews_ltm_yoy.png", hline=0)
    panel(full, "dump_date", "multi_listing_share", "Multi-listing hosts: share of listings whose host has >1 listing in the city (full-scope dumps)", "share of listings, %", "inside_airbnb_multi_listing_share.png")
    panel(full, "dump_date", "superhost_share", "Superhost share of listings (full-scope dumps)", "share, %", "inside_airbnb_superhost_share.png")
    panel(full, "dump_date", "listings", "Listings per dump (full-scope dumps)", "listings", "inside_airbnb_listings.png", pct=False)
    panel(full, "dump_date", "share_entire_home", "Entire-home share of listings (full-scope dumps)", "share, %", "inside_airbnb_entire_home_share.png")
    panel(full, "dump_date", "reviews_ltm_sum", "Reviews in the last twelve months, all listings (bookings-velocity proxy, full-scope dumps)", "reviews LTM", "inside_airbnb_reviews_ltm_level.png", pct=False)
    log(f"figures written to {FIG}")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("step", choices=["discover", "download", "build", "figures", "all"])
    ap.add_argument("--workers", type=int, default=6)
    ap.add_argument("--cities", nargs="*")
    a = ap.parse_args()
    steps = {"discover": discover, "download": download, "build": build, "figures": figures}
    for st in (["discover", "download", "build", "figures"] if a.step == "all" else [a.step]):
        steps[st](a)


if __name__ == "__main__":
    sys.exit(main())
