"""Derive market-level forward booking curves from Inside Airbnb calendar files.

588M calendar rows -> a small aggregate that carries the signal, so the raw
bulk never needs to enter the repo. This is the 'commit derived aggregates'
pattern CONTRIBUTING prescribes.

available='f' conflates BOOKED / host-blocked / inactive listing. It is a bounded
proxy, never occupancy. Column is named blocked_rate for that reason.
"""
import duckdb, time, os
from pathlib import Path

SSD = '/Volumes/PortableSSD/ABNB_DATA_EXPANSION/raw_expansion/v2_2026-09-05/inside_airbnb_current'
OUT = Path('processed/airbnb_quant_panel_v2_staging/derived')
OUT.mkdir(parents=True, exist_ok=True)

con = duckdb.connect()
con.execute("SET memory_limit='6GB';")
con.execute("SET temp_directory='/Volumes/PortableSSD/ABNB_DATA_EXPANSION/duckdb_tmp';")
con.execute("SET preserve_insertion_order=false;")

t0 = time.time()
con.execute(f"""
create or replace view cal as
select
  regexp_extract(filename, 'inside_airbnb_current/([^/]+)/', 1)                       as country,
  regexp_extract(filename, 'inside_airbnb_current/[^/]+/([^/]+)/', 1)                 as region,
  regexp_extract(filename, 'inside_airbnb_current/[^/]+/[^/]+/([^/]+)/', 1)           as market,
  strptime(regexp_extract(filename,'(\\d{{4}}-\\d{{2}}-\\d{{2}})/calendar',1),'%Y-%m-%d')::date as snapshot_date,
  try_cast(date as date)   as stay_date,
  available,
  try_cast(minimum_nights as integer) as minimum_nights,
  listing_id
from read_csv_auto('{SSD}/*/*/*/*/calendar.csv.gz', filename=true, ignore_errors=true,
                   columns={{'listing_id':'VARCHAR','date':'VARCHAR','available':'VARCHAR',
                            'minimum_nights':'VARCHAR','maximum_nights':'VARCHAR'}})
""")

print('building booking curves...', flush=True)
con.execute(f"""
copy (
  select country, region, market, snapshot_date,
    case when date_diff('day', snapshot_date, stay_date) <=  30 then 'h000_030'
         when date_diff('day', snapshot_date, stay_date) <=  60 then 'h031_060'
         when date_diff('day', snapshot_date, stay_date) <=  90 then 'h061_090'
         when date_diff('day', snapshot_date, stay_date) <= 180 then 'h091_180'
         else                                                        'h181_372' end as horizon,
    count(*)                                                              as listing_nights,
    count(distinct listing_id)                                            as listings,
    sum(case when available='f' then 1 else 0 end)                        as blocked_nights,
    round(sum(case when available='f' then 1 else 0 end)::double/count(*), 5) as blocked_rate,
    round(median(minimum_nights), 2)                                      as median_min_nights
  from cal
  where stay_date is not null and snapshot_date is not null
    and date_diff('day', snapshot_date, stay_date) between 0 and 372
  group by 1,2,3,4,5
  order by 1,3,5
) to '{OUT}/booking_curves_by_market.csv' (header, delimiter ',')
""")
print(f'  booking curves done [{time.time()-t0:.0f}s]', flush=True)

t1 = time.time()
con.execute(f"""
copy (
  select country, region, market, snapshot_date,
    date_diff('day', snapshot_date, stay_date) as days_ahead,
    count(*) as listing_nights,
    round(sum(case when available='f' then 1 else 0 end)::double/count(*),5) as blocked_rate
  from cal
  where stay_date is not null and snapshot_date is not null
    and date_diff('day', snapshot_date, stay_date) between 0 and 372
  group by 1,2,3,4,5 order by 1,3,5
) to '{OUT}/booking_curve_daily.csv' (header, delimiter ',')
""")
print(f'  daily curve done [{time.time()-t1:.0f}s]', flush=True)

for f in ['booking_curves_by_market.csv','booking_curve_daily.csv']:
    p = OUT/f
    print(f'  {f}: {sum(1 for _ in open(p))-1:,} rows, {p.stat().st_size/1e6:.1f} MB', flush=True)
print(f'TOTAL [{time.time()-t0:.0f}s]', flush=True)
