"""Market-level listing aggregates from Inside Airbnb listings.csv.gz (2026 vintage)."""
import duckdb, time
from pathlib import Path
V1='raw/inside_airbnb'   # READ-ONLY: frozen v1, never written
SSD='/Volumes/PortableSSD/ABNB_DATA_EXPANSION/raw_expansion/v2_2026-09-05/inside_airbnb_current'
OUT=Path('processed/airbnb_quant_panel_v2_staging/derived'); OUT.mkdir(parents=True,exist_ok=True)
con=duckdb.connect(); con.execute("SET memory_limit='6GB';")
con.execute("SET temp_directory='/Volumes/PortableSSD/ABNB_DATA_EXPANSION/duckdb_tmp';")
t0=time.time()
con.execute(f"""
copy (
 select
  regexp_extract(filename,'inside_airbnb(?:_current)?/([^/]+)/',1) as country,
  regexp_extract(filename,'inside_airbnb(?:_current)?/[^/]+/([^/]+)/',1) as region,
  regexp_extract(filename,'inside_airbnb(?:_current)?/[^/]+/[^/]+/([^/]+)/',1) as market,
  strptime(regexp_extract(filename,'(\\d{{4}}-\\d{{2}}-\\d{{2}})/listings',1),'%Y-%m-%d')::date as snapshot_date,
  count(*) as listings,
  count(distinct host_id) as hosts,
  round(avg(case when room_type='Entire home/apt' then 1.0 else 0.0 end),4) as entire_home_share,
  round(avg(case when try_cast(calculated_host_listings_count as integer)>1 then 1.0 else 0.0 end),4) as multi_host_share,
  round(avg(case when host_is_superhost='t' then 1.0 else 0.0 end),4) as superhost_share,
  round(avg(case when license is not null and length(trim(license))>0 then 1.0 else 0.0 end),4) as license_disclosed_share,
  count(try_cast(replace(replace(price,'$',''),',','') as double)) as price_n,
  round(median(try_cast(replace(replace(price,'$',''),',','') as double)),2) as price_median_native,
  round(avg(try_cast(availability_365 as integer)),1) as avail365_mean,
  round(avg(try_cast(availability_30 as integer)),2) as avail30_mean,
  sum(try_cast(number_of_reviews as integer)) as reviews_total,
  sum(try_cast(number_of_reviews_ltm as integer)) as reviews_ltm,
  sum(try_cast(number_of_reviews_l30d as integer)) as reviews_l30d,
  round(avg(try_cast(review_scores_rating as double)),3) as rating_mean,
  round(avg(try_cast(estimated_occupancy_l365d as double)),2) as est_occupancy_l365d_mean
 from read_csv_auto(['{SSD}/*/*/*/*/listings.csv.gz','{V1}/*/*/*/*/listings.csv.gz'],
                    filename=true, ignore_errors=true,
                    union_by_name=true, sample_size=-1, all_varchar=true)
 group by 1,2,3,4 order by 1,3
) to '{OUT}/market_summary_2026.csv' (header, delimiter ',')
""")
p=OUT/'market_summary_2026.csv'
print(f'market_summary_2026.csv: {sum(1 for _ in open(p))-1} markets, {p.stat().st_size/1024:.0f} KB [{time.time()-t0:.0f}s]')
