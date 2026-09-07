"""Count Inside Airbnb reviews ("thank-you reviews") per market per quarter, from Theo's local files.

Why this exists: the bulk reviews.csv.gz files (258 files, 7.4 GB) live on Theo's external
volume (/Volumes/PortableSSD/...), not in the repo, and data.insideairbnb.com is blocked from
the cloud sandbox. So the count has to be run on the machine that has the volume. This script
does it with DuckDB directly over the gzipped CSVs - no unzipping, no pandas load of 640k rows.

What a "review" measures: every completed stay can leave one review, and Airbnb estimates roughly
half of stays do (Inside Airbnb's own 50% assumption). So review count per quarter is a stable
proxy for *completed nights-with-a-review*, i.e. realised demand in that city. It lags booking
(Airbnb reports Nights BOOKED) by the lead time, typically 3-8 weeks.

Inputs
  data/manifests/inside_airbnb_download_log.csv  (kind == 'reviews', local_path, row_count)

Outputs (data/processed/)
  inside_airbnb_reviews_by_market_quarter.csv   market, quarter, reviews, reviews_yoy
  inside_airbnb_reviews_us_total_quarter.csv    US-only sum by quarter + YoY (comparable to Airbnb NA nights)

Run (on Theo's machine, repo venv, volume mounted):
  pip install duckdb            # if not already there
  python analysis/src/count_reviews_duckdb.py
  python analysis/src/count_reviews_duckdb.py --countries united-states   # US only
  python analysis/src/count_reviews_duckdb.py --manifest path/to/other_log.csv

Rules baked in
  * Each file's snapshot_date decides its last COMPLETE quarter; later quarters are dropped
    (a snapshot on 2026-06-22 has a partial Q2-26, so Q1-26 is the last quarter kept).
  * Reviews written before 2019-01-01 are dropped (pre-COVID base only needed for YoY from 2020).
  * If a market has several snapshots, the latest is used (reviews.csv.gz is cumulative history).
  * Text is NOT read - only listing_id, id and date columns are projected, so this is fast.
"""
import argparse
import sys
from pathlib import Path

import duckdb

ROOT = Path(__file__).resolve().parents[2]


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--manifest", default=ROOT / "data/manifests/inside_airbnb_download_log.csv")
    ap.add_argument("--countries", nargs="*", default=None, help="e.g. united-states france  (default: all)")
    ap.add_argument("--min-date", default="2019-01-01")
    ap.add_argument("--out", default=ROOT / "data/processed")
    args = ap.parse_args()
    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)

    con = duckdb.connect()
    con.execute(
        """
        CREATE TABLE manifest AS
        SELECT country, region, city, CAST(snapshot_date AS DATE) AS snapshot_date, local_path, row_count
        FROM read_csv_auto(?, header=true)
        WHERE kind = 'reviews' AND classification = 'ok' AND http_status = 200
        """,
        [str(args.manifest)],
    )
    if args.countries:
        con.execute("DELETE FROM manifest WHERE country NOT IN (SELECT UNNEST(?))", [args.countries])

    # latest snapshot per market
    con.execute(
        """
        CREATE TABLE latest AS
        SELECT * FROM (
            SELECT *, ROW_NUMBER() OVER (PARTITION BY country, region, city ORDER BY snapshot_date DESC) AS rn
            FROM manifest) WHERE rn = 1
        """
    )
    files = con.execute("SELECT country, region, city, snapshot_date, local_path FROM latest ORDER BY 1,2,3").fetchall()
    missing = [f for f in files if not Path(f[4]).exists()]
    if missing:
        print(f"WARNING: {len(missing)} manifest files not found on disk (volume mounted?). First: {missing[0][4]}", file=sys.stderr)
    files = [f for f in files if Path(f[4]).exists()]
    print(f"{len(files)} markets with a reviews file on disk")

    con.execute("CREATE TABLE counts (country VARCHAR, region VARCHAR, city VARCHAR, snapshot_date DATE, quarter DATE, reviews BIGINT)")
    for country, region, city, snap, path in files:
        # last complete quarter = quarter start of snapshot minus 1 day
        con.execute(
            """
            INSERT INTO counts
            SELECT ?, ?, ?, ?, date_trunc('quarter', CAST(date AS DATE)) AS quarter, COUNT(*)
            FROM read_csv_auto(?, header=true, ignore_errors=true, columns={'listing_id':'VARCHAR','id':'VARCHAR','date':'VARCHAR','reviewer_id':'VARCHAR','reviewer_name':'VARCHAR','comments':'VARCHAR'})
            WHERE TRY_CAST(date AS DATE) >= CAST(? AS DATE)
              AND date_trunc('quarter', CAST(date AS DATE)) < date_trunc('quarter', CAST(? AS DATE))
            GROUP BY 5
            """,
            [country, region, city, snap, path, args.min_date, snap],
        )
        print(f"  {country}/{region}/{city} ({snap})")

    con.execute(
        """
        CREATE TABLE by_market AS
        SELECT country || '/' || coalesce(region,'') || '/' || city AS market, country, quarter, reviews,
               reviews / LAG(reviews, 4) OVER (PARTITION BY country, region, city ORDER BY quarter) - 1 AS reviews_yoy
        FROM counts ORDER BY market, quarter
        """
    )
    con.execute(f"COPY by_market TO '{out / 'inside_airbnb_reviews_by_market_quarter.csv'}' (HEADER)")

    # US total, restricted to quarters where every US market's snapshot covers the quarter
    con.execute(
        """
        CREATE TABLE us AS
        WITH cutoff AS (SELECT MIN(date_trunc('quarter', snapshot_date)) AS q FROM latest WHERE country = 'united-states')
        SELECT quarter, SUM(reviews) AS reviews
        FROM counts, cutoff WHERE country = 'united-states' AND quarter < cutoff.q
        GROUP BY quarter ORDER BY quarter
        """
    )
    con.execute(
        f"""
        COPY (SELECT quarter, reviews, reviews / LAG(reviews, 4) OVER (ORDER BY quarter) - 1 AS reviews_yoy FROM us ORDER BY quarter)
        TO '{out / 'inside_airbnb_reviews_us_total_quarter.csv'}' (HEADER)
        """
    )
    print(con.execute("SELECT quarter, reviews, ROUND(100*(reviews / LAG(reviews,4) OVER (ORDER BY quarter) - 1),1) AS yoy_pct FROM us ORDER BY quarter").df().tail(12).to_string(index=False))
    print(f"\nwritten: {out / 'inside_airbnb_reviews_by_market_quarter.csv'}\n         {out / 'inside_airbnb_reviews_us_total_quarter.csv'}")
    print("\nNext: join US total YoY to Airbnb North America revenue YoY (data/processed/airbnb_regional_revenue_quarterly.csv)"
          " and test whether review growth leads reported nights by one quarter.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
